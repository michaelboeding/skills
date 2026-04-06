#!/bin/bash
# Auto Permissions Review Hook for Claude Code
# - Per-session: each session independently enables/disables via session ID files
# - Only active when accept-edits (or more permissive) mode is on
# Toggle: /auto-permissions-review-enable and /auto-permissions-review-disable

SESSION_DIR="$HOME/.claude/ai-review-sessions"
LOG_FILE="$HOME/.claude/ai-review.log"

# Debug logging (set to 1 to enable, 0 to disable)
DEBUG=1

log() {
  [ "$DEBUG" = "1" ] && printf '%s %s\n' "$(date '+%H:%M:%S')" "$1" >> "$LOG_FILE"
}

# Read the tool call JSON from stdin
INPUT=$(cat)

# Parse fields needed for self-management
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)
TOOL_INPUT=$(printf '%s' "$INPUT" | jq -c '.tool_input // {}' 2>/dev/null)

# Helper: output the correct hookSpecificOutput JSON
allow() {
  local reason="${1:-Approved by AI review}"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"%s"}}\n' "$reason"
}

deny() {
  local reason="${1:-Blocked by AI review}"
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$reason"
}

# --- Self-management: handle enable/disable regardless of permission mode ---
if printf '%s' "$TOOL_INPUT" | grep -q "ai-review"; then
  if printf '%s' "$TOOL_INPUT" | grep -q "ai-review-enable"; then
    mkdir -p "$SESSION_DIR"
    touch "$SESSION_DIR/$SESSION_ID"
    log "Enabled for session $SESSION_ID"
  elif printf '%s' "$TOOL_INPUT" | grep -q "ai-review-disable"; then
    rm -f "$SESSION_DIR/$SESSION_ID"
    log "Disabled for session $SESSION_ID"
  else
    log "Allowing hook management command"
  fi
  allow "Hook management command"
  exit 0
fi

# --- Check if this session is enabled ---
if [ ! -f "$SESSION_DIR/$SESSION_ID" ]; then
  exit 0
fi

log "Hook fired for session $SESSION_ID"

# --- Parse tool info ---
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
PERMISSION_MODE=$(printf '%s' "$INPUT" | jq -r '.permission_mode // "default"' 2>/dev/null)

log "Permission mode: $PERMISSION_MODE | Tool: $TOOL_NAME"

# --- Auto-allow read-only tools (any permission mode) ---
case "$TOOL_NAME" in
  Read|Glob|Grep|LS|WebSearch|WebFetch|ToolSearch|TaskGet|TaskList)
    log "Auto-allowing read-only tool: $TOOL_NAME"
    allow "Read-only tool"
    exit 0
    ;;
esac

# --- Read-only Bash commands (any permission mode) ---
if [ "$TOOL_NAME" = "Bash" ]; then
  CMD=$(printf '%s' "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null)
  if echo "$CMD" | grep -qE '^(ls|cat|head|tail|find|tree|wc|which|file|diff|sort|pwd|echo|stat|du|df|uname|whoami|date|env|printenv|git (status|log|show|diff|branch|remote|tag)|npm list|pip list|cargo --version|node --version|python --version)'; then
    log "Auto-allowing read-only Bash: $CMD"
    allow "Read-only command"
    exit 0
  fi
fi

# --- Write tools: only Haiku-review in accept-edits mode ---
# In default mode, edits/writes should still show normal permission prompt
case "$TOOL_NAME" in
  Edit|Write|NotebookEdit)
    case "$PERMISSION_MODE" in
      acceptEdits|auto|dontAsk|bypassPermissions)
        log "Write tool in permissive mode — sending to Haiku"
        ;;
      *)
        log "Write tool in default mode — normal prompt"
        exit 0
        ;;
    esac
    ;;
esac

# --- Bash commands that aren't obviously read-only: Haiku reviews (any mode) ---
log "Sending to Haiku for review: $TOOL_NAME"

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

Respond with EXACTLY one line of text, nothing else:
- ALLOW
- BLOCK: <short reason>"

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
  allow "Approved by Haiku"
elif echo "$RESPONSE" | grep -qi "^BLOCK"; then
  REASON=$(echo "$RESPONSE" | sed 's/^BLOCK: *//')
  REASON=$(echo "$REASON" | sed 's/"/\\"/g')
  log "Decision: BLOCK — $REASON"
  deny "[Auto Review] $REASON"
else
  log "Could not parse response, falling through"
  exit 0
fi
