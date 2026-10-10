"""pipeline/brush_common.py: roots, exit codes, the console and file writes
(docs/CONTRACTS.md, F2).

Every test points the roots at a temporary folder or at names that do not
exist. resolve_paths only works out names, so nothing here reads or creates
the real library, catalog or vault, and one test proves that.

    python -m unittest discover -s brushes/pipeline/tests
"""

import argparse
import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))

import brush_common as bc  # noqa: E402
import fixtures  # noqa: E402

BRUSHES = PIPELINE.parent


class Constants(unittest.TestCase):
    def test_exit_codes(self):
        self.assertEqual((bc.EXIT_OK, bc.EXIT_REFUSED, bc.EXIT_USAGE), (0, 1, 2))

    def test_environment_names(self):
        self.assertEqual(bc.ENV_ROOT, "ROSW_BRUSHES_ROOT")
        self.assertEqual(bc.ENV_LIBRARY, "ROSW_BRUSHES_LIBRARY")
        self.assertEqual(bc.ENV_CATALOG, "ROSW_BRUSHES_CATALOG")
        self.assertEqual(bc.ENV_VAULT, "ROSW_BRUSHES_VAULT")
        self.assertEqual(bc.ENV_INDEX, "ROSW_BRUSHES_INDEX")
        self.assertEqual(bc.ENV_NAMES, {"root": bc.ENV_ROOT, "library": bc.ENV_LIBRARY,
                                        "catalog": bc.ENV_CATALOG, "vault": bc.ENV_VAULT,
                                        "index": bc.ENV_INDEX})

    def test_flags(self):
        self.assertEqual(bc.FLAGS, {"root": "--root", "library": "--library",
                                    "catalog": "--catalog", "vault": "--vault"})

    def test_the_paths_tuple(self):
        self.assertEqual(bc.Paths._fields, ("root", "schema", "catalog", "vault", "previews", "tags",
                                            "vocabulary", "index", "library", "app"))

    def test_the_port(self):
        self.assertEqual(bc.APP_PORT, 8719)

    def test_the_tool_root_is_the_brushes_folder(self):
        self.assertEqual(bc.TOOL_ROOT, BRUSHES.resolve())
        self.assertEqual(bc.TOOL_ROOT.name, "brushes")


class Roots(fixtures.BrushCase):
    """flag beats environment beats default."""

    def env(self, **values):
        patcher = mock.patch.dict(os.environ, {bc.ENV_NAMES[k]: str(v) for k, v in values.items()})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_the_defaults_hang_off_the_folder_that_holds_the_code(self):
        paths = bc.resolve_paths()
        root = BRUSHES.resolve()
        self.assertEqual(paths.root, root)
        self.assertEqual(paths.schema, root / "schema")
        self.assertEqual(paths.catalog, root / "catalog")
        self.assertEqual(paths.vault, root / "vault")
        self.assertEqual(paths.previews, root / "vault" / "_Previews")
        self.assertEqual(paths.tags, root / "vault" / "_BrushTags")
        self.assertEqual(paths.vocabulary, root / "vault" / "_BrushTags" / "vocabulary.yaml")
        self.assertEqual(paths.index, root / "vault" / "tools" / "rag_index" / "index.json")
        self.assertEqual(paths.library, root / "library")
        self.assertEqual(paths.app, root / "app")

    def test_every_path_is_absolute(self):
        for path in bc.resolve_paths():
            self.assertTrue(path.is_absolute(), path)
        for path in bc.resolve_paths(root="relative/root", vault="v"):
            self.assertTrue(path.is_absolute(), path)

    def test_the_root_variable_moves_the_data(self):
        self.env(root=self.tmp)
        paths = bc.resolve_paths()
        self.assertEqual(paths.root, self.tmp)
        for name in ("catalog", "vault", "library"):
            self.assertEqual(getattr(paths, name), self.tmp / name)
        self.assertEqual(paths.index, self.tmp / "vault" / "tools" / "rag_index" / "index.json")

    def test_the_schema_and_the_app_are_code_and_never_move(self):
        """A test root, a --root flag and ROSW_BRUSHES_ROOT move the data only:
        validation and the app server read the one schema/ and app/ beside
        pipeline/, wherever the data is."""
        code = BRUSHES.resolve()
        for paths in (bc.resolve_paths(), bc.resolve_paths(root=self.tmp / "flag-root"),
                      bc.resolve_paths(root=self.tmp, library=self.tmp / "l", catalog=self.tmp / "c",
                                       vault=self.tmp / "v")):
            self.assertEqual(paths.schema, code / "schema")
            self.assertEqual(paths.app, code / "app")
        self.env(root=self.tmp / "env-root", library=self.tmp / "lib", catalog=self.tmp / "cat",
                 vault=self.tmp / "vlt", index=self.tmp / "ix.json")
        paths = bc.resolve_paths()
        self.assertEqual((paths.schema, paths.app), (bc.TOOL_ROOT / "schema", bc.TOOL_ROOT / "app"))
        self.assertTrue((paths.app / "index.html").is_file(), "the app that is served is the code's")

    def test_each_variable_moves_its_own_folder_only(self):
        self.env(root=self.tmp / "r", library=self.tmp / "lib", catalog=self.tmp / "cat",
                 vault=self.tmp / "vlt", index=self.tmp / "ix" / "index.json")
        paths = bc.resolve_paths()
        self.assertEqual(paths.root, self.tmp / "r")
        self.assertEqual(paths.library, self.tmp / "lib")
        self.assertEqual(paths.catalog, self.tmp / "cat")
        self.assertEqual(paths.vault, self.tmp / "vlt")
        self.assertEqual(paths.previews, self.tmp / "vlt" / "_Previews")
        self.assertEqual(paths.tags, self.tmp / "vlt" / "_BrushTags")
        self.assertEqual(paths.vocabulary, self.tmp / "vlt" / "_BrushTags" / "vocabulary.yaml")
        self.assertEqual(paths.index, self.tmp / "ix" / "index.json")

    def test_a_flag_beats_the_variable(self):
        self.env(root=self.tmp / "env-root", library=self.tmp / "env-lib",
                 catalog=self.tmp / "env-cat", vault=self.tmp / "env-vault")
        paths = bc.resolve_paths(root=self.tmp / "flag-root", library=self.tmp / "flag-lib",
                                 catalog=self.tmp / "flag-cat", vault=self.tmp / "flag-vault")
        self.assertEqual(paths.root, self.tmp / "flag-root")
        self.assertEqual(paths.library, self.tmp / "flag-lib")
        self.assertEqual(paths.catalog, self.tmp / "flag-cat")
        self.assertEqual(paths.vault, self.tmp / "flag-vault")
        self.assertEqual(paths.previews, self.tmp / "flag-vault" / "_Previews")

    def test_a_root_flag_beats_the_root_variable_for_what_follows_from_it(self):
        self.env(root=self.tmp / "env-root")
        paths = bc.resolve_paths(root=self.tmp / "flag-root")
        self.assertEqual(paths.library, self.tmp / "flag-root" / "library")
        self.assertEqual(paths.vault, self.tmp / "flag-root" / "vault")

    def test_a_folder_variable_beats_the_root_flag(self):
        self.env(library=self.tmp / "env-lib")
        paths = bc.resolve_paths(root=self.tmp / "flag-root")
        self.assertEqual(paths.library, self.tmp / "env-lib")
        self.assertEqual(paths.catalog, self.tmp / "flag-root" / "catalog")

    def test_the_index_variable_beats_the_vault(self):
        self.env(index=self.tmp / "elsewhere.json")
        paths = bc.resolve_paths(vault=self.tmp / "flag-vault")
        self.assertEqual(paths.index, self.tmp / "elsewhere.json")
        self.assertEqual(paths.tags, self.tmp / "flag-vault" / "_BrushTags")

    def test_an_empty_value_counts_as_absent(self):
        self.env(root="", library="   ")
        paths = bc.resolve_paths(vault="")
        self.assertEqual(paths.root, BRUSHES.resolve())
        self.assertEqual(paths.library, BRUSHES.resolve() / "library")
        self.assertEqual(paths.vault, BRUSHES.resolve() / "vault")

    def test_strings_and_paths_are_both_accepted(self):
        self.assertEqual(bc.resolve_paths(root=str(self.tmp)).root, bc.resolve_paths(root=self.tmp).root)

    def test_resolving_creates_nothing_and_reads_nothing(self):
        before = fixtures.tree_digest(self.tmp)
        real = {name: (BRUSHES / name).exists() for name in ("catalog", "vault", "library", "schema")}
        paths = bc.resolve_paths(root=self.tmp / "nowhere", library=self.tmp / "no-library")
        bc.resolve_paths()
        self.assertFalse(paths.root.exists())
        self.assertFalse(paths.library.exists())
        self.assertEqual(fixtures.tree_digest(self.tmp), before)
        self.assertEqual(list(self.tmp.iterdir()), [])
        self.assertEqual({name: (BRUSHES / name).exists() for name in real}, real)


class Arguments(fixtures.BrushCase):
    def test_a_parser_gets_the_four_flags(self):
        parser = bc.add_path_arguments(argparse.ArgumentParser())
        args = parser.parse_args(["--root", str(self.tmp), "--library", str(self.tmp / "l"),
                                  "--catalog", str(self.tmp / "c"), "--vault", str(self.tmp / "v")])
        paths = bc.paths_from_args(args)
        self.assertEqual((paths.root, paths.library, paths.catalog, paths.vault),
                         (self.tmp, self.tmp / "l", self.tmp / "c", self.tmp / "v"))

    def test_no_flag_means_the_default(self):
        args = bc.add_path_arguments(argparse.ArgumentParser()).parse_args([])
        self.assertEqual(bc.paths_from_args(args), bc.resolve_paths())

    def test_a_script_may_take_only_some_of_them(self):
        parser = bc.add_path_arguments(argparse.ArgumentParser(), names=("root", "vault"))
        with self.assertRaises(SystemExit), mock.patch("sys.stderr", io.StringIO()):
            parser.parse_args(["--library", "x"])
        args = parser.parse_args(["--vault", str(self.tmp / "v")])
        self.assertEqual(bc.paths_from_args(args).vault, self.tmp / "v")
        self.assertEqual(bc.paths_from_args(args).library, BRUSHES.resolve() / "library")


class StoredPaths(fixtures.BrushCase):
    def test_a_stored_path_is_posix_and_relative(self):
        target = self.tmp / "_Previews" / "demo-set" / "b_0123456789ab.stroke.png"
        self.assertEqual(bc.stored_path(target, self.tmp), "_Previews/demo-set/b_0123456789ab.stroke.png")
        self.assertNotIn("\\", bc.stored_path(target, self.tmp))

    def test_a_path_outside_the_base_is_refused(self):
        with self.assertRaises(ValueError):
            bc.stored_path(self.tmp.parent / "elsewhere.png", self.tmp)


class Writing(fixtures.BrushCase):
    def test_text_is_utf8_with_lf_on_every_platform(self):
        target = self.tmp / "note.md"
        bc.write_text(target, "one\ntwo é \U0001f4a7\n")
        self.assertEqual(target.read_bytes(), "one\ntwo é \U0001f4a7\n".encode("utf-8"))
        self.assertNotIn(b"\r", target.read_bytes())
        self.assertFalse(target.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_text_that_already_holds_crlf_keeps_it(self):
        target = self.tmp / "tail.md"
        bc.write_text(target, "generated\n## Notes\r\nthe author's line\r\n")
        self.assertEqual(target.read_bytes(), b"generated\n## Notes\r\nthe author's line\r\n")
        self.assertEqual(bc.read_text(target), "generated\n## Notes\r\nthe author's line\r\n")

    def test_it_makes_the_folder_replaces_the_file_and_leaves_no_temporary(self):
        target = self.tmp / "a" / "b" / "file.json"
        self.assertEqual(bc.write_text(target, "first\n"), target)
        bc.write_text(target, "second\n")
        self.assertEqual(target.read_bytes(), b"second\n")
        self.assertEqual([p.name for p in target.parent.iterdir()], ["file.json"])

    def test_a_failed_write_leaves_the_old_file_whole(self):
        target = self.tmp / "kept.txt"
        bc.write_text(target, "old\n")
        with mock.patch("os.replace", side_effect=OSError("disk says no")):
            with self.assertRaises(OSError):
                bc.write_text(target, "new\n")
        self.assertEqual(target.read_bytes(), b"old\n")
        self.assertEqual([p.name for p in self.tmp.iterdir()], ["kept.txt"])

    def test_bytes_are_written_the_same_way(self):
        target = self.tmp / "p" / "tile.png"
        data = fixtures.make_png(4, 4)
        bc.write_bytes(target, data)
        self.assertEqual(target.read_bytes(), data)
        self.assertEqual([p.name for p in target.parent.iterdir()], ["tile.png"])

    def test_generated_json_has_one_spelling(self):
        value = {"b": [1, 2.5, True, None], "a": {"name": "Broken Conté", "z": 1, "c": 2}}
        text = bc.json_text(value)
        self.assertEqual(text, '{\n  "a": {\n    "c": 2,\n    "name": "Broken Conté",\n    "z": 1\n  },\n'
                               '  "b": [\n    1,\n    2.5,\n    true,\n    null\n  ]\n}\n')
        self.assertEqual(json.loads(text), value)
        self.assertEqual(bc.json_text({"b": 1, "a": 2}), bc.json_text({"a": 2, "b": 1}))

    def test_json_refuses_nan_and_infinity(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                bc.json_text({"value": bad})

    def test_write_json(self):
        target = self.tmp / "catalog" / "catalog.json"
        bc.write_json(target, {"schema": "x", "counts": {"brushes": 0}})
        self.assertEqual(target.read_bytes(), bc.json_text({"counts": {"brushes": 0}, "schema": "x"}).encode("utf-8"))


class Console(unittest.TestCase):
    def test_both_streams_become_utf8(self):
        out, err = mock.Mock(), mock.Mock()
        with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", err):
            bc.open_console()
        out.reconfigure.assert_called_once_with(encoding="utf-8", errors="replace")
        err.reconfigure.assert_called_once_with(encoding="utf-8", errors="replace")

    def test_a_stream_that_cannot_be_reconfigured_is_left_alone(self):
        with mock.patch.object(sys, "stdout", io.StringIO()), mock.patch.object(sys, "stderr", object()):
            bc.open_console()


class Isolated(fixtures.BrushCase):
    """The modules import under `python -I` from another directory: no reliance
    on the working directory, on PYTHONPATH or on PYTHONIOENCODING."""

    def run_isolated(self, code, **env):
        environment = {k: v for k, v in os.environ.items() if not k.upper().startswith("PYTHON")}
        environment.update(env)
        return subprocess.run([sys.executable, "-I", "-B", "-c", code, str(PIPELINE)],
                              cwd=str(self.tmp), env=environment, capture_output=True, timeout=120)

    CODE = ("import sys; sys.path.insert(0, sys.argv[1]); import brush_common, identity; "
            "brush_common.open_console(); p = brush_common.resolve_paths(); "
            "print(p.root); print(p.library); print(identity.brush_id(b'A')); print('\\u00e9\\U0001f4a7')")

    def test_default_root_from_another_directory(self):
        done = self.run_isolated(self.CODE)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        lines = done.stdout.decode("utf-8").splitlines()
        self.assertEqual(Path(lines[0]), BRUSHES.resolve())
        self.assertEqual(Path(lines[1]), BRUSHES.resolve() / "library")
        self.assertEqual(lines[2], "b_8f525da47bd2")
        self.assertEqual(lines[3], "é\U0001f4a7", "stdout is UTF-8 without PYTHONIOENCODING")

    def test_the_variables_are_read_even_when_python_ignores_its_own(self):
        done = self.run_isolated(self.CODE, ROSW_BRUSHES_ROOT=str(self.tmp / "data"),
                                 ROSW_BRUSHES_LIBRARY=str(self.tmp / "originals"))
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        lines = done.stdout.decode("utf-8").splitlines()
        self.assertEqual(Path(lines[0]), self.tmp / "data")
        self.assertEqual(Path(lines[1]), self.tmp / "originals")
        self.assertEqual(list(self.tmp.iterdir()), [], "resolving created nothing")


if __name__ == "__main__":
    unittest.main()
