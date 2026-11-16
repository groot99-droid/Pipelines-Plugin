---
id: cmd_20261113_props
type: content-md
kind: 3d
title: WrymWretch props (Meshy models)
project: "[[wrymwretch]]"
status: in-progress
created: 2026-11-13
updated: 2026-11-13
pipelines: [asset-3d]
context_brand: [visual_identity, render_philosophy]
artifacts:
  - path: wrymwretch/3d/props/forbidden-door-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/forbidden-door-image.glb
    role: final
  - path: wrymwretch/3d/props/game-table-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/game-table-image.glb
    role: final
  - path: wrymwretch/3d/props/heartstone-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/heartstone-image.glb
    role: final
  - path: wrymwretch/3d/props/kill-list-slate-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/kill-list-slate-image.glb
    role: final
  - path: wrymwretch/3d/props/king-statue-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/king-statue-image.glb
    role: final
  - path: wrymwretch/3d/props/lantern-crystal-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/lantern-crystal-image.glb
    role: final
  - path: wrymwretch/3d/props/living-shard-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/living-shard-image.glb
    role: final
  - path: wrymwretch/3d/props/memory-crystal-remesh-thumb.png
    role: reference
  - path: wrymwretch/3d/props/memory-crystal-remesh.glb
    role: final
  - path: wrymwretch/3d/props/monolith-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/monolith-image.glb
    role: final
  - path: wrymwretch/3d/props/outpost-gate-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/outpost-gate-image.glb
    role: final
  - path: wrymwretch/3d/props/prophecy-pedestal-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/prophecy-pedestal-image.glb
    role: final
  - path: wrymwretch/3d/props/prophecy-tome-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/prophecy-tome-image.glb
    role: final
  - path: wrymwretch/3d/props/queen-statue-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/queen-statue-image.glb
    role: final
  - path: wrymwretch/3d/props/remembering-water-flask-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/remembering-water-flask-image.glb
    role: final
  - path: wrymwretch/3d/props/remnant-mask-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/remnant-mask-image.glb
    role: final
  - path: wrymwretch/3d/props/wyrm-skull-image-thumb.png
    role: reference
  - path: wrymwretch/3d/props/wyrm-skull-image.glb
    role: final
tags: [wrymwretch, esc-zine99, props, meshy]
---

## Overview

Textured 3D models of WrymWretch's props, one of the ten games in the author's esc-ZINE99 repository,
made with Meshy image-to-3D from each prop's object image (`esc-zine99/games/wrymwretch/assets/objects/`).
16 of the game's 30 props are made and kept, in the game's signature bone-and-silver reliquary look.
They go on to assemble-3d through the game's Blender build files, which expect `models/<object>.glb`.

## Next Steps

- [ ] Make the other 14 props (split-tree, witness-tent, moot-fire, tribe-banner, crystalline-tree, memory-platform, wyrm-rib, ward-cot, torch-sconce, candle-stand, storm-crystal-pillar, sky-watch-telescope, tide-shrine-stone, mossy-boulder) once the Meshy balance covers them (30 credits each; 5 left).
- [ ] Check the Six Realms table's top (its hex board) in Blender; the thumbnail does not show it.
- [ ] At assembly, decimate to about 0.95 if the triangle caps are to hold exactly (15 of 16 are 0.7 to 3.9 percent over).

## Timeline

### 2026-11-13 · asset-3d · wrymwretch-props-meshy-models-from-the-30-object-d6e18b
Meshy balance 490. Pilot: memory-crystal image-to-3D (30 credits) came back as the raw mesh, 3,288,606 triangles and 100 MB, because target_polycount applies only with should_remesh. Stepped back to the recipe; revised with a 5-credit remesh of the pilot (to 30,000) and should_remesh on the other 15 (30 credits each). All 16 tasks succeeded; 485 credits spent in all, balance 5. Inspected each GLB: 13.6 to 18.1 MB, 2048 px PBR textures, triangles 0.7 to 3.9 percent over their caps on 15 of 16 (prophecy-tome under). The author: "they are good for rn", "Yes, keep all 16". Kept the 16 models as final and their thumbnails as reference; discarded the heavy pilot mesh.

## Method

Meshy image-to-3D through `studio/pipeline/meshy_client.py`, each object image sent as a data URI. Fields: should_texture true, enable_pbr true, should_remesh true, target_polycount 30000 (60000 for king-statue, queen-statue, monolith, wyrm-skull), topology triangle, target_formats ["glb"], no texture_prompt. memory-crystal: image op without should_remesh, then a remesh op (target_polycount 30000). The ledger, per task (image data omitted):

```
memory-crystal:image  task 01a1d63b-3b1a-76fe-ab28-7970b8f1980c  spent 30  {"should_texture": true, "enable_pbr": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
memory-crystal:remesh  task 01a1d644-25d9-727d-b3bd-90acf42fd272  spent 5  {"input_task_id": "01a1d63b-3b1a-76fe-ab28-7970b8f1980c", "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
heartstone:image  task 01a1d644-2733-727b-9317-ea6f79c11e5c  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
prophecy-tome:image  task 01a1d644-2c2a-762b-b3b3-7d1f34acb0db  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
prophecy-pedestal:image  task 01a1d644-3139-75a4-993d-8b66e1ebb159  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
forbidden-door:image  task 01a1d644-3571-7080-ab7b-3da6f299b64a  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
lantern-crystal:image  task 01a1d644-39f7-732b-987f-7d45406c2e95  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
living-shard:image  task 01a1d644-3e05-71fc-974d-cd2056ecfda0  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
remnant-mask:image  task 01a1d644-41fb-757c-9e38-bd9597a81c09  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
game-table:image  task 01a1d644-4666-7048-bae8-238faf9db16e  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
kill-list-slate:image  task 01a1d644-4afa-7224-a3a4-13651ff67e52  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
remembering-water-flask:image  task 01a1d644-5014-73fd-8960-f1851605dc5b  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
outpost-gate:image  task 01a1d644-5441-724e-b3ca-52bc18133a78  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 30000, "topology": "triangle", "target_formats": ["glb"]}
king-statue:image  task 01a1d644-592a-7241-a065-a33917a5672d  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 60000, "topology": "triangle", "target_formats": ["glb"]}
queen-statue:image  task 01a1d644-5ee4-72cc-a330-54be6774e807  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 60000, "topology": "triangle", "target_formats": ["glb"]}
monolith:image  task 01a1d644-6305-72d2-9b13-7c88be06ceca  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 60000, "topology": "triangle", "target_formats": ["glb"]}
wyrm-skull:image  task 01a1d644-6731-7557-9762-2473751ee999  spent 30  {"should_texture": true, "enable_pbr": true, "should_remesh": true, "target_polycount": 60000, "topology": "triangle", "target_formats": ["glb"]}
```

## Decisions in Force

- STATED 2026-11-13: generated imagery: motifs, framing, texture: WrymWretch's signature bone-and-silver reliquary look: carved ivory bone and tarnished silver relief with fine black crack lines; one object per model, whole and isolated, as in its source image in games/wrymwretch/assets/objects/; no text, no people.
- STATED 2026-11-13: quality bar: Textured with PBR maps, at most 30,000 triangles (hero pieces at most 60,000), GLB at most 25 MB, 2048 px textures, one closed object matching its source image's silhouette, scaled in Blender to its height in assets.json; a model that misses its silhouette or loses the bone-and-silver texture is discarded, not patched.
- Prompt style: no text prompt; Meshy textures from the source image alone, so the model keeps the image's look.
- Budget: should_remesh is always on with target_polycount; Meshy lands a few percent over the target. The author accepted that overshoot for these 16 on 2026-11-13.

## Links

- esc-ZINE99 `games/wrymwretch/assets/assets.json` (object sizes and source images), `games/wrymwretch/blender/` (where the models are placed)
