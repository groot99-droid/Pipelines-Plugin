# Right-Door-Wrong-Exit

**Liminal click-through game with a first-person 3D walk.** Source: https://github.com/groot99-droid/Right-Door-Wrong-Exit

Generated 20 November 2026 from the repository clone (`git log`, `git ls-files`, and the files at HEAD). Counts are as cloned. Commit dates are git author dates in UTC and can differ from when the work was done (merged PRs, integration passes).

## 1. Numbers

| Measure | Value |
|---|---|
| Commits (all branches) | 47 (33 non-merge, 14 merge) |
| First commit | 2026-08-22 |
| Last commit | 2026-11-19 |
| Days with commits | 10 |
| Tracked files | 52 |
| Checked-out branch | HEAD |
| Commit authors (non-merge, by name) | Claude: 28; groot99-droid: 5 |

Author names are git author names: "Claude" marks commits made by a Claude session, and the owner's GitHub handle marks commits made by the owner. Email addresses are left out.

**Tracked files by type (top 15):** .js 20; .mp4 14; .mp3 8; (none) 2; .html 2; .mjs 2; .yml 1; .png 1; .md 1; .css 1

**Tracked files by top-level folder:** (root) 28; walk 15; vendor 5; tools 3; .github 1

## 2. Activity by month and by day

| Month | Non-merge commits |
|---|---|
| 2026-08 | 20 |
| 2026-09 | 3 |
| 2026-10 | 9 |
| 2026-11 | 1 |

**Per day (non-merge commits):** 2026-08-22 7; 2026-08-24 9; 2026-08-25 4; 2026-09-30 3; 2026-10-01 1; 2026-10-03 2; 2026-10-09 2; 2026-10-29 3; 2026-10-30 1; 2026-11-19 1

## 3. Layout (folders and file counts)

- **(repository root)** 28 files
- **walk/** 15 files
  - walk/scenes/ 8
- **vendor/** 5 files
  - vendor/three/ 5
- **tools/** 3 files
- **.github/** 1 files
  - .github/workflows/ 1

## 5. CI workflows

- `.github/workflows/walk-test.yml`: walk test

## 6. Documents inventory (1 Markdown files)

Markdown files by folder (top 25): (root) 1

- `README.md` (4295 words): Right Door, Wrong Exit. Sections: The loop; Running locally; The 3D walk; Structure; Notes

## 10. Pull requests merged (13)

- 2026-08-22 #1 from `groot99-droid/claude/repo-strengths-improvements-xg77rc`
- 2026-08-22 #2 from `groot99-droid/claude/repo-strengths-improvements-xg77rc`
- 2026-08-24 #3 from `groot99-droid/claude/interactive-loading-screens-7vgp3q`
- 2026-08-24 #4 from `groot99-droid/claude/interactive-loading-screens-7vgp3q`
- 2026-08-25 #5 from `groot99-droid/claude/interactive-loading-screens-7vgp3q`
- 2026-08-25 #6 from `groot99-droid/claude/interactive-loading-screens-7vgp3q`
- 2026-08-25 #7 from `groot99-droid/claude/interactive-loading-screens-7vgp3q`
- 2026-09-30 #8 from `groot99-droid/claude/dreamy-edison-pmxzka`
- 2026-09-30 #9 from `groot99-droid/claude/dreamy-edison-pmxzka`
- 2026-10-01 #10 from `groot99-droid/claude/keen-euler-x8wtu5`
- 2026-10-09 #11 from `groot99-droid/claude/happy-galileo-qjw2sc`
- 2026-10-30 #12 from `groot99-droid/claude/pensive-curie-kr7vcq`
- 2026-11-19 #13 from `groot99-droid/claude/inspiring-cori-juqfrm`

## 11. Source documents (verbatim)

Each file below is quoted from the repository at HEAD. Lines start with ">" so its headings do not mix with this document's.

### Source file: README.md

> # Right Door, Wrong Exit
>
> A single-page, click-through liminal-space walkthrough in the backrooms genre. It opens on an
> arcade-cabinet title card with a **START** button; starting the walk drops you into a loading
> screen — the clip alone, no overlay — that runs for five seconds and then glitches into the
> first room. Each room plays a looping video behind a
> typewritten caption, and once the caption finishes typing a **NEXT** button appears. NEXT then glitches you
> *into* the room you were just looking at, in first person, and you have to walk to its exit —
> the stairs, the end of the hall, the couch, the arch, the grate, the red glow, the EXIT door —
> before the next loading screen plays. Every room has a 3D scene; after the last one the loop
> returns you to the title card.
>
> Built with plain HTML, CSS, and JavaScript — no framework, no build step. The only dependency is
> a vendored copy of [three.js](https://threejs.org/) r160 (MIT, `vendor/three/`) for the 3D scenes.
>
> ## The loop
>
> ```
> gate ──click──▶ 0.PNG (home) ──START──▶ a.MP4 (5 s of clip)  ──glitch──▶ A.mp4 (room + caption)
>                               ▲                                              │
>                               │                                            NEXT
>                               │                                              ▼
>                               │                    3D walk: reach the room's exit
>                               │                                              │
>                               └────── b.MP4 … g.MP4 ◀── fade to black ───────┘
> ```
>
> | Room | Video | Loading clip | Audio | 3D walk | Phase |
> | --- | --- | --- | --- | --- | --- |
> | The Dining Room — The Anchor | `A.mp4` | `a.MP4` | `A.mp3` | `dining` · find the stairs | 1 · The Departure from Reality |
> | The Hallway — The Descent | `B.mp4` | `b.MP4` | `B.mp3` | `hallway` · walk to the end | 1 · The Departure from Reality |
> | Teal Room, Square Door — The Glitch | `C.mp4` | `c.MP4` | `C.mp3` | `teal` · find somewhere to rest | 2 · The Holding Cells |
> | Teal Room, Arched Door — The Mutation | `D.MP4` | `d.MP4` | `D.mp3` | `teal2` · get through the arch | 2 · The Holding Cells |
> | Flooded Corridor — The Decay | `E.mp4` | `e.MP4` | `E.mp3` | `flooded` · reach the red door | 3 · The System Breakdown |
> | Trampoline Park — The Macro-Structure | `F.mp4` | `f.MP4` | `F.mp3` | `trampoline` · keep moving | 4 · The Empty Expanse |
> | Grocery Store — The Anomaly | `G.mp4` | `g.MP4` | `G.mp3` | `grocery` · find the exit | 4 · The Empty Expanse |
>
> The home screen runs on `0.PNG` and `0.mp3`.
>
> ## Running locally
>
> Serve the directory with any static file server (the videos need to be fetched over HTTP, not
> opened via `file://`):
>
> ```bash
> python3 -m http.server 8080
> ```
>
> Then open `http://localhost:8080/index.html`.
>
> ## The 3D walk
>
> After the Chronicle Museum walkthrough (`Earth_Worldbuild/_Museum`), each scene is a first-person
> room built in three.js from code — no model downloads. Pressing NEXT in a room that has a scene
> glitches into it; an objective sits at the top of the screen (**FIND THE STAIRS**, **WALK TO THE
> END**) and changes to the arrival prompt (**GO UP**, **THE END**) as you get close. Stepping onto
> the exit hands the camera over for a short climb or approach, fades to black, and the next
> chapter's loading screen plays, its audio track starting as usual. A white **SKIP** tab is offered
> during a walk, as on the loading screens, so a room is never a dead end.
>
> | Input | Action |
> | --- | --- |
> | `W A S D` / arrows | walk |
> | mouse | look (click the room to capture the mouse; click-drag works if the browser refuses Pointer Lock) |
> | touch | left half of the screen: a thumb joystick appears where you press · right half: drag to look |
> | `E` / `Space` / `Enter`, or a click once the mouse is captured | use the thing in front of you, when the prompt offers it (or click the prompt; on a phone, tap it) |
> | `SKIP` tab | straight to the loading screen |
>
> ### Scenes
>
> - **`dining`** — the Dining Room: cream plaster walls, green shag carpet, the round maple table
>   and four arrow-back chairs, the sideboard with its green ceramic lamp, the wall of family
>   photographs, sheer curtains, a light switch, and the dark, steep, green-carpeted stairwell in
>   the back wall. Reaching its foot climbs you up towards the door at the top. Someone was getting
>   ready for guests: the good china stands in crooked towers against the right wall, between the
>   curtains and the front wall, beside the folded tablecloths, and a short stack waits on the
>   sideboard.
> - **`hallway`** — the Hallway, built to its room video: you start on a lower landing at the
>   foot of a short carpeted flight (two wide low treads, then five steps) that climbs into a
>   long, narrow corridor of pale plaid-printed walls, a worn tan diamond-pattern carpet, and
>   surface-mounted twin-tube fluorescents that flicker one at a time while the buzz gets louder
>   the further you walk. At the far end an amber-lit vestibule, its ceiling stacked with light
>   bars, and under it a stairwell of mossy pixel-block stone going **down**, into the shaft of
>   the next loading clip.
> - **`teal`** — Teal Room, Square Door: the clean teal box, cream ceiling, coarse brown flecked
>   carpet, the orange angular leather sofa, the plain doorway that is pitch black (it blocks: "it
>   just swallows it"), the little blocky plant, and from the log a fake window whose sun never
>   moves and a watch on the HUD that runs backward. Reach the couch and close your eyes; the
>   next clip is the sleeper on it.
> - **`teal2`** — Teal Room, Arched Door: the same room, wrong. You wake up low beside a rounded
>   cognac sofa and stand; the room is narrower, the doorway is a black arch, the plant is tall
>   and spiky. Patches of wallpaper are peeled back on a glowing green grid that pulses; the walls
>   breathe; the patches shift when you are not looking; a hum rises the closer you get. Get
>   through the arch before it finishes.
> - **`flooded`** — Flooded Corridor: white tile to hip height, steel handrails, a painted sky
>   along the whole left wall, empty wooden frames down the right, square recessed light panels,
>   the yellow tactile strip, and a skin of standing water that mirrors the lights (the room is
>   drawn again upside down under a glossy floor: no render target, one extra draw call per
>   material). Drips fall from the ceiling as square blue blocks that melt into puddles; the
>   corridor groans. The red door at the end is the lure: the grate in front of it sags underfoot,
>   then gives way, and you fall into the riveted shaft of the next clip. Against the painted sky,
>   heaps of sodden cardboard boxes and wet paper, slumped where the water left them; on the first,
>   on the carton at its top, three photographs, still dripping.
> - **`trampoline`** — Trampoline Park: black beds edged in yellow set in orange padded frames,
>   pale pads between, padded columns, angled bed walls, a dark truss ceiling with a lattice of
>   LED panels, and the concrete apron you land on. One 28 m cell of it is drawn four times
>   (instanced) and you are wrapped back onto it: the ground repeats, the same scuff mark passes
>   under your feet, DISTANCE reads NaN. After a hundred metres or so a digital chime sounds and
>   a single red glow appears on the horizon. Head for it; the next clip's radar finds it.
> - **`grocery`** — Grocery Store: glossy speckled vinyl, an acoustic-tile ceiling with continuous
>   fluorescent rows (the left one flickers), cream columns, empty grey gondola shelving, and in a
>   clearing at the heart of it the red cart roped off with sagging caution tape. The shelving is
>   a **maze** (a seeded perfect maze with a few loops, generated at build time; the test checks
>   it is solvable): the entrance doors behind you are black glass and locked, the anomaly pings
>   when you come near the cart, and the lit EXIT sign shows over the shelves on the far wall.
>   Find the way. The exit closes the loop: a fade, and the title card. The shelves were stripped,
>   but what was left has been pushed into the dead ends of the aisles: pyramids of identical
>   unlabelled tins with flats of cardboard beside them. In three of them one tin is red.
>
> ### Mini games
>
> Three rooms have one, and each is a bonus: the exit is open from the start and the game never
> touches it, so rushing through (or SKIP) works as before. A line under the readout keeps the
> score from the moment you arrive, and stops changing once you reach the exit. The things you can
> use are targets: when you stand within reach and look at one, a prompt appears under the middle
> of the screen (`E · TAKE THE RED TIN`, a button you can click; on a phone `TAP · …`), and `E`,
> `Space`, `Enter`, a click while the mouse is captured, or a click on the prompt uses it.
>
> | Room | Game | Win |
> | --- | --- | --- |
> | `dining` | **Lights Out**: when the lamp clicks off, one of the photographs on the wall changes (turned upside down, gone to grey lines, gone dark) and stays changed until you find it; the next one changes at the first lamp-off after that. Every photo is a target while a change is waiting, so the prompt (`THAT ONE?`) gives nothing away; a small picture light comes on over the photo it points at, and a wrong guess counts nothing. | three found: the lamp stays on, and the room holds still |
> | `flooded` | **Fill the Frames**: take the photographs off the sodden heap, one at a time, and hang them in the empty frames down the right. | three hung: the corridor stops groaning for a while, and the painted sky's clouds start to drift (with reduced motion the sky clears instead, and holds still) |
> | `grocery` | **Shopping List**: find the three red tins in the dead-end pyramids, then put them in the roped-off cart. | the cart has its tins: `PING_ACKNOWLEDGED`, and the anomaly and the flickering row hold steady |
>
> ### Piles
>
> Every pile belongs to one room: the china and linen in the dining room, the sodden boxes and paper
> in the flooded corridor, the tins and cardboard flats in the grocery store's dead ends. They are
> built by the seeded generators in `walk/piles.js` (`pyramid`, `stack`, `heap`) through the room's
> builder, so a pile costs one draw call per material however many pieces it has, and looks the same
> on every visit. Every piece is measured from its own geometry and set down on the floor or on the
> pieces under it, never inside one and never below the floor (in a mirrored room it never crosses
> its own reflection); a sheet of paper or a photograph keeps 1.5 mm off what it lies on. So where
> two things meet there is one surface to draw, not two fighting over the same pixels. A pyramid's
> tins are spaced by their real width, each layer resting on the one below; a stack's piece rests on
> the one below it whatever its twist, and two stacks side by side stand apart. A heap is settled
> piece by piece: each is dropped on what is already there and comes to rest on it, tilted down the
> slope it lands on, inside a keep-in box the room gives it (off the wall tile, short of the
> walkway) and under a ceiling (the handrail brackets). It must be held the way it could bear: what
> holds it is round its middle, and it reaches no further past that than a box could stand out (a
> third of its narrow side), cardboard trodden flat 6 cm or a wet sheet 2 cm, so nothing juts out
> flat over a drop like a shelf; a box with something lying on it has its lid pressed flat, so what
> lies there lies on the lid; and no flat face of a piece lies within 2 mm of the flooded corridor's
> water. A heap can be given a crown, one more piece put down last where the room asks and settled
> like the rest: the photographs' carton, its lid broader than the prints, so they lie on it whole;
> and wet paper can be strewn over the bare lids round it, each sheet wholly on its lid. A heap is
> settled a frame's worth at a time, so building one never holds the page for long. Every pile is
> solid: its collider is the box of what it drew. A game's item (a red tin, a photograph) is drawn
> on its own, so it can be taken away while the pile and its collider stay put. The grocery piles go
> only in dead ends, where nothing lies beyond them, so no aisle is ever blocked.
>
> ### What moves
>
> Each room video is a fixed-camera, five-second loop with one thing happening in it, and each
> 3D room plays the same beat, stretched to a 20–40 s cycle so it comes round whether you rush
> or dawdle (`cycle()` and the hash-driven `stutter()` in `walk/build.js` keep it deterministic;
> `prefers-reduced-motion` turns the strobes into slow fades):
>
> | Room | In the clip | In the room |
> | --- | --- | --- |
> | `dining` | still, then the green lamp clicks off at 4.35 s | every 28 s the lamp clicks off for three seconds (light, bulb and shade), with a switch click |
> | `hallway` | one fluorescent tube at a time greys out and comes back | nine fixtures with a material each, stuttering one at a time; the buzz rises down the hall; the amber bars breathe |
> | `teal` | the black of the doorway lifts for a moment at the end | every 24 s the doorway lifts to charcoal and swallows again; the camera drifts if you stand still |
> | `teal2` | a slow low push toward the arch, the leaves stirring | you drift toward the arch as you stand; the plant sways; the arch keeps growing and snaps back |
> | `flooded` | the water shimmers; the red door is lit, then dark, then stutters on | two water skins scrolled against each other; a 30 s door cycle: lit, dark for a long while, stutter, steady |
> | `trampoline` | the LED lattice pulses and flickers | the LEDs breathe on a 2.3 s sine with a hash-driven stutter; the panel lights follow |
> | `grocery` | the tube rows breathe, with a hard dip and a smaller one | all rows breathe; twice a 9 s loop the store dips (the left row still flickers on its own) |
>
> Each room is one file: `walk/walk.js` registers the rooms in chapter order and maps ids to
> `walk/scenes/<id>.js`. A scene module exports `meta` (objective, arrival prompt, start position,
> optionally `riseFrom` to wake up low, and `chapter`: its letter, title, epithet, track, loading clip,
> room video, caption tilt, caption, stamp and log entry) and `build({ quality, yieldFrame })`, which returns the
> batched geometry group, the lights, the AABB colliders, the walkable bounds, the trigger and
> near-goal boxes, the exit camera path (an array, or a function of where the player is), the
> exit's duration / easing / fade / shake, fog and exposure, and optionally `update(pos, dt,
> camera, ctx)` for animation (drips, flicker, breathing walls, the light pool) and `wrap(pos)` for
> an endless floor. A mini game adds `interact`, a list of targets (`{ x, y, z, reach, size, label,
> enabled(), use(ctx) }`, and optionally `hover(on)`, told when the prompt starts and stops pointing
> at it; picked by `walk/play.js`), and optionally `dispose()` for anything the scene swapped out of
> its materials. `ctx` lets a scene change the objective, write the readout and tally lines, and
> play the synthesized sounds (`walk/sound.js`: hum, buzz, chime, drip, groan, ping, click, and
> pickup, wrong and win for the games), which follow the SOUND toggle; it also says whether motion
> is reduced (`ctx.reduced`) and whether the exit has begun (`ctx.exiting`).
> `?chapter=C` in the URL makes START open on that room.
>
> ### Built for phones
>
> - **Nothing to download but three.js.** Every texture — carpet pile, plaster, wood grain,
>   curtain pleats, ceiling tiles, the wallpaper, the faded photos — is generated on the device from
>   seeded noise (`walk/textures.js`) with normal and roughness maps, at 512 px on a phone and
>   1024 px on a desktop. Generation is spread over idle callbacks while the room video plays, so
>   the video never stutters.
> - **The room is built while you read the caption**, and its shaders are compiled then, so NEXT
>   drops straight in.
> - **One draw call per material**: geometry is merged per material (`walk/build.js`), and the
>   trampoline park's cell is instanced. Draw calls per room run from 14 (teal) to 45 (the grocery
>   maze with its piles and floor reflection); every room keeps a constant number of lights.
> - **Static shadow maps**: the rooms with shadow-casting lamps render their shadow maps once per
>   walk; the long rooms use a constant pool of lights that re-park on the nearest fixtures as you
>   walk, so the shaders never recompile.
> - **Adaptive resolution**: the pixel ratio drops when frames run long and climbs back when
>   there is headroom. No post-processing pass; AgX tone mapping in the renderer.
> - Collision is circle-vs-box sliding (everything in these rooms is a box), and a portrait phone
>   gets a taller field of view.
> - If the module or WebGL is unavailable (an old browser, a blocked fetch) the game falls back
>   to the loading screen as before.
>
> ### Testing
>
> `tools/walk_test.mjs` drives the real page in headless Chromium (software WebGL). For every
> chapter it opens `index.html?chapter=<id>`, goes through the gate and START, ends the caption,
> presses NEXT, and drives the room with deterministic steps: screenshots, the room's own checks
> (the table and the black doorway block, the watch runs backward, you wake up low and stand, the
> grid pulses, the drips fall, the park wraps and the chime brings the glow, the maze has a route
> and the light row flickers, and every room's animation plays: the lamp clicks off, the tubes
> flicker one at a time, the doorway lifts, the arch grows, the red door lights, the LEDs pulse, the
> rows dip), the piles and the mini games, the scripted route to the exit, and then that the right
> loading clip (or the title card, after the grocery store) follows. A room with a game is visited
> twice: first straight to the exit without playing (it opens; in the dining room the climb starts
> just before a lamp-off, and no photograph changes during it), then for the piles and the game. One
> pile in each room (the china, the sodden heap, a pyramid of tins, before and after its red tin is
> gone) and every stack of trays is walked into and blocks you. The piles are measured as they are
> on screen (every vertex of every piece the test measures is one the room draws): no two pieces of
> a pile pass into each other, none sinks into what it stands on, and each lies inside its collider
> and the room; the grocery piles and their trays sit only in dead ends, the trays clear of the
> tins; the heaps stay off the wall, out of the walkway and under the handrail, and every heap piece
> is held where it touches and never stands out over a drop; the photographs lie level without
> crossing, each on the carton over nine tenths of it at least, and so does the wet paper strewn on
> the photo heap's lids; no drip lands on a heap. Each game is played through with "use" as a player
> gives it: `E`, `Space` and `Enter` in turn, pressed on the keyboard (a held key's auto-repeat must
> use nothing), and a tap on the prompt in `--mobile`. Along the way: the score line is up from the
> start and keeps the count, the photo the dining prompt points at is lit (and on screen its own
> pixels are at least 15% brighter for it), a changed photo is put back as it was, the flooded sky
> clears and holds still under reduced motion, and the game leaves the exit's trigger and colliders
> as they were. It reports draw calls, triangles and console errors, and writes `tools/out/*.png`
> and `report.json` (git-ignored).
>
> ```bash
> node tools/walk_test.mjs                    # desktop viewport, all chapters
> node tools/walk_test.mjs --mobile           # 390×844, touch, 2× DPR
> node tools/walk_test.mjs --scene teal,G     # some chapters (scene id or letter)
> node tools/scene_shot.mjs flooded --view "grate:29,1.62,0,-1.57,-0.3"   # look-dev shots
> ```
>
> `tools/scene.html?scene=<id>` runs a room on its own (what `scene_shot.mjs` drives).
>
> Playwright and Chromium are found at their usual global locations (`CHROMIUM=` overrides).
>
> ## Structure
>
> - `index.html` — four stacked screens (home / loading / room / walk) plus the glitch veil and log
>   panel, and the import map for three.js.
> - `styles.css` — screen layout, glitch and flicker animations, typewriter card, log panel, walk HUD
>   (objective, readout, tally, use prompt, hint, joystick, fade).
> - `script.js` — the state machine that drives home → load → glitch → room → next → walk → load,
>   over the chapters it loads from the scene files at startup (`walk.js` `chapters()`; START waits
>   for them).
> - `walk/walk.js` — the walk runtime: renderer, scene registry, prepare/start/skip, adaptive
>   resolution, the exit animation, the scene context. `walk/controls.js` (movement, look, touch,
>   head bob, the use key), `walk/build.js` (materials, batching, instancing, the mirrored floor,
>   colliders), `walk/play.js` (the mini games' targets and prompt), `walk/piles.js` (the seeded
>   pile generators), `walk/textures.js` (procedural maps and canvas paintings), `walk/sound.js`
>   (synthesized sounds), and the rooms in `walk/scenes/`: `dining`, `hallway`, `teal` and `teal2` (sharing
>   `teal_common.js`), `flooded`, `trampoline`, `grocery`.
> - `vendor/three/` — three.js r160 (MIT) and the three addons the walk uses.
> - `tools/walk_test.mjs` — the browser test; `tools/scene.html` + `tools/scene_shot.mjs` — the scene viewer.
> - `0.PNG` — the arcade-cabinet home screen.
> - `A.mp4` … `G.mp4` — the seven room videos.
> - `a.MP4` … `g.MP4` — the seven loading-screen clips, one per room.
> - `0.mp3` — the home screen's audio track.
> - `A.mp3` … `G.mp3` — one audio track per room, started by the room's loading screen.
>
> ## Notes
>
> - **Filenames are case-sensitive.** The loading clips (`a.MP4`) and room videos (`A.mp4`) differ
>   only by case, which is fine on GitHub Pages and other Linux hosts. Cloning onto a
>   case-insensitive filesystem (default macOS/Windows) will collide those pairs — work with the
>   files through GitHub, or rename them before cloning locally.
> - Captions type themselves out character by character; clicking the paper card (or pressing
>   Enter/Space) skips to the end of the caption. Enter/Space also works for START and NEXT.
> - `CAPTION_HOLD_MS` after a caption finishes typing, the card fades out and leaves the room on
>   its own. NEXT stays put.
> - The `LOG` tab on the right slides out the in-world log entry for the room you're standing in.
> - A loading screen is the clip and nothing else: while `body.phase-load` is set, the scanline
>   overlay, the vignette, the sound toggle and the LOG tab are all hidden, and the video isn't
>   crop-scaled.
> - It shows exactly `LOAD_SECONDS` (5.0) of clip, counted in playback time, not wall-clock: the
>   count starts when the video actually starts and pauses while it buffers, so a slow clip still
>   gets its full five seconds. Three ceilings sit behind it so a loading screen can never hang:
>   `LOAD_START_MS` (the clip never got going), `LOAD_STALL_MS` (the picture stopped moving) and
>   `LOAD_CAP_MS` (absolute). The stall guard re-arms only on a real advance in `currentTime` — a
>   `timeupdate` on its own is not proof of progress, since a stalled clip keeps firing them with
>   the picture frozen.
> - A white **SKIP** tab sits where the LOG tab does, but only while a clip is loading, so a slow
>   or broken clip is never a dead end.
> - The upcoming room video only starts downloading once the loading clip is actually playing, so
>   the two aren't competing for the connection while the loading screen is what's on screen. The
>   next room's loading clip is prefetched while you read the current room.
> - Each section owns one audio track. `0.mp3` runs under the home screen; a room's track starts
>   with its loading clip and keeps playing through the glitch and the room itself, so the five
>   seconds of loading and the room that follows are one continuous piece of sound.
> - The video clips are silent — muted in the markup and again in `script.js`, with nothing that
>   ever unmutes them. The section track is the only sound. Muting them also keeps them from
>   taking the audio session on mobile, which is what used to cut the track off when a room
>   started. The track still reclaims playback if anything else pauses it (capped, and the sound
>   toggle always wins).
> - Browsers block audible playback until the visitor interacts with the page, so the site opens
>   on a `CLICK ANYWHERE TO BEGIN` veil over the darkened title card. That one click (or keypress)
>   is what lets `0.mp3` start; the veil then fades and leaves you on the home screen with START
>   still to press. The `SOUND ON` toggle mutes and unmutes everything — section track and clip
>   audio together.
> - `prefers-reduced-motion` swaps the glitch for a plain fade and prints captions instantly; the
>   loading screens still play in full either way.
>

## 12. Full commit log (date, hash, subject)

Every commit, oldest first. Merge commits are shown with their subjects.


### 2026-08

- 2026-08-22 c35efba9 Initial commit
- 2026-08-22 5a473c55 Add files via upload
- 2026-08-22 01911f56 Fix broken asset paths for video and audio sources
- 2026-08-22 ebc34191 Fill out README with project description and run instructions
- 2026-08-22 316c25ab Merge pull request #1 from groot99-droid/claude/repo-strengths-improvements-xg77rc [merge]
- 2026-08-22 84c9e5e2 Delete Backrooms Reel (Mobile).dc.html
- 2026-08-22 37428154 Pause off-screen videos and respect prefers-reduced-motion
- 2026-08-22 3e8e9d42 Keep letter flicker and scroll parallax always on
- 2026-08-22 a7b927f5 Merge pull request #2 from groot99-droid/claude/repo-strengths-improvements-xg77rc [merge]
- 2026-08-24 6765f220 Add files via upload
- 2026-08-24 987395f0 Replace scroll reel with a click-through home → loading → room loop
- 2026-08-24 3fc459a9 Strip the home screen down to the artwork and the START button
- 2026-08-24 de05e319 Drop the room counter and lower the START button
- 2026-08-24 aab60bf0 Add files via upload
- 2026-08-24 8fe8d9cd Merge main to pick up the eight section audio files [merge]
- 2026-08-24 4697458c Give every section its own audio track and unmute the clips
- 2026-08-24 62d58750 Open on a click-anywhere veil so the home track can play
- 2026-08-24 7689e59a Merge pull request #3 from groot99-droid/claude/interactive-loading-screens-7vgp3q [merge]
- 2026-08-24 1ff14be0 Keep the section track playing over the room video, and drop the clip volume
- 2026-08-24 64755d8f Mute the clips and let each loading screen play its clip in full
- 2026-08-24 645a6318 Merge pull request #4 from groot99-droid/claude/interactive-loading-screens-7vgp3q [merge]
- 2026-08-25 fb648cb3 Fix loading screens being cut off, and drop the loading overlay
- 2026-08-25 ef7ff54a Merge pull request #5 from groot99-droid/claude/interactive-loading-screens-7vgp3q [merge]
- 2026-08-25 b5772f72 Bare loading screens, a 5.0s trim, and a caption that clears itself
- 2026-08-25 94f49ba6 Drop the phase label from the room header
- 2026-08-25 3ddb1631 Merge pull request #6 from groot99-droid/claude/interactive-loading-screens-7vgp3q [merge]
- 2026-08-25 ba23a360 Fix the loading screen hanging, and add a white SKIP tab
- 2026-08-25 f0847fa3 Merge pull request #7 from groot99-droid/claude/interactive-loading-screens-7vgp3q [merge]

### 2026-09

- 2026-09-30 815d55b4 Add first-person 3D walk scenes between rooms: the dining room and the hallway
- 2026-09-30 022b740f Keep the walk objective clear of the sound toggle on narrow screens
- 2026-09-30 ac203292 Merge pull request #8 from groot99-droid/claude/dreamy-edison-pmxzka [merge]
- 2026-09-30 039d3020 Build the remaining walk-through rooms and a stairwell down at THE END
- 2026-09-30 e5949e9e Merge pull request #9 from groot99-droid/claude/dreamy-edison-pmxzka [merge]

### 2026-10

- 2026-10-01 bd8b65f5 Refine rooms B–G and animate every room to its video's movement
- 2026-10-01 fe7d7c0d Merge pull request #10 from groot99-droid/claude/keen-euler-x8wtu5 [merge]
- 2026-10-03 109e9679 Add mini games and room-only piles to the dining room, flooded corridor and grocery store
- 2026-10-03 421d53f4 Fix the shared mini-game input, phone prompt and photo orientation
- 2026-10-09 eeed3b29 Settle the pilot rooms' piles cleanly and finish the review changes
- 2026-10-09 a984e72a Never step the walk backward after a long build
- 2026-10-09 cdd0d49b Merge pull request #11 from groot99-droid/claude/happy-galileo-qjw2sc [merge]
- 2026-10-29 f5f337fd Run the walk test on every push and pull request
- 2026-10-29 b91e95e6 Walk test: wait for the DOM, not every load, on a room's second visit
- 2026-10-29 61c87fa7 Walk test: read teal2's waking eye height when the walk starts
- 2026-10-30 09fdc991 Each room's scene file holds its chapter; script.js reads them from there
- 2026-10-30 419651d9 Merge pull request #12 from groot99-droid/claude/pensive-curie-kr7vcq [merge]

### 2026-11

- 2026-11-19 4c4b78ef docs: README loading screen is five seconds (LOAD_SECONDS), not the full clip or four seconds
- 2026-11-19 605f9992 Merge pull request #13 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
