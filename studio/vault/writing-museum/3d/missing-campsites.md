---
id: cmd_20260930_missing-campsites
type: content-md
kind: 3d
title: Missing Campsites — museum room
project: "[[writing-museum]]"
status: complete
created: 2026-09-30
updated: 2026-10-01
pipelines: [scene-3d]
context_brand: [render_philosophy, motion_language]
context_domain: [writing-museum/build/mapping.json]
artifacts:
  - path: writing-museum/3d/missing-campsites/missing-campsites.json
    role: final
  - path: writing-museum/3d/missing-campsites/contact_sheet.png
    role: reference
  - path: writing-museum/3d/missing-campsites/view_missing-campsites.png
    role: reference
tags: [3d, writing-museum, horror-prose]
---

## Overview

One walkable room of the Writing Museum for "Missing Campsites" (`04_Book_Concepts/02_Missing_Campsites.md`, horror-prose): its 2 chunks hung as 2 verbatim text panels, each cited by vault path and lines, behind door 4 of ten on the north wall of the hall. One of the ten rooms made through `scene-3d` as the studio's first 3D work; the three constraints below were stated by the author for this set and are what a later 3D run recalls. Built on 2026-09-30 and reviewed on 2026-10-01; the author marked it keep. The room's look (cast-iron-glass door, #2f2224 walls, stone floor, black-lacquer frames, #ffb070 light at 110) came from the work's own mode and tags through the mapping table, recorded in Method with its sources.

## Timeline

### 2026-09-30 · scene-3d · wm-missing-campsites
Wrote `writing-museum/data/scenes/missing-campsites.json`; check ok; lint ok; built the museum with this scene (10 × 8 m, 2 panels, rows 1, 1, 0); walk test 5/5 passed (door_missing-campsites, lint_prestep, load, no_console_errors, classic_mode_loads).

### 2026-10-01 · scene-3d · wm-missing-campsites
Review. Full walk of the finished museum 35/35 passed; this room from its door view at 35 draw calls, 2548 triangles; door, corner and west views rendered. Every attestation row holds but one: the builder changed after this build (`works.py` now leaves every bold header label off a panel), and the `when to re-render` rule as stated calls for a rebuild. A rebuild with the fixed builder, diffed against this one, is byte for byte the same for this scene. The author kept the scene and stated that the rule does not apply in that case (Decisions in Force). Two panels read verbatim against the work; title card from frontmatter only. Author: keep.
→ `writing-museum/data/scenes/missing-campsites.json`, `walk/view_missing-campsites.png`, `walk/contact_sheet.png`, and `view_missing-campsites_door.png`, `_corner.png`, `_west.png` under `writing-museum/tools/out/`

## Method

The scene spec, exactly as written at execute (values and their sources):

```json
{
  "id": "missing-campsites",
  "order": 4,
  "work": "04_Book_Concepts/02_Missing_Campsites.md",
  "name": "Missing Campsites",
  "hub_side": "N",
  "panels": "all",
  "min_w": 10,
  "min_d": 8,
  "style": {
    "theme": "cast-iron-glass",
    "frame": "black-lacquer",
    "frame_small": "thin-metal",
    "wall": "#2f2224",
    "light": {
      "color": "#ffb070",
      "intensity": 110
    },
    "floor": "stone",
    "trim": "stone"
  },
  "sources": {
    "theme": "mapping.json mode.horror-prose (frontmatter mode: horror-prose)",
    "frame": "mapping.json mode.horror-prose (frontmatter mode: horror-prose)",
    "frame_small": "mapping.json mode.horror-prose (frontmatter mode: horror-prose)",
    "wall": "mapping.json mood.dread (mood_tag in 2 of 2 chunks)",
    "light": "mapping.json mood.dread (mood_tag in 2 of 2 chunks)",
    "floor": "mapping.json motif.threshold (motif_tag in 1 of 2 chunks)",
    "trim": "mapping.json motif.threshold (motif_tag in 1 of 2 chunks)"
  }
}
```

Commands as run, in this order, from the repo root (builder at commit ecefef0 or later: the header rule matters for this work's panels):

```
python writing-museum/build/build_museum.py check writing-museum/data/scenes/missing-campsites.json
python writing-museum/build/build_museum.py build --lint
python writing-museum/build/build_museum.py build
node writing-museum/tools/walk_test.mjs --grep missing-campsites,lint,load,no_console --out studio/pipeline/runs/wm-missing-campsites/walk
```

The spec is the file at `writing-museum/data/scenes/missing-campsites.json`; the kept copy under `studio/assets/` is the same bytes. The build writes the shared exports `writing-museum/data/museum-manifest.json` and `museum-layout.json`, which every scene spec on disk composes, so a rebuild reproduces this room from the spec alone. This run was executed before the studio's compute gate existed (merged 2026-10-01); a later rebuild mints a `museum_walk` token first (`compute_gate.py mint museum_walk`, then `consume`). Panel sizes come from the text through `works.py` (1.2 m wide prose, 0.9 m verse, 0.8 m short; height from the wrapped lines; a chunk over 260 words in parts; the transcription header, every bold label line and the rule, left off). The mapping rows used are named in `sources` above; the table is a reference and was not binding.

## Decisions in Force

- STATED 2026-09-30: quality bar: A scene passes when its lint and its walk test pass: every selected passage hung once, no overlaps, panels between 0.45 m and 5.6 m above the floor, doors clear; from the room's door view at most 450 draw calls and 2,000,000 triangles; no console errors; and the three standard views (door, corner, west) on the contact sheet. Panel text is verbatim and cited by vault path and lines.
- STATED 2026-09-30: when to re-render: Rebuild and re-walk a scene when its scene spec, the mapping table, the builder, the viewer or the work's sidecar changes; otherwise accept the last build. A failed lint or walk test is a finding for review, never a silent retry; a retry is a new execute with its own go-ahead.
- STATED 2026-10-01: when to re-render, clarified: "does re render constraint apply in a identical, byte for byte scenario? Answer: No." A builder, viewer or mapping change whose rebuild is byte for byte the same for a scene does not call for a re-execute; the comparison is made against a rebuild and recorded in the review.
- STATED 2026-09-30: camera grammar: First-person walk at 1.7 m eye height with panels centred on a 1.55 m eye row, 70 degree field of view, 4.2 m/s walk; guided tour at 2.5 m/s with a 6 s dwell at each passage; no cuts inside a scene, a fade through a door between scenes; three fixed views per room: door, corner and west.
- Passages hung: all chunks of the work (2), as the vault's chunker cuts them, transcription header left off.
- Order in the hall: door 4 of ten, north wall.
- The panel text is the author's own, verbatim, cited by path and lines; nothing on a panel, placard or title card says more than the work's own words.

## Open Questions

- Whether the studio should author `render_philosophy` and `motion_language` as gates now that ten notes state the same three lines.

## Contradictions

## Links

- [[writing-museum]] · the other rooms: [[endless-temple]] · [[wrymwretch]] · [[melting-away]] · [[low-in-the-water]] · [[following-the-sheep]] · [[yellow-drop]] · [[heartstream]] · [[trip-tracker]] · [[architecture-of-being]]
