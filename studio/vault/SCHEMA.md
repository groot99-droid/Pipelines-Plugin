# Content MD — Schema

A **Content MD** is the durable record of one made thing: a character, a design,
an audio piece, a shot, a brush. It captures the exact steps that produced it,
what state it is in, and what happens next.

It is the unit of memory for the studio. No session state persists between
tasks. A Content MD is read cold and is sufficient to resume the work.

`studio/pipeline/spec.yaml` holds the machine-readable form of this file, under
`content_md:`. `studio/pipeline/content_md.py lint` checks a note against it.

---

## The one rule

**The first screenful must answer: what is this, and what do I do next.**

`## Overview` and `## Next Steps` come first, always, before any detail. A person
opening the file in Obsidian and an agent reading the first 40 lines must both
get a usable answer without scrolling. Everything below those two sections is
reference material for when the answer is not enough.

---

## File placement

```
studio/vault/
├── SCHEMA.md              ← this file
├── CLAUDE.md              ← the rules every pipeline follows
├── _templates/
│   └── content-md.md      ← Obsidian template
├── _Context/brand/        ← the brand gates
├── _Pipelines/            ← a map of the pipelines that write here
├── one-offs/
│   └── <kind>/
│       └── <slug>.md      ← a piece with no project
└── <project>/
    └── <kind>/
        └── <slug>.md      ← e.g. aurora/character/aurora-lead.md
```

A folder whose name starts with `_` or `.` never holds a Content MD.

A pipeline writes a note only at `<project>/<kind>/<slug>.md`, where `<kind>` is
one of the Kinds below. A piece with no project goes under `one-offs/`. Names use
letters, digits, spaces, dots, underscores and hyphens.

One Content MD per made thing, not per session. Resuming work **updates** the
existing file: it appends to `## Timeline` and rewrites `## Next Steps`. It does
not create a second file.

---

## Frontmatter

YAML, Obsidian-native.

```yaml
---
id: cmd_20260823_aurora-lead
type: content-md
kind: character
title: Aurora — Lead Character
project: "[[Project Aurora]]"
status: in-progress
created: 2026-08-23
updated: 2026-08-23
pipelines: [still-image, brush]
context_brand: [visual_identity, color_science]
context_domain: []
artifacts:
  - path: assets/aurora/concept-01.png
    role: concept-frame
tags: [character, protagonist]
---
```

| Field | Rule |
|---|---|
| `id` | `cmd_<YYYYMMDD>_<slug>`. Stable for the life of the note |
| `type` | always `content-md`. It marks the file as a note |
| `kind` | one word from Kinds, below |
| `title` | the human title |
| `project` | a wikilink to the project note. Set only when the author names a project |
| `status` | one word from Status, below |
| `created`, `updated` | `YYYY-MM-DD` |
| `pipelines` | the pipelines that have written to this note |
| `context_brand` | the gates this note's decisions speak to. The ladder finds notes by this field |
| `context_domain` | reference libraries a recipe cited. Never binding |
| `artifacts` | `path` and `role`: `concept-frame`, `final`, `variant`, `reference` or `export` |

### Required
`id`, `type`, `kind`, `title`, `status`, `created`, `updated`

### Optional
`project`, `pipelines`, `context_brand`, `context_domain`, `artifacts`, `tags`

`project` is optional so a one-off piece does not need a project note invented
for it.

### Fixed for the life of the note
`id`, `type`, `created`

No two notes share an `id`. A note is cited by it.

### Kinds
`character` · `design` · `audio` · `video` · `3d` · `brush` · `copy` · `ui` ·
`world` · `other`

Kinds are a flat vocabulary on purpose. Hierarchy lives in `project`.

### Status
| value | meaning |
|---|---|
| `seed` | Intent captured, nothing made yet |
| `in-progress` | Active work, has artifacts |
| `blocked` | Needs something before it can continue. Next Steps says what |
| `complete` | Done; may still be referenced as precedent |
| `archived` | Superseded or abandoned; kept for learning |

---

## Body

Sections in this order. Omit a section only when it is genuinely empty. Do not
pad it, and do not reorder.

Nothing comes before `## Overview` but, if wanted, one `# title` line.

### `## Overview`
Two to four sentences. What this thing is, where it stands, why it exists.
Written so someone who has never seen the project understands it. Always present.

### `## Next Steps`
Markdown checkboxes, most important first. Each one concrete enough to start
without asking a question.

If `status: blocked`, the blocker is the first item, as an open checkbox, and
names what would unblock it.

If a run stopped partway, the first item names the run and the stage to resume.

A `complete` or `archived` note may omit this section. A finished thing may have
no next step, and a filler one is worse than none.

```markdown
- [ ] Resume run `hub-surfaces-3f8a1c` at review
- [ ] Reconcile jacket colour against `color_science`: current amber reads warm
- [x] Lock front-facing reference
```

### `## Timeline`
Append-only, oldest first. One entry per work session. This is the record of the
exact steps: enough to reproduce, not a transcript.

An entry is headed `### <YYYY-MM-DD> · <what did the work>`. When a pipeline did
the work, name it and the run.

```markdown
### 2026-08-23 · still-image · aurora-lead-9c21e0
Generated 12 concept frames from the brief. Kept 3. Discarded the rest for
silhouette drift: the shoulder line kept widening past the brief's "lean".
→ `assets/aurora/concept-01.png`, `concept-04.png`, `concept-09.png`
```

### `## Method`
The reproducible recipe: prompts, parameters, settings, tool versions, and where
each value came from. What a future run needs to match this one. Prefer a code
block over prose.

### `## Decisions in Force`
Decisions that constrain future work on this thing. Each one is a rule a later
session must respect or explicitly overturn. They bind a run exactly as a brand
gate does.

Mark where each came from when it was not simply decided here:

```markdown
- Amber (`#F2A33C`) is an accent only, never the dominant. Overturns the initial
  warm-key direction from 08-21.
- STATED 2026-09-28: no visible tech; the world is pre-industrial.
- PROVISIONAL, derived from [[aurora-lead]], [[harbor-dusk]], [[north-gate]]:
  key light sits camera left.
```

### `## Open Questions`
Unresolved, with enough context to be answerable later. Deleted when answered.
The answer goes to Decisions in Force.

### `## Contradictions`
Conflicts with other Content MDs, each naming the other file. Written when
detected, cleared when resolved. Empty is the normal state.

### `## Links`
Wikilinks to related notes. Obsidian's graph is built from these.

---

## For agents writing these

- **Never fabricate a Timeline entry.** Only record steps actually taken. Build
  the entry from the run's `execute_log.md` and `review.md`, never from its
  `recipe.md`. An unrecorded step is recoverable; a fictional one poisons every
  future read.
- **Rewrite `## Next Steps` in full** at the end of each session. It describes
  the present, not an accumulating backlog.
- **Append to `## Timeline`, never edit past entries.** Correct a wrong entry
  with a new dated one that says what was wrong.
- **Bump `updated`.**
- **Move answered Open Questions into Decisions in Force.** Do not leave both.
- **`## Method` must be sufficient to reproduce.** If a parameter mattered, it
  goes in.
- **No presigned or share link, and no credential, goes in a note.**
- **Write through `content_md.py`.** It previews the change and writes only
  after the author has seen it.

---

## Where this came from

Carried from Creative-Headquarters `vault/SCHEMA.md`. Every change of rule is
listed. Wording was tightened throughout, and references to the hub, the archive
and Dataview were removed, because none of them exists here.

| Was | Is | Why |
|---|---|---|
| `skills:` | `pipelines:` | pipelines do the work here |
| inline comments in the frontmatter example | a table beside it | the tools that read notes there took the comment as part of the value |
| a note may sit anywhere under `<project>/<kind>/` | a run writes only at `<project>/<kind>/<slug>.md`, with `<kind>` from the vocabulary; `one-offs/` is the project of a piece that has none | a path is how a note is found, and a loose rule let a note land on the vault's own files |
| folders starting with `_` are ignored by ingest | a folder starting with `_` or `.` never holds a note | the same rule, applied to writing as well as reading |
| `_examples/` | removed | an example that lints as a note is counted as one |
| `project` is optional | `project` is set only when the author names one | a project that was inferred is a claim nobody made |
| `context_domain` lists libraries used | the same, and what it lists is never binding | a library is reference material, not a gate |
| any empty section may be omitted | `## Overview` is always present | it is half of the one rule |
| `## Next Steps` always present | optional when `complete` or `archived` | a finished thing may have no next step |
| a blocked note says what blocks it | the blocker is the first item, as an open checkbox | so that it can be checked, and found |
| — | a run that stopped partway is named in the first Next Step, with the stage | the note must be enough to resume |
| no text is expected before `## Overview` | none is allowed, but a `# title` line | the first screenful is for the two answers |
| Timeline heading `<date> · <skill>` | `<date> · <what did the work>`; a pipeline names itself and the run | a run is how a session is found again |
| `## Method` holds the recipe | and where each value came from | a value with no source cannot be told from an invented one |
| Decisions in Force constrain future work | and bind a run exactly as a brand gate does | `Router.md` §7 said so; the schema did not |
| — | `STATED` and `PROVISIONAL` markers in Decisions in Force; a provisional one cites at least three notes | a later session must be able to tell a decision from a derivation |
| — | `id`, `type` and `created` are fixed for the life of the note, and no two notes share an `id` | a note is cited by its id |
| — | no presigned link, share link or credential in a note | the vault is synced and committed |
| agents append and revise by hand | agents write through `content_md.py` | every write is previewed and confirmed |
