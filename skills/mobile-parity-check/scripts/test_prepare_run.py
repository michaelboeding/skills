#!/usr/bin/env python3
"""Integration tests in disposable repositories; never touches real app repos."""

import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock


SPEC = importlib.util.spec_from_file_location("prepare_run", Path(__file__).with_name("prepare_run.py"))
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True, check=True,
    ).stdout.strip()


class PrepareRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mobile-parity-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        # Ignore host global/system Git config and templates for disposable repos.
        self.env = mock.patch.dict(os.environ, {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Parity Test", "GIT_COMMITTER_NAME": "Parity Test",
            "GIT_AUTHOR_EMAIL": "parity@example.invalid", "GIT_COMMITTER_EMAIL": "parity@example.invalid",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.repos = {}
        self.bases = {}
        self.snapshots = {}
        for platform in ("ios", "android"):
            repo = self.root / (platform + " app with spaces")
            repo.mkdir()
            git(repo, "init", "--template=")
            git(repo, "symbolic-ref", "HEAD", "refs/heads/development")
            (repo / "screen.txt").write_text("base screen\n")
            git(repo, "add", "screen.txt")
            git(repo, "-c", "commit.gpgsign=false", "commit", "-m", "base")
            self.bases[platform] = git(repo, "rev-parse", "HEAD")
            (repo / "screen.txt").write_text("newer screen\n")
            git(repo, "add", "screen.txt")
            git(repo, "-c", "commit.gpgsign=false", "commit", "-m", "newer")
            git(repo, "remote", "add", "origin", f"git@github.com:example/{platform}.git")
            (repo / "screen.txt").write_text("staged user's work\n")
            git(repo, "add", "screen.txt")
            (repo / "screen.txt").write_text("unstaged user's work\n")
            (repo / "untracked.txt").write_text("keep me\n")
            self.repos[platform] = repo
            self.snapshots[platform] = self.snapshot(repo)

    def snapshot(self, repo):
        return {
            "head": git(repo, "rev-parse", "HEAD"),
            "branch": git(repo, "symbolic-ref", "HEAD"),
            "status": git(repo, "status", "--porcelain"),
            "staged": git(repo, "diff", "--cached"),
            "unstaged": git(repo, "diff"),
            "untracked": (repo / "untracked.txt").read_bytes(),
            "remotes": git(repo, "remote", "-v"),
        }

    def args(self, output=None, run_id="test-run"):
        return [
            "--ios-repo", str(self.repos["ios"]), "--ios-ref", self.bases["ios"],
            "--android-repo", str(self.repos["android"]), "--android-ref", self.bases["android"],
            "--reference-platform", "ios", "--reference-reason", "Test design baseline",
            "--output", str(output or self.root / "audit output"), "--run-id", run_id,
        ]

    def invoke(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = PREPARE.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def assert_sources_unchanged(self):
        for platform, repo in self.repos.items():
            self.assertEqual(self.snapshot(repo), self.snapshots[platform])

    def assert_no_audit_branches(self):
        for repo in self.repos.values():
            self.assertEqual(git(repo, "branch", "--list", "michaelboeding/parity/*"), "")

    def test_dry_run_changes_nothing(self):
        code, stdout, stderr = self.invoke(self.args() + ["--dry-run"])
        self.assertEqual(code, 0, stderr)
        plan = json.loads(stdout)
        self.assertEqual(plan["status"], "planned")
        self.assertEqual(plan["platforms"]["ios"]["base_sha"], self.bases["ios"])
        self.assertFalse((self.root / "audit output").exists())
        self.assert_no_audit_branches()
        self.assert_sources_unchanged()

    def test_prepares_pinned_clean_worktrees_and_preserves_dirty_sources(self):
        code, _, stderr = self.invoke(self.args())
        self.assertEqual(code, 0, stderr)
        manifest = json.loads((self.root / "audit output/run.json").read_text())
        self.assertEqual(manifest["status"], "prepared")
        for platform, item in manifest["platforms"].items():
            self.assertTrue(item["source_dirty"])
            self.assertFalse(item["uncommitted_included"])
            worktree = Path(item["worktree"])
            self.assertEqual(git(worktree, "rev-parse", "HEAD"), self.bases[platform])
            self.assertEqual(git(worktree, "symbolic-ref", "--short", "HEAD"), item["branch"])
            self.assertEqual(git(worktree, "status", "--porcelain"), "")
            self.assertEqual((worktree / "screen.txt").read_text(), "base screen\n")
            self.assertFalse((worktree / "untracked.txt").exists())
        self.assert_sources_unchanged()

    def test_invalid_second_ref_fails_before_any_mutation(self):
        args = self.args()
        args[args.index("--android-ref") + 1] = "missing-ref"
        code, _, _ = self.invoke(args)
        self.assertEqual(code, 1)
        self.assertFalse((self.root / "audit output").exists())
        self.assert_no_audit_branches()
        self.assert_sources_unchanged()

    def test_android_branch_collision_does_not_create_ios_branch(self):
        branch = "michaelboeding/parity/test-run/android"
        git(self.repos["android"], "branch", branch)
        code, _, stderr = self.invoke(self.args())
        self.assertEqual(code, 1)
        self.assertIn("already exists", stderr)
        self.assertEqual(git(self.repos["ios"], "branch", "--list", "michaelboeding/parity/*"), "")
        self.assertFalse((self.root / "audit output").exists())
        self.assert_sources_unchanged()

    def test_nested_output_and_existing_output_are_rejected(self):
        for output in (self.repos["ios"] / "audit", self.root):
            with self.subTest(output=output):
                code, _, _ = self.invoke(self.args(output=output))
                self.assertEqual(code, 1)
        self.assert_no_audit_branches()
        self.assert_sources_unchanged()

    def test_partial_failure_retains_manifest_and_successful_worktree(self):
        original_git = PREPARE.git

        def fail_android(repo, *args, **kwargs):
            if Path(repo) == self.repos["android"] and args[:2] == ("worktree", "add"):
                raise PREPARE.SetupError("Simulated disk/setup failure on Android")
            return original_git(repo, *args, **kwargs)

        with mock.patch.object(PREPARE, "git", side_effect=fail_android):
            code, _, stderr = self.invoke(self.args())
        self.assertEqual(code, 1)
        self.assertIn("Partial setup retained", stderr)
        manifest = json.loads((self.root / "audit output/run.json").read_text())
        self.assertEqual(manifest["status"], "partial")
        self.assertEqual(manifest["platforms"]["ios"]["state"], "ready")
        self.assertEqual(manifest["platforms"]["android"]["state"], "inspect-after-failure")
        self.assertEqual(git(Path(manifest["platforms"]["ios"]["worktree"]), "rev-parse", "HEAD"), self.bases["ios"])
        self.assert_sources_unchanged()


if __name__ == "__main__":
    unittest.main(verbosity=2)
