---
name: auto-permissions-review-enable
description: Enable the auto permissions review hook for this session. When enabled and accept-edits mode is on, Claude Haiku evaluates every tool call for safety before execution. Requires auto-permissions-review to be installed first.
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

Write "pending" to the flag file. The hook will bind to this session on the next tool call.

```bash
echo "pending" > ~/.claude/ai-review-enabled && echo "Auto permissions review is now ON for this session."
```

### Step 3: Confirm

Tell the user:
- Auto permissions review is now **enabled for this session**
- It only activates when **accept-edits mode** is on (Shift+Tab)
- In default permission mode, normal prompts appear as usual
- Closing this session automatically deactivates it
- Use `/auto-permissions-review-disable` to turn it off early
