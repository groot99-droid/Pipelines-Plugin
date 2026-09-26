#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for maintenance/harvest-site-tokens.py (maintainer tooling).

These live in maintenance/tests/, NOT in catalog/scripts/tests/, because
catalog/ is the stdlib-only half of the tool and the skill runs only what is
in it. A test importing a module that half does not carry would break its own
test run.

Stdlib-only (unittest), matching the rest of the project.

Run with:
    python -m unittest discover -s maintenance/tests -v
"""

import importlib.util
import sys
import unittest
from pathlib import Path

# The module has a hyphen in its name, so it cannot be imported normally.
_MODULE_PATH = Path(__file__).resolve().parent.parent / "harvest-site-tokens.py"
_spec = importlib.util.spec_from_file_location("harvest_site_tokens", _MODULE_PATH)
harvest = importlib.util.module_from_spec(_spec)
sys.modules["harvest_site_tokens"] = harvest
_spec.loader.exec_module(harvest)


def capture(**overrides):
    """A capture that passes validation, so each test can break one thing."""
    base = {
        "url": "https://example.com",
        "title": "Example",
        "viewport": {"w": 1440, "h": 900},
        "elementsSampled": 2000,
        "elementsSkipped": 100,
        "iframes": 0,
        "backgroundsByArea": [{"value": f"#00000{i}", "weight": 100 - i}
                              for i in range(6)],
        "textColorsByGlyphs": [{"value": "#111827", "weight": 5000}],
        "borderColors": [],
        "typeSteps": [{"value": "16px|400|24px", "weight": 100}],
        "spacing": [{"value": "8px", "weight": 10}],
        "radii": [],
        "families": [{"value": "Inter", "weight": 900}],
    }
    base.update(overrides)
    return base


class TestValidationGuards(unittest.TestCase):
    """Each guard corresponds to a failure mode hit against a real site."""

    def test_clean_capture_has_no_problems(self):
        self.assertEqual(harvest.validate(capture()), [])

    def test_storybook_shell_is_rejected(self):
        # primer.style: tokens live in an iframe, so the outer document yields
        # almost no color but still yields a plausible type scale.
        problems = harvest.validate(capture(
            iframes=3,
            backgroundsByArea=[{"value": "#FFFFFF", "weight": 10}],
        ))
        self.assertTrue(any("iframe" in p for p in problems))

    def test_dropped_colors_are_caught(self):
        # tailwindcss.com with an rgb-only parser: one background on a page of
        # hundreds of swatches.
        problems = harvest.validate(capture(
            backgroundsByArea=[{"value": "#FFFFFF", "weight": 1}]))
        self.assertTrue(any("distinct background" in p for p in problems))

    def test_unrendered_page_is_caught(self):
        problems = harvest.validate(capture(elementsSampled=12))
        self.assertTrue(any("elements sampled" in p for p in problems))

    def test_missing_type_scale_is_caught(self):
        self.assertTrue(any("type steps" in p
                            for p in harvest.validate(capture(typeSteps=[]))))

    def test_zero_viewport_is_advisory(self):
        problems = harvest.validate(capture(viewport={"w": 0, "h": 0}))
        self.assertTrue(any("viewport" in p for p in problems))


class TestRadiusNormalization(unittest.TestCase):
    def test_pill_radius_is_not_recorded_as_a_measurement(self):
        # calc(infinity)/9999px resolves to an enormous used value.
        result = harvest.normalize_radii([
            {"value": "1.67772e+07px", "weight": 6},
            {"value": "8px", "weight": 18},
        ])
        self.assertEqual(result["pillUses"], 6)
        self.assertEqual(result["measured"], [(8.0, 18)])

    def test_measured_radii_are_sorted(self):
        result = harvest.normalize_radii([
            {"value": "12px", "weight": 1}, {"value": "4px", "weight": 1}])
        self.assertEqual([v for v, _ in result["measured"]], [4.0, 12.0])

    def test_empty_input(self):
        self.assertEqual(harvest.normalize_radii([]),
                         {"measured": [], "pillUses": 0})


class TestSpacingInference(unittest.TestCase):
    def test_clean_8px_scale(self):
        result = harvest.infer_spacing_base([
            {"value": "8px", "weight": 10}, {"value": "16px", "weight": 10},
            {"value": "32px", "weight": 10},
        ])
        self.assertEqual(result["base"], 8)
        self.assertEqual(result["share"], 1.0)
        self.assertEqual(result["offScale"], [])

    def test_em_derived_values_are_reported_not_rounded_away(self):
        # A site mixing 4px steps with em-derived 11.2px does not have a 4px
        # scale; recording one would be wrong.
        result = harvest.infer_spacing_base([
            {"value": "4px", "weight": 40}, {"value": "16px", "weight": 20},
            {"value": "11.2px", "weight": 30},
        ])
        self.assertIn(11.2, result["offScale"])
        self.assertLess(result["share"], 1.0)

    def test_tie_resolves_to_largest_base(self):
        # 8/16/32 are multiples of 2, 4 and 8 alike. Reporting "2px" for a
        # clean 8px scale is a wrong characterization, not a cautious one.
        result = harvest.infer_spacing_base([
            {"value": "8px", "weight": 1}, {"value": "16px", "weight": 1},
            {"value": "32px", "weight": 1}, {"value": "24px", "weight": 1},
        ])
        self.assertEqual(result["base"], 8)

    def test_genuine_4px_scale_is_not_promoted_to_8(self):
        result = harvest.infer_spacing_base([
            {"value": "4px", "weight": 10}, {"value": "12px", "weight": 10},
            {"value": "20px", "weight": 10},
        ])
        self.assertEqual(result["base"], 4)

    def test_no_spacing_returns_none(self):
        self.assertIsNone(harvest.infer_spacing_base([]))


class TestFontVarDetection(unittest.TestCase):
    def test_css_var_names_are_not_mistaken_for_families(self):
        # tailwindcss.com resolves font-family to the var name itself.
        for name in ("plexMono", "inter", "geistSans"):
            self.assertTrue(harvest.looks_like_css_var(name), name)

    def test_real_family_names_pass_through(self):
        for name in ("Inter", "Geist", "IBM Plex Mono", "Cormorant Garamond"):
            self.assertFalse(harvest.looks_like_css_var(name), name)

    def test_empty_is_not_a_var(self):
        self.assertFalse(harvest.looks_like_css_var(""))


class TestTypeSummary(unittest.TestCase):
    def test_computes_line_height_ratio(self):
        rows = harvest.summarize_type([{"value": "16px|400|24px", "weight": 5}])
        self.assertEqual(rows[0]["ratio"], 1.5)

    def test_sorted_by_usage(self):
        rows = harvest.summarize_type([
            {"value": "12px|400|16px", "weight": 5},
            {"value": "16px|400|24px", "weight": 99},
        ])
        self.assertEqual(rows[0]["size"], "16px")


class TestReport(unittest.TestCase):
    def test_untrusted_capture_is_flagged_loudly(self):
        text = harvest.report(capture(iframes=3, backgroundsByArea=[
            {"value": "#FFF", "weight": 1}]))
        self.assertIn("CAPTURE NOT TRUSTED", text)

    def test_clean_capture_is_not_flagged(self):
        self.assertNotIn("CAPTURE NOT TRUSTED", harvest.report(capture()))

    def test_report_runs_on_a_sparse_capture_without_crashing(self):
        harvest.report({"url": "https://x.test"})


class TestNotShipped(unittest.TestCase):
    """The harvest tool must never reach catalog/scripts/, or the skill's
    stated 'no network access' contract becomes false."""

    def test_tool_is_absent_from_the_stdlib_only_half(self):
        scripts = Path(__file__).resolve().parents[2] / "catalog" / "scripts"
        self.assertTrue(scripts.is_dir(), f"catalog/scripts not found at {scripts}")
        for name in ("harvest-site-tokens.py", "harvest_site_tokens.py"):
            self.assertFalse((scripts / name).exists(),
                             f"harvest tool leaked into {scripts}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
