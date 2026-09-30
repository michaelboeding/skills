---
name: mobile-parity-check
description: Compare the UI and UX of iOS and Android apps in either direction. Pin the reference versions, create isolated branches in both repositories, launch simulators with matching fake data, and audit screens, navigation, interactions, visual states, and accessibility. Deliver a developer-ready PDF with paired screenshots, full UI/UX analysis, and actionable findings. Use for mobile UI/UX parity audits and port quality checks; broader backend audits and feature implementation are separate work.
---

# Mobile UI/UX Parity Check

Produce a reproducible comparison of what users see and how they accomplish tasks on iOS and Android. **The primary deliverable is a self-contained PDF with images and full UI/UX analysis.** Fixtures, builds, code inspection, and functional assertions support that comparison. Do not let backend or unit-test work replace actually viewing and using both apps.

Default to auditing and reporting. Changes to either app are limited to the test harness, fake data, and build setup needed for the audit unless product fixes are also requested.

## Establish the comparison

Read both repositories' instructions and build documentation. Infer paths, schemes, flavors, and existing UI test tools before asking for missing details. Resolve:

- **Repositories and versions:** identify both roots and the branch, tag, or commit to evaluate in each.
- **Design authority:** iOS reference, Android reference, or bidirectional comparison against requirements/designs. Honor a stated source of truth. If none is established, ask while inventorying both; if no answer arrives, report bidirectional differences with the preferred design unresolved. Commit recency does not establish design correctness.
- **Meaning of latest:** use the user's named release/development branch. Otherwise inspect documentation, remote default/upstream branches, and recent history and state the chosen interpretation. Fetch the selected remote when possible, then pin immutable SHAs. Do not substitute local HEAD silently for a requested remote version. If freshness is unverified, label the local snapshot clearly. Explicit pinned refs stay pinned.
- **UI/UX scope:** default to the union of both apps' discoverable screens, flows, roles, and major visual/interaction states. Record requested limits and known intentional differences. "Everything" requires a coverage inventory, not a claim of exhaustive proof.

Show a brief run contract with selected refs/SHAs, design reference and rationale, scope, device pair, and fixture strategy. Proceed with established choices; clarify only unresolved decisions that affect the audit.

## Isolate both apps

Create a branch and worktree per platform at the selected SHAs before adding fixtures. Default names are `michaelboeding/parity/<run-id>/ios` and `michaelboeding/parity/<run-id>/android`. Preserve original checkouts, uncommitted changes, and SSH remotes. Do not stash, reset, switch, merge, or push the user's branches as setup. If uncommitted work is explicitly in scope, preserve and document a separate snapshot including required untracked files; a worktree at HEAD does not include it.

Use the bundled helper when ordinary Git worktrees suit the environment. Set `PARITY_SKILL_DIR` to this skill's actual directory and replace example paths/refs:

```bash
python3 "$PARITY_SKILL_DIR/scripts/prepare_run.py" \
  --ios-repo "/path/to/ios-repo" --ios-ref "origin/main" \
  --android-repo "/path/to/android-repo" --android-ref "origin/main" \
  --reference-platform ios --reference-reason "User designated iOS as the design reference" \
  --output "/path/outside-the-repos/parity-run" --dry-run
```

Inspect the plan, then rerun without `--dry-run`, passing its `run_id` through `--run-id` and its `base_sha` values as the two refs so moving branches cannot change the selection. Retain the original requested ref names in the run contract. The helper refuses collisions, creates both worktrees, and writes `run.json`. It does not fetch, copy dirty files, launch apps, or claim test results. Partial failures preserve the manifest and created resources for recovery. If the host requires a managed worktree tool, use it and record equivalent paths/SHAs.

Choose a durable run directory outside both checkouts. Keep audit-only app edits in the new worktrees and evidence/reports in the run directory. Record final tested HEADs, dirty patches, and required untracked fixture/test files so the tested state can be rebuilt. Exclude credentials, caches, and real customer data.

## Prepare comparable screens and flows

Read [references/uiux-audit.md](references/uiux-audit.md) for the audit matrix and [references/fixtures.md](references/fixtures.md) before adding fake data. Inventory **both** apps' navigation, screens, feature flags, roles, and states; retain screens/features present on only one platform.

Create `coverage.json` with stable screen/flow/scenario/checkpoint IDs, preconditions, semantic steps, expected UI outcomes, and initial `not-run` statuses. Cover every discovered screen on the baseline device pair, then relevant small-screen, large-text, dark-mode, keyboard, and orientation states. Make exclusions and unexecuted combinations visible.

Load one canonical synthetic dataset through small platform adapters. Match account role, flags, IDs, text, images, dates, units, and counts. Verify representative rendered content before comparison. Keep real views, navigation, validation, formatting, and state transitions active; static replacement screens would invalidate the audit. Use independent copies of mutable state so one app's actions do not change the other's starting point.

Use local or designated test services with no production fallback. Fixtures should expose visual and interaction risks: empty, typical, crowded, long text, missing image, loading, failed request, denied permission, and other relevant states. Deep backend correctness testing is outside the default scope; verify data only as needed to establish fair inputs and the visible result of user actions.

## Launch, inspect, and interact

Read [references/simulator-workflow.md](references/simulator-workflow.md). Discover installed tools/runtimes and existing UI automation. Build from both audit worktrees, install those exact artifacts, and launch an iOS Simulator and Android Emulator with explicit device IDs. Record configuration, artifact/hash, OS/API level, screen dimensions, UI driver, commands, and outcomes.

Align comparable logical screen sizes, language, appearance, text scale, orientation, permissions, and fixture state. Native platform conventions may differ; preserve the intended task, content hierarchy, brand language, accessibility, and usability instead of requiring identical pixels.

For each scenario:

1. Reset both apps to the documented fixture and visual state.
2. Perform the same user intent through each platform's normal controls. Observe taps, discoverability, back/cancel behavior, feedback, keyboard/focus, and state retention.
3. Wait for observable UI readiness. Inspect layout, typography, spacing, assets, copy, affordances, clipping, scrolling, and the result of each action.
4. Capture matching checkpoints with screenshots and available accessibility/UI hierarchy evidence. Record transitions, gestures, animation, or intermittent problems when stills cannot explain them.
5. Compare the actual images and interaction evidence. Preserve originals and label any crop, mask, or scale. Pixel diffs can locate candidates but cannot decide cross-platform UX correctness.
6. Reproduce differences from a clean fixture. Distinguish a parity defect, documented native variation, shared UX problem, optional improvement, and harness/environment failure. Retain uncertainty and failed retests.

Use existing relevant UI checks and targeted functional assertions as supporting evidence. Matching tests or source code do not establish visual parity. A mocked BLE/camera/purchase flow can establish only the simulated UI state, not real integration behavior.

For build/device/login/automation failures, retain the command and log, attempt bounded setup repairs, and continue independent work. Do not rewrite product behavior or upgrade the app to make the audit pass. A blocked platform yields a partial report with no invented paired comparison.

## Report and hand off

Read [references/report-contract.md](references/report-contract.md) and start from [assets/report-template.md](assets/report-template.md). Deliver:

- `report.pdf` (required by default): a self-contained visual report with executive summary, complete screen/flow coverage, embedded paired screenshots, full UI/UX analysis, findings by impact, interaction evidence, accepted native differences, shared UX concerns, suggested improvements, and developer handoff. Full analysis covers the audited scope and explicitly identifies untested areas.
- `report.md`: the editable source containing the same analysis and evidence captions as the PDF.
- `findings.json` and `coverage.json`: stable IDs and structured observations linked to the same evidence.
- `run.json`, canonical fixtures, raw captures/logs, and reproducible audit patches/new files.

Use checkpoint outcomes `matched`, `difference`, `intentional`, `blocked`, `not-run`, and `not-applicable`. `matched` requires both sides to execute the comparable checkpoint. Report denominators and untested areas; zero findings does not establish parity. A native variation needs a rationale and equivalent task outcome. A flawed reference behavior becomes a shared/quality finding, not a requirement to copy the flaw.

For every actionable finding, include user impact, precise visual/interaction discrepancy, expected behavior and basis, paired evidence, reproduction, likely code locations, suggested ownership, and retest criteria. Label subjective design suggestions separately from verified defects. If an earlier audit exists, mark findings new, persisting, resolved with retest evidence, or not retested.

Generate the PDF using the available PDF skill/tooling when present, or an established local PDF renderer. Embed the images and substantive analysis; the reader must not need local image paths, Markdown, JSON, or this chat to understand the findings. Follow the PDF layout and verification requirements in the report contract.

Check evidence links, JSON, cross-references, and counts. Render every PDF page and visually inspect screenshots, text, tables, captions, and page breaks before delivery. Separate `complete`, `partial`, or `blocked` audit coverage from the verdict about UI/UX parity and from PDF export status. If export or visual verification is blocked, retain sources and evidence and report the incomplete PDF deliverable explicitly. Do not silently substitute Markdown. Do not generate or reconstruct screenshots as test evidence.

Retain audit branches/worktrees and reports for reproduction; shut down only resources started by this run. Package the report when requested. Do not send messages, post issues, publish branches, or create PRs just to deliver it. Before any email, show the exact message, recipients, and attachments and wait for approval.
