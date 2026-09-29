---
title: "Studio pipeline"
type: pipeline
folder: _Pipelines
tags: [pipelines, pipeline/studio]
---

# Studio pipeline

Makes one thing through six checkpointed stages and leaves a note behind, rather
than one freeform generation. Code lives outside this vault, at
`studio/pipeline/` in the repo that contains it.

## Stages

**intake → context → recipe → execute → review → record**

Every stage is a checkpoint: the skill stops, shows the stage's output, and
waits. Two stages need more than a review. **Execute** and **record** each need
an explicit go-ahead, which the skill records before it does the work.

A failed stage leaves the run at the same stage, with the refusal logged, so
advancing again re-checks only that stage.

## What it reads

- `spec.yaml` — the single source of truth for the pipelines, the stages, the
  gates and the refusals.
- [[CLAUDE.md]] — the rules. `spec.yaml` summarises and points back to it.
- [[_Context/brand/README|The brand gates]] a pipeline requires, in full.
- The note being continued: its Overview, Next Steps, Decisions in Force and
  Method.
- Past notes, to recall a decision or derive one from at least three.

## What it writes

One Content MD per made thing, per [[SCHEMA.md]]: a Timeline entry for the
session, Next Steps rewritten, the decisions now in force, and the method as it
was run.

Everything else a run produces sits in `studio/pipeline/runs/<run-id>/`, which is
bookkeeping and can be deleted once the run is complete or abandoned.

## What it will not do

- **It will not write to the vault without a preview and a yes.**
- **It will not make anything before its context is attested.**
- **It will not guess a constraint.** It asks, and if there is no answer it
  parks the run and writes the blocker into the note.
- **It will not write a brand gate or change `tokens.json`.** It proposes.
- **It will not touch `creative-writing/vault/`.**
- **It will not start a pipeline that is not implemented.**

## What it cannot do

It cannot stop a connector being called outside a pipeline. A pipeline is entered
by choice.

It cannot tell whether what an attestation says is true. It checks that what a
row cites exists. [[CLAUDE.md]] lists the rest under "What is not enforced".

## How to run it

The Claude Code skill `studio-pipeline`, in a session opened on the repo. It
walks the stages with you and keeps the run's state through
`studio/pipeline/studio_run.py`.

There is no standalone script. The connectors a stage calls exist only inside a
live Claude Code session.

## Related

- [[_Pipelines/_index|Pipelines index]]
- [[SCHEMA.md]]
- [[CLAUDE.md]]
