#!/usr/bin/env python3
"""Synthetic behavior checks; no live searches or demand validation."""

from datetime import date, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analyze_trends import analyze, read_export, shift_period


class TrendAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "trends.csv"

    def write(self, text):
        self.path.write_text(text, encoding="utf-8")
        return self.path

    def monthly(self, value, partial=False):
        rows = ["Category: All categories", "", "Month,gear" + (",isPartial" if partial else "")]
        start = date(2024, 1, 1)
        for i in range(34):
            d = shift_period(start, "monthly", i)
            rows.append(f"{d:%Y-%m},{value(d)}" + (f",{str(d == date(2026, 10, 1)).lower()}" if partial else ""))
        return self.write("\n".join(rows) + "\n")

    def test_monthly_growth_matches_same_complete_season(self):
        self.monthly(lambda d: 30 if d.year == 2026 else 20)
        result = analyze(self.path, date(2026, 10, 1))
        series = result["series"][0]
        self.assertEqual(result["excluded_periods"], 1)
        self.assertEqual(series["recent_window"]["start"], "2026-07-01")
        self.assertEqual(series["prior_year_window"]["start"], "2025-07-01")
        self.assertAlmostEqual(series["relative_interest_change_pct"], 50)

    def test_repeated_fall_peak_is_not_year_over_year_growth(self):
        self.monthly(lambda d: 80 if d.month in (7, 8, 9) else 20)
        series = analyze(self.path, date(2026, 10, 1))["series"][0]
        self.assertEqual(series["relative_interest_change_pct"], 0)
        self.assertEqual(series["descriptive_month_means"]["8"]["mean_index"], 80)

    def test_missing_censored_and_zero_are_distinct(self):
        self.monthly(lambda d: "" if d == date(2026, 7, 1) else "<1" if d == date(2026, 8, 1)
                     else 0 if d == date(2026, 9, 1) else 20)
        series = analyze(self.path, date(2026, 10, 1))["series"][0]
        self.assertEqual(series["coverage"]["missing_periods"], 1)
        self.assertEqual(series["coverage"]["censored_periods"], 1)
        self.assertEqual(series["coverage"]["zero_periods"], 1)
        self.assertIsNone(series["recent_window"]["mean_index"])
        self.assertIsNone(series["relative_interest_change_pct"])

    def test_small_and_zero_baselines_do_not_create_growth_claim(self):
        for base, reason in ((0, "zero-baseline"), (2, "small-baseline-below-5-index-points")):
            with self.subTest(base=base):
                self.monthly(lambda d: 50 if d.year == 2026 else base)
                series = analyze(self.path, date(2026, 10, 1))["series"][0]
                self.assertIsNone(series["relative_interest_change_pct"])
                self.assertEqual(series["change_unavailable_reason"], reason)

    def test_explicit_partial_values_are_excluded(self):
        self.monthly(lambda d: 20, partial=True)
        result = analyze(self.path, date(2026, 11, 1))
        self.assertEqual(result["history_end_exclusive"], "2026-10-01")
        self.assertEqual(result["excluded_periods"], 1)

    def test_internal_partial_does_not_shift_window_to_older_values(self):
        self.monthly(lambda d: 20, partial=True)
        text = self.path.read_text().replace("2026-08,20,false", "2026-08,20,true")
        self.write(text)
        series = analyze(self.path, date(2026, 10, 1))["series"][0]
        self.assertEqual(series["recent_window"]["start"], "2026-07-01")
        self.assertEqual(series["recent_window"]["observed_periods"], 2)
        self.assertIsNone(series["relative_interest_change_pct"])

    def test_weekly_matching_and_unfinished_row(self):
        start = date(2024, 9, 29)
        rows = ["Week,gear"]
        for i in range(105):
            d = start + timedelta(weeks=i)
            rows.append(f"{d},{20 if i < 52 else 30}")
        self.write("\n".join(rows))
        result = analyze(self.path, date(2026, 10, 1))
        series = result["series"][0]
        self.assertEqual(result["excluded_periods"], 1)
        self.assertEqual(series["prior_year_window"]["start"], "2025-06-29")
        self.assertAlmostEqual(series["relative_interest_change_pct"], 50)
        self.assertTrue(any("364 days" in warning for warning in result["warnings"]))

    def test_daily_leap_day_is_not_imputed(self):
        start = date(2023, 2, 28)
        rows = ["Day,gear"]
        for i in range(367):
            rows.append(f"{start + timedelta(days=i)},20")
        self.write("\n".join(rows))
        result = analyze(self.path, date(2024, 3, 1), periods=1)
        series = result["series"][0]
        self.assertEqual(series["recent_window"]["start"], "2024-02-29")
        self.assertIsNone(series["relative_interest_change_pct"])

    def test_irregular_dates_and_duplicate_columns_fail(self):
        invalid = ["Month,gear\n2025-01,20\n2025-03,30\n",
                   "Day,gear\n2025-01-01,20\n2025-01-01,30\n",
                   "Month,gear,gear\n2025-01,20,30\n"]
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(ValueError):
                read_export(text)

    def test_nonfinite_out_of_range_and_invalid_partial_fail(self):
        for raw in ("nan", "inf", "101", "-1", "Breakout"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                read_export(f"Month,gear\n2025-01,{raw}\n")
        with self.assertRaises(ValueError):
            read_export("Month,gear,isPartial\n2025-01,20,maybe\n")

    def test_bom_multiple_series_and_cli_output(self):
        self.write("\ufeffCategory: All categories\n\nMonth,quiet gear,boot drying\n2025-01,20,<1\n")
        output = Path(self.temp.name) / "analysis.json"
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("analyze_trends.py")),
                                 str(self.path), "--as-of", "2025-02-01", "--output", str(output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = json.loads(output.read_text())
        self.assertEqual(len(saved["series"]), 2)
        self.assertEqual(saved["series"][1]["coverage"]["censored_periods"], 1)
        self.assertEqual(len(saved["input_sha256"]), 64)

    def test_cli_preserves_raw_input_and_rejects_invalid_window(self):
        self.write("Month,gear\n2025-01,20\n")
        original = self.path.read_bytes()
        base = [sys.executable, str(Path(__file__).with_name("analyze_trends.py")),
                str(self.path), "--as-of", "2025-02-01"]
        for extra in (["--output", str(self.path)], ["--periods", "0"]):
            result = subprocess.run(base + extra, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
