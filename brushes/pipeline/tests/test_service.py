"""pipeline/service.py: the layer both servers stand on (docs/CONTRACTS.md, F10).

Every test builds a small synthetic library in a temporary folder with
fixtures.py, makes its catalog, previews and notes with the real builders
(ingest.py build, previews.py render, notes.py write), and calls the service on
it. None reads the real library, catalog or vault, and a class-wide check holds
that the service writes nothing under library/, catalog/ or vault/.

`make_world` and `WorldCase` are also what test_mcp_server_full.py and
test_app_server.py build their data with.

    python -m unittest discover -s brushes/pipeline/tests -p "test_service.py"
"""

import ast
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import brush_common as bc  # noqa: E402
import brush_model  # noqa: E402
import container  # noqa: E402
import fixtures  # noqa: E402
import gbr  # noqa: E402
import identity  # noqa: E402
import ingest  # noqa: E402
import notes  # noqa: E402
import png_io  # noqa: E402
import previews  # noqa: E402
import service  # noqa: E402

BRUSHES = PIPELINE.parent
MACHINE_PATH = re.compile(r"[A-Za-z]:[\\/](?:Users|Windows|Program)|/Users/|/home/")
UUID = re.compile(fixtures.UUID_PATTERN)

try:
    import yaml
except ImportError:
    yaml = None


# ── a synthetic world ────────────────────────────────────────────────────────

def id_of(brush):
    return identity.brush_id(brush.archive, brush.shape, brush.grain, brush.subs)


def quiet(module, *argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = module.main(list(argv))
    if code != 0:
        raise AssertionError(f"{module.__name__} {argv}: exit {code}\n{out.getvalue()}{err.getvalue()}")


class World:
    """A data root with the standard synthetic library, its catalog, previews
    and notes. `ids` names eight of its brushes."""

    def __init__(self, root):
        self.root = Path(root)
        self.lib = fixtures.write_library(self.root / "library")
        quiet(ingest, "build", "--root", str(self.root))
        quiet(previews, "render", "--confirm", "--root", str(self.root))
        quiet(notes, "write", "--confirm", "--root", str(self.root))
        self.paths = bc.resolve_paths(root=self.root)
        user, official = self.lib["user_set"]["brushes"], self.lib["official_set"]["brushes"]
        self.brushes = {"inker": user[0], "pencil": user[1], "conte": user[2], "inker2": user[3],
                        "marker": self.lib["loose"][1]["brush"], "dual": official[0],
                        "plain": official[1], "earth": official[2]}
        self.ids = {name: id_of(brush) for name, brush in self.brushes.items()}

    def service(self, **options):
        return service.BrushService(self.paths, **options)

    def build_index(self):
        """Write the search index (a test world is a temporary folder)."""
        service.engine().build_index(self.paths.vault, self.paths.catalog, write=True)

    def copy_to(self, target, *, library=True):
        shutil.copytree(self.root, target, ignore=None if library else shutil.ignore_patterns("library"))
        return World.__new__(World)._attach(target, self)

    def _attach(self, target, other):
        self.root = Path(target)
        self.lib, self.brushes, self.ids = other.lib, other.brushes, other.ids
        self.paths = bc.resolve_paths(root=self.root)
        return self


def make_link(link, target, *, directory):
    """A symbolic link, or on Windows a junction for a folder; False when the
    account can make neither."""
    try:
        os.symlink(target, link, target_is_directory=directory)
        return True
    except (OSError, NotImplementedError):
        pass
    if directory and sys.platform == "win32":
        done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        return done.returncode == 0 and Path(link).exists()
    return False


def snapshot(folder):
    """Every path under a folder (folders too) with the hash of each file: equal
    before and after means nothing was written, made, renamed or removed."""
    folder = Path(folder)
    out = {}
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder).as_posix()
        out[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return out


class WorldCase(unittest.TestCase):
    """A class that shares one read-only world. A test that must change files
    copies it first (`self.copy_world`)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        kept = {k: v for k, v in os.environ.items() if not k.upper().startswith(fixtures.ENV_PREFIX)}
        patcher = mock.patch.dict(os.environ, kept, clear=True)
        patcher.start()
        cls.addClassCleanup(patcher.stop)
        cls.tmp = Path(tempfile.mkdtemp(prefix="brushes-svc-")).resolve()
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        cls.world = World(cls.tmp / "brushes")
        cls.before = snapshot(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        try:
            after = snapshot(cls.tmp)
            changed = sorted(set(after) ^ set(cls.before)) + [k for k in after if k in cls.before
                                                              and after[k] != cls.before[k]]
            if changed:
                raise AssertionError(f"the shared world was changed: {changed[:5]}")
        finally:
            super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.svc = self.world.service()
        self.n = 0

    def ident(self, name):
        return self.world.ids[name]

    def copy_world(self, *, library=True):
        self.n += 1
        target = Path(tempfile.mkdtemp(prefix="brushes-copy-")).resolve()
        self.addCleanup(shutil.rmtree, target, ignore_errors=True)
        return self.world.copy_to(target / "brushes", library=library)

    def assertApi(self, code, call, *args, status=None, **kwargs):
        with self.assertRaises(service.ApiError) as caught:
            call(*args, **kwargs)
        self.assertEqual(caught.exception.code, code, caught.exception.message)
        if status is not None:
            self.assertEqual(caught.exception.status, status)
        return caught.exception

    def exported(self, request):
        """(Export, {path: bytes} of the file when it is a zip)."""
        export = self.svc.build_export(request)
        members = dict(fixtures.zip_entries(export.data))
        return export, members


def one(base, **more):
    """An export request for one brush."""
    return {"format": "brush", "brushes": [dict({"base": base}, **more)]}


# ── helpers that need no world ───────────────────────────────────────────────

class Helpers(unittest.TestCase):
    def test_ids_are_only_the_one_form(self):
        for good in ("b_0123456789ab", "b_ffffffffffff"):
            self.assertEqual(service.check_id(good), good)
        for bad in ("b_0123456789a", "b_0123456789abc", "B_0123456789ab", "b_0123456789aX", "", None, 12,
                    "../b_0123456789ab", "b_0123456789ab\n", ["b_0123456789ab"]):
            with self.assertRaises(service.ApiError) as caught:
                service.check_id(bad)
            self.assertEqual((caught.exception.code, caught.exception.status), ("bad_argument", 400))

    def test_a_set_is_named_by_its_slug(self):
        self.assertEqual(service.check_set_slug("demo-set"), "demo-set")
        for bad in ("Demo Set", "../x", "", "-a", "a" * 49, None):
            with self.assertRaises(service.ApiError):
                service.check_set_slug(bad)

    def test_the_error_carries_what_a_server_needs(self):
        error = service.ApiError("unknown_id", "no such brush", 404, hint="search", data={"id": 1})
        self.assertEqual((error.code, error.message, error.status, error.hint, error.data),
                         ("unknown_id", "no such brush", 404, "search", {"id": 1}))
        self.assertEqual(str(error), "no such brush")
        self.assertEqual(service.ApiError("x", "y").status, 400)

    def test_a_path_is_shown_relative(self):
        base = Path(tempfile.gettempdir()) / "repo"
        self.assertEqual(service.repo_relative(base / "brushes" / "library", base), "brushes/library")
        self.assertEqual(service.repo_relative(base, base), ".")
        self.assertEqual(service.repo_relative(base.parent / "other", base), "../other")

    def test_the_next_steps_are_dry_runs_of_built_verbs_on_disk(self):
        steps = service.next_steps(["official", "catalog", "index"])
        self.assertEqual(len(steps), 3)
        for step in steps:
            self.assertNotIn("--confirm", step)
            self.assertTrue(step.startswith("python brushes/"))
        self.assertEqual(service.next_steps([]), [])
        self.assertEqual(service.next_steps(["catalog"], Path("/no/such/brushes")), [])

    def test_files_are_counted_by_name_only(self):
        folder = Path(tempfile.mkdtemp(prefix="brushes-count-"))
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        (folder / "a").mkdir()
        for name in ("a/One.brush", "a/Two.BRUSHSET", "a/notes.txt", "Three.brushset"):
            (folder / name).write_bytes(b"x")
        self.assertEqual(service.count_files(folder), {"files": 4, "brushset": 2, "brush": 1})
        self.assertEqual(service.count_files(folder / "missing"), {"files": 0, "brushset": 0, "brush": 0})

    def test_base64_is_strict_and_capped(self):
        self.assertEqual(service._b64("QUJD", "x", 10), b"ABC")
        for bad in ("QUJD!", "QUJ", 5, None, "QUJD\n\n"):
            with self.assertRaises(service.ApiError):
                service._b64(bad, "x", 10)
        with self.assertRaises(service.ApiError) as caught:
            service._b64(service.b64(b"x" * 100), "x", 10)
        self.assertEqual(caught.exception.code, "too_large")

    def test_an_export_folder_may_not_lie_inside_the_data(self):
        paths = bc.resolve_paths(root=Path(tempfile.gettempdir()) / "data-root")
        for inside in (paths.library, paths.library / "user", paths.catalog, paths.vault / "x", bc.TOOL_ROOT,
                       bc.TOOL_ROOT / "device-tests"):
            self.assertIsNotNone(service.check_export_dir(inside, paths), inside)
        self.assertIsNone(service.check_export_dir(Path(tempfile.gettempdir()) / "exports-elsewhere", paths))

    def test_write_export_never_overwrites(self):
        folder = Path(tempfile.mkdtemp(prefix="brushes-write-"))
        self.addCleanup(shutil.rmtree, folder, ignore_errors=True)
        target = service.write_export(folder / "out", "a-brush.brush", b"one")
        self.assertEqual(target.read_bytes(), b"one")
        with self.assertRaises(service.ApiError) as caught:
            service.write_export(folder / "out", "a-brush.brush", b"two")
        self.assertEqual((caught.exception.code, caught.exception.status), ("exists", 409))
        self.assertEqual(target.read_bytes(), b"one")
        self.assertEqual(sorted(p.name for p in (folder / "out").iterdir()), ["a-brush.brush"], "no .tmp left")
        for bad in ("../x.brush", "x/y.brush", "X.brush", "x.exe", "", ".brush", "a b.brush", "x\\y.brush"):
            with self.assertRaises(service.ApiError):
                service.write_export(folder / "out", bad, b"x")


# ── status ───────────────────────────────────────────────────────────────────

class StatusStates(unittest.TestCase):
    """The four index states, each from a data root made for it."""

    assertApi = WorldCase.assertApi

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="brushes-state-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {k: v for k, v in os.environ.items()
                                               if not k.upper().startswith(fixtures.ENV_PREFIX)}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = self.tmp / "brushes"

    def service(self, **options):
        options.setdefault("check_seconds", 0)
        return service.BrushService(bc.resolve_paths(root=self.root), **options)

    def test_an_empty_root_is_not_ingested_and_says_what_to_run(self):
        status = self.service().status()
        self.assertEqual(list(status), ["server", "version", "mode", "root", "index", "counts",
                                        "library_present", "library_files", "vocabulary_axes", "export",
                                        "next_steps"])
        self.assertEqual(status["index"]["state"], "not_ingested")
        self.assertIn("catalog.json", status["index"]["reason"])
        self.assertIsNone(status["counts"])
        self.assertEqual(status["vocabulary_axes"], [])
        self.assertIs(status["library_present"], False)
        self.assertEqual(status["export"], {"enabled": False, "dir": None})
        self.assertEqual(status["root"], "brushes")

    def test_a_data_call_without_a_catalog_lists_the_commands_in_order(self):
        svc = self.service()
        for call in (lambda: svc.search("ink"), lambda: svc.facets(), lambda: svc.list_sets(),
                     lambda: svc.similar("b_0123456789ab"), lambda: svc.get_brush("b_0123456789ab")):
            with self.assertRaises(service.ApiError) as caught:
                call()
            error = caught.exception
            self.assertEqual((error.code, error.status), ("not_ingested", 503))
            self.assertIn("python brushes/pipeline/ingest.py build", error.hint)
            self.assertLess(error.hint.index("ingest.py"), error.hint.index("brush_search.py"))

    def test_the_methods_that_need_no_catalog_still_work(self):
        svc = self.service()
        self.assertIn("groups", svc.settings_schema())
        self.assertEqual(svc.vocabulary()["axes"], {})
        report = svc.validate_patch({"plotSpacing": 0.2}, era="E4")
        self.assertTrue(report["ok"])
        self.assertEqual(report["base"]["kind"], "schema_defaults")

    def test_a_catalog_and_no_index_file_is_memory_and_nothing_is_written(self):
        world = World(self.root)
        before = snapshot(self.tmp)
        svc = self.service()
        status = svc.status()
        self.assertEqual(status["index"]["state"], "memory")
        self.assertIn("is missing", status["index"]["reason"])
        self.assertEqual(status["counts"]["brushes"], 8)
        envelope = svc.search("inker")
        self.assertEqual(envelope["index"], "memory")
        self.assertEqual(svc.status()["index"]["state"], "memory")
        self.assertFalse(world.paths.index.exists())
        self.assertEqual(snapshot(self.tmp), before)

    def test_a_fresh_index_file_is_fresh_and_a_changed_input_makes_it_stale(self):
        world = World(self.root)
        world.build_index()
        svc = self.service()
        self.assertEqual(svc.status()["index"]["state"], "fresh")
        self.assertEqual(svc.search("inker")["index"], "fresh")
        note = next(world.paths.vault.glob("0*_*/*.md"))
        note.write_bytes(note.read_bytes() + b"\nA line the index has not seen.\n")
        status = svc.status()
        self.assertEqual(status["index"]["state"], "stale")
        self.assertIn("notes", status["index"]["reason"])
        self.assertEqual(svc.search("inker")["index"], "stale", "a stale index is still served, and flagged")

    def test_an_unreadable_index_file_is_memory(self):
        world = World(self.root)
        world.paths.index.parent.mkdir(parents=True, exist_ok=True)
        world.paths.index.write_bytes(b"not json at all")
        svc = self.service()
        self.assertEqual(svc.search("inker")["index"], "memory")
        self.assertIn("unreadable", svc.status()["index"]["reason"])

    def test_a_catalog_that_cannot_be_read_is_not_ingested_not_a_crash(self):
        world = World(self.root)
        (world.paths.catalog / "catalog.json").write_bytes(b"{broken")
        svc = self.service()
        self.assertEqual(svc.status()["index"]["state"], "not_ingested")
        self.assertIsNone(svc.status()["counts"])
        self.assertApi("not_ingested", svc.search, "ink", status=503)

    def test_the_state_is_always_one_of_the_four(self):
        seen = set()
        svc = self.service()
        seen.add(svc.status()["index"]["state"])
        world = World(self.root)
        seen.add(self.service().status()["index"]["state"])
        world.build_index()
        seen.add(self.service().status()["index"]["state"])
        note = next(world.paths.vault.glob("0*_*/*.md"))
        note.write_bytes(note.read_bytes() + b"\nmore\n")
        seen.add(self.service().status()["index"]["state"])
        self.assertEqual(seen, set(service.INDEX_STATES))

    def test_counts_are_the_catalogs_own_and_the_library_is_counted_by_name(self):
        world = World(self.root)
        status = self.service().status()
        catalog = json.loads((world.paths.catalog / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(status["counts"], catalog["counts"])
        self.assertEqual(status["library_files"]["user"], {"files": 3, "brushset": 1, "brush": 2})
        self.assertEqual(status["library_files"]["official"], {"files": 1, "brushset": 1, "brush": 0})
        self.assertIs(status["library_present"], True)
        self.assertEqual(status["next_steps"], ["python brushes/vault/tools/brush_search.py index"])

    def test_the_export_block_names_the_folder_relative_to_the_base(self):
        World(self.root)
        status = self.service(export_dir=self.tmp / "exports").status()
        self.assertEqual(status["export"], {"enabled": True, "dir": "exports"})
        self.assertNotIn(str(self.tmp), json.dumps(status))

    def test_the_vocabulary_axes_come_from_the_vault(self):
        world = World(self.root)
        vocabulary = world.paths.vocabulary
        vocabulary.parent.mkdir(parents=True, exist_ok=True)
        vocabulary.write_text("# medium_tags: the tool\nmedium_tags:\n  - charcoal   # coarse black\n"
                              "mark_tags:\n  - line   # one stroke\n", encoding="utf-8", newline="\n")
        self.assertEqual(self.service().status()["vocabulary_axes"], ["medium", "mark"])
        listed = self.service().vocabulary()
        self.assertEqual(list(listed["axes"]), ["medium", "mark"])
        self.assertEqual(listed["axes"]["medium"]["description"], "the tool")
        self.assertEqual(listed["axes"]["medium"]["tags"], [{"tag": "charcoal", "definition": "coarse black"}])
        self.assertEqual(list(self.service().vocabulary("mark_tags")["axes"]), ["mark"])
        self.assertApi("bad_argument", self.service().vocabulary, "colour")

    def test_the_mode_is_checked(self):
        with self.assertRaises(ValueError):
            service.BrushService(bc.resolve_paths(root=self.root), mode="other")
        self.assertEqual(self.service(mode="snapshot").status()["mode"], "snapshot")


# ── search, similar, facets, sets ────────────────────────────────────────────

class Search(WorldCase):
    def test_words_find_a_brush_and_the_envelope_carries_the_index(self):
        envelope = self.svc.search("conte")
        self.assertEqual(envelope["results"][0]["name"], "Broken Cont\u00e9")
        self.assertEqual(envelope["results"][0]["brush_id"], self.ident("conte"))
        self.assertEqual(envelope["ranking"], "cosine")
        self.assertEqual(envelope["index"], "memory")
        for key in ("query", "tags", "where", "where_not", "total", "offset", "results"):
            self.assertIn(key, envelope)

    def test_only_brushes_are_returned(self):
        for row in self.svc.search("demo", top=50)["results"]:
            self.assertEqual(row["source_type"], "brush")
            self.assertRegex(row["brush_id"], r"^b_[0-9a-f]{12}$")

    def test_no_query_and_no_filter_browses_in_set_order(self):
        envelope = self.svc.search()
        self.assertEqual(envelope["ranking"], "filter-order")
        self.assertEqual(envelope["total"], 8)
        self.assertEqual(self.svc.search(top=3, offset=3)["offset"], 3)
        self.assertEqual(len(self.svc.search(top=3, offset=6)["results"]), 2)

    def test_a_filter_narrows(self):
        envelope = self.svc.search(where=["kind=stamp"])
        self.assertEqual([r["brush_id"] for r in envelope["results"]], [self.ident("inker2")])
        self.assertEqual(self.svc.search(where_not=["kind=stamp"])["total"], 7)
        self.assertEqual(self.svc.search(where=["library=official"])["total"], 3)
        self.assertEqual(self.svc.search("modern", where=["library=user"])["total"], 0)

    def test_an_unknown_tag_or_filter_is_bad_argument_with_the_valid_list(self):
        error = self.assertApi("bad_argument", self.svc.search, tags=["colour=nope"], status=400)
        self.assertIn("medium", error.message + (error.hint or ""), "the valid axes are listed")
        error = self.assertApi("bad_argument", self.svc.search, tags=["texture=nope"], status=400)
        self.assertIn("texture", error.message)
        error = self.assertApi("bad_argument", self.svc.search, where=["no_such_facet=1"])
        self.assertTrue(error.message)
        self.assertApi("bad_argument", self.svc.search, tags=["medium"])
        self.assertApi("bad_argument", self.svc.search, tags=["Medium=x"])
        self.assertApi("bad_argument", self.svc.search, tags="medium=charcoal")

    def test_the_limits_are_checked(self):
        for kwargs in ({"top": 0}, {"top": 201}, {"top": True}, {"top": "5"}, {"top": 1.5}, {"offset": -1},
                       {"offset": 100001}, {"query": "x" * 501}, {"query": 7}, {"query": "a\x00b"},
                       {"where": ["a=b"] * 13}, {"tags": ["medium=x"] * 13}, {"where": ["x" * 121]}):
            self.assertApi("bad_argument", self.svc.search, **kwargs)
        self.assertApi("bad_argument", self.svc.search, top=26, top_max=25)
        self.assertEqual(len(self.svc.search(top=25, top_max=25)["results"]), 8)

    def test_a_filter_is_required_when_the_caller_says_so(self):
        self.assertApi("bad_argument", self.svc.search, require_filter=True)
        self.assertApi("bad_argument", self.svc.search, "   ", require_filter=True)
        self.assertEqual(self.svc.search("inker", require_filter=True)["index"], "memory")

    def test_a_query_with_no_usable_word_is_empty_not_an_error(self):
        envelope = self.svc.search("zzzzqqq nothing matches this")
        self.assertEqual((envelope["total"], envelope["results"]), (0, []))

    def test_settings_are_included_only_when_asked(self):
        self.assertNotIn("settings", self.svc.search("inker")["results"][0])
        self.assertIn("settings", self.svc.search("inker", settings=True)["results"][0])


class Similar(WorldCase):
    def test_neighbours_of_a_brush(self):
        envelope = self.svc.similar(self.ident("inker"), top=3)
        self.assertEqual(envelope["method"], "gower-v1")
        self.assertEqual(envelope["query"]["brush_id"], self.ident("inker"))
        self.assertEqual(len(envelope["results"]), 3)
        self.assertNotIn(self.ident("inker"), [r["brush_id"] for r in envelope["results"]])
        row = envelope["results"][0]
        for key in ("compared_keys", "coverage", "differs"):
            self.assertIn(key, row)
        self.assertEqual(envelope["index"], "memory")

    def test_unknown_and_malformed_ids(self):
        self.assertApi("unknown_id", self.svc.similar, "b_000000000000", status=404)
        self.assertApi("bad_argument", self.svc.similar, "inker")
        self.assertApi("bad_argument", self.svc.similar, self.ident("inker"), top=0)

    def test_settings_that_are_not_a_library_brush(self):
        base = json.loads((self.world.paths.catalog / "brushes" / f"{self.ident('inker')}.json")
                          .read_text(encoding="utf-8"))["settings"]
        envelope = self.svc.similar_settings(base, top=2)
        top = envelope["results"][0]["score"]
        self.assertEqual(top, 1.0)
        self.assertIn(self.ident("inker"), [r["brush_id"] for r in envelope["results"] if r["score"] == top],
                      "the brush itself is as close as anything")
        self.assertIsNone(envelope["query"]["brush_id"])
        for bad in (None, {}, [], "x"):
            self.assertApi("bad_argument", self.svc.similar_settings, bad)

    def test_other_sets_leaves_the_brushs_own_set_out(self):
        own = self.svc.search(where=["set=demo-set"], top=50)["results"]
        self.assertTrue(own)
        envelope = self.svc.similar(self.ident("inker"), top=25, other_sets=True)
        self.assertTrue(all(r["set"] != "demo-set" for r in envelope["results"]))


class Facets(WorldCase):
    def test_counts_over_the_brushes(self):
        counts = self.svc.facets()
        self.assertEqual(counts["brushes"], 8)
        self.assertEqual(counts["index"], "memory")
        self.assertEqual(counts["facets"]["kind"]["values"], {"stamp": 1, "stroke": 7})
        self.assertEqual(self.svc.facets(where=["kind=stamp"])["brushes"], 1)
        self.assertApi("bad_argument", self.svc.facets, where=["nope=1"])

    def test_the_vocabulary_lists_facets_with_their_rules(self):
        facets = {row["name"]: row for row in self.svc.vocabulary()["facets"]}
        self.assertEqual(facets["kind"]["type"], "enum")
        self.assertEqual(facets["kind"]["values"], ["stamp", "stroke"])
        self.assertTrue(facets["kind"]["description"])
        self.assertIn(facets["spacing"]["type"], ("enum", "number"), "a few brushes make it an enum")
        self.assertTrue(facets["spacing"]["values"])


class Sets(WorldCase):
    def test_every_set_with_its_keys(self):
        sets = self.svc.list_sets()["sets"]
        self.assertEqual({s["set_slug"] for s in sets}, {"demo-set", "demo-modern", "demo-pack-loose"})
        for row in sets:
            for key in ("set_slug", "set_id", "name", "library", "vendor", "brush_count", "tagged", "note"):
                self.assertIn(key, row)
            self.assertEqual(row["tagged"], 0)
        demo = next(s for s in sets if s["set_slug"] == "demo-set")
        self.assertEqual((demo["name"], demo["brush_count"], demo["library"], demo["vendor"]),
                         ("Demo Set ", 4, "user", "Fixture Vendor"))
        loose = next(s for s in sets if s["set_slug"] == "demo-pack-loose")
        self.assertEqual((loose["kind"], loose["title"]), ("loose", "Demo Pack (loose brushes)"))

    def test_a_library_narrows(self):
        self.assertEqual([s["set_slug"] for s in self.svc.list_sets("official")["sets"]], ["demo-modern"])
        self.assertEqual(len(self.svc.list_sets("user")["sets"]), 2)
        self.assertApi("bad_argument", self.svc.list_sets, "both")

    def test_one_set_with_its_rows_in_order(self):
        one_set = self.svc.get_set("demo-set")
        self.assertEqual([r["name"] for r in one_set["brushes"]],
                         ["Demo Inker", "Demo  Pencil", "Broken Cont\u00e9", "Demo Inker"])
        self.assertEqual(one_set["set"]["brush_count"], 4)
        self.assertEqual(one_set["brushes"][0]["brush_id"], self.ident("inker"))
        self.assertApi("unknown_id", self.svc.get_set, "no-such-set", status=404)
        self.assertApi("bad_argument", self.svc.get_set, "../etc")


# ── one brush, previews, schema ──────────────────────────────────────────────

class GetBrush(WorldCase):
    def test_the_default_parts(self):
        brush = self.svc.get_brush(self.ident("inker"))
        self.assertEqual((brush["id"], brush["name"], brush["library"], brush["era"], brush["family"]),
                         (self.ident("inker"), "Demo Inker", "user", "E4", "legacy"))
        self.assertEqual(brush["home"]["set_slug"], "demo-set")
        self.assertEqual([s["set_slug"] for s in brush["sets"]], ["demo-set", "demo-pack-loose"])
        self.assertIsNone(brush["dual"])
        self.assertEqual(brush["preview_kinds"], ["stroke", "shape", "grain"])
        self.assertIs(brush["approximate"], False)
        self.assertEqual(brush["tag_state"], "untagged")
        self.assertEqual(brush["medium_tags"], [])
        self.assertEqual(brush["visual"], "")
        self.assertIsNone(brush["visual_basis"])
        self.assertEqual(brush["textures"]["shape"]["source"], "embedded")
        self.assertIn("kind", brush["facets"])
        self.assertTrue(brush["note"]["path"].endswith("demo-set.md"))
        self.assertGreater(brush["note"]["lines"][0], 0)
        self.assertNotIn("settings", brush)
        self.assertEqual(brush["duplicates"][0]["set"], "demo-pack-loose")

    def test_include_chooses_the_parts(self):
        brush = self.svc.get_brush(self.ident("inker"), ["settings"])
        self.assertIn("settings", brush)
        for absent in ("facets", "tag_state", "visual", "textures", "note"):
            self.assertNotIn(absent, brush)
        self.assertEqual(set(self.svc.get_brush(self.ident("inker"), "settings,note")) & {"settings", "note"},
                         {"settings", "note"})
        self.assertApi("bad_argument", self.svc.get_brush, self.ident("inker"), ["everything"])
        self.assertApi("bad_argument", self.svc.get_brush, self.ident("inker"), ["settings"] * 7)

    def test_a_dual_brush_names_its_second_brush(self):
        dual = self.svc.get_brush(self.ident("dual"))
        self.assertEqual(dual["dual"]["name"], "Modern Dual Secondary")
        self.assertEqual(set(dual["dual"]), {"name", "era", "blend_code"})
        self.assertEqual(dual["family"], "modern")

    def test_unknown_and_malformed_ids(self):
        self.assertApi("unknown_id", self.svc.get_brush, "b_000000000000", status=404)
        for bad in ("../../etc/passwd", "b_0123456789ab/../x", "b_0123456789ab.json", "B_0123456789AB"):
            self.assertApi("bad_argument", self.svc.get_brush, bad, status=400)

    def test_settings_are_every_archive_key_as_the_catalog_holds_them(self):
        record = json.loads((self.world.paths.catalog / "brushes" / f"{self.ident('dual')}.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(self.svc.get_brush(self.ident("dual"), ["settings"])["settings"], record["settings"])


class Previews(WorldCase):
    def test_a_stored_preview_is_served_whole(self):
        data, meta = self.svc.preview(self.ident("inker"), "stroke")
        self.assertTrue(data.startswith(png_io.SIGNATURE))
        self.assertEqual((meta["kind"], meta["width"], meta["height"]), ("stroke", 530, 162))
        self.assertIs(meta["approximate"], False)
        path = self.world.paths.previews / "demo-set" / f"{self.ident('inker')}.stroke.png"
        self.assertEqual(data, path.read_bytes())
        for kind in ("shape", "grain"):
            tile, meta = self.svc.preview(self.ident("inker"), kind)
            self.assertEqual((meta["width"], meta["height"]), (256, 256))

    def test_a_bundled_texture_has_no_tile(self):
        error = self.assertApi("no_preview", self.svc.preview, self.ident("pencil"), "shape", status=404)
        self.assertIn("inside the drawing app", error.message)
        self.assertIn("previews.py", error.hint)

    def test_ids_and_kinds_are_checked(self):
        self.assertApi("unknown_id", self.svc.preview, "b_000000000000", "stroke")
        self.assertApi("bad_argument", self.svc.preview, "b_0123456789ab/../..", "stroke")
        self.assertApi("bad_argument", self.svc.preview, self.ident("inker"), "thumbnail")
        self.assertApi("bad_argument", self.svc.preview, self.ident("inker"), "../stroke")

    def test_a_stored_path_that_leaves_the_previews_folder_is_refused(self):
        world = self.copy_world()
        secret = world.root / "vault" / "secret.png"
        secret.write_bytes(png_io.SIGNATURE + b"stolen")
        outside = world.root.parent / "outside.png"
        outside.write_bytes(fixtures.make_png())
        record_path = world.paths.catalog / "brushes" / f"{world.ids['inker']}.json"
        for evil in ("../secret.png", "_Previews/../secret.png", "_Previews/x/../../secret.png",
                     str(outside), outside.as_posix(), "C:/Windows/win.ini", "/etc/passwd", "..\\secret.png",
                     "_Previews\\demo-set\\x.png", "_Previews/demo-set/\x00.png", "", "_Previews/", "_Previews/.."):
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["preview"]["stroke"] = evil
            record_path.write_text(json.dumps(record), encoding="utf-8", newline="\n")
            error = self.assertApi("no_preview", world.service().preview, world.ids["inker"], "stroke")
            self.assertNotIn("stolen", error.message)
            self.assertNotIn(str(world.root), error.message)

    def test_a_link_or_junction_out_of_the_previews_folder_is_refused(self):
        world = self.copy_world()
        outside = world.root.parent / "outside-previews"
        outside.mkdir()
        (outside / "x.png").write_bytes(fixtures.make_png())
        record_path = world.paths.catalog / "brushes" / f"{world.ids['inker']}.json"
        tried = 0
        for name, target, directory in (("linked-dir", outside, True), ("linked.stroke.png", outside / "x.png", False)):
            link = world.paths.previews / name
            if not make_link(link, target, directory=directory):
                continue
            tried += 1
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["preview"]["stroke"] = f"_Previews/{name}" + ("/x.png" if directory else "")
            record_path.write_text(json.dumps(record), encoding="utf-8", newline="\n")
            self.assertTrue((world.paths.vault / record["preview"]["stroke"]).is_file(), "the link works")
            self.assertApi("no_preview", world.service().preview, world.ids["inker"], "stroke")
        if not tried:
            self.skipTest("this account can make neither a symbolic link nor a junction")

    def test_a_file_that_is_not_a_png_or_is_too_large_is_refused(self):
        world = self.copy_world()
        path = world.paths.previews / "demo-set" / f"{world.ids['inker']}.stroke.png"
        path.write_bytes(b"not a png")
        self.assertApi("no_preview", world.service().preview, world.ids["inker"], "stroke")
        path.write_bytes(png_io.SIGNATURE + bytes(service.PREVIEW_MAX_BYTES + 10))
        self.assertApi("no_preview", world.service().preview, world.ids["inker"], "stroke")
        path.unlink()
        self.assertApi("no_preview", world.service().preview, world.ids["inker"], "stroke")

    def test_preview_set_gives_what_exists_and_names_what_does_not(self):
        payload, files = self.svc.preview_set(self.ident("pencil"), ["stroke", "shape", "grain"])
        self.assertEqual([kind for kind, _ in files], ["stroke"])
        self.assertEqual([i["kind"] for i in payload["images"]], ["stroke"])
        self.assertEqual([m["kind"] for m in payload["missing"]], ["shape", "grain"])
        self.assertEqual(payload["name"], "Demo  Pencil")
        error = self.assertApi("no_preview", self.svc.preview_set, self.ident("pencil"), ["shape"])
        self.assertIn("missing", error.data)
        self.assertApi("bad_argument", self.svc.preview_set, self.ident("pencil"), [])
        self.assertApi("bad_argument", self.svc.preview_set, self.ident("pencil"), "stroke")
        payload, files = self.svc.preview_set(self.ident("inker"), ["stroke", "stroke"])
        self.assertEqual(len(files), 1, "a kind asked for twice is sent once")


class SettingsSchema(WorldCase):
    def test_compact_rows(self):
        schema = self.svc.settings_schema()
        self.assertEqual(len(schema["keys"]), 260)
        self.assertEqual(schema["keys"]["plotSpacing"]["t"], "real")
        self.assertEqual(set(schema["keys"]["plotSpacing"]), {"t", "min", "max", "def", "eras", "group"})
        self.assertIn("stroke", [g["group"] for g in schema["groups"]])
        self.assertEqual(sum(g["keys"] for g in schema["groups"]), 260)

    def test_a_group_and_keys_narrow_it(self):
        group = self.svc.settings_schema(group="stroke")
        self.assertTrue(group["keys"])
        self.assertTrue(all(row["group"] == "stroke" for row in group["keys"].values()))
        named = self.svc.settings_schema(keys=["plotSpacing", "stamp", "nope"], detail="full")
        self.assertEqual(sorted(named["keys"]), ["plotSpacing", "stamp"])
        self.assertEqual(named["unknown_keys"], ["nope"])
        self.assertIn("label", named["keys"]["plotSpacing"])
        self.assertIn("observed", named["keys"]["plotSpacing"])

    def test_arguments_are_checked(self):
        self.assertApi("bad_argument", self.svc.settings_schema, group="no-such-tab")
        self.assertApi("bad_argument", self.svc.settings_schema, detail="long")
        self.assertApi("bad_argument", self.svc.settings_schema, keys=["a"] * 61)
        self.assertApi("bad_argument", self.svc.settings_schema, keys="plotSpacing")


# ── patches ──────────────────────────────────────────────────────────────────

class ValidatePatch(WorldCase):
    def test_against_a_library_brush(self):
        report = self.svc.validate_patch({"plotSpacing": 0.25, "stamp": True}, base_id=self.ident("inker"))
        self.assertTrue(report["ok"])
        self.assertEqual(report["era"], "E4")
        self.assertEqual(report["applied"], {"plotSpacing": 0.25, "stamp": True})
        self.assertEqual(report["base"], {"kind": "library", "id": self.ident("inker"), "era": "E4"})
        for key in ("clamped", "rejected", "unchanged", "warnings"):
            self.assertIn(key, report)
        envelope = json.loads(report["patch_text"])
        self.assertEqual(envelope, {"schema": "rosw-brushes-patch/1", "base_id": self.ident("inker"),
                                    "summary": envelope["summary"], "changes": report["applied"]})
        self.assertIn("2 setting(s)", envelope["summary"])

    def test_a_value_equal_to_the_base_is_unchanged_not_applied(self):
        report = self.svc.validate_patch({"name": "Demo Inker", "stamp": False}, base_id=self.ident("inker"))
        self.assertEqual((report["applied"], report["unchanged"]), ({}, ["name", "stamp"]))
        self.assertIsNone(report["patch_text"])

    def test_rejections_say_why(self):
        report = self.svc.validate_patch({"noSuchKey": 1, "plotSpacing": "wide", "stamp": 5},
                                         base_id=self.ident("inker"))
        self.assertFalse(report["ok"])
        codes = {r["key"]: r["code"] for r in report["rejected"]}
        self.assertEqual(codes["noSuchKey"], "unknown_key")
        self.assertEqual(codes["plotSpacing"], "wrong_type")
        self.assertEqual(codes["stamp"], "wrong_type")
        for item in report["rejected"]:
            self.assertEqual(set(item), {"key", "value", "code", "reason"})
        self.assertIsNone(report["patch_text"], "nothing applied, nothing to paste")

    def test_a_modern_key_on_a_legacy_brush_is_not_in_era(self):
        report = self.svc.validate_patch({"renderingMaxTransfer": True}, base_id=self.ident("inker"))
        self.assertEqual([(r["key"], r["code"]) for r in report["rejected"]], [("renderingMaxTransfer", "not_in_era")])

    def test_against_a_base_of_members(self):
        base = {"members": [{"path": path, "b64": service.b64(data)}
                            for path, data in self.world.brushes["inker"].members]}
        report = self.svc.validate_patch({"plotSpacing": 0.25}, base=base)
        self.assertEqual((report["ok"], report["base"]), (True, {"kind": "members", "era": "E4"}))
        only_archive = {"members": [{"path": "Brush.archive",
                                     "b64": service.b64(self.world.brushes["inker"].archive)}]}
        self.assertTrue(self.svc.validate_patch({"plotSpacing": 0.25}, base=only_archive, era="E4")["ok"])

    def test_the_base_is_named_one_way_only(self):
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True}, base_id=self.ident("inker"),
                       base={"members": []})
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True}, base=[1])
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True},
                       base={"members": [{"path": "Brush.archive", "b64": "!!"}]})
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True}, base={"model": {}})
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True},
                       base={"members": [{"path": "Shape.png", "b64": ""}]})
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True},
                       base={"members": [{"path": "../Brush.archive", "b64": "QQ=="}]})

    def test_an_era_given_with_a_base_must_be_the_bases_own(self):
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True}, base_id=self.ident("inker"),
                       era="M220")
        self.assertTrue(self.svc.validate_patch({"stamp": True}, base_id=self.ident("inker"), era="E4")["ok"])

    def test_with_no_base_the_template_of_the_era_is_used_or_the_schema_defaults_say_so(self):
        report = self.svc.validate_patch({"plotSpacing": 0.3})
        self.assertTrue(report["ok"])
        self.assertEqual(report["era"], brush_model.NEW_BRUSH_ERA)
        self.assertEqual(report["base"]["kind"], "schema_defaults", "the fixture library has no donor brush")
        self.assertIn("donor", report["base"]["note"])
        self.assertEqual(self.svc.validate_patch({"plotSpacing": 0.3}, era="E0")["era"], "E0")
        self.assertApi("bad_argument", self.svc.validate_patch, {"plotSpacing": 0.3}, era="Z9")

    def test_arguments_are_checked(self):
        for changes in (None, [], "x", 5):
            self.assertApi("bad_argument", self.svc.validate_patch, changes)
        self.assertApi("bad_argument", self.svc.validate_patch, {f"k{i}": 1 for i in range(401)})
        self.assertApi("bad_argument", self.svc.validate_patch, {"stamp": True}, base_id="inker")
        self.assertApi("unknown_id", self.svc.validate_patch, {"stamp": True}, base_id="b_000000000000")
        self.assertApi("too_large", self.svc.validate_patch, {"name": "x" * (2 * 1024 * 1024)})

    def test_without_the_originals_a_library_base_is_library_missing(self):
        world = self.copy_world(library=False)
        error = self.assertApi("library_missing", world.service().validate_patch, {"stamp": True},
                               base_id=world.ids["inker"], status=409)
        self.assertNotIn(str(world.root), error.message)

    def test_the_cases_of_the_patch_file_give_the_same_reports_through_the_service(self):
        cases = json.loads((BRUSHES / "schema" / "patch_cases.json").read_text(encoding="utf-8"))["cases"]
        self.assertGreater(len(cases), 10)
        for case in cases:
            base = brush_model.case_base(case["era"], case.get("assign"))
            _, report = service.BrushService.report_patch(
                base, case["changes"], mode=case.get("mode", "strict"),
                allow_unknown=case.get("allow_unknown", False))
            expect = case["expect"]
            for key in ("ok", "era", "applied", "clamped", "unchanged", "warnings"):
                self.assertEqual(report[key], expect[key], (case["id"], key))
            self.assertEqual([(r["key"], r["code"], r["value"]) for r in report["rejected"]],
                             [(r["key"], r["code"], r["value"]) for r in expect["rejected"]], case["id"])


# ── the library's originals, and import ──────────────────────────────────────

class OpenLibraryBrush(WorldCase):
    def test_every_brush_opens_with_its_original_settings(self):
        for name, brush in self.world.brushes.items():
            response = self.svc.open_library_brush(self.ident(name))
            decoded = brush_model.decode(brush.archive)
            self.assertEqual(response["kind"], "brush", name)
            self.assertEqual((response["name"], response["era"], response["library_id"]),
                             (decoded.name, decoded.era, self.ident(name)), name)
            self.assertEqual(response["settings"], brush_model.to_json(decoded)["params"], name)
            self.assertEqual(response["meta"]["archive_sha256"], hashlib.sha256(brush.archive).hexdigest())
            self.assertEqual(response["meta"]["class"], "SilicaBrush")
            self.assertEqual(response["meta"]["key_count"], decoded.key_count)
            self.assertEqual(response["meta"]["unknown_keys"], [])
            self.assertEqual(response["base"]["members"], [
                {"path": path, "b64": service.b64(data)} for path, data in brush.members], name)

    def test_textures_embedded_bundled_blank_and_none(self):
        inker = self.svc.open_library_brush(self.ident("inker"))["textures"]
        self.assertEqual(inker["shape"]["source"], "embedded")
        self.assertEqual(base64_of(inker["shape"]["png_b64"]), self.world.brushes["inker"].shape)
        self.assertEqual((inker["shape"]["width"], inker["shape"]["height"]), (8, 8))
        self.assertEqual(base64_of(inker["thumbnail"]["png_b64"]),
                         self.world.brushes["inker"].member(container.THUMBNAIL))
        pencil = self.svc.open_library_brush(self.ident("pencil"))["textures"]
        self.assertEqual(pencil["shape"], {"source": "bundled", "ref": fixtures.BUNDLED_SHAPE,
                                           "standin_png_b64": None, "approximate": True})
        self.assertEqual(pencil["grain"], {"source": "blank", "ref": fixtures.BLANK_GRAIN})
        conte = self.svc.open_library_brush(self.ident("conte"))["textures"]
        self.assertEqual(conte["grain"], {"source": "none"})
        plain = self.svc.open_library_brush(self.ident("plain"))["textures"]
        self.assertIsNone(plain["thumbnail"])

    def test_a_dual_brush_carries_its_second_brush(self):
        response = self.svc.open_library_brush(self.ident("dual"))
        self.assertEqual(response["sub"]["settings"]["name"], "Modern Dual Secondary")
        self.assertEqual(set(response["sub"]), {"settings", "textures", "meta"})
        self.assertIsNone(self.svc.open_library_brush(self.ident("inker"))["sub"])

    def test_texture_modes(self):
        none = self.svc.open_library_brush(self.ident("inker"), "none")
        self.assertNotIn("png_b64", none["textures"]["shape"])
        self.assertEqual(none["textures"]["thumbnail"], {"present": True})
        self.assertEqual(none["base"], {"library_id": self.ident("inker")})
        preview = self.svc.open_library_brush(self.ident("inker"), "preview")
        tile = base64_of(preview["textures"]["shape"]["png_b64"])
        self.assertTrue(tile.startswith(png_io.SIGNATURE))
        self.assertIs(preview["textures"]["shape"]["preview"], True)
        self.assertEqual(preview["base"], {"library_id": self.ident("inker")})
        self.assertApi("bad_argument", self.svc.open_library_brush, self.ident("inker"), "huge")

    def test_unknown_malformed_and_missing_originals(self):
        self.assertApi("unknown_id", self.svc.open_library_brush, "b_000000000000", status=404)
        self.assertApi("bad_argument", self.svc.open_library_brush, "x")
        world = self.copy_world(library=False)
        self.assertApi("library_missing", world.service().open_library_brush, world.ids["inker"], status=409)

    def test_a_catalog_path_that_leaves_the_library_is_refused(self):
        world = self.copy_world()
        outside = world.root.parent / "elsewhere.brush"
        outside.write_bytes(fixtures.brush_file(self.world.brushes["inker"]))
        record_path = world.paths.catalog / "brushes" / f"{world.ids['marker']}.json"
        for evil in ("../../elsewhere.brush", str(outside), "user/../../../elsewhere.brush", "/x.brush",
                     "user\\demo-pack\\Loose_Marker.brush", "user/demo-pack/Loose_Marker.txt", "",
                     "C:/x.brush", "user//Loose_Marker.brush"):
            record = json.loads(record_path.read_text(encoding="utf-8"))
            for occurrence in record["occurrences"]:
                occurrence["container"] = evil
            record_path.write_text(json.dumps(record), encoding="utf-8", newline="\n")
            error = self.assertApi("library_missing", world.service().open_library_brush, world.ids["marker"])
            self.assertNotIn(str(world.root.parent), error.message)

    def test_a_brush_that_changed_since_the_catalog_is_not_returned_under_its_old_id(self):
        world = self.copy_world()
        target = world.paths.library / "user" / "demo-pack" / "Loose_Marker.brush"
        other = fixtures.make_brush("Someone Else", number=77)
        target.write_bytes(fixtures.brush_file(other))
        self.assertApi("library_missing", world.service().open_library_brush, world.ids["marker"])

    def test_a_git_lfs_pointer_says_to_pull(self):
        world = self.copy_world()
        (world.paths.library / "user" / "demo-pack" / "Loose_Marker.brush").write_bytes(fixtures.LFS_POINTER)
        error = self.assertApi("library_missing", world.service().open_library_brush, world.ids["marker"])
        self.assertIn("git lfs pull", error.message + (error.hint or ""))


def base64_of(text):
    import base64
    return base64.b64decode(text)


class Import(WorldCase):
    def setUp(self):
        super().setUp()
        self.set_bytes = (self.world.paths.library / "user" / "demo-pack" / "Demo_Set.brushset").read_bytes()
        self.brush_bytes = (self.world.paths.library / "user" / "demo-pack" / "Loose_Marker.brush").read_bytes()

    def test_a_set_gives_a_manifest(self):
        manifest = self.svc.decode_upload(self.set_bytes, "Demo_Set.brushset")
        self.assertEqual((manifest["kind"], manifest["name"], manifest["brush_count"]), ("brushset", "Demo Set ", 4))
        self.assertEqual([b["name"] for b in manifest["brushes"]],
                         ["Demo Inker", "Demo  Pencil", "Broken Cont\u00e9", "Demo Inker"])
        first = manifest["brushes"][0]
        self.assertEqual(set(first), {"member", "index", "name", "era", "key_count", "shape", "grain", "dual",
                                      "has_thumbnail", "library_id"})
        self.assertEqual((first["era"], first["key_count"], first["dual"], first["has_thumbnail"]),
                         ("E4", 101, False, True))
        self.assertEqual(first["shape"], {"source": "embedded", "ref": None})
        self.assertEqual(manifest["brushes"][1]["shape"], {"source": "bundled", "ref": fixtures.BUNDLED_SHAPE})
        self.assertEqual([b["library_id"] for b in manifest["brushes"]],
                         [self.ident(n) for n in ("inker", "pencil", "conte", "inker2")])
        self.assertEqual(len({b["member"] for b in manifest["brushes"]}), 4)

    def test_a_member_gives_that_brush_and_one_brush_gives_itself(self):
        manifest = self.svc.decode_upload(self.set_bytes, "Demo_Set.brushset")
        third = manifest["brushes"][2]
        brush = self.svc.decode_upload(self.set_bytes, "Demo_Set.brushset", member=third["member"])
        self.assertEqual((brush["kind"], brush["name"], brush["member"]), ("brush", "Broken Cont\u00e9", third["member"]))
        self.assertEqual(brush["library_id"], self.ident("conte"))
        self.assertEqual(brush["settings"], brush_model.to_json(brush_model.decode(
            self.world.brushes["conte"].archive))["params"])
        loose = self.svc.decode_upload(self.brush_bytes, "Loose_Marker.brush")
        self.assertEqual((loose["kind"], loose["name"], loose["library_id"]), ("brush", "Loose Marker", self.ident("marker")))
        self.assertEqual([m["path"] for m in loose["base"]["members"]], self.world.brushes["marker"].paths())

    def test_a_brush_the_catalog_does_not_know_has_no_library_id(self):
        other = fixtures.brush_file(fixtures.make_brush("Stranger", number=88))
        self.assertIsNone(self.svc.decode_upload(other, "Stranger.brush")["library_id"])

    def test_an_import_keeps_every_original_member_for_the_export(self):
        brush = self.svc.decode_upload(self.set_bytes, member=self.svc.decode_upload(
            self.set_bytes)["brushes"][0]["member"])
        members = {m["path"]: base64_of(m["b64"]) for m in brush["base"]["members"]}
        self.assertEqual(members, dict(self.world.brushes["inker"].members))

    def test_the_member_and_texture_arguments_are_checked(self):
        self.assertApi("bad_argument", self.svc.decode_upload, self.set_bytes, member="s0/NOPE")
        self.assertApi("bad_argument", self.svc.decode_upload, self.set_bytes, member="x" * 401)
        self.assertApi("bad_argument", self.svc.decode_upload, self.brush_bytes, textures="big")
        self.assertApi("bad_argument", self.svc.decode_upload, b"")
        self.assertApi("bad_argument", self.svc.decode_upload, "text")

    def test_garbage_is_unsupported_and_a_pointer_says_to_pull(self):
        self.assertApi("unsupported_file", self.svc.decode_upload, b"this is not a zip file at all", status=415)
        self.assertApi("unsupported_file", self.svc.decode_upload, fixtures.make_zip([("readme.txt", b"hi")]),
                       status=415)
        self.assertApi("library_missing", self.svc.decode_upload, fixtures.LFS_POINTER, status=409)

    def test_hostile_files_end_in_an_api_error_or_a_clean_result_never_a_crash(self):
        for name, data in fixtures.hostile_files().items():
            try:
                result = self.svc.decode_upload(data, name)
            except service.ApiError as exc:
                self.assertIn(exc.code, {"unsupported_file", "corrupt_file", "library_missing", "too_large",
                                         "bad_argument"}, name)
                self.assertNotIn(str(self.world.root), exc.message)
            else:
                self.assertIn(result["kind"], {"brush", "brushset"}, name)

    def test_entries_outside_the_set_are_listed_as_skipped_and_nothing_is_created(self):
        before = snapshot(self.tmp)
        manifest = self.svc.decode_upload(fixtures.hostile_files()["traversal.brushset"], "t.brushset")
        data = manifest if manifest["kind"] == "brushset" else None
        skipped = (data or manifest)["skipped"] if data else None
        if skipped is None:
            self.assertIn("warnings", manifest)
        else:
            reasons = " ".join(s["entry"] for s in skipped)
            self.assertIn("outside.txt", reasons)
        self.assertEqual(snapshot(self.tmp), before)
        self.assertFalse((self.tmp / "outside.txt").exists())

    def test_a_ratio_bomb_is_refused_as_corrupt(self):
        error = self.assertApi("corrupt_file", self.svc.decode_upload, fixtures.ratio_bomb(20), status=422)
        self.assertTrue(error.message)

    def test_a_set_inside_a_zip_is_found(self):
        wrapped = fixtures.make_zip([("pack/Demo_Set.brushset", self.set_bytes)])
        manifest = self.svc.decode_upload(wrapped, "pack.zip")
        self.assertEqual(manifest["brush_count"], 4)


# ── export ───────────────────────────────────────────────────────────────────

class ExportUnedited(WorldCase):
    def test_every_brush_re_exports_with_its_archive_and_every_member_byte_identical(self):
        for name, brush in self.world.brushes.items():
            export, members = self.exported(one({"library_id": self.ident(name)}))
            self.assertEqual(members[container.ARCHIVE], brush.archive, name)
            self.assertEqual(members, dict(brush.members), name)
            self.assertEqual({m["state"] for m in export.report["members"]}, {"verbatim"}, name)
            self.assertEqual(sorted(m["path"] for m in export.report["members"]), sorted(brush.paths()), name)
            self.assertEqual(export.report["brushes"][0]["applied"], {})
            has_reset = any(path.startswith("Reset/") for path in brush.paths())
            self.assertEqual(export.report["warnings"], ["Reset/ is kept verbatim"] if has_reset else [], name)
            self.assertFalse(export.dry_run)

    def test_the_exported_file_reads_back_as_the_same_brush(self):
        for name, brush in self.world.brushes.items():
            export = self.svc.build_export(one({"library_id": self.ident(name)}))
            folder = container.read_brush(export.data)
            self.assertEqual(self.svc._id_of(folder), self.ident(name), name)
            self.assertEqual(folder.archive, brush.archive)

    def test_the_report_is_the_dry_run_shape_of_the_contract(self):
        export = self.svc.build_export(one({"library_id": self.ident("inker")}))
        report = export.report
        self.assertEqual(list(report), ["filename", "size", "sha256", "members", "brushes", "warnings"])
        self.assertEqual((report["filename"], report["size"], report["sha256"]),
                         ("demo-inker.brush", len(export.data), hashlib.sha256(export.data).hexdigest()))
        self.assertEqual(set(report["brushes"][0]), {"name", "uuid", "era", "applied", "rejected", "warnings"})
        self.assertEqual(set(report["members"][0]), {"path", "size", "state"})
        self.assertEqual(export.filename, "demo-inker.brush")

    def test_a_base_of_members_is_the_same_as_the_library_id(self):
        brush = self.world.brushes["earth"]
        members = [{"path": path, "b64": service.b64(data)} for path, data in brush.members]
        _, from_members = self.exported(one({"members": members}))
        _, from_library = self.exported(one({"library_id": self.ident("earth")}))
        self.assertEqual(from_members, from_library)
        self.assertEqual(from_members, dict(brush.members))

    def test_dry_run_builds_the_same_report_and_marks_it(self):
        request = one({"library_id": self.ident("inker")})
        wet = self.svc.build_export(request)
        dry = self.svc.build_export(dict(request, dry_run=True))
        self.assertTrue(dry.dry_run)
        self.assertEqual((dry.report["size"], dry.report["sha256"]), (wet.report["size"], wet.report["sha256"]))

    def test_reset_is_kept_verbatim_and_the_report_says_so(self):
        export, members = self.exported(one({"library_id": self.ident("dual")}))
        self.assertIn("Reset/ is kept verbatim", export.report["warnings"])
        for path, data in self.world.brushes["dual"].members:
            if path.startswith("Reset/"):
                self.assertEqual(members[path], data)

    def test_a_set_keeps_its_folder_names_for_unchanged_brushes(self):
        request = {"format": "brushset", "name": "Mine \u00e9",
                   "brushes": [{"base": {"library_id": self.ident("inker")}},
                               {"base": {"library_id": self.ident("pencil")}, "changes": {"plotSpacing": 0.3}}]}
        export = self.svc.build_export(request)
        found = container.read_brushset(export.data)
        self.assertEqual(found.name, "Mine \u00e9")
        uuids = [u for u, _ in found.brushes]
        self.assertEqual(uuids[0], self.world.brushes["inker"].uuid)
        self.assertNotEqual(uuids[1], self.world.brushes["pencil"].uuid)
        self.assertRegex(uuids[1], UUID.pattern)
        self.assertEqual(found.brushes[0][1].archive, self.world.brushes["inker"].archive)
        self.assertEqual(export.filename, "mine-e.brushset")
        states = {m["path"]: m["state"] for m in export.report["members"]}
        self.assertEqual(states[f"{uuids[0]}/Brush.archive"], "verbatim")
        self.assertEqual(states[f"{uuids[1]}/Brush.archive"], "re-encoded")
        self.assertEqual(states["brushset.plist"], "re-encoded")
        self.assertEqual([b["uuid"] for b in export.report["brushes"]], uuids)


class ExportEdited(WorldCase):
    def test_a_changed_key_round_trips_through_the_decoder(self):
        for name in ("inker", "pencil", "conte", "marker", "dual", "plain"):
            base = brush_model.decode(self.world.brushes[name].archive)
            export, members = self.exported(one({"library_id": self.ident(name)},
                                                changes={"plotSpacing": 0.25, "name": "Changed \u00e9"}))
            decoded = brush_model.decode(members[container.ARCHIVE])
            self.assertEqual(decoded.params["plotSpacing"], 0.25, name)
            self.assertEqual(decoded.name, "Changed \u00e9", name)
            self.assertEqual(decoded.era, base.era, name)
            self.assertEqual(decoded.key_count, base.key_count, name)
            for key, value in base.params.items():
                if key not in ("plotSpacing", "name"):
                    self.assertEqual(decoded.params[key], value, (name, key))
            self.assertEqual([i for i in brush_model.validate(decoded) if i.level == "error"], [], name)
            self.assertNotEqual(members[container.ARCHIVE], self.world.brushes[name].archive)
            states = {m["path"]: m["state"] for m in export.report["members"]}
            self.assertEqual(states[container.ARCHIVE], "re-encoded", name)
            for path, data in self.world.brushes[name].members:
                if path != container.ARCHIVE:
                    self.assertEqual(members[path], data, (name, path))
            self.assertEqual(export.filename, "changed-e.brush")
            self.assertEqual(export.report["brushes"][0]["applied"]["plotSpacing"], 0.25)

    def test_the_old_thumbnail_stays_and_is_flagged_stale(self):
        export = self.svc.build_export(one({"library_id": self.ident("inker")}, changes={"plotSpacing": 0.25}))
        self.assertTrue(any("stale_thumbnail" in w for w in export.report["warnings"]))
        self.assertIn({"key": "QuickLook/Thumbnail.png", "code": "stale_thumbnail"},
                      export.report["brushes"][0]["warnings"])
        unchanged = self.svc.build_export(one({"library_id": self.ident("plain")}, changes={"plotSpacing": 0.25}))
        self.assertFalse(any("stale_thumbnail" in w for w in unchanged.report["warnings"]), "it has no thumbnail")

    def test_a_change_equal_to_the_base_changes_nothing(self):
        export, members = self.exported(one({"library_id": self.ident("inker")},
                                            changes={"name": "Demo Inker", "stamp": False}))
        self.assertEqual(members[container.ARCHIVE], self.world.brushes["inker"].archive)
        self.assertEqual(export.report["brushes"][0]["applied"], {})

    def test_rejected_changes_are_422_with_the_list_and_nothing_is_built(self):
        request = one({"library_id": self.ident("inker")}, changes={"noSuchKey": 1, "plotSpacing": 0.2})
        error = self.assertApi("invalid_settings", self.svc.build_export, request, status=422)
        self.assertEqual([(r["key"], r["code"]) for r in error.data["rejected"]], [("noSuchKey", "unknown_key")])
        request["brushes"][0]["mode"] = "clamp"
        self.assertApi("invalid_settings", self.svc.build_export, request, status=422)

    def test_a_value_outside_what_the_library_holds_is_applied_with_a_warning(self):
        export = self.svc.build_export(one({"library_id": self.ident("inker")}, changes={"plotSpacing": 50}))
        self.assertIn({"key": "plotSpacing", "code": "outside_observed"}, export.report["brushes"][0]["warnings"])

    def test_a_replaced_shape_is_written_as_8_bit_grey_and_the_bundled_name_is_cleared(self):
        grey = fixtures.make_png(8, 8, "L", lambda x, y: (x * 30) % 256)
        rgba = fixtures.make_png(8, 8, "RGBA", lambda x, y: (x * 30 % 256, 0, 0, 255))
        export, members = self.exported(one({"library_id": self.ident("pencil")},
                                            textures={"shape": {"png_b64": service.b64(grey)}}))
        self.assertEqual(members[container.SHAPE], grey, "an 8-bit grey PNG is written as it is")
        self.assertIsNone(brush_model.decode(members[container.ARCHIVE]).params["bundledShapePath"])
        states = {m["path"]: m["state"] for m in export.report["members"]}
        self.assertEqual(states[container.SHAPE], "replaced")
        export, members = self.exported(one({"library_id": self.ident("inker")},
                                            textures={"shape": {"png_b64": service.b64(rgba)}}))
        info = png_io.png_info(members[container.SHAPE])
        self.assertEqual((info["color_type"], info["bit_depth"], info["interlace"]), (0, 8, 0))
        self.assertTrue(any(w.startswith("converted") for w in export.report["warnings"]))

    def test_the_base_images_own_bytes_are_kept_never_converted(self):
        own = self.world.brushes["inker"].shape
        export, members = self.exported(one({"library_id": self.ident("inker")},
                                            textures={"shape": {"png_b64": service.b64(own)},
                                                      "grain": {"keep": True}}))
        self.assertEqual(members, dict(self.world.brushes["inker"].members))

    def test_a_bundled_texture_drops_the_member_and_names_the_file(self):
        export, members = self.exported(one({"library_id": self.ident("inker")},
                                            textures={"grain": {"bundled": "Brush-Preset-Stained-Paper-1.jpg"}}))
        self.assertNotIn(container.GRAIN, members)
        self.assertEqual(brush_model.decode(members[container.ARCHIVE]).params["bundledGrainPath"],
                         "Brush-Preset-Stained-Paper-1.jpg")
        states = {m["path"]: m["state"] for m in export.report["members"]}
        self.assertEqual(states[container.GRAIN], "dropped")

    def test_bad_texture_requests(self):
        base = {"library_id": self.ident("inker")}
        for textures in ({"shape": {"keep": True, "bundled": "x.png"}}, {"shape": {"keep": False}},
                         {"shape": {"bundled": "a/b.png"}}, {"shape": {"bundled": ""}}, {"shape": {"bundled": 5}},
                         {"shape": {"png_b64": "!!"}}, {"shape": {"png_b64": service.b64(b"not a png")}},
                         {"shape": {"other": 1}}, {"metal": {"keep": True}}, {"shape": "keep"}, "x"):
            self.assertIn(self.assertApi_any(self.svc.build_export, one(base, textures=textures)),
                          {"bad_argument", "corrupt_file"}, textures)

    def assertApi_any(self, call, *args):
        with self.assertRaises(service.ApiError) as caught:
            call(*args)
        return caught.exception.code

    def test_the_thumbnail_can_be_omitted_or_replaced(self):
        base = {"library_id": self.ident("inker")}
        export, members = self.exported(one(base, thumbnail={"omit": True}))
        self.assertNotIn(container.THUMBNAIL, members)
        self.assertEqual({m["path"]: m["state"] for m in export.report["members"]}[container.THUMBNAIL], "dropped")
        width, height = png_io.THUMBNAIL_SIZE
        ink = fixtures.make_png(width, height, "RGBA", lambda x, y: (255, 255, 255, 255 if 100 < x < 900 and y == 160 else 0))
        export, members = self.exported(one(base, thumbnail={"png_b64": service.b64(ink)}))
        written = png_io.read_png(members[container.THUMBNAIL])
        self.assertEqual((written.width, written.height, written.mode), (width, height, "RGBA"))
        self.assertEqual(png_io.alpha_plane(written).pixels, png_io.alpha_plane(png_io.read_png(ink)).pixels)
        self.assertIn("sRGB", png_io.png_info(members[container.THUMBNAIL])["chunks"])
        small = fixtures.make_png(10, 10, "RGBA")
        self.assertApi("bad_argument", self.svc.build_export, one(base, thumbnail={"png_b64": service.b64(small)}))
        for bad in ({"omit": False}, {"keep": False}, {"omit": True, "keep": True}, "omit", {"nope": 1}):
            self.assertApi("bad_argument", self.svc.build_export, one(base, thumbnail=bad))

    def test_a_dual_brushs_second_archive_is_changed_by_sub(self):
        export, members = self.exported(one({"library_id": self.ident("dual")},
                                            sub={"changes": {"name": "Second"}}))
        self.assertEqual(brush_model.decode(members["Sub01/Brush.archive"]).name, "Second")
        self.assertEqual(members[container.ARCHIVE], self.world.brushes["dual"].archive)
        states = {m["path"]: m["state"] for m in export.report["members"]}
        self.assertEqual(states["Sub01/Brush.archive"], "re-encoded")
        self.assertEqual(states[container.ARCHIVE], "verbatim")
        self.assertEqual(members["Reset/Brush.archive"], dict(self.world.brushes["dual"].members)["Reset/Brush.archive"])
        self.assertApi("bad_argument", self.svc.build_export, one({"library_id": self.ident("inker")},
                                                                  sub={"changes": {"name": "x"}}))
        error = self.assertApi("invalid_settings", self.svc.build_export,
                               one({"library_id": self.ident("dual")}, sub={"changes": {"nope": 1}}))
        self.assertEqual(error.data["rejected"][0]["key"], "sub.nope")

    def test_a_new_brush_needs_the_donor_from_the_library(self):
        error = self.assertApi("library_missing", self.svc.build_export,
                               {"format": "brush", "brushes": [{"base": None}]}, status=409)
        self.assertIn("donor", error.message)

    def test_an_emoji_name_gives_an_ascii_file_name(self):
        export = self.svc.build_export(one({"library_id": self.ident("inker")},
                                           changes={"name": "Cont\u00e9 \U0001f4a7 6B \u6d53\u58a8"}))
        self.assertEqual(export.filename, "conte-6b.brush")
        self.assertTrue(export.filename.isascii())
        self.assertEqual(brush_model.decode(container.read_brush(export.data).archive).name,
                         "Cont\u00e9 \U0001f4a7 6B \u6d53\u58a8")
        named = self.svc.build_export({"format": "brushset", "name": "\U0001f4a7\U0001f4a7",
                                       "brushes": [{"base": {"library_id": self.ident("inker")}}]})
        self.assertEqual(named.filename, "untitled.brushset")
        self.assertEqual(container.read_brushset(named.data).name, "\U0001f4a7\U0001f4a7")


class ExportFormats(WorldCase):
    def test_gbr_of_an_embedded_shape(self):
        export = self.svc.build_export({"format": "gbr", "spacing": 25,
                                        "brushes": [{"base": {"library_id": self.ident("inker")}}]})
        read = gbr.read_gbr(export.data)
        self.assertEqual((read.width, read.height, read.spacing, read.name), (8, 8, 25, "Demo Inker"))
        self.assertEqual(export.filename, "demo-inker.gbr")
        self.assertEqual(export.report["members"], [{"path": "demo-inker.gbr", "size": len(export.data),
                                                     "state": "replaced"}])

    def test_gbr_of_a_bundled_shape_has_no_image_unless_one_is_supplied(self):
        request = {"format": "gbr", "brushes": [{"base": {"library_id": self.ident("pencil")}}]}
        self.assertApi("bad_argument", self.svc.build_export, request)
        png = fixtures.make_png(8, 8, "L", lambda x, y: 255 if x == y else 0)
        request["brushes"][0]["textures"] = {"shape": {"png_b64": service.b64(png)}}
        self.assertEqual(gbr.read_gbr(self.svc.build_export(request).data).width, 8)
        for spacing in (0, 1001, "x", True, 1.5):
            self.assertApi("bad_argument", self.svc.build_export, dict(request, spacing=spacing))

    def test_a_kit_is_a_zip_of_the_files_given(self):
        mask = fixtures.make_png()
        files = [{"path": "ink/ink-1.png", "b64": service.b64(mask)},
                 {"path": "stroke-preview.png", "b64": service.b64(mask)},
                 {"path": "brush-recipe.md", "b64": service.b64(b"# Recipe\n")},
                 {"path": "gimp/shape.gbr", "b64": service.b64(gbr.write_gbr(2, 2, bytes(4)))}]
        export = self.svc.build_export({"format": "kit", "name": "Kit \u00e9", "files": files})
        self.assertEqual(export.filename, "kit-e-kit.zip")
        self.assertEqual(sorted(dict(fixtures.zip_entries(export.data))),
                         ["brush-recipe.md", "gimp/shape.gbr", "ink/ink-1.png", "stroke-preview.png"])
        with_brush = self.svc.build_export({"format": "kit", "files": files,
                                            "brushes": [{"base": {"library_id": self.ident("inker")}}]})
        self.assertIn("demo-inker.brush", dict(fixtures.zip_entries(with_brush.data)))

    def test_a_kit_takes_only_the_known_entry_names(self):
        png = service.b64(fixtures.make_png())
        for path in ("../evil.png", "/abs.png", "C:\\x.png", "ink/../../x.png", "ink/a/b.png", "readme.md",
                     "gimp/shape.png", "ink/x.exe", "mask/.png", "x" * 200, "ink\\x.png", "stroke-preview.PNG"):
            self.assertApi("bad_argument", self.svc.build_export,
                           {"format": "kit", "files": [{"path": path, "b64": png}]})
        for files in (None, [], "x", [{"path": "brush-recipe.md"}], [{"path": "brush-recipe.md", "b64": "QQ==",
                                                                       "x": 1}]):
            self.assertApi("bad_argument", self.svc.build_export, {"format": "kit", "files": files})
        self.assertApi("bad_argument", self.svc.build_export,
                       {"format": "kit", "files": [{"path": "ink/a.png", "b64": service.b64(b"not png")}]})
        self.assertApi("bad_argument", self.svc.build_export,
                       {"format": "kit", "files": [{"path": "gimp/a.gbr", "b64": service.b64(b"not gbr")}]})
        self.assertApi("bad_argument", self.svc.build_export,
                       {"format": "kit", "files": [{"path": f"ink/{i}.png", "b64": png} for i in range(65)]})

    def test_a_request_is_checked_before_anything_is_built(self):
        base = {"library_id": self.ident("inker")}
        bad = [
            None, [], "x", {}, {"format": "zip"}, {"format": "brush"}, {"format": "brush", "brushes": []},
            {"format": "brush", "brushes": [{"base": base}, {"base": base}]},
            {"format": "brushset", "brushes": [{"base": base}]},
            {"format": "brushset", "name": "x", "brushes": []},
            {"format": "brushset", "name": "", "brushes": [{"base": base}]},
            {"format": "brushset", "name": "x" * 121, "brushes": [{"base": base}]},
            {"format": "brush", "brushes": [{"base": base}], "extra": 1},
            {"format": "brush", "brushes": [{"base": base, "extra": 1}]},
            {"format": "brush", "brushes": ["x"]},
            {"format": "brush", "dry_run": "yes", "brushes": [{"base": base}]},
            {"format": "brush", "brushes": [{"base": {"library_id": "nope"}}]},
            {"format": "brush", "brushes": [{"base": {"library_id": base["library_id"], "members": []}}]},
            {"format": "brush", "brushes": [{"base": {"path": "x"}}]},
            {"format": "brush", "brushes": [{"base": "b_0123456789ab"}]},
            {"format": "brush", "brushes": [{"base": {"members": []}}]},
            {"format": "brush", "brushes": [{"base": {"members": [{"path": "Shape.png", "b64": ""}]}}]},
            {"format": "brush", "brushes": [{"base": base, "mode": "lenient"}]},
            {"format": "brush", "brushes": [{"base": base, "changes": []}]},
            {"format": "brush", "brushes": [{"base": base, "uuid": "not-a-uuid"}]},
            {"format": "brushset", "name": "x", "brushes": [{"base": base}] * 201},
        ]
        for request in bad:
            self.assertApi("bad_argument", self.svc.build_export, request)
        same = fixtures.brush_uuid(1)
        self.assertApi("bad_argument", self.svc.build_export, {
            "format": "brushset", "name": "x",
            "brushes": [{"base": base, "uuid": same}, {"base": {"library_id": self.ident("pencil")}, "uuid": same}]})

    def test_a_given_folder_name_is_used_upper_cased(self):
        wanted = str(fixtures.brush_uuid(5)).lower()
        export = self.svc.build_export({"format": "brushset", "name": "x", "brushes": [
            {"base": {"library_id": self.ident("inker")}, "uuid": wanted}]})
        self.assertEqual(container.read_brushset(export.data).brushes[0][0], wanted.upper())


# ── hostile and odd input ────────────────────────────────────────────────────

class Hardening(WorldCase):
    """Whatever JSON can spell ends in a result or an ApiError, never in
    another exception."""

    def test_odd_values_never_escape_as_anything_but_an_api_error(self):
        i, d = self.ident("inker"), self.ident("dual")
        base = {"library_id": i}
        deep = cur = {}
        for _ in range(500):
            cur["a"] = {}
            cur = cur["a"]
        calls = [
            lambda: self.svc.build_export({"format": "brush", "brushes": [{"base": base, "changes": {"name": "\ud800x"}}]}),
            lambda: self.svc.build_export({"format": "brushset", "name": "\ud800", "brushes": [{"base": base}]}),
            lambda: self.svc.search("\ud800 ink"),
            lambda: self.svc.build_export({"format": "brush", "brushes": [{"base": None, "era": ["x"]}]}),
            lambda: self.svc.validate_patch({"stamp": True}, era=5),
            lambda: self.svc.validate_patch({"name": deep}, base_id=i),
            lambda: self.svc.validate_patch({"dynamicsPressureSizeCurve": {"points": [[0, 0]] * 1000}}, base_id=i),
            lambda: self.svc.validate_patch({"dynamicsPressureSizeCurve": 5, "colorDynamics": [1, 2]}, base_id=i),
            lambda: self.svc.build_export({"format": "brush", "brushes": [{
                "base": {"members": [{"path": "Brush.archive", "b64": service.b64(b"junk")}]}}]}),
            lambda: self.svc.build_export({"format": "brush", "brushes": [{"base": base, "textures": {
                "shape": {"png_b64": service.b64(png_io.SIGNATURE + bytes(20))}}}]}),
            lambda: self.svc.build_export({"format": "brush", "brushes": [{"base": {"library_id": d}, "sub": 5}]}),
            lambda: self.svc.build_export({"format": "brush", "brushes": [{"base": base, "textures": []}]}),
            lambda: self.svc.decode_upload(b"PK\x03\x04" + bytes(100)),
            lambda: self.svc.decode_upload(b"x", member=["a"]),
            lambda: self.svc.get_brush(i, {"a": 1}),
            lambda: self.svc.vocabulary(5),
            lambda: self.svc.settings_schema(keys={"a": 1}),
            lambda: self.svc.search(tags={"a": 1}),
            lambda: self.svc.list_sets(["user"]),
            lambda: self.svc.get_set(5),
            lambda: self.svc.preview(i, ["stroke"]),
            lambda: self.svc.similar_settings({"a": "\ud800"}),
            lambda: self.svc.similar_settings({"a": deep}),
        ]
        for number, call in enumerate(calls):
            try:
                call()
            except service.ApiError as exc:
                self.assertIsInstance(exc.code, str, number)
                self.assertIsInstance(exc.status, int, number)
                self.assertNotIn("Traceback", exc.message)
            except Exception as exc:
                self.fail(f"call {number} raised {type(exc).__name__}: {exc}")

    def test_a_lone_surrogate_is_refused_where_it_would_reach_a_file(self):
        for call in (lambda: self.svc.build_export({"format": "brush", "brushes": [{
                         "base": {"library_id": self.ident("inker")}, "changes": {"name": "\ud800"}}]}),
                     lambda: self.svc.build_export({"format": "brushset", "name": "\udfff", "brushes": [{
                         "base": {"library_id": self.ident("inker")}}]})):
            error = self.assertApi_(call)
            self.assertEqual(error.code, "bad_argument")
            self.assertIn("surrogate", error.message)

    def assertApi_(self, call):
        with self.assertRaises(service.ApiError) as caught:
            call()
        return caught.exception

    def test_nesting_is_capped(self):
        deep = cur = {}
        for _ in range(40):
            cur["a"] = {}
            cur = cur["a"]
        self.assertApi("bad_argument", self.svc.validate_patch, {"name": deep}, base_id=self.ident("inker"))


# ── the export folder ────────────────────────────────────────────────────────

class ExportBrush(WorldCase):
    def setUp(self):
        super().setUp()
        self.out = Path(tempfile.mkdtemp(prefix="brushes-out-")).resolve()
        self.addCleanup(shutil.rmtree, self.out, ignore_errors=True)
        self.svc = self.world.service(export_dir=self.out / "exports")

    def test_disabled_without_a_folder(self):
        svc = self.world.service()
        self.assertApi("export_disabled", svc.export_brush, self.ident("inker"), status=403)
        self.assertApi("export_disabled", svc.write_export, "a.brush", b"x", status=403)

    def test_a_dry_run_writes_nothing_and_says_what_it_would(self):
        result = self.svc.export_brush(self.ident("inker"), {"plotSpacing": 0.25}, "Fresh Name")
        self.assertIs(result["dry_run"], True)
        self.assertEqual(result["would_write"], f"fresh-name-{self.ident('inker')[2:10]}.brush")
        self.assertEqual(result["validation"][0]["applied"]["plotSpacing"], 0.25)
        self.assertIn("members", result)
        self.assertFalse((self.out / "exports").exists())

    def test_confirm_writes_one_file_and_never_over_another(self):
        result = self.svc.export_brush(self.ident("inker"), {"plotSpacing": 0.25}, "Fresh \U0001f4a7", True)
        self.assertIs(result["dry_run"], False)
        name = result["written"]
        self.assertTrue(name.endswith(f"-{self.ident('inker')[2:10]}.brush"), name)
        self.assertTrue(name.isascii())
        written = (self.out / "exports" / name).read_bytes()
        self.assertEqual(hashlib.sha256(written).hexdigest(), result["sha256"])
        self.assertEqual(brush_model.decode(container.read_brush(written).archive).params["plotSpacing"], 0.25)
        self.assertEqual(sorted(p.name for p in (self.out / "exports").iterdir()), [name])
        self.assertApi("exists", self.svc.export_brush, self.ident("inker"), {"plotSpacing": 0.25},
                       "Fresh \U0001f4a7", True, status=409)
        self.assertEqual(sorted(p.name for p in (self.out / "exports").iterdir()), [name])

    def test_the_arguments_are_checked(self):
        self.assertApi("bad_argument", self.svc.export_brush, "nope")
        self.assertApi("bad_argument", self.svc.export_brush, self.ident("inker"), [], None)
        self.assertApi("bad_argument", self.svc.export_brush, self.ident("inker"), None, "", True)
        self.assertApi("bad_argument", self.svc.export_brush, self.ident("inker"), None, None, "yes")
        self.assertApi("unknown_id", self.svc.export_brush, "b_000000000000")
        self.assertApi("invalid_settings", self.svc.export_brush, self.ident("inker"), {"nope": 1}, None, True)
        self.assertFalse((self.out / "exports").exists(), "a refusal writes nothing, not even the folder")


# ── nothing is written ───────────────────────────────────────────────────────

class ReadOnly(WorldCase):
    def test_a_battery_of_calls_changes_nothing_under_the_data_root(self):
        before = snapshot(self.tmp)
        svc = self.world.service()
        i = self.ident
        svc.status(); svc.search("ink"); svc.search(); svc.facets(); svc.vocabulary(); svc.list_sets()
        svc.get_set("demo-set"); svc.get_brush(i("inker"), list(service.INCLUDE_PARTS))
        svc.similar(i("inker")); svc.preview_set(i("inker"), ["stroke", "shape", "grain"])
        svc.settings_schema(detail="full"); svc.validate_patch({"stamp": True}, base_id=i("inker"))
        svc.open_library_brush(i("dual")); svc.build_export(one({"library_id": i("dual")}, changes={"stamp": True}))
        svc.decode_upload((self.world.paths.library / "user" / "demo-pack" / "Demo_Set.brushset").read_bytes())
        self.assertEqual(snapshot(self.tmp), before)

    def test_the_source_writes_files_only_in_write_export(self):
        """F12: service.write_export is the one writer. No other function opens
        a file for writing, makes a folder, renames, removes or links."""
        tree = ast.parse((PIPELINE / "service.py").read_text(encoding="utf-8"))
        offenders = []
        for function in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if function.name == "write_export":
                continue
            for node in ast.walk(function):
                if not isinstance(node, ast.Call):
                    continue
                name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
                receiver = getattr(getattr(node.func, "value", None), "id", "")
                if name in {"write_text", "write_bytes", "write_json", "mkdir", "unlink", "rmdir", "rename",
                            "link", "symlink", "touch", "truncate", "copyfile", "move", "rmtree"}:
                    offenders.append((function.name, name))
                if receiver in {"os", "shutil"} and name in {"remove", "replace", "copy", "makedirs"}:
                    offenders.append((function.name, f"{receiver}.{name}"))
                if name == "open" and any(isinstance(a, ast.Constant) and isinstance(a.value, str)
                                          and set(a.value) & set("wxa+") for a in node.args[1:2]):
                    offenders.append((function.name, "open for writing"))
        self.assertEqual(offenders, [])

    def test_the_search_engine_is_loaded_without_writing_bytecode(self):
        tools = BRUSHES / "vault" / "tools"
        before = sorted(p.name for p in tools.rglob("*"))
        service.engine()
        self.assertEqual(sorted(p.name for p in tools.rglob("*")), before)


class TheModule(unittest.TestCase):
    def test_it_is_a_library_module_with_no_main(self):
        tree = ast.parse((PIPELINE / "service.py").read_text(encoding="utf-8"))
        self.assertNotIn("main", {n.name for n in tree.body if isinstance(n, ast.FunctionDef)})

    def test_it_imports_the_standard_library_and_its_siblings_only(self):
        tree = ast.parse((PIPELINE / "service.py").read_text(encoding="utf-8"))
        siblings = {path.stem for path in PIPELINE.glob("*.py")}
        stdlib = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else None
        for node in ast.walk(tree):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.level == 0 else [])
            for name in names:
                top = name.split(".")[0]
                self.assertTrue(top in siblings or top == "__future__" or stdlib is None or top in stdlib, name)
                self.assertNotEqual(top, "yaml")

    def test_every_text_open_names_utf8_and_the_file_is_lf(self):
        raw = (PIPELINE / "service.py").read_bytes()
        self.assertNotIn(b"\r", raw)
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        tree = ast.parse(raw.decode("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "open":
                mode = node.args[1].value if len(node.args) > 1 and isinstance(node.args[1], ast.Constant) else "r"
                if "b" not in mode:
                    self.assertIn("encoding", {k.arg for k in node.keywords})
        self.assertIsNone(MACHINE_PATH.search(raw.decode("utf-8")))

    def test_the_spec_lists_it_as_a_library_module_and_the_document_names_its_methods(self):
        documented = ("status", "search", "get_brush", "similar", "list_sets", "vocabulary", "preview",
                      "settings_schema", "validate_patch", "decode_upload", "open_library_brush",
                      "build_export", "write_export")
        text = (BRUSHES / "docs" / "CONTRACTS.md").read_text(encoding="utf-8")
        listed = " ".join(text.split("(`BrushService`:", 1)[1].split(")", 1)[0].split())
        self.assertEqual(re.findall(r"`?([a-z_]+)`?", listed), list(documented))
        for name in documented:
            self.assertTrue(callable(getattr(service.BrushService, name)), name)
        if yaml is not None:
            spec = yaml.safe_load((BRUSHES / "spec.yaml").read_text(encoding="utf-8"))
            self.assertIn("pipeline/service.py", spec["cli"]["library_modules"])


if __name__ == "__main__":
    unittest.main()
