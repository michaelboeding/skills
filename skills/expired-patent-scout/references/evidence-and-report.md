# Evidence records and opportunity report

Read while collecting evidence and preparing the deliverable. The PDF and structured ledger must agree on patent IDs, dates, status basis, territory, ranking, and unresolved questions.

## Candidate ledger

Write `candidates.json` with `schema_version: 1` and these top-level objects:

- `scope`: `as_of`, `window_start`, `window_end` as ISO dates, `targets` as a nonempty list, and `jurisdictions` as a nonempty list of uppercase country codes. For a user-requested future list, set `include_upcoming: true` and `upcoming_end` to the agreed future date; otherwise omit it or use false. Record activities and other intake details in `research.json`.
- `sources`: objects with unique `id`, `title`, `url`, `kind`, and `accessed_on`. Kinds are `official-register`, `official-document`, `patent-publication`, `official-guidance`, `company`, or `secondary`. Add a locator and saved evidence path when appropriate. A patent publication can be the actual document hosted by a mirror; a secondary summary is not a publication.
- `candidates`: one record per patent/jurisdiction assessment. Related records share a `family_id`; do not merge distinct territorial statuses.

Required candidate fields:

| Field | Meaning |
| --- | --- |
| `id`, `patent_number`, `jurisdiction` | Stable lead ID and exact document/territory |
| `status` | One of the statuses in the verification reference |
| `bucket` | `recent-term-expiry`, `fee-lapse-lead`, `upcoming-expiry`, `older-expiry`, `unverified`, or `excluded` |
| `status_basis` | `official-event`, `official-record-calculation`, `secondary-only`, or `unknown` |
| `effective_end_date` | ISO date, or null when unresolved; future dates are forecasts |
| `status_checked_on` | Date the decisive status check was actually performed, or null if not checked |
| `basis_summary`, `status_sources` | Explanation of the events/calculation and source IDs supporting it |
| `claims_summary`, `claims_sources` | Plain-language granted claim/mechanism analysis and publication/document IDs; empty only for incomplete leads |
| `family_review`, `family_notes` | `searched`, `partial`, or `not-checked`, plus results/limitations and related-right IDs |
| `shortlisted` | Boolean for the record-supported recent-expiry product-exploration shortlist; not a legal-safety flag |

Also retain title, patent type, original/current assignee with evidence, filing/grant dates, family/member list, brand/product connection and its basis, source/figure locators, product ideas, fit/effort reasoning, active-right concerns, open questions, and next steps. These carry the substantive analysis beyond the minimum machine checks.

`recent-term-expiry` requires `term-expired`, record-supported status, and an elapsed date in the requested window. `fee-lapse-lead` requires `fee-lapsed` and an elapsed in-window lapse date. `upcoming-expiry` requires an `active` patent and a date on/after the as-of day; include only if the user requested that list. `older-expiry` retains a supported term end before the window. Incomplete, stale, contradictory, or secondary-only evidence belongs in `unverified` until resolved.

For supported buckets, check status on the report's as-of date and include candidate-specific official evidence refreshed that day. Older supporting documents remain useful for historical facts. If the run crosses days, refresh the decisive check or downgrade the claim of currency; do not falsify an access date. Shortlisted records additionally require a claims summary with document evidence and an initial family search with notes. Finding active rights does not invalidate the research lead, but those concerns must accompany it.

Run `scripts/validate_candidates.py` before delivery. It checks dates, bucket/status consistency, source references, duplicate patent-country records, and shortlist prerequisites. A successful check does not inspect source content, authenticate an office, calculate a patent term, prove completeness of a family search, or establish legal availability.

## PDF contents

Use `assets/report-template.md` as the editable source and produce `report.pdf` by default:

1. Scope, countries/activities, exact date window, as-of date, methods, and limits.
2. Ranked product-exploration shortlist with patent IDs, useful mechanism, effective term end, territory, status basis, fit, and remaining review.
3. Detailed opportunity cards with sourced patent drawings, relevant claims, plain-language mechanism, brand linkage, two concrete product concepts at most, feasibility assumptions, and suggested prototype/review tasks.
4. Per-country family/related-right maps showing active, pending, expired, and unverified records; distinguish documented concern from speculation.
5. Fee-lapse leads, requested upcoming expirations, older/incomplete leads, and excluded candidates in separate sections with reasons.
6. Source/evidence index, search coverage, access gaps, and a handoff for technical and patent review.

Figures should come from the actual patent document, with patent number, figure/page, and source. Use readable crops without changing the teaching; keep the original excerpt accessible. If adding an explanatory diagram, label it as the analyst's interpretation. Do not present a product photograph as proof that it implements a claimed invention. Missing figures are a stated limitation, not an invitation to fabricate them.

Provide inline citations close to status, date, ownership, and claim assertions. Summarize claims accurately and cite claim numbers instead of copying long claims wholesale. Distinguish official event dates from the analyst's calculations. Every assertion in the summary must be supported in its detailed card.

Use the available PDF skill/tooling; embed the essential images and full analysis so the PDF stands alone. Keep tables readable with repeated headers, page numbers, and a contents page for longer reports. After export, render every page, inspect text/figures/captions, and reconcile tables and IDs with JSON. If PDF generation or visual QA fails, preserve the sources and disclose the incomplete PDF deliverable.

## Handoff and limits

Conclude with the strongest research leads, what can be prototyped or investigated next, and exact outstanding rights questions for a patent professional. Do not label a whole branded product "free to copy" because one patent ended. State the scope of the preliminary search and recommend review before commercialization.

Keep `report.md`, `research.json`, `candidates.json`, `search-log.md`, and evidence alongside the PDF. External report delivery and recurring monitoring require a separate request. No-result reports should show work performed and sensible next search options; do not quietly expand scope to make the results appear stronger.
