"""pipeline/brush_file.py: inspect, export and roundtrip, on synthetic files.

The command runs in this process (main(argv), output captured) except where a
test says it runs `python -I` from another folder. Zips are read back with
zipfile and never compared with fixed bytes. The real library is read only by
the opt-in class at the end, when ROSW_BRUSHES_CORPUS names a folder.

    python -m unittest discover -s brushes/pipeline/tests
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import plistlib
import re
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import fixtures  # noqa: E402
import brush_common as bc  # noqa: E402
import brush_file  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import identity  # noqa: E402

CORPUS = os.environ.get("ROSW_BRUSHES_CORPUS", "")
SCRIPT = PIPELINE / "brush_file.py"
UUID_FORM = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$")


def run(*argv):
    """(exit code, stdout, stderr) of brush_file.main in this process."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = brush_file.main([str(arg) for arg in argv])
        except SystemExit as exc:               # argparse refusing an argument
            code = exc.code
    return code, out.getvalue(), err.getvalue()


def read_back(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return [(info.orig_filename, archive.read(info)) for info in archive.infolist()]


def full_brush(number, family="modern", name="Full Brush"):
    return fixtures.make_brush(name, family, number=number, dual=True, reset=True, author=True,
                               empty=("", "Reset", "AuthorPicture"),
                               extras=[("Extra/unknown.bin", b"\x00\x01unknown\xff")])


def rebuilt(data):
    """A fixture archive built again from its parameters and the schema, the
    way the app numbers and lays out its own: it decodes as fidelity byte."""
    return brush_model.encode(brush_model.from_json(brush_model.to_json(brush_model.decode(data))))


def byte_members(brush):
    """The brush's members with every archive rebuilt, so that each decodes as
    fidelity byte."""
    return [(path, rebuilt(data) if path.rsplit("/", 1)[-1] == "Brush.archive" else data)
            for path, data in brush.members]


class Case(fixtures.BrushCase):
    def put(self, relative, data):
        path = self.tmp / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


# ── inspect ──────────────────────────────────────────────────────────────────

class Inspect(Case):
    def setUp(self):
        super().setUp()
        self.user = fixtures.standard_user_brushes()
        self.official = fixtures.standard_official_brushes()
        self.set_path = self.put("Demo_Set.brushset", fixtures.brushset_file(fixtures.USER_SET_NAME, self.user))
        self.official_path = self.put("official.brushset", fixtures.brushset_file(
            "Official", self.official, plist_extra={"iconName": "icon"}, double_empty=True))

    def test_text(self):
        code, out, err = run("inspect", self.set_path, "--root", self.tmp)
        self.assertEqual(code, 0, err)
        self.assertIn('brushset "Demo Set "  4 brushes', out)
        for brush in self.user:
            self.assertIn(f'"{brush.name}"', out)
            self.assertIn(brush.uuid, out)
            self.assertIn(identity.brush_id(brush.archive, brush.shape, brush.grain, brush.subs), out)
        for words in ("era E4 (legacy, 101 keys)", "era E3 (legacy, 88 keys)", "era E0 (legacy, 52 keys)",
                      "fidelity table", "shape  embedded", "shape  bundled  Brush-Preset-Hard.png",
                      "grain  blank", "grain  none", "Brush.archive", "QuickLook/Thumbnail.png"):
            self.assertIn(words, out)

    def test_json(self):
        code, out, err = run("inspect", self.official_path, "--json", "--root", self.tmp)
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(report["schema"], "rosw-brushes-inspect/1")
        (item,) = report["containers"]
        self.assertEqual((item["kind"], item["name"], item["brush_count"]), ("brushset", "Official", 3))
        self.assertEqual(item["plist_keys"], ["brushes", "name", "iconName"])
        self.assertTrue([w for w in item["warnings"] if "the first wins" in w])
        for record, brush in zip(item["brushes"], self.official):
            self.assertEqual(record["uuid"], brush.uuid)
            self.assertEqual(record["id"], identity.brush_id(brush.archive, brush.shape, brush.grain, brush.subs))
            self.assertEqual(record["textures"]["shape"]["source"], brush.shape_source)
            self.assertEqual(record["textures"]["grain"]["source"], brush.grain_source)
            self.assertEqual([m["path"] for m in record["members"]], brush.paths())
            self.assertEqual(record["family"], "modern")
        earth = item["brushes"][2]
        views = {m["path"]: m["view"] for m in earth["members"]}
        self.assertEqual(views[".empty"], "placeholder")
        self.assertEqual(views["Extra/unknown.bin"], "unknown")
        self.assertTrue(views[self.official[2].bundled_shape].startswith("shape (named"))
        self.assertEqual(earth["textures"]["shape"]["member"], self.official[2].bundled_shape)
        self.assertEqual(earth["warnings"], ["an unknown member, kept as it is: Extra/unknown.bin"])
        dual = item["brushes"][0]
        self.assertEqual([a["path"] for a in dual["other_archives"]],
                         ["Sub01/Brush.archive", "Reset/Brush.archive", "Reset/Sub01/Brush.archive"])
        self.assertEqual(dual["reset"], {"same_as_live": False})

    def test_a_texture_supplied_in_the_library(self):
        bundled = self.tmp / "library" / "bundled"
        bundled.mkdir(parents=True)
        (bundled / fixtures.BUNDLED_SHAPE).write_bytes(fixtures.make_png(3, 3))
        code, out, err = run("inspect", self.set_path, "--json", "--root", self.tmp)
        self.assertEqual(code, 0, err)
        pencil = json.loads(out)["containers"][0]["brushes"][1]
        self.assertEqual(pencil["textures"]["shape"]["source"], "bundled-supplied")
        self.assertEqual(pencil["id"], identity.brush_id(self.user[1].archive), "a supplied file is not hashed")

    def test_a_nested_file_and_what_was_skipped(self):
        vendor = self.put("vendor.zip", fixtures.make_zip([
            ("Pack/Set.brushset", fixtures.brushset_file("Inner", self.user[:1])),
            ("Pack/bad.brush", b"PK\x03\x04 not a zip")]))
        code, out, err = run("inspect", vendor, "--root", self.tmp)
        self.assertEqual(code, 0, err)
        self.assertIn("Pack/Set.brushset", out)
        self.assertIn("skipped", out)
        self.assertIn("Pack/bad.brush", out)

    def test_what_it_refuses(self):
        pointer = self.put("p.brushset", fixtures.LFS_POINTER)
        code, _, err = run("inspect", pointer)
        self.assertEqual(code, 2)
        self.assertIn("git lfs pull", err)
        self.assertEqual(run("inspect", self.tmp / "missing.brush")[0], 2)
        self.assertEqual(run("inspect", self.put("docs.zip", fixtures.make_zip([("a.pdf", b"%PDF")])))[0], 1)
        self.assertEqual(run("inspect", self.put("x.brush", b"PK\x03\x04 nope"))[0], 1)
        self.assertEqual(run("inspect")[0], 2)

    def test_an_archive_that_does_not_decode_is_still_shown(self):
        path = self.put("bad.brush", fixtures.hostile_files()["wrong-magic.brush"])
        code, out, err = run("inspect", path, "--json")
        self.assertEqual(code, 0, err)
        brush = json.loads(out)["containers"][0]["brushes"][0]
        self.assertIsNone(brush["era"])
        self.assertTrue([w for w in brush["warnings"] if "cannot be decoded" in w])


# ── export ───────────────────────────────────────────────────────────────────

class Export(Case):
    def setUp(self):
        super().setUp()
        self.brush = full_brush(101)
        self.brush_path = self.put("in/Full.brush", fixtures.brush_file(self.brush))
        self.pair = [full_brush(102, "legacy", "Legacy One"), full_brush(103, "modern", "Modern Two")]
        self.set_path = self.put("in/Pair.brushset", fixtures.brushset_file(
            "Pair Set", self.pair, plist_extra={"iconName": "icon"}))
        self.out = self.tmp / "out"

    def written(self):
        files = sorted(self.out.iterdir()) if self.out.is_dir() else []
        self.assertEqual(len(files), 1, files)
        return files[0], files[0].read_bytes()

    def test_a_dry_run_writes_nothing_and_shows_the_plan(self):
        before = fixtures.tree_digest(self.tmp)
        code, out, err = run("export", "--from", self.brush_path, "--change", "plotSpacing=0.5",
                             "--out", self.out, "--root", self.tmp)
        self.assertEqual(code, 0, err)
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertFalse(self.out.exists())
        self.assertTrue(out.rstrip().endswith(brush_file.DRY_RUN_LINE))
        self.assertRegex(out, r"re-encoded\s+Brush\.archive")
        for path in self.brush.paths():
            if path != "Brush.archive":
                self.assertRegex(out, rf"verbatim\s+{re.escape(path)}\s")
        self.assertIn("applied  plotSpacing = 0.5", out)
        self.assertIn("stale_thumbnail", out)
        self.assertIn("Reset/ is kept verbatim", out)

    def test_one_key_changed_and_every_other_member_byte_for_byte(self):
        code, out, err = run("export", "--from", self.brush_path, "--change", "plotSpacing=0.5",
                             "--out", self.out, "--confirm", "--root", self.tmp)
        self.assertEqual(code, 0, err)
        path, data = self.written()
        self.assertEqual(path.name, "full-brush.brush")
        members = dict(read_back(data))
        self.assertEqual(set(members), set(self.brush.paths()))
        for name, original in self.brush.members:
            if name == "Brush.archive":
                continue
            self.assertEqual(members[name], original, name)
        base = brush_model.decode(self.brush.archive)
        edited = brush_model.decode(members["Brush.archive"])
        self.assertEqual(edited.params["plotSpacing"], 0.5)
        self.assertEqual({k: v for k, v in edited.params.items() if k != "plotSpacing"},
                         {k: v for k, v in base.params.items() if k != "plotSpacing"})
        self.assertEqual(edited.era, base.era)
        self.assertIn(f"wrote    {path}", out)

    def test_an_unchanged_brush_exports_its_archive_bytes(self):
        code, _, err = run("export", "--from", self.brush_path, "--out", self.out, "--confirm",
                           "--root", self.tmp)
        self.assertEqual(code, 0, err)
        _, data = self.written()
        self.assertEqual(sorted(read_back(data)), sorted(self.brush.members))

    def test_one_brush_of_a_set_into_a_new_set(self):
        code, out, err = run("export", "--from", self.set_path, "--brush", "2", "--set", "Edited & Co",
                             "--change", "plotSpacing=0.25", "--out", self.out, "--confirm",
                             "--root", self.tmp)
        self.assertEqual(code, 0, err)
        path, data = self.written()
        self.assertEqual(path.name, "edited-co.brushset")
        members = dict(read_back(data))
        plist = plistlib.loads(members.pop("brushset.plist"))
        self.assertEqual(plist["name"], "Edited & Co")
        (uuid,) = plist["brushes"]
        self.assertRegex(uuid, UUID_FORM)
        self.assertNotEqual(uuid, self.pair[1].uuid, "a changed brush gets a fresh folder name")
        for name, original in self.pair[1].members:
            if name != "Brush.archive":
                self.assertEqual(members[f"{uuid}/{name}"], original, name)
        self.assertEqual(brush_model.decode(members[f"{uuid}/Brush.archive"]).params["plotSpacing"], 0.25)

    def test_an_unchanged_brush_of_a_set_keeps_its_folder_name(self):
        code, _, err = run("export", "--from", self.set_path, "--brush", "Legacy One", "--set", "Kept",
                           "--out", self.out, "--confirm", "--root", self.tmp)
        self.assertEqual(code, 0, err)
        _, data = self.written()
        members = dict(read_back(data))
        self.assertEqual(plistlib.loads(members["brushset.plist"])["brushes"], [self.pair[0].uuid])
        self.assertEqual(members[f"{self.pair[0].uuid}/Brush.archive"], self.pair[0].archive)

    def test_a_whole_set(self):
        code, out, err = run("export", "--from", self.set_path, "--out", self.out, "--confirm",
                             "--root", self.tmp)
        self.assertEqual(code, 0, err)
        path, data = self.written()
        self.assertEqual(path.name, "pair-set.brushset")
        source = dict(read_back(self.set_path.read_bytes()))
        self.assertEqual(dict(read_back(data)), source, "every member and the plist, byte for byte")
        self.assertRegex(out, r"verbatim\s+brushset\.plist")
        code, out, err = run("export", "--from", self.set_path, "--set", "Renamed", "--root", self.tmp)
        self.assertEqual(code, 0, err)
        self.assertRegex(out, r"re-encoded\s+brushset\.plist")

    def test_a_library_brush_by_its_id(self):
        library = fixtures.write_library(self.tmp / "library")
        inker = library["user_set"]["brushes"][0]
        brush_id = identity.brush_id(inker.archive, inker.shape, inker.grain, inker.subs)
        code, out, err = run("export", "--from", brush_id, "--out", self.out, "--confirm",
                             "--root", self.tmp)
        self.assertEqual(code, 0, err)
        self.assertIn("user/demo-pack/", out)
        _, data = self.written()
        self.assertEqual(dict(read_back(data))["Brush.archive"], inker.archive)
        code, _, err = run("export", "--from", "b_000000000000", "--root", self.tmp)
        self.assertEqual(code, 1)
        self.assertIn("no brush b_000000000000", err)
        self.assertEqual(run("export", "--from", brush_id, "--root", self.tmp / "nowhere")[0], 2)

    def test_a_change_that_is_refused_writes_nothing(self):
        for change, code_word in (("plotSpacing=\"wide\"", "wrong_type"), ("noSuchKey=1", "unknown_key"),
                                  ("plotSpacing=NaN", "wrong_type")):
            code, out, err = run("export", "--from", self.brush_path, "--change", change, "--out", self.out,
                                 "--confirm", "--root", self.tmp)
            self.assertEqual(code, 1, change)
            self.assertIn(code_word, out)
            self.assertFalse(self.out.exists())

    def test_how_a_value_is_read(self):
        self.assertEqual(brush_file.parse_changes(["a=0.5", "b=true", "c=My Brush", 'd="7"', "e=[1, 2]",
                                                   "f=Infinity", "g="]),
                         {"a": 0.5, "b": True, "c": "My Brush", "d": "7", "e": [1, 2], "f": "Infinity",
                          "g": ""})
        code, out, err = run("export", "--from", self.brush_path, "--change", "name=New Name ",
                             "--root", self.tmp)
        self.assertEqual(code, 0, err)
        self.assertIn("export   new-name.brush", out)
        self.assertIn('"New Name "', out)

    def test_usage(self):
        cases = [
            ("--from", self.set_path, "--change", "plotSpacing=0.5"),
            ("--from", self.brush_path, "--confirm"),
            ("--from", self.brush_path, "--out", PIPELINE / "exports"),
            ("--from", self.brush_path, "--out", self.tmp / "library" / "x"),
            ("--from", self.brush_path, "--change", "novalue"),
            ("--from", self.brush_path, "--change", "a=1", "--change", "a=2"),
            ("--from", self.brush_path, "--brush", "1"),
            ("--from", self.set_path, "--brush", "9"),
            ("--from", self.tmp / "missing.brush"),
            ("--from", self.brush_path, "--set", "  "),
            (),
        ]
        for argv in cases:
            code, _, _ = run("export", *argv, "--root", self.tmp)
            self.assertEqual(code, 2, argv)
        self.assertFalse((PIPELINE / "exports").exists())

    def test_it_never_writes_over_a_file(self):
        argv = ("export", "--from", self.brush_path, "--out", self.out, "--confirm", "--root", self.tmp)
        self.assertEqual(run(*argv)[0], 0)
        path, first = self.written()
        path.write_bytes(b"mine")
        code, _, err = run(*argv)
        self.assertEqual(code, 1)
        self.assertIn("already there", err)
        self.assertEqual(path.read_bytes(), b"mine")
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), [path.name], "no .tmp is left behind")

    def test_json_is_the_dry_run_shape(self):
        code, out, err = run("export", "--from", self.brush_path, "--change", "plotSpacing=0.5", "--json",
                             "--root", self.tmp)
        self.assertEqual(code, 0, err)
        plan = json.loads(out)
        self.assertTrue({"filename", "size", "sha256", "members", "brushes", "warnings"} <= set(plan))
        self.assertEqual({m["state"] for m in plan["members"]}, {"verbatim", "re-encoded"})
        (brush,) = plan["brushes"]
        self.assertTrue({"name", "uuid", "era", "applied", "rejected", "warnings"} <= set(brush))
        self.assertEqual(brush["applied"], {"plotSpacing": 0.5})
        self.assertEqual(brush["warnings"], [{"key": "QuickLook/Thumbnail.png", "code": "stale_thumbnail"}])
        # Section 0: a dry run says so. With --json stdout stays one object, so
        # the line goes to stderr, and the object says what was written.
        self.assertEqual((plan["dry_run"], plan["written"]), (True, None))
        self.assertIn("DRY RUN   nothing is written without --confirm.", err)
        self.assertNotIn("DRY RUN", out)

    def test_json_with_confirm_says_where_the_file_went(self):
        code, out, err = run("export", "--from", self.brush_path, "--json", "--out", self.out,
                             "--confirm", "--root", self.tmp)
        self.assertEqual(code, 0, err)
        plan = json.loads(out)
        path, _ = self.written()
        self.assertFalse(plan["dry_run"])
        self.assertEqual(Path(plan["written"]).name, path.name)
        self.assertEqual(Path(plan["written"]).resolve(), path.resolve())
        self.assertNotIn("DRY RUN", out + err)


# ── roundtrip ────────────────────────────────────────────────────────────────

class Roundtrip(Case):
    def setUp(self):
        super().setUp()
        self.user = fixtures.standard_user_brushes()
        self.official = fixtures.standard_official_brushes()

    def byte_files(self):
        """A folder of files whose every archive is of fidelity byte."""
        folder = self.tmp / "byte"
        brushes = [fixtures.make_brush("Byte One", number=111), full_brush(112),
                   full_brush(113, "legacy")]
        made = [fixtures.Brush(b.name, byte_members(b), family=b.family, era=b.era, uuid=b.uuid,
                               archive=None, shape=b.shape, grain=b.grain, subs=[], shape_source="",
                               grain_source="", bundled_shape=None, bundled_grain=None) for b in brushes]
        self.put("byte/One.brush", fixtures.brush_file(made[0]))
        self.put("byte/Pair.brushset", fixtures.brushset_file("Pair", made[1:], plist_extra={"iconName": "i"},
                                                              double_empty=True, stored=True))
        return folder

    def test_a_folder_of_byte_archives(self):
        folder = self.byte_files()
        self.put("byte/_docs/ignored.brush", b"not read")
        self.put("byte/__MACOSX/._One.brush", b"not read")
        self.put("byte/partial.brush.part", b"not read")
        self.put("byte/notes.txt", b"not read")
        code, out, err = run("roundtrip", folder)
        self.assertEqual(code, 0, out + err)
        lines = out.strip().splitlines()
        self.assertEqual([line.split()[0] for line in lines], ["ok", "ok", "total"])
        self.assertIn("One.brush  1 loose  1 brushes  1 archives (1 byte, 0 table)", out)
        self.assertIn("Pair.brushset  1 set  2 brushes  8 archives (8 byte, 0 table)", out)
        self.assertIn("2 files (1 sets, 1 loose brushes): 3 brushes, 9 archives (9 byte, 0 table)", lines[-1])
        self.assertIn("0 failed", lines[-1])

    def test_table_archives_fail_unless_allowed(self):
        self.put("t/Demo.brushset", fixtures.brushset_file(fixtures.USER_SET_NAME, self.user))
        self.put("t/Official.brushset", fixtures.brushset_file("O", self.official, plist_extra={"iconName": "i"},
                                                               double_empty=True))
        code, out, _ = run("roundtrip", self.tmp / "t")
        self.assertEqual(code, 1)
        self.assertIn("fidelity table", out)
        self.assertIn("table Demo.brushset :: ", out)
        code, out, err = run("roundtrip", self.tmp / "t", "--allow-table")
        self.assertEqual(code, 0, out + err)
        self.assertIn("ok    Demo.brushset  1 set  4 brushes  4 archives (0 byte, 4 table)", out)
        self.assertIn("2 later entries with a name already met were dropped", out,
                      "a dropped duplicate is reported on the file's line")

    def test_what_fails(self):
        hostile = fixtures.hostile_files()
        brush = fixtures.make_brush("Slash", number=114)
        cases = {
            "slash.brush": (fixtures.make_zip(byte_members(brush) + [("Sub\\evil.png", b"x")]), "not carried"),
            "magic.brush": (hostile["wrong-magic.brush"], "cannot be decoded"),
            "nozip.brush": (hostile["not-a-zip.brush"], "cannot be read"),
            "noarchive.brush": (hostile["no-archive.brush"], "holds no brushset.plist"),
            "traversal.brushset": (hostile["traversal.brushset"], "not carried"),
        }
        for name, (data, words) in cases.items():
            path = self.put(f"bad/{name}", data)
            code, out, _ = run("roundtrip", path, "--allow-table")
            self.assertEqual(code, 1, name)
            self.assertIn(words, out, name)
            self.assertTrue(out.startswith("FAIL"), name)

    def test_a_mismatch_in_the_codec_or_the_writer_is_caught(self):
        folder = self.byte_files()
        with mock.patch.object(brush_file.brush_model, "encode", return_value=b"other bytes"):
            code, out, _ = run("roundtrip", folder)
        self.assertEqual(code, 1)
        self.assertIn("an unchanged export is not the source bytes", out)
        stand_in = mock.Mock(rule_encode=mock.Mock(return_value=b"other bytes"))
        with mock.patch.object(brush_file, "keyed_archive", stand_in):      # the command's own check only
            code, out, _ = run("roundtrip", folder / "One.brush")
        self.assertEqual(code, 1)
        self.assertIn("decoded as byte, but the rules write other bytes", out)
        real = container.write_brush

        def dropping(item, **options):
            item = item.copy()
            item.remove("QuickLook/Thumbnail.png")
            return real(item, **options)

        with mock.patch.object(brush_file.container, "write_brush", side_effect=dropping):
            code, out, _ = run("roundtrip", folder / "One.brush")
        self.assertEqual(code, 1)
        self.assertIn("does not read back as its members", out)

    def test_environment(self):
        pointer = self.put("lfs/p.brushset", fixtures.LFS_POINTER)
        code, out, _ = run("roundtrip", pointer.parent)
        self.assertEqual(code, 2)
        self.assertIn("git lfs pull", out)
        self.assertEqual(run("roundtrip", self.tmp / "missing")[0], 2)
        (self.tmp / "empty").mkdir()
        self.assertEqual(run("roundtrip", self.tmp / "empty")[0], 1, "no file at all is not a pass")

    def test_it_runs_isolated_from_any_folder(self):
        folder = self.byte_files()
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "roundtrip", str(folder)],
                                cwd=str(self.tmp), capture_output=True, text=True, encoding="utf-8",
                                timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 failed", result.stdout)


class TheCommand(unittest.TestCase):
    def test_the_verbs_and_flags_are_the_declared_ones(self):
        parser = brush_file.build_parser()
        verbs = next(action for action in parser._actions if isinstance(action.choices, dict))
        self.assertEqual(list(verbs.choices), ["inspect", "export", "roundtrip"])
        export = verbs.choices["export"]
        flags = {flag for action in export._actions for flag in action.option_strings}
        self.assertTrue({"--from", "--out", "--confirm"} <= flags)
        self.assertEqual(brush_file.DRY_RUN_LINE, "DRY RUN   nothing is written without --confirm.")
        self.assertEqual(bc.EXIT_USAGE, brush_file.Usage.exit_code)

    def test_the_file_is_utf8_with_line_feeds_and_a_main(self):
        raw = SCRIPT.read_bytes()
        self.assertNotIn(b"\r", raw)
        text = raw.decode("utf-8")
        self.assertIn("def main(argv=None):", text)
        self.assertIn("raise SystemExit(main())", text)
        self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parent))", text)


@unittest.skipUnless(CORPUS, "set ROSW_BRUSHES_CORPUS to a folder of brush files to run this")
class Corpus(unittest.TestCase):
    """Gate G1: `python -I brush_file.py roundtrip <corpus>` passes, every archive
    of fidelity byte."""

    def test_the_corpus_roundtrips(self):
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "roundtrip", CORPUS],
                                capture_output=True, text=True, encoding="utf-8", timeout=3600)
        tail = result.stdout.strip().splitlines()[-1]
        self.assertEqual(result.returncode, 0, result.stdout[-3000:] + result.stderr[-2000:])
        self.assertRegex(tail, r" 0 failed")
        self.assertRegex(tail, r"\(\d[\d,]* byte, 0 table\)")
        print(f"\n{tail}", file=sys.stderr)


if __name__ == "__main__":
    unittest.main()
