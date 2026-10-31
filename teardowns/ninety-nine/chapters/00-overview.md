# Overview and the argument

NINETY-NINE is one continuous first-person walk down through a building. The building is real and
rendered photoreal. The company inside it is fake and rendered low-poly PS1. Eight scenes each
offer two choices, made by walking into a threshold rather than by clicking, and a running score
picks each room's compliant or hostile render and, at the end, one of four losses
([[sec:DOC1:0]], [[sec:DOC1:1.2]], [[scene:S0]] to [[scene:S8]]). The owner's answers frame this
chapter. The "you" on the final card should be "degrading", holding "a lot of weight and malice".
Doc 1's two hard positions still stand ("Yes, both"). The game is made first for its owner ("Me").
And the teardown should help decide "How to merge, and work back in the old blender and Higgsfield
sets". The argument holds together in the build. The leftover pipelines are closer to usable than
"stale" suggests: one of them already ships in the game.

## The argument: no correct answer, no escape

**Describe.** Doc 1 states the premise in three lines: "There is no correct answer. There is no
escape. There are three ways to stop being a person" (`docs/01_GAME_LOGIC.md:17`). The structure
enforces it. A fixed spine of nine scenes in a fixed order ("Nobody skips a scene. Nobody unlocks a
scene"), and two renders per scene chosen by the running `conformance` score, not by the choice
just made ([[sec:DOC1:1.2]]). Doc 1 names the cost and picks a side: on a replay "their agency was
cosmetic". It is built on reading 2, "It is the thesis, and revealing it on replay is the final
payload" ([[sec:DOC1:1.3]]). §9.1 asks again whether the absence of a good ending is correct
([[sec:DOC1:9]]). A fourth ending, RETAINED, was added later "(Doc 1 §9.1 left a fourth door
open)". It is reached only by a near-perfect compliance run that also opens the box, and it is
still assimilation: "Welcome, you. It will not happen twice." (`ninety-nine/text/endings.json:23`).

**Compare** *(Claude's analysis)*. The Stanley Parable also offers walked choices through doors,
and comments on choosing. It rewards replay with variety, and its many endings make the player's
agency the subject. Ninety-Nine does the opposite: the same rooms in the same order, angrier or
calmer, with a replay that subtracts. Papers, Please makes compliance the mechanic, as this game
does, but it keeps an ending where you get out. Ninety-Nine refuses one.

**Critique** *(Claude's analysis)*. With "Yes, both" the design is consistent, and RETAINED does not
break it: the fourth door opens onto another loss. The open risk is the one Doc 1 names itself.
The thesis lands only on a *second* run, and the owner is the first audience. A player who plays
once sees a beautifully lit building and one loss. If the replay reveal is the payload, something
in the first run should make a second one feel owed. §9.2 already proposes exactly that: one
object, a slip on the floor in the same place in both renders, "the only evidence that the two
buildings are one building".

## The word "you"

**Describe.** Canon C4: "The company never says 'you'". Company text uses "the candidate", "the
applicant", "personnel", and "The word 'you' appears exactly once in the entire game: on the final
card of the ending. That switch is the last beat" ([[sec:DOC1:3]]). The cards end "Welcome, you.",
"You are not on file." and "Please wait, you." (`ninety-nine/text/endings.json:7`,
`ninety-nine/text/endings.json:13`, `ninety-nine/text/endings.json:19`). The rule has one
deliberate crack. The S4-C manager says "You're early. That's already in the file."
(`ninety-nine/text/system.json:19`, [[sec:DOC1:9]] §9.4). A test counts every "you" in the
company's copy and allows only those lines (`ninety-nine/test/cases/canon.text.js:36`). Naming
works as a ladder. In S2 the compliant render calls him "Ninety-nine." and the hostile one calls
him "Shaun.", a name "she never asked" for (`ninety-nine/text/system.json:17`,
[[sec:DOC1:s2-the-call]]). Everywhere else he is "the candidate".

**Critique** *(Claude's analysis)*. Doc 1 frames the "you" as a *switch*, the moment the game turns
to the player. The owner's reading is sharper: "It should feel degrading, like how they call him a
number instead of his name… it's universal used to give a command to someone beneath you." On that
reading the naming ladder runs downward: Shaun, then 99, then the candidate, then "you", the one
word that carries no identity at all. The cards mostly fit it. "Welcome, you." and "Please wait,
you." are exactly the owner's "Hey you, get me something": a vocative, then a command or a
formula. "You are not on file." is the odd one out. It is a statement, not an address, so it
reads more as information than as contempt. A form like "Leave, you." or "Not on file, you." would
match the other two. The manager's crack, "You're early", now fits the reading too, rather than
looking like an inconsistency, which was §9.4's worry. It is the one superior in the building
speaking down. Whether that cheapens the cards' "you" or sets it up is the open question.

## Made for one person

**Describe.** The owner names themself as the first audience. The project is built as an Obsidian
vault, with its own conventions, guardrails and graph tags ([[sec:CLAUDE:docs-as-vault]]). It has a
test page opened by hand, an optional headless runner and an autopilot that walks whole games
([[sec:TESTS:tests]]).

**Critique** *(Claude's analysis)*. "Me" explains the depth of the documentation. Four specs with
dated amendment notes and an asset revision log are what a designer keeps to talk to themself
across sessions. It also lowers the stakes of the replay problem above: an owner who plays it many
times is the one player guaranteed to see the spine.

## The old sets, and the merge

**Describe.** Two pipelines predate the continuous building of 2026-10-03:

- **The hand-built Blender sets.** `ninety-nine_pilots.blend` holds three pilots with walkthrough
  animations, and stills for all fifteen environments ([[sec:BLENDER_PLAN:status]]). Its materials
  come from a two-tier factory, `PhotorealArch_*` for the building and `LowPolyProp_*` for the
  company, flat-shaded with vertex snapping (`blender/material_factories.py:1`). That is canon C1
  written as code.
- **The Higgsfield scene-builder projects**: 18 rooms rebuilt from `rooms.json` with the shared
  catalog props, each with a ShotCam and four proofs (`in`, `out`, `leave`, `arrive`), 36 clips in
  all ([[sec:HIGGSFIELD:what-one-project-holds]]).

Both are marked "Stale until rebuilt". They predate doorways, connectors and the polish, and the
REBUILD_NOTE lists five ports `higgsfield_scene.py` needs: walls with holes, door leaves per kind,
smaller ports, a missing threshold-era builder, and the polish's prop builders
([[sec:REBUILD:status]], [[sec:REBUILD:what-higgsfieldscene-py-needs-at-rebuild-time]]). "The game
reads nothing from these projects", with one exception: `library.glb`, the prop library every room
draws from, was exported from the Higgsfield "NINETY-NINE — Prop Library" project
([[sec:GLB:assets-glb]]).

**Compare** *(Claude's analysis)*. The owner cites Who Did It as where their understanding grew.
That game's art comes from a pipeline: a Blender rig for characters, Higgsfield for props,
portraits and backdrops, and one finishing pass to one palette (`teardowns/who-did-it/chapters/06-art-audio.md`).
Ninety-Nine's two pipelines already have the same shape. The Blender factory sets the materials,
and Higgsfield supplies the props. What Who Did It added is that the pipeline *feeds the game*,
not a parallel copy of it.

**Critique** *(Claude's analysis)*. "Can be re-used" is right. There are three uses, and each costs
differently:

1. **As the game's source, through the existing GLB route.** `library.glb` shows the path: build in
   Higgsfield or Blender, export a GLB, and `src/stage/library.js` gives it the company treatment.
   Extending it from props to architecture would let Blender's `PhotorealArch_*` materials (and baked
   light) reach the live rooms. That is the biggest gain for C1's photoreal half, and the most work:
   every room's doorways and colliders still come from `build_rooms.py`.
2. **As cinematics.** The 36 `leave` and `arrive` clips and the Blender walkthroughs are camera moves
   through the sets. The game took the camera away only for carried moments and the endings'
   pull-backs (`CLAUDE.md`). Rebuilt sets could render those pull-backs offline, or a title sequence.
3. **As the bridge to Right Door, Wrong Exit.** That game's grammar is exactly a loading clip, then
   a room video, then a walk (Right Door teardown, chapter 0). Ninety-Nine's per-room `leave` and
   `arrive` clips are that game's loading clips in all but name. A Right Door–style chapter between
   two Ninety-Nine rooms, or a Right Door room reached through Ninety-Nine's grate, could be built
   from material that already exists.

The REBUILD_NOTE's five ports are needed for uses 1 and 2. Use 3 can start from the stale clips,
because they are already clips. A stale room is still a room.

## Owner's word

- *At the final card, "you" appears for the only time in the game (Welcome, you. / You are not on
  file. / Please wait, you.). What should the player feel at that word?* — "It should feel
  degrading, like how they call him a number instead of his name. That “you” is holding a lot of
  weight and malice. It’s literally belittling his identity by referring to him in the only way
  which gives him not characteristics. You doesn’t have gender, it’s doesn’t have a name, it’s
  universal used to give a command to someone beneath you. Example: Hey you, get me something. See
  how you makes them sound like an object" ([[answer:1]])
- *Doc 1 says there is no correct answer and no escape: three ways to stop being a person (§0,
  §9.1), and on replay the spine shows agency was cosmetic (§1.3, reading 2). Do you still stand by
  both?* — "Yes, both" ([[answer:2]])
- *Who is Ninety-Nine for first?* — "Me" ([[answer:3]])
- *What should this teardown help you decide next?* — "How to merge, and work back in the old
  blender and Higgsfield sets. My understanding of game design as increased since I’ve worked with
  “Who did it” so I’m confident those old pieces can be re used" ([[answer:4]])

## Open threads

- EXPULSION's "You are not on file.": should it become a vocative command like the other two
  cards?
- The manager's "You're early": keep it as the one superior speaking down, or remove it so the
  cards' "you" is the only one?
- The replay payload: build §9.2's slip, the one object in the same place in both renders, so a
  first run hints that a second is owed?
- The old sets: which use comes first? Source for the live rooms (GLB), cinematics, or the bridge
  to Right Door?
- Later chapters gather the cost of each: datasets (stage 2), the building (stage 5), art (stage 6)
  and the stale pipelines (stage 8).
