# How it was made: history and reversals

Ninety-Nine's git history has 109 commits and six merged pull requests, from 2026-09-13 to
2026-10-17 ([[history:summary]]). It records three shapes of the game:

1. **The video era.** Four specs, 43 generated stills, 40 clips and seven mini-games. It reached
   git in one commit of 288 files on 2026-09-30 (a59aff5), after work outside the repository from
   mid-September.
2. **The 3D sets.** Walkable rooms first appeared beside the video the same day (af63aba). The AI
   video and still pipeline was replaced by live 3D sets on 2026-10-01 (0681d90).
3. **The continuous walk.** On 2026-10-03 the game became one walk, rooms joined by doorways and
   choices made by walking (65184db). The mini-games were retired that day. Seven per-scene polish
   passes (2026-10-08 to 10-10) and four engine follow-ups (10-16) followed.

The owner's answers in this stage are the most personal of the teardown. The video era was "A
necessary sketch". All three regrets offered apply: the mini-games, generating before designing,
and the parallel pipelines. And the specs are kept as "a reference for growth… failing is a real
delight when you can look back and see the strides you took".

## A necessary sketch

**Describe.** The video era fixed things the 3D game still uses:

- **The naming scheme** `S{n}_{C|H}`, which still names every set, sound and folder ([[sec:DOC2:1]],
  [[sec:CLAUDE:naming-scheme]]).
- **The canon C1 to C8,** written for stills and clips: "If a generated asset or built component
  violates one of these, it is wrong and gets rebuilt" ([[sec:DOC1:3]]).
- **The spine and the render,** chosen in Doc 1 §1.2 explicitly because 256 video paths were
  impossible to produce ([[sec:DOC1:1.2]]).

What the sketch got wrong was the medium. Asset Revisions records a series of repairs before the
3D switch:

- a transition clip that played backwards, then forwards, re-cut;
- a push-in that ran in reverse, un-reversed;
- a Blender re-skin that was "a flat grey blockout", rolled back to the AI originals;
- a manager walk cycle "rejected" and replaced by a billboard sprite

([[sec:REVISIONS:done-in-this-pass]], [[sec:REVISIONS:still-to-regenerate]]).

**Critique** *(Claude's analysis)*. "A necessary sketch" is fair, and the record supports a sharper
version: the sketch got the *rules* right and the *assets* wrong. Every lasting decision, the
spine, the renders, the canon and the naming, came out of the video era, and every file it made
needed fixing or was thrown away. That is the usual shape of a good prototype. The cost was that
the files, unlike the rules, were expensive to make. Chapter 6's plan to bring back stills,
transitions and ending films "hands on" applies the lesson: the medium returns only where the
rules already fit it.

## Three regrets

**Describe.** The owner names all three offered:

- **The mini-games.** Seven were specified in eleven modes, built, then retired in one day
  ([[minigame:MG-01]] to [[minigame:MG-07]]). Chapter 3 records the owner's verdict: "felt more
  like chores… a Band-Aid for the lack of game play".
- **Generating before designing.** The stills and clips were made from Doc 2's prompt library
  before the rooms existed as space. When the rooms were built, the clips no longer matched them,
  and were removed rather than reshot ([[sec:GENERATED:generated-assets]]).
- **The parallel pipelines.** The Blender pilots, the Higgsfield scene-builder projects and the live
  three.js rooms were built side by side. Two of them have been stale since 2026-10-03
  ([[sec:REBUILD:status]]).

**Critique** *(Claude's analysis)*. The three regrets share a cause: each built *output* before
the thing it served was settled. The mini-games came before the walk, the media before the rooms,
and three copies of the sets before one set was final. The teardown's own decisions so far show
the owner reversing that order:

- Stage 0 brings the old sets back *into* the live game, not beside it.
- Stage 2 merges the scene data so a scene has one source.
- Stage 6 returns media only with a hands-on edit, after the rooms exist.

The one place the old pattern could return is chapter 3's room drift and chapter 5's look change.
Both should land in the live rooms before any Blender or Higgsfield rebuild, so that the rebuild
copies a settled set.

## The specs as a record of growth

**Describe.** The four specs were written first, and the build has since been recorded in dated
amendment notes at the top of each section. The spec text below an amendment is "left as
written" ([[sec:DESIGN_DOCS:design-docs]]). Doc 3 is kept whole, "as the record of what was built
and then replaced" (`docs/03_MINIGAME_UX.md:7`). Asset Revisions is marked "Superseded" and kept
"as the history". The game was playtested by its owner and by peers, on the owner's computer.

**Critique** *(Claude's analysis)*. The owner reads the README, plays the game and reads Claude's
replies. The specs are read by the sessions that build it. So the specs' *accuracy* matters most
to the reader who is not the owner. This teardown found several places where a session following
the specs would be misled:

- Doc 1 says the 256-path sweep "re-runs in CI", and there is no CI (chapter 4).
- Doc 1 §6 cites a Doc 4 §4.3 that does not exist (stage 0's scan).
- Doc 4 §14 names one exception to its no-buttons rule where the game has two (chapter 1).
- Doc 4 §12's performance budget still counts video clips (chapter 4).

Keeping the specs as a record of growth and keeping them accurate do not conflict. The amendment
notes already do both. What is missing is an amendment wherever the game has moved and no note
says so. The decisions in this teardown (C1 lifted, the drone going, Harlowe as the previous 99,
the overlays replaced) will each need one.

## Owner's word

- *The game went from generated video (Sept) to a continuous 3D walk (Oct 1–3). Looking back, was
  the video era a detour, or a necessary sketch?* — "A necessary sketch" ([[answer:25]])
- *Which decision would you make differently with what you know now? (options: the mini-games;
  generating before designing; the parallel pipelines; nothing yet)* — "all of the above, except
  the last" ([[answer:26]])
- *The game was built in AI sessions: four specs, then pull requests and review passes with dated
  amendments. Was that faster, or did the reviews cost more than they saved?* — "ive got no answer
  for this one i dont understand the question" ([[answer:27]])
- *Simpler version: you built Ninety-Nine by writing four design documents first, then having
  Claude sessions build it, with you reviewing each change. When the game changed direction (video
  → 3D walk, mini-games → walking), the documents got 'amendment' notes instead of being rewritten.
  Do the four documents still help you, or are they in the way now?* — "i honestly just used them
  as a reference for growth, i used them to build the game, got claude to amend them, and keep
  them around bc it shows the growth. failing is a real delight when you can look back and see the
  strides you took. ive i havent read much of anything but the responses claude gives me, the
  readme, and actually testing my creation. i played it, my peers played it on my computer, and
  the designs of both of these games taught me what i know today" ([[answer:28]])

## Open threads

- Land the room drift and the C1 look in the live rooms *before* the Blender or Higgsfield rebuild,
  so the rebuild copies a settled set?
- One amendment pass over the specs for the four inaccuracies above, and the teardown's own
  decisions?
- Peer playtests on the owner's computer: worth one written note per session (what they did at
  each threshold), now that friction and drift will make runs differ?
