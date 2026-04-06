#!/bin/bash
# Installer for Auto Permissions Review Hook
# Usage: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS="$CLAUDE_DIR/settings.json"

echo "Installing Auto Permissions Review Hook..."

# Create directories
mkdir -p "$HOOKS_DIR"

# Copy hook script
cp "$SCRIPT_DIR/ai-review.sh" "$HOOKS_DIR/ai-review.sh"
chmod +x "$HOOKS_DIR/ai-review.sh"
echo "  Hook script -> $HOOKS_DIR/ai-review.sh"

# Update settings.json
if [ ! -f "$SETTINGS" ]; then
  echo '{}' > "$SETTINGS"
fi

# Check if hook is already registered
if jq -e '.hooks.PreToolUse[]?.hooks[]? | select(.command | contains("ai-review.sh"))' "$SETTINGS" >/dev/null 2>&1; then
  echo "  Hook already registered in settings.json, skipping."
else
  # Add the hook entry using jq
  UPDATED=$(jq '
    .hooks //= {} |
    .hooks.PreToolUse //= [] |
    .hooks.PreToolUse += [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "bash ~/.claude/hooks/ai-review.sh"
      }]
    }]
  ' "$SETTINGS")
  echo "$UPDATED" > "$SETTINGS"
  echo "  Hook registered in $SETTINGS"
fi

echo ""
echo "Done! Inside Claude Code:"
echo "   /auto-permissions-review-enable   -> turn on (this session only)"
echo "   /auto-permissions-review-disable  -> turn off"
echo ""
echo "   Starts DISABLED. Only active when accept-edits mode is on."
