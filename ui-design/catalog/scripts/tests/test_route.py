#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for route.py, the brief router (stdlib unittest)."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import route

LEDGERLY = "freelancer invoicing SaaS fintech trustworthy"


class TestStemKey(unittest.TestCase):
    def test_inflections_collapse_to_the_catalog_form(self):
        self.assertEqual(route.stem_key("invoicing"), route.stem_key("invoice"))
        self.assertEqual(route.stem_key("freelancer"), route.stem_key("freelance"))
        self.assertEqual(route.stem_key("shopping"), route.stem_key("shop"))
        self.assertEqual(route.stem_key("services"), route.stem_key("service"))

    def test_short_words_are_left_alone(self):
        self.assertEqual(route.stem_key("saas"), "saas")
        self.assertEqual(route.stem_key("bill"), "bill")


class TestLedgerlyRegression(unittest.TestCase):
    """The brief that started this: the literal search picks the wrong row."""

    @classmethod
    def setUpClass(cls):
        cls.result = route.route(LEDGERLY)

    def test_invoice_and_billing_tool_is_a_candidate(self):
        names = [c["product_type"] for c in self.result["candidates"]]
        self.assertIn("Invoice & Billing Tool", names)
        self.assertEqual(names[0], "Invoice & Billing Tool")

    def test_ambiguity_with_freelancer_platform_is_flagged(self):
        flagged = [w for w in self.result["warnings"]
                   if "Invoice & Billing Tool" in w["message"]
                   and "Freelancer Platform" in w["message"]]
        self.assertTrue(flagged, self.result["warnings"])

    def test_the_emitted_design_system_command_names_the_right_row(self):
        self.assertIn("Invoice & Billing Tool", self.result["commands"][0])
        self.assertIn("--design-system", self.result["commands"][0])
        self.assertNotIn("--persist", self.result["commands"][0])


class TestConfidentBrief(unittest.TestCase):
    def test_a_brief_in_the_catalogs_own_words_raises_no_ambiguity(self):
        result = route.route("beauty spa wellness service")
        self.assertEqual(result["candidates"][0]["product_type"], "Beauty/Spa/Wellness Service")
        self.assertFalse([w for w in result["warnings"] if w["code"] == "ambiguous"])

    def test_gibberish_says_no_match(self):
        result = route.route("zzzqqq")
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["warnings"][0]["code"], "no-match")
        self.assertEqual(result["commands"], [])


class TestManifest(unittest.TestCase):
    def test_parts_have_the_documented_shape_and_unique_ids(self):
        parts = route.route(LEDGERLY, stack="nextjs")["manifest"]
        ids = [p["part_id"] for p in parts]
        self.assertEqual(len(ids), len(set(ids)))
        for part in parts:
            self.assertEqual(set(part), {"part_id", "kind", "target", "query", "n"})
            self.assertIn(part["kind"], ("domain", "stack"))

    def test_accessibility_is_always_present(self):
        self.assertIn("ux-a11y", [p["part_id"] for p in route.route("kids coding game")["manifest"]])

    def test_stack_parts_only_appear_with_a_stack(self):
        without = route.route(LEDGERLY)["manifest"]
        with_stack = route.route(LEDGERLY, stack="nextjs")["manifest"]
        self.assertFalse([p for p in without if p["kind"] == "stack"])
        self.assertTrue([p for p in with_stack if p["kind"] == "stack" and p["target"] == "nextjs"])

    def test_fan_out_is_recommended_only_for_wide_briefs(self):
        narrow = route.route("beauty spa wellness service")["fan_out"]
        wide = route.route("invoicing dashboard with animated charts and navigation menu",
                           stack="react")["fan_out"]
        self.assertFalse(narrow["recommended"])
        self.assertTrue(wide["recommended"])
        self.assertGreaterEqual(wide["parts"], route.FAN_OUT_MIN_PARTS)


class TestCli(unittest.TestCase):
    def test_json_output_round_trips(self):
        done = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "route.py"), LEDGERLY, "--json"],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
            check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["candidates"][0]["product_type"],
                         "Invoice & Billing Tool")


if __name__ == "__main__":
    unittest.main()
