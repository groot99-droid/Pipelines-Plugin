import _paths  # noqa: F401  (puts src/ on sys.path)
import json
import tempfile
import unittest
from pathlib import Path

from videoeditor import questionnaire as Q
from videoeditor import recipes
from videoeditor.cli import main as ve


def brief(**answers):
    return Q.build_brief(["/nonexistent/src.mp4"], answers)


class RecipeSelection(unittest.TestCase):
    def test_action_wins_over_everything(self):
        b = brief(content="action", goal="highlights", captions="opus")
        self.assertEqual(b["recipe"], "action_montage")

    def test_highlights_vs_single_edit(self):
        self.assertEqual(brief(content="dialogue", goal="highlights")["recipe"], "highlight_clips")
        self.assertEqual(brief(content="dialogue", goal="single_edit")["recipe"], "long_form")

    def test_overlays_add_explainer_without_changing_primary(self):
        b = brief(content="dialogue", goal="single_edit", overlays="manim")
        self.assertEqual((b["recipe"], b["addons"]), ("long_form", ["explainer"]))
        self.assertEqual(brief(goal="single_edit")["addons"], [])

    def test_overlay_engines_offered_are_ones_the_cli_accepts(self):
        (q,) = [q for q in Q.QUESTIONS if q.key == "overlays"]
        self.assertEqual(q.choices, ["none", "pil", "remotion", "manim"])
        self.assertNotIn("hyperframes", q.help)

    def test_every_recipe_has_playbook_and_steps(self):
        for name in ("highlight_clips", "long_form", "action_montage", "explainer"):
            r = recipes.get(name)
            self.assertTrue(r.playbook.exists(), r.playbook)
            self.assertTrue(r.steps(brief(overlays="pil")))


class Pruning(unittest.TestCase):
    def test_action_skips_goal_and_captions(self):
        b = brief(content="action")
        self.assertNotIn("goal", b)
        self.assertNotIn("captions", b)

    def test_reframe_only_asked_for_landscape_source_going_vertical(self):
        # no probe (missing file) -> orientation unknown -> reframe never applies
        self.assertNotIn("reframe", brief(deliverable="vertical"))
        reframe_q = next(q for q in Q.QUESTIONS if q.key == "reframe")
        self.assertTrue(reframe_q.applies({"deliverable": "vertical", "source_orientation": "landscape"}))
        self.assertFalse(reframe_q.applies({"deliverable": "landscape", "source_orientation": "landscape"}))
        self.assertFalse(reframe_q.applies({"deliverable": "vertical", "source_orientation": "vertical"}))

    def test_validate_warnings(self):
        self.assertEqual(Q.validate({"content": "action", "captions": "opus", "deliverable": "vertical"}),
                         ["captions ignored for action montage: the strike sounds are the rhythm"])
        self.assertEqual(Q.validate({"content": "dialogue", "deliverable": "landscape", "source_orientation": "vertical"}),
                         ["vertical source with landscape deliverable: output will be letterboxed or cropped hard"])


class Validation(unittest.TestCase):
    def test_bad_choice_and_unknown_key_exit(self):
        with self.assertRaises(SystemExit):
            brief(deliverable="diagonal")
        with self.assertRaises(SystemExit):
            brief(nonsense="x")

    def test_schema_matches_questions(self):
        self.assertEqual([q["key"] for q in Q.schema()], Q.QUESTION_KEYS)


class CliSmoke(unittest.TestCase):
    def test_ask_saves_brief_and_plan_runs(self):
        with tempfile.TemporaryDirectory() as td:
            edit = Path(td) / "edit"
            ve(["ask", "/nonexistent/a.mp4", "--defaults", "--edit-dir", str(edit),
                "--answers", json.dumps({"goal": "highlights", "deliverable": "vertical", "captions": "opus"})])
            saved = json.loads((edit / "brief.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["recipe"], "highlight_clips")
            ve(["plan", "--edit-dir", str(edit)])


if __name__ == "__main__":
    unittest.main()


class Interactive(unittest.TestCase):
    def test_numbers_names_and_blank_default(self):
        from unittest import mock
        answers = iter(["2", "", "action"])  # 2nd choice, default, by name
        with mock.patch("builtins.input", lambda _="": next(answers)):
            q = {q.key: q for q in Q.QUESTIONS}
            self.assertEqual(Q.ask_interactive(q["deliverable"]), "landscape")
            self.assertEqual(Q.ask_interactive(q["content"]), "dialogue")
            self.assertEqual(Q.ask_interactive(q["content"]), "action")
