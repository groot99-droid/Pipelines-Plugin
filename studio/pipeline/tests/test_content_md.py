"""The note writer: what it accepts, what it refuses, and when it writes."""

import json
import unittest
from datetime import date

from helpers import GOOD_NOTE, NOTE, PIPELINE, StudioCase, content_md, precedent

NEXT = "- [ ] Review the proposed palette against the contrast floors"


class Lint(StudioCase):
    def errors(self, text, path=NOTE):
        return content_md.lint(text, self.env, path)[0]

    def assertRefused(self, text, needle):
        errors = self.errors(text)
        self.assertTrue(any(needle in error for error in errors),
                        f"no error mentioning {needle!r} in {errors}")

    def test_a_good_note(self):
        errors, warnings = content_md.lint(GOOD_NOTE, self.env, NOTE)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_no_frontmatter(self):
        self.assertRefused("## Overview\n\nA thing.\n", "no frontmatter")

    def test_frontmatter_that_is_not_a_set_of_fields(self):
        for front in ("- a\n- b", "just a sentence", "id: [unclosed"):
            with self.subTest(front=front):
                errors = self.errors(f"---\n{front}\n---\n\n## Overview\n\nA thing.\n")
                self.assertEqual(len(errors), 1)
                self.assertIn("frontmatter", errors[0])

    def test_windows_line_endings_and_a_byte_order_mark(self):
        self.assertEqual(self.errors(GOOD_NOTE.replace("\n", "\r\n")), [])
        self.assertEqual(self.errors("\ufeff" + GOOD_NOTE), [])

    def test_each_required_field(self):
        for field in self.env.spec["content_md"]["required"]:
            with self.subTest(field=field):
                lines = [line for line in GOOD_NOTE.splitlines()
                         if not line.startswith(f"{field}:")]
                self.assertRefused("\n".join(lines) + "\n", f"`{field}` is required")

    def test_vocabularies(self):
        self.assertRefused(GOOD_NOTE.replace("kind: ui", "kind: poem"), "`kind` is `poem`")
        self.assertRefused(GOOD_NOTE.replace("status: in-progress", "status: parked"),
                           "`status` is `parked`")
        self.assertRefused(GOOD_NOTE.replace("type: content-md", "type: note"), "`type` must be")

    def test_the_id(self):
        for bad in ("ops-console", "cmd_2026_ops", "cmd_20260928_Ops_Console", "cmd_20260928_"):
            with self.subTest(id=bad):
                self.assertRefused(GOOD_NOTE.replace("cmd_20260928_ops-console", bad), "`id` is")

    def test_dates(self):
        self.assertRefused(GOOD_NOTE.replace("created: 2026-09-28", "created: last week"),
                           "`created` is not a date")
        self.assertRefused(GOOD_NOTE.replace("created: 2026-09-28", "created: 2026-13-45"),
                           "the frontmatter does not parse")
        self.assertRefused(GOOD_NOTE.replace("created: 2026-09-28", 'created: "2026-13-45"'),
                           "`created` is not a date")
        self.assertRefused(GOOD_NOTE.replace("updated: 2026-09-28", "updated: 2026-09-01"),
                           "is before `created`")

    def test_comments_in_the_frontmatter_are_not_part_of_the_value(self):
        text = GOOD_NOTE.replace("kind: ui", "kind: ui          # see Kinds")
        self.assertEqual(self.errors(text), [])

    def test_a_title_with_a_colon(self):
        self.assertEqual(self.errors(GOOD_NOTE.replace("title: Ops console",
                                                       'title: "Ops: the console"')), [])

    def test_a_gate_the_spec_does_not_have(self):
        self.assertRefused(GOOD_NOTE.replace("[fixture_look, fixture_colour]", "[house_style]"),
                           "`context_brand` names `house_style`")

    def test_a_list_field_written_as_a_word(self):
        self.assertRefused(GOOD_NOTE.replace("tags: [ui]", "tags: ui"), "`tags` must be a list")

    # ── the first screenful ───────────────────────────────────────────────

    def test_overview_comes_first(self):
        swapped = GOOD_NOTE.replace("## Overview", "## TEMP").replace("## Next Steps", "## Overview") \
                           .replace("## TEMP", "## Next Steps")
        errors = self.errors(swapped)
        self.assertTrue(any("must be the first section" in e for e in errors), errors)
        self.assertTrue(any("out of order" in e for e in errors), errors)

    def test_next_steps_comes_second(self):
        text = GOOD_NOTE.replace(f"## Next Steps\n\n{NEXT}\n\n", "")
        text = text.replace("## Decisions in Force", "## Next Steps\n\n- [ ] Review\n\n"
                            "## Decisions in Force")
        errors = self.errors(text)
        self.assertTrue(any("must come second" in e for e in errors), errors)

    def test_text_before_the_first_section(self):
        long = "\n".join(f"Paragraph {n} of preamble." for n in range(50))
        self.assertRefused(GOOD_NOTE.replace("## Overview", long + "\n\n## Overview", 1),
                           "text before the first section")
        self.assertRefused(GOOD_NOTE.replace("## Overview", "# Ops console\n\nSome notes.\n\n"
                                             "## Overview", 1), "text before the first section")

    def test_a_title_line_may_come_first(self):
        text = GOOD_NOTE.replace("## Overview", "# Ops console\n\n<!-- a comment -->\n\n## Overview", 1)
        self.assertEqual(self.errors(text), [])

    def test_an_empty_overview(self):
        text = GOOD_NOTE.replace("A design direction for an operations console. "
                                 "One search run so far.", "<!-- to be written -->")
        self.assertRefused(text, "`## Overview` is required")

    def test_a_finished_note_may_have_no_next_step(self):
        for status in self.env.spec["content_md"]["next_steps_optional_when"]:
            with self.subTest(status=status):
                text = GOOD_NOTE.replace("status: in-progress", f"status: {status}").replace(
                    f"## Next Steps\n\n{NEXT}\n\n", "")
                self.assertEqual(self.errors(text), [])

    def test_an_unfinished_note_may_not(self):
        for status in ("seed", "in-progress", "blocked"):
            with self.subTest(status=status):
                text = GOOD_NOTE.replace("status: in-progress", f"status: {status}").replace(
                    f"## Next Steps\n\n{NEXT}\n\n", "")
                self.assertRefused(text, "`## Next Steps` is required")

    def test_a_blocked_note_leads_with_its_blocker(self):
        blocked = GOOD_NOTE.replace("status: in-progress", "status: blocked")
        self.assertEqual(self.errors(blocked), [])
        done = blocked.replace("- [ ] Review", "- [x] Review")
        self.assertRefused(done, "the first item under Next Steps must be the blocker")

    def test_next_steps_are_checkboxes(self):
        self.assertRefused(GOOD_NOTE.replace(NEXT, "Review the palette some time."),
                           "holds no checkbox items")

    # ── sections ──────────────────────────────────────────────────────────

    def test_a_heading_inside_a_code_fence_is_not_a_section(self):
        body = GOOD_NOTE.split("---\n", 2)[2]
        titles = [title for title, _ in content_md.sections(body)]
        self.assertEqual(titles, ["Overview", "Next Steps", "Timeline", "Method",
                                  "Decisions in Force"])

    def test_fences_of_other_shapes(self):
        for opener, closer in (("~~~", "~~~"), ("````", "````"), ("```python", "```")):
            with self.subTest(fence=opener):
                text = GOOD_NOTE.replace("```\nsearch.py", f"{opener}\nsearch.py").replace(
                    "inside a code fence\n```", f"inside a code fence\n{closer}")
                self.assertEqual(self.errors(text), [])

    def test_a_shorter_fence_inside_a_longer_one_does_not_close_it(self):
        text = GOOD_NOTE.replace("```\nsearch.py", "````\n```\nsearch.py").replace(
            "inside a code fence\n```", "inside a code fence\n```\n## Timeline\n````")
        self.assertEqual(self.errors(text), [])

    def test_a_section_twice(self):
        self.assertRefused(GOOD_NOTE + "\n## Method\n\nAgain.\n", "more than once")

    # ── the timeline ──────────────────────────────────────────────────────

    def test_timeline_headings(self):
        self.assertRefused(GOOD_NOTE.replace("### 2026-09-28 · ui-direction", "### Monday"),
                           "It must read")
        self.assertRefused(GOOD_NOTE.replace("### 2026-09-28 · ui-direction · ops-console-aaaaaa",
                                             "### 2026-09-28"), "It must read")

    def test_timeline_is_oldest_first(self):
        text = GOOD_NOTE.replace("## Method", "### 2026-09-01 · ui-direction · earlier\nOlder.\n\n"
                                 "## Method")
        self.assertRefused(text, "oldest first")

    def test_entries_are_read_one_by_one(self):
        text = GOOD_NOTE.replace("## Method", "### 2026-09-29 · ui-direction · later\nSecond.\n\n"
                                 "## Method")
        entries = content_md.timeline_entries(text.split("---\n", 2)[2])
        self.assertEqual(len(entries), 2)
        self.assertTrue(entries[0].startswith("### 2026-09-28"))
        self.assertTrue(entries[0].endswith("Analytics Dashboard."))
        self.assertEqual(entries[1], "### 2026-09-29 · ui-direction · later\nSecond.")

    # ── decisions ─────────────────────────────────────────────────────────

    def test_a_provisional_decision_names_its_sources(self):
        good = "- PROVISIONAL, derived from [[a]], [[b]], [[c]]: key light sits camera left."
        self.assertEqual(self.errors(GOOD_NOTE + good + "\n"), [])
        for bad in ("- PROVISIONAL: key light sits camera left.",
                    "- PROVISIONAL, from [[a]] and [[b]]: key light sits camera left.",
                    "- PROVISIONAL, from [[a]], [[a]], [[A]]: key light sits camera left."):
            with self.subTest(line=bad):
                self.assertRefused(GOOD_NOTE + bad + "\n", "PROVISIONAL decision cites")

    # ── what never goes in a note ─────────────────────────────────────────

    def test_links_that_are_credentials(self):
        for link in ("https://bucket.s3.amazonaws.com/a.png?X-Amz-Signature=abc&X-Amz-Expires=60",
                     "HTTPS://bucket.s3.amazonaws.com/a.png?X-Amz-Signature=abc",
                     "https://files.example.com/a.png?sig=abc123",
                     "https://share.example.com/v/9?token=abc",
                     "https://acct.blob.core.windows.net/c/a.png?sv=2022&sig=abc",
                     "https://storage.googleapis.com/b/a.png?X-Goog-Signature=abc",
                     "https://drive.google.com/file/d/1AbC/view?usp=sharing",
                     "https://docs.google.com/document/d/1AbC/edit?usp=sharing",
                     "https://www.dropbox.com/s/abc123/file.png?dl=0",
                     "https://www.dropbox.com/scl/fi/abc/file.png?rlkey=x",
                     "https://app.box.com/s/abcdef123456",
                     "https://contoso.sharepoint.com/:i:/g/personal/x/abc",
                     "https://1drv.ms/u/s!abc"):
            with self.subTest(link=link):
                self.assertRefused(GOOD_NOTE + f"\n## Links\n\n- {link}\n", "is a credential")

    def test_a_plain_link_is_fine(self):
        for link in ("https://fonts.google.com/specimen/JetBrains+Mono?query=mono",
                     "https://www.w3.org/TR/WCAG22/#contrast-minimum",
                     "https://docs.google.com/document/d/1AbC/edit",
                     "https://github.com/owner/repo/blob/main/README.md?plain=1"):
            with self.subTest(link=link):
                self.assertEqual(self.errors(GOOD_NOTE + f"\n## Links\n\n- {link}\n"), [])

    def test_credentials(self):
        for secret in ("sk-ant-" + "a" * 24, "sk-" + "b" * 24, "gsk_" + "c" * 20,
                       "AIza" + "d" * 30, "ghp_" + "e" * 30, "AKIA" + "F" * 16,
                       "xoxb-" + "1" * 12 + "-abc", "eyJ" + "g" * 12 + ".eyJ" + "h" * 12 + ".sig12",
                       "-----BEGIN RSA PRIVATE KEY-----"):
            with self.subTest(shape=secret[:6]):
                self.assertRefused(GOOD_NOTE + f"\n## Links\n\n- {secret}\n",
                                   "shaped like a credential")

    def test_a_template_placeholder_left_in(self):
        self.assertRefused(GOOD_NOTE.replace("2026-09-28 · ui-direction", "{{date:YYYY-MM-DD}} · x"),
                           "template placeholder")

    def test_the_folder_and_the_kind_disagree(self):
        _, warnings = content_md.lint(GOOD_NOTE, self.env, "one-offs/brush/ops-console.md")
        self.assertTrue(any("sits in `brush/`" in w for w in warnings), warnings)
        _, warnings = content_md.lint(GOOD_NOTE, self.env, "ops-console.md")
        self.assertTrue(any("the vault root" in w for w in warnings), warnings)

    def test_the_template_in_the_vault_is_not_a_finished_note(self):
        template = (PIPELINE.parent / "vault/_templates/content-md.md").read_text(encoding="utf-8")
        self.assertTrue(self.errors(template))


class PlanAndApply(StudioCase):
    def setUp(self):
        super().setUp()
        self.run_id = self.new_run()
        self.through(self.run_id, "review")
        self.note = self.vault / NOTE

    def propose(self, text):
        self.put(self.run_id, "note_update.md", text)

    def confirm(self, what="record"):
        self.assertEqual(self.run_cmd("confirm", self.run_id, what, "--words", "write it")[0], 0)

    def flushed(self):
        return GOOD_NOTE.replace(NEXT, f"- [ ] Resume run `{self.run_id}` at record.\n{NEXT}")

    def test_a_plan_writes_nothing_to_the_vault(self):
        self.propose(GOOD_NOTE)
        code, out, _ = self.note_cmd("plan", self.run_id)
        self.assertEqual(code, 0)
        self.assertFalse(self.note.exists())
        self.assertFalse((self.vault / "one-offs").exists())
        plan = (self.runs / self.run_id / "record_plan.md").read_text(encoding="utf-8")
        self.assertIn("ready for the author", plan)
        self.assertIn("+## Overview", plan)

    def test_a_plan_for_a_bad_note_is_refused_and_says_why(self):
        self.propose(GOOD_NOTE.replace("kind: ui", "kind: poem"))
        code, _, err = self.note_cmd("plan", self.run_id)
        self.assertEqual(code, 1)
        self.assertIn("`kind` is `poem`", err)
        plan = (self.runs / self.run_id / "record_plan.md").read_text(encoding="utf-8")
        self.assertIn("REFUSED", plan)
        self.assertNotIn("To write it", plan)

    def test_a_refused_plan_cannot_be_applied(self):
        self.propose(GOOD_NOTE.replace("kind: ui", "kind: poem"))
        self.note_cmd("plan", self.run_id)
        self.confirm()
        self.propose(GOOD_NOTE.replace("kind: ui", "kind: poem"))
        code, _, err = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("the plan on file was refused", err)
        self.assertFalse(self.note.exists())

    def test_apply_without_a_plan(self):
        self.propose(GOOD_NOTE)
        code, _, err = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("no plan", err)

    def test_a_plan_file_written_by_hand_is_not_a_plan(self):
        """The plan lives in state.json. A file beside it proves nothing."""
        self.propose(GOOD_NOTE)
        self.confirm()
        self.put(self.run_id, "record_plan.json", json.dumps({
            "purpose": "record", "ok": True, "planned_at_epoch": 0,
            "proposed_sha": content_md.digest(GOOD_NOTE), "existing_sha": None}))
        code, _, err = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("there is no plan", err)
        self.assertFalse(self.note.exists())

    def test_a_plan_leaves_no_file_that_could_be_trusted(self):
        self.propose(GOOD_NOTE)
        self.note_cmd("plan", self.run_id)
        self.assertFalse((self.runs / self.run_id / "record_plan.json").exists())
        self.assertTrue(self.state(self.run_id)["plan"]["ok"])

    def test_apply_without_confirm_is_a_dry_run(self):
        self.propose(GOOD_NOTE)
        self.note_cmd("plan", self.run_id)
        self.confirm()
        code, out, _ = self.note_cmd("apply", self.run_id)
        self.assertEqual(code, 0)
        self.assertIn("DRY RUN", out)
        self.assertFalse(self.note.exists())

    def test_apply_without_a_recorded_go_ahead(self):
        self.propose(GOOD_NOTE)
        self.note_cmd("plan", self.run_id)
        code, _, err = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("no go-ahead", err)
        self.assertFalse(self.note.exists())

    def test_a_go_ahead_given_before_the_plan_does_not_count(self):
        self.propose(GOOD_NOTE)
        self.confirm()
        self.note_cmd("plan", self.run_id)
        code, _, err = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("older than the plan", err)
        self.assertFalse(self.note.exists())

    def test_a_note_changed_after_the_plan(self):
        self.propose(GOOD_NOTE)
        self.note_cmd("plan", self.run_id)
        self.confirm()
        self.propose(GOOD_NOTE.replace("One search run so far.", "Two search runs so far."))
        code, _, err = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("has not seen this version", err)
        self.assertFalse(self.note.exists())

    def test_a_go_ahead_for_one_purpose_is_not_a_go_ahead_for_another(self):
        self.propose(self.flushed())
        self.assertEqual(self.note_cmd("plan", self.run_id, "--as", "flush")[0], 0)
        self.confirm("record")
        code, _, err = self.note_cmd("apply", self.run_id, "--as", "flush", "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("no go-ahead is recorded for `flush`", err)
        self.assertFalse(self.note.exists())

    def test_a_plan_made_for_one_purpose_is_not_applied_as_another(self):
        self.propose(self.flushed())
        self.note_cmd("plan", self.run_id, "--as", "flush")
        self.confirm("record")
        code, _, err = self.note_cmd("apply", self.run_id, "--as", "record", "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("Plan again", err)
        self.assertFalse(self.note.exists())

    def test_plan_confirm_apply(self):
        self.propose(GOOD_NOTE.rstrip("\n"))
        self.assertEqual(self.note_cmd("plan", self.run_id)[0], 0)
        self.confirm()
        code, out, _ = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 0)
        self.assertEqual(self.note.read_text(encoding="utf-8"), GOOD_NOTE)
        self.assertNotIn(b"\r\n", self.note.read_bytes())
        self.assertEqual(list(self.note.parent.glob("*.tmp")), [])
        self.assertEqual(self.run_cmd("advance", self.run_id)[0], 0)

    def test_an_id_another_note_already_has(self):
        self.place("aurora/ui/other.md", GOOD_NOTE)
        self.propose(GOOD_NOTE)
        code, _, err = self.note_cmd("plan", self.run_id)
        self.assertEqual(code, 1)
        self.assertIn("already has", err)

    # ── stopping partway ──────────────────────────────────────────────────

    def test_a_flush_names_the_run_and_the_stage(self):
        for first in (NEXT, f"- [ ] Resume run `{self.run_id}`",
                      "- [ ] Resume at record", f"- [ ] Resume run `{self.run_id}` at recording"):
            with self.subTest(first=first):
                self.propose(GOOD_NOTE.replace(NEXT, f"{first}\n{NEXT}"))
                code, _, err = self.note_cmd("plan", self.run_id, "--as", "flush")
                self.assertEqual(code, 1)
                self.assertIn("must name the run and the stage", err)

    def test_a_flush_does_not_advance_the_run(self):
        self.propose(self.flushed())
        self.assertEqual(self.note_cmd("plan", self.run_id, "--as", "flush")[0], 0)
        self.confirm("flush")
        self.assertEqual(self.note_cmd("apply", self.run_id, "--as", "flush", "--confirm")[0], 0)
        self.assertTrue(self.note.is_file())
        self.assertEqual(self.state(self.run_id)["completed_stages"][-1], "review")

    def test_a_second_session_finds_its_place_from_the_note(self):
        self.propose(self.flushed())
        self.note_cmd("plan", self.run_id, "--as", "flush")
        self.confirm("flush")
        self.note_cmd("apply", self.run_id, "--as", "flush", "--confirm")
        first = content_md.first_step(self.note.read_text(encoding="utf-8"))
        self.assertIn(self.run_id, first)
        self.assertIn("record", first)

    # ── parking ───────────────────────────────────────────────────────────

    def blocked(self, first):
        return GOOD_NOTE.replace("status: in-progress", "status: blocked").replace(
            NEXT, f"{first}\n{NEXT}")

    def test_a_parked_note_needs_a_parked_run(self):
        self.propose(self.blocked("- [ ] BLOCKED on `fixture_voice`: how controls are worded."))
        code, _, err = self.note_cmd("plan", self.run_id, "--as", "park")
        self.assertEqual(code, 1)
        self.assertIn("is not parked", err)

    def test_a_parked_note_is_blocked_and_names_the_constraint(self):
        self.run_cmd("park", self.run_id, "--constraint", "fixture_voice", "--needs", "Wording.")
        self.propose(GOOD_NOTE.replace(NEXT, "- [ ] BLOCKED on `fixture_voice`: wording."))
        code, _, err = self.note_cmd("plan", self.run_id, "--as", "park")
        self.assertEqual(code, 1)
        self.assertIn("must be `blocked`", err)

        self.propose(self.blocked("- [ ] BLOCKED: something is missing."))
        code, _, err = self.note_cmd("plan", self.run_id, "--as", "park")
        self.assertEqual(code, 1)
        self.assertIn("must name what the run is blocked on", err)

    def test_park_plan_confirm_apply(self):
        self.run_cmd("park", self.run_id, "--constraint", "fixture_voice", "--needs", "Wording.")
        self.propose(self.blocked("- [ ] BLOCKED on `fixture_voice`: how controls are worded."))
        self.assertEqual(self.note_cmd("plan", self.run_id, "--as", "park")[0], 0)
        self.confirm("park")
        self.assertEqual(self.note_cmd("apply", self.run_id, "--as", "park", "--confirm")[0], 0)
        self.assertIn("status: blocked", self.note.read_text(encoding="utf-8"))
        self.assertEqual(self.state(self.run_id)["status"], "parked")


class WhatTheAttestationOwes(StudioCase):
    """A constraint that was derived or stated must reach the note as such."""

    def at_record(self, row, notes=()):
        for name in notes:
            self.place(f"aurora/ui/{name}.md", precedent(name))
        run_id = self.new_run()
        self.through(run_id, "intake")
        self.put(run_id, "attestation.md", self.attestation([row]))
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        for name, text in (("recipe.md", "One search.\n"),):
            self.put(run_id, name, text)
        self.run_cmd("advance", run_id)
        self.run_cmd("confirm", run_id, "execute", "--words", "run it")
        self.put(run_id, "execute_log.md", "Ran it.\n")
        self.run_cmd("advance", run_id)
        self.put(run_id, "review.md", "Fine.\n")
        self.assertEqual(self.run_cmd("advance", run_id)[0], 0)
        return run_id

    def test_a_derivation_must_not_come_back_as_a_decision(self):
        names = ("aurora-lead", "harbor-dusk", "north-gate")
        cites = ", ".join(f"[[{name}]]" for name in names)
        run_id = self.at_record(f"| key light | fixture_look | L2 DERIVED | {cites} | PROVISIONAL |",
                                names)
        for decision in ("- Key light sits camera left.",
                         "- PROVISIONAL, from [[aurora-lead]], [[harbor-dusk]], [[other]]: key light left."):
            with self.subTest(decision=decision):
                self.put(run_id, "note_update.md", GOOD_NOTE + decision + "\n")
                code, _, err = self.note_cmd("plan", run_id)
                self.assertEqual(code, 1)
                self.assertIn("was derived", err)
        self.put(run_id, "note_update.md",
                 GOOD_NOTE + f"- PROVISIONAL, derived from {cites}: key light sits camera left.\n")
        code, _, err = self.note_cmd("plan", run_id)
        self.assertEqual(code, 0, err)

    def test_what_the_author_stated_is_recorded_as_stated(self):
        today = date.today()
        run_id = self.at_record(f"| imagery motifs | fixture_look | STATED | the author, {today} | resolved |")
        self.put(run_id, "note_update.md", GOOD_NOTE)
        code, _, err = self.note_cmd("plan", run_id)
        self.assertEqual(code, 1)
        self.assertIn("was stated by the author", err)
        self.put(run_id, "note_update.md",
                 GOOD_NOTE + f"- STATED {today}: imagery motifs are line work only.\n")
        code, _, err = self.note_cmd("plan", run_id)
        self.assertEqual(code, 0, err)

    def test_a_flush_owes_them_once_context_is_done(self):
        today = date.today()
        run_id = self.at_record(f"| imagery motifs | fixture_look | STATED | the author, {today} | resolved |")
        flushed = GOOD_NOTE.replace(NEXT, f"- [ ] Resume run `{run_id}` at record\n{NEXT}")
        self.put(run_id, "note_update.md", flushed)
        code, _, err = self.note_cmd("plan", run_id, "--as", "flush")
        self.assertEqual(code, 1)
        self.assertIn("was stated by the author", err)
        self.put(run_id, "note_update.md", flushed + f"- STATED {today}: imagery motifs are line work.\n")
        code, _, err = self.note_cmd("plan", run_id, "--as", "flush")
        self.assertEqual(code, 0, err)

    def test_a_flush_before_context_is_done_owes_nothing(self):
        run_id = self.new_run()
        self.through(run_id, "intake")
        self.put(run_id, "attestation.md", self.attestation(
            [f"| imagery motifs | fixture_look | STATED | the author, {date.today()} | resolved |"]))
        self.put(run_id, "note_update.md",
                 GOOD_NOTE.replace(NEXT, f"- [ ] Resume run `{run_id}` at context\n{NEXT}"))
        code, _, err = self.note_cmd("plan", run_id, "--as", "flush")
        self.assertEqual(code, 0, err)


class SecondSession(StudioCase):
    """A note already in the vault, and a later run that updates it."""

    def setUp(self):
        super().setUp()
        first = self.new_run("first-run")
        self.through(first, "record")
        self.run_id = self.new_run("second-run")
        self.through(self.run_id, "review")
        self.note = self.vault / NOTE
        self.assertTrue(self.note.is_file())

    def plan(self, text):
        self.put(self.run_id, "note_update.md", text)
        return self.note_cmd("plan", self.run_id)

    def test_the_run_knows_it_is_continuing(self):
        self.assertFalse(self.state(self.run_id)["note_is_new"])

    def test_appending_to_the_timeline(self):
        text = GOOD_NOTE.replace("## Method", "### 2026-09-29 · ui-direction · second-run\n"
                                 "Ran the accessibility searches.\n\n## Method") \
                        .replace("updated: 2026-09-28", "updated: 2026-09-29")
        code, _, err = self.plan(text)
        self.assertEqual(code, 0, err)
        plan = (self.runs / self.run_id / "record_plan.md").read_text(encoding="utf-8")
        self.assertIn("+### 2026-09-29", plan)
        self.assertIn("existing", plan)

    def test_editing_a_past_entry(self):
        for old, new in (("Matched category: Analytics Dashboard.", "Matched category: Fintech."),
                         ("· ops-console-aaaaaa", "· another-run"),
                         ("Ran one design-system search.", "Ran one design-system search.\nAnd more.")):
            with self.subTest(change=new):
                code, _, err = self.plan(GOOD_NOTE.replace(old, new))
                self.assertEqual(code, 1)
                self.assertIn("append-only", err)

    def test_removing_a_past_entry(self):
        text = GOOD_NOTE.replace("### 2026-09-28 · ui-direction · ops-console-aaaaaa\n"
                                 "Ran one design-system search. Matched category: Analytics "
                                 "Dashboard.\n\n", "")
        code, _, err = self.plan(text)
        self.assertEqual(code, 1)
        self.assertIn("append-only", err)

    def test_hiding_the_timeline(self):
        hidden = GOOD_NOTE.replace("## Timeline", "## History")
        fenced = GOOD_NOTE.replace("## Timeline", "```\n## Timeline").replace("## Method", "```\n\n## Method")
        inserted = GOOD_NOTE.replace("### 2026-09-28 · ui-direction · ops-console-aaaaaa",
                                     "### 2026-09-27 · ui-direction · earlier\nInserted.\n\n"
                                     "### 2026-09-28 · ui-direction · ops-console-aaaaaa")
        for name, text in (("renamed", hidden), ("fenced", fenced), ("inserted before", inserted)):
            with self.subTest(how=name):
                code, _, err = self.plan(text)
                self.assertEqual(code, 1)
                self.assertIn("append-only", err)

    def test_whitespace_is_not_a_change(self):
        text = GOOD_NOTE.replace("Matched category: Analytics Dashboard.",
                                 "Matched category: Analytics Dashboard.   ").replace("\n", "\r\n")
        code, _, err = self.plan(text)
        self.assertEqual(code, 0, err)

    def test_fields_that_are_fixed(self):
        for old, new, field in (("cmd_20260928_ops-console", "cmd_20260928_console", "id"),
                                ("created: 2026-09-28", "created: 2026-09-01", "created")):
            with self.subTest(field=field):
                code, _, err = self.plan(GOOD_NOTE.replace(old, new))
                self.assertEqual(code, 1)
                self.assertIn(f"`{field}` changed", err)
        for field in self.env.spec["content_md"]["immutable"]:
            self.assertIn(field, ("id", "type", "created"))

    def test_updated_does_not_go_backwards(self):
        self.note.write_text(GOOD_NOTE.replace("updated: 2026-09-28", "updated: 2026-10-05"),
                             encoding="utf-8")
        code, _, err = self.plan(GOOD_NOTE)
        self.assertEqual(code, 1)
        self.assertIn("went backwards", err)

    def test_a_vault_note_that_cannot_be_read_is_not_written_over(self):
        self.note.write_text(GOOD_NOTE.replace("id: cmd_20260928_ops-console", "id: [unclosed"),
                             encoding="utf-8")
        rewritten = GOOD_NOTE.replace("Matched category: Analytics Dashboard.", "Rewritten.") \
                             .replace("cmd_20260928_ops-console", "cmd_20260928_other")
        code, _, err = self.plan(rewritten)
        self.assertEqual(code, 1)
        self.assertIn("Fix it by hand first", err)

    def test_the_vault_note_changed_after_the_plan(self):
        text = GOOD_NOTE.replace("One search run so far.", "Two search runs so far.")
        self.assertEqual(self.plan(text)[0], 0)
        self.assertEqual(self.run_cmd("confirm", self.run_id, "record", "--words", "yes")[0], 0)
        self.note.write_text(GOOD_NOTE.replace("One search run so far.", "Edited by hand."),
                             encoding="utf-8")
        code, _, err = self.note_cmd("apply", self.run_id, "--confirm")
        self.assertEqual(code, 1)
        self.assertIn("changed after the plan", err)
        self.assertIn("Edited by hand.", self.note.read_text(encoding="utf-8"))

    def test_nothing_to_change(self):
        self.assertEqual(self.plan(GOOD_NOTE)[0], 0)
        plan = self.state(self.run_id)["plan"]
        self.assertEqual(plan["proposed_sha"], plan["existing_sha"])


class LintCommand(StudioCase):
    def test_every_note_in_the_vault(self):
        self.place("aurora/ui/console.md", GOOD_NOTE)
        self.place("aurora/ui/broken.md",
                   GOOD_NOTE.replace("kind: ui", "kind: poem").replace("ops-console", "broken"))
        self.place("SCHEMA.md", "# not a note\n")
        self.place("claude.md", "# not a note either\n")
        self.place("_Context/brand/README.md", "# not a note\n")
        code, out, _ = self.note_cmd("lint", "--all")
        self.assertEqual(code, 1)
        self.assertIn("2 note(s), 1 failing", out)
        checked = [line.split()[-1] for line in out.splitlines()
                   if line.startswith(("ok ", "FAIL "))]
        self.assertEqual(checked, ["aurora/ui/broken.md", "aurora/ui/console.md"])

    def test_two_notes_with_one_id(self):
        self.place("aurora/ui/a.md", GOOD_NOTE)
        self.place("aurora/ui/b.md", GOOD_NOTE)
        code, out, _ = self.note_cmd("lint", "--all")
        self.assertEqual(code, 1)
        self.assertIn("already has", out)

    def test_a_note_the_author_placed_by_hand_is_still_linted(self):
        self.place("loose-note.md", GOOD_NOTE)
        code, out, _ = self.note_cmd("lint", "loose-note.md")
        self.assertEqual(code, 0)
        self.assertIn("the vault root", out)

    def test_it_needs_a_target(self):
        self.assertEqual(self.note_cmd("lint")[0], 2)

    def test_a_vault_that_is_not_there(self):
        import shutil
        shutil.rmtree(self.vault)
        self.assertEqual(self.note_cmd("lint", "--all")[0], 0)
        self.assertEqual(self.note_cmd("lint", "aurora/ui/x.md")[0], 2)


if __name__ == "__main__":
    unittest.main()
