# Studio

Makes one thing at a time through six checkpointed stages, and leaves a note
behind that says how it was made, what is decided about it, and what happens
next.

It carries the ideas of Creative-Headquarters ("Studio Headless OS") into this
repo. Most of that repo was a specification that no code implemented. What it
contained is in [docs/INVENTORY.md](docs/INVENTORY.md). What became of each idea
is in [docs/IDEAS.md](docs/IDEAS.md).

```
studio/
  pipeline/
    spec.yaml          the contract: gates, pipelines, stages, refusals
    studio_run.py      the bookkeeper: keeps a run's state, refuses what the spec refuses
    content_md.py      lints a note, previews a write, writes after a go-ahead
    studio_common.py   what those two share
    tests/
    runs/<run-id>/     one run's state and stage outputs. Ignored by git
  vault/               the Obsidian vault. Open THIS folder in Obsidian
    CLAUDE.md          the rules, authoritative
    SCHEMA.md          the note
    _Context/brand/    the brand gates, and tokens.json
    _Pipelines/        a map of the pipelines
    _templates/
  docs/
```

The skill is at `.claude/skills/studio-pipeline/SKILL.md`, at the repo root.

## The six stages

**intake → context → recipe → execute → review → record**

| Stage | Leaves | |
|---|---|---|
| intake | `brief.md` | what is being made, in the author's words |
| context | `attestation.md` | every constraint it needs, and where each came from |
| recipe | `recipe.md` | exactly what will be run, and the source of every value |
| execute | `execute_log.md` | runs the recipe. Needs an explicit go-ahead |
| review | `review.md` | each output against each constraint |
| record | the note | writes into the vault. Needs an explicit go-ahead |

Every stage is a checkpoint: the skill stops, shows the author the stage's
output, and waits.

## The rule underneath

**Nothing is made before its context is resolved, attested and sourced.**

A constraint comes from a brand gate the author wrote, from a decision recorded
in a past note, or from precedent across at least three past notes. If it comes
from none of those, the pipeline asks. If there is no answer it parks the run and
writes the reason into the note. It does not guess.

## Pipelines

Nine are declared in `spec.yaml`. One is implemented.

| Pipeline | Makes | Status |
|---|---|---|
| `ui-direction` | a design direction for a surface or a product, through `plugins/ui-design` | implemented |
| `ui-build` | markup and CSS in which every value is a token | not yet |
| `brand-gate` | one brand gate, transcribed from the author | not yet |
| `brush` | a brush and an importable file | not yet |
| `still-image`, `video-shot`, `music-cue`, `edit-2d`, `scene-3d` | through connectors | not yet |

A pipeline that is not implemented is a real entry: what it needs, what it
carries from the skill it replaces, and what is still open. It does not start.

To add one, add an entry under `pipelines:` with `status: implemented`. The
stages do not change.

## Running it

In a Claude Code session opened on this repo, use the `studio-pipeline` skill.

There is no standalone script. The tools a stage calls exist only inside a live
session. The two commands below keep the books and write the note; the skill
runs them.

```
python studio/pipeline/studio_run.py new --pipeline ui-direction --title "Ops console"
python studio/pipeline/studio_run.py stage   <run-id>     # the current stage's instructions
python studio/pipeline/studio_run.py facts   <run-id>     # what is on disk for each gate
python studio/pipeline/studio_run.py advance <run-id>     # mark the stage done, if its checks pass
python studio/pipeline/studio_run.py status               # every run

python studio/pipeline/content_md.py lint --all
python studio/pipeline/content_md.py plan  <run-id>       # preview; writes nothing to the vault
python studio/pipeline/content_md.py apply <run-id> --confirm
```

Exit codes: 0 done, 1 refused, 2 usage or configuration error.

Needs Python 3 and `pyyaml` (`pip install -r studio/pipeline/requirements.txt`).

## What it writes, and when

| Where | When |
|---|---|
| `studio/pipeline/runs/<run-id>/` | freely. Bookkeeping; safe to delete once the run is complete or abandoned |
| `studio/vault/` | only through `content_md.py apply --confirm`, after a plan and a go-ahead recorded after that plan, and only at `<project>/<kind>/<slug>.md` |
| anywhere else | only in `execute`, only what the recipe named, only after a go-ahead |

`content_md.py apply` without `--confirm` is a dry run.

## What it does not do

- It does not read or write `creative-writing/vault/`.
- It does not write a brand gate or change `tokens.json`. It proposes a change.
- It does not edit `plugins/ui-design/`. It runs that plugin's scripts.
- **It does not stop a tool being called outside a pipeline.** The bookkeeper can
  refuse to record that a stage is done. It cannot refuse a tool call.
- **It does not know whether the author reviewed a stage**, or gave a go-ahead.
  It advances when told to, and records a go-ahead on the skill's word.
- **It does not know whether an attestation is true.** It checks that every
  needed constraint has a row and that what each row cites exists. Whether the
  gate says what the row claims is for the author to read.

`studio/vault/CLAUDE.md` lists the rest under "What is not enforced".

## Checking it

```
python -m unittest discover -s studio/pipeline/tests
```

The tests run against temporary folders and the real spec. They check that each
refusal refuses, and that the spec, the gate folder, the documents and the skill
agree with one another.

After adding a skill or an agent, regenerate the repo index:

```
python plugins/ui-design/maintenance/generate-index.py
python plugins/ui-design/maintenance/verify.py
```
