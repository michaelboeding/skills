#!/bin/bash
# sidequest.sh - Spawn a new Claude Code session in a separate terminal
#
# Usage:
#   sidequest.sh --task "Fix the bug" [--context "Working on X"] [--branch "main"] [--files "a.swift,b.swift"]
#   sidequest.sh --task "Fix the bug" --no-context
#
# Options:
#   --task      Required. The task description for the sidequest
#   --context   Optional. Summary of current work for context
#   --branch    Optional. Current git branch name
#   --files     Optional. Comma-separated list of key files
#   --no-context  Skip all context, start fresh
#   --iterm     Force use of iTerm
#   --terminal  Force use of Terminal.app

set -e

# Parse arguments
TASK=""
CONTEXT=""
BRANCH=""
FILES=""
NO_CONTEXT=false
FORCE_TERMINAL=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --task)
      TASK="$2"
      shift 2
      ;;
    --context)
      CONTEXT="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --files)
      FILES="$2"
      shift 2
      ;;
    --no-context)
      NO_CONTEXT=true
      shift
      ;;
    --iterm)
      FORCE_TERMINAL="iTerm"
      shift
      ;;
    --terminal)
      FORCE_TERMINAL="Terminal"
      shift
      ;;
    *)
      # If no flag, treat as task description
      if [[ -z "$TASK" ]]; then
        TASK="$1"
      fi
      shift
      ;;
  esac
done

# Validate required arguments
if [[ -z "$TASK" ]]; then
  echo "Error: Task description is required"
  echo "Usage: sidequest.sh --task \"Your task description\" [--context \"...\"] [--no-context]"
  exit 1
fi

# Detect terminal application
detect_terminal() {
  if [[ -n "$FORCE_TERMINAL" ]]; then
    echo "$FORCE_TERMINAL"
    return
  fi

  if [[ "$TERM_PROGRAM" == "iTerm.app" ]]; then
    echo "iTerm"
  elif [[ "$TERM_PROGRAM" == "Apple_Terminal" ]]; then
    echo "Terminal"
  else
    # Default to Terminal.app
    echo "Terminal"
  fi
}

# Build the context prompt
build_prompt() {
  local prompt=""

  if [[ "$NO_CONTEXT" == true ]]; then
    prompt="SIDEQUEST MODE

Your task: $TASK

This is an independent task. Focus only on completing this sidequest."
  else
    prompt="SIDEQUEST from main task.

Main task context:"
    prompt="$prompt
- Working directory: $PWD"

    if [[ -n "$BRANCH" ]]; then
      prompt="$prompt
- Git branch: $BRANCH"
    fi

    if [[ -n "$CONTEXT" ]]; then
      prompt="$prompt
- Was working on: $CONTEXT"
    fi

    if [[ -n "$FILES" ]]; then
      prompt="$prompt
- Key files: $FILES"
    fi

    prompt="$prompt

Your sidequest task: $TASK

This is separate from the main task. Focus only on this sidequest."
  fi

  echo "$prompt"
}

# Escape string for AppleScript
escape_for_applescript() {
  local str="$1"
  # Escape backslashes first, then double quotes
  str="${str//\\/\\\\}"
  str="${str//\"/\\\"}"
  # Escape newlines
  str="${str//$'\n'/\\n}"
  echo "$str"
}

# Launch in iTerm
launch_iterm() {
  local prompt="$1"
  local escaped_prompt
  escaped_prompt=$(escape_for_applescript "$prompt")

  osascript <<EOF
tell application "iTerm"
  activate
  tell current window
    create tab with default profile
    tell current session
      write text "cd '$PWD' && claude -p \"$escaped_prompt\""
    end tell
  end tell
end tell
EOF
}

# Launch in Terminal.app
launch_terminal() {
  local prompt="$1"
  local escaped_prompt
  escaped_prompt=$(escape_for_applescript "$prompt")

  osascript <<EOF
tell application "Terminal"
  activate
  do script "cd '$PWD' && claude -p \"$escaped_prompt\""
end tell
EOF
}

# Main execution
main() {
  local terminal_app
  terminal_app=$(detect_terminal)

  local prompt
  prompt=$(build_prompt)

  echo "Launching sidequest in $terminal_app..."
  echo "Task: $TASK"

  case "$terminal_app" in
    iTerm)
      launch_iterm "$prompt"
      ;;
    Terminal)
      launch_terminal "$prompt"
      ;;
    *)
      echo "Error: Unknown terminal application: $terminal_app"
      exit 1
      ;;
  esac

  echo ""
  echo "Sidequest started in new terminal!"
  echo "Task: $TASK"
  echo "Continue your main quest here."
}

main
