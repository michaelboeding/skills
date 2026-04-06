---
name: auto-permissions-review-install
description: Install an AI-powered permission review hook that uses Claude Haiku to evaluate tool call safety before execution. Per-session, auto-approves read-only operations, sends ambiguous Bash commands to Haiku, and only reviews edits in accept-edits mode. Use when setting up auto-approve with AI review, reducing permission fatigue, or wanting Claude to review its own tool calls.
triggers:
  - permission hook
  - ai review
  - auto approve
  - permission fatigue
  - auto permissions
  - install ai review
---

# Auto Permissions Review

Installs a `PreToolUse` hook that reduces permission prompt fatigue by auto-approving safe operations and sending ambiguous commands to Claude Haiku for review.

## Behavior

| Tool | Default mode | Accept-edits mode |
|------|-------------|-------------------|
| `Read`, `Glob`, `Grep`, `LS`, etc. | instant allow | instant allow |
| Simple Bash (`ls`, `cat`, `find`, `git status`) | instant allow | instant allow |
| Complex Bash (pipes, substitution) | Haiku reviews | Haiku reviews |
| `Edit`, `Write` | normal prompt (you decide) | Haiku reviews |

Key design choices:
- **Per-session** -- each terminal session independently enables/disables. Multiple sessions can run simultaneously without conflicts.
- **Read-only operations never prompt** -- `Read`, `Glob`, `Grep`, and common Bash reads are auto-approved instantly with no API call.
- **Ambiguous Bash always goes to Haiku** -- piped commands, subshells, and anything not in the read-only pattern list gets reviewed regardless of mode.
- **Edits respect your permission mode** -- in default mode you still approve edits manually. In accept-edits mode (Shift+Tab), Haiku reviews them.

## Related Commands

| Command | What It Does |
|---------|--------------|
| `/auto-permissions-review-install` | Install the hook (run once) |
| `/auto-permissions-review-enable` | Turn on for this session |
| `/auto-permissions-review-disable` | Turn off for this session |

## How It Works

1. User runs `/auto-permissions-review-enable` -- hook creates `~/.claude/ai-review-sessions/<session_id>`
2. Tool call triggers `PreToolUse` hook
3. Hook checks if a file for this session's ID exists
4. Read-only tools and simple Bash reads are auto-approved instantly
5. Complex Bash commands go to `claude -p --model claude-haiku-4-5-20251001 --permission-mode plan`
6. Write tools check permission mode -- Haiku in accept-edits, normal prompt in default
7. Haiku responds `ALLOW` or `BLOCK: <reason>`
8. Hook returns the decision to Claude Code

## Installation

Run the install script to set everything up:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/auto-permissions-review-install/scripts/install.sh"
```

This will:
1. Copy `ai-review.sh` to `~/.claude/hooks/`
2. Register the `PreToolUse` hook in `~/.claude/settings.json`

## Workflow

### Step 1: Check If Already Installed

```bash
[ -f ~/.claude/hooks/ai-review.sh ] && echo "Already installed" || echo "Not installed"
```

If already installed, tell the user and ask if they want to reinstall.

### Step 2: Run the Installer

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/auto-permissions-review-install/scripts/install.sh"
```

### Step 3: Confirm and Explain

After installation, tell the user:

```
Auto Permissions Review hook installed.

Usage:
  /auto-permissions-review-enable   -- turn on (this session only)
  /auto-permissions-review-disable  -- turn off (this session only)

Read-only operations are auto-approved instantly.
Ambiguous Bash commands are reviewed by Haiku.
Edits only go through Haiku when accept-edits mode is on (Shift+Tab).
Each session enables independently.
```

## Customization

The hook script is at `~/.claude/hooks/ai-review.sh`. Users can:
- Change the model (swap `claude-haiku-4-5-20251001` for any model)
- Add patterns to the read-only Bash allowlist
- Modify the Haiku evaluation prompt/rules
- Set `DEBUG=0` to disable logging

## Debug Log

When `DEBUG=1` (default), all hook activity is logged to `~/.claude/ai-review.log`:

```bash
cat ~/.claude/ai-review.log
```

## Requirements

- Claude Code CLI (`claude` command available)
- `jq` installed (`brew install jq`)
