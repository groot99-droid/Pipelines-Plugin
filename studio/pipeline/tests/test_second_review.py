"""The holes the second review found (studio/docs/REVIEW.md), each pinned.

Every test here failed, or crashed, against the code the review read.
"""

import json
import os
import shutil
from datetime import date, timedelta

from helpers import GOOD_NOTE, HEADER, NOTE, StudioCase, content_md, precedent

TODAY = date.today().isoformat()
NEXT = "- [ ] Review the proposed palette against the contrast floors"
THREE = ("aurora-lead", "harbor-dusk", "north-gate")
CITES = ", ".join(f"[[{name}]]" for name in THREE)


class Base(StudioCase):
    def at_context(self, run_id=None):
        run_id = self.new_run(run_id)
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

    def precedents(self, kind="ui"):
        for name in THREE:
            self.place(f"aurora/{kind}/{name}.md", precedent(name, kind=kind))

    def at_record(self, rows=(), run_id=None):
        run_id = self.at_context(run_id)
        self.put(run_id, "attestation.md", self.attestation(list(rows)))
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 0, err)
        self.put(run_id, "recipe.md", "One search.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "run it")[0], 0)
        self.put(run_id, "execute_log.md", "Ran it.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        self.put(run_id, "review.md", "Fine.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        return run_id

    def write(self, run_id, text, purpose="record"):
        """Plan, confirm and apply one write. Returns (exit code, stderr)."""
        self.put(run_id, "note_update.md", text)
        code, _, err = self.note_cmd("plan", run_id, "--as", purpose)
        if code:
            return code, err
        self.assertEqual(self.run_cmd("confirm", run_id, purpose, "--words", "write it")[0], 0)
        code, _, err = self.note_cmd("apply", run_id, "--as", purpose, "--confirm")
        return code, err

    def plan(self, run_id, text, purpose="record"):
        self.put(run_id, "note_update.md", text)
        return self.note_cmd("plan", run_id, "--as", purpose)


def stated(constraint="imagery motifs", gate="fixture_look", day=None):
    return f"| {constraint} | {gate} | STATED | the author, {day or TODAY} | resolved |"


# ── high ─────────────────────────────────────────────────────────────────────

class RecordEndsWithARecordWrite(Base):
    """1. The record stage cannot be finished through a flush or a park."""

    def test_a_flush_does_not_finish_it(self):
        run_id = self.at_record()
        flushed = GOOD_NOTE.replace(NEXT, f"- [ ] Resume run `{run_id}` at record\n{NEXT}")
        self.assertEqual(self.write(run_id, flushed, "flush")[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "yes")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("last written as a flush", err)
        self.assertEqual(self.state(run_id)["status"], "active")

    def test_a_park_does_not_finish_it(self):
        run_id = self.at_record()
        self.run_cmd("park", run_id, "--constraint", "fixture_voice", "--needs", "Wording.")
        blocked = GOOD_NOTE.replace("status: in-progress", "status: blocked").replace(
            NEXT, f"- [ ] BLOCKED on `fixture_voice`: wording.\n{NEXT}")
        self.assertEqual(self.write(run_id, blocked, "park")[0], 0)
        self.assertEqual(self.run_cmd("unpark", run_id)[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "yes")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("last written as a park", err)

    def test_record_needs_its_own_go_ahead(self):
        run_id = self.at_record()
        self.assertEqual(self.plan(run_id, GOOD_NOTE)[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("`record` needs the author's go-ahead", err)

    def test_a_write_older_than_the_last_go_ahead(self):
        run_id = self.at_record()
        self.assertEqual(self.write(run_id, GOOD_NOTE)[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "and again")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("before the latest record go-ahead", err)


class OneTableAsAReaderSeesIt(Base):
    """2. The attestation is the one table a reader sees."""

    def test_two_tables(self):
        second = HEADER + "| palette | fixture_colour | L3 | nothing | UNRESOLVED |\n"
        self.refused(self.attestation() + "\n## More\n\n" + second, "2 context-resolution tables")

    def test_a_table_in_a_comment_is_not_the_table(self):
        hidden = "<!--\n" + HEADER + "\n".join(self.rows()) + "\n-->\n\n"
        shown = self.attestation(["| imagery motifs | fixture_look | L3 | nothing | UNRESOLVED |"])
        self.refused(hidden + shown, "L3 is UNRESOLVED")

    def test_only_a_table_in_a_comment(self):
        self.refused("<!--\n" + self.attestation() + "\n-->\n", "no context-resolution table")

    def test_a_comment_left_open_hides_the_table(self):
        self.refused("<!-- draft\n\n" + self.attestation(), "no context-resolution table")

    def test_a_table_indented_four_spaces_is_code(self):
        indented = "\n".join("    " + line for line in self.attestation().split("\n"))
        self.refused(indented, "no context-resolution table")

    def test_a_table_indented_three_spaces_is_a_table(self):
        lines = self.attestation().split("\n")
        self.passes("\n".join("   " + line if line.startswith("|") else line for line in lines))


class RecallingALine(Base):
    """3. An L1 quote is a real line, from one visible bullet."""

    def row(self, quote, cited="[[aurora-lead]]", state="resolved"):
        return f'| key light | fixture_look | L1 RECALLED | {cited} "{quote}" | {state} |'

    def test_a_blank_or_short_quote(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        for quote in (" ", "K", "Key light"):
            with self.subTest(quote=quote):
                self.refused(self.attestation([self.row(quote)]), "too short")

    def test_a_note_with_no_decisions(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead").split("## Decisions")[0])
        self.refused(self.attestation([self.row(" ")]), "has no Decisions in Force")

    def test_struck_out_text(self):
        self.place("aurora/ui/aurora-lead.md", precedent(
            "aurora-lead", decisions=("~~Key light sits camera left.~~ Key light sits camera right.",)))
        self.refused(self.attestation([self.row("Key light sits camera left.")]), "copied, not paraphrased")

    def test_a_quote_across_two_bullets(self):
        self.place("aurora/ui/aurora-lead.md", precedent(
            "aurora-lead", decisions=("Key light sits camera left.", "Fill stays soft and low.")))
        self.refused(self.attestation([self.row("camera left. - Fill stays soft")]),
                     "copied, not paraphrased")

    def test_a_line_in_a_comment_or_a_fence(self):
        text = (precedent("aurora-lead") + "\n<!--\n- Rim light is always cyan.\n-->\n"
                "```\n- Rim light is always cyan.\n```\n")
        self.place("aurora/ui/aurora-lead.md", text)
        self.refused(self.attestation([self.row("Rim light is always cyan.")]), "copied, not paraphrased")

    def test_every_note_cited_is_checked(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        self.place("aurora/ui/palette-note.md", precedent("palette-note", gates=("fixture_colour",)))
        line = "Key light sits camera left."
        self.refused(self.attestation([self.row(line, "[[aurora-lead]], [[ghost]]")]),
                     "[[ghost]] is not a note")
        self.refused(self.attestation([self.row(line, "[[aurora-lead]], [[palette-note]]")]),
                     "does not list `fixture_look`")

    def test_a_note_cited_by_path_or_with_its_extension(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        for cited in ("[[aurora/ui/aurora-lead]]", "[[aurora-lead.md]]", "[[aurora/ui/aurora-lead.md]]"):
            with self.subTest(cited=cited):
                self.passes(self.attestation([self.row("Key light sits camera left.", cited)]))

    def test_two_notes_with_one_file_name(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        self.place("harbor/ui/aurora-lead.md", precedent("aurora-lead").replace(
            "cmd_20260901_aurora-lead", "cmd_20260902_aurora-lead"))
        self.refused(self.attestation([self.row("Key light sits camera left.")]), "could be any of")

    def test_a_file_that_is_not_a_note(self):
        self.place("aurora/ui/aurora-lead.md",
                   "# A page\n\n## Decisions in Force\n\n- Key light sits camera left.\n")
        self.refused(self.attestation([self.row("Key light sits camera left.")]),
                     "is not a note in the vault")


class ProvisionalStaysProvisional(Base):
    """4. A PROVISIONAL decision is recalled as one, and kept as one."""

    LINE = f"PROVISIONAL, derived from {CITES}: key light sits camera left."

    def setUp(self):
        super().setUp()
        self.place("aurora/ui/ops-lead.md", precedent("ops-lead", decisions=(self.LINE,)))

    def row(self, state):
        return (f'| key light | fixture_look | L1 RECALLED | [[ops-lead]] '
                f'"key light sits camera left." | {state} |')

    def test_recalled_as_settled(self):
        self.refused(self.attestation([self.row("resolved")]), "still PROVISIONAL")

    def test_recalled_as_provisional(self):
        self.passes(self.attestation([self.row("PROVISIONAL")]))

    def test_a_settled_line_is_not_recalled_as_provisional(self):
        self.place("aurora/ui/aurora-lead.md", precedent("aurora-lead"))
        row = ('| key light | fixture_look | L1 RECALLED | [[aurora-lead]] '
               '"Key light sits camera left." | PROVISIONAL |')
        self.refused(self.attestation([row]), "is not marked PROVISIONAL")

    def test_the_record_keeps_the_marker(self):
        run_id = self.at_record([self.row("PROVISIONAL")])
        code, _, err = self.plan(run_id, GOOD_NOTE + "- Key light sits camera left.\n")
        self.assertEqual(code, 1)
        self.assertIn("was recalled from a PROVISIONAL decision", err)
        code, _, err = self.plan(run_id, GOOD_NOTE + f"- {self.LINE}\n")
        self.assertEqual(code, 0, err)

    def written_with_the_line(self):
        first = self.new_run("first-run")
        self.through(first, "record", note_text=GOOD_NOTE + f"- {self.LINE}\n")

    def test_a_later_write_cannot_drop_the_marker(self):
        self.written_with_the_line()
        second = self.new_run("second-run")
        self.through(second, "review")
        for text in (GOOD_NOTE + "- Key light sits camera left.\n", GOOD_NOTE):
            with self.subTest(text=text[-40:]):
                code, _, err = self.plan(second, text)
                self.assertEqual(code, 1)
                self.assertIn("was changed or removed", err)

    def test_the_author_stating_it_settles_it(self):
        self.written_with_the_line()
        run_id = self.at_record([stated("key light")])
        code, _, err = self.plan(run_id, GOOD_NOTE + f"- STATED {TODAY}: key light sits camera left.\n")
        self.assertEqual(code, 0, err)


# ── medium ───────────────────────────────────────────────────────────────────

class ThePlanIsForOneNote(Base):
    """5 and 6. The plan lives in state.json and names the note it is for."""

    def test_moving_the_note_drops_the_plan(self):
        run_id = self.at_record()
        self.assertEqual(self.plan(run_id, GOOD_NOTE)[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "yes")[0], 0)
        self.assertEqual(self.run_cmd("note", run_id, "one-offs/ui/elsewhere.md")[0], 0)
        code, _, err = self.note_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("there is no plan", err)
        self.assertFalse((self.vault / "one-offs/ui/elsewhere.md").exists())
        self.assertFalse((self.vault / NOTE).exists())

    def test_a_plan_for_another_path(self):
        run_id = self.at_record()
        self.assertEqual(self.plan(run_id, GOOD_NOTE)[0], 0)
        self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "yes")[0], 0)
        path = self.runs / run_id / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state["note_path"] = "one-offs/ui/elsewhere.md"
        path.write_text(json.dumps(state), encoding="utf-8")
        code, _, err = self.note_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("Plan again", err)
        self.assertFalse((self.vault / "one-offs/ui/elsewhere.md").exists())

    def test_a_refused_plan_stays_refused(self):
        run_id = self.at_record()
        self.place("aurora/ui/other.md", GOOD_NOTE)
        self.assertEqual(self.plan(run_id, GOOD_NOTE)[0], 1)
        (self.vault / "aurora/ui/other.md").unlink()
        self.run_cmd("confirm", run_id, "record", "--words", "yes")
        code, _, err = self.note_cmd("apply", run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("the plan on file was refused", err)


class TheAttestationIsKept(Base):
    """7 and 8. What context found binds every later write, however the file
    is changed afterwards."""

    def test_rewriting_or_removing_the_attestation(self):
        run_id = self.at_record([stated()])
        self.assertEqual(len(self.state(run_id)["attested"]), len(self.rows()) + 1)
        attestation = self.runs / run_id / "attestation.md"
        for change in ("rewritten", "removed"):
            with self.subTest(attestation=change):
                if change == "rewritten":
                    attestation.write_text(self.attestation(), encoding="utf-8")
                else:
                    attestation.unlink()
                code, _, err = self.plan(run_id, GOOD_NOTE)
                self.assertEqual(code, 1)
                self.assertIn("was stated by the author", err)

    def test_a_park_after_context_owes_them_too(self):
        run_id = self.at_record([stated()])
        self.run_cmd("park", run_id, "--constraint", "fixture_voice", "--needs", "Wording.")
        blocked = GOOD_NOTE.replace("status: in-progress", "status: blocked").replace(
            NEXT, f"- [ ] BLOCKED on `fixture_voice`: wording.\n{NEXT}")
        code, _, err = self.plan(run_id, blocked, "park")
        self.assertEqual(code, 1)
        self.assertIn("was stated by the author", err)


class EachRowItsOwnLine(Base):
    """9 and 10. One line per owed row, and its gate in context_brand."""

    def test_two_stated_rows_and_one_line(self):
        run_id = self.at_record([stated("imagery motifs"), stated("imagery framing")])
        one = GOOD_NOTE + f"- STATED {TODAY}: imagery motifs are line work.\n"
        code, _, err = self.plan(run_id, one)
        self.assertEqual(code, 1)
        self.assertIn("has no line of its own", err)
        code, _, err = self.plan(run_id, one + f"- STATED {TODAY}: imagery framing is square.\n")
        self.assertEqual(code, 0, err)

    def test_two_derived_rows_and_one_line(self):
        self.precedents()
        rows = [f"| {name} | fixture_look | L2 DERIVED | {CITES} | PROVISIONAL |"
                for name in ("key light", "rim light")]
        run_id = self.at_record(rows)
        one = GOOD_NOTE + f"- PROVISIONAL, derived from {CITES}: key light and rim light sit left.\n"
        code, _, err = self.plan(run_id, one)
        self.assertEqual(code, 1)
        self.assertIn("has no line of its own", err)

    def test_a_line_that_does_not_name_its_constraint(self):
        run_id = self.at_record([stated()])
        code, out, err = self.plan(run_id, GOOD_NOTE + f"- STATED {TODAY}: line work only.\n")
        self.assertEqual(code, 0, err)
        self.assertIn("does not name it", out)

    def test_three_stated_rows_of_one_day_keep_their_own_lines(self):
        rows = [stated(name, "fixture_look") for name in ("quality bar", "when to re-render", "camera grammar")]
        run_id = self.at_record(rows)
        lines = "".join(f"- STATED {TODAY}: {name}: as the author said.\n"
                        for name in ("quality bar", "when to re-render", "camera grammar"))
        code, out, err = self.plan(run_id, GOOD_NOTE + lines)
        self.assertEqual(code, 0, err)
        self.assertNotIn("does not name it", out)

    def test_the_gate_is_in_context_brand(self):
        run_id = self.at_record([stated("scale note", "fixture_type")])
        line = f"- STATED {TODAY}: scale note: the body is 13px.\n"
        code, _, err = self.plan(run_id, GOOD_NOTE + line)
        self.assertEqual(code, 1)
        self.assertIn("context_brand does not list it", err)
        listed = GOOD_NOTE.replace("[fixture_look, fixture_colour]",
                                   "[fixture_look, fixture_colour, fixture_type]")
        code, _, err = self.plan(run_id, listed + line)
        self.assertEqual(code, 0, err)


class OneRowPerNeed(Base):
    """11. A row is for a need when it is the need, not when it mentions it."""

    def test_a_row_that_only_mentions_the_need(self):
        row = "| NOT the palette | fixture_colour | L0 | fixture_colour.context.md section 2 | resolved |"
        self.refused(self.attestation([row], without=["palette"]), "no row for `palette`")

    def test_one_row_for_two_needs(self):
        row = ("| palette, semantic binding | fixture_colour | L0 | fixture_colour.context.md "
               "section 2 | resolved |")
        self.refused(self.attestation([row], without=["palette", "semantic binding"]),
                     "no row for `semantic binding`")

    def test_the_same_need_twice(self):
        row = "| palette | fixture_colour | L0 | fixture_colour.context.md section 2 | resolved |"
        self.refused(self.attestation([row]), "2 rows are for `palette`")

    def test_a_need_with_more_said_after_it(self):
        for written in ("palette: ten values", "palette (ten values)", "Palette — ten values",
                        "palette - ten values"):
            with self.subTest(written=written):
                row = f"| {written} | fixture_colour | L0 | fixture_colour.context.md section 2 | resolved |"
                self.passes(self.attestation([row], without=["palette"]))


class AnL0RowCitesItsOwnGate(Base):
    """12. An L0 row names its own gate's file, and no other gate's."""

    def test_no_file(self):
        row = "| grounds | fixture_look | L0 AUTHORED | section 2 | resolved |"
        self.refused(self.attestation([row]), "names the gate's own file")

    def test_another_gates_file(self):
        row = "| grounds | fixture_look | L0 AUTHORED | fixture_colour.context.md section 2 | resolved |"
        self.refused(self.attestation([row]), "names the gate's own file")
        row = ("| grounds | fixture_look | L0 AUTHORED | fixture_look.context.md section 2, "
               "fixture_colour.context.md section 2 | resolved |")
        self.refused(self.attestation([row]), "another gate's file")


class WhatAReaderSees(StudioCase):
    """13. The lint refuses a note a reader would read differently."""

    def errors(self, text):
        return content_md.lint(text, self.env, NOTE)[0]

    def assertRefused(self, text, needle):
        errors = self.errors(text)
        self.assertTrue(any(needle in error for error in errors),
                        f"no error mentioning {needle!r} in {errors}")

    def test_a_heading_off_the_margin_or_with_a_tab(self):
        for heading in (" ## Timeline", "   ## Timeline", "##\tTimeline"):
            with self.subTest(heading=heading):
                self.assertRefused(GOOD_NOTE.replace("## Timeline", heading), "off the margin")

    def test_a_heading_made_by_underlining(self):
        for rule in ("--------", "========"):
            with self.subTest(rule=rule):
                self.assertRefused(GOOD_NOTE.replace("## Timeline", f"Timeline\n{rule}"), "underlines it")

    def test_a_title_that_differs_only_in_case(self):
        self.assertRefused(GOOD_NOTE.replace("## Timeline", "## timeline"), "is written `## Timeline`")

    def test_a_fence_or_a_comment_left_open(self):
        self.assertRefused(GOOD_NOTE + "\n```\nstray\n", "never closed")
        self.assertRefused(GOOD_NOTE + "\n<!-- stray\n", "never closed")

    def test_inline_code_at_the_start_of_a_line_opens_no_fence(self):
        text = GOOD_NOTE.replace("A design direction", "```--json``` is the flag. A design direction")
        self.assertEqual(self.errors(text), [])

    def test_text_before_the_first_entry(self):
        self.assertRefused(GOOD_NOTE.replace("## Timeline\n", "## Timeline\n\nSome notes.\n"),
                           "before its first entry")

    def test_a_timeline_written_as_bullets(self):
        text = GOOD_NOTE.replace("### 2026-09-28 · ui-direction · ops-console-aaaaaa",
                                 "- 2026-09-28 · ui-direction · ops-console-aaaaaa")
        self.assertRefused(text, "before its first entry")

    def test_a_line_that_reads_like_an_entry(self):
        for line in ("#### 2026-09-29 · ui-direction · x", "###2026-09-29 · x", "##### 2026-09-29"):
            with self.subTest(line=line):
                text = GOOD_NOTE.replace("## Method", f"{line}\nMore.\n\n## Method")
                self.assertRefused(text, "reads like a Timeline entry")

    def test_a_fenced_entry_heading_is_not_an_entry(self):
        text = GOOD_NOTE.replace("## Method", "```\n### 2026-09-29 · pasted\n```\n\n## Method")
        self.assertEqual(self.errors(text), [])
        self.assertEqual(len(content_md.timeline_entries(text.split("---\n", 2)[2])), 1)


class NotUtf8(Base):
    """14. A file that is not UTF-8 is named, never a traceback."""

    def latin(self):
        path = self.vault / "aurora/ui/latin.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(GOOD_NOTE.replace("Ops console", "Café console")
                         .replace("ops-console", "latin").encode("cp1252"))

    def test_a_note_in_the_vault(self):
        self.latin()
        run_id = self.new_run()
        code, _, err = self.run_cmd("facts", run_id)
        self.assertEqual(code, 0, err)
        self.assertIn("not UTF-8", err)
        code, out, _ = self.note_cmd("lint", "--all")
        self.assertEqual(code, 1)
        self.assertIn("not UTF-8", out)

    def test_a_plan_beside_it(self):
        self.latin()
        run_id = self.at_record()
        code, _, err = self.plan(run_id, GOOD_NOTE)
        self.assertEqual(code, 0, err)

    def test_a_stage_output_in_utf16(self):
        run_id = self.at_context()
        (self.runs / run_id / "attestation.md").write_bytes(self.attestation().encode("utf-16"))
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 2)
        self.assertIn("not UTF-8", err)
        self.assertNotIn("Traceback", err)


class GoingBack(Base):
    """15. `back` takes a run one stage back and clears what that undoes."""

    def test_it_needs_a_reason(self):
        run_id = self.at_context()
        code, _, err = self.run_cmd("back", run_id, "--why", "  ")
        self.assertEqual(code, 2)
        self.assertIn("--why is empty", err)

    def test_nothing_comes_before_the_first_stage(self):
        run_id = self.new_run()
        code, _, err = self.run_cmd("back", run_id, "--why", "redo")
        self.assertEqual(code, 1)
        self.assertIn("first stage", err)

    def test_back_to_execute_needs_a_new_go_ahead_and_new_work(self):
        run_id = self.new_run()
        self.through(run_id, "execute")
        code, out, err = self.run_cmd("back", run_id, "--why", "the search matched the wrong category")
        self.assertEqual(code, 0, err)
        state = self.state(run_id)
        self.assertEqual(state["completed_stages"], ["intake", "context", "recipe"])
        self.assertEqual(self.env.stages[state["next_stage_index"]]["id"], "execute")
        self.assertEqual([c["what"] for c in state["confirmations"]], [])
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("needs the author's go-ahead", err)
        log = self.runs / run_id / "execute_log.md"
        os.utime(log, (log.stat().st_mtime - 60, log.stat().st_mtime - 60))
        self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "run it again")[0], 0)
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("before the confirmation", err)
        self.put(run_id, "execute_log.md", "Ran it again. Exit 0.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)

    def test_back_to_context_drops_what_it_kept(self):
        run_id = self.new_run()
        self.through(run_id, "context")
        self.assertTrue(self.state(run_id)["attested"])
        self.assertEqual(self.run_cmd("back", run_id, "--why", "a row was wrong")[0], 0)
        state = self.state(run_id)
        self.assertIsNone(state["attested"])
        self.assertEqual(self.env.stages[state["next_stage_index"]]["id"], "context")

    def test_a_complete_or_parked_run_stays_where_it_is(self):
        done = self.new_run()
        self.through(done, "record")
        code, _, err = self.run_cmd("back", done, "--why", "x")
        self.assertEqual(code, 1)
        self.assertIn("complete", err)
        parked = self.at_context()
        self.run_cmd("park", parked, "--constraint", "fixture_voice", "--needs", "x")
        code, _, err = self.run_cmd("back", parked, "--why", "x")
        self.assertEqual(code, 1)
        self.assertIn("parked", err)


class LinksAndKeys(StudioCase):
    """17. More shapes of a link or a key that is a credential."""

    def test_more_shapes(self):
        for text in ("sk-proj-" + "a" * 40,
                     "bucket.s3.amazonaws.com/a.png?X-Amz-Signature=abc",
                     "https://files.example.com/a.png?X%2DAmz%2DSignature=abc",
                     "https://files.example.com/a.png?%73ig=abc",
                     "https://files.example.com/it's/a.png?sig=abc",
                     "drive.google.com/file/d/1AbC/view?usp=sharing",
                     "www.dropbox.com/s/abc123/file.png"):
            with self.subTest(text=text[:40]):
                errors = content_md.lint(GOOD_NOTE + f"\n## Links\n\n- {text}\n", self.env, NOTE)[0]
                self.assertTrue(any("credential" in error for error in errors), errors)


# ── low ──────────────────────────────────────────────────────────────────────

class SectionsCited(Base):
    def test_every_section_in_a_range(self):
        row = "| palette extra | fixture_colour | L0 | fixture_colour.context.md section 2-5 | resolved |"
        self.refused(self.attestation([row]), "does NOT answer")

    def test_the_plural(self):
        row = "| grounds | fixture_look | L0 | fixture_look.context.md sections 2 and 3 | resolved |"
        self.passes(self.attestation([row]))

    def test_a_section_named_inside_a_quote_is_not_cited(self):
        row = ('| grounds | fixture_look | L0 | fixture_look.context.md section 2: "Product '
               'work built for a client is not bound by this — see §7" | resolved |')
        self.passes(self.attestation([row]))

    def test_a_level_in_bold(self):
        rows = [row.replace("L0 AUTHORED", "**L0 AUTHORED**") for row in self.rows()]
        self.passes("## Context resolution\n\n" + HEADER + "\n".join(rows) + "\n")

    def test_a_level_that_cannot_be_read_is_not_told_to_park(self):
        row = "| grounds | fixture_look | probably fine | fixture_look.context.md section 2 | resolved |"
        run_id = self.at_context()
        self.put(run_id, "attestation.md", self.attestation([row]))
        code, _, err = self.run_cmd("advance", run_id)
        self.assertEqual(code, 1)
        self.assertIn("is not a level", err)
        self.assertNotIn("park the run", err)


class StatedDates(Base):
    def test_a_real_day_in_this_run(self):
        later = (date.today() + timedelta(days=3)).isoformat()
        for day, why in (("1999-99-99", "is not a date"), (later, "after today"),
                         ("2020-01-01", "before this run began")):
            with self.subTest(day=day):
                self.refused(self.attestation([stated(day=day)]), why)


class Derived(Base):
    def test_cited_by_id_and_recorded_by_name(self):
        self.precedents()
        ids = ", ".join(f"[[cmd_20260901_{name}]]" for name in THREE)
        run_id = self.at_record([f"| key light | fixture_look | L2 DERIVED | {ids} | PROVISIONAL |"])
        code, _, err = self.plan(
            run_id, GOOD_NOTE + f"- PROVISIONAL, derived from {CITES}: key light sits camera left.\n")
        self.assertEqual(code, 0, err)


class NotePathsHold(Base):
    def test_more_names_that_are_not_a_note(self):
        self.place("blocked/ui", "a file, not a folder\n")
        run_id = self.new_run()
        for path in ("aurora/ui/nul .md", "aurora/ui\n/x.md", "aurora/ui/x\n.md", "CLAUDE.md/ui/x.md",
                     "aurora/ui/" + "a" * 300 + ".md", "blocked/ui/x.md", "aurora/brush/x.md"):
            with self.subTest(path=path[:40]):
                code, _, err = self.run_cmd("note", run_id, path)
                self.assertEqual(code, 2, err)
                self.assertIsNone(self.state(run_id)["note_path"])

    def test_a_file_system_error_is_an_error_not_a_crash(self):
        shutil.rmtree(self.runs)
        self.runs.write_text("not a folder\n", encoding="utf-8")
        code, _, err = self.run_cmd("new", "--pipeline", "ui-direction", "--title", "x", "--run-id", "x")
        self.assertEqual(code, 2)
        self.assertNotIn("Traceback", err)


class VaultScans(Base):
    def test_a_folder_named_like_a_note(self):
        (self.vault / "aurora/ui/folder.md").mkdir(parents=True)
        self.place(NOTE, GOOD_NOTE)
        self.assertEqual(self.note_cmd("lint", "--all")[0], 0)
        self.assertEqual(self.run_cmd("facts", self.new_run())[0], 0)

    def test_a_gate_written_as_a_link(self):
        text = GOOD_NOTE.replace("context_brand: [fixture_look, fixture_colour]",
                                 "context_brand: [[fixture_look]]")
        errors = content_md.lint(text, self.env, NOTE)[0]
        self.assertTrue(any("not a name" in error for error in errors), errors)

    def test_a_field_written_twice(self):
        text = GOOD_NOTE.replace("status: in-progress", "status: in-progress\nstatus: complete")
        errors = content_md.lint(text, self.env, NOTE)[0]
        self.assertTrue(any("written twice" in error for error in errors), errors)

    def test_other_list_markers_a_fenced_placeholder_and_closing_hashes(self):
        for text in (GOOD_NOTE.replace("- [ ] Review", "* [ ] Review"),
                     GOOD_NOTE.replace("- [ ] Review", "+ [ ] Review"),
                     GOOD_NOTE.replace("status: in-progress", "status: blocked")
                              .replace("- [ ] Review", "* [ ] Review"),
                     GOOD_NOTE.replace('search.py "internal', 'search.py "{{query}} internal'),
                     GOOD_NOTE.replace("## Overview", "## Overview ##")):
            with self.subTest(text=text[:0]):
                self.assertEqual(content_md.lint(text, self.env, NOTE)[0], [])


class Runs(Base):
    def test_a_flush_names_its_own_run_not_a_longer_one(self):
        run_id = self.new_run("k-1")
        self.through(run_id, "review")
        code, _, err = self.plan(run_id, GOOD_NOTE.replace(NEXT, f"- [ ] Resume run `k-12` at record\n{NEXT}"),
                                 "flush")
        self.assertEqual(code, 1)
        self.assertIn("must name the run and the stage", err)

    def test_status_lists_a_broken_run(self):
        run_id = self.new_run()
        (self.runs / run_id / "state.json").write_text("{broken", encoding="utf-8")
        code, out, _ = self.run_cmd("status")
        self.assertEqual(code, 0)
        self.assertIn("broken", out)
        self.assertIn(run_id, out)
        code, out, _ = self.run_cmd("status", "--json")
        self.assertEqual([run["status"] for run in json.loads(out)], ["broken"])

    def test_a_complete_run_on_the_same_note_is_not_a_warning(self):
        first = self.new_run("first")
        self.through(first, "record")
        second = self.new_run("second")
        code, out, _ = self.run_cmd("note", second, NOTE)
        self.assertEqual(code, 0)
        self.assertNotIn("also working", out)

    def test_parking_a_complete_run(self):
        run_id = self.new_run()
        self.through(run_id, "record")
        code, _, err = self.run_cmd("park", run_id, "--constraint", "fixture_voice", "--needs", "x")
        self.assertEqual(code, 1)
        self.assertIn("complete", err)


# ── the spec and the stage text ──────────────────────────────────────────────

class StageText(Base):
    def test_a_stage_can_say_what_comes_after_it(self):
        record = next(stage for stage in self.env.stages if stage["id"] == "record")
        self.assertTrue(record.get("then"))
        run_id = self.new_run()
        self.through(run_id, "review")
        _, out, _ = self.run_cmd("stage", run_id)
        self.assertIn(" ".join(record["then"].split()), out)

    def test_facts_prints_what_is_open(self):
        cfg = self.env.pipeline("ui-direction")
        self.assertTrue(cfg.get("open"))
        _, out, _ = self.run_cmd("facts", self.new_run())
        for item in cfg["open"]:
            self.assertIn(" ".join(item.split()), out)

    def test_the_stage_notes_name_real_paths(self):
        run_id = self.new_run()
        self.through(run_id, "context")
        _, out, _ = self.run_cmd("stage", run_id)
        for key in ("contract", "guide", "router"):
            self.assertIn(self.env.pipeline("ui-direction")["executes_through"][key], out)
