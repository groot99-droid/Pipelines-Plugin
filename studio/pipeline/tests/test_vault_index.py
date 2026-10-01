"""vault_index.py: rows, index and search over a temporary vault."""

import json
import sys
import unittest

from helpers import GOOD_NOTE, NOTE, PIPELINE, StudioCase, precedent

sys.path.insert(0, str(PIPELINE.parent / "vault" / "tools"))
import vault_index  # noqa: E402


class Rows(StudioCase):
    def setUp(self):
        super().setUp()
        self.place(NOTE, GOOD_NOTE)
        self.place("aurora/design/harbor-dusk.md", precedent("harbor-dusk", kind="design"))
        self.place("aurora/design/north-gate.md", precedent("north-gate", kind="design", status="blocked")
                   .replace("## Decisions in Force", "## Next Steps\n\n- [ ] Author the key light\n- [ ] Second\n\n## Decisions in Force"))
        self.place("_Context/not-a-note.md", GOOD_NOTE)      # under a _ folder: never a note
        self.place("aurora/design/plain.md", "# Plain\n\nNo frontmatter, so not a Content MD.\n")

    def test_one_row_per_content_md(self):
        rows = vault_index.note_rows(self.env)
        self.assertEqual(sorted(r["path"] for r in rows),
                         ["aurora/design/harbor-dusk.md", "aurora/design/north-gate.md", NOTE])

    def test_a_row_carries_the_desk_fields_and_no_body(self):
        row = next(r for r in vault_index.note_rows(self.env) if r["path"] == NOTE)
        self.assertEqual(row["title"], "Ops console")
        self.assertEqual(row["kind"], "ui")
        self.assertEqual(row["status"], "in-progress")
        self.assertEqual(row["context_brand"], ["fixture_look", "fixture_colour"])
        self.assertEqual(row["pipelines"], ["ui-direction"])
        self.assertTrue(row["overview"].startswith("A design direction"))
        self.assertEqual(row["next_steps_open"], 1)
        self.assertTrue(row["first_step"].startswith("Review the proposed palette"))
        self.assertNotIn("body", row)
        self.assertNotIn("Matched category", json.dumps(row))

    def test_a_blocked_note_names_its_blocker_first(self):
        row = next(r for r in vault_index.note_rows(self.env) if r["path"].endswith("north-gate.md"))
        self.assertEqual(row["status"], "blocked")
        self.assertEqual(row["first_step"], "Author the key light")
        self.assertEqual(row["next_steps_open"], 2)

    def test_the_project_is_shown_without_its_brackets(self):
        self.place("aurora/design/linked.md", precedent("linked", kind="design")
                   .replace("pipelines:", 'project: "[[Project Aurora]]"\npipelines:'))
        row = next(r for r in vault_index.note_rows(self.env) if r["path"].endswith("linked.md"))
        self.assertEqual(row["project"], "Project Aurora")


class Index(StudioCase):
    def setUp(self):
        super().setUp()
        self.place(NOTE, GOOD_NOTE)
        self.place("aurora/design/harbor-dusk.md", precedent("harbor-dusk", kind="design",
                   decisions=("Key light sits camera left.", "The harbour is drawn at dusk, never noon.")))
        self.index = vault_index.build_index(self.env)

    def test_the_index_holds_rows_vectors_and_previews_but_no_text(self):
        self.assertEqual(len(self.index["notes"]), 2)
        self.assertTrue(self.index["chunks"])
        for chunk in self.index["chunks"]:
            self.assertEqual(set(chunk), {"path", "title", "heading", "preview", "vector", "norm"})
            self.assertLessEqual(len(chunk["preview"]), vault_index.PREVIEW_CHARS + 1)
        self.assertNotIn("text", self.index["chunks"][0])

    def test_search_names_the_note_and_the_section(self):
        hits = vault_index.search_index(self.index, "harbour dusk")
        self.assertTrue(hits)
        score, chunk = hits[0]
        self.assertEqual(chunk["path"], "aurora/design/harbor-dusk.md")
        self.assertEqual(chunk["heading"], "Decisions in Force")
        self.assertGreater(score, 0)

    def test_search_narrows_by_kind_and_status(self):
        self.assertEqual({c["path"] for _, c in vault_index.search_index(self.index, "console dashboard", kind="ui")},
                         {NOTE})
        self.assertEqual(vault_index.search_index(self.index, "console", kind="design"), [])
        self.assertEqual(vault_index.search_index(self.index, "", kind="design"), [])

    def test_the_index_round_trips_through_json(self):
        out = self.root / "index.json"
        code, stdout, _ = self.call(vault_index, "index", "--out", str(out))
        self.assertEqual(code, 0)
        loaded = vault_index.load_index(out)
        self.assertEqual(len(loaded["chunks"]), len(self.index["chunks"]))
        code, stdout, _ = self.call(vault_index, "search", "harbour", "--index", str(out), "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)[0]["path"], "aurora/design/harbor-dusk.md")

    def test_a_missing_index_is_a_usage_error(self):
        code, _, err = self.call(vault_index, "search", "x", "--index", str(self.root / "none.json"))
        self.assertEqual(code, 2)
        self.assertIn("no index", err)


if __name__ == "__main__":
    unittest.main()
