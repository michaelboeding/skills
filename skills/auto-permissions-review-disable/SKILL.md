---
name: auto-permissions-review-disable
description: Disable the auto permissions review hook for this session. Tool calls return to normal permission prompts. Other terminal sessions are not affected.
triggers:
  - disable ai review
  - turn off permission review
  - disable auto permissions
---

# Auto Permissions Review - Disable

Turn off the auto permissions review hook for this session only.

## Workflow

### Step 1: Disable for this session

The hook detects this command by the keyword and removes this session's file automatically.

```bash
echo "ai-review-disable" && echo "Auto permissions review is now OFF for this session."
```

### Step 2: Confirm

Tell the user:
- Auto permissions review is now **disabled for this session**
- Other terminal sessions are not affected
- Normal permission prompts will appear for all tool calls
- Use `/auto-permissions-review-enable` to turn it back on
