# Sets, scenes and endings as data

Ninety-Nine keeps its game in three data files, not in code. `rooms.json` holds the sets: 31 rooms
and connectors, built by `build_rooms.py` and never edited by hand. `scenes.json` holds the
choices: per scene and render, the room, the two thresholds, the beats, the ambience and the
captions. It is edited by hand. `endings.json` holds the four endings ([[data:data/rooms]],
[[data:data/scenes]], [[data:data/endings]]). The owner's answers frame this chapter. The split
between built sets and hand-written scenes should go ("Merge them"). A new scene should be
writable by "Someone working from the data alone". And the beat vocabulary should keep growing,
with every new key documented ("Let it grow, but document each"). These three answers point the
same way. Today the knowledge needed to write a scene lives in four places, and the merge is the
chance to make it one.

## Two files, one scene

**Describe.** `build_rooms.py` is 2,494 lines of Python. Each set is a function (`waiting_room`,
`desk_void`, `garage`…) that places boxes and props and declares doorways with `door()`, threshold
zones with `zone()` and join points with `anchor()` ([[anchor:builders]],
`ninety-nine/tools/build_rooms.py:339`). `check_room()` fails the build on a door that runs off its
wall, a zone off the floor or inside a solid box, a room with no entry, or an alias that changes
more than its spawn, name and shots (`ninety-nine/tools/build_rooms.py:2349`,
`ninety-nine/tools/build_rooms.py:2356`). Six keys are aliases of another room (`S2_C`, `S2_H`,
`S6_C`, `S7_H`, `SE_RETAINED`, `SE_EXPUL`), so a scene can change where the player stands without
changing rooms ([[data:data/rooms/rooms]]). `scenes.json` (1,793 lines) names those zones and
doors by string: a threshold's `zone`, its `exit` door, its `via` connector
([[data:data/scenes/scenes]]). The game itself only warns in the console when a name is missing
(`ninety-nine/src/director.js:688`). The browser tests check the names across files: every
threshold zone exists in its room, every exit has a door and a connector, and every door, prop,
light, actor and shot a beat names exists where it plays
(`ninety-nine/test/cases/manifest.validate.js:151`, `ninety-nine/test/cases/manifest.validate.js:268`).

**Compare** *(Claude's analysis)*. Splitting geometry from script is the normal engine division:
level geometry in one tool, triggers and dialogue in another. What is unusual here is that the
*trigger volumes* (the zones) live on the geometry side, and their *meaning* (which choice, which
beat) lives on the script side. So every choice is split across the two files.

**Critique** *(Claude's analysis)*. "Merge them" fixes exactly that seam. One scene is today a
builder function in Python, a block in `scenes.json`, often a connector, and sometimes an alias.
The tests catch a name that drifts, but only when someone opens the test page. The rooms and the
scenes are not one-to-one, though. S1's room serves S2, the desk room carries both S5's and S6's
thresholds, S8 H is played in `SET_DIVE`, and the connectors belong to no scene. So "one file per
scene" does not fit the data's real shape. Two shapes would:

1. **Per scene, with the room by reference.** Each scene's file holds its two branches *and* the
   zones and doors it adds to its room. The builder places those zones into the named room, so
   a zone exists exactly where it is used. Shared rooms stay shared.
2. **Per room, with the scenes inside.** Each builder function also returns the thresholds and
   beats played in that room. This is closer to today's Python, but it puts the story into code,
   which works against the next answer.

Shape 1 also serves the owner's authoring answer. The second option is mine, for comparison.

## Writing a scene from the data alone

**Describe.** To write a scene today, an author needs `build_rooms.py`'s helpers (`door()`,
`zone()`, `anchor()`, the connector builders, `fixed`, `sync`, `drive`, `labelInk`). They also
need the prop builders in `src/walk/props.js`, which "all share one table, so reusing a builder
name silently replaces the earlier one". On top of that come the beat vocabulary in `scenes.json`'s
`_comment` (a single 3,305-character string), the walk-through in Scene Flow, and the conventions
in `CLAUDE.md` ([[sec:CLAUDE:workflow]], [[sec:SCENE_FLOW:how-to-read-it]]).

**Critique** *(Claude's analysis)*. "Someone working from the data alone" sets a high bar. It means
a reader with the data files and the docs, and without the owner or a session that has read the
director. The pieces are all written down, which is rare, but they are spread out. The hardest
one to read is the most important: the beat vocabulary is one long line of prose inside a JSON
string. Three things would close most of the gap:

- **The vocabulary as a table.** One page, one row per key: what it does, its fields, an example,
  and which scene uses it first.
- **A scene template.** The smallest valid scene (one room, two thresholds, one beat), checked by
  the same tests.
- **The tests runnable from the command line,** so an author knows a new scene is valid without
  opening the test page. `run_tests.cjs` already exists, but needs Node and Playwright
  ([[sec:TESTS:optional-the-node-runners-dev-only]]).

## The beat vocabulary

**Describe.** The director's `runBeats` reads 34 beat keys in a fixed order: `sfxCue`, `caption`,
`rattle`, `show`/`hide`, `light`, `env`, `breath`, `footfall`, `screen`, `display`, `swing`,
`setFlag`, `hold`/`drop`, `actor`, `seal`, `open`/`close`, `lookAt`, `sit`, `moveTo`, `shot`,
`ride`, `shake`, `together`, `waitMs`… ([[anchor:beats]], `ninety-nine/src/director.js:330`). The
same keys are listed a second time in the test's `BEAT` set, so a typo fails "Assertion 1b… a typo
is a silent no-op in the game" (`ninety-nine/test/cases/manifest.validate.js:70`,
`ninety-nine/test/cases/manifest.validate.js:75`). They are described a third time in the
`_comment`. Doc 4's amendments record when keys arrived, for example `display` and `swing` with
S7 C's cab on 2026-10-16 ([[sec:DOC4:4]]).

**Critique** *(Claude's analysis)*. "Let it grow, but document each" is already half built. The
test refuses an undocumented key *in the data*. It does not refuse a new key in the director that
nobody documented. Every new beat today means three edits that must agree: the director's
`if (b.key)`, the test's `BEAT` set, and the `_comment`. One registry would make the rule hold
mechanically: a list of beat keys with their fields and a one-line description, which the director
iterates, the test reads, and the reference page is generated from. Then "document each" is the
only way to add one. It also answers the authoring question above, since the generated page is
the vocabulary table.

## Owner's word

- *The sets are built: build_rooms.py writes rooms.json (367 KB, 31 rooms and connectors). The
  choices are hand-edited: scenes.json names each scene's rooms, thresholds and beats. Is that
  split the right one?* — "Merge them" ([[answer:8]])
- *Who should be able to author a new scene later?* — "Someone working from the data alone"
  ([[answer:9]])
- *The beat vocabulary has grown to 34 keys the director reads (caption, swing, display, breath,
  footfall, ride, sit, actor…). Where would you stop it?* — "Let it grow, but document each"
  ([[answer:10]])

## Open threads

- The merge's shape: per scene with the room by reference (shape 1), or per room with the scenes
  inside (shape 2)?
- A beat registry that the director, the test and a generated reference page all read?
- A scene template and a command-line test run, so a new author knows a scene is valid?
- The Higgsfield and Blender rebuild (stage 0) reads `rooms.json`. A merge that changes how rooms
  are built should land before that rebuild, not after it.
