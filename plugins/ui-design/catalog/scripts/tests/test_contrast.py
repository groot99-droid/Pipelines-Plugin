#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the WCAG 2.2 contrast gate (contrast.py).

Stdlib-only (unittest, not pytest) to match test_core.py -- this project ships
with zero external dependencies.

Run with:
    python -m unittest discover -s catalog/scripts/tests -v
or directly:
    python catalog/scripts/tests/test_contrast.py
"""

import csv
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from contrast import (  # noqa: E402
    NON_TEXT_MINIMUM,
    TEXT_MINIMUM,
    advisories,
    contrast_ratio,
    evaluate_palette,
    failures,
    format_report,
    relative_luminance,
)
from core import DATA_DIR  # noqa: E402

# colors.csv header -> design system colors dict key
CSV_TO_KEY = {
    "Primary": "primary", "On Primary": "on_primary",
    "Secondary": "secondary", "On Secondary": "on_secondary",
    "Accent": "accent", "On Accent": "on_accent",
    "Background": "background", "Foreground": "foreground",
    "Card": "card", "Card Foreground": "card_foreground",
    "Muted": "muted", "Muted Foreground": "muted_foreground",
    "Border": "border", "Destructive": "destructive",
    "On Destructive": "on_destructive", "Ring": "ring",
}


class TestPrimitives(unittest.TestCase):
    def test_luminance_extremes(self):
        self.assertAlmostEqual(relative_luminance("#FFFFFF"), 1.0, places=6)
        self.assertAlmostEqual(relative_luminance("#000000"), 0.0, places=6)

    def test_shorthand_hex_expands(self):
        self.assertAlmostEqual(relative_luminance("#FFF"), 1.0, places=6)

    def test_malformed_returns_none_rather_than_raising(self):
        # Generation must survive a single bad CSV cell.
        for value in ("", None, "#GGGGGG", "#12345", "nope"):
            self.assertIsNone(relative_luminance(value))

    def test_contrast_ratio_is_symmetric_and_bounded(self):
        self.assertAlmostEqual(contrast_ratio("#000", "#FFF"), 21.0, places=4)
        self.assertAlmostEqual(contrast_ratio("#FFF", "#000"), 21.0, places=4)
        self.assertAlmostEqual(contrast_ratio("#FFF", "#FFF"), 1.0, places=4)

    def test_contrast_ratio_none_when_either_side_invalid(self):
        self.assertIsNone(contrast_ratio("#000", "bogus"))
        self.assertIsNone(contrast_ratio("bogus", "#000"))


class TestEvaluatePalette(unittest.TestCase):
    def test_missing_colors_are_skipped_not_failed(self):
        # A palette with no `destructive` has nothing to check there - that is
        # not the same as failing.
        report = evaluate_palette({"foreground": "#000", "background": "#FFF"})
        pairs = {entry["pair"] for entry in report}
        self.assertIn("foreground-on-background", pairs)
        self.assertNotIn("on-destructive-on-destructive", pairs)

    def test_unparseable_color_is_skipped(self):
        report = evaluate_palette({"foreground": "not-a-color", "background": "#FFF"})
        self.assertEqual(report, [])

    def test_empty_input_is_safe(self):
        self.assertEqual(evaluate_palette({}), [])
        self.assertEqual(evaluate_palette(None), [])

    def test_text_failure_is_enforceable(self):
        report = evaluate_palette({"on_accent": "#FFFFFF", "accent": "#FFFF00"})
        self.assertEqual([e["pair"] for e in failures(report)],
                         ["on-accent-on-accent"])
        self.assertEqual(advisories(report), [])

    def test_non_text_failure_is_advisory_only(self):
        report = evaluate_palette({"border": "#F3F4F6", "background": "#FFFFFF"})
        self.assertEqual(failures(report), [])
        self.assertEqual([e["pair"] for e in advisories(report)],
                         ["border-on-background"])

    def test_thresholds_are_applied_per_pair_kind(self):
        report = evaluate_palette({
            "foreground": "#767676", "background": "#FFFFFF",  # ~4.54:1
            "border": "#767676",                               # same ratio, non-text
        })
        by_pair = {e["pair"]: e for e in report}
        self.assertEqual(by_pair["foreground-on-background"]["wcag22Minimum"], TEXT_MINIMUM)
        self.assertEqual(by_pair["border-on-background"]["wcag22Minimum"], NON_TEXT_MINIMUM)
        # One ratio, two verdicts - the border clears 3:1 while the text barely
        # clears 4.5:1.
        self.assertTrue(by_pair["foreground-on-background"]["passes"])
        self.assertTrue(by_pair["border-on-background"]["passes"])


class TestFormatReport(unittest.TestCase):
    def test_marks_distinguish_fail_from_warn(self):
        report = evaluate_palette({
            "on_accent": "#FFFFFF", "accent": "#FFFF00",
            "border": "#F3F4F6", "background": "#FFFFFF",
            "foreground": "#000000",
        })
        text = format_report(report)
        self.assertIn("[FAIL]", text)   # text pair
        self.assertIn("[WARN]", text)   # non-text pair
        self.assertIn("[PASS]", text)

    def test_empty_report_is_empty_string(self):
        self.assertEqual(format_report([]), "")


class TestShippedPalettes(unittest.TestCase):
    """The catalog itself must stay clean.

    This is the regression that matters: if someone adds a palette to
    colors.csv whose body text fails 4.5:1, it should be caught here rather
    than shipped. Non-text shortfalls are deliberately not asserted on -- 173
    of 192 palettes use a sub-3:1 border by design.
    """

    @classmethod
    def setUpClass(cls):
        with open(DATA_DIR / "colors.csv", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_catalog_is_not_empty(self):
        self.assertGreater(len(self.rows), 100)

    def test_every_shipped_palette_passes_text_contrast(self):
        broken = []
        for row in self.rows:
            colors = {key: row.get(header, "")
                      for header, key in CSV_TO_KEY.items()}
            for entry in failures(evaluate_palette(colors)):
                broken.append(
                    f"{row.get('Product Type', '?')}: {entry['pair']} "
                    f"= {entry['ratio']}:1"
                )
        self.assertEqual(broken, [], "palettes below WCAG 2.2 text minimum:\n"
                                     + "\n".join(broken))


if __name__ == "__main__":
    unittest.main(verbosity=2)
