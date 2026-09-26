#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the DTCG token exporter (tokens.py).

Stdlib-only (unittest, not pytest) to match test_core.py -- this project ships
with zero external dependencies.

Run with:
    python -m unittest discover -s catalog/scripts/tests -v
or directly:
    python catalog/scripts/tests/test_tokens.py
"""

import json
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from design_system import generate_design_system  # noqa: E402
from tokens import (  # noqa: E402
    EXTENSION_KEY,
    _spring_params,
    _first_duration_ms,
    _px_to_rem,
    _token_name,
    dumps_dtcg,
    to_dtcg,
)


SAMPLE = {
    "project_name": "Sample",
    "category": "SaaS Dashboard",
    "colors": {
        "primary": "#2563EB",
        "on_primary": "#FFFFFF",
        "background": "#FFFFFF",
        "foreground": "#111827",
        # Deliberately short contrast, to prove the report is computed rather
        # than assumed to pass.
        "accent": "#FFFF00",
        "on_accent": "#FFFFFF",
    },
    "typography": {"heading": "Inter", "body": "Inter"},
    "style": {"id": "minimalism-and-swiss-style", "name": "Minimalism"},
    "pattern": {"name": "Hero-Centric"},
    "spacing_scale": None,
    "motion_snippet": {},
    "dials": {},
    "source_identities": {},
    "anti_patterns": "",
}


class TestHelpers(unittest.TestCase):
    def test_token_name_strips_css_prefix(self):
        self.assertEqual(_token_name("--color-on-primary"), "on-primary")
        self.assertEqual(_token_name("--color-primary"), "primary")

    def test_px_to_rem(self):
        self.assertEqual(_px_to_rem("16px"), "1rem")
        self.assertEqual(_px_to_rem("4px"), "0.25rem")
        self.assertIsNone(_px_to_rem("9999"))
        self.assertIsNone(_px_to_rem("auto"))

    def test_duration_range_takes_lower_bound(self):
        # "300-450ms" must not yield 450ms: the unit is attached to the upper
        # bound, so a naive \d+ms search picks the wrong number.
        self.assertEqual(_first_duration_ms("300-450ms"), "300ms")
        self.assertEqual(_first_duration_ms("150-200ms"), "150ms")

    def test_duration_single_and_seconds(self):
        self.assertEqual(_first_duration_ms("250ms"), "250ms")
        self.assertEqual(_first_duration_ms("1.2s"), "1200ms")

    def test_duration_scrub_driven_is_none(self):
        self.assertIsNone(_first_duration_ms("tied to scroll position"))
        self.assertIsNone(_first_duration_ms(""))
        self.assertIsNone(_first_duration_ms(None))


class TestDtcgShape(unittest.TestCase):
    def setUp(self):
        self.doc = to_dtcg(SAMPLE)

    def test_every_token_declares_type_and_value(self):
        """Walk the tree; any leaf with $value must also carry $type."""
        def walk(node, path=""):
            if not isinstance(node, dict):
                return
            if "$value" in node:
                self.assertIn("$type", node, f"{path} has $value but no $type")
                return
            for key, child in node.items():
                if key.startswith("$"):
                    continue
                walk(child, f"{path}.{key}")

        walk(self.doc)

    def test_color_tokens_present(self):
        self.assertEqual(self.doc["color"]["primary"]["$value"], "#2563EB")
        self.assertEqual(self.doc["color"]["primary"]["$type"], "color")

    def test_empty_color_values_are_omitted(self):
        # SAMPLE defines no "secondary"; it must not appear as an empty token.
        self.assertNotIn("secondary", self.doc["color"])

    def test_font_family_is_a_list_with_fallback(self):
        value = self.doc["font"]["family"]["heading"]["$value"]
        self.assertIsInstance(value, list)
        self.assertEqual(value[0], "Inter")
        self.assertIn("sans-serif", value)

    def test_spacing_defaults_to_mid_density_when_no_dial(self):
        self.assertEqual(self.doc["space"]["md"]["$value"], "16px")
        self.assertEqual(
            self.doc["space"]["md"]["$extensions"][EXTENSION_KEY]["rem"], "1rem"
        )

    def test_radius_and_shadow_always_emitted(self):
        self.assertIn("full", self.doc["radius"])
        self.assertEqual(self.doc["shadow"]["sm"]["$type"], "shadow")

    def test_motion_omitted_when_no_snippet(self):
        self.assertNotIn("motion", self.doc)

    def test_serializes_to_json(self):
        json.loads(dumps_dtcg(SAMPLE))


class TestContrastReport(unittest.TestCase):
    def setUp(self):
        self.report = to_dtcg(SAMPLE)["$extensions"][EXTENSION_KEY]["contrast"]
        self.by_pair = {entry["pair"]: entry for entry in self.report}

    def test_reports_a_passing_pair(self):
        entry = self.by_pair["foreground-on-background"]
        self.assertTrue(entry["passes"])
        self.assertGreater(entry["ratio"], 4.5)

    def test_reports_a_failing_pair_rather_than_hiding_it(self):
        # White on yellow is ~1.07:1. The exporter must report the failure.
        entry = self.by_pair["on-accent-on-accent"]
        self.assertFalse(entry["passes"])
        self.assertLess(entry["ratio"], 4.5)

    def test_pairs_with_missing_colors_are_skipped(self):
        self.assertNotIn("on-destructive-on-destructive", self.by_pair)


class TestMotionTokens(unittest.TestCase):
    def test_known_gsap_ease_becomes_cubic_bezier(self):
        doc = to_dtcg({
            **SAMPLE,
            "motion_snippet": {
                "Duration": "200-300ms",
                "Easing": "power2.out",
                "Category": "Hover",
            },
        })
        easing = doc["motion"]["easing"]["default"]
        self.assertEqual(easing["$type"], "cubicBezier")
        self.assertEqual(len(easing["$value"]), 4)
        self.assertEqual(doc["motion"]["duration"]["default"]["$value"], "200ms")

    def test_unmapped_ease_is_flagged_not_fabricated(self):
        doc = to_dtcg({
            **SAMPLE,
            "motion_snippet": {"Duration": "400ms", "Easing": "rough.custom(9)"},
        })
        easing = doc["motion"]["easing"]["default"]
        self.assertNotEqual(easing["$type"], "cubicBezier")
        self.assertTrue(easing["$extensions"][EXTENSION_KEY]["unmapped"])

    def test_scrub_driven_row_emits_no_duration(self):
        doc = to_dtcg({
            **SAMPLE,
            "motion_snippet": {
                "Duration": "tied to scroll position",
                "Easing": "none",
            },
        })
        self.assertNotIn("duration", doc.get("motion", {}))


class TestEndToEnd(unittest.TestCase):
    """The exporter must work against a real generated design system, not
    only the hand-built SAMPLE fixture."""

    def test_generate_with_dtcg_format(self):
        result = generate_design_system(
            "SaaS analytics dashboard", "Acme", output_format="dtcg",
            motion=5, density=8,
        )
        doc = json.loads(result["text"])
        self.assertIn("color", doc)
        self.assertIn("space", doc)
        # density=8 is the dense tier
        self.assertEqual(doc["space"]["md"]["$value"], "8px")
        ext = doc["$extensions"][EXTENSION_KEY]
        self.assertEqual(ext["dials"]["density"], 8)
        self.assertTrue(ext["contrast"], "expected a non-empty contrast report")



class TestSpringTokens(unittest.TestCase):
    def test_parses_authored_spring_string(self):
        self.assertEqual(
            _spring_params("stiffness: 280, damping: 18, mass: 1 (overshoots)"),
            {"stiffness": 280.0, "damping": 18.0, "mass": 1.0},
        )

    def test_parses_fractional_mass(self):
        self.assertEqual(
            _spring_params("stiffness: 200, damping: 28, mass: 1.1 (heavier)")["mass"],
            1.1,
        )

    def test_non_spring_rows_yield_none(self):
        # motion.csv marks scrub/loop/timer rows as not spring-shaped; those
        # must not produce a plausible-looking token.
        for text in (
            "n/a - scrub-driven; position is bound to scroll, not to a physics model",
            "n/a - continuous loop; use a duration, not a spring",
            "n/a - timer-driven; advance is a discrete step, not an animation",
            "", None,
        ):
            self.assertIsNone(_spring_params(text))

    def test_spring_emitted_under_extensions_not_as_cubic_bezier(self):
        doc = to_dtcg({
            **SAMPLE,
            "motion_snippet": {
                "Duration": "300-450ms",
                "Easing": "back.out(1.4)",
                "Spring Params": "stiffness: 280, damping: 18, mass: 1",
                "Reduced Motion": "@media (prefers-reduced-motion: reduce) { animation: none }",
            },
        })
        spring = doc["motion"]["spring"]["default"]
        self.assertNotEqual(spring["$type"], "cubicBezier")
        self.assertEqual(
            spring["$extensions"][EXTENSION_KEY]["spring"]["damping"], 18.0
        )

    def test_reduced_motion_is_emitted(self):
        doc = to_dtcg({
            **SAMPLE,
            "motion_snippet": {
                "Duration": "200ms", "Easing": "power2.out",
                "Reduced Motion": "@media (prefers-reduced-motion: reduce) { transition: none }",
            },
        })
        self.assertIn("reduced-motion", doc["motion"]["reducedMotion"]["default"]["$value"])

    def test_no_spring_group_when_row_is_not_spring_shaped(self):
        doc = to_dtcg({
            **SAMPLE,
            "motion_snippet": {
                "Duration": "tied to scroll position",
                "Easing": "none",
                "Spring Params": "n/a - scrub-driven; bound to scroll",
            },
        })
        self.assertNotIn("spring", doc.get("motion", {}))


class TestMotionCsvContract(unittest.TestCase):
    """Every motion.csv row must carry the three new columns with real values."""

    @classmethod
    def setUpClass(cls):
        import csv
        from core import DATA_DIR
        with open(DATA_DIR / "motion.csv", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_columns_present_and_populated(self):
        for row in self.rows:
            for column in ("Spring Params", "CSS Snippet", "Reduced Motion"):
                with self.subTest(no=row["No"], column=column):
                    self.assertTrue(row.get(column, "").strip(),
                                    f"row {row['No']} has empty {column}")

    def test_every_row_states_a_reduced_motion_fallback(self):
        for row in self.rows:
            self.assertIn("prefers-reduced-motion", row["Reduced Motion"],
                          f"row {row['No']} lacks an explicit opt-out")

    def test_spring_params_either_parse_or_say_why_not(self):
        for row in self.rows:
            raw = row["Spring Params"]
            with self.subTest(no=row["No"]):
                if _spring_params(raw) is None:
                    # Must explain itself rather than being blank or vague.
                    self.assertTrue(raw.lower().startswith("n/a"),
                                    f"row {row['No']}: unparseable and unexplained: {raw!r}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
