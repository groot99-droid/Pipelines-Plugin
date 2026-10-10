"""pipeline/ingest.py: `where` and `adopt` (docs/CONTRACTS.md, F11 and F12).

Every test builds its own source folder and its own library in a temporary
folder, from the synthetic brush files in fixtures.py. None reads the real
library or the author's own brush files. The real library/sources.json is read
once, as text, to check that its patterns sort a list of file NAMES the way the
manifest says; no brush file is opened for that.

    python -m unittest discover -s brushes/pipeline/tests
"""

import contextlib
import hashlib
import io
import json
import os
import plistlib
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import fixtures  # noqa: E402
import identity  # noqa: E402
import ingest  # noqa: E402

BRUSHES = PIPELINE.parent
SCRIPT = PIPELINE / "ingest.py"
PACK = fixtures.USER_PACK
DRY_RUN = "DRY RUN   nothing is written without --confirm."
PDF = b"%PDF-1.4\n% a fixture, not a document\n"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF fixture"


def sha(data):
    return hashlib.sha256(data).hexdigest()


class AdoptCase(fixtures.BrushCase):
    """A temporary data root with a manifest, and a temporary folder to adopt from."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "brushes"
        self.library = self.root / "library"
        self.library.mkdir(parents=True)
        self.sources = fixtures.standard_sources()
        self.write_sources()
        self.src = self.tmp / "downloads" / "procreate brushes"
        self.src.mkdir(parents=True)
        brushes = fixtures.standard_user_brushes()
        self.set_bytes = fixtures.brushset_file(fixtures.USER_SET_NAME, brushes)
        self.inker = fixtures.brush_file(brushes[0])
        self.marker = fixtures.brush_file(fixtures.make_brush("Loose Marker", era="E1b", number=5,
                                                              grain="bundled"))
        self.stray = fixtures.brush_file(fixtures.make_brush("Stray", number=6))

    def write_sources(self):
        with open(self.library / "sources.json", "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(self.sources, ensure_ascii=False, indent=2) + "\n")

    def put(self, relative, data, under=None):
        target = (under or self.src) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return target

    def small_corpus(self):
        """The shape of a real download folder, in small: an unpacked pack with a
        set, a loose brush, documents and artwork; the vendor's zip of the same
        files beside it; and one brush that belongs to no pack."""
        self.put("Demo Pack/Demo_Set_.brushset.zip", self.set_bytes)
        self.put("Demo Pack/Loose/Demo Ink\u00e9r.brush", self.inker)
        self.put("Demo Pack/Read Me.pdf", PDF)
        self.put("Demo Pack/cover.jpg", JPEG)
        self.put("Demo Pack/Canvas.procreate", self.stray + b"")       # a zip, and never a brush
        self.put("Demo Pack/.DS_Store", b"\x00\x00\x00\x01Bud1")
        self.put("zip files/Demo_Pack.zip", fixtures.make_zip([
            ("Demo Pack/Demo_Set_.brushset", self.set_bytes),
            ("Demo Pack/Loose/Demo Ink\u00e9r.brush", self.inker),
            ("Demo Pack/Read Me.pdf", PDF),
            ("Demo Pack/Extras/More.zip", fixtures.make_zip([("Loose_Marker.brush", self.marker)])),
            ("__MACOSX/Demo Pack/._Demo_Set_.brushset", b"\x00\x05\x16\x07resource fork"),
        ]))
        self.put("Other/Stray.brush", self.stray)

    def adopt(self, *argv, src=None, free=10 ** 12):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ingest.main(["adopt", str(src or self.src), *argv, "--root", str(self.root)],
                               disk_free=lambda folder: free)
        return code, out.getvalue(), err.getvalue()

    def stored(self):
        """Every file in the library but the manifest, as POSIX paths."""
        return sorted(p.relative_to(self.library).as_posix() for p in self.library.rglob("*")
                      if p.is_file() and p.name != "sources.json")

    def held(self, relative):
        return (self.library / relative).read_bytes()


# ── names ────────────────────────────────────────────────────────────────────

class TheNameRule(unittest.TestCase):
    def test_a_set(self):
        cases = {
            "Autumn_Flow.brushset.zip": "Autumn_Flow.brushset",
            "Autumn_Stamps_.brushset.zip": "Autumn_Stamps_.brushset",
            "Sargent\u2019s_Oils.brushset.zip": "Sargent_s_Oils.brushset",
            "Procreate 3D Lettering Bundle.brushset.zip": "Procreate_3D_Lettering_Bundle.brushset",
            "BrushUp-_Paint_Pens.brushset.zip": "BrushUp-_Paint_Pens.brushset",
            "FTOON_-_Canvas_X.brushset.zip": "FTOON_-_Canvas_X.brushset",
            "Plain.brushset": "Plain.brushset",
            "UPPER.BRUSHSET.ZIP": "UPPER.brushset",
            "Pack.zip": "Pack.brushset",
            "Misnamed.brush": "Misnamed.brushset",
            "v2.1 final.brushset": "v2.1_final.brushset",
            "\u6d53\u58a8\u6de1\u5f69.brushset": "____.brushset",
            "folder/inside/Deep.brushset.zip": "Deep.brushset",
            "odd.data": "odd.data.brushset",
        }
        for original, expected in cases.items():
            self.assertEqual(ingest.adopted_name(original, "set"), expected, original)

    def test_a_brush(self):
        cases = {
            "Broken_Conte.brush": "Broken_Conte.brush",
            "Broken Cont\u00e9.brush": "Broken_Conte.brush",
            "Broken Conte\u0301.brush": "Broken_Conte.brush",
            "RSCo_Dusty\u2019s_Grit_Liner.brush": "RSCo_Dusty_s_Grit_Liner.brush",
            "Frankentoon_-_Tech_Pen_0.5.brush": "Frankentoon_-_Tech_Pen_0.5.brush",
            "Frankentoon_-_China_Ink_.brush": "Frankentoon_-_China_Ink_.brush",
            "a/b\\c:d*e?.brush": "c_d_e_.brush",
            "Thing.zip": "Thing.brush",
            "Thing.brush.zip": "Thing.brush",
            "Stra\u00dfe & co.brush": "Stra_e___co.brush",
            ".brush": "untitled.brush",
            "....brush": "untitled.brush",
            ".hidden.brush": "hidden.brush",
            "CON.brush": "x-CON.brush",
            "nul.v2.brush": "x-nul.v2.brush",
            "name\x00\n\t.brush": "name___.brush",
        }
        for original, expected in cases.items():
            self.assertEqual(ingest.adopted_name(original, "brush"), expected, original)

    def test_every_name_is_plain_ascii_and_one_path_part(self):
        hostile = ["../../etc/passwd.brush", "C:\\Windows\\x.brush", "/abs.brush", "a\u202eb.brush",
                   "x" * 500 + ".brush", "\U0001f4a7Everything.brushset", " . .brush", "-rf.brush"]
        for original in hostile:
            for kind, suffix in (("set", ".brushset"), ("brush", ".brush")):
                name = ingest.adopted_name(original, kind)
                self.assertRegex(name, r"^[A-Za-z0-9_-][A-Za-z0-9._-]*$", original)
                self.assertTrue(name.endswith(suffix), original)
                self.assertLessEqual(len(name), ingest.NAME_MAX + len(suffix) + 2)
                self.assertNotIn("..", name.split("/"))
        self.assertFalse(ingest.adopted_name("x.brushset.zip", "set").endswith(".zip"))

    def test_a_document(self):
        self.assertEqual(ingest.document_name("Read Me.pdf"), "Read_Me.pdf")
        self.assertEqual(ingest.document_name("Monoliners - Stroke Guide.jpg"), "Monoliners_-_Stroke_Guide.jpg")
        self.assertEqual(ingest.document_name("README"), "README")
        self.assertEqual(ingest.document_name(".pdf"), "pdf")
        self.assertEqual(ingest.document_name("Watercolour Canvas .procreate"), "Watercolour_Canvas_.procreate")

    def test_a_name_made_unique_by_its_hash(self):
        digest = "0123456789abcdef" * 4
        self.assertEqual(ingest.with_hash("Inker.brush", digest), "Inker_01234567.brush")
        self.assertEqual(ingest.with_hash("v2.1.brushset", digest), "v2.1_01234567.brushset")
        self.assertEqual(ingest.with_hash("README", digest), "README_01234567")

    def test_show_takes_the_control_characters_out(self):
        self.assertEqual(ingest.show("a\x1b[2Jb\nc\x00"), "a?[2Jb?c?")
        self.assertEqual(ingest.show("Cont\u00e9 \u6d53"), "Cont\u00e9 \u6d53")


# ── what a zip is ────────────────────────────────────────────────────────────

class Sniffing(unittest.TestCase):
    def test_by_the_root_entries(self):
        self.assertEqual(ingest.sniff({"brushset.plist", "A/Brush.archive"}), ("set", ""))
        self.assertEqual(ingest.sniff({"Brush.archive", "Shape.png"}), ("brush", ""))
        self.assertEqual(ingest.sniff({"brushset.plist", "Brush.archive"}), ("set", ""))
        self.assertEqual(ingest.sniff({"Top/brushset.plist", "Top/A/Brush.archive"}), ("set", "Top/"))
        self.assertEqual(ingest.sniff({"Top/brushset.plist", "Other/A/Brush.archive"}), ("other", ""))
        self.assertEqual(ingest.sniff({"Top/brushset.plist", "loose.txt"}), ("other", ""))
        self.assertEqual(ingest.sniff({"A/Brush.archive"}), ("other", ""))
        self.assertEqual(ingest.sniff({"a/b/brushset.plist"}), ("other", ""))
        self.assertEqual(ingest.sniff({"BRUSHSET.PLIST"}), ("other", ""))
        self.assertEqual(ingest.sniff({"Pack/x.brush", "Pack/y.pdf"}), ("other", ""))
        self.assertEqual(ingest.sniff(set()), ("other", ""))

    def test_the_fixture_files(self):
        brushes = fixtures.standard_user_brushes()
        cases = {
            "a brush": (fixtures.brush_file(brushes[0]), "brush"),
            "a set": (fixtures.brushset_file("S", brushes), "set"),
            "a set with the plist first": (fixtures.brushset_file("S", brushes, plist_first=True), "set"),
            "a set inside one top folder": (fixtures.brushset_file("S", brushes, prefix="S.brushset/"), "set"),
            "an official-style set": (fixtures.brushset_file(
                "S", fixtures.standard_official_brushes(), plist_extra={"iconName": "i"},
                double_empty=True, stored=True), "set"),
            "a zip of documents": (fixtures.make_zip([("a.pdf", PDF)]), "other"),
        }
        for what, (data, expected) in cases.items():
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = {info.orig_filename for info in ingest.list_entries(archive)}
            self.assertEqual(ingest.sniff(names)[0], expected, what)

    def test_entries_that_do_not_count(self):
        data = fixtures.make_zip([
            ("__MACOSX/brushset.plist", b"x"), ("A/.DS_Store", b"x"), ("A/", b""),
            ("A/Brush.archive", b"first"), ("A/Brush.archive", b"second"), ("Thumbs.db", b"x"),
            ("A/desktop.ini", b"x"), ("A/__MACOSX/._Shape.png", b"x")])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            infos = ingest.list_entries(archive)
            self.assertEqual([info.orig_filename for info in infos], ["A/Brush.archive"])
            self.assertEqual(ingest.read_entry(archive, infos[0], 100), b"first", "the first of a repeated name")

    def test_an_empty_placeholder_is_an_entry_of_its_folder(self):
        """The one rule of CONTRACTS F3: junk is part of no folder; a `.empty`
        inside a brush folder is a member like any other, and is listed."""
        data = fixtures.make_zip([
            ("A/Brush.archive", b"a"), ("A/AuthorPicture/.empty", b""), ("A/.empty", b""),
            ("A/AuthorPicture/.empty", b""), ("A/Signature/.empty", b"not even empty")])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = [info.orig_filename for info in ingest.list_entries(archive)]
        self.assertEqual(names, ["A/Brush.archive", "A/AuthorPicture/.empty", "A/.empty",
                                 "A/Signature/.empty"])
        self.assertEqual(ingest.JUNK_NAMES, {".ds_store", "thumbs.db", "desktop.ini"})
        self.assertEqual(ingest.JUNK_FOLDERS, {"__macosx"})

    def test_an_empty_placeholder_never_decides_what_a_container_is(self):
        brushes = fixtures.standard_user_brushes()
        inside = fixtures.brushset_file("S", brushes, prefix="S.brushset/")
        with zipfile.ZipFile(io.BytesIO(inside)) as archive:
            names = {info.orig_filename for info in ingest.list_entries(archive)}
        self.assertEqual(ingest.sniff(names), ("set", "S.brushset/"))
        self.assertEqual(ingest.sniff(names | {".empty"}), ("set", "S.brushset/"),
                         "a placeholder beside the one top folder changes nothing")
        self.assertEqual(ingest.sniff({".empty", "A/.empty"})[0], "other")
        self.assertEqual(ingest.sniff({"Brush.archive", ".empty"}), ("brush", ""))

    def test_a_set_name_is_read_from_an_xml_plist_only(self):
        self.assertEqual(ingest.plist_set_name(fixtures.brushset_plist("Demo Set ", ["A"])), "Demo Set ")
        self.assertEqual(ingest.plist_set_name(fixtures.brushset_plist("\u6d53\u58a8", ["A"],
                                                                       {"iconName": "x"})), "\u6d53\u58a8")
        self.assertIsNone(ingest.plist_set_name(fixtures.brushset_plist("Binary", ["A"], binary=True)))
        self.assertIsNone(ingest.plist_set_name(plistlib.dumps(["A"], fmt=plistlib.FMT_XML)))
        self.assertIsNone(ingest.plist_set_name(plistlib.dumps({"name": 7}, fmt=plistlib.FMT_XML)))
        self.assertIsNone(ingest.plist_set_name(b"<?xml version='1.0'?><plist><dict><key>name</key>"))
        self.assertIsNone(ingest.plist_set_name(b""))
        bomb = (b'<?xml version="1.0"?><!DOCTYPE plist [<!ENTITY a "aaaaaaaaaa">'
                b'<!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">]>'
                b"<plist version=\"1.0\"><dict><key>name</key><string>&b;</string></dict></plist>")
        self.assertIsNone(ingest.plist_set_name(bomb), "entity declarations are never expanded")

    def test_hostile_entry_names(self):
        for name in ("../x.brush", "a/../../x.brush", "/abs.brush", "C:/x.brush", "c:x.brush",
                     "a\\b.brush", "..\\x.brush", "x\x00.brush", ""):
            self.assertTrue(ingest.hostile(name), repr(name))
        for name in ("x.brush", "Pack/Sub Folder/x.brush", "a..b/x.brush", "..a/x.brush", "\u6d53.brush"):
            self.assertEqual(ingest.hostile(name), "", name)

    def test_a_mac_made_name_is_shown_as_it_was_meant(self):
        info = zipfile.ZipInfo("x")
        info.orig_filename = "Caf\u00e9 \u2019.brush".encode("utf-8").decode("cp437")
        info.flag_bits = 0
        self.assertEqual(ingest.shown_name(info), "Caf\u00e9 \u2019.brush")
        info.flag_bits = 0x800
        self.assertEqual(ingest.shown_name(info), info.orig_filename)
        plain = zipfile.ZipInfo("Plain.brush")
        self.assertEqual(ingest.shown_name(plain), "Plain.brush")
        odd = zipfile.ZipInfo("x")
        odd.orig_filename, odd.flag_bits = "\u00e9\u00e9", 0
        self.assertEqual(ingest.shown_name(odd), "\u00e9\u00e9", "not UTF-8 underneath: left alone")


# ── which pack ───────────────────────────────────────────────────────────────

class PackMatching(unittest.TestCase):
    def setUp(self):
        self.sources = fixtures.standard_sources()
        self.sources["packs"].append({"id": "second-pack", "match": ["Second*", "**/second.zip"], "sets": {}})

    def test_patterns_ignore_case_and_a_star_crosses_a_slash(self):
        for path in ("Demo Pack/Demo_Set.brushset", "demo pack/deep/er/x.brush", "DEMO PACK/x.brush",
                     "zip files/Demo_Pack.zip", "a/b/demo_pack.ZIP", "Demo_Pack.zip"):
            self.assertEqual(ingest.packs_for(path, self.sources), [PACK], path)
        self.assertEqual(ingest.packs_for("Second Pack/x.brush", self.sources), ["second-pack"])

    def test_no_pack_and_two_packs(self):
        for path in ("Other/Stray.brush", "Demo Pack", "x/Demo Pack/y.brush", "Demo_Pack.zip.bak"):
            self.assertEqual(ingest.packs_for(path, self.sources), [], path)
        self.sources["packs"][1]["match"].append("Demo Pack/Loose/**")
        self.assertEqual(ingest.packs_for("Demo Pack/Loose/x.brush", self.sources), [PACK, "second-pack"])

    def test_a_path_already_laid_out_as_a_library_is_its_pack(self):
        self.assertEqual(ingest.packs_for(f"user/{PACK}/Anything.brushset", self.sources), [PACK])
        self.assertEqual(ingest.packs_for("user/second-pack/Demo Pack/x.brush", self.sources), ["second-pack"])
        self.assertEqual(ingest.packs_for("user/not-a-pack/x.brush", self.sources), [])
        self.assertEqual(ingest.packs_for(f"user/{PACK}", self.sources), [])

    def test_the_real_manifest_sorts_the_names_of_the_authors_folder(self):
        """File names only, typed here; no brush file is opened."""
        real = ingest.load_sources(BRUSHES / "library")
        expected = {
            "autumn-brush-box": ["Autumn_Brush_Box_for_Procreate/Autumn_Flow.brushset.zip",
                                 "Autumn_Brush_Box_for_Procreate/Autumn_Stamps_.brushset.zip",
                                 "zip files/Autumn_Brush_Box_for_Procreate.zip"],
            "tgts-grain-shaders": ["TGTS-GrainShader-Procreate-V2.0/Grain_Shaders.brushset.zip",
                                   "zip files/Grain_Shader_Brushes_For_Procreate.zip"],
            "rsco-dry-brush-pack": [
                "The Dry Brush Pack for Procreate by RetroSupply/A. Brushes/Brush Set/RSCo_Dry_Brush_Pack.brushset.zip",
                "The Dry Brush Pack for Procreate by RetroSupply/A. Brushes/Individual Brushes/RSCo_Dry_Wood.brush",
                "zip files/The_Dry_Brush_Pack_for_Procreate.zip"],
            "frankentoon-canvas-x": ["Frankentoon - Canvas X/Brushes/FTOON_-_Canvas_X.brushset.zip",
                                     "zip files/Canvas_X_-_Procreate_Brush_Pack.zip"],
            "frankentoon-nautika": [
                "Nautika_-_Brush_Pack_for_Procreate/01 Nautika Brushes/Frankentoon_-_Salt.brush",
                "zip files/Nautika_-_Brush_Pack_for_Procreate.zip"],
            "insecto-charcoal": ["Insecto Charcoal Procreate/Procreate Brushes/Broken_Conte.brush",
                                 "zip files/Charcoal_Set_-_Procreate_Brushes.zip"],
            "bocadebra-forest-tales": ["Bocadebra Brushes for Procreate/Forest_Tales.brushset.zip",
                                       "zip files/Texture_brushes_for_Procreate.zip"],
            "brushup-paint-pens": ["BrushUp- Paint Pens/BrushUp-_Paint_Pens.brushset.zip",
                                   "zip files/Paint_Pens_for_Procreate.zip"],
            "igb-vintage-ink-kit": ["Procreate_Vintage_Ink_Brushes/IGB_Vintage_Ink_Kit.brushset.zip",
                                    "zip files/Procreate_Vintage_Ink_Brushes.zip"],
            "lettering-3d": ["Procreate 3D Lettering Bundle/Procreate 3D Lettering Bundle.brushset.zip",
                             "zip files/Procreate_3D_Lettering_Bundle.zip"],
            "trendy-stamps": ["Trendy_Stamps_for_Procreate/PD_Floral_Stamps.brushset.zip",
                              "zip files/Trendy_Stamps_for_Procreate.zip"],
            "monoliners": ["Monoliners Brushset/Brushset/Monoliners.brushset.zip",
                           "Monoliners Brushset/Individual Brushes/Blobby_Smooth.brush",
                           "zip files/Monoliners_Procreate_Brush_Set.zip"],
            "everything-watercolour": ["Pattern_Procreate_brushes/Everything_Watercolour.brushset.zip",
                                       "zip files/EVERYTHING_WATERCOLOUR_for_Procreate.zip"],
            "pattern": ["Pattern_Procreate_brushes/Pattern Procreate brushes/Pattern.brushset.zip",
                        "zip files/Pattern_Procreate_brushes.zip"],
            "starter-kit": ["Starter Kit Procreate brushes/Starter_Kit.brushset.zip",
                            "zip files/Procreate_Brushes_Starter_Kit.zip"],
            "sargents-oils": ["Sargent_s_Oils_____Procreate_Brushes/Sargent\u2019s_Oils.brushset.zip",
                              "zip files/Sargent_s_Oils_____Procreate_Brushes.zip"],
            "painterly-pack": ["Painterly_Pack.brushset.zip",
                               "zip files/Painterly_Pack_____Procreate_Brushes.zip"],
            "urban-sketching": ["Urban_Sketching.brushset.zip",
                                "zip files/Urban_Sketching_____Procreate_Brushes.zip"],
            "texturetown": ["TextureTown.brushset.zip", "zip files/Texture_Town_Brush_Set_for_procreate.zip"],
        }
        self.assertEqual(sorted(expected), sorted(pack["id"] for pack in real["packs"]))
        for pack, paths in expected.items():
            for path in paths:
                self.assertEqual(ingest.packs_for(path, real), [pack], path)
        self.assertEqual(ingest.packs_for("Somebody Else/New.brushset", real), [])


# ── the dry run ──────────────────────────────────────────────────────────────

class DryRun(AdoptCase):
    def test_it_prints_the_plan_and_writes_nothing(self):
        self.small_corpus()
        before = fixtures.tree_digest(self.tmp)
        code, out, err = self.adopt()
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        self.assertEqual(out.rstrip("\n").splitlines()[-1], DRY_RUN)
        self.assertEqual(ingest.DRY_RUN_LINE, DRY_RUN)
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertEqual(self.stored(), [])
        self.assertFalse((self.library / "user").exists())

    def test_the_plan_says_what_would_happen(self):
        self.small_corpus()
        _, out, _ = self.adopt()
        self.assertIn("4 brush files (1 sets, 3 brushes)", out)
        self.assertIn("2 more copies of them recognised", out)
        self.assertIn("2 other zip files searched", out)
        for line in ("Demo_Set_.brushset   'Demo Set ', 4 brushes", "Demo_Inker.brush", "Loose_Marker.brush",
                     "Stray.brush", "from  Demo Pack/Demo_Set_.brushset.zip   (+1 identical)",
                     "from  zip files/Demo_Pack.zip!/Demo Pack/Extras/More.zip!/Loose_Marker.brush",
                     "4 files to copy", "0 already in the library"):
            self.assertIn(line, out)
        total = sum(len(data) for data in (self.set_bytes, self.inker, self.marker, self.stray))
        self.assertIn(f"{total:,} bytes", out)
        self.assertIn("NOT ADOPTED", out)
        self.assertIn("WARNINGS", out)
        self.assertIn("Other/Stray.brush fits no pack", out)
        self.assertNotIn("REFUSED", out)

    def test_the_plan_does_not_depend_on_the_order_files_were_made_in(self):
        self.small_corpus()
        _, first, _ = self.adopt()
        again = self.tmp / "again" / "procreate brushes"
        files = sorted(p for p in self.src.rglob("*") if p.is_file())
        for path in reversed(files):
            self.put(path.relative_to(self.src).as_posix(), path.read_bytes(), under=again)
        _, second, _ = self.adopt(src=again)
        self.assertEqual(first.replace(str(self.src), "SRC"), second.replace(str(again), "SRC"))
        _, third, _ = self.adopt()
        self.assertEqual(first, third)

    def test_nothing_found_is_a_clean_dry_run(self):
        self.put("Demo Pack/Read Me.pdf", PDF)
        code, out, _ = self.adopt()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("0 brush files", out)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("nothing to copy", out)
        self.assertEqual(self.stored(), [])


# ── a confirmed adoption ─────────────────────────────────────────────────────

class Confirmed(AdoptCase):
    def test_each_container_is_copied_once_byte_for_byte(self):
        self.small_corpus()
        code, out, err = self.adopt("--confirm")
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        self.assertEqual(self.stored(), [f"user/{PACK}/Demo_Inker.brush", f"user/{PACK}/Demo_Set_.brushset",
                                         f"user/{PACK}/Loose_Marker.brush", "user/unsorted/Stray.brush"])
        self.assertEqual(self.held(f"user/{PACK}/Demo_Set_.brushset"), self.set_bytes)
        self.assertEqual(self.held(f"user/{PACK}/Demo_Inker.brush"), self.inker)
        self.assertEqual(self.held(f"user/{PACK}/Loose_Marker.brush"), self.marker,
                         "a file found only inside a zip inside a zip is written from memory")
        self.assertEqual(self.held("user/unsorted/Stray.brush"), self.stray)
        self.assertIn("4 files copied", out)
        self.assertNotIn("DRY RUN", out)

    def test_no_zip_no_document_no_artwork_and_no_part_file_is_left(self):
        self.small_corpus()
        self.adopt("--confirm")
        for path in self.stored():
            self.assertTrue(path.endswith((".brushset", ".brush")), path)
            self.assertRegex(path, r"^user/[a-z0-9-]+/[A-Za-z0-9._-]+$")
        self.assertFalse(any("Canvas" in path or "_docs" in path for path in self.stored()))

    def test_the_source_folder_is_not_touched(self):
        self.small_corpus()
        before = fixtures.tree_digest(self.src)
        self.adopt("--confirm")
        self.assertEqual(fixtures.tree_digest(self.src), before)

    def test_the_manifest_is_not_written(self):
        self.small_corpus()
        before = (self.library / "sources.json").read_bytes()
        self.adopt("--confirm")
        self.assertEqual((self.library / "sources.json").read_bytes(), before)

    def test_nothing_is_written_outside_library_user(self):
        self.small_corpus()
        known = {p for p in self.tmp.rglob("*")}
        elsewhere = fixtures.temp_dir(self)
        with contextlib.ExitStack() as stack:
            stack.callback(os.chdir, os.getcwd())
            os.chdir(elsewhere)
            self.adopt("--confirm")
        new = sorted(p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*") if p not in known)
        self.assertTrue(new)
        for path in new:
            self.assertTrue(path.startswith("brushes/library/user"), path)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.assertFalse((self.root / "catalog").exists())
        self.assertFalse((self.root / "vault").exists())

    def test_a_second_run_copies_nothing(self):
        self.small_corpus()
        self.adopt("--confirm")
        before = fixtures.tree_digest(self.library)
        stamps = {p: p.stat().st_mtime_ns for p in self.library.rglob("*") if p.is_file()}
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("nothing to copy", out)
        self.assertIn("0 files to copy", out)
        self.assertIn("4 already in the library", out)
        self.assertEqual(fixtures.tree_digest(self.library), before)
        self.assertEqual({p: p.stat().st_mtime_ns for p in self.library.rglob("*") if p.is_file()}, stamps)
        code, out, _ = self.adopt()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("present", out)

    def test_a_file_the_library_holds_elsewhere_is_not_copied_again(self):
        self.small_corpus()
        self.put("user/unsorted/Renamed_By_Hand.brushset", self.set_bytes, under=self.library)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertNotIn(f"user/{PACK}/Demo_Set_.brushset", self.stored())
        self.assertIn("held  user/unsorted/Renamed_By_Hand.brushset", out)
        self.assertIn("3 files copied", out)

    def test_only_the_new_file_is_copied_when_one_is_added(self):
        self.small_corpus()
        self.adopt("--confirm")
        fresh = fixtures.brush_file(fixtures.make_brush("Fresh", number=7))
        self.put("Demo Pack/Loose/Fresh.brush", fresh)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("1 files copied", out)
        self.assertEqual(self.held(f"user/{PACK}/Fresh.brush"), fresh)

    def test_one_file_can_be_adopted_on_its_own(self):
        vendor = self.put("Demo_Pack.zip", fixtures.make_zip([("Demo_Set_.brushset.zip", self.set_bytes)]))
        code, _, _ = self.adopt("--confirm", src=vendor)
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Demo_Set_.brushset"])

    def test_too_little_disk_space_is_exit_2_and_writes_nothing(self):
        self.small_corpus()
        code, out, _ = self.adopt(free=1000)
        self.assertEqual(code, bc.EXIT_OK, "the dry run still shows the plan")
        self.assertIn("1,000 bytes free", out)
        code, _, err = self.adopt("--confirm", free=1000)
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("free", err)
        self.assertEqual(self.stored(), [])

    def test_a_copy_that_does_not_match_its_hash_is_thrown_away(self):
        source = self.put("x.brush", self.inker)
        dest = self.library / "user" / PACK / "x.brush"
        with self.assertRaises(ingest.IngestError):
            ingest.copy_checked(ingest.Location("x.brush", source), sha(self.marker), dest)
        self.assertEqual(self.stored(), [])
        ingest.copy_checked(ingest.Location("x.brush", source), sha(self.inker), dest)
        self.assertEqual(dest.read_bytes(), self.inker)
        with self.assertRaises(ingest.IngestError):
            ingest.copy_checked(ingest.Location("x.brush", source), sha(self.inker), dest)
        self.assertEqual(self.stored(), [f"user/{PACK}/x.brush"], "an existing file is never replaced")


# ── kinds by content, and nesting ────────────────────────────────────────────

class ContentNotExtension(AdoptCase):
    def test_the_stored_extension_follows_what_the_file_is(self):
        self.put("Demo Pack/A_Set.brush", self.set_bytes)
        self.put("Demo Pack/A_Brush.zip", self.inker)
        self.put("Demo Pack/Other_Brush.dat", self.marker)
        code, _, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/A_Brush.brush", f"user/{PACK}/A_Set.brushset",
                                         f"user/{PACK}/Other_Brush.dat.brush"])

    def test_a_set_zipped_with_its_folder_is_a_set(self):
        wrapped = fixtures.brushset_file("Wrapped", fixtures.standard_user_brushes()[:2], prefix="Wrapped/")
        self.put("Demo Pack/Wrapped.brushset.zip", wrapped)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.held(f"user/{PACK}/Wrapped.brushset"), wrapped)
        self.assertIn("'Wrapped', 2 brushes", out)

    def test_a_procreate_file_is_never_adopted_whatever_it_holds(self):
        self.put("Demo Pack/Canvas.procreate", self.inker)
        self.put("Demo Pack/Zipped.zip", fixtures.make_zip([("Art/Canvas.procreate", self.marker)]))
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [])
        self.assertIn("0 brush files", out)
        self.assertIn("artwork", out)

    def test_three_zips_deep_is_read_and_four_is_not(self):
        deep = fixtures.brush_file(fixtures.make_brush("Deep", number=8))
        deeper = fixtures.brush_file(fixtures.make_brush("Deeper", number=9))

        def wrap(name, data, layers):
            for layer in range(layers, 0, -1):
                data = fixtures.make_zip([(name, data)])
                name = f"layer{layer}.zip"
            return data

        self.put("Demo Pack/three.zip", wrap("Deep.brush", deep, 3))
        self.put("Demo Pack/four.zip", wrap("Deeper.brush", deeper, 4))
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Deep.brush"])
        self.assertEqual(self.held(f"user/{PACK}/Deep.brush"), deep)
        self.assertEqual(ingest.CAPS["nesting_depth"], 3)
        self.assertIn("SKIPPED", out)
        self.assertIn("Deeper.brush: nested more than 3 zips deep", out)

    def test_a_zip_met_again_is_searched_once_and_its_brushes_counted_in_both_places(self):
        inner = fixtures.make_zip([("Loose.brush", self.inker)])
        self.put("Demo Pack/outer.zip", fixtures.make_zip([("a.zip", inner), ("b.zip", inner), ("c/a.zip", inner)]))
        self.put("Demo Pack/second copy of inner.zip", inner)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Loose.brush"])
        self.assertIn("(+3 identical)", out)
        self.assertIn("2 other zip files searched", out)

    def test_a_copy_of_a_zip_in_a_known_place_sorts_what_the_first_copy_held(self):
        vendor = fixtures.make_zip([("Sets/Inner.brushset", self.set_bytes)])
        self.put("Aaa Unknown Folder/Vendor.zip", vendor)
        self.put("zip files/Demo_Pack.zip", vendor)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Inner.brushset"])
        self.assertNotIn("WARNINGS", out)

    def test_a_zip_met_again_deeper_does_not_reach_past_the_depth_cap(self):
        holder = fixtures.make_zip([("b.zip", fixtures.make_zip([("x.brush", self.inker)]))])
        self.put("Demo Pack/a.zip", holder)                         # x.brush is two zips deep here
        self.put("Demo Pack/z.zip", fixtures.make_zip([             # and four zips deep here
            ("l1.zip", fixtures.make_zip([("l2.zip", holder)]))]))
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/x.brush"])
        self.assertNotIn("identical", out)
        self.assertIn("Demo Pack/z.zip!/l1.zip!/l2.zip!/b.zip!/x.brush: nested more than 3 zips deep", out)

    def test_a_zip_that_holds_itself_ends(self):
        scanner = ingest.Scanner(self.src)
        loop = fixtures.make_zip([("again.zip", b"placeholder")])
        scanner.searched[sha(loop)] = []            # as if it were being searched right now
        outer = self.put("Demo Pack/outer.zip", fixtures.make_zip([("loop.zip", loop), ("x.brush", self.inker)]))
        scanner.file("Demo Pack/outer.zip", outer)
        self.assertEqual([c.kind for c in scanner.containers.values()], ["brush"])
        self.assertEqual(scanner.zips_searched, 1, "the zip already being searched was not opened again")

    def test_the_set_name_is_checked_against_the_manifest(self):
        self.put("Demo Pack/Known.brushset", self.set_bytes)
        unknown = fixtures.brushset_file("Not In The Manifest", fixtures.standard_user_brushes()[:1])
        self.put("Demo Pack/Unknown.brushset", unknown)
        code, out, _ = self.adopt()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("the set name 'Not In The Manifest' (Unknown.brushset) is not in the `sets` of pack", out)
        self.assertNotIn("the set name 'Demo Set '", out)

    def test_files_that_are_never_brushes_are_ignored_quietly(self):
        self.put("Demo Pack/.DS_Store", b"Bud1")
        self.put("Demo Pack/Thumbs.db", b"\xd0\xcf\x11\xe0")
        self.put("__MACOSX/Demo Pack/._Set.brushset", self.set_bytes)
        self.put("Demo Pack/__MACOSX/Loose.brush", self.inker)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [])
        self.assertNotIn("SKIPPED", out)
        self.assertIn("0 other files on disk not adopted", out)


# ── duplicates and names ─────────────────────────────────────────────────────

class DuplicatesAndNames(AdoptCase):
    def test_the_copy_on_disk_names_the_file_not_the_one_in_the_zip(self):
        self.put("zip files/Demo_Pack.zip", fixtures.make_zip([("In The Zip.brushset", self.set_bytes)]))
        self.put("Demo Pack/On_Disk.brushset.zip", self.set_bytes)
        self.adopt("--confirm")
        self.assertEqual(self.stored(), [f"user/{PACK}/On_Disk.brushset"])

    def test_a_copy_in_a_known_pack_decides_over_a_stray_one(self):
        self.put("Aaa Unknown Folder/First.brushset", self.set_bytes)
        self.put("Demo Pack/Second.brushset", self.set_bytes)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Second.brushset"])
        self.assertNotIn("WARNINGS", out)

    def test_the_same_file_in_two_packs_is_stored_once_and_noted(self):
        self.sources["packs"].append(dict(self.sources["packs"][0], id="second-pack",
                                          match=["Second Pack/**"], sets={}))
        self.write_sources()
        self.put("Demo Pack/Shared.brush", self.inker)
        self.put("Second Pack/Shared.brush", self.inker)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Shared.brush"])
        self.assertIn("NOTES", out)
        self.assertIn("also found in the files of second-pack", out)

    def test_two_different_files_with_one_name_both_survive(self):
        self.put("Demo Pack/A/Inker.brush", self.inker)
        self.put("Demo Pack/B/Inker.brush", self.marker)
        self.put("Demo Pack/C/INKER.BRUSH", self.stray)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        stored = self.stored()
        self.assertEqual(len(stored), 3)
        contents = sorted(self.held(path) for path in stored)
        self.assertEqual(contents, sorted([self.inker, self.marker, self.stray]))
        self.assertEqual(len({path.lower() for path in stored}), 3, "no two names differ only in case")
        hashed = [path for path in stored if path.rsplit("/", 1)[-1].lower() != "inker.brush"]
        self.assertEqual(len(hashed), 2)
        for path in hashed:
            self.assertRegex(path, rf"^user/{PACK}/(?i:inker)_[0-9a-f]{{8}}\.brush$")
            self.assertIn(sha(self.held(path))[:8], path)
        self.assertIn("would also be named", out)
        before = fixtures.tree_digest(self.library)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(fixtures.tree_digest(self.library), before, "and the second run finds all three")

    def test_a_name_the_library_already_gave_out_stays_with_its_file(self):
        """Whichever of the two hashes sorts first: the plan must not depend on it."""
        for number, (held, new) in enumerate(((self.inker, self.marker), (self.marker, self.inker))):
            self.root = self.tmp / f"data{number}"
            self.library = self.root / "library"
            self.library.mkdir(parents=True)
            self.write_sources()
            self.src = self.tmp / f"source{number}"
            self.put("Demo Pack/A/One.brush", held)
            self.assertEqual(self.adopt("--confirm")[0], bc.EXIT_OK)
            self.put("Demo Pack/B/One.brush", new)
            code, out, _ = self.adopt("--confirm")
            self.assertEqual(code, bc.EXIT_OK, out)
            self.assertEqual(self.stored(), sorted([f"user/{PACK}/One.brush",
                                                    f"user/{PACK}/One_{sha(new)[:8]}.brush"]))
            self.assertEqual(self.held(f"user/{PACK}/One.brush"), held)
            self.assertEqual(self.held(f"user/{PACK}/One_{sha(new)[:8]}.brush"), new)
            self.assertIn("1 files copied", out)
            self.assertIn("nothing to copy", self.adopt("--confirm")[1])

    def test_names_that_fold_to_one_are_told_apart(self):
        self.put("Demo Pack/Cont\u00e9.brush", self.inker)
        self.put("Demo Pack/Conte.brush", self.marker)
        self.adopt("--confirm")
        stored = self.stored()
        self.assertEqual(len(stored), 2)
        self.assertIn(f"user/{PACK}/Conte.brush", stored)


# ── packs: none, and too many ────────────────────────────────────────────────

class Packs(AdoptCase):
    def test_a_file_that_fits_no_pack_goes_to_unsorted_with_a_warning(self):
        self.put("Somebody Else/New Set.brushset", self.set_bytes)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), ["user/unsorted/New_Set.brushset"])
        self.assertIn("WARNINGS", out)
        self.assertIn("Somebody Else/New Set.brushset fits no pack in sources.json", out)

    def test_unsorted_cannot_be_a_pack_of_the_manifest(self):
        self.sources["packs"].append(dict(self.sources["packs"][0], id="unsorted"))
        self.write_sources()
        code, _, err = self.adopt()
        self.assertEqual(code, bc.EXIT_USAGE)

    def test_a_pack_id_too_long_for_its_loose_set_is_refused(self):
        """48 characters is a slug, but `<id>-loose` would not be one."""
        longest = "p" * identity.PACK_ID_MAX
        self.sources["packs"].append(dict(self.sources["packs"][0], id=longest, match=["Long/**"]))
        self.write_sources()
        self.assertEqual(self.adopt()[0], bc.EXIT_OK)
        self.sources["packs"][-1]["id"] = longest + "p"
        self.write_sources()
        self.put("Demo Pack/Known.brushset", self.set_bytes)
        code, out, err = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn(f"at most {identity.PACK_ID_MAX} characters", err)
        self.assertEqual(self.stored(), [], "nothing is adopted under a manifest that is refused")

    def test_a_path_that_fits_two_packs_stops_the_run(self):
        self.sources["packs"].append(dict(self.sources["packs"][0], id="second-pack",
                                          match=["Demo Pack/Loose/**"], sets={}))
        self.write_sources()
        self.small_corpus()
        code, out, _ = self.adopt()
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("REFUSED", out)
        self.assertIn(f"fits more than one pack ({PACK}, second-pack)", out)
        self.assertEqual(out.rstrip("\n").splitlines()[-1], DRY_RUN)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertEqual(out.rstrip("\n").splitlines()[-1], "REFUSED   nothing was written.")
        self.assertEqual(self.stored(), [])

    def test_a_different_file_under_the_same_name_is_never_overwritten(self):
        self.small_corpus()
        old = self.put(f"user/{PACK}/Demo_Inker.brush", b"PK\x03\x04 an older, different file", under=self.library)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_REFUSED)
        self.assertIn("CONFLICT", out)
        self.assertIn(f"user/{PACK}/Demo_Inker.brush already exists and is a different file", out)
        self.assertEqual(old.read_bytes(), b"PK\x03\x04 an older, different file")
        self.assertEqual(self.stored(), [f"user/{PACK}/Demo_Inker.brush"], "and nothing else was copied")

    def test_a_missing_or_broken_manifest_is_exit_2(self):
        self.small_corpus()
        (self.library / "sources.json").write_text("[]", encoding="utf-8")
        self.assertEqual(self.adopt()[0], bc.EXIT_USAGE)
        (self.library / "sources.json").unlink()
        code, _, err = self.adopt()
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("sources.json", err)

    def test_a_source_that_is_not_there_or_is_the_library_is_exit_2(self):
        code, _, err = self.adopt(src=self.tmp / "nowhere")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.put(f"user/{PACK}/Held.brush", self.inker, under=self.library)
        for inside in (self.library, self.library / "user", self.root, self.tmp):
            code, _, err = self.adopt("--confirm", src=inside)
            self.assertEqual(code, bc.EXIT_USAGE, inside)
            self.assertIn("overlap", err)
        self.assertEqual(self.stored(), [f"user/{PACK}/Held.brush"])


# ── documents ────────────────────────────────────────────────────────────────

class Documents(AdoptCase):
    def test_without_the_flag_no_document_is_copied(self):
        self.small_corpus()
        _, out, _ = self.adopt("--confirm")
        self.assertFalse(any("_docs" in path for path in self.stored()))
        self.assertIn("NOT ADOPTED", out)
        self.assertIn("--with-docs", out)

    def test_with_the_flag_they_go_to_the_ignored_folder_only(self):
        self.small_corpus()
        self.put("Other/notes.txt", b"loose notes")
        code, out, _ = self.adopt("--with-docs", "--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        docs = [path for path in self.stored() if "/_docs/" in path]
        self.assertEqual(docs, [f"user/{PACK}/_docs/Canvas.procreate", f"user/{PACK}/_docs/Read_Me.pdf",
                                f"user/{PACK}/_docs/cover.jpg", "user/unsorted/_docs/notes.txt"])
        self.assertEqual(self.held(f"user/{PACK}/_docs/Read_Me.pdf"), PDF)
        self.assertEqual(self.held(f"user/{PACK}/_docs/Canvas.procreate"), self.stray)
        brushes = [path for path in self.stored() if "/_docs/" not in path]
        self.assertEqual(brushes, [f"user/{PACK}/Demo_Inker.brush", f"user/{PACK}/Demo_Set_.brushset",
                                   f"user/{PACK}/Loose_Marker.brush", "user/unsorted/Stray.brush"])
        self.assertIn("DOCUMENTS", out)
        self.assertNotIn(".DS_Store", " ".join(self.stored()))
        for path in docs:
            self.assertEqual(path.split("/")[2], "_docs")

    def test_a_second_run_with_the_flag_copies_nothing(self):
        self.small_corpus()
        self.adopt("--with-docs", "--confirm")
        before = fixtures.tree_digest(self.library)
        code, out, _ = self.adopt("--with-docs", "--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("nothing to copy", out)
        self.assertEqual(fixtures.tree_digest(self.library), before)

    def test_documents_with_one_name_are_kept_apart_and_equal_ones_are_one(self):
        self.put("Demo Pack/A/swatches.jpg", JPEG)
        self.put("Demo Pack/B/swatches.jpg", JPEG + b"different")
        self.put("Demo Pack/C/swatches.jpg", JPEG)
        code, _, _ = self.adopt("--with-docs", "--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        docs = self.stored()
        self.assertEqual(len(docs), 2)
        self.assertIn(f"user/{PACK}/_docs/swatches.jpg", docs)
        other = next(path for path in docs if path != f"user/{PACK}/_docs/swatches.jpg")
        self.assertRegex(other, rf"^user/{PACK}/_docs/swatches_[0-9a-f]{{8}}\.jpg$")
        self.assertEqual({self.held(path) for path in docs}, {JPEG, JPEG + b"different"})

    def test_documents_inside_a_zip_are_not_taken_out(self):
        self.put("zip files/Demo_Pack.zip", fixtures.make_zip([("Guide.pdf", PDF), ("x.brush", self.inker)]))
        self.adopt("--with-docs", "--confirm")
        self.assertEqual(self.stored(), [f"user/{PACK}/x.brush"])

    def test_the_library_index_does_not_take_a_document_for_a_brush_file(self):
        self.put(f"user/{PACK}/_docs/Looks_Like.brush", self.inker, under=self.library)
        self.put("Demo Pack/Inker.brush", self.inker)
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn(f"user/{PACK}/Inker.brush", self.stored())


# ── files from strangers ─────────────────────────────────────────────────────

class Untrusted(AdoptCase):
    def snapshot(self):
        return {p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*")}

    def test_the_hostile_fixtures_do_no_harm(self):
        hostile = fixtures.hostile_files()
        hostile.pop("lfs-pointer.brushset")
        for name, data in hostile.items():
            self.put(f"Demo Pack/{name}", data)
        before = self.snapshot()
        code, out, err = self.adopt("--confirm")
        self.assertEqual((code, err), (bc.EXIT_OK, ""))
        new = sorted(self.snapshot() - before)
        for path in new:
            self.assertTrue(path.startswith("brushes/library/user"), path)
        for name in ("not-a-zip.brush", "empty.brushset", "no-archive.brush"):
            self.assertIn(f"Demo Pack/{name}:", out)
            self.assertNotIn(name.rsplit(".", 1)[0].replace("-", "_"), " ".join(self.stored()))
        self.assertIn("SKIPPED", out)
        stored = self.stored()
        # A container is copied whole and never unpacked: what is inside it is the reader's to judge.
        self.assertIn(f"user/{PACK}/traversal.brushset", stored)
        self.assertEqual(self.held(f"user/{PACK}/traversal.brushset"), hostile["traversal.brushset"])
        for path in stored:
            self.assertRegex(path, rf"^user/{PACK}/[a-z-]+\.(brush|brushset)$")
        for stray in ("outside.txt", "absolute.txt", "drive.txt", "climb.txt"):
            self.assertFalse(any(path.endswith(stray) for path in self.snapshot()), stray)

    def test_entries_with_hostile_names_inside_a_zip_are_refused(self):
        brushes = [fixtures.brush_file(fixtures.make_brush(f"H{n}", number=60 + n)) for n in range(6)]
        self.put("Demo Pack/vendor.zip", fixtures.make_zip([
            ("../evil.brush", brushes[0]), ("/abs.brush", brushes[1]), ("C:\\drive.brush", brushes[2]),
            ("ok/../../climb.brush", brushes[3]), ("back\\slash.brush", brushes[4]), ("Good.brush", brushes[5])]))
        before = self.snapshot()
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Good.brush"])
        self.assertEqual(sorted(self.snapshot() - before),
                         ["brushes/library/user", f"brushes/library/user/{PACK}",
                          f"brushes/library/user/{PACK}/Good.brush"])
        self.assertEqual(out.count("an entry name with `..`"), 2)
        self.assertEqual(out.count("an entry name with a backslash"), 2)
        self.assertEqual(out.count("an absolute entry name"), 1)

    def test_a_git_lfs_pointer_in_the_source_is_exit_2(self):
        self.small_corpus()
        self.put("Demo Pack/Pointer.brushset", fixtures.LFS_POINTER)
        code, _, err = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("git lfs pull", err)
        self.assertEqual(self.stored(), [])

    def test_a_git_lfs_pointer_in_the_library_is_exit_2(self):
        self.small_corpus()
        self.put(f"user/{PACK}/Demo_Inker.brush", fixtures.LFS_POINTER, under=self.library)
        code, _, err = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_USAGE)
        self.assertIn("git lfs pull", err)
        self.assertEqual(self.held(f"user/{PACK}/Demo_Inker.brush"), fixtures.LFS_POINTER)
        self.assertEqual(self.stored(), [f"user/{PACK}/Demo_Inker.brush"])

    def test_a_pointer_inside_a_zip_is_skipped(self):
        self.put("Demo Pack/vendor.zip", fixtures.make_zip([("Pointer.brushset", fixtures.LFS_POINTER),
                                                           ("Good.brush", self.inker)]))
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [f"user/{PACK}/Good.brush"])
        self.assertIn("Pointer.brushset: a Git LFS pointer", out)

    def test_an_entry_that_inflates_out_of_proportion_is_not_inflated(self):
        bomb = fixtures.make_zip([("big.zip", bytes(20 * ingest.MIB)), ("Good.brush", self.inker)])
        self.assertLess(len(bomb), ingest.MIB)
        self.put("Demo Pack/vendor.zip", bomb)
        with mock.patch.object(zipfile.ZipExtFile, "read", autospec=True,
                               side_effect=zipfile.ZipExtFile.read) as reads:
            code, out, _ = self.adopt()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("big.zip: it inflates more than 200:1", out)
        self.assertIn("1 brush files", out)
        opened = [call.args[0].name for call in reads.call_args_list]
        self.assertIn("Good.brush", opened)
        self.assertNotIn("big.zip", opened, "the size and ratio in the directory were enough to refuse it")

    def test_a_container_with_a_bomb_in_it_is_not_adopted(self):
        self.put("Demo Pack/Bomb.brush", fixtures.ratio_bomb(20))
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [])
        self.assertIn("Demo Pack/Bomb.brush: an entry that inflates more than 200:1", out)

    def test_the_size_caps(self):
        self.put("Demo Pack/vendor.zip", fixtures.make_zip([("Inner.brushset", self.set_bytes)]))
        self.put("Demo Pack/Loose.brush", self.inker)
        with mock.patch.dict(ingest.CAPS, {"upload_bytes": len(self.inker) + 1}):
            code, out, _ = self.adopt()
        self.assertIn("1 brush files (0 sets, 1 brushes)", out)
        self.assertIn("Demo Pack/vendor.zip: ", out)
        with mock.patch.dict(ingest.CAPS, {"upload_bytes": len(self.inker) - 1}):
            _, out, _ = self.adopt()
        self.assertIn("0 brush files", out)
        self.assertIn("Demo Pack/Loose.brush: ", out)
        with mock.patch.dict(ingest.CAPS, {"entry_bytes": 64}):
            _, out, _ = self.adopt()
        self.assertIn("0 brush files", out)
        self.assertIn("the cap is 64", out)
        with mock.patch.dict(ingest.CAPS, {"archive_bytes": 16}):
            _, out, _ = self.adopt()
        self.assertIn("0 brush files", out)
        self.assertIn("a Brush.archive of", out)
        with mock.patch.dict(ingest.CAPS, {"total_bytes": len(self.set_bytes) - 1}):
            _, out, _ = self.adopt()
        self.assertIn("Inner.brushset: more than", out)
        with mock.patch.dict(ingest.CAPS, {"zip_entries": 3}):
            _, out, _ = self.adopt()
        self.assertIn("0 brush files", out)
        self.assertIn("entries; the cap is 3", out)
        code, out, _ = self.adopt()
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn("2 brush files (1 sets, 1 brushes)", out)
        self.assertNotIn("SKIPPED", out)

    def test_the_inflation_budget_is_per_file_on_disk(self):
        budget = ingest.Budget(10)
        budget.spend(6)
        budget.spend(4)
        with self.assertRaises(ingest.Skip):
            budget.spend(1)
        self.assertEqual(ingest.Budget().left, ingest.CAPS["total_bytes"])

    def test_the_caps_are_the_declared_ones(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml is not installed")
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        declared = spec["format"]["caps"]
        self.assertTrue(set(ingest.CAPS) <= set(declared))
        for name, value in ingest.CAPS.items():
            self.assertEqual(value, declared[name], name)
        self.assertEqual(spec["commit_policy"]["limits"]["plain_blob_mb"] * 1000 * 1000, ingest.PLAIN_BLOB_LIMIT)
        self.assertEqual(spec["library"]["adoption_rename"], {".brushset.zip": ".brushset"})
        self.assertEqual(f"library/{ingest.USER_DIR}", spec["layout"]["library_user"])
        self.assertEqual(ingest.SOURCES_SCHEMA, spec["library"]["sources_schema"])

    def test_a_file_over_the_plain_blob_limit_is_named_in_the_plan(self):
        self.small_corpus()
        with mock.patch.object(ingest, "PLAIN_BLOB_LIMIT", len(self.set_bytes) - 1):
            _, out, _ = self.adopt()
        self.assertIn("must go through Git LFS", out)
        self.assertIn(f"user/{PACK}/Demo_Set_.brushset", out.split("must go through Git LFS", 1)[1])

    def test_a_symbolic_link_is_not_followed(self):
        target = self.put("elsewhere/Real.brush", self.inker, under=self.tmp)
        (self.src / "Demo Pack").mkdir(parents=True)
        try:
            os.symlink(target, self.src / "Demo Pack" / "Link.brush")
        except (OSError, NotImplementedError):
            self.skipTest("this account cannot make symbolic links")
        code, out, _ = self.adopt("--confirm")
        self.assertEqual(code, bc.EXIT_OK)
        self.assertEqual(self.stored(), [])
        self.assertIn("Link.brush: not a regular file", out)

    def test_a_name_in_the_plan_cannot_drive_the_terminal(self):
        self.put("Demo Pack/vendor.zip", fixtures.make_zip([("bad\x1b[2Jname\r.brush", self.inker)]))
        _, out, _ = self.adopt()
        self.assertNotIn("\x1b", out)
        self.assertNotIn("\r", out)
        self.assertIn("bad?[2Jname?.brush", out)


# ── where, and the command line ──────────────────────────────────────────────

class WhereAndCommandLine(AdoptCase):
    def main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ingest.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_where_prints_every_root_and_makes_nothing(self):
        before = fixtures.tree_digest(self.tmp)
        code, out, _ = self.main("where", "--root", str(self.root))
        self.assertEqual(code, bc.EXIT_OK)
        lines = {line.split()[0]: line for line in out.splitlines()}
        self.assertEqual(list(lines), list(bc.Paths._fields) + ["manifest"])
        self.assertIn(str(self.library), lines["library"])
        self.assertIn("present", lines["library"])
        self.assertIn("missing", lines["catalog"])
        self.assertIn(str(self.root / "vault"), lines["vault"])
        self.assertIn("1 user packs, 0 official files", lines["manifest"])
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertFalse((self.root / "catalog").exists())

    def test_where_follows_flags_and_environment(self):
        other = self.tmp / "other-library"
        code, out, _ = self.main("where", "--root", str(self.root), "--library", str(other))
        self.assertEqual(code, bc.EXIT_OK)
        self.assertIn(str(other), out)
        self.assertIn("manifest    missing", out)
        with mock.patch.dict(os.environ, {bc.ENV_ROOT: str(self.root)}):
            code, out, _ = self.main("where")
        self.assertIn(str(self.library), out)
        code, out, _ = self.main("--root", str(self.root), "where")
        self.assertIn(str(self.library), out)

    def test_only_the_verbs_that_exist_are_accepted(self):
        for argv in ([], ["build"], ["report"], ["census"], ["scan"], ["adopt"],
                     ["adopt", str(self.src), "--force"], ["where", "extra"]):
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
                ingest.main(argv + ["--root", str(self.root)])
            self.assertEqual(raised.exception.code, bc.EXIT_USAGE, argv)
        parser = ingest.build_parser()
        verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
        self.assertEqual(list(verbs.choices), ["where", "adopt"])
        adopt = parser.parse_args(["adopt", "somewhere"])
        self.assertEqual((adopt.src, adopt.with_docs, adopt.confirm), ("somewhere", False, False))

    def test_the_verbs_and_flags_are_among_the_declared_ones(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml is not installed")
        spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
        declared = spec["cli"]["scripts"]["pipeline/ingest.py"]
        parser = ingest.build_parser()
        verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
        self.assertTrue(set(verbs.choices) <= set(declared["verbs"]))
        flags = {flag for action in verbs.choices["adopt"]._actions for flag in action.option_strings}
        self.assertTrue(set(declared["flags"]["adopt"]) <= flags)
        self.assertEqual(declared["confirm"], ["adopt"])

    def test_it_runs_isolated_from_any_directory(self):
        self.small_corpus()
        elsewhere = fixtures.temp_dir(self)
        env = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        for argv in (["where", "--root", str(self.root)],
                     ["adopt", str(self.src), "--root", str(self.root)]):
            done = subprocess.run([sys.executable, "-I", str(SCRIPT), *argv], cwd=str(elsewhere), env=env,
                                  capture_output=True, timeout=120)
            self.assertEqual(done.returncode, bc.EXIT_OK, done.stderr.decode("utf-8", "replace"))
        text = done.stdout.decode("utf-8")
        self.assertIn("4 brush files (1 sets, 3 brushes)", text)
        self.assertIn("Demo Ink\u00e9r.brush", text, "the console is UTF-8 whatever the code page")
        self.assertEqual(text.rstrip("\r\n").splitlines()[-1], DRY_RUN)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.assertEqual(self.stored(), [])


if __name__ == "__main__":
    unittest.main()
