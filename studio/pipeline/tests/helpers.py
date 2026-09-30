"""Shared by the studio tests. Every test runs against temporary folders: the
real vault and the real run folder are never touched.

The machinery is the real spec's: its stages, ladder, note rules and pipelines.
The brand context is not. Each test writes a spec whose gates, and what each
pipeline needs from them, are the fixture below, so these tests do not change
when the studio's own gates are replaced. test_context.py is where the real
context is checked.
"""

import contextlib
import copy
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

PIPELINE = Path(__file__).resolve().parent.parent
REPO = PIPELINE.parent.parent
sys.path.insert(0, str(PIPELINE))

import content_md  # noqa: E402
import studio_common  # noqa: E402
import studio_run  # noqa: E402

# A made-up context with the shapes the ladder must handle: a gate with a
# declared gap, a gate with none, a gate whose gap is its last section, and a
# gate nobody has written.
FIXTURE_GATES = {
    name: {"file": f"{name}.context.md", "must_answer": answer}
    for name, answer in (("fixture_look", "What the surfaces look like."),
                         ("fixture_type", "Typefaces and scale."),
                         ("fixture_colour", "The palette and what it means."),
                         ("fixture_voice", "How things are worded."))
}


def fixture_gate(name, answers, gap=None):
    """A gate file in the shape gate_md.py writes: provenance, a glossary that
    answers nothing, numbered answers, and an Unresolved section last."""
    lines = [f"# {name}", "", "## 0. Provenance", "",
             "Answered by the author on 2026-09-01, in run fixture-000000.", "",
             "## 1. Routing glossary", "", "Where to look.", ""]
    for number in answers:
        lines += [f"## {number}. {name} topic {number}", "", f"What {name} says in section {number}.", ""]
    if gap:
        lines += [f"## {gap[0]}. Unresolved", "", f"- {gap[1]}", ""]
    return "\n".join(lines)


# The files written for the authored fixture gates. fixture_voice has none.
FIXTURE_FILES = {
    "fixture_look": fixture_gate("fixture_look", range(2, 7), ("7", "generated imagery")),
    "fixture_type": fixture_gate("fixture_type", range(2, 7)),
    "fixture_colour": fixture_gate("fixture_colour", range(2, 5), ("5", "working space")),
}
FIXTURE_NEEDS = [
    {"gate": "fixture_look", "needs": ["interface identity", "off-limits list", "scope"]},
    {"gate": "fixture_type", "needs": ["the studio scale", "hierarchy", "scope boundary"]},
    {"gate": "fixture_colour", "needs": ["palette", "semantic binding", "the three contrast floors"]},
]


def fixture_spec():
    """The real spec, with the fixture in place of its brand context."""
    spec = yaml.safe_load(studio_common.SPEC_PATH.read_text(encoding="utf-8"))
    spec["gates"] = copy.deepcopy(FIXTURE_GATES)
    spec["known_conflicts"] = []
    for cfg in spec["pipelines"].values():
        if cfg.get("status") == "implemented" and cfg.get("requires_context"):
            cfg["requires_context"] = copy.deepcopy(FIXTURE_NEEDS)
            cfg["open"] = ["fixture_look states no scope for itself; `scope` resolves as STATED."]
        elif cfg.get("requires_context"):
            cfg["requires_context"] = [{"gate": "fixture_voice", "needs": ["wording"]}]
    return spec


NOTE = "one-offs/ui/ops-console.md"

GOOD_NOTE = """---
id: cmd_20260928_ops-console
type: content-md
kind: ui
title: Ops console
status: in-progress
created: 2026-09-28
updated: 2026-09-28
pipelines: [ui-direction]
context_brand: [fixture_look, fixture_colour]
tags: [ui]
---

## Overview

A design direction for an operations console. One search run so far.

## Next Steps

- [ ] Review the proposed palette against the contrast floors

## Timeline

### 2026-09-28 · ui-direction · ops-console-aaaaaa
Ran one design-system search. Matched category: Analytics Dashboard.

## Method

```
search.py "internal analytics dashboard" --design-system --json
## not a heading, this line is inside a code fence
```

## Decisions in Force

- STATED 2026-09-28: dense layout, one screen, no scrolling.
"""

HEADER = "| Constraint | Gate | Level | Source | State |\n|---|---|---|---|---|\n"


def precedent(name, kind="ui", gates=("fixture_look",), decisions=("Key light sits camera left.",),
              status="complete"):
    """A small, valid note to recall from or derive from."""
    lines = "\n".join(f"- {line}" for line in decisions)
    return f"""---
id: cmd_20260901_{name}
type: content-md
kind: {kind}
title: {name}
status: {status}
created: 2026-09-01
updated: 2026-09-01
pipelines: [ui-direction]
context_brand: [{', '.join(gates)}]
---

## Overview

A finished piece, kept as precedent.

## Decisions in Force

{lines}
"""


class StudioCase(unittest.TestCase):
    """A temporary vault, gate folder and run folder around the real spec."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="studio-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.runs = self.root / "runs"
        self.vault = self.root / "vault"
        self.context = self.vault / "_Context" / "brand"
        self.context.mkdir(parents=True)
        self.runs.mkdir()
        self.spec_path = self.root / "spec.yaml"
        self.spec_path.write_text(yaml.safe_dump(fixture_spec(), sort_keys=False, allow_unicode=True),
                                  encoding="utf-8")
        self.env = studio_common.Env(self.spec_path, runs_dir=self.runs, vault_dir=self.vault,
                                     context_dir=self.context)
        for name, text in FIXTURE_FILES.items():
            (self.context / FIXTURE_GATES[name]["file"]).write_text(text, encoding="utf-8")

    def folders(self):
        return ["--spec", str(self.spec_path), "--runs-dir", str(self.runs),
                "--vault-dir", str(self.vault), "--context-dir", str(self.context)]

    def call(self, module, *arguments):
        """(exit code, stdout, stderr) of one command, run in this process."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = module.main(self.folders() + [str(a) for a in arguments])
        return code, out.getvalue(), err.getvalue()

    def run_cmd(self, *arguments):
        return self.call(studio_run, *arguments)

    def note_cmd(self, *arguments):
        return self.call(content_md, *arguments)

    def new_run(self, run_id=None, pipeline="ui-direction"):
        if run_id is None:
            self.count = getattr(self, "count", 0) + 1
            run_id = f"ops-console-{self.count:06d}"
        code, out, err = self.run_cmd("new", "--pipeline", pipeline, "--title", "Ops console",
                                      "--run-id", run_id)
        self.assertEqual(code, 0, err)
        return run_id

    def put(self, run_id, name, text):
        path = self.runs / run_id / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def place(self, relative, text):
        path = self.vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def state(self, run_id):
        return studio_common.load_state(self.env, run_id)

    def rows(self, pipeline="ui-direction", without=()):
        """One L0 row for each constraint the pipeline needs, as the spec lists them."""
        lines = []
        for need in self.env.pipeline(pipeline)["requires_context"]:
            gate = self.env.spec["gates"][need["gate"]]
            section = studio_common.gate_sections(self.env, need["gate"])["answers"][0]["section"]
            for wanted in need["needs"]:
                if wanted in without or need["gate"] in without:
                    continue
                lines.append(f"| {wanted} | {need['gate']} | L0 AUTHORED | "
                             f"{gate['file']} section {section} | resolved |")
        return lines

    def attestation(self, extra=(), without=(), pipeline="ui-direction", prose=""):
        rows = self.rows(pipeline, without) + list(extra)
        return ("# Attestation: run\n\nPIPELINE: ui-direction\n\n## Context resolution\n\n"
                + HEADER + "\n".join(rows) + "\n\n## Key constraints extracted\n\n"
                "- Ten colours, four of them bound to states.\n" + prose)

    def through(self, run_id, last_stage, note=NOTE, note_text=GOOD_NOTE):
        """Advance a run through every stage up to and including `last_stage`."""
        order = [stage["id"] for stage in self.env.stages]
        for stage in order[: order.index(last_stage) + 1]:
            if stage == "intake":
                self.put(run_id, "brief.md", "An operations console.\n")
                self.assertEqual(self.run_cmd("note", run_id, note)[0], 0)
            elif stage == "context":
                self.put(run_id, "attestation.md", self.attestation())
            elif stage == "recipe":
                self.put(run_id, "recipe.md", "One search.\n")
            elif stage == "execute":
                self.assertEqual(self.run_cmd("confirm", run_id, "execute", "--words", "run it")[0], 0)
                self.put(run_id, "execute_log.md", "Ran one search. Exit 0.\n")
            elif stage == "review":
                self.put(run_id, "review.md", "Category matches the brief.\n")
            elif stage == "record":
                self.put(run_id, "note_update.md", note_text)
                code, _, err = self.note_cmd("plan", run_id)
                self.assertEqual(code, 0, err)
                self.assertEqual(self.run_cmd("confirm", run_id, "record", "--words", "write it")[0], 0)
                self.assertEqual(self.note_cmd("apply", run_id, "--confirm")[0], 0)
            code, out, err = self.run_cmd("advance", run_id)
            self.assertEqual(code, 0, f"{stage}: {err}")
