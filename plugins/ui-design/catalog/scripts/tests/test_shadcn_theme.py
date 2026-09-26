#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the OKLCH conversion and the shadcn/ui theme exporter.

Stdlib-only (unittest, not pytest) to match test_core.py.

Run with:
    python -m unittest discover -s catalog/scripts/tests -v
or directly:
    python catalog/scripts/tests/test_shadcn_theme.py
"""

import re
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from design_system import generate_design_system  # noqa: E402
from oklch import (  # noqa: E402
    format_oklch, hex_to_oklch, hex_to_rgb, oklab_to_hex, oklch_to_hex,
)
from shadcn_theme import LIGHT_MAPPING, to_shadcn_css  # noqa: E402


SAMPLE = {
    "project_name": "Sample",
    "style": {"name": "Minimalism"},
    "colors": {
        "background": "#FFFFFF", "foreground": "#111827",
        "card": "#FFFFFF", "card_foreground": "#111827",
        "primary": "#2563EB", "on_primary": "#FFFFFF",
        "secondary": "#3B82F6", "on_secondary": "#000000",
        "accent": "#F97316", "on_accent": "#000000",
        "muted": "#F3F4F6", "muted_foreground": "#4B5563",
        "destructive": "#DC2626", "on_destructive": "#FFFFFF",
        "border": "#E5E7EB", "ring": "#2563EB",
    },
    "contrast": [],
}


class TestOklchConversion(unittest.TestCase):
    """Verified against published sRGB->OKLCH reference values."""

    REFERENCE = [
        ("#FFFFFF", 1.0000, 0.0000, None),
        ("#000000", 0.0000, 0.0000, None),
        ("#FF0000", 0.6280, 0.2577, 29.23),
        ("#00FF00", 0.8664, 0.2948, 142.50),
        ("#0000FF", 0.4520, 0.3132, 264.05),
        ("#2563EB", 0.5461, 0.2152, 262.88),
        ("#808080", 0.5999, 0.0000, None),
    ]

    def test_matches_reference_values(self):
        for hex_color, lightness, chroma, hue in self.REFERENCE:
            with self.subTest(hex=hex_color):
                got_l, got_c, got_h = hex_to_oklch(hex_color)
                self.assertAlmostEqual(got_l, lightness, delta=0.002)
                self.assertAlmostEqual(got_c, chroma, delta=0.002)
                if hue is not None:
                    self.assertAlmostEqual(got_h, hue, delta=0.5)

    def test_achromatic_hue_is_zero_not_noise(self):
        # Grays have no meaningful hue; a/b rounding must not leak an angle.
        for gray in ("#000000", "#808080", "#FFFFFF"):
            self.assertEqual(hex_to_oklch(gray)[2], 0.0)

    def test_shorthand_hex(self):
        self.assertEqual(hex_to_rgb("#FFF"), hex_to_rgb("#FFFFFF"))

    def test_invalid_input_returns_none(self):
        for value in ("", None, "#GGG", "#12345", "rgb(0,0,0)"):
            self.assertIsNone(hex_to_oklch(value))
            self.assertIsNone(format_oklch(value))

    def test_format_shape(self):
        self.assertRegex(
            format_oklch("#2563EB"),
            r"^oklch\(-?[\d.]+ -?[\d.]+ -?[\d.]+\)$",
        )


class TestShadcnTheme(unittest.TestCase):
    def setUp(self):
        self.css = to_shadcn_css(SAMPLE)

    def test_emits_root_block(self):
        self.assertIn(":root {", self.css)
        self.assertIn("}", self.css)
        self.assertIn("--radius:", self.css)

    def test_every_mapped_variable_present(self):
        for variable, _key, _alias in LIGHT_MAPPING:
            self.assertIn(f"--{variable}:", self.css)

    def test_values_are_oklch_by_default(self):
        self.assertIn("--primary: oklch(", self.css)
        self.assertNotIn("--primary: #", self.css)

    def test_hex_format_option(self):
        css = to_shadcn_css(SAMPLE, color_format="hex")
        self.assertIn("--primary: #2563EB;", css)
        self.assertNotIn("oklch(", css)

    def test_rejects_unknown_format(self):
        with self.assertRaises(ValueError):
            to_shadcn_css(SAMPLE, color_format="hsl")

    def test_aliases_are_marked_in_output(self):
        self.assertIn("alias of --card", self.css)
        self.assertIn("alias of --border", self.css)

    def test_chart_and_sidebar_vars_are_not_fabricated(self):
        self.assertNotIn("--chart-1", self.css)
        self.assertNotIn("--sidebar", self.css)

    def test_missing_colors_are_reported_not_emitted_empty(self):
        sparse = {"project_name": "Sparse", "style": {},
                  "colors": {"background": "#FFF", "foreground": "#000"},
                  "contrast": []}
        css = to_shadcn_css(sparse)
        self.assertNotIn("--primary:", css)
        self.assertIn("Not emitted", css)
        self.assertIn("--primary", css)  # named in the note

    def test_contrast_failures_surface_as_comments(self):
        bad = {**SAMPLE, "colors": {**SAMPLE["colors"],
                                    "accent": "#FFFF00", "on_accent": "#FFFFFF"},
               "contrast": []}
        css = to_shadcn_css(bad)
        self.assertIn("Contrast notes", css)
        self.assertIn("FAIL", css)

    def test_no_unbalanced_css_comment(self):
        # An unterminated /* would comment out the rest of globals.css.
        self.assertEqual(self.css.count("/*"), self.css.count("*/"))


class TestEndToEnd(unittest.TestCase):
    def test_generate_with_shadcn_format(self):
        result = generate_design_system(
            "SaaS analytics dashboard", "Acme", output_format="shadcn",
        )
        css = result["text"]
        self.assertIn(":root {", css)
        self.assertIn("--primary: oklch(", css)
        self.assertEqual(css.count("/*"), css.count("*/"))
        # Every declaration inside :root must terminate.
        root = css.split(":root {", 1)[1].split("}", 1)[0]
        for line in root.strip().splitlines():
            stripped = line.split("/*")[0].strip()
            if stripped:
                self.assertTrue(stripped.endswith(";"), f"unterminated: {line!r}")

    def test_declarations_are_well_formed(self):
        css = generate_design_system("portfolio", "P", output_format="shadcn")["text"]
        root = css.split(":root {", 1)[1].split("}", 1)[0]
        for line in root.strip().splitlines():
            stripped = line.split("/*")[0].strip()
            if stripped:
                self.assertRegex(stripped, r"^--[a-z0-9-]+: .+;$")

class TestOklchInverse(unittest.TestCase):
    """The inverse is pinned by round-tripping against the forward conversion,
    which is itself pinned to published reference values above."""

    def test_round_trips_exactly_across_the_gamut(self):
        import random
        random.seed(7)
        cases = ["#FFFFFF", "#000000", "#FF0000", "#00FF00", "#0000FF",
                 "#2563EB", "#808080", "#E8B4B8", "#1E293B", "#F97316"]
        cases += ["#%06X" % random.randrange(0x1000000) for _ in range(500)]
        worst = 0
        for hex_color in cases:
            lightness, chroma, hue = hex_to_oklch(hex_color)
            back, _clipped = oklch_to_hex(lightness, chroma, hue)
            worst = max(worst, max(
                abs(int(hex_color[i:i + 2], 16) - int(back[i:i + 2], 16))
                for i in (1, 3, 5)))
        self.assertEqual(worst, 0, f"worst per-channel error {worst}/255")

    def test_in_gamut_colors_are_not_flagged_clipped(self):
        lightness, chroma, hue = hex_to_oklch("#2563EB")
        _hex, clipped = oklch_to_hex(lightness, chroma, hue)
        self.assertFalse(clipped)

    def test_out_of_gamut_is_flagged_rather_than_silently_clamped(self):
        # Chroma far beyond sRGB: the hex is a clamp, and callers must be able
        # to tell, since clamping can shift hue.
        _hex, clipped = oklch_to_hex(0.6, 0.5, 150)
        self.assertTrue(clipped)

    def test_matches_browser_canvas_conversion(self):
        # Cross-checked against Chrome's own color engine via a 1x1 canvas:
        #   oklch(0.5461 0.2152 262.881) -> #2563EB
        self.assertEqual(oklch_to_hex(0.5461, 0.2152, 262.881)[0], "#2563EB")

    def test_oklab_grayscale_axis(self):
        self.assertEqual(oklab_to_hex(1.0, 0.0, 0.0)[0], "#FFFFFF")
        self.assertEqual(oklab_to_hex(0.0, 0.0, 0.0)[0], "#000000")


if __name__ == "__main__":
    unittest.main(verbosity=2)
