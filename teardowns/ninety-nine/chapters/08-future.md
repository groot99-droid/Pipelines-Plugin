# Future: what is stale and what is next

This last chapter gathers what the other eight decided. The owner's answers close the teardown on
three points. Everything gathered comes first, as one programme ("all of those"). The two games
merge in three steps, "All three, in that order": a shared engine, then a shared fiction, then
Right Door's rooms inside the building. And the game is never finished ("Never: it keeps growing"),
the same answer the owner gave for Right Door.

## What is stale

**Describe.** The scan found 40 stated plans. Most of them are marked as withdrawn or superseded by
the documents themselves ([[sec:REBUILD:status]], [[sec:REVISIONS:asset-revisions]]):

- **The Higgsfield scene-builder projects** (18 rooms). They are "Stale until rebuilt" since the
  continuous building, and `higgsfield_scene.py` needs five ports before it can rebuild them
  ([[sec:REBUILD:what-higgsfieldscene-py-needs-at-rebuild-time]]).
- **The Blender pilots and renders.** The `.blend`'s render output paths still point at pre-rename
  folders, and fixing them needs Blender open on that file ([[sec:BLENDER:known-follow-up-render-output-paths]]).
- **Asset Revisions' "Still to regenerate".** It lists stills and clips for a pipeline that no
  longer exists ([[sec:REVISIONS:still-to-regenerate]]).
- **Doc 3 and parts of Doc 2 and Doc 4,** kept as the record (chapter 7).

**Critique** *(Claude's analysis)*. "Stale" now means two different things. The Higgsfield and
Blender sets are stale *and wanted*: stage 0 brings them back. Asset Revisions' to-do list is stale
*and finished*: its regenerations will never happen in that form, because stage 6 returns media
only as hand-edited stills, transitions and ending films. Marking that list closed, rather than
leaving it as an open plan, would keep the scan from carrying it forward as unfinished work.

## One programme, in the order the work depends on

**Describe.** The owner chose all four starting points: CI and the scene-data merge, the
low-to-mid poly look, room drift and screen effects, and the merge with Right Door.

**Critique** *(Claude's analysis)*. All four can be worked on, but they depend on each other, so
the order in which they *land* matters. From the chapters:

1. **CI** (chapter 4). It protects everything after it. It is shared with Right Door, so it is also
   the first piece of the shared engine.
2. **The scene-data merge** (chapter 2). Option 3 first, a build-time check of the links between
   rooms and scenes. Then option 1, choices owned by scene files. Both come before anything
   changes how rooms are built.
3. **Room drift and the screen effects** (chapter 3), as data on the merged scenes, with the
   overlays removed. The specs get their amendments (chapter 7).
4. **The look** (chapter 5): the PS1 treatment replaced by one finishing pass, and the prop mix
   (chapter 6).
5. **The Blender and Higgsfield rebuild** (stage 0), *after* 3 and 4, so it copies settled rooms.
   This is the step chapter 7 warned about. Done earlier, it repeats the parallel-pipeline regret.
6. **The edited media** (chapter 6): ending films first, then transitions at the carried moments.
7. **The merge's three steps** (below), the first of which is already under way with 1.

The decisions about the drone, Harlowe and the oblique friction line are content changes. They can
land at any point after CI.

## The merge, in three steps

**Describe.** The Right Door teardown laid out the three ways the games can meet (its chapter 0).
The owner now orders them.

**Critique** *(Claude's analysis)*. Each step makes the next one cheaper:

1. **A shared engine.** Both games use three.js r160 with no bundler. Right Door brings device
   tiers, an adaptive pixel ratio, seeded pile generators and a Playwright walk test. Ninety-Nine
   brings data-built rooms, connectors, a director and beats. A shared module of walk runtime, tiers
   and test harness is the first concrete piece. Its first two parts, the CI job and the device
   tiering, are already on both teardowns' lists.
2. **A shared fiction.** Ninety-Nine's PENDING REVIEW sends the candidate back to a waiting room
   with a slip reading 99. Right Door's loop sends the walker back to its title card. Making them
   the same place costs a few lines of text and one room. It needs no engine work and no new
   rooms. It also fits the two games' shared argument, "no escape" and "Trapped: there was never a
   way out" (stage 0 of both teardowns).
3. **Right Door inside the building.** Its seven rooms become a layer under Ninety-Nine's hostile
   path, reached through the grate. This is the costliest step:
   - the hand-written three.js rooms move into the shared engine, or are ported to data;
   - they come under Ninety-Nine's canon: C1's two layers, C3's descent and C4's text;
   - Right Door's loading clips become carried moments, the one place this game takes the camera.

   By then the shared engine (step 1) and the returned transitions (chapter 6) have done half of
   that work.

## Never finished

**Describe.** Both games are open-ended in their owner's eyes. Right Door: "Never: it keeps
growing". Ninety-Nine: the same. The owner's measure of progress is what they learned, not
completion. They keep the specs "bc it shows the growth" (chapter 7). The games were playtested on
the owner's computer by the owner and peers.

**Critique** *(Claude's analysis)*. A game that keeps growing still needs a way to tell that each
step worked. Two habits already point to one:

- **The teardowns themselves** can be re-run after each step. `udgt.py diff` shows what moved, and
  the briefs record what the owner thinks of it.
- **The peer playtests** can become a short written note per session. Chapter 3's drift and
  friction will make runs differ, so a note of what each peer did at each threshold becomes the
  only record of how the weather behaves.

With CI catching what breaks and these two catching what changed, "never finished" stays a choice
and does not turn into drift.

## Owner's word

- *This teardown has gathered a lot of work for Ninety-Nine. What comes first? (options: CI and the
  scene-data merge; the look: C1 low-to-mid poly; room drift and screen FX; merging with Right
  Door)* — "all of those" ([[answer:29]])
- *How should the two games merge, now that both teardowns are in? (options: shared engine first;
  shared fiction; Right Door inside the building; all three, in that order)* — "All three, in that
  order" ([[answer:30]])
- *What would make Ninety-Nine finished, and what would make you stop?* — "Never: it keeps growing"
  ([[answer:31]])

## Open threads

- Mark Asset Revisions' "Still to regenerate" as closed, since the video pipeline is replaced by
  hand-edited media?
- Start the programme at CI, shared with Right Door, as the first piece of the shared engine?
- The shared fiction (PENDING REVIEW's waiting room as Right Door's title card) as the first
  visible sign of the merge?
- Re-run both teardowns after each step, and keep a short note per peer playtest?
