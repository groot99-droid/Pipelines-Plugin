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

    def test_authored_means_the_file_is_there(self):
        for name, gate in self.spec["gates"].items():
            with self.subTest(gate=name):
                self.assertEqual(bool(gate["authored"]), (GATES / gate["file"]).is_file())
                self.assertEqual(gate["file"], f"{name}.context.md")
                self.assertTrue(gate["must_answer"])

    def test_no_gate_file_is_undeclared(self):
        on_disk = {path.name for path in GATES.glob("*.context.md")}
        declared = {gate["file"] for gate in self.spec["gates"].values()}
        self.assertLessEqual(on_disk, declared)

    def test_every_section_the_spec_cites_is_in_the_gate(self):
        for name, gate in self.spec["gates"].items():
            if not gate["authored"]:
                continue
            headings = re.findall(r"^## (\d+)\. (.+)$", read(GATES / gate["file"]), re.M)
            numbers = {number for number, _ in headings}
            for item in gate["answers"] + gate["unresolved"]:
                with self.subTest(gate=name, section=item["section"]):
                    self.assertIn(item["section"], numbers)
            unresolved = {number for number, title in headings if title.strip() == "Unresolved"}
            self.assertEqual(unresolved, {item["section"] for item in gate["unresolved"]},
                             "a gate's own Unresolved section and the spec's list must match")

    def test_the_gate_readme_agrees_with_the_spec(self):
        rows = re.findall(r"^\| `(\w+)` \| (.+?) \| .+? \| (.+?) \|$", read(GATES / "README.md"), re.M)
        listed = {name: (state, needed) for name, state, needed in rows}
        self.assertEqual(set(listed), set(self.spec["gates"]))
        for name, (state, needed) in listed.items():
            with self.subTest(gate=name):
                gate = self.spec["gates"][name]
                self.assertEqual(state.startswith("**authored**"), bool(gate["authored"]))
                self.assertEqual("declared gap" in state, bool(gate.get("unresolved")))
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
        tokens = json.loads(read(GATES / self.spec["tokens"]["file"]))
        flat = {}
        for group, values in tokens["color"].items():
            for name, value in values.items():
                flat[f"{group}.{name}"] = value.upper()
        stated = {name: value.upper() for name, value in re.findall(
            r"^\| `([a-z-]+)` \| `(#[0-9A-Fa-f]{6})` \|", read(GATES / "color_science.context.md"), re.M)}
        names = {"bg.base": "bg", "bg.raise": "bg-raise", "bg.panel": "bg-panel",
                 "line.base": "line", "ink.base": "ink", "ink.dim": "ink-dim",
                 "accent.cyan": "cyan", "accent.amber": "amber", "accent.alert": "alert",
                 "accent.queued": "queued"}
        self.assertEqual(set(flat), set(names))
        self.assertEqual(len(stated), 10)
        for token, gate_name in names.items():
            with self.subTest(token=token):
                self.assertEqual(flat[token], stated[gate_name])

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
