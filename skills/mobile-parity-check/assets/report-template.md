# UI/UX parity report — {{app}} — {{run_id}}

<!-- Author the full analysis here and export report.pdf as the primary deliverable.
Embed actual screenshots in the PDF; local image links and JSON are supplementary.
Include complete coverage and analysis in the PDF, even if that needs appendices.
Render and visually review every final page. Remove all unused placeholders. -->

{{Report date and contents/page navigation for a long PDF.}}

## Result

{{Exact compared versions, design authority, UI/UX verdict, completeness, highest-impact findings, and practical limits. State unresolved design direction.}}

| Coverage | Count |
| --- | ---: |
| Inventoried / compared screens | {{screens}} |
| Inventoried / compared flows | {{flows}} |
| Total planned checkpoints | {{total}} |
| Matched | {{matched}} |
| Differences | {{difference}} |
| Accepted native/design variations | {{intentional}} |
| Blocked | {{blocked}} |
| Not run | {{not_run}} |
| Not applicable, with reasons | {{not_applicable}} |

Paired checkpoint coverage: {{compared}} / {{applicable}} ({{percent_or_NA}}).
Completeness: {{complete_partial_or_blocked}}.

## Screen comparison gallery

| Screen / state / environment | iOS | Android | Observation / finding IDs |
| --- | --- | --- | --- |
| {{screen_state_variant}} | {{embedded_ios_screenshot_or_explicit_unavailable_reason}} | {{embedded_android_screenshot_or_explicit_unavailable_reason}} | {{result}} |

{{For PDF layout, place paired images on dedicated pages when the table would make them too small. Label platform, screen/state, environment, and evidence ID. Include captured frames, timestamps, and written navigation/interaction analysis when still images are insufficient; recordings are supplementary. Use raw captures and label annotated/cropped variants.}}

## Full UI/UX analysis

{{Assess each relevant dimension: layout/hierarchy, typography/copy, brand/imagery, navigation/discovery, interaction/feedback, forms/keyboards, state completeness, responsive behavior, accessibility, and motion/continuity. Explain actual observations, strengths, differences, user impact, and recommendations with screen/finding/evidence IDs. State when a dimension was untested. Include successful/matched behavior as well as defects.}}

## UI/UX findings

| ID | Severity / confidence | Dimension and user impact | Platform / owner | Evidence |
| --- | --- | --- | --- | --- |
| {{id}} | {{severity_confidence}} | {{dimension_impact}} | {{platform_owner}} | {{relative_links}} |

### {{id}} — {{title}}

- **Type / severity / confidence:** {{classification}}.
- **Screen / scenario / checkpoint / fixture:** {{ids}}.
- **Preconditions and reset:** {{device_account_flags_reset}}.
- **Reproduction:** {{semantic_steps_or_command_link}}.
- **Expected design/behavior and basis:** {{requirement_reference_or_unresolved}}.
- **iOS observation:** {{actual_appearance_interaction}}.
- **Android observation:** {{actual_appearance_interaction}}.
- **User impact:** {{task_friction_accessibility_or_visual_problem}}.
- **Repeatability:** {{attempts_results}}.
- **Code locations / likely cause:** {{locations_and_labeled_hypotheses}}.
- **Suggested fix / ownership:** {{recommendation_or_unresolved}}.
- **Retest acceptance:** {{observable_criteria}}.

| iOS evidence | Android evidence |
| --- | --- |
| {{embedded_ios_image_or_captured_failure_evidence}} | {{embedded_android_image_or_captured_failure_evidence}} |

{{Readable detail crops with full-screen context, exact region/video timestamps, UI assertions, and relevant log excerpts. The finding must be understandable from the PDF without opening another file. Repeat issue blocks and remove unused placeholders.}}

## Accepted platform variations

{{Observed variation, native/design rationale, equivalent task outcome, and evidence.}}

## Shared UX issues and improvement suggestions

{{Keep demonstrated issues shared by both apps separate from optional subjective design recommendations. Link findings and state the expected user benefit.}}

## Coverage and blockers

{{Include the complete coverage table in the PDF, using an appendix if large; coverage.json is supplementary. Account for every screen/flow and tested environment; show excluded, blocked, and untested states, accessibility methods, hardware/mock limits, and steps needed to complete coverage.}}

## Developer handoff

{{Group actionable finding IDs by iOS, Android, shared/backend, and unresolved ownership. Include reproduce/reset instructions, evidence, suggested fixes, and retest criteria. Do not infer recipients or send automatically.}}

## Comparison and reproduction details

| Item | iOS | Android |
| --- | --- | --- |
| Repository | {{ios_repo}} | {{android_repo}} |
| Selected ref and pinned SHA | {{ios_base}} | {{android_base}} |
| Audit branch and worktree | {{ios_worktree}} | {{android_worktree}} |
| Tested HEAD and patch/extra files | {{ios_tested_state}} | {{android_tested_state}} |
| Configuration and build artifact/hash | {{ios_build}} | {{android_build}} |
| Device ID, dimensions, OS/API | {{ios_device}} | {{android_device}} |
| Locale, units, appearance, text scale | {{ios_environment}} | {{android_environment}} |

Design reference and rationale: {{authority}}.
Meaning of latest and freshness: {{branch_fetch_or_local_limitation}}.
Scope/exclusions: {{scope}}.
Fixtures, seed, clock, and hashes: {{fixtures}}.
UI driver, commands, and replay/reset recipe: {{instructions}}.
Mocked services and unverified integrations: {{limits}}.

{{Link run.json, fixtures, audit patches/new files, captures, and command logs. List retained branches/worktrees and devices/processes, with resource-specific optional cleanup instructions.}}

## Change since previous audit

{{If applicable: previous run/revisions and findings new, persisting, resolved with retest evidence, or not retested. Otherwise remove this section.}}
