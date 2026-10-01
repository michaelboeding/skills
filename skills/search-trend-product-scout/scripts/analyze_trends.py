#!/usr/bin/env python3
"""Describe one regular, 0-100 Google Trends CSV; never fetch or rank products."""

import argparse
import csv
from datetime import date, timedelta
import hashlib
import io
import json
import math
from pathlib import Path
import re
from statistics import mean


HEADERS = {"month": "monthly", "week": "weekly", "day": "daily", "date": "auto"}
DEFAULT_PERIODS = {"monthly": 3, "weekly": 13, "daily": 90}
YEAR_PERIODS = {"monthly": 12, "weekly": 52, "daily": 365}
MIN_BASELINE = 5.0


def iso_date(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Use an ISO date: YYYY-MM-DD")
    return date.fromisoformat(value)


def shift_period(start, frequency, count=1):
    if frequency == "monthly":
        month_number = start.year * 12 + start.month - 1 + count
        return date(month_number // 12, month_number % 12 + 1, 1)
    return start + timedelta(days=count * (7 if frequency == "weekly" else 1))


def prior_year(start, frequency):
    if frequency == "monthly":
        return shift_period(start, frequency, -12)
    if frequency == "weekly":
        return start - timedelta(weeks=52)
    try:
        return start.replace(year=start.year - 1)
    except ValueError:
        return None  # Leap days have no exact prior-year match.


def parse_value(raw):
    raw = raw.strip()
    if raw.lower() in ("", "na", "n/a"):
        return None, "missing"
    if raw == "<1":
        return None, "censored"
    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"Unsupported index {raw!r}; expected 0-100, <1, or blank") from None
    if not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError(f"Index must be finite and within 0-100: {raw!r}")
    return value, "observed"


def read_export(content, frequency="auto"):
    rows = [row for row in csv.reader(io.StringIO(content)) if any(cell.strip() for cell in row)]
    header_index = next((i for i, row in enumerate(rows)
                         if row[0].strip().lower() in HEADERS), None)
    if header_index is None:
        raise ValueError("No Month/Week/Day/Date header found; use an English interest-over-time CSV")
    header = [cell.strip() for cell in rows[header_index]]
    if len(header) < 2 or any(not label for label in header):
        raise ValueError("Header needs a date column and nonempty term labels")
    if len({label.casefold() for label in header}) != len(header):
        raise ValueError("Duplicate column labels")
    partial_index = next((i for i, label in enumerate(header) if label.lower() == "ispartial"), None)
    term_indices = [i for i in range(1, len(header)) if i != partial_index]
    if not term_indices:
        raise ValueError("No term columns found")
    parsed = []
    monthly_format = []
    for line, row in enumerate(rows[header_index + 1:], start=header_index + 2):
        if len(row) != len(header):
            raise ValueError(f"Row {line}: expected {len(header)} columns, got {len(row)}")
        raw_date = row[0].strip()
        is_month = bool(re.fullmatch(r"\d{4}-\d{2}", raw_date))
        start = iso_date(raw_date + "-01" if is_month else raw_date)
        monthly_format.append(is_month)
        partial_raw = row[partial_index].strip().lower() if partial_index is not None else "false"
        if partial_raw not in ("", "true", "false", "1", "0"):
            raise ValueError(f"Row {line}: invalid isPartial value")
        parsed.append({"start": start, "partial": partial_raw in ("true", "1"),
                       "values": [parse_value(row[i]) for i in term_indices]})
    if not parsed:
        raise ValueError("No data rows found")
    dates = [row["start"] for row in parsed]
    if any(right <= left for left, right in zip(dates, dates[1:])):
        raise ValueError("Dates must increase without duplicates")
    if frequency == "auto":
        frequency = HEADERS[header[0].lower()]
        if frequency == "auto":
            if all(monthly_format) or (len(dates) > 1 and all(d.day == 1 for d in dates)
                                      and all(shift_period(a, "monthly") == b
                                              for a, b in zip(dates, dates[1:]))):
                frequency = "monthly"
            elif len(dates) > 1:
                differences = {(b - a).days for a, b in zip(dates, dates[1:])}
                frequency = {frozenset({1}): "daily", frozenset({7}): "weekly"}.get(frozenset(differences))
            else:
                frequency = None
    if frequency not in YEAR_PERIODS:
        raise ValueError("Cannot infer a regular frequency; use --frequency for an ambiguous Date series")
    if frequency == "monthly" and any(d.day != 1 for d in dates):
        raise ValueError("Monthly dates must be period starts (first day of the month)")
    if frequency != "monthly" and any(monthly_format):
        raise ValueError("Weekly/daily series require YYYY-MM-DD dates")
    if any(shift_period(a, frequency) != b for a, b in zip(dates, dates[1:])):
        raise ValueError("Series has gaps or mixed frequency; preserve missing rows rather than silently skipping them")
    return frequency, [header[i] for i in term_indices], parsed


def describe_window(dates, complete, term_index, frequency):
    valid_dates = [d for d in dates if d is not None]
    values = [complete[d]["values"][term_index][0]
              if d in complete else None for d in dates]
    return {"start": min(valid_dates).isoformat() if valid_dates else None,
            "end_exclusive": shift_period(max(valid_dates), frequency).isoformat() if valid_dates else None,
            "expected_periods": len(dates),
            "observed_periods": sum(v is not None for v in values),
            "mean_index": mean(values) if values and all(v is not None for v in values) else None}


def analyze(path, as_of, frequency="auto", periods=None):
    path = Path(path)
    raw = path.read_bytes()
    frequency, labels, rows = read_export(raw.decode("utf-8-sig"), frequency)
    periods = DEFAULT_PERIODS[frequency] if periods is None else periods
    if not isinstance(periods, int) or not 1 <= periods <= YEAR_PERIODS[frequency]:
        raise ValueError(f"periods must be 1-{YEAR_PERIODS[frequency]} for {frequency} data")
    complete = {row["start"]: row for row in rows
                if not row["partial"] and shift_period(row["start"], frequency) <= as_of}
    if not complete:
        raise ValueError("No complete periods on or before the as-of date")
    last = max(complete)
    recent = [shift_period(last, frequency, i) for i in range(1 - periods, 1)]
    baseline = [prior_year(d, frequency) for d in recent]
    warnings = ["Relative, sampled interest indices are not search counts or sales.",
                "Compare numeric levels only within compatible, jointly scaled data.",
                "Source URL and filter settings must be recorded separately."]
    if len(complete) < len(rows):
        warnings.append(f"Excluded {len(rows) - len(complete)} partial or unfinished periods.")
    if shift_period(last, frequency, 2) <= as_of:
        warnings.append("History ends more than one interval before as-of; treat it as historical, not current momentum.")
    if frequency == "weekly":
        warnings.append("Prior-year matching uses 52 weeks (364 days); seasonal month grouping uses period starts.")
    if len({d.year for d in complete}) < 2:
        warnings.append("Less than two calendar years are represented; recurring seasonality is unconfirmed.")
    results = []
    for term_index, label in enumerate(labels):
        current = describe_window(recent, complete, term_index, frequency)
        previous = describe_window(baseline, complete, term_index, frequency)
        reason = None
        if current["mean_index"] is None or previous["mean_index"] is None:
            reason = "incomplete-or-missing-pairs"
        elif previous["mean_index"] == 0:
            reason = "zero-baseline"
        elif previous["mean_index"] < MIN_BASELINE:
            reason = "small-baseline-below-5-index-points"
        growth = ((current["mean_index"] / previous["mean_index"] - 1) * 100
                  if reason is None else None)
        values = [row["values"][term_index] for row in complete.values()]
        months = {}
        for month in range(1, 13):
            month_rows = [(d, row["values"][term_index]) for d, row in complete.items() if d.month == month]
            observed = [value for _, (value, _) in month_rows if value is not None]
            months[str(month)] = {"mean_index": mean(observed) if observed else None,
                                  "observed_periods": len(observed),
                                  "total_periods": len(month_rows),
                                  "years_observed": len({d.year for d, (v, _) in month_rows if v is not None})}
        term_warnings = []
        if any(state != "observed" for _, state in values):
            term_warnings.append("Missing/censored values are retained; month means use observed values only.")
        if any(v == 0 for v, _ in values):
            term_warnings.append("Zero indices can mean insufficient search data, not absence of demand.")
        if any(item["years_observed"] < 2 for item in months.values()):
            term_warnings.append("Some calendar months lack observations from two years; seasonal coverage is uneven.")
        results.append({"label": label, "coverage": {
            "complete_periods": len(values), "observed_periods": sum(v is not None for v, _ in values),
            "missing_periods": sum(state == "missing" for _, state in values),
            "censored_periods": sum(state == "censored" for _, state in values),
            "zero_periods": sum(v == 0 for v, _ in values)},
            "recent_window": current, "prior_year_window": previous,
            "relative_interest_change_pct": growth, "change_unavailable_reason": reason,
            "descriptive_month_means": months, "warnings": term_warnings})
    return {"schema_version": 1, "input_file": str(path.resolve()),
            "input_sha256": hashlib.sha256(raw).hexdigest(), "as_of": as_of.isoformat(),
            "frequency": frequency, "recent_periods": periods, "units": "relative index (0-100)",
            "history_start": min(complete).isoformat(),
            "history_end_exclusive": shift_period(last, frequency).isoformat(),
            "excluded_periods": len(rows) - len(complete), "warnings": warnings, "series": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--as-of", required=True, help="Research date in YYYY-MM-DD format")
    parser.add_argument("--frequency", choices=("auto", "monthly", "weekly", "daily"), default="auto")
    parser.add_argument("--periods", type=int, help="Recent periods to compare (default depends on frequency)")
    parser.add_argument("--output", type=Path, help="JSON path; omit to print JSON")
    args = parser.parse_args()
    try:
        if args.output and (args.output.resolve() == args.csv.resolve()
                            or (args.output.exists() and args.csv.exists() and args.output.samefile(args.csv))):
            raise ValueError("Output must not overwrite the raw input CSV")
        result = analyze(args.csv, iso_date(args.as_of), args.frequency, args.periods)
        output = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except (ValueError, OSError, csv.Error) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
