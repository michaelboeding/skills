# Search evidence and seasonal comparisons

## Source routes

Check current documentation and access at run time. As checked on October 1, 2026, the [official Google Trends API](https://developers.google.com/search/apis/trends) is an alpha requiring access; its scaling differs from Explore. Prefer the public Explore UI and its CSV exports when API access is absent. An unavailable source is an access gap, not permission to invent data or repeatedly retry blocked endpoints.

Google documents [CSV export and citation](https://support.google.com/trends/answer/4365538?hl=en). Keep the original export, Explore URL, screenshot where useful, retrieval date, terms/topics, country, category, search property, period, and time granularity. If only a screenshot is available, mark approximate chart readings; do not manufacture a precise series. A URL alone is insufficient evidence that data was retrieved.

Use an accessible keyword-volume provider or Google Ads Keyword Planner when available. [Google's historical-metric definitions](https://support.google.com/google-ads/answer/3022575?hl=en) describe close variants, targeting, and advertiser competition. Preserve estimates/ranges; CPC and ad competition are commercial clues, not product sales, profitability, or counts of competing products. Search Console describes the user's own site and cannot establish total category demand.

## What can be concluded

- Explore's 0–100 values represent sampled, relative search interest. Zero can reflect insufficient data. Do not convert these indices into search counts, revenue, or market size. [Google Trends data FAQ](https://support.google.com/trends/answer/4365533?hl=en)
- Broad topics and literal terms cover different queries. Record the selection, spelling, language, and filters; investigate ambiguous terms. [Compare terms and topics](https://support.google.com/trends/answer/4359550?hl=en)
- Related “rising” queries compare with the preceding period; “Breakout” denotes growth above 5,000%, potentially from a tiny base. This does not measure addressable demand or willingness to pay. [Related-search definitions](https://support.google.com/trends/answer/4355000?hl=en)
- Autocomplete and discussion posts help discover vocabulary and problems. They are qualitative observations, influenced by selection and context.
- Manufacturer listings establish advertised specifications and prices, not independent proof of performance. Reviews indicate reported experiences and may reflect selection bias. Preserve dates, sample/collection method, and contrary accounts; do not imply representative frequency from a few anecdotes.

## Compare compatible observations

Within one Explore export, use the same market, category, search property, date window, and normalization for numeric comparisons. Independently normalized charts cannot be ranked by comparing their peaks or average indices. Re-query candidates together when possible. Larger batches can use a documented shared anchor and compatible overlapping periods, with explicit calibration and sensitivity checks; this skill's helper does not implement calibration.

First inspect multiple years to identify recurring seasonality. Compare recent complete periods with the corresponding prior-year season, then inspect persistence and additional years if available. Explain the calendar window and whether the comparison is approximate. A short-window jump can simply be seasonal. Exclude partial intervals and label historical/stale datasets rather than presenting them as current.

Check news, launches, promotions, weather, season dates, and changes in terminology as alternative explanations. Repeated queries or sampling noise can matter at low interest. For fragile signals, broaden a query sensibly or repeat retrieval once and disclose disagreement. Do not cherry-pick the export giving the largest increase.

Growth of the index reflects changing relative search share. Call it “relative search-interest change,” with the actual window and source, rather than absolute demand growth. Keep missing data, suppressed small values, and measured zero distinct.

## Turning hunting searches into queries

Treat the following as hypotheses to investigate, not current findings:

| Customer job | Query directions | Possible concept to test |
|---|---|---|
| Carry equipment quietly | quiet gear, strap noise, pack organization, product-specific reviews | Quiet organizer or retention accessory |
| Keep feet comfortable | wet hunting boots, boot drying, cold feet, weather-specific use | Portable drying/storage concept |
| Keep cameras operating | trail camera battery life, solar compatibility, mounting issues | Compatible power or mounting accessory |

Verify which species, season, setting, and customer create the problem. Distinguish shopping from permits, safety information, news, and entertainment. Compare alternatives already sold before calling a gap unmet. Do not turn these examples into recommended products without evidence.

## CSV helper contract

An Explore export can include a weekly bucket starting before the selected range. Preserve the original export and use only full periods within the requested boundaries for analysis. If a boundary bucket overlaps the start or end, omit it conservatively in a documented derived copy; retain the common scaling. The helper uses `--as-of` to exclude unfinished periods but cannot infer the selected start/end from the CSV alone. Record the actual analyzed period separately from the requested range.

`scripts/analyze_trends.py` reads a single regular interest-over-time export; it makes no network calls. Python 3.9+ and the standard library are sufficient.

- UTF-8/BOM CSV; an English first-column header `Month`, `Week`, `Day`, or `Date`; subsequent columns are distinct term labels. Preamble and blank rows are accepted. An optional `isPartial` column is recognized.
- Dates use `YYYY-MM` for monthly periods or `YYYY-MM-DD` for period starts. Values must be finite indices in [0, 100]. Empty/NA cells are missing; `<1` is censored and remains unknown. Other formats fail with an explanation instead of silent conversion.
- Dates must be increasing without gaps, duplicates, or mixed frequency. Header-based detection can be overridden with `--frequency monthly|weekly|daily`; supply this for an ambiguous one-row `Date` series. Do not use the helper for API scales outside 0–100.
- `--as-of` is required. A monthly period ends at the next month's start; weekly/daily periods end after seven/one days. Rows explicitly partial or ending after that date are excluded. This assumes ISO period-start dates, not period-end dates.
- The default recent window is 3 monthly, 13 weekly, or 90 daily periods. `--periods` can select another positive window up to one year. Growth compares matched periods: 12 calendar months earlier, 52 weeks earlier (364 days, an approximation), or the same date a year earlier for daily data. A leap day without a match is not imputed.
- Growth requires every paired value in the selected window. Missing/censored values, insufficient history, partial/gapped pairs, a zero baseline, or a baseline mean below 5 index points produce a null percentage and an explanation. The 5-point threshold is a conservative heuristic on this export's scale, not a significance test.
- Seasonality is a descriptive mean by period-start calendar month, with observed counts. Weekly periods can cross month boundaries; these means are approximate, not a seasonal-adjustment model. Sparse years, unequal coverage, and incomplete values are flagged.
- The output includes input hash, period bounds, coverage, means, percentage when supported, and warnings. It neither authenticates source settings nor identifies winners. Maintain the source/filter log separately, and inspect the raw chart before drawing conclusions.

Example:

```bash
python3 scripts/analyze_trends.py multiTimeline.csv \
  --as-of 2026-10-01 --periods 3 --output trend-analysis.json
```

Use charts labeled with the relative-index units, source, market, terms/topics, date range, and aggregation. Keep separately scaled runs in separate panels unless explicitly calibrated.
