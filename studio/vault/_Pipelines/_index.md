---
title: "Pipelines — Index"
type: moc
folder: _Pipelines
tags: [moc, pipelines]
---

# Pipelines — Index

The tooling that writes into this vault. This folder is a map, not machinery:
**the pipelines themselves live outside the vault**, in `studio/pipeline/` in the
repo that contains it. One note per pipeline, so a pipeline is reachable from
the graph.

## Where things sit

This vault is `studio/vault/` inside the `Pipelines` repo. Open **this folder**
in Obsidian, not the repo root.

```
Pipelines/                     the repo (not the Obsidian vault)
├── .claude/skills, agents     the Claude Code skills and subagents
├── studio/
│   ├── vault/                 ← you are here
│   ├── pipeline/              the spec, the bookkeeper, the note writer
│   └── docs/                  what was carried from Creative-Headquarters
└── creative-writing/          a separate tool, with its own vault
```

## The pipelines

All of them are entries in one file, `studio/pipeline/spec.yaml`, and run the
same six stages: **intake → context → recipe → execute → review → record**.

| Pipeline | Note | Makes | Status |
|---|---|---|---|
| ui-direction | [[_Pipelines/studio\|studio]] | a design direction for a surface or a product | in use |
| ui-build | [[_Pipelines/studio\|studio]] | markup and CSS in which every value is a token | not yet implemented |
| brand-gate | [[_Pipelines/studio\|studio]] | one brand gate, transcribed from the author | not yet implemented |
| brush | [[_Pipelines/studio\|studio]] | a brush and an importable file | not yet implemented |
| still-image | [[_Pipelines/studio\|studio]] | still images from a brief | not yet implemented |
| video-shot | [[_Pipelines/studio\|studio]] | a shot, or a chain that holds continuity | not yet implemented |
| music-cue | [[_Pipelines/studio\|studio]] | one cue | not yet implemented |
| edit-2d | [[_Pipelines/studio\|studio]] | a batch edit or a composite | not yet implemented |
| scene-3d | [[_Pipelines/studio\|studio]] | a scene, a camera path or a render | not yet implemented |

## Adding a pipeline

1. Add an entry under `pipelines:` in `studio/pipeline/spec.yaml`.
2. Add a row to the table above.
3. Run `python -m unittest discover -s studio/pipeline/tests`.

The six stages do not change. They read the entry's rules out of the spec.

## Related

- [[CLAUDE.md]] — the rules every pipeline follows.
- [[SCHEMA.md]] — the note every pipeline leaves.
- [[_Context/brand/README|Brand gates]] — what a pipeline must resolve first.
