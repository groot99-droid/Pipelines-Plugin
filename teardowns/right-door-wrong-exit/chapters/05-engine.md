# Engine, phones and tests

Under the screens and the rooms there are three layers. The first is a hand-written state machine
in `script.js` that drives home → load → glitch → room → next → walk → load. The second is a walk
runtime in `walk/` on a vendored three.js r160, with no framework and no build step
([[area:shell]], [[area:walk]], [[anchor:timings]]). The third is a 1,114-line browser test that
drives the real page ([[area:tools]], [[sec:README:testing]]). The owner's answers set three
targets. The floor is "My own phone". The test should run "Yes, on every push", where today it
runs only by hand. And the case-only file pairs should go: "Rename them". All three can be done.
The test has one blind spot that matters more once it runs on every push: it never plays a
video.

## The runtime, and a phone as the floor

**Describe.** The walk sorts the device into a phone or a desktop by touch, screen size, cores and
memory. A phone gets 512 px textures and 512 px shadow maps, a desktop 1024
(`walk/walk.js:37`). The renderer uses AgX tone mapping and no post-processing pass. Its shadow
maps render once per walk, because the rooms are static (`walk/walk.js:74`). The pixel ratio
adapts: after 1.2 s of slow frames it steps down by 0.25, to a floor of 0.75 on a phone. After 6 s
of headroom it steps back up (`walk/walk.js:259`). A portrait screen gets a taller field of view,
88° below an aspect of 0.8 (`walk/walk.js:251`). Geometry is merged to one draw call per material.
The long rooms re-park a fixed pool of lights on the nearest fixtures, so shaders never recompile
([[sec:README:built-for-phones]]). If the module or WebGL fails, the game falls back to the loading
screens (`script.js:507`).

**Compare** *(Claude's analysis)*. Ninety-Nine also vendors three.js r160 and has no bundler
(`The-Intern/docs/04_TECHNICAL_BUILD.md:16`). Its rooms are built from data
(`build_rooms.py` → `rooms.json`), while this game's rooms are code. If the two ever share an
engine (chapter 0's second option), this runtime is the more phone-tuned of the two: the
adaptive pixel ratio, the device tiers and the light pool.

**Critique** *(Claude's analysis)*. "My own phone" is a clear floor, but the code does not know
which phone that is. The tiering works by guess (`cores <= 4 || mem <= 4`). The only numbers the
test can hold the game to are draw-call budgets per room, checked in software WebGL: dining
under 60, hallway under 40, teal and teal2 under 30, flooded under 60 (`tools/walk_test.mjs:618`
to `tools/walk_test.mjs:799`). Those are good proxies for a phone, and they are already enforced.
What they cannot say is whether the owner's phone keeps up. Two cheap steps would anchor the
floor. Note the phone (model and browser) in the README. And have the walk show its frame time and
pixel ratio on screen behind a URL flag (as `?chapter=` already is), so a walk on the owner's
phone becomes the real test.

## The test, on every push

**Describe.** `tools/walk_test.mjs` serves the repo itself and opens the game in headless Chromium
with software WebGL (SwiftShader). For each chapter it goes through the gate, START, the caption
and NEXT, then drives the room deterministically. It checks the room's own behaviour (collisions,
animations, the maze's solvability, the treadmill wrap, piles measured from what is on screen),
plays each game with E, Space and Enter in turn, walks to the exit, and checks which loading clip,
or the title card, follows (`tools/walk_test.mjs:1`, [[sec:README:testing]]). A `--mobile` pass
runs at 390 × 844 with touch and 2× pixel density. It finds Playwright in a global install and
Chromium at `CHROMIUM`, or its usual path (`tools/walk_test.mjs:28`, `tools/walk_test.mjs:40`).
There is no `.github/` folder: nothing runs it automatically.

**Critique** *(Claude's analysis)*. Running it on every push is a small workflow: install Node and
Playwright with its Chromium on an Ubuntu runner, then run `node tools/walk_test.mjs` and
`node tools/walk_test.mjs --mobile`, and keep `tools/out/` as an artifact for the screenshots and
`report.json`. The test is already written for this. It brings its own server, it finds Chromium
by path, and it fails with a list of named checks. Two things to settle first:

1. **The test cannot see the loading screens.** Its own header says so: "there is no H.264
   decoder, so every loading clip errors out and the loader moves on by itself"
   (`tools/walk_test.mjs:5`). Every check of the 5.0 s count, the stall guard, the room video
   waiting for the clip, and SKIP on a loading screen is therefore untested. In chapter 1 the
   owner called the loading screen "A room of its own" ([[answer:5]]). It is the most carefully
   engineered part of the shell, and the one part CI would pass without looking at. I believe
   Playwright's bundled Chromium lacks the proprietary codecs, and that branded Chrome (Playwright's
   `channel: 'chrome'`) has them. A CI run on Chrome could then play the clips. That is worth
   checking before relying on it.
2. **Run time and flakiness.** The test drives two full visits of every game room, at software
   speed. A first CI run should record how long it takes, so the owner can decide whether
   `--mobile` runs on every push or only on pull requests.

## The file names

**Describe.** Loading clips are lowercase with an uppercase extension (`a.MP4`), and room videos
are uppercase with a lowercase extension (`A.mp4`). D's room video is the exception, `D.MP4`. On a
case-insensitive file system, `a.MP4` and `A.mp4` are the same name ([[sec:README:notes]]). The
names appear in the `CHAPTERS` array (`load`, `video`, `audio`; `script.js:12`). They also appear in
the walk test's expected next clip per room (`next: 'b.MP4'` and so on;
`tools/walk_test.mjs:592` to `tools/walk_test.mjs:921`), in a comment in `walk/textures.js:426`,
and in the README's tables and Structure list ([[sec:README:the-loop]], [[sec:README:structure]]).

**Critique** *(Claude's analysis)*. Renaming is mechanical and fits in one change. Move the files
into folders by role (`load/`, `room/`, `audio/`), give them the same lowercase name and
extension, and update the four places that name them. Doing it before chapter 3's open-ended
growth ([[answer:12]]) means every new room is added in the new scheme, and nothing depends on a
case-sensitive host. It is also the change that most needs CI first. A missed name breaks only the
room it belongs to, and that is exactly what the walk test's "the right loading clip follows"
check catches. It can only catch it, though, if the clip names it checks are updated in the same
commit.

## Owner's word

- *What is the slowest phone it must run on?* — "My own phone" ([[answer:17]])
- *The walk test (Playwright, headless Chromium, desktop and --mobile) runs only by hand: the repo
  has no CI. Should it run on every push?* — "Yes, on every push" ([[answer:18]])
- *The loading clips and room videos differ only by case (a.MP4 / A.mp4), which collides on macOS
  and Windows checkouts. Rename them, or keep the pairs?* — "Rename them" ([[answer:19]])

## Open threads

- Add a GitHub Actions workflow for the walk test, desktop and `--mobile`. Then rename the media in
  one commit behind it.
- Try branded Chrome in CI, so the loading screens are tested too.
- Name the owner's phone in the README, and add a frame-time readout behind a URL flag for walking
  it on that phone.
- Folder layout for the renamed media: by role (`load/`, `room/`, `audio/`) or by room (`a/`,
  `b/`, …)?
