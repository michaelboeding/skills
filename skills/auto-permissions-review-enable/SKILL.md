---
name: auto-permissions-review-enable
description: Enable the auto permissions review hook for this session. Auto-approves read-only operations, sends ambiguous Bash to Haiku, and reviews edits only in accept-edits mode. Other terminal sessions are not affected.
triggers:
  - enable ai review
  - turn on permission review
  - enable auto permissions
---

# Auto Permissions Review - Enable

Turn on the auto permissions review hook for the current session.

## Workflow

### Step 1: Check if the hook is installed

```bash
[ -f ~/.claude/hooks/ai-review.sh ] && echo "installed" || echo "not installed"
```

If not installed, tell the user to run `/auto-permissions-review-install` first to install it.

### Step 2: Enable for this session

The hook detects this command by the keyword and creates a session file automatically.

```bash
mkdir -p ~/.claude/ai-review-sessions && echo "ai-review-enable" && echo "Auto permissions review is now ON for this session."
```

### Step 3: Confirm

Tell the user:
- Auto permissions review is now **enabled for this session**
- Read-only tools (`Read`, `Glob`, `Grep`, etc.) are auto-approved instantly
- Ambiguous Bash commands are reviewed by Haiku
- Edits only go through Haiku when **accept-edits mode** is on (Shift+Tab)
- Other terminal sessions are not affected
- Use `/auto-permissions-review-disable` to turn it off
