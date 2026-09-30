#!/usr/bin/env python3
"""Check candidate-ledger consistency; never determine legal patent status.

Python 3.9+, standard library only. Reads one local JSON file, makes no network
requests, and does not calculate patent terms or decide freedom to operate.
"""

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


STATUSES = {"term-expired", "fee-lapsed", "active", "pending", "abandoned-application", "revoked-or-cancelled", "unknown"}
BUCKETS = {"recent-term-expiry", "fee-lapse-lead", "upcoming-expiry", "older-expiry", "unverified", "excluded"}
BASES = {"official-event", "official-record-calculation", "secondary-only", "unknown"}
KINDS = {"official-register", "official-document", "patent-publication", "official-guidance", "company", "secondary"}
OFFICIAL = {"official-register", "official-document"}
CLAIM_DOCUMENTS = {"official-document", "patent-publication"}
SUPPORTED = {"recent-term-expiry", "fee-lapse-lead", "upcoming-expiry", "older-expiry"}


def validate(data):
    errors = []

    def problem(where, message):
        errors.append(f"{where}: {message}")

    def read_date(value, where, optional=False):
        if optional and value is None:
            return None
        if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            try:
                return date.fromisoformat(value)
            except ValueError:
                pass
        problem(where, "expected an ISO date YYYY-MM-DD")
        return None

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    if not isinstance(data, dict):
        return ["ledger: expected a JSON object"]
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        problem("schema_version", "expected 1")
    scope = data.get("scope")
    if not isinstance(scope, dict):
        return errors + ["scope: expected an object"]
    as_of = read_date(scope.get("as_of"), "scope.as_of")
    start = read_date(scope.get("window_start"), "scope.window_start")
    end = read_date(scope.get("window_end"), "scope.window_end")
    if start and end and start > end:
        problem("scope", "window_start is after window_end")
    if end and as_of and end > as_of:
        problem("scope", "recent-expiration window extends beyond as_of")
    for key in ("targets", "jurisdictions"):
        values = scope.get(key)
        if not isinstance(values, list) or not values or not all(text(v) for v in values):
            problem(f"scope.{key}", "expected a nonempty list of strings")
    countries = scope.get("jurisdictions", [])
    countries = {v for v in countries if isinstance(v, str)} if isinstance(countries, list) else set()
    if any(v != v.upper() for v in countries):
        problem("scope.jurisdictions", "use uppercase country codes")
    upcoming = scope.get("include_upcoming", False)
    if type(upcoming) is not bool:
        problem("scope.include_upcoming", "expected a boolean")
    future_end = read_date(scope.get("upcoming_end"), "scope.upcoming_end") if upcoming is True else None
    if future_end and as_of and future_end < as_of:
        problem("scope.upcoming_end", "must be on or after as_of")

    raw_sources = data.get("sources")
    candidates = data.get("candidates")
    if not isinstance(raw_sources, list) or not isinstance(candidates, list):
        return errors + ["sources and candidates: expected arrays"]
    sources = {}
    source_dates = {}
    for index, source in enumerate(raw_sources):
        where = f"sources[{index}]"
        if not isinstance(source, dict):
            problem(where, "expected an object")
            continue
        identifier = source.get("id")
        if not text(identifier):
            problem(where, "missing source id")
            continue
        if identifier in sources:
            problem(where, f"duplicate source id {identifier}")
        sources[identifier] = source
        if not text(source.get("title")):
            problem(where, "missing source title")
        url = source.get("url")
        try:
            parsed = urlparse(url) if isinstance(url, str) else None
            valid_url = parsed is not None and parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        except ValueError:
            valid_url = False
        if not valid_url:
            problem(where, "source URL must be HTTP(S)")
        if not isinstance(source.get("kind"), str) or source["kind"] not in KINDS:
            problem(where, "invalid source kind")
        accessed = read_date(source.get("accessed_on"), where + ".accessed_on")
        source_dates[identifier] = accessed
        if accessed and as_of and accessed > as_of:
            problem(where, "source accessed after the report as_of date")

    seen_ids, seen_patents = set(), set()
    for index, item in enumerate(candidates):
        where = f"candidates[{index}]"
        if not isinstance(item, dict):
            problem(where, "expected an object")
            continue
        for key in ("id", "patent_number", "jurisdiction", "basis_summary"):
            if not text(item.get(key)):
                problem(where, f"missing {key}")
        identifier = item.get("id")
        if text(identifier):
            if identifier in seen_ids:
                problem(where, f"duplicate candidate id {identifier}")
            seen_ids.add(identifier)
        number, country = item.get("patent_number"), item.get("jurisdiction")
        if text(number) and text(country):
            pair = (re.sub(r"\s+", "", number).upper(), country)
            if pair in seen_patents:
                problem(where, "duplicate patent/jurisdiction assessment")
            seen_patents.add(pair)
            if country not in countries:
                problem(where, "jurisdiction is outside the agreed scope")

        status, bucket, basis = item.get("status"), item.get("bucket"), item.get("status_basis")
        for key, value, allowed in (("status", status, STATUSES), ("bucket", bucket, BUCKETS), ("status_basis", basis, BASES)):
            if not isinstance(value, str) or value not in allowed:
                problem(where, f"invalid {key}")
        if not all(isinstance(v, str) for v in (status, bucket, basis)):
            continue
        effective = read_date(item.get("effective_end_date"), where + ".effective_end_date", optional=True)
        checked = read_date(item.get("status_checked_on"), where + ".status_checked_on", optional=True)
        if checked and as_of and checked > as_of:
            problem(where, "status check is after as_of")
        refs = {}
        for key in ("status_sources", "claims_sources"):
            values = item.get(key)
            if not isinstance(values, list) or not all(text(v) for v in values):
                problem(where, f"{key} must be a list of source IDs")
                values = []
            refs[key] = [sources[v] for v in values if v in sources]
            for value in values:
                if value not in sources:
                    problem(where, f"unknown source {value} in {key}")
        for key in ("claims_summary", "family_notes"):
            if not isinstance(item.get(key), str):
                problem(where, f"{key} must be a string, empty only if incomplete")
        family = item.get("family_review")
        if not isinstance(family, str) or family not in {"searched", "partial", "not-checked"}:
            problem(where, "invalid family_review")
        if type(item.get("shortlisted")) is not bool:
            problem(where, "shortlisted must be a boolean")

        if bucket in SUPPORTED:
            if basis not in {"official-event", "official-record-calculation"}:
                problem(where, "supported bucket needs official event/record basis")
            if checked is None or checked != as_of:
                problem(where, "supported bucket needs a status check on as_of")
            official = [s for s in refs["status_sources"] if isinstance(s.get("kind"), str) and s["kind"] in OFFICIAL]
            if not official or not any(source_dates.get(s["id"]) == as_of for s in official):
                problem(where, "needs candidate-specific official evidence refreshed on as_of")
            if effective is None:
                problem(where, "supported bucket needs an effective end date")
        expected_status = {
            "recent-term-expiry": "term-expired", "fee-lapse-lead": "fee-lapsed",
            "upcoming-expiry": "active", "older-expiry": "term-expired",
        }.get(bucket)
        if expected_status and status != expected_status:
            problem(where, f"{bucket} requires status {expected_status}")
        if effective and as_of:
            if bucket in {"recent-term-expiry", "fee-lapse-lead", "older-expiry"} and effective >= as_of:
                problem(where, "expired date must precede as_of; today is not assumed elapsed")
            if bucket in {"recent-term-expiry", "fee-lapse-lead"} and start and end and not start <= effective <= end:
                problem(where, "effective end date is outside the recent window")
            if bucket == "older-expiry" and start and effective >= start:
                problem(where, "older-expiry must precede window_start")
            if bucket == "upcoming-expiry" and (effective < as_of or (future_end and effective > future_end)):
                problem(where, "upcoming date is outside the requested future window")
        if bucket == "upcoming-expiry" and upcoming is not True:
            problem(where, "upcoming list was not requested in scope")
        if item.get("shortlisted") is True:
            if bucket != "recent-term-expiry":
                problem(where, "shortlisted records must be supported recent term expirations")
            if not text(item.get("claims_summary")) or not any(isinstance(s.get("kind"), str) and s["kind"] in CLAIM_DOCUMENTS for s in refs["claims_sources"]):
                problem(where, "shortlist requires claims review with patent-document evidence")
            if family != "searched" or not text(item.get("family_notes")):
                problem(where, "shortlist requires an initial family search with findings/limits")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Cannot read candidate ledger: {exc}", file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("Candidate ledger failed consistency checks:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    count = len(data["candidates"])
    shortlisted = sum(c.get("shortlisted") is True for c in data["candidates"])
    print(f"Record checks passed: {count} candidate(s), {shortlisted} shortlisted.")
    print("This does not verify source content, patent status, or freedom to operate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
