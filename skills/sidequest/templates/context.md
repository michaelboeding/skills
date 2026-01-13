# Sidequest Context Prompt Template

This template is used to format the context prompt when spawning a sidequest session.

## User Choice Flow

Before gathering context, Claude asks the user via `AskUserQuestion`:

```
Include a summary of this chat in the sidequest?

Options:
1. Yes, include summary - Pass context about current work to help the new session
2. No, start fresh - Start the sidequest with no context from this session
```

If `--no-context` flag was provided, this question is skipped.

## With Context (user selected "Yes, include summary")

```
SIDEQUEST from main task.

Main task context:
- Working directory: {{working_directory}}
- Git branch: {{git_branch}}
- Was working on: {{current_task_summary}}
- Key files: {{recent_files}}
- Progress: {{progress_notes}}

Your sidequest task: {{sidequest_task}}

This is separate from the main task. Focus only on this sidequest.
```

## Without Context (user selected "No" or --no-context flag)

```
SIDEQUEST MODE

Your task: {{sidequest_task}}

This is an independent task. Focus only on completing this sidequest.
```

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{working_directory}}` | Current PWD | `/Users/dev/myapp` |
| `{{git_branch}}` | Current git branch | `feature/user-auth` |
| `{{current_task_summary}}` | Brief summary from main session | `Building user authentication with JWT` |
| `{{recent_files}}` | Comma-separated recent files | `auth.ts, login.tsx, middleware.ts` |
| `{{progress_notes}}` | Key progress/decisions made | `Login endpoint complete, working on token refresh` |
| `{{sidequest_task}}` | User's sidequest task description | `Add a settings page with dark mode toggle` |

## Example Rendered Prompt

```
SIDEQUEST from main task.

Main task context:
- Working directory: /Users/dev/my-nextjs-app
- Git branch: feature/user-auth
- Was working on: Building user authentication with JWT
- Key files: auth.ts, login.tsx, middleware.ts
- Progress: Login endpoint complete, working on token refresh

Your sidequest task: Add a settings page with dark mode toggle

This is separate from the main task. Focus only on this sidequest.
```
