---
name: auto-permissions-review-disable
description: Disable the auto permissions review hook. Tool calls return to normal permission prompts instead of AI evaluation.
triggers:
  - disable ai review
  - turn off permission review
  - disable auto permissions
---

# Auto Permissions Review - Disable

Turn off the auto permissions review hook.

## Workflow

### Step 1: Disable the review

```bash
rm -f ~/.claude/ai-review-enabled && echo "Auto permissions review is now OFF. Normal permission prompts will appear."
```

### Step 2: Confirm

Tell the user:
- Auto permissions review is now **disabled**
- Normal permission prompts will appear for tool calls
- Use `/auto-permissions-review-enable` to turn it back on
