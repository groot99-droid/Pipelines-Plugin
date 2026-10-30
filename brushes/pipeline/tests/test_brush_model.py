"""pipeline/brush_model.py: a Brush.archive as parameters, and back.

Kinds of evidence, kept apart:

  schema-only builds  `brush_model.case_base(era)` is a brush made of nothing
                      but schema/silica_keys.json: every key of an era with its
                      default. Built, encoded and decoded again, it must read as
                      fidelity "byte" and rebuild "exact".
  frozen goldens      GOLDENS below holds the sha256 of each era's schema-only
                      build. They were recorded only after the corpus test at
                      the end of this file had rebuilt every archive of the
                      real library from its parameters and the schema alone, so
                      a change to the byte path shows here, where there is no
                      library. A change to a census column of the schema (a
                      default, a key order) changes them too: record them again
                      only after the corpus test passes.
  plistlib            tests/fixtures.py writes archives with plistlib, a layout
                      the app's writer does not use: they must read as
                      fidelity "table" and still export their source bytes.
  patch cases         schema/patch_cases.json, the table the app runs too.
  the real library    opt-in. Set ROSW_BRUSHES_CORPUS to a library folder and
                      run this file with an isolated interpreter:

        python -I -m unittest discover -s brushes/pipeline/tests -p test_brush_model.py

                      Every Brush.archive of every .brush and .brushset under it
                      is decoded, turned into JSON text, read back from that
                      text alone and encoded: the bytes must be the file's own.

    python -m unittest discover -s brushes/pipeline/tests
"""

import collections
import copy
import hashlib
import json
import math
import os
import plistlib
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))         # for `fixtures`, when one file is run by path

import bplist  # noqa: E402
import brush_common  # noqa: E402
import brush_model as bm  # noqa: E402
import fixtures  # noqa: E402
import keyed_archive as ka  # noqa: E402
from bplist import BrushModelError, CodecError, LimitExceeded, PDict, Real, UID  # noqa: E402

try:
    import yaml
except ImportError:                                 # pragma: no cover - CI installs it
    yaml = None

BRUSHES = PIPELINE.parent
SCHEMA_FILE = BRUSHES / "schema" / "silica_keys.json"
CASES_FILE = BRUSHES / "schema" / "patch_cases.json"
CORPUS = os.environ.get("ROSW_BRUSHES_CORPUS", "").strip()

# sha256 of encode(case_base(era)): see the module docstring before changing one.
GOLDENS = {
    "E0": "fb8c7918595cfa1601b574222697e7cce0c0139516ed6bea30f0b6c5f8b7aefb",
    "E1": "afa8731d74a7f491555d04e1d057bba71093367854aab870ade370d4afd03a95",
    "E1b": "bf54ce6002887c3f7f800ced8cda61cbda52c6d5be508b098eef609fc06145a8",
    "E1c": "85a22dbdae9e86edbdce85a8e286558950de2fa7c6ae7554543aafc98a852367",
    "E2": "0aa0254d203f30384f9cabc5c5abb28a544f8e27b5e363810f26f743e6f02b54",
    "E3": "3bf33c589e6d13aa77ad1c311d52351b2dfe7c303452afec12573552cc7a4773",
    "E4": "98cc02be19a8728349556fed0b1489f34af6627a3a43f4ce34cc5e34e772131f",
    "M172": "54f50a7f3897af5e7ac44c1deed624bae65dc3389b475b1e780a9d8998ffb36d",
    "M173": "e6d19d6006e90fc94798297d939b064aa4b8160d44590c006247da0cff749c20",
    "M220": "2c12cdc7145b6559d66225249c6abb0e2a1036d9d4248eef8833e73255660ab1",
    "M242": "8a7e711d0df69997f5e12fcf8185740c7f7d1d71a16427df140e769d17b466ef",
}
CONTRACT_REJECT_CODES = ("unknown_key", "wrong_type", "not_in_enum", "non_finite", "read_only",
                         "not_in_era", "curve_invalid")
IDENTITY = ["{0.000000, 0.000000}", "{1.000000, 1.000000}"]
NEG_ZERO = {"$real32": "80000000"}


def schema():
    return bm.load_schema()


def era_row(era):
    return next(row for row in schema()["eras"] if row["id"] == era)


def era_keys(era):
    return set(era_row(era)["key_order"])


def built(era, assign=None):
    """(Brush, bytes) of a schema-only build, decoded again from its bytes."""
    data = bm.encode(bm.case_base(era, assign))
    return bm.decode(data), data


def changed_keys(one, two):
    keys = set(one.params) | set(two.params)
    return sorted(k for k in keys
                  if json.dumps(one.params.get(k), sort_keys=True)
                  != json.dumps(two.params.get(k), sort_keys=True))


def instance(objects, chain, fields):
    """Append an instance (and its class entry) to a graph; fields is
    [(key, value)] without `$class`. Returns its UID."""
    holder = PDict()
    objects.append(holder)
    uid = UID(len(objects) - 1)
    holder.extend(fields)
    objects.append(PDict([("$classname", chain[0]), ("$classes", list(chain))]))
    holder.append(("$class", UID(len(objects) - 1)))
    return uid


def graph_archive(root_fields, chain=("SilicaBrush", "ValkyrieBrush", "NSObject"), extra=None):
    """The bytes of a keyed archive whose root holds `root_fields`. `extra`
    is called with the objects list before the root's class is added, and
    returns more root fields."""
    objects = ["$null"]
    root = PDict()
    objects.append(root)
    for key, value in root_fields:
        if isinstance(value, str):                  # text is an entry of its own, as the app's
            objects.append(value)
            value = UID(len(objects) - 1)
        root.append((key, value))
    if extra:
        root.extend(extra(objects))
    objects.append(PDict([("$classname", chain[0]), ("$classes", list(chain))]))
    root.append(("$class", UID(len(objects) - 1)))
    archive = ka.Archive(("$version", "$archiver", "$top", "$objects"), 100000, "NSKeyedArchiver",
                         objects)
    return ka.rule_encode(archive, "ios_modern")


def zip_bytes(entries):
    return fixtures.make_zip(entries)


# ── the schema ───────────────────────────────────────────────────────────────

class SchemaLoading(fixtures.BrushCase):
    def tearDown(self):
        super().tearDown()
        bm._LOADED = None

    def test_the_schema_is_read_beside_the_code_whatever_the_data_root(self):
        os.environ[brush_common.ENV_ROOT] = str(self.tmp)
        os.environ[brush_common.ENV_LIBRARY] = str(self.tmp / "library")
        bm._LOADED = None
        self.assertEqual(bm.SCHEMA_PATH, brush_common.TOOL_ROOT / "schema" / "silica_keys.json")
        self.assertEqual(bm.SCHEMA_PATH, brush_common.resolve_paths().schema / "silica_keys.json")
        loaded = bm.load_schema()
        self.assertEqual(loaded, json.loads(SCHEMA_FILE.read_text(encoding="utf-8")))
        self.assertIs(bm.load_schema(), loaded)

    def test_a_missing_schema_is_no_schema(self):
        bm._LOADED = None
        with mock.patch.object(bm, "SCHEMA_PATH", self.tmp / "absent.json"):
            with self.assertRaises(BrushModelError) as caught:
                bm.load_schema()
        self.assertEqual(caught.exception.code, "no_schema")

    def test_a_schema_that_is_not_json_is_bad_schema(self):
        bad = self.tmp / "silica_keys.json"
        bad.write_text("{not json", encoding="utf-8", newline="\n")
        bm._LOADED = None
        with mock.patch.object(bm, "SCHEMA_PATH", bad):
            with self.assertRaises(BrushModelError) as caught:
                bm.load_schema()
        self.assertEqual(caught.exception.code, "bad_schema")

    def test_a_schema_of_the_wrong_shape_is_bad_schema(self):
        broken = copy.deepcopy(schema())
        broken["keys"].append(dict(broken["keys"][0]))
        with self.assertRaises(BrushModelError) as caught:
            bm.detect_era(["name"], schema=broken)
        self.assertEqual(caught.exception.code, "bad_schema")
        broken = copy.deepcopy(schema())
        del broken["classes"]["$class_entry"]
        with self.assertRaises(BrushModelError) as caught:
            bm.detect_era(["name"], schema=broken)
        self.assertEqual(caught.exception.code, "bad_schema")

    def test_aliases_and_settings_follow_the_schema(self):
        self.assertEqual(bm.aliases_of("dynamicsGlazeFlow"), ["dynamicsGlazedFlow"])
        self.assertEqual(bm.aliases_of("dynamicsGlazedFlow"), ["dynamicsGlazeFlow"])
        self.assertEqual(bm.aliases_of("notAKey"), [])
        modern = bm.case_base("M220").params
        legacy = bm.case_base("E4").params
        self.assertEqual(bm.setting(modern, "dynamicsGlazeFlow"), modern["dynamicsGlazedFlow"])
        self.assertEqual(bm.setting(legacy, "dynamicsGlazedFlow"), legacy["dynamicsGlazeFlow"])
        # An alias of another type is not the same setting.
        self.assertIsNone(bm.setting(modern, "dynamicsRenderType"))
        self.assertEqual(bm.setting(modern, "notAKey", "fallback"), "fallback")


# ── eras ─────────────────────────────────────────────────────────────────────

class Eras(unittest.TestCase):
    def test_every_era_matches_its_own_key_set_exactly(self):
        for row in schema()["eras"]:
            self.assertEqual(bm.detect_era(row["key_order"]), (row["id"], True, [], []), row["id"])
            self.assertEqual(bm.nearest_era(row["key_order"]), row["id"])
            self.assertEqual(bm.family_of(row["id"]), row["family"])
            for variant in row["variants"]:
                self.assertEqual(bm.detect_era(variant["key_order"])[:2], (row["id"], True))

    def test_class_is_counted_whether_or_not_it_is_named(self):
        keys = era_keys("E3") - {"$class"}
        self.assertEqual(bm.detect_era(keys), ("E3", True, [], []))

    def test_M220_takes_any_subset_of_its_optional_curves(self):
        row = era_row("M220")
        optional = row["optional_keys"]
        self.assertGreaterEqual(len(optional), 1)
        base = set(row["key_order"])
        for count in range(len(optional) + 1):
            keys = base | set(optional[:count])
            self.assertEqual(bm.detect_era(keys), ("M220", True, [], []), count)
        self.assertEqual(bm.detect_era(base | set(optional[-2:]))[:2], ("M220", True))

    def test_any_other_key_set_is_X_and_names_what_differs_from_the_nearest(self):
        keys = era_keys("E3") | {"grainDepth"}
        self.assertEqual(bm.detect_era(keys), ("X89", False, [], ["grainDepth"]))
        self.assertEqual(bm.nearest_era(keys), "E3")
        self.assertEqual(bm.family_of(keys), "legacy")
        keys = era_keys("M220") - {"paintPressure", "hoverFill"}
        era, exact, missing, extra = bm.detect_era(keys)
        self.assertEqual((era, exact, extra), ("X218", False, []))
        self.assertEqual(missing, ["hoverFill", "paintPressure"])
        self.assertEqual(bm.family_of(keys), "modern")

    def test_a_count_alone_decides_nothing(self):
        e3 = era_keys("E3")
        swapped = (e3 - {"taperShape"}) | {"grainDepth"}
        self.assertEqual(len(swapped), 88)
        era, exact, missing, extra = bm.detect_era(swapped)
        self.assertEqual((era, exact, missing, extra), ("X88", False, ["taperShape"], ["grainDepth"]))

    def test_an_optional_curve_outside_M220_is_X(self):
        keys = era_keys("M242") | {"dynamicsPressureAttackCurve"}
        self.assertEqual(bm.detect_era(keys)[:2], ("X243", False))
        self.assertEqual(bm.nearest_era(keys), "M242")

    def test_a_tie_goes_to_the_earlier_era(self):
        e1, e1b = era_keys("E1"), era_keys("E1b")
        self.assertEqual(e1b - e1, {"dynamicsTiltCompression"})
        # One key from E1b's set missing, one unknown key: equally far from both? No:
        # E1 plus an unknown key is 1 from E1 and 2 from E1b.
        self.assertEqual(bm.nearest_era(e1 | {"strange"}), "E1")
        # E1 plus half of what E1b adds is a tie between the two; the table's
        # earlier row wins. Build such a set by hand with a made-up schema.
        made = copy.deepcopy(schema())
        made["eras"] = [dict(era_row("E1"), id="A", key_order=["$class", "a", "b"],
                             variants=[], optional_keys=[]),
                        dict(era_row("E1"), id="B", key_order=["$class", "a", "c"],
                             variants=[], optional_keys=[])]
        self.assertEqual(bm.detect_era(["a"], schema=made), ("X2", False, ["b"], []))
        self.assertEqual(bm.nearest_era(["a"], schema=made), "A")

    def test_an_unknown_era_name_is_bad_era(self):
        with self.assertRaises(BrushModelError) as caught:
            bm.family_of("E9")
        self.assertEqual(caught.exception.code, "bad_era")


# ── building from the schema alone ───────────────────────────────────────────

class SchemaOnlyBuild(unittest.TestCase):
    def test_every_era_builds_to_its_golden_bytes(self):
        self.assertEqual(sorted(GOLDENS), sorted(row["id"] for row in schema()["eras"]))
        for era, golden in GOLDENS.items():
            data = bm.encode(bm.case_base(era))
            self.assertEqual(hashlib.sha256(data).hexdigest(), golden, era)

    def test_a_build_reads_back_byte_for_byte(self):
        for row in schema()["eras"]:
            brush, data = built(row["id"])
            self.assertEqual((brush.era, brush.family, brush.profile),
                             (row["id"], row["family"], row["profile"]), row["id"])
            self.assertEqual((brush.fidelity, brush.rebuild), ("byte", "exact"), row["id"])
            self.assertEqual(brush.key_order, row["key_order"], row["id"])
            self.assertEqual(list(brush.top_order), row["top_order"], row["id"])
            self.assertEqual(list(brush.root_class), row["root_class"], row["id"])
            self.assertIs(bm.encode(brush), brush.archive.source)
            self.assertEqual(bm.export_state(brush), "source")
            plain = plistlib.loads(data)
            self.assertEqual(list(plain), row["top_order"])

    def test_json_text_alone_rebuilds_the_same_bytes(self):
        for row in schema()["eras"]:
            brush, data = built(row["id"])
            text = json.dumps(bm.to_json(brush), allow_nan=False, sort_keys=True)
            again = bm.from_json(json.loads(text))
            self.assertEqual(again.fidelity, "built")
            self.assertEqual(bm.encode(again), data, row["id"])
            self.assertEqual(bm.export_state(again), "canonical")

    def test_a_curve_has_a_resolution_in_a_legacy_brush_only(self):
        self.assertEqual(bm.case_base("E4").params["dynamicsPressureSizeCurve"],
                         {"points": IDENTITY, "resolution": 1024})
        self.assertEqual(bm.case_base("M220").params["dynamicsPressureSizeCurve"],
                         {"points": IDENTITY})

    def test_an_unknown_era_has_no_case_base(self):
        with self.assertRaises(BrushModelError) as caught:
            bm.case_base("X12")
        self.assertEqual(caught.exception.code, "bad_era")


# ── plistlib archives (fixtures) ─────────────────────────────────────────────

class PlistlibArchives(unittest.TestCase):
    def test_legacy_fixtures_are_their_eras_and_read_as_table(self):
        for era in fixtures.LEGACY_ERAS:
            data = fixtures.make_archive("legacy", era=era, name="Fixture")
            brush = bm.decode(data)
            self.assertEqual((brush.era, brush.family), (era, "legacy"), era)
            self.assertEqual(brush.fidelity, "table", era)
            self.assertEqual(brush.profile, "ios_legacy", era)
            self.assertEqual(brush.name, "Fixture")
            self.assertEqual(bm.encode(brush), data, era)
            codes = [issue.code for issue in bm.validate(brush)]
            self.assertIn("fidelity_table", codes)

    def test_a_changed_table_archive_is_written_into_its_own_graph(self):
        data = fixtures.make_archive("legacy", era="E3", name="Fixture",
                                     overrides={"plotSpacing": 0.3})
        brush = bm.decode(data)
        patched, report = bm.apply_patch(brush, {"plotSpacing": 0.6})
        self.assertTrue(report["ok"])
        out = bm.encode(patched)
        self.assertNotEqual(out, data)
        again = bm.decode(out)
        self.assertEqual(changed_keys(brush, again), ["plotSpacing"])
        self.assertEqual(again.params["plotSpacing"], bm._f32(0.6))
        self.assertEqual((again.era, again.fidelity), ("E3", "byte"))
        self.assertEqual(plistlib.loads(out)["$top"], {"root": plistlib.UID(1)})
        codes = [issue.code for issue in bm.validate(patched)]
        self.assertIn("fidelity_table", codes)

    def test_a_wrapped_name_is_kept_with_its_wrapper(self):
        data = fixtures.make_archive("legacy", era="E4", name="Wrapped", wrap_name=True)
        brush = bm.decode(data)
        self.assertEqual(brush.params["name"], {"string": "Wrapped", "wrapper": "NSMutableString"})
        self.assertEqual(brush.name, "Wrapped")
        patched, report = bm.apply_patch(brush, {"name": "Renamed"})
        self.assertEqual(report["applied"], {"name": {"string": "Renamed",
                                                       "wrapper": "NSMutableString"}})
        self.assertEqual(bm.decode(bm.encode(patched)).params["name"],
                         {"string": "Renamed", "wrapper": "NSMutableString"})


# ── JSON forms ───────────────────────────────────────────────────────────────

class JsonForms(unittest.TestCase):
    def test_the_frozen_form(self):
        brush, _ = built("E3")
        form = bm.to_json(brush)
        self.assertEqual(sorted(form), sorted(["schema", "era", "family", "profile", "top_order",
                                               "root_class", "key_order", "params", "shared"]))
        self.assertEqual(form["schema"], bm.MODEL_SCHEMA)
        self.assertEqual(form["key_order"], era_row("E3")["key_order"])
        self.assertEqual(list(form["params"]), [k for k in form["key_order"] if k != "$class"])
        self.assertEqual(form["shared"], [])
        json.dumps(form, allow_nan=False)

    def test_values_json_cannot_carry_are_tagged_and_come_back(self):
        assign = {"dynamicsTiltAngle": NEG_ZERO, "futureReal": {"$real32": 1.0},
                  "futureDouble": {"$real64": 0.1}, "futureInt": {"$int": 7},
                  "futureFlag": True}
        brush, data = built("M220", assign)
        self.assertEqual(brush.era, "X224")
        for key, value in assign.items():
            self.assertEqual(brush.params[key], value, key)
        self.assertIn(b"\x22\x80\x00\x00\x00", data)          # a 4-byte real, -0.0
        text = json.dumps(bm.to_json(brush), allow_nan=False)
        self.assertEqual(bm.encode(bm.from_json(json.loads(text))), data)

    def test_a_real_under_an_int_key_keeps_its_width(self):
        brush, data = built("E4", {"blendMode": {"$real32": 2.0}})
        self.assertEqual(brush.params["blendMode"], {"$real32": 2.0})
        self.assertEqual(bm.encode(bm.from_json(json.loads(json.dumps(bm.to_json(brush))))), data)
        self.assertIn("type_mismatch", [issue.code for issue in bm.validate(brush)])

    def test_from_json_refuses_what_is_not_the_form(self):
        good = bm.to_json(bm.case_base("E3"))

        def refused(change, code="bad_json"):
            obj = copy.deepcopy(good)
            change(obj)
            with self.assertRaises(BrushModelError) as caught:
                bm.from_json(obj)
            self.assertEqual(caught.exception.code, code)

        refused(lambda o: o.update(schema="other/1"))
        refused(lambda o: o["key_order"].remove("$class"))
        refused(lambda o: o["key_order"].append("name"))
        refused(lambda o: o.update(era="E4"))
        refused(lambda o: o.update(family="modern"))
        refused(lambda o: o.update(profile="ios_future"))
        refused(lambda o: o.update(top_order=["$version", "$objects"]))
        refused(lambda o: o.update(root_class=[]))
        refused(lambda o: o.update(shared=[["name"]]))
        refused(lambda o: o.update(shared=[["name", "nope"]]))
        refused(lambda o: (o["params"].update(future=1), o["key_order"].append("future"),
                           o.update(era=None)), "bad_value")
        refused(lambda o: o["params"].update(dynamicsPressureSizeCurve={"points": [1, 2]}),
                "bad_value")
        refused(lambda o: o["params"].update(color={"$data": "xyz"}), "bad_value")
        self.assertEqual(bm.from_json(good).era, "E3")
        # A value of another type than its row says is kept, as a file may hold
        # one, and validate names it.
        odd = copy.deepcopy(good)
        odd["params"]["plotSpacing"] = "wide"
        brush = bm.from_json(odd)
        self.assertEqual(bm.decode(bm.encode(brush)).params["plotSpacing"], "wide")
        self.assertIn("type_mismatch", [issue.code for issue in bm.validate(brush)])

    def test_an_unreadable_value_is_opaque_and_cannot_be_built(self):
        def loop(objects):
            holder = PDict()
            objects.append(holder)
            uid = UID(len(objects) - 1)
            holder.append(("next", uid))
            objects.append(PDict([("$classname", "Loop"), ("$classes", ["Loop", "NSObject"])]))
            holder.append(("$class", UID(len(objects) - 1)))
            return [("loop", uid)]

        data = graph_archive([("name", "x")], extra=loop)
        brush = bm.decode(data)
        self.assertEqual(brush.params["loop"], {"$opaque": "an entry that holds itself"})
        self.assertEqual(brush.rebuild, "kept")
        self.assertEqual(brush.fidelity, "table")
        self.assertIs(bm.encode(brush), brush.archive.source)
        codes = [issue.code for issue in bm.validate(brush)]
        self.assertIn("opaque_value", codes)
        with self.assertRaises(BrushModelError) as caught:
            bm.encode(bm.from_json(json.loads(json.dumps(bm.to_json(brush)))))
        self.assertEqual(caught.exception.code, "opaque")
        # The graph that was read is still written around a change.
        patched, report = bm.apply_patch(brush, {"name": "y"})
        again = bm.decode(bm.encode(patched))
        self.assertEqual((again.params["name"], again.params["loop"]), ("y", brush.params["loop"]))

    def test_an_unknown_class_is_kept_verbatim(self):
        def odd(objects):
            uid = instance(objects, ("FutureThing", "NSObject"),
                           [("weight", Real.f32(0.5)), ("label", "inline"), ("list", [1, 2])])
            return [("future", uid)]

        data = graph_archive([("name", "x")], extra=odd)
        brush = bm.decode(data)
        form = brush.params["future"]
        self.assertEqual(form["$class"], "FutureThing")
        self.assertEqual(form["$fields"], [["weight", {"$real32": 0.5}], ["label", {"$inline": "inline"}],
                                           ["list", {"$list": [{"$int": 1}, {"$int": 2}]}], ["$class", None]])
        self.assertEqual(bm.encode(bm.from_json(json.loads(json.dumps(bm.to_json(brush))))), data)

    def test_the_text_of_a_real(self):
        self.assertEqual(bm.real_text(0.1), "0.1")
        self.assertEqual(bm.real_text(0.10000000149011612), "0.1")
        self.assertEqual(bm.real_text(1.0), "1")
        self.assertEqual(bm.real_text(0.7338709831237793), "0.733871")
        self.assertTrue(bm.same_real(0.1, 0.10000000149011612))
        self.assertFalse(bm.same_real(0.0, -0.0))
        self.assertEqual(bm.scalar(NEG_ZERO), -0.0)
        self.assertEqual(math.copysign(1.0, bm.scalar(NEG_ZERO)), -1.0)
        self.assertEqual(bm.scalar({"$int": 3}), 3)
        self.assertIsNone(bm.scalar("text"))


# ── patches ──────────────────────────────────────────────────────────────────

class PatchCases(unittest.TestCase):
    """schema/patch_cases.json: the table both Python and the app run."""

    @classmethod
    def setUpClass(cls):
        cls.table = json.loads(CASES_FILE.read_text(encoding="utf-8"))

    def test_the_table_has_its_shape(self):
        self.assertEqual(self.table["schema"], "rosw-brushes-patch-cases/1")
        ids = [case["id"] for case in self.table["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        codes = {r["code"] for case in self.table["cases"] for r in case["expect"]["rejected"]}
        self.assertEqual(codes, set(CONTRACT_REJECT_CODES))
        for case in self.table["cases"]:
            self.assertLessEqual(set(case), {"id", "about", "era", "assign", "mode",
                                             "allow_unknown", "changes", "expect"}, case["id"])
            self.assertEqual(sorted(case["expect"]), sorted(
                ["ok", "era", "applied", "clamped", "rejected", "unchanged", "warnings"]), case["id"])

    def test_every_case(self):
        for case in self.table["cases"]:
            with self.subTest(case=case["id"]):
                base = bm.case_base(case["era"], case.get("assign"))
                patched, report = bm.apply_patch(base, case["changes"],
                                                 mode=case.get("mode", "strict"),
                                                 allow_unknown=case.get("allow_unknown", False))
                report = json.loads(json.dumps(report, allow_nan=False))
                expect = case["expect"]
                for name in ("ok", "era", "applied", "clamped", "unchanged", "warnings"):
                    self.assertEqual(report[name], expect[name], name)
                self.assertEqual([{k: r[k] for k in ("key", "value", "code")} for r in report["rejected"]],
                                 expect["rejected"])
                for rejected in report["rejected"]:
                    self.assertIsInstance(rejected["reason"], str)
                # Nothing but what was applied changed, and the result builds.
                self.assertEqual(changed_keys(base, patched), sorted(expect["applied"]))
                again = bm.decode(bm.encode(patched))
                self.assertEqual(changed_keys(patched, again), [])


class Patches(unittest.TestCase):
    def test_codes_are_the_contracts(self):
        self.assertEqual(bm.REJECT_CODES[:len(CONTRACT_REJECT_CODES)], CONTRACT_REJECT_CODES)
        self.assertEqual(bm.REJECT_CODES[len(CONTRACT_REJECT_CODES):], ("out_of_range",))
        self.assertEqual(bm.WARNING_CODES, ("outside_observed", "stale_thumbnail"))

    def test_keys_not_named_are_never_touched(self):
        brush, data = built("M220")
        patched, report = bm.apply_patch(brush, {"plotSpacing": 0.75})
        self.assertEqual(report["applied"], {"plotSpacing": 0.75})
        out = bm.encode(patched)
        again = bm.decode(out)
        self.assertEqual(changed_keys(brush, again), ["plotSpacing"])
        self.assertEqual((again.fidelity, again.rebuild, again.profile), ("byte", "exact", "ios_modern"))
        self.assertEqual(again.key_order, brush.key_order)
        self.assertEqual(bm.export_state(patched), "canonical")
        # The input brush is not changed by the patch.
        self.assertIs(bm.encode(brush), brush.archive.source)

    def test_a_patch_that_changes_nothing_exports_the_source_bytes(self):
        brush, data = built("E4")
        patched, report = bm.apply_patch(brush, {"plotSpacing": 0, "stamp": False})
        self.assertEqual(report["unchanged"], ["plotSpacing", "stamp"])
        self.assertFalse(bm.is_modified(patched))
        self.assertIs(bm.encode(patched), data)

    def test_a_change_to_a_shared_zero_changes_one_key(self):
        brush, data = built("E4")
        zeros = [k for k, v in brush.params.items() if v == 0.0 and isinstance(v, float)]
        self.assertGreater(len(zeros), 5)
        patched, _ = bm.apply_patch(brush, {zeros[0]: 0.3})
        again = bm.decode(bm.encode(patched))
        self.assertEqual(changed_keys(brush, again), [zeros[0]])
        self.assertTrue(all(again.params[k] == 0.0 for k in zeros[1:]))

    def test_two_keys_that_share_one_text_part_when_one_changes(self):
        brush, data = built("M220", {"bundledShapePath": "Shared.png", "bundledGrainPath": "Shared.png"})
        # Make the two keys one entry, as three library files have them.
        archive = ka.decode(data)
        root = ka.root(archive)
        root.set("bundledGrainPath", root.get("bundledShapePath"))
        shared_data = ka.rule_encode(ka.renumber(archive), "ios_modern")
        shared = bm.decode(shared_data)
        self.assertEqual(shared.shared, [["bundledShapePath", "bundledGrainPath"]])
        self.assertEqual((shared.fidelity, shared.rebuild), ("byte", "exact"))
        self.assertEqual(bm.encode(bm.from_json(json.loads(json.dumps(bm.to_json(shared))))),
                         shared_data)
        patched, report = bm.apply_patch(shared, {"bundledGrainPath": "Other.png"})
        self.assertEqual(patched.shared, [])
        again = bm.decode(bm.encode(patched))
        self.assertEqual((again.params["bundledShapePath"], again.params["bundledGrainPath"]),
                         ("Shared.png", "Other.png"))
        self.assertEqual(again.shared, [])

    def test_an_optional_curve_takes_the_stored_order_of_its_key_set(self):
        row = era_row("M220")
        variant = next(v for v in row["variants"] if v["key_count"] == 221)
        added = (set(variant["key_order"]) - set(row["key_order"])).pop()
        brush, _ = built("M220")
        patched, report = bm.apply_patch(brush, {added: [[0, 0], [0.4, 0.6], [1, 1]]})
        self.assertTrue(report["ok"])
        self.assertEqual(patched.key_order, variant["key_order"])
        self.assertEqual(patched.era, "M220")
        again = bm.decode(bm.encode(patched))
        self.assertEqual((again.era, again.fidelity, again.rebuild), ("M220", "byte", "exact"))
        self.assertEqual(again.key_order, variant["key_order"])

    def test_an_unseen_key_set_appends_the_key_and_is_valid_not_canonical(self):
        row = era_row("M220")
        seen = [set(v["key_order"]) for v in row["variants"]]
        optional = row["optional_keys"]
        pair = next((a, b) for a in optional for b in optional
                    if a < b and set(row["key_order"]) | {a, b} not in seen)
        brush, _ = built("M220")
        patched, report = bm.apply_patch(brush, {pair[0]: IDENTITY, pair[1]: IDENTITY})
        self.assertTrue(report["ok"])
        self.assertEqual(patched.key_order[-2:], list(pair))
        self.assertEqual(bm.export_state(patched), "valid")
        self.assertIn("fidelity_valid", [issue.code for issue in bm.validate(patched)])
        again = bm.decode(bm.encode(patched))
        self.assertEqual(again.era, "M220")
        self.assertEqual(changed_keys(patched, again), [])

    def test_a_key_whose_place_in_the_numbering_is_guessed_is_valid_not_canonical(self):
        """bundledHeightPath is nil in every library archive, so where the app
        numbers it is a guess (encode_order.guessed). Giving it a value of its
        own is written, and reported as valid, never as canonical."""
        self.assertEqual(schema()["encode_order"]["guessed"], {"modern": ["bundledHeightPath"]})
        for era in ("M220", "M242"):
            brush, _ = built(era)
            self.assertIsNone(brush.params["bundledHeightPath"])
            other, report = bm.apply_patch(brush, {"plotSpacing": 0.75})
            self.assertEqual(bm.export_state(other), "canonical", era)
            patched, report = bm.apply_patch(brush, {"bundledHeightPath": "Height.png"})
            self.assertTrue(report["ok"], era)
            self.assertEqual(bm.export_state(patched), "valid", era)
            issues = [(issue.code, issue.key) for issue in bm.validate(patched)]
            self.assertIn(("fidelity_valid", "bundledHeightPath"), issues, era)
            again = bm.decode(bm.encode(patched))
            self.assertEqual(again.params["bundledHeightPath"], "Height.png")
            self.assertEqual(changed_keys(patched, again), [])
            # Set back to nil, it holds no entry: the layout is known again.
            back, _ = bm.apply_patch(patched, {"bundledHeightPath": None, "plotSpacing": 0.75})
            self.assertEqual(bm.export_state(back), "canonical", era)

    def test_hard_limits_clamp_or_reject_and_soft_ones_never_do(self):
        made = copy.deepcopy(schema())
        row = next(r for r in made["keys"] if r["key"] == "plotSpacing")
        row["limits"], row["limits_hard"] = [0.0, 1.0], True
        base = bm.case_base("M220", schema=made)
        _, report = bm.apply_patch(base, {"plotSpacing": 1.5}, schema=made)
        self.assertEqual([(r["code"], r["value"]) for r in report["rejected"]], [("out_of_range", 1.5)])
        self.assertFalse(report["ok"])
        patched, report = bm.apply_patch(base, {"plotSpacing": 1.5}, mode="clamp", schema=made)
        self.assertEqual(report["clamped"], [{"key": "plotSpacing", "from": 1.5, "to": 1.0,
                                              "min": 0.0, "max": 1.0}])
        self.assertEqual(report["applied"], {"plotSpacing": 1.0})
        self.assertTrue(report["ok"])
        self.assertEqual(patched.params["plotSpacing"], 1.0)
        # The real schema holds no hard limit.
        self.assertFalse([r["key"] for r in schema()["keys"] if r["limits_hard"]])

    def test_a_bad_mode_or_a_bad_patch_raises(self):
        brush = bm.case_base("E1")
        with self.assertRaises(BrushModelError) as caught:
            bm.apply_patch(brush, {}, mode="loose")
        self.assertEqual(caught.exception.code, "bad_mode")
        with self.assertRaises(BrushModelError) as caught:
            bm.apply_patch(brush, [("plotSpacing", 1)])
        self.assertEqual(caught.exception.code, "bad_patch")

    def test_a_key_that_is_not_text_is_unknown(self):
        _, report = bm.apply_patch(bm.case_base("E1"), {7: 1})
        self.assertEqual([(r["key"], r["code"]) for r in report["rejected"]], [("7", "unknown_key")])

    def test_a_patch_envelope_is_the_contracts(self):
        self.assertEqual(bm.PATCH_SCHEMA, "rosw-brushes-patch/1")


# ── curves ───────────────────────────────────────────────────────────────────

class Curves(unittest.TestCase):
    def test_numeric_pairs_are_written_end_points_first(self):
        self.assertEqual(bm.canonical_curve([[0.75, 0.9], [0, 0], [0.25, 0.1], [1, 1]]),
                         ["{0.000000, 0.000000}", "{1.000000, 1.000000}",
                          "{0.250000, 0.100000}", "{0.750000, 0.900000}"])
        self.assertEqual(bm.canonical_curve([[0.2, 0], [1, 0.8]]),
                         ["{0.200000, 0.000000}", "{1.000000, 0.800000}"])

    def test_strings_in_the_archives_form_are_kept_as_given(self):
        points = ["{0.000000, 0.000000}", "{0.250000, 0.330000}", "{1.000000, 1.000000}"]
        self.assertEqual(bm.canonical_curve(points), points)

    def test_what_is_not_a_curve(self):
        for points in ([], [[0, 0]], [[0, 0]] * 65, [[0, 0], [1, 2]], [[0, 0], [-0.1, 1]],
                       [[0, 0], [float("nan"), 1]], ["{0, 0}", "{1, 1}"], [[0, 0], [1]],
                       [[0, 0], [True, 1]], "{0.000000, 0.000000}", None):
            with self.assertRaises(BrushModelError) as caught:
                bm.canonical_curve(points)
            self.assertEqual(caught.exception.code, "curve_invalid", points)

    def test_point_text(self):
        self.assertEqual(bm.point_text(0.5, -0.0), "{0.500000, 0.000000}")
        self.assertEqual(bm.point_text(1, 1), "{1.000000, 1.000000}")

    def test_curve_points_and_set_curve(self):
        brush = bm.case_base("E4")
        self.assertEqual(bm.curve_points(brush, "dynamicsPressureSizeCurve"), [(0.0, 0.0), (1.0, 1.0)])
        bm.set_curve(brush, "dynamicsPressureSizeCurve", [[0, 0], [1, 1], [0.3, 0.6]])
        self.assertEqual(brush.params["dynamicsPressureSizeCurve"],
                         {"points": ["{0.000000, 0.000000}", "{1.000000, 1.000000}",
                                     "{0.300000, 0.600000}"], "resolution": 1024})
        self.assertEqual(bm.curve_points(brush, "dynamicsPressureSizeCurve"),
                         [(0.0, 0.0), (0.3, 0.6), (1.0, 1.0)])
        self.assertEqual(bm.curve_points(brush, "dynamicsPressureSizeCurve", file_order=True),
                         [(0.0, 0.0), (1.0, 1.0), (0.3, 0.6)])
        with self.assertRaises(BrushModelError):
            bm.set_curve(brush, "dynamicsPressureSizeCurve", [[0, 0]])
        with self.assertRaises(BrushModelError):
            bm.curve_points(brush, "plotSpacing")


# ── new brushes ──────────────────────────────────────────────────────────────

class NewBrushes(fixtures.BrushCase):
    """A synthetic library stands in for the real one: its donor is a
    schema-only build, named by a patched NEW_BRUSH_DONORS."""

    def make_library(self, era="M220", assign=None):
        donor = bm.encode(bm.case_base(era, assign))
        entry = "0A1B2C3D-0000-4000-8000-000000000001/Brush.archive"
        library = self.tmp / "library"
        (library / "official" / "demo").mkdir(parents=True)
        (library / "official" / "demo" / "demo.brushset").write_bytes(zip_bytes([
            (entry, donor), ("brushset.plist", fixtures.brushset_plist("Demo", [entry.split("/")[0]]))]))
        donors = {name: {"container": "official/demo/demo.brushset", "entry": entry,
                         "archive_sha256": hashlib.sha256(donor).hexdigest()}
                  for name in bm.NEW_BRUSH_ERAS}
        patcher = mock.patch.dict(bm.NEW_BRUSH_DONORS, donors)
        patcher.start()
        self.addCleanup(patcher.stop)
        return library, donor

    def test_the_default_era_and_the_donors_are_the_specs(self):
        self.assertEqual(bm.NEW_BRUSH_ERA, "M220")
        self.assertEqual(bm.NEW_BRUSH_ERAS, ("M220", "E4"))
        self.assertEqual(sorted(bm.NEW_BRUSH_DONORS), sorted(bm.NEW_BRUSH_ERAS))
        for era, donor in bm.NEW_BRUSH_DONORS.items():
            self.assertEqual(sorted(donor), ["archive_sha256", "container", "entry"])
            self.assertRegex(donor["archive_sha256"], "^[0-9a-f]{64}$")
            self.assertRegex(donor["container"], r"^(user|official)/[a-z0-9-]+/[^/]+\.brush(set)?$")
            self.assertTrue(donor["entry"].endswith("/Brush.archive"))
            self.assertNotIn("Reset/", donor["entry"])
            self.assertNotIn("Sub01/", donor["entry"])

    def test_only_name_date_and_textures_are_replaced(self):
        library, donor_bytes = self.make_library(assign={"bundledShapePath": "Hard.png",
                                                         "bundledGrainPath": "Paper.jpg"})
        donor = bm.decode(donor_bytes)
        brush = bm.new_brush("Fresh Brush ", now=1700000000.0, library=library)
        self.assertEqual(brush.era, "M220")
        self.assertEqual(changed_keys(donor, brush),
                         ["bundledGrainPath", "bundledShapePath", "creationDate", "name"])
        self.assertEqual(brush.params["name"], "Fresh Brush ")
        self.assertEqual(brush.params["creationDate"], {"time": 1700000000.0 - bm.NS_EPOCH})
        self.assertIsNone(brush.params["bundledShapePath"])
        again = bm.decode(bm.encode(brush))
        self.assertEqual((again.era, again.fidelity, again.rebuild), ("M220", "byte", "exact"))
        self.assertEqual(changed_keys(brush, again), [])
        self.assertEqual(bm.export_state(brush), "canonical")

    def test_overrides_follow_the_patch_rules(self):
        library, _ = self.make_library()
        brush = bm.new_brush("N", now=0, library=library,
                             overrides={"plotSpacing": 0.25, "bundledShapePath": "Brush-Preset-Hard.png"})
        self.assertEqual((brush.params["plotSpacing"], brush.params["bundledShapePath"]),
                         (0.25, "Brush-Preset-Hard.png"))
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush("N", now=0, library=library, overrides={"blendMode": 99})
        self.assertEqual(caught.exception.code, "bad_override")

    def test_E4_is_selectable(self):
        library, _ = self.make_library(era="E4")
        brush = bm.new_brush("Legacy", era="E4", library=library)
        self.assertEqual((brush.era, brush.family, brush.params["name"]), ("E4", "legacy", "Legacy"))
        self.assertNotIn("creationDate", brush.params)

    def test_the_library_root_comes_from_the_environment(self):
        library, _ = self.make_library()
        os.environ[brush_common.ENV_LIBRARY] = str(library)
        self.assertEqual(bm.new_brush("Env", now=0).params["name"], "Env")

    def test_without_the_library_it_says_so(self):
        self.make_library()
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush("N", library=self.tmp / "no-library")
        self.assertEqual(caught.exception.code, "library_missing")
        self.assertIn("library", caught.exception.detail)
        empty = self.tmp / "empty"
        empty.mkdir()
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush("N", library=empty)
        self.assertEqual(caught.exception.code, "library_missing")

    def test_a_pointer_a_changed_file_and_a_wrong_era_are_refused(self):
        library, donor = self.make_library()
        path = library / "official" / "demo" / "demo.brushset"
        original = path.read_bytes()
        path.write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:00\nsize 1\n")
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush("N", library=library)
        self.assertEqual(caught.exception.code, "lfs_pointer")
        self.assertIn("git lfs pull", caught.exception.detail)
        path.write_bytes(original)
        bm.NEW_BRUSH_DONORS["M220"] = dict(bm.NEW_BRUSH_DONORS["M220"], archive_sha256="0" * 64)
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush("N", library=library)
        self.assertEqual(caught.exception.code, "donor_mismatch")
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush("N", era="E4", library=library)          # the donor is an M220 brush
        self.assertEqual(caught.exception.code, "donor_mismatch")
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush("N", era="M242", library=library)
        self.assertEqual(caught.exception.code, "bad_era")
        with self.assertRaises(BrushModelError) as caught:
            bm.new_brush(7, library=library)
        self.assertEqual(caught.exception.code, "bad_value")
        bm.NEW_BRUSH_DONORS["M220"] = dict(bm.NEW_BRUSH_DONORS["E4"])
        for now in ("soon", float("inf")):
            with self.assertRaises(BrushModelError) as caught:
                bm.new_brush("N", now=now, library=library)
            self.assertEqual(caught.exception.code, "bad_value")


# ── the library, read in memory ──────────────────────────────────────────────

class LibraryArchives(fixtures.BrushCase):
    def test_archives_are_read_in_memory_in_a_fixed_order(self):
        library = self.tmp / "library"
        (library / "user" / "b-pack" / "_docs").mkdir(parents=True)
        (library / "user" / "a-pack").mkdir(parents=True)
        one, two = bm.encode(bm.case_base("E1")), bm.encode(bm.case_base("E2"))
        (library / "user" / "b-pack" / "Set.brushset").write_bytes(zip_bytes([
            ("U1/Brush.archive", one), ("U1/Sub01/Brush.archive", two), ("U2/Brush.archive", two),
            ("U2/Brush.archive", one), ("../evil/Brush.archive", one), ("__MACOSX/U1/Brush.archive", one),
            ("U3/Brush.archive.txt", one),
            ("brushset.plist", plistlib.dumps({"brushes": ["U1", "U2", "U3"], "name": "Set"}))]))
        (library / "user" / "a-pack" / "Loose.brush").write_bytes(zip_bytes([("Brush.archive", one)]))
        (library / "user" / "b-pack" / "_docs" / "Doc.brush").write_bytes(zip_bytes([("Brush.archive", one)]))
        (library / "user" / "a-pack" / "notes.txt").write_text("x", encoding="utf-8")
        before = fixtures.tree_digest(library)
        found = list(bm.library_archives(library))
        self.assertEqual([label for label, _ in found], [
            "user/a-pack/Loose.brush :: Brush.archive",
            "user/b-pack/Set.brushset :: U1/Brush.archive",
            "user/b-pack/Set.brushset :: U1/Sub01/Brush.archive",
            "user/b-pack/Set.brushset :: U2/Brush.archive"])
        self.assertEqual([data for _, data in found], [one, one, two, two])
        self.assertEqual(fixtures.tree_digest(library), before)
        self.assertEqual(bm.read_library_archive(library, "user/b-pack/Set.brushset",
                                                 "U1/Sub01/Brush.archive"), two)

    def test_what_is_refused(self):
        library = self.tmp / "library"
        library.mkdir()
        (library / "big.brush").write_bytes(zip_bytes([("Brush.archive", bytes(bplist.MAX_BYTES + 1))]))
        with self.assertRaises(LimitExceeded) as caught:
            list(bm.library_archives(library))
        self.assertEqual(caught.exception.code, "archive_bytes")
        (library / "big.brush").write_bytes(b"not a zip")
        with self.assertRaises(BrushModelError) as caught:
            list(bm.library_archives(library))
        self.assertEqual(caught.exception.code, "bad_container")
        # The one reader's rules: a set whose plist is not a set's is not read.
        (library / "big.brush").unlink()
        (library / "Set.brushset").write_bytes(zip_bytes([
            ("U1/Brush.archive", bm.encode(bm.case_base("E1"))), ("brushset.plist", b"<plist/>")]))
        with self.assertRaises(BrushModelError) as caught:
            list(bm.library_archives(library))
        self.assertEqual(caught.exception.code, "bad_container")
        self.assertIn("bad_plist", caught.exception.detail)
        (library / "Set.brushset").write_bytes(b"version https://git-lfs.github.com/spec/v1\noid x\n")
        with self.assertRaises(BrushModelError) as caught:
            list(bm.library_archives(library))
        self.assertEqual(caught.exception.code, "lfs_pointer")
        with self.assertRaises(BrushModelError) as caught:
            list(bm.library_archives(self.tmp / "absent"))
        self.assertEqual(caught.exception.code, "library_missing")
        for name in ("../outside.brush", str(self.tmp / "abs.brush"), "a\\b.brush", "C:x.brush",
                     "/abs.brush", "a//b.brush", ""):
            with self.assertRaises(BrushModelError):
                bm.read_library_archive(library, name, "Brush.archive")

    def test_too_many_entries(self):
        library = self.tmp / "library"
        library.mkdir()
        entries = [(f"f{n}", b"") for n in range(bm.MAX_ZIP_ENTRIES + 1)]
        (library / "many.brushset").write_bytes(zip_bytes(entries))
        with self.assertRaises(LimitExceeded) as caught:
            list(bm.library_archives(library))
        self.assertEqual(caught.exception.code, "zip_entries")


# ── what is not a brush ──────────────────────────────────────────────────────

class NotABrush(unittest.TestCase):
    def test_bytes_that_are_not_a_property_list(self):
        with self.assertRaises(CodecError):
            bm.decode(b"not a plist")
        with self.assertRaises(CodecError):
            bm.decode(plistlib.dumps(["a"], fmt=plistlib.FMT_BINARY))

    def test_a_root_that_is_not_a_silica_brush(self):
        data = graph_archive([("name", "x")], chain=("SomethingElse", "NSObject"))
        with self.assertRaises(BrushModelError) as caught:
            bm.decode(data)
        self.assertEqual(caught.exception.code, "not_a_brush")

    def test_a_root_that_names_a_key_twice(self):
        data = graph_archive([("name", "x"), ("plotSpacing", Real.f32(0.1)),
                              ("plotSpacing", Real.f32(0.2))])
        with self.assertRaises(BrushModelError) as caught:
            bm.decode(data)
        self.assertEqual(caught.exception.code, "duplicate_key")

    def test_a_graph_that_names_one_entry_along_many_paths_is_refused_quickly(self):
        """A few hundred bytes whose instances each name the next one several
        times unfold into width ** levels values. One budget for the whole
        archive (the plist_objects cap) stops it, in time linear in the cap;
        it is never made `$opaque`, which is per root key."""
        def dag(width, levels):
            def build(objects):
                uid = len(objects)
                objects.append("leaf")
                uid = UID(uid)
                for _ in range(levels):
                    uid = instance(objects, ("Foo", "NSObject"), [(f"f{n}", uid) for n in range(width)])
                return [("foo", uid)]
            return graph_archive([("name", "x")], extra=build)

        for width, levels in ((3, 10), (4, 10), (8, 8), (40, 6), (100, 15)):
            data = dag(width, levels)
            self.assertLess(len(data), 20000)
            started = time.perf_counter()
            with self.assertRaises(LimitExceeded) as caught:
                bm.decode(data)
            self.assertEqual(caught.exception.code, "plist_objects")
            self.assertLess(time.perf_counter() - started, 5.0, (width, levels))
            result = bm.census([data])
            self.assertEqual((result["distinct"], len(result["unreadable"])), (0, 1))
            self.assertIn("plist_objects", result["unreadable"][0]["error"])
        small = bm.decode(dag(2, 4))                # 2 ** 4 paths is a form like any other
        self.assertEqual(json.dumps(small.params["foo"]).count('"leaf"'), 16)
        self.assertEqual(bm.MAX_FORM_VALUES, bplist.MAX_OBJECTS)

    def test_nesting_is_capped(self):
        def deep(objects):
            uid = instance(objects, ("Leaf", "NSObject"), [("v", 1)])
            for _ in range(bm.MAX_FORM_DEPTH + 3):
                uid = instance(objects, ("Box", "NSObject"), [("inner", uid)])
            return [("deep", uid)]

        brush = bm.decode(graph_archive([("name", "x")], extra=deep))
        self.assertEqual(json.dumps(brush.params["deep"]).count("$opaque"), 1)


# ── validate and export state ────────────────────────────────────────────────

class Validate(unittest.TestCase):
    def test_a_clean_build_has_no_warning(self):
        brush, _ = built("M220", {"name": "Named"})
        self.assertEqual([i for i in bm.validate(brush) if i.level != "info"], [])

    def test_an_unknown_era_is_named_with_its_nearest(self):
        brush, data = built("E3", {"futureKey": {"$int": 1}})
        issues = {issue.code: issue for issue in bm.validate(brush)}
        self.assertIn("unknown_era", issues)
        self.assertIn("E3", issues["unknown_era"].message)
        self.assertIn("unknown_key", issues)
        self.assertEqual((brush.era, brush.family), ("X89", "legacy"))
        self.assertIs(bm.encode(brush), data)
        patched, report = bm.apply_patch(brush, {"plotSpacing": 0.5})
        self.assertEqual(bm.export_state(patched), "valid")
        self.assertEqual(bm.decode(bm.encode(patched)).params["plotSpacing"], 0.5)

    def test_an_issue_has_its_four_fields(self):
        issue = bm.Issue("warning", "x", None, "m")
        self.assertEqual((issue.level, issue.code, issue.key, issue.message), ("warning", "x", None, "m"))


# ── census ───────────────────────────────────────────────────────────────────

class Census(unittest.TestCase):
    def sources(self):
        return [("one", bm.encode(bm.case_base("E3", {"name": "Secret Name"}))),
                ("two", bm.encode(bm.case_base("E3", {"name": "", "plotSpacing": 0.5}))),
                ("same", bm.encode(bm.case_base("E3", {"name": "", "plotSpacing": 0.5}))),
                ("three", bm.encode(bm.case_base("M220", {"authorName": "A Person"}))),
                ("broken", b"not an archive")]

    def test_a_census_counts_distinct_archives_by_era(self):
        result = bm.census(self.sources())
        self.assertEqual(result["schema"], bm.CENSUS_SCHEMA)
        self.assertEqual((result["archives"], result["distinct"]), (5, 3))
        self.assertEqual([u["label"] for u in result["unreadable"]], ["broken"])
        self.assertEqual([(e["id"], e["count"], e["family"]) for e in result["eras"]],
                         [("E3", 2, "legacy"), ("M220", 1, "modern")])
        self.assertEqual(result["eras"][0]["key_order"], era_row("E3")["key_order"])
        self.assertEqual(result["eras"][0]["rebuild"], {"exact": 2})
        spacing = result["keys"]["plotSpacing"]
        self.assertEqual((spacing["type"], spacing["count"], spacing["min"], spacing["max"]),
                         ("real", 3, 0.0, 0.5))
        self.assertEqual(spacing["eras"], {"E3": 2, "M220": 1})
        self.assertEqual(spacing["common"], [[0.0, 2], [0.5, 1]])
        self.assertEqual(spacing["default"], 0.0)
        self.assertEqual(result["keys"]["blendMode"]["nested"]["values"], {"0": 3})
        self.assertEqual(result["encode"]["legacy"]["conflicts"], [])

    def test_free_text_is_counted_and_never_listed(self):
        result = bm.census(self.sources())
        text = json.dumps(result)
        self.assertNotIn("Secret Name", text)
        self.assertNotIn("A Person", text)
        name = result["keys"]["name"]
        self.assertEqual(name["nested"]["text"], {"empty": 2, "text": 1})
        self.assertEqual(name["distinct"], 2)
        self.assertEqual(name["common"], [["", 2]])
        author = result["keys"]["authorName"]
        self.assertEqual((author["nested"]["text"], author["common"], author["default"]),
                         ({"text": 1}, [], None))

    def test_census_columns_have_the_schemas_shape(self):
        columns = bm.census_columns(bm.census(self.sources()))
        self.assertEqual(sorted(columns), ["classes", "encode_order", "eras", "keys"])
        row = columns["keys"]["plotSpacing"]
        self.assertEqual(sorted(row), ["default", "eras", "observed", "type"])
        self.assertEqual(sorted(row["observed"]), sorted(bm.OBSERVED_FIELDS))
        self.assertEqual(row["eras"], ["E3", "M220"])
        era = columns["eras"][0]
        for name in ("id", "family", "encode_family", "profile", "key_count", "key_order",
                     "top_order", "root_class", "optional_keys", "variants"):
            self.assertIn(name, era)
        self.assertEqual(columns["classes"]["ValkyrieMagnitudinalCurve"]["fields_by_family"],
                         {"legacy": ["points", "resolution", "$class"], "modern": ["points", "$class"]})

    def test_without_a_schema_eras_are_named_by_count(self):
        sources = self.sources()[:2]
        with mock.patch.object(bm, "SCHEMA_PATH", Path(os.devnull) / "absent.json"), \
                mock.patch.object(bm, "_LOADED", None):
            result = bm.census(sources)
        self.assertEqual([(e["id"], e["count"]) for e in result["eras"]], [("K88", 2)])
        self.assertEqual(result["keys"]["dynamicsPressureSizeCurve"]["type"], "curve_ref")
        self.assertEqual(result["keys"]["blendMode"]["type"], "int")

    def test_merge_orders(self):
        merged = bm.merge_orders([["a", "b", "d"], ["a", "c", "d"], [["x", "y"], "d"]])
        self.assertEqual(merged["order"], ["a", "b", "c", "x", "y", "d"])
        self.assertEqual(merged["conflicts"], [])
        self.assertIn(["b", "c"], merged["unproven"])
        self.assertEqual(bm.merge_orders([["a", "b"], ["b", "a"]])["conflicts"], [["a", "b"]])
        self.assertEqual(bm.merge_orders([["b", "a"], ["a", "c"]]),
                         bm.merge_orders([["a", "c"], ["b", "a"]]))


# ── spec.yaml ────────────────────────────────────────────────────────────────

@unittest.skipIf(yaml is None, "pyyaml is not installed")
class SpecAgreement(unittest.TestCase):
    def test_the_new_brush_era_is_the_specs(self):
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        self.assertEqual(spec["format"]["new_brush_era"], bm.NEW_BRUSH_ERA)
        self.assertEqual(spec["format"]["new_brush_eras"], list(bm.NEW_BRUSH_ERAS))
        self.assertEqual(spec["format"]["profiles"], sorted(bm.FAMILY_PROFILE.values()))
        self.assertEqual(spec["format"]["families"], list(bm.FAMILY_PROFILE))


# ── the real library (opt-in) ────────────────────────────────────────────────

@unittest.skipUnless(CORPUS, "set ROSW_BRUSHES_CORPUS to a library folder to walk the real brush files")
class RealLibrary(unittest.TestCase):
    """Every Brush.archive of the library rebuilt from its JSON parameters and
    the schema alone. 100 percent or a failure."""

    @classmethod
    def setUpClass(cls):
        if not sys.flags.isolated:
            raise AssertionError(
                "brush files are read only by an isolated interpreter. Run:  python -I -m unittest "
                "discover -s brushes/pipeline/tests -p test_brush_model.py")
        cls.root = Path(CORPUS).resolve()
        if not cls.root.is_dir():
            raise AssertionError(f"ROSW_BRUSHES_CORPUS is not a folder: {CORPUS}")
        cls.rows = collections.OrderedDict()
        cls.problems = collections.defaultdict(list)
        cls.samples = {}
        seen = {}
        for label, data in bm.library_archives(cls.root):
            digest = hashlib.sha256(data).digest()
            if digest not in seen:
                seen[digest] = cls.check(label, data)
            era, passed = seen[digest]
            row = cls.rows.setdefault(era, collections.Counter())
            row["archives"] += 1
            for name, ok in passed.items():
                row[name] += ok
        if not cls.rows:
            raise AssertionError(f"no .brush or .brushset file under {cls.root}")
        cls.total = collections.Counter()
        for row in cls.rows.values():
            cls.total.update(row)
        lines = ["", f"{'era':6} {'arch':>5} {'byte':>5} {'exact':>5} {'json':>5} {'source':>6}"]
        for era, row in list(cls.rows.items()) + [("TOTAL", cls.total)]:
            lines.append(f"{era:6} {row['archives']:5} {row['byte']:5} {row['exact']:5} "
                         f"{row['json']:5} {row['source']:6}")
        sys.stderr.write("\n".join(lines) + "\n")

    @classmethod
    def check(cls, label, data):
        passed = dict.fromkeys(("byte", "exact", "json", "source"), False)
        try:
            brush = bm.decode(data)
        except CodecError as exc:
            cls.problems["read"].append(f"{label}: {exc}")
            return "?", passed
        passed["byte"] = brush.fidelity == "byte"
        passed["exact"] = brush.rebuild == "exact"
        passed["source"] = bm.encode(brush) is brush.archive.source
        text = json.dumps(bm.to_json(brush), allow_nan=False, sort_keys=True)
        try:
            passed["json"] = bm.encode(bm.from_json(json.loads(text))) == data
        except CodecError as exc:
            cls.problems["json"].append(f"{label}: {exc}")
        for name, ok in passed.items():
            if not ok:
                cls.problems[name].append(label)
        cls.samples.setdefault(brush.era, (label, data))
        return brush.era, passed

    def all_pass(self, name):
        self.assertEqual(self.problems[name][:20], [], name)
        self.assertEqual(self.total[name], self.total["archives"], name)

    def test_it_found_archives(self):
        self.assertGreater(self.total["archives"], 0)
        self.assertEqual(self.problems["read"][:20], [])

    def test_every_archive_is_byte_and_exact(self):
        self.all_pass("byte")
        self.all_pass("exact")

    def test_the_json_parameters_and_the_schema_alone_rebuild_every_archive(self):
        self.all_pass("json")

    def test_an_unchanged_brush_exports_its_source(self):
        self.all_pass("source")

    def test_one_change_per_era_changes_one_key(self):
        for era, (label, data) in sorted(self.samples.items()):
            brush = bm.decode(data)
            patched, report = bm.apply_patch(brush, {"plotSpacing": 0.75})
            self.assertTrue(report["ok"], label)
            out = bm.encode(patched)
            plistlib.loads(out)
            again = bm.decode(out)
            self.assertEqual(changed_keys(brush, again), ["plotSpacing"], label)
            self.assertEqual((again.fidelity, again.profile, again.era),
                             ("byte", brush.profile, brush.era), label)

    def test_the_schemas_census_columns_are_not_stale(self):
        if self.root != (brush_common.TOOL_ROOT / "library").resolve():
            self.skipTest("the census columns describe the tool's own library/")
        fresh = bm.census_columns(bm.census(self.root))
        held = schema()
        rows = {row["key"]: row for row in held["keys"]}
        self.assertEqual(sorted(fresh["keys"]), sorted(rows))
        for key, column in fresh["keys"].items():
            if column["type"] is not None:
                self.assertEqual(rows[key]["type"], column["type"], key)
            for name in ("eras", "default", "observed"):
                self.assertEqual(rows[key][name], column[name], f"{key}.{name}")
        self.assertEqual(len(held["eras"]), len(fresh["eras"]))
        for mine, theirs in zip(held["eras"], fresh["eras"]):
            for name, value in theirs.items():
                self.assertEqual(mine[name], value, f"{mine['id']}.{name}")
        for family, order in fresh["encode_order"].items():
            guessed = held["encode_order"]["guessed"].get(family, [])
            self.assertEqual([k for k in held["encode_order"][family] if k not in guessed], order, family)
        for name, column in fresh["classes"].items():
            self.assertEqual(held["classes"][name]["fields_by_family"], column["fields_by_family"], name)
            self.assertEqual(held["classes"][name].get("chain"), column.get("chain"), name)

    def test_the_new_brush_donors_are_in_the_library(self):
        if self.root != (brush_common.TOOL_ROOT / "library").resolve():
            self.skipTest("the donors are files of the tool's own library/")
        for era in bm.NEW_BRUSH_ERAS:
            donor = bm.load_donor(era, library=self.root)
            self.assertEqual((donor.era, donor.fidelity, donor.rebuild), (era, "byte", "exact"))
            brush = bm.new_brush("ROSW test", era=era, now=1700000000.0, library=self.root)
            again = bm.decode(bm.encode(brush))
            self.assertEqual((again.era, again.fidelity, again.name), (era, "byte", "ROSW test"))
            self.assertEqual(changed_keys(donor, again),
                             sorted({"name", "creationDate", *bm.TEXTURE_KEYS} & set(donor.params)
                                    - {k for k in bm.TEXTURE_KEYS if donor.params.get(k) is None}))


if __name__ == "__main__":
    unittest.main()
