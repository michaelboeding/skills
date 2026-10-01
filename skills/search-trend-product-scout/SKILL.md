---
name: search-trend-product-scout
description: Discover and rank product ideas in a category using search trends, customer problems, and competing products. Use when a user wants trend-led product opportunities in areas such as hunting, outdoor gear, pets, or home goods, with an evidence-backed opportunity report.
---

# Search Trend Product Scout

Turn category search behavior into a shortlist of useful products worth testing. Connect a measured search signal to a specific customer problem, existing solutions, a differentiated concept, and a practical validation experiment.

## Intake

Reuse information already supplied. Ask a compact set of questions about missing essentials using an available question tool or ordinary conversation:

- Category, subcategories, customer, and problems of interest. Broad categories are valid starting points.
- Target country/region and language. State a proposed market if omitted; do not silently blend global and local results.
- Physical products, software, services, or any of these; desired selling price; manufacturing capabilities and development budget, when known.
- Research period and constraints such as seasonal versus year-round products, existing brands, materials, fulfillment, or channels.

If only the category is known, proceed with a stated market assumption and a broad first pass. Use five years for seasonal context and the latest complete comparable periods for momentum when data permits. Unknown price or budget remains unknown; it need not block discovery.

## Collect usable evidence

Read [references/trend-research.md](references/trend-research.md) before interpreting trend data. Confirm available access before promising metrics:

- Use Google Trends Explore through available browser tools, user-provided exports, or an authorized official API. Verify the API's current availability; do not assume public access.
- Use accessible keyword-volume tools as optional corroboration, recording geography, period, and whether values are estimates or ranges.
- Use product listings, manufacturer pages, reviews, and public customer discussions to investigate use cases, prices, recurring failures, and existing solutions.
- When time-series data is unavailable, deliver a preliminary qualitative opportunity scan, explicitly identify the missing measurements, and request an export or access if needed. Search snippets, autocomplete, and social engagement do not establish measured growth.

Preserve raw files and a source log containing URLs, retrieval dates, exact terms or topic IDs, filters, periods, and claim-level references. Keep interpretation distinct from what was observed.

## Find opportunities

1. Map the category into user jobs, activities, environments, product families, and pain points. Expand queries using observed related searches, synonyms, and problem language. Separate brands, news, informational queries, and product intent.
2. Evaluate sustained interest, recurring seasonality, same-season year-over-year change, related queries, and regional relevance. Check one-off events and weak baselines before calling something an emerging opportunity. Keep comparisons on compatible scales.
3. Investigate the promising clusters against customer accounts and current products. A complaint becomes stronger when it recurs in independent sources; record conflicting feedback and products that already solve it.
4. Convert a cluster into a concept: who needs it, when they use it, the problem, proposed mechanism/features, current alternatives, differentiation, price hypothesis, and practical build constraints. Search growth alone does not validate willingness to pay.
5. Rank using the rubric in [references/opportunity-report.md](references/opportunity-report.md). Recommend an interview, prototype, competitive check, or purchase-intent experiment and what result would change the recommendation.

For hunting, useful starting dimensions include species/activity, weather, footwear, carrying/organization, concealment/noise, camera power/mounting, and gear care. These are query seeds, not established trends. Distinguish gear shopping from searches about licenses, season dates, regulations, news, or the word “hunting” in another context. Investigate local timing rather than assuming all hunting activity peaks in fall.

## Analyze exported series

For a regular Google Trends interest-over-time CSV, use the standard-library helper when it fits:

```bash
python3 scripts/analyze_trends.py /path/to/multiTimeline.csv \
  --as-of YYYY-MM-DD --output /path/to/trend-analysis.json
```

Use the current research date in the user's timezone. The helper supports English `Month`, `Week`, `Day`, or `Date` headers with ISO dates and a regular monthly/weekly/daily series. It excludes unfinished periods, preserves missing/censored values, reports comparable prior-year windows and descriptive seasonality, and suppresses growth from very small baselines. Read its scope and limitations in [references/trend-research.md](references/trend-research.md). It does not fetch data, prove demand, combine independently scaled exports, or rank products.

## Deliver the report

Use [references/opportunity-report.md](references/opportunity-report.md) and [assets/report-template.md](assets/report-template.md). Unless the user chooses another format, deliver an illustrated PDF plus editable Markdown, a ranked opportunity CSV, source log, raw trend exports, and any analysis JSON.

Include charts from actual data, customer problem evidence, sourced competitors/prices, concept analysis, confidence and gaps, and next experiments. Label sketches or generated visuals as proposed concepts. Cite image sources and only use assets available for the report. If PDF tools are unavailable, preserve the editable report and disclose that the PDF was not produced. Render and inspect exported PDF pages with available PDF tooling before delivery.

Return a small, well-supported shortlist; fewer ideas are better than padding. Explain the strongest candidates and what still needs testing. A preliminary scan may contain unvalidated ideas, but must not claim measured trends or market validation.

For chosen mechanisms, an optional next step is the sibling `expired-patent-scout` if available and requested. Pass the concept and target markets; search trends do not establish patent clearance. Research does not authorize sending reports, contacting customers/suppliers, placing orders, or launching paid experiments.
