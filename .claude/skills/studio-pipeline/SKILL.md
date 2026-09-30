---
name: studio-pipeline
description: Walk one made thing through the studio's checkpointed pipeline (intake, context, recipe, execute, review, record), resolving and attesting its brand context before anything is run and leaving a Content MD in the studio vault. Use when the author wants a design system, palette, font pairing, style direction, UX review or accessibility audit made through the studio, a walkable 3D scene of the Writing Museum for a work they name, or asks to start, resume or park a studio run. Not for the creative-writing vault, which has its own pipeline.
---

# Studio pipeline

All paths in this file are relative to the **Pipelines repo root**, which is
your working directory. The layout:

- `studio/pipeline/` — `spec.yaml`, the bookkeeper `studio_run.py`, and the note
  writer `content_md.py`.
- `studio/vault/` — the Obsidian vault: Content MDs, the brand gates under
  `_Context/brand/`, `SCHEMA.md`, and the vault's own `CLAUDE.md`.
- `studio/pipeline/runs/<run-id>/` — one run's state and stage outputs.

Where a path is given vault-relative (for example `aurora/ui/console.md`) it
means relative to `studio/vault/`.

Read `studio/pipeline/spec.yaml` now, in full, before doing anything else. It is
the source of truth for the pipelines, the stage order, the stage instructions,
the gates and the refusals. Do not re-derive or improvise stage logic that
contradicts it. If it and this file ever disagree, **spec.yaml wins**.

Then read `studio/vault/CLAUDE.md` in full. It is authoritative for the rules
the spec summarises.

## What you are, and what the bookkeeper is

You are the executor. You do the work of every stage, in this session, because
the tools a stage calls exist only here.

`studio_run.py` is a bookkeeper. It keeps the run's state and refuses to mark a
stage done until what the spec declares for it is true. It never calls a model or
a tool. Run it with Bash. When it refuses, it is right: fix what it names. Never
edit `state.json` by hand, and never work around a refusal.

## How to run this

1. **Determine the pipeline.** Check `pipelines:` in the spec for the entry the
   request fits and that its `status` is `implemented`. If the request fits a
   pipeline that is not implemented, say so and stop; do not run its work under
   another pipeline's name. If it is unclear which pipeline the author means,
   ask. Do not guess.

2. **Start or resume the run.**

   ```
   python studio/pipeline/studio_run.py new --pipeline <name> --title "<working title>"
   python studio/pipeline/studio_run.py status
   python studio/pipeline/studio_run.py status <run-id>
   ```

   If the author is continuing something, read its note first. A note whose
   first Next Step names a run and a stage is a run to resume, not a new one.
   If that run is no longer under `studio/pipeline/runs/`, start a new run on
   the same note; do not recreate the old one.

3. **Walk the stages in the spec's `stages:` list, in order, one at a time.**
   For each stage:

   - Print its instructions, filled in for this run's pipeline, and follow them:

     ```
     python studio/pipeline/studio_run.py stage <run-id>
     ```

   - Do the stage's work. Save its output in the run folder under the filename
     the stage declares.
   - **Stop and show the author the result.** Every stage is a checkpoint. Do
     not go on until the author has reviewed this stage's output and says to
     continue. If they want changes, redo the stage; do not patch forward.
   - Then, and only then:

     ```
     python studio/pipeline/studio_run.py advance <run-id>
     ```

   - To redo an earlier stage, go back one stage at a time. It clears the
     go-aheads from that stage on:

     ```
     python studio/pipeline/studio_run.py back <run-id> --why "<what is being redone>"
     ```

4. **Intake.** Capture the brief in the author's words. Settle which note this
   run reads and writes, and tell the bookkeeper:

   ```
   python studio/pipeline/studio_run.py note <run-id> <project>/<kind>/<slug>.md
   ```

   The path is always three parts: a project, the kind this pipeline makes, and
   the file. Use `one-offs/<kind>/<slug>.md` when the author names no project.
   Never infer a project. Do not create the note; it is first written at record,
   or earlier by a flush or a park.

5. **Context.** Run `facts` first. It reports what is on disk; it does not read
   the gates for you.

   ```
   python studio/pipeline/studio_run.py facts <run-id>
   ```

   Read every gate file it lists, in full. Resolve each needed constraint on the
   ladder in `studio/vault/CLAUDE.md` and write `attestation.md` in the shape the
   stage instructions give: one row for each constraint `facts` lists, in its
   words.

   - A constraint a gate declares unresolved is not answered by that gate.
   - If a constraint is unresolved, **ask the author.** If they state it, the
     row's Level becomes `STATED`, its Source names the author and today's date,
     and its State is `resolved`. If they do not, park the run (see below).
   - Never fill a constraint from general knowledge, a reference library, or the
     design catalog.
   - An L0 row names its own gate's file and the section. An L1 row quotes at
     least three words from one bullet of the note's Decisions in Force. A line
     recalled from a `PROVISIONAL` decision is still `PROVISIONAL`.
   - The bookkeeper checks that what each row cites exists. It cannot check that
     the section you cite says what you say it does. Cite only what you read,
     and quote only what is there. The author reads the attestation to check.

6. **Recipe.** Every tool call execute will make, with every parameter and the
   source of each. A parameter with no source does not go in; ask. State what
   leaves the machine.

7. **Execute needs an explicit go-ahead.** Showing the recipe and hearing "looks
   good" about the recipe is the recipe checkpoint. Separately ask whether to
   run it, and only on a clear yes:

   ```
   python studio/pipeline/studio_run.py confirm <run-id> execute --words "<what the author said>"
   ```

   Record the confirmation **before** running anything. Then run the recipe as
   written and nothing else. Write `execute_log.md` as you go: what was run and
   what came back, not what was planned.

   Call no tool whose name contains a word listed under `connectors: never` in
   the spec.

8. **Review.** One line for each output against each attested constraint, and
   how it was checked. A failed output is a finding. A retry is a new execute
   with its own go-ahead.

9. **Record is the highest-stakes step.** It writes into the vault.

   - Write `note_update.md` in the run folder: the **complete** note as it should
     read afterwards, per `studio/vault/SCHEMA.md`.
   - Build the Timeline entry from `execute_log.md` and `review.md` only. Never
     from `recipe.md`. Leave every existing Timeline entry exactly as it is.
   - Under Decisions in Force, record each constraint the attestation derived as
     `PROVISIONAL, derived from [[a]], [[b]], [[c]]: ...`, citing the same notes,
     and each one the author stated as `STATED <date>: ...`, each on a bullet of
     its own that names the constraint. List each one's gate under
     `context_brand`. Leave a `PROVISIONAL` decision already in the note as it
     is, unless the author has now stated it. The writer refuses the note
     otherwise.
   - Preview it. This writes nothing to the vault:

     ```
     python studio/pipeline/content_md.py plan <run-id>
     ```

   - Show the author `record_plan.md`. Only after a clear yes to **that plan**:

     ```
     python studio/pipeline/studio_run.py confirm <run-id> record --words "<what the author said>"
     python studio/pipeline/content_md.py apply <run-id> --confirm
     python studio/pipeline/studio_run.py advance <run-id>
     ```

     Advance straight after apply: the yes to the plan was this stage's
     checkpoint. The stage ends only with a record write; a flush or a park
     does not finish it.

   - If you change `note_update.md` after planning, plan again and show it
     again. The writer refuses a note the author has not seen.

   Never write a note into the vault with Write or Edit.

## Writing a brand gate

The `brand-gate` pipeline runs the same six stages and writes one gate as well
as its note. At intake, name the gate:

```
python studio/pipeline/studio_run.py gate <run-id> <gate>
```

It needs no brand context, so its attestation says so, with no table. Execute
is the interview: ask the recipe's questions and log the author's answers
verbatim. Never offer answers to choose from; a gate records taste, and options
would be generated. Review builds the gate from the transcript alone. At record,
write the gate before the note:

```
python studio/pipeline/gate_md.py plan <run-id>
python studio/pipeline/studio_run.py confirm <run-id> gate --words "<what the author said>"
python studio/pipeline/gate_md.py apply <run-id> --confirm
```

Show the author `gate_plan.md`, which holds the whole gate, before the confirm.

## Parking a run

When a constraint cannot be resolved and the author has not stated it:

```
python studio/pipeline/studio_run.py park <run-id> --constraint <name> --needs "<what would resolve it>"
```

If the run has no note yet, set one first with `studio_run.py note`. Then put the
blocker in the note: write `note_update.md` with `status: blocked` and, as the
first item under Next Steps, an open checkbox that names the constraint
(`park.md` in the run folder has the line). Then:

```
python studio/pipeline/content_md.py plan <run-id> --as park
python studio/pipeline/studio_run.py confirm <run-id> park --words "<what the author said>"
python studio/pipeline/content_md.py apply <run-id> --as park --confirm
```

Parking is a correct result. Say so plainly; do not apologise for it or try to
route around it.

To resume once the constraint is resolved: `studio_run.py unpark <run-id>`.

## Stopping before the run is finished

If the session is ending partway through a run, the note must say where. If the
run has no note yet, set one first with `studio_run.py note`. Write
`note_update.md` with the first Next Step naming the run id and the stage to
resume, and a Timeline entry for what this session actually did. Once context
is done, a flush owes the same `PROVISIONAL` and `STATED` decisions a record
does. Then:

```
python studio/pipeline/content_md.py plan <run-id> --as flush
python studio/pipeline/studio_run.py confirm <run-id> flush --words "<what the author said>"
python studio/pipeline/content_md.py apply <run-id> --as flush --confirm
```

A flush does not advance the run. A session that ends without one leaves only
the run folder behind, and the note says nothing of it.

## What this skill does not do

- It does not read, search or write anything under `creative-writing/vault/`.
  If the author wants a made thing to draw on one of those works, they name the
  work at a checkpoint and you read that work only.
  The `scene-3d` pipeline is that case: the work is named at intake, and only
  that work, its `_ChunkTags` sidecar and its chunks are read, through
  `writing-museum/build/build_museum.py` (see `writing-museum/README.md`).
- It does not write or edit a file under `studio/vault/_Context/brand/`, except
  a gate a `brand-gate` run writes through `gate_md.py` after the author's yes.
  A change to `tokens.json` is proposed as a diff and left for the author.
- It does not edit anything under `plugins/ui-design/`. That plugin is published
  and its catalog files are fingerprinted; run its scripts, do not change them.
- It does not start a pipeline whose status is not `implemented`.
