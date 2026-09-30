"""The contract is stated in several places. They must agree.

These tests read the real spec and the real documents, for the machinery:
stages, checks, refusals, the ladder, the note rules and the commands. The
brand context itself is checked in test_context.py. They write nothing.
"""

import re
import unittest

from helpers import PIPELINE, REPO, content_md, studio_common, studio_run

STUDIO = PIPELINE.parent
VAULT = STUDIO / "vault"
GATES = VAULT / "_Context" / "brand"
SKILL = REPO / ".claude" / "skills" / "studio-pipeline" / "SKILL.md"


def read(path):
    return path.read_text(encoding="utf-8")


class Spec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = studio_common.Env()
        cls.spec = cls.env.spec

    def test_the_spec_points_at_the_real_folders(self):
        self.assertEqual(self.env.vault, VAULT.resolve())
        self.assertEqual(self.env.context, GATES.resolve())
        self.assertEqual(self.env.runs, (PIPELINE / "runs").resolve())

    # ── stages ────────────────────────────────────────────────────────────

    def test_every_check_a_stage_names_exists(self):
        for stage in self.spec["stages"]:
            for name in stage.get("checks", []):
                with self.subTest(stage=stage["id"], check=name):
                    self.assertIn(name, studio_run.CHECKS)

    def test_every_check_is_used(self):
        used = {name for stage in self.spec["stages"] for name in stage.get("checks", [])}
        self.assertEqual(used, set(studio_run.CHECKS))

    def test_stage_entries_are_whole(self):
        ids = [stage["id"] for stage in self.spec["stages"]]
        self.assertEqual(len(ids), len(set(ids)))
        for stage in self.spec["stages"]:
            with self.subTest(stage=stage["id"]):
                for key in ("id", "title", "checkpoint", "description", "prompt", "checks"):
                    self.assertIn(key, stage)
                self.assertTrue(studio_common.stage_outputs(stage))
                self.assertIn("outputs_exist", stage["checks"])

    def test_every_stage_is_a_checkpoint(self):
        for stage in self.spec["stages"]:
            with self.subTest(stage=stage["id"]):
                self.assertIs(stage["checkpoint"], True)

    def test_a_stage_that_needs_a_go_ahead_checks_for_one(self):
        needing = [s for s in self.spec["stages"] if s.get("requires_explicit_confirm")]
        self.assertTrue(needing)
        for stage in needing:
            with self.subTest(stage=stage["id"]):
                self.assertIn("confirmed", stage["checks"])
        self.assertTrue(self.spec["stages"][-1].get("requires_explicit_confirm"),
                        "the stage that writes the note must need a go-ahead")

    def test_context_comes_before_anything_is_run(self):
        ids = [stage["id"] for stage in self.spec["stages"]]
        attesting = next(s["id"] for s in self.spec["stages"] if "no_unresolved" in s["checks"])
        running = next(s["id"] for s in self.spec["stages"] if "confirmed_before_output" in s["checks"])
        self.assertLess(ids.index(attesting), ids.index(running))

    # ── pipelines ─────────────────────────────────────────────────────────

    def test_every_gate_a_pipeline_needs_is_declared(self):
        for name, cfg in self.spec["pipelines"].items():
            for need in cfg.get("requires_context", []):
                with self.subTest(pipeline=name, gate=need["gate"]):
                    self.assertIn(need["gate"], self.spec["gates"])
                    self.assertTrue(need.get("needs"), "say what is needed from the gate")

    def test_every_pipeline_makes_a_kind_the_schema_knows(self):
        for name, cfg in self.spec["pipelines"].items():
            with self.subTest(pipeline=name):
                self.assertIn(cfg["status"], ("implemented", "not_yet_implemented"))
                self.assertIn(cfg["kind"], self.spec["content_md"]["kinds"])
                self.assertIn(cfg["class"], ("none", "spend", "local-compute"))
                self.assertTrue(cfg.get("makes"))
                self.assertTrue(cfg.get("from"))

    def test_an_implemented_pipeline_has_what_it_runs_through(self):
        implemented = {n: c for n, c in self.spec["pipelines"].items() if c["status"] == "implemented"}
        self.assertTrue(implemented)
        for name, cfg in implemented.items():
            with self.subTest(pipeline=name):
                for key, path in cfg["executes_through"].items():
                    self.assertTrue((REPO / path).is_file(), f"{key}: {path} is not in the repo")
                for stage in self.spec["stages"]:
                    if f"{{pipeline.stage_notes.{stage['id']}}}" in stage["prompt"]:
                        self.assertTrue(cfg["stage_notes"].get(stage["id"]),
                                        f"no stage_notes.{stage['id']}")
                self.assertIn("leaves_machine", cfg)

    def test_no_pipeline_lists_a_tool_it_may_never_call(self):
        never = self.spec["connectors"]["never"]
        for name, cfg in self.spec["pipelines"].items():
            for tool in (cfg.get("connector") or {}).get("tools", []):
                for word in never:
                    with self.subTest(pipeline=name, tool=tool, word=word):
                        self.assertNotIn(word, tool.lower())

    def test_every_refusal_says_what_enforces_it(self):
        ids = [refusal["id"] for refusal in self.spec["refusals"]]
        self.assertEqual(len(ids), len(set(ids)))
        scripts = {"studio_run.py": studio_run, "content_md.py": content_md}
        for refusal in self.spec["refusals"]:
            with self.subTest(refusal=refusal["id"]):
                self.assertTrue(refusal["rule"])
                self.assertTrue(refusal["enforced_by"])
                named = re.findall(r"(studio_run\.py|content_md\.py) ([a-z]+)", refusal["enforced_by"])
                for script, command in named:
                    choices = scripts[script].build_parser()._subparsers._group_actions[0].choices
                    self.assertIn(command, choices, f"{script} has no `{command}`")

    # ── the ladder ────────────────────────────────────────────────────────

    def test_every_level_says_what_it_cites_and_what_state_it_leaves(self):
        ladder = self.spec["ladder"]
        self.assertEqual(set(ladder["levels"]), {"L0", "L1", "L2", "STATED", "L3"})
        for name, level in ladder["levels"].items():
            with self.subTest(level=name):
                self.assertTrue(level["rule"])
                self.assertTrue(level["source"])
                self.assertIn(level["state"], ladder["states"])
        self.assertEqual(ladder["levels"]["L2"]["state"], ladder["provisional_marker"])
        self.assertEqual(ladder["levels"]["L3"]["state"], ladder["unresolved_marker"])
        self.assertGreaterEqual(ladder["levels"]["L2"]["min_notes"], 3)

    def test_the_level_names_in_the_spec_are_the_ones_the_code_reads(self):
        for name, level in self.spec["ladder"]["levels"].items():
            for written in (name, level["name"], f"{name} {level['name']}", level["name"].lower()):
                with self.subTest(written=written):
                    self.assertEqual(studio_common.level_of({"level": written}), name)
        self.assertIsNone(studio_common.level_of({"level": "probably fine"}))

    def test_the_example_in_the_rules_is_an_attestation_the_code_can_read(self):
        rules = read(VAULT / "CLAUDE.md")
        example = re.search(r"```\n(\| Constraint \|.+?)```", rules, re.S).group(1)
        rows = studio_common.attestation_rows(example)
        levels = [studio_common.level_of(row) for row in rows]
        self.assertEqual(levels, ["L0", "L1", "L2", "STATED", "L3"])
        for row, level in zip(rows, levels):
            with self.subTest(level=level):
                self.assertEqual(studio_common.squeeze(row["state"]),
                                 self.spec["ladder"]["levels"][level]["state"].casefold())

    def test_the_stage_instructions_show_the_same_columns(self):
        context = next(s for s in self.spec["stages"] if "no_unresolved" in s["checks"])
        header = re.search(r"^\s*(\| Constraint .+\|)\s*$", context["prompt"], re.M).group(1)
        cells = [cell.casefold() for cell in studio_common.table_cells(header)]
        self.assertEqual(cells, list(studio_common.ATTESTATION_COLUMNS))



    # ── documents ─────────────────────────────────────────────────────────

    def test_the_schema_document_and_the_spec_use_the_same_words(self):
        schema = read(VAULT / "SCHEMA.md")
        rules = self.spec["content_md"]
        for kind in rules["kinds"]:
            self.assertIn(f"`{kind}`", schema)
        for status in rules["statuses"]:
            self.assertIn(f"`{status}`", schema)
        for field in rules["required"] + rules["optional"]:
            self.assertIn(f"`{field}`", schema)
        headings = re.findall(r"^### `## (.+)`$", schema, re.M)
        self.assertEqual(headings, rules["sections"])

    def test_the_template_has_every_field_and_section(self):
        template = read(VAULT / "_templates" / "content-md.md")
        rules = self.spec["content_md"]
        for field in rules["required"] + rules["optional"]:
            self.assertRegex(template, rf"(?m)^{field}:")
        titles = re.findall(r"^## (.+)$", template, re.M)
        self.assertEqual(titles, rules["sections"])

    def test_the_rules_document_names_every_stage(self):
        rules = read(VAULT / "CLAUDE.md")
        for stage in self.spec["stages"]:
            self.assertRegex(rules, rf"\| \d \| {stage['id']} \|")
        for marker in (self.spec["ladder"]["unresolved_marker"],
                       self.spec["ladder"]["provisional_marker"]):
            self.assertIn(marker, rules)

    def test_the_pipelines_map_lists_every_pipeline(self):
        rows = dict(re.findall(r"^\| ([a-z0-9-]+) \| \[\[.+?\]\] \| .+? \| (.+?) \|$",
                               read(VAULT / "_Pipelines" / "_index.md"), re.M))
        self.assertEqual(set(rows), set(self.spec["pipelines"]))
        for name, status in rows.items():
            with self.subTest(pipeline=name):
                implemented = self.spec["pipelines"][name]["status"] == "implemented"
                self.assertEqual(status == "in use", implemented)

    def test_the_skill_defers_to_the_spec(self):
        skill = read(SKILL)
        front = studio_common.front_matter(skill)
        self.assertEqual(front["name"], "studio-pipeline")
        self.assertEqual(set(front), {"name", "description"})
        self.assertIn("studio/pipeline/spec.yaml", skill)
        self.assertIn("studio/vault/CLAUDE.md", skill)
        self.assertIn("spec.yaml wins", skill)
        for stage in self.spec["stages"]:
            self.assertIn(stage["id"], front["description"])

    def test_the_skill_uses_only_commands_that_exist(self):
        commands = {
            "studio_run.py": set(studio_run.build_parser()._subparsers._group_actions[0].choices),
            "content_md.py": set(content_md.build_parser()._subparsers._group_actions[0].choices),
        }
        texts = [read(SKILL), read(VAULT / "CLAUDE.md"), read(PIPELINE / "spec.yaml")]
        for script, known in commands.items():
            used = set()
            for text in texts:
                used |= set(re.findall(rf"python studio/pipeline/{re.escape(script)} ([a-z]+)", text))
            self.assertTrue(used)
            self.assertLessEqual(used, known, f"{script}: {used - known} is not a command")

    # ── the ledger ────────────────────────────────────────────────────────

    def test_the_ledger_does_not_claim_what_is_not_there(self):
        """A row that says an idea was carried, changed or rebuilt, and names a
        path in this repo, is a claim that the path exists."""
        ledger = read(STUDIO / "docs" / "IDEAS.md")
        legend = dict(re.findall(r"^\| (carried|changed|rebuilt|planned|deferred|dropped) \| (.+?) \|$",
                                 ledger, re.M))
        self.assertEqual(set(legend), {"carried", "changed", "rebuilt", "planned", "deferred", "dropped"})
        built = ("carried", "changed", "rebuilt")
        rows = 0
        for line in ledger.splitlines():
            cells = studio_common.table_cells(line) if line.startswith("|") else []
            if len(cells) < 3 or cells[-1] not in legend or cells[0] in legend:
                continue
            rows += 1
            named = re.findall(r"`((?:studio|plugins|\.claude|brush-designer)/[^`<>*]*)`", line)
            for path in named:
                with self.subTest(row=cells[0][:60], path=path):
                    if cells[-1] in built:
                        self.assertTrue((REPO / path).exists(),
                                        f"marked {cells[-1]}, and {path} is not in the repo")
        self.assertGreater(rows, 50)

    def test_the_ledger_marks_a_pipeline_as_the_spec_does(self):
        ledger = read(STUDIO / "docs" / "IDEAS.md")
        for name, cfg in self.spec["pipelines"].items():
            rows = [studio_common.table_cells(line) for line in ledger.splitlines()
                    if line.startswith("|") and f"| `{name}` |" in line]
            for cells in rows:
                with self.subTest(pipeline=name):
                    if cfg["status"] == "implemented":
                        self.assertIn(cells[-1], ("rebuilt", "carried", "changed"))
                    else:
                        self.assertEqual(cells[-1], "planned")


    def test_the_scripts_say_how_they_read_a_file(self):
        """This machine's default encoding is cp1252. A read that does not
        name utf-8 breaks on the first non-ASCII character."""
        for script in ("studio_common.py", "studio_run.py", "content_md.py"):
            source = read(PIPELINE / script)
            with self.subTest(script=script):
                bare = re.findall(r"\.(?:read_text|write_text)\(\s*\)", source)
                self.assertEqual(bare, [])
                self.assertNotRegex(source, r"(?<![\w.])open\(")


if __name__ == "__main__":
    unittest.main()
