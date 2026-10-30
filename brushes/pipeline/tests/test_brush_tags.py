"""vault/tools/brush_tags.py: the tagger block, the closed vocabulary, stale
detection, plan, apply, check and suggestions (docs/CONTRACTS.md F8, F11, F12).

Every test builds a synthetic catalog and vault in a temporary folder with the
helpers of test_brush_search.py. No test reads the real library, catalog or
vault, and none touches the network.

    python -m unittest discover -s brushes/pipeline/tests -p "test_brush_*.py"
"""

import ast
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

PIPELINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE))
sys.path.insert(0, str(PIPELINE / "tests"))

import fixtures  # noqa: E402
import test_brush_search as tbs  # noqa: E402

bs = tbs.bs
tags = tbs.load_tool("brush_tags")
TAGS_SCRIPT = tbs.TOOLS / "brush_tags.py"
STAMP = "2026-03-04T05:06:07Z"

NOTE = "02_Vendor_Packs/inks.md"


def block_text(world, name, slug="inks", *, variant=None, fp=None, brush_id=None, **fields):
    """The text of one tagger block for a brush of the fixture, as the tagger
    would write it. `fields` override the ten lines."""
    bid = brush_id or world.id(name, slug)
    record = world.records[bid]
    parsed = bs.parse_note((world.vault / world.note(slug)).read_text(encoding="utf-8"))
    section = next(s for s in parsed["sections"] if s["brush_id"] == bid)
    lines = {"medium_tags": "(none)", "mark_tags": "(none)", "texture_tags": "(none)", "edge_tags": "(none)",
             "motif_tags": "(none)", "use_tags": "(none)", "visual": "A plain hairline stroke.",
             "evidence": "sheet", "notes": "The name and the sheet agree.", "suggestions": "(none)"}
    lines.update(fields)
    header = (f'### brush {bid} (name: "{record["name"]}", chunk {section["chunk_index"]}, '
              f'lines {section["start_line"]}-{section["end_line"]}, '
              f'fp: {fp or record["content_sha256"][:16]})')
    return "\n".join([header] + [f"{key}: {value}" for key, value in lines.items()]) + "\n"


class TagsCase(tbs.WorldCase):
    def setUp(self):
        super().setUp()
        self.dry = self.world.id("Dry Ink Pen")
        self.wet = self.world.id("Wet Ink Brush")
        self.tech = self.world.id("Technical Liner 0.5")

    def apply(self, text, **kw):
        kw.setdefault("now", STAMP)
        return tags.apply_blocks(self.vault, self.catalog, NOTE, text, **kw)

    def good(self, name="Dry Ink Pen", **fields):
        fields.setdefault("medium_tags", "nib-pen")
        fields.setdefault("use_tags", "line-art, shading")
        return block_text(self.world, name, **fields)

    def sidecar(self, slug="inks"):
        return json.loads(self.world.sidecar(slug).read_text(encoding="utf-8"))

    def run_tags(self, *argv, stdin=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch.object(sys, "stdin", io.StringIO(stdin or "")):
                try:
                    code = tags.main(list(argv) + self.world.args())
                except SystemExit as stop:
                    code = stop.code
        return code, out.getvalue(), err.getvalue()


# ── the tagger block ─────────────────────────────────────────────────────────

class BlockParser(TagsCase):
    def test_a_good_block(self):
        text = self.good(texture_tags="paper-tooth, gritty", suggestions="mark:crosshatch -- parallel strokes, crossed")
        blocks, stray = tags.parse_tagger_blocks(text)
        self.assertEqual(stray, [])
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block["errors"], [])
        self.assertEqual(block["id"], self.dry)
        self.assertEqual(block["name"], "Dry Ink Pen")
        self.assertEqual(block["fp"], self.world.records[self.dry]["content_sha256"][:16])
        self.assertEqual(sorted(block["fields"]), sorted(tags.BLOCK_KEYS))
        self.assertIsInstance(block["chunk"], int)
        self.assertEqual(len(block["lines"]), 2)

    def test_two_blocks_in_order(self):
        text = self.good("Dry Ink Pen") + "\n" + self.good("Wet Ink Brush")
        blocks, _ = tags.parse_tagger_blocks(text)
        self.assertEqual([b["id"] for b in blocks], [self.dry, self.wet])

    def test_none_and_empty_lists(self):
        self.assertEqual(tags._split_tags("(none)"), [])
        self.assertEqual(tags._split_tags("none"), [])
        self.assertEqual(tags._split_tags(""), [])
        self.assertEqual(tags._split_tags(" Nib-Pen ,`line` , nib-pen"), ["nib-pen", "line"])

    def test_a_code_fence_around_the_reply_is_dropped(self):
        blocks, stray = tags.parse_tagger_blocks("```\n" + self.good() + "```\n")
        self.assertEqual((len(blocks), stray, blocks[0]["errors"]), (1, [], []))
        blocks, stray = tags.parse_tagger_blocks("```text\n" + self.good() + "```")
        self.assertEqual((len(blocks), stray), (1, []))

    def test_text_before_the_first_block_is_stray_not_a_block(self):
        blocks, stray = tags.parse_tagger_blocks("Here are the tags:\n\n" + self.good())
        self.assertEqual(len(blocks), 1)
        self.assertEqual(stray, ["Here are the tags:"])

    def test_a_wrapped_line_continues_the_one_before(self):
        text = self.good(notes="The name says dry")
        text += "and the sheet shows a broken line.\n"
        block = tags.parse_tagger_blocks(text)[0][0]
        self.assertEqual(block["fields"]["suggestions"], "(none) and the sheet shows a broken line.")

    def test_crlf_input(self):
        blocks, _ = tags.parse_tagger_blocks(self.good().replace("\n", "\r\n"))
        self.assertEqual((len(blocks), blocks[0]["errors"]), (1, []))

    def test_a_name_with_quotes_and_commas_still_parses(self):
        text = '### brush b_0123456789ab (name: "Say "hi", ok", chunk 3, lines 10-20, fp: 0123456789abcdef)\n' + \
            "\n".join(f"{k}: (none)" for k in tags.BLOCK_KEYS) + "\n"
        block = tags.parse_tagger_blocks(text)[0][0]
        self.assertEqual((block["name"], block["chunk"], block["lines"]), ('Say "hi", ok', 3, (10, 20)))
        self.assertEqual(block["errors"], [])

    def test_a_malformed_header_makes_a_block_with_an_error(self):
        text = "### brush b_0123456789ab (name: Dry, chunk 1)\nmedium_tags: nib-pen\n"
        blocks, _ = tags.parse_tagger_blocks(text)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["id"], "b_0123456789ab")
        self.assertIn("malformed block header", blocks[0]["errors"][0])
        blocks, _ = tags.parse_tagger_blocks("### brush\nmedium_tags: x\n")
        self.assertIsNone(blocks[0]["id"])

    def test_a_missing_line_is_an_error_naming_it(self):
        text = self.good().replace("edge_tags: (none)\n", "")
        block = tags.parse_tagger_blocks(text)[0][0]
        self.assertEqual(block["errors"], ["missing line `edge_tags:`"])

    def test_a_repeated_line_is_an_error(self):
        block = tags.parse_tagger_blocks(self.good() + "visual: again\n")[0][0]
        self.assertIn("`visual` appears twice", block["errors"])

    def test_an_unknown_axis_line_is_an_error(self):
        block = tags.parse_tagger_blocks(self.good() + "shape_tags: round\n")[0][0]
        self.assertTrue(any("shape_tags" in e for e in block["errors"]))

    def test_no_blocks_in_empty_or_unrelated_text(self):
        for text in ("", "\n\n", "nothing to see\n"):
            self.assertEqual(tags.parse_tagger_blocks(text)[0], [])

    def test_the_block_keys_are_the_f8_ten_in_order(self):
        self.assertEqual(tags.BLOCK_KEYS, ("medium_tags", "mark_tags", "texture_tags", "edge_tags", "motif_tags",
                                           "use_tags", "visual", "evidence", "notes", "suggestions"))

    def test_evidence(self):
        self.assertEqual(tags._parse_evidence("sheet"), (["sheet"], None))
        self.assertEqual(tags._parse_evidence("stroke, shape, grain"), (["stroke", "shape", "grain"], None))
        self.assertEqual(tags._parse_evidence("none"), ([], None))
        self.assertEqual(tags._parse_evidence("Sheet sheet"), (["sheet"], None))
        self.assertIsNone(tags._parse_evidence("card")[0])
        self.assertIsNone(tags._parse_evidence("")[0])

    def test_suggestions_split_on_commas_between_suggestions_only(self):
        items = tags._split_suggestions("mark:crosshatch -- crossed, parallel, texture:glitter -- sparkle bits")
        self.assertEqual([(i["axis"], i["suggestion"]) for i in items], [("mark", "crosshatch"), ("texture", "glitter")])
        self.assertEqual(items[0]["why"], "crossed, parallel")
        self.assertEqual(tags._split_suggestions("(none)"), [])
        items = tags._split_suggestions("something odd")
        self.assertEqual((items[0]["axis"], items[0]["suggestion"]), (None, "something odd"))
        items = tags._split_suggestions("medium_tags:ballpoint -- biro")
        self.assertEqual((items[0]["axis"], items[0]["suggestion"]), ("medium", "ballpoint"))


# ── apply ────────────────────────────────────────────────────────────────────

class Apply(TagsCase):
    def test_a_dry_run_writes_nothing_and_says_so(self):
        before = fixtures.tree_digest(self.vault)
        report = self.apply(self.good())
        self.assertEqual((report["accepted"], report["rejected"], report["dry_run"], report["written"]),
                         ([self.dry], [], True, False))
        self.assertEqual(fixtures.tree_digest(self.vault), before)
        code, out, err = self.run_tags("apply", "--file", NOTE, stdin=self.good())
        self.assertEqual(code, 0, err)
        self.assertIn("DRY RUN   nothing is written without --confirm.", out)
        self.assertEqual(fixtures.tree_digest(self.vault), before)
        self.assertFalse(self.world.sidecar("inks").exists())

    def test_confirm_writes_the_sidecar_in_the_f8_shape(self):
        text = self.good(texture_tags="paper-tooth", mark_tags="line") + self.good("Wet Ink Brush", medium_tags="watercolor")
        report = self.apply(text, confirm=True)
        self.assertTrue(report["ok"])
        self.assertTrue(report["written"])
        data = self.sidecar()
        self.assertEqual(list(data), ["brushes", "file", "generator", "schema", "updated", "vocabulary_fingerprint"])
        self.assertEqual((data["schema"], data["file"], data["generator"], data["updated"]),
                         (1, NOTE, "brush-tagger v1", STAMP))
        self.assertEqual(data["vocabulary_fingerprint"], bs.vocabulary_fingerprint(bs.load_vocabulary_full(self.vault)))
        self.assertEqual(sorted(data["brushes"]), sorted([self.dry, self.wet]))
        entry = data["brushes"][self.dry]
        record = self.world.records[self.dry]
        self.assertEqual(entry["content_sha256"], record["content_sha256"])
        self.assertEqual(entry["name"], "Dry Ink Pen")
        self.assertEqual((entry["medium_tags"], entry["mark_tags"], entry["texture_tags"], entry["use_tags"]),
                         (["nib-pen"], ["line"], ["paper-tooth"], ["line-art", "shading"]))
        self.assertEqual((entry["edge_tags"], entry["motif_tags"]), ([], []))
        self.assertEqual(entry["visual"], "A plain hairline stroke.")
        self.assertEqual(entry["visual_basis"], "described-not-measured")
        self.assertEqual(entry["evidence"], {"previews": ["sheet"], "stroke_source": "thumbnail"})
        self.assertEqual((entry["tagged"], entry["tagger"]), (STAMP, "brush-tagger v1"))
        self.assertEqual(sorted(entry), sorted(tags.ENTRY_KEYS))

    def test_the_sidecar_is_the_one_json_spelling_with_lf(self):
        self.apply(self.good(), confirm=True)
        raw = self.world.sidecar("inks").read_bytes()
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"}\n"))
        self.assertEqual(raw.decode("utf-8"), bs.json_text(json.loads(raw)))
        self.assertFalse(self.world.sidecar("inks").with_name(self.world.sidecar("inks").name + ".tmp").exists())

    def test_the_timestamp_is_real_when_none_is_given(self):
        report = tags.apply_blocks(self.vault, self.catalog, NOTE, self.good(), confirm=True)
        stamp = self.sidecar()["updated"]
        self.assertRegex(stamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertNotEqual(stamp[-9:], "T00:00:00Z")
        self.assertEqual(self.sidecar()["brushes"][self.dry]["tagged"], stamp)
        self.assertTrue(report["written"])

    def test_both_logs_are_appended(self):
        self.apply(self.good(suggestions="mark:crosshatch -- crossed lines"), confirm=True)
        log = self.vault / "_BrushTags" / "_backfill_log.jsonl"
        rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["action"], rows[0]["file"], rows[0]["brush_ids"], rows[0]["count"]),
                         ("tagged", NOTE, [self.dry], 1))
        self.assertEqual((rows[0]["timestamp"], rows[0]["generator"]), (STAMP, "brush-tagger v1"))
        self.assertIn("vocabulary_fingerprint", rows[0])
        sug = [json.loads(line) for line in
               (self.vault / "_BrushTags" / "_vocabulary_suggestions.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(sug), 1)
        self.assertEqual((sug[0]["file"], sug[0]["brush_id"], sug[0]["name"], sug[0]["axis"], sug[0]["suggestion"],
                          sug[0]["why"]), (NOTE, self.dry, "Dry Ink Pen", "mark", "crosshatch", "crossed lines"))
        self.apply(self.good("Wet Ink Brush"), confirm=True)
        rows = (self.vault / "_BrushTags" / "_backfill_log.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(rows), 2)                                    # appended, not rewritten

    def test_nothing_is_logged_or_written_without_confirm(self):
        self.apply(self.good(suggestions="mark:crosshatch -- x"))
        self.assertFalse((self.vault / "_BrushTags" / "_backfill_log.jsonl").exists())
        self.assertFalse((self.vault / "_BrushTags" / "_vocabulary_suggestions.jsonl").exists())

    def test_a_wrong_fp_is_rejected(self):
        report = self.apply(self.good(fp="0" * 16), confirm=True)
        self.assertEqual(report["accepted"], [])
        self.assertIn("fp 0000000000000000", report["rejected"][0]["reason"])
        self.assertFalse(report["ok"])
        self.assertFalse(self.world.sidecar("inks").exists())

    def test_an_id_that_is_not_in_the_note_is_rejected(self):
        pumpkin = self.world.id("Pumpkin 1")
        text = block_text(self.world, "Pumpkin 1", "stamps")
        report = self.apply(text)
        self.assertEqual(report["rejected"], [{"id": pumpkin, "reason": "the id is not a brush section of this note"}])

    def test_an_id_outside_ids_is_rejected_and_one_that_never_came_back_is_missing(self):
        text = self.good("Dry Ink Pen") + self.good("Wet Ink Brush")
        report = self.apply(text, ids=f"{self.dry},{self.tech}")
        self.assertEqual(report["accepted"], [self.dry])
        self.assertEqual(report["rejected"], [{"id": self.wet, "reason": "the id is not in --ids"}])
        self.assertEqual(report["missing"], [self.tech])
        self.assertFalse(report["ok"])

    def test_a_tag_outside_the_vocabulary_is_rejected_and_logged_as_a_suggestion(self):
        report = self.apply(self.good(medium_tags="nib-pen, ballpoint"), confirm=True)
        self.assertEqual(report["accepted"], [])
        self.assertIn("medium_tags: not in the vocabulary: ballpoint", report["rejected"][0]["reason"])
        sug = (self.vault / "_BrushTags" / "_vocabulary_suggestions.jsonl").read_text(encoding="utf-8")
        row = json.loads(sug.splitlines()[0])
        self.assertEqual((row["axis"], row["suggestion"], row["brush_id"]), ("medium", "ballpoint", self.dry))
        self.assertIn("not in the vocabulary", row["why"])
        self.assertFalse(self.world.sidecar("inks").exists())

    def test_an_axis_over_its_cap_is_rejected(self):
        for field, value, cap in (("medium_tags", "nib-pen, charcoal, watercolor", 2),
                                  ("mark_tags", "line, stipple, picture-stamp", 2),
                                  ("texture_tags", "paper-tooth, smooth, gritty", 3),
                                  ("edge_tags", "crisp, soft", 2), ("motif_tags", "fruit-vegetable, flower", 2),
                                  ("use_tags", "line-art, shading, decorating", 3)):
            with self.subTest(axis=field):
                report = self.apply(block_text(self.world, "Dry Ink Pen", **{field: value}))
                ok = len(value.split(",")) <= cap
                self.assertEqual(bool(report["accepted"]), ok, report)
        report = self.apply(block_text(self.world, "Dry Ink Pen", medium_tags="nib-pen, charcoal, watercolor"))
        self.assertIn("3 tags is over the cap of 2", report["rejected"][0]["reason"])

    def test_empty_visual_with_evidence_is_rejected_and_without_evidence_is_fine(self):
        report = self.apply(block_text(self.world, "Dry Ink Pen", visual="(none)", evidence="sheet"))
        self.assertIn("visual is empty while evidence is not none", report["rejected"][0]["reason"])
        report = self.apply(block_text(self.world, "Dry Ink Pen", visual="(none)", evidence="none"), confirm=True)
        self.assertEqual(report["accepted"], [self.dry])
        entry = self.sidecar()["brushes"][self.dry]
        self.assertEqual((entry["visual"], entry["evidence"]["previews"]), ("", []))

    def test_a_bad_evidence_word_is_rejected(self):
        report = self.apply(block_text(self.world, "Dry Ink Pen", evidence="card"))
        self.assertIn("evidence `card`", report["rejected"][0]["reason"])

    def test_a_second_block_for_one_id_is_rejected(self):
        report = self.apply(self.good() + self.good())
        self.assertEqual(report["accepted"], [self.dry])
        self.assertEqual(report["rejected"], [{"id": self.dry, "reason": "a second block for the same id"}])

    def test_a_malformed_block_is_rejected_with_its_reason(self):
        text = self.good().replace("notes: The name and the sheet agree.\n", "")
        report = self.apply(text)
        self.assertEqual(report["rejected"][0]["reason"], "missing line `notes:`")

    def test_good_blocks_are_written_even_when_another_is_rejected(self):
        text = self.good("Dry Ink Pen") + self.good("Wet Ink Brush", medium_tags="mystery")
        report = self.apply(text, confirm=True)
        self.assertEqual((report["accepted"], len(report["rejected"]), report["ok"]), ([self.dry], 1, False))
        self.assertEqual(list(self.sidecar()["brushes"]), [self.dry])
        rows = [json.loads(l) for l in (self.vault / "_BrushTags" / "_backfill_log.jsonl").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual([r["action"] for r in rows], ["tagged", "rejected"])
        self.assertEqual(rows[1]["rejected"][0]["id"], self.wet)

    def test_a_second_apply_merges_and_a_retag_replaces(self):
        self.apply(self.good("Dry Ink Pen") + self.good("Wet Ink Brush", medium_tags="watercolor"), confirm=True,
                   now="2026-03-04T05:06:07Z")
        report = self.apply(self.good("Dry Ink Pen", medium_tags="charcoal") + self.good("Technical Liner 0.5"),
                            confirm=True, now="2026-04-04T00:00:01Z")
        self.assertEqual((report["accepted"], report["retagged"]), ([self.dry, self.tech], [self.dry]))
        data = self.sidecar()
        self.assertEqual(sorted(data["brushes"]), sorted([self.dry, self.wet, self.tech]))
        self.assertEqual(data["brushes"][self.dry]["medium_tags"], ["charcoal"])
        self.assertEqual(data["brushes"][self.wet]["medium_tags"], ["watercolor"])
        self.assertEqual(data["brushes"][self.wet]["tagged"], "2026-03-04T05:06:07Z")
        self.assertEqual(data["updated"], "2026-04-04T00:00:01Z")
        actions = [json.loads(l)["action"] for l in (self.vault / "_BrushTags" / "_backfill_log.jsonl").read_text(
            encoding="utf-8").splitlines()]
        self.assertEqual(actions, ["tagged", "tagged", "retagged"])

    def test_an_unreadable_sidecar_is_a_usage_error_and_is_left_alone(self):
        path = self.world.sidecar("inks")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(tags.UsageError):
            self.apply(self.good(), confirm=True)
        self.assertEqual(path.read_text(encoding="utf-8"), "{broken")

    def test_a_note_that_is_not_there_is_a_usage_error(self):
        with self.assertRaises(tags.UsageError):
            tags.apply_blocks(self.vault, self.catalog, "02_Vendor_Packs/nope.md", self.good())
        with self.assertRaises(tags.UsageError):
            tags.apply_blocks(self.vault, self.catalog, "../nope.md", self.good())

    def test_the_file_can_be_a_set_slug(self):
        code, out, err = self.run_tags("apply", "--file", "inks", stdin=self.good())
        self.assertEqual(code, 0, err)
        self.assertEqual(tags.resolve_note(self.vault, self.catalog, "inks"), NOTE)
        with self.assertRaises(tags.UsageError):
            tags.resolve_note(self.vault, self.catalog, "ink-pack-loose")        # a pseudo-set with no note
        with self.assertRaises(tags.UsageError):
            tags.resolve_note(self.vault, self.catalog, "nonsense")

    def test_no_blocks_is_exit_1(self):
        code, out, err = self.run_tags("apply", "--file", NOTE, stdin="nothing useful\n")
        self.assertEqual(code, 1)
        self.assertIn("no tagger blocks", err)

    def test_the_cli_exit_codes_and_the_confirm_flag(self):
        code, out, err = self.run_tags("apply", "--file", NOTE, "--confirm", stdin=self.good())
        self.assertEqual(code, 0, err)
        self.assertTrue(self.world.sidecar("inks").is_file())
        self.assertNotIn("DRY RUN", out)
        code, out, err = self.run_tags("apply", "--file", NOTE, "--confirm", stdin=self.good(fp="1" * 16))
        self.assertEqual(code, 1)
        self.assertIn("REJECTED", out)
        self.assertEqual(self.run_tags("apply", stdin="")[0], 2)                     # --file is required
        self.assertEqual(self.run_tags("apply", "--file", "../x.md", stdin=self.good())[0], 2)

    def test_apply_reads_a_file_with_from(self):
        reply = self.tmp / "reply.txt"
        reply.write_text(self.good(), encoding="utf-8")
        code, out, err = self.run_tags("apply", "--file", NOTE, "--from", str(reply), "--confirm")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.run_tags("apply", "--file", NOTE, "--from", str(self.tmp / "nope.txt"))[0], 2)

    def test_apply_json_report(self):
        code, out, err = self.run_tags("apply", "--file", NOTE, "--json", stdin=self.good())
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual((report["accepted"], report["dry_run"]), ([self.dry], True))

    def test_an_applied_sidecar_reaches_the_index_and_the_search(self):
        self.apply(self.good(mark_tags="line", visual="A dry hairline."), confirm=True)
        index = bs.build_index(self.vault, self.catalog, write=False)
        chunk = bs.resolve_brush(index, "Dry Ink Pen")
        self.assertEqual((chunk["tag_state"], chunk["medium_tags"], chunk["mark_tags"]), ("tagged", ["nib-pen"], ["line"]))
        envelope = bs.search_index(index, tags=["medium=nib-pen", "use=shading"])
        self.assertEqual([r["name"] for r in envelope["results"]], ["Dry Ink Pen"])
        self.assertEqual(index["warnings"][-1].startswith("NOTE:"), True)
        errors, warnings, summary = tags.check_sidecars(self.vault, self.catalog)
        self.assertEqual((errors, warnings, summary["entries"]), ([], [], 1))

    def test_a_changed_brush_makes_the_applied_entry_stale(self):
        self.apply(self.good(), confirm=True)
        path = self.catalog / "brushes" / f"{self.dry}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["content_sha256"] = "f" * 64
        path.write_text(json.dumps(record), encoding="utf-8")
        index = bs.build_index(self.vault, self.catalog, write=False)
        self.assertEqual(bs.resolve_brush(index, self.dry)["tag_state"], "stale")
        errors, warnings, _ = tags.check_sidecars(self.vault, self.catalog)
        self.assertEqual(errors, [])
        self.assertTrue(any("stale" in w for w in warnings))


# ── plan ─────────────────────────────────────────────────────────────────────

def many(count, name="Brush"):
    return [{"name": f"{name} {n:02d}", "set": "inks", "spacing": 0.01 + n / 1000, "settings": {"maxSize": 0.1}}
            for n in range(1, count + 1)]


class Plan(TagsCase):
    def plan(self, **kw):
        return tags.build_plan(self.vault, self.catalog, **kw)

    def test_everything_is_untagged_at_first(self):
        plan = self.plan()
        self.assertEqual(plan["counts"], {"tag": len(tbs.SPECS)})
        ids = [i for call in plan["calls"] for i in call["ids"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(plan["pending"], len(ids))
        self.assertEqual(plan["sheet"], {"rows": 8, "sheets_per_call": 2})

    def test_a_call_names_the_chunk_lines_and_fp_the_tagger_needs(self):
        plan = self.plan(only="inks")
        call = plan["calls"][0]
        self.assertEqual((call["call"], call["file"], call["set"]), ("inks#1", NOTE, "inks"))
        chunk = call["chunks"][0]
        self.assertEqual(chunk["id"], self.dry)
        self.assertEqual(chunk["fp"], self.world.records[self.dry]["content_sha256"][:16])
        lines = (self.vault / NOTE).read_text(encoding="utf-8").split("\n")
        first = int(chunk["lines"].split("-")[0])
        self.assertEqual(lines[first - 1], "## Dry Ink Pen")
        self.assertEqual(call["names"][:3], ["Dry Ink Pen", "Wet Ink Brush", "Technical Liner 0.5"])
        self.assertEqual(call["decisions"][self.dry], "tag")

    def test_what_was_applied_is_skipped_and_force_brings_it_back(self):
        self.apply(self.good(), confirm=True)
        plan = self.plan()
        self.assertEqual(plan["counts"]["skip_valid"], 1)
        self.assertEqual(plan["counts"]["tag"], len(tbs.SPECS) - 1)
        self.assertNotIn(self.dry, [i for c in plan["calls"] for i in c["ids"]])
        forced = self.plan(force=True)
        self.assertEqual(forced["counts"], {"force": len(tbs.SPECS)})
        self.assertIn(self.dry, [i for c in forced["calls"] for i in c["ids"]])

    def test_a_stale_entry_is_retagged(self):
        self.apply(self.good(), confirm=True)
        path = self.catalog / "brushes" / f"{self.dry}.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["content_sha256"] = "e" * 64
        path.write_text(json.dumps(record), encoding="utf-8")
        plan = self.plan(only="inks")
        self.assertEqual(plan["counts"]["retag"], 1)
        call = next(c for c in plan["calls"] if self.dry in c["ids"])
        self.assertEqual(call["decisions"][self.dry], "retag")

    def test_ids_and_only_narrow_the_plan(self):
        plan = self.plan(ids=[self.dry, self.world.id("Charcoal Stick")])
        self.assertEqual(sorted(i for c in plan["calls"] for i in c["ids"]), sorted([self.dry, self.world.id("Charcoal Stick")]))
        self.assertEqual({c["set"] for c in self.plan(only="PAINTS")["calls"]}, {"paints"})
        self.assertEqual(self.plan(only="nothing-like-this")["calls"], [])

    def test_twenty_brushes_make_three_sheets_and_two_calls(self):
        with tbs.fixtures_temp() as tmp:
            world = tbs.make_world(tmp, brushes=many(20))
            plan = tags.build_plan(world.vault, world.catalog, only="inks")
            self.assertEqual([c["sheets"] for c in plan["calls"]], [["sheet-01.png", "sheet-02.png"], ["sheet-03.png"]])
            self.assertEqual([len(c["ids"]) for c in plan["calls"]], [16, 4])
            self.assertEqual([c["call"] for c in plan["calls"]], ["inks#1", "inks#2"])
            self.assertEqual(plan["pending"], 20)
            order = [i for c in plan["calls"] for i in c["ids"]]
            self.assertEqual(order, [tbs.brush_id(s) for s in many(20)])          # in note order

    def test_only_the_sheets_with_pending_brushes_are_called(self):
        with tbs.fixtures_temp() as tmp:
            specs = many(20)
            world = tbs.make_world(tmp, brushes=specs)
            keep = {tbs.brush_id(s): {} for s in specs[:16]}                         # sheets 1 and 2 are done
            tbs.write_sidecar(world, "inks", keep)
            plan = tags.build_plan(world.vault, world.catalog, only="inks")
            self.assertEqual([c["sheets"] for c in plan["calls"]], [["sheet-03.png"]])
            self.assertEqual(plan["counts"], {"skip_valid": 16, "tag": 4})

    def test_a_pending_brush_in_a_later_sheet_joins_the_first_call(self):
        with tbs.fixtures_temp() as tmp:
            specs = many(20)
            world = tbs.make_world(tmp, brushes=specs)
            done = {tbs.brush_id(s): {} for s in specs[8:16]}                        # sheet 2 is done
            tbs.write_sidecar(world, "inks", done)
            plan = tags.build_plan(world.vault, world.catalog, only="inks")
            self.assertEqual([c["sheets"] for c in plan["calls"]], [["sheet-01.png", "sheet-03.png"]])
            self.assertEqual(len(plan["calls"][0]["ids"]), 12)

    def test_missing_sheets_are_reported_and_fail_the_command(self):
        plan = self.plan(only="inks")
        self.assertIn("inks", plan["missing_sheets"])
        self.assertFalse(plan["calls"][0]["sheets_present"])
        code, out, err = self.run_tags("plan", "--only", "inks")
        self.assertEqual(code, 1)
        self.assertIn("render --sheets-only", out)
        self.assertIn("inks#1", out)
        code, out, err = self.run_tags("plan", "--only", "inks", "--allow-no-sheets")
        self.assertEqual(code, 0, err)

    def test_built_sheets_make_the_plan_ready_and_sheets_json_places_the_brushes(self):
        folder = self.vault / "_Previews" / "_sheets" / "inks"
        folder.mkdir(parents=True)
        cells = [{"n": 1, "id": self.tech, "name": "Technical Liner 0.5"}]
        other = [{"n": 1, "id": self.dry}, {"n": 2, "id": self.wet}]
        (folder / "sheets.json").write_text(json.dumps({"schema": "rosw-brushes-sheets/1", "sheets": [
            {"file": "sheet-01.png", "cells": cells}, {"file": "sheet-02.png", "cells": other}]}), encoding="utf-8")
        plan = self.plan(only="inks")
        self.assertEqual(plan["missing_sheets"], [])
        call = plan["calls"][0]
        self.assertTrue(call["sheets_present"])
        self.assertEqual(call["sheets"], ["sheet-01.png", "sheet-02.png"])
        self.assertEqual(self.run_tags("plan", "--only", "inks")[0], 0)

    def test_a_set_whose_note_is_missing_is_blocked_not_planned(self):
        self.world.note_path("paints").unlink()
        plan = self.plan()
        self.assertEqual([b["set"] for b in plan["blocked"]], ["paints"])
        self.assertEqual(len(plan["blocked"][0]["ids"]), 4)
        self.assertEqual(plan["counts"]["blocked"], 4)
        self.assertNotIn("paints", {c["set"] for c in plan["calls"]})

    def test_a_pseudo_set_without_a_note_is_not_planned(self):
        self.assertNotIn("ink-pack-loose", {c["set"] for c in self.plan()["calls"]})

    def test_limit(self):
        self.assertEqual(len(self.plan(limit=1)["calls"]), 1)

    def test_plan_json_and_text(self):
        code, out, err = self.run_tags("plan", "--json", "--allow-no-sheets")
        data = json.loads(out)
        self.assertEqual(set(data), {"calls", "blocked", "counts", "missing_sheets", "sheet", "pending"})
        code, out, err = self.run_tags("plan", "--allow-no-sheets", "--only", "stamps")
        self.assertIn("Pumpkin 1", out)
        self.assertIn("[tag]", out)

    def test_plan_is_read_only(self):
        before = fixtures.tree_digest(self.world.root)
        self.run_tags("plan", "--allow-no-sheets")
        self.assertEqual(fixtures.tree_digest(self.world.root), before)


# ── check ────────────────────────────────────────────────────────────────────

class Check(TagsCase):
    def setUp(self):
        super().setUp()
        self.apply(self.good(mark_tags="line", visual="A dry hairline."), confirm=True)

    def edit(self, change):
        path = self.world.sidecar("inks")
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def run_check(self, *extra):
        return self.run_tags("check", *extra)

    def test_a_clean_vault_passes(self):
        code, out, err = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("checked 1 sidecars, 1 entries: 0 errors, 0 warnings", out)

    def test_each_error_makes_it_fail(self):
        cases = {
            "an unknown tag": (lambda d: d["brushes"][self.dry].update(medium_tags=["mystery"]), "not in the vocabulary"),
            "over the cap": (lambda d: d["brushes"][self.dry].update(medium_tags=["nib-pen", "charcoal", "watercolor"]), "cap"),
            "a repeated tag": (lambda d: d["brushes"][self.dry].update(use_tags=["shading", "shading"]), "repeats"),
            "a wrong file": (lambda d: d.update(file="02_Vendor_Packs/other.md"), "its own note path"),
            "visual_basis": (lambda d: d["brushes"][self.dry].update(visual_basis="measured"), "visual_basis"),
            "a bad time": (lambda d: d["brushes"][self.dry].update(tagged="yesterday"), "`tagged`"),
            "a bad updated": (lambda d: d.update(updated="2026-01-01"), "`updated`"),
            "missing key": (lambda d: d["brushes"][self.dry].pop("notes"), "missing key `notes`"),
            "missing top key": (lambda d: d.pop("generator"), "missing key `generator`"),
            "bad hash": (lambda d: d["brushes"][self.dry].update(content_sha256="abc"), "64 hex"),
            "bad evidence": (lambda d: d["brushes"][self.dry].update(evidence={"previews": ["card"]}), "evidence.previews"),
            "empty visual": (lambda d: d["brushes"][self.dry].update(visual=""), "visual is empty"),
            "not a list": (lambda d: d["brushes"][self.dry].update(mark_tags="line"), "not a list"),
            "bad id": (lambda d: d["brushes"].update({"nope": d["brushes"][self.dry]}), "not a brush id"),
            "wrong schema": (lambda d: d.update(schema=2), "schema"),
        }
        for name, (change, needle) in cases.items():
            with self.subTest(case=name):
                tbs.write_sidecar(self.world, "inks", {self.dry: {"medium_tags": ["nib-pen"]}})
                self.edit(change)
                code, out, err = self.run_check()
                self.assertEqual(code, 1, out)
                self.assertIn(needle, out)
                self.assertRegex(out, r"[1-9]\d* errors")

    def test_an_unparsable_sidecar_is_an_error(self):
        self.world.sidecar("inks").write_text("{nope", encoding="utf-8")
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", out)

    def test_stale_and_orphan_are_warnings_and_strict_makes_them_errors(self):
        self.edit(lambda d: d["brushes"].update({"b_ffffffffffff": dict(d["brushes"][self.dry])}))
        record_path = self.catalog / "brushes" / f"{self.dry}.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["content_sha256"] = "d" * 64
        record_path.write_text(json.dumps(record), encoding="utf-8")
        code, out, _ = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("stale", out)
        self.assertIn("orphan", out)
        code, out, _ = self.run_check("--strict")
        self.assertEqual(code, 1)
        self.assertIn("warnings count as errors under --strict", out)

    def test_a_vocabulary_change_is_a_warning(self):
        (self.vault / "_BrushTags" / "vocabulary.yaml").write_text(tbs.VOCABULARY + "  - extra-use  # one more\n",
                                                                   encoding="utf-8")
        code, out, _ = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("another vocabulary", out)
        self.assertEqual(self.run_check("--strict")[0], 1)

    def test_divergent_duplicates_are_a_warning(self):
        tbs.write_sidecar(self.world, "stamps", {self.dry: {"medium_tags": ["charcoal"]}}, file="01_Procreate_Defaults/stamps.md")
        code, out, _ = self.run_check()
        self.assertEqual(code, 0, out)
        self.assertIn("two sidecars hold different current tags", out)

    def test_a_bad_log_line_is_an_error(self):
        with open(self.vault / "_BrushTags" / "_backfill_log.jsonl", "a", encoding="utf-8", newline="\n") as handle:
            handle.write("not json\n")
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("_backfill_log.jsonl line", out)

    def test_no_vocabulary_is_an_error_not_a_crash(self):
        (self.vault / "_BrushTags" / "vocabulary.yaml").unlink()
        code, out, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("vocabulary", out)

    def test_check_json(self):
        code, out, _ = self.run_check("--json")
        data = json.loads(out)
        self.assertEqual((code, data["ok"], data["errors"], data["entries"]), (0, True, [], 1))

    def test_no_sidecars_at_all_is_clean(self):
        self.world.sidecar("inks").unlink()
        code, out, _ = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("checked 0 sidecars", out)

    def test_check_writes_nothing(self):
        before = fixtures.tree_digest(self.world.root)
        self.run_check("--strict")
        self.assertEqual(fixtures.tree_digest(self.world.root), before)


# ── suggestions ──────────────────────────────────────────────────────────────

class Suggestions(TagsCase):
    def test_none_logged(self):
        code, out, _ = self.run_tags("suggestions")
        self.assertEqual((code, out), (0, "No suggestions logged.\n"))

    def test_counted_by_axis_and_word(self):
        self.apply(self.good("Dry Ink Pen", suggestions="mark:crosshatch -- crossed"), confirm=True)
        self.apply(self.good("Wet Ink Brush", suggestions="mark:crosshatch -- crossed lines, texture:glitter -- shiny"),
                   confirm=True)
        groups = tags.summarise_suggestions(self.vault)
        self.assertEqual([(g["suggestion"], g["count"]) for g in groups],
                         [("mark:crosshatch", 2), ("texture:glitter", 1)])
        self.assertEqual(len(groups[0]["brushes"]), 2)
        code, out, _ = self.run_tags("suggestions")
        self.assertIn("  2  mark:crosshatch", out)
        code, out, _ = self.run_tags("suggestions", "--json")
        self.assertEqual(json.loads(out)[0]["count"], 2)


# ── rules every script follows ───────────────────────────────────────────────

class Rules(unittest.TestCase):
    def test_the_verbs_are_the_contracts(self):
        parser = tags.build_parser()
        verbs = next(a for a in parser._actions if isinstance(a.choices, dict))
        self.assertEqual(list(verbs.choices), ["plan", "apply", "check", "suggestions"])

    def test_the_declared_flags_exist(self):
        parser = tags.build_parser()
        verbs = next(a for a in parser._actions if isinstance(a.choices, dict)).choices
        apply_flags = {opt for action in verbs["apply"]._actions for opt in action.option_strings}
        self.assertTrue({"--file", "--ids", "--confirm"} <= apply_flags)
        self.assertIn("--strict", {opt for action in verbs["check"]._actions for opt in action.option_strings})

    def test_only_apply_takes_confirm(self):
        parser = tags.build_parser()
        verbs = next(a for a in parser._actions if isinstance(a.choices, dict)).choices
        for name, sub in verbs.items():
            has = "--confirm" in {opt for action in sub._actions for opt in action.option_strings}
            self.assertEqual(has, name == "apply", name)

    def test_the_sheet_batching_is_what_the_spec_says(self):
        text = (tbs.BRUSHES / "spec.yaml").read_text(encoding="utf-8")
        self.assertIn("sheet: {rows: 8, sheets_per_call: 2}", text)
        self.assertEqual((tags.SHEET_ROWS, tags.SHEETS_PER_CALL), (8, 2))

    def test_the_caps_and_axes_are_the_specs(self):
        text = (tbs.BRUSHES / "spec.yaml").read_text(encoding="utf-8")
        self.assertIn("caps: {medium: 2, mark: 2, texture: 3, edge: 2, motif: 2, use: 3}", text)
        self.assertIn("axes: [medium, mark, texture, edge, motif, use]", text)
        self.assertEqual(tags.CAPS, {"medium": 2, "mark": 2, "texture": 3, "edge": 2, "motif": 2, "use": 3})

    def test_no_network_module_and_no_pipeline_import(self):
        tree = ast.parse(TAGS_SCRIPT.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        banned = {"socket", "ssl", "urllib", "http", "requests", "subprocess", "yaml", "pipeline", "brush_common"}
        self.assertEqual(imported & banned, set())
        self.assertIn("brush_search", imported)

    def test_text_is_utf8_lf_and_the_script_ends_in_main(self):
        source = TAGS_SCRIPT.read_text(encoding="utf-8")
        for match in re.finditer(r"\bopen\(([^)]*)\)", source):
            self.assertIn("encoding=", match.group(1), match.group(0))
        self.assertNotIn(b"\r", TAGS_SCRIPT.read_bytes())
        self.assertTrue(source.rstrip().endswith("raise SystemExit(main())"))
        self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parent))", source)

    def test_python_dash_I_from_another_folder(self):
        with tbs.fixtures_temp() as tmp:
            world = tbs.make_world(Path(tmp) / "data")
            elsewhere = Path(tmp) / "cwd"
            elsewhere.mkdir()
            env = {k: v for k, v in os.environ.items() if not k.startswith("ROSW_BRUSHES_")}
            run = lambda *a, stdin=None: subprocess.run(
                [sys.executable, "-I", str(TAGS_SCRIPT), *a, *world.args()], capture_output=True, text=True,
                encoding="utf-8", cwd=elsewhere, env=env, input=stdin)
            self.assertEqual(run("check").returncode, 0)
            plan = run("plan", "--json", "--allow-no-sheets")
            self.assertEqual(plan.returncode, 0, plan.stderr)
            self.assertGreater(json.loads(plan.stdout)["pending"], 0)
            text = block_text(world, "Dry Ink Pen", medium_tags="nib-pen")
            dry = run("apply", "--file", NOTE, stdin=text)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn("DRY RUN", dry.stdout)
            wrote = run("apply", "--file", NOTE, "--confirm", stdin=text)
            self.assertEqual(wrote.returncode, 0, wrote.stderr)
            self.assertTrue(world.sidecar("inks").is_file())
            self.assertEqual(run("check", "--strict").returncode, 0)
            self.assertEqual(run("apply", "--file", NOTE, stdin="junk").returncode, 1)
            self.assertEqual(run("apply").returncode, 2)

    def test_the_generated_sidecar_holds_no_absolute_path(self):
        with tbs.fixtures_temp() as tmp:
            world = tbs.make_world(Path(tmp) / "data")
            tags.apply_blocks(world.vault, world.catalog, NOTE, block_text(world, "Dry Ink Pen", medium_tags="nib-pen"),
                              confirm=True, now=STAMP)
            raw = world.sidecar("inks").read_text(encoding="utf-8")
            self.assertNotIn(str(tmp), raw)
            self.assertIsNone(re.search(r"[A-Za-z]:[\\/]", raw))


class RealVocabularyAgainstTheTagger(unittest.TestCase):
    """The shipped vocabulary is what `apply` enforces."""

    def test_a_block_using_the_real_vocabulary_is_accepted(self):
        with tbs.fixtures_temp() as tmp:
            world = tbs.make_world(Path(tmp) / "data")
            (world.vault / "_BrushTags" / "vocabulary.yaml").write_text(
                tbs.REAL_VOCABULARY.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
            text = block_text(world, "Dry Ink Pen", medium_tags="technical-pen", mark_tags="monoline",
                              texture_tags="dry-broken, paper-tooth", edge_tags="crisp", use_tags="line-art, comic-toning")
            report = tags.apply_blocks(world.vault, world.catalog, NOTE, text)
            self.assertEqual((report["accepted"], report["rejected"]), ([tbs.brush_id(tbs.SPECS[0])], []))
            report = tags.apply_blocks(world.vault, world.catalog, NOTE,
                                       block_text(world, "Dry Ink Pen", medium_tags="nib-pens"))
            self.assertEqual(report["accepted"], [])


if __name__ == "__main__":
    unittest.main()
