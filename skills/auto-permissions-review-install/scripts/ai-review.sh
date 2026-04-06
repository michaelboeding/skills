#!/bin/bash
# Auto Permissions Review Hook for Claude Code
# - Per-session: only runs for the session that enabled it
# - Only active when accept-edits (or more permissive) mode is on
# Toggle: /auto-permissions-review-enable and /auto-permissions-review-disable

FLAG_FILE="$HOME/.claude/ai-review-enabled"
LOG_FILE="$HOME/.claude/ai-review.log"

# Debug logging (set to 1 to enable, 0 to disable)
DEBUG=1

log() {
  [ "$DEBUG" = "1" ] && printf '%s %s\n' "$(date '+%H:%M:%S')" "$1" >> "$LOG_FILE"
}

# Exit silently if not enabled
[ ! -f "$FLAG_FILE" ] && exit 0

# Read the tool call JSON from stdin
INPUT=$(cat)

log "Hook fired"

# --- Permission mode gate ---
PERMISSION_MODE=$(printf '%s' "$INPUT" | jq -r '.permission_mode // "default"' 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$PERMISSION_MODE" ]; then
  log "ERROR: Failed to parse permission_mode from input"
  log "INPUT: $INPUT"
  exit 0
fi

log "Permission mode: $PERMISSION_MODE"

case "$PERMISSION_MODE" in
  acceptEdits|auto|dontAsk|bypassPermissions) ;; # proceed with review
  *)
    log "Skipping — permission mode '$PERMISSION_MODE' does not need AI review"
    exit 0
    ;;
esac

# --- Per-session binding ---
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)
STORED=$(cat "$FLAG_FILE" 2>/dev/null)

log "Session check: stored='$STORED' current='$SESSION_ID'"

if [ "$STORED" = "pending" ]; then
  echo "$SESSION_ID" > "$FLAG_FILE"
  log "Bound to session $SESSION_ID"
elif [ "$STORED" != "$SESSION_ID" ]; then
  log "Skipping — different session"
  exit 0
fi

# --- Build review request ---
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
TOOL_INPUT=$(printf '%s' "$INPUT" | jq -c '.tool_input // {}' 2>/dev/null)

log "Reviewing: $TOOL_NAME"

# Allow the hook's own management commands (enable, disable, install check)
if printf '%s' "$TOOL_INPUT" | grep -q "ai-review"; then
  log "Allowing hook management command (self-reference)"
  exit 0
fi

# Optional: skip review for read-only tools (uncomment to use)
# case "$TOOL_NAME" in
#   Read|Glob|Grep|LS) log "Skipping read-only tool"; exit 0 ;;
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

# Ensure claude is in PATH (nvm, homebrew, etc.)
export PATH="$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node/" 2>/dev/null | tail -1)/bin:$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Call Claude Haiku in print mode (no tools, no recursion)
RESPONSE=$(printf '%s' "$PROMPT" | claude -p --model claude-haiku-4-5-20251001 --permission-mode plan 2>/dev/null)
CLAUDE_EXIT=$?

log "Claude exit code: $CLAUDE_EXIT"
log "Claude response: $RESPONSE"

if [ $CLAUDE_EXIT -ne 0 ] || [ -z "$RESPONSE" ]; then
  log "ERROR: claude -p failed or returned empty"
  exit 0
fi

# Parse the response
if echo "$RESPONSE" | grep -qi "^ALLOW"; then
  log "Decision: ALLOW"
  exit 0
elif echo "$RESPONSE" | grep -qi "^BLOCK"; then
  REASON=$(echo "$RESPONSE" | sed 's/^BLOCK: *//')
  REASON=$(echo "$REASON" | sed 's/"/\\"/g')
  log "Decision: BLOCK — $REASON"
  printf '{"decision":"block","reason":"[Auto Review] %s"}\n' "$REASON"
else
  log "Could not parse response, falling through"
  exit 0
fi
