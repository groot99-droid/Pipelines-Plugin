# Art, audio and the asset pipeline

Who Did It's look comes from a pipeline, not from one artist's hand:
- characters are rendered with a Blender rig, and props, portraits and backdrops are generated with Higgsfield;
- everything is pushed through one finishing tool to one palette;
- every file is recorded in `CREDITS.md` and `assets/source/MANIFEST.md` ([[doc:ASSETS]], [[sec:ASSETS:6.3]]).

Sound comes from your own sound library in this repo, from CC0 sources, and from generated speech for the
Vicar.

You answered:
- the face of the game is **a mix of generated and rendered pixel iso**, with a switch between **HD, 8-bit and
  low poly**, each drawing everything in its own style;
- you **don't mind if everything is generated, as long as it looks good**, and hand-drawing is for special
  pieces, not the bulk;
- when nothing is happening, the game is **music-led**.

## Three styles, one set of assets

**Describe.** [[dec:A79]] put your words into the data: you want to "enjoy it in 8 bit or Low Poly", chosen "at
the click of a button", with high definition later. `style.json` `artStyles` lists the styles:
- **`8bit`** is the default. It has the pixel finish and nearest filtering.
- **`lowpoly`** has no pixel finish, linear filtering, and its own root, `lowpoly/`.
- **`hd`** is `reserved`.

The segmented control "8-bit | Low poly | HD" is `apps/client/src/ui/artStyle/ArtStyleSwitch.ts` (UI.md
14.18). Every shipped folder has a matching low-poly folder of the same size: characters 50 and 50, portraits
13 and 13, buildings 5 and 5, and so on through ground, clues, kit, props and the round-6 world set.

The 8-bit finish is `tools/sprites/pixel.ts` ([[sec:ASSETS:6.11]]):
- **Renders:** alpha is cut at 0.5, each pixel is snapped to the 64-colour world palette in OKLab, and a 2 × 2
  mode downscale keeps one-pixel outlines.
- **Generated images:** background removal, a chroma key with spill cleanup, a crop, a box downscale to the art
  grid, then the same palette snap.

The palette has three tiers ([[sec:ASSETS:6.1]]):
- the ten tokens, for the UI and runtime tints;
- the five-colour night set, for the DOM only ([[dec:A106]]);
- the 64-colour world palette in 16 ramps, for all art. Black is never used, and saturated colours cover at
  most 10% of a frame.

**Compare** (Claude's analysis). Few games ship two finished art styles. The nearest are the remasters with a
"classic graphics" toggle: Halo Anniversary, the Monkey Island special editions, Diablo II: Resurrected.
Those keep two whole sets of art. Yours keeps one *source* (the Blender scene and the generation) and two
*finishes*, which costs far less. HD then becomes a third finish of the same source, not a third set.

**Critique** (Claude's analysis).
- **The pipeline is the art direction.** Without a lead artist, `pixel.ts` and the world palette are what
  make 157 webp and 183 png files from different sources look like one game. Keep them as the single gate.
  Your answer, "if it looks good", already has a test: it passed the finish.
- **HD is cheapest as "no finish".** The generated sources are 2k, and the renders come out at display
  scale before the 2 × 2 downscale. So HD can be the same pipeline with steps 2 to 3 skipped, palette-snapped
  or not. Reserve a `hd/` root now, so that the manifest keys (`char/<lookId>/<anim>/<dir>`) are the same in all
  three.
- **One gap in the style rule.** The DOM UI is styled once, in night glass (chapter 1). It does not change with
  the art style. That is right for menus, but the role card is part of "what you hold". In low poly, a pixel
  portrait on the card would clash with a smooth world, unless the card's portrait also comes from the
  `lowpoly/portraits/` root. Check that it does.

## Generated art, as long as it looks good

**Describe.** `CREDITS.md` has 166 rows:
- 90 cite Higgsfield, each by its catalogue id in this repo's `studio/library/catalog.json`;
- 67 are your own;
- 79 are CC0, and 4 are CC-BY with a credit.

Some rows match more than one source. The rule is CC0 by default, CC-BY only with a row, and never Synty or
raw Mixamo or Quaternius sources ([[sec:ASSETS:6.5]]). Masters stay on your laptop under the studio's
`studio/assets/who-did-it/`. Each has a studio note and a `MANIFEST.md` row with its hash ([[sec:ASSETS:6.10]]).

**Compare** (Claude's analysis). Indie games that lean on generated art mostly hit two problems:
- **Drift:** each generation is a little off-model.
- **Provenance:** a store or a publisher asks where the art came from.

Your pipeline answers both. The palette snap and the fixed render rig hold the drift down, and the catalogue
id on every credit row answers provenance. Most teams add that bookkeeping only after a store asks.

**Critique** (Claude's analysis). "If it looks good" is a fine rule for a game among friends. Two things
would make it hold for a wider release:
- **Character consistency.** Characters are where generated art drifts most, and where a hidden-role game
  needs it least: a look *is* the role since [[dec:A49]]. The Blender rig keeps characters consistent across
  directions and frames. Keep characters on the rig, even when portraits and props are generated.
- **The sale clause.** CLAUDE.md already says the ONUB name changes if the game is sold. Add one line to
  ASSETS 6.5: "before a sale, re-check each generated asset's terms against the catalogue". The ids are
  already there. It is a checklist, not a project.

## Music-led

**Describe.** Music is played per map and per phase. The client's `MusicDirector.ts` maps the phase to a class,
and `music.json` maps each class to a playlist ([[sec:GDD:3.18]]). For Hollowmere:

| Phase | Playlist | Track and length |
|---|---|---|
| Opening | `hollowmere_opening` | `load_hollowmere`, 118 s |
| Day and dusk | `hollowmere_day`, `_dusk` | `theme_railroad_barons`, 64 s |
| Night | `hollowmere_night` | `bed_tense`, 20 s |
| Meeting | `hollowmere_meeting` | `bed_heartbeat`, 20 s |
| Final Night | `hollowmere_finalnight` | `bed_tick`, 18 s |
| Game over | `hollowmere_gameover` | `end_the_fade`, 67 s |

There are 12 tracks, about 12.4 minutes of music in all. Blackpine has its own theme
(`theme_extraction_camp`, 72 s) and shares the three beds. There are also 26 sound effects and ambiences:
the four ambience beds for village, forest, cave and house, the bell, the doors, crows, a storm, the train's
arrival and brake, five stings, and the scream. 24 of them come from your sound library, picked by measured
envelope "since no session can listen" ([[open:A96]]).

**Compare** (Claude's analysis). Music-led games with long sessions use adaptive scores in layers or
stems. Red Dead Redemption 2 and Hades add and remove stems as the state changes, so the music never loops
audibly. Among Us has almost no music in play. That silence is part of its tension, and it is the opposite of
your choice.

**Critique** (Claude's analysis). Music-led is a good fit for "dread, then suspicion", but the current
library cannot carry a 20-to-25-minute match:
- **Loop fatigue.** A match plays the day theme four times or more, around 4 minutes of a 64 s track, and the
  20 s night bed about 20 times. Players will hear the seams by the third night.
- **Make the beds layered, not longer.** Split `bed_tense` into stems (pulse, drone, high strings) and add or
  remove them with the state: the night's clock, a body unreported, the Final Night. This also gives
  Book V's town moods (chapter 5) a sound: Calm, Panicked, Entranced and Rioting as four mixes of one bed.
  Your sound library and the studio's audio pipeline can make stems as easily as tracks.
- **Mark the dread.** If music leads, a body or a scream should *cut* it: two seconds of silence, then the
  sting. In a music-led game, silence works as an alarm. Nothing in the client ducks the music today: `MusicDirector.ts` only crossfades
  between playlists.
- **The ferry horn and loaf crack** are quick-mode sounds. They can go with the ONUB removal ([[dec:A115]]),
  unless Port-au-Levain uses them in round 8.

## Smaller findings

- [[open:A92]] and [[open:A93]]: opening lengths and transition timings are one number each for every map.
  `load_hollowmere` is 118 s and `load_blackpine` is 81 s, so the opening's `openingS` cap (120 s) suits
  only Hollowmere.
- The Blender camera, the projection and the direction table are documented to the pixel in SPRITES §10
  ([[sec:SPRITES:10.2]], [[sec:SPRITES:10.3]], [[sec:SPRITES:10.4]]). That is why rendered and generated
  sprites agree in the world. Keep the camera locked, as SPRITES says.
- The `docs/ui/` screenshots are stale (chapter 1). The art itself has no reference sheet either. A
  contact sheet of every look in both finishes, made by the walk test, would show drift at a glance.

## Owner's word

- 2026-10-23, *Pixel art, rendered isometric, or both: which is the game's real face?* "It’s a mix between ai
  generated and Rendered Pixel ISO, however the mode can be switched between HD 8 bit and Low poly and all of
  them render everything in their style"
- 2026-10-23, *Where should generated art stop?* "I don’t care if everything is AI generated if it looks good. I
  don’t hate the idea of handrawing and may do it for certain games or pieces but it is absolutely not my go to
  for large scale works"
- 2026-10-23, *What should the game sound like when nothing is happening?* "Music-led"

## Open threads

- HD as a third finish of the same sources (skip the downscale), with a reserved `hd/` root and the same keys.
- Does the role card's portrait follow the art style?
- Keep characters on the Blender rig, even when other art is generated.
- One line in ASSETS 6.5: re-check generated assets' terms against the catalogue before any sale.
- Layered beds (stems) for night, meeting and Final Night, and the four town moods as four mixes.
- Cut the music for two seconds before a kill or scream sting.
- A contact sheet of every look in each finish, made by the walk test.
