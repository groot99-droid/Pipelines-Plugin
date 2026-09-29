---
title: "Creative-writing pipeline"
type: pipeline
folder: _Pipelines
tags: [pipelines, pipeline/creative-writing]
---

# Creative-writing pipeline

Turns one idea into a vault-integrated piece through six checkpointed stages,
rather than one freeform generation. Code lives outside this vault, at
`creative-writing/pipeline/` in the repo that contains it.

## Stages

**intake → reference pull → outline → draft → self-revision → vault integration**

Every stage is a checkpoint: nothing advances until the previous stage's output
has been reviewed. A failed stage leaves the run's state untouched, so retrying
the same command re-runs only that stage.

## Plot logic

The outline stage requires a **causal ledger**: a row per beat, each naming the
earlier beat it depends on and a phrase copied from that beat's `Changes`, so a
story is a chain of *but* and *therefore*, never *and then*. A checker verifies
the ledger and a failing one gets one repair pass; the report is kept beside the
outline as `plot_logic_report.md`. A **register** (`liminal`, `psychedelic`,
`cosmic`) can be chosen at intake to overlay a mode with a state track and shape
rules. Rules: [[CLAUDE.md]] ("Plot logic"). Reasoning and worked ledgers:
[[_Craft/_index|Craft notes]].

## What it reads

- `spec.yaml` — the single source of truth for stage order, stage prompts,
  per-mode rules, and the frontmatter schema. Both ways of running the pipeline
  read it; neither keeps its own copy of that logic.
- [[CLAUDE.md]] — the vault's voice and craft rules. `spec.yaml` summarizes and
  points back to it; it does not replace it.
- Actual vault passages, via `tools/vault_search.py` and a librarian pass, never
  a raw dump of whole files into whichever model is writing.

## What it writes

A new work under its mode's target folder, plus the four things that make it a
real vault citizen rather than a loose file: frontmatter, a `_index.md` entry, a
companion note under `_Annotations/`, and a reindex. That is the vault's own
5-step Maintenance procedure from [[CLAUDE.md]], run for you.

Output that has been drafted but **not** integrated waits in
[[_Idea_Library/_index|the Idea Library]] — a folder there is not equivalent to
integration.

## What it will not do

- **It will not write to the vault without explicit confirmation.** The
  integration stage prints a dry-run preview unless it is given `--confirm`
  (the skill asks for approval at the same point). Keep it that way.
- **It will not touch the 63 originals.** Those are certified verbatim
  transcriptions; the pipeline only adds new files.
- **It will not guess a mode.** `unclassified` is deliberately a stub — for a
  piece that isn't one of the four modes, it asks which register you want.

## Two ways to run it

- **The Claude Code skill** (`creative-writing-pipeline`) — conversational,
  walks the stages with you, and delegates drafting and reference-condensation
  to subagents. Needs no Ollama.
- **The standalone script** (`run_pipeline.py`) — a CLI that persists state and
  artifacts per run between invocations. Drafts through a pluggable backend
  (Ollama by default, Anthropic or Gemini opt-in).

Both read the same `spec.yaml`. Extending the pipeline to another mode means
adding an entry there, not changing either entry point.

## Related

- [[_Pipelines/_index|Pipelines index]]
- [[_Idea_Library/_index|Idea Library]] — this pipeline's staging area
- [[00_INDEX.md|The Living Archive — Index]] — what it references and adds to
