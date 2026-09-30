---
name: expired-patent-scout
description: Find recently expired patents relevant to specified brands, products, or technology areas and develop evidence-backed product opportunity leads. Ask for target brands/products, countries, and expiration window; research ownership and patent families, verify jurisdiction-specific status, and deliver an illustrated PDF with useful mechanisms, remaining risks, and next steps. Use for expired-patent opportunity scouting, not patent drafting or a legal freedom-to-operate opinion.
---

# Expired Patent Scout

Find useful technical ideas whose relevant patent term appears to have ended in the user's target markets, then explain what product opportunities merit further work. This is a research shortlist, not legal clearance to manufacture or sell. Recommend patent counsel review of selected implementations and jurisdictions before commercial reliance.

## Start with a short intake

Ask about the user's interests **before choosing the search targets**. Reuse answers already present. Use an available question tool or concise chat questions, without requiring a particular vendor's tool name. Group the essential questions:

1. **What should we investigate?** Brands/companies, specific products or model names, technology areas, or problems the user wants to solve. Product/brand links and known patent numbers are helpful but optional. A category is enough; named brands are not required.
2. **Where would it be made and sold?** Countries for manufacture, import, sale, and use. Ask for the initial research market if the user is undecided; do not label something globally expired based on one country's record.
3. **What counts as recent?** Offer the last 12 months, 24 months, or a custom range. Use the last 24 calendar months as the stated working default when this preference is omitted, and record absolute dates plus an as-of date using the user's current date. Ask whether a separate upcoming-expiration list would help; include it only when requested.

Ask about constraints only when they affect ranking: intended customer/use case, price range, manufacturing capabilities, appetite for electronics/software, utility mechanisms versus product appearance, and research depth. Default to a focused shortlist of up to 10 strong opportunities, with fewer when the evidence supports fewer. Do not fill a quota with weak or unrelated patents.

If the target area is missing, keep intake pending and do not invent brands. If markets are missing, continue technical/brand discovery but leave jurisdiction-specific conclusions unresolved. Do not ask for brands now when the task is only to create or edit this skill.

Save the agreed scope in `research.json`: targets, countries/activities, date window, patent types, exclusions, optional future window, constraints, and as-of date. State material assumptions before searching.

## Discover candidates

Read [references/search-workflow.md](references/search-workflow.md). Research current records on every run; memory and snippets are insufficient for current legal status.

Expand brands into documented parent companies, subsidiaries, former names, acquired portfolios, and relevant original/current assignees. Distinguish ownership evidence, product marking, and simple technical similarity; a patent assigned to a company is not proof that a particular product uses it.

Search both assignee portfolios and the underlying technology using synonyms, patent classifications, and citations. Brand-only searches miss relevant mechanisms held by other companies. Review grants and families, then filter by the **effective expiration/lapse date**, not filing, publication, grant, news, or database-update date. Search upstream as needed to calculate term, and keep later active improvements visible.

Maintain a search log with source, exact query/filters, date, results screened, exclusions, and access limitations. Group related patents as one opportunity where appropriate while retaining separate country/member records. A discovery database or a mirrored patent document can aid research; its status label alone does not verify expiration.

## Verify status and remaining rights

Read [references/status-verification.md](references/status-verification.md) before classifying candidates. For each relevant patent/country, inspect the official file, applicable term facts, maintenance/renewal events, disclaimers/extensions, and any later restoration or amendment information. Link exact records with access dates and document/event locators.

Separate:

- **Recent term expirations:** supported official event or explained calculation from official records, with the end date inside the requested window and already elapsed.
- **Fee-lapse leads:** nonpayment cases with restoration/reinstatement uncertainty, shown separately from term-ended opportunities.
- **Upcoming expirations:** requested forecasts with assumptions, still treated as unexpired.
- **Older disclosures, abandoned applications, revoked/cancelled claims, and unverified leads:** clearly labeled background or further-research material, not counted as recently expired grants.

Do not assume a universal term, add 20 years to an arbitrary priority date, or treat a pending application/PCT publication as an expired worldwide patent. Where an office does not certify an expiration date, label a supported calculation as a calculation. If decisive records are inaccessible or conflicting, retain uncertainty rather than certifying the result.

Check continuations, divisionals, relevant continuations-in-part, reissues, national counterparts, and other active/pending patents covering the proposed implementation. Expiration of one member is not expiration of the whole family. An active improvement can matter even when the underlying mechanism is old. Record the search performed and actual potential overlap; merely sharing a family or citation is not proof of a blocker.

## Turn disclosures into useful opportunities

Read the relevant granted claims, current amendments/certificates where applicable, specification, and figures. For each serious candidate, explain:

- The concrete problem and mechanism, in plain language, and the specific claims/features being discussed.
- What the disclosure teaches versus what the claims covered; figures and abstracts are not substitutes for claim review.
- Its documented or inferred connection to the target brand/product, with the distinction made explicit.
- One or two product concepts or adaptations, useful differentiation, prototype questions, and implementation effort assumptions.
- Related active/pending rights, missing know-how, manufacturing/regulatory dependencies when relevant, and the next evidence needed.

Rank technical/commercial fit separately from status confidence and unresolved rights. Use explainable qualitative rankings, not an invented probability of legal safety. Product-market fit, costs, and novelty are hypotheses unless separately researched. Do not promise patentability of an improvement or that an expired patent licenses a brand, appearance, software, or complete commercial product.

Prioritize opportunities with record-supported term expiration, close fit, useful disclosure, and a completed initial claims/family review. Incomplete leads remain available in a separate research queue. Zero verified candidates is a valid result: report the search limits and propose a narrower target or wider time window without silently changing the requested scope.

## Report and validate

Read [references/evidence-and-report.md](references/evidence-and-report.md) and use [assets/report-template.md](assets/report-template.md). Default to an illustrated `report.pdf` with executive summary, ranked opportunities, sourced patent figures where available, status timeline, claims/mechanism analysis, country/family cautions, product ideas, and next steps. Include the complete candidate/exclusion ledger and source links. Preserve `report.md`, `research.json`, `candidates.json`, search log, and supporting evidence.

Use actual patent figures with patent/figure/page citations; clearly label any newly drawn explanatory diagram as an interpretation. Do not generate an image and present it as patent evidence. Read available PDF tooling instructions, embed figures at readable size, render every final PDF page, and inspect it before delivery. If export or record access is blocked, state the incomplete deliverable and preserve the research.

Validate the candidate ledger with the bundled helper:

```bash
python3 "$PATENT_SCOUT_SKILL_DIR/scripts/validate_candidates.py" "/path/to/run/candidates.json"
```

It checks record consistency, dates, evidence references, and shortlist requirements. It does **not** fetch sources, calculate legal patent terms, verify authenticity, or determine freedom to operate. Independently verify those matters. Recheck decisive official status records on the report's as-of date before promoting a lead, and flag source latency or unresolved events.

Deliver research and a clear next-step brief. Do not pay fees, file patent documents, contact owners, send reports, or schedule monitoring unless separately requested. A requested future-expiration list is a static research output, not an instruction to create an automation.
