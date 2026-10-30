# Art, audio and the asset pipelines

Ninety-Nine's art has been made three ways, one after another:

1. **Generated stills and clips (the video era).** Higgsfield and Kling made 43 stills and 40 clips.
   They were removed on 2026-10-01, when the game became 3D-only (commit 0681d90,
   [[sec:GENERATED:generated-assets]]).
2. **The hand-built Blender sets and their renders**
   ([[sec:BLENDER:the-render-bridge-track-b1-b3]]).
3. **The live three.js rooms,** built from data, with props from the Higgsfield catalog
   ([[sec:GLB:assets-glb]]).

Its sound is a drone, 18 ambience beds, 11 sound-effect stems, 24 synthesized cues and a
generative score ([[anchor:sfx-cues]], `ninety-nine/src/music.js:1`).

The owner's answers in this stage bring the first era back on new terms. The company's new props
come from "A mix". The video era's stills, transitions and ending films are missed, with "a much
more hands on editing approach when adding them back". And with the drone going, the building
should use "music, sfx, and the rooms tone… to create different moments and envelop the player".

## Props: a mix, with one finishing pass

**Describe.** Today every company prop is one of two things:

- **A box built by a prop builder** in `src/walk/props.js`.
- **A catalog model cloned from `library.glb`.** The library is exported from the Higgsfield
  "NINETY-NINE — Prop Library" project. Every model gets the PS1 treatment: flat shading and vertex
  snapping, its own vertex colours, and no photo textures (`ninety-nine/src/stage/library.js:1`,
  [[sec:GLB:assets-glb]]).

The Blender pilots use their own `LowPolyProp_*` factory ([[sec:BLENDER:files]]). Chapter 5 moved
C1 from PS1 to "low to mid poly".

**Compare** *(Claude's analysis)*. Who Did It, the owner's other game, mixes sources too: a Blender
rig for its characters, and Higgsfield for props, portraits and backdrops. It holds them together
with one finishing tool that pushes everything to one palette, and records every file in a
manifest (`teardowns/who-did-it/chapters/06-art-audio.md`). That finishing pass is what makes a
mix read as one world.

**Critique** *(Claude's analysis)*. "A mix" works if the mix has a single last step. Today that
step exists, but it is the PS1 treatment, which chapter 5 removes. Its replacement should do the
same job at the new level: one shading model, one palette ramp, one rule for textures. Every
source would pass through it:

- **The catalog** for common furniture.
- **Blender-authored or kitbashed pieces** for the signature props: the stapler, the CRT, the
  cab's panel, the box.
- **Generated 3D** where neither fits.

The natural home for the pass is the runtime's `library.js` path, because it already applies one
treatment to everything in the GLB, plus one Blender factory for the authored pieces. A manifest
row per prop, recording its source and licence, would follow Who Did It's practice and the catalog
note "their licence is the catalog's" (`ninety-nine/assets/glb/README.md`).

## The stills, the transitions and the ending films, edited by hand

**Describe.** The video era is documented in Doc 2. It covers the naming scheme, the looping
trick, the style block, negative prompts, a per-scene prompt library and a QC checklist
([[sec:DOC2:1]], [[sec:DOC2:5]], [[sec:DOC2:8]]). Asset Revisions records how the files were re-cut
and what was still to regenerate when they were removed (marked "Superseded",
[[sec:REVISIONS:asset-revisions]]). Some material survives:

- **The removed files** are still in the game's git history (83 stills and clips were added over
  its life).
- **The Blender renders.** `blender/renders/_game/` keeps 26 stills and 3 clips under the game's
  old names.
- **The Higgsfield proofs:** 36 `leave` and `arrive` clips.
- **The last copies of the reference stills,** kept in `blender/refs/` ([[sec:REFS:reference-images]]).

The continuous walk takes the camera only for carried moments and the endings' pull-backs
(`CLAUDE.md`).

**Critique** *(Claude's analysis)*. The three things the owner misses each have a place in the
current game, at different costs:

1. **The look of the stills.** It can return as a *target*, not a file: a reference board per
   room from the old stills, against which the live rooms' light, fog and materials are tuned. It
   costs nothing in the build and fits the photoreal half of C1.
2. **The ending films.** This fits most naturally. The endings already take the camera, run a
   pull-back, hold for 4 s and cut to the card. An edited film could replace the pull-back with no
   change to the walk. "Hands on" suits it: a short, finished piece per ending.
3. **The transitions.** This is the hardest, because the game was rebuilt so that "nothing cuts".
   A transition clip could return in two places without breaking that:
   - **Carried moments** that already leave the walk: the cab's descent, the fall into the pool,
     the chute.
   - **The Right Door bridge** (stage 0), where a clip between rooms is that game's own grammar.

"A much more hands on editing approach" also argues for a gate between generation and the game.
The generated files went in by naming convention and were re-cut after the fact (Asset
Revisions). The studio pipeline in this repository already has `still-image`, `video-shot` and
`music-cue` pipelines. They record the author's go-ahead before anything is kept
(`studio/pipeline/spec.yaml`). Routing the returning media through them would make every clip an
edit the owner signed off on.

## Sound: building moments from music, effects and room tone

**Describe.** The audio bus carries the drone, the store's hum, ambience beds crossfaded per scene
and trimmed to a common loudness, a generative score, sound effects and a voice. The voice
sidechain-ducks the ambience and the music (`ninety-nine/src/audio.js:1`). The score is two
engines: "muzak" (an eight-bar loop, at 80% speed and pitch in hostile rooms), and "pad", "slow
detuned chords a fifth above the 48 Hz drone", with "deep" and "water" presets. A scene can also
name an external file, though "nothing ships there" (`ninety-nine/src/music.js:9`). Beats can play
cues, one-shots and music changes, and the `env` beat already lerps a room's fog, light and grain
over time ([[anchor:beats]]).

**Critique** *(Claude's analysis)*. The owner's answer describes a *mix that changes with the
moment*. The pieces exist, but they are set per scene, not per moment:

1. **A mix beat.** The `env` beat lerps the room's look over time. An audio equivalent (music,
   ambience and effect levels, a filter, lerped over seconds) would let a beat swell the room tone
   as he approaches a threshold, or drop the music to nothing at a carried moment. That is the
   "different moments" the answer asks for, written as data.
2. **The key without the drone.** The pads are tuned to G, a fifth above the drone. If the drone
   goes (chapter 4), keeping the score in G keeps the store's 48 Hz hum in relation to everything
   the player has heard. EXPULSION's "He never left" can then point to the score instead of the
   drone.
3. **Recorded music.** The `{file}` hook is ready, and the repository's `sound-library` and the
   studio's `music-cue` pipeline are the owner's own sources for it. Recorded cues for a few key
   moments, over the generative bed elsewhere, is the same "mix" logic as the props.

## Owner's word

- *With C1 moving to low-to-mid poly, where should the company's new props come from?* — "A mix"
  ([[answer:22]])
- *The generated stills and clips of the video era were removed when the game became 3D-only. Is
  there anything from that era you miss?* — "the look of the stills, the transitions, the endings
  as films. id like to take a much more hands on editing approach when adding them back"
  ([[answer:23]])
- *If the drone goes, what should the building sound like when nothing is happening?* — "music,
  sfx, and the rooms tone, utilized to create different moments and envelop the player in the
  environments" ([[answer:24]])

## Open threads

- The finishing pass that replaces the PS1 treatment: one shading model, one palette ramp, and a
  manifest row per prop (source and licence)?
- Ending films in place of the pull-backs: which ending first?
- Transitions: carried moments only (cab, fall, chute), or also the Right Door bridge?
- A reference board per room from the old stills, to tune the live rooms against?
- An audio mix beat beside `env`, and the score kept in G as the hum's reference?
- Route returning media through the studio's `still-image`, `video-shot` and `music-cue`
  pipelines for the owner's go-ahead?
