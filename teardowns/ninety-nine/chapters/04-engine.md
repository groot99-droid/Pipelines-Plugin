# Engine, audio and tests

Under the walk there are three systems:

- **The stage:** one three.js renderer drawing the building live ([[area:building]]).
- **The audio bus:** the 48 Hz drone, the store's hum, ambience beds, generated music, sound
  effects and a voice, all on one Web Audio context.
- **The tests:** a browser page that runs 12 case files, with a headless runner and an autopilot
  that plays whole games ([[area:tests]], [[area:tools]]).

The owner's answers move all three:

- The tests should run "Yes, on every push", which the specs have asked for all along.
- The drone, canon C7, "could go".
- The floor is "Phones too", which is exactly what Doc 4 §12 already says and what the renderer
  does not yet do.

## Tests, and the CI the specs already promised

**Describe.** The suite is a fetch-and-assert harness in the browser: "no Node on this machine,
so it's a fetch-and-assert harness, not a CI script" ([[sec:TESTS:tests]]). It runs 125 rows:

- the 256-path sweep (27 / 27 / 202);
- the canon checks, C4 and the drone;
- the data validator for `scenes.json` against `rooms.json`;
- the room checks, with WebGL cases that "take seconds on a GPU and a few minutes" in software.

`tools/run_tests.cjs` runs the page headless when Node and Playwright are present. Its exit code
is 0 for pass, 1 for any failure, and 2 when the page never reported
(`ninety-nine/tools/run_tests.cjs:1`). `tools/walkthrough.cjs` plays whole games with the autopilot
and checks each ending card against what `state.js` resolves (`ninety-nine/tools/walkthrough.cjs:1`).
There is no `.github/` folder.

**Critique** *(Claude's analysis)*. "Yes, on every push" closes a gap the specs opened. Doc 4 asks
for CI four times:

- a check that `DEBUG_RESUME` is false (§3.7, `docs/04_TECHNICAL_BUILD.md:164`);
- `validate.js` "in CI" (§4.2, `docs/04_TECHNICAL_BUILD.md:215`);
- the C4 grep "as a CI step" (§11.2, `docs/04_TECHNICAL_BUILD.md:496`);
- "validate it in CI" for asset names (§15, `docs/04_TECHNICAL_BUILD.md:554`).

Doc 1 goes further and states the sweep is re-run "in CI" (`docs/01_GAME_LOGIC.md:438`), which is
not true today. `state.js` admits it: no automated CI exists, so `DEBUG_RESUME` is "a manual
pre-deploy checklist item" (`ninety-nine/src/state.js:13`).

The runner is ready for CI: it has an exit code, a timeout and a list of expected 404s. A GitHub
Actions job needs Python for `dev_server.py`, plus Node and Playwright. Two choices remain:

1. **Speed.** The WebGL cases take minutes in software rendering, and a walkthrough "takes several
   minutes" per path. A sensible split runs the pure cases and the data validator on every push,
   and the WebGL cases plus two or three walkthrough plans (all-succumb, all-resist, the waverer)
   on pull requests.
2. **Sharing with Right Door.** Both games now want the same Playwright-in-CI job (Right Door
   chapter 5). Building it once is the cheapest first step of a shared engine.

## The drone that "could go"

**Describe.** Canon C7: "One continuous drone. A 48 Hz HVAC bed runs from the moment the lobby
doors close to the final card. It never restarts, never cuts on a scene change, and detunes by
roughly 4 cents per scene, so by scene 8 it beats audibly against its own memory"
([[sec:DOC1:3]]). In code it is a single oscillator plus a reference oscillator, started exactly
once (`ninety-nine/src/audio.js:1`). Several other things depend on it:

- The store's hum in S8 H "reads the drone's detune, never writes it".
- Doc 1's EXPULSION card is written around it: the store's hum "is 48 Hz, detuned exactly as far as
  the building's drone. He never left." ([[sec:DOC1:6.4]]).
- Fracture drives "audio detune depth" ([[sec:DOC1:2.3]]).
- A test file of its own checks it: started once, never restarted, the hum's detune, the fade at
  the card (`ninety-nine/test/cases/audio.drone.js:39`).

Since the drone was specified, the game gained generated music (`ninety-nine/src/music.js`), with
pads and muzak per scene.

**Critique** *(Claude's analysis)*. "It could go" lines up with the owner's Right Door answer that
a room at rest should sound like "The track alone". The owner prefers music to a synthesized bed in
both games. Removing it is a canon change, though, not a mixing change, and it reaches four places:

1. **C7 itself.** Remove it, or rewrite it as "one continuous *music*", with the generated score
   carrying the never-restarts rule instead.
2. **EXPULSION's meaning.** "He never left" works because the store's hum matches a drone the
   player has heard for the whole game. Without the drone, the hum needs a new reference, such as
   the music's key or the receptionist's call, or the line loses its proof.
3. **Fracture's audio.** With the overlays gone (chapter 3), the drone's detune depth is one of the
   last places fracture is *heard*. If the drone goes, fracture needs another voice, such as the
   music's detune.
4. **The tests.** `audio.drone.js` and part of `audio.mix.js` change with it.

A middle path keeps the drone but makes it nearly inaudible until fracture rises: present for
the waverer, absent for the committed. That keeps EXPULSION's proof and moves the drone from a
constant into the weather.

## Phones too

**Describe.** Doc 4 §12 sets a performance budget: 2 s to first frame, 60 fps, 45 MB for a full
run. It adds: "Mobile Safari is the constraint. Test on a four-year-old iPhone before anything
else" ([[sec:DOC4:12]]). Doc 4 §13 asks for landscape lock with an in-world portrait warning
([[sec:DOC4:13]]). The renderer sets its pixel ratio to 1 and never changes it
(`ninety-nine/src/stage/stage.js:89`). Touch controls switch on whenever the device reports touch
(`ninety-nine/src/walk/controls.js:311`).

**Compare** *(Claude's analysis)*. Right Door, on the same three.js version, sorts devices into
phone and desktop tiers. It sets texture and shadow sizes by tier, and adapts the pixel ratio to
the frame rate (Right Door teardown, chapter 5). Ninety-Nine has none of that. Its fixed pixel
ratio of 1 is safe for speed but soft on a high-density screen, and nothing lowers the load when
frames run long.

**Critique** *(Claude's analysis)*. "Phones too" is Doc 4's own rule, and the build has not caught
up. Three things follow:

1. **Port Right Door's tiering and adaptive pixel ratio.** It is the most concrete piece of shared
   engine between the two games, and it is already written.
2. **Measure the budget.** Nothing reports frame time, first frame or download size. A frame-time
   readout behind a URL flag, as in Right Door's chapter 5, would make "Phones too" testable on the
   owner's own phone.
3. **Review §12 itself.** It was written for the video era: its 45 MB download counted video clips,
   and it budgets "scene + mini-game" frame rate. It needs restating for a continuous 3D walk.

The headless walkthrough can run at a phone's size (`--width=640 --height=360`), but not with
touch input (chapter 1). A phone pass in CI would prove the layout, not the controls.

## Owner's word

- *Ninety-Nine's tests run in a browser page opened by hand (12 case files), with an optional
  headless runner and an autopilot that plays whole games. For Right Door you chose CI on every
  push. Same here?* — "Yes, on every push" ([[answer:16]])
- *The 48 Hz drone (C7) is one oscillator from the lobby doors to the final card, never restarted,
  detuning ~4 cents per scene. Is it the game's most important system?* — "It could go"
  ([[answer:17]])
- *You play on desktop. What is the slowest machine it must run well on?* — "Phones too"
  ([[answer:18]])

## Open threads

- CI: pure cases on every push, with WebGL cases and walkthroughs on pull requests? One shared job
  with Right Door?
- Doc 1 §7.1's "re-runs this sweep in CI": true once CI lands. Until then, amend it?
- The drone: remove it (rewriting C7 and EXPULSION's hum), or let fracture decide how much is heard?
- Port Right Door's device tiers and adaptive pixel ratio. Restate Doc 4 §12 for the 3D walk.
