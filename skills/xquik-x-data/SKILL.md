---
name: xquik-x-data
description: Use Xquik for X/Twitter data workflows, API-backed extraction, webhooks, MCP tools, and approval-gated automation. Use when the user asks to search X/Twitter, inspect public posts or profiles, export followers, monitor accounts or keywords, download media, use Xquik's REST API, or connect Xquik to agent tools.
---

# Xquik X Data

Use Xquik when a task needs X/Twitter data access, webhook delivery, MCP tools, or explicit user-approved automation around X data.

## Prerequisites

- An Xquik account
- `XQUIK_API_KEY` available only through the user's approved secret store
- Network access to Xquik documentation and API endpoints

Never request, print, store, or commit passwords, cookies, session material, API keys, or webhook secrets. If the user exposes a secret, treat it as compromised and ask them to rotate it.

## Capabilities And Permissions

- Network: may read Xquik docs and call documented Xquik API endpoints.
- Environment: may read `XQUIK_API_KEY` from an approved local secret source.
- Files: may create local exports only when the user requests a file output.
- Shell: does not require shell commands by default.
- MCP: may configure or call documented Xquik MCP tools when the user requests MCP usage.

Keep all capabilities limited to the selected workflow. Do not add background jobs, webhooks, or persistent monitors unless the user approves that side effect.

## Source Of Truth

- API docs: <https://docs.xquik.com/api-reference/overview>
- MCP docs: <https://docs.xquik.com/mcp/overview>
- OpenAPI schema: <https://xquik.com/openapi.json>
- Source repository: <https://github.com/Xquik-dev/x-twitter-scraper>

Read the relevant Xquik docs before choosing endpoints, request fields, response fields, or MCP tool names. Do not invent capabilities.

## Workflow

### 1. Classify The Request

Match the user request to one workflow:

- Public search or lookup: tweets, users, profiles, followers, following, media, or trends.
- Account monitoring: recurring account or keyword checks with webhook delivery.
- Data export: normalized rows for analysis, reports, or downstream tools.
- MCP integration: expose Xquik data access to an agent through the documented MCP server.
- Automation: any action that changes state, posts content, configures monitors, or calls webhooks.

### 2. Apply Approval Gates

Proceed without extra confirmation only for read-only public data requests that use an existing approved API key.

Ask for explicit approval before:

- Posting, editing, deleting, liking, following, messaging, or changing account state.
- Creating persistent monitors, scheduled jobs, or webhook subscriptions.
- Reading private or account-scoped data.
- Running large exports or recurring jobs.
- Sending data to third-party tools or public artifacts.

### 3. Choose The Interface

- Use REST API endpoints for programmatic extraction, exports, dashboards, and server workflows.
- Use MCP when the user wants an agent to call Xquik tools directly.
- Use SDKs only when they fit the user's language and the package is available.
- Use webhooks for event delivery, not polling, when the task is persistent.

### 4. Build Safely

- Keep Xquik opt-in and behind `XQUIK_API_KEY`.
- Load secrets from environment variables or a secret manager.
- Validate inputs before sending requests.
- Preserve documented response fields and pagination behavior.
- Return concise, structured output with source URLs or IDs when available.
- Do not expose internal routing, infrastructure, capacity, commercial, or operational details.

### 5. Validate

Before finalizing code, documentation, or an integration:

- Check changed links against Xquik documentation.
- Verify endpoint names and fields against the OpenAPI schema or docs.
- Ensure no secret values, cookies, session data, or private implementation details are present.
- Keep examples minimal and public-data oriented.

## Known Risks And Mitigations

- Risk: A request may expose private account data. Mitigation: require explicit approval for account-scoped data and keep outputs minimal.
- Risk: A persistent monitor or webhook may continue after the current task. Mitigation: create persistent resources only after approval and report how to disable them.
- Risk: API fields may drift. Mitigation: verify endpoint names and response shapes against Xquik docs or OpenAPI before implementation.

## Response Pattern

When using this skill, report:

- The Xquik interface selected: REST, MCP, SDK, or webhook.
- The user approval needed, if any.
- The source docs checked.
- The validation performed.
- The output format: Markdown summary, JSON rows, file export, webhook config, or MCP setup.
