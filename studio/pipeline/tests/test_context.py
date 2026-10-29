"""The studio's own brand context agrees with itself and with the spec.

These are the only tests that read the real gates, tokens.json and the real
vault's notes. The brand context is to be replaced: when it is, these tests are
rewritten with it. Every other test runs on the fixture context in helpers.py,
so replacing the context does not touch them.

They write nothing.
"""

import json
import re
import unittest

from helpers import PIPELINE, content_md, studio_common

import gate_md

STUDIO = PIPELINE.parent
VAULT = STUDIO / "vault"
GATES = VAULT / "_Context" / "brand"


def read(path):
    return path.read_text(encoding="utf-8")


class Context(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = studio_common.Env()
        cls.spec = cls.env.spec

    # ── the gates on disk ─────────────────────────────────────────────────

    def test_every_gate_is_named_for_its_file(self):
        for name, gate in self.spec["gates"].items():
            with self.subTest(gate=name):
                self.assertEqual(gate["file"], f"{name}.context.md")
                self.assertTrue(gate["must_answer"])

    def test_no_gate_file_is_undeclared(self):
        on_disk = {path.name for path in GATES.glob("*.context.md")}
        declared = {gate["file"] for gate in self.spec["gates"].values()}
        self.assertLessEqual(on_disk, declared)

    def test_every_authored_gate_has_the_shape_the_bookkeeper_reads(self):
        for name, gate in self.spec["gates"].items():
            path = GATES / gate["file"]
            if not path.is_file():
                continue
            with self.subTest(gate=name):
                self.assertEqual(gate_md.lint_gate(read(path)), [])
                self.assertTrue(studio_common.gate_sections(self.env, name)["answers"])

    def test_the_gate_readme_agrees_with_the_spec(self):
        rows = re.findall(r"^\| `(\w+)` \| (.+?) \| .+? \| (.+?) \|$", read(GATES / "README.md"), re.M)
        listed = {name: (state, needed) for name, state, needed in rows}
        self.assertEqual(set(listed), set(self.spec["gates"]))
        for name, (state, needed) in listed.items():
            with self.subTest(gate=name):
                sections = studio_common.gate_sections(self.env, name)
                self.assertEqual(state.startswith("**authored**"), sections is not None)
                self.assertEqual("declared gap" in state, bool(sections and sections["unresolved"]))
                users = {p for p, cfg in self.spec["pipelines"].items()
                         if any(need["gate"] == name for need in cfg.get("requires_context", []))}
                stated = set() if needed.strip() == "none yet" else {
                    item.strip() for item in needed.split(",")}
                self.assertEqual(stated, users)

    def test_the_rules_example_cites_real_gates(self):
        rules = read(VAULT / "CLAUDE.md")
        example = re.search(r"```\n(\| Constraint \|.+?)```", rules, re.S).group(1)
        for row in studio_common.attestation_rows(example):
            with self.subTest(row=row["row"][:50]):
                self.assertIn(row["gate"], self.spec["gates"])

    # ── tokens ────────────────────────────────────────────────────────────

    def test_the_tokens_and_the_colour_gate_state_the_same_palette(self):
        """Every colour in tokens.json is in the colour gate's palette section,
        and every colour that section states is a token. Neither the section's
        number nor the token names are assumed: both come from the files, so
        replacing the gate and the tokens together does not touch this test."""
        tokens = json.loads(read(GATES / self.spec["tokens"]["file"]))

        def hexes(value):
            if isinstance(value, dict):
                return [h for v in value.values() for h in hexes(v)]
            if isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
                return [value.upper()]
            return []

        in_tokens = hexes(tokens["color"])
        gate = read(GATES / self.spec["gates"]["color_science"]["file"])
        palette = [body for title, body in studio_common.sections(gate)
                   if "palette" in title.casefold()]
        self.assertEqual(len(palette), 1, "the colour gate has one section whose title says palette")
        stated = [value.upper() for value in re.findall(r"`(#[0-9A-Fa-f]{6})`", palette[0])]
        self.assertTrue(stated, "the palette section states its colours as `#RRGGBB`")
        self.assertEqual(sorted(set(in_tokens)), sorted(set(stated)))
        self.assertEqual(len(in_tokens), len(set(in_tokens)), "a token colour is stated once")

    def test_the_tokens_say_who_may_change_them(self):
        tokens = json.loads(read(GATES / self.spec["tokens"]["file"]))
        self.assertIn("agent proposes", tokens["mutation_policy"])

    # ── the vault as it stands ────────────────────────────────────────────

    def test_every_note_in_the_vault_passes_the_lint(self):
        for path in studio_common.vault_notes(self.env):
            relative = path.relative_to(self.env.vault).as_posix()
            with self.subTest(note=relative):
                errors, _ = content_md.lint(read(path), self.env, relative)
                self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
