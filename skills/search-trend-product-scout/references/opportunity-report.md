# From evidence to a product decision

## Candidate record

For each concept preserve:

- ID, customer/activity, search cluster, market, and season/context.
- Actual trend observations: source/query/filter references, period, growth when supported, seasonality, volume estimates if available, and ambiguity or missing data.
- Problem evidence: dated accounts, review sample/method, repeated themes, contrary accounts, and whether existing products solve it.
- Concept, proposed differentiation, current alternatives with dated prices/specifications, and practical build/compatibility constraints.
- Price hypothesis, cost assumptions or quotes, channel/fulfillment constraints, and calculations used for any economics estimate. Label unsupported costs as unknown and do not infer profit from retail price alone.
- Evidence confidence, unresolved questions, experiment, effort/cost assumption, success signal, and what would cause rejection.

Record fact, inference, and proposed design distinctly. Use citations at the level needed to trace each consequential claim. If geography, use cases, or sources differ, explain why they are transferable before combining them.

## Ranking rubric

Use high/medium/low/unknown assessments with concise evidence, rather than an unexplained numeric score. Tailor importance to the user's constraints. “Unknown” never silently becomes a favorable assessment.

| Dimension | Evidence to consider |
|---|---|
| Search signal | Persistence, same-season comparison, scale, source quality, regional fit |
| Problem strength | Concrete failure/need, repetition across independent accounts, consequence |
| Differentiation | Existing solutions, what remains unresolved, likely defensibility/compatibility |
| Build feasibility | Materials/mechanism, sourcing, tooling, reliability and applicable requirements |
| Commercial fit | Target price, credible cost information, channel, shipping, purchase intent |

State overall confidence separately from attractiveness. A promising concept with no trend data is a hypothesis; a strong trend with no unresolved problem can be a weak product opportunity. Weak or adverse evidence can reduce rank. Do not let a high growth percentage from a tiny baseline dominate.

Prefer “test next,” “research first,” or “deprioritize” with a reason. Choose a few worthwhile concepts; only return ten if the evidence supports ten. Include promising rejected ideas and why they lost when that helps the decision.

## Validation experiments

Choose the smallest experiment resolving the main uncertainty. Examples include contextual interviews, a feature-specific prototype, field testing against a current alternative, or an explicitly authorized purchase-intent test. Describe the audience, question, observation, cost/effort assumption, decision rule, and stopping condition. Specify thresholds as proposed hypotheses when they have not been agreed or derived from evidence.

Do not describe a proposed interview or ad test as already completed. Drafting a test does not authorize outreach, posting, purchases, paid campaigns, or collecting personal information.

## Report package

Adapt [../assets/report-template.md](../assets/report-template.md). The default package contains:

- `product-opportunities.pdf`: illustrated analysis with executive recommendation, real trend charts, opportunity cards, comparison matrix, evidence, limitations, and experiments.
- `product-opportunities.md`: editable report.
- `opportunities.csv`: one row per concept with rank, customer, problem, concept, supporting source IDs, search-signal assessment, confidence, differentiation, feasibility, price hypothesis, recommendation, and next test.
- `sources.csv`: source IDs, URLs, retrieval dates, source type, query/settings where relevant, and claims supported.
- `data/`: original trend exports and any helper JSON. Preserve raw evidence rather than only screenshots of results.

Create scope notes with the actual research date, assumptions, source availability, filters, collection method, and omitted work. The PDF should be useful without this chat; include source identifiers/URLs and methodology inside it. Number figures and cite actual chart sources. Include competitor imagery only when it is accessible and usable for this report; custom sketches must be labeled as concepts. Avoid decorative visuals that imply tested performance.

Render the PDF and inspect pages for readable charts, units, wrapping, clipped tables, broken links, and figure/citation placement. If the research is preliminary, mark that status prominently. Do not draw fabricated growth charts to fill the layout.
