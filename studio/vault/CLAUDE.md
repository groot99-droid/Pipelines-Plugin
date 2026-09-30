# CLAUDE.md — the studio vault

This file is authoritative for anything that makes a thing through the studio or
writes a note into this vault. `studio/pipeline/spec.yaml` is its
machine-readable form and points back here. If they disagree on a rule, this
file is right and the spec is to be fixed.

Paths are relative to the Pipelines repo root unless they start inside the vault.

## Purpose and scope

This vault is the studio's memory. Each made thing has one note, a **Content
MD**, that records how it was made, what is decided about it, and what happens
next. [SCHEMA.md](SCHEMA.md) defines the note.

Notes are written by the author, in Obsidian, and by pipelines, through
`studio/pipeline/content_md.py`. Nothing else writes here.

This vault is separate from `creative-writing/vault/`. That vault holds 63
verbatim works under its own rules and is not touched from here.

## The prime rule

**Nothing is made before its context is resolved, attested and sourced.**

Context carries the why. A pipeline carries the how. Running the how without the
why produces work that is off-brand, so it does not happen.

Output is a function of the input and the matched context, and nothing else. A
constraint that cannot be sourced is a constraint the studio does not have.
Derived is allowed and labelled. Invented is not allowed at all.

## The six stages

Every pipeline runs the same six, in order. Every one is a checkpoint: show the
author the stage's output and stop. Go on only when they say so. If they want
changes, redo the stage. Do not patch forward.

Stopping is yours to do. The bookkeeper advances a stage when it is told to and
the stage's checks pass; it cannot tell whether the author was shown anything.

| # | Stage | Leaves | The point |
|---|---|---|---|
| 1 | intake | `brief.md` | what is being made, in the author's words |
| 2 | context | `attestation.md` | what constrains it, and where each constraint came from |
| 3 | recipe | `recipe.md` | exactly what will be run, and the source of every value |
| 4 | execute | `execute_log.md`, artifacts | run the recipe and nothing else. Needs the author's go-ahead |
| 5 | review | `review.md` | each output against each constraint |
| 6 | record | the note | what was done, what is decided, what is next. Needs the author's go-ahead |

`python studio/pipeline/studio_run.py stage <run-id>` prints the current stage's
instructions, filled in for the run's pipeline. Follow those. Do not improvise a
stage that contradicts them.

To redo an earlier stage, go back one stage at a time:

```
python studio/pipeline/studio_run.py back <run-id> --why "<what is being redone>"
```

It clears the go-aheads from that stage on, and what the run kept from them. A
retried execute therefore needs a new go-ahead and a new log.

## Resolving context: the ladder

For each constraint a pipeline needs, stop at the first level that resolves it.

| Level | It resolves when | Cite | State |
|---|---|---|---|
| **L0 authored** | the gate file exists in `_Context/brand/` **and** the constraint is not one the gate declares unresolved | the file, and `section N` | resolved |
| **L1 recalled** | a note whose `context_brand` names the gate states the constraint under Decisions in Force | the note as `[[note]]`, and the line in double quotes, copied exactly | resolved |
| **L2 derived** | no note states it, and it can be inferred from **at least three** notes of the same kind. Weigh a complete note over one in progress, and a recent one over an old one | every note used, as `[[note]]` | `PROVISIONAL` |
| **STATED** | the author states it at the context checkpoint | the author, and the date | resolved |
| **L3 unresolved** | none of the above | nothing | `UNRESOLVED` |

**Authored is not complete.** A gate says, in its Unresolved section, what it
does not answer; `studio_run.py facts` prints each such section as a DECLARED
GAP. A run needing one of those treats it as unresolved, though the file exists
and loads. Reading "the file exists" as "the question is answered" is the
failure this rule exists to prevent.

**Fewer than three notes is a coincidence, not precedent.**

**At L3, ask the author.** If they state the constraint, record it as stated; it
becomes a Decision in Force when the note is written, and the next run recalls
it at L1. If they do not, park the run. Never fill the gap from general
knowledge, from a reference library, or from the design catalog.

A note's own Decisions in Force bind a run exactly as a gate does. Read them in
the context stage, beside the gates.

## The attestation

The context stage writes `attestation.md` and shows it before any tool is
called. One row for every constraint the pipeline needs, in the words
`studio_run.py facts` prints:

```
| Constraint | Gate | Level | Source | State |
|---|---|---|---|---|
| palette | color_science | L0 AUTHORED | color_science.context.md section 2 | resolved |
| dense layout | visual_identity | L1 RECALLED | [[ops-console]] "dense layout, one screen, no scrolling" | resolved |
| key light direction | visual_identity | L2 DERIVED | [[aurora-lead]], [[harbor-dusk]], [[north-gate]] | PROVISIONAL |
| line work only | visual_identity | STATED | the author, 2026-09-28 | resolved |
| imagery motifs | visual_identity | L3 | nothing: visual_identity declares it unresolved | UNRESOLVED |
```

Inside a table cell, the pipe of a wikilink alias is written `\|`.

A run does not leave the context stage unless every needed constraint has
exactly one row, no row is at L3, and each row is backed the way its level
requires:

- an L0 row names its own gate's file, and only sections the gate answers;
- every note an L1 row cites is in the vault and lists the gate under
  `context_brand`, and each quoted line, at least three words, is in one bullet
  under Decisions in Force, not in struck-out text;
- the notes an L2 row cites are three, in the vault, and of the kind being made;
- a STATED row gives a real date, not after today and not before the run.

A line recalled from a decision marked `PROVISIONAL` is still a derivation. Its
row's State is `PROVISIONAL`, and the note keeps the marker.

When the context stage is done, the bookkeeper keeps the rows. Every later write
is held to them, whatever happens to `attestation.md` afterwards.

**That is a check of the record, not of the truth.** Nothing but a reader can
tell whether section 2 really states the constraint the row says it does. That
is what the checkpoint is for: the author reads the attestation.

## Parking

A run that cannot be grounded is parked. The blocker goes into the note as the
first item under Next Steps, saying which constraint is missing and what would
resolve it, and the note's status becomes `blocked`. A person returning later
reads why, in the note.

Parking is a correct result, not a failure.

## The note

- **One note per made thing.** A second session updates it. A run reads and
  writes one note; once it has written, it cannot be pointed at another.
- **A run writes a note at `<project>/<kind>/<slug>.md`** and nowhere else.
  `one-offs/` is the project of a piece that has none.
- **The note is not created at intake.** Its first write is at record, at a
  flush, or at a park, because every write is previewed and confirmed. A session
  that ends without a flush leaves only the run folder behind.
- **Overview and Next Steps come first.**
- **What was derived is recorded as derived**, under Decisions in Force, marked
  `PROVISIONAL` and citing the same notes. What the author stated is recorded as
  `STATED`, with the date. Otherwise the next run recalls a derivation as if it
  were a decision. Each takes a bullet of its own, and its gate is listed under
  `context_brand`. Once context is done, every write owes them: record, flush
  and park.
- **A `PROVISIONAL` decision stays as it is** until the author states the
  constraint. A later run changes it only with a `STATED` row.
- **The record stage ends with a record write.** A flush or a park writes the
  note but does not finish the stage.
- **The Timeline is append-only.** A wrong entry is corrected by a new one.
- **Never record a step that was not taken.** A Timeline entry is built from
  `execute_log.md` and `review.md`. Never from `recipe.md`, which is what was
  planned.
- **Next Steps is rewritten in full** each session.
- **State lives in the note.** `studio/pipeline/runs/` is bookkeeping. A run's
  folder may be deleted once the run is complete or abandoned, not before: a
  flushed or parked note names a run that must still be there. If the run a note
  names is gone, start a new run on the same note. If stopping would lose
  something the note does not say, the note is wrong; fix it first.

### Stopping partway

A session that stops before the last stage ends with a flush: a note update
whose first Next Step names the run and the stage to resume, with a Timeline
entry for what this session did. It is previewed and confirmed like any other
write:

```
python studio/pipeline/content_md.py plan <run-id> --as flush
python studio/pipeline/studio_run.py confirm <run-id> flush --words "<what the author said>"
python studio/pipeline/content_md.py apply <run-id> --as flush --confirm
```

## Writing into the vault

Every write is previewed and confirmed. `content_md.py plan` writes nothing to
the vault. `content_md.py apply` without `--confirm` writes nothing. With it,
apply still refuses unless the author's go-ahead was recorded after the plan was
made. Keep it that way.

Never write a note with an editor tool in place of `content_md.py`.

## Brand gates

The files in `_Context/brand/` are the author's. They encode taste and prior
decisions, which cannot be generated.

- Never write, edit or create a gate file from a search result, a library or an
  inference. A gate is transcribed from what the author says.
- `tokens.json` follows the same rule: **the author commits; an agent proposes.**
  A proposed change is a diff and a statement of what it would break.
- The three authored gates were carried unchanged from Creative-Headquarters, so
  their provenance sections name paths from that repo. `spec.yaml` lists what
  each path means here, under `known_conflicts`.

## Two token authorities

| | Studio surfaces | Product and client work |
|---|---|---|
| What | the studio's own interfaces | anything made for a project |
| Authority | `tokens.json` and the three gates | that project's own design system |
| A pipeline's role | proposes, never commits | sole author |

The studio palette and typeface do not travel to a client project. Reaching for
them because they are "the studio's" is a category error.

## What leaves the machine

- The recipe says what leaves the machine, and to where, before execute is
  confirmed.
- Nothing under `creative-writing/vault/` is read into a brief, a recipe or a
  prompt unless the author names the work at a checkpoint.
- A note never holds a presigned link, a share link or a credential. The lint
  knows signed query parameters, the share links of a few hosts, and a few key
  prefixes. A shape it does not know passes, so do not rely on it: leave them out.
- No pipeline calls a connector tool that shares, publishes, invites or deploys.

## Refusals

These hold always.

- A pipeline that is not `implemented` does not start.
- A run with an unresolved constraint does not advance.
- A derived constraint is never presented as an authored one.
- Nothing that spends, runs heavy compute, or writes outside the run folder
  happens before the author's go-ahead.
- A Timeline step that was not taken is never recorded.
- Nothing is written into the vault without a preview and a yes.
- A brand gate is never generated.

## What is not enforced

Said plainly, so nobody relies on a guarantee that does not exist.

- A pipeline is entered by choice. A connector can be called without one.
- The bookkeeper can refuse to mark a stage done. It cannot refuse a tool call.
- A checkpoint stage advances when `advance` is run. The bookkeeper cannot tell
  whether the author reviewed it.
- It records that the author gave a go-ahead because it is told so. It cannot
  hear the author.
- It checks what an attestation cites. It cannot check that the citation says
  what the row claims.
- It does not check that the level chosen is the first one on the ladder that
  holds. A constraint a gate answers could be written as `STATED`; the author
  sees that at the checkpoint.
- It checks that a go-ahead for execute was recorded, and that the log is not
  older than it. It sees nothing that was run and not logged.
- A note edited by hand in Obsidian passes through none of this. The lint reads
  it afterwards.

## Maintenance

After adding or changing a note by hand:

```
python studio/pipeline/content_md.py lint --all
```

After changing `spec.yaml`, a gate, `tokens.json`, `SCHEMA.md` or this file:

```
python -m unittest discover -s studio/pipeline/tests
```

After adding a pipeline, a skill or an agent:

```
python plugins/ui-design/maintenance/generate-index.py
python plugins/ui-design/maintenance/verify.py
```
