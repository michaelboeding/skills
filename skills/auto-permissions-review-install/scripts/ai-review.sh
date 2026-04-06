#!/bin/bash
# Auto Permissions Review Hook for Claude Code
# - Per-session: only runs for the session that enabled it
# - Only active when accept-edits (or more permissive) mode is on
# Toggle: /auto-permissions-review-enable and /auto-permissions-review-disable

FLAG_FILE="$HOME/.claude/ai-review-enabled"

# Exit silently if not enabled
[ ! -f "$FLAG_FILE" ] && exit 0

# Read the tool call JSON from stdin
INPUT=$(cat)

# --- Permission mode gate ---
# Only run when auto-accepting is on. In default mode the user is
# already reviewing manually, so AI review just adds latency.
PERMISSION_MODE=$(echo "$INPUT" | jq -r '.permission_mode // "default"')
case "$PERMISSION_MODE" in
  acceptEdits|auto|dontAsk|bypassPermissions) ;; # proceed with review
  *) exit 0 ;; # default/plan — normal permission flow handles it
esac

# --- Per-session binding ---
# On first hook call after enable, bind to this session's ID.
# Subsequent calls from other sessions are ignored.
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
STORED=$(cat "$FLAG_FILE" 2>/dev/null)

if [ "$STORED" = "pending" ]; then
  # First hook call after enable — bind to this session
  echo "$SESSION_ID" > "$FLAG_FILE"
elif [ "$STORED" != "$SESSION_ID" ]; then
  # Different session — skip review
  exit 0
fi

# --- Build review request ---
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}')

# Optional: skip review for read-only tools (uncomment to use)
# case "$TOOL_NAME" in
#   Read|Glob|Grep|LS) exit 0 ;;
# esac

PROMPT="You are a security reviewer for a coding agent. Evaluate whether this tool call is safe to execute.

Tool: $TOOL_NAME
Input: $TOOL_INPUT

Rules:
- ALLOW read-only operations (reading files, listing directories, searching)
- ALLOW standard development commands (npm test, npm install, git add, git commit, cargo build, make, etc.)
- ALLOW file edits within the current working directory
- BLOCK commands that delete important files outside the working directory
- BLOCK commands that could leak secrets or credentials
- BLOCK destructive git operations (force push, reset --hard on main)
- BLOCK commands that affect system configuration
- BLOCK network requests to unknown/suspicious endpoints
- When in doubt, BLOCK

Respond with EXACTLY one line:
- ALLOW
- BLOCK: <short reason>

No other output."

# Call Claude Haiku in print mode (no tools, no recursion)
RESPONSE=$(echo "$PROMPT" | claude -p --model claude-haiku-4-5-20251001 --permission-mode plan 2>/dev/null)

# Parse the response
if echo "$RESPONSE" | grep -qi "^ALLOW"; then
  echo '{"decision":"allow"}'
elif echo "$RESPONSE" | grep -qi "^BLOCK"; then
  REASON=$(echo "$RESPONSE" | sed 's/^BLOCK: *//')
  REASON=$(echo "$REASON" | sed 's/"/\\"/g')
  echo "{\"decision\":\"block\",\"reason\":\"[Auto Review] $REASON\"}"
else
  # Can't parse response — fall through to normal permission prompt
  exit 0
fi
