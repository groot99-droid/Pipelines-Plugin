"""Artifacts: what a run keeps, and what a note may list.

`studio_run.py keep` copies a file the run made into the assets folder after
the execute go-ahead; a record write lists every kept file, and every listed
artifact is a file under that folder with a role the spec allows.
"""

import unittest

from helpers import GOOD_NOTE, NOTE, StudioCase


def with_artifacts(note, entries):
    block = "artifacts:\n" + "".join(f"  - path: {path}\n    role: {role}\n" for path, role in entries)
    return note.replace("tags: [ui]\n", "tags: [ui]\n" + block)


class Keep(StudioCase):
    def test_a_kept_file_lands_under_project_kind_slug_and_is_remembered(self):
        run_id = self.new_run()
        self.through(run_id, "execute")
        self.put(run_id, "palette.json", '{"cyan": "#00E5FF"}\n')
        code, out, err = self.run_cmd("keep", run_id, "palette.json", "--role", "export")
        self.assertEqual(code, 0, err)
        target = self.assets / "one-offs" / "ui" / "ops-console" / "palette.json"
        self.assertTrue(target.is_file())
        self.assertIn("- path: one-offs/ui/ops-console/palette.json", out)
        kept = self.state(run_id)["kept"]
        self.assertEqual([(k["path"], k["role"]) for k in kept], [("one-offs/ui/ops-console/palette.json", "export")])
        self.assertEqual(len(kept[0]["sha"]), 64)

    def test_keep_refusals(self):
        run_id = self.new_run()
        self.through(run_id, "recipe")
        self.put(run_id, "out.png", "png bytes\n")
        code, _, err = self.run_cmd("keep", run_id, "out.png", "--role", "final")
        self.assertEqual(code, 1)
        self.assertIn("before the execute go-ahead", err)
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "run it")[0], 0)
        code, _, err = self.run_cmd("keep", run_id, "out.png", "--role", "poster")
        self.assertEqual(code, 2)
        self.assertIn("--role is one of", err)
        code, _, err = self.run_cmd("keep", run_id, "../spec.yaml", "--role", "final")
        self.assertEqual(code, 1)
        self.assertIn("not in the run folder", err)
        code, _, err = self.run_cmd("keep", run_id, "missing.png", "--role", "final")
        self.assertEqual(code, 1)
        code, _, err = self.run_cmd("keep", run_id, "state.json", "--role", "final")
        self.assertEqual(code, 1)
        self.assertIn("bookkeeping", err)
        self.assertEqual(self.run_cmd("keep", run_id, "out.png", "--role", "final")[0], 0)
        self.assertEqual(self.run_cmd("keep", run_id, "out.png", "--role", "final")[0], 0)  # same bytes: fine
        self.put(run_id, "out.png", "other bytes\n")
        code, _, err = self.run_cmd("keep", run_id, "out.png", "--role", "final")
        self.assertEqual(code, 1)
        self.assertIn("never written over", err)
        self.assertEqual(len(self.state(run_id)["kept"]), 1)

    def test_a_run_with_no_note_keeps_nothing(self):
        run_id = self.new_run()
        self.put(run_id, "out.png", "x")
        code, _, err = self.run_cmd("keep", run_id, "out.png", "--role", "final")
        self.assertEqual(code, 1)
        self.assertIn("no note", err)


class RecordListsWhatWasKept(StudioCase):
    def setUp(self):
        super().setUp()
        self.run_id = self.new_run()
        self.through(self.run_id, "execute")
        self.put(self.run_id, "palette.json", "{}\n")
        self.assertEqual(self.run_cmd("keep", self.run_id, "palette.json", "--role", "export")[0], 0)
        self.put(self.run_id, "review.md", "Fine.\n")
        self.assertEqual(self.run_cmd("advance", self.run_id)[0], 0)

    def test_a_record_that_leaves_a_kept_file_out_is_refused(self):
        self.put(self.run_id, "note_update.md", GOOD_NOTE)
        code, out, err = self.note_cmd("plan", self.run_id)
        self.assertEqual(code, 1)
        self.assertIn("kept `one-offs/ui/ops-console/palette.json` and the note does not list it", err)

    def test_a_record_with_the_wrong_role_is_refused(self):
        self.put(self.run_id, "note_update.md",
                 with_artifacts(GOOD_NOTE, [("one-offs/ui/ops-console/palette.json", "final")]))
        code, out, err = self.note_cmd("plan", self.run_id)
        self.assertEqual(code, 1)
        self.assertIn("was kept as `export`, and the note says `final`", err)

    def test_a_record_that_lists_it_is_written(self):
        self.put(self.run_id, "note_update.md",
                 with_artifacts(GOOD_NOTE, [("one-offs/ui/ops-console/palette.json", "export")]))
        code, out, err = self.note_cmd("plan", self.run_id)
        self.assertEqual(code, 0, out + err)
        self.assertEqual(self.run_cmd("confirm", self.run_id, "record", "--words", "write it")[0], 0)
        self.assertEqual(self.note_cmd("apply", self.run_id, "--confirm")[0], 0)
        self.assertEqual(self.run_cmd("advance", self.run_id)[0], 0)
        self.assertEqual(self.state(self.run_id)["status"], "complete")

    def test_a_record_that_lists_a_file_that_is_not_there_is_refused(self):
        self.put(self.run_id, "note_update.md",
                 with_artifacts(GOOD_NOTE, [("one-offs/ui/ops-console/palette.json", "export"),
                                            ("one-offs/ui/ops-console/ghost.png", "final")]))
        code, out, err = self.note_cmd("plan", self.run_id)
        self.assertEqual(code, 1)
        self.assertIn("`one-offs/ui/ops-console/ghost.png` is not under the assets folder", err)

    def test_a_flush_does_not_owe_the_artifacts(self):
        self.put(self.run_id, "note_update.md", GOOD_NOTE.replace(
            "- [ ] Review the proposed palette against the contrast floors",
            f"- [ ] Resume run `{self.run_id}` at record"))
        code, out, err = self.note_cmd("plan", self.run_id, "--as", "flush")
        self.assertEqual(code, 0, out + err)


class Lint(StudioCase):
    def lint(self, entries):
        self.place(NOTE, with_artifacts(GOOD_NOTE, entries))
        code, out, err = self.note_cmd("lint", NOTE)
        return code, out + err

    def test_a_link_is_never_an_artifact(self):
        for path in ("https://example.com/x.png", "file:///tmp/x.png", "//host/share/x.png"):
            with self.subTest(path=path):
                code, text = self.lint([(path, "final")])
                self.assertEqual(code, 1)
                self.assertIn("never a link", text)

    def test_a_path_stays_under_the_assets_folder(self):
        for path in ("../secrets/key.pem", "/etc/passwd", "one-offs/../../x.png"):
            with self.subTest(path=path):
                code, text = self.lint([(path, "final")])
                self.assertEqual(code, 1)
                self.assertIn("leaves the assets folder", text)

    def test_role_shape_and_duplicates(self):
        code, text = self.lint([("one-offs/ui/ops-console/a.png", "poster")])
        self.assertEqual(code, 1)
        self.assertIn("role `poster`", text)
        code, text = self.lint([("one-offs/ui/ops-console/a.png", "final"), ("one-offs/ui/ops-console/a.png", "final")])
        self.assertEqual(code, 1)
        self.assertIn("listed twice", text)
        self.place(NOTE, GOOD_NOTE.replace("tags: [ui]\n", "tags: [ui]\nartifacts:\n  - one-offs/ui/ops-console/a.png\n"))
        code, out, err = self.note_cmd("lint", NOTE)
        self.assertEqual(code, 1)
        self.assertIn("`- path: ...` and `role: ...`", out + err)

    def test_a_missing_file_is_a_warning_in_lint(self):
        code, text = self.lint([("one-offs/ui/ops-console/a.png", "final")])
        self.assertEqual(code, 0, text)
        self.assertIn("is not under the assets folder", text)
        target = self.assets / "one-offs" / "ui" / "ops-console" / "a.png"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"png")
        code, text = self.lint([("one-offs/ui/ops-console/a.png", "final")])
        self.assertEqual(code, 0)
        self.assertNotIn("not under the assets folder", text)


if __name__ == "__main__":
    unittest.main()
