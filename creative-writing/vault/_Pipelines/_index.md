---
title: "Pipelines — Index"
type: moc
folder: _Pipelines
tags: [moc, pipelines]
---

# Pipelines — Index

The tooling that writes into this vault, and the tooling that will write into
it later. This folder is a map, not machinery: **the pipelines themselves live
outside the vault**, in the `Pipelines` repo that contains it. One note per
pipeline, so a pipeline is reachable from the graph instead of being something
you have to remember exists.

## Where things actually sit

This vault is `creative-writing/vault/` inside the `Pipelines` repo. Its
sibling `creative-writing/pipeline/` holds the code for the pipeline below.
Open **this folder** in Obsidian, not the repo root — every link in this vault
is written vault-absolute and only resolves with this folder as the vault root.

```
Pipelines/                     the repo (not the Obsidian vault)
├── .claude/skills, agents     the Claude Code skills and subagents
├── creative-writing/
│   ├── vault/                 ← you are here
│   └── pipeline/              the creative-writing pipeline's code
└── <next-tool>/               future tools live as siblings
```

## The pipelines

| Pipeline | Note | Writes into | Stages | Status |
|---|---|---|---|---|
| Creative writing | [[_Pipelines/creative-writing\|creative-writing]] | this vault | 6, each a checkpoint | in use |

## Adding a pipeline

1. Build it in its own top-level folder in the `Pipelines` repo.
2. Add a note here named after it, following
   [[_Pipelines/creative-writing|creative-writing]]'s shape: what it does, what
   it reads, what it writes, where its checkpoints are, and what it will
   **not** do on its own.
3. Add a row to the table above.
4. If it writes into this vault, say so explicitly in its note — anything that
   can modify the 63 verbatim originals needs that stated in the open, and
   [[CLAUDE.md]] governs what it is allowed to touch.

## Related

- [[00_INDEX.md|The Living Archive — Index]] — the 63 works these pipelines reference.
- [[_Idea_Library/_index|Idea Library]] — where pipeline output waits before integration.
- [[CLAUDE.md]] — the voice and craft rules every pipeline has to respect.
- [[OBSIDIAN.md]] — how this vault is set up as an Obsidian vault.
