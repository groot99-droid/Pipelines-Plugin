"""schema/silica_keys.json: the one list of archive keys (docs/CONTRACTS.md F4).

The file is authored. Its census columns come from a census of the library
(the opt-in corpus test in test_brush_model.py compares them with a fresh
one); this file checks what holds without the library: the shape of every
row, that the eras' key lists agree with each other and with the rows, and
that spec.yaml declares the same eras, profiles and tabs.

    python -m unittest discover -s brushes/pipeline/tests
"""

import json
import re
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import brush_model  # noqa: E402
import keyed_archive  # noqa: E402

try:
    import yaml
except ImportError:                                 # pragma: no cover - CI installs it
    yaml = None

BRUSHES = PIPELINE.parent
SCHEMA_FILE = BRUSHES / "schema" / "silica_keys.json"

TOP_LEVEL = ["schema_version", "sources", "profiles", "eras", "classes", "encode_order", "groups",
             "keys"]
ROW_FIELDS = ["key", "type", "eras", "default", "limits", "limits_hard", "observed", "enum",
              "aliases", "retired", "replaced_by", "group", "section", "label", "confidence", "ui",
              "display", "step", "hint", "ai", "preview", "advanced", "notes"]
TABS = ["ai", "stroke", "stabilization", "taper", "shape", "grain", "dynamics", "pencil", "wetmix",
        "color", "rendering", "properties", "materials", "about"]
TYPES = ["real", "int", "bool", "string_ref", "data_ref", "curve_ref", "roll_ref", "array_ref",
         "date_ref"]
REFERENCE_TYPES = {"string_ref", "data_ref", "curve_ref", "roll_ref", "array_ref", "date_ref"}
UI = {"slider", "toggle", "select", "stepper", "curve", "text", "readonly", "hidden"}
DISPLAY = {"percent", "signedPercent", "factor", "raw", "enum"}
CONFIDENCE = {"verified", "inferred", "unknown"}
PREVIEW = {"honoured", "approx", "ignored"}
ERA_FIELDS = {"id", "family", "encode_family", "profile", "count", "key_count", "key_order",
              "top_order", "root_class", "versions", "optional_keys", "variants", "notes"}
# The widgets a type may be shown with.
UI_OF_TYPE = {"real": {"slider", "readonly", "hidden"}, "int": {"select", "stepper", "readonly", "hidden"},
              "bool": {"toggle", "readonly", "hidden"}, "string_ref": {"text", "readonly", "hidden"},
              "data_ref": {"readonly", "hidden"}, "curve_ref": {"curve", "readonly", "hidden"},
              "roll_ref": {"readonly", "hidden"}, "array_ref": {"readonly", "hidden"},
              "date_ref": {"readonly", "hidden"}}


def load():
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


class FileAndShape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SCHEMA_FILE.read_bytes()
        cls.schema = load()
        cls.rows = cls.schema["keys"]
        cls.by_key = {row["key"]: row for row in cls.rows}

    def test_the_file_is_utf8_lf_json_with_a_final_newline(self):
        self.assertFalse(self.raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r", self.raw)
        self.assertTrue(self.raw.endswith(b"}\n"))
        self.raw.decode("utf-8")

    def test_no_absolute_path_and_no_timestamp(self):
        text = self.raw.decode("utf-8")
        self.assertIsNone(re.search(r"[A-Za-z]:[\\/]|/Users/|/home/|\\\\", text))
        self.assertIsNone(re.search(r"\b20\d\d-\d\d-\d\dT\d\d:", text))

    def test_the_top_level_is_the_contracts(self):
        self.assertEqual(list(self.schema), TOP_LEVEL)
        self.assertEqual(self.schema["schema_version"], 1)
        self.assertEqual(sorted(self.schema["profiles"]), sorted(keyed_archive.PROFILES))
        sources = self.schema["sources"]
        self.assertGreater(sources["archives"], 0)
        self.assertLessEqual(sources["distinct"], sources["archives"])
        self.assertEqual(sources["census"], brush_model.CENSUS_SCHEMA)

    def test_groups_are_the_fourteen_tabs(self):
        groups = self.schema["groups"]
        self.assertEqual([g["id"] for g in groups], TABS)
        self.assertEqual([g["order"] for g in groups], list(range(len(TABS))))
        for group in groups:
            self.assertEqual(sorted(group), ["id", "label", "order"])
            self.assertTrue(group["label"].strip())

    def test_every_row_has_every_column_and_one_key(self):
        keys = [row["key"] for row in self.rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertNotIn("$class", keys)
        for row in self.rows:
            self.assertEqual(list(row), ROW_FIELDS, row["key"])

    def test_every_column_takes_its_values(self):
        for row in self.rows:
            key = row["key"]
            self.assertIn(row["type"], TYPES, key)
            self.assertIn(row["group"], TABS, key)
            self.assertIn(row["ui"], UI, key)
            self.assertIn(row["ui"], UI_OF_TYPE[row["type"]], key)
            self.assertIn(row["display"], DISPLAY, key)
            self.assertIn(row["confidence"], CONFIDENCE, key)
            self.assertIn(row["preview"], PREVIEW, key)
            for flag in ("limits_hard", "retired", "ai", "advanced"):
                self.assertIsInstance(row[flag], bool, f"{key}.{flag}")
            for text in ("section", "label"):
                self.assertTrue(isinstance(row[text], str) and row[text].strip(), f"{key}.{text}")
            for text in ("hint", "notes"):
                self.assertTrue(row[text] is None or (isinstance(row[text], str) and row[text].strip()),
                                f"{key}.{text}")
            self.assertTrue(row["eras"], key)
            self.assertIsInstance(row["observed"], dict, key)
            for name in brush_model.OBSERVED_FIELDS:
                self.assertIn(name, row["observed"], key)

    def test_a_limit_is_a_range_and_holds_only_when_verified(self):
        for row in self.rows:
            key, limits = row["key"], row["limits"]
            if row["type"] == "real":
                self.assertIsInstance(limits, list, key)
                self.assertEqual(len(limits), 2, key)
                self.assertLess(limits[0], limits[1], key)
                low, high = row["observed"]["min"], row["observed"]["max"]
                self.assertLessEqual(limits[0], low, key)
                self.assertLessEqual(high, limits[1], key)
                self.assertIsInstance(row["step"], (int, float), key)
                self.assertGreater(row["step"], 0, key)
            else:
                self.assertIsNone(limits, key)
            if row["limits_hard"]:
                self.assertEqual(row["confidence"], "verified", key)
                self.assertIsNotNone(limits, key)

    def test_an_int_key_is_an_enum_of_whole_numbers(self):
        for row in self.rows:
            key = row["key"]
            if row["type"] != "int":
                self.assertIsNone(row["enum"], key)
                continue
            enum = row["enum"]
            self.assertTrue(enum, key)
            for value, meaning in enum.items():
                self.assertRegex(value, r"^-?[0-9]+$", key)
                self.assertEqual(sorted(meaning), ["label", "verified"], key)
                self.assertIsInstance(meaning["verified"], bool, key)
            self.assertIn(str(row["default"]), enum, key)
            self.assertEqual(sorted(enum, key=int), sorted(row["observed"]["nested"]["values"], key=int),
                             key)
            self.assertEqual(row["display"], "enum", key)

    def test_defaults_are_values_of_their_type(self):
        for row in self.rows:
            key, kind, default = row["key"], row["type"], row["default"]
            if kind == "real":
                self.assertIsInstance(default, float, key)
            elif kind == "int":
                self.assertIs(type(default), int, key)
            elif kind == "bool":
                self.assertIsInstance(default, bool, key)
            elif kind == "string_ref":
                self.assertTrue(default is None or isinstance(default, str), key)
            elif kind == "curve_ref":
                self.assertEqual(sorted(default), ["points"], key)
                brush_model.canonical_curve(default["points"])
            elif kind == "roll_ref":
                self.assertEqual(sorted(default), sorted(["mode", "activationFalloff",
                                                          "activationOrigin", "activationRange"]), key)
            elif kind == "array_ref":
                self.assertIsInstance(default, list, key)
            elif kind == "date_ref":
                self.assertEqual(sorted(default), ["time"], key)
            elif kind == "data_ref":
                self.assertEqual(sorted(default), ["$data"], key)

    def test_free_text_is_never_listed(self):
        for key in brush_model.FREE_TEXT_KEYS:
            common = self.by_key[key]["observed"]["common"]
            self.assertTrue(all(value in ("", None) for value, _ in common), key)

    def test_aliases_name_one_setting_both_ways(self):
        """An alias is the same setting under another era's key (F4): the same
        type, named from both sides. A replacement whose mapping is unknown is
        `replaced_by`, never an alias."""
        for row in self.rows:
            for alias in row["aliases"]:
                self.assertIn(alias, self.by_key, row["key"])
                self.assertIn(row["key"], self.by_key[alias]["aliases"], row["key"])
                self.assertNotEqual(alias, row["key"])
                self.assertEqual(self.by_key[alias]["type"], row["type"], (row["key"], alias))
            for other in row["replaced_by"]:
                self.assertIn(other, self.by_key, row["key"])
        self.assertEqual(self.by_key["dynamicsGlazeFlow"]["aliases"], ["dynamicsGlazedFlow"])
        self.assertEqual(self.by_key["dynamicsRenderType"]["aliases"], [])
        self.assertEqual(sorted(self.by_key["dynamicsRenderType"]["replaced_by"]),
                         ["renderingMaxTransfer", "renderingModulatedTransfer", "renderingRecursiveMixing"])

    def test_no_preview_is_claimed_without_a_measurement(self):
        for row in self.rows:
            if row["preview"] == "honoured":
                self.assertIn("measure", (row["notes"] or "").lower(), row["key"])


class Eras(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load()
        cls.eras = cls.schema["eras"]
        cls.rows = {row["key"]: row for row in cls.schema["keys"]}

    def present(self, era):
        """Every key an era's archives may hold: its own and its variants'."""
        keys = set(era["key_order"])
        for variant in era["variants"]:
            keys.update(variant["key_order"])
        return keys

    def test_each_era_row_has_its_fields(self):
        for era in self.eras:
            self.assertEqual(set(era), ERA_FIELDS, era["id"])
            self.assertIn(era["family"], ("legacy", "modern"), era["id"])
            self.assertEqual(era["encode_family"], era["family"], era["id"])
            self.assertIn(era["profile"], self.schema["profiles"], era["id"])
            self.assertEqual(sorted(era["top_order"]), sorted(keyed_archive.ENVELOPE_KEYS), era["id"])
            self.assertEqual(era["root_class"][0], "SilicaBrush", era["id"])
            self.assertEqual(era["root_class"][-1], "NSObject", era["id"])
            self.assertGreater(era["count"], 0, era["id"])

    def test_every_key_list_is_consistent(self):
        sets = []
        for era in self.eras:
            order = era["key_order"]
            self.assertEqual(len(order), era["key_count"], era["id"])
            self.assertEqual(len(set(order)), len(order), era["id"])
            self.assertIn("$class", order, era["id"])
            variant_extra = set()
            for variant in era["variants"]:
                keys = variant["key_order"]
                self.assertEqual(len(keys), variant["key_count"], era["id"])
                self.assertEqual(len(set(keys)), len(keys), era["id"])
                self.assertLess(set(order), set(keys), era["id"])
                variant_extra.update(set(keys) - set(order))
                sets.append(frozenset(keys))
            self.assertEqual(era["optional_keys"], sorted(variant_extra), era["id"])
            sets.append(frozenset(order))
        self.assertEqual(len(sets), len(set(sets)), "two eras or variants share one key set")

    def test_only_M220_has_variants(self):
        self.assertEqual([era["id"] for era in self.eras if era["variants"]], ["M220"])
        m220 = next(era for era in self.eras if era["id"] == "M220")
        self.assertTrue(all(key.startswith("dynamicsPressure") for key in m220["optional_keys"]))
        self.assertEqual(m220["key_count"], 220)
        self.assertTrue(all(221 <= len(v["key_order"]) <= 223 for v in m220["variants"]))

    def test_rows_and_eras_agree(self):
        ids = [era["id"] for era in self.eras]
        listed = set()
        for era in self.eras:
            listed |= self.present(era)
        listed.discard("$class")
        self.assertEqual(listed, set(self.rows))
        for key, row in self.rows.items():
            expected = [era["id"] for era in self.eras if key in self.present(era)]
            self.assertEqual(row["eras"], expected, key)
            self.assertEqual(row["eras"], [e for e in ids if e in row["eras"]], key)

    def test_the_families_have_their_own_envelope_order(self):
        for era in self.eras:
            expected = (["$version", "$objects", "$archiver", "$top"] if era["family"] == "legacy"
                        else ["$version", "$archiver", "$top", "$objects"])
            self.assertEqual(era["top_order"], expected, era["id"])

    def test_a_retired_key_is_one_the_newest_era_has_dropped(self):
        newest = self.eras[-1]
        optional = {key for era in self.eras for key in era["optional_keys"]}
        for key, row in self.rows.items():
            dropped = key not in self.present(newest) and key not in optional
            self.assertEqual(row["retired"], dropped, key)

    def test_the_encode_order_lists_every_reference_key_of_its_family(self):
        encode = self.schema["encode_order"]
        self.assertEqual(sorted(encode), ["guessed", "legacy", "modern"])
        for family in ("legacy", "modern"):
            order = encode[family]
            self.assertEqual(len(order), len(set(order)), family)
            keys = set()
            for era in self.eras:
                if era["family"] == family:
                    keys |= self.present(era)
            expected = {key for key in keys - {"$class"} if self.rows[key]["type"] in REFERENCE_TYPES}
            self.assertEqual(set(order), expected, family)
            for key in encode["guessed"].get(family, []):
                self.assertIn(key, order, family)

    def test_brush_model_reads_the_eras_the_same_way(self):
        for era in self.eras:
            self.assertEqual(brush_model.detect_era(era["key_order"])[:2], (era["id"], True))


class Classes(unittest.TestCase):
    def test_each_class_has_its_chain_form_and_fields(self):
        classes = load()["classes"]
        self.assertEqual(classes["$class_entry"]["fields"], ["$classname", "$classes"])
        forms = []
        for name, spec in classes.items():
            if name.startswith("$"):
                continue
            self.assertEqual(spec["chain"][0], name)
            self.assertEqual(spec["chain"][-1], "NSObject")
            self.assertIn("$class", spec["fields"], name)
            forms.append(spec["form"])
            for family, fields in spec["fields_by_family"].items():
                self.assertIn(family, ("legacy", "modern"), name)
                self.assertEqual([f for f in spec["fields"] if f in fields], fields, name)
                missing = set(spec["fields"]) - set(fields)
                self.assertLessEqual(missing, set(spec.get("optional", ())), name)
        self.assertEqual(sorted(forms), sorted(set(forms)))
        self.assertEqual(sorted(forms), ["array", "curve", "date", "points", "roll", "string"])
        curve = classes["ValkyrieMagnitudinalCurve"]
        self.assertEqual(curve["resolution"], {"legacy": 1024, "modern": None})


@unittest.skipIf(yaml is None, "pyyaml is not installed")
class SpecAgreement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        cls.schema = load()

    def test_the_eras_are_the_specs(self):
        declared = self.spec["format"]
        eras = self.schema["eras"]
        self.assertEqual(declared["eras"], [era["id"] for era in eras])
        self.assertEqual(declared["era_keys"], {era["id"]: era["key_count"] for era in eras})
        self.assertEqual(declared["era_family"], {era["id"]: era["family"] for era in eras})
        self.assertLessEqual(set(declared["new_brush_eras"]), set(declared["eras"]))
        self.assertIn(declared["new_brush_era"], declared["eras"])

    def test_the_profiles_are_the_specs(self):
        self.assertEqual(sorted(self.spec["format"]["profiles"]), sorted(self.schema["profiles"]))
        used = {era["profile"] for era in self.schema["eras"]}
        self.assertEqual(used, set(self.schema["profiles"]))

    def test_the_tabs_are_the_specs(self):
        app = self.spec["surfaces"]["app"]
        self.assertEqual(app["tabs"], [group["id"] for group in self.schema["groups"]])
        self.assertEqual(app["tabs"], TABS)
        self.assertNotIn(app["library_tab"], app["tabs"])


if __name__ == "__main__":
    unittest.main()
