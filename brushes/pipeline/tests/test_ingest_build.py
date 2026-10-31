"""pipeline/ingest.py: `build`, `report`, the facets and apply_preview_results
(docs/CONTRACTS.md F5, F11 and F12).

Every test builds a small synthetic library in a temporary folder with
fixtures.py and builds its catalog there. None reads the real library or the
real catalog; schema/facets.json and spec.yaml are read as the code's own
assets.

    python -m unittest discover -s brushes/pipeline/tests
"""

import contextlib
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import fixtures  # noqa: E402
import identity  # noqa: E402
import ingest  # noqa: E402

BRUSHES = PIPELINE.parent
SCRIPT = PIPELINE / "ingest.py"
CATALOG_FILES = ("catalog.json", "textures.json", "thumbnails.json", "containers.json", "ingest_report.json")
TEXTURE_FACETS = ("shape_coverage", "shape_aspect", "shape_midtone", "shape_edge_touch", "grain_mean",
                  "grain_contrast")
MEASURED_WORDS = re.compile(r"^(shape-(even|wide|tall|hard|mixed|soft)|grain-(flat|subtle|medium|strong))$")


def spec_facet_names():
    """The `facets:` list of spec.yaml, read without pyyaml (it is a plain block list)."""
    text = (BRUSHES / "spec.yaml").read_text(encoding="utf-8")
    block = text.split("\nfacets:\n", 1)[1]
    names = []
    for line in block.splitlines():
        match = re.fullmatch(r"  - ([a-z_]+)", line)
        if not match:
            break
        names.append(match.group(1))
    return names


class BuildCase(fixtures.BrushCase):
    """A temporary data root holding the standard synthetic library."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "brushes"
        self.lib = fixtures.write_library(self.root / "library")
        self.library = self.root / "library"
        self.catalog = self.root / "catalog"
        self.paths = bc.resolve_paths(root=str(self.root))

    def main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ingest.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def build(self, *argv, root=None):
        code, out, err = self.main("build", "--root", str(root or self.root), *argv)
        self.assertEqual(code, bc.EXIT_OK, out + err)
        return out

    def read(self, relative, catalog=None):
        return json.loads((Path(catalog or self.catalog) / relative).read_text(encoding="utf-8"))

    def record(self, brush_id):
        return self.read(f"brushes/{brush_id}.json")

    def id_of(self, brush):
        return identity.brush_id(brush.archive, brush.shape, brush.grain, brush.subs)

    def write_sources(self, sources):
        with open(self.library / "sources.json", "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(sources, ensure_ascii=False, indent=2) + "\n")


# ── what is written ──────────────────────────────────────────────────────────

class WhatIsWritten(BuildCase):
    def test_the_catalog_files_of_f5(self):
        out = self.build()
        self.assertIn("8 brushes in 9 places", out)
        for name in CATALOG_FILES:
            self.assertTrue((self.catalog / name).is_file(), name)
        catalog = self.read("catalog.json")
        self.assertEqual(catalog["schema"], "rosw-brushes-catalog/1")
        self.assertEqual(catalog["ingest_version"], ingest.INGEST_VERSION)
        self.assertEqual(catalog["facet_rules_version"], ingest.load_facet_rules()["facet_rules_version"])
        self.assertRegex(catalog["library_fingerprint"], r"^sha256:16:[0-9a-f]{16}$")
        self.assertEqual(catalog["counts"], {"brushes": 8, "occurrences": 9, "sets": 3, "notes": 3,
                                             "packs": 2, "textures": catalog["counts"]["textures"],
                                             "by_library": {"user": 5, "official": 3}})
        ids = sorted(path.stem for path in (self.catalog / "brushes").glob("*.json"))
        self.assertEqual(ids, [row["id"] for row in catalog["brushes"]])
        slugs = sorted(path.stem for path in (self.catalog / "sets").glob("*.json"))
        self.assertEqual(slugs, ["demo-modern", "demo-pack-loose", "demo-set"])
        for row in catalog["sets"]:
            self.assertEqual(self.read(f"sets/{row['set_slug']}.json"), row, "the set file is its row")
        self.assertEqual(self.read("thumbnails.json"), {}, "previews.py fills it; build starts it empty")
        self.assertEqual(set(catalog["brushes"][0]), {
            "id", "name", "display_name", "home_set", "position", "library", "family", "era",
            "key_count", "facets", "facet_words", "preview", "occurrence_count"})
        self.assertEqual(set(catalog["sets"][0]), {
            "set_slug", "set_id", "name", "title", "kind", "library", "pack", "pack_kind",
            "brush_count", "note", "brushes"})

    def test_a_brush_record_has_the_f5_shape(self):
        self.build()
        inker = self.lib["user_set"]["brushes"][0]
        record = self.record(self.id_of(inker))
        self.assertEqual(set(record), {
            "schema", "id", "content_sha256", "name", "display_name", "slug", "library", "pack",
            "family", "era", "format", "home", "occurrences", "shape", "grain", "thumbnail",
            "secondary", "reset", "author", "settings", "facets", "facet_words", "preview", "warnings"})
        self.assertEqual(record["schema"], "rosw-brushes-brush/1")
        self.assertEqual(record["content_sha256"],
                         identity.content_sha256(inker.archive, inker.shape, inker.grain, inker.subs))
        self.assertEqual((record["library"], record["pack"], record["family"], record["era"]),
                         ("user", fixtures.USER_PACK, "legacy", "E4"))
        self.assertEqual(set(record["format"]), {"key_count", "version", "ref_size", "archive_bytes",
                                                 "archive_sha256", "classes"})
        self.assertEqual(record["format"]["archive_bytes"], len(inker.archive))
        self.assertEqual(record["format"]["classes"], list(fixtures.BRUSH_CHAIN))
        self.assertEqual(set(record["thumbnail"]), {"present", "sha256", "width", "height", "color_type"})
        self.assertEqual((record["thumbnail"]["width"], record["thumbnail"]["height"]), (53, 16))
        self.assertEqual(set(record["author"]), {"name", "has_picture", "has_signature", "creation_date"})
        self.assertEqual(record["settings"]["plotSpacing"], record["settings"]["plotSpacing"])
        self.assertIn("name", record["settings"])
        self.assertEqual(set(record["preview"]), {"stroke", "stroke_source", "shape", "shape_source",
                                                  "grain", "grain_source"})
        occurrence = record["occurrences"][0]
        self.assertEqual(set(occurrence), {"set_slug", "set_id", "position", "pack", "container",
                                           "container_sha256", "entry_prefix"})
        self.assertEqual(occurrence["container"], "user/demo-pack/Demo_Set.brushset")
        self.assertEqual(occurrence["entry_prefix"], inker.uuid + "/")

    def test_ids_are_identitys_and_names_are_verbatim(self):
        self.build()
        user = self.lib["user_set"]["brushes"]
        ids = [self.id_of(brush) for brush in user]
        row = self.read("sets/demo-set.json")
        self.assertEqual(row["brushes"], ids, "plist order")
        self.assertEqual(row["set_id"], identity.set_id(fixtures.USER_SET_NAME, ids))
        self.assertEqual(row["name"], "Demo Set ", "the trailing space is kept")
        self.assertEqual(row["title"], "Demo Set")
        self.assertEqual((row["kind"], row["library"], row["pack_kind"], row["brush_count"]),
                         ("set", "user", "vendor", 4))
        pencil = self.record(ids[1])
        self.assertEqual((pencil["name"], pencil["display_name"], pencil["slug"]),
                         ("Demo  Pencil", "Demo  Pencil", "demo-pencil"))
        official = self.read("sets/demo-modern.json")
        self.assertEqual(official["name"], fixtures.OFFICIAL_SET_NAME)
        self.assertEqual(official["title"], "Modern 1 (fixture)", "an official set takes the manifest's title")
        self.assertEqual((official["library"], official["pack_kind"], official["note"]),
                         ("official", "official", "01_Procreate_Defaults/demo-modern.md"))
        self.assertEqual(row["note"], "02_Vendor_Packs/demo-set.md")

    def test_two_brushes_with_one_name_in_one_set_are_two_ids(self):
        self.build()
        user = self.lib["user_set"]["brushes"]
        self.assertEqual(user[0].name, user[3].name)
        self.assertNotEqual(self.id_of(user[0]), self.id_of(user[3]))
        report = self.read("ingest_report.json")
        self.assertEqual(report["name_collisions"],
                         [{"set_slug": "demo-set", "name": "Demo Inker",
                           "ids": [self.id_of(user[0]), self.id_of(user[3])]}])

    def test_the_spelling_and_no_machine_paths(self):
        self.build()
        for path in sorted(self.catalog.rglob("*")):
            if not path.is_file():
                continue
            raw = path.read_bytes()
            self.assertNotIn(b"\r", raw, path.name)
            text = raw.decode("utf-8")
            self.assertEqual(text, bc.json_text(json.loads(text)), f"{path.name}: the one JSON spelling")
            self.assertNotIn(str(self.tmp), text)
            self.assertNotIn(self.tmp.as_posix(), text)
            self.assertNotIn(str(self.tmp).replace("\\", "\\\\"), text)

    def test_it_runs_isolated_from_any_directory(self):
        elsewhere = fixtures.temp_dir(self)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "build", "--root", str(self.root)],
                              cwd=str(elsewhere), env=env, capture_output=True, timeout=300)
        self.assertEqual(done.returncode, bc.EXIT_OK, done.stderr.decode("utf-8", "replace"))
        done = subprocess.run([sys.executable, "-I", str(SCRIPT), "report", "--root", str(self.root)],
                              cwd=str(elsewhere), env=env, capture_output=True, timeout=300)
        self.assertEqual(done.returncode, bc.EXIT_OK, done.stderr.decode("utf-8", "replace"))
        self.assertIn("8 (user 5, official 3)", done.stdout.decode("utf-8"))
        self.assertEqual(list(elsewhere.iterdir()), [])


# ── determinism ──────────────────────────────────────────────────────────────

class Determinism(BuildCase):
    def test_two_builds_are_the_same_bytes(self):
        self.build()
        first = fixtures.tree_digest(self.catalog)
        out = self.build()
        self.assertIn("WROTE     0 files changed, 0 removed", out)
        self.assertEqual(fixtures.tree_digest(self.catalog), first)

    def test_another_folder_and_another_write_order_give_the_same_bytes(self):
        self.build()
        other = self.tmp / "elsewhere" / "deeper" / "brushes"
        (other / "library").mkdir(parents=True)
        files = sorted(self.lib["files"].items(), reverse=True)        # written in the other order
        for relative, data in files:
            target = other / "library" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        shutil.copyfile(self.library / "sources.json", other / "library" / "sources.json")
        self.build(root=other)
        self.assertEqual(fixtures.tree_digest(other / "catalog"), fixtures.tree_digest(self.catalog))

    def test_a_stale_record_is_removed_by_a_full_build(self):
        self.build()
        stale = self.catalog / "brushes" / "b_000000000000.json"
        stale.write_text("{}\n", encoding="utf-8")
        (self.catalog / "sets" / "gone.json").write_text("{}\n", encoding="utf-8")
        out = self.build()
        self.assertIn("2 removed", out)
        self.assertFalse(stale.exists())
        self.assertFalse((self.catalog / "sets" / "gone.json").exists())


# ── duplicates, loose sets, dual brushes, Reset, textures ────────────────────

class Placement(BuildCase):
    def test_a_duplicate_is_one_record_with_its_home_in_the_real_set(self):
        self.build()
        inker = self.lib["user_set"]["brushes"][0]
        record = self.record(self.id_of(inker))
        self.assertEqual(record["home"], {"set_slug": "demo-set", "position": 1})
        self.assertEqual([(o["set_slug"], o["position"], o["container"]) for o in record["occurrences"]],
                         [("demo-set", 1, "user/demo-pack/Demo_Set.brushset"),
                          ("demo-pack-loose", 1, "user/demo-pack/Demo_Inker.brush")])
        self.assertEqual(record["occurrences"][1]["entry_prefix"], "")
        report = self.read("ingest_report.json")
        self.assertEqual([row["id"] for row in report["duplicates"]], [record["id"]])
        self.assertEqual(report["duplicates"][0]["occurrences"], ["demo-set#1", "demo-pack-loose#1"])
        row = [r for r in self.read("catalog.json")["brushes"] if r["id"] == record["id"]][0]
        self.assertEqual(row["occurrence_count"], 2)

    def test_the_loose_pseudo_set(self):
        self.build()
        row = self.read("sets/demo-pack-loose.json")
        members = [self.id_of(self.lib["loose"][0]["brush"]), self.id_of(self.lib["loose"][1]["brush"])]
        self.assertEqual(row["brushes"], members, "Demo_Inker.brush before Loose_Marker.brush")
        self.assertEqual((row["kind"], row["name"], row["title"]),
                         ("loose", "demo-pack-loose", "Demo Pack (loose brushes)"))
        self.assertEqual(row["set_id"], identity.set_id("demo-pack-loose", members))
        self.assertEqual(row["note"], "03_Loose/demo-pack-loose.md")
        self.assertEqual(self.record(members[1])["home"], {"set_slug": "demo-pack-loose", "position": 2})

    def test_a_pseudo_set_with_no_home_brush_keeps_its_row_and_has_no_note(self):
        (self.library / "user" / fixtures.USER_PACK / "Loose_Marker.brush").unlink()
        self.build()
        row = self.read("sets/demo-pack-loose.json")
        self.assertIsNone(row["note"])
        self.assertEqual(row["brush_count"], 1)
        counts = self.read("catalog.json")["counts"]
        self.assertEqual((counts["sets"], counts["notes"], counts["brushes"]), (3, 2, 7))

    def test_a_dual_brush_carries_its_secondary_and_it_is_not_counted(self):
        self.build()
        dual = self.lib["official_set"]["brushes"][0]
        record = self.record(self.id_of(dual))
        secondary = record["secondary"]
        self.assertEqual(set(secondary), {"name", "component_sha256", "era", "settings", "shape", "grain"})
        sub_archive, sub_shape, sub_grain = dual.subs[0]
        self.assertEqual(secondary["component_sha256"],
                         identity.content_sha256(sub_archive, sub_shape, sub_grain))
        self.assertEqual((secondary["name"], secondary["era"]), ("Modern Dual Secondary", "M220"))
        self.assertEqual(secondary["shape"]["source"], "embedded")
        self.assertEqual(secondary["shape"]["texture_id"], identity.texture_id(sub_shape))
        self.assertEqual(secondary["grain"]["source"], "blank")
        self.assertIs(record["facets"]["dual"], True)
        self.assertIn("dual", record["facet_words"])
        self.assertEqual(self.read("catalog.json")["counts"]["brushes"], 8, "a secondary is no brush")
        textures = self.read("textures.json")
        self.assertIn("shape", textures[identity.texture_id(sub_shape)]["used_as"])

    def test_a_reset_tree_is_described_and_never_a_brush(self):
        self.build()
        dual = self.lib["official_set"]["brushes"][0]
        reset = self.record(self.id_of(dual))["reset"]
        self.assertEqual(set(reset), {"archive_sha256", "same_as_live", "differing_keys", "differing_count",
                                      "has_secondary", "thumbnail_sha256"})
        self.assertIs(reset["same_as_live"], False)
        self.assertIn("paintSize", reset["differing_keys"])
        self.assertIs(reset["has_secondary"], True)
        self.assertRegex(reset["thumbnail_sha256"], r"^[0-9a-f]{64}$")
        self.assertIsNone(self.record(self.id_of(self.lib["user_set"]["brushes"][0]))["reset"])

    def test_textures_embedded_named_and_bundled_only(self):
        self.build()
        textures = self.read("textures.json")
        pencil = self.record(self.id_of(self.lib["user_set"]["brushes"][1]))
        self.assertEqual(pencil["shape"], {"source": "bundled", "bundled_name": fixtures.BUNDLED_SHAPE,
                                           "texture_id": None, "inverted": False})
        self.assertEqual(pencil["grain"]["source"], "blank")
        self.assertEqual(pencil["grain"]["bundled_name"], fixtures.BLANK_GRAIN)
        self.assertIsNone(pencil["grain"]["texture_id"])
        self.assertIn("shape-bundled", pencil["facet_words"])
        self.assertIn("grain-blank", pencil["facet_words"])
        earth_brush = self.lib["official_set"]["brushes"][2]
        earth = self.record(self.id_of(earth_brush))
        self.assertEqual(earth["shape"]["source"], "embedded", "a texture kept under its own name")
        self.assertEqual(earth["shape"]["texture_id"], identity.texture_id(earth_brush.shape))
        self.assertEqual(earth["shape"]["bundled_name"], earth_brush.bundled_shape)
        held = textures[earth["shape"]["texture_id"]]
        self.assertEqual(set(held), {"sha256", "width", "height", "used_as", "shape_tiles", "grain_tile", "stats"})
        self.assertEqual((held["width"], held["height"], held["used_as"]), (8, 8, ["shape"]))
        self.assertEqual((held["shape_tiles"], held["grain_tile"], held["stats"]),
                         ({"n": None, "i": None}, None, None))
        report = self.read("ingest_report.json")
        self.assertEqual(report["bundled_textures"]["shape"][fixtures.BUNDLED_SHAPE], 2)
        self.assertIn(fixtures.BLANK_GRAIN, report["bundled_textures"]["grain"])

    def test_a_file_outside_every_pack_is_unsorted(self):
        stray = fixtures.make_brush("Stray", number=40)
        (self.library / "Stray.brush").write_bytes(fixtures.brush_file(stray))
        self.build()
        row = self.read("sets/unsorted-loose.json")
        self.assertEqual((row["pack"], row["kind"], row["pack_kind"], row["note"]),
                         ("unsorted", "loose", "vendor", "03_Loose/unsorted-loose.md"))
        report = self.read("ingest_report.json")
        self.assertTrue(any(w["where"] == "Stray.brush" and "unsorted" in w["message"]
                            for w in report["warnings"]))
        self.assertIn("unsorted", [pack["id"] for pack in self.read("catalog.json")["packs"]])


# ── refusals ─────────────────────────────────────────────────────────────────

class Refusals(BuildCase):
    def test_two_sets_with_one_slug_is_exit_1_and_writes_nothing(self):
        other = fixtures.brushset_file("Demo Set", [fixtures.make_brush("Other", number=30)])
        (self.library / "user" / fixtures.USER_PACK / "Other.brushset").write_bytes(other)
        code, out, _ = self.main("build", "--root", str(self.root))
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("two sets have the slug 'demo-set'", out)
        self.assertFalse(self.catalog.exists())

    def test_something_skipped_is_listed_and_strict_makes_it_exit_1(self):
        bad = fixtures.hostile_files()["truncated-archive.brush"]
        (self.library / "user" / fixtures.USER_PACK / "Broken.brush").write_bytes(bad)
        code, out, _ = self.main("build", "--strict", "--root", str(self.root))
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("--strict", out)
        self.assertFalse(self.catalog.exists(), "nothing is written")
        self.build()
        report = self.read("ingest_report.json")
        self.assertEqual([row["where"] for row in report["skipped"]], ["user/demo-pack/Broken.brush"])
        self.assertEqual(self.read("catalog.json")["counts"]["brushes"], 8)

    def test_a_pointer_a_missing_library_and_a_missing_catalog_are_exit_2(self):
        code, _, err = self.main("build", "--root", str(self.tmp / "nowhere"))
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("no library folder", err)
        code, _, err = self.main("report", "--root", str(self.root))
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("run `ingest.py build` first", err)
        (self.library / "user" / fixtures.USER_PACK / "Pointer.brush").write_bytes(fixtures.LFS_POINTER)
        code, _, err = self.main("build", "--root", str(self.root))
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("git lfs pull", err)
        self.assertFalse(self.catalog.exists())

    def test_build_never_reads_docs_bundled_or_part_files(self):
        docs = self.library / "user" / fixtures.USER_PACK / "_docs"
        docs.mkdir()
        (docs / "Copy.brush").write_bytes(fixtures.brush_file(fixtures.make_brush("In Docs", number=41)))
        (self.library / "user" / fixtures.USER_PACK / "Half.brush.part").write_bytes(b"PK\x03\x04")
        self.build()
        self.assertEqual(self.read("catalog.json")["counts"]["brushes"], 8)
        self.assertEqual(self.read("ingest_report.json")["skipped"], [])


# ── --only ───────────────────────────────────────────────────────────────────

class Only(BuildCase):
    def test_only_writes_the_records_of_one_set_or_pack(self):
        self.build()
        official_ids = self.read("sets/demo-modern.json")["brushes"]
        user_ids = self.read("sets/demo-set.json")["brushes"]
        for brush_id in official_ids + user_ids[:1]:
            (self.catalog / "brushes" / f"{brush_id}.json").unlink()
        out = self.build("--only", "demo-official")
        self.assertIn("--only demo-official: 3 brush records, 1 sets", out)
        for brush_id in official_ids:
            self.assertTrue((self.catalog / "brushes" / f"{brush_id}.json").is_file())
        self.assertFalse((self.catalog / "brushes" / f"{user_ids[0]}.json").exists(),
                         "a record outside --only is neither written nor removed")
        self.build("--only", "demo-set")
        self.assertTrue((self.catalog / "brushes" / f"{user_ids[0]}.json").is_file())

    def test_only_with_an_unknown_name_is_exit_2(self):
        code, _, err = self.main("build", "--only", "no-such-set", "--root", str(self.root))
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("no-such-set", err)


# ── the preview-derived fields ───────────────────────────────────────────────

class PreviewFields(BuildCase):
    def test_before_previews_the_record_is_in_its_pre_preview_form(self):
        self.build()
        for path in sorted((self.catalog / "brushes").glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            preview = record["preview"]
            self.assertEqual((preview["stroke"], preview["shape"], preview["grain"]), (None, None, None))
            self.assertEqual(preview["shape_source"], record["shape"]["source"])
            self.assertEqual(preview["grain_source"], record["grain"]["source"])
            for name in TEXTURE_FACETS:
                self.assertIsNone(record["facets"][name], name)
            self.assertFalse([word for word in record["facet_words"] if MEASURED_WORDS.match(word)])
            if record["grain"]["source"] == "embedded":
                self.assertIs(record["facets"]["has_grain"], True)
        plain = self.record(self.id_of(self.lib["official_set"]["brushes"][1]))
        self.assertEqual(plain["preview"]["stroke_source"], "none")
        self.assertIn("no-thumbnail", plain["facet_words"])
        self.assertEqual(self.record(self.id_of(self.lib["user_set"]["brushes"][0]))["preview"]["stroke_source"],
                         "thumbnail")

    def measure(self, record, contrast):
        """What previews.py would leave behind for one brush."""
        thumbnails = {record["id"]: {"source_sha256": record["thumbnail"]["sha256"],
                                     "stroke": f"_Previews/demo-set/{record['id']}.stroke.png",
                                     "stroke_source": "thumbnail", "alpha_max": 255, "alpha_hi": 200,
                                     "gain": 1.27, "ink_fraction": 0.2, "bbox": [0, 0, 53, 16]}}
        textures = self.read("textures.json")
        shape_id, grain_id = record["shape"]["texture_id"], record["grain"]["texture_id"]
        textures[shape_id]["shape_tiles"] = {"n": f"_Previews/_textures/{shape_id}.n.shape.png",
                                             "i": f"_Previews/_textures/{shape_id}.i.shape.png"}
        textures[shape_id]["stats"] = {"shape": {
            "n": {"coverage": 0.612345, "aspect": 1.0, "midtone": 0.1, "edge_touch": 0.0},
            "i": {"coverage": 0.38, "aspect": 2.0, "midtone": 0.9, "edge_touch": 0.5}}, "grain": None}
        textures[grain_id]["grain_tile"] = f"_Previews/_textures/{grain_id}.grain.png"
        textures[grain_id]["stats"] = {"shape": None, "grain": {"mean": 0.5, "contrast": contrast}}
        bc.write_json(self.catalog / "thumbnails.json", thumbnails)
        bc.write_json(self.catalog / "textures.json", textures)

    def test_apply_preview_results_fills_the_three_fields_and_nothing_else(self):
        self.build()
        inker = self.id_of(self.lib["user_set"]["brushes"][0])
        before = self.record(inker)
        others = {path.name: path.read_bytes() for path in (self.catalog / "brushes").glob("*.json")
                  if path.stem != inker}
        self.measure(before, contrast=0.3)
        self.assertEqual(ingest.apply_preview_results(self.paths), 1)
        after = self.record(inker)
        self.assertEqual({k: v for k, v in after.items() if k not in ("facets", "facet_words", "preview")},
                         {k: v for k, v in before.items() if k not in ("facets", "facet_words", "preview")})
        self.assertEqual(after["preview"]["stroke"], f"_Previews/demo-set/{inker}.stroke.png")
        self.assertEqual(after["preview"]["shape"],
                         f"_Previews/_textures/{after['shape']['texture_id']}.n.shape.png", "not inverted")
        self.assertEqual(after["preview"]["grain"],
                         f"_Previews/_textures/{after['grain']['texture_id']}.grain.png")
        facets = after["facets"]
        self.assertEqual((facets["shape_coverage"], facets["shape_aspect"], facets["shape_midtone"]),
                         (0.6123, 1.0, 0.1), "rounded to 4 places")
        self.assertEqual((facets["grain_mean"], facets["grain_contrast"]), (0.5, 0.3))
        for word in ("shape-even", "shape-hard", "grain-strong"):
            self.assertIn(word, after["facet_words"])
        for path in (self.catalog / "brushes").glob("*.json"):
            if path.stem != inker:
                self.assertEqual(path.read_bytes(), others[path.name], "no other record changes")
        row = [r for r in self.read("catalog.json")["brushes"] if r["id"] == inker][0]
        self.assertEqual((row["facets"], row["facet_words"], row["preview"]),
                         (after["facets"], after["facet_words"], after["preview"]), "catalog rows are copies")
        self.assertEqual(ingest.apply_preview_results(self.paths), 0, "equal text is not written again")

    def test_a_flat_embedded_grain_has_no_grain_once_measured(self):
        self.build()
        inker = self.id_of(self.lib["user_set"]["brushes"][0])
        self.measure(self.record(inker), contrast=0.005)
        ingest.apply_preview_results(self.paths)
        record = self.record(inker)
        self.assertIs(record["facets"]["has_grain"], False)
        self.assertIn("grain-flat", record["facet_words"])

    def test_a_stale_thumbnail_entry_is_the_pre_preview_form_and_a_rebuild_keeps_measurements(self):
        self.build()
        inker = self.id_of(self.lib["user_set"]["brushes"][0])
        self.measure(self.record(inker), contrast=0.3)
        ingest.apply_preview_results(self.paths)
        measured = self.record(inker)
        thumbnails = (self.catalog / "thumbnails.json").read_bytes()
        self.build()
        self.assertEqual(self.record(inker), measured, "a rebuild keeps what was measured")
        self.assertEqual((self.catalog / "thumbnails.json").read_bytes(), thumbnails, "left as it is")
        self.assertIsNotNone(self.read("textures.json")[measured["grain"]["texture_id"]]["stats"])
        stale = self.read("thumbnails.json")
        stale[inker]["source_sha256"] = "0" * 64
        bc.write_json(self.catalog / "thumbnails.json", stale)
        ingest.apply_preview_results(self.paths)
        record = self.record(inker)
        self.assertIsNone(record["preview"]["stroke"])
        self.assertIsNone(record["facets"]["grain_contrast"])
        self.assertEqual(record["preview"]["stroke_source"], "thumbnail")


# ── the facet rules ──────────────────────────────────────────────────────────

class FacetRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = ingest.load_facet_rules()

    def facets(self, params, rules=None, **given):
        values = {"era": "E4", "family": "legacy", "shape_source": "embedded", "grain_source": "embedded",
                  "dual": False, "stroke_source": "thumbnail"}
        values.update(given)
        return ingest.compute_facets(ingest.FacetInput(params=params, **values), rules or self.rules)

    def test_the_names_agree_with_the_spec_the_file_and_the_code(self):
        names = spec_facet_names()
        self.assertEqual(len(names), 52)
        self.assertEqual(list(self.rules["facets"]), names, "schema/facets.json, in the spec's order")
        self.assertEqual(list(ingest.FACET_FUNCTIONS), names, "one function per facet")
        self.assertTrue(set(self.rules["word_order"]) <= set(names))
        for name, rule in self.rules["facets"].items():
            self.assertIsInstance(rule.get("rule"), str, name)
        self.assertEqual(self.rules["schema"], "rosw-brushes-facets/1")
        self.assertEqual(self.facets({}).keys(), set(names))

    def test_a_file_that_names_other_facets_is_refused(self):
        tmp = Path(fixtures.temp_dir(self))
        broken = copy.deepcopy(self.rules)
        broken["facets"]["sparkle"] = {"rule": "made up"}
        bc.write_json(tmp / "facets.json", broken)
        with self.assertRaises(ingest.EnvironmentProblem) as raised:
            ingest.load_facet_rules(tmp / "facets.json")
        self.assertIn("sparkle", str(raised.exception))

    def test_thresholds_are_read_from_the_file(self):
        params = {"plotSpacing": 0.05}
        self.assertEqual(self.facets(params)["spacing_class"], "tight")
        tmp = Path(fixtures.temp_dir(self))
        moved = copy.deepcopy(self.rules)
        moved["facets"]["spacing_class"]["classes"][0]["upto"] = 0.06
        moved["facets"]["tilt"]["above"] = 0.5
        bc.write_json(tmp / "facets.json", moved)
        loaded = ingest.load_facet_rules(tmp / "facets.json")
        self.assertEqual(self.facets(params, loaded)["spacing_class"], "continuous")
        self.assertIs(self.facets({"dynamicsTiltSize": 0.3})["tilt"], True)
        self.assertIs(self.facets({"dynamicsTiltSize": 0.3}, loaded)["tilt"], False)

    def test_class_boundaries(self):
        cases = [
            ("spacing_class", {"plotSpacing": 0.02}, "continuous"),
            ("spacing_class", {"plotSpacing": 0.0201}, "tight"),
            ("spacing_class", {"plotSpacing": 0.1}, "tight"),
            ("spacing_class", {"plotSpacing": 0.5}, "visible"),
            ("spacing_class", {"plotSpacing": 0.51}, "dotted"),
            ("pressure_size_class", {"dynamicsPressureSize": -0.03}, "inverse"),
            ("pressure_size_class", {"dynamicsPressureSize": -0.02}, "none"),
            ("pressure_size_class", {"dynamicsPressureSize": 0.02}, "low"),
            ("pressure_size_class", {"dynamicsPressureSize": 0.35}, "medium"),
            ("pressure_size_class", {"dynamicsPressureSize": 0.7}, "high"),
            ("pressure_opacity_class", {"dynamicsPressureOpacity": 0.5}, "medium"),
            ("size_class", {"maxSize": 1.0}, "fine"),
            ("size_class", {"maxSize": 6.0}, "medium"),
            ("size_class", {"maxSize": 12.0}, "broad"),
            ("size_class", {"maxSize": 12.5}, "max"),
            ("grain_movement", {"textureMovement": 0.0}, "static"),
            ("grain_movement", {"textureMovement": 0.5}, "partial"),
            ("grain_movement", {"textureMovement": 0.999}, "rolling"),
            ("taper", {"taperStartLength": 0.02}, "start"),
            ("taper", {"pencilTaperEndLength": 0.5}, "end"),
            ("taper", {"taperStartLength": 0.01, "taperEndLength": 0.2, "pencilTaperStartLength": 0.3}, "both"),
            ("taper", {"taperStartLength": 0.01}, "none"),
            ("translucent", {"maxOpacity": 0.998}, True),
            ("translucent", {"maxOpacity": 0.999}, False),
            ("speed", {"dynamicsSpeedOpacity": -0.5}, True),
            ("tilt", {"dynamicsTiltBleed": 0.02}, False),
            ("shape_rotation", {"shapeRotation": -1.0}, True),
            ("color_dynamics", {"dynamicsJitterHue": 0.0, "dynamicsTiltSecondaryColor": 0.1}, True),
            ("kind", {"stamp": True}, "stamp"),
            ("kind", {}, "stroke"),
            ("spacing", {"plotSpacing": 0.10000000149011612}, 0.1),
        ]
        for name, params, wanted in cases:
            with self.subTest(name=name, params=params):
                self.assertEqual(self.facets(params)[name], wanted)

    def test_wet_mix_and_the_render_code_by_era(self):
        legacy = {"dynamicsRenderType": 3, "dynamicsMix": 0.0}
        self.assertIs(self.facets(legacy)["wet_mix"], True)
        self.assertEqual(self.facets(legacy)["render_code"], "render-type-3")
        mixed = {"dynamicsRenderType": 2, "dynamicsMix": 0.5}
        self.assertIs(self.facets(mixed)["wet_mix"], False, "the render key decides when it exists")
        e0 = {"dynamicsGlazeType": 1, "dynamicsMix": 0.5}
        facets = self.facets(e0, era="E0")
        self.assertEqual((facets["render_code"], facets["wet_mix"]), ("glaze-type-1", True))
        modern = {"renderingMaxTransfer": True, "renderingModulatedTransfer": False,
                  "renderingRecursiveMixing": True, "dynamicsMix": 0.0}
        facets = self.facets(modern, era="M220", family="modern")
        self.assertEqual((facets["render_code"], facets["wet_mix"]), ("transfer-max.flat.rec", False))
        self.assertIsNone(self.facets({})["render_code"])

    def test_a_tagged_real_is_read_as_its_number_and_an_absent_key_as_none(self):
        facets = self.facets({"plotSpacing": {"$real32": "80000000"}, "dynamicsPressureSize": {"$real64": 0.5}})
        self.assertEqual(facets["spacing"], 0.0, "negative zero is zero")
        self.assertEqual(facets["pressure_size"], 0.5)
        self.assertIsNone(self.facets({})["size_max"])
        self.assertIsNone(self.facets({})["size_class"])
        self.assertIsNone(self.facets({})["blend_code"])

    def test_sources_and_words(self):
        facets = self.facets({"blendMode": 5, "plotSpacing": 0.3}, shape_source="bundled-supplied",
                             grain_source="blank", dual=True, stroke_source="none", era="M220")
        self.assertIs(facets["uses_bundled_shape"], True)
        self.assertIs(facets["uses_bundled_grain"], True)
        self.assertIs(facets["has_grain"], False)
        words = ingest.facet_words(facets, self.rules)
        for word in ("stroke", "spacing-visible", "shape-bundled", "grain-blank", "dual", "blend-5",
                     "era-m220", "no-thumbnail"):
            self.assertIn(word, words)
        self.assertNotIn("blend-0", ingest.facet_words(self.facets({"blendMode": 0}), self.rules))
        self.assertNotIn("taper-none", ingest.facet_words(self.facets({}), self.rules))
        self.assertNotIn("pressure-size-none", ingest.facet_words(self.facets({}), self.rules))
        self.assertEqual(words, [word for name in self.rules["word_order"] for word in words
                                 if word in ingest.facet_words({name: facets[name]}, self.rules)],
                         "words follow word_order")
        bundled = self.facets({}, grain_source="bundled")
        self.assertIs(bundled["has_grain"], True)


if __name__ == "__main__":
    unittest.main()
