"""The bookkeeper refuses what the spec says it refuses, and nothing else."""

import json
import os
import time
import unittest
from datetime import date

from helpers import GOOD_NOTE, HEADER, NOTE, StudioCase, precedent, studio_run


class Starting(StudioCase):
    def test_a_stub_pipeline_does_not_start(self):
        stub = next(name for name, cfg in self.env.spec["pipelines"].items()
                    if cfg["status"] != "implemented")
        code, _, err = self.run_cmd("new", "--pipeline", stub, "--title", "Shot 7")
        self.assertEqual(code, 1)
        self.assertIn(self.env.pipeline(stub)["status"], err)
        self.assertEqual(list(self.runs.iterdir()), [])

    def test_every_stub_is_refused(self):
        for name, cfg in self.env.spec["pipelines"].items():
            if cfg["status"] == "implemented":
                continue
            with self.subTest(pipeline=name):
                self.assertEqual(self.run_cmd("new", "--pipeline", name, "--title", "x")[0], 1)

    def test_an_unknown_pipeline_is_a_usage_error(self):
        code, _, err = self.run_cmd("new", "--pipeline", "hologram", "--title", "x")
        self.assertEqual(code, 2)
        self.assertIn("no pipeline", err)

    def test_a_new_run_starts_at_the_first_stage(self):
        run_id = self.new_run()
        state = self.state(run_id)
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["next_stage_index"], 0)
        self.assertEqual(state["completed_stages"], [])
        code, out, _ = self.run_cmd("status", run_id, "--json")
        self.assertEqual(json.loads(out)["next_stage"], self.env.stages[0]["id"])

    def test_a_run_id_is_not_reused(self):
        self.new_run("same-id")
        code, _, err = self.run_cmd("new", "--pipeline", "ui-direction", "--title", "x",
                                    "--run-id", "same-id")
        self.assertEqual(code, 2)
        self.assertIn("already exists", err)

    def test_a_run_id_that_is_a_path(self):
        for bad in ("../escape", "a/b", "a\\b", "A-Capital", "x" * 90, "con:1", "a b", "a.b"):
            with self.subTest(run_id=bad):
                code, _, _ = self.run_cmd("new", "--pipeline", "ui-direction", "--title", "x",
                                          "--run-id", bad)
                self.assertEqual(code, 2)
        self.assertEqual(list(self.runs.iterdir()), [])

    def test_a_broken_state_file_is_an_error_not_a_crash(self):
        run_id = self.new_run()
        state = self.runs / run_id / "state.json"
        for broken in ("{not json", "[]", '{"run_id": "ops-console-aaaaaa"}'):
            with self.subTest(text=broken):
                state.write_text(broken, encoding="utf-8")
                for command in (("status", run_id), ("advance", run_id), ("stage", run_id)):
                    code, _, err = self.run_cmd(*command)
                    self.assertEqual(code, 2, err)
                    self.assertNotIn("Traceback", err)
        self.assertEqual(self.run_cmd("status")[0], 0)


class NotePaths(StudioCase):
    def test_paths_that_are_not_a_note(self):
        run_id = self.new_run()
        for path in ("_Context/brand/fixture_look.context.md", "../outside.md",
                     "C:/somewhere/note.md", "/etc/note.md", "aurora/ui/README.md",
                     "aurora/ui/SCHEMA.md", "aurora/ui/note.txt", ".obsidian/x.md",
                     "aurora//x.md", "_Pipelines/studio.md",
                     # names Windows would fold onto a reserved file
                     "claude.md", "CLAUDE.MD", "schema.md", "aurora/ui/Readme.md",
                     "aurora/ui/claude.md", "aurora/ui/x.md.", "aurora/ui /x.md",
                     "aurora/ui/x.md:stream.md", "aurora/ui/con.md", "aurora/ui/NUL.md",
                     # not where SCHEMA.md puts a note
                     "note.md", "aurora/note.md", "aurora/poem/x.md", "a/b/ui/x.md",
                     "aurora/UI/x.md"):
            with self.subTest(path=path):
                code, _, err = self.run_cmd("note", run_id, path)
                self.assertEqual(code, 2, err)
                self.assertIsNone(self.state(run_id)["note_path"])

    def test_a_reserved_file_cannot_be_reached_in_any_case(self):
        self.place("CLAUDE.md", "# the rules\n")
        for path in ("claude.md", "Claude.md", "one-offs/ui/claude.md", "one-offs/ui/SCHEMA.md",
                     "one-offs/ui/readme.md", "CLAUDE.md/ui/x.md", "aurora/ui/Readme.MD"):
            with self.subTest(path=path):
                run_id = self.new_run()
                self.through(run_id, "intake")
                code, _, err = self.run_cmd("note", run_id, path)
                self.assertEqual(code, 2)
                self.assertIn("reserved", err)
                self.assertEqual(self.state(run_id)["note_path"], "one-offs/ui/ops-console.md")
        self.assertEqual((self.vault / "CLAUDE.md").read_text(encoding="utf-8"), "# the rules\n")

    def test_a_plain_path_inside_the_vault(self):
        run_id = self.new_run()
        code, out, _ = self.run_cmd("note", run_id, "aurora/ui/console.md")
        self.assertEqual(code, 0)
        self.assertIn("new", out)
        self.assertEqual(self.state(run_id)["note_path"], "aurora/ui/console.md")

    def test_a_project_name_with_a_space(self):
        run_id = self.new_run()
        self.assertEqual(self.run_cmd("note", run_id, "Project Aurora/ui/console.md")[0], 0)

    def test_a_run_that_has_written_keeps_its_note(self):
        run_id = self.new_run()
        self.through(run_id, "record")
        code, _, err = self.run_cmd("note", run_id, "one-offs/ui/another.md")
        self.assertEqual(code, 1)
        self.assertIn("one note", err)
        self.assertEqual(self.state(run_id)["note_path"], NOTE)

    def test_two_live_runs_on_one_note_are_pointed_out(self):
        first = self.new_run("first")
        self.run_cmd("note", first, NOTE)
        second = self.new_run("second")
        code, out, _ = self.run_cmd("note", second, NOTE)
        self.assertEqual(code, 0)
        self.assertIn("run `first` is also working on this note", out)


class Intake(StudioCase):
    def test_refused_without_a_brief(self):
        run_id = self.new_run()
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("brief.md", err)
        self.assertEqual(self.state(run_id)["next_stage_index"], 0)

    def test_refused_with_an_empty_brief(self):
        run_id = self.new_run()
        self.put(run_id, "brief.md", "  \n")
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("empty", err)

    def test_refused_without_a_note(self):
        run_id = self.new_run()
        self.put(run_id, "brief.md", "A console.\n")
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("no note", err)

    def test_a_refusal_is_logged_and_changes_nothing_else(self):
        run_id = self.new_run()
        self.run_cmd("advance", run_id)
        state = self.state(run_id)
        self.assertEqual(state["completed_stages"], [])
        self.assertEqual(state["events"][-1]["event"], "refused")


class Context(StudioCase):
    """The attestation is read by column. Each level is backed its own way."""

    def at_context(self):
        run_id = self.new_run()
        self.through(run_id, "intake")
        return run_id

    def refused(self, attestation, needle):
        run_id = self.at_context()
        self.put(run_id, "attestation.md", attestation)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1, err)
        self.assertIn(needle, err)
        self.assertEqual(self.state(run_id)["completed_stages"], ["intake"])

    def passes(self, attestation):
        run_id = self.at_context()
        self.put(run_id, "attestation.md", attestation)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 0, err)

    def three_notes(self, kind="ui"):
        for name in ("aurora-lead", "harbor-dusk", "north-gate"):
            self.place(f"aurora/{kind}/{name}.md", precedent(name, kind=kind))

    # ── the table ─────────────────────────────────────────────────────────

    def test_a_clean_attestation(self):
        self.passes(self.attestation())

    def test_no_table(self):
        self.refused("# Attestation\n\nAll three gates were read and are fine.\n",
                     "no context-resolution table")

    def test_a_table_inside_a_code_fence_is_not_the_table(self):
        self.refused("```\n" + self.attestation() + "\n```\n", "no context-resolution table")

    def test_a_table_with_other_columns(self):
        self.refused("| Gate | Note |\n|---|---|\n| fixture_look fixture_colour "
                     "fixture_type | fine |\n", "no context-resolution table")

    def test_an_empty_table(self):
        self.refused("## Context resolution\n\n" + HEADER + "\nNothing to resolve.\n", "has no rows")

    def test_a_pipe_inside_a_cell(self):
        row = "| key light | fixture_look | L1 RECALLED | [[aurora-lead|Aurora]] \"x\" | resolved |"
        self.refused(self.attestation([row]), "Write a pipe inside a cell")

    # ── every needed constraint has a row ─────────────────────────────────

    def test_a_required_gate_with_no_row(self):
        self.refused(self.attestation(without=["fixture_colour"]), "no row for `fixture_colour`")

    def test_a_needed_constraint_with_no_row(self):
        need = self.env.pipeline("ui-direction")["requires_context"][0]["needs"][1]
        self.refused(self.attestation(without=[need]), f"no row for `{need}`")

    def test_gates_crammed_into_one_row(self):
        row = "| everything | fixture_look fixture_type fixture_colour | L0 | section 2 | resolved |"
        self.refused("## Context resolution\n\n" + HEADER + row + "\n", "is not a gate in the spec")

    def test_a_gate_named_only_in_prose(self):
        self.refused(self.attestation(without=["fixture_colour"],
                                      prose="\nfixture_colour was considered.\n"),
                     "no row for `fixture_colour`")

    def test_a_gate_the_spec_does_not_have(self):
        row = "| tone | house_style | L0 AUTHORED | house_style.context.md section 1 | resolved |"
        self.refused(self.attestation([row]), "`house_style` is not a gate")

    # ── nothing unresolved goes on ────────────────────────────────────────

    def test_rows_that_are_not_resolved(self):
        for level, state, why in (("L3", "UNRESOLVED", "L3 is UNRESOLVED"),
                                  ("L3", "unresolved", "L3 is UNRESOLVED"),
                                  ("L3", "open", "L3 is UNRESOLVED"),
                                  ("L3", "resolved", "L3 is UNRESOLVED"),
                                  ("UNRESOLVED", "resolved", "L3 is UNRESOLVED"),
                                  ("L0 AUTHORED", "unresolved", "its state is"),
                                  ("L0 AUTHORED", "open", "its state is"),
                                  ("L0 AUTHORED", "", "its state is"),
                                  ("L0 AUTHORED", "UNRESOLVED", "its state is"),
                                  ("probably fine", "resolved", "is not a level"),
                                  ("", "resolved", "is not a level")):
            with self.subTest(level=level, state=state):
                row = f"| imagery motifs | fixture_look | {level} | section 2 | {state} |"
                self.refused(self.attestation([row]), why)

    def test_the_word_in_prose_does_not_block(self):
        self.passes(self.attestation(prose="\nNothing here is UNRESOLVED.\n"))

    # ── L0 ────────────────────────────────────────────────────────────────

    def test_a_declared_gap_cited_as_authored(self):
        for gate in ("fixture_look", "fixture_colour"):
            gap = self.env.spec["gates"][gate]["unresolved"][0]
            for written in (f"section {gap['section']}", f"§{gap['section']}",
                            f"Section  {gap['section']}"):
                with self.subTest(gate=gate, written=written):
                    row = f"| {gap['topic']} | {gate} | L0 AUTHORED | {gate}.context.md {written} | resolved |"
                    self.refused(self.attestation([row]), "does NOT answer")

    def test_a_gap_cited_beside_a_real_section(self):
        for cited in ("section 2 and section 7", "sections 2 and 7", "§2, §7", "sections 5-7"):
            with self.subTest(cited=cited):
                row = f"| imagery | fixture_look | L0 | fixture_look.context.md {cited} | resolved |"
                self.refused(self.attestation([row]), "does NOT answer")

    def test_l0_with_no_section(self):
        row = "| grounds | fixture_look | L0 AUTHORED | fixture_look.context.md | resolved |"
        self.refused(self.attestation([row]), "as `section N`")

    def test_l0_citing_a_section_the_gate_does_not_have(self):
        row = "| grounds | fixture_look | L0 AUTHORED | fixture_look.context.md section 12 | resolved |"
        self.refused(self.attestation([row]), "no section 12")

    def test_l0_for_a_gate_nobody_has_written(self):
        row = "| wording | fixture_voice | L0 AUTHORED | fixture_voice.context.md section 2 | resolved |"
        self.refused(self.attestation([row]), "`fixture_voice` is not authored")

    # ── L1 ────────────────────────────────────────────────────────────────

    def test_recalling_a_line_a_note_really_has(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        for cited in ("[[aurora-lead]]", "[[cmd_20260901_aurora-lead]]",
                      "[[aurora-lead\\|Aurora]]", "[[Aurora-Lead]]"):
            with self.subTest(cited=cited):
                row = (f"| key light | fixture_look | L1 RECALLED | {cited} "
                       '"Key light sits  camera left." | resolved |')
                self.passes(self.attestation([row]))

    def test_recalling_from_a_note_that_does_not_exist(self):
        row = '| key light | fixture_look | L1 RECALLED | [[no-such-note]] "invented" | resolved |'
        self.refused(self.attestation([row]), "[[no-such-note]] is not a note in the vault")

    def test_recalling_a_line_the_note_does_not_have(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        row = ('| key light | fixture_look | L1 RECALLED | [[aurora-lead]] '
               '"Key light sits camera right." | resolved |')
        self.refused(self.attestation([row]), "copied, not paraphrased")

    def test_a_line_outside_decisions_in_force_is_not_a_decision(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        row = ('| key light | fixture_look | L1 RECALLED | [[aurora-lead]] '
               '"A finished piece, kept as precedent." | resolved |')
        self.refused(self.attestation([row]), "under Decisions in Force")

    def test_recalling_without_quoting(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        row = "| key light | fixture_look | L1 RECALLED | [[aurora-lead]] says so | resolved |"
        self.refused(self.attestation([row]), "in double quotes")

    def test_recalling_from_a_note_that_does_not_speak_to_the_gate(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead", gates=("fixture_colour",)))
        row = ('| key light | fixture_look | L1 RECALLED | [[aurora-lead]] '
               '"Key light sits camera left." | resolved |')
        self.refused(self.attestation([row]), "does not list `fixture_look`")

    def test_a_template_in_the_vault_is_not_a_note(self):
        self.place("_templates/aurora-lead.md", precedent("aurora-lead"))
        row = ('| key light | fixture_look | L1 RECALLED | [[aurora-lead]] '
               '"Key light sits camera left." | resolved |')
        self.refused(self.attestation([row]), "is not a note in the vault")

    # ── L2 ────────────────────────────────────────────────────────────────

    def derived(self, cites, state="PROVISIONAL", level="L2 DERIVED"):
        return f"| key light | fixture_look | {level} | {cites} | {state} |"

    def test_derived_from_three_notes_of_this_kind(self):
        self.three_notes()
        self.passes(self.attestation([self.derived("[[aurora-lead]], [[harbor-dusk]], [[north-gate]]")]))

    def test_a_derivation_presented_as_settled(self):
        self.three_notes()
        cites = "[[aurora-lead]], [[harbor-dusk]], [[north-gate]]"
        for level in ("L2 DERIVED", "L2", "DERIVED", "derived"):
            with self.subTest(level=level):
                self.refused(self.attestation([self.derived(cites, "resolved", level)]),
                             "never presented as settled")

    def test_derived_from_two_notes(self):
        self.three_notes()
        for state in ("PROVISIONAL", "provisional"):
            with self.subTest(state=state):
                self.refused(self.attestation([self.derived("[[aurora-lead]], [[harbor-dusk]]", state)]),
                             "coincidence")

    def test_derived_from_nothing(self):
        self.refused(self.attestation([self.derived("inferred")]), "cites 0 note")

    def test_the_same_note_three_times_is_one_note(self):
        self.three_notes()
        cites = "[[aurora-lead]], [[Aurora-Lead]], [[cmd_20260901_aurora-lead]]"
        self.refused(self.attestation([self.derived(cites)]), "cites 1 note")

    def test_derived_from_notes_that_do_not_exist(self):
        self.refused(self.attestation([self.derived("[[ghost-a]], [[ghost-b]], [[ghost-c]]")]),
                     "is not a note in the vault")

    def test_derived_from_notes_of_another_kind(self):
        self.three_notes(kind="brush")
        self.refused(self.attestation([self.derived("[[aurora-lead]], [[harbor-dusk]], [[north-gate]]")]),
                     "of the same kind")

    def test_only_a_derivation_is_provisional(self):
        row = ("| grounds | fixture_look | L0 AUTHORED | fixture_look.context.md section 2 "
               "| PROVISIONAL |")
        self.refused(self.attestation([row]), "only a derived constraint")

    # ── stated ────────────────────────────────────────────────────────────

    def test_stated_by_the_author(self):
        row = f"| imagery motifs | fixture_look | STATED | the author, {date.today()} | resolved |"
        self.passes(self.attestation([row]))

    def test_stated_with_no_date(self):
        row = "| imagery motifs | fixture_look | STATED | the author | resolved |"
        self.refused(self.attestation([row]), "gives the date")


class Execute(StudioCase):
    def at_execute(self):
        run_id = self.new_run()
        self.through(run_id, "recipe")
        return run_id

    def test_refused_without_a_go_ahead(self):
        run_id = self.at_execute()
        self.put(run_id, "execute_log.md", "Ran it.\n")
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("go-ahead", err)

    def test_a_go_ahead_needs_words(self):
        run_id = self.at_execute()
        code, _, err = self.run_cmd("confirm", run_id, "execute", "--words", "   ")
        self.assertEqual(code, 2)
        self.assertIn("--words is empty", err)
        self.assertEqual(self.state(run_id)["confirmations"], [])

    def test_a_go_ahead_is_for_the_current_stage_only(self):
        run_id = self.at_execute()
        code, _, err = self.run_cmd("confirm", run_id, "record", "--words", "yes")
        self.assertEqual(code, 1)
        self.assertIn("execute", err)

    def test_a_go_ahead_given_early_is_not_kept_for_later(self):
        run_id = self.new_run()
        for stage in ("execute", "record"):
            with self.subTest(stage=stage):
                self.assertEqual(self.run_cmd("confirm", run_id, stage, "--words", "yes")[0], 1)
        self.assertEqual(self.state(run_id)["confirmations"], [])

    def test_work_that_ran_ahead_of_the_go_ahead(self):
        run_id = self.at_execute()
        log = self.put(run_id, "execute_log.md", "Ran it.\n")
        an_hour_ago = time.time() - 3600
        os.utime(log, (an_hour_ago, an_hour_ago))
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "run it")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("before the confirmation", err)

    def test_the_clock_slack_is_seconds_not_minutes(self):
        self.assertLessEqual(studio_run.CLOCK_SLACK_SECONDS, 5)
        run_id = self.at_execute()
        log = self.put(run_id, "execute_log.md", "Ran it.\n")
        a_minute_ago = time.time() - 60
        os.utime(log, (a_minute_ago, a_minute_ago))
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "run it")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("before the confirmation", err)

    def test_go_ahead_then_work(self):
        run_id = self.at_execute()
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "run it")[0], 0)
        self.put(run_id, "execute_log.md", "Ran it.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        self.assertEqual(self.state(run_id)["confirmations"][0]["words"], "run it")


class Checkpoints(StudioCase):
    def test_a_plain_checkpoint_takes_no_confirmation(self):
        run_id = self.new_run()
        code, _, err = self.run_cmd("confirm", run_id, "intake", "--words", "yes")
        self.assertEqual(code, 1)
        self.assertIn("does not take a confirmation", err)

    def test_one_advance_is_one_stage(self):
        run_id = self.new_run()
        self.through(run_id, "intake")
        self.assertEqual(self.state(run_id)["next_stage_index"], 1)
        self.assertEqual(self.run_cmd("advance", run_id)[0], 1)
        self.assertEqual(self.state(run_id)["next_stage_index"], 1)


class Parking(StudioCase):
    def test_a_parked_run_does_not_advance(self):
        run_id = self.new_run()
        self.through(run_id, "intake")
        code, out, _ = self.run_cmd("park", run_id, "--constraint", "fixture_voice",
                                    "--needs", "How controls are worded.")
        self.assertEqual(code, 0)
        self.assertIn("BLOCKED on `fixture_voice`", out)
        state = self.state(run_id)
        self.assertEqual(state["status"], "parked")
        self.assertEqual(state["parked"]["stage"], "context")
        self.assertTrue((self.runs / run_id / "park.md").is_file())

        self.put(run_id, "attestation.md", self.attestation())
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("parked", err)

    def test_unparking_resumes_where_it_stopped(self):
        run_id = self.new_run()
        self.through(run_id, "intake")
        self.run_cmd("park", run_id, "--constraint", "fixture_voice", "--needs", "x")
        self.assertEqual(self.run_cmd("unpark", run_id)[0], 0)
        state = self.state(run_id)
        self.assertEqual(state["status"], "active")
        self.assertIsNone(state["parked"])
        self.put(run_id, "attestation.md", self.attestation())
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)

    def test_parking_says_what_and_what_would_resolve_it(self):
        run_id = self.new_run()
        for constraint, needs in (("fixture_voice", " "), (" ", "How controls are worded.")):
            with self.subTest(constraint=constraint, needs=needs):
                code, _, _ = self.run_cmd("park", run_id, "--constraint", constraint, "--needs", needs)
                self.assertEqual(code, 2)
        self.assertEqual(self.state(run_id)["status"], "active")

    def test_only_a_parked_run_is_unparked(self):
        run_id = self.new_run()
        self.assertEqual(self.run_cmd("unpark", run_id)[0], 1)

    def test_a_park_go_ahead_needs_a_parked_run(self):
        run_id = self.new_run()
        code, _, err = self.run_cmd("confirm", run_id, "park", "--words", "yes")
        self.assertEqual(code, 1)
        self.assertIn("not parked", err)
        self.run_cmd("park", run_id, "--constraint", "fixture_voice", "--needs", "x")
        self.assertEqual(self.run_cmd("confirm", run_id, "park", "--words", "yes")[0], 0)

    def test_parking_before_a_note_is_chosen_says_so(self):
        run_id = self.new_run()
        code, out, _ = self.run_cmd("park", run_id, "--constraint", "fixture_voice", "--needs", "x")
        self.assertEqual(code, 0)
        self.assertIn("this run has no note yet", out)


class WholeRun(StudioCase):
    def test_six_stages_to_a_note(self):
        run_id = self.new_run()
        last = self.env.stages[-1]["id"]
        self.through(run_id, last)
        state = self.state(run_id)
        self.assertEqual(state["status"], "complete")
        self.assertEqual(state["completed_stages"], [s["id"] for s in self.env.stages])
        self.assertTrue((self.vault / NOTE).is_file())
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("complete", err)
        self.assertEqual(self.state(run_id)["completed_stages"], [s["id"] for s in self.env.stages])

    def test_record_is_refused_until_the_note_is_in_the_vault(self):
        run_id = self.new_run()
        self.through(run_id, "review")
        self.put(run_id, "note_update.md", GOOD_NOTE)
        self.assertEqual(self.note_cmd("plan", run_id)[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "write it")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("not in the vault", err)

    def test_record_is_refused_if_the_vault_holds_a_different_note(self):
        run_id = self.new_run()
        self.through(run_id, "review")
        self.put(run_id, "note_update.md", GOOD_NOTE)
        self.note_cmd("plan", run_id)
        self.run_cmd("confirm", run_id, "record", "--words", "write it")
        self.note_cmd("apply", run_id, "--confirm")
        self.place(NOTE, GOOD_NOTE.replace("One search run so far.", "Edited afterwards."))
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("not the note that was previewed", err)

    def test_a_second_session_finds_its_place_from_the_run_id(self):
        run_id = self.new_run()
        self.through(run_id, "recipe")
        code, out, _ = self.run_cmd("status", run_id)
        self.assertEqual(code, 0)
        self.assertIn("execute", out)
        self.assertIn("intake, context, recipe", out)


class StageInstructions(StudioCase):
    def test_every_placeholder_is_filled_for_an_implemented_pipeline(self):
        for name, cfg in self.env.spec["pipelines"].items():
            if cfg["status"] != "implemented":
                continue
            run_id = self.new_run(f"fill-{name}", name)
            state = self.state(run_id)
            for stage in self.env.stages:
                with self.subTest(pipeline=name, stage=stage["id"]):
                    text = studio_run.fill(stage["prompt"], self.env, state)
                    self.assertNotIn("[nothing under", text)
                    self.assertNotIn("{pipeline", text)
                    self.assertNotIn("<run-id>", text)

    def test_a_missing_key_is_said_not_hidden(self):
        run_id = self.new_run()
        text = studio_run.fill("{pipeline.no_such_key}", self.env, self.state(run_id))
        self.assertIn("nothing under `no_such_key`", text)

    def test_the_stage_command_prints_the_current_stage(self):
        run_id = self.new_run()
        code, out, _ = self.run_cmd("stage", run_id)
        self.assertEqual(code, 0)
        self.assertIn("1. Intake", out)
        self.assertIn("brief.md", out)
        self.assertIn("Establish the consumer first", out)


class Facts(StudioCase):
    def test_gates_and_the_notes_that_name_them(self):
        self.place(NOTE, GOOD_NOTE)
        self.place("_Pipelines/studio.md", GOOD_NOTE)
        self.place("SCHEMA.md", GOOD_NOTE)

        run_id = self.new_run()
        code, out, _ = self.run_cmd("facts", run_id, "--json")
        self.assertEqual(code, 0)
        facts = json.loads(out)
        gates = {gate["gate"]: gate for gate in facts["gates"]}
        self.assertEqual(set(gates), {"fixture_look", "fixture_type", "fixture_colour"})
        self.assertTrue(all(gate["on_disk"] and gate["agrees"] for gate in gates.values()))
        self.assertEqual(gates["fixture_colour"]["notes_naming_it"], [NOTE])
        self.assertEqual(gates["fixture_type"]["notes_naming_it"], [])
        self.assertEqual(facts["notes_in_vault"], 1)
        self.assertTrue(gates["fixture_look"]["unresolved"])

    def test_it_prints_each_need_in_the_words_the_attestation_must_use(self):
        run_id = self.new_run()
        _, out, _ = self.run_cmd("facts", run_id)
        for need in self.env.pipeline("ui-direction")["requires_context"]:
            for wanted in need["needs"]:
                self.assertIn(f"- {wanted}", out)

    def test_a_flag_that_disagrees_with_the_disk(self):
        gate = self.env.spec["gates"]["fixture_colour"]["file"]
        (self.context / gate).unlink()
        run_id = self.new_run()
        code, out, _ = self.run_cmd("facts", run_id)
        self.assertEqual(code, 0)
        self.assertIn("MISMATCH", out)


if __name__ == "__main__":
    unittest.main()
