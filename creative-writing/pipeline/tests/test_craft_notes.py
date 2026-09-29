"""The vault's craft notes (_Craft/) stay honest.

1. Every causal ledger in a note is run through the checker and must produce the
   verdict on its `Expect:` line.
2. Every quotation of three or more words in a note, and in the registers' guidance
   in spec.yaml, must appear verbatim (ignoring typography) in a file elsewhere in the
   vault. The notes claim their quotations are checked; this is the check.
"""
import re
import sys
import unittest
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE))

import plot_logic as pl  # noqa: E402

SPEC = pl.load_spec()
VAULT = (PIPELINE / SPEC["vault_root"]).resolve()
CRAFT = VAULT / "_Craft"
NOTES = sorted(p for p in CRAFT.glob("*.md") if p.name != "_index.md")

# Quotation spans: straight or curly double quotes, on one line. Ellipses split a span in parts.
_QUOTE_RE = re.compile(r'"([^"\n]+?)"|“([^”\n]+?)”')


def norm(text: str) -> str:
    t = text.lower()
    for a, b in (("’", "'"), ("‘", "'"), ("‑", "-"), ("‐", "-"),
                 ("–", " "), ("—", " "), (" ", " ")):
        t = t.replace(a, b)
    t = re.sub(r"[^a-z0-9'\s-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def corpus() -> str:
    """Everything a note may quote: the works, annotations, indexes, the vault's own CLAUDE.md and
    the idea library (pipeline outputs). Never the craft notes themselves, and never the pipeline
    spec, whose register guidance is itself checked against this corpus."""
    parts = []
    for p in VAULT.rglob("*.md"):
        if CRAFT in p.parents or ".obsidian" in p.parts:
            continue
        parts.append(p.read_text(encoding="utf-8"))
    return norm("\n".join(parts))


def spans(text: str):
    """Yield each quotation in a note's prose. Skips frontmatter, wikilinks, and the Because
    column of ledger tables (those are handles into the ledger's own Changes cells)."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i, ln in enumerate(lines[1:], start=1) if ln.strip() == "---"), 0)
        lines = lines[end + 1:]
    because_col = None
    for line in lines:
        line = re.sub(r"\[\[[^\]]*\]\]", "", line)
        if line.strip().startswith("|"):
            cells = re.split(r"(?<!\\)\|", line)
            heads = [c.strip().lower() for c in cells]
            if "because" in heads:                  # a ledger's header row: remember the column to skip
                because_col = heads.index("because")
            elif because_col is not None and len(cells) > because_col:
                cells = cells[:because_col] + cells[because_col + 1:]
            line = "|".join(cells)
        else:
            because_col = None
        for m in _QUOTE_RE.finditer(line):
            yield m.group(1) or m.group(2)


def unverified(text: str, haystack: str) -> list:
    bad = []
    for span in spans(text):
        for part in re.split(r"\.\.\.|…", span):
            n = norm(part)
            if len(n.split()) >= 3 and n not in haystack:
                bad.append(part.strip())
    return bad


class CraftNotes(unittest.TestCase):
    def test_notes_exist(self):
        self.assertEqual([p.name for p in NOTES],
                         ["cosmic-horror.md", "liminality.md", "plot-logic.md", "psychedelia.md"])

    def test_every_ledger_has_the_verdict_it_declares(self):
        seen = 0
        for note in NOTES:
            for ledger, result in pl.check_text(note.read_text(encoding="utf-8"), SPEC):
                if ledger.title == "(none)":
                    continue
                seen += 1
                where = f"{note.name}: {ledger.title}"
                self.assertIn(ledger.expect, ("pass", "fail"), f"{where}: needs an Expect: pass|fail line")
                self.assertTrue(ledger.mode, f"{where}: needs a Mode: line")
                got = "pass" if result["ok"] else "fail"
                detail = [f"{f.code} row {f.row}: {f.message}" for f in result["findings"] if f.level == "error"]
                self.assertEqual(got, ledger.expect, f"{where}: {detail}")
        self.assertGreaterEqual(seen, 10)

    def test_the_failing_ledgers_fail_for_the_reason_the_notes_give(self):
        text = (CRAFT / "plot-logic.md").read_text(encoding="utf-8")
        nightly = next(r for lg, r in pl.check_text(text, SPEC) if "Nightly Inventory" in lg.title)
        self.assertEqual(sorted(f.row for f in nightly["findings"] if f.code == "and-then"), [2, 3])
        self.assertEqual([f.code for f in nightly["findings"] if f.level == "error"], ["and-then", "and-then"])

        text = (CRAFT / "cosmic-horror.md").read_text(encoding="utf-8")
        camp = next(r for lg, r in pl.check_text(text, SPEC) if lg.title.endswith("as pitched"))
        self.assertEqual(sorted(f.row for f in camp["findings"] if f.code == "and-then"), [3, 4])
        self.assertIn("no-investigates", [f.code for f in camp["findings"]])

        two = next(r for lg, r in pl.check_text((CRAFT / "plot-logic.md").read_text(encoding="utf-8"), SPEC)
                   if "Two Who Woke" in lg.title)
        self.assertTrue({"no-but", "smooth-run"} <= {f.code for f in two["findings"]})

    def test_quotations_in_the_notes_are_verbatim(self):
        haystack = corpus()
        missing = [f"{n.name}: \"{q}\"" for n in NOTES for q in unverified(n.read_text(encoding="utf-8"), haystack)]
        self.assertEqual(missing, [], "quotations not found in the vault:\n  " + "\n  ".join(missing))

    def test_quotations_in_register_guidance_are_verbatim(self):
        haystack = corpus()
        missing = [f"{name}: \"{q}\"" for name, cfg in SPEC["registers"].items()
                   for q in unverified(cfg["guidance"], haystack)]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
