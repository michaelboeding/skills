---
name: auto-permissions-review-install
description: Install an AI-powered permission review hook that uses Claude Haiku to evaluate tool call safety before execution. Per-session, only active when accept-edits mode is on. Use when setting up auto-approve with AI review, reducing permission fatigue, or wanting Claude to review its own tool calls.
triggers:
  - permission hook
  - ai review
  - auto approve
  - permission fatigue
  - auto permissions
  - install ai review
---

# Auto Permissions Review

Installs a `PreToolUse` hook that sends tool calls to Claude Haiku for safety evaluation. Two key behaviors:

1. **Per-session** -- enabling it only affects the current Claude Code session. New sessions start with it off.
2. **Accept-edits only** -- the review only fires when accept-edits mode (Shift+Tab) or a more permissive mode is active. In default mode you're already reviewing manually, so the hook stays silent.

## How It Works

1. User runs `/auto-permissions-review-enable` -- writes "pending" to flag file
2. User toggles accept-edits on (Shift+Tab)
3. Claude Code wants to use a tool (Bash, Write, Edit, etc.)
4. `PreToolUse` hook fires, reads `session_id` and `permission_mode` from stdin
5. First call: binds to this session's ID. Subsequent sessions are ignored.
6. Checks permission mode -- only proceeds if `acceptEdits`, `auto`, or more permissive
7. Pipes tool call to `claude -p --model claude-haiku-4-5-20251001 --permission-mode plan`
8. Haiku responds `ALLOW` or `BLOCK: <reason>`
9. Hook returns the decision to Claude Code

## Related Commands

| Command | What It Does |
|---------|--------------|
| `/auto-permissions-review-install` | Install the hook (run once) |
| `/auto-permissions-review-enable` | Turn on for this session |
| `/auto-permissions-review-disable` | Turn off |

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
  /auto-permissions-review-disable  -- turn off

The hook only fires when accept-edits mode is on (Shift+Tab).
In default permission mode, normal prompts appear as usual.
Each new session starts with it off.
```

## Customization

The hook script is at `~/.claude/hooks/ai-review.sh`. Users can:
- Change the model (swap `claude-haiku-4-5-20251001` for any model)
- Uncomment the allowlist to skip review for read-only tools
- Modify the evaluation prompt/rules
- Restrict which permission modes trigger the review

## Requirements

- Claude Code CLI (`claude` command available)
- `jq` installed (`brew install jq`)
