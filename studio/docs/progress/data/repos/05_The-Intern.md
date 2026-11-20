# The-Intern

**ninety-nine: continuous first-person narrative game.** Source: https://github.com/groot99-droid/The-Intern

Generated 20 November 2026 from the repository clone (`git log`, `git ls-files`, and the files at HEAD). Counts are as cloned. Commit dates are git author dates in UTC and can differ from when the work was done (merged PRs, integration passes).

## 1. Numbers

| Measure | Value |
|---|---|
| Commits (all branches) | 116 (91 non-merge, 25 merge) |
| First commit | 2026-09-13 |
| Last commit | 2026-11-19 |
| Days with commits | 17 |
| Tracked files | 307 |
| Checked-out branch | HEAD |
| Commit authors (non-merge, by name) | Claude: 87; groot99-droid: 4 |

Author names are git author names: "Claude" marks commits made by a Claude session, and the owner's GitHub handle marks commits made by the owner. Email addresses are left out.

**Tracked files by type (top 15):** .png 106; .js 45; .mp4 42; .wav 41; .md 25; .py 16; .json 14; .html 4; (none) 3; .blend 3; .cjs 3; .csv 2; .yml 1; .glb 1; .css 1

**Tracked files by top-level folder:** blender 171; ninety-nine 106; sfx-raw 13; (root) 6; docs 5; .obsidian 4; .claude 1; .github 1

## 2. Activity by month and by day

| Month | Non-merge commits |
|---|---|
| 2026-09 | 6 |
| 2026-10 | 84 |
| 2026-11 | 1 |

**Per day (non-merge commits):** 2026-09-13 1; 2026-09-30 5; 2026-10-01 2; 2026-10-03 4; 2026-10-04 6; 2026-10-08 18; 2026-10-09 19; 2026-10-10 4; 2026-10-11 2; 2026-10-15 7; 2026-10-16 17; 2026-10-17 2; 2026-10-29 1; 2026-10-30 2; 2026-11-19 1

## 3. Layout (folders and file counts)

- **blender/** 171 files
  - blender/higgsfield/ 75
  - blender/renders/ 74
  - blender/refs/ 4
- **ninety-nine/** 106 files
  - ninety-nine/assets/ 38
  - ninety-nine/src/ 32
  - ninety-nine/test/ 16
  - ninety-nine/tools/ 6
  - ninety-nine/text/ 4
  - ninety-nine/vendor/ 4
  - ninety-nine/data/ 3
- **sfx-raw/** 13 files
- **(repository root)** 6 files
- **docs/** 5 files
- **.obsidian/** 4 files
- **.claude/** 1 files
- **.github/** 1 files
  - .github/workflows/ 1

## 5. CI workflows

- `.github/workflows/tests.yml`: tests

## 6. Documents inventory (25 Markdown files)

Markdown files by folder (top 25): docs 5; ninety-nine/assets 4; (root) 3; blender 2; blender/higgsfield 2; blender/refs 1; blender/renders 1; ninety-nine 1; ninety-nine/assets/glb 1; ninety-nine/src 1; ninety-nine/src/walk 1; ninety-nine/src/world 1; ninety-nine/test 1; sfx-raw 1

- `CLAUDE.md` (1928 words): CLAUDE.md. Sections: What this is; Naming scheme; Canon (Doc 1 §3) — never violate these when adding/generating anything; Don't touch without asking; Workflow; Docs-as-vault
- `README.md` (407 words): The New Intern — NINETY-NINE. Sections: Layout; Map
- `blender/Blender Pipeline.md` (1713 words): Blender Pipeline. Sections: Files; The scene-builder copies (Higgsfield); The render bridge (Track B1/B3); Atmospheric motifs (Track C); S4_C cubicle furniture; Subsections; Known follow-up: render output paths
- `blender/PLAN_remaining_scenes.md` (1027 words): Plan: Remaining "Ninety-Nine" 3D Environments. Sections: Status; Sequencing: 4 phases, cheapest/most-reusable first; New shared assets needed (add to `_SharedAssetLibrary`, reused across phases); Process changes from the pilot (lessons learned); Verification per scene (unchanged from pilot); Immediate next step
- `blender/higgsfield/README.md` (925 words): Higgsfield scene-builder projects. Sections: What one project holds; The shoot; Projects; Rebuilding after a set changes
- `blender/higgsfield/REBUILD_NOTE.md` (9811 words): Higgsfield rebuild note. Sections: Status; Runtime-only vs geometry; What changed at the continuous building, per room (`c1d415e` → `65184db`); What the polish changed, per room (`9684b87` → `58f762e`); What the follow-ups changed, per room (`20293e8` → `0add444`); Doorways; What `higgsfield_scene.py` needs at rebuild time; Commands and order
- `blender/refs/Reference Images.md` (96 words): Reference Images
- `blender/renders/Scene Renders.md` (276 words): Scene Renders
- `docs/01_GAME_LOGIC.md` (4722 words): NINETY-NINE. Sections: Document 1 of 4: Game Logic; 0. PREMISE; 1. THE ARCHITECTURE PROBLEM, AND THE SOLUTION; 2. STATE MODEL; 3. CANON: RULES THAT NEVER BREAK; 4. THE SPINE; 5. SCENE BREAKDOWNS; 6. TEXT LIBRARY; 7. COMBINATORICS: HOW 256 PATHS RESOLVE; 8. PRODUCTION SCOPE
- `docs/02_GENERATION_HIGGSFIELD.md` (4419 words): NINETY-NINE. Sections: Document 2 of 4: Generation Pipeline; 1. NAMING CONVENTION (NON-NEGOTIABLE); 2. THE CORE TECHNIQUE; 3. GLOBAL STYLE BLOCK; 4. NEGATIVE PROMPTS; 5. PROMPT LIBRARY; 6. AUDIO ARCHITECTURE; 7. PRODUCTION ORDER; 8. QC CHECKLIST
- `docs/03_MINIGAME_UX.md` (4326 words): NINETY-NINE. Sections: Document 3 of 4: Mini-Game UX Specification; 1. THE GOVERNING PRINCIPLE; 2. COMPONENT INDEX; MG-01: THE INTAKE FORM; MG-02: THE SCAN / THE DOOR; MG-03: THE CORRIDOR / THE LABYRINTH; MG-04: THE STAPLER / THE IGNITION; MG-05: THE REQUISITION TERMINAL / THE RUN; MG-06: THE PANEL / THE EDGE; MG-07: THE HANDOFF / THE BREATH
- `docs/04_TECHNICAL_BUILD.md` (3768 words): NINETY-NINE. Sections: Document 4 of 4: Technical Build Specification; 1. STACK DECISION; 2. FILE TREE; 3. STATE MODULE; 4. THE MANIFEST; 5. RENDERER; 6. MINI-GAME CONTRACT; 7. AUDIO; 8. PRELOADING; 9. THE BAIL-OUT
- `docs/Design Docs.md` (316 words): Design Docs
- `ninety-nine/App Overview.md` (1296 words): App Overview. Sections: Entry points; Subsections; `data/` — spine, ending logic, rooms (3 files); `text/` — player-facing copy (4 files); `vendor/`; `tools/` — dev-only (6 files)
- `ninety-nine/assets/Asset Revisions.md` (697 words): Asset Revisions. Sections: Done in this pass; Still to regenerate; Audio, for the record
- `ninety-nine/assets/Generated Assets.md` (343 words): Generated Assets. Sections: Scenes (each has a room and an AMB bed); Endings; Library SFX (not generated, sourced from raw files); Cross-links; Revisions
- `ninety-nine/assets/README.md` (378 words): NINETY-NINE — assets. Sections: Engine notes; Not generated
- `ninety-nine/assets/Scene Flow.md` (4325 words): Scene Flow. Sections: How to read it; S0 — THE UPLOAD (no branch); S1 — THE WAITING ROOM; S2 — THE CALL; S3 — THE THRESHOLD; S4 — THE FLOOR; S5 — THE DESK / THE GARAGE; S6 — THE REQUISITION / THE RUN; S7 — THE DESCENT; S8 — THE DELIVERY / THE DIVE
- `ninety-nine/assets/glb/README.md` (170 words): assets/glb
- `ninety-nine/src/Source Code.md` (2849 words): Source Code. Sections: Subsections
- `ninety-nine/src/walk/Walk Mode.md` (2260 words): Walk Mode. Sections: Files
- `ninety-nine/src/world/World.md` (1107 words): World
- `ninety-nine/test/Tests.md` (2141 words): Tests. Sections: How to run it; `cases/` (12 files); Optional: the Node runners (dev only)
- `sfx-raw/Raw SFX Library.md` (159 words): Raw SFX Library. Sections: Integrated; Not yet integrated

## 10. Pull requests merged (9)

- 2026-09-30 #1 from `groot99-droid/claude/affectionate-brahmagupta-v3uqqn`
- 2026-09-30 #2 from `groot99-droid/claude/sleepy-ramanujan-digrr2`
- 2026-09-30 #3 from `groot99-droid/claude/trusting-cerf-do1ws9`
- 2026-09-30 #4 from `groot99-droid/claude/eager-cray-d280uk`
- 2026-10-02 #5 from `groot99-droid/claude/exciting-albattani-46k7o3`
- 2026-10-17 #6 from `groot99-droid/claude/blissful-faraday-bdt4c6`
- 2026-10-30 #7 from `groot99-droid/claude/pensive-curie-kr7vcq`
- 2026-11-04 #8 from `groot99-droid/claude/pensive-curie-kr7vcq`
- 2026-11-19 #9 from `groot99-droid/claude/inspiring-cori-juqfrm`

## 11. Source documents (verbatim)

Each file below is quoted from the repository at HEAD. Lines start with ">" so its headings do not mix with this document's.

### Source file: README.md

> ---
> tags: [router]
> ---
>
> # The New Intern — NINETY-NINE
>
> Project home for **ninety-nine**, a browser game, plus the pipeline and design material that produced it.
>
> ## Layout
>
> - **`ninety-nine/`** — the game itself: a static web app (`index.html`, `style.css`, `src/`, `data/`, `text/`, `vendor/` for three.js) with its audio in `ninety-nine/assets/aud` (tracked in `ninety-nine/assets/MANIFEST.csv`) and the optional open-source prop library in `ninety-nine/assets/glb`. The game is one continuous first-person walk through live 3D rooms (`data/rooms.json`, joined into one building by `src/world/`, drawn by `src/stage/`, played by `src/director.js`). Choices are places to walk to; there are no mini-games, and the AI-generated stills and clips are gone. See [`ninety-nine/assets/README.md`](ninety-nine/assets/README.md). Run it locally via the `ninety-nine` config in `.claude/launch.json` (`python ninety-nine/tools/dev_server.py 8000`). Tests live in `ninety-nine/test/`.
> - **`docs/`** — design/spec documents referenced throughout the pipeline as "Doc 1"–"Doc 4": game logic, the Higgsfield generation pipeline, mini-game UX (retired 2026-10-03), and the technical build. Dated amendment notes mark where the build has moved on.
> - **`blender/`** — the hand-built Blender pipeline (scene file, reference images, per-scene renders). Its plan, `blender/PLAN_remaining_scenes.md`, is a historical record: it predates the continuous building. The sets the game plays are also rebuilt as Blender scenes in the Higgsfield 3D scene builder by `ninety-nine/tools/higgsfield_scene.py`; `blender/higgsfield/` lists the projects and their proof renders. The projects are stale until rebuilt for the continuous building (see [[blender/higgsfield/REBUILD_NOTE]]).
> - **`sfx-raw/`** — raw, human-named sound effect sources; 10 of the 12 are already integrated into the manifest-tracked pipeline in `ninety-nine/assets/aud` (see [[sfx-raw/Raw SFX Library]] for which two aren't yet).
> - **`.claude/`** — Claude Code harness config (`launch.json`, the dev server launch config).
> - **`.github/workflows/tests.yml`** — CI: rebuilds the rooms, runs the suite headless on every push and pull request, and plays three autopilot walkthroughs on pull requests (see [[ninety-nine/test/Tests|Tests]]).
>
> ## Map
>
> A router into the per-folder index notes — each one lists every file in that folder with a one-line description, so you (or an agent) can jump straight to the relevant "bit" instead of reading everything. Open this folder as an Obsidian vault to browse it as a linked graph.
>
> - [[CLAUDE|CLAUDE.md]] — persistent AI-assistant context: naming scheme, canon rules, don't-touch list
> - **[[ninety-nine/App Overview|ninety-nine/]]** — the game
>   - [[ninety-nine/src/Source Code|src/]] → [[ninety-nine/src/world/World|world/]] · [[ninety-nine/src/walk/Walk Mode|walk/]]
>   - [[ninety-nine/assets/Generated Assets|assets/]]
>   - [[ninety-nine/test/Tests|test/]]
> - [[docs/Design Docs|docs/]] — design & spec docs (Doc 1–4)
> - **[[blender/Blender Pipeline|blender/]]**
>   - [[blender/higgsfield/README|higgsfield/]] → [[blender/higgsfield/REBUILD_NOTE|REBUILD_NOTE]]
>   - [[blender/refs/Reference Images|refs/]]
>   - [[blender/renders/Scene Renders|renders/]]
> - [[sfx-raw/Raw SFX Library|sfx-raw/]] — raw sound sources
>

### Source file: CLAUDE.md

> ---
> tags: [router]
> ---
>
> # CLAUDE.md
>
> ← [[README|Router]]
>
> Persistent context for working in this repo. Start at [[README|README.md]]'s Map section (or the vault graph if you have this open in Obsidian) for a per-folder file index — this file is conventions/guardrails, not a file listing.
>
> ## What this is
>
> **ninety-nine**: a static-web narrative game (no build step). The player is an intern at a company that is fake (rendered low-poly PS1) inside a building that is real (rendered photoreal) — see Canon below. [[docs/Design Docs|docs/]] holds the 4 source-of-truth specs: Doc 1 logic, Doc 2 asset generation, Doc 3 mini-game UX (**retired** 2026-10-03), Doc 4 technical build. [[ninety-nine/src/Source Code|ninety-nine/src/]] implements them; where the build has moved on, a dated amendment note sits at the top of the spec's section.
>
> **The game is one continuous first-person walk.** The player spawns in the apartment and walks, without a cut, through one building of live three.js rooms from `ninety-nine/data/rooms.json`:
>
> - [[ninety-nine/src/world/World|src/world/]] places each room in one world space. When a choice is made, it joins the next room behind a doorway through a `CN_*` connector; the door seals behind him and the room he left is dropped.
> - Each scene's two choices are **threshold zones** in its room. Walking into one commits the choice (`src/director.js`). Friction comes from how he moves (hesitation, doubling back).
> - There are no mini-games, no choice buttons and no fades to black between rooms. The camera is taken from him only for carried moments: sitting at the computer, the call, the cab's descent, the fall into the pool, the chute, the endings' pull-backs.
>
> Doc 2's generated stills and clips, Doc 4 §5's video pool and Doc 3's mini-games no longer exist (the docs describe what they replaced). A parallel [[blender/Blender Pipeline|blender/]] pipeline hand-builds 3D versions of the same environments, and `ninety-nine/tools/higgsfield_scene.py` rebuilds every set in the Higgsfield 3D scene builder (Blender 5.2) with the open-source catalog props and the same camera moves. Those projects predate the continuous building and are stale until rebuilt ([[blender/higgsfield/REBUILD_NOTE|REBUILD_NOTE]]).
>
> ## Naming scheme
>
> Sets, audio and scene folders follow `S{n}_{C|H}` (Doc 2 §1 / Doc 4 §4; the old `_{IMG_IN|IMG_OUT|VID|TRN}` suffixes named the removed stills and clips -- their roles are now the set's `in` / `out` poses and its `loop` / `leave` + `arrive` shots). `C` = compliant/succumb render, `H` = hostile/resist render. `S0_X` is the branchless prologue. Endings are `SE_{ASSIM|EXPUL|PEND|RETAINED}`; extra sets are `SET_{STREET|DIVE}`.
>
> Connectors, the passages the continuous building joins rooms with, are `CN_{NAME}`: `CN_STAIRS_APT`, `CN_VESTIBULE`, `CN_CORRIDOR_OFFICE`, `CN_CORRIDOR_SERVICE`, `CN_STAIRS_CONCRETE`, `CN_CORRIDOR_DOWN`, `CN_RAMP_DOWN`, `CN_CHUTE`. They have no scene, no render, no clock and no slip, and they only run level or down (C3).
>
> Several keys are **aliases** of one room, so the scene changes where the player stands: `S2_*` is `S1_*`, `S6_C` is `S5_C` (the desk room carries S5's and S6's thresholds), `S7_H` is `S6_H`, `SE_RETAINED` is `SE_ASSIM` and `SE_EXPUL` is `S8_H`. S8 H's scene is played in `SET_DIVE`; `S8_H` is the store the chute lets out into.
>
> The spine (Doc 1 §4) — scene number → name → what C/H actually mean there:
>
> | # | Scene | Compliant (C) | Hostile (H) |
> |---|---|---|---|
> | S0 | THE UPLOAD | — no branch — | |
> | S1 | THE WAITING ROOM | Sterile, ordered | Scattered, over-lit |
> | S2 | THE CALL | "Ninety-nine." | "Shaun." |
> | S3 | THE THRESHOLD | Red curtain, green ENTER | Locked glass doors |
> | S4 | THE FLOOR | Cubicle maze, the manager | Janitorial labyrinth |
> | S5 | THE DESK | Unmarked desk, stapler | Parking garage, rusted cars |
> | S6 | THE REQUISITION | Spreadsheet of items | The run that does not end |
> | S7 | THE DESCENT | Damaged freight elevator | Concrete edge over the pool |
> | S8 | THE DELIVERY | Mailroom → boardroom | Grate → chute → store |
> | E | ENDING | ASSIMILATION / RETAINED | EXPULSION / PENDING REVIEW |
>
> A file/folder named e.g. `S5_H` is always "the parking garage," `S4_C` is always "the cubicle maze" — decode any asset name against this table before assuming what it contains.
>
> ## Canon (Doc 1 §3) — never violate these when adding/generating anything
>
> - **C1** Company-owned things (people, furniture, vehicles, signage, clothing, paper) render low-poly PS1. The building itself (floors, walls, glass, water, fog, light) renders photoreal.
> - **C2** Shadows fall toward the building's core, regardless of light position.
> - **C3** No windows, no sky, no ascent after the lobby doors close. Elevators/stairs only descend.
> - **C4** Company text never says "you" — "the candidate" / "the applicant" / "personnel." "You" appears exactly once, ever: the final ending card.
> - **C5** No NPC blinks or looks up; faces are static or 4-frame jaw loops.
> - **C6** Shaun's hands are low-poly from the very first shot, before he's even hired.
> - **C7** One continuous 48Hz drone from lobby-doors-closed to the final card; never restarts; detunes ~4 cents/scene.
> - **C8** Every clock in every render is the same clock, no hands.
>
> ## Don't touch without asking
>
> - `blender/refs/*.png` — the last copies of the AI reference stills (the game's `assets/img` is gone) and may be loaded into `ninety-nine_pilots.blend` by relative path; deleting risks breaking a live reference-image link.
> - `ninety-nine_pilots.blend` render output paths — 11 scenes' saved output paths still point at pre-rename folder names (see [[blender/Blender Pipeline|blender/Blender Pipeline.md]] for the exact old→new table). Fixing this needs Blender open with the MCP addon connected *to this specific file* — check `get_blendfile_summary_path_info` reports this file, not a different one, before writing to it.
> - `ninety-nine/assets/aud` — the single source of truth for generated audio (the old duplicate `FINAL_NINETY-NINE_*` delivery folders were consolidated away). Don't regenerate/overwrite without checking `MANIFEST.csv` first. `assets/img` and `assets/vid` were removed deliberately (the game is 3D-only); do not bring them back.
> - [[blender/material_factories.py|blender/material_factories.py]], [[blender/prop_builders.py|prop_builders.py]], [[blender/helpers.py|helpers.py]] — exported *mirrors* of Text datablocks that live inside the `.blend`. The `.blend` copies are authoritative; editing only the `.py` files here has no effect in Blender.
>
> ## Workflow
>
> - Run the game: `.claude/launch.json` → `ninety-nine` config (`python ninety-nine/tools/dev_server.py 8000`). Plain `python -m http.server` won't work (no-cache headers + HTTP Range support are required — see [[ninety-nine/App Overview|App Overview]]).
> - Run tests: open `ninety-nine/test/index.html` through that same dev server (fetches are same-origin). No Node on this machine — see [[ninety-nine/test/Tests|Tests]]. On GitHub, `.github/workflows/tests.yml` builds the rooms and runs the suite on every push and pull request, plus three autopilot walkthroughs on pull requests. Where Node + Playwright exist, `node ninety-nine/tools/run_tests.cjs` runs the suite headless and `node ninety-nine/tools/walkthrough.cjs` plays whole games with the autopilot (optional, dev only).
> - Preview a room without playing to it: `ninety-nine/test/rooms.html?room=S5_H` plays a shot (`&shot=in`), and `&walk=1` walks it alone (connectors too).
> - Start the game part-way (dev only): `ninety-nine/index.html?start=S5&render=H` puts the candidate just inside that scene's room, with a score that gives that render, and starts the drone. `&conf=N` / `&diss=N` set the score itself (−8..8, 0..7): the render then follows it, and a score no real game could reach is allowed with a console warning. `?autopilot=SSRRSSRR` walks him through by himself (`src/dev/autopilot.js`): one letter per scene S1–S8, S to succumb, R to resist. It follows a navgrid built from the rooms' colliders, with A*. Extra options are `&seed=H` (answer the form NOT WILLING), `&bail=S4` and `&speed=2.5`, and it combines with `?start=`. It logs `[autopilot]` lines to the console.
> - Sets are data: edit `ninety-nine/tools/build_rooms.py` and re-run it, never `data/rooms.json` by hand.
>   - A room's doorways are `door()` calls: a wall, an offset along it, a size, and a kind (`door` / `glass` / `curtain` / `shutter` / `slide` / `open`). `jib=True` makes a hinged door a flush leaf in the wall (S3 C's service door), `glass='glass_clear'` a pane seen through, and `mat='velvet'` hangs a curtain as cloth.
>   - Its threshold zones are `zone()` calls (a zone at a chair carries the `seat` he sits into), and extra join points are `anchor()` calls. `entry` names the doorway a connector arrives through. Connectors are the `cn_*` builders; each ends in a collar of wall (`MOUTH`) so a wider or taller doorway behind it shows wall, and `manifest.validate` fails a join that does not fit.
>   - A box or prop with `fixed` stays put when its room moves (S7 C's shaft). A light's `sync` names props whose glow follows it, `labelInk` (`dark` / `backed`) sets how a room's labels are drawn, and an actor's `drive` walks him by the candidate's progress (a zone's `armAfter` may name him).
>   - `check_room()` fails the build when a door runs off or overlaps on its wall, a zone is off the floor or inside a solid box, a room has no entry, an alias changes more than `ALIAS_KEYS` (spawn, name, shots, notes), a fixed box collides or is floor, a drive breaks its rules, a `sync` names no prop, or hands appear anywhere but `S0_X` / `SE_PEND`.
>   - A set's `shots` are now the carried moments, the endings' pull-backs, and the `in` / `out` / `leave` / `arrive` poses the Higgsfield proofs render.
>   - Prop builders are in `ninety-nine/src/walk/props.js`, a scene's in its `// ---- polish: <group> -- begin/end ----` block. All blocks share one table, so reusing a builder name silently replaces the earlier one.
> - Choices are data too: `ninety-nine/data/scenes.json` (hand-edited) names, per scene and render, the room, `next`, the ambience, music and captions, the `onEnter` beats, and the two `thresholds`.
>   - A threshold (succumb / resist) gives its label, its zone(s) in that room, the `exit` door and the `via` connector it opens (`viaDark`: unlit until he is in it), `setFlag`, `sfxCue`, `beat` and `approach`. `beatZones` are non-choice moments, `idle` / `stillness` play when he waits, `bumpCount` counts pushes on a locked door, `drive` holds a driven actor's beats, `unseen` changes the room behind his back, `env` sets the room's atmosphere for the scene and `hum` the store's hum. Beats include `env`, `breath` / `footfall`, `display`, `swing`, and `open` with an `amount`. The beat vocabulary is in the file's `_comment`; `test/cases/manifest.validate.js` fails on a key the director does not read.
>   - Keep its zone and door names in step with `build_rooms.py`: its `check_links()` fails the build when `scenes.json` or `endings.json` names a zone, door, anchor, connector, shot or prop that the room it names does not have (aliases resolved). At run time the director still only warns in the console.
>   - `data/endings.json` gives each ending's room, zone, `autoSeconds`, `preShot` / `beats` / `show`, pull-back shot, `routes` and `hum`. [[ninety-nine/assets/Scene Flow|Scene Flow]] walks all of it in order.
> - The Blender copies of the sets live in Higgsfield 3D scene-builder projects (`blender/higgsfield/projects.json`); `python ninety-nine/tools/higgsfield_scene.py <ROOM> build|imports|place|proof` prints what the scene-builder MCP tools take. Rebuild a project after changing a set in `build_rooms.py`. All of them are stale since the continuous building: the tool must first learn doorways, `floorY`, pitched boxes, hidden props, `noFloor`, `fixed` parts and the polish's prop builders, as listed in [[blender/higgsfield/REBUILD_NOTE|REBUILD_NOTE]]. Until then it strips the runtime-only keys and warns about props it cannot build.
> - Music is generated (`ninety-nine/src/music.js`), not a file — nothing under `assets/aud` is music, and nothing there needs a licence.
>
> ## Docs-as-vault
>
> This folder doubles as an Obsidian vault (`.obsidian/graph.json` sets graph color groups by tag: `router`, `game-code`, `generated-asset`, `design-doc`, `blender-pipeline`, `raw-source`). When adding a new file that belongs in the knowledge graph, add it as a bullet with a real `[[wikilink]]` (not a backtick mention) to the relevant section note, and vice versa — a mention without a wikilink is invisible to the graph and shows up as an orphan.
>

### Source file: docs/Design Docs.md

> ---
> tags: [design-doc]
> ---
>
> # Design Docs
>
> ← [[README|Router]]
>
> The 4 numbered specs. Doc 1 is the master source of truth; Docs 2–4 derive from it and must not contradict it. Where the build has moved on from a spec, a dated amendment note at the top of the section says so, and the spec text below it is left as written. The 2026-10-03 notes cover the continuous first-person walk; the 2026-10-16 notes cover the engine follow-ups that came after it.
>
> - **[[docs/01_GAME_LOGIC|01_GAME_LOGIC.md]]** — Doc 1 of 4: game logic. Source material: *Following The Sheep* (Elijah Skinner); structural reference: *Right Door Wrong Exit*. Defines the spine, scoring (conformance/dissonance), the canon rules (e.g. C4 "never say you"), and ending resolution. §4 and §5 carry 2026-10-03 amendments: choices are walked thresholds, and friction comes from movement.
> - **[[docs/02_GENERATION_HIGGSFIELD|02_GENERATION_HIGGSFIELD.md]]** — Doc 2 of 4: generation pipeline for Higgsfield (stills) and Kling (motion + audio). Output filenames are consumed directly by Doc 4. See [[ninety-nine/assets/Generated Assets|ninety-nine/assets/]] for the resulting files and [[blender/Blender Pipeline|blender/]] for the parallel 3D pipeline this also informs. Its S6 section carries a 2026-10-16 amendment: S6 H's breathing and footfalls are synthesized in the game.
> - **[[docs/03_MINIGAME_UX|03_MINIGAME_UX.md]]** — Doc 3 of 4: mini-game UX spec, 7 components / 11 modes. **Retired 2026-10-03**: the mini-games were removed at the author's request, along with their implementation (`ninety-nine/src/minigames/`). Choices are now threshold zones the candidate walks to, and friction comes from how he moves ([[ninety-nine/assets/Scene Flow|Scene Flow]]). Kept as the record of what was built and replaced.
> - **[[docs/04_TECHNICAL_BUILD|04_TECHNICAL_BUILD.md]]** — Doc 4 of 4: technical build spec for Claude Code. Implements Doc 1 and consumes Doc 2. It hosted Doc 3 until the mini-games went; its §6 mini-game contract is retired, and §7.4, §9 and §14 carry 2026-10-03 amendments. §4.1 (the `display` and `swing` beats, `fixed` room parts) and §7.2 (the store's hum) carry 2026-10-16 ones. Implemented across [[ninety-nine/src/Source Code|ninety-nine/src/]].
>

### Source file: ninety-nine/App Overview.md

> ---
> tags: [game-code]
> ---
>
> # App Overview
>
> ← [[README|Router]]
>
> The game: a static web app, no build step, served as-is by [[ninety-nine/tools/dev_server.py|tools/dev_server.py]].
>
> ## Entry points
> - **[[ninety-nine/index.html|index.html]]** — the single page. `#scene-layer` holds the stage's WebGL canvas: the building drawn live through the candidate's eyes. `#hud-layer` holds the threshold labels, the captions, the walk hint and the touch joystick. `#screen-layer` holds the application form, laid over the apartment's CRT while he sits at it. Then the ending card and the boot-error panel. Loads [[ninety-nine/src/main.js|src/main.js]] as a module.
> - **[[ninety-nine/style.css|style.css]]** — all styling; diegetic UI treated as "an object in the room" per Doc 4 §14.
>
> ## Subsections
> - [[ninety-nine/src/Source Code|src/]] — the engine modules (state, director, stage, the continuous building in [[ninety-nine/src/world/World|world/]], audio, etc.)
> - [[ninety-nine/assets/Generated Assets|assets/]] — audio beds and one-shots (tracked by manifest) and the optional prop library; no stills, no clips
> - [[ninety-nine/test/Tests|test/]] — the in-browser test harness and cases
>
> ## `data/` — spine, ending logic, rooms (3 files)
> - **[[ninety-nine/data/scenes.json|data/scenes.json]]** — single source of truth linking Doc 1 logic to the building (Doc 4 §15). Per scene and render it gives the room the scene is played in, `next`, the ambience, music and captions, the `onEnter` beats, and the two `thresholds`. A threshold (succumb / resist) is a zone in that room the candidate walks to: its `label`, its `zone`(s), the `exit` door and `via` connector it opens, `setFlag`, `sfxCue`, the `beat` that plays on commit, the `approach` that plays on the way, and `viaDark` (the passage stays unlit until he is in it). Beats are a small vocabulary the director runs in order (sounds, captions, doors, an `open` with an `amount` that swings a door only part-way, show / hide, light fades, the room's own atmosphere (`env`), his breathing and heavier footfalls (`breath`, `footfall`), screens, a new reading on the cab's indicator (`display`), a knocked prop's damped `swing`, held props, actors, carried moves, `together`, rides with `stops`), listed in the file's `_comment`. `beatZones` are moments that are not choices (THE PACKAGE; the silent strips down S6 H's run, where his breathing deepens). A branch may also carry `idle` (nothing chosen for so long: S2 repeats the call, S7 C commits REFUSE), `stillness` (he has stood still for so long: S4 H's ajar door swings wider), `drive` (the beats of an actor walked by his progress: S4 H's manager, 20 m ahead), `unseen` (a change made only once that part of the room is out of his view: S4 C's aisle closing up behind him), `env` (the room's atmosphere for the scene: S6 H's run takes the garage's sodium haze), `hum` (the store's hum, which carries the drone's detune; S8 H) and `bumpCount` (pushes on a locked door are counted: props appear at given counts, and at the `at`-th push a flag is set, friction is added and a caption lands; S3 H). S0 has `start` (the APPLY desk), `out` (the apartment door) and `report` (the tower). Hand-edited; its zone and door names must match `tools/build_rooms.py`. Walked in full in [[ninety-nine/assets/Scene Flow|Scene Flow]].
> - **[[ninety-nine/data/endings.json|data/endings.json]]** — Doc 1 §2.4 `resolveEnding()` output map. Each ending is a room of the building, with the `zone` that starts its pull-back (or `autoSeconds` without it), the pull-back `shot` (plus `preShot`, `show` and `beats`: PENDING sits him down, the hands appear with the 99 slip in his lap, and the speaker says "One hundred."), its ambience, `flagOverlays` (NEVER_SAT hides the boardroom's `mychair` and the slip on it; DELIVERED hides the package he carried in until the camera leaves him), `routes` (the way on from a room that is not the ending's: the store's staff door, toward the waiting room), `hum` (EXPULSION carries the store's hum on) and the pre-card hold. It drives which ending card renders.
> - **[[ninety-nine/data/rooms.json|data/rooms.json]]** — every 3D set (one per scene+render, per ending, plus the street and the dive) and the eight `CN_*` connectors that join them. Each record has its doorways (`doors`), threshold `zones` (a zone at a chair carries the `seat` pose he sits into), `anchors`, `entry`, camera `shots` (the carried moments, the endings' pull-backs, and the poses the Higgsfield proofs render) and catalog prop placements. A box or prop marked `fixed` stays where the room was placed when the room moves (S7 C's shaft, which the cab goes down). A light's `sync` names props whose glow follows that light. An actor's `drive` lets the director walk him by the candidate's progress. `labelInk` (`dark` / `backed`) changes how the room's labels are drawn. Generated by `tools/build_rooms.py`. Built by [[ninety-nine/src/walk/Walk Mode|walk/]] and placed in one world by [[ninety-nine/src/world/World|world/]].
>
> Note: `data/endings.json` is a different file from `text/endings.json` below (structure/routing vs. display copy for the same endings) — don't confuse the two when following a link.
>
> ## `text/` — player-facing copy (4 files)
> - **[[ninety-nine/text/endings.json|text/endings.json]]** — Doc 1 §6.4 ending-card copy. Rule C4 ("never say 'you'") deliberately breaks here, exactly once per card, in the signoff.
> - **[[ninety-nine/text/form.json|text/form.json]]** — S0 application copy: 3 fields, each a WILLING / NOT WILLING pair, read by [[ninety-nine/src/application.js|application.js]] and laid over the apartment's CRT. Two or more refusals seed the hostile render (render only, never score). Replaced Doc 1 §6.2's ten typed fields and their ghost-text degradation.
> - **[[ninety-nine/text/manifest.json|text/manifest.json]]** — Doc 1 §6.3 requisition item list, drawn on the S6 C terminal's screen (`src/screens.js`); mundane and impossible items interleave, ~60% mundane. Doc 3's MG-05, which first used it, is retired.
> - **[[ninety-nine/text/system.json|text/system.json]]** — Doc 1 §6.1 company/system copy, including what the screens say (the posting, the Harlowe desktop, the requisition title) and the spoken captions; obeys C4 without exception.
>
> ## `vendor/`
> - `three/three.module.js` — three.js r160 (MIT), the stage's renderer; `three/GLTFLoader.js` + `three/utils/BufferGeometryUtils.js` (r160 examples, MIT) load the prop library.
>
> ## `tools/` — dev-only (6 files)
> - **[[ninety-nine/tools/build_rooms.py|tools/build_rooms.py]]** — writes `data/rooms.json`. That covers every set, its default shots (`shots_for()`: in, out, loop, leave, arrive) and overrides, and the catalog placements (`CATALOG`). The continuous building adds `door()` (a doorway on a wall), `zone()` (a threshold zone), `anchor()` (an extra join point), the `cn_*` connector builders, and `check_room()`. That check fails the build when a door runs off or overlaps on its wall, a zone sits outside the floor or inside a solid box, a room lacks an entry, an alias changes more than `ALIAS_KEYS`, a fixed box collides or is floor, an actor's `drive` breaks its rules (an axis, a path that runs one way along it, a lead, an end), a light's `sync` names no prop, or hands appear outside `S0_X` / `SE_PEND`. The museum's `build_layout.py` pattern: rooms with repeated geometry come from a loop, not by hand.
> - **[[ninety-nine/tools/higgsfield_scene.py|tools/higgsfield_scene.py]]** — rebuilds one set inside the Higgsfield 3D scene builder (Blender 5.2 headless): prints the bpy code (`build`), the catalog imports (`imports`), the duplicate placements (`place`) and the proof render (`proof`) that the scene-builder MCP tools take. Same shell, props, lights and camera shots as the stage, so the Blender scene and the game agree. It strips the runtime-only keys (zones, anchors, entry...) and warns about prop types it cannot build yet. The projects are stale until rebuilt for doorways, connectors and the new props: see [[blender/higgsfield/REBUILD_NOTE|REBUILD_NOTE]].
> - **[[ninety-nine/tools/dev_server.py|tools/dev_server.py]]** — local static server with `Cache-Control: no-store` (plain `http.server` caches ES modules too aggressively) and real HTTP Range support (required for `<video>`/`<audio>` seeking; Python's default handler doesn't send 206 Partial Content). Not part of the shipped game.
> - **[[ninety-nine/tools/run_tests.cjs|tools/run_tests.cjs]]** — optional, needs Node and Playwright: runs [[ninety-nine/test/Tests|test/index.html]] in headless Chromium and exits non-zero on any failure. The suite itself needs only a browser.
> - **[[ninety-nine/tools/walkthrough.cjs|tools/walkthrough.cjs]]** — optional, needs Node and Playwright: plays whole games with the autopilot (`?autopilot=PLAN`), screenshots each scene into `tools/out/` (git-ignored) and checks each path's ending card.
> - **[[ninety-nine/tools/lib/devserver.cjs|tools/lib/devserver.cjs]]** — what the two runners share: start `dev_server.py` on a free port, find Playwright, the SwiftShader flags.
>

## 12. Full commit log (date, hash, subject)

Every commit, oldest first. Merge commits are shown with their subjects.


### 2026-09

- 2026-09-13 edd58b99 Initial commit
- 2026-09-30 a59aff5e Add ninety-nine game, design docs, Blender pipeline, and assets
- 2026-09-30 1dfd5e31 Add root index.html redirect and .nojekyll for GitHub Pages
- 2026-09-30 636f6f68 Merge pull request #1 from groot99-droid/claude/affectionate-brahmagupta-v3uqqn [merge]
- 2026-09-30 af63aba6 Fix prologue video direction, audio mix, spine logic; add generative music and walkable 3D rooms
- 2026-09-30 3b1c882c Merge pull request #2 from groot99-droid/claude/sleepy-ramanujan-digrr2 [merge]
- 2026-09-30 776ad553 Fix soft-loop race that clobbered transitions; compose render-flip transitions
- 2026-09-30 c36486a2 Merge pull request #3 from groot99-droid/claude/trusting-cerf-do1ws9 [merge]
- 2026-09-30 dc99f294 Fix hold-to-run, revamp the 3D rooms, faststart the transition clips
- 2026-09-30 e06eb2e1 Merge pull request #4 from groot99-droid/claude/eager-cray-d280uk [merge]

### 2026-10

- 2026-10-01 0681d901 Replace the AI video/still pipeline with live 3D sets and camera shots
- 2026-10-01 2ef202af Build every set in the Higgsfield scene builder and shoot its proofs
- 2026-10-02 c1d415e7 Merge pull request #5 from groot99-droid/claude/exciting-albattani-46k7o3 [merge]
- 2026-10-03 65184db2 Make the game one continuous walk: rooms joined by doorways, choices by walking
- 2026-10-03 5f36a82e Walkthrough fixes: floor re-sync after carried moves, autopilot doorways, dev scene start
- 2026-10-03 8e4d308a Locked doors shudder and rattle when walked into; branches can count the pushes
- 2026-10-03 e9674246 Autopilot: mark a blocked cell and re-plan when stuck; log the route
- 2026-10-04 9684b873 Document the continuous walk; note the Higgsfield rebuild for later
- 2026-10-04 fc6d0c9d Director debug state keeps the ending id after the card shows
- 2026-10-04 77069547 Merge docs, vault notes and the Higgsfield rebuild note [merge]
- 2026-10-04 58186063 Dev start: enter through the room's entry; a held-entry room gets its arrival corridor
- 2026-10-04 be623ddc S0 polish: photoreal street facades and tower, dawn light, street furniture; apartment desk, bed, door glow
- 2026-10-04 7012da8d S0 polish: concrete tower base, the address from the crossing, quieter lamps, fewer shadow casters
- 2026-10-04 264f9550 Polish S1-S2: the waiting room and the call, both renders
- 2026-10-08 3a83d2f5 Merge branch tip (dev start fixes, docs) into the polish worktree [merge]
- 2026-10-08 b78a17e1 Merge branch tip (dev start fixes, docs) into the polish worktree [merge]
- 2026-10-08 02feb1f8 Polish S1-S2: maroon chairs, dark lobby glass in H, one wall tile
- 2026-10-08 40097503 S2 H: the speaker clicks, then hisses, then "Shaun."
- 2026-10-08 962445de Port the test suite to the continuous walk; add headless runners
- 2026-10-08 b3e2618e S0 polish: his desk lamp, soft drifting dust, smoother desk wood, hands in the sit frame; a street-size clock, the address plate, a touch more dawn light
- 2026-10-08 06324bde S1-S2: a thin spine inside the reception counter for the autopilot
- 2026-10-08 a7f1632c S0 street: plain stone kerbs, pavements that cast no shadow (cleaner kerb edges under the low sun)
- 2026-10-08 bc53ef82 S0 street: a fifth parked car before the crossing
- 2026-10-08 c4d64380 S0 street: dawn through his open street door warms the foot of the stairs; street sign poles collide
- 2026-10-08 903123c0 S3: velvet curtain, live ENTER sign, laser reader, dead street, counted pushes
- 2026-10-08 43d624e4 S3 C: dust in the green light, following the sign's cycle
- 2026-10-08 c0edbb86 S4 polish: open the floor, make both thresholds read, keep the H manager 20 m ahead
- 2026-10-08 8f3adb73 S4: painted office walls, a slower approach, a brighter ajar gap
- 2026-10-08 3e4c9955 Polish S5-S6: the desk under one troffer, the garage, the run and its edge
- 2026-10-08 1efafddc S5-S6: label READ, car doors on the aisle side, rebar past the lip, fifth car in sight
- 2026-10-08 f4aff7e9 S5 C: the troffer's own spill on the ceiling tiles round it
- 2026-10-08 f91521d7 S5-S6 C: STAPLE commits right behind the chair; softer station lamps
- 2026-10-08 583c775e Polish S7: the freight cab, its gate, its indicator, and a ride that goes down in steps
- 2026-10-08 08fab5b1 S7 C: REFUSE covers the whole doorway, jamb to jamb
- 2026-10-09 3f5beaee Polish S8 and the endings: mailroom, dive, store, boardroom, pending room
- 2026-10-09 807896bf S8 polish: cavernous mailroom fog, lamp pools, form readable in the box
- 2026-10-09 29501286 S1-S2 review: placard no longer blacks out, S2 door labels stay in view
- 2026-10-09 7c8c48c4 Merge the S1-S2 polish: the waiting room and the call [merge]
- 2026-10-09 d22eaf19 Engine requests from the polish pass
- 2026-10-09 31b949a7 S8 + endings: blurred faces, carton towers, a glass boardroom table
- 2026-10-09 c77a6680 Boardroom: the package's stain soaks across the glass
- 2026-10-09 1de57331 S0 street critic: no sparkle on kerbs and paint, the dead end in his building's shade, a stone tower base
- 2026-10-09 2b75b38f S4 critic: unskippable H bands, a step back at the far door, tinted office furniture
- 2026-10-09 c70cc94c S3 review: readable labels, no stray lamp, counted pushes add friction
- 2026-10-09 be465155 S4 H: leave the breaker panel untinted
- 2026-10-09 7b970fed S3 review: pure black behind the curtain, a clear pane with no false lamps
- 2026-10-09 20510bff S5-S6 critic: water that reads as water, a well with its grate, soft troffer dust
- 2026-10-09 1cb5fc10 Merge claude/blissful-faraday-bdt4c6 into polish-S7 [merge]
- 2026-10-09 acd6384e Merge the S0-street polish (reviewed) [merge]
- 2026-10-09 8bf25696 Merge the S5-S6 polish (reviewed) [merge]
- 2026-10-09 8e0bca75 Merge the S4 polish (reviewed) [merge]
- 2026-10-09 9f40c4f8 Merge the S3 polish (reviewed) [merge]
- 2026-10-09 8b272f9a Merge branch 'claude/blissful-faraday-bdt4c6' into polish-S8-E [merge]
- 2026-10-09 ae6300b6 Engine review fixes: the cab seals, EXIT stops every chain, touch works
- 2026-10-09 2c66f2af Endings can run their own beats; a beat can start the music
- 2026-10-09 63811c69 S7 review: one continuous ride, a dark panel, a real caged bulb, 25 s of nothing refuses
- 2026-10-09 1fc18c7e Merge claude/blissful-faraday-bdt4c6 into polish-S7 (the cab seal fix, the S3-S6 polish) [merge]
- 2026-10-09 7692b322 S8-E critic: printed slips, maroon pending chairs, caustics, store fascia, shafts of high-bay light
- 2026-10-09 183c431e S8-E critic: the twelve faceless, the ring stops when he lifts the package
- 2026-10-09 ffbae9ec S7 C: the press-to-ride beats held as one move; REFUSE pulls him to the cab's middle
- 2026-10-09 eae1d025 S7 C: the cab's docstring says what it is now
- 2026-10-10 3ea9b8d8 S8-E critic: caustics on the surface overhead, the form clear of the sheet it lies on
- 2026-10-10 84d12147 Merge the S8-E polish (reviewed) [merge]
- 2026-10-10 58f762ea S7 follow-ups and the last review findings
- 2026-10-10 14666bba Give each clashing prop builder its own name; refresh the docs after the polish
- 2026-10-10 0823d0e6 Endings: PENDING's hands in his lap before the call; the pending curtain in velvet
- 2026-10-11 854fc58c Integration review fixes: connector collars, light slots for the next room, still holds, prop details
- 2026-10-11 20293e8f Docs: the endings' order and frozen hold, connector collars, the light slots kept for the next room
- 2026-10-15 60208281 Engine: fixed room parts, swing and display beats, the cab's materials
- 2026-10-15 f07a76d8 S4 materials and builders: beige cinderblock, green troffers, one warped cubicle texture
- 2026-10-15 82e7c710 Engine: actors driven by the candidate's progress, changes made out of view, doors swung part-way
- 2026-10-15 2b4e599f S4: the manager driven 20 m ahead, the aisle that closes behind him, the door that opens for stillness
- 2026-10-15 33494468 S7 C: a real shaft, the doors handed over, the bulb swings, one indicator
- 2026-10-15 da32f705 S4 H: the manager starts 20 m ahead of where the scene begins
- 2026-10-15 80e5ca76 skinned_glb: box-project UVs onto a catalog model that has none
- 2026-10-16 9a49de2c stillness: still means within 5 cm of where he stopped, not under 2 cm a frame
- 2026-10-16 76c0bd20 unseen: the default point falls back to the record's entry doorway
- 2026-10-16 4fb3d577 canon.text: drop the S4 H corridor bands from a comment (the drive replaced them)
- 2026-10-16 dbfe8aeb S7 C follow-up: the landings check walks every beat list; the cab's floor clanks
- 2026-10-16 18ac4ce5 Engine follow-ups (env): a room's own atmosphere, light sync, the store hum, S6 H's breath, dev score
- 2026-10-16 b1433e9f The hum's leave check reads the room's group, not a fresh instance list each frame
- 2026-10-16 08c8aba5 Look follow-ups: clear glass, velvet curtain doorways, jib doors, wood grain
- 2026-10-16 d0413e0e Catalog tints: keep the models' vertex colours and multiply the slot in
- 2026-10-16 eff0d1c0 Controls: clamp a blocked step to the wall; swim with no ascent
- 2026-10-16 ea9d61e6 Tests: the look keys, slots, catalog tints and controls
- 2026-10-16 63a55c87 Labels: a room's own ink -- dark on a pale halo, or on a dark plate
- 2026-10-16 08d681ef Dev start into the dive: swim before the teleport
- 2026-10-16 e58df1a1 Checks for the S4 keys: an open beat's amount is 0..1, a drive names only the keys stepDrive reads, and drive.footstep needs footsteps
- 2026-10-16 fad59835 Velvet doorway halves hang behind the drape round them
- 2026-10-16 4f16138a Env critic: owned glow freed with the sync clones, layers cleared at the card, a dev-score test
- 2026-10-16 8f61f95f Swing: each knock keeps its own period
- 2026-10-16 da6fb212 Merge fu-s4: actors driven by progress, changes made out of view, S4 stillness and materials [merge]
- 2026-10-16 5a3bb201 Merge fu-s7: a fixed shaft for the cab, swing and display beats, the cab's materials [merge]
- 2026-10-16 02d26218 Merge fu-env: a room's own atmosphere, light sync, the store hum, S6 H's breath, the dev score [merge]
- 2026-10-16 0add444d Merge fu-look: clear glass, velvet doorways, jib doors, catalog tints, wood grain, the step clamp, no ascent swimming, label ink [merge]
- 2026-10-16 9ba2e8f5 Docs for the engine follow-ups: drives, unseen, the shaft, env, hum, look
- 2026-10-17 a985b20c Docs check for the follow-ups: six small corrections
- 2026-10-17 e89297e0 Fixes from the follow-ups review: the store hum, the velvet doorway, the sedan's door
- 2026-10-17 9f93ef55 Merge pull request #6 from groot99-droid/claude/blissful-faraday-bdt4c6 [merge]
- 2026-10-29 bfc1d4be Run the test suite in CI, and the autopilot walkthroughs on pull requests
- 2026-10-30 7a74993e build_rooms: fail the build when scenes.json or endings.json names a missing zone, door or connector
- 2026-10-30 bb0cc618 Merge pull request #7 from groot99-droid/claude/pensive-curie-kr7vcq [merge]
- 2026-10-30 4cc65989 Docs: record that the tests now run in CI

### 2026-11

- 2026-11-04 80343e77 Merge pull request #8 from groot99-droid/claude/pensive-curie-kr7vcq [merge]
- 2026-11-19 be77354d docs: README lists CI and the real .claude contents; the Blender scene plan is marked historical
- 2026-11-19 f5b6aa1d Merge pull request #9 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
