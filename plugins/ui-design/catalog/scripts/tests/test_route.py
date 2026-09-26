#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for route.py, the brief router (stdlib unittest)."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

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


def stub_stack_search(empty):
    """A search_stack stand-in: parts whose (stack, query) is in `empty` find nothing."""
    def search_stack(query, stack, max_results, diagnostics=False):
        if (stack, query) in empty:
            return {"count": 0, "results": [], "diagnostics": {"token_coverage": 0.0}}
        return {"count": 1, "results": [{"Guideline": "g"}], "diagnostics": {"token_coverage": 1.0}}
    return search_stack


class TestStackProbe(unittest.TestCase):
    """Stack parts are dispatched only if the stack's own data can answer them."""

    A11Y_QUERY = route.BASELINE[3]

    def probed(self, search_stack, stack="svelte", brief=LEDGERLY):
        with mock.patch.object(route.core, "search_stack", search_stack):
            return route.route(brief, stack=stack)

    def test_an_unanswerable_stack_part_moves_to_not_covered(self):
        result = self.probed(stub_stack_search({("svelte", self.A11Y_QUERY)}))
        self.assertNotIn("stack-svelte-a11y", [p["part_id"] for p in result["manifest"]])
        self.assertEqual([p["part_id"] for p in result["not_covered"]], ["stack-svelte-a11y"])
        entry = result["not_covered"][0]
        self.assertEqual(set(entry), {"part_id", "target", "query", "reason"})
        self.assertEqual((entry["target"], entry["query"]), ("svelte", self.A11Y_QUERY))
        self.assertIn("no rows", entry["reason"])

    def test_the_domain_part_for_the_same_concern_is_kept(self):
        result = self.probed(stub_stack_search({("svelte", self.A11Y_QUERY)}))
        self.assertIn("ux-a11y", [p["part_id"] for p in result["manifest"]])

    def test_low_coverage_rows_count_as_not_covered(self):
        def search_stack(query, stack, max_results, diagnostics=False):
            return {"count": 1, "results": [{"Guideline": "g"}],
                    "diagnostics": {"token_coverage": route.LOW_COVERAGE - 0.01}}
        result = self.probed(search_stack)
        self.assertFalse([p for p in result["manifest"] if p["kind"] == "stack"])
        self.assertTrue(result["not_covered"])
        self.assertIn("token_coverage", result["not_covered"][0]["reason"])

    def test_dropping_parts_lowers_the_fan_out_count(self):
        kept = self.probed(stub_stack_search(set()))["fan_out"]
        dropped = self.probed(stub_stack_search({("svelte", self.A11Y_QUERY)}))["fan_out"]
        self.assertEqual((kept["parts"], kept["recommended"]), (4, True))
        self.assertEqual((dropped["parts"], dropped["recommended"]), (3, False))

    def test_a_stack_the_catalog_covers_keeps_its_part(self):
        result = route.route(LEDGERLY, stack="react")
        self.assertIn("stack-react-a11y", [p["part_id"] for p in result["manifest"]])
        self.assertNotIn("stack-react-a11y", [p["part_id"] for p in result["not_covered"]])

    def test_angular_a11y_part_is_dispatched_now_that_angular_has_rows(self):
        result = route.route(LEDGERLY, stack="angular")
        self.assertIn("stack-angular-a11y", [p["part_id"] for p in result["manifest"]])
        self.assertNotIn("stack-angular-a11y", [p["part_id"] for p in result["not_covered"]])

    def test_domain_parts_are_never_probed(self):
        calls = []
        def search_stack(query, stack, max_results, diagnostics=False):
            calls.append(stack)
            return {"count": 1, "results": [{"Guideline": "g"}], "diagnostics": {"token_coverage": 1.0}}
        self.probed(search_stack)
        self.assertEqual(set(calls), {"svelte"})

    def test_without_a_stack_nothing_is_probed_or_dropped(self):
        result = route.route(LEDGERLY)
        self.assertEqual(result["not_covered"], [])

    def test_the_text_report_names_what_was_not_dispatched(self):
        result = self.probed(stub_stack_search({("svelte", self.A11Y_QUERY)}))
        report = route.format_report(result)
        self.assertIn("Not covered", report)
        self.assertIn("stack-svelte-a11y", report.split("Not covered")[1])
        self.assertNotIn("Not covered", route.format_report(route.route(LEDGERLY)))


class TestStackQueryOverrides(unittest.TestCase):
    """A stack that words a concern differently gets its own query, and only that stack."""

    def a11y_query(self, stack):
        parts = route.build_manifest(route.tokens_of(LEDGERLY), stack)
        return next(p["query"] for p in parts if p["part_id"] == f"stack-{stack}-a11y")

    def test_an_overridden_stack_uses_its_own_query(self):
        for stack in ("nextjs", "astro"):
            self.assertEqual(self.a11y_query(stack), route.STACK_QUERY_OVERRIDES[(stack, "a11y")])
            self.assertNotEqual(self.a11y_query(stack), route.BASELINE[3])

    def test_every_other_stack_keeps_the_shared_query(self):
        for stack in ("react", "angular", "vue", "svelte"):
            self.assertEqual(self.a11y_query(stack), route.BASELINE[3])

    def test_the_override_is_only_for_the_concern_it_names(self):
        parts = route.build_manifest(route.tokens_of(LEDGERLY), "nextjs")
        forms = next(p for p in parts if p["part_id"] == "stack-nextjs-forms")
        self.assertEqual(forms["query"], "form validation input")

    def test_every_override_still_finds_rows_in_its_stack(self):
        """Real data: an override that stops answering must fail here, not go quiet."""
        for (stack, concern), query in route.STACK_QUERY_OVERRIDES.items():
            probe = route.core.search_stack(query, stack, route.PART_N, diagnostics=True)
            coverage = probe.get("diagnostics", {}).get("token_coverage")
            self.assertTrue(probe.get("results"), f"{stack}/{concern}: no rows for {query!r}")
            self.assertGreaterEqual(coverage, route.LOW_COVERAGE, f"{stack}/{concern}")

    def test_nextjs_and_astro_accessibility_parts_are_now_dispatched(self):
        for stack in ("nextjs", "astro"):
            result = route.route(LEDGERLY, stack=stack)
            ids = [p["part_id"] for p in result["manifest"]]
            self.assertIn(f"stack-{stack}-a11y", ids)
            self.assertNotIn(f"stack-{stack}-a11y", [p["part_id"] for p in result["not_covered"]])


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
