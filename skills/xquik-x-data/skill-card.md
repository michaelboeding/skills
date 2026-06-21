# Skill Card

## Description

xquik-x-data guides agents through Xquik-backed X/Twitter data workflows with explicit approval gates for private data, persistent jobs, webhooks, and write actions.

This skill is for development and operational workflows that use an approved Xquik account and API key.

## Owner

Xquik-dev maintains the referenced product documentation and source repository. This repository maintainer controls catalog inclusion.

## License/Terms Of Use

- Skill contribution license: repository MIT license
- Xquik product terms: <https://xquik.com/terms>

## Use Case

Use this skill when a user asks an agent to search X/Twitter, inspect public posts or profiles, export data, configure webhooks, use Xquik MCP tools, or integrate Xquik into data workflows.

## Deployment Geography For Use

Global, subject to the user's local laws, Xquik account eligibility, and applicable platform terms.

## Known Risks And Mitigations

Risk: The user may request private or account-scoped data.

Mitigation: Require explicit approval for private or account-scoped data and keep output minimal.

Risk: Persistent monitors and webhook subscriptions can outlive the current task.

Mitigation: Create persistent resources only after explicit approval and report how to disable them.

Risk: API fields or endpoint behavior can change.

Mitigation: Verify endpoint names, fields, and response shapes against Xquik docs or OpenAPI before implementation.

Risk: Secrets can leak through examples, logs, or generated files.

Mitigation: Use only approved secret stores and scan outputs for API keys, cookies, session material, and webhook secrets.

## References

- Xquik API docs: <https://docs.xquik.com/api-reference/overview>
- Xquik MCP docs: <https://docs.xquik.com/mcp/overview>
- Xquik OpenAPI schema: <https://xquik.com/openapi.json>
- Source repository: <https://github.com/Xquik-dev/x-twitter-scraper>

## Skill Output

Output types: plans, API usage guidance, MCP setup guidance, code snippets, JSON rows, Markdown summaries, file exports, and webhook configuration guidance.

Output format: match the user request and keep records structured enough for downstream tools.

Other properties: default to read-only public data workflows unless the user explicitly approves private data, persistent jobs, webhooks, or write actions.

## Skill Version

Initial catalog contribution for this repository.

## Ethical Considerations

Use this skill only for authorized X/Twitter workflows. Do not help bypass access controls, harvest private data without consent, or hide automation side effects from the user.
