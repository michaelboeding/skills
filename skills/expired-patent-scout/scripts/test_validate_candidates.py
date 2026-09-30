#!/usr/bin/env python3
"""Synthetic record tests; no actual patents or legal conclusions are used."""
import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("validate_candidates", Path(__file__).with_name("validate_candidates.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def ledger():
    return {
        "schema_version": 1,
        "scope": {"as_of": "2026-09-30", "window_start": "2024-09-30", "window_end": "2026-09-30", "targets": ["Synthetic test mechanism"], "jurisdictions": ["US"]},
        "sources": [
            {"id": "S1", "title": "Synthetic official record", "url": "https://example.invalid/record", "kind": "official-register", "accessed_on": "2026-09-30"},
            {"id": "S2", "title": "Synthetic patent document", "url": "https://example.invalid/document", "kind": "patent-publication", "accessed_on": "2026-09-30"},
        ],
        "candidates": [{
            "id": "TEST-1", "patent_number": "TEST-PATENT-1", "jurisdiction": "US",
            "status": "term-expired", "bucket": "recent-term-expiry", "status_basis": "official-record-calculation",
            "effective_end_date": "2026-06-01", "status_checked_on": "2026-09-30",
            "basis_summary": "Synthetic calculation narrative; not a real patent.", "status_sources": ["S1"],
            "claims_summary": "Synthetic mechanism description.", "claims_sources": ["S2"],
            "family_review": "searched", "family_notes": "Synthetic family search; real legal status was not researched.",
            "shortlisted": True,
        }],
    }


class LedgerTests(unittest.TestCase):
    def test_supported_record_passes_consistency_checks(self):
        self.assertEqual(MODULE.validate(ledger()), [])

    def test_fee_lapse_cannot_be_promoted_as_term_expiration(self):
        data = ledger()
        data["candidates"][0]["status"] = "fee-lapsed"
        self.assertTrue(MODULE.validate(data))
        data["candidates"][0].update(bucket="fee-lapse-lead", shortlisted=False)
        self.assertEqual(MODULE.validate(data), [])

    def test_secondary_labels_and_general_guidance_do_not_verify_status(self):
        for kind in ("secondary", "official-guidance", "patent-publication"):
            with self.subTest(kind=kind):
                data = ledger()
                data["sources"][0]["kind"] = kind
                self.assertTrue(MODULE.validate(data))

    def test_future_or_same_day_expiry_is_not_already_elapsed(self):
        for day in ("2026-09-30", "2026-10-01"):
            with self.subTest(day=day):
                data = ledger()
                data["candidates"][0]["effective_end_date"] = day
                self.assertTrue(MODULE.validate(data))

    def test_wrong_country_and_older_dates_cannot_enter_recent_list(self):
        for changes in ({"jurisdiction": "DE"}, {"effective_end_date": "2023-04-01"}):
            with self.subTest(changes=changes):
                data = ledger()
                data["candidates"][0].update(changes)
                self.assertTrue(MODULE.validate(data))

    def test_stale_decisive_evidence_requires_recheck(self):
        data = ledger()
        data["sources"][0]["accessed_on"] = "2026-09-29"
        self.assertTrue(MODULE.validate(data))

    def test_shortlist_requires_claims_and_family_review(self):
        for changes in ({"claims_sources": []}, {"claims_summary": ""}, {"family_review": "partial"}, {"family_notes": ""}):
            with self.subTest(changes=changes):
                data = ledger()
                data["candidates"][0].update(changes)
                self.assertTrue(MODULE.validate(data))

    def test_unknown_sources_and_duplicate_patents_fail(self):
        data = ledger()
        data["candidates"][0]["claims_sources"] = ["MISSING"]
        self.assertTrue(MODULE.validate(data))
        data = ledger()
        duplicate = copy.deepcopy(data["candidates"][0])
        duplicate["id"] = "TEST-2"
        data["candidates"].append(duplicate)
        self.assertTrue(MODULE.validate(data))

    def test_upcoming_results_require_explicit_future_scope(self):
        data = ledger()
        data["candidates"][0].update(status="active", bucket="upcoming-expiry", effective_end_date="2027-03-01", shortlisted=False)
        self.assertTrue(MODULE.validate(data))
        data["scope"].update(include_upcoming=True, upcoming_end="2027-09-30")
        self.assertEqual(MODULE.validate(data), [])

    def test_honest_unverified_and_empty_results_are_valid(self):
        data = ledger()
        data["candidates"][0].update(
            status="unknown", bucket="unverified", status_basis="unknown", effective_end_date=None,
            status_checked_on=None, status_sources=[], claims_summary="", claims_sources=[],
            family_review="not-checked", family_notes="", shortlisted=False,
        )
        self.assertEqual(MODULE.validate(data), [])
        data["candidates"] = []
        data["sources"] = []
        self.assertEqual(MODULE.validate(data), [])

    def test_malformed_records_report_errors(self):
        for data in ([], {}, {"schema_version": 1, "scope": []}):
            with self.subTest(data=data):
                self.assertTrue(MODULE.validate(data))
        data = ledger()
        data["candidates"][0].update(status=[], shortlisted="yes")
        self.assertTrue(MODULE.validate(data))
        data = ledger()
        data["sources"][0]["accessed_on"] = "2026-02-30"
        self.assertTrue(MODULE.validate(data))
        data = ledger()
        data["sources"][0]["kind"] = []
        self.assertTrue(MODULE.validate(data))


if __name__ == "__main__":
    unittest.main(verbosity=2)
