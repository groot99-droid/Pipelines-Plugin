"""The brand-gate pipeline: a gate transcribed from an interview, shown whole,
written only after the author's yes, and read back by the bookkeeper from its
own headings."""

import unittest
from datetime import date

from helpers import FIXTURE_FILES, StudioCase, studio_common

import gate_md

TODAY = date.today().isoformat()


def gate_text(run_id, gate="fixture_voice", answers=("Plain words", "Second person"),
              unresolved=("banned phrasings",), provenance=None):
    lines = [f"# {gate}", "", "## 0. Provenance", "",
             provenance if provenance is not None else
             f"Answered by the author on {TODAY}, in run {run_id}. Transcribed from execute_log.md.",
             ""]
    number = 0
    for number, title in enumerate(answers, 1):
        lines += [f"## {number}. {title}", "", f"\"{title}\", in the author's words.", ""]
    if unresolved:
        lines += [f"## {number + 1}. Unresolved", ""] + [f"- {item}" for item in unresolved] + [""]
    return "\n".join(lines)


def gate_note(run_id, gate="fixture_voice"):
    return f"""---
id: cmd_20260930_{gate.replace('_', '-')}
type: content-md
kind: other
title: The {gate} gate
status: complete
created: {TODAY}
updated: {TODAY}
pipelines: [brand-gate]
context_brand: [{gate}]
---

## Overview

How the {gate} brand gate was written, from an interview with the author.

## Timeline

### {TODAY} · brand-gate · {run_id}
Wrote {gate} from the interview: two questions answered, one left unresolved.

## Method

Asked the questions in the recipe, in order.
"""


class GateRun(StudioCase):
    """A brand-gate run, driven stage by stage."""

    def begin(self, gate="fixture_voice", run_id="voice-gate"):
        run_id = self.new_run(run_id, pipeline="brand-gate")
        self.put(run_id, "brief.md", f"Write the {gate} gate.\n")
        self.assertEqual(self.run_cmd("gate", run_id, gate)[0], 0)
        self.assertEqual(self.run_cmd("note", run_id, f"one-offs/other/{gate}.md")[0], 0)
        return run_id

    def advance(self, run_id):
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 0, err)

    def to_review(self, run_id):
        self.advance(run_id)                                   # intake
        self.put(run_id, "attestation.md", "# Attestation\n\nThis pipeline needs no brand context.\n")
        self.advance(run_id)                                   # context
        self.put(run_id, "recipe.md", "1. How are controls worded?\n2. Whom does it address?\n")
        self.advance(run_id)                                   # recipe
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "ask me")[0], 0)
        self.put(run_id, "execute_log.md", 'Q1. How are controls worded?\nA. "Plain words"\n')
        self.advance(run_id)                                   # execute

    def at_record(self, gate="fixture_voice", run_id="voice-gate"):
        run_id = self.begin(gate, run_id)
        self.to_review(run_id)
        self.put(run_id, "gate_update.md", gate_text(run_id, gate))
        self.put(run_id, "review.md", "Each section came from one answer in the transcript.\n")
        self.advance(run_id)                                   # review
        return run_id

    def gate_cmd(self, *arguments):
        return self.call(gate_md, *arguments)

    def write_gate(self, run_id):
        code, _, err = self.gate_cmd("plan", run_id)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.run_cmd("confirm", run_id, "gate", "--words", "write it")[0], 0)
        code, _, err = self.gate_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 0, err)

    def write_note(self, run_id, gate="fixture_voice"):
        self.put(run_id, "note_update.md", gate_note(run_id, gate))
        code, _, err = self.note_cmd("plan", run_id)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "write it")[0], 0)
        self.assertEqual(self.note_cmd("apply", run_id, "--confirm")[0], 0)


class WholeRun(GateRun):
    def test_an_interview_becomes_a_gate(self):
        run_id = self.at_record()
        gate_file = self.context / "fixture_voice.context.md"
        self.assertFalse(gate_file.exists())
        self.write_gate(run_id)
        self.write_note(run_id)
        self.advance(run_id)
        state = self.state(run_id)
        self.assertEqual(state["status"], "complete")
        self.assertEqual(gate_file.read_text(encoding="utf-8").rstrip("\n"),
                         gate_text(run_id).rstrip("\n"))
        sections = studio_common.gate_sections(self.env, "fixture_voice")
        self.assertEqual([item["topic"] for item in sections["answers"]], ["Plain words", "Second person"])
        self.assertEqual(sections["unresolved"], [{"section": "3", "topic": "banned phrasings"}])

    def test_the_plan_shows_the_whole_gate(self):
        run_id = self.at_record()
        self.assertEqual(self.gate_cmd("plan", run_id)[0], 0)
        plan = (self.runs / run_id / "gate_plan.md").read_text(encoding="utf-8")
        self.assertIn(gate_text(run_id).rstrip("\n"), plan)
        self.assertIn("ready for the author", plan)
        self.assertFalse((self.context / "fixture_voice.context.md").exists())

    def test_a_rewrite_shows_the_change_as_well(self):
        run_id = self.at_record("fixture_look", "look-gate")
        self.assertEqual(self.gate_cmd("plan", run_id)[0], 0)
        plan = (self.runs / run_id / "gate_plan.md").read_text(encoding="utf-8")
        self.assertIn("rewrites fixture_look.context.md", plan)
        self.assertIn("## What changes", plan)

    def test_the_next_run_reads_the_new_gate(self):
        run_id = self.at_record("fixture_look", "look-gate")
        self.write_gate(run_id)
        answers = {item["section"] for item in studio_common.gate_sections(self.env, "fixture_look")["answers"]}
        self.assertEqual(answers, {"1", "2"})
        ui = self.new_run("ui-after")
        self.through(ui, "intake")
        row = "| grounds | fixture_look | L0 AUTHORED | fixture_look.context.md section 5 | resolved |"
        self.put(ui, "attestation.md", self.attestation([row]))
        code, _, err = self.run_cmd("advance", ui)
        self.assertEqual(code, 1)
        self.assertIn("answers nothing in a section 5", err)


class Intake(GateRun):
    def test_a_gate_run_names_its_gate(self):
        run_id = self.new_run("voice-gate", pipeline="brand-gate")
        self.put(run_id, "brief.md", "A gate.\n")
        self.run_cmd("note", run_id, "one-offs/other/fixture_voice.md")
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("names no gate", err)

    def test_only_a_gate_writing_pipeline_names_one(self):
        run_id = self.new_run()
        code, _, err = self.run_cmd("gate", run_id, "fixture_voice")
        self.assertEqual(code, 1)
        self.assertIn("does not write a brand gate", err)
        code, _, err = self.run_cmd("confirm", run_id, "gate", "--words", "yes")
        self.assertEqual(code, 1)
        self.assertIn("does not write a brand gate", err)

    def test_a_gate_the_spec_does_not_have(self):
        run_id = self.new_run("voice-gate", pipeline="brand-gate")
        code, _, err = self.run_cmd("gate", run_id, "house_style")
        self.assertEqual(code, 2)
        self.assertIn("no gate `house_style`", err)

    def test_one_gate_per_run(self):
        run_id = self.at_record()
        self.write_gate(run_id)
        code, _, err = self.run_cmd("gate", run_id, "fixture_look")
        self.assertEqual(code, 1)
        self.assertIn("A run writes one gate", err)


class Context(GateRun):
    def test_a_pipeline_that_needs_nothing_needs_no_table(self):
        run_id = self.begin()
        self.advance(run_id)
        for text in ("# Attestation\n\nNo brand context is needed.\n",
                     "## Context resolution\n\n| Constraint | Gate | Level | Source | State |\n|---|---|---|---|---|\n"):
            with self.subTest(text=text[:20]):
                self.put(run_id, "attestation.md", text)
                code, _, err = self.run_cmd("advance", run_id)
                self.assertEqual(code, 0, err)
                self.assertEqual(self.run_cmd("back", run_id, "--why", "again")[0], 0)

    def test_a_table_it_does_write_is_still_checked(self):
        run_id = self.begin()
        self.advance(run_id)
        self.put(run_id, "attestation.md", self.attestation(
            ["| wording | fixture_voice | L3 | nothing | UNRESOLVED |"]))
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("L3 is UNRESOLVED", err)

    def test_a_pipeline_that_needs_context_still_needs_the_table(self):
        run_id = self.new_run()
        self.through(run_id, "intake")
        self.put(run_id, "attestation.md", "# Attestation\n\nNo brand context is needed.\n")
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("no context-resolution table", err)

    def test_facts_says_which_gate_is_written(self):
        run_id = self.begin("fixture_look", "look-gate")
        _, out, _ = self.run_cmd("facts", run_id)
        self.assertIn("needs no brand context", out)
        self.assertIn("writes the gate fixture_look", out)
        self.assertIn("DECLARED GAP  section 7", out)


class WritingTheGate(GateRun):
    def test_provenance_names_the_author_the_date_and_the_run(self):
        run_id = self.at_record()
        for provenance, why in (("Answered on 2026-09-30, in run voice-gate.", "the author"),
                                (f"Answered by the author on {TODAY}.", "names the run"),
                                ("Answered by the author, in run voice-gate.", "the date"),
                                ("Answered by the author on 2020-01-01, in run voice-gate.", "the date")):
            with self.subTest(provenance=provenance):
                self.put(run_id, "gate_update.md", gate_text(run_id, provenance=provenance))
                code, _, err = self.gate_cmd("plan", run_id)
                self.assertEqual(code, 1)
                self.assertIn(why, err)

    def test_the_title_names_the_gate(self):
        run_id = self.at_record()
        self.put(run_id, "gate_update.md", gate_text(run_id).replace("# fixture_voice", "# Voice"))
        code, _, err = self.gate_cmd("plan", run_id)
        self.assertEqual(code, 1)
        self.assertIn("the title line names the gate", err)

    def test_apply_needs_a_plan_and_a_go_ahead_after_it(self):
        run_id = self.at_record()
        code, _, err = self.gate_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("there is no gate plan", err)
        self.run_cmd("confirm", run_id, "gate", "--words", "yes")
        self.assertEqual(self.gate_cmd("plan", run_id)[0], 0)
        code, _, err = self.gate_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("older than the plan", err)
        self.assertFalse((self.context / "fixture_voice.context.md").exists())

    def test_apply_without_confirm_is_a_dry_run(self):
        run_id = self.at_record()
        self.gate_cmd("plan", run_id)
        self.run_cmd("confirm", run_id, "gate", "--words", "yes")
        code, out, _ = self.gate_cmd("apply", run_id)
        self.assertEqual(code, 0)
        self.assertIn("DRY RUN", out)
        self.assertFalse((self.context / "fixture_voice.context.md").exists())

    def test_a_gate_changed_after_the_plan(self):
        run_id = self.at_record()
        self.gate_cmd("plan", run_id)
        self.run_cmd("confirm", run_id, "gate", "--words", "yes")
        self.put(run_id, "gate_update.md", gate_text(run_id, answers=("Plain words",)))
        code, _, err = self.gate_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("has not seen this version", err)

    def test_the_gate_on_disk_changed_after_the_plan(self):
        run_id = self.at_record("fixture_look", "look-gate")
        self.gate_cmd("plan", run_id)
        self.run_cmd("confirm", run_id, "gate", "--words", "yes")
        (self.context / "fixture_look.context.md").write_text("# fixture_look\n\nEdited.\n", encoding="utf-8")
        code, _, err = self.gate_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("changed after the plan", err)


class RecordWritesTheGate(GateRun):
    def test_record_is_refused_without_the_gate(self):
        run_id = self.at_record()
        self.write_note(run_id)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("has not written the gate `fixture_voice`", err)

    def test_a_gate_edited_after_it_was_written(self):
        run_id = self.at_record()
        self.write_gate(run_id)
        self.write_note(run_id)
        path = self.context / "fixture_voice.context.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nAdded by hand.\n", encoding="utf-8")
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("not the gate that was shown", err)

    def test_a_gate_written_before_the_latest_go_ahead(self):
        run_id = self.at_record()
        self.write_gate(run_id)
        self.write_note(run_id)
        self.run_cmd("confirm", run_id, "gate", "--words", "and again")
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("before the latest gate go-ahead", err)

    def test_going_back_drops_the_gate_plan(self):
        run_id = self.at_record()
        self.gate_cmd("plan", run_id)
        self.assertTrue(self.state(run_id)["gate_plan"])
        self.assertEqual(self.run_cmd("back", run_id, "--why", "one more question")[0], 0)
        self.assertIsNone(self.state(run_id)["gate_plan"])


class TheShapeOfAGate(StudioCase):
    def errors(self, text):
        return gate_md.lint_gate(text)

    def assertRefused(self, text, needle):
        errors = self.errors(text)
        self.assertTrue(any(needle in error for error in errors), f"no {needle!r} in {errors}")

    def test_the_fixture_gates_pass(self):
        for name, text in FIXTURE_FILES.items():
            with self.subTest(gate=name):
                self.assertEqual(self.errors(text), [])

    def test_what_it_refuses(self):
        good = gate_text("voice-gate")
        for text, needle in (
                (good.replace("# fixture_voice\n", ""), "title line"),
                (good.replace("## 0. Provenance", "## 0. History"), "`## 0. Provenance`"),
                (good.replace("## 2. Second person", "## 1. Second person"), "numbered in order"),
                (good + "\n## 4. Unresolved\n\n- more\n", "one Unresolved section"),
                (good + "\n## 4. Afterword\n\nMore.\n", "Unresolved section comes last"),
                (gate_text("voice-gate", answers=()), "answers nothing"),
                (good.replace("## 1. Plain words", "## Plain words"), "is not a gate section"),
                (good + "\n{{todo}}\n", "template placeholder"),
                (good + "\nsk-" + "a" * 30 + "\n", "credential"),
                (good + "\n```\nopen fence\n", "never closed")):
            with self.subTest(needle=needle):
                self.assertRefused(text, needle)

    def test_the_bookkeeper_reads_the_headings(self):
        sections = studio_common.gate_sections(self.env, "fixture_colour")
        self.assertEqual([item["section"] for item in sections["answers"]], ["2", "3", "4"])
        self.assertEqual(sections["unresolved"], [{"section": "5", "topic": "working space"}])
        self.assertIsNone(studio_common.gate_sections(self.env, "fixture_voice"))

    def test_lint_command(self):
        code, out, _ = self.call(gate_md, "lint", "--all")
        self.assertEqual(code, 0)
        self.assertIn("3 gate(s), 0 failing", out)
        (self.context / "fixture_type.context.md").write_text("no shape at all\n", encoding="utf-8")
        code, out, _ = self.call(gate_md, "lint", "fixture_type")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
