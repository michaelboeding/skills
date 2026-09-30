# Matching fake data

Read before introducing fixtures. The objective is equal screen content and reachable interaction states while exercising original product code.

## Canonical contract

Store a platform-neutral fixture set in `fixtures/` with a schema/version, scenario ID, deterministic seed, fixed clock, timezone, locale, units, roles, feature flags, and stable entity IDs. Use explicit date offsets and numeric units/precision. Use visibly fake identities and synthetic media. Hash the fixture files and record hashes in `run.json`.

Use the same canonical input on both platforms. If storage/API formats differ, document the adapter mapping and verify representative imported records: IDs, counts, null values, order, permissions, displayed text/values, and assets. Separate hand-crafted datasets that merely look similar can create false UI findings. Use identical image bytes or a documented deterministic asset mapping.

Choose states that reveal UI/UX problems: no items, one item, typical content, many items, long names/body text, optional fields missing, unavailable images, delayed/failed responses, denied permission, and meaningful numeric/date boundaries. Include forms with valid/invalid inputs and success/failure outcomes. Do not invent irrelevant states or features.

## Injection and reset

Prefer an existing debug/demo mode or injection boundary. Otherwise add the smallest audit-only adapter: repository/service implementation, URL interception, local stub, or launch-selected demo account. Retain real views, parsing, validation, formatting, state transitions, and navigation. Do not precompute the app's expected result inside the adapter or replace a feature with a static mock screen.

Make fixture activation explicit and verify it after launch. Keep it excluded from release builds or disabled outside the audit configuration. Inspect the diff to confirm that fixture work has not changed the visual behavior being evaluated.

Give mutable scenarios independent platform namespaces or restore the canonical baseline before each run. Record reset commands and a success check. Repeat runs must not accumulate duplicate data, share edits, consume one-time states, or inherit unrelated simulator sessions. Installation alone is not a data reset.

Test services must fail closed when unavailable; do not fall back to production. Route analytics, purchase, push, email/SMS, and other write-producing effects to local stubs or designated test environments. Check destination routing with a deliberately unavailable stub or rejected request. If isolation cannot be established, block those scenarios rather than using real customer accounts.

## State the limits

An auth bypass can expose downstream screens but does not test the login experience. A stubbed purchase response can test a success/error state but not the real store sheet. Fake BLE events can test connected/disconnected UI, not a radio handshake. Keep those boundaries visible in coverage and findings.

Verify data to support the UI/UX comparison, not to expand into a general database/backend audit. Record only the data/contract checks needed to prove equivalent inputs and visible outcomes.
