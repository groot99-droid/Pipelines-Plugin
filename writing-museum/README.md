# The Writing Museum

A walkable 3D museum of the creative-writing vault, generated in the browser from data and
fashioned after the Chronicle Museum (`Earth_Worldbuild/_Museum`, the same author's). A **Hall**
has a door to every scene; each scene is one room for one work of `creative-writing/vault/`,
whose passages hang on the walls as text panels, verbatim, at a size that follows the text. The
room's door theme, wall paint, trim, floor, frames and light come from the work's own labels (its
`mode` and its chunk-level `mood_tags` and `motif_tags`), resolved through one legible table
(`build/mapping.json`) inside a studio run that records where every value came from.

Every scene is a made thing of the studio: it is built only through the `scene-3d` pipeline
(`studio/pipeline/spec.yaml`), and its Content MD lives in `studio/vault/writing-museum/3d/<id>.md`.
This folder holds the engine and the data; the studio vault holds the record.

## How to view it

```
python -m http.server 8768 --directory writing-museum
```

Open `http://localhost:8768/web/index.html`. **Explore** (walk yourself), **Start guided tour**
(be walked from passage to passage, through the doors) or **Resume last visit**. The controls
are the Chronicle Museum's (`?` or `H` in the viewer lists them): WASD or arrows walk, the mouse
looks, click or `E` reads a panel or goes through a door, `M` is the floor plan, `Tab` the go-to
panel, `Space` `N` `P` drive the tour, `Esc` closes things; touch and a standard gamepad work too.

`?room=<id>`, `?work=<panel-id>`, `?resume=1`, `?classic`, `?view=<name>`, `?debug` and `?test` are
the Chronicle Museum's URL flags and mean the same here.

Three.js r160 is vendored in `web/vendor/three/` (MIT). The textures and the sky are CC0
(`assets/CREDITS.md`). There are no sculptures: `assets/models.json` is an empty catalog.

## Pipeline

```
creative-writing/vault/<work>.md  +  _ChunkTags/<work>.md.tags.json       (read only; never written)
        │  build/works.py            one entry per work; its works are PASSAGES (the vault's own
        │                            chunks, transcription header left off, sized as panels)
        │  build/mapping.json        mode / mood / motif  ->  theme, wall, light, floor, trim, frames
        ▼
data/scenes/<id>.json               one scene spec per work, written by a studio run at execute
        │  build/build_museum.py build   (--lint checks and writes nothing)
        │    └─ build/layout.py          hall + one room per scene, salon-grid packer, lint
        ▼
data/museum-manifest.json           everything textual: rooms, the wing, works, passages, credits
data/museum-layout.json             everything spatial: boxes, mouldings, doors, hangs, frames, fixtures, views
        ▼
web/js/*                            the Chronicle Museum viewer; procroom.js draws a text panel
                                    into a CanvasTexture when a hang's work carries `text`
```

```
python writing-museum/build/build_museum.py propose <vault-path> [--id ID] [--order N] [--json]
python writing-museum/build/build_museum.py check data/scenes/<id>.json
python writing-museum/build/build_museum.py build [--lint]
python -m unittest discover -s writing-museum/build/tests
node writing-museum/tools/walk_test.mjs [--grep name] [--no-shots] [--out DIR] [--list]
```

`propose` prints the scene spec the mapping table suggests for a work, with the source of every
value, and the work's passages with their panel sizes. It is a reference for the recipe stage of
a `scene-3d` run, never binding: the run decides, and records what it decided and why.

The scene spec (`data/scenes/<id>.json`) is documented at the top of `build/build_museum.py`. Its
`id` is the scene, the door, the room and the note's slug; `order` places its door in the hall;
`panels` is `"all"` or a list of chunk numbers; `style` holds the resolved look; `sources` is the
run's own record of where each value came from (the builder ignores it).

## What was copied, and what changed

`web/` is the Chronicle Museum viewer, copied on 2026-09-30, with these changes: `procroom.js`
draws text panels; `interactions.js` shows a passage and its citation on the placard, has no
rewrite layer and no image paths; `index.html` and `ui.js` say passage where they said painting.
`build/layout.py` is that museum's `build_layout.py` with the per-room style read from the scene
spec, no props or models, and a hall whose length follows its door count. `build/works.py` plays
the part `people_entries.py` plays there. `tools/walk_test.mjs` is that harness, driven by the
manifest instead of fixed room ids, with two fixes of its own (2026-10-01): the map-click test
enters the museum before opening the map, since the entry overlay sits above the map, and clicks
the centre of a door's hit area rather than its first scanned edge point, which the mouse rounds
off; the placard test ignores the `*` of italics. Both are worth carrying back to that repo.

## What it does not do

- It never writes into `creative-writing/vault/`. The 63 works stay verbatim; a panel shows a
  passage and cites its path and lines.
- It never writes into `studio/vault/`. The note is written by the run, through `content_md.py`.
- `data/scenes/` is not edited by hand. A scene spec is written by a `scene-3d` run at execute,
  after the author's go-ahead, and re-made by a new run.
- `tools/out/` (screenshots, `report.json`) is git-ignored.
