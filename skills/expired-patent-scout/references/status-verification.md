# Status verification

Read before deciding that a candidate belongs in a recently expired list. Patent status is document-, claim-, jurisdiction-, and time-specific. The output is a research assessment with traceable evidence, not a legal clearance certificate.

## Evidence standard

Capture the patent/application number and kind, territory, patent type, relevant filing/benefit chain, grant date, apparent proprietor, decisive events, and the report's as-of date. Separate:

- An **official event** stating the relevant change, with effective date and subsequent history checked.
- An **official-record calculation**, with the term rule, inputs, adjustments, and unresolved assumptions explained.
- A **secondary report or estimate**, which remains unverified.

An office's general guidance page explains a rule but does not prove a candidate's status. Record the actual file/event/calculation. An aggregator's "expired" label, an old priority date, and an expired parent patent are each insufficient by themselves.

Use effective term-end/lapse dates for the recent window, separately from event publication and retrieval dates. For date-only evidence, do not treat an expiration dated today as already elapsed; place it in upcoming/unverified until the timing is resolved. Default ledger validation requires the effective end date to precede the as-of date for an expired shortlist.

## U.S. patents

Consult current [USPTO term guidance](https://www.uspto.gov/patents/laws/patent-term-calculator) and the actual file. The USPTO describes its calculator as an estimation resource; do not label your arithmetic as an office-certified expiration date. Check patent type, relevant filing/benefit dates, grant, adjustments/extensions, disclaimers, and maintenance history.

For utility/plant cases, identify the applicable domestic/international benefit chain rather than blindly using the earliest displayed priority date. U.S. provisional and foreign priority dates are not interchangeable with the filing date that controls the ordinary term. Older transitional cases and design patents require different rules. Read terminal-disclaimer language and associated patents, plus relevant adjustments/extensions, before relying on a date. See [MPEP 2701](https://www.uspto.gov/web/offices/pac/mpep/s2701.html); verify current rules at execution time rather than embedding a universal expiration formula.

For nonpayment, inspect actual due/grace periods, the expiration event, and any later petition or acceptance of delayed payment. Do not treat an unpaid fee still within its payment window as an expired patent. A fee-expired U.S. patent may be reinstated; keep these leads in a separate group and do not infer permanent availability from a long lapse. See [maintenance guidance](https://www.uspto.gov/patents/maintain) and [MPEP 2590](https://www.uspto.gov/web/offices/pac/mpep/s2590.html).

Design/plant patents do not use the same maintenance-fee regime as utility patents. Absence of a utility maintenance record is not evidence of their expiration. See [MPEP 2504](https://www.uspto.gov/web/offices/pac/mpep/s2504.html).

## Other jurisdictions and families

For an EP grant, check the relevant post-grant national status or Unitary Patent record. An EP procedural status or INPADOC event may be useful but is not a blanket status for every country. The [EPO's legal-status guidance](https://register.epo.org/help?lng=en&topic=eplegalstatus) directs users to the applicable registers for current post-grant information. For other countries, consult the responsible office's term, renewal, restoration, and extension rules.

A PCT publication is not a worldwide granted patent. Likewise, an abandoned application is not an expired granted patent; continuations or national counterparts may have survived. Track each relevant member separately. Family and citation searches identify possible active/pending rights, but assess what their claims actually concern instead of labeling every related record a blocker.

For revoked/cancelled rights, verify the decision, finality/appeal status, affected claims, and territories. Do not relabel partial cancellation as whole-patent expiration. If legal effect is unresolved, classify it as further research.

## Classification and promotion

| Status | Treatment |
| --- | --- |
| `term-expired` | Eligible for a recent-term-expiry candidate only when supported, elapsed, and in the requested country/date window |
| `fee-lapsed` | Separate lead with restoration uncertainty and current event history |
| `active` | Exclude from expired results; optionally show a requested upcoming estimate |
| `pending` | Potential future rights / further review, not an expired grant |
| `abandoned-application` | Separate public disclosure with surviving-family review needed |
| `revoked-or-cancelled` | Separate status-specific analysis; record finality and claim extent |
| `unknown` | Verification queue, never a confirmed expired result |

Keep patent-specific status confidence separate from broader freedom-to-operate uncertainty. Mark a lead ready for deeper product exploration only after the relevant claims and initial family/overlap search have been performed. Where related active rights are found, describe the concrete potential overlap and next review needed; do not promise unrestricted use.

The [WIPO public-domain/FTO toolkit](https://www.wipo.int/tisc/en/docs/tisc-toolkit-freedom-to-operate-description.pdf) explains why another patent can still cover a feature of a product despite an identified right no longer being in force. Product implementation also does not automatically carry rights to a competitor's trademarks, appearance, software, or confidential know-how. Keep the conclusion specific to the researched mechanism and jurisdiction.

At delivery, recheck decisive records and record their access dates. If the portal is inaccessible, data is delayed, or sources disagree, describe exactly what remains unverified and provide a useful partial result. No candidates found means none verified within the performed search, not that no patents exist.
