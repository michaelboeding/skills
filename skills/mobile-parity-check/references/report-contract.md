# UI/UX report contract

Read when recording results and handing off. The default deliverable is `report.pdf`, with embedded screenshots and full analysis that stands on its own. Keep `report.md` as editable source and JSON/raw evidence as supporting files. Lead with visual and interaction findings; build/setup details support reproducibility and belong after the findings.

## Run and coverage

Extend the helper's `run.json` with remote freshness, scope/reference decisions, final tested HEADs and patches/new files, fixtures/reset instructions, build artifact hashes, device/OS/screen configurations, UI driver, command outcomes, and retained resources. Record no secret values. A branch name alone does not reproduce dirty audit edits.

`coverage.json` contains `schema_version: 1`, `run_id`, and `checkpoints`. Each checkpoint needs:

- `id`, `screen_id`, `flow_id`, `scenario_id`, `dimension`, `variant`, `fixture_id`, `fixture_hash`;
- `preconditions`, `reset`, `steps`, `expected`, `expectation_basis`;
- `ios` and `android`: execution status (`executed`, `failed`, `blocked`, `not-run`), observation, device/build identity, and evidence paths;
- comparison `status`, `reason`, and `finding_ids`.

Unavailable observations are null with a reason. Keep every planned row, including untested ones. A shared UX defect can link to a matched checkpoint because equally flawed behavior is still a quality issue.

| Status | Meaning |
| --- | --- |
| `matched` | Both apps executed comparable actions/inputs and the specified UI/UX assertion matched |
| `difference` | Evidence establishes a meaningful mismatch, including verified missing UI or app failure |
| `intentional` | Supported native/design variation with rationale and equivalent observed task outcome |
| `blocked` | A prerequisite prevented a valid paired comparison |
| `not-run` | In-scope work not yet executed |
| `not-applicable` | Excluded with a scope/requirement-based reason |

Show all counts, plus screen and flow coverage. Applicable = total minus not-applicable. Compared = matched + difference + intentional. Paired coverage = compared/applicable. If reporting parity among compared checkpoints, use (matched + intentional)/compared and show counts/formula. Zero denominators are `N/A`. Do not invent an overall UX score from these counts.

Completeness is `complete` only when every applicable planned checkpoint was compared, `partial` when some were compared and some blocked/not-run, and `blocked` when no valid paired comparison was possible. When nothing is applicable, explain that no comparison was performed. A complete audit may contain defects; a partial audit with no differences is still partial.

## Findings

`findings.json` contains `schema_version: 1`, `run_id`, and `findings`. Use stable IDs such as `PARITY-001`. Each record includes:

| Field | Content |
| --- | --- |
| `id`, `title`, `kind`, `dimension` | Specific discrepancy; kind = `parity-defect`, `shared-ux-issue`, `improvement`, `unresolved-difference`, or `harness-environment` |
| `severity`, `confidence` | P0–P3 impact and `confirmed`, `suspected`, or `inconclusive`; explain uncertainty |
| `affected_platforms`, `owner_hint` | iOS, Android, both, or unresolved; name people only when known |
| `screen_ids`, `scenario_ids`, `checkpoint_ids`, `fixture_id` | Links to coverage |
| `preconditions`, `steps` | Reset, account, device, flags, and precise semantic actions |
| `expected`, `expectation_basis` | Design/reference/requirement evidence or unresolved direction |
| `observed_ios`, `observed_android` | Actual appearance/behavior, not inferred results |
| `impact`, `evidence` | Task friction or usability failure and paired captures/recordings/assertions; include region/timestamps when useful |
| `reproduction` | Attempt count/results, including flaky/failed retests |
| `code_locations`, `likely_cause` | Repo/path/line at a stated revision/patch; label hypotheses |
| `suggested_fix`, `retest` | Design/implementation direction and observable acceptance criteria |
| `history` | New, persisting, resolved, or not retested when a prior audit exists |

Keep severity separate from confidence. P0 is a critical broadly blocking/destructive UX failure; P1 blocks an important flow, hides an essential action, or prevents required access; P2 materially degrades a usable flow, content, layout, or accessibility; P3 is minor polish. Base severity on demonstrated user impact, not pixel difference size. Optional improvements stay separate from the defect backlog and are labeled recommendations.

Confirmed parity findings need paired observations. For a missing feature, document the equivalent entry points checked. Source inspection alone supports suspicion. A reproduced crash is product evidence even without a rendered screen. Deduplicate a shared root issue across checkpoints while keeping all affected scenario links. Do not assume the non-reference platform owns every fix or copy a reference bug.

## Presentation and handoff

Start from `assets/report-template.md`. Lead with the reference versions, UI/UX result, strongest differences, and coverage limits. Include a screen comparison gallery and detailed issue blocks with paired screenshots. Include analysis by UI/UX dimension, explaining observed strengths, differences, user impact, and recommendations with evidence IDs. For interaction findings, include steps, tap/flow differences, feedback, and recordings/timestamps when relevant. Keep accepted native variations, shared UX issues, and optional improvements distinct.

Group actionable handoff by iOS, Android, shared/backend, and unresolved ownership. Each issue must be usable without chat history: finding IDs, exact tested state, fixture/reset recipe, reproduction, evidence, suggested fix, and retest acceptance.

Embed screenshots in the PDF; links to local files are supplementary and do not replace images or analysis. Use relative evidence paths in the source/package for portability. A requested shareable ZIP includes `report.pdf`, its editable source, sanitized manifests, fixtures, required harness patches/new files, and linked evidence, excluding worktree `.git`, caches, dependencies, and production configuration. An HTML companion is optional. Preserve the same findings, counts, and limits across formats.

Before delivery, parse JSON, resolve every finding/checkpoint reference, check file links, reconcile counts, and inspect paired screenshots at useful size. If captures are missing, label the gap rather than inventing substitute visuals. Mark prior findings resolved only after actual retest.

## PDF composition

The PDF is a full report, not an executive-summary export with the details left in JSON. Include:

1. **Run identification and summary:** app pair, date, pinned versions, design authority, audit scope/completeness, highest-impact issues, and practical limitations.
2. **Screen and flow gallery:** labeled iOS/Android captures at corresponding checkpoints, including matched screens as well as differences; place a large gallery in an appendix if needed. Include a clear disposition for each inventoried screen/flow.
3. **Full UI/UX analysis:** layout/hierarchy, typography/copy, imagery/brand, navigation/discovery, interactions/feedback, forms/keyboards, state completeness, responsive behavior, accessibility, and motion/continuity. Explain observed results and user impact, and mark any dimension not assessed.
4. **Detailed findings:** every actionable issue, severity/confidence, expected versus observed outcomes, exact reproduction, paired images or relevant captured failure evidence, likely code locations, suggested owner/fix, and retest acceptance. Include readable detail crops alongside full-screen context when needed.
5. **Native variations and improvements:** rationale for accepted differences, shared UX problems, and optional recommendations kept distinct from confirmed parity defects.
6. **Developer handoff and appendices:** prioritized work by platform/owner, complete coverage table with blocked/not-run/excluded checkpoints and reasons, fixture/setup/replay details, revisions, and evidence index. Include prior-audit changes when available.

Use a consistent page size, readable typography, heading hierarchy, page numbers, and a contents page/bookmarks for a long report. Keep screenshot aspect ratios intact and label platform, screen/state, environment variant, and evidence ID. Show two screenshots side by side only when readable; use larger facing/sequential pages or labeled crops when needed. Keep original captures in the evidence bundle. Do not shrink a full phone screen into a dense findings table.

Full analysis is bounded by executed coverage. A blocked or partial audit still gets a PDF containing actual observations, available images, and explicit limitations; never fabricate missing counterpart images. For animation or gestures, include representative captured frames, timestamps, and a written account in the PDF, with recordings as supplementary files. Important conclusions cannot depend solely on opening a video or local path.

## PDF generation and verification

Read the available PDF skill when using it. Prefer existing PDF tooling, such as ReportLab or an established HTML-to-PDF workflow, and discover bundled dependencies when the environment provides them. Export `report.pdf` from the final analysis; no particular renderer is required. Record renderer/command and export status in `run.json`.

After the last content/layout change, render **every page** to images with Poppler or equivalent and visually review them. Fix clipped text, truncated tables, missing images, tiny captions, distorted screenshots, orphaned headings, and broken page breaks. A successful export command or text extraction does not prove visual quality. Check extracted text for every finding ID and required section; reconcile PDF counts and observations against the JSON/source. Verify contents/page references, captions, and evidence labels.

Reopen the final PDF to confirm it is readable, contains embedded images and selectable analysis text, and has no unfinished template fields. For a partial audit, confirm the limitations are prominent. If rendering/export dependencies prevent completion, keep the source/evidence and report that PDF production or visual QA is blocked rather than declaring the report finished. Deliver the PDF as the primary file, with supporting source/data available separately.
