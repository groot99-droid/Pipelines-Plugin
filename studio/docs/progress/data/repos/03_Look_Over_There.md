# Look_Over_There

**Walkable multilevel Backrooms game (three.js), hosts older games as doors.** Source: https://github.com/groot99-droid/Look_Over_There

Generated 20 November 2026 from the repository clone (`git log`, `git ls-files`, and the files at HEAD). Counts are as cloned. Commit dates are git author dates in UTC and can differ from when the work was done (merged PRs, integration passes).

## 1. Numbers

| Measure | Value |
|---|---|
| Commits (all branches) | 268 (137 non-merge, 131 merge) |
| First commit | 2026-11-01 |
| Last commit | 2026-11-20 |
| Days with commits | 16 |
| Tracked files | 358 |
| Checked-out branch | HEAD |
| Commit authors (non-merge, by name) | Claude: 123; groot99-droid: 14 |

Author names are git author names: "Claude" marks commits made by a Claude session, and the owner's GitHub handle marks commits made by the owner. Email addresses are left out.

**Tracked files by type (top 15):** .js 143; .mjs 60; .glb 47; .json 32; .wav 29; .md 15; .py 12; (none) 5; .jpg 5; .html 4; .yml 2; .csv 2; .blend 1; .css 1

**Tracked files by top-level folder:** games 90; shared 82; tools 78; models 34; world 24; server 12; characters 10; docs 10; (root) 6; monsters 5; audio 4; .github 2; blender 1

## 2. Activity by month and by day

| Month | Non-merge commits |
|---|---|
| 2026-11 | 137 |

**Per day (non-merge commits):** 2026-11-01 7; 2026-11-02 7; 2026-11-03 1; 2026-11-05 8; 2026-11-06 2; 2026-11-07 2; 2026-11-08 5; 2026-11-10 10; 2026-11-11 9; 2026-11-12 47; 2026-11-14 13; 2026-11-15 3; 2026-11-16 7; 2026-11-19 15; 2026-11-20 1

## 3. Layout (folders and file counts)

- **games/** 90 files
  - games/intern/ 75
  - games/rdwe/ 15
- **shared/** 82 files
- **tools/** 78 files
  - tools/physics/ 12
  - tools/blender/ 6
- **models/** 34 files
  - models/items/ 25
  - models/world/ 3
- **world/** 24 files
- **server/** 12 files
- **characters/** 10 files
- **docs/** 10 files
- **(repository root)** 6 files
- **monsters/** 5 files
- **audio/** 4 files
- **.github/** 2 files
  - .github/workflows/ 2
- **blender/** 1 files

## 5. CI workflows

- `.github/workflows/pages.yml`: Deploy to GitHub Pages
- `.github/workflows/tests.yml`: Tests

## 6. Documents inventory (15 Markdown files)

Markdown files by folder (top 25): docs 10; (root) 1; models 1; models/items 1; models/world 1; monsters 1

- `README.md` (1546 words): Look Over There. Sections: The game; Beyond the building: Farway; Multiplayer
- `docs/AUDIO.md` (828 words): Sound. Sections: How it is made; What plays; Limits
- `docs/BACKEND.md` (1528 words): Backend: accounts, saves and the leaderboard. Sections: Decisions; What it has to hold; What exists today; Architecture; Data model (first sketch); Sign-in; Security and privacy; Cost; What the owner has to do; Build steps for session 5
- `docs/GAMEPLAY.md` (7893 words): Gameplay plan. Sections: The round; Surviving; Progress: one puzzle per floor; Movement, sight and hearing; Roles that emerge (built); Build order; Characters; Fighting back: the Error Deletion Ray (built); Bots for tuning; Health and spawns (built)
- `docs/ITEMS.md` (16565 words): Items: the rules for every item. Sections: Contents; 1. Rules every item shares; 2. The price ladder [PROPOSAL]; 3. The three items that already exist; 4. Weapons: the master arsenal; 5. Consumables; 6. Med kit and Spicy Brew (new); 7. Dealer items; 8. Food; 9. The ten weapons compared
- `docs/MANIFEST.md` (3617 words): The world manifest. Sections: What reads it; What it does not hold yet; Adding things; Statuses; The Overworld, v0 (built); The City, v0 (built, session 9); Going back in, slice 1 (built); Gate return (fixed); Commands
- `docs/MODELS.md` (463 words): Models for the puzzle objects. Sections: Needed now (fuses); Needed later; Preparing a model for the game
- `docs/PHYSICS.md` (2233 words): Physics: the decision. Sections: Decision; What was measured, and where; Fit with the box colliders; Visual only in rooms: what it costs; The prototype; Licences; What I could not measure; Open items
- `docs/ROUND.md` (5094 words): The round: requirements. Sections: Round states; A. The round today and what it needs; B. What Farway adds; C. Going back in (partly built: each requirement's status is in the table); D. Co-op inside the games (design note, session 11); Decisions
- `docs/SESSIONS.md` (4191 words): Sessions: how the work is split. Sections: Status; Order; Rules for every session; Briefs
- `docs/WORLD.md` (7200 words): Farway: world bible v2. Sections: 1. Premise; 2. Tone: how to tell the three apart [SETTLED]; 3. The map; 4. Places; 5. Systems; 6. Scene budget (rough); 7. Technology and plan; 8. Version 0 [MY CALL]; 9. Proposals for what you left open [MY CALL]; 10. Still open
- `models/README.md` (437 words): models/
- `models/items/README.md` (796 words): models/items/. Sections: How they were prepared; What each file is
- `models/world/README.md` (280 words): models/world/. Sections: How they were prepared
- `monsters/README.md` (12 words): (no title)

## 10. Pull requests merged (55)

- 2026-11-05 #2 from `groot99-droid/claude/stoic-cannon-dej2nw`
- 2026-11-08 #3 from `groot99-droid/claude/manifest-loader`
- 2026-11-10 #5 from `groot99-droid/claude/gate-return`
- 2026-11-10 #4 from `groot99-droid/claude/results-local`
- 2026-11-10 #6 from `groot99-droid/claude/tune-original`
- 2026-11-10 #7 from `groot99-droid/claude/modes-parties`
- 2026-11-10 #8 from `groot99-droid/claude/physics-decision`
- 2026-11-10 #9 from `groot99-droid/claude/overworld-v0`
- 2026-11-11 #12 from `groot99-droid/claude/solo-test-stable`
- 2026-11-12 #11 from `groot99-droid/claude/city-v0`
- 2026-11-12 #10 from `groot99-droid/claude/going-back-in`
- 2026-11-12 #13 from `groot99-droid/claude/solo-test-stable`
- 2026-11-12 #14 from `groot99-droid/claude/city-v0-intern`
- 2026-11-12 #15 from `groot99-droid/claude/city-v0-grocery`
- 2026-11-12 #16 from `groot99-droid/claude/going-back-in`
- 2026-11-12 #17 from `groot99-droid/claude/mp-test-stable`
- 2026-11-12 #22 from `groot99-droid/claude/mp-test-stable`
- 2026-11-12 #23 from `groot99-droid/claude/going-back-in`
- 2026-11-12 #19 from `groot99-droid/claude/city-v0-pay`
- 2026-11-12 #20 from `groot99-droid/claude/city-v0-jobs`
- 2026-11-12 #21 from `groot99-droid/claude/city-v0-save`
- 2026-11-12 #24 from `groot99-droid/claude/city-v0-anomalies`
- 2026-11-12 #25 from `groot99-droid/claude/city-v0-newgame`
- 2026-11-12 #28 from `groot99-droid/claude/quirky-ramanujan-qajuxd`
- 2026-11-12 #26 from `groot99-droid/claude/city-v0-stalker`
- 2026-11-12 #27 from `groot99-droid/claude/city-v0-trash`
- 2026-11-12 #29 from `groot99-droid/claude/city-v0-sleep`
- 2026-11-12 #30 from `groot99-droid/claude/city-v0-mall`
- 2026-11-12 #32 from `groot99-droid/claude/quirky-ramanujan-qajuxd`
- 2026-11-12 #31 from `groot99-droid/claude/city-v0-museum`
- 2026-11-12 #33 from `groot99-droid/claude/city-v0-report`
- 2026-11-12 #34 from `groot99-droid/claude/city-v0-factory`
- 2026-11-12 #35 from `groot99-droid/claude/city-v0-lab`
- 2026-11-13 #36 from `groot99-droid/claude/city-v0-routines`
- 2026-11-13 #37 from `groot99-droid/claude/city-v0-theft`
- 2026-11-13 #38 from `groot99-droid/claude/city-v0-hud`
- 2026-11-13 #39 from `groot99-droid/claude/city-v0-watchers`
- 2026-11-14 #40 from `groot99-droid/claude/sessions-round-4`
- 2026-11-16 #45 from `groot99-droid/claude/item-models`
- 2026-11-16 #44 from `groot99-droid/claude/item-rules`
- 2026-11-16 #42 from `groot99-droid/claude/gbi-rooms`
- 2026-11-16 #41 from `groot99-droid/claude/world-rooms`
- 2026-11-16 #43 from `groot99-droid/claude/mp-test-finale`
- 2026-11-16 #49 from `groot99-droid/claude/flamethrower`
- 2026-11-16 #50 from `groot99-droid/claude/fuse-model`
- 2026-11-16 #51 from `groot99-droid/claude/trap-models`
- 2026-11-16 #52 from `groot99-droid/claude/lobby-rooms-race`
- 2026-11-19 #53 from `groot99-droid/claude/inspiring-cori-juqfrm`
- 2026-11-19 #54 from `groot99-droid/claude/crossbow-model`
- 2026-11-19 #56 from `groot99-droid/claude/held-weapon-models`
- 2026-11-19 #58 from `groot99-droid/claude/ammo-pack-model`
- 2026-11-19 #60 from `groot99-droid/claude/dreamcore-forest`
- 2026-11-20 #55 from `groot99-droid/claude/games-in-parties`
- 2026-11-20 #61 from `groot99-droid/claude/laser-dissector`
- 2026-11-20 #62 from `groot99-droid/claude/rebar-shear`

## 11. Source documents (verbatim)

Each file below is quoted from the repository at HEAD. Lines start with ">" so its headings do not mix with this document's.

### Source file: README.md

> # Look Over There
>
> A walkable multi-level Backrooms building (flooded poolrooms, office maze, white plaster room, the "Look Over There" showroom, the parking lot), built in Blender and served as a static three.js page.
>
> - `index.html` is the whole game: keyboard (WASD / arrow keys), mouse look, or an Xbox controller.
> - `world/<scene>.glb` + `world/<scene>.json` are the Draco-compressed geometry and the collision boxes, doors and cameras of one scene (B1, L1, L2, L3, L4; L4 includes the parking lot and the city). Only one scene is loaded at a time; the floors are joined by a door at the top of each staircase.
> - `blender/Look_Over_There.blend` is the final Blender file (all textures packed, stored with Git LFS).
> - `.github/workflows/pages.yml` publishes `index.html` and `world/` to GitHub Pages on every push to `main`.
>
> Run it locally by serving the folder (`python -m http.server`) and opening `index.html`.
>
> ## The game
>
> You start on the pool level (B1) and work upwards. Every door is shut: you open one with X (controller) or X / E (keyboard) and the monsters have to open them too.
> **Controls** (the same on keyboard and controller; `H` in game lists them):
> - Move WASD / left stick; look mouse / right stick; jump Space / A.
> - Crouch (toggle) Shift / left-stick click: press again to walk normally. Run (hold) R / right-stick click: faster than any monster, but loud and it tires you; running stands you up.
> - X (keyboard X or F) is the action button: doors, fuses, switches, notes, the power, the keypad, loot, and (held beside a downed teammate) lifting them.
> - Y takes out what you carry (tap again to rotate through the ray gun, the cloak and the beacon; hold for the wheel). Keyboard: Y, or 1 / 2 / 3.
> - RT / left click uses what you hold: the gun fires, the cloak switches on or off, a beacon is rolled. LT / right click: the gun aims; the cloak's secondary is a **short circuit** (it goes dead for 5 minutes and every monster within 8 m is stunned for 5 s, so you can run through them); a beacon's secondary **reverses its frequency** (for 12 s the monsters run from it, then they come back and group up round it).
> - LB / RB (Q / E): the consumable slots: Q throws a flash-vial (stuns, kills nothing), E sets an almond water land mine or a nail-bomb tripwire (`shared/consumables.js`). Each ammo pack adds one of each.
> - 1 to 5 (keyboard): the held items; in Going back in, 5 holds the second arsenal weapon (`shared/loadout.js`).
> - D-pad up / View / Tab / M: the handheld map. The camera feeds have no controls for now.
> If a monster sees you it chases; if it catches you, you die and come back on the same floor in a random spot.
>
> Monsters (config in `world/monsters.json`): Sinew of the Abyss on B1, The Pale Traveler on L1, a clawed creature on L2, the first creature in the showroom (L4).
> Models are in `monsters/`; the two Meshy exports that came with their own animations are used as-is (textures shrunk), and the rig-only ones got idle/walk/run/attack clips from `tools/make_monster_anims.py`.
>
> ## Beyond the building: Farway
>
> The building above is the Original, one place in a larger world, Farway (`docs/WORLD.md`, the world bible; `docs/MANIFEST.md`, the manifest that links the scenes; `docs/ROUND.md`, what a round must do). Built so far, solo unless noted (`docs/SESSIONS.md` has the status of every piece of work):
>
> - **Overworld**: the parking lot and the bus out (`world/parking_lot.json`, `world/street.json`). In rooms, players see each other there (presence only).
> - **City v0 on Hallam Row**: the apartment and its computer, a day clock and night rules, five jobs (the Intern quiz, the trash route, the museum night guard, the factory floor, the laboratory) paid by performance, hunger and rest, the grocery and theft, the mall, the stalker and the watchers, pedestrians with routines, the anomalies and reporting them, saving and New Game. In rooms, presence only.
> - **Going back in**: chambers below the building, a wave on entry and stairs down; the loadout locker and the arsenal (hunting crossbow, pneumatic bolt driver, stun baton, moth jelly dart, propane flamethrower; two carried at once), monster health and the Slowed, Jellied and Burning statuses. Rooms of up to 10 play the first two chambers, run by the server. `docs/ITEMS.md` holds the proposed rules for every item.
> - **The hidden games**: two gates open into `games/intern/` and `games/rdwe/`, copies of the author's other games.
> - **Models**: `models/` (the fuse, the ray gun, the cloak, the beacon) and the 24 item models in `models/items/`; see their READMEs.
>
> ## Multiplayer
>
> Up to 8 players share one building and its monsters. `node server/server.js` (after `cd server && npm ci`) serves the game and relays the room on one port; open `http://localhost:8080/`, pick one of five characters, enter a name and a room code, and send friends the same code (or `/?room=CODE`). Everyone readies up in a waiting room, then the group starts together on B1; anyone joining later drops straight in. The server runs the monsters and keeps each player's health, rounds, cloak and beacons (see docs/GAMEPLAY.md); press `H` in game for the controls, or open `/?sound=1` to audition the sounds.
>
> **Deploying on Railway.** The service was connected to `groot99-droid/Look_Over_There`, branch `claude/stoic-cannon-dej2nw`. As of 2026-11-19 that branch is 211 commits behind `main`, so a deploy from it is out of date: switch the source to `main` under the service's Settings > Source. If the repository is ever renamed again, re-attach the source there; a stale name stops deploys on push.
>
> In a room you see each other as the chosen characters (name tags, and arrows on the handheld map), share open doors (X / E also shuts an open door), and are hunted by the same monsters. One client per floor (chosen by the server, handed over when they leave) simulates that floor's monsters and the others follow its snapshots. The stair door at the top of each floor is locked until that floor's puzzle is done: on B1 (and for now L2) find three fuses, press E / X to pick one up (one at a time), and E / X at the door to put it in (a carrier is louder to the monsters and drops the fuse if downed); on L1 flip two far-apart switches, one at a time in any order, though each flip is loud and draws the monsters; on L2 find four notes (each holds one digit, shown to the whole team) and type the code at the door's keypad, where a wrong code is loud and locks it for 8 s ; L3 is a break floor with a power box that turns the building's power on, and on L4 the store's glass doors stay shut until the power is on, so otherwise you must find the power switch in the far corner of the store, which is loud. Opening the doors sets off a 60 s alarm that sends the L4 monsters to the doors; walking out onto the parking lot is your finish (the lot is safe), and when everyone is out the results show places, times and your best time. B1 has a locker for each player (one gun each) and every floor has ammo packs (press E). Fire the ray gun with the left mouse button, F or the controller's right bumper: a hit does not kill, it deletes the monster to a far spot out of sight. The handheld map shows a monster only while a security camera can see it, and for 3 s after (`docs/GAMEPLAY.md` has the rules). A monster that catches you downs only you: a teammate holds E / X beside you for 4 s to lift you, or you wake at the stairs after 45 s. You only learn which floor a teammate is on, never where.
>
> "Play solo" skips the server entirely (and keeps the old die-and-respawn rule), so the GitHub Pages build still works alone. To play online from Pages, point it at a server with `?server=wss://your-host/ws`. `Dockerfile` deploys the server to Railway. Tests: `node --test shared/*.test.js` (the rules), `cd server && npm test` (the relay), `node tools/manifest.mjs check` (the world manifest; these three run in `.github/workflows/tests.yml` on every push and before every session's push), `node tools/mp_test.mjs` (two headless browsers in a room) and `node tools/solo_test.mjs` (solo play and the optional model loader). `node tools/bots.mjs 3` plays whole rounds with a team of bot players (runner, bait, scout) and prints a tuning report (run it locally; what it found is in `docs/GAMEPLAY.md`). The plan for where the gameplay goes next is in `docs/GAMEPLAY.md`.
> Opening a stair door shows a lit hallway behind it (drawn only through the doorway, so it never runs into the level around it); stepping through the doorway takes you to the other floor, where the same hallway is behind you. The two gates to the hidden games still open into a short walkable passage first.
> On B1, L1 and L2 there is one of each kind of prop; fire alarms, clocks and security cameras are the only things that repeat. `tools/blender/verify_world.py` checks the ceilings, the stair parts against everything around them, and the duplicates.
>

### Source file: docs/SESSIONS.md

> # Sessions: how the work is split
>
> The Farway plan is too big for one session. This file splits it into sessions that can run side by side, says which must come first, and gives each a brief that stands on its own, since a new session starts from its prompt and a fresh checkout.
>
> Read first: `docs/WORLD.md` (what Farway is), `docs/ROUND.md` (what a round must do), `docs/MANIFEST.md` (the world manifest), `docs/GAMEPLAY.md` (what is built).
>
> ## Status
>
> | # | Session | When | Needs | Status |
> |---|---|---|---|---|
> | 1 | Manifest core and loader | done | | **done**, merged (PR #3) |
> | 2 | Gate return fix, links read from the manifest | Now | 1 | **done**, merged (PR #5) |
> | 3 | Results v2, local: deaths, revives, score, a round log line | Now | 1 | **done**, merged (PR #4) |
> | 12 | Tune the Original, starting with B1 | Now | 1 (better with 3) | **bot pass done and merged** (PR #6): down time 20 s, 6 packs on B1; needs the owner's playtests |
> | 6 | Overworld v0 | Next | 1 and 3, after 2 | **done**, merged (PR #9); solo only, rooms cannot enter it yet |
> | 7 | Physics: decision and a playground prototype | Next | | **done**, merged (PR #8); `docs/PHYSICS.md` accepted by the owner with cannon-es, visual only in rooms |
> | 4 | Modes and parties | Next | 1 | **done**, merged (PR #7); server and lobby, "go to a friend" is server-side only |
> | 8 | Going back in prototype | Then | 3 and 4 | **slices 1 to 3 merged** (PR #10, solo only): the options screen to a chamber, a wave on entry, stairs down (2 of 20 chambers); the loadout locker and the hunting crossbow; the Q/E consumables. Rooms still refuse the mode ("soon"). Next step: session 16 |
> | 9 | City v0 on Hallam Row | Then | 6 | **slices 1 to 21 merged** (PRs #11, #14, #15, #19 to #21, #24 to #27, #29 to #31, #33 to #39; solo only): bus, street, day clock and night rules, apartment and computer, stalker and bed, the five jobs (Intern quiz, trash route, museum, factory, lab) and pay, hunger, rest, grocery and theft with its camera, saving and New Game, the mall, the anomalies and reporting them, pedestrians with routines, the HUD layout, the watchers. Not played by a person yet |
> | 13 | Make `tools/solo_test.mjs` deterministic | Now | | **done**, merged (PR #12): the flaky checks needed room around a random respawn spot; the test now stages a spot that has it. No game change |
> | 14 | Make `tools/mp_test.mjs` deterministic | Now | | **done**, merged (PR #17): the recurring failures were the test racing the server (the server acts on its own, trailing, record of where a player is) and an L1 monster parked where it had no path to the noise. The test now waits for the server's view; 7 of 7 runs passed. Going back in's per-frame work in rooms was not measurable. No game change |
> | 15 | `mp_test`: the L4 finale switch race | Round 4 | 14 | **done**, merged (PR #43): not a teleport race (the server takes the power by floor, not position). The failure was not reproduced on its own in 12 finale runs; forcing Xia down at the press gives the same failed checks and the same crash, and she stood unguarded on B1 while the second page loaded. The test now guards each player once the round has them and checks the server's and the page's view at the press; missing results fail a check instead of throwing. A second, older flake (a 60 s wait for two pages to arrive on L4) got the finale's 170 s. 6 of 6 runs passed (114 checks). No game change |
> | 16 | Going back in in rooms | Round 4 | 4 and 8; waits for the owner's playtest and decisions | **slices 1 to 3 merged** (PR #42): a room of up to 10 plays the two chambers; the server starts each wave once and owns the bolts, kills, loadout and consumables (`docs/ROUND.md`, "Session 16"). Open for the owner: the locker's name, the crossbow at the start, wave size for a party, a finish and score for the mode. Not played by a person yet |
> | 17 | Overworld and City in rooms, and "go to a friend" in the page | Round 4 | 4, 6 and 9; waits for the owner's playtest | **slices 1 to 3 merged** (PR #41), presence only: a room walks out to the parking lot, rides the bus to Hallam Row and uses the apartment, and sees each other there (the manifest's `presence` scenes; the server relays positions and runs no rules); P lists the party with where each player is and a Go button. Every other interior, both games and Going back in stay solo only. Not played by a person; seven questions for the owner are in the PR |
> | 18 | Item rules: one document for every item | Round 4 | | **written, merged** (PR #44): `docs/ITEMS.md` proposes rules, prices and tuning tables for all 24 modelled items plus the ray, cloak and beacon. A design document only: no game code, models or manifest changed. Waits for the owner's critique before any of it is built |
> | 19 | Build the pneumatic bolt driver (the first arsenal weapon after the crossbow) | Round 4 | 18 | **built, merged** (PR #46): `shared/driver.js`, monster health (`hp`, `MonsterSim.hurt`), key 5 and a locker row, solo only. Rooms (session 16) and the Market are not touched |
> | 20 | Build the stun baton, the two-weapon carry cap and the weapon slots | Round 4 | 19 | **built, merged** (PR #47): `shared/baton.js`, `ARSENAL`/`canTake` in `shared/loadout.js`, solo only. Rooms and the Market are not touched |
> | 21 | Build the moth jelly dart and the Slowed and Jellied statuses | Round 4 | 20 | **built, merged** (PR #48): `shared/dart.js`, `MonsterSim.slow`/`jelly`/`statusTick`, solo only. Rooms and the Market are not touched |
> | 22 | Build the propane flamethrower and the Burning status | Round 4 | 21 | **built, merged** (PR #49): `shared/flame.js`, `MonsterSim.burn`, solo only. Rooms and the Market are not touched |
> | 23 | Build the frequency horn | Round 4 | 22 | **built**, draft PR on `claude/frequency-horn`: `shared/horn.js`, `shared/cone.js`, `MonsterSim.shove`, solo only. Rooms and the Market are not touched |
> | 24 | Build the rocket launcher | Round 4 | 23 | **built**, draft PR on `claude/rocket-launcher`, stacked on session 23's `claude/frequency-horn`: `shared/rocket.js`, `shared/flight.js`, solo only. Rooms and the Market are not touched |
> | 25 | Build the laser pointer dissector | Round 4 | 24 | **built**, draft PR on `claude/laser-dissector`, stacked on session 24's `claude/rocket-launcher`: `shared/laser.js`, `MonsterSim.provoke`, solo only. Rooms and the Market are not touched |
> | 26 | Build the hydraulic rebar shear (the owner's design) and the chamber barricades | Round 4 | 25 | **built**, draft PR on `claude/rebar-shear`, stacked on session 25's `claude/laser-dissector`: `shared/shear.js`, `shared/barricade.js`, a chained door is a wall to the nav, solo only. Rooms and the Market are not touched |
> | 5 | Backend: Postgres, anonymous accounts, Discord sign-in, leaderboard | Later | 3 | decided, plan in `docs/BACKEND.md`; not started |
> | 10 | Editor for scenes and links | Later | 1 | not started |
> | 11 | Games inside parties (co-op in Right Door, Wrong Exit and the Intern) | Later | 4 | **slices 1 and 2 in the draft PR for `claude/games-in-parties`** (design note; manifest `coop` areas and game places, server relay, tests): both games still solo only. Slices 3 (Right Door, Wrong Exit drawn in a room) and 4 (the Intern) are next; the owner chose the defaults for the three open questions |
>
> Update this table in the last commit of each session.
>
> ## Order
>
> ```
> Now:    2    3    12          touch different files, so they can run side by side
> Next:   6 (after 2 and 3)    7    4
> Then:   8 (needs 3 and 4)    9 (needs 6)
> Later:  5 (needs 3)    10    11 (needs 4)
> Round 4: 15 to 22, all merged by 2026-11-16 (PRs #41 to #49)
> ```
>
> Also merged outside the sessions on 2026-11-16: the 24 item models (PR #45), the fuse model (PR #50), the land mine and tripwire models (PR #51), and a lobby fix (PR #52). Status as of 2026-11-19.
>
> - **Round 4 starts with a playtest by the owner.** Nothing from sessions 6, 8, 9 or 12 has been played by a person yet. Sessions 16 and 17 were planned to wait for that; both were merged on 2026-11-16 without it, so the owner's playtest and open decisions (the score formula, the name of the Going back in locker, "different truths per area", whether the crossbow starts in your hands) still apply to what is now on `main`.
>
> - **The game does not need the backend to be built.** Session 5 waits until there are players who want saved progress or a ranking across players, or until the server log is not enough data. Until then the Original-complete flag lives in the browser and the best time is per browser.
> - **Session 12 matters most for whether the game is fun.** The Original is untuned (see its brief), and a bigger world does not help if the opening floor is too punishing.
> - Sessions in the same row can run side by side. A session in a later row starts when what it needs has merged.
>
> ## Rules for every session
>
> 1. Start from `main` after the manifest PR is merged. Work on a branch named `claude/<short-name>`, one branch and one draft PR per session.
> 2. Before pushing, run all three:
>    - `node --test shared/*.test.js`
>    - `cd server && npm ci && npm test`
>    - `node tools/manifest.mjs check`
> 3. A change to what the game does needs a test that fails first and passes after. Say in the PR what you ran and what you did not run. Do not say a browser flow works unless you drove it.
> 4. Stay inside your files (table below). If you must touch another session's region, keep it to a few lines and say so in the PR.
> 5. Follow the existing style: short comments that say why. No key or secret in any file, and tests use fake values.
> 6. When you need a decision from the owner, write the question and the default you will use, and carry on with the default.
>
> ### Who touches `index.html`
>
> `index.html` is one large file, so parallel sessions conflict there. Keep to these regions:
>
> | Region | Session |
> |---|---|
> | gates, `goLink`, `enterGame`, the "That door does not open in a room" toast | 2 |
> | the finale and `#results` (markup, styles and code) | 3 |
> | the lobby overlay and the join code | 4 |
> | `loadScene`, scene types, the options screen at the store doors | 6 |
> | held items, consumable slots, the chamber loader | 8 |
> | the player's walk, run and crouch numbers (`WALK_SPEED`, `RUN_SPEED`, `RUN_S`, `RECOVER_S`) | 12 |
>
> Merge order when several are open: 2, then 3, then 6.
>
> ---
>
> ## Briefs
>
> Every prompt below starts with this line:
> > You are working in `groot99-droid/Look_Over_There`. Read `docs/WORLD.md`, `docs/ROUND.md`, `docs/MANIFEST.md` and `docs/SESSIONS.md` first, branch from `main`, and follow the rules in `docs/SESSIONS.md`.
>
> ### Session 2: gate return fix, links read from the manifest
> - **Goal.** Reproduce the suspected bug first. After Right Door, Wrong Exit ends, the page may call `loadScene(l.scene || S.id)` with `S.id` equal to the passage scene `T`, which has no entry in `SCENES`. Prove it in a headless browser, then fix it using `returnTo` from the manifest. Read the "solo only" toast from the manifest's `soloOnly` flag.
> - **Touches.** `index.html` (gates region), a new `tools/gates_test.mjs`.
> - **Done when.** The new test fails on `main` for the Right Door, Wrong Exit gate and passes after the fix. Both gates return to L4 at the arrival point in their link. The Intern's gate still works.
> - **Prompt.** Reproduce the gate return bug in `tools/gates_test.mjs` (Playwright, same style as `tools/stairs_test.mjs`): walk to each gate in solo play, enter the game, end it, and assert the player is back on L4. For Right Door, Wrong Exit, end it by calling the walk module's finish. For the Intern, post the `intern-ending` message. Show the test failing, then fix `enterGame` using `REGISTRY` and the link's `returnTo`. Make the room toast read `soloOnly`.
>
> ### Session 3: results v2, local
> - **Goal.** RND-20 to RND-23 in `docs/ROUND.md`, with no database and no accounts.
> - **Touches.** `server/playerstate.js`, `server/server.js` (stat hooks, the run record), `shared/finish.js`, the `#results` region of `index.html`.
> - **Does not touch.** Accounts, storing run records, ranking. Those are session 5, later.
> - **Done when.** The server counts downs, deaths, revives given, shots, shots that hit, beacons thrown and time per floor, and each counter has a test. At the end it builds the run record from RND-21 and writes it to the server log as one JSON line, without player names. The results screen shows time, deaths, revives, score and the best time on this browser. The first Original finish shows a welcome to Farway and sets `original_complete` in `localStorage`.
> - **Decided.** A death is a down nobody revived (the 45 s ran out, or any down in solo play). Revives given are counted and add to the score. Use the RND-27 formula, which is a placeholder.
> - **Prompt.** Add per-player counters to the server's player state, with tests. Build the run record in `shared/finish.js` as a pure function with tests, and log it as one JSON line per finished round with no names. Extend the `results` message and the results screen. Store `original_complete` in `localStorage` under one key, wrapped in try and catch.
>
> ### Session 4: modes and parties
> - **Goal.** RND-10 to RND-14, and the first half of RND-12: a party is a room, each player's place is separate from the party, any player can join or leave a floor at any time, and "go to a friend" jumps to their floor.
> - **Touches.** The join and lobby code in `server/server.js` and the lobby overlay in `index.html`; `shared/registry.js` lookups for modes.
> - **Done when.** A client joins with a `mode`. The room takes its floors, size and finish from the manifest. A party key groups people by mode and code. `GET /rooms?mode=` lists open rooms. The server refuses to start if the manifest's room size exceeds the player colours.
> - **Decided.** Room size is 10 (done in the manifest PR). Make sure the lobby, name tags and spawns handle 10.
>
> ### Session 5: backend (Postgres, anonymous accounts, Discord sign-in, leaderboard)
> - **When.** Later. The game does not need it to be built. Start it when players want saved progress or a ranking, or when the server log is not enough data.
> - **Decided.** `docs/BACKEND.md` is the plan: Postgres as its own Railway service, anonymous accounts first, Discord sign-in, server-only writes, 18+ audience. Email and marketing come later.
> - **Goal.** The five build steps in `docs/BACKEND.md`: the store interface with an in-memory and a Postgres implementation, anonymous sessions, Discord sign-in, run records and the leaderboard, and the privacy routes.
> - **Touches.** New files under `server/store/` and `server/auth/`, a few lines in `server/server.js` (the join and the end of a round), new migration files. Nothing in `index.html` except a sign-in button and the leaderboard screen, kept to a small new region.
> - **Needs.** Session 3 merged for steps 4 and 5. Steps 1 to 3 can start earlier.
> - **The owner must first** create the Discord application, add the Railway Postgres service and set the variables listed in `docs/BACKEND.md`. Never put a secret in a file, a test or a chat.
> - **Done when.** The existing server tests pass unchanged against the in-memory store, a reload keeps `original_complete`, Discord sign-in works against a fake Discord in tests, and a time sent by a client is refused.
> - **Prompt.** Follow `docs/BACKEND.md` step by step. Start with the store interface and migrations, with every existing test passing on the in-memory store. Use a fake Discord server in tests. Say in the PR what ran against a real database and what did not.
>
> ### Session 6: Overworld v0
> - **Goal.** The smallest Overworld. Promote `overworld` to built in the manifest with a `parking_lot` scene made from `world/Exterior.glb`, the table and chairs as the spawn, the Look Over There store doors, and one sky mode. Walking out of L4 after the Original continues into it. The store doors show an options screen: Original, or Going back in (disabled, "soon"). The link `lot.L4.front_doors>overworld` requires `original_complete`.
> - **Touches.** The `loadScene` and scene-type region of `index.html`, new files under `world/`, the manifest.
> - **Does not touch.** The city, the bus, the forest, physics.
> - **Done when.** A solo round ends in the Overworld, a reload keeps the flag, and `node tools/manifest.mjs check` passes with the Overworld built.
> - **Needs.** Sessions 1 and 3, and after session 2.
>
> ### Session 7: physics decision and playground prototype
> - **Goal.** Choose how objects get gravity and physics everywhere. Compare a WASM engine (Rapier) with a small JS one (cannon-es) on download size, step cost with 200 bodies, and fit with the existing box colliders. Write `docs/PHYSICS.md`. Build an isolated prototype (a kickable ball, a swing) under `tools/physics/`.
> - **Does not touch.** `index.html`. Nothing merges into the game until the owner accepts the document.
> - **Decision to carry on with a default.** Physics objects are visual only in rooms (each client simulates them, the server does not).
>
> ### Session 8: Going back in prototype
> - **Goal.** GBI-1 to GBI-8 for one floor. A chamber scene loaded through the manifest, the wave starting on entry, a stairs-down chamber, a loadout locker, consumable slots on Q and E, and one lethal weapon with its own ammo rule (the hunting crossbow).
> - **Needs.** Sessions 3 and 4. Split it further before starting if it grows.
>
> ### Session 9: city v0 on Hallam Row
> - **Goal.** A street scene reached by the bus, the apartment with its computer, a 15-minute game day, the night rule (stores close, then danger), and the Intern's job at 666 Hallam Row through the shared application quiz.
> - **Needs.** Session 6.
>
> ### Session 10: editor for scenes and links
> - **Goal.** A local page for placing doors, spawn points and links and writing them to the manifest and the scene files. Decide first whether the manifest becomes JSON with a thin JS wrapper (so a tool can write it safely); `node tools/manifest.mjs export` already produces the JSON.
> - **Needs.** Session 1.
>
> ### Session 11: games inside parties
> - **Goal.** RND-15. Co-op inside Right Door, Wrong Exit and the Intern is optional: a player can enter a game alone or with friends, and friends can pop in at any time. A party of 10 can split across levels and games.
> - **Needs.** Session 4 (a party is a room, and a player's place is separate from the party).
> - **Start with a design note** in `docs/ROUND.md` before code: one instance per party and game, which players are in it, and what is shared. Default for version 1: players in the same instance see each other walk (presence and positions only), and each player's puzzles stay their own. Shared puzzle state comes later.
> - **Done when.** Two clients enter Right Door, Wrong Exit separately, meet in one instance, and leave without breaking the other's game. The gate's `soloOnly` flag is dropped for that game in the manifest. Then the same for the Intern.
>
> ### Session 12: tune the Original, starting with B1
> - **Why.** The Original is untuned. `docs/GAMEPLAY.md` plans about 20 minutes, with B1 taking about 4. The owner's solo round took 36 minutes, with about 23 downs on B1, and no bot team ever solved B1's fuse puzzle. Expanding the world does not help if the opening floor is too punishing.
> - **Goal.** A team of 3 or 4 can finish B1 in about 4 minutes without being downed over and over. Then the same for L1 and L2.
> - **Starting numbers.** These are defaults for the owner to confirm: B1 cleared in about 4 minutes, and fewer than 5 downs per player on B1.
> - **Levers to try, one at a time,** from the notes in `docs/GAMEPLAY.md`:
>   - a shorter down time (45 s now; try 20 s first);
>   - more ammo on B1 (more packs, or more rounds per pack);
>   - spawns nearer the fuses, or fuses nearer the spawn. The group spawns far east and the fuses are in the west, about 80 m of path through one corridor where nearly every death happened;
>   - fewer monsters on B1 (4 now), or a way round that corridor;
>   - whether the cloak is worth its cost. The owner rarely used it.
> - **Method.** Change one lever, then take 3 playtests with real players, noting time per floor, downs, and what they say about it. The bots can run each change, but they are too cautious (see the bot note in `docs/GAMEPLAY.md`), so make them take more risks before trusting them. Use session 3's round log line once it exists, or time rounds by hand.
> - **Touches.** The numbers in `shared/health.js`, `shared/spawn.js`, `shared/loot.js` (the loot counts are in the manifest), `shared/fuses.js`, `shared/monsters.js`, `world/monsters.json`, and the player constants in `index.html`. No new features.
> - **Done when.** The targets above are met in 3 playtests with 3 or 4 players, and the PR shows the numbers before and after for each lever.
> - **Decision to carry on with a default.** The targets above. The owner may change them.
> - **Prompt.** Reproduce the problem first: run `node tools/bots.mjs` on B1 and record time to the first fuse and downs per player. Then change the levers one at a time, in the order above, and record the same numbers after each. Keep every change in the numbers, never in new rules. Ask the owner for playtests and write down what they report.
>
> ### Session 15: `mp_test`: the L4 finale switch race
> - **Goal.** `tools/mp_test.mjs` still fails now and then in the finale room: "the L4 switch sets off the alarm for both players" fails, and every finale check after it fails with it. The test teleports Xia to the L4 power switch and presses X at once, the same teleport-then-act race session 14 fixed at the L1 switch, the L2 keypad and doors and the L4 far switch, but this one was not covered.
> - **Touches.** `tools/mp_test.mjs` only. A game or server change only if you find a real bug, as its own commit with a test that fails first.
> - **Done when.** The finale switch waits on the server's view of the player (the same `serverSees`/`atServer` approach the test already uses) before the press. Failure output prints what the page and the server each see. `mp_test` passes at least 6 runs in a row, one at a time, and the PR lists every run. No assertion weakened, no timeout widened, no blind sleep.
>
> ### Session 16: Going back in in rooms
> - **Goal.** Let a party play Going back in together. The server runs chambers as floors (`floorY`, monsters, waves), starts the wave when the first player steps in, and owns bolts, kills and the loadout. The mode's `status` becomes built and the lobby's disabled button is enabled. Session 8 wrote down what is needed in `docs/ROUND.md`.
> - **Touches.** `server/server.js` and the floor sim, the manifest (`going_back_in` and the `gbi` area), the lobby region and the chamber region of `index.html`, server and browser tests.
> - **Waits for.** The owner's playtest of the solo mode and the open decisions (the locker's name, the crossbow at the start).
> - **Done when.** Two clients in one room play a chamber and take the stairs to the next one, and a server test with 10 clients passes.
>
> ### Session 17: Overworld and City in rooms, and "go to a friend"
> - **Goal.** A party can walk out of the Original into the parking lot together and ride the bus to Hallam Row, seeing each other (presence and positions only, as session 11's default). Each player's City clock, needs and jobs stay their own in version 1. The page gets the "go to a friend" button that session 4 left server-side.
> - **Touches.** `server/server.js` (page scenes a room can hold with presence only), the scene region of `index.html`, the lobby region for the friend list, tests.
> - **Waits for.** The owner's playtest of the solo City.
> - **Done when.** Two clients in one room meet in the parking lot and on the street and see each other move, and "go to a friend" moves one to the other's scene in a browser test.
>

### Source file: docs/ROUND.md

> # The round: requirements
>
> A **round** is one play-through of a **mode** by a **room** of 1 to 10 players: from the ready-up to the results. This file says what a round must do for Farway.
>
> - **BUILT**: it is in the game now and a test covers it (`tools/mp_test.mjs`, `tools/stairs_test.mjs`, `server/*.test.js`, `shared/*.test.js`).
> - **CHANGE**: it exists and must change.
> - **NEW**: nothing exists yet.
> - **OPEN**: it needs a decision from the owner first. The question is in the "Decisions" list.
>
> Modes live in the world manifest (`shared/farway.manifest.js`, `modes`): `original` is built, `going_back_in` is planned. A mode names its area, its floors in order, its room size and how a round finishes. Docs: `docs/MANIFEST.md`, `docs/GAMEPLAY.md`, `docs/SESSIONS.md` (who builds what).
>
> ## Round states
>
> ```
> join (room code) -> LOBBY (pick a character, ready up)
>   -> everyone ready -> COUNTDOWN 10 s -> PLAYING (stages, floor by floor)
>   -> everyone still in the room is out -> RESULTS -> [Play again] or [Walk out to the Overworld]
> A player who joins during PLAYING skips the lobby and spawns with the group. A round runs until the room empties.
> ```
>
> ## A. The round today and what it needs
>
> | ID | Requirement | Status | How we know |
> |---|---|---|---|
> | RND-1 | A room is joined by code. It holds `modes.<mode>.players.max` players (10), each with their own colour, and refuses more with `{t:"full"}`. | BUILT | `server/server.test.js` fills a room |
> | RND-2 | Lobby: pick one of five characters, ready up. When everyone is ready a 10 s countdown starts, then the round starts for the room. Someone who joins mid-round skips the lobby. | BUILT | `tools/mp_test.mjs` |
> | RND-3 | The stages are the mode's floors, in order. A gated floor's stair door stays locked until its puzzle is solved: fuses (B1), switches (L1), a keypad (L2). L3 has none. L4 needs power. | BUILT | `shared/*.test.js`, `tools/stairs_test.mjs` |
> | RND-4 | On L4 the store's glass doors open when the power is on, then a 60 s alarm runs. Walking out onto the parking lot is your finish. | BUILT | `shared/finish.test.js`, `shared/power.test.js` |
> | RND-5 | The round ends when everyone still in the room is out. Place is the order you left in. Someone who leaves the room does not hold it up. Solo ends the moment you walk out. | BUILT | `shared/finish.test.js` |
> | RND-6 | A caught player is downed, not dead. A teammate revives them in 4 s. After 45 s they wake at the stairs they came up. Solo: die, wait 3 s, respawn somewhere random. | BUILT | `server/playerstate.test.js` |
> | RND-7 | The server owns each player's HP, rounds, beacons, cloak and down state. A client sends intents and cannot give itself anything. | BUILT | `server/playerstate.test.js` |
> | RND-8 | Monsters run on the server at 20 Hz, one simulation per room and floor that has a player. Snapshots go out at 10 Hz. | BUILT | `server/floors.test.js` |
> | RND-9 | A round must never name a floor that is not a multiplayer scene of the manifest. | BUILT (session 1) | `shared/manifest.test.js`, `server/server.test.js` |
>
> ## B. What Farway adds
>
> ### Modes and parties
>
> | ID | Requirement | Status | How we know |
> |---|---|---|---|
> | RND-10 | A client joins with a `mode`. The server reads the mode's floors, room size and finish from the manifest, and a room keeps one mode for its life. | BUILT | `server/server.test.js`: `original` takes its floors, cap and finish from the manifest; `going_back_in` is refused with `{t:"refused",reason:"soon"}`, an unknown mode with `unknown_mode`. |
> | RND-11 | The room size comes only from the manifest (10). The server refuses to start if it has fewer player colours than the size. | BUILT | `server/server.js` throws at start if colours are short; `server/floors.test.js` simulates a full room. |
> | RND-12 | A party is a room (the same mode and the same code). Where you are is separate from who you party with: ten players can split across floors, chambers and games in any number of groups, and each player can join or leave a place at any time. A player can jump to a friend. | PART BUILT: the party key is mode plus code, and `{t:"goto",to:id}` returns a friend's place and spot: a floor, or a page scene the manifest marks `presence` (the parking lot, Hallam Row, the apartment), refused with the missing flag if you may not enter it. In the page, P lists the party with where each player is and a Go button (session 17; `tools/world_mp_test.mjs`). Rooms cannot enter chambers, games or the City's other interiors yet. | Ten clients in one party stand in three different places, and a late joiner goes to a friend's place. |
> | RND-13 | The server can list open rooms for a mode: code, mode, players, phase, floor furthest along. | BUILT | `GET /rooms?mode=original` returns only open, non-full rooms. |
> | RND-14 | Until RND-15 lands the two game gates are solo only. A manifest link marks this with `soloOnly`, and the page reads the flag instead of hard-coding it. | CHANGE | A test asserts the toast comes from the manifest flag. |
> | RND-15 | Co-op inside a game (Right Door, Wrong Exit, the Intern) is optional, never required. A player may enter a game alone or with friends, and friends can pop in at any time. Each game runs one instance per party, and the players inside it see each other. A game's gate stops being solo only once the game supports this. | SLICE 2 BUILT (section D): the manifest and server can hold game places (`coop` areas, `REGISTRY.gamePlaces`, `goto` through them, a player in a game does not hold the finish); both games still `soloOnly` until the page draws other players | Two clients enter Right Door, Wrong Exit separately and meet in one instance. |
>
> ### Results, deaths and ranking
>
> | ID | Requirement | Status | How we know |
> |---|---|---|---|
> | RND-20 | The server counts per player: downs, **deaths** (a down nobody revived: the 45 s ran out, or any down in solo play), **revives given**, shots, shots that hit, beacons thrown, cloak seconds, time on each floor. Today it keeps none of these. | BUILT, except cloak seconds (not counted yet) | `server/playerstate.test.js` covers each counter. |
> | RND-21 | At the end the server builds one **run record**: `{roomCode, mode, startedAt, endedAt, floors: [{scene, ms}], players: [{name, char, place, ms, downs, deaths, revives, shots, score}]}`. Only the server writes it. For now it goes to the server log as one JSON line without names; a database comes with session 5. | BUILT (the record has no names; solo play has no server, so it is not logged) | A test plays a fake round and checks the record. |
> | RND-22 | The results screen shows place, time, deaths, revives and score, your best time on this browser, and a welcome to Farway the first time you finish the Original. | BUILT (shows place, time, deaths, revives, score, best; the browser check is `tools/results_test.mjs`, solo only) | A browser test finishes a solo round and reads the screen. |
> | RND-23 | Finishing the Original for the first time sets the flag `original_complete`. It is stored on this device first and moves to the account when accounts exist. | BUILT (stored on this browser only) | The flag survives a reload. |
> | RND-24 | After the results the player can walk out to the Overworld. The link `lot.L4.front_doors>overworld` requires `original_complete`. | BUILT, solo and in a room (the walk out is offered on the results screen once the flag is held; `tools/overworld_test.mjs`). In a room the lot is a `presence` scene: the server relays who is there and where and runs nothing, and it lets a player in only with the flag, which it knows for itself once that player has finished a round in the room (`server/presence.test.js`, `tools/world_mp_test.mjs`) | `tools/manifest.mjs links` shows it open once the flag is held. |
> | RND-25 | Ranking is online and counts runs from the whole game. Boards are kept apart by mode and by group size: solo, 2 to 4, 5 to 10. Whether a board ranks by time or by score is open. | NEW | `docs/BACKEND.md`; Decision 1 (time or score) |
> | RND-26 | A run time is accepted only from a run record the server made. A client cannot send a time. | NEW | A test posts a made-up time and it is refused. |
> | RND-27 | Revives count toward a player's total score and deaths count against it. Starting formula, to tune: 1000, plus 150 per revive, minus 100 per death, minus 1 per 5 s of round time, never below 0. | BUILT (placeholder numbers in `SCORE`, `shared/finish.js`; not confirmed by the owner) | A test scores a made-up run. |
>
> ### Safety and load
>
> | ID | Requirement | Status | How we know |
> |---|---|---|---|
> | RND-30 | A finish is accepted only from L4 with the power on. | BUILT | `server/server.test.js` |
> | RND-31 | The server rejects puzzle claims that the floor's state does not allow (a fuse you are not near, a wrong code, a switch already on). | BUILT | `shared/*.test.js` |
> | RND-32 | The server tick averages under 5 ms with a full room. It measured 0.31 ms with 8 bots. Measure again at 10. | BUILT at 8, CHANGE at 10 | `node tools/bots.mjs 8` prints the tick time. |
> | RND-33 | Each socket has a message budget (a burst of 240, 90 a second, a kick past 600). | BUILT | `server/server.test.js` |
>
> ## C. Going back in (partly built: each requirement's status is in the table)
>
> A 20-wave run: 5 floors, 4 chambers each, top down: L4, L3, L2, L1, B1. A chamber is as big as an original floor.
>
> | ID | Requirement | Status | How we know |
> |---|---|---|---|
> | GBI-1 | The mode `going_back_in` lists its floors top down, `chambersPerFloor: 4` and `waves: 20`. Version 1 has 4 chambers per floor, so no randomness yet. The existing floor is one of the four. | PART BUILT: the mode has these and a `startChamber`; 2 of the 20 chambers exist | Manifest check, `shared/manifest.test.js`. |
> | GBI-2 | A chamber is a scene of the manifest. The 4th chamber on each floor has the stairs down. Chambers join with a mix of vent crawls, elevators, stairs, doors and painted-sky halls. | PART BUILT: two chambers, joined by stairs, alone and in a room. The walk to the bottom floor is not built. | `tools/gbi_test.mjs` walks from the Overworld through the stairs; `tools/gbi_mp_test.mjs` takes them with two players. |
> | GBI-3 | The wave starts when the players enter the chamber. The rest is quiet time: objects to find, puzzles, loot, defences to build. A chamber is cleared when its objectives are done. | PART BUILT: the wave starts on entry (alone; in a room, once, when the first player steps in). Cleared by kill count only; the other objectives are not built. | `shared/gbi.test.js`, `tools/gbi_test.mjs`, `server/gbi.test.js` |
> | GBI-4 | Unkillable threats are environmental (crushing walls, lava floor, high tides, toxic gas, chainsaw blades). Special entities come later. | NEW | One hazard per chamber type. |
> | GBI-5 | Doors can be closed, trapped or barricaded, and nothing else. Players can crawl into vents. Monsters never use vents. | PART BUILT, solo only: a chained supply cage in every chamber and a chained door where one is safe to chain (session 26, `shared/barricade.js`); only the rebar shear opens them. Vents are not built. | `shared/barricade.test.js`, `tools/shear_test.mjs` |
> | GBI-6 | A safe house on every floor holds a shop, a stash, a save, crafting and a respawn point. | NEW | |
> | GBI-7 | A locker (one per safe house and one per chamber) shows your loadout and lets you change it. After you die it returns your weapons and gear for free. It does not return ammo, consumables or perks. Those are bought back at the Market or a safe house. The existing one-time loot locker on B1 needs a different name. | PART BUILT: one per chamber, alone and in a room (each player's loadout is kept by the server); no safe house, no Market | `tools/gbi2_test.mjs` dies and checks what the locker returns; `server/gbi.test.js`, `tools/gbi_mp_test.mjs` |
> | GBI-8 | Lethal weapons come from the arsenal (ten weapons, three consumables). Each needs its own ammo rule. The ray, the cloak and the beacon stay non-lethal. Q and E (LB and RB) are consumable slots. | PART BUILT: five weapons (the hunting crossbow; the pneumatic bolt driver, stun baton, moth jelly dart and propane flamethrower from sessions 19 to 22, solo only), the two-weapon carry cap, and the Q/E slots with the three consumables. Not built: the rocket launcher, laser dissector, rebar shear, frequency horn and gravity gauntlet (rules proposed in `docs/ITEMS.md`). | `shared/crossbow.test.js`, `shared/driver.test.js`, `shared/baton.test.js`, `shared/dart.test.js`, `shared/flame.test.js`, `shared/loadout.test.js`, `shared/consumables.test.js`, `tools/gbi2_test.mjs`, `tools/gbi3_test.mjs`, `tools/driver_test.mjs`, `tools/baton_test.mjs`, `tools/dart_test.mjs`, `tools/flame_test.mjs` |
> | GBI-9 | Money comes from clearing chambers and from kills and revives. Level comes from achievements. Money and items are shared with the rest of the game. Progress is its own save. | NEW | |
> | GBI-10 | Per-run score goes to an online leaderboard, with personal and overall bests. | NEW | `docs/BACKEND.md` |
> | GBI-11 | The 20 waves stay 20 when floors are added, by sampling. | NEW | |
>
> ### Session 8 plan: Going back in, in slices (solo only)
>
> | Slice | GBI items | Status |
> |---|---|---|
> | 1 | GBI-1 (the mode names its first chamber), GBI-2 (two chambers as manifest scenes, stairs down between them), GBI-3 (the wave starts on entry) | BUILT, solo only: `tools/gbi_test.mjs`, `shared/gbi.test.js` |
> | 2 | GBI-7 (the loadout locker), GBI-8 for one weapon: the hunting crossbow with its own ammo rule | BUILT, solo only: `shared/crossbow.test.js`, `shared/loadout.test.js`, `tools/gbi2_test.mjs`. The Q/E consumable slots are NOT built (they still say empty) |
> | 3 | GBI-8's consumable slots: Q and E, with the flash-vial, the land mine and the tripwire | BUILT, solo only: `shared/consumables.test.js`, `tools/gbi3_test.mjs` |
> | 4 | GBI-8: the pneumatic bolt driver (`docs/ITEMS.md` 4.1), the first weapon that hurts instead of killing: monsters get health (`hp` in `world/monsters.json`, `MonsterSim.hurt`) | BUILT, solo only: `shared/driver.test.js`, `shared/monsters.test.js`, `tools/driver_test.mjs`. Key 5 holds it; the locker panel has a fourth gear row, so the E slot's key moved from 4 to 5 |
> | 5 | GBI-8: the stun baton (`docs/ITEMS.md` 4.4), and the arsenal's two-weapon carry cap with weapon slots on keys 4 and 5 | BUILT, solo only: `shared/baton.test.js`, `shared/loadout.test.js`, `tools/baton_test.mjs`. The baton starts in the locker (you carry two arsenal weapons at most); the locker's E-slot key is now 6 |
> | 6 | GBI-8: the moth jelly dart (`docs/ITEMS.md` 4.9) and the Slowed and Jellied statuses | BUILT, solo only: `shared/dart.test.js`, `shared/monsters.test.js`, `tools/dart_test.mjs`. It starts in the locker with the baton (two weapons at most); the locker's E-slot key is now 7 |
> | 7 | GBI-8: the propane flamethrower (`docs/ITEMS.md` 4.3) and the Burning status | BUILT, solo only: `shared/flame.test.js`, `shared/monsters.test.js`, `tools/flame_test.mjs`. It starts in the locker (two weapons at most); the locker's E-slot key is now 8 |
> | 8 | GBI-8: the frequency horn (`docs/ITEMS.md` 4.8) and the knockback and `shove` it needs | BUILT, solo only: `shared/horn.test.js`, `shared/cone.test.js`, `tools/horn_test.mjs`. It starts in the locker (two weapons at most); the locker's E-slot key is now 9 |
> | 9 | GBI-8: the almond water rocket launcher (`docs/ITEMS.md` 4.5) and `shared/flight.js`, the projectile shared with the dart | BUILT, solo only: `shared/rocket.test.js`, `tools/rocket_test.mjs`. It starts in the locker with one rocket (two weapons at most); the locker's E-slot key is now 0 (the tenth row) |
> | 10 | GBI-8: the laser pointer dissector (`docs/ITEMS.md` 4.6) | BUILT, solo only: `shared/laser.test.js`, `tools/laser_test.mjs`. It starts in the locker (two weapons at most); the locker's E-slot swap is now the E key |
> | 11 | GBI-8: the hydraulic rebar shear (`docs/ITEMS.md` 4.7, the owner's design: four fresh cuts, then worn) and GBI-5's barricades | BUILT, solo only: `shared/shear.test.js`, `shared/barricade.test.js`, `tools/shear_test.mjs`. It starts in the locker (two weapons at most); it is the eleventh locker row, which has no number key (click it) |
> | left | GBI-8's last weapon (the gravity gauntlet), GBI-4 hazards, GBI-5 vents and the other barricades, GBI-6 safe house, GBI-9 to GBI-11, and rooms running the mode (the server still answers `{t:"refused",reason:"soon"}`) | NEW |
>
> What slice 1 does: from the Overworld's store-doors options screen, "Going back in" loads `gbi_L4_4` (the 4th chamber of L4, which is the L4 model with the store sealed) as wave 4 of 20, and the wave (3 monsters, 16 m or more from you) starts as you land. Its stairs-down door leads to `gbi_L3_1` (the L3 model; wave 5, its own 3 monsters). That chamber's way down and the 14 other chambers are not built. The chamber's wave number is its floor's place in the mode times four plus its index. The stairs are open from the start: there are no clear rules yet (objects, puzzles, kill count, timer), so "cleared" is not checked. Death is the solo rule (respawn at a random spot in the same chamber).
>
> What a room needed to run the mode is done (session 16, below): the chamber scenes are `multiplayer` scenes the server's floor sims run, the server starts each wave, the mode's `status` is `built`, and the lobby's "GOING BACK IN" button is enabled.
>
> ### Session 16: Going back in in a room
>
> A room joined with mode `going_back_in` (party key `going_back_in:CODE`, up to 10) starts everyone together in the mode's `startChamber`. The round has no end yet (no finish, no run record, no score): it lasts until the room empties.
>
> | Slice | What | Status |
> |---|---|---|
> | 1 | The server runs each chamber as a floor (`server/floorsim.js`, `chamber`). The wave (`shared/gbi.js`, the same plan as alone) starts once, when the first player steps in, at least 16 m from them; everyone in the chamber is told its monsters (`wave`: each as `[wid, x, z]`), and follows the same snapshots. A chamber is kept for the life of the room and stands still while nobody is in it. The stairs-down door leads to the next chamber. | BUILT: `server/gbi.test.js` (ten clients, one wave), `tools/gbi_mp_test.mjs` (two pages) |
> | 2 | The server owns the crossbow (`bolt`: bolts, the reload, the kill), each kill is for the life of the room (`kill`, by `wid`), the wave is cleared when all its monsters are dead, and the locker's loadout is each player's own (`gear`; the `me` message carries `carry` and `bolts`). | BUILT: the same two files |
> | 3 | The Q and E consumables: the server counts them (`me.kit`), a flash-vial stuns where it lands (`use` slot 0, `flash`), a land mine or a tripwire is set where the server has you, shown to everyone (`trap`), and goes off on the server (`sprung`, then `kill`). The E slot's choice is made at the locker (`gear` with `a: "e"`). | BUILT: the same two files |
>
> What the server owns in a room: where the wave starts and its monsters, health, the ray's rounds, the bolts, the loadout, the consumables, kills, traps and the cleared flag. What stays on the page: drawing, the locker's place (seeded from the scene, so the same for everyone; the server does not check you stand at it, as it does not for ammo packs), the first guess of a bolt's beam, and where a flash-vial lands (the server only checks it is within the throw).
>
> Death in a room: you are downed first and a teammate can lift you (nothing is lost). If nobody does within the down time, that is a death: you get up at a random spot in the same chamber, your gear is in the locker, and your rounds, bolts, beacons and consumables are gone (`docs/WORLD.md`, "Death in Going back in").
>
> Not built: waves that scale with the party (every wave is the manifest's count, 3; a suggestion is in the PR), a finish, score and run record for the mode, the 18 other chambers, the Market and safe houses.
>
> **Slice 2 rules (defaults the owner may change).**
> - *Crossbow:* its own ammo, bolts, not rounds. One per shot, at most 6 carried, 4 at the start (the Market does not exist, so the crossbow starts in your hands), +2 from each ammo pack you pick up while you carry it, 1.8 s reload between shots. A bolt that hits kills the monster for good (the ray still only banishes). A shot makes half the ray's noise. Key 4 holds it.
> - *Locker:* one per chamber, placed like a pack, opened with the action button (X / E). A panel lists the ray, the cloak and the crossbow: carry one or leave it in the locker (keys 1 to 3, a click, or D-pad and A). The game pauses while it is open.
> - *Death:* all your gear goes to the locker, and ray rounds, bolts and beacons are gone. Walk to a locker and take the gear back for free; the ammo does not come back. A beacon is counted as charges, so it is lost like ammo (the doc lists it as gear; say if you want the device kept).
> - *Kills:* a kill is counted, and killing every monster of the wave clears it (toast). That is the only clear rule so far.
> - *Name:* the panel and the code call it "the locker" and "the loadout locker". The open question (Decision 2) stands.
>
> **Slice 3 rules (defaults the owner may change).** The doc names the three consumables but not which slot holds what, nor their numbers.
> - *Q (support): the phosphor-core flash-vial.* Thrown up to 6 m ahead (it stops at a wall); every monster within 6 m of where it lands is stunned for 6 s. It kills nothing. Max 3, start 2.
> - *E (combat / objective): the almond water land mine or the nail-bomb tripwire, chosen at the locker (key 4, or the E row with D-pad and A).* The mine is set down where you stand, arms after 1.5 s, and kills the one monster that comes within 1.2 m. Max 3, start 2. The tripwire arms after 0.5 s; a monster within 2 m sets it off and every monster within 3 m dies; the blast is loud, so monsters within 25 m go and look. Max 2, start 1. Both count as kills toward the wave. A trap is yours to walk into too: nothing here hurts the player (monsters are the only target in v1).
> - *Refills:* each ammo pack adds one flash-vial and one of the E item, up to the cap. The Market does not exist yet, so there is no other source.
> - *Death:* all consumables are gone and the locker does not return them (docs/WORLD.md). Traps already set stay until a monster springs them, and are cleared when you change chamber.
> - *Controls:* Q and RB-side E are as `docs/GAMEPLAY.md` says (LB / Q support, RB / E combat). `tools/controls_test.mjs` still passes. In the Original the slots stay empty.
>
> ## D. Co-op inside the games (design note, session 11)
>
> Status: **design only, no code yet.** Written first, as `docs/SESSIONS.md` asks, so the owner can change a default before it is built. Everything marked *Default* is what the build will do unless told otherwise.
>
> **What exists.** A room is a party of up to 10 (RND-12). A player's place is separate from the party. Since session 17 a place can be a *presence scene*: the server relays position snapshots between the players whose `scene` string is the same and runs no rules there (`presencePlace`, `presenceSnap` in `server/server.js`; `REGISTRY.presence` and `REGISTRY.canReach` in `shared/registry.js`). The two games are solo only today: `soloOnly` on their gate links, and the page refuses the door in a room. Each game draws itself in its own renderer, hidden behind the page's: Right Door, Wrong Exit (`games/rdwe/walk.js`, a chain of rooms walked one after another, `enterGame` can start the chain at any room) and the Intern (`games/intern/`, an iframe with its own three.js, nine spine stages S0 to S8).
>
> **The idea.** A game room is just one more presence scene. Nothing about the game's own rules moves to the server.
>
> 1. **A place inside a game.** `rdwe:<room>` (`rdwe:dining`, `rdwe:teal`, ...) and `intern:<stage>` (`intern:S3`). The manifest lists them as the `places` of the game's area, each with `presence: true`; `REGISTRY.canReach` reaches a game place through the gate link (once its `soloOnly` is dropped) and, from there, any place of the same game. The server accepts a player's place only if `canReach` says so, as it does for the parking lot.
> 2. **One instance per party, game and place.** The party is the room, so the instance is "this room's players whose place is `rdwe:teal`". The server already broadcasts a snapshot only to players with the same place string, so two players in `rdwe:teal` see each other and a third in `rdwe:hallway` does not. No instance object is created or destroyed.
> 3. **Who is in it.** Whoever's place string matches. A player may enter alone (nobody else is in the place) or with friends (they walk through the gate, or "go to a friend" in a game: `goto` returns the friend's place and the page calls `enterGame` at that room). Friends can arrive and leave at any time, because arriving is changing a place string.
> 4. **What is shared.** Presence and positions only: where each player is, which way they face, crouching, moving. Each player's puzzles, pickups, ending and progress through the chain stay their own page's state. *Default for version 1, as in session 11's brief.* Shared puzzle state comes later and is a separate decision per game.
> 5. **Leaving.** A player who finishes or quits a game goes back to L4 at the gate's arrival point (the fix of session 2); their place changes to `L4`, and the others in the game see them vanish. Nothing in the others' game ends, because nothing else was shared. A player who disconnects is removed from their place as for any floor.
> 6. **How the others are drawn.** Each game draws other players in its own scene, not the page's:
>    - Right Door, Wrong Exit: the page hands `walk.start` a list of peers (position, yaw, colour) that it updates from the room's snapshots, and the walk draws a plain figure for each in the walker's scale (`RDWE_SCALE`, so a player is the same size to everyone). Its own position goes out through the page's existing state message, with the game's place as the `scene`.
>    - The Intern: the page and the iframe talk by `postMessage`, as they already do for `intern-ending`. The page posts peers into the iframe and the iframe posts its player's position out; the iframe draws figures in its own scene (scaled by `INTERN_SCALE`).
> 7. **Soundless and harmless.** Other players are shown but have no collision, cannot touch or hurt anyone and make no game-affecting noise. *Default.* (Footsteps heard in the Intern's drone would change a game built around silence; revisit with the owner.)
> 8. **The round outside.** A player inside a game is not on a floor, so the Original's finish must decide what to do with them. *Default:* a player in a game does not block the round: the finish waits for the players on floors, and a player still inside a game when it ends is not ranked, and gets the results on their return. Alternative, if the owner prefers: they count as present and the round waits. Chosen so that one player in a long game cannot hold a room hostage.
> 9. **Room size and the server.** The 10 cap, name tags, colours and the message budget are the room's, unchanged. Presence snapshots are sent at the page's usual state rate. The server holds no game state, so there is nothing new to measure for the tick.
> 10. **`soloOnly`.** The manifest flag is dropped per game only when that game's slice below passes its test. The page already reads the flag (session 2), and the manifest check already requires a built link that a room can follow to end in `multiplayer` or `presence` scenes.
>
> **Order of work** (each slice its own commit, tested):
> 1. This note.
> 2. Server and manifest: game places as presence scenes, `canReach` and `goto` through them, tests. `soloOnly` stays.
> 3. Right Door, Wrong Exit in a room: peers drawn in its scene; `tools/games_party_test.mjs` has two clients enter the game separately, meet in one place, and leave without breaking the other's game. Then drop `soloOnly` on its gate.
> 4. The Intern: the postMessage bridge and the same test. Then drop its `soloOnly`.
>
> **Not in this session.** Shared puzzle state, shared endings, voice or text between players in a game, games reached from the Overworld's forest or the city (their links stay planned), and the City's job shifts, which stay solo.
>
> **Questions for the owner** (each has the default above): (a) are other players audible in the Intern, or only visible; (b) does a player inside a game block the round's finish; (c) should a player be able to jump into a friend's *Intern* stage, or only to Right Door, Wrong Exit rooms (the Intern's stages build on each other's state).
>
> ## Decisions
>
> Settled:
> - Room size is 10.
> - Co-op inside the games is optional, and friends can pop in at any time, so a party of 10 can split across levels and games (RND-12, RND-15).
> - A death is a down nobody revived. Revives are counted and add to the total score (RND-20, RND-27).
> - Backend: PostgreSQL on Railway (Hobby now, Pro when needed). Players start anonymous and can sign in with Discord. The audience is 18 and over. Email sign-in and marketing email come later. See `docs/BACKEND.md`.
>
> Still open:
> 1. **Score formula and what ranks the board.** The RND-27 formula is a placeholder. A board can rank by time, by score, or have one of each.
> 2. **Name for the Going back in locker**, since the existing locker is a one-time pickup.
>

### Source file: docs/GAMEPLAY.md

> # Gameplay plan
>
> A co-op round for 2–10 players (the room size is `modes.original.players.max` in the world manifest): climb the building together (B1 → L1 → L2 → L3 → L4) and get out. About 20 minutes.
> Status: **built** = in the game and covered by `tools/mp_test.mjs` / `server/server.test.js`; **planned** = not built.
> The numbers are starting points, not tuned.
>
> ## The round
>
> | Stage | Floor | Time | Notes |
> |---|---|---|---|
> | Ready-up | lobby | 1 min | **built.** Pick a character, ready up, a short countdown, the group spawns together on B1. Someone joining mid-round skips the lobby. |
> | 1 | B1 pools | ~4 min | Sinew of the Abyss. The teaching floor. |
> | 2 | L1 offices | ~5 min | The Pale Traveler. 127 doors, so doors matter. |
> | 3 | L2 | ~5 min | The clawed creature. The biggest floor. |
> | 4 | L3 white room | ~1 min | No monsters. Checkpoint: everyone regroups. |
> | 5 | L4 showroom + lot | ~4 min | The first creature. Alarm hunt at the end. |
>
> ## Surviving
>
> - **Crouch** halves how far monsters see you and makes no noise, but you move at 2.2 against their 5.4–5.5 chase speed: you cannot outrun one, so you hide and use doors. (built; original)
> - **Close doors** (built): X / E on an open door shuts it, unless someone is standing in it. Monsters open doors (0.5 s each) but never shut them; stair doors never shut. A door you shut is shut for everyone.
> - **Downed, not dead** (built): in a room, a caught player drops where they fell and everyone else on the floor gets a scream arrow toward the body. A teammate holds E / X beside them for 4 s to lift them (and gets 4 s of safety afterwards). Unrevived after 45 s, you wake at the stairs you came up. Solo play keeps the old rule: die, wait 3 s, respawn somewhere random.
> - **Floors are private** (built): you only learn that someone is on another floor, never where.
> - **Monster count scales** (planned): 3 per floor for 1–2 players, 4 for 3–5, 5 for 6–8.
> - **Floor reset** (planned): if everyone on a floor is down at once, its fuses reset and you restart at the stairs.
>
> ## Progress: one puzzle per floor
>
> The stair door at the top of each floor stays locked until that floor's puzzle is solved. The order the owner chose:
>
> | Floor | Puzzle | Status |
> |---|---|---|
> | B1 | **Fuses:** 3 lie around the floor; carry them one at a time to the stair door | **built** |
> | L1 | **Switches:** two far-apart switches, flipped one at a time in any order; each flip is loud and draws nearby monsters to look | **built** |
> | L2 | **Keypad:** a 4-digit code, each digit on a note found at a different place, shared by the team | **built** |
> | L3 | Break floor, no monsters. A **fuse box** here is an optional shortcut that powers L4's doors early | **built** |
> | L4 | **The trick:** the store's glass doors are shut unless the power is on; the L3 box turns it on early, otherwise the power switch is on the far side of the room, with the monsters | **built** |
>
> ### Fuses (built)
> - Three fuses per gated floor, in the same places for everyone (seeded, in the floor's main walkable area, away from the door and from where monsters start). Press E / X within 1.5 m to pick one up; E / X at the door puts it in. One carried at a time. Three lamps above the door go from red to green.
> - Priority of E / X: lift a downed teammate, then pick up a fuse, then the door.
> - A carrier is easier to find: monsters hear a carrier walking or running 1.5x as far, and a crouching carrier is no longer silent (heard at 0.4x the hearing range) and is seen from 0.75x instead of 0.5x. Other players see a glow round a carrier.
> - A downed carrier drops the fuse where they fell. A carrier who leaves the floor or the room puts it back where it started. A powered door stays powered.
> - State is held by the server per room (`shared/fuses.js` is the one rule set, used by the server and by solo play); a late joiner sees the current state.
> - The art is the owner's Meshy model, `models/fuse.glb` (a glass cartridge fuse with brass-grey end caps, 2,096 triangles, scaled to 0.4 m); the code-made cylinder stays as the fallback if the file cannot load.
>
> ### Switches (built)
> - Two switch posts stand at least 14 m apart (usually 25+), in the same places for everyone (seeded, like the fuses). Press E / X within 1.6 m to flip one. They are flipped one at a time, by anyone, in any order, and stay flipped; both on powers the stair door. The lamps over the door and the HUD (`SWITCHES 1/2`) show progress.
> - A flip is loud: every monster on the floor within 40 m goes to look at the switch (unless it is already chasing someone). The server runs the monsters, so this works the same in a room and solo.
> - A player arriving on the floor later sees which switches are already on. State is held by the server per room (`shared/switches.js` is the one rule set).
> - Placeholder art in code; an optional `models/switch.glb` replaces it (see `docs/MODELS.md`).
>
> ### Keypad (built)
> - Four notes stand at least 8 m apart (usually 15+), in the same places for everyone. Note *i* holds digit *i* of the code. Press E / X within 1.5 m to read one: that digit is shown to the whole team (a toast, the `CODE _ 2 _ 3` line in the HUD, and the "Notes found" line on the keypad). A note is read once.
> - Press E / X at the locked door to open the keypad: type the digits with the number keys, Backspace, Enter (or click the buttons); Esc or E closes it. You cannot move while it is open. The code is made by the server when the room first reaches the floor and never leaves it: clients only ever receive the digits that were found. Solo play keeps the code in the game.
> - A wrong code is loud and locks the keypad for 8 s for everyone: every monster within 40 m of the door goes to look. Typing during the lock does nothing. Malformed input (not 4 digits) is ignored, not counted.
> - A late joiner sees which notes were already read. Rules: `shared/keypad.js`.
> - The notes and the door panel are drawn in code; `keypad` in `docs/MODELS.md` is not wired to a model yet.
>
> ### Power: the L3 box and the L4 trick (built)
> - The room has one power flag (`shared/power.js`). It starts off and is thrown **once**, by anyone, and stays on. Two places can throw it: the **power box on L3** (the prop that is already in the Blender file, at the south wall, with a lever and lamp added) and a **power switch on L4** in the far north-west alcove of the store, about 49 m from where the stairs bring you in.
> - **Off:** the store's glass entrance is shut, and the model has no collider there, so a collider is added across the 5.4 m opening; monsters cannot pass either. **On:** the glass rolls up out of the opening, the collider goes, and the monsters' walkable map is rebuilt so they can use the way out too.
> - The L3 box is silent (no monsters on L3), so it is the quick, safe way. The L4 switch is loud: every monster within 40 m goes to look at it, the same as the L1 switches.
> - Everyone in the room hears of it wherever they are: a toast, `POWER ON` in the HUD, and the doors are already open when you arrive. A late joiner is told in the welcome message. L3 to L4 stairs are never locked.
> - The L4 switch is a placeholder in code (the L3 box is the real model). The finale is below.
>
> ### Finale: the alarm, the way out, the parking lot (built)
> - **The alarm** goes off once the L4 doors are open and someone is in the store: if the L4 switch is thrown, at once; if the quiet L3 box was used, when the first player arrives. It lasts 60 s (`ALARM 0:41` in the HUD, a red pulse at the screen edge). While it runs, every L4 monster heads for the doors every 2 s, unless it is already chasing someone. A late joiner is told how much of it is left.
> - **The way out:** walking out of the store onto the parking lot (past z 28.8 between the doors) is your finish. The lot is safe: it is off the monsters' map, and a player who is out is not a target. You can walk back in to help a teammate; your place stays.
> - **The round ends when everyone still in the room is out.** Someone who leaves the room does not hold it up. Then everyone sees the results: place (the order they left), time (from the start of the round), and the best time on this browser (`BEST` or `NEW RECORD`). Solo ends the moment you walk out.
> - Rules: `shared/finish.js`; the server keeps the run and the alarm (`exit` is accepted only from L4 with the power on).
> - Not done: a siren sound (now built: docs/AUDIO.md); the best record is per browser, not shared; the 60 s and the hunt are untuned.
>
> ## Movement, sight and hearing
>
> - **You:** walk 4 m/s (quiet), hold R (press in the left stick on a controller) to run at 7.5 m/s (loud) for about 4 s, then a short recovery (the bar under the screen, back to 30% before you can run again), crouch (Shift; B or a push of the right stick on a controller) at 2.2 m/s (silent). A monster chases at 5.4 to 5.7 m/s, so running pulls away from one and walking does not.
> - **They see** up to 16 m in a 110 degree view and need a clear line (8 m if you crouch). A monster that has seen you runs to the spot where it last saw you, not to where you are now, and gives up 2.5 s after losing sight (or on arriving), then searches that spot for 6 s.
> - **They hear** by what you are doing: running at the full range (9 m), walking at half (4.5 m), crouching not at all (a crouching carrier at 0.4x). A wall between you halves it. Hearing sends a monster to look, at its searching pace, never straight into a chase; only seeing you starts a chase.
> - The numbers are `NOISE_WALK`, `NOISE_CARRY_CROUCH`, `NOISE_WALL`, `CHASE_LOSE_S`, `SEARCH_S` above `class Monster`, and `WALK_SPEED`, `RUN_SPEED`, `RUN_S`, `RECOVER_S` by the player, in `index.html`. All untuned until the bots and real players have used them.
>
> ## Roles that emerge (built)
>
> No assigned classes. **Monsters show on the handheld map only through the cameras** (built): every security camera on the floor sweeps on its loop, and a monster inside a camera's view (within 40 m, not behind a wall) is marked on everyone's map with pulsing rings; the mark stays at its last seen spot and fades over 3 s. A floor's blind spots are the places no camera reaches. Nobody has to hold a feed open, but the map is only as good as the sweep, so a player who watches the feeds can tell the team what the map cannot. Each client runs the cameras on its own clock, so two players' sweeps can be a few seconds out of step. Scouts, carriers and revivers come from the fuse and revive rules.
>
> ## Build order
>
> 1. Ready-up lobby, group spawn, floor-only position relay: **built**
> 2. Downed and revive, scream arrow: **built**
> 3. Close doors: **built**
> 4. Fuses and the gated stair door: **built** (B1). Switches on L1, the keypad on L2, and the L3 box / L4 power trick: **built**. The finale and score (7) are built too. The next steps are server-side monsters (6) and bots (8).
> 5. Monsters on the map only through cameras: **built**
> 6. Monster simulation on the server: **built** (`server/floorsim.js`, rules shared with the page in `shared/world.js` and `shared/monsters.js`). There is no host any more: every client follows the server's snapshots.
> 7. Finale alarm and scoring: **built**
> 8. Bot players to tune the numbers: **first version built** (`tools/bots.mjs`, see below)
>
> ## Characters
>
> Five playable characters (`characters/<id>.glb`, picked in the lobby, shown to everyone else with name tags): `plaid`, `suit`, `shorts`, `red`, `white`. Duplicates are allowed. Each has Walking and Running clips; standing still plays the walk almost frozen (no idle clip), crouching walks slowly, being downed lies the model down. `tools/optimize_character.mjs` produced them from the Meshy exports (1024 px WebP texture, ~30–76k vertices, Draco; about 0.5–0.7 MB each).
>
> ## Fighting back: the Error Deletion Ray (built)
>
> The gun is `models/gun.glb` (Meshy's "Error Deletion Ray", 10k triangles). It is in the game (`GUN` in `index.html`): held bottom right, fired with the left mouse button, F or the right trigger; teammates are seen holding it. The section below is the plan it was built from. These are the owner's decisions and the rules built from them; anything marked *assumed* is mine and open to change.
>
> **Decisions (owner).**
> - A hit **does not kill: it no-clips the monster to another place on the map** (the ray deletes it from where it stands and it reappears elsewhere).
> - Ammo is **scarce and found on every floor**.
> - **One gun per player, found on B1** (lockers in the opening).
> - A shot is **as quiet as running** (heard at 9 m, halved through a wall), not an alarm.
>
> **The shot.** Aim with the camera; fire with the left mouse button or `F` (controller: the right trigger; run and crouch moved to the stick clicks). Hitscan: a ray from the camera, 25 m long, blocked by walls and shut doors (the same `segClear` test the monsters' sight uses), hitting a monster inside a 0.6 m radius, 2.2 m tall capsule. One shot every 0.6 s. No reload: the rounds you carry are your magazine. You cannot fire while carrying a fuse (your hands are full: drop it first), while crouching-and-reviving, or while downed.
>
> **What a hit does (assumed details).** The monster glitches for 0.5 s (a flicker and a cyan scanline), then is placed at a spot on its own floor that is at least 35 m away by path from every player, out of every player's sight and at least 15 m from any player; it forgets its chase, waits 4 s, and goes back to patrolling. It cannot be banished again for 8 s. The spot is random among those, so the ray can land a monster near an objective: it relieves a chase, it does not clear a floor. Other monsters are not affected; a monster that was chasing someone else keeps chasing.
>
> **Ammo (assumed numbers).** A gun starts with 3 rounds; an ammo pack holds 3; you carry at most 9. B1 has 8 lockers (one gun each, taken once by whoever opens it, a player holds one) plus 3 packs; L1, L2 and L4 have 3 packs each; L3 (no monsters) has 4, as the place to restock before the finale. Packs sit at seeded spots in the floor's main walkable area (like the fuses and notes), the same for everyone, and are taken once for the whole room. Rounds are never shared between players except by dropping: a downed player keeps their gun and rounds.
>
> **What it changes.**
> - *The game's premise:* monsters were unbeatable and the answer was hiding. Now there is a way out of a chase, but a scarce one: three rounds is about one escape per player per floor. Expect the 8 to 11 downs per bot on B1 to fall a lot; the bots (below) are how to check.
> - *Roles:* the bait stops being a sacrifice, since a hit sends the lure's monster away; the scout can clear the stairs; the runner can shoot a monster off a fuse.
> - *Noise:* a shot is not an alarm (it is a run), so shooting a monster that is watching you does not call the others, but two monsters near each other will still hear it at 9 m.
> - *Cameras and the map:* a banished monster only shows on the map if a camera sees where it lands.
> - *The finale:* the 60 s alarm sends every L4 monster to the doors; the rounds saved for L4 (3 packs and what is left from L3) decide whether the last run is a rush or a fight.
> - *Scoring:* worth adding later: shots fired and hit, and rounds left at the exit.
> - *Tuning to revisit once it exists:* the monsters' chase speed against the run speed, the 45 s down time, the sight range, how many monsters B1 needs.
>
> **How it is built (the architecture).**
> - `shared/loot.js` (pure, with tests): lockers and ammo packs per floor, taken once; the same rules in the server and in solo play, like `shared/fuses.js`.
> - Server: relays loot state to the floor (late joiners get it on arrival), checks a `shot` (the ray must start near the shooter, and the server takes the round) and resolves it on its own monsters. A banish is a position jump in the snapshot (clients snap a monster that moves more than 8 m) plus a `zap` message so every client plays the effect.
> - Client: the held gun (scaled to about 0.55 m, bottom right, a short recoil kick and a cyan flash from the tip), a small cross-hair, a round counter, lockers drawn in code, ammo packs drawn with the owner's Meshy model (`models/ammo_pack.glb`, an upright case 0.4 m tall; the code-made box stays if it cannot load), and the other players seen holding it.
> - Monster: a `banish(spot)` method and the placement rule above.
> - Bots: a bot with rounds fires at a chasing monster that is within 12 m, in sight, when its escape margin is under 2 s, and the bait uses it to pull a monster off the runner's way. Then rerun `tools/bots.mjs` and compare downs per floor with and without the gun: the first real test of the idea.
>
> **Build order.** 1. `shared/loot.js`, the server relay, lockers and packs: **built** (below). 2. The held gun, firing, hit and banish: **built** (below). 3. The bots' use of it and the comparison run: **built**; first result below (the gun cuts downs by about a third and does not by itself let a team finish B1). 4. Tuning, then scoring.
>
> **Settled (owner).** "Another location" means far away and out of sight (at least 35 m by path from every player, out of every player's view, at least 15 m from any player), as written above, not a fixed set of spots. The banished monster visibly flickers out and in (a 0.5 s glitch and cyan scanline). *Still open:* friendly fire is assumed off.
>
> **Step 1, built: lockers and ammo packs.** B1 has 8 lockers and 3 packs; L1, L2 and L4 have 3 packs each and L3 has 4 (the numbers above). They stand at seeded spots in the floor's main walkable area, the same for everyone (lockers at least 6 m apart where the floor allows, packs 10 m). Press E (or X on the controller) within 1.5 m: a locker gives you the gun with 3 rounds (once per player: a second locker is refused while you carry one), a pack adds 3 rounds (refused at 9). A locker or pack is taken once for the whole room, and a late joiner sees what is gone; a player who leaves puts their locker back, so a room can always arm everyone. The rounds show bottom right as `RAY ● ● ● 3/9`. Rules: `shared/loot.js`; the server keeps the state per floor and checks every pickup. The gun itself cannot be fired or seen yet (step 2). Solo play uses the same rules locally.
>
> **Step 2, built: the gun in your hand.** Once you have a gun it is held bottom right (the Meshy model, scaled to about 0.55 m, with a short kick and a cyan flash when it fires). Fire with the left mouse button (once the mouse is captured), `F`, or the controller's right bumper (the cameras keep LB and D-pad right). One shot every 0.6 s, each costs a round. You cannot fire with a fuse in your hands, with the map or camera device out, while downed, or at the end screen; with no rounds it clicks ("Out of rounds").
> - *The ray:* from your eye along the aim, 25 m long, stopped by walls and shut doors; a monster is hit if the ray passes within 0.6 m of any of three points up its body. A thin cyan beam is drawn to where the ray ended, for you and for everyone on the floor.
> - *A hit:* the server decides it (in solo, the page does). The monster is deleted: it flickers for 0.5 s while it does nothing, then stands at a spot on its floor that is at least 15 m from every player, out of every player's sight, and (where the floor allows) at least 35 m away by path; it forgets the chase, waits 4 s and patrols again. It cannot be banished again for 8 s: a shot at it in that time is a wasted round. Everyone sees the glitch at both places (a cyan flash) because the host announces it (`zap`).
> - *Noise:* a shot is heard as a run (9 m, halved through a wall) for half a second, even if you are crouching: the shooter counts as running for the monsters' hearing.
> - *In a room:* the shooter sends a `shot` intent; the server validates it, counts the round (clients cannot give themselves rounds), decides the hit and sends everyone the beam and the `zap`.
> - Other players are seen holding the ray gun; the bots use it; sound is built (docs/AUDIO.md).
>
> ## Bots for tuning
>
> `node tools/bots.mjs [bots=3] [--timeout=600] [--deaths] [--trail] [--debug]` runs N real game clients (headless browsers, `?bot=1`, the game's own code, no drawing) in one room on a local server and prints a report: time on each floor, downs, revives, stuck moments, seconds fleeing and waiting, tick rate, and each bot's place, time and the alarm left when it got out. Run it locally; it is slow in software rendering. The bots' mind is `tools/bot_brain.mjs`.
>
> **How they think.** Everything runs on the game's own walkable grid.
> - *Arrival times.* Dijkstra distance fields from the bot and from every monster on the floor. The bot covers a distance in `tb(d)` (running while its stamina bar lasts, then walking); a monster in `d / chase speed`. The **margin** of a cell is the least, over the monsters, of (monster time to the cell minus bot time to the cell): positive means the bot gets there first by that many seconds.
> - *Safe route.* The cheapest path that keeps out of every monster's sight ring (16 m, 8 m if crouching) and uses only cells with a margin of at least 2 s; the margin and the ring are relaxed in steps (2 s and 60% of the ring, 1 s, 0 s, then anything). If only a risky route is open, the bot waits still and quiet (crouched) while its spot is safe, up to 25 s, as a patrol passes.
> - *Flee.* From the reachable cells with a margin of at least half a second it picks the best-scored one that every chaser's line of sight misses (and, for the bait, that is far from the runner), preferring open space over dead ends, runs there, then crouches and keeps still for 6 s.
> - *Team* (the runner process relays a blackboard of every bot's position, role and claim every 0.4 s): the **runner** fetches what the floor needs (fuses, switches, notes) and claims one item so two bots do not go for the same; the **bait** goes to a visible spot 9 to 13 m from the monster that threatens the runner most and draws it off (and flees away from the runner); the **scout** waits at a safe spot near the stairs, types the code on L2 and throws the L3 power. With no runner left on a floor the others do the runner's work, and anyone lifts a downed teammate when the way is safe.
>
> **What the runs showed (3 bots, B1, 600 s each).** Nobody got off B1 in any of them. Downs per bot: plain bots 8 to 11 (and about the same with the new monster rules: they run straight at monsters and away in a straight line); team bots with margins and hiding 8 to 10; with the patient waiting and open-space fleeing 6, 6 and 8. A bot is down for 45 s each time, so six downs is most of a round, and a third of the rest was spent waiting for patrols. The harness is sound: the tick rate is a steady 50 ms with no stalls, and the measured speeds are exactly walk 4, run 7.5 and crouch 2.2 m/s.
>
> **The gun, with and without (step 3).** The bots now arm themselves (each opens a locker on B1, claiming one so two bots do not go for the same), pick up an ammo pack that is within about 22 m by path when they are down to 5 rounds or fewer, and fire at a chasing monster that has come within 13 m, aimed at its body, only when the ray would hit it (not through a wall, not at a monster that is still immune or glitching), while they keep fleeing. `node tools/bots.mjs 3 --nogun` is the control: the same team that never arms. Two pairs of 600 s rounds, 3 bots on B1 each (downs per bot, bait and scout and runner in that order of the log):
>
> | | gun | no gun |
> |---|---|---|
> | run 1 | 4, 6, 5 (15) | 9, 6, 8 (23) |
> | run 2 | 2, 7, 7 (16) | 7, 8, 9 (24) |
>
> - *The gun roughly cuts downs by a third* (31 against 47 over the four runs): 12 and 12 shots, every one a hit, every round spent (3 rounds each plus packs; each bot ended with none), so the three starting rounds are used up well inside the 10 minutes. Armed times were slow in the second pair (26, 67 and 74 s) because the lockers are spread out.
> - *It did not let anyone finish B1.* Fuses in the door: 0 of 3 in all four runs, with or without guns. Downs are only part of the cost: a bot downed 7 times is out for 7 x 45 s = about 5 of the 10 minutes, the team also waits for patrols (about 150 s each for the runner and the bait) and crosses about 80 m to the fuses.
> - *Run to run the spread is large* (a bot's downs ranged 2 to 9), so one pair of runs shows a direction, not a measurement.
> - *What to try next, in order:* a short down time (45 s is long for a bot team and probably for people), ammo for the whole trip (more packs or more rounds per pack on B1), and a spawn nearer the fuses or fuses nearer the spawn. The bots can run each of these changes in about 10 minutes.
>
> **What it says about the floor.** The room spawn on B1 is at the far east (about x 14, z -22) and the fuses are in the west, so a team has to cross the whole floor, about 80 m of path, through the corridor near x 0 to 9, z -10 to -15 where nearly every death happened, and where the monsters from (24, -8), (3, 6) and (-7, -1) all patrol. Dying twice within 0.2 m of the same spot says the route, not the bot, is the problem. Before blaming the bots, consider: moving the spawn nearer the fuses (or the fuses nearer the spawn), thinning B1's four monsters, and giving that corridor a way round.
>
> **Not done:** no bot has finished a floor, so there are no L1 to L4 timings, no alarm margin and no placings from them yet. The bots do not shut doors behind them (the doors-as-a-tool idea), and they read the monsters' positions straight from the game.
>
> ## Health and spawns (built)
>
> - **Health.** 100 HP. A monster touch (within 1 m, line of sight) hits for 35, at most once every 1.2 s per monster, and you get a 1 s grace after any hit, so three hits (in about 3 s or more) down you. +1 HP/s after 10 s without damage. A lifted teammate returns with 50 HP; a self-respawn after the down timer gives 100. HUD: bar bottom-left, a red flash on a hit, a stronger vignette under 36 HP; a teammate's HP shows as a thin bar under their name. Rules: `shared/health.js`; the floor's host decides a touch and relays `{t:"hit", dmg}` (server: host only, damage clamped 1..50). HP is trusted to each client, like ammo.
> - **Spawns.** Each player draws their own random spot at round start and after every down, on every floor: `shared/spawn.js`, weight `exp(-d/15) + 0.02` with d the distance to the nearest unfinished objective (B1 fuses not in the door, L1 switches off, L2 notes not found; L3 and L4 uniform), never within 16 m of a monster. On B1 the median spawn is 11.4 m from a fuse against 18.8 m for a uniform draw.
> - **Bots (4, guns, 600 s, B1).** Before: 0/3 fuses in the door in all four runs, team downs 15 to 24. After health + spawns: 1/3 fuses, 13 team downs (2, 5, 2, 4), the floor still not finished. Bots do not yet read their HP.
>
> ## The cloak and the AFK Beacon (built)
>
> - **Cloak** (`models/cloak.glb`, `shared/cloak.js`). One per player, in the same B1 locker as the gun. `V` (controller: left trigger) toggles it. On, monsters cannot see you beyond 1.5 m, but they still hear you (running while cloaked is loud). The battery lasts about 15 s of use and recharges in about 45 s after a 2 s wait while off; it cannot be switched on below 10%. You see a cyan edge shimmer and a battery bar; teammates see you flicker. Held at the bottom left.
> - **AFK Beacon** (`models/beacon.glb`, `shared/beacon.js`, `shared/loot.js`). Two lie on every floor (taken once, carry at most 2). `G` (controller: right bumper) rolls one up to 12 m ahead (it stops at a wall). For 25 s every monster within 30 m of it goes to a spot on a 1.5 to 3 m ring round the can and idles there facing it, shuffling apart when they bump; they ignore players, even a monster already chasing drops the chase, unless a player is within 4 m of that monster (it still sees them). When the 25 s end they search at the can for 6 s and then patrol. The thrower sends `{t:"beacon", x, z}`; the server relays it to the rest of the floor; the floor's host runs the lure. The can shows a pulsing LED and a ring that shrinks with the time left.
> - **Models.** Both Meshy exports (12 to 16 MB, 10k triangles, 2048 px maps) were reduced to 1024 px WebP maps and Draco: `beacon.glb` 0.9 MB, `cloak.glb` 0.8 MB, geometry unchanged. The beacon is 1.9 x 1.2 x 0.8 units (shown 0.36 m long); the cloak 1.0 x 1.9 x 0.6 units (held at 0.12x).
> - **Bots.** They pick up beacons within 20 m, roll one at a chaser 7 to 22 m away, and switch the cloak on when a monster is within 14 m and off when clear; below 50 HP they flee a monster that is not on patrol.
> - **Bot run with everything (4 bots, guns, cloak, beacons, 600 s, B1).** 0/3 fuses in the door, 17 team downs (4, 5, 5, 3), each bot hit 7 to 10 times, cloak on 71 to 100 s each, beacons thrown 0, 0, 0, 2. Not better than the health + spawns run (1/3, 13 downs); one run each is within the spread seen before (15 to 24 downs), so this says only that the items did not obviously help yet. The bots rarely walk to a beacon and the cloak is on whenever a monster is within 14 m, which drains it early; both are tuning for later.
>
> ## Cameras, and bots that only know what they can know (built)
>
> - **Measured first** (`node tools/cam_coverage.mjs`): over a full sweep the cameras cover 56% of B1 (27 cameras), 53% of L1 (24), 53% of L2 (35), 60% of L3 (2) and 54% of L4 (4); at any one moment 21%, 18%, 20%, 44% and 2%. So there was plenty to see; the problem was that it could not be read.
> - **One clock.** The server's time is sent at join; every client computes each camera's sweep from it, so everyone sees the same picture at the same moment (`welcome.now`, `ctime()`).
> - **Team map** (M / View). Every camera and the cone it covers right now (green; red while it sees a monster; the chosen camera outlined). A sighting stays 6 s (it was 3), fading, with the monster's name and an arrow for the way it was facing. A ring pulses while it is in view.
> - **Feed.** A caption names the camera ("CAM 12 / 35") and says which monsters are in view. `Q` / `T` (or LB / D-pad left and right), the mouse wheel and `1` to `9` choose a camera; **`Z`** (D-pad down) jumps to the nearest camera that sees a monster right now.
> - **Buzz.** When a camera sees a monster within 14 m of anyone on the floor, a line shows for 3 s ("CAM 12: sinew near Bob") with a short buzz, at most once per camera per 8 s.
> - **Fair bots.** By default a bot knows only a monster it can see (18 m, line of sight) or hear (6 m), one a teammate reported on the team blackboard, and, for the scout (the watcher), one a security camera shows; it remembers an unseen monster at its last spot for 8 s with no idea what it does. `--omniscient` restores the old all-knowing bots; `--nocams` stops the scout reading cameras.
> - **Bots, 4 each, guns, cloak and beacons, 600 s, B1 (one run each, so a rough guide):**
>
>   | bots know | fuses in the door | team downs | hits taken |
>   |---|---|---|---|
>   | everything (`--omniscient`) | 1/3 | 12 | 31 |
>   | what they see and hear, plus cameras through the scout | 1/3 | 12 | 27 |
>   | what they see and hear, no cameras (`--nocams`) | 0/3 | 17 | 32 |
>
>   The scout learned of monsters through cameras alone for 356 s of the round. Fair bots with cameras did as well as all-knowing ones; without cameras they did worse. No team finished B1 in any of the runs, and one run each cannot separate a real effect from the spread (earlier runs ranged from 15 to 24 downs).
>
> ## Bot tuning of the beacon and the cloak (tried, inconclusive)
>
> New rules: the cloak goes on only when a monster is within 9 m or hunting, never below 40% battery, never when two teammates already have theirs on, and off once clear (16 m) or flat; bots collect beacons from up to 28 m away and roll one at a monster that has not seen them (9 to 28 m), not only at a chaser. Measured with the new per-bot figures (time to first fuse, seconds carrying, cloak seconds wasted).
>
> 4 bots, B1, 450 s, three rounds each:
>
> | | fuses in the door | team downs | hits taken | beacons thrown |
> |---|---|---|---|---|
> | tuned | 0, 1, 1 | 14, 15, 13 | 30, 28, 25 | 2, 2, 1 |
> | old (`--legacy-items`) | 0, 0, 0 | 13, 6, 14 | 27, 15, 29 | 2, 2, 2 |
>
> The cloak is no longer wasted (1 to 9 s per round with no monster near, against all of its use before), but the round outcomes are inside the spread: no clear gain. The real finding is that bots throw only 1 to 2 beacons per round between four of them, so they rarely hold one; the beacon pickups are not on their way. The next step would be to route the runner past the nearest beacon at the start, not to tune throwing.
>
> ## Server-run monsters and player state
>
> - **Monsters** run on the server, one `Floor` per room and floor that has a player (`server/floorsim.js`), at 20 Hz; snapshots go out at 10 Hz as `{t:"m", scene, l:[[x,z,yaw,speed,state]...], d}`. The rules are the same code the page runs in solo (`shared/world.js`, `shared/monsters.js`); `tools/world_parity.mjs` checks that the page and the server build the same navigation grid, boxes, doors and spawns. A server tick for 8 players costs about 0.25 ms.
> - **The server owns your state** (`server/playerstate.js`): HP, rounds, the gun, beacons carried, the cloak battery, down / respawn / revive. You send intents (`shot`, `beacon`, `cloak`, `loot`, `revive`, `door`, `switch`, `keypad`, `power`); it answers `{t:"me", hp, gun, rounds, beacons, cloak}` and puts your server HP and cloak into what other players see. A modified client cannot give itself rounds or health, hit monsters from across the map, or open a door it is not near.
> - **Position stays the client's** (as in most games like this). The server drops off-map positions, and each socket has a message budget (a burst of 240, 90 per second, a kick past 600 flooded).
> - **Controls list:** `H` in game. Voices: each monster kind has its own growl and pitch.
>
> **Bots against the server-run monsters, beacon pickup radius 40 m versus 20 m (4 bots, B1, 450 s, three runs each).** Total downs per run (all four bots): 9, 10, 10 with the wider radius; 8, 8, 8 with the old one. Beacons thrown per run: 2, 2, 2 against 2, 2, 2. Nobody left B1 in any of the six runs. So widening the pickup radius did not get more beacons thrown, and the downs are no better (if anything slightly more, within the noise of three runs). The bots stay sharing the same two beacons and rarely have a reason to throw them; this is not tuned, and the numbers do not show the beacon or the cloak changing the outcome. The harness itself is healthy with the server running the monsters: the bots' tick stays at 50 ms (max 84 ms, no gap over 150 ms).
>
> **Load check, 8 bots in one room on B1 (300 s, server and eight software-rendered browsers on one machine).** The server's simulation tick averaged 0.31 ms over 6,226 ticks, with one spike to 38 ms (a path search or the machine sharing its CPU with the browsers; not investigated). The target was an average under 5 ms. Nobody left B1 in that time, as in the earlier runs.
>
> ## Note: the bots are not reckless enough (owner's play, 2026-11-05)
>
> The owner finished a full solo round in **36 minutes**. Floor 1 (B1) was the hardest and the last floor the quickest; the owner went down about **23** times on B1. They used up the ray gun's rounds **5 times**, threw **4 beacons**, and used the cloak rarely because it was only kind of useful.
>
> The bots play very differently. In the 300 to 450 s runs they waited 150 to 260 s of each run for patrols to pass, threw 0 to 2 beacons per run in total, fired 0 to 6 shots per bot, and used the cloak for a few seconds. Their first fuse came at 200 to 400 s, or never. They are far too cautious: they do not spend ammo, beacons or the cloak the way a person who is losing does, and they take on the risk of a run far less. Treat their downs and "nobody got out" as a weak measure, not as evidence about difficulty (those runs were also capped at 5 to 10 minutes, against a human's 36).
>
> Before using the bots to tune a floor again: make them spend resources and take risks (fire when a monster is within range, throw a beacon when chased, wait less), and give them a time limit near a human round. The cloak's usefulness is a design question for the owner's play, not something the bots can answer.
>
> ## Controls and secondary abilities (owner's design, 2026-11-05)
>
> - **Held items.** `HELD.item` is one of the ray gun, the cloak or a beacon (or empty hands). The first thing you pick up is in your hands. Y (tap) rotates, Y (hold) opens a wheel (right stick, arrows or the mouse wheel choose; release takes it). RT / left click is the primary use of the held item; LT / right click aims the gun (zoom, slower look) or is the secondary of the cloak and the beacon.
> - **Cloak, secondary: short circuit** (`shared/cloak.js`: `shortCircuit`, `BROKEN_S` 300, `STUN_R` 8, `STUN_S` 5). The cloak is dead for 5 minutes (no switching on, no recharge; the server counts it down) and every monster within 8 m on your floor is stunned for 5 s: a stunned monster neither moves nor hits (`MonsterSim.stun`, `stunNear`). In a room the server decides (`cloak2` intent, `Floor.cloakBlast`), tells the floor (`stun`) and puts the seconds left in `me.cloak.x`.
> - **Beacon, secondary: reverse the frequency** (`shared/beacon.js`: `reverse`, `REVERSE_S` 12, `GROUP_S` 10). The nearest running beacon within 30 m: for 12 s the monsters it would pull run up to 18 m away from it (`MonsterSim.flee`); then it pulls again and they group up round it (it is kept running at least 10 s more). Once per beacon. In a room: `beacon2` intent, `Floor.reverseBeacon`, `reverse` message.
> - **Going back in only (sessions 8 and 19 to 26):** keys 4 and 5 hold the first and the second arsenal weapon you carry (two at most: the hunting crossbow, the pneumatic bolt driver, the stun baton, the moth jelly dart, the propane flamethrower, the frequency horn, the rocket launcher (which you cannot run with) and the laser dissector (hold left click or RT for the beam, right click or LT for the dot) and the rebar shear (hold left click or RT to spool, let go to cut; when the spring is worn, hold right click or LT 3 s to reset the jaw; a cut opens the chained supply cage and a chained door); the crossbow and the driver at the start; the flamethrower burns while you hold left click or RT); Q throws a flash-vial and E sets a land mine or a tripwire (LB / RB on a controller). The Original has none of these and no loadout locker. In a room of the mode (session 16; pick GOING BACK IN in the lobby) the server owns all of it: the wave, the bolts, the loadout, the consumables and the kills (the bolt driver is solo only so far).
> - **Not built yet:** in the Original the consumable slots (LB / RB, Q / E) hold nothing; the camera feeds have no controls (a later item is meant to bring them back as a full-screen ability). Walk, run and crouch speeds and the run stamina are this game's (4 / 7.5 / 2.2 m/s); main's unified paces were not adopted because the monsters are tuned against these.
> - **Stairs** are main's: a stair door opens onto a lit hallway drawn through the doorway; step into the doorway to cross. Tests: `tools/stairs_test.mjs`, `tools/controls_test.mjs`.
>
> ## Session 12: tuning B1 with the bots (2026-11-08)
>
> All runs: 4 bots, B1, 420 s, `node tools/bots.mjs 4 --bold --timeout=420` (`--bold` is new: a 5 s patience budget instead of 25 s, shooting from 20 m, ammo packs fetched from 40 m). One run per row, so the spread (a bot's downs ranged 0 to 7 in the same setting) is as large as most effects. Team downs, fuses in the door out of 3:
>
> | Setting | Team downs | Fuses in door | Notes |
> |---|---|---|---|
> | Original numbers, cautious bots | 5 | 1 | waited 51 to 166 s each |
> | Original numbers, `--bold` | 10 | 0 | the baseline for the rows below |
> | Down time 45 s to 20 s | 12 | 0 | more downs, since a bot is back in the corridor sooner |
> | and B1 packs 3 to 6 | 4 | 0 | the largest change seen; every gun used |
> | and spawn weight `NEAR_M` 15 to 8 | 10 | 1 | inside the spread; **reverted** |
> | and B1 monsters 4 to 3 | 14 | 0 | no better, and three server tests assume 4; **reverted** |
>
> **What stayed:** down time 20 s (`DOWNED_S` in `server/playerstate.js` and `index.html`, one number each) and 6 packs on B1 (`shared/farway.manifest.js`). The pinned tests were updated on purpose (`shared/loot.test.js`, `shared/manifest.test.js`, and two test titles).
>
> **What the bots cannot tell us.** No bot team delivered a fuse in more than 1 of 8 runs, and the runner often carried a fuse for 300 to 400 s of 420 (stuck counts of 50 to 100). That looks like the bots' route to the stair door, not only the floor's difficulty, so time to clear B1 is not measured here. Not tried: moving the round-start spawn (`groupSpawn` in `index.html`, outside this session's files), a way round the corridor, and changing the cloak (the owner's call).
>
> ### Playtest checklist for the owner (3 or 4 players, B1 only, a stopwatch)
> 1. Time from the countdown to the third fuse in the door. Target about 4 min.
> 2. Downs per player on B1. Target under 5.
> 3. With a 20 s down time: does it feel like a penalty, or like nothing? Try 30 s if nothing.
> 4. With 6 packs: do you run out of rounds before the corridor, or have spare at the end? If spare, take packs back to 4 or 5.
> 5. Where does everyone go down? If it is still the corridor near x 0 to 9, z -10 to -15, the next lever is the spawn or a way round it.
> 6. Does anyone use the cloak? (Not changed.)
>

### Source file: docs/WORLD.md

> # Farway: world bible v2
>
> Built from the owner's answers to a planning questionnaire (2026-11-04 to 2026-11-06), then checked against this repo at commit 6c4bcb1.
>
> Every line carries a tag.
>
> - **[SETTLED]** the owner said it.
> - **[BUILT]** verified in this repo, and a test covers it.
> - **[MY CALL]** proposed by the planning assistant where the owner said "you decide" or left it open. Not confirmed; the owner may veto it.
> - **[OPEN]** needs a decision from the owner.
>
> ---
>
> ## 1. Premise
>
> - Farway is the generated world. Project Never Land runs it. A supercomputer in Secret Operations generated it and controls everything. [SETTLED]
> - The world is an allegory for being taken. "Far Away" means taken, Never Land echoes the ranch, and being "noclipped" means being abducted. The Backrooms resonates because it is hard to accept how many people go missing, so it works as a quiet answer to a scarier real world. [SETTLED]
> - The allegory lives in the mechanics. [MY CALL]
>   - The lure is a job application: the drag-and-drop quiz, for the Intern and every other job.
>   - Isolation is the empty city and the one apartment.
>   - Surveillance is the cameras and the agents.
>   - Confinement is the cell.
>   - Control is the keycards and access levels.
>   - The player's base weapon is the Error Deletion Ray, which no-clips a monster to another place. That is the same act as taking a person. Admin's red version, renamed "ATL X", deletes.
>   - The game's own title, "Look Over There", is the abductor's distraction line.
> - Guardrails. [MY CALL]
>   - No real names, cases or victims in the game.
>   - Nothing graphic.
>   - Show the machinery of taking people, never the harm.
>   - Consider a short content note on first launch.
> - The Neverland ranch is a real place. Keep "Never Land" generic in-game, with no direct reference.
> - Different truths per area. [OPEN] Proposals are in section 9.
>
> ## 2. Tone: how to tell the three apart [SETTLED]
>
> | Mode | Feels like | Where |
> |---|---|---|
> | Dreamcore | Happy and dreamlike, but fake | Overworld, the dreamcore forest and house, playground, tree house |
> | Liminal | Off and empty but seemingly normal | City, hotel upper floors, mall, grocery |
> | Backrooms | A mix of both, but hostile and stripped of navigability, built to disorient | Look Over There floors and chambers, the atrium anomaly maze, Secret Operations |
>
> - The Overworld is plastic, like a simulation, and eerily beautiful.
> - It has four skies: clear with no clouds, drifting anime clouds, sunrise and sunset, and a bright starry night. A game day is 15 real minutes.
> - Film grain and a VHS look, both. Voice and text, both. Each game keeps its own walker scale, because it adds to the liminal oddness.
>
> ## 3. The map
>
> ```
> FARWAY
> |
> OVERWORLD (hub, 10 minutes end to end)
> |  table and chairs (spawn), Market, groundskeepers, playground (mini-games for money),
> |  tree house, parking lot, Look Over There store, endless hills with physics toys,
> |  fake 2D horizon, "more to come" facades
> |
> +-- LOOK OVER THERE doors ----> options: [Original] or [Going back in]
> |        Original: B1 > L1 > L2 > L3 > L4, then walk out onto the parking lot
> |        Going back in: top down L4 > L3 > L2 > L1 > B1, 4 chambers a floor, 20 waves
> |
> +-- bus station (just a ride) --> CITY
> |        Hallam Row (jobs), apartment tower = HOTEL, mall, grocery
> |
> +-- road > forest > meadow with SHED > DREAMCORE HOUSE (Right Door, Wrong Exit, ~50 rooms)
> |        shed and tree house lead to their own addons later
> |
> SECRET OPERATIONS (Project Never Land): hidden no-clearance entrance deep in the Right Door,
> Wrong Exit maze, keycard doors everywhere else, hardest boss (The Registrar), Admin access
> ```
>
> ### Connector types you named [SETTLED]
>
> | Connector | Used for |
> |---|---|
> | Stair door with lit hallway (built) | Look Over There floors |
> | Painted-sky hall with an EXIT door | Every hall between worlds |
> | Elevator (reused from the Intern) | Hotel floors; the apartment to every level |
> | Service corridors and lifts | The hidden network; Intern, grocery back-of-house, Look Over There backstage |
> | Bus ride | Overworld to city |
> | Pool dive | Intern escape to Secret Operations; hotel sub-floor pools to B1 pools (a long way) |
> | Vent crawl, stairs, door | Chamber to chamber in Going back in (all mixed) |
> | Gate (built) | Overworld to games. Today the gates to Right Door, Wrong Exit and the Intern are solo only. |
>
> ## 4. Places
>
> ### Overworld [SETTLED unless tagged]
> - v0 is built (session 6): finish the Original alone, press "Walk out" on the results screen, and you arrive at a table and chairs in the parking lot, facing the store, under a clear sky. Walking up to the glass doors opens the options screen: Original (starts a fresh round) or Going back in (alone only; session 8: it lands you in the first chamber, with its wave starting). Rooms stay in the store for now. [BUILT]
> - Walking out of Look Over There onto the parking lot ends the Original. The results screen already shows place, time and your best time on this browser. [BUILT] Still to add: deaths (downs nobody revived), revives, a score that counts revives, an online ranking, a congratulations and a welcome to Farway. [SETTLED]
> - A first-time player sees the whole Overworld at once, and new facades appear as things are added.
> - The Market sells weapons, gear, food, keycards and cosmetics. It is also where lost ammo, consumables and perks are bought back (section 5).
> - Groundskeepers maintain the hedges. They watch you or ignore you.
> - The endless hills never get you further away. They hold little puzzles and toys you can kick around, with physics.
> - The edge of the world is a fake 2D render of more world that looks real.
> - You land back at the door you left after any game.
> - The playground has real playground equipment, each a mini-game that pays money (section 5).
>
> ### Dreamcore forest and house [SETTLED]
> - Road, then forest, then a meadow with the shed, then the house. The shed is in the forest, not in the Overworld.
> - The shed is an entrance and a puzzle. The tree house is a puzzle and an entrance. Both lead to their own addons later.
> - The house is much bigger inside.
> - **v0 is built** (`shared/forest.js`, scenes `forest` and `meadow`): a signpost by the parking lot's north-west hedge walks you down the road (F, as the bus is taken; the Overworld's own road scene is still planned). The forest is a winding path north through pastel trees under a pink haze; a bright gap at its end leads into the meadow (you walk through it, and back out the meadow's south edge). The meadow has flowers, the shed beside the path (the owner's Meshy model, `models/world/shed.glb`; locked: its puzzle and addon come later) and the house at the end (the owner's "moonlit cabin", `models/world/cottage.glb`). The house's door is Right Door, Wrong Exit, solo only as its other gate is, and you come back out in front of the house. Both scenes are presence scenes: a party sees each other walk there. Blockout trees and flowers; no groundskeepers, puzzles or sounds yet. [BUILT]
>
> ### Look Over There [SETTLED unless tagged]
>
> **Original (built).** A co-op round for 2 to 10 players, about 20 minutes, solo allowed. [BUILT]
> - You climb B1, L1, L2, L3, L4 together and get out. One puzzle gates each floor.
>
> | Floor | Puzzle |
> |---|---|
> | B1 pools | Three fuses, carried one at a time to the stair door |
> | L1 offices | Two far-apart switches, each flip is loud and draws monsters |
> | L2 | A 4-digit code, one digit on each of four notes the team finds |
> | L3 white room | No monsters. An optional fuse box powers L4's doors early. |
> | L4 showroom | The glass doors are shut unless the power is on. Then a 60-second alarm hunt, then out onto the parking lot. |
>
> - Survival: crouch is quiet and halves how far monsters see you, but you cannot outrun them, so you hide and use doors. Doors can be closed, and a door you shut is shut for everyone.
> - Health: 100 HP, 35 per monster hit. In a room you are downed, not dead: teammates revive you in 4 seconds, and you wake at the stairs after 45 seconds. Solo: die, wait 3 seconds, respawn at a random spot.
> - Monsters are server-run: Sinew of the Abyss on B1, the Pale Traveler on L1, the clawed creature on L2, the first creature on L4, none on L3. Monster count scaling by player count is planned.
> - Cameras sweep each floor, and monsters show on the team map only when a camera sees them.
> - Five playable characters: plaid, suit, shorts, red, white. The suit is the agent model for Secret Operations. [SETTLED]
> - The owner's own solo run took 36 minutes with about 23 downs on B1, so the numbers are untuned. [BUILT note]
>
> **The base kit (built).** Three items, all non-lethal. [BUILT]
>
> | Item | Primary | Secondary |
> |---|---|---|
> | Error Deletion Ray (the "noclipper") | Fires a ray that no-clips a monster to another place at least 15 m away and out of sight; it flickers, waits 4 seconds, then patrols again. A shot is as loud as running. 3 starting rounds, 9 max. | Aim and zoom |
> | Cloak | Monsters cannot see you beyond 1.5 m but still hear you. About 15 seconds of use, 45 to recharge. | Short circuit: stuns every monster within 8 m for 5 seconds, then the cloak is dead for 5 minutes |
> | AFK Beacon | Roll it up to 12 m. For 25 seconds monsters within 30 m go and idle around it. | Reverse: monsters run from it for 12 seconds, then group up round it. Once per beacon. |
>
> - Controls: Y takes out the gun, cloak or beacon (tap rotates, hold opens a wheel). Shift or left-stick click crouches (toggle). R or right-stick click runs (hold). RT or left click uses what you hold. LT or right click aims the gun. X is action.
> - Q and E (LB and RB on a controller) are consumable slots, empty today. That is where the arsenal's consumables and the dealer items will go.
> - Loot today: B1 has 8 lockers, each holding one ray and one cloak, taken once. Ammo packs lie on every floor (3 rounds each). Two beacons per floor.
> - The existing locker is a one-time pickup. The Going back in locker is a loadout station. They need different names. [OPEN]
>
> **Going back in.** [SETTLED]
> - A 20-wave run: 5 floors, 4 chambers each, top down: L4, L3, L2, L1, B1. A chamber is as big as an original floor, and the 4th always has the stairs down.
> - Version 1 is 4 chambers per floor with no randomness yet. The existing floor is one of the four, so that is 15 new chambers.
> - Each chamber has one wave, triggered on entering. The rest is quiet time: find objects, puzzles, loot, build defences, explore.
> - A chamber is cleared by all of these: missing objects, puzzles, kill count, surviving a timer.
> - Chambers connect with any mix of vent crawls, elevators, stairs, doors and painted-sky halls.
> - Unkillable threats: crushing walls, floor is lava, high tides, toxic gas, moving chainsaw blades. Special entities come later.
> - Soft pressure: light, battery, a noise meter, hunger.
> - Doors can be closed, trapped or barricaded. Doors only.
> - You can crawl into vents. Monsters never use them.
> - Safe houses on every floor hold a shop, stash, save, crafting and a respawn point.
> - Lockers sit one per safe house and one per chamber. They show your loadout, let you change it, and return your gear for free after you die.
> - Money comes from clearing chambers and from every kill and revive. Level comes from achievements.
> - Own save, with money and items shared. Online leaderboard per run, plus personal and overall bests.
> - Lethal weapons are bought at the Market. The arsenal is in section 5.
>
> ### City [SETTLED unless tagged]
> - Open streets plus interiors. 15 real minutes a day. Needs: hunger and sleep. Food comes from the grocery by cart and checkout. A bed saves and skips the night.
> - At night stores close. There is a grace period until midnight, then everything turns dangerous. Unkillable monsters come out and you must get to your apartment. The mall can lock you in.
> - The stalker is the city's creature. It never touches you while you look at it. If you ignore it too long while alone, it grabs you and bites your head off. It is the only monster that follows between areas.
> - Threats are separate: stalker, agents, cell (a puzzle escape), death. You can also get into trouble by stealing or being seen on camera in a restricted area. Anomalies are both spot-and-report and avoid.
> - NPCs: mannequin-like figures and people with routines. The lit windows are a mix of decoration, NPC apartments, apartments you can visit and things watching you.
> - Apartment computer: job search, mini-games, mail, news, bank, map.
> - Applications are a drag-and-drop quiz. Answer wrong and you are rejected, answer right and you are accepted. One application at a time.
> - The player is whoever they choose. Customisable: name, face and body, clothes, starting gear. The Intern and every other role are jobs the player takes.
>
> **City v0 plan (session 9).** Slice 1 is built: a bus stop in the Overworld's parking lot takes you to `street`, a blockout of Hallam Row (road, sidewalks, shop doors with signs, the apartment tower's entrance, lamp posts, a bus shelter), with a 15-minute game day and the first half of the night rule (stores close). The clock starts at 08:00 on day 1, runs only while you are on the street (leaving by the bus pauses it; a reload starts again at 08:00), and stores are open 08:00 to 20:00. Solo only. No art exists, so it is boxes. Slice 2: the apartment interior with its computer is built (the tower door opens into it; four pages: mail, news, job search, map). The danger after midnight is built too (one stalker on the street from 00:00 to 06:00, frozen while you look at it, a blackout wakes you at 06:00 in your apartment, the bus does not run, a bed skips the night). Defaults: no death and no penalty in v0, the stalker is the only night threat (the other unkillable monsters in the owner's note are not built) (20:00 to midnight is the grace period; the owner's wording is "everything turns dangerous" at midnight, taken as 00:00 to 06:00). Slice 3 (its own PR, stacked on this one): the Intern's job at 666 Hallam Row through the shared application quiz: apply on the computer, a wrong answer is a rejection until tomorrow, an acceptance sets `job_intern`, and the door of 666 then starts a shift (the Intern game). Defaults: the quiz is three rounds (sort tasks, match a form to a day, an ungraded intrusive round), rejection waits one game day. Slice 4 (stacked on slice 3): hunger and the grocery. Hunger drains with the City's clock over 36 game hours, warnings at 30 and 10, fainting at 0 wakes you at home at 06:00; the grocery behind the street's door is open by day, with a cart (8 items, 2 without), four foods, a checkout, and the food going to a fridge in the apartment; you start with $20; the computer has a Bank page. Slice 5 (stacked on slice 4): pay by performance. The Intern game reports how the shift went and the pay follows it: a base by ending (ASSIMILATION $20, RETAINED $14, PENDING $8, EXPULSION $4), plus $1 per point of conformance, minus $1 per point of friction, $0 to $30, and nothing for quitting. Defaults: those numbers; an expulsion does not cost you the job. Slice 6 (stacked on slice 5): the other four jobs. Each has its own application quiz and flag; you can hold several jobs; their shifts are stubs (a screen, 4 hours and flat pay, 3 hours in the evening for the museum guard) until each job's game is built. Slice 7 (stacked on slice 6): saving. The bed saves the City to the browser (by day it only saves; from 20:00 it also skips the night) and a reload resumes from the last save. Defaults: the bed is the only save point; no New Game control yet. Slice 8 (stacked on slice 7): the three city anomalies from section 9, as blockout. A PHARMACY sign on the filler building across from the mall changes one letter each time you walk past it; six pedestrians stand on the sidewalks while the stores are open, all facing up the street toward 666, and are gone when the stores close; after dark a single lit window hangs high over the grass past the east side's last building, where there is no building. Defaults: they are drawn only (nothing to bump into, no interaction), the sign's changes are not saved (a reload puts PHARMACY back), and the pedestrians stand still. Slice 9 (stacked on slice 8): New Game and the save line. The bank page says when the City was last saved (or that it has not been); a sixth computer page, SYSTEM, has New Game, which asks twice and then forgets the City (the save, every job, money, the fridge, the clock, the sign) and starts it again at 08:00 on day 1 with $20. Defaults: New Game is only on the apartment's computer; it keeps the Original's flag and everything outside the City. Slice 10 (stacked on slice 9): the stalker follows you. At night only the street and your apartment are open (the stores shut at 20:00, the bus does not run), so following means it no longer goes away when you go in: if it is out, it waits outside the tower's door, 14 m up or down the street on the side it came from, and is there when you step out (a toast warns you). The apartment stays safe. Defaults: it waits 14 m away (its closest spawn distance), it is gone at dawn, after you sleep and after a blackout, and it follows only between the street and the apartment. Slice 11 (stacked on slice 10): the trash truck worker's game, the first job game after the Intern. The route is Hallam Row: starting the shift at 41 puts eight green bins at the kerb; F at a bin empties it and F back at 41 clocks you out. It keeps the stub's hours (4, starting between 08:00 and 16:00) and is paid by performance: $2 a bin and $4 more for the whole route clocked out on time ($20 at best, the stub paid $10). Running out of time or leaving the street (the bus, a door) ends the shift and pays the bins only. Defaults: those numbers, the eight bin spots, no truck yet (you walk the route), and the bins collide with nothing. Slice 12 (stacked on slice 11): sleep as a need. Rest (0 to 100, on the HUD after the money) drains while you are awake in the City, so a full bar lasts 20 waking hours; it warns at 30 (tired) and 10 (exhausted), and at 0 you pass out and wake at home at 06:00. The bed refills it: 12 an hour asleep, so a night from 20:00 fills it; by day, when you are tired, the bed lets you nap for 3 hours (and saves). Rest is saved. Defaults: those numbers; you start the City at 90; passing out, fainting or being caught leaves you at 60 at least; being exhausted does not slow you down yet (the walking speed is in the physics region, which this slice does not touch). Slice 13 (stacked on slice 12): the mall locks you in. The street's MALL door opens by day (08:00 to 20:00) into a blockout atrium: a dry fountain, two benches and eight shuttered shopfronts. Unlike the grocery, nobody shows you out: at 20:00 the lights go down to the emergency lights and the doors lock with you inside until 06:00. The clock, hunger and rest run as usual, the stalker cannot come in, and a bench lets you sleep through to 06:00. Defaults: locked until dawn (06:00), not until the stores open; the benches do not save (only the bed at home does); no shops open inside yet. Slice 14 (stacked on slice 13): the museum night guard's game. With the job, 108's door between 20:00 and 21:00 starts a 3-hour shift in the galleries, a blockout hall with six statues on plinths. The statues follow the stalker's rule: the one you look at never moves, and the others, out of your sight, step off their plinths one step at a time (three at most) and turn to face you. F next to a moved statue sets it back. At the end of the shift you are back on the street, paid $2 for each statue on its plinth and $1 for each you set back (up to $8): $20 at best, against the stub's $16. Walking out early, fainting or passing out loses the shift and pays nothing. Defaults: those numbers, a statue moves every 9 seconds it is not watched, the statues cannot hurt you, and they are drawn only (you can walk through them). Slice 15 (stacked on slice 14): reporting the anomalies ("spot-and-report"). You spot one by seeing it yourself: the PHARMACY sign once it has changed, two or more of the pedestrians at once by day, the lit window at night (a line on screen says you noticed). The computer has a REPORT page (key 6; SYSTEM moves to key 7) with six reports, three real (the slice 8 anomalies) and three that are not (a streetlight that follows people home, a door that was not there yesterday, a bus driver with no face). A true report of something you have spotted pays $5, once each; a report of something unreal, or of a real thing you have not seen yourself, is false and costs $2. What you have spotted and reported is saved; New Game clears it. Defaults: those numbers and the three decoys; no cost for looking. Slice 16 (stacked on slice 15): the factory floor worker's game. With the job, 330's door between 08:00 and 16:00 starts a 4-hour shift on the factory floor, a blockout hall with one conveyor belt and three bins (gears, bolts, springs). A part comes down the belt every 4 seconds in a fixed mixed order; F by the belt picks one up (one at a time), F at a bin drops it in, and what reaches the end of the belt falls into the reject chute. Pay: $1 for each part in the right bin, $1 off for each in the wrong one, from $0 to $20 (the stub paid $12). Walking out early, fainting or passing out loses the shift. Defaults: those numbers, the belt's speed (0.8 m/s, 20 s end to end) and no cost for missed parts. Only the lab is still a stub. Slice 17 (stacked on slice 16): the laboratory worker's game, the last of the five jobs. With the job, 214's door between 08:00 and 16:00 starts a 4-hour shift in the lab, a white blockout room with five stations (sink, scale, centrifuge, freezer, log book) and a sealed door on the north wall marked "B2 · AUTHORISED STAFF ONLY" (the way toward Secret Operations, not built). Each procedure card, shown on the HUD, names three stations in order; F at each in turn does the card, and F at a wrong station spoils it (the toast says which station it wanted) and the next card comes up. Pay: $3 a card done, $1 off a card spoiled, from $0 to $20 (the stub paid $14). Walking out early, fainting or passing out loses the shift. Defaults: those numbers, three stations a card, no time limit per card. Every job now has its own game; the stub shift screen is no longer reached (its hours, `STUB_SHIFTS`, still set when each shift can start). Slice 18 (stacked on slice 17): pedestrians with routines ("people with routines"). By day, each of the six pedestrians walks a short beat up and down its sidewalk (3 m either side of where it stood) while you are not looking, and stands still the moment it is in your view; they always face up the street, even mid-step, so whenever you look they are all facing the same way. At night they are gone and their routines stop. Spotting them for the REPORT page uses where they are now. Defaults: a 3 m beat at 1.2 m/s, no turning, no collisions, not saved (a reload puts them back where they started). Slice 19 (stacked on slice 18): stealing and the camera ("you can also get into trouble by stealing or being seen on camera"). A security camera high on the grocery's north wall sweeps to and fro (40 degrees each way every 12 seconds); its red light shows where it is looking, and it watches the door about a third of the time. Walking out of the door with what you have not paid for: if the camera is turned away you keep it (it goes to your fridge, like a purchase); if it is on you, you are fined $5 plus what it would have cost (never more than you have) and it goes back on the shelves. Being shown out at closing still puts everything back. Defaults: those numbers, the camera only in the grocery, no record of thefts and no police yet. Slice 20 (stacked on slice 19): the City HUD's layout. With rest and the job games the needs line had grown long enough to run into the toast at the top of the screen. The needs now sit on one line and what you are doing (a cart, a route, a shift's statues, parts or card) on its own line under them, wrapping inside the HUD's width; while the City HUD is up the toast sits below it (further down on narrow screens). Outside the City the toast is where it always was. Slice 21 (stacked on slice 20): the watchers ("the lit windows are a mix of decoration, NPC apartments... and things watching you"). At night three of the street's lit windows (one on the filler block across from the mall, one at 330, one high in the apartment tower) have a dark figure against the lit glass that turns to follow you (the buildings are solid blockout boxes, so it stands just in front of the pane as a silhouette) as you walk past; by day they are gone. Seeing one in front of you within 30 m spots it, and "Someone in a lit window who turns to watch you" is now a fourth real report on the REPORT page ($5, like the others). Defaults: three windows, drawn only, no other effect yet. Defaults: those numbers, no stealing, no penalty for fainting, nothing saved. Left out of slice 1: hunger and sleep, the stalker, NPCs, any interior (the doors say "nothing inside yet"), saving the clock, multiplayer in the City. Decisions taken by default: the street is the manifest's `city`/`street` scene and the other `jobs` area stays planned (Hallam Row's doors are on `street` for now); `Press F` is the action key in new prompts because that is what the game binds (older prompts say E).
>
> **Hallam Row, the jobs street.** The Intern's company is already at 666 Hallam Row in the game. [BUILT] The other addresses are a proposal. [MY CALL]
>
> | Address | Job | Notes |
> |---|---|---|
> | 41 Hallam Row | Trash truck worker | Municipal sanitation depot. The job is on the street, along a route. |
> | 108 Hallam Row | Museum night guard | A small museum where everything comes alive at night. |
> | 214 Hallam Row | Laboratory worker | The nearest job to Secret Operations. |
> | 330 Hallam Row | Factory floor worker | |
> | 666 Hallam Row | The Intern | The last number on the street. |
>
> - The numbers climb as the jobs get stranger, and new jobs fill in between. The street gets longer as you unlock addons.
> - Pay scales with performance. Job games are their own addons, mixed with the Intern's engine and chamber tech.
>
> ### Hotel tower [SETTLED unless tagged]
> - It is the apartment tower. Order from the bottom: sub-floor pools, lobby, floor 1 (motel), floor 2 (green carpet), floor 3 (apartments), roof.
> - Entry: street, lobby front, a back door past the deli area under the loft, a narrow hall into the atrium. The atrium is the hub. Each floor has its own section of the atrium and you move between floors by elevator.
> - Floors 1 and 2: 20 openable doors each, two levels joined by a staircase, each level a scene, rooms loaded in when opened. A Hello Neighbor style game. The neighbor is a hotel resident and the stalker. It guards a secret about the hotel.
> - Floor 3: 10 doors on one level. Peaceful. Every player gets an apartment, and up to 10 players share the floor. The others hold other players, clues, empty rooms. The roof is the upper level: city skyline, a puzzle and a safe house.
> - Sub floor: 11 separate pool scenes, peaceful with puzzles. Connected underwater to B1's pools but separate pools, and you must beat many levels to travel between.
> - Lobby: peaceful, a hub with shops. Shady dealers sell items that change gameplay (section 5). It also has puzzles.
> - Atrium anomaly maze: separate scenes off the atrium, one-way routes, you leave only by solving. Photos: IMG_2988, 2989, 2990, 2910, 2986, 3015, 3036. The elevator can glitch you into it.
> - Facade doors that do not open are places for future features.
> - Photos assigned: floor 1 corridor IMG_2999, Room 1 and Room 2 are two rooms, floor 2 dining IMG_2903 and reception IMG_2984 are hand-built key rooms, IMG_2985 is a hand-built key room and PNG image is a redesign of it. The escalators and the other staircase are separate places.
>
> ### Mall [SETTLED]
> - Old and abandoned, and also being built. Nobody visible, scaffolding only. Themed wings: bookstore, cinema, entertainment.
> - Shops you can enter: the bookstore, its front desk and the cinema lobby.
> - IMG_2909 and IMG_3012 are scenes. The other painted-sky spaces are hall connectors. IMG_2991 and IMG_3014 are one scene. IMG_3008 and IMG_3010 are one scene.
> - Mannequins are monster, set dressing and NPCs. The mirror bathroom is a portal and a puzzle.
>
> ### Grocery [SETTLED]
> - Open by day and abandoned by night. Three scenes, plus basement, back-of-house, staff areas, more aisles, a second floor. It is the same room as the end of Right Door, Wrong Exit and a bigger version. The red-cart clearing is IMG_3027.
> - The back-of-house door to Secret Operations is a staff door, a freight lift and a keycard reader.
>
> ### Right Door, Wrong Exit [SETTLED]
> - About 50 rooms. Rooms are remade larger and psychedelic. Super Liminal style: object distortion, perspective shifting, off-looking objects, distorted halls, multi-choice navigation, psychological puzzles, environmental storytelling. Room mini-games also become gates. Every door is different, with fixed exits.
> - The notebook is a graph of connections, not of space.
> - No true exit. Each completed room builds to a finale: the map opens into hide and seek. You win by hacking the computers to turn off the cameras. A swarm of secret agents arrives late. After beating it, you can play with friends.
> - One ending, many exits.
> - Hidden Secret Operations entrance: a room that repeats, or a door visible from one angle.
>
> ### Secret Operations (Project Never Land) [SETTLED unless tagged]
> - A shooter. Fight the bad guys, destroy the base. It reuses and reskins Look Over There with weapons and gear carrying over. Agents are the suit character.
> - Entrances: one hidden with no clearance, the rest need a keycard. Keycards are tiered by progress and very expensive at the Market.
> - Admin access: noclip, spawn items, teleport, delete players and monsters. Unlocked by beating the hardest boss. The game does not end.
> - The control room with a single chair in a cell: you are watched if caught.
> - Sections before the boss are open-ended.
>
> **The boss: The Registrar.** [MY CALL] The supercomputer that generated the world, in the green zone with the pink stripe.
> - It runs on the world's own rules, turned on you. It sees through cameras, files people, and no-clips them away.
> - Arena: a long green server hall with the pink stripe on the walls, the control room and cell at one end, cameras on every wall.
> - Phase 1, Intake. Cameras and agents. You cut the breakers and smash cameras to blind it. Damaged cameras can hurt you.
> - Phase 2, Processing. It "files" players: it no-clips each player to a random place in the base. You have to get back, and the cell is a puzzle room you must solve to leave.
> - Phase 3, Release. The arena's sky and geometry glitch, like the four Overworld skies failing. You fire at the server racks while it deletes the floor under you.
> - Win: its core is destroyed and you gain Admin access. Farway keeps running, but the world now answers to you.
>
> ## 5. Systems
>
> The rules for every item (the arsenal, consumables, dealer items, food, the med kit and Spicy Brew) are proposed in `docs/ITEMS.md` (session 18), for the owner to critique.
>
> **Money.** Job pay by performance, chests and piggy banks in Right Door, Wrong Exit, chamber clears, kills and revives. Level is based on how much of the game you have beaten, marked by achievements.
>
> **Death in Going back in.** [SETTLED]
> - The locker returns your weapons and gear for free: the ray, cloak, beacon and your arsenal loadout.
> - It does not return ammo, consumables or perks. You buy those back at the Market or a safe house.
> - Starting prices (numbers to tune): ammo cheap, consumables mid, perks expensive. [MY CALL]
>
> **Master arsenal (10 weapons, 3 consumables).** Pneumatic bolt driver, hunting crossbow, propane flamethrower, stun-baton capacitor, almond water aerosol rocket launcher, optical laser pointer dissector, hydraulic rebar shear, sound-amplified frequency horn, moth jelly dart, spring-loaded gravity gauntlet. Consumables: almond water land mine, compressed-air nail-bomb tripwire, phosphor-core incendiary flash-vial. These all need their own ammo rules, since today only the ray has rounds. Several names come from Backrooms community lore (almond water, deathmoths). That wiki is believed to be CC BY-SA, so attribute it if any text is lifted.
>
> **Dealer items (fictional names from the start, effects everywhere).** The downsides were accepted by the owner ("use those"). Durations are starting numbers. [MY CALL]
>
> | Item | Effect | Downside | Duration |
> |---|---|---|---|
> | Green plant | Slower, hungrier, all enemies become passive, 64-bit waving filter | Slowness and hunger | 5 min |
> | Paper tab | Fast, mushroom effects, plus the wave filter | A longer, harsher crash | 5 min, then a 2 min crash |
> | Mushrooms | A wavy, weirder world, in a good way | Unreliable depth: jumps and throws land off target | 3 min |
> | White powder | Faster and stronger | A crash afterwards: slower, weaker, louder, as long as the boost | 60 s boost, 60 s crash |
> | Alcohol | Funny walk and run, wobble grows with each drink, 5% less damage per bottle | Blackout at 5 drinks for 15 s, impossible to aim stably | per drink |
>
> **Playground mini-games.** Each pays money by performance and doubles as a physics test. The list is an expansion of the owner's "real playground". [MY CALL]
>
> | Equipment | Mini-game |
> |---|---|
> | Swing | Pump with good timing to reach the highest arc, then jump off at the peak for distance. |
> | Slide | Steer a fast line down, picking up coins, fastest time wins. |
> | Seesaw | Keep the plank level for 30 seconds with a partner or a groundskeeper. |
> | Merry-go-round | Stay on as it spins faster. |
> | Monkey bars | A stamina traverse. |
> | Sandbox | Dig for coins against a timer. |
> | Spring riders | Bounce onto targets. |
> | Climbing frame | Climb a route to a prize. |
>
> **Physics.** Kickable balls and toys, pushable furniture, throwable items, dropped loot, doors and barricades, water. Not ragdoll monsters. Applies everywhere. The playground is the best first test.
>
> **Monsters.** Every monster has a custom kill animation, and the number of hits to kill you differs by monster. After a kill: depends on the monster, fade to a random respawn spot, a stats screen, a short replay.
>
> **Cameras.** A sighting sends agents and sounds an alarm in that area, only in restricted areas. Cut the breaker or smash cameras: they stay damaged until fixed, and this can hurt players. Agents are killable.
>
> **Co-op.** Parties group by game so friends can join whenever, like Roblox's multi-lobby system. Hide and seek with friends: either side seeks.
> - Built: rooms of up to 10 on a Node server, with the monsters simulated on the server at 20 Hz. [BUILT]
> - Room size is 10. Co-op inside the games is optional: players enter any game alone or together, and friends can pop in at any time, so a party of 10 can split across levels and games. Today the gates to Right Door, Wrong Exit and the Intern are solo only. [SETTLED]
> - A death is a down nobody revived. Revives given are counted and add to the total score. [SETTLED]
>
> **Accounts and saves.** Account-based. Checkpoints plus beds and safe houses. Achievements plus a found-things list. Online leaderboard. None of this exists yet. The best time is stored per browser.
>
> ## 6. Scene budget (rough)
>
> | Area | Hand-built | Templated or reused |
> |---|---|---|
> | Overworld and forest | about 6 | |
> | Look Over There original floors | 5 (exist) | |
> | Going back in, version 1 | 15 new chambers | 5 existing floors |
> | Right Door, Wrong Exit | about 43 new rooms | 7 exist |
> | Hotel | about 35 scenes | 50 rooms from a handful of layouts |
> | Mall | about 18 scenes | connectors |
> | Grocery | about 5 scenes | |
> | Secret Operations | about 12 scenes plus boss | reskinned chambers |
> | Job addons | 4 to 5 games | |
>
> This is on the order of 150 hand-built spaces. The photos are all AI-generated, so they are references to recreate. Use them as textures only after checking the generator's terms.
>
> ## 7. Technology and plan
>
> - **Corrected from v1:** there is already a backend. A Node server (`server/server.js`, a Dockerfile, deployed to Railway) runs rooms of up to 10. It simulates the monsters per floor at 20 Hz, owns each player's HP, rounds and downs, and has message rate limits. The rules are shared with solo play in `shared/`. [BUILT]
> - **What the server lacks for the plan:**
>   - accounts and saves;
>   - an online leaderboard (best time is per browser);
>   - parties that split across levels and games, and join at any time;
>   - gates and addons inside rooms.
> - **The key integration point.** The server accepts only the five floors (`FLOORS` in `shared/world.js`, plus the puzzle and loot tables). New scenes, chambers and addons must be added there, so the manifest must drive that list or every addon needs a server change.
> - **Unverified:** a real controller, the live site after the merge, Safari, and the speeds. The unit tests pass; the browser flows were not all driven.
> - The owner's stated order: connection system and shared save, then the physics decision, then the Overworld from the existing exterior, then the options screen and safe houses, with a world manifest soon. Overworld, city, manifest and physics come before the hotel, mall, grocery, Going back in and Secret Operations. [SETTLED]
> - Weeks to months, no time limit, the owner and the planning assistant, one repo. [SETTLED]
> - Backend decided: PostgreSQL on Railway (Hobby now, Pro when needed), anonymous start and Discord sign-in, audience 18 and over. See `docs/BACKEND.md`. [SETTLED]
> - Addons are folders in one repo, loaded on demand through the manifest. [SETTLED]
> - A small editor for doors, spawn points and links. [SETTLED]
>
> ## 8. Version 0 [MY CALL]
>
> The smallest version where the world feels real:
> - Finish Look Over There, walk out onto the parking lot, and get the results with deaths and the welcome to Farway.
> - The Overworld with the table, store, parking lot, one sky mode and the road to the forest.
> - A bus to one short city street with the apartment, the Intern's job at 666 Hallam Row, the grocery and the night rule.
> - Everything else as a facade, reserved in the manifest.
>
> ## 9. Proposals for what you left open [MY CALL]
>
> - Three city anomalies: a shop sign that changes one letter each time you pass; pedestrians that all face the same direction; a lit window in a building that is not there.
> - Intern application questions: sort tasks, match a form to a day, then slowly more intrusive ones (who knows where you are, who would notice if you were gone).
> - Secret Operations reskin: all five floors' chamber pools plus unique lab and corridor sections.
> - Off limits: real names and cases, graphic harm, real-money gambling, committing keys, and changing the original floors' collision data without the tests.
> - Lore: the Overworld is the holding area, a safe-looking world that makes the taken feel fine. Red means flagged by the system. The hum is the servers. The final secret is that the player was taken too.
>
> ## 10. Still open
>
> 1. The score formula, and whether a board ranks by time or by score.
> 2. Name for the Going back in locker, since the existing locker is a one-time pickup.
> 3. Ranking: deaths, an online leaderboard and accounts need a backend the owner has not chosen yet.
> 4. Company names for the Hallam Row jobs, if you want them.
> 5. Lore truths per area.
> 6. How the arsenal's ammo works, since only the ray has rounds today.
> 7. The Intern's redesign.
>

## 12. Full commit log (date, hash, subject)

Every commit, oldest first. Merge commits are shown with their subjects.


### 2026-11

- 2026-11-01 3e06200f Initial commit
- 2026-11-01 4c304650 Add walkable build, Blender file and Pages workflow
- 2026-11-01 d7452043 Rebuild furnishing: orderly rooms, no distortion, more fire safety, cameras per room
- 2026-11-01 d2b0a99d Fix stairs to the showroom; add monsters that patrol, see, chase and kill
- 2026-11-01 4e2ed1b5 Add the Meshy creature as the monster, with generated idle/walk/run/attack clips
- 2026-11-01 092e20dc Closed doors, crouch, handheld camera/map device, B1 start, per-floor monsters
- 2026-11-01 5730d7e1 Make the gamepad left trigger crouch (Shift)
- 2026-11-02 b701c103 Right Door, Wrong Exit in-world: stairwell gate on the lawn opens the dining room, original walk modules vendored, controller support
- 2026-11-02 613c0cf3 RDWE rooms larger: walker scaled 1/1.7 (room coordinates untouched), shadow maps freed on exit
- 2026-11-02 1dc76226 The Intern in-world: sidewalk apartment door opens the original game (own window, scaled walker, controller), returns on its ending
- 2026-11-02 68a03e7a Final Blender file: stair doors, gates, stacked site levels removed; build scripts for the new steps
- 2026-11-02 892c8c2e Ceilings for every floor scene, walkability fixes (L1 sealed room, lot-to-street gap), unified controls: walk/run/crouch/jump in every game, left trigger runs
- 2026-11-02 bc6a8598 Walkable transition passage between every door pair
- 2026-11-02 3f0b4846 Blender file updated: ceilings, walkability fixes
- 2026-11-03 5004cae1 Stairs in their level's finish, full ceilings, seen-not-walked hallway behind stair doors, one prop of each kind on B1/L1/L2
- 2026-11-05 e8c5706d Tests: both ends of a test pair must be on the walkable main region (the merged geometry has clear lines off the map)
- 2026-11-05 ec8b91fb Cloak short circuit (stun blast, cloak dead for 5 min) and beacon reverse: shared rules, server floors and tests
- 2026-11-05 016bd22a Universal controls: held items and the Y wheel, crouch toggle, run on R / right stick, X action, RT/LT primary and secondary, cloak short circuit, beacon reverse; cameras off the controls
- 2026-11-05 7da6844d controls test reads the held state; HELD and AIM exported for tests
- 2026-11-05 6cc54b54 controls test: taps are one frame pair
- 2026-11-05 e496cb2b controls test: fix the rotation sequence
- 2026-11-05 d94f26d0 Docs: the universal controls, the cloak's short circuit, the beacon's reverse
- 2026-11-05 6eb3a8f8 solo test: spawn-lean threshold for the merged geometry, longer level-load wait
- 2026-11-05 6c4bcb1f Merge pull request #2 from groot99-droid/claude/stoic-cannon-dej2nw [merge]
- 2026-11-06 b6b73d76 Docs: the manifest, the round requirements, the session plan, the Farway world bible
- 2026-11-06 b5ab594a World manifest and loader: one place for scenes, floors, puzzles, loot, links and modes
- 2026-11-07 2415f44a Room size 10, parties that split across places, deaths and revives in the score
- 2026-11-07 eb384636 Backend plan: Postgres on Railway, anonymous start, Discord sign-in
- 2026-11-08 104efd81 Session plan: build what the game needs now, backend later, add a session to tune the Original
- 2026-11-08 47a1d91e Merge pull request #3 from groot99-droid/claude/manifest-loader [merge]
- 2026-11-08 43f969fa Results v2, local: per-player counters, run record log line, score, results screen
- 2026-11-08 802bd196 Tune B1: 20 s down time, 6 ammo packs on B1; bots get a --bold mode
- 2026-11-08 35ecf0e6 Gate return: Right Door, Wrong Exit returns to L4 (gates test, enterGame reads the manifest)
- 2026-11-08 d2e19167 Session 12: bot results for B1 levers, playtest checklist, status
- 2026-11-10 91f050c9 Merge pull request #5 from groot99-droid/claude/gate-return [merge]
- 2026-11-10 5963bf42 Merge main into results-local (resolve SESSIONS.md status rows) [merge]
- 2026-11-10 1453dd2e solo_test: B1 now has 6 packs (pinned count updated on purpose)
- 2026-11-10 932b9b67 Merge pull request #4 from groot99-droid/claude/results-local [merge]
- 2026-11-10 95970823 Merge main into claude/tune-original (keep 20 s down time on top of the new stats) [merge]
- 2026-11-10 76ce5f22 Modes and parties: join with a mode, party key, GET /rooms, goto a friend, lobby mode and open rooms, 10-player checks
- 2026-11-10 d2fed5b8 Physics: decision document and isolated prototype (tools/physics)
- 2026-11-10 3e4be275 Overworld v0: parking lot after the Original, table spawn, store-doors options screen
- 2026-11-10 3ab0fec5 Merge pull request #6 from groot99-droid/claude/tune-original [merge]
- 2026-11-10 58585b7a Merge remote-tracking branch 'origin/main' into v7 [merge]
- 2026-11-10 5fa11130 Physics: owner chose cannon-es; document rewritten around it, with 50-body measurement
- 2026-11-10 395f8018 mp_test: count data rows now that the results table has a header row
- 2026-11-10 53574e93 Merge pull request #7 from groot99-droid/claude/modes-parties [merge]
- 2026-11-10 83b1f1d1 Merge main into overworld-v0 (resolve SESSIONS.md status rows) [merge]
- 2026-11-10 235d2155 SESSIONS.md: session 1 row says merged
- 2026-11-10 9455c238 Merge main into physics-decision (SESSIONS.md status rows) [merge]
- 2026-11-10 c2d475be SESSIONS.md: fix merged status rows
- 2026-11-10 59a6d7bc Merge pull request #8 from groot99-droid/claude/physics-decision [merge]
- 2026-11-10 ef302c7e Merge main into overworld-v0 (physics merged; SESSIONS.md rows) [merge]
- 2026-11-10 ec51aa57 Merge pull request #9 from groot99-droid/claude/overworld-v0 [merge]
- 2026-11-10 d57c10a8 City v0 slice 1: bus to Hallam Row, 15-minute day clock, stores close at night
- 2026-11-10 aed21777 Going back in, slice 1: chambers in the manifest, a wave on entry, stairs down, options screen enabled (solo)
- 2026-11-11 357194d8 Going back in, slice 2: pure rules for the crossbow and the locker, and the browser test (red)
- 2026-11-11 b73bc166 City v0 slice 2: the apartment interior with its computer
- 2026-11-11 cf212833 Going back in, slice 2: the loadout locker and the hunting crossbow (solo)
- 2026-11-11 5d9bd346 gbi2_test: make the test player immune to the live wave (it was killed mid-test once)
- 2026-11-11 37e1b1cc solo_test: stage a spot with room for the cloak, beacon and health checks
- 2026-11-11 659a9afb Going back in, slice 3: pure consumable rules and the browser test (red)
- 2026-11-11 251db24d City v0 slice 2: the night danger (the stalker from midnight to 06:00) and a bed that skips the night
- 2026-11-11 b2564d21 Going back in, slice 3: the Q and E consumables (flash-vial, land mine, tripwire), solo
- 2026-11-11 43372d3f Merge pull request #12 from groot99-droid/claude/solo-test-stable [merge]
- 2026-11-11 b1baf71c solo_test: hold the finale alarm open and close the first page before the second
- 2026-11-12 958ad4de Merge main into city-v0 (SESSIONS.md rows) [merge]
- 2026-11-12 06f03543 Merge main into solo-test-stable [merge]
- 2026-11-12 53ace355 City v0 slice 3: the Intern's job through the shared application quiz
- 2026-11-12 67bf7462 Merge pull request #11 from groot99-droid/claude/city-v0 [merge]
- 2026-11-12 2995ad01 Merge main into going-back-in (City v0 merged first): keep both sides in index.html, manifest tests and docs [merge]
- 2026-11-12 1c244578 City v0 slice 4: hunger and the grocery
- 2026-11-12 778c748b Merge pull request #10 from groot99-droid/claude/going-back-in [merge]
- 2026-11-12 8481906b Merge main into city-v0-intern (Going back in merged): keep both sides [merge]
- 2026-11-12 bbe3ffbe Merge city-v0-intern (now carrying main's Going back in) into city-v0-grocery: keep both sides [merge]
- 2026-11-12 85003c54 Merge main into solo-test-stable [merge]
- 2026-11-12 87d5c663 mp_test: remove two timing races a slow page loses (door open, monster heard a noise)
- 2026-11-12 18fb8dc9 City v0 slice 5: pay by performance for a shift at the Intern
- 2026-11-12 b16a87c5 mp_test: wait for the server's view before actions that depend on it; park the L1/L2 monsters where they can reach the noise
- 2026-11-12 87d54331 mp_test: compare monsters once both pages follow the server's stopped monsters; wait for the server's view before the L4 far switch
- 2026-11-12 3944c1e7 mp_test: wait for the server to have the player in place, not for a monster's search
- 2026-11-12 5544377a Merge pull request #13 from groot99-droid/claude/solo-test-stable [merge]
- 2026-11-12 f82383b7 City v0 slice 6: the other four jobs (applications, flags and stub shifts)
- 2026-11-12 70fda720 Fix the #10 merge: keep Going back in enabled on the options screen
- 2026-11-12 d20a0386 Merge the #15 fix (Going back in enabled on the options screen) into city-v0-pay [merge]
- 2026-11-12 64b088e8 Merge city-v0-pay (with the #15 options-screen fix) into city-v0-jobs [merge]
- 2026-11-12 9ed0977e Merge city-v0-jobs (with the #15 options-screen fix) into city-v0-save [merge]
- 2026-11-12 342f25d1 City v0 slice 7: saving the City at the bed
- 2026-11-12 7007c649 mp_test: print what the page and the server see when the locker or note check fails
- 2026-11-12 6f495128 Merge pull request #14 from groot99-droid/claude/city-v0-intern [merge]
- 2026-11-12 25177edf Merge main into city-v0-grocery (Going back in and the Intern's job merged first): keep both sides; session 9 status row [merge]
- 2026-11-12 ad07dc83 docs: session 14 row in the status table
- 2026-11-12 ea674aaf Merge pull request #15 from groot99-droid/claude/city-v0-grocery [merge]
- 2026-11-12 49938990 Merge main (slices 1 to 4 merged) into city-v0-pay: keep both sides [merge]
- 2026-11-12 0d1c46b4 Merge city-v0-pay (now with main's slices 1 to 4) into city-v0-jobs: keep both sides [merge]
- 2026-11-12 1295d5b4 Merge city-v0-jobs (now with main's slices 1 to 4) into city-v0-save: keep both sides [merge]
- 2026-11-12 609d2508 mp_test: wait for the server to hear a teleported player before acting; compare stopped monsters
- 2026-11-12 dc8d5aba Merge city-v0-jobs into city-v0-save: the city_test job search fix [merge]
- 2026-11-12 703f7892 city_test: the job search now lists all five jobs as hiring (slice 6 opened the other four)
- 2026-11-12 4f5b749d docs: session 14 row says PR #17 is ready for review
- 2026-11-12 df31f76d Merge pull request #16 from groot99-droid/claude/going-back-in [merge]
- 2026-11-12 ee41350d Merge main into mp-test-stable (session 13's mp_test fixes merged first) [merge]
- 2026-11-12 a07039f6 City slice 8: the three city anomalies (the sign that changes a letter, the pedestrians who face one way, the window with no building)
- 2026-11-12 b397a33f City slice 9: New Game on the computer's SYSTEM page, and the bank says when the City was last saved
- 2026-11-12 7e2f864e City slice 10: the stalker follows you: at night it waits outside your apartment door
- 2026-11-12 d0ed5621 Merge pull request #17 from groot99-droid/claude/mp-test-stable [merge]
- 2026-11-12 ca1f5822 Merge remote-tracking branch 'origin/main' into v19 [merge]
- 2026-11-12 3d3370e2 docs: session 14 row says merged (PR #17)
- 2026-11-12 3cd331b4 Merge main into solo-test-stable: keep main's mp_test fixes, add only what it lacks [merge]
- 2026-11-12 d7bc3906 City slice 11: the trash truck worker's route on Hallam Row, paid by the bins
- 2026-11-12 8642e05e Merge pull request #22 from groot99-droid/claude/mp-test-stable [merge]
- 2026-11-12 30e6d1a5 docs: session 8 row says slices 1 to 3 merged (PR #10) and the mp_test fix (PR #16)
- 2026-11-12 b89b6e13 Merge pull request #23 from groot99-droid/claude/going-back-in [merge]
- 2026-11-12 98955a86 newgame_test: the clock has run two frames since New Game, so check it is under a second, not exactly 0
- 2026-11-12 5520728b Merge claude/city-v0-newgame: the newgame_test clock check [merge]
- 2026-11-12 86c12117 Merge claude/city-v0-stalker: the newgame_test clock check [merge]
- 2026-11-12 091a5e99 City slice 12: rest, the second need: drains awake, warns, you pass out at 0; the bed refills it and naps by day
- 2026-11-12 e3b7c732 Merge branch 'v19' into v20 [merge]
- 2026-11-12 279b8261 Merge pull request #19 from groot99-droid/claude/city-v0-pay [merge]
- 2026-11-12 bea45bb5 City slice 13: the mall locks you in: in by day, locked from 20:00 to 06:00, benches to sleep on
- 2026-11-12 d2d6cb9d City slice 14: the museum night guard: statues that move only while you are not looking
- 2026-11-12 fdb76f25 Merge remote-tracking branch 'origin/main' into v20 [merge]
- 2026-11-12 d8d175f9 Merge pull request #20 from groot99-droid/claude/city-v0-jobs [merge]
- 2026-11-12 dbb780da Merge remote-tracking branch 'origin/main' into v21 [merge]
- 2026-11-12 145c41ed City slice 15: report the anomalies: spot them on the street, report them on the computer
- 2026-11-12 785f036f City slice 16: the factory floor: sort parts off a conveyor belt into the right bins
- 2026-11-12 ff5bd1d6 Merge pull request #21 from groot99-droid/claude/city-v0-save [merge]
- 2026-11-12 d47a55ba follow_test: measure the stalker's wait 14 m along the street (it stands on the road, so it is further than 14 m in a straight line)
- 2026-11-12 9d913724 Trash route: the bus ends the shift before you ride (the City's tick, which ends it on leaving, does not run in the Overworld)
- 2026-11-12 ae689af9 Merge claude/city-v0-stalker: the follow_test check and the trash route's bus fix [merge]
- 2026-11-12 40f1b21e Merge claude/city-v0-trash: the follow_test check and the trash route's bus fix [merge]
- 2026-11-12 4109da57 Merge claude/city-v0-sleep: the follow_test check and the trash route's bus fix [merge]
- 2026-11-12 08ffd299 Merge claude/city-v0-museum: the follow_test check and the trash route's bus fix [merge]
- 2026-11-12 7aa6d50e Merge claude/city-v0-report: the follow_test check and the trash route's bus fix [merge]
- 2026-11-12 e6716d65 Merge claude/city-v0-mall: the follow_test check and the trash route's bus fix [merge]
- 2026-11-12 abcf5f5e Merge remote-tracking branch 'origin/main' into v24 [merge]
- 2026-11-12 131269f1 City slice 17: the laboratory: follow procedure cards from station to station (the last stub becomes a game)
- 2026-11-12 fbca5219 Merge claude/city-v0-sleep: the rest_test tolerance [merge]
- 2026-11-12 43b961e8 rest_test: allow 10% on the drain rate (the page's own frame loop also runs between the test's steps)
- 2026-11-12 ab7f592c Merge claude/city-v0-museum: the rest_test tolerance [merge]
- 2026-11-12 bb2d6e69 Merge claude/city-v0-factory: the rest_test tolerance [merge]
- 2026-11-12 b91f6733 Merge claude/city-v0-report: the rest_test tolerance [merge]
- 2026-11-12 4b72e344 Merge claude/city-v0-mall: the rest_test tolerance [merge]
- 2026-11-12 23950d11 City slice 18: pedestrians with routines: they walk their beats while you are not looking, and stand still when you are
- 2026-11-12 b2987fbf Merge claude/city-v0-sleep: the grocery_test hunger warning check [merge]
- 2026-11-12 09ac601d grocery_test: give the hunger warning check 8 frames (the HUD redraws every 0.2 s of City time; 4 frames sat exactly on that boundary) and print what it saw
- 2026-11-12 516fdbd9 Merge claude/city-v0-lab: the grocery_test hunger warning check [merge]
- 2026-11-12 09ebae2e Merge claude/city-v0-museum: the grocery_test hunger warning check [merge]
- 2026-11-12 1a89031a Merge claude/city-v0-factory: the grocery_test hunger warning check [merge]
- 2026-11-12 bb46c110 Merge claude/city-v0-report: the grocery_test hunger warning check [merge]
- 2026-11-12 3358c367 Merge claude/city-v0-mall: the grocery_test hunger warning check [merge]
- 2026-11-12 0c37eeb8 Merge pull request #24 from groot99-droid/claude/city-v0-anomalies [merge]
- 2026-11-12 7a5572c0 Merge remote-tracking branch 'origin/main' into v25 [merge]
- 2026-11-12 6620a71e mp_test: wait on state for the L1/L2 noise checks and the L2 doors
- 2026-11-12 b87fc582 CI: run tools/mp_test.mjs on pull requests
- 2026-11-12 8e0e19dc CI: run the unit tests and the manifest check on pull requests too
- 2026-11-12 e6a2cfb4 Merge pull request #25 from groot99-droid/claude/city-v0-newgame [merge]
- 2026-11-12 9964e84d Merge remote-tracking branch 'origin/main' into v26 [merge]
- 2026-11-12 9b61cb67 Merge pull request #28 from groot99-droid/claude/quirky-ramanujan-qajuxd [merge]
- 2026-11-12 fc2258e0 Museum and trash shifts: do not tick while a scene loads (passing out jumped the clock past the shift's end first, so the shift ended as done, paid in full, and sent you to the street)
- 2026-11-12 5f4e3ee3 Merge claude/city-v0-lab: shift ticks wait while a scene loads [merge]
- 2026-11-12 2d38fe2a Lab shift: do not tick while a scene loads (the same fix as the museum's)
- 2026-11-12 54b46036 Factory shift: do not tick while a scene loads (the same fix as the museum's: passing out mid-shift must lose the shift, not finish it)
- 2026-11-12 f97a867d Merge claude/city-v0-museum: shift ticks wait while a scene loads [merge]
- 2026-11-12 7220f82f Merge claude/city-v0-factory: shift ticks wait while a scene loads [merge]
- 2026-11-12 2f3d9518 Merge claude/city-v0-report: shift ticks wait while a scene loads [merge]
- 2026-11-12 f7eaebfc City slice 19: stealing and the grocery's camera: walk out unseen and keep it, or be fined
- 2026-11-12 b373cbaf Merge remote-tracking branch 'origin/main' into v26 [merge]
- 2026-11-12 255dface Merge pull request #26 from groot99-droid/claude/city-v0-stalker [merge]
- 2026-11-12 0ba10142 Merge remote-tracking branch 'origin/main' into v27 [merge]
- 2026-11-12 f704db68 City slice 20: the HUD's layout: the job on its own line, and the toast below the HUD while it is up
- 2026-11-12 5a260f81 Merge pull request #27 from groot99-droid/claude/city-v0-trash [merge]
- 2026-11-12 0be14dc0 Merge remote-tracking branch 'origin/main' into v29 [merge]
- 2026-11-12 ace7262f mp_test: record each page's teleports and print them when a player is not where the test put them
- 2026-11-12 d38f4388 Merge pull request #29 from groot99-droid/claude/city-v0-sleep [merge]
- 2026-11-12 519eebd4 Merge remote-tracking branch 'origin/main' into v30 [merge]
- 2026-11-12 d605ba01 City slice 21: the watchers: dark figures in three lit windows at night that turn to follow you
- 2026-11-12 e68458f9 Merge pull request #30 from groot99-droid/claude/city-v0-mall [merge]
- 2026-11-12 a503929f Merge remote-tracking branch 'origin/main' into v31 [merge]
- 2026-11-12 ccc3e315 Merge pull request #32 from groot99-droid/claude/quirky-ramanujan-qajuxd [merge]
- 2026-11-12 5c546bdc Slice 19 fix: import the grocery camera's camSees as shopCamSees (index.html already has the Original's camSees, so the page failed to parse and the lobby never appeared)
- 2026-11-12 39f1db12 Merge claude/city-v0-theft: the shopCamSees fix, the page parse test and the theft_test fix [merge]
- 2026-11-12 254080ee theft_test: read the camera's angle and the clock in one call (the page's own frame loop moved the clock between two calls)
- 2026-11-12 b6fd7fa4 Merge claude/city-v0-hud: the shopCamSees fix, the page parse test and the theft_test fix (the import line keeps both windowSlots and shopCamSees) [merge]
- 2026-11-12 3b84f793 Merge remote-tracking branch 'origin/main' into v31 [merge]
- 2026-11-12 5c3664c1 Merge pull request #31 from groot99-droid/claude/city-v0-museum [merge]
- 2026-11-12 e1dc98fc Merge remote-tracking branch 'origin/main' into v33 [merge]
- 2026-11-12 b053a328 Merge pull request #33 from groot99-droid/claude/city-v0-report [merge]
- 2026-11-12 23bbc711 Merge remote-tracking branch 'origin/main' into v34 [merge]
- 2026-11-12 d985b8df Merge pull request #34 from groot99-droid/claude/city-v0-factory [merge]
- 2026-11-12 ec21bb89 Merge remote-tracking branch 'origin/main' into v35 [merge]
- 2026-11-12 0ae31261 Merge pull request #35 from groot99-droid/claude/city-v0-lab [merge]
- 2026-11-12 d94f712b Watchers: stand against the outside of the pane so they can be seen
- 2026-11-12 2f9d1719 watchers_test: face away from every figure until the step that looks at one
- 2026-11-13 f9a3e067 Merge pull request #36 from groot99-droid/claude/city-v0-routines [merge]
- 2026-11-13 43f5fcd1 Merge pull request #37 from groot99-droid/claude/city-v0-theft [merge]
- 2026-11-13 a70b8457 Merge pull request #38 from groot99-droid/claude/city-v0-hud [merge]
- 2026-11-13 c80db325 Merge pull request #39 from groot99-droid/claude/city-v0-watchers [merge]
- 2026-11-14 dc67c44e SESSIONS.md: current status (City slices 1 to 21, Going back in 1 to 3) and round 4 (sessions 15 to 17)
- 2026-11-14 c9ae4fb6 Merge pull request #40 from groot99-droid/claude/sessions-round-4 [merge]
- 2026-11-14 4ff2b362 Rooms can walk out to the parking lot together (presence only)
- 2026-11-14 99eecb3b Going back in in rooms, slice 1: the server runs the chambers and starts each wave once
- 2026-11-14 f572df23 The bus to Hallam Row in a room, and go to a friend in the page
- 2026-11-14 8533419a Going back in in rooms, slices 2 and 3: the server owns bolts, kills, the loadout and the consumables
- 2026-11-14 f6a007c7 In the City the room's HUD line says only presence is shared (a toast was replaced by the next one)
- 2026-11-14 c7fba1b3 mp_test: guard the finale players from the moment they join, and wait for the server at the L4 switch
- 2026-11-14 70ef98d2 SESSIONS.md: session 16 status (Going back in in rooms, slices 1 to 3)
- 2026-11-14 be73b5a6 SESSIONS.md: session 17's row (slices 1 to 3 in draft PR #41)
- 2026-11-14 517c9ac5 mp_test: guard a finale player once the round has started, not before
- 2026-11-14 f9757709 mp_test: the finale press waits only for what it needs (the server's floor for Xia, her page's reach)
- 2026-11-14 d0b38d3d mp_test: the main room's arrival on a floor gets the finale's 170 s, and says what the server saw if it fails
- 2026-11-14 7b76b65b SESSIONS.md: session 15 status
- 2026-11-15 f65444aa Session 18: docs/ITEMS.md, proposed rules for every item
- 2026-11-15 32f05cdf ITEMS.md: Spicy Brew per the owner's relayed rule
- 2026-11-15 0b000113 Item models: the owner's 24 Meshy models (arsenal, consumables, dealer items, food, extras)
- 2026-11-16 7ba98274 Merge pull request #45 from groot99-droid/claude/item-models [merge]
- 2026-11-16 952f5c3a Merge pull request #44 from groot99-droid/claude/item-rules [merge]
- 2026-11-16 34a5f648 Merge remote-tracking branch 'origin/main' into v42 [merge]
- 2026-11-16 879ed842 Build the pneumatic bolt driver (solo Going back in)
- 2026-11-16 68fcf452 Merge pull request #42 from groot99-droid/claude/gbi-rooms [merge]
- 2026-11-16 f4f877c4 Merge main into bolt-driver; keep the driver solo-only (SOLO_GEAR) [merge]
- 2026-11-16 d316f2e7 Merge main into claude/world-rooms: Going back in rooms meet session 17's presence scenes [merge]
- 2026-11-16 0325f93c Build the stun baton, the two-weapon carry cap and the weapon slots (solo Going back in)
- 2026-11-16 d62f0e14 Build the moth jelly dart and the Slowed and Jellied statuses (solo Going back in)
- 2026-11-16 2c471faa Build the propane flamethrower and the Burning status (solo Going back in)
- 2026-11-16 581e5597 Merge pull request #41 from groot99-droid/claude/world-rooms [merge]
- 2026-11-16 9ed3b484 Merge main into mp-test-finale (#43) [merge]
- 2026-11-16 a7695499 Merge pull request #43 from groot99-droid/claude/mp-test-finale [merge]
- 2026-11-16 c15852f6 Merge main into the weapons stack tip (#49): keep both sides of the window.__game list [merge]
- 2026-11-16 7a5271f9 Merge pull request #49 from groot99-droid/claude/flamethrower [merge]
- 2026-11-16 56b09994 The fuse: the owner's Meshy model at models/fuse.glb
- 2026-11-16 efdb4222 Merge pull request #50 from groot99-droid/claude/fuse-model [merge]
- 2026-11-16 bc56b4cb The land mine and the nail-bomb tripwire are drawn with the owner's Meshy models
- 2026-11-16 87d66197 Merge pull request #51 from groot99-droid/claude/trap-models [merge]
- 2026-11-16 4b586a0a The lobby: Solo pressed before the open-rooms list returns no longer throws
- 2026-11-16 01256235 Merge pull request #52 from groot99-droid/claude/lobby-rooms-race [merge]
- 2026-11-19 ab80018a docs: README covers Farway's modes, consumables and the stale Railway branch; sessions 15-22 merged; ray gun and five weapons built
- 2026-11-19 ede43502 Merge pull request #53 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
- 2026-11-19 f66c9d12 The hunting crossbow in your hands is the owner's Meshy model
- 2026-11-19 5b624b02 Merge remote-tracking branch 'origin/main' into claude/crossbow-model [merge]
- 2026-11-19 32408b9e Merge pull request #54 from groot99-droid/claude/crossbow-model [merge]
- 2026-11-19 b661a501 The bolt driver, stun baton, moth jelly dart and flamethrower in your hands are the owner's Meshy models
- 2026-11-19 48ee9ac8 Design note for co-op inside the games (session 11, slice 1)
- 2026-11-19 b0819307 Games inside parties, slice 2: game rooms as presence places in the manifest and the server
- 2026-11-19 a926a764 Build the frequency horn (solo Going back in)
- 2026-11-19 95d0aadb Merge pull request #56 from groot99-droid/claude/held-weapon-models [merge]
- 2026-11-19 e8568763 Build the rocket launcher (solo Going back in)
- 2026-11-19 742f1455 The ammo pack is the owner's Meshy model; the dreamcore meadow's shed is stored for its scene
- 2026-11-19 e914cb4b Merge pull request #58 from groot99-droid/claude/ammo-pack-model [merge]
- 2026-11-19 636fe52a The dreamcore forest and meadow: the road from the lot, the path, the gap, the shed and the house
- 2026-11-19 2ce362e9 Build the laser pointer dissector (solo Going back in)
- 2026-11-19 75090b8a Merge pull request #60 from groot99-droid/claude/dreamcore-forest [merge]
- 2026-11-19 782813ef The hydraulic rebar shear and the chamber barricades (solo Going back in)
- 2026-11-19 7b72dd28 Horn test: stage the knockback lines on floor the knockback can cross
- 2026-11-19 b969eb03 Merge remote-tracking branch 'origin/main' into claude/frequency-horn [merge]
- 2026-11-19 28780898 Merge commit 'b969eb0' into claude/rocket-launcher [merge]
- 2026-11-19 66e39266 Merge branch 'claude/rocket-launcher' into claude/laser-dissector [merge]
- 2026-11-19 d535aa2e Merge branch 'claude/laser-dissector' into claude/rebar-shear [merge]
- 2026-11-19 57d8488b Merge remote-tracking branch 'origin/main' into v55 [merge]
- 2026-11-19 d0ddc041 Merge branch 'v55' into vtip [merge]
- 2026-11-19 16eccf96 Combine main, #55 and the weapon stack for testing; #55's coop test now uses the hotel as its planned area (the forest is built)
- 2026-11-19 6bb35fcb coop test: use the hotel as the planned area (the dreamcore forest is built now)
- 2026-11-19 e1da42bf Merge branch 'v55' into vtip [merge]
- 2026-11-19 a5ca0be6 gbi2 test: the locker now has eleven rows after a death (the rebar shear)
- 2026-11-20 feae6565 horn_test: the knockback-0.5 case needs a line clear past 13 m, as the first case does
- 2026-11-20 8888cc5d Merge pull request #55 from groot99-droid/claude/games-in-parties [merge]
- 2026-11-20 0db6c2d3 Merge pull request #61 from groot99-droid/claude/laser-dissector [merge]
- 2026-11-20 a152ac8d Merge pull request #62 from groot99-droid/claude/rebar-shear [merge]
