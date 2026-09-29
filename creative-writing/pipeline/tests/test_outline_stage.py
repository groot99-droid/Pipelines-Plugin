"""The outline stage of run_pipeline.py with the model stubbed out: rules are
injected, the ledger is checked, a failing ledger gets exactly one repair pass,
and modes with no plot logic are left alone."""
import sys
import tempfile
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE))

import run_pipeline as rp  # noqa: E402

GOOD = """# Outline

## Causal ledger

Mode: horror-prose

| # | Link | Because | Beat | Response | Changes |
|---|------|---------|------|----------|---------|
| 1 | open | - | Lamp dims early. | denies | He logs it instead of looking |
| 2 | T | 1 "logs it" | He logs everything. | investigates | The log outgrows the job |
| 3 | B | 2 "the log" | A page in his hand he cannot recall. | denies | An entry with no memory attached |

Ending: cyclical
"""

BAD = GOOD.replace("| 2 | T | 1 \"logs it\" |", "| 2 | A | - |")


class OutlineStage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self._runs, rp.RUNS_DIR = rp.RUNS_DIR, Path(self.tmp.name)
        self.addCleanup(setattr, rp, "RUNS_DIR", self._runs)
        self.run_id = "t"
        rp.run_dir(self.run_id).mkdir()
        rp.write_artifact(self.run_id, "idea.md", "idea")
        rp.write_artifact(self.run_id, "references.md", "refs")
        self.spec = rp.load_spec()
        self.prompts = []
        self._draft, self.replies = rp.draft, []
        rp.draft = self._fake_draft
        self.addCleanup(setattr, rp, "draft", self._draft)

    def _fake_draft(self, prompt):
        self.prompts.append(prompt)
        return self.replies.pop(0)

    def test_rules_are_injected_into_the_prompt(self):
        self.replies = [GOOD]
        rp.handle_outline(self.run_id, self.spec, "horror-prose")
        self.assertIn('"## Causal ledger"', self.prompts[0])
        self.assertNotIn("{plot_logic}", self.prompts[0])

    def test_clean_ledger_passes_with_one_model_call(self):
        self.replies = [GOOD]
        msg = rp.handle_outline(self.run_id, self.spec, "horror-prose")
        self.assertEqual(len(self.prompts), 1)
        self.assertIn("PASSED", msg)
        self.assertTrue((rp.run_dir(self.run_id) / "plot_logic_report.md").exists())

    def test_failing_ledger_gets_one_repair_pass(self):
        self.replies = [BAD, GOOD]
        msg = rp.handle_outline(self.run_id, self.spec, "horror-prose")
        self.assertEqual(len(self.prompts), 2)
        self.assertIn("checker report", self.prompts[1])
        self.assertIn("PASSED", msg)
        self.assertEqual(rp.read_artifact(self.run_id, "outline.md"), GOOD)

    def test_a_repair_that_makes_things_worse_is_discarded(self):
        worse = BAD.replace("Ending: cyclical", "")
        self.replies = [BAD, worse]
        msg = rp.handle_outline(self.run_id, self.spec, "horror-prose")
        self.assertEqual(rp.read_artifact(self.run_id, "outline.md"), BAD)
        self.assertIn("FAILED", msg)

    def test_no_second_repair(self):
        self.replies = [BAD, BAD]
        rp.handle_outline(self.run_id, self.spec, "horror-prose")
        self.assertEqual(len(self.prompts), 2)

    def test_modes_without_plot_logic_are_untouched(self):
        self.replies = ["An essay outline."]
        msg = rp.handle_outline(self.run_id, self.spec, "essay-self-help")
        self.assertEqual(len(self.prompts), 1)
        self.assertNotIn("PLOT LOGIC", self.prompts[0])
        self.assertFalse((rp.run_dir(self.run_id) / "plot_logic_report.md").exists())
        self.assertNotIn("plot logic", msg)

    def test_a_register_turns_it_on_for_a_poem(self):
        self.replies = ["No ledger here.", "Still no ledger."]
        msg = rp.handle_outline(self.run_id, self.spec, "confessional-poetry", ["psychedelic"])
        self.assertIn("Self (psychedelic)", self.prompts[0])
        self.assertEqual(len(self.prompts), 2)  # a missing ledger is repaired once...
        self.assertIn("FAILED", msg)            # ...and if still missing, reported, not swallowed


META = (
    "```json\n"
    '{"title": "A Test Piece", "genre": ["horror"], "themes": ["dread"], "archetypes": [], '
    '"status": "draft", "pov": "third-limited", "tense": "past", "project": "", '
    '"index_entry_summary": "A test.", "annotation_patterns": ["catalogued-escalation"], '
    '"annotation_body": "Analysis."}\n'
    "```"
)


class IntegrationFrontmatter(unittest.TestCase):
    """handle_vault_integration in dry-run mode (nothing is written to the real vault)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self._runs, rp.RUNS_DIR = rp.RUNS_DIR, Path(self.tmp.name)
        self.addCleanup(setattr, rp, "RUNS_DIR", self._runs)
        rp.run_dir("t").mkdir()
        for name in ("idea.md", "outline.md", "plot_logic_report.md", "draft_revised.md", "revision_notes.md"):
            rp.write_artifact("t", name, f"{name} body")
        self.spec = rp.load_spec()
        self.vault = rp.vault_root_from_spec(self.spec)
        self._draft, rp.draft = rp.draft, lambda prompt: META
        self.addCleanup(setattr, rp, "draft", self._draft)
        self.captured = {}
        self._plan = rp.vi.plan_integration

        def spy(vault_root, work):
            self.captured["work"] = work
            return self._plan(vault_root, work)

        rp.vi.plan_integration = spy
        self.addCleanup(setattr, rp.vi, "plan_integration", self._plan)

    def test_register_is_recorded_when_used(self):
        rp.handle_vault_integration("t", self.spec, "horror-prose", self.vault, confirm=False, registers=["cosmic"])
        fm = self.captured["work"].frontmatter
        self.assertEqual(fm["register"], ["cosmic"])
        self.assertIn("register/cosmic", fm["tags"])
        self.assertEqual(fm["mode"], "horror-prose")                   # a register never changes the mode
        self.assertIn("register/cosmic", self.captured["work"].annotation_frontmatter["tags"])

    def test_ordinary_piece_has_no_register_field(self):
        rp.handle_vault_integration("t", self.spec, "horror-prose", self.vault, confirm=False)
        self.assertNotIn("register", self.captured["work"].frontmatter)


if __name__ == "__main__":
    unittest.main()
