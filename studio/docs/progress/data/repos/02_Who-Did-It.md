# Who-Did-It

**Multiplayer hidden-role game (HollowMere), Phaser client, Colyseus server.** Source: https://github.com/groot99-droid/Who-Did-It

Generated 20 November 2026 from the repository clone (`git log`, `git ls-files`, and the files at HEAD). Counts are as cloned. Commit dates are git author dates in UTC and can differ from when the work was done (merged PRs, integration passes).

## 1. Numbers

| Measure | Value |
|---|---|
| Commits (all branches) | 2824 (1400 non-merge, 1424 merge) |
| First commit | 2026-10-10 |
| Last commit | 2026-11-20 |
| Days with commits | 30 |
| Tracked files | 2698 |
| Checked-out branch | HEAD |
| Commit authors (non-merge, by name) | Claude: 1256; groot99-droid: 140; 6Z: 2; 8N: 1; 10X: 1 |

Author names are git author names: "Claude" marks commits made by a Claude session, and the owner's GitHub handle marks commits made by the owner. Email addresses are left out.

**Tracked files by type (top 15):** .ts 1098; .png 530; .json 459; .webp 172; .md 130; .svg 87; .py 59; .ogg 55; .css 19; .txt 18; .jpg 17; .html 12; .woff2 12; (none) 10; .mjs 5

**Tracked files by top-level folder:** apps 1775; docs 237; packages 232; assets 229; tools 181; LICENSES 22; (root) 18; .github 3; .claude 1

## 2. Activity by month and by day

| Month | Non-merge commits |
|---|---|
| 2026-10 | 1078 |
| 2026-11 | 322 |

**Per day (non-merge commits):** 2026-10-10 46; 2026-10-11 2; 2026-10-15 1; 2026-10-16 60; 2026-10-17 11; 2026-10-18 88; 2026-10-19 3; 2026-10-20 4; 2026-10-22 67; 2026-10-23 254; 2026-10-24 152; 2026-10-25 73; 2026-10-26 2; 2026-10-27 2; 2026-10-29 72; 2026-10-30 241; 2026-11-06 48; 2026-11-07 24; 2026-11-08 35; 2026-11-10 24; 2026-11-11 22; 2026-11-12 65; 2026-11-13 6; 2026-11-14 5; 2026-11-15 3; 2026-11-16 9; 2026-11-17 6; 2026-11-19 71; 2026-11-20 4

## 3. Layout (folders and file counts)

- **apps/** 1775 files
  - apps/client/ 1334
  - apps/server/ 411
  - apps/walk/ 30
- **docs/** 237 files
  - docs/round8/ 99
  - docs/ui/ 30
  - docs/round11/ 24
  - docs/round9/ 14
  - docs/round10/ 10
  - docs/round5/ 10
  - docs/story/ 9
  - docs/round6/ 8
  - docs/round7/ 8
  - docs/PLAYTESTS/ 5
  - docs/guides/ 4
  - docs/accounts/ 1
  - docs/map-revamp/ 1
  - docs/round12/ 1
- **packages/** 232 files
  - packages/content/ 181
  - packages/shared/ 51
- **assets/** 229 files
  - assets/source/ 229
- **tools/** 181 files
  - tools/blender/ 82
  - tools/sprites/ 70
  - tools/auto/ 10
  - tools/bots/ 10
  - tools/grid/ 7
  - tools/world3/ 2
- **LICENSES/** 22 files
  - LICENSES/vendors/ 14
  - LICENSES/fonts/ 6
- **(repository root)** 18 files
- **.github/** 3 files
  - .github/workflows/ 3
- **.claude/** 1 files

## 4. package.json (root)

- name: who-did-it; version: 0.0.0
- scripts: `build`; `lint`; `typecheck`; `test`; `format`; `assets:render`; `docs:protocol`; `bots`; `grid:export`; `bots:soak`; `bots:live`; `bots:story`; `auto`; `e2e`
- devDependencies: @eslint/js, eslint, globals, prettier, typescript, typescript-eslint, vitest

## 5. CI workflows

- `.github/workflows/ci.yml`: CI
- `.github/workflows/pages.yml`: pages
- `.github/workflows/soak.yml`: soak

## 6. Documents inventory (130 Markdown files)

Markdown files by folder (top 25): docs 13; docs/round9 13; assets/source/prompts 11; docs/round8 11; docs/round11 10; docs/round5 10; docs/story 9; docs/round6 8; docs/round7 8; docs/round10 6; docs/PLAYTESTS 5; docs/guides 4; (root) 3; LICENSES/vendors 3; LICENSES/fonts 1; apps/client/src/ui/theme 1; apps/walk 1; assets/source 1; assets/source/renders 1; docs/accounts 1; docs/map-revamp 1; docs/round10/handoffs 1; docs/round11/handoff 1; docs/round12 1; docs/round8/hd-look 1

- `CLAUDE.md` (1075 words): CLAUDE.md — Who Did It. Sections: What this repo is; Read first; Layout; Conventions that must not drift; Connection to the owner's ROSW repo (groot99-droid/Pipelines-Plugin); Compact instructions
- `CREDITS.md` (9526 words): Credits. Sections: Policy; Third-party assets; Generated assets; Hand-made original art (CC BY 4.0, `LICENSE-ASSETS`); The owner's own writing (shelf pages); Adobe generative use
- `LICENSES/fonts/README.md` (267 words): Font licences
- `LICENSES/vendors/README.md` (857 words): Vendor terms. Sections: Recorded links
- `LICENSES/vendors/opengameart-ambience-license-2026-10-18.md` (68 words): (no title)
- `LICENSES/vendors/opengameart-rain-long-thunder-license-2026-10-16.md` (66 words): OpenGameArt entry: "Rain + Long Thunder"
- `README.md` (603 words): Who Did It. Sections: Status; Layout; Related repo; Owner-only admin page (Railway variables); Documents
- `apps/client/src/ui/theme/README.md` (529 words): `apps/client/src/ui/theme`. Sections: Opting a screen in; Rules the tests enforce; Faction secrecy
- `apps/walk/README.md` (1172 words): @wdi/walk. Sections: Opening a world; Hosting the GLB; The GLB contract; Controls; Collision
- `assets/source/MANIFEST.md` (6579 words): Source masters
- `assets/source/prompts/README.md` (121 words): Higgsfield prompt sheets
- `assets/source/prompts/cave-chamber.md` (254 words): (6) Cave chamber with teal moss. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Notes; After generating
- `assets/source/prompts/forest-floor-tile.md` (248 words): (7) Tiling forest floor with fog. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Notes; After generating
- `assets/source/prompts/house-exterior.md` (290 words): (4) House exterior from 40° above. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Notes; After generating
- `assets/source/prompts/note-thumbprint.md` (249 words): (9) Hand-written note with a smeared thumbprint. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Notes; After generating
- `assets/source/prompts/parlour-interior.md` (252 words): (5) Dim parlour from 40° above. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Notes; After generating
- `assets/source/prompts/portrait-bust-deco.md` (275 words): (10) Portrait bust in an Art-Deco frame. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Notes; After generating
- `assets/source/prompts/props.md` (325 words): (8) Single props: brass key, bloodied knife, oil lantern. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Image to 3D; Notes; After generating
- `assets/source/prompts/villager-base-grey.md` (409 words): (2) Generic villager body, flat grey. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Image to 3D; Notes; After generating
- `assets/source/prompts/villager-turnaround.md` (455 words): (1) Villager turnaround sheet. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Image to 3D; Notes; After generating
- `assets/source/prompts/wolf-shadow.md` (298 words): (3) Hunched wolf-shadow. Sections: Prompt; Attach; Tool and settings (`ASSETS.md` 6.9); Image to 3D; Notes; After generating
- `assets/source/renders/README.md` (93 words): Render locks
- `docs/ARCHITECTURE.md` (6696 words): Technical Architecture. Sections: 5. Technical architecture
- `docs/ASSETS.md` (8608 words): Asset Pipeline and Style Guide. Sections: 6. Asset pipeline & style guide
- `docs/DECISIONS.md` (75255 words): Decisions Log. Sections: Decisions locked with the owner (2026-10-09); 8. Decisions & changes from review; 9. Open questions for the owner; Amendments (2026-10-10); Spike results (M0); Open questions added at integration (2026-10-10)
- `docs/GDD.md` (45297 words): Game Design Document. Sections: 1. Vision & pillars; 2. Player experience: the first 10 minutes; 3. Game design
- `docs/MASTER_PLAN.md` (13401 words): Who Did It — Master Plan (V1 top-down 2.5D, V2 first-person). Sections: 1. Vision & pillars; 2. Player experience: the first 10 minutes; 3. Game design; 4. World bible; 5. Technical architecture; 6. Asset pipeline & style guide; 7. Production plan; 8. Decisions & changes from review; 9. Open questions for the owner
- `docs/PLAYTESTS/2026-xx-xx-m2.md` (331 words): 2026-xx-xx, M2 playtest. Sections: Setup; What M2 checks; Bugs; What we learned; Actions
- `docs/PLAYTESTS/FORM.md` (611 words): Feedback form. Sections: Reading the responses; Questions for the later milestones
- `docs/PLAYTESTS/README.md` (3413 words): Playtests. Sections: 1. Owner prerequisites (before inviting anyone); 2. Who and what; 3. Session plan; 4. The match log; 5. The host's script; 6. When something goes wrong; 7. After the session; 8. Quick mode evening (M3b); 9. NPC session (M3c)
- `docs/PLAYTESTS/SCORECARD.md` (1307 words): M3 scorecard: fun or stop. Sections: 0. The bar, set before session 1; 1. Session; 2. Matches; 3. From the form; 4. Session read; 5. Decision line (second session only); 6. M3b, quick mode; 7. M3c, NPC fill
- `docs/PLAYTESTS/TEMPLATE.md` (385 words): YYYY-MM-DD, <milestone> playtest. Sections: Setup; Matches; Bugs; Form summary; Debrief; What we learned; Actions
- `docs/PROTOCOL.md` (4989 words): Wire protocol. Sections: Client to server; Server to client; Payload types; Admin (WDI_ADMIN only); Studio (WDI_ADMIN only); Error codes; Refusal reasons; Join errors
- `docs/README.md` (712 words): Who Did It — documentation
- `docs/RESEARCH.md` (8167 words): Research Log (2026-10-09). Sections: Technology stack and hosting; Asset tooling, libraries and licensing
- `docs/ROADMAP.md` (5329 words): Production Plan. Sections: 7. Production plan
- `docs/SESSIONS.md` (65796 words): Parallel sessions (started 2026-10-10). Sections: Branches and pull requests; Interfaces between sessions; Briefs; Integration log (2026-10-10); Round 2 (started 2026-10-10, after PRs #1 to #6 merged); Integration log, round 2 (2026-10-15); Round 3 (started 2026-10-16, after round 2 landed at a98cc3f); Integration log, round 3 (2026-10-16); Round 4 (started 2026-10-16, after round 3 landed at 2f829e2); Integration log, round 4 (2026-10-17)
- `docs/SPRITES.md` (13540 words): Sprite Conventions. Sections: 1. Cells, scale and directions; 2. Rendered frame files; 3. Atlas keys; 4. Feet pivot manifest; 5. Asset manifest and loading; 6. Overlay passes; 7. Palette tokens; 8. Placeholder keys through M3; 9. UI icons; 10. Isometric projection
- `docs/UI.md` (31131 words): UI design system. Sections: 1. Principles; 2. Palette; 3. Type; 4. Space, radius, stroke, grid; 5. Ink stroke and paper fill; 6. Components; 7. The role card; 8. Shadows and glows; 9. Motion; 10. Accessibility checklist and measured contrast
- `docs/WORLD.md` (5308 words): World Bible and Level Design. Sections: 4. World bible
- `docs/accounts/plan.md` (4373 words): Player accounts: the plan. Sections: 1. What exists today (verified in the tree at `2f70cb5b`); 2. Owner-facing choices, each with a recommended default; 3. Where it sits in the code (paths for the contract); 4. Privacy and role secrecy; 5. The save store (story saves attach here); 6. Migration: how a device becomes an account; 7. Abuse, limits, deletion, export, retention; 8. Split into PRs (each under 400 lines, in order, tests listed); 9. Proposed DECISIONS row (the orchestrator adds it; this session does not); 10. Open questions for the owner (each with its default)
- `docs/guides/ADMIN_GUIDE.md` (409 words): Admin guide: auto-mode. Sections: Turning it on; The page; Replaying a failure; The headless runner
- `docs/guides/HOST_GUIDE.md` (489 words): Host guide. Sections: Making a party; Lobby settings; When something sticks; Running your own server
- `docs/guides/HOW_TO_PLAY.md` (945 words): How to play Who Did It. Sections: Getting in; Controls; Your role card; The loop of a match; Clues and the Notebook; Gathering, crafting, quests, creatures; Winning; Tips for a first game
- `docs/guides/README.md` (112 words): Guides
- `docs/map-revamp/interiors-plan.md` (2356 words): Map revamp: the interiors plan. Sections: 1. What is built (base `753b563`); 2. The interiors that already exist as scenes; 3. The buildings with no place on the map yet; 4. How a 3D interior is built (pipeline); 5. Adding a brand-new building to the game; 6. Order of work; 7. Who does what; 8. Open questions for the owner
- `docs/round10/README.md` (2067 words): Round 10: world mode, the build. Sections: Context; The sessions; Compaction; How a session works; The playtest gate; Status (2026-10-29); Status (2026-10-30): paused
- `docs/round10/handoffs/10A-plans.md` (1050 words): 10A's plans for K1 and T4, with 6Z's answers. Sections: K1. Weapons (I24), after C6; T4. Town work, windows, stations and silhouettes (I37, I38, I39; row 30), after C4c and C4d; Code read at 23cf829d; Branches
- `docs/round10/part2.md` (5551 words): Round 10, part 2: what is left. Sections: Why this file; The state at the stop; Open pull requests and branches at the stop; The merge queue for part 2; Each session's remaining steps; Handoffs; The owner's open questions; How part 2 resumes; The merged-tree check
- `docs/round10/rolecards.md` (14167 words): Round 10 (10R): the role cards and the Satchel. Sections: 0. The brief; 1. The audit; 2. The trifold; 3. Every action and every button; 4. Win conditions and lore, per role; 5. The Satchel; 6. The style; 7. Role secrecy; 8. Phone, desktop and access; 9. The build
- `docs/round10/scope.md` (13872 words): Round 10: the scope census (10S). Sections: 0. The brief; 1. The inventory; 2. The missing design; 3. The wire; 4. The build plan; 5. Questions for the owner
- `docs/round10/seams.md` (9418 words): Round 10 seams: what the sessions share. Sections: 1. Shared files; 2. Ids the plan already fixes; 3. The wire; 4. Paths each session owns; 5. Reserved rows; 6. Invariants and checks; 7. Merge order
- `docs/round10/wave2-briefs.md` (3430 words): Round 10, wave 2: the spawn briefs. Sections: 10N; 10K; 10T; 10M; Common to the four
- `docs/round11/README.md` (1631 words): Round 11: the full Blender makeover (planning, design only). Sections: Context; What the makeover covers; The sessions; Rules for both sessions; Status (2026-10-30)
- `docs/round11/handoff/prop-models.md` (457 words): Who Did It: 3D asset index. Sections: Contents; Conventions; Props: what each is for; Known gaps and flags
- `docs/round11/look.md` (7931 words): Round 11: materials, styles and budgets (11B). Sections: 1. Where the art stands today (2026-10-29); 2. The makeover's look in one paragraph; 3. Materials; 4. The styles; 5. Budgets; 6. Characters; 7. The owner's ROSW 3D pipeline, and where it meets this plan; 8. V2: what a model must carry; 9. The sample sheets; 10. Questions for the owner
- `docs/round11/owner-answers.md` (708 words): Round 11: the owner's answers. Sections: CL3: the long shadows come in round 11; The plan approved (2026-10-30); What three defaults still need from the owner
- `docs/round11/pipeline.md` (5765 words): Round 11, 11A: the render pipeline. Sections: 0. The proposal in brief; 1. What the makeover changes in the pipeline; 2. Camera and scale; 3. Lighting; 4. Render passes; 5. The tooling; 6. Where Blender runs; 7. Where the plan meets ROSW; 8. Sample sheets; 9. Questions for the owner
- `docs/round11/props.md` (5472 words): Round 11: the prop list (P1). Sections: 1. What is listed; 2. The rules used; 3. Totals; 4. The handoff's known gaps, checked against the sheets; 5. The table; 5.1 Not props: hide spots, body spots and buildings; 6. Questions, answered by the owner on 2026-11-19 ("use the defaults"); 7. Method
- `docs/round11/questions.md` (1562 words): Round 11: questions for the owner. Sections: Scope: what the makeover covers; Camera and light; Styles and figures; Budgets; Where and how the renders run
- `docs/round11/round11-plan-v2.md` (2213 words): Round 11, revised: building the sprite world (A615). Sections: 1. What carries over from the approved plan; 2. Rules for every pull request; 3. Sessions; 4. The pull requests; 5. Merge order; 6. Questions for the owner; 7. What it costs, roughly
- `docs/round11/round11-plan.md` (3424 words): Round 11: the build plan (the full Blender makeover). Sections: 1. Rules for every pull request; 2. Sessions; 3. The long shadows (CL3); 4. Tooling and passes; 5. Session 11M: materials and styles (11B's half); 6. The look gate; 7. The art drops; 8. Merge order; 9. Question for the owner
- `docs/round11/seams.md` (499 words): Round 11 seams: who owns what (the sprite world, A616). Sections: 1. The first sessions (started 2026-11-19); 2. Shared files; 3. What no session touches in round 11
- `docs/round11/tiles-brief.md` (1013 words): 11P P2: tiles and wall textures (brief, draft). Sections: 1. What P2 delivers; 2. Format (proposed, R1 must confirm); 3. Sources, in order; 4. Where it lives; 5. Done, and the tests; 6. Proposed `seams.md` row (for the orchestrator); 7. Open questions (proposed defaults, owner or orchestrator)
- `docs/round12/sprite-world.md` (1066 words): The sprite world: the merged 2.5D look (A615). Sections: 1. The look; 2. What it replaces; 3. Constraints that bind the build; 4. Build steps; 5. Owner answers and what is still open; 6. The prototype
- `docs/round5/README.md` (592 words): Round 5: the contract documents
- `docs/round5/art-index.md` (261 words): The owner's ONUB room images (supplied 2026-10-17)
- `docs/round5/art-plan.md` (24647 words): Round-5 art plan: Sessions 5K, 5L and 5M. Sections: 1. Ground rules for all three sessions; 2. Higgsfield workflow and prompt templates; 3. Session 5K: world environment; 4. Session 5L: characters; 5. Session 5M: ONUB art; 6. Order of work, seams and integration; 7. What needs the owner; 8. Calls this plan made beyond the round-5 decisions; 9. Pre-seed: the code that landed; Appendix. The round-5 style: formula, palette and the ASSETS lines that change
- `docs/round5/deck-data.md` (5509 words): Deck data: the main deck, the new roles, Impersonate and the look catalogue (round 5, 5F and 5G). Sections: 1. roles.json; 2. abilities.json; 3. items.json (new rows); 4. balance.json; 5. clues.json and `ClueKind`; 6. looks.json (new file, `packages/content/data/looks.json`); 7. validate.ts (rules to add or change); 8. Content index (`packages/content/src/index.ts`); 9. Art keys for 5L (from this catalogue)
- `docs/round5/deck-wire.md` (10012 words): Deck wire: public looks, avatars, covers and Impersonate (round 5, 5F; with 5G's rules wire). Sections: 1. Schema (`packages/shared/src/schema/index.ts`); 2. Shared constants, pure rules and random streams; 3. Protocol (`packages/shared/src/protocol/index.ts`); 4. Server rules (5F); 5. Rules wire (5G); 6. Privacy invariants (each one a test in section 7); 7. Tests; 8. Hooks, locked call sites and seams (X5, X6); 9. Text for the docs (ARCHITECTURE, SPRITES); 10. Contract phase: what each session removes (X1)
- `docs/round5/npc.md` (10561 words): NPC routines and the NPC tells (round 5, Session 5H). Sections: Part 1. Data and contract; Part 2. Tests
- `docs/round5/onub-contract.md` (19337 words): ONUB v2: the round-5 contract for Sessions 5A to 5E. Sections: 1. Sessions, paths and what is locked; 2. Pre-seed: `@wdi/shared` (landed in 265bda9); 3. Pre-seed: `@wdi/content` (landed in 265bda9); 4. Pre-seed: server seams; 5. Pre-seed: client seams; 6. Private and public, per phase; 7. Frozen `data-testid` hooks; 8. Copy ids: who owns which namespace; 9. Round-4 code: the compile cut and what each session deletes (landed in 265bda9); 10. Seams
- `docs/round5/owner-brief.md` (2999 words): Round 5: the owner's brief and ONUB spec (2026-10-17, verbatim). Sections: The brief; The ONUB spec
- `docs/round5/seams.md` (4576 words): Round-5 seams. Sections: 1. Pre-seeded hooks; 2. Producer -> consumer; 3. Loose ends the pre-seed left outside its paths
- `docs/round5/world.md` (15443 words): Schemas, maps and scene outlines (round 5). Sections: 1. What lands where, and in what order; 2. `packages/content/src/schemas/scene.ts` (whole file); 3. `packages/content/src/schemas/maps.ts` (new) and the content index; 4. `metrics.json` and `schemas/metrics.ts`; 5. Validator rules; 6. The map files; 7. Changes to the existing scenes; 8. The new scenes; 9. Code that reads the maps; 10. Tests
- `docs/round6/README.md` (540 words): Round 6: the contract documents
- `docs/round6/auto-admin.md` (2470 words): Round-6 contract: the admin auto-mode. Sections: 1. What the code already gives us (verified at a60d855); 2. The sim clock and 10x (6A); 3. The all-NPC match (6A); 4. The headless harness and the CLI (6A); 5. The event bus and the invariants (6B); 6. The admin wire (locked; `packages/shared/src/protocol/admin.ts`); 7. The GitHub login (6C); 8. The multi-screen observer (6D); 9. What is not in round 6
- `docs/round6/bible-seams.md` (1095 words): Round-6 contract: the Bible's seams, rounds 6 to 9. Sections: 1. What round 6 pre-seeds for the Bible (6Z lands, nobody fills in round 6); 2. The staging; 3. What the Bible asks for that stays out
- `docs/round6/cutscene-music.md` (1772 words): Round-6 contract: cutscenes, loading, transitions, the trailer, music. Sections: 1. Cutscenes (6J); 2. Loading and transitions (6K); 3. Music (6L); 4. Order and ownership
- `docs/round6/m5b-data.md` (1364 words): Round-6 contract: M5b, resources, crafting, mobs, quests, mini-games. Sections: 1. Content (6E); 2. Server; 3. Client (6I); 4. Art (6M); 5. Order
- `docs/round6/media.md` (2839 words): Round-6 media: the owner's audio, the two videos, the ROSW route. Sections: 1. The owner's uploads (2026-10-21); 2. The music budget (DECISIONS A81); 3. The videos (6N; the owner's cinematic and loop, and one ROSW `video-shot` run); 4. Stingers, the narration bed and the ambiences (6N from the sound library; 6L the playlist slots); 5. The ROSW side; 6. The owner's answers (2026-10-22) and what is still open; 7. The provenance rows
- `docs/round6/owner-brief.md` (15208 words): Round 6: the owner's brief. Sections: 1. The request; 2. The Bible; 3. What the Bible names that the code does not have
- `docs/round6/seams.md` (2152 words): Round-6 seams. Sections: 1. Pre-seeded hooks; 2. Producer -> consumer; 3. Loose ends
- `docs/round7/README.md` (551 words): Round 7: the contract documents
- `docs/round7/map-intros.md` (477 words): Map intro tracks and cinematic openings (7A). Sections: 1. Findings (6Z, 2026-10-23); 2. The contract
- `docs/round7/minigames.md` (778 words): Mini-games: the stations and the polish (7M, round 7). Sections: 1. Each row drawn as its own station (A151 (3)); 2. The teardown's findings (ROSW `teardowns/who-did-it/`, read only); 3. Lore drifts, for the owner (not changed here)
- `docs/round7/parties.md` (1199 words): Parties, profiles, friends and Quit. Sections: 1. The rule in one paragraph; 2. Wire (7D; `packages/shared/src/protocol/index.ts`, `PROTOCOL.md` regenerated); 3. Server (7D); 4. Client (7C); 5. What this design accepts and records
- `docs/round7/quick-mode-removal.md` (1394 words): The quick mode leaves; Crumb's Ovens gains its rooms. Sections: 1. The decision; 2. Inventory (7J); 3. 7J's PRs; 4. Crumb's Ovens' rooms (7K); 5. Order and gates
- `docs/round7/seams.md` (183 words): Round-7 seams. Sections: 1. Module evaluation order
- `docs/round7/ui-reskin.md` (1537 words): The re-skin: the owner's two mockups, every screen. Sections: 1. What the mockups are; 2. What exists and is kept; 3. The theme pieces (7B), before any screen; 4. The screens and their owners; 5. Order and gates
- `docs/round7/vendettas.md` (1082 words): Vendettas, the Daily Train and the Vicar's memorial (7H, 7I). Sections: 1. What round 6 left (`bible-seams.md` 1); 2. Vendettas (7H); 3. The Daily Train, the memorial and the Ascended Vicar (7I); 4. Order
- `docs/round8/README.md` (1263 words): Round 8: the contract documents
- `docs/round8/art.md` (2966 words): Art: characters, scale, HD and the rooms (8F, 8I, 8J, 8K). Sections: 1. The owner's sixteen references; 2. Characters and their size (8F); 3. HD (8I); 4. The rooms: placement and detail (8J HollowMere, 8K BlackPine); 5. Materials from Poly Haven, for all three styles (8I, with 8F, 8G, 8J, 8K); 6. Tests the sessions owe
- `docs/round8/body.md` (1543 words): Bodies: health, stamina, effects, fists, inspect (8A, 8B). Sections: 1. What exists today (6Z, read on 6e5a91b); 2. Health and stamina (8A); 3. The damage table; 4. Fists (8A); 5. The knockout; 6. Effects (8A; ids are fixed in [seams.md](seams.md), numbers in `effects.json`); 7. Inspect and the relations table (8B); 8. Tests the sessions owe
- `docs/round8/canon.md` (3811 words): Round 8 addendum C: the canon pass (8V). Sections: 1. The rulings of A201; 2. The lore facts the game shows; 3. Conflicts and their fixes; 4. The places the game leaves out; 5. Proposals (the owner's; built by nobody); 6. Not scheduled; 7. Shelves, letters and boards (C4+, with 7M); 8. The pull requests
- `docs/round8/economy.md` (1266 words): The economy: Book IV on today's maps and roles (8C, 8D). Sections: 1. The four pillars, as built this round; 2. Scrip (8C); 3. Taxes, Indebted, Faith, rumours, HQ (8D); 4. What stays for R9; 5. Tests the sessions owe
- `docs/round8/hd-look/README.md` (658 words): The HD look sheet (8I, DECISIONS A164). Sections: The columns; The files; How each cell was made; What to look at
- `docs/round8/icons/README.md` (914 words): Round 8 icons (8N): the review sheets. Sections: Handover: what the icon line still has to draw (8N, 2026-10-24)
- `docs/round8/living.md` (2116 words): Round 8 addendum B: the living world (8Q, 8R, 8S, 8T, 8U). Sections: 1. The world index (8Q); 2. Habitats (8Q); 3. The hive (8R); 4. Roles (8S); 5. Talk (8T); 6. Briarberry (8U); 7. Sessions, ownership and grants
- `docs/round8/motion.md` (1007 words): Motion: every new animation (8F, 8G, 8H). Sections: 1. Characters (8F); 2. Creatures, resources, VFX (8G); 3. The interface (8H); 4. Tests the sessions owe
- `docs/round8/seams.md` (2675 words): Round 8 seams: what the sessions share. Sections: 1. The wire: schema version 6; 2. Ids; 3. Protocol; 4. The bus (`sim/events/bus.ts`); 5. The locked one-line hooks; 6. Who owns which path; 7. Merge order
- `docs/round8/stations.md` (3061 words): Stations: the hands-on widgets (7M, round 8 addendum C). Sections: 1. The ask, verbatim; 2. The rules every widget keeps (6Z, 2026-10-24); 3. The audit: what a station is today; 4. The well, as the owner set it (rounds 1 and 2); 5. The reader and the lore data; 6. PR split (one concern each, under 400 lines, drafts, 6Z merges)
- `docs/round8/teardown.md` (1266 words): Round 8 addendum: the teardown answers (8L, 8M, 8N, 6Z). Sections: 1. Anti-cheat (8L); 2. Rules (8M); 3. Icons (8N); 4. The canon pass (later); 5. Process (6Z); 6. Sessions, ids and grants
- `docs/round8/townsfolk.md` (928 words): Moods, mugging and ambient townsfolk (8E). Sections: 1. Needs and moods (NPC seats and ambient townsfolk); 2. Ambient townsfolk; 3. The mugging rule; 4. Tests 8E owes
- `docs/round9/README.md` (1770 words): Round 9: the world-mode design round (design only, no code). Sections: Context; Decisions so far; What the code does today (from the read-only survey); Deliverables; Who does it; Review loop with the owner; Checks; Status (2026-10-25)
- `docs/round9/admin-studio.md` (2064 words): Admin Studio: creative mode, the room editor and reports (owner request, 2026-10-25). Sections: 1. The link and the gate; 2. Creative mode (walk the world); 3. The room editor; 4. Reports (screenshots and notes Claude picks up); 5. Where it all goes: GitHub; 6. Pull requests; 8. Modes: Overview, World, Room and NPC (owner, 2026-10-25); 7. Not in scope
- `docs/round9/emergent-play.md` (3978 words): Round 9: emergent play (9C). Sections: 1. The rule behind the example; 2. The rogue, step by step; 3. One day of the rogue; 4. Three more player-invented strategies; 5. What it asks of the logic table; Open questions for the owner; 6. Reconciled
- `docs/round9/failures.md` (7650 words): Round 9 (9B): failure messages. Sections: 1. What the player sees today, and why; 2. Census; 3. The rule; 4. The reason list; 5. In-world lines come from the interaction, not the reason; 6. How the reason reaches the player; 7. Build plan and tests (for round 10; not part of this PR); 8. Open questions for the owner; 9. Appendix: every refusal site; 10. Reconciled
- `docs/round9/followup-4.md` (2933 words): Round 9: the follow-up calls (owner, 2026-10-26). Sections: 1. The answers, as saved; 2. The rules; 3. Readings to confirm; 4. Where this lands
- `docs/round9/gdd-map.md` (3074 words): Round 9 (9D): the GDD map. Sections: 1. Existing sections that change; 2. New sections; 3. Content files at a glance; 4. Reconciled; 5. New questions the reconciliation raised
- `docs/round9/living-world.md` (8659 words): Round 9: the living world (9C). Sections: 0. Rules this design keeps; 1. Citizens: NPCs that walk, chat and give tasks; 2. How the systems feed each other; 3. Mob bosses; 4. Achievements; 5. Gear; 6. Pacing; 7. What this asks of other documents; Open questions for the owner; 8. Reconciled
- `docs/round9/logic-table.md` (11394 words): Round 9 (9B): the logic table. Sections: 1. What is wrong today; 2. The idea in one paragraph; 3. The schema: `packages/content/data/interactions.json`; 4. Replacing the hard-coded dispatch; 5. Audit of all 605 props; 6. Chests: placed by rules; 7. Nodes and props; 8. New items; 9. How the table extends what exists; 10. The table
- `docs/round9/owner-answers.md` (2873 words): Round 9: the owner's questionnaire answers. Sections: World mode: dealing, the Killer and the train; The logic table: tools, objects and chests; Failure messages and NFY; The living world: NPCs, systems, gear and achievements; Playing your own way (the rogue); Your newest rules: sleep and busy NPCs
- `docs/round9/owner-brief.md` (2543 words): Round 9: the owner's brief (2026-10-24). Sections: The owner's words, verbatim; The brief broken into workstreams (6Z's reading, for the owner to correct); Follow-up answers (2026-10-24, verbatim where quoted); Second follow-up (2026-10-25, verbatim); Third follow-up: "function without the killer" (2026-10-25, verbatim)
- `docs/round9/phases.md` (5235 words): Round 9 (9A): the phase screens. Sections: 0. What the meeting is today; 1. The phases at a glance; 2. Dawn and the train; 3. The Inquest; 4. The Tribunal; 5. The Final Night and the end trial; 6. On the line; 7. The victories ledger; 8. Story chapter cards; 9. Arrival: the role card and the Killer's pick
- `docs/round9/round10-plan.md` (3004 words): Round 9 (9D): the round-10 build plan. Sections: 1. Rules for every pull request; 2. Sessions; 3. The next-playtest slice (session 10A); 4. The rest of round 10; 5. What breaks when I'm gone (owner answer WM1); 6. Dependencies at a glance; 7. Questions for 6Z
- `docs/round9/world-mode.md` (13464 words): Round 9 (9A): world mode. Sections: 1. The deal; 2. How each role wins; 3. Stopping the Killer; 4. Disguises; 5. What replaces voting; 6. The train brings back the day's dead; 7. Pacing; 8. Effects that do not kill; 9. Story mode (1 player); 10. The art style is chosen in the menu only
- `docs/story/README.md` (2517 words): Story mode: the build contract. Sections: What story mode is; Decisions taken for the owner's absence; Seams: the interfaces the four sessions share; Sessions; How the work lands; Definition of done
- `docs/story/arc.md` (7978 words): Story mode, part 2: the HollowMere arc. Sections: 0. The shape in one page; 1. The acts; 2. The sections; 3. Coverage; 4. What each section uses, and what the engine needs; 5. The schema change, for P1; 6. Questions for the owner; 7. Answers (owner, 2026-11-07); 8. Part 2 build decisions (owner, 2026-11-07)
- `docs/story/orchestrator-handoff.md` (2116 words): Story mode part 2: orchestrator handoff. Sections: Standing rules from the owner; Open decisions (owner only); The Vicar design that was agreed; Merges that wait for the owner; Round-10 lanes the orchestrator owns (2026-11-12); Sessions; Archival routine; On hold; Art; Resuming
- `docs/story/part2.md` (1000 words): Story mode, part 2: the full story. Sections: What the owner asked for; Design changes this makes; Workstreams; Order; What it costs; Open questions
- `docs/story/questions.md` (910 words): Story mode: the owner's questionnaire. Sections: A. What shipped, to confirm; B. Rules to settle; C. Content and scope; D. Process; Answers (owner, 2026-11-06)
- `docs/story/rite.md` (1847 words): Brief: the Medium's rite and the 10X Vicar. Sections: 1. What the owner decided; 2. What exists today; 3. Questions to settle before code (each has a default); 4. The build, as pull requests; 5. Rules R must keep; 6. Paths R owns; 7. Done when
- `docs/story/script.md` (2425 words): Story mode: the script of A Winter in HollowMere. Sections: Chapter 1: The Wake Loaf; Chapter 2: The Watchman's Night; Chapter 3: The Bandit's Heist; Chapter 4: The Works; Open questions for the owner
- `docs/story/status.md` (5270 words): Story mode: status. Sections: S1. Story content; S2. Story engine; S3. Wire and client; S4. Tests and the bot; Session ids (2026-11-06, from 6Z's spawn); P4. Achievements (E1); P0. The arc (part 2); P1. The section schema; P2. Engine (part 2); P3. Story client (part 2)
- `docs/story/test-plan.md` (636 words): Story mode: test plan (S4). Sections: The fixture (`apps/server/test/story/fixture.ts`); Server suites (`apps/server/test/story/`); E2E (`apps/client/e2e/story*.spec.ts`); The bot (`tools/bots/`); Bugs found in other sessions' paths
- `packages/content/README.md` (648 words): @wdi/content. Sections: Files; Scenes; Adding a record
- `tools/blender/README.md` (4021 words): tools/blender. Sections: Commands; Character file contract; IsoCam calibration (round 5, 2026-10-18); Calibration results and rig decisions (2026-10-10, SpriteCam, retired in round 5)
- `tools/blender/models/README.md` (229 words): tools/blender/models. Sections: `models.lock.json`; `fetch_models.py`
- `tools/sprites/README.md` (1705 words): tools/sprites (`@wdi/sprites`)

## 7. Decision log index (docs/DECISIONS.md, 293 numbered rows)

Each row is a decision ID and the opening of its text (cut at 230 characters). The full text is in the file.

- **A1** Open question 3 (hat replaces boots as the third trait)
- **A2** Open question 7 (where masters live)
- **A3** Theme addition: One Night Ultimate Baguette
- **A4** Connection to the ROSW repo
- **A5** Engine line (open question 1)
- **A6** Hosting (open question 2)
- **A7** First playable (open question 8)
- **A8** Marketplace settings (A4)
- **A9** Render rig (ASSETS 6.2), from Session D's calibration render
- **A10** Well ladder (GDD 3.6, WORLD 4.3)
- **A11** Interior minimum (WORLD 4.2)
- **A12** Roster interface (ARCHITECTURE 5.8)
- **A13** Matchmake throttle (ARCHITECTURE 5.3)
- **A17** AI art licence (owner, 2026-10-10: "open source the AI art")
- **A15** Quick mode length (open question 12)
- **A16** NPC fill (owner request 2026-10-10)
- **A14** Higgsfield concepts (ASSETS 6.5)
- **A18** Practice at 4 (open question 4)
- **A19** Original art licence (open question 6)
- **A20** Final Night (open question 8)
- **A21** Quick-mode sleep model (open question 9)
- **A22** Public name (open question 10)
- **A23** ROSW studio project (open question 11)
- **A24** Quick mode length (open question 12)
- **A25** Calibration sheet (open question 14)
- **A26** NPC fill policy (open question 15)
- **A27** Toon ramp stops (ASSETS 6.2, follow-up to A25)
- **A29** Round 2 integration (PRs #7 to #11, 2026-10-15)
- **A28** M1 finish (Session F, `claude/m1-finish`)
- **A30** Round 3 contract (M3 first playable, 2026-10-16)
- **A31** M3 match flow (Session K, `claude/m3-flow`)
- **A32** Round 3, Session L (`claude/m3-kill`)
- **A33** Meeting, game over, theme (Session M, `claude/m3-meeting`)
- **A34** World actions, client (Session N, `claude/m3-world`, 2026-10-16)
- **A35** Round 3, Session O (`claude/m3-bots`)
- **A36** M3 art (Session P, `claude/m3-art`, 2026-10-16)
- **A37** Playtest kit, audio, copy (Session Q, `claude/m3-playtest`, 2026-10-16)
- **A38** Round 3 integration (PRs #12 to #18, 2026-10-16)
- **A39** Round 4 contract (M3b quick mode, M3c NPC fill, 2026-10-16)
- **A40** Round 4, Session R: quick mode on the server (M3b, 2026-10-16)
- **A41** M3c NPC fill, server (Session S, `claude/m3c-npc`, 2026-10-16)
- **A42** Round 4, Session T (`claude/m3b-world`)
- **A43** Round 4, Session U (quick mode: client meeting and end, 2026-10-16)
- **A44** Lobby settings on the client (Session V, round 4)
- **A45** Round 4 bots, e2e and CI (Session W, `claude/r4-bots`, 2026-10-17; recorded by the orchestrator at integration, since W's paths left out this file)
- **A46** Round 4 art (Session X, `claude/r4-art`, 2026-10-17)
- **A47** Round 4 content, copy and audio (Session Y, `claude/r4-content`, 2026-10-17; recorded by the orchestrator at integration, since Y's paths left out this file)
- **A48** Round 4 integration (PRs #19 to #26, 2026-10-17)
- **A49** Round 5 owner decisions (2026-10-17)
- **A50** Round 5 contract (orchestrator, 2026-10-17)
- **A51** Correction to A40: a quick-mode Start below `players.min` (bug #21 of the round-4 review; recorded at the round-5 pre-seed, 2026-10-17)
- **A52** Round 5 Session 5A: ONUB v2 rules, deal and prep (`claude/r5-onub-rules`, 2026-10-18)
- **A53** Round 5 Session 5B (ONUB v2 server night and morning, `claude/r5-onub-night`, 2026-10-18)
- **A54** Round 5 Session 5C (`claude/r5-onub-prep-ui`, 2026-10-18)
- **A55** Round 5 Session 5D (ONUB v2 client night, morning and results; 2026-10-18)
- **A56** Round 5 Session 5E (ONUB v2 bots, NPC brains, e2e and soak; 2026-10-18)
- **A57** Round 5 Session 5F (`claude/r5-avatars`, 2026-10-18)
- **A58** Round 5 Session 5G (2026-10-18)
- **A59** Round 5 Session 5H (NPC routines and fixes, `claude/r5-npc`, 2026-10-18)
- **A60** Round 5 Session 5I (isometric client and lighting, `claude/r5-iso`, 2026-10-18)
- **A61** Round 5 Session 5J: maps, the exporter and the map choice (Session 5J, 2026-10-18)
- **A62** Round 5 world art (Session 5K, `claude/r5-world-art`, 2026-10-18)
- **A63** Round 5 Session 5L, character art (`claude/r5-char-art`, PR #33, 2026-10-18)
- **A64** Round 5 Session 5M, ONUB art (`claude/r5-onub-art`, 2026-10-18)
- **A65** Round 5 integration (reserved)
- **A79** Art styles and the ONUB images' provenance (owner, 2026-10-18; recorded by the orchestrator)
- **A80** The art-style switch on the client (Session 5N, 2026-10-18)
- **A81** Round 6: the owner's answers and the contract (owner, 2026-10-21 and 2026-10-22; recorded by 6Z)
- **A82** Reserved for session 6Z (round 6)
- **A83** Round 6, 6A: the clock and the all-NPC match (6A, 2026-10-22)
- **A84** Round 6, 6B: the event bus, the match event log and the invariants (6B, 2026-10-22)
- **A85** The admin gate: GitHub login, one seatless admin client (6C, 2026-10-22)
- **A86** Admin client (6D, round 6, 2026-10-22). One Phaser game: `Admin` owns the connection (`AdminLink`: the live room through `connectAdmin`, or `mockAdmin.ts` under `?mock=1`) and an `AdminStore` that the DOM panels and the viewports ...
- **A87** M5b content (6E, round 6). Resources are the six the round-5 scene nodes already named (timber, stone, tinOre, resin, herb, mushroom); each is also an `items.json` row of a new kind `material` that stacks to `balance.resources.sta...
- **A88** Gathering and crafting (6F, round 6). The inventory lives in `sim/Inventory.ts`: `addStack(player, item, qty)`, `take(player, item, qty)`, `count`, `canAdd`, and the atomic `exchange(player, takes, gives)` with its dry run `canExc...
- **A89** Mobs and dark visibility (6G, round 6). One creature per spawner (its id is the spawner's), awake in the spawner's parts of the day, frozen outside the world phases, gone at the lobby, the card and in the quick mode; FSM `idle, ro...
- **A90** Quests and mini-games (6H, round 6). The pure rules take their numbers from the caller: `generateMinigame(kind, difficulty, rng, bases)` and `checkMinigame(puzzle, answer)` in `rules/minigames.ts`, because `@wdi/shared` cannot imp...
- **A91** M5b client (6I, round 6). One DOM layer (`ui/M5bLayer.ts`) owns the pockets, crafting and quest panels, the E prompt and the mini-game modal. 6Z granted the three locked-file requests inside the PR: `WorldFeed` carries `inventory`...
- **A92** Cutscene data and timing (Session 6J, 2026-10-22)
- **A93** Round 6: loading, transitions, the trailer and the budget test (session 6K)
- **A94** Reserved for session 6L (round 6)
- **A95** 6M (round 6): the M5b art is drawn in code on the world ramps (route R5) and finished per style like a rig render, so no generation, `.blend` or MANIFEST row is needed. Keys `nodes`, `tools`, `anims_tools`, `mobs`, `anims_mobs`, `...
- **A96** 6N (round 6): the library half of the round-6 audio, from ROSW release `SFX_2026_01`
- **A97** 6P (round 6): the integration
- **A98** Opening cinematic before the menu (owner, 2026-10-22; 6Z). The owner supplied a 29.1 s 1080p cinematic made with Dreamina (shipped at 22.3 s since A102), with its own stereo sound (effects still to be layered), an 8 s silent Higgs...
- **A99** The Vicar's final words are voiced (owner, 2026-10-23; 6N). The Vicar's final words are voiced with Higgsfield speech generation, replacing the no-voice rule of `media.md` 3 (the memorial run's intake had the words as captions onl...
- **A100** The Killer NPC's kill-opportunity timer (owner, 2026-10-23; 6Z). The owner: "when they are in a room alone with another player or NPC for over 30 seconds they will move to kill then immediately flee the scene"; the strike chance "...
- **A101** The maps' intro tracks and longer, cinematic openings (owner, 2026-10-23; 7A). The owner: "the other music files were for the world theme music. the files titled HollowMere, BlackPine and Port AU Levain are the intro tracks they n...
- **A102** The opening cinematic ends just after the explosion (owner, 2026-10-23; 6N). The owner: "trim the opening cinematic to align with the loading screen right after the glitch transitions to the meadow, it shouldn't be longer than 1.2...
- **A103** The whole game is re-skinned to the owner's two Claude Design mockups (owner, 2026-10-23; 6Z). The owner uploaded `Main_Menu-html.zip` and `Party_Lobby-html.zip` ("can you swap the UI with these"; screenshots in `docs/ui/*-mockup-...
- **A104** Open and private parties, the party list, the device profile, friends and Quit (owner, 2026-10-23; 6Z). From the owner's second answer in A103. Decided: a party is open (listed to everyone) or private (unlisted, except to invited ...
- **A105** The round-7 contract (6Z, 2026-10-23). Round 7 opens before round 6's #73 (6P) and A102 (6N) land, on the owner's instruction to continue without them for the day; ten sessions (7A to 7I, 7P) under `docs/round7/`, SESSIONS Round 7...
- **A106** Theme pieces for the re-skin (7B, round 7). The night set is a separate `palette.json` `night` block (`night`, `violet`, `indigo`, `lilac`, `snow`; the accent stays `lantern`), not five more `colors`, because `colors` is also the ...
- **A107** The menu, its dialogs, the profile, friends, Quit and the party list (7C; Sonnet 5.5). Decided: the landing form becomes the mockup's menu (`ui/Landing.ts`, `ui/menu.css`, `ui/menu/`, copy in `ui/copy/menu.ts`, UI.md 14.25); Start...
- **A108** The parties server (7D; Sonnet 5.5). Decided: `CreateOptions extends JoinOptions` (`visibility`, `invited?`) for `create("party")` only, `JoinOptions.profile?`, `Player.profile` on the public roster (schema version 4); `balance.js...
- **A109** The lobby re-skin (7E; Sonnet 5.5). Decided: the lobby is three glass columns (code, mode, NPCs and seats; map, art style and sound; deck and actions) in `ui/lobby.css`, tokens only, each rule scoped to `.wdi-lobby` and standing i...
- **A110** The match screens on the night theme (7F; Sonnet 5.5). Decided: the role card keeps its nine-slice frame, its flip and every id, and moves to an indigo fill with lilac text; the role name and the faction word take Press Start 2P, ...
- **A111** The table screens in the night theme (7G, round 7). The meeting, game over, main-mode cards, seat picker, shot toast, over view, and the over view are re-skinned in their own files, `ui/table.css`, with no change to `components.cs...
- **A112** The four vendettas as rules (7H, 2026-10-23). From Book I.3 under A105's limits. Decided: the draw is uniform over the rows a match allows (the Zealot needs a dealt Vicar, the Bandit an open manor hall, the Bandit and the Hitman H...
- **A113** The Daily Train stops at a platform on HollowMere's overworld (7I, 2026-10-23). `vendettas.md` 3 left 7I the call between an appended `station` scene and an overworld spot. Decided: the spot. A scene would break the hand-pinned sc...
- **A114** Reserved for the round-7 integration (7P)
- **A115** The quick mode is removed (owner, 2026-10-23; 7J). The owner asked "did you get rid of quick mode" and chose, from the options put to them, "Remove the quick mode entirely" and "Now, in round 7": One Night Ultimate Baguette (GDD 3...
- **A116** The owner's bakery pictures become rooms (owner, 2026-10-23; 7K). The owner: "you must make individual rooms for those pictures i sent that you used in onub"; asked where, they chose "Both": the four station pictures (fridge, mixe...
- **A117** The quick mode's removal, as built (7J, 2026-10-23). Implementation calls inside A115, none a rule change. Three deletion PRs: the client (#109), then the server, shared, content and tools with schema version 5 (#121), then the as...
- **A118** Crumb's Ovens' four station rooms (7K, 2026-10-23). Decided: the scene ids share the stem `crumb_` (`crumb_cold`, `crumb_mixing`, `crumb_oven`, `crumb_proofing`, appended to `SCENE_IDS` in that order) with the object prefixes `cf`...
- **A131** The Vicar's martyrdom pays the task bar (7I, 2026-10-23). Owner's rule: the Vicar must die a martyr, killed by an active Killer's strike, not by wolves or any other hostile means, to gain a tenfold buff, so that no Killer but the ...
- **A121** The martyr's boost lasts ten minutes; the day haze is softened (owner, 2026-10-23; 6Z). Two questions put to the owner. (1) A131's open question, whether the martyr's tenfold task weight carries into the room's next match: the own...
- **A133** The task deal (7M, 2026-10-23). Nothing dealt tasks in a live match (A90, A97 (5)); `sim/Tasks.ts` now deals at `startMatch` after `assignCovers` (one call in `handlers/lobby.ts`), on a `tasks` stream of its own (`seeds.ts`, `auto...
- **A134** Round 8: bodies, coin, motion and art (owner, 2026-10-23; 6Z). The owner asked, verbatim: "plan then add health, stamina, and metrics for health drain from all the different attacks and the minor effects such as slowness, bleeding...
- **A135** The round-8 contract (6Z, 2026-10-23). `docs/round8/` (README, body, economy, townsfolk, motion, art, seams). ROADMAP R8 becomes "Bodies, coin, motion and art"; evolutions, the law pipeline and Port-au-Levain move to R9 (with the ...
- **A137** Inspect and the relations table, as built (8B, 2026-10-23). Implementation calls inside A134 and A135. `act.inspect` names an avatar handle; it needs a living, placed inspector out of transit, a world phase, the target's current a...
- **A138** Scrip: the purse, the stake and `movePurse` (8C, 2026-10-23). `Private.purse` and `Private.bank` (u32, own client only) join schema version 6 as seams.md 1 row 2. Scrip moves only through `movePurse(room, from, to, amount, reason)...
- **A139** Rent, Faith, rumours and HQ: the data (8D, 2026-10-23). `economy.json` gains `rent`, `quota`, `curfew`, `faith`, `notices` and `hq` (schema `schemas/economy.ts`, cross-checks `validateEconomy.ts`). 8D's calls, approved by 6Z: (1) ...
- **A140** Needs and moods (8E, 2026-10-23; the owner's "hungry/scared/angry/etc NPCs", A134). Four needs per NPC seat in room memory, keyed by the brain so a new card resets them; the mood is the strongest need over one threshold, Desperate...
- **A145** HollowMere's rooms are placed by rule (8J, 2026-10-23). art.md 4.1 becomes a content test, `packages/content/test/placement.ts` (shared, so 8K reuses it for BlackPine) with `placement.hollowmere.test.ts`. Every prop kind, decor ta...
- **A144** The material library (8I, 2026-10-23; first row of 8I, under A155). `tools/blender/materials/`: `roles.py` holds 47 roles, each a Poly Haven slug, a texel density in metres per repeat (walls 2 m, brick and flagstone 1.5 m, cobble ...
- **A146** Blackpine placement (8K, 2026-10-23). `packages/content/test/placement.blackpine.test.ts` runs every `bp_` scene through 8J's shared check (`test/placement.ts`) with Blackpine's prop, spot and light-holder classes, plus three wall...
- **A166** Blackpine rooms placed (8K, 2026-10-23). All eight `bp_` scenes pass the placement test with nothing pending (art.md 4.1): every hung piece (the range, basin, pegs, gearing, shelves, telephone, tool rack) stands on the floor tile ...
- **A155** Poly Haven materials for all three art styles (owner, 2026-10-23; 6Z; second row of A135). The owner asked: "Can you use my Polyhaven textures and more for the HD version and maybe even rerender them as 8 bit and low poly for bett...
- **A136** Bodies, as built (8A, 2026-10-23). Implementation calls inside A134 and A135 (`docs/round8/body.md`), none against them. (1) Health is 100, so a fist is 8 and a wolf bite 25 (GDD 3.22); the two-hit-point model of 3.6 and 3.15 is g...
- **A164** The HD finish (8I, 2026-10-23; second row of 8I, under A144). HD is the same rig and the same toon look rendered at twice the display scale (`rig_common.STYLE_FACTOR`; 181.02 px per ground metre, a 128 px character cell rendered a...
- **A141** The character scale: the drawn-figure fix, with the closer camera as the alternative (8F, 2026-10-23). The owner asked for figures about 1.5 times taller on screen (A134, art.md 2). Measuring the shipped client showed why they loo...
- **A142** Creatures, resource breaks, VFX and transport motion (8G, 2026-10-23). Decided, step 1: every creature gains `hp` in `mobs.json` (GDD 3.15), sized so a few fists drive off a rat or a bat and a wolf takes a fight; 8A tunes them aga...
- **A161** The round-8 character redesign (8F, 2026-10-23). The ten world looks and the plain `villager` are rebuilt by `build_looks.py` on a new base of about four heads (art.md 2): still 1.7 m, so the GDD 3.1 height factors, the 112 px cap...
- **A143** Interface motion (8H, round 8, 2026-10-23). `docs/round8/motion.md` 3. Decided: motion is tokens only (UI.md 9), each duration and distance zeroed under reduced motion in `tokens.css` and checked by `ui/theme/motion.test.ts`; the ...
- **A162** The round-8 effects are runtime particles (8G, 2026-10-23). Decided: the VFX list of motion.md 2 is drawn as Phaser particle bursts from seven shapes the client draws once at boot (`view/vfx/`), not as baked atlas frames. A baked ...
- **A160** Ambient townsfolk (8E, 2026-10-23; second row of A140; townsfolk.md 2). Figures are `Avatar`s under opaque handles registered in the handle memory's `sceneOf` (so `avatarOf` finds them and the lobby sweep removes them) but never i...
- **A180** The mugging (8E, 2026-10-23; third row of A140, the second plus 20 again; townsfolk.md 3). Decided: the rule of GDD 3.24 "The mugging", built in `sim/townsfolk/mug.ts` and run first in `runTownsfolk` (a mugger figure is walked or ...
- **A168** The owner's answers to the teardown brief (owner, 2026-10-23). Through 6Z's questionnaire, after the UDGT teardown session's handover (ROSW `teardowns/who-did-it/`, #118). Anti-cheat: all four proposals: the `bloody` bit by range ...
- **A169** The round-8 addendum (6Z, 2026-10-23). `docs/round8/teardown.md` turns A168 into work: 8L anti-cheat (Opus), 8M rules (Opus), 8N icons (Fable), each with its reserved row (A170, A171, A172; second rows plus 20). 6Z's calls: blood ...
- **A171** Rules: the match length (8M, round 8, 2026-10-23). A168 asks for matches of 20 to 25 minutes. Step 1 of `teardown.md` 2: the all-NPC soak (`pnpm auto --matches 50 --seed 1`, timed from grace) measured medians of 10.9, 16.1, 16.8 a...
- **A170** Anti-cheat: what a client receives is what it may know (8L, round 8, 2026-10-23). From A168 and A169 (`docs/round8/teardown.md` 1). Blood by range (PR 1): `Avatar` is one shared schema instance per scene, so a status bit in `Avata...
- **A190** Anti-cheat, continued (8L, round 8, 2026-10-23). The second row of A170. Night sight on the server (PR 2): `canSee` (`sim/Sight.ts`) treats every scene as dark while `dayPartOf` the phase is `night` (the night and the Final Night)...
- **A173** The living world: the owner's request and answers (owner, 2026-10-24). Request, verbatim: "a few things i need to add, tell me up front if we already have that all NPCs need to be connected some how like a hive mind, and that hive...
- **A174** The bell rings at night for a body (6Z, 2026-10-24, from the owner's "bell rings at night"). GDD 3.8: the bell may be rung at night, by a seat or an NPC, while an unreported body lies in the world; with no such body the night rule...
- **A176** The hive (8R, round 8, 2026-10-24). From A173 and A174 (`docs/round8/living.md` 3). The blackboard (`sim/npc/hive/board.ts`) is rebuilt every tick from the public world: unhidden bodies by their public `Body.of`, creatures by thei...
- **A196** The body bands and the night bell (8R, round 8, 2026-10-24). From A174 and the owner's playtest: an NPC Detective walked within range of a body and did nothing. NPC body sight was a bare distance (3.5 tiles at night, 7 otherwise, ...
- **A178** Talk: the meeting notes (8T, round 8, 2026-10-24). From A173 ("anonymous when chatting at meetings") and `docs/round8/living.md` 5. PR 1, templates only. A new channel `ChatChannel` `notes`, reached by a new C2S `chat.note` `{text...
- **A198** Talk: the model notes (8T, round 8, 2026-10-24). The second row of A178 (A178 plus 20). PR 2. NPC meeting notes from the Messages API over `fetch` (no SDK is a dependency), only with `ANTHROPIC_API_KEY` on the server and never in ...
- **A151** The fifth mini-game kind (7M, 2026-10-23). Nine fetch tasks shared four kinds (A115 kept them from the quick mode), so three tasks each played a slide or a crates that had nothing to do with their station. Decided: (1) a `tap` kin...
- **A200** Stations: hands-on widgets at every station (owner, 2026-10-24; 7M). The owner asked, verbatim: "i want a diverse collection of mini UI/UX widgets at every station in the game partially for the game, mostly for the wacky fun fille...
- **A201** The canon pass: the lore is in (owner, 2026-10-24). The owner: "narrative worldbuilding is done". The lore of the Narrative WorldBuilding session merged into ROSW main (Pipelines-Plugin #17, 55e6c64): 75 `project: who-did-it` work...
- **A202** The round-8 sounds for 8G (owner, 2026-10-24; 6Z). The owner approved 18 library sounds by ear in the 2026-10-24 questionnaire: mob_wolf_attack `dark-horror-sound-fx/werewolf`, mob_hurt_wolf `dark-horror-sound-fx/mutated-dog`, mob...
- **A191** Rules: the Final Night, a short hunt then the trial (8M, round 8, 2026-10-23; second row of A171). `teardown.md` 2.2 from A168 and 6Z's call in A169. Decided: `finalNight.huntS` 90 s becomes 45 s; the forced meeting after it (reas...
- **A221** The canon map (8V, round 8, 2026-10-24). From A201 (`teardown.md` 4). `docs/round8/canon.md` maps every ruling of A201 and every lore fact the game shows to its file, id, copy and GDD or WORLD row, from the Ledger (I-XIX) and the ...
- **A222** Round 9: world mode, the owner's brief (owner, 2026-10-24; 6Z). After the first playtest of the round-8 build, the owner set the direction for round 9. The full text is verbatim in `docs/round9/owner-brief.md`, with 6Z's reading a...
- **A223** Round 10: start the build, by model and by context size (owner, 2026-10-29; 6Z). The owner's words: "start round 10s sessions, opus, sonnet, and fable towards the end to fix all other issues. autocompact the sessions at 500k for a...
- **A224** The round-10 contract (6Z, 2026-10-29). `docs/round10/` (README and seams) and the Round 10 section of `docs/SESSIONS.md`. (1) The plan's 10A and 10D are split by model: 10A (Opus: A1, A12, A7), 10F (Opus: A9, A10, D1), 10H (Sonne...
- **A225** Refusal reasons: the contract (10A, round 10, A1; 2026-10-29). `packages/shared/src/protocol/refusals.ts` holds the closed, append-only `RefusalReason` list (the 48 live reasons of `docs/round9/failures.md` 4.1 to 4.6 and the 11 o...
- **A226** The logic table: schema and validator (10F, A9, 2026-10-29). `packages/content/data/interactions.json` and its schema land with no behaviour: the capability tags, one class per `live` kind (26), no interactions and no loot tables....
- **A227** Pacing for world mode (10H, A5, round 10, 2026-10-29). `balance.json`, `abilities.json` and `clues.json` take the factors of `world-mode.md` 7 (D 4, N 3, C 3.5): the day 480 s, dusk 30 s, night 300 s, a cycle 810 s; kill cooldowns...
- **A228** The refusal sweep (10G, round 10). A2: `reject` (`sim/World.ts`) and `refuse` (`sim/Flow.ts`) are one function, `sendRefusal` (`sim/refusal.ts`), with two forms while A3 moves the `sim/` sites: `(reason, args?, {msg?, interaction?...
- **A229** Guard figures: the Constables and the Clerk (10B, round 10, B1; 2026-10-29). GDD 3.24, 3.31 and 3.17; F4 2.2 (a4) and R2. The guards are built on the round-8 townsfolk figures, so they get the figures' guarantees for free: no seat...
- **A230** The train returns the day's dead, and the Dusk Train (10C, C1, round 10, 2026-10-29). `sim/Train.ts` keeps who is on the line in room memory and brings them back at the next day's arrival (GDD 3.3, 3.22); `Private.onLine` is the o...
- **A231** Depletion (10D, D2, round 10, 2026-10-29). The resolver already empties a pile and brings it back (A10, A11), and D1's NPC seats already hold through it, so D2 adds the tool prices and the proof: (1) the general stores (`store`, `...
- **A233** The refusal words 10G's sweep left (10X, round 10, x1; 2026-10-30). 10G's A2 to A4 (A228) listed the refusals whose reason or args looked wrong; each is settled here, and `refusalWords.test.ts` pins the changed ones. Changed: (1) ...
- **A234** Refusal lines on a phone and the greyed prompt (10Y, y1, round 10, 2026-10-30). A4's display (A228, UI.md 14.45) checked at 390 x 844 and 1280 x 720 by `apps/client/e2e/refusals.spec.ts`, with failures.md 6.2's two parked items: a...
- **A236** Round 11: the plan approved (owner, 2026-10-30; 6Z). The owner approved `docs/round11/round11-plan.md`: "yes merge" in 11A's session, then "3. confirm" in 6Z's, where item 3 was the plan's approval with CL3a's default. CL3a takes ...
- **A237** The role cards and the Satchel: the owner's answers (owner, 2026-10-30; 10R). The owner answered `docs/round10/rolecards.md` 10 and 11 (Q-A1 to Q-E3, 18 questions), recorded verbatim in its section 12. The card is the trifold of `...
- **A239** The evidence verbs, part one: the Lens and the plant (10V, V1a, round 10, 2026-10-30). GDD 3.2 and 3.4; `docs/round10/rolecards.md` 11, owner answers Q-A3 ("Round 10's tail") and Q-A4 ("Build the ones we were going to grey out"). ...
- **A240** Snares, the server (10N, round 10, K6a; 2026-10-30). GDD 3.5 and 3.14; scope.md 2.5; seams.md 3 row 31. (1) Setting a snare is an item verb that never asks the card: anyone holding a Snare sets one. The `abilities.json` row keeps ...
- **A241** Candles for all and Handcuffs (10K, round 10, K3; 2026-10-30). GDD 3.5, 3.15, 3.31; `scope.md` 2.5 (I28, I29); seams.md 3 row 14 and 6. (1) Every start kit without a light gains one Candle (`roles.json`: the Killer, Accomplice, He...
- **A242** New places (10T, round 10, T6a; 2026-10-30; scope.md I42). `cottage_fisher` (`fc`) and `sea_exit` (`se`) are greybox scenes in HollowMere's map, appended to `SCENE_IDS`, tilemaps and navs exported with `tools/grid`; the south-east...
- **A243** Barks: the server (10M, round 10, M1a; 2026-10-30). The quick-chat wheel was declared and never built: `chat.quick` had no handler, no message carried a bubble and `chat.quickChat` held 8 lines, so "8 lines, humans only" was the w...
- **A245** The inventory: slots on the server (10A, round 10, A12; 2026-10-29). GDD 3.30. `ItemStack` gains `slot` and `Inventory` gains `selected` (both private; `SCHEMA_VERSION` 7, shared with A10 by whichever merges first), so the invento...
- **A246** The logic table's resolver (10F, A10, 2026-10-29). `apps/server/src/sim/interact/resolve.ts` runs `act.hold {action: 'interact', targetId, via?}` beside the legacy actions; humans and NPC seats share it. (1) Wire: `SceneState.prop...
- **A247** Weaker mobs and effects that stop at 1 health (10H, A6, round 10, 2026-10-29). From `living-world.md` 6.1 (owner answer LW11, default). Bites become 12, 9, 3 and 2 (wolf, boar, bat, rat) and the effect chances 35%, 20% and 30%; th...
- **A249** The Constables' briefing (10B, round 10, B2; 2026-10-29). GDD 3.31 and 3.4; `world-mode.md` 3.1, `phases.md` 13.3; seams.md 3 row 8 (6Z). (1) Every collectible clue (`clues.json` `collectible`) is briefed `law.briefingAfterS` (30,...
- **A250** Owing the line, part one (10C, C2a, round 10, 2026-10-30). `sim/economy/fare.ts` keeps each seat's fare in room memory; a return on the morning train adds `respawn.fareDebt`, and `Private.fare` (seams.md 3 row 11) shows it to its ...
- **A251** The mill and timber (10D, D3, round 10, 2026-10-29). `head_saw` moves from `keep` to `interact` in the census and gets the class `headSaw`; `saw_horse` (already `interact`) gets `sawHorse`. Two interactions, `sawLogs` (head saw: 1...
- **A253** Chop and smash sound (10X, round 10, x2; 2026-10-30). The logic table (`docs/round9/logic-table.md` 2) gave the Axe's cut modes the noise `chop` and the Pickaxe's break modes `smash`, and A11 shipped them silent because the noise ...
- **A254** Noise lines by kind (10Y, round 10, 2026-10-30). The HUD log picked a noise's line by regex (bell, scream, run or step) and read every other kind as `log.door`, so the `chop` and `smash` kinds 10X's x2 sends from the logic table w...
- **A256** Every gameplay feature in round 10; round 11 is Blender only (owner, 2026-10-30; 6Z). The owner, verbatim: "Real quick how many rounds are you trying to stretch everything, for me round 11 is blender only really, every gameplay fe...
- **A257** The dossier: the paper of the role card and the Satchel (10R, R2, round 10, 2026-10-30). The owner's Q-E1 (A237): "Design those to be paper like", "Only card and Satchel"; the HUD and the world's panels stay on A110's night glass....
- **A260** Rope, and NPC seats with snares (10N, round 10, K6b; 2026-10-30). GDD 3.5 and 3.12; seams.md 6 ("nothing a seat does marks it human"). (1) Rope is an item verb like the Snare (A240): any seat holding one frees a held seat in reach...
- **A262** The mood hooks (10T, round 10, T6b; 2026-10-30; scope.md I40). `sim/npc/moodHooks.ts` narrows a work trip's pool by mood (GDD 3.24); one call line each in `sim/npc/routine.ts` `pickStation` and `sim/townsfolk/run.ts` `pickStation`...
- **A265** Sleeping: beds, homes and the night skip (10A, round 10, A7a; 2026-10-29). GDD 3.32. `sim/Sleep.ts`: a `sleep` hold at a bed within reach lies the seat down at dusk or night (never in the Final Night's hunt). When every active pla...
- **A266** Never-idle NPC seats (10F, D1, 2026-10-29). An NPC seat's routine is a chain of real actions, through the verbs a human uses (GDD 3.12 "Chores"; living-world.md 1.8, owner answers NW3 and NW4). (1) `routines.json` `activities` and...
- **A267** Berries, Game and Stew (10H, S2, round 10, 2026-10-30). From `logic-table.md` 9.6. `resources.json` gets `berries` (2 s, yield 2, respawn 75 s) with two NodeSpots in each of `forest`, `forest_deep` and `bp_woods` (ids `fo.nd_berri...
- **A269** Walk with me: the server (10B, round 10, B8a; 2026-10-29). GDD 3.31; `world-mode.md` 3.1 and R6, `living-world.md` 1.4, `failures.md` 10; seams.md 3 row 10 (6Z). (1) `pair.ask {targetId}` and `pair.answer {yes}` are queued and con...
- **A270** Owing the line, part two (10C, C2b, round 10, 2026-10-30). The Clerk's labour errand, the dear stall, an NPC seat's errand and the two-day check (GDD 3.23; seams.md 3 row 11). Choices made: (1) the errand is `act.hold {action: 'er...
- **A271** The lock-pick: rules and server (10D, D5a, round 10, 2026-10-29). Built on 6Z's reading of LT 8.5: the picker's own `minigameStart.public` carries `{pins, setPoints, band, snapAt, minAttemptS, maxAttempts}` (the set points are a p...
- **A273** talk.test.ts made deterministic (10X, round 10, x3; 2026-10-30). "The call runs off the tick" read `fake.prompts.length` after its last `advance`, and on some seeds that tick starts a second NPC note's call, counted in `prompts` b...
- **A274** The round's new screens on a phone and a desktop (10Y, y3, round 10, 2026-10-30). The inventory and crafting square (A13), the asleep veil (A8), On the line (C1b) and the lock-pick (A311) are driven through `e2e/screens.spec.ts` a...
- **A276** 10S's plan reviewed, and wave 2 (6Z, round 10, 2026-10-30). 6Z's review of `scope.md` (#420) asked for six changes before its rows join `seams.md` 3, all of them secrecy. World mode always deals the Killer to a human, so anything ...
- **A285** Sleeping: what a bed restores and Exhaustion (10A, round 10, A7b; 2026-10-29). GDD 3.32. `sim/SleepRest.ts`, called by `sim/Sleep.ts` on a phase change and in the night. Choices made with 6Z: (1) A bed restores at the dawn that en...
- **A286** Containers and loot (10F, S1, round 10, 2026-10-30). GDD 3.14; `docs/round9/logic-table.md` 6.1 to 6.4. (1) `interactions.json` gains `lootTables` (the ten themes of 6.3) and a `containers` block (the classes dealt, the stocked cr...
- **A287** The forge chain (10H, S3, round 10, 2026-10-30). From `logic-table.md` 7.1, 8.1, 8.2 (the numbers are its proposals). Items: `tinIngot` (kind `deliverable`, because a recipe may not make a `material`), `ironAxe`, `ironPickaxe`, `f...
- **A289** Petitions: the server (10B, round 10, B3a; 2026-10-30). GDD 3.31; `world-mode.md` 3.1 and 5, `followup-4.md` 2.1, `phases.md` 13.1; seams.md 3 row 13 (6Z). (1) `petition.open {accused, charge, entries}` and `petition.sign {id}` ar...
- **A290** What breaks when I'm gone (10C, C3, round 10, 2026-10-30). GDD 3.23; `round10-plan.md` 5; seams.md 3 row 15 (6Z). Choices made with 6Z: (1) every card of `roles.json` carries `townWork {work: 'stall' \| 'faith' \| 'worn' \| 'none'...
- **A291** The bakery's parts and the Herb Bread (10D, D4a, round 10, 2026-10-30). Five recipes on Hollowmere (`dough` at the dough mixer, `proofedDough` at the proofing cabinet, `herbFilling` at the cold shelves, `wakeLoaf` and `herbBread` ...
- **A293** The Logs tooltip (10X, round 10, x8; 2026-10-30). 10G parked it: `items.json` said "Crafting waits for the mill" after D3 shipped the saws (GDD 3.14: the mill's head saw turns one Log into 2 Timber, a saw horse one into 1). The li...
- **A294** Samples stamped by the server tick (10Y, y4, round 10, 2026-10-30). The client stamped each interpolation sample with the frame time that first showed it (`EntityView.ts`), so a patch that carried two ticks, or one the network hel...
- **A296** The end trial, departures, barks, snares and the ledger (6Z, round 10, 2026-10-30). Rulings on six wire rows and the mood hooks, all of them secrecy but (5) (`seams.md` 3, 6). (1) The end trial (B6d, row 35; `phases.md` 5). From B...
- **A309** The manhunt (10B, round 10, B4; 2026-10-30). GDD 3.31; `world-mode.md` 3.1; seams.md 3 row 14 and 6Z's B4 ruling. (1) A passed petition's warrant waits its turn; one manhunt at a time, `manhunt.durationS` 120, public as `GameState...
- **A310** Paint The Town Red: the mode (10C, C5a, round 10, 2026-10-30). GDD 3.8; `world-mode.md` 1.6, followup-4 2.2; seams.md 3 row 18 (6Z). Choices made with 6Z's six rulings: (1) the mode is decided inside `Deck.ts`'s locked deal hook (...
- **A311** The lock-pick screen (10D, D5b, round 10, 2026-10-30). `view/minigames/lockpick.ts` joins the registry as kind `lockpick`; the host gains the optional `pub` (the server's `public`, which the widget draws its board from; the other ...
- **A313** The grindstone (10X, round 10, x9; 2026-10-30). `docs/round9/logic-table.md` 8.1 promised that a grindstone restores a worn tool; A11 shipped the wear without it, and 10G parked it. `interactions.json` gains the class `grindstone`...
- **A314** The Studio NPC editor's save, verified end to end (10Y, round 10, 2026-10-30). The round-9 leftover (`docs/round10/README.md`, "Toward the end"). The server half was already proven (`studioSaveFiles.test.ts`: a `routines.json` bod...
- **A329** The Constables' own petitions (10B, round 10, B3c; 2026-10-30). GDD 3.31; `world-mode.md` 1.6 and 12 R3 ("the Constables open their own petitions on a briefing that fits one figure"); 6Z's approval of 10B's note. (1) Paint The Tow...
- **A330** Paint The Town Red: the Knife on the guards (10C, C5c, round 10, 2026-10-30). GDD 3.8, 3.24; 6Z's grants and rulings for C5's guard step. (1) `Kill.ts` `handleKill` gains one early block, `knifeGuard`, after the role and body chec...
- **A331** The scratch and the fine (10D, D5c, round 10, 2026-10-30; seams.md 3 row 12). A lock a pick opens leaves a `scratch` clue (`ClueKind` 11, appended) on the picked prop's tile: `value` and `dir` 0 whoever picks, `reader` anyone, col...
- **A333** Figures stuck on the client (10X, x4, round 10, 2026-10-30). The production bug: a seat that walked out of another seat's Blood ring (`clues.blood.params.visibleTiles`) froze on that seat's screen where it left the ring, never mov...
- **A334** The ability discs on a phone (10Y, y6, round 10, 2026-10-30). 10R's role-card audit (`docs/round10/rolecards.md` 1.2 A3): the touch cluster had one ability disc, Act (Q), so a phone could not use Impersonate, Salts, Chalk, Rope or...
- **A349** The county jail, held and released (10B, round 10, B5b; 2026-10-30). GDD 3.27; `world-mode.md` 5.1; seams.md 3 row 19 (6Z). The owner (2026-10-30): "keep the default for B5, jail and try them": the cell holds, and the Tribunal tri...
- **A350** The Hitman's arrival (10C, C4a, round 10, 2026-10-30). GDD 3.33, 3.20; `world-mode.md` 1.5, followup-4 2.6; seams.md 3 row 20 (6Z). 6Z's rulings: the C4 split (C4a the arrival, C4b the day weapon and the Dusk Train, C4c the hardsh...
- **A351** Armour with properties (10D, D6a, round 10, 2026-10-30). `items.json` gains kind `armour` and an optional `armor {tier, resist?, staminaRegenMult?, speedMult?}` block on the Quilted coat (tier 1) and the Leather jerkin (tier 2, bl...
- **A353** Figures in the seats' views (10X, x5, round 10, 2026-10-30). A160 left open "the `Visibility.ts` line that puts the living figures of a scene in the seats' views", and no later row closed it: `reconcileAvatars` wanted only handles...
- **A354** The vendetta on the card (10Y, y7, round 10, 2026-10-30). 10R's role-card audit (`docs/round10/rolecards.md` 1.2 A4): `VENDETTA_COPY['vendetta.goal.*']` was used nowhere, the role card never read `Private.vendetta`, so a Killer ne...
- **A369** The county jail's cell (10B, round 10, B5a; 2026-10-30). GDD 3.27; `world-mode.md` 5.1; seams.md 3 row 19 (6Z); 6Z's approval of the B5 split and grant 1. (1) `cj_cell` is appended to `SCENE_IDS` (ids `cj.`), a 12x8 house interior...
- **A370** The Hitman's day weapon and the Dusk Train (10C, C4b, round 10, 2026-10-30). GDD 3.33, 3.20; followup-4 2.6 b6; seams.md 3 row 21 (6Z). Stacked on C4a (#401); 6Z merges C4a, C4b and 10Y's client PR back to back. 6Z's rulings: (1) ...
- **A371** Skinning (10D, D6b, round 10, 2026-10-30). `skinningKnife` (tool `skin` 1, 20 uses, neutral, `use: skin`), `hide` (material) and `game` (food) join `items.json`; `mobs.json` rows gain an optional `skin {hide, game}` (wolf 2/1, boa...
- **A373** One patch per tick (10X, x7, round 10, 2026-10-30). `PartyRoom` ran two timers at 50 ms, the fixed step's and the patch's (`patchRate`), and they drifted against each other, so a patch carried two ticks or none by turns, the clien...
- **A374** The hand recipes point to the square (10Y, round 10, 2026-10-30). Owner answer (b) on `docs/round10/rolecards.md` 1.2: the Craft panel stays, Make and the `craft` hold stay for the station recipes, and a recipe with no station (to...
- **A389** The Tribunal (10B, round 10, B6a; 2026-10-30). GDD 3.8; `phases.md` 4, `world-mode.md` 5; seams.md 3 row 22 and row 19's amendment (6Z). 6Z's rulings (2026-10-30): B6 splits into B6a (the Tribunal, the verdict and the death, jail ...
- **A390** The dormant role and the hardships (10C, C4c, round 10, 2026-10-30). GDD 3.33, 3.23; followup-4 2.6 b1 to b5; seams.md 3 rows 11, 15 and 20. Stacked on C4b (#408). (1) The dormant role moved here from C4a (6Z's review: the sign sh...
- **A391** Rent in kind and the boarded house (10D, D7, round 10, 2026-10-30). `act.payRent` (`sim/economy/rent.ts`) takes the purse first and goods at the market's `pay` price toward the rest (cheapest first), whole or not at all (`NEED_SCR...
- **A392** The Clerk's rent ledger (10C, C4d, round 10, 2026-10-30). GDD 3.33; followup-4 2.6 b5 and 2.7; seams.md 3 row 37 (6Z). Stacked on C4c (#432). (1) `ledger.read {propId}` (C2S, new) at a `ledger` prop in reach is queued and consumed...
- **A393** The Bandage knockback (10X, x10, round 10, 2026-10-30). GDD 3.2's role table has said "both are knocked back" since round 3 and its M3 note "the knockback still waits"; the blackout and the Claimed entries were built in `Struck.ts...
- **A394** The phone's top rows, the band's floor and the out slot (10Y, round 10, 2026-10-30). CSS only, UI.md 14.51.4. On a phone (`components.css`, the 480px block) the goal chip and the Notebook button own the top row, the clock sits in ...
- **A409** The Final Night's end trial (10B, round 10, B6d; 2026-10-30). GDD 3.3 and 3.8; `phases.md` 5, `world-mode.md` 2 and 3; seams.md 3 row 35 (6Z). 6Z's rulings (2026-10-30): the end trial is the only Final Night verdict from B6d on, i...
- **A411** Quest chains (10D, D9a, round 10, 2026-10-30). `quests.json` rows gain an optional `after` (a quest of the same giver, one step deep; the validator checks both). `handleQuestAccept` refuses a step whose `after` is not done with `N...
- **A413** The Herb Bread's buff lasts until the dawn (10X, x11, round 10, 2026-10-30; owner ruling through 6Z: "dawn"). D4a (A371) gave the private Resistant effect a clock, `durationS` 780, "about to the next dawn". It now lasts until the ...
- **A414** UI.md 14 against the copy modules (10Y, round 10, 2026-10-30). The copy deck's tables had parted from the client over six rounds: 18 rows named keys no module holds (the ghost lines of 14.8, the game-over reasons of 14.10, the mee...
- **A431** Talk to a figure (10D, D9c, round 10, 2026-10-30; seams.md 3 row 16). `talk.ask {targetId, ask}` (`ask` is `town` or `time`) is queued in `step()` by `sim/townsfolk/talk.ts` and answered `balance.figureTalk.delayS` later as a syst...
- **A433** NPC night baking, the R6 audit's first cut (10X, x13, round 10, 2026-10-30; _proposed_). The owner's ruling through 6Z: NPC work gains the night class at the lit bakery stations, as a first cut, marked _proposed_. `routines.json` ...
- **A434** The imported look's toon group (10Y, y11, round 10, 2026-10-30). 11B found (`docs/round11/look.md` 1.3, `pipeline.md` 5.4) that `batch_render.import_character` appends a look's `.blend` with its own copy of the toon node group, so...
- **A451** The jail's mini-games (10D, D8, round 10, 2026-10-30). GDD 3.27; `round9/world-mode.md` 5.1; owner answer LW10. (1) Three props in `cj_cell` on new stems with census decisions (`barbell`, `sparring_post`, `scrub_pail`, all `intera...
- **A453** Decoded views (10X, x14, round 10, 2026-10-30; _proposed_). 6Z's x14 ruling, option (a): `pnpm auto -- --views` attaches a shadow `StateView` per seat (`sim/auto/shadowViews.ts`), built by `createPlayerView` and reconciled in `Vis...
- **A454** The figures' nameplates by the look on the wire (10Y, y12, round 10, 2026-10-30). UI.md 14.36; GDD 3.24 and 3.31. Found: `figureName(lookOf)` keyed the Clerk's and the Tallyman's lines as `figure.villager_clerk` and `figure.villag...
- **A471** The mugging's Flee and Fight (10D, S4, round 10, 2026-10-30). GDD 3.24; A180 part two; scope A256. Both answers of the private prompt (UI 14.36.1) now run in `sim/townsfolk/mug.ts`, with nothing new on the wire. (1) Flee: a chase ...
- **A474** On the line: the place, the book and the bells (10Y, y13, round 10, 2026-10-30). UI.md 14.47 and 14.51.5; GDD 3.3 and 3.22; `docs/round9/phases.md` 6. C1b (A230, UI.md 14.47) shipped the screen with its clock, its cause line and w...
- **A491** The bakery's pastry dishes (10D, D4b, round 10, 2026-11-12). GDD 3.14; logic table 7.1 and R12. Built on S2's berries and Game (#430, still a draft when this began, at the owner's word to start): the PR is stacked on that branch a...
- **A494** The stale e2e specs: the ghost's cutscene, the gathered one and the counter by the square (10Y, y14, round 10, 2026-10-30). `e2e/cutscene.spec.ts`, `e2e/m5b.spec.ts`, `net/mock/worldMock.ts`; UI.md 14.44. The whole Playwright suit...
- **A514** The Playwright suite in CI (10Y, y15, round 10, 2026-10-30). `.github/workflows/ci.yml`; ARCHITECTURE 5.10 and 5.12; 6Z's answer to the question A494 left open. A third job, `e2e`, runs the whole Playwright suite against the real ...
- **A518** Story client, part 2 (P3): section and NPC-line cards. `story.card` gains the kinds `section` (the section that starts; replaces the chapter title card after the first section) and `line` (a scripted NPC speaking), and the optiona...
- **A519** Story client, part 2 (P3): save and resume, client half. `story.saved` (S2C, private: `{ save }`) and `story.start.resume` (the save passed back untouched) per `docs/accounts/plan.md` 5 (A1). The client keeps the save in a `StoryS...
- **A520** Story client, part 2 (P3): the end screen. A dedicated screen after the story's last end card: the chapters in order with their one-line summaries, counters and a Lost mark, and the story-tree achievements earned on the device (A5...
- **A534** The art style in the menu only (10Y, S5, round 10, 2026-10-30). Round 9's `world-mode.md` 10 and `phases.md` 10, the owner verbatim: "in the new mode I want the 8bit/lowpoly/HD gone inside the game, it breaks it when used, menu on...
- **A554** The stale e2e gates go (10Y, y16, round 10, 2026-10-30). 6Z's rule after A514 (4): a gate whose reason no longer holds goes, and a spec that then fails is fixed or attributed, never left skipped. `match.spec.ts`, `npc.spec.ts` and...
- **A555** The cover-up verbs (10V, V2, round 10, 2026-11-07). GDD 3.4; `docs/round10/rolecards.md` 11 (owner answers Q-A3 and Q-A4); seams.md 3 row 38 (proposed). `sim/verbs/coverup.ts` runs Drag body, Clean (the Bloody Rag), Wash (the Buck...
- **A574** The Hitman's client half (10Y, round 10, C4b, 2026-11-12). GDD 3.33; UI.md 14.51.7; seams.md 3 rows 20 and 21, read as they stand, so nothing is added to the wire. (1) The Derringer's slot. It is an item ability (`scope: item`) th...
- **A575** NPC seats present and file (10B, B6d2, round 10, 2026-11-07). `apps/server/src/sim/npc/trial.ts`; GDD 3.8 and 3.12 "Presenting and filing"; seams.md 3 row 35. The rule that closes B6a's tell and row 35's human-only filing. (1) Str...
- **A576** The evidence verbs, part two: Dust, Compare and Autopsy (10V, V1b, round 10, 2026-11-07). GDD 3.2 and 3.4; `seams.md` 3 row 24; `rolecards.md` 11. `sim/verbs/prints.ts` (Dust, Compare, the print memory) and `sim/verbs/autopsy.ts`....
- **A578** The hiding spots and the kit verbs (10V, V3, round 10, 2026-11-07). GDD 3.2, 3.4 and 3.7; `docs/round10/rolecards.md` 11. `sim/verbs/hiding.ts` runs Hide, Check and Burst Out (`act.hide`, `act.check`, `act.burst {spotId}`, queued ...
- **A579** A body in reach wins the E prompt (owner, 2026-11-12; 10S, W1a1, PR #447). GDD 3.4. The client's prompt (`scenes/World.ts updateTarget`) took the strictly nearest of a body, a clue, the bell and a door, so a killer standing on the...
- **A420** Story mode's wire and cards (S3, story mode, 2026-11-06). `packages/shared/src/protocol/index.ts`, `docs/PROTOCOL.md`, UI.md 14.61, `apps/client/src/ui/story/`. Decided, following `docs/story/README.md` 3: `story.start {storyId, c...
- **A401** The story schema, and the Bandit is the Thief card (S1, story mode, 2026-11-06). `docs/story/README.md` 1; `packages/content/src/schemas/story.ts`, `validateStory.ts`, `data/story.json`. `roles.json` has no Bandit card: the Bandit...
- **A415** The story engine moves the card, not the seat (S2, story mode, 2026-11-06). A client is bound to its seat id (session id) all through the handlers, so a chapter break cannot move the player to another seat id. `switchRole` (`sim/s...
- **A416** The beat runner (S2, story mode, 2026-11-06). One Step stage after `runEvents`. Triggers are evaluated as README 1a fixes them (`tick` = chapter ticks, which stop while a card pauses the clock; events latched per leaf). Cards queu...
- **A417** Story rooms are lone-human lobbies (S2, story mode, 2026-11-06). `story.start` is honoured only from the room's leader when it is the only human, in the lobby, once; the room becomes an auto room with the story's NPC roster under ...
- **A430** Story mode: the Bandit is the outlaw, and the story gets two Killer chapters (owner, 2026-11-06; supersedes the Thief mapping of A401). The owner: "the bandit is the outlaw, a thief could be a heist man later", and asked for Kille...
- **A516** Story mode, part 2: the full story (owner, 2026-11-06). Answers to `docs/story/questions.md`. The story becomes the whole lore on HollowMere, every role in it; a chapter is built around the lore, not one role, so it is made of sec...
- **A515** The HollowMere arc is approved, with eight changes (owner, 2026-11-07). Every section, cast card and through-line of `docs/story/arc.md` is approved as written (no story, tone or revision requests). Changes to the questions: Q-A5 ...
- **A517** Part 2 build decisions (owner, 2026-11-07). W1: the Medium's resurrection applies in every game, multiplayer included; the owner's note: it only applies if the Vicar wants to return with the 10X buff. W2: build player accounts now...
- **A440** Achievements are chains of steps on bus events, and trees by `after` (P4, E1, 2026-11-06). `packages/content/data/achievements.json` holds trees and achievements; an achievement's steps are patterns on a sim bus kind (who, exact d...
- **A441** Evaluation is a bus subscriber, progress is per match (P4, E1, 2026-11-06). `sim/achievements/` subscribes once per room to every bus kind, so a step is evaluated in `step()` after the tick's events are delivered (never in a messa...
- **A442** The `achv` message is private and names only an achievement (P4, E1, 2026-11-06). `achv {id, step, steps, done}` goes to the earning seat's own client and is never in the state, a broadcast, a spectator or the admin room; the A168...
- **A443** The trial steps wait on B6 (P4, E1, 2026-11-06). B6a is merged and B6b to B6d are not, so no step names a `tribunal.*` kind. The list of what waits is in `docs/story/status.md` (P4). No reward changes power: an achievement is a ti...
- **A589** The story engine runs sections (P2, E1 and E7, 2026-11-07). `sim/story` plays an arc chapter as its sections in order (`units.ts` flattens the arc; the running unit is a section, and `story.chapterStart`/`End`, the card's `chapter...
- **A579** A failed section replays once, in place (P2, owner A515, 2026-11-08). A death in a section ends it as failed and shows its end card, then the same section starts again: `switchRole` on the card the seat already holds makes the sea...
- **A577** The story save is a port with a device implementation (P2, accounts plan 5 A1, 2026-11-08). `apps/server/src/accounts/saves.ts`: `StorySave`, `SaveStore {get, put, clear}`, `DeviceSaveStore` and `saveStoreFor`. The engine writes a...
- **A556** Story client, part 2 (P3): the menu lists arc chapters. The Story menu and the end screen read `content.storyArc` chapters (their ids are on every card and save, P2's #479) instead of the part-1 plays of `content.story`, one row p...
- **A580** The chapter's cast is a swap after the deal (P2, E2, 2026-11-08). A chapter may name `cast`, the cards at the table. `Deck.ts` (locked) deals only deck cards, so the cast is not a deal: after the first section's card has moved, `c...
- **A581** No early win (P2, E3, 2026-11-08). `endMatch` asks the story first (`holdMatch`): before the story's last section a win is held, `story.win` is emitted, and the next story step ends the running section as done (never failed, no re...
- **A582** The NPC Killer's vendetta per section (P2, E4, 2026-11-08). `Unit.npcVendetta` is set on the NPC Killer when a section starts (`setVendetta`, `resetProgress`), after the swap and the cast, never on a replay. The player's later Kil...
- **A583** A fixed Hitman in a story (P2, E5, 2026-11-08). `turnForStory` (`vendettas/arrival.ts`) turns the player's seat at the section's start: arrival state set by hand (day null, `story` true), the `hitman` vendetta, `Private.hitman`, t...
- **A584** The heir section waits for its `startWhen` (P2, E6, 2026-11-08). `runInherit` emits the bus event `inherit {seat}` (none today; no existing listener changes). A `Unit` with `startWhen` is not started by `afterEndCard`: `state.wait...
- **A586** Pick events; read events wait for a reader (P2, E9, 2026-11-08). `lockResult` (`Minigames.ts`) emits `story.picked {lock}` for the picker when a lock opens, and the runner's inbox lets it through beside `story.enter` and `story.pi...
- **A585** Night-power events (P2, E8, 2026-11-08). `applyPower` (`NightPowers.ts`), the one path for a human's and an NPC's accepted power, emits `nightPower {ability, target}` with the user's seat. Server-internal like every bus event: `AD...
- **A587** The company trigger is an event the runner hears for (P2, E10, 2026-11-08). `watchCompany` (`story/Story.ts`) counts, per seat and per section, the ticks the player and that seat are alive, placed and in one scene in a world phase...
- **A588** Cutscenes play and the bell rings from a beat (P2, E12, 2026-11-08). A `cutscene` action now also broadcasts `cutscene { id, scope: 'all' }` (it only emitted `story.cutscene` before); a new `meeting: true` action queues a bell mee...
- **A591** Staging at a break (P2, E14, 2026-11-08). `npcOrder goTo` already works from a section's `tick: 0` beat; what was missing was a spot in the scene and a typo guard. `args.spawn` names a spawn of `args.scene` (else the first), and `...
- **A590** Holy-war rules vs. B6 (P2, E13, 2026-11-08). GDD 3.20's prose said the Zealot's doubt is sown at 45 s while `balance.json` `vendettas.conversion.shareS` is 160 (round 9 `world-mode.md` moved it to 160 so shared time counts in ever...
- **A600** The Medium's rite: the owner's answers, and the Medium card retired (R, R1, 2026-11-10). The owner took the default on every one of R-Q1 to R-Q8 of `docs/story/rite.md` 3 (2026-11-10). R-Q1: the 10X buff is the area-spread convers...
- **A601** The martyr's shade (R, R2, 2026-11-10; A600 R-Q3, R-Q4). `sim/rite/shade.ts`: the first seat of a match in the Vicar's public look struck by the Knife, cover or not, is the match's shade from its death (`markDead` asks `becomesSha...
- **A602** The Medium and the rite (R, R3, 2026-11-10; A600 R-Q2, R-Q7). `sim/rite/rite.ts`, run each tick from `runMemorial` (no locked line). The Medium is an avatar with no seat at `balance.json` `rite.site` (scene `forest_deep`, spawn `w...
- **A603** The martyr's return, the gated due, the candidacy gone (R, R4, 2026-11-10; A600 R-Q5, R-Q6, R-Q8). `sim/rite/return.ts`. The shade's wait now ends in `rite.ts` (a `phase` listener for `day` and `finalNight`; `shade.ts` exports `en...
- **A604** The 10X Vicar's buff (R, R5, 2026-11-10; A600 R-Q1). `sim/rite/buff.ts`. At the return (`return.ts`) the fresh body takes the new private effect `ascended` (`EffectId` 17, appended after the base's D4b dishes took 15 and 16 when `...
- **A605** The rite on the client (R, R7, 2026-11-10; A600, `docs/story/rite.md` R7). `ui/rite/RiteLayer.ts` with `rules.ts`, and `ui/copy/rite.ts`. The feed passes the private `rite` message to its bus (`WorldFeedEvents.rite`). A per-feed m...
- **A606** Conversion, the sermon and the Peaceful route (story I9, 2026-11-11; round 10 scope I9 and 2.2, W7; built by R on the owner's word, into `claude/story-part2`). `sim/economy/conversion.ts`, `sim/routes/peaceful.ts`, run each tick f...
- **A607** The conversion aura (story R6, 2026-11-12; A600 R-Q1 and R-Q3, owner defaults of 2026-11-10; built on I9, A606). `sim/rite/aura.ts`, run each tick from `runMemorial` before `runConversion`. While the dealt Vicar (`dealtVicarOf`) w...
- **A608** R8, the martyr's section, drafted (story R, 2026-11-12, on the owner's "draft the R8 arc.md section and start R8"). `docs/story/arc.md` 3.4 "The Strength of Ten": card `vicar`, played as the martyr's shade (the rite at `rite.site`...
- **A609** The owner's sign-off on the round-10 proposals (owner, 2026-11-13, "all yes"). The owner approved, as built and merged, every item each PR listed under its owner sign-off: #422 (S4, the mugging's Flee and Fight: `moods.mug` `chase...
- **A610** V2 starts with a first-person walk-through of the 3D HollowMere (owner, 2026-11-13; built by W3D on `claude/v2-walk`). The owner wants to walk the village, woods, mine and outskirts that the Blender session built from the owner's ...
- **A611** Two views of the game: the 2.5D game stays, and a 3D HD first-person view is added (owner, 2026-11-15). The owner's words: "I still want to have the option between the 2.5d 8 bit (or low poly depending on which is better look) but...
- **A612** Every map-revamp building gets an interior (owner, 2026-11-16). The owner's words: "each map-revamp building gets an interior". Every building listed in `docs/map-revamp/interiors-plan.md` section 3 that a player can enter (the ou...
- **A613** Two modes only: 2.5D and 3D. The three 2.5D art styles become one (owner, 2026-11-16). The owner's words: "We are going to mix all of the best parts of 8bit, low poly, and HD 2.5 into one mode and now there will only be to modes: ...
- **A614** Each room is its own GLB, and the village is cut into sections joined by portals (owner, 2026-11-16). The owner's words, relayed by the Blender session and confirmed to the orchestrator: "Each room should be its own GLB. Also each...
- **A615** The merged 2.5D look: a sprite world with depth (owner, 2026-11-17). The owner's words: "Characters are HD, everything else is 8 for small objects and a more complex designs are 64bit to 128bit. New map revamp should be modeled af...
- **A616** Round 11 re-planned for the sprite world, with every default (owner, 2026-11-19). The owner's words: "Approved, use the defaults and merge 551". (1) `docs/round11/round11-plan-v2.md` replaces `round11-plan.md` (A236) as the round'...
- **A617** Open questions the code has settled (docs pass, 2026-11-19; recorded, not decided). Each item below was settled by code or by a later row; the earlier rows keep their text, and this row is the pointer. (1) A610, where the GLB is h...
- **A618** S0: Three.js joins the client for the sprite world (round 11, plan step S0, 2026-11-19). (1) `apps/client` takes `three 0.186.1` and `@types/three 0.186.0`, the exact pins of `apps/walk` (`ARCHITECTURE.md` 5.1); no other Three.js ...

## 8. Questionnaires in this repo

- `docs/round11/questions.md`: 22 questions. SC1 Which art stays outside Blender? (11A P9, 11B Q10); SC2 Models from Meshy (your ROSW `asset-3d` pipeline) in the shipped art? (11A P7, 1; SC3 Export every master for V2, the first-person version? (11B Q13); CL1 Keep the camera and the scale exactly as they are? (11A P1); CL2 One light for every style? (11A P2); CL3 Long shadows from buildings, as a ground layer that fades at dusk? (11A P3); CL4 Lamps that light the walls as you carry them? (11A P4, 11B Q14); ST1 Keep all three styles: 8-bit, low poly and HD? (11B Q1); ST2 8-bit figures: flat colour or textured? (11B Q5); ST3 Low-poly figures: flat colour or textured? (11B Q6); ST4 HD figures: how do they fit? (11B Q2); ST5 Render the HD figures under the sky light? (11B Q15); ST6 Texture sizes: 1k maps for every sprite render, with the 2k maps kept for V2? (1; ST7 A colour check for low poly and HD? (11B Q12); BU1 A memory cap for HD alone? (11B Q3); BU2 The HD download budget? (11B Q4); BU3 The first load: keep the 12 MiB cap, and leave the 8 MiB target for later? (11B ; BU4 The test phone and the frame-rate floor? (11B Q9); RN1 Where do the renders run? (11A P5); RN2 HD render quality: 8 samples instead of 32? (11A P5, 11B Q16); RN3 May the cloud environment install Blender for every session? (11A P6); RN4 Keep a copy of the free Kenney model packs as a release download of this repo? (
- `docs/story/questions.md`: 17 questions. A1 Chapter 3 is the Bandit, the outlaw. The Killer card with the `bandit` heist ven; A2 Chapter 4 is the Activist. The Killer card with the `activist` sabotage vendetta; A3 Four chapters, in this order. Baker, Watchman, Bandit, Activist. Chapters play i; A4 The chapter looks. The Bandit walks as the `drifter` look and the Activist as th; B1 A dead player. A death inside a chapter ends it as failed, shows the failed line; B2 Pausing. The world pauses only while a story card is up (there is no second huma; B3 Saving. None. A story is one sitting of about 25 minutes of play; leaving ends i; B4 The handover moves the card, not the seat (DECISIONS A415). The player keeps the; B5 The story's end. After chapter 4 the room ends as a Village win.; C1 A fifth Killer chapter. The Zealot (the Skin-Walk, needs a Vicar) or the Hitman ; C2 A heist-man chapter on the Thief card. The Thief card is never dealt in a story ; C3 NPC dialogue. Beats show narration only; the NPCs speak through the existing tal; C4 Other towns. Port-au-Levain and BlackPine stories (Bible V.1) are out of scope.; D1 Playtest. Chapters 3 and 4 ask the player to stand still beside a target unseen.; D2 Achievements. Each chapter end emits `story.chapterEnd` for round 10's E1 (achie; D3 The check I did not run. `pnpm auto` at 50 ran on the head before the Killer cha; D4 Production. The base deploys to Railway on every push, so story mode is live.

## 10. Pull requests merged (395)

- 2026-10-21 #46 from `groot99-droid/claude/r5-art-style`
- 2026-10-22 #47 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #76 from `groot99-droid/claude/r6-rosw-media-3`
- 2026-10-23 #77 from `groot99-droid/claude/r6-rosw-media-4`
- 2026-10-23 #78 from `groot99-droid/claude/r6-vicar-voice`
- 2026-10-23 #79 from `groot99-droid/claude/r6-intro-explosion`
- 2026-10-23 #80 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #81 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #82 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #85 from `groot99-droid/claude/r7-parties-server`
- 2026-10-23 #86 from `groot99-droid/claude/r7-theme`
- 2026-10-23 #88 from `groot99-droid/claude/r7-vendettas`
- 2026-10-23 #84 from `groot99-droid/claude/r6-intro-trim`
- 2026-10-23 #89 from `groot99-droid/claude/r7-parties-server`
- 2026-10-23 #93 from `groot99-droid/claude/r6-test-determinism`
- 2026-10-23 #83 from `groot99-droid/claude/r7-map-intros`
- 2026-10-23 #91 from `groot99-droid/claude/r7-lobby`
- 2026-10-23 #92 from `groot99-droid/claude/r7-lobby-b`
- 2026-10-23 #87 from `groot99-droid/claude/r7-train`
- 2026-10-23 #90 from `groot99-droid/claude/r7-match-ui`
- 2026-10-23 #96 from `groot99-droid/claude/r7-theme`
- 2026-10-23 #98 from `groot99-droid/claude/r7-match-ui`
- 2026-10-23 #94 from `groot99-droid/claude/r7-menu`
- 2026-10-23 #101 from `groot99-droid/claude/r7-map-intros`
- 2026-10-23 #99 from `groot99-droid/claude/r7-match-ui`
- 2026-10-23 #97 from `groot99-droid/claude/r7-vendettas`
- 2026-10-23 #104 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #100 from `groot99-droid/claude/r7-theme`
- 2026-10-23 #102 from `groot99-droid/claude/r7-lobby-3`
- 2026-10-23 #106 from `groot99-droid/claude/r7-menu`
- 2026-10-23 #108 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #105 from `groot99-droid/claude/r7-map-intros`
- 2026-10-23 #107 from `groot99-droid/claude/r7-vendettas`
- 2026-10-23 #111 from `groot99-droid/claude/r7-ovens`
- 2026-10-23 #95 from `groot99-droid/claude/r7-table-ui`
- 2026-10-23 #110 from `groot99-droid/claude/r7-menu`
- 2026-10-23 #112 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #113 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #116 from `groot99-droid/claude/r7-map-intros`
- 2026-10-23 #103 from `groot99-droid/claude/r7-train`
- 2026-10-23 #109 from `groot99-droid/claude/r7-remove-quick`
- 2026-10-23 #117 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #120 from `groot99-droid/claude/r7-table-ui`
- 2026-10-23 #114 from `groot99-droid/claude/r7-ovens`
- 2026-10-23 #115 from `groot99-droid/claude/r7-vendettas`
- 2026-10-23 #122 from `groot99-droid/claude/r7-ovens`
- 2026-10-23 #119 from `groot99-droid/claude/r7-map-intros`
- 2026-10-23 #123 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #121 from `groot99-droid/claude/r7-remove-quick`
- 2026-10-23 #124 from `groot99-droid/claude/r7-map-intros`
- 2026-10-23 #125 from `groot99-droid/claude/r7-vendettas`
- 2026-10-23 #126 from `groot99-droid/claude/r7-map-intros`
- 2026-10-23 #73 from `groot99-droid/claude/r6-integration`
- 2026-10-23 #127 from `groot99-droid/claude/r7-remove-quick`
- 2026-10-23 #128 from `groot99-droid/claude/r7-vendettas`
- 2026-10-23 #129 from `groot99-droid/claude/r7-minigames`
- 2026-10-23 #130 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #131 from `groot99-droid/claude/r8-body`
- 2026-10-23 #135 from `groot99-droid/claude/r8-creatures-vfx`
- 2026-10-23 #133 from `groot99-droid/claude/r8-hollowmere-rooms`
- 2026-10-23 #136 from `groot99-droid/claude/r8-ui-motion`
- 2026-10-23 #145 from `groot99-droid/claude/r7-minigames`
- 2026-10-23 #118 from `groot99-droid/claude/sweet-maxwell-lmsiw3`
- 2026-10-23 #144 from `groot99-droid/claude/r8-characters`
- 2026-10-23 #139 from `groot99-droid/claude/r8-inspect`
- 2026-10-23 #137 from `groot99-droid/claude/r8-ui-motion-panels`
- 2026-10-23 #165 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-23 #140 from `groot99-droid/claude/r8-ui-motion-activation`
- 2026-10-23 #150 from `groot99-droid/claude/r8-inspect-ui`
- 2026-10-23 #147 from `groot99-droid/claude/r8-ui-motion-transitions`
- 2026-10-23 #153 from `groot99-droid/claude/r8-creatures-vfx-breaks`
- 2026-10-23 #161 from `groot99-droid/claude/r8-creatures-vfx-transport`
- 2026-10-23 #143 from `groot99-droid/claude/r8-blackpine-rooms`
- 2026-10-23 #149 from `groot99-droid/claude/r8-blackpine-kit`
- 2026-10-23 #151 from `groot99-droid/claude/r8-blackpine-placed`
- 2026-10-23 #172 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #190 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #146 from `groot99-droid/claude/r8-creatures-vfx-fx`
- 2026-10-24 #189 from `groot99-droid/claude/r8-creatures-vfx-coins`
- 2026-10-24 #141 from `groot99-droid/claude/r8-scrip`
- 2026-10-24 #148 from `groot99-droid/claude/r8-scrip-wages`
- 2026-10-24 #155 from `groot99-droid/claude/r8-scrip-shops`
- 2026-10-24 #158 from `groot99-droid/claude/r8-scrip-bank`
- 2026-10-24 #180 from `groot99-droid/claude/r8-scrip-coins`
- 2026-10-24 #152 from `groot99-droid/claude/r8-hollowmere-chapel`
- 2026-10-24 #162 from `groot99-droid/claude/r8-hollowmere-manor-art`
- 2026-10-24 #163 from `groot99-droid/claude/r8-hollowmere-manor`
- 2026-10-24 #175 from `groot99-droid/claude/r8-hollowmere-shot-hook`
- 2026-10-24 #138 from `groot99-droid/claude/r8-hd`
- 2026-10-24 #160 from `groot99-droid/claude/r8-hd-render`
- 2026-10-24 #167 from `groot99-droid/claude/r8-anticheat`
- 2026-10-24 #192 from `groot99-droid/claude/r8-anticheat-replay`
- 2026-10-24 #171 from `groot99-droid/claude/r8-icons`
- 2026-10-24 #183 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #156 from `groot99-droid/claude/r8-blackpine-economy`
- 2026-10-24 #200 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #154 from `groot99-droid/claude/r8-characters-2a`
- 2026-10-24 #198 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #195 from `groot99-droid/claude/r8-characters-4`
- 2026-10-24 #196 from `groot99-droid/claude/r8-characters-5`
- 2026-10-24 #197 from `groot99-droid/claude/r8-characters-6`
- 2026-10-24 #181 from `groot99-droid/claude/r8-anticheat-vote`
- 2026-10-24 #199 from `groot99-droid/claude/r8-blackpine-shops`
- 2026-10-24 #132 from `groot99-droid/claude/r8-civic`
- 2026-10-24 #168 from `groot99-droid/claude/r8-hd-proposal`
- 2026-10-24 #205 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #174 from `groot99-droid/claude/r8-scrip-shop-panel`
- 2026-10-24 #177 from `groot99-droid/claude/r8-scrip-purse-hud`
- 2026-10-24 #211 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #184 from `groot99-droid/claude/r8-characters-2b`
- 2026-10-24 #203 from `groot99-droid/claude/r8-characters-7`
- 2026-10-24 #213 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #134 from `groot99-droid/claude/r8-civic-rumours`
- 2026-10-24 #201 from `groot99-droid/claude/r8-civic-faith`
- 2026-10-24 #202 from `groot99-droid/claude/r8-talk`
- 2026-10-24 #216 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #214 from `groot99-droid/claude/r8-scrip-feedback`
- 2026-10-24 #215 from `groot99-droid/claude/r8-ui-motion-hud`
- 2026-10-24 #176 from `groot99-droid/claude/r8-rules`
- 2026-10-24 #220 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #218 from `groot99-droid/claude/r8-talk`
- 2026-10-24 #169 from `groot99-droid/claude/r8-hd-client`
- 2026-10-24 #170 from `groot99-droid/claude/r8-hd-budgets`
- 2026-10-24 #221 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #212 from `groot99-droid/claude/r8-blackpine-altar`
- 2026-10-24 #182 from `groot99-droid/claude/r8-hollowmere-budget`
- 2026-10-24 #191 from `groot99-droid/claude/r8-hollowmere-tavern`
- 2026-10-24 #193 from `groot99-droid/claude/r8-hollowmere-widow`
- 2026-10-24 #217 from `groot99-droid/claude/r8-stations`
- 2026-10-24 #223 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #219 from `groot99-droid/claude/r8-civic-rent`
- 2026-10-24 #224 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #222 from `groot99-droid/claude/r8-civic-hq`
- 2026-10-24 #208 from `groot99-droid/claude/r8-hive`
- 2026-10-24 #227 from `groot99-droid/claude/r8-creatures-vfx-sounds`
- 2026-10-24 #210 from `groot99-droid/claude/r8-hive-senses`
- 2026-10-24 #225 from `groot99-droid/claude/r8-civic-ui-feed`
- 2026-10-24 #226 from `groot99-droid/claude/r8-civic-ui`
- 2026-10-24 #228 from `groot99-droid/claude/r8-hollowmere-apothecary`
- 2026-10-24 #185 from `groot99-droid/claude/r8-rules-3`
- 2026-10-24 #187 from `groot99-droid/claude/r8-rules-4`
- 2026-10-24 #179 from `groot99-droid/claude/r8-rules-2`
- 2026-10-24 #229 from `groot99-droid/claude/r8-civic-seams`
- 2026-10-24 #232 from `groot99-droid/claude/r8-hollowmere-bakery`
- 2026-10-24 #231 from `groot99-droid/claude/r8-creatures-vfx-hq`
- 2026-10-24 #233 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #230 from `groot99-droid/claude/r8-hive`
- 2026-10-24 #234 from `groot99-droid/claude/r8-hollowmere-barn`
- 2026-10-24 #235 from `groot99-droid/claude/r8-hq-real-props`
- 2026-10-24 #236 from `groot99-droid/claude/r8-hollowmere-forest`
- 2026-10-24 #237 from `groot99-droid/claude/r8-hive`
- 2026-10-24 #238 from `groot99-droid/claude/r8-hollowmere-overworld`
- 2026-10-24 #239 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #142 from `groot99-droid/claude/r8-townsfolk`
- 2026-10-24 #240 from `groot99-droid/claude/r8-canon`
- 2026-10-24 #241 from `groot99-droid/claude/r8-canon-c2`
- 2026-10-24 #242 from `groot99-droid/claude/r8-canon-c3`
- 2026-10-24 #157 from `groot99-droid/claude/r8-townsfolk-moods`
- 2026-10-24 #247 from `groot99-droid/claude/r8-talk`
- 2026-10-24 #249 from `groot99-droid/claude/r7-minigames`
- 2026-10-24 #248 from `groot99-droid/claude/r8-icons`
- 2026-10-24 #250 from `groot99-droid/claude/r8-icons-mark`
- 2026-10-24 #251 from `groot99-droid/claude/r8-icons-hud`
- 2026-10-24 #204 from `groot99-droid/claude/r8-hd-renders`
- 2026-10-24 #255 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-24 #159 from `groot99-droid/claude/r8-townsfolk-figures`
- 2026-10-24 #254 from `groot99-droid/claude/r8-talk`
- 2026-10-24 #194 from `groot99-droid/claude/r8-characters-3`
- 2026-10-24 #166 from `groot99-droid/claude/r8-body-2`
- 2026-10-24 #173 from `groot99-droid/claude/r8-body-3`
- 2026-10-24 #164 from `groot99-droid/claude/r8-townsfolk-death`
- 2026-10-24 #186 from `groot99-droid/claude/r8-body-4`
- 2026-10-24 #206 from `groot99-droid/claude/r8-townsfolk-mug`
- 2026-10-24 #188 from `groot99-droid/claude/r8-body-5`
- 2026-10-24 #256 from `groot99-droid/claude/r8-shelf-pages`
- 2026-10-24 #207 from `groot99-droid/claude/r8-townsfolk-mug-run`
- 2026-10-24 #259 from `groot99-droid/claude/r8-seal-meeting`
- 2026-10-24 #209 from `groot99-droid/claude/r8-townsfolk-mug-ui`
- 2026-10-24 #262 from `groot99-droid/claude/r8-ui-motion-body`
- 2026-10-24 #258 from `groot99-droid/claude/r8-scrip-ko`
- 2026-10-24 #253 from `groot99-droid/claude/r8-body-6`
- 2026-10-24 #257 from `groot99-droid/claude/r8-talk`
- 2026-10-24 #243 from `groot99-droid/claude/r8-canon-r1`
- 2026-10-24 #244 from `groot99-droid/claude/r8-canon-r2`
- 2026-10-25 #264 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #267 from `groot99-droid/claude/r9-world-mode`
- 2026-10-25 #265 from `groot99-droid/claude/r9-living-world`
- 2026-10-25 #266 from `groot99-droid/claude/r9-logic-table`
- 2026-10-25 #268 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #269 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #270 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #271 from `groot99-droid/claude/r9-gdd-map`
- 2026-10-25 #263 from `groot99-droid/claude/lucid-dijkstra-8kvpkz-keepalive`
- 2026-10-25 #260 from `groot99-droid/claude/lucid-dijkstra-8kvpkz`
- 2026-10-25 #261 from `groot99-droid/claude/lucid-dijkstra-8kvpkz-mobs`
- 2026-10-25 #272 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #274 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #276 from `groot99-droid/claude/r9-studio-protocol`
- 2026-10-25 #275 from `groot99-droid/claude/r9-studio-server-s2`
- 2026-10-25 #273 from `groot99-droid/claude/r9-studio-server`
- 2026-10-25 #280 from `groot99-droid/claude/r9-studio-server-nav`
- 2026-10-25 #279 from `groot99-droid/claude/r9-studio-client`
- 2026-10-25 #277 from `groot99-droid/claude/r9-studio-server-s1b`
- 2026-10-25 #281 from `groot99-droid/claude/r9-studio-client-t1b`
- 2026-10-25 #278 from `groot99-droid/claude/r9-studio-server-s1c`
- 2026-10-25 #282 from `groot99-droid/claude/r9-studio-client-t2`
- 2026-10-25 #288 from `groot99-droid/claude/r9-studio-server-tilemap`
- 2026-10-25 #284 from `groot99-droid/claude/r9-studio-client-t3`
- 2026-10-25 #285 from `groot99-droid/claude/r9-studio-client-t4a`
- 2026-10-25 #283 from `groot99-droid/claude/r9-studio-server-s3`
- 2026-10-25 #287 from `groot99-droid/claude/r9-studio-server-s4`
- 2026-10-25 #286 from `groot99-droid/claude/r9-studio-client-t4b`
- 2026-10-25 #289 from `groot99-droid/claude/r9-studio-client-t5a`
- 2026-10-25 #294 from `groot99-droid/claude/r9-studio-server-s5`
- 2026-10-25 #290 from `groot99-droid/claude/r9-studio-client-t5b`
- 2026-10-25 #291 from `groot99-droid/claude/r9-studio-client-t5c`
- 2026-10-25 #295 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #292 from `groot99-droid/claude/r9-studio-client-t5d`
- 2026-10-25 #293 from `groot99-droid/claude/r9-studio-client-t5e`
- 2026-10-25 #296 from `groot99-droid/claude/r9-studio-editor-art`
- 2026-10-25 #297 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 #298 from `groot99-droid/claude/r9-studio-editor-materials`
- 2026-10-25 #301 from `groot99-droid/claude/r9-studio-overview-a`
- 2026-10-25 #303 from `groot99-droid/claude/r9-studio-npc-server`
- 2026-10-25 #299 from `groot99-droid/claude/r9-studio-editor-buildings`
- 2026-10-25 #305 from `groot99-droid/claude/r9-studio-npc-routes-a`
- 2026-10-25 #308 from `groot99-droid/claude/r9-studio-npc-people-pure`
- 2026-10-25 #300 from `groot99-droid/claude/r9-studio-overview`
- 2026-10-25 #302 from `groot99-droid/claude/r9-studio-editor-movables`
- 2026-10-25 #309 from `groot99-droid/claude/r9-studio-npc-server-n1`
- 2026-10-25 #306 from `groot99-droid/claude/r9-studio-editor-rotation`
- 2026-10-25 #304 from `groot99-droid/claude/r9-studio-npc-routes`
- 2026-10-25 #310 from `groot99-droid/claude/r9-studio-npc-people`
- 2026-10-25 #307 from `groot99-droid/claude/r9-studio-modes`
- 2026-10-26 #311 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-27 #312 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-27 #313 from `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-29 #314 from `groot99-droid/claude/laughing-planck-vt4dcs`
- 2026-10-29 #315 from `groot99-droid/claude/r10-a9-interactions`
- 2026-10-29 #326 from `groot99-droid/claude/laughing-planck-vt4dcs`
- 2026-10-29 #322 from `groot99-droid/claude/r10-a6-mobs`
- 2026-10-29 #325 from `groot99-droid/claude/r10-a3-sim`
- 2026-10-29 #323 from `groot99-droid/claude/r10-a12-inventory`
- 2026-10-29 #327 from `groot99-droid/claude/r10-a11-tools`
- 2026-10-29 #329 from `groot99-droid/claude/laughing-planck-vt4dcs`
- 2026-10-29 #331 from `groot99-droid/claude/r10-a7a-bed-frames`
- 2026-10-29 #324 from `groot99-droid/claude/r10-a12b-moves`
- 2026-10-29 #328 from `groot99-droid/claude/r10-a3-sim2`
- 2026-10-29 #333 from `groot99-droid/claude/r10-d1-npc-seats`
- 2026-10-30 #386 from `groot99-droid/claude/r10-y3-new-screens`
- 2026-10-30 #391 from `groot99-droid/claude/r10-c5a-painttown`
- 2026-10-30 #395 from `groot99-droid/claude/laughing-planck-vt4dcs`
- 2026-10-30 #389 from `groot99-droid/claude/r10-y5-studio-npc-save`
- 2026-10-30 #393 from `groot99-droid/claude/r10-c5b-paintview`
- 2026-10-30 #396 from `groot99-droid/claude/laughing-planck-vt4dcs`
- 2026-10-30 #384 from `groot99-droid/claude/r10-x4-stuck-figures`
- 2026-10-30 #390 from `groot99-droid/claude/r10-y6-phone-discs`
- 2026-10-30 #394 from `groot99-droid/claude/r10-b3c-constable-petitions`
- 2026-10-30 #392 from `groot99-droid/claude/r10-y7-vendetta-goal`
- 2026-10-30 #403 from `groot99-droid/claude/r10-x5-figures-in-views`
- 2026-10-30 #399 from `groot99-droid/claude/r10-b5a-cell`
- 2026-10-30 #405 from `groot99-droid/claude/r10-b5b-jail`
- 2026-10-30 #404 from `groot99-droid/claude/r10-x7-patch-per-tick`
- 2026-10-30 #370 from `groot99-droid/claude/r10-x1-refusals`
- 2026-10-30 #380 from `groot99-droid/claude/r10-d9c-talk`
- 2026-10-30 #375 from `groot99-droid/claude/r10-x2-chop-smash-noise`
- 2026-10-30 #411 from `groot99-droid/claude/r10-b5c-cell-rumours`
- 2026-10-30 #413 from `groot99-droid/claude/r10-x10-bandage-knockback`
- 2026-10-30 #410 from `groot99-droid/claude/r10-d8-jail-games`
- 2026-10-30 #414 from `groot99-droid/claude/r10-x15-rent-flake`
- 2026-10-30 #398 from `groot99-droid/claude/r10-y8-hand-craft`
- 2026-10-30 #402 from `groot99-droid/claude/r10-y9-phone-band`
- 2026-10-30 #406 from `groot99-droid/claude/r10-y10-copy-drift`
- 2026-10-30 #407 from `groot99-droid/claude/r10-y11-toon-remap`
- 2026-10-30 #409 from `groot99-droid/claude/r10-y12-figure-names`
- 2026-10-30 #412 from `groot99-droid/claude/r10-y13-line-extras`
- 2026-10-30 #416 from `groot99-droid/claude/r10-r2-answers`
- 2026-10-30 #420 from `groot99-droid/claude/r10-s1-scope`
- 2026-10-30 #415 from `groot99-droid/claude/r10-x8-logs-tooltip`
- 2026-10-30 #417 from `groot99-droid/claude/r10-y14-stale-e2e`
- 2026-10-30 #418 from `groot99-droid/claude/r10-x11-herb-bread-dawn`
- 2026-10-30 #424 from `groot99-droid/claude/r10-y15-e2e-ci`
- 2026-10-30 #400 from `groot99-droid/claude/laughing-planck-vt4dcs`
- 2026-10-30 #408 from `groot99-droid/claude/r10-c4b-dusktrain`
- 2026-10-30 #427 from `groot99-droid/claude/r10-b6a-tribunal`
- 2026-10-30 #419 from `groot99-droid/claude/r10-r1-actions`
- 2026-10-30 #423 from `groot99-droid/claude/r10-r2-paper`
- 2026-10-30 #439 from `groot99-droid/claude/r10-y17-ci-timeout`
- 2026-10-30 #446 from `groot99-droid/claude/r10-x18-herb-bread-timeout`
- 2026-10-30 #433 from `groot99-droid/claude/laughing-planck-vt4dcs`
- 2026-11-06 #449 from `groot99-droid/claude/story-s4-fixture`
- 2026-11-06 #451 from `groot99-droid/claude/story-s4-suites`
- 2026-11-06 #450 from `groot99-droid/claude/story-s1-schema`
- 2026-11-06 #452 from `groot99-droid/claude/story-s2-enable-story`
- 2026-11-06 #454 from `groot99-droid/claude/story-s1-status`
- 2026-11-06 #453 from `groot99-droid/claude/story-s3-protocol-cards`
- 2026-11-06 #455 from `groot99-droid/claude/story-s4-streams`
- 2026-11-06 #456 from `groot99-droid/claude/story-s2-seat-handover`
- 2026-11-06 #457 from `groot99-droid/claude/story-s3-catalog`
- 2026-11-06 #460 from `groot99-droid/claude/story-s2-seat-handover`
- 2026-11-06 #458 from `groot99-droid/claude/story-s4-e2e`
- 2026-11-06 #461 from `groot99-droid/claude/story-s4-bot-run`
- 2026-11-06 #462 from `groot99-droid/claude/story-s4-handoff`
- 2026-11-06 #465 from `groot99-droid/claude/story-p0-arc`
- 2026-11-07 #468 from `groot99-droid/claude/story-p1-schema`
- 2026-11-07 #470 from `groot99-droid/claude/story-answers`
- 2026-11-07 #476 from `groot99-droid/claude/story-p3-cards`
- 2026-11-07 #477 from `groot99-droid/claude/story-p3-save`
- 2026-11-08 #479 from `groot99-droid/claude/story-p2-sections`
- 2026-11-08 #478 from `groot99-droid/claude/story-p3-endscreen`
- 2026-11-08 #482 from `groot99-droid/claude/story-p3-arc-catalog`
- 2026-11-08 #481 from `groot99-droid/claude/story-p2-replay`
- 2026-11-08 #485 from `groot99-droid/claude/story-p2-save`
- 2026-11-08 #487 from `groot99-droid/claude/story-p2-nowin`
- 2026-11-08 #488 from `groot99-droid/claude/story-p2-npcvendetta`
- 2026-11-08 #489 from `groot99-droid/claude/story-p2-hitman`
- 2026-11-08 #490 from `groot99-droid/claude/story-p2-heir`
- 2026-11-08 #491 from `groot99-droid/claude/story-p2-nightpower`
- 2026-11-08 #492 from `groot99-droid/claude/story-p2-readpick`
- 2026-11-08 #494 from `groot99-droid/claude/story-p2-basemerge`
- 2026-11-10 #459 from `groot99-droid/claude/story-s3-live`
- 2026-11-10 #504 from `groot99-droid/claude/story-s3-status`
- 2026-11-10 #506 from `groot99-droid/claude/story-s3-handoff`
- 2026-11-11 #512 from `groot99-droid/claude/story-s3-fixnote`
- 2026-11-11 #514 from `groot99-droid/claude/story-s3-replay`
- 2026-11-12 #517 from `groot99-droid/claude/story-s3-tidy`
- 2026-11-12 #520 from `groot99-droid/claude/story-s3-acctnote`
- 2026-11-12 #522 from `groot99-droid/claude/story-s3-tidy2`
- 2026-11-12 #472 from `groot99-droid/claude/accounts-plan`
- 2026-11-12 #444 from `groot99-droid/claude/r10-s3-forge`
- 2026-11-12 #428 from `groot99-droid/claude/r10-s5-artstyle`
- 2026-11-12 #422 from `groot99-droid/claude/r10-s4-mugging`
- 2026-11-12 #533 from `groot99-droid/claude/story-s3-status-e2e`
- 2026-11-12 #437 from `groot99-droid/claude/r10-x12-flaky-tests`
- 2026-11-12 #443 from `groot99-droid/claude/r10-c4d-ledger`
- 2026-11-12 #471 from `groot99-droid/claude/ui-renumber`
- 2026-11-12 #445 from `groot99-droid/claude/r10-t6b-moods`
- 2026-11-12 #397 from `groot99-droid/claude/r10-x14-decoded-views`
- 2026-11-12 #430 from `groot99-droid/claude/r10-s2-berries`
- 2026-11-12 #425 from `groot99-droid/claude/r10-x9-grindstone`
- 2026-11-12 #429 from `groot99-droid/claude/r10-s1-containers`
- 2026-11-12 #531 from `groot99-droid/claude/interiors-plan`
- 2026-11-12 #535 from `groot99-droid/claude/story-handoff-docs`
- 2026-11-12 #442 from `groot99-droid/claude/r10-x17-constable-file-npc`
- 2026-11-12 #426 from `groot99-droid/claude/r10-c5c-knifeguards`
- 2026-11-12 #534 from `groot99-droid/claude/r10-y1-refusal-lines`
- 2026-11-12 #536 from `groot99-droid/claude/r10-d4b-dishes`
- 2026-11-12 #431 from `groot99-droid/claude/r10-x13-npc-night-bake`
- 2026-11-12 #441 from `groot99-droid/claude/r10-k6-snares`
- 2026-11-12 #537 from `groot99-droid/claude/story-r8-log`
- 2026-11-12 #440 from `groot99-droid/claude/r10-k3-candles`
- 2026-11-13 #435 from `groot99-droid/claude/r10-m1-barks`
- 2026-11-13 #447 from `groot99-droid/claude/r10-w1a1-seat-ids`
- 2026-11-13 #538 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-13 #539 from `groot99-droid/claude/blender-hollowmere-3d`
- 2026-11-13 #540 from `groot99-droid/claude/v2-walk`
- 2026-11-14 #542 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-14 #541 from `groot99-droid/claude/v2-walk`
- 2026-11-15 #544 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-16 #543 from `groot99-droid/claude/v2-walk`
- 2026-11-16 #545 from `groot99-droid/claude/nice-davinci-b9wlz6`
- 2026-11-16 #546 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-16 #548 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #550 from `groot99-droid/claude/inspiring-cori-juqfrm`
- 2026-11-19 #549 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #551 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #552 from `groot99-droid/claude/inspiring-cori-juqfrm`
- 2026-11-19 #553 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #557 from `groot99-droid/claude/r11-d-h1-models`
- 2026-11-19 #558 from `groot99-droid/claude/r11-t-art-drop-warning`
- 2026-11-19 #554 from `groot99-droid/claude/r11-d-s0-three`
- 2026-11-19 #555 from `groot99-droid/claude/r11-t-bpy-job`
- 2026-11-19 #561 from `groot99-droid/claude/r11-d-h1-meshy-licence`
- 2026-11-19 #556 from `groot99-droid/claude/r11-p-prop-list`
- 2026-11-19 #563 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #562 from `groot99-droid/claude/focused-cori-c2owsz`
- 2026-11-19 #564 from `groot99-droid/claude/inspiring-cori-juqfrm`
- 2026-11-19 #568 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #565 from `groot99-droid/claude/r11-r-r1-scene`
- 2026-11-19 #566 from `groot99-droid/claude/r11-r-r1-render`
- 2026-11-19 #559 from `groot99-droid/claude/r11-t-render-lock-writer`
- 2026-11-19 #567 from `groot99-droid/claude/r11-r-r1-budget`
- 2026-11-19 #569 from `groot99-droid/claude/r11-p-p2-brief`
- 2026-11-19 #560 from `groot99-droid/claude/r11-t-render-lock-check`
- 2026-11-19 #570 from `groot99-droid/claude/r11-r-m5b-list-nudge`
- 2026-11-19 #574 from `groot99-droid/claude/r11-r-hitman-flake`
- 2026-11-19 #573 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #571 from `groot99-droid/claude/r11-f-figure-rig`
- 2026-11-19 #581 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #576 from `groot99-droid/claude/r11-p-p2b-walls`
- 2026-11-19 #584 from `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 #575 from `groot99-droid/claude/r11-p-p2a-ground`
- 2026-11-19 #572 from `groot99-droid/claude/gallant-goodall-k95p1k`
- 2026-11-20 #577 from `groot99-droid/claude/r11-t-blender-figures-step`
- 2026-11-20 #579 from `groot99-droid/claude/inspiring-cori-juqfrm`

## 11. Source documents (verbatim)

Each file below is quoted from the repository at HEAD. Lines start with ">" so its headings do not mix with this document's.

### Source file: README.md

> # Who Did It
>
> A browser multiplayer hidden-role game for 4 to 10 players, played from a link.
> Open the page, **Create Party** or **Join Party** with a 5-character code, press Start, and
> each player receives a secret role card. Then the village of HollowMere opens up: enter houses,
> climb to lofts, slip into the forest and the cave, find bodies, collect clues, and vote on who
> did it before the Cabal reaches parity.
>
> It crosses Among Us (tasks, bodies, emergency meetings), Mafia / Werewolf (hidden factions and
> a vote as the climax), a whodunit (physical clues with hidden traits and a Detective who verifies
> them) and Hello Neighbor (enterable houses, locked doors, hiding spots, wolves in the woods).
>
> ## Status
>
> **Playable now:** [https://groot99-droid.github.io/Who-Did-It/](https://groot99-droid.github.io/Who-Did-It/),
> served from GitHub Pages against the Railway server. The player manuals are in
> [`docs/guides/`](docs/guides/README.md) and beside the game at
> [`/Who-Did-It/help/`](https://groot99-droid.github.io/Who-Did-It/help/). Rounds 1 to 9 of the roadmap are merged;
> round 10 (world mode) and story mode's part 2 are merged in part, with what is left in
> [`docs/round10/part2.md`](docs/round10/part2.md). The first step of V2, a first-person walk through the 3D
> HollowMere, is served at [`/Who-Did-It/walk/`](https://groot99-droid.github.io/Who-Did-It/walk/).
> `docs/ROADMAP.md` 7.0 carries each milestone's status. Everything about the design lives in [`docs/`](docs/README.md).
>
> | Version | Rendering | Networking | Players | Art |
> |---|---|---|---|---|
> | **V1** (this repo first) | Isometric 2.5D in Phaser 4 with pre-rendered 3D sprites from Blender | Static client on GitHub Pages, authoritative Colyseus server (Render Free, then Railway) | 4-10 | Stylized toon-noir |
> | **V2** (started: `apps/walk`, single-player, A610) | First-person 3D in the browser, same server, rules and world data | same | 4-10 | 3D HD (A611) |
>
> ## Layout
>
> ```
> apps/client/      Phaser + Vite client, deployed to GitHub Pages
> apps/server/      Colyseus authoritative game server
> apps/walk/        V2 first step: Three.js first-person walk-through, deployed beside the client at /walk/
> packages/shared/  schema, protocol, pure rules engine, constants
> packages/content/ roles, traits, items, clues, tasks, balance, maps, scenes and story data (JSON)
> tools/            Blender render rig and 3D village build, sprite packer, grid exporter, bot swarm, auto runner
> assets/source/    the masters' manifest, concepts, prompts and review sheets
> docs/             game design, world bible, architecture, asset pipeline, roadmap, decisions, round contracts
> ```
>
> ## Related repo
>
> Art masters, studio notes and the Higgsfield generations library live in the owner's ROSW repo,
> [Pipelines-Plugin](https://github.com/groot99-droid/Pipelines-Plugin); see `docs/ASSETS.md` 6.10.
> This repo's `.claude/settings.json` registers that marketplace and enables its `ui-design` and `udgt` plugins;
> the game's teardown lives in ROSW `teardowns/who-did-it/`.
>
> ## Owner-only admin page (Railway variables)
>
> The server can serve an admin room, where the owner watches an all-NPC match at up to 10x, signed in with GitHub. It is
> off unless every variable below is set on the server host (Railway: the service's Variables tab); the values are never
> written into this repo. There is no password: GitHub identifies the owner and the login allowlist decides.
>
> | Variable | Value |
> |---|---|
> | `WDI_ADMIN` | `1` |
> | `WDI_ADMIN_GITHUB_CLIENT_ID`, `WDI_ADMIN_GITHUB_CLIENT_SECRET` | from a GitHub OAuth app whose callback URL is `https://<railway host>/auth/github/callback` |
> | `WDI_ADMIN_GITHUB_LOGINS` | the allowed GitHub login, `groot99-droid` (comma-separated for more) |
> | `WDI_ADMIN_SECRET` | `openssl rand -base64 32`, run on your own machine |
> | `WDI_ADMIN_CLIENT_URL` | `https://groot99-droid.github.io/Who-Did-It/` |
>
> Unset any one of them and the room and both routes disappear. Details: [Architecture 5.11](docs/ARCHITECTURE.md).
>
> ## Documents
>
> - [Game design](docs/GDD.md), the only source of rules and numbers together with `balance.json`
> - [World bible](docs/WORLD.md), HollowMere, BlackPine and their scenes
> - [Architecture](docs/ARCHITECTURE.md), lobby codes, role secrecy, netcode, deployment
> - [Asset pipeline](docs/ASSETS.md), Blender rig, Higgsfield, Adobe, licensing
> - [Roadmap](docs/ROADMAP.md), the milestones, their status and the first 14 days
> - [Decisions and open questions](docs/DECISIONS.md)
> - [Research log](docs/RESEARCH.md)
>

### Source file: CLAUDE.md

> # CLAUDE.md — Who Did It
>
> ## What this repo is
>
> A browser multiplayer hidden-role game for 4 to 10 players: a static Phaser client on
> GitHub Pages and an authoritative Colyseus server. V1 is isometric 2.5D (since round 5,
> DECISIONS A49) with pre-rendered and generated sprites; V2 is first-person 3D on the same
> server, rules and world data; its first step is `apps/walk`, a single-player first-person walk through
> the 3D HollowMere (DECISIONS A610), and the game now has two modes, 2.5D and 3D (A613). The quick mode
> it once had was removed in round 7 (DECISIONS A115, `GDD.md` 3.11).
>
> Implementation started 2026-10-10 in four parallel sessions and has run in rounds since; `docs/SESSIONS.md`
> says which paths each session owns, round by round. Everything in the layout below is built and merged;
> `docs/ROADMAP.md` 7.0 gives each milestone's status.
>
> ## Read first
>
> - `docs/README.md` is the index. `docs/MASTER_PLAN.md` is the frozen v0.1 plan.
> - `docs/GDD.md` and `packages/content/data/balance.json` are the only sources of rules
>   and numbers. A behaviour change is not done until `GDD.md` changes in the same pull
>   request. No other document restates a number; it references `GDD.md`.
> - `docs/DECISIONS.md` logs every decision with the owner, the changes made during review,
>   and the open questions. Resolve an open question there before building on it.
> - `docs/SESSIONS.md` is the coordination contract between parallel sessions: read it before
>   writing any file and stay inside your session's paths.
> - `docs/ROADMAP.md` carries the milestones and the definition of done for each one. One
>   branch and one session per milestone task, pull requests under 400 lines, tests for
>   every rules change.
>
> ## Layout
>
> ```
> apps/client/      Phaser + Vite client (base '/Who-Did-It/', hash routing), DOM overlay HUD, admin page, Studio
> apps/server/      Colyseus server: PartyRoom, AdminRoom, StudioRoom, sim/ (Step, Commands, Visibility, Portals, ...)
> apps/walk/        V2 first step (A610): Vite + Three.js first-person walk-through, base '/Who-Did-It/walk/'
> packages/shared/  @wdi/shared: schema (builder style, no decorators), protocol, pure rules, constants
> packages/content/ @wdi/content: every rules record, balance, looks, maps, scenes, story (JSON + zod)
> tools/            grid exporter, sprite packer, Blender rig and 3D village build, bot swarm, auto runner
> assets/source/    MANIFEST.md (masters' paths and hashes), concepts, prompts, review sheets
> docs/             design, world, architecture, assets, roadmap, decisions, research, one folder per round
> ```
>
> Versions are pinned in `docs/ARCHITECTURE.md` 5.1. Sessions never upgrade dependencies.
>
> ## Conventions that must not drift
>
> - Role secrecy: a player's role card, inventory, notebook and cooldowns live only in that
>   player's private view. In the main mode a seat's public look is its card's character
>   (owner decision, 2026-10-17, DECISIONS A49), except for the cover roles, which wear another
>   card's look: nothing a client receives may reveal that a seat wears a cover, a
>   cover-wearer's true role, or who walks under an impersonation beyond what the drawn figure
>   shows. Nothing secret shares a random stream with anything public (`sim/seeds.ts`).
>   Debug handlers register only with `WDI_DEBUG=1`.
> - Every client action is queued and consumed inside the server `step()`; nothing mutates
>   state in a message callback.
> - Scene, portal, spawn and clue ids in `packages/content/data/scenes/*.json` are frozen;
>   V2 reads the same graph. `SCENE_IDS` is append-only; a new map adds new ids with new
>   prefixes and never renames or reuses one (GDD 3.13, WORLD 4.3).
> - Atlas keys are `char/<lookId>/<anim>/<dir>` with the look ids of `looks.json` (plus
>   `villager` for figures that are not seats); cover cards have no world character. The 2.5D
>   mode presents isometrically on the client only: data, wire and facing are world frame, an atlas
>   `<dir>` is screen frame, and the direction table lives once in `@wdi/shared` (`dirFromVector`).
> - Assets: CC0 by default, CC-BY only with a `CREDITS.md` row, never Synty, never raw
>   Mixamo or Quaternius sources in the repo. See `docs/ASSETS.md` 6.5.
>
> ## Connection to the owner's ROSW repo (groot99-droid/Pipelines-Plugin)
>
> - Art masters (`.ai`, `.aep`, `.psd`, character `.blend`, source `.glb`) live on the
>   owner's laptop in the ROSW checkout under `studio/assets/who-did-it/<kind>/<slug>/`,
>   which that repo git-ignores. Each made thing has a studio note in
>   `studio/vault/who-did-it/<kind>/<slug>.md` written by the studio pipeline, never by hand.
>   `assets/source/MANIFEST.md` in this repo mirrors every master's path, hash and date.
> - Higgsfield generations are catalogued in ROSW `studio/library/catalog.json`; a
>   `CREDITS.md` row for a generated asset cites that catalog id.
> - Sounds come from ROSW `sound-library/` (the owner's own recordings and tracks: `catalog.json`
>   versioned, the originals on that repo's GitHub Releases, fetched by id with the `sound-library`
>   skill, never committed anywhere). A shipped sound's `CREDITS.md` and `MANIFEST.md` rows cite its
>   catalog id; a library sound has no studio note (`docs/round6/media.md` 7).
> - `.claude/settings.json` registers the ROSW marketplace and enables its `ui-design`
>   plugin (style catalog, contrast-checked design-system generator); see `docs/ASSETS.md`
>   6.10. The `rosw` plugin itself (creative-writing and studio pipelines) only works from
>   the ROSW checkout, so it is not enabled here.
> - The game's teardown lives in ROSW `teardowns/who-did-it/` (the `udgt` plugin, enabled in
>   `.claude/settings.json`). It maps every design choice to its decision, its section, its data, its
>   code and its history, and it holds the owner's answers to the teardown briefs, verbatim. Before
>   changing a mechanic, a screen or a dataset, the `udgt-consult` skill answers "why is it like this"
>   from it (ROSW checked out beside this repo). It reads this repo and never writes it.
> - ROSW `writing-museum/` is a Three.js first-person viewer with doors, rooms, lights,
>   touch and gamepad input. It was the candidate seed for the V2 renderer; V2's first step,
>   `apps/walk` (A610), is its own Three.js viewer and copies nothing from it.
>
> ## Compact instructions
>
> Every session compacts its context at the size of its kind of work (DECISIONS A223): 500k for precise work, 800k
> for work that needs more context, 300k for testing, fixing and organizing. `.claude/settings.json` (`autoCompactWindow`)
> holds the 500k default; the window is read when a session starts, so a 300k or 800k session is spawned from its tier
> branch (`docs/round10/README.md`, "Compaction"). When a
> compaction summary is written for a session of `docs/SESSIONS.md`, it keeps, in this order: the session id
> (for example 6F) and its branch; the PR split step it is on and which PRs are open, merged or unpushed; the
> files it has edited since its last push; every contract request it has made in a PR description and whether
> the orchestrator answered; the test command and its last result; and the sections of the contract documents
> it still has to read. It drops tool output, file contents it can re-read, and anything a document already
> says. A session that resumes after a compaction re-reads its brief and `docs/round<N>/seams.md` before the
> next edit.
>

### Source file: docs/README.md

> # Who Did It — documentation
>
> | File | What it owns |
> |---|---|
> | [MASTER_PLAN.md](MASTER_PLAN.md) | The full v0.1 master plan (frozen snapshot). Start here. |
> | [GDD.md](GDD.md) | Game design: pillars, first ten minutes, roles, match loop, clues, items, PvE, stealth, meetings, balance, cut list, and the record of the removed quick mode (3.11). The only source of numbers together with `balance.json`. |
> | [WORLD.md](WORLD.md) | World bible: Hollowmere, scene graph with ids and exits, overworld sketch, portal rules, bestiary, lighting. |
> | [ARCHITECTURE.md](ARCHITECTURE.md) | Stack, monorepo layout, lobby and join codes, state schema and role secrecy, protocol, netcode, deployment, security, testing, V2 path. |
> | [ASSETS.md](ASSETS.md) | Palette, Blender 8-direction rig, per-asset pipelines, Higgsfield tool map, Adobe usage, licensing policy, backlog, budgets. |
> | [ROADMAP.md](ROADMAP.md) | Milestones and their status, parallel tracks, placeholder strategy, risk register, playtest plan, day 1-14 schedule, V2 outline. |
> | [DECISIONS.md](DECISIONS.md) | Decisions locked with the owner, changes from review, open questions. |
> | [PROTOCOL.md](PROTOCOL.md) | Generated wire protocol: message tables, payload types, error codes (`pnpm docs:protocol`). |
> | [SPRITES.md](SPRITES.md) | Sprite conventions: atlas keys, frame names, cells, pivots, the manifest and the art styles; the contract between `tools/blender`, `tools/sprites` and the client. |
> | [UI.md](UI.md) | DOM design system: palette roles, type and spacing scale, components, card frames, measured contrast, screen mockups, the M3 copy deck. |
> | [guides/](guides/README.md) | Player manuals: how to play, the host guide and the admin guide. Served beside the game at `/help/`. |
> | [PLAYTESTS/](PLAYTESTS/README.md) | How a playtest session runs, the feedback form, the fun-or-stop scorecard, the notes template and one entry per session. |
> | [RESEARCH.md](RESEARCH.md) | Sourced facts behind the version pins, hosting choice and licensing rules. |
> | [round5/](round5/README.md) | The round-5 contract documents: the owner's brief, the ONUB v2 contract, the deck wire and data, the world and maps, the NPC routines, the art plan, and the seams of the pre-seed (every hook and its locked call site). |
> | [round6/](round6/README.md) | The round-6 contract documents: the owner's brief and the Bible, the admin auto-mode, cutscenes and music, M5b, the Bible's seams across rounds 7 to 9, the media brief, and the seams of the pre-seed. |
> | [round7/](round7/README.md) | The round-7 contract documents: the whole-game re-skin to the owner's two mockups, open and private parties with profiles and friends, the map intro tracks and cinematic openings, and the vendettas, the Daily Train and the Vicar's memorial. |
> | [round8/](round8/README.md) | The round-8 contract documents: bodies, coin, motion and art, the teardown answers, the living world, the canon, and the seams of the round. |
> | [round9/](round9/README.md) | The round-9 design of world mode: the core loop, the full-screen phases, the logic table, the refusal reasons, the living world, emergent play, the owner's answers and follow-ups, the GDD map, the round-10 build plan and the admin Studio. |
> | [round10/](round10/README.md) | The round-10 contract: the sessions that build world mode, their models and compaction sizes, and the seams they share. Paused on 2026-10-30. The pull requests open at the pause merged between 2026-11-07 and 2026-11-12; the steps still to build (B6b, B6c, B7, W1a2 to W8 and the rest) are in [`part2.md`](round10/part2.md). |
> | [round11/](round11/README.md) | The round-11 plan, the full Blender makeover: the render pipeline, materials and budgets, the owner's answers and the approved plan. Design only; not built yet. The revised plan for the sprite world of A615, [`round11-plan-v2.md`](round11/round11-plan-v2.md), replaced it on 2026-11-19 (A616). |
> | [round12/sprite-world.md](round12/sprite-world.md) | The merged 2.5D look (A615): a sprite world with depth, steps S0 to S6. |
> | [story/](story/README.md) | Story mode: the part-1 contract, the arc, the script, the rite, the test plan, the orchestrator's handoff and the status log. Part 2 merged into the base with #538. |
> | [accounts/](accounts/plan.md) | The player-accounts plan (a plan, not code). |
> | [map-revamp/](map-revamp/interiors-plan.md) | The map revamp's interiors plan for the 3D HollowMere (DECISIONS A611 to A614). |
> | [ui/](ui/) | Screenshots of the client's screens at 390 px and 1280x720, cited by `UI.md`. |
> | [SESSIONS.md](SESSIONS.md) | The parallel build sessions, round by round: path ownership, branches, PR base, seams, briefs and the integration logs. |
>
> Rule: a mechanic change updates `GDD.md` in the same pull request. Numbers never live in two documents.
>

### Source file: docs/SESSIONS.md

> # Parallel sessions (started 2026-10-10)
>
> Four Claude Code sessions build the first milestones in parallel, one track each. This file is
> the coordination contract: which paths each session owns, where PRs go, and the brief each
> session was started with. A session reads this file first and never writes outside its paths.
>
> ## Branches and pull requests
>
> | Session | Model | Track | Branch | Owns |
> |---|---|---|---|---|
> | **A. Server & shared** | Sonnet 5.5 | Code | `claude/m0-server` | root tooling (`eslint.config.js`, prettier, vitest config, root `package.json` scripts), `.github/workflows/ci.yml`, `packages/shared/**`, `apps/server/**`, `docs/DECISIONS.md` (spike results only), `docs/ARCHITECTURE.md` (only when code forces a correction) |
> | **B. Client & Pages** | Sonnet 5.5 | Code | `claude/m0-client` | `apps/client/**` except `apps/client/public/assets/**`, `.github/workflows/pages.yml`, `LICENSES/fonts/**` |
> | **C. Content data** | Opus 5.5 | Content | `claude/content-data` | `packages/content/**`, `docs/GDD.md`, `docs/WORLD.md` (id corrections only), the zod pin row in `docs/ARCHITECTURE.md` 5.1 |
> | **D. Art pipeline** | Opus 5.5 | Art | `claude/art-pipeline` | `tools/blender/**`, `tools/sprites/**`, `assets/**`, `apps/client/public/assets/**`, `CREDITS.md`, `LICENSES/vendors/**`, `docs/SPRITES.md`, `docs/ASSETS.md` |
> | **E. Decisions round (plan mode)** | Opus 5.5 | Design | `claude/decisions-round-3` | `docs/DECISIONS.md` and every document or data file a decision changes (`docs/GDD.md`, `WORLD.md`, `ARCHITECTURE.md`, `ASSETS.md`, `ROADMAP.md`, `packages/content/data/**`), `LICENSE-ASSETS`, `CREDITS.md`. Started 2026-10-10 after A to D closed; no other session runs beside it. |
>
> - Base branch and PR target: `claude/zen-turing-m1jnw0` (the repo's default branch; no `main`
>   exists yet). When the owner renames the default branch to `main`, open PRs follow automatically.
> - Draft PRs, under 400 lines where the work allows (split by step or by data file). Each PR runs
>   `pnpm lint && pnpm typecheck && pnpm test` clean before push.
> - The root scaffold (`package.json`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `.nvmrc`,
>   `.npmrc`, `.gitignore`, `.gitattributes`, `LICENSE`) is shared. Only Session A edits root
>   files; the others add their package under `apps/*`, `packages/*` or `tools/*`.
> - `pnpm-lock.yaml` will conflict between PRs. Resolution: merge the base branch, run
>   `pnpm install` (pnpm resolves lockfile conflict markers itself), commit.
> - Versions are pinned in `docs/ARCHITECTURE.md` 5.1. No session upgrades or substitutes a
>   dependency. New dependencies a session needs (zod, free-tex-packer-core, mitt, eslint tooling)
>   are added with a caret pin to the current npm release and recorded in 5.1 by that session.
> - Role secrecy and the server `step()` rules in `CLAUDE.md` apply to every PR.
>
> ## Interfaces between sessions
>
> | From | To | Contract |
> |---|---|---|
> | C content | A shared/server | `roles.json` is keyed so `assignRoles(ids, settings, rng)` reads a roster row by player count with no transformation; every record carries `gddRef`. Until C merges, A tests rules with inline fixtures that copy C's field names from this file's brief. |
> | A shared | B client | Message names, payloads and error codes in `docs/ARCHITECTURE.md` 5.5. B keeps a local copy in `src/net/protocol.ts` with a TODO to import `@wdi/shared/protocol` once A merges. |
> | D art | B client | Placeholder manifest keys in `docs/SPRITES.md`. Code imports keys, never paths. `?art=placeholder` keeps playtests running. |
> | C content | D art | Scene ids, sizes and the ASCII grid legend (`#` wall, `D` door, `S` spawn, `H` hiding spot, `B` body spot, `.` floor) are frozen by C; D's placeholder tiles and `bld_<id>_ext` keys use those ids. |
>
> Suggested merge order when several PRs are ready: A (tooling) -> C (content) -> B (client) -> D (art).
>
> ## Briefs
>
> ### A. Server & shared (Sonnet 5.5)
>
> Read `CLAUDE.md`, this file, `docs/ARCHITECTURE.md` 5.1-5.8 and 5.10-5.12, `docs/ROADMAP.md` 7.1
> (M0, M1) and 7.7 days 1, 2 and 4. Deliver in order:
>
> 1. Root tooling: `eslint.config.js` (typescript-eslint flat config), prettier, vitest config, root
>    scripts wired with `pnpm -r`; `.github/workflows/ci.yml` per 5.10 (checkout@v7, setup-node@v7
>    on 22, pnpm via corepack, lint + typecheck + test, dist size report, `lfs: false`).
> 2. `packages/shared` (`@wdi/shared`): `version.ts` (`BUILD_VERSION` from env with a dev
>    fallback), `constants.ts` (`TILE_PX = 64` and only the radii ARCHITECTURE or GDD name; never
>    invent numbers), `metrics.ts`, `dirFromVector` with a unit test, `schema/` in
>    `@colyseus/schema` 5 builder style exactly as 5.4 (`Presence`, `Private`, `Player`, `Door`,
>    `SceneState`, `Settings` with `mode` uint8, `MeetingState`, `GameState`), `protocol/` with the
>    typed message names, payload types and error codes of 5.5, `rules/` with `mulberry32` and only
>    what M1 needs (`assignRoles`, `dealTraits`) tested with inline fixtures.
> 3. `apps/server`: Colyseus 0.18, `GET /health` -> `{ok, build, rooms, tickP95, patchBytes}`, CORS
>    per 5.10, `trust proxy` plus the token bucket on matchmake, `PartyRoom` with a custom 5-char
>    `roomId` from an unambiguous alphabet, `presence.sadd` uniqueness, private matchmaking,
>    `maxClients = 10`, `joinById`, one generic join error, the version handshake,
>    `setFixedTimestep` 20 Hz with `sim/Step.ts` in the 5.6 order (empty stages are fine), a command
>    queue (nothing mutates state in a message callback), `onJoin` with a `StateView` holding the
>    player's own `Player` and its `SceneState`. Debug handlers only under `WDI_DEBUG=1`.
> 4. Day-2 spike results in `docs/DECISIONS.md` under "Spike results (M0)": custom `roomId` +
>    `joinById`, one `.view()` field hidden from other clients, `setFixedTimestep` behaviour.
> 5. `@colyseus/testing` tests: 10 bots join and each sees only its own `priv`; the 11th join and a
>    version mismatch are refused with the same generic error.
>
> Check Colyseus 0.18 and `@colyseus/schema` 5 APIs with Context7 before writing them. Never add
> `colyseus.js`; `@colyseus/sdk` is client-only and does not belong here.
>
> ### B. Client & Pages (Sonnet 5.5)
>
> Read `CLAUDE.md`, this file, `docs/ARCHITECTURE.md` 5.1, 5.3, 5.5, 5.9, 5.10, `docs/ROADMAP.md`
> 7.1 (M0, M1) and 7.7 days 2, 3, 5 and 7. Deliver in order:
>
> 1. `apps/client` from the official Phaser 4 Vite + TypeScript template (phaser 4.2.1, vite ^8.3,
>    typescript ~5.9; drop the template's log-ping script), `base: '/Who-Did-It/'`, hash routing,
>    `pixelArt: false`, `src/{main,net,scenes,view,ui,flags}`; a Boot scene that reads flags
>    (`?art=placeholder`, `?mock=1`, `#/join/CODE`) and polls `${VITE_SERVER_URL}/health`; a
>    "Waking the village..." state while the Render Free server wakes; the canvas prints
>    `{ok, build}` once `/health` answers.
> 2. `NetworkService` over `@colyseus/sdk` ^0.18.5 (never `colyseus.js`): `create("party", {name,
>    build, deviceId})`, `joinById(code.toUpperCase())`, typed `send` / `request` from a local
>    `src/net/protocol.ts` copied from 5.5 (TODO: import `@wdi/shared` when it merges), a `mitt`
>    bus, the reconnection token in `localStorage` keyed by room code, every join failure shown as
>    "party not found or unavailable".
> 3. DOM overlay (`pointer-events: none` except controls): Landing (Create Party, Join Party, name
>    2-16 chars), Lobby (code, copy-link, player list, leader Start gated at 4 with a confirm
>    dialog), RoleCard (CSS flip, 12 s, Ready, Tab to reopen) driven by the `roleReveal` payload of
>    5.5 with a fixture behind `?mock=1`. Fonts Oswald + Inter self-hosted, licence texts in
>    `LICENSES/fonts/`.
> 4. `.github/workflows/pages.yml` per 5.10 (`VITE_SERVER_URL`, `VITE_BUILD_VERSION=${GITHUB_SHA::8}`
>    from Actions variables, configure-pages@v6, upload-pages-artifact@v5 of `apps/client/dist`,
>    deploy-pages@v5) on push to the default branch; the PR lists what the owner must set.
> 5. Playwright ^1.64 smoke: two contexts create then join and both reach the lobby, against the
>    `?mock=1` fixture while the server is absent; use the pre-installed Chromium, never
>    `playwright install`.
>
> Nothing in the client stores or shows another player's role. Check Phaser 4.2 and
> `@colyseus/sdk` APIs with Context7 first.
>
> ### C. Content data (Opus 5.5)
>
> Read `CLAUDE.md`, this file, `docs/GDD.md` in full, `docs/WORLD.md` 4.2-4.8,
> `docs/ARCHITECTURE.md` 5.2, 5.4, 5.8, 5.14, `docs/ASSETS.md` 6.1, `docs/DECISIONS.md`.
> Goal: `packages/content` (`@wdi/content`) is the single machine-readable source of every
> roster, number and scene id that `GDD.md` and `WORLD.md` describe, validated by zod and tests.
> Deliver:
>
> 1. Package skeleton: `package.json` (`@wdi/content`, ESM, exports data and validators), zod,
>    vitest; one zod schema per file in `src/schemas/`; `src/index.ts` validates every JSON at
>    import and exports typed data.
> 2. `data/palette.json`, `data/metrics.json` (ASSETS 6.1, WORLD 4.2), `data/roles.json`,
>    `traits.json`, `items.json`, `abilities.json`, `clues.json`, `tasks.json`, `balance.json`:
>    every number copied from GDD 3.x, each record carrying `gddRef`. Where the GDD is silent or
>    ambiguous, choose and change `GDD.md` in the same PR.
> 3. `data/scenes/*.json` for all 15 scenes of WORLD 4.3: frozen ids, profile, size, portals with
>    target scene and spawn, spawn ids, hiding and body spots, an ASCII grid at the exact tile size
>    (`#` wall, `D` door, `S` spawn, `H` hiding spot, `B` body spot, `.` floor; overworld per 4.4);
>    tests that every portal resolves, every grid matches its size and profile gating is consistent.
> 4. Quick mode: `data/roles.onub.json`, `data/balance.onub.json` (decks 4-10, night windows,
>    timers, winner table) with tests for N+3 loaves per deck and a window for every role.
> 5. `pnpm --filter @wdi/content test` green and a short `packages/content/README.md`.
>
> Design field names so `assignRoles(ids, settings, rng)` reads `roles.json` by player count
> without transformation and so Tiled exports can replace the grids later with the same
> `.nav.json` contract (ASSETS 6.3). No server or client code.
>
> ### D. Art pipeline (Opus 5.5)
>
> Read `CLAUDE.md`, this file, `docs/ASSETS.md` in full, `docs/WORLD.md` 4.1, 4.2, 4.7,
> `docs/GDD.md` 3.1-3.2, `docs/DECISIONS.md` open questions 5 and 6. Deliver:
>
> 1. `docs/SPRITES.md`: atlas key grammar `char/<body>/<anim>/<dir>` with non-role body ids, the
>    8-direction order and frame regex of ASSETS 6.2, 128 px cells, the `Feet` pivot manifest,
>    overlay passes (body, scarf, hat_cap, hat_bowler, blood), palette tokens, and every placeholder
>    key M1-M3 needs (one villager body with idle / walk / swing / die x 8 directions, overlays, the
>    clue sprites of 6.3, `bld_<id>_ext` for the Small-profile buildings, the 6 ground tilesets).
> 2. `tools/blender/build_rig.py` builds `render_rig.blend` from nothing on Blender 5.2 LTS
>    (orthographic camera X = 40° Z = 0°, straight-down tile camera, turntable `TT`, camera-parented
>    lights, toon node group, outline preset, 1 m checker cube and grid plane, EEVEE settings of
>    6.2) so the rig is reproducible; `batch_render.py` (frame regex, 12 fps `frame_step`, 128 px
>    cells, material-override passes, `Feet` -> `manifest.json`); `palettize.py`. Run the `--smoke`
>    calibration render if Blender or the `bpy` wheel installs in the container and commit the sheet
>    under `apps/client/public/assets/calibration/`; otherwise document the exact command and mark
>    the PR unverified.
> 3. `tools/sprites/pack.ts` on free-tex-packer-core (exporter `Phaser3`, `allowRotation: false`,
>    `allowTrim: true`, `detectIdentical: true`, `pot: true`, padding 2, extrude 1, max 2048, sorted
>    inputs), `gen-anims.ts` writing per-frame origins from `manifest.json`, a unit test on a
>    synthetic frame set, and `placeholder.ts` generating the placeholder atlas for every key in
>    `SPRITES.md` (flat palette shapes, direction arrow, label).
> 4. `assets/source/prompts/<slug>.md` for prompts (1)-(10) of ASSETS 6.4 with the style suffix
>    verbatim and the `generate_3d` settings of 6.9; `assets/source/MANIFEST.md` template;
>    `CREDITS.md` header and policy (6.5); `LICENSES/vendors/README.md` listing the vendor terms
>    to save before the first asset. If Higgsfield tools are available in the session, generate the
>    hero villager concept (prompt 1) and one turnaround, save under `assets/source/concepts/` with
>    a `CREDITS.md` row citing the generation id, and stop there; if not, stop at the prompt sheets
>    and say so.
> 5. Faction and trait icons as SVG (Village, Cabal, Neutral; Height, Scarf, Hat variants) in
>    `apps/client/public/assets/ui/icons/` on the 48 px grid, 2 px ink stroke, palette only; listed
>    in `SPRITES.md`.
>
> CC0 by default, CC-BY only with a `CREDITS.md` row, never Synty, never raw Mixamo or Quaternius
> in the repo. Leave `LICENSE-ASSETS` absent until open question 6 is answered.
>
> ## Integration log (2026-10-10)
>
> All four sessions finished their briefs in one pass each and opened draft PRs #1 to #4. The
> orchestrator merged the four branches into `claude/zen-turing-m1jnw0` in the order A, C, B, D
> (the only conflicts were in `pnpm-lock.yaml`, regenerated with `pnpm install`), reviewed the
> integrated tree, and fixed the seams in one commit on top of the merges:
>
> - Session A's eslint and prettier now apply to every package: the client's untyped room, the
>   Playwright spec swept up by vitest, and the formatting of B, C and D files; `packages/content/data`,
>   `apps/client/public/assets` and `assets/source` are prettier-ignored because their generators own
>   their layout.
> - `assignRoles` reads `roster[String(n)].deal`, the row shape of `roles.json` (A12); rules numbers left
>   `@wdi/shared/constants.ts` for `balance.json`.
> - The matchmake throttle keys on the last `x-forwarded-for` hop and `maxMessagesPerSecond` is applied
>   (A13); the client treats `CloseCode.CONSENTED`, not 1000, as a consented leave.
> - Docs reconciled: well ladder (A10), interior minimum (A11), rig built from code (A9), the Hireling act
>   id, the M4 task count, the quick-mode chip, dependency rows in ARCHITECTURE 5.1, root `assets:render`.
> - Held back: the two Higgsfield concept images stay on `claude/art-pipeline` until open question 13.
>
> ### Follow-ups for the next sessions
>
> 1. **Client imports `@wdi/shared/protocol`** instead of its local copy: add the workspace dependency,
>    delete the duplicated types in `apps/client/src/net/protocol.ts`, and align the `roleReveal` payload
>    (trait value ids, `teammates[]` element shape, `uses: number | null`). M1 blocker before Start works.
> 2. **Server Start**: `lobby.start` handler calling `assignRoles(ids, settings, rng, roles.rosters)` with
>    `@wdi/content` as a server dependency, then `roleReveal` per client and the lobby -> roleReveal phase.
> 3. **Accomplice kit**: GDD 3.2 lists Forged Alibi (V1.5) in the kit while `roles.json` omits it; either
>    add it with a `ships` flag or move it to the V1.5 note and delete the dead test exception.
> 4. `tools/sprites` declares `engines.node >= 22.18` (type stripping) against the root `>= 22.12`;
>    `batch_render.py` writes `Feet` pivots only during the `body` pass; ARCHITECTURE 5.4's excerpt still
>    shows `t.array(t.string())`; `/health.patchBytes` is not fed yet.
> 5. **Owner**: open questions 12 to 14 in `docs/DECISIONS.md`; GitHub Pages source = GitHub Actions and the
>    `VITE_SERVER_URL` Actions variable; the Render Free service for `apps/server`.
>
> ## Round 2 (started 2026-10-10, after PRs #1 to #6 merged)
>
> Five sessions, one track each, same rules as round 1 (draft PRs against `claude/zen-turing-m1jnw0`,
> under 400 lines where the work allows, lint + typecheck + test clean before every push, pinned
> versions only, no model identifiers in committed files). Code and tooling run on Sonnet 5.5; design
> and art run on Opus 5.5 or Fable 5.1.
>
> | Session | Model | Track | Branch | Owns |
> |---|---|---|---|---|
> | **F. M1 finish** | Sonnet 5.5 | Code | `claude/m1-finish` | `packages/shared/src/protocol/**`, `packages/shared/src/rules/roles.ts`, `apps/server/src/rooms/PartyRoom.ts` (lobby, Start, roleReveal, phase machine), `apps/server/src/rooms/handlers/lobby.ts` (new), `apps/server/test/lobby*.test.ts`, `apps/client/src/net/**`, `apps/client/src/ui/**` (except `theme/`), `apps/client/src/scenes/{Boot,Landing,Lobby,RoleReveal}.ts`, `apps/client/e2e/**`, `tools/bots/**`, `docs/PROTOCOL.md` (generated), `docs/ARCHITECTURE.md` 5.3 to 5.5 and 5.8, the Accomplice kit in `packages/content/data/roles.json` with `docs/GDD.md` 3.2 |
> | **G. M2 movement + one house** | Sonnet 5.5 | Code | `claude/m2-movement` | `apps/server/src/sim/**`, `apps/server/src/rooms/handlers/movement.ts` (new), `apps/server/test/sim*.test.ts`, `packages/shared/src/{collision,nav}/**` (new), `apps/client/src/scenes/{Preload,World}.ts` (new), `apps/client/src/view/**`, `apps/client/src/input/**` (new), `apps/client/src/net/mock/**` (extend the `?mock=1` fixture only), `tools/grid/**`, `packages/content/src/nav*` (new), `docs/ARCHITECTURE.md` 5.6 to 5.7. Scene, portal and spawn ids in `packages/content/data/scenes/*.json` stay frozen; G may add a `nav` export contract beside them. |
> | **H. Character art** | Opus 5.5 | Art | `claude/art-villager` | `assets/source/**`, `apps/client/public/assets/**` except `ui/` and `calibration/`, `tools/blender/**` (render and pipeline scripts; rig constants only with a `docs/DECISIONS.md` row), `tools/sprites/**`, `CREDITS.md`, `assets/source/MANIFEST.md`, `docs/ASSETS.md` 6.3, 6.4, 6.7 |
> | **I. UI design system** | Fable 5.1 | Design | `claude/ui-design-system` | `docs/UI.md` (new), `apps/client/public/assets/ui/**`, `apps/client/src/ui/theme/**` (new: tokens and component CSS, a README), `packages/content/data/style.json` and its schema, the UI paragraph of `docs/ASSETS.md` 6.1 |
> | **J. ROSW studio project** | Sonnet 5.5 | Process | `claude/rosw-studio` here; a branch in `groot99-droid/Pipelines-Plugin` | In this repo only `docs/ASSETS.md` 6.10 (status) and `assets/source/MANIFEST.md`; everything else lives in the ROSW repo and needs push access there (`add_repo` with push; stop and report if refused) |
>
> ### Seams in round 2
>
> | From | To | Contract |
> |---|---|---|
> | F | G | When every player is Ready on the role card (or its 12 s elapse), F sets `phase = PLAY` and sends each client `sceneEnter {sceneId: "overworld", spawn, facing}` (ARCHITECTURE 5.5). G's `World` scene starts on `sceneEnter`; until F merges, G drives `World` from the `?mock=1` fixture, which G extends with `sceneEnter` and presence updates. |
> | G | F | `PartyRoom` already queues every C->S message into `CommandQueue`; G consumes `input.move` and `act.enterPortal` inside `sim/Step.ts` and never adds message handlers to `PartyRoom`. If G needs one line in `PartyRoom` (an import and a `registerMovement(this)` call), it is the only line G touches there. |
> | I | F | `apps/client/src/ui/theme/tokens.css` (palette, type scale, spacing, the Art-Deco card frame classes) is importable by F's DOM screens. F does not wait for it; I's README says how to swap it in. |
> | H | G | `docs/SPRITES.md` keys stay. H replaces the content behind `char_villager` (and overlays) with real renders under the same keys and `manifest.json` layout; G loads by key and never by path. |
> | H | tools | H fixes the `tools/sprites` engines field (`>= 22.12`, no unflagged type stripping at runtime) and makes `batch_render.py` write `Feet` pivots on every pass, not only `body`. |
> | J | H | J's studio notes and `higgsfield-library-sync` catalog ids are what H cites in `CREDITS.md` rows once J exists; until then H cites generation ids as D did. |
>
> Suggested merge order: F, G, I, H, J.
>
> ### Round 2 log: F (M1 finish)
>
> Done on `claude/m1-finish`: follow-ups 1 to 3 and the 5.4 excerpt of item 4 above. For G: lobby and role-card messages (`lobby.start`, `lobby.ready`, `role.ready`) go to `PartyRoom.lobbyCommands`, not `commands`, so `sim/Commands.ts` never sees them and its `lobby.ready` case is dead code you can delete. `PartyRoom` calls `runLobbyCommands` and `runLobbyPhase` after `step()`. `net.roleCard` keeps the player's own card for Tab in any scene; `RoleReveal` starts a `World` scene (if registered) on `sceneEnter`. The server runs from source with `pnpm --filter @wdi/server serve` (tsx needs `--conditions=development` to read `@wdi/content` source).
>
> ## Integration log, round 2 (2026-10-15)
>
> All five sessions finished their briefs; H and I were cut off by the org usage limit after their PRs
> were up and resumed on 2026-10-15. The orchestrator merged F, G, I, H, J in that order (conflicts: the
> F/G union in `apps/client/package.json`, `PartyRoom.ts` imports, `tsup.config.ts`, root scripts and
> `tools/bots/package.json`; the H/J union in `CREDITS.md` and `MANIFEST.md`; the lockfile), ran the
> unit suites, the Playwright suites against the real server, and a review pass, then fixed the seams in
> one commit (DECISIONS A29):
>
> - One first `sceneEnter` per player (the sim places; the lobby handler only switches the phase).
> - One starter of the World scene (the router); the role card sleeps so Tab still reopens it in play;
>   the mock world triggers on the card's `lobby.ready`; its loop keeps wall-clock time under load.
> - A seat that completes its join after Start is refused (test added).
> - Door reach and the collision box moved from code into `balance.json` and `metrics.json` (GDD 3.7,
>   WORLD 4.2); the dead `lobby.ready` branch left `sim/Commands.ts`; placement marks views dirty.
> - The default asset manifest's stand-in paths no longer climb above `assets/`.
> - The World HUD classes are namespaced `wdi-world-*` so the theme's opt-in cannot restyle them.
> - Credits rows for the two self-hosted OFL fonts; `docs/UI.md` in the docs index; the 5.6 step
>   excerpt and the tsup bundling note in ARCHITECTURE.
>
> ### Follow-ups for round 3
>
> 1. **Client room exposure**: `net/worldRouter.ts` still reads `NetworkService`'s private room through a
>    cast and polls it every 250 ms, and `sceneEnter` is registered on the room twice; expose the room (a
>    getter or event) and attach the world feed from there.
> 2. **HUD adopts the theme**: replace `view/hud.css` with the `wdi-hud-*` components of `docs/UI.md`
>    (the `wdi-world-*` namespace then disappears), and wire the lobby, card and landing screens to
>    `ui/theme/` per its README.
> 3. **M3 first playable**: kill -> body -> clues -> report -> meeting -> vote -> win, per ROADMAP M3; then
>    M3b quick mode, M3c NPC fill.
> 4. **Art**: the owner's sign-off on the villager block-out contact sheet; the real buildings, tiles and
>    clue sprites still point at placeholder stand-ins in the default manifest.
> 5. **Small**: `placeNewPlayers` scans every sim player each tick to see whether the profile is fixed
>    (keep a flag); `assets/source/MANIFEST.md` is not prettier-formatted (ignored by lint).
> 6. **Owner**: GitHub Pages source and `VITE_SERVER_URL`; the Render service; a 2022 mid-range Android
>    frame-rate check and the first 2-4 person playtest (M2 exit); run the studio pipeline from the ROSW
>    checkout for the notes PR groot99-droid/Pipelines-Plugin#10 lists.
>
> ## Round 3 (started 2026-10-16, after round 2 landed at a98cc3f)
>
> Seven sessions build **M3, the first playable** (ROADMAP: kill -> body -> clues -> report -> meeting ->
> vote -> win) plus the round-3 follow-ups 1, 2 and 5 above, the art and audio M3 needs, and the
> playtest kit for the M3 exit. M3b (quick mode) and M3c (NPC fill) are round 4; nothing in round 3 may
> make them harder (the `loft` scene, `Settings.mode`, `Winner.debtor/nobody` and the NPC seats stay as
> designed). Same rules as rounds 1 and 2: draft PRs against `claude/zen-turing-m1jnw0`, under 400 lines
> where the work allows (split by step), `pnpm lint && pnpm typecheck && pnpm test` clean before every
> push, pinned versions only, no model identifiers in committed files, `docs/GDD.md` changes in the same
> PR as a behaviour change. Code and tooling run on Sonnet 5.5; art and design run on Opus 5.5.
>
> **Pre-seeded on the base branch** (commit "Round 3 contract" and its follow-up, DECISIONS A30), so no
> two sessions add the same thing: the schema fields `Body.of`, `Clue.value`, `Clue.dir`,
> `GameState.startTick` and `NotebookEntry.status` 4 (`teaching`); the shared constants `ClueKind` and
> `NotebookStatus` (`@wdi/shared/constants`); the protocol types `DeathCause`, `MeetingReason`,
> `ChatChannel` and the `killed`, `meetingStart`, `chat.msg`, `voteResult` payloads
> (`@wdi/shared/protocol`, `docs/PROTOCOL.md` regenerated); `StatusBit.bloody` = 2 in both mirrors
> (`apps/server/src/sim/constants.ts`, L, and `apps/client/src/view/animIds.ts`, N); the `RoomSim` seam
> fields (`PlayerSim.dead`, `sceneIdx`, `bloodyUntilTick`, `bandagedUntilTick`, `hold`,
> `resetForLobby()`; `RoomSim.meetingRequests`, `deaths`, `profileFixed`, `clueSeq` per scene,
> `resetForLobby()`); `enterScene(..., transit, announce = true)` in `Portals.ts`, which mirrors
> `PlayerSim.sceneIdx` and writes the public `Player.sceneId` only while the player is alive or their
> death is public; `Visibility.ts` keyed on `sceneIdx`; the stage stubs `sim/Clues.ts` (`runDecay`, L)
> and `sim/Phases.ts` (`runPhases`, K) already called by `sim/Step.ts`; `meeting.vote` and `chat.say`
> routed to `PartyRoom.lobbyCommands` (the flow queue K drains); the four empty rules modules
> `packages/shared/src/rules/{votes,win,kill,clues}.ts` already exported by `rules/index.ts`;
> `apps/server/test/simHelpers.ts` recording every server message and taking white-box roles by bot
> name; the `meetingRequest` event and optional `resume()` on the client `WorldFeed`; the
> `data-testid="hud-clock"` hook the three e2e suites locate the HUD by; the two numbers
> `phases.gameOverS` and `chat.maxChars` in `balance.json` with their GDD 3.3 and 3.5 lines. **Nobody
> edits** `packages/shared/src/{schema,protocol,rules}/index.ts`, `packages/shared/src/index.ts`,
> `apps/server/src/sim/Step.ts`, `apps/server/test/simHelpers.ts`, `balance.json` or its schema: a
> session that needs another contract writes it in its PR description and carries on with a local
> stand-in; the orchestrator adds it to the base branch. Every `*Tick` field is in ticks: a seconds value
> from content is multiplied by `TICK_RATE` at the write, as `secondsToTicks` in `handlers/lobby.ts`
> does. Content paths are the whole file: `clues.clues.blood.decay.seconds`,
> `clues.clues.footprints.decay.seconds`, `clues.clues.blood.params.visibleTiles`,
> `abilities.abilities.kill.rangeTiles`, `roles.roles[id].bellPulls`.
>
> | Session | Model | Track | Branch | Owns |
> |---|---|---|---|---|
> | **K. Match flow** | Sonnet 5.5 | Code | `claude/m3-flow` | `apps/server/src/rooms/**` (PartyRoom, `handlers/{lobby,debug,movement}.ts`), `apps/server/src/sim/{Phases,Meeting,Chat,Win,Visibility}.ts`, `apps/server/src/services/MatchLog.ts` (new), `apps/server/test/flowHelpers.ts` (new) and `apps/server/test/{flow,meeting,chat,win,lobby,party,visibility}*.test.ts`, `packages/shared/src/rules/{votes,win}.ts` and their tests, `docs/GDD.md` 3.3, 3.5 (the chat lines), 3.7 (the ghost lines) and 3.8 (one sentence each, only where the PR changes behaviour, marked "(M3)"), `docs/ARCHITECTURE.md` 5.7 and 5.8 |
> | **L. Kill, bodies, clues, Notebook** | Sonnet 5.5 | Code | `claude/m3-kill` | `apps/server/src/sim/{Commands,Movement,Portals,PortalQueue,RoomSim,World,constants,Clues}.ts`, new `apps/server/src/sim/{Actions,Kill,Death,Bodies,Hold,Noise}.ts`, `apps/server/test/killHelpers.ts` (new) and `apps/server/test/{sim,kill,clue,hold,report,ghost}*.test.ts`, `packages/shared/src/rules/{kill,clues}.ts` and their tests, `docs/GDD.md` 3.2 (the Kill and Bandage rows) and 3.4 (one sentence each, marked "(M3)"), `docs/ARCHITECTURE.md` 5.6 |
> | **M. Screens: meeting, game over, chat, theme** | Sonnet 5.5 | Code | `claude/m3-meeting` | `apps/client/src/ui/**` (the theme's `tokens.css` and `components.css` only for fixes noted in the PR, never the `.wdi-hud*`, `.wdi-log*`, `.wdi-edge-cue*`, `.wdi-toast*`, `.wdi-stick*`, `.wdi-touch-*` or `.wdi-notebook*` rules), `apps/client/src/net/{NetworkService,mock,fixtures,protocol,worldRouter}.ts`, new `apps/client/src/net/{meeting,meetingColyseus}.ts` and `net/mock/meetingMock.ts`, `apps/client/src/scenes/{Boot,Preload,Landing,Lobby,RoleReveal,registry}.ts`, new `scenes/{Meeting,GameOver}.ts`, `apps/client/src/main.ts`, `apps/client/index.html`, `apps/client/e2e/{party,smoke}.spec.ts`, new `e2e/meeting.spec.ts`, `apps/client/public/mockups/**`, `docs/UI.md` 11 and 12, `docs/ARCHITECTURE.md` 5.9 |
> | **N. World actions** | Sonnet 5.5 | Code | `claude/m3-world` | `apps/client/src/scenes/World.ts`, `apps/client/src/view/**` (Hud, hud.css, EntityView, PlayerView, animIds, assets, greybox; new `BodyView`, `ClueView`, `PropView`, `Lighting`, `NotebookPanel`, `AudioBus`), `apps/client/src/input/**`, `apps/client/src/net/{world,worldColyseus}.ts`, `apps/client/src/net/mock/worldMock.ts`, `apps/client/e2e/world.spec.ts`, `docs/SPRITES.md` 5 (loading notes only) |
> | **O. Bots, match e2e, soak** | Sonnet 5.5 | Code | `claude/m3-bots` | `tools/bots/**`, `tools/grid/test/**`, new `apps/client/e2e/match.spec.ts`, `apps/client/e2e/env.ts`, `apps/client/playwright.config.ts`, root `package.json` scripts, `docs/ARCHITECTURE.md` 5.12, `docs/ROADMAP.md` 7.5 (the Bot-only row only) |
> | **P. Art: props, clues, VFX, body** | Opus 5.5 | Art | `claude/m3-art` | `assets/**`, `apps/client/public/assets/**` except `ui/`, `audio/` and `calibration/` (so `manifest.json`, `chars/`, `clues/`, new `props/`, `vfx/`), `tools/blender/**`, `tools/sprites/**`, `CREDITS.md` (rows appended at the end of the "Generated assets" and "Hand-made original art" tables), `assets/source/MANIFEST.md`, the `assets/source` line of `.prettierignore` (the one root file P edits), `docs/ASSETS.md` 6.3 and 6.7, `docs/SPRITES.md` 8 |
> | **Q. Playtest kit, audio, copy** | Opus 5.5 | Design | `claude/m3-playtest` | new `docs/PLAYTESTS/**`, new `apps/client/public/assets/audio/**` (files plus its own `audio/manifest.json`), `LICENSES/**` (new licence texts only), `CREDITS.md` (rows appended at the end of the "Third-party assets" table), `docs/UI.md` 14 (new: the M3 copy deck), `docs/ROADMAP.md` 7.5 (the feedback form, a new paragraph after the metrics paragraph), `docs/GDD.md` 2 (wording only, no rule or number) |
>
> Suggested merge order: L, K, N, M, O, P, Q. Shared documents: edits stay inside the named section
> with no renumbering or reflow, and the orchestrator keeps both sides of any conflict. Decisions a
> session has to make go to `docs/DECISIONS.md` under its reserved number (K A31, L A32, M A33, N A34,
> O A35, P A36, Q A37; a second row takes the number plus 10), never editing an older row. Nobody else
> touches GDD 3.x. Owner, before the first M3 playtest: the Railway Hobby service and `VITE_SERVER_URL`
> (ROADMAP M3, A6) and the Pages source; Q's `docs/PLAYTESTS/README.md` lists them as prerequisites.
>
> ### Briefs
>
> **K. Match flow (server).** Build the loop around the kill: phases, meetings, votes, chat, win, game
> over, ghosts' views, lobby reconnection, the debug helpers tests need, and the match log. Everything
> runs inside the fixed step: `runPhases(room)` in `sim/Phases.ts` is called by `step()` last; the flow
> commands (`lobby.*`, `meeting.vote`, `chat.say`) arrive in `PartyRoom.lobbyCommands` and are drained
> by `runLobbyCommands`. Phases (GDD 3.3, A30): `beginPlay` and `runDebugStart` both set
> `GameState.startTick`; grace -> day -> dusk -> night -> day... with `round` + 1 on every entry into
> day; every length from `balance.phases`. On the grace -> day transition `runPhases` sets
> `priv.cooldownEndTick.set("kill", tick + byCount[n].killCooldownS * TICK_RATE)` for every seat whose
> role lists `kill` (the Knife's first cooldown; L's `validateKill` reads only `cooldownEndTick`).
> Meetings: drain `simOf(room).meetingRequests` (pushed by L's report and bell); on the first request
> move every player, living or dead, with `enterScene(room, player, p, 'overworld', 'square_<ordinal %
> 10>', false, false)` (the seventh argument suppresses the `sceneEnter`; L keeps the default), set
> `sim.viewsDirty = true`, flip `alive = false` for every `PlayerSim.dead`, reset `hasVoted = false` and
> `priv.myVote = ""` on every seat, fill `MeetingState` (`phase`, `reason`, `callerId`, `bodyOf`,
> `endsTick`; `missing` and `board` stay empty until M4), then broadcast `meetingStart` and set
> `meetingDiscussion` with `byCount[n].discussionS` (n = max(4, seats)), in that order. `MeetingState.phase`
> holds the same `Phase` id as `GameState.phase` (0 outside a meeting) and `MeetingState.endsTick`
> mirrors `phaseEndsTick`, which every meeting `setPhase` sets and broadcasts as `phaseChange`. Votes
> (`sim/Meeting.ts`): from living players in `meetingDiscussion` and `meetingVote`, `targetId` a living
> player's id or `"skip"`; a repeated vote replaces `priv.myVote` without any reply and `hasVoted` stays
> true (no retraction); a vote in `reveal` or outside a meeting is refused 425, from a dead player 422,
> with an unknown or dead target 422; when every living player has voted go to `reveal` at once (in
> `meetingDiscussion` too), else after `voteS`. `resolveVotes(votes, living)` in
> `packages/shared/src/rules/votes.ts` is pure: plurality, a tie or a Skip plurality ejects nobody; the
> anti-stall rules of GDD 3.8 stay off (their arguments exist, default off). `reveal` lasts `revealS`:
> broadcast `voteResult {tally, ejectedId?, role?}` (counts per target and `skip`; voters never
> revealed); an ejected player gets `dead = true`, `alive = false`, private `killed {sceneId, cause:
> "ejected", roles}`. `checkWin` (`rules/win.ts`, pure, GDD 3.8: Village when no Cabal lives; Cabal at
> `byCount[n].cabalWin`, `parity` at 6+, `villageAtMostOne` at 4-5; neutral roles count for nobody;
> tasks and Final Night are M4) runs on the tick a `DeathEvent` is drained from `sim.deaths` and, for an
> ejection, when the reveal phase ends, so the stamp and the role line show for the whole reveal; never
> on a bare tick. No winner: on entering `immunity` (`immunityS`, a world phase in which L refuses
> kills) call `enterScene(room, player, p, 'overworld', 'square_<ordinal % 10>', false)` again for every
> player, living or dead, and set `sim.viewsDirty = true`: this announced `sceneEnter` is the client's
> cue to leave the meeting; then `day`. Winner: phase `gameOver`, `winner`, broadcast `gameOver
> {winner, roles, summary}` (no `sceneEnter`), one match-log line (`services/MatchLog.ts`: JSON to
> stdout with players, duration, winner, kills, meetings, each ejection's correctness, vote accuracy per
> meeting, clues collected per player; ROADMAP 7.5), and after `phases.gameOverS` `resetToLobby`:
> phase `lobby`, `room.unlock()`, every seat kept with `alive`, `ready`, `hasVoted`, traits, `sceneId`,
> `presence` and `priv` cleared, bodies and clues cleared, `simOf(room).resetForLobby()` (which resets
> every `PlayerSim`). Chat (`sim/Chat.ts`): `chat.say` text trimmed to `balance.chat.maxChars`, empty
> refused 422; from a living player only in `meetingDiscussion`, `meetingVote` and `reveal` (425
> otherwise), sent to every client as channel `meeting`; from a dead player in any phase, sent to dead
> players only as channel `ghost`; the Cabal channel and quick chat are M4. Visibility: a living viewer
> receives the presence of living (`!dead`), placed players in its scene; a dead viewer receives
> everyone in its scene; scene tests use `PlayerSim.sceneIdx`, never the public `sceneId`; in the
> meeting, reveal and gameOver phases no presence is encoded (`isWorldPhase` is false). Blood is the one
> presence field that correlates with a role in M3 (only the Killer gains it): it is encoded to every
> client in the scene, so a modified client reads it beyond 3 tiles; V1 accepts this (A30, like
> darkness). Disconnect: in phase `lobby`, `onLeave` keeps the seat with `connected = false` through
> `this.allowReconnection(client, balance.disconnect.deathAfterS)` and frees it when the window lapses
> or the player left consented (GDD 3.10 "reconnection in lobby"); during play `onLeave` only sets
> `connected = false` and pushes `{playerId, cause: "vanished", tick}` to `sim.deaths`, and the next
> `runPhases` sets `PlayerSim.dead` and runs `checkWin` from the drain (no body, no reconnection; both
> M7); the leader passes as today. Debug (`WDI_DEBUG=1` only, flags consumed in the step; `debug.play`
> stays exactly as today): `debug.deal {roles: {sessionId: roleId}}` (any client; a test maps names to
> ids through the public roster) fixes the next deal: at Start the fixed seats take their roles, each
> such role is removed once from the roster row, and `assignRoles` deals the remaining roles to the
> remaining ids, so the roster counts hold; `debug.clock {phase?, clearCooldowns?}` with `phase` a name
> among `grace`, `day`, `dusk`, `night`, `immunity` (else 422) jumps first (a fresh `phaseEndsTick`,
> `round` unchanged), then `clearCooldowns: true` zeroes every `cooldownEndTick` entry and every
> `bandagedUntilTick`. Tests with `@colyseus/testing` (helpers in `test/flowHelpers.ts`, importing
> `simHelpers` unchanged): the phase loop and the Knife cooldown at day; a report moves everyone to
> the square, sends `meetingStart` after the placements and no `sceneEnter`; after the reveal every
> client receives a second `sceneEnter`; a vote from a dead player is refused; early end when all have
> voted; a second meeting starts with `hasVoted` false; tie ejects nobody; the ejected role is revealed
> and `gameOver` arrives only after `revealS`; Village and Cabal wins at 4, 5 and 6 seats; ghost chat
> reaches only the dead; a living client never receives a dead player's presence and never sees a
> ghost's `sceneId` change before the meeting; Blood state absent from the meeting roster (no public
> `Player` field changes with the Blood timer); a dropped lobby bot that reconnects within the window
> keeps its seat and name; the lobby reset keeps the seats and clears the private state; the match log
> line. K calls only the existing `enterScene` (Portals.ts) and `isWorldPhase` / `sceneKey` (World.ts),
> whose signatures L keeps. Do not touch `sim/Commands.ts`, `Portals.ts`, `Movement.ts`, `RoomSim.ts`
> or the schema.
>
> **L. Kill, bodies, clues, Notebook (server).** The verbs. `sim/Commands.ts` keeps its switch and
> dispatches `act.ability`, `act.hold`, `act.reportBody` and `act.bell` to `sim/Actions.ts`; every
> payload is untrusted. "Alive" below always means `!PlayerSim.dead`, never the public `alive`, which
> stays true for a ghost until the meeting. Kill (`sim/Kill.ts`, GDD 3.2 and A30): `act.ability
> {abilityId: "kill", targetId}` from a player whose `priv.role.roleId` lists `kill`; refused unless the
> phase is day, dusk or night (425), the actor is alive, placed, not busy (426) and past
> `priv.cooldownEndTick.get("kill")` (424, the entry K writes at day); the target is alive, in the same
> scene (`sceneIdx`), not in transit, within `abilities.abilities.kill.rangeTiles` plus the distance the
> target moved in the last 250 ms (`positionAt`, 427), with no solid tile on the straight line between
> them; a Bandaged target (`bandagedUntilTick > tick`) refuses with 422 "nothing happens", spends the
> bandage, and the attacker still gains Blood and restarts the cooldown. `validateKill` in
> `packages/shared/src/rules/kill.ts` is pure over plain numbers and a `solidBetween` callback, with
> property tests. On a kill: the victim's `PlayerSim.dead = true` (the public `alive` stays true until
> the next meeting, A30), `sim.viewsDirty = true` so the living stop receiving the victim's presence on
> that tick, push `{playerId, cause: "knife", killerId, tick}` to `sim.deaths`, send the victim private
> `killed {sceneId, cause: "knife", roles}` (every seat's roleId; ghosts see all roles), spawn the `Body`
> (`id: "body_<playerId>"`, `of`, `hidden: false`) in that scene's `bodies`, give the killer
> `bloodyUntilTick = tick + clues.clues.blood.decay.seconds * TICK_RATE` (OR `StatusBit.bloody` into
> `presence.statusBits` where `Movement.ts` writes them), reset `cooldownEndTick.kill` from
> `byCount[n].killCooldownS * TICK_RATE`, and emit the scream (`sim/Noise.ts`, `emitNoise` moved out of
> `Portals.ts`, radius `noise.killScream`). `Body.x/y` and `Clue.x/y` are pixel centres of their tile
> (`tileCentre(tx, TILE_PX)`), the same units as `Presence.x/y`. Clues (`rules/clues.ts` pure,
> `sim/Clues.ts`): every kill spawns Footprints (`ClueKind.footprints`, `value` = the killer's height
> index) at the kill tile with `dir` toward the nearest portal of the scene, and a Thread
> (`ClueKind.thread`, `value` = the killer's scarf index) on the walkable tile beside that portal; the
> 2-of-3 choice, felt and prints come with M4(a). Ids: the teaching clue is `clue_teaching`; every other
> clue is `clue_<sceneId>_<n>` from `sim.clueSeq` (one counter per scene, so an id never counts kills
> elsewhere); a `NotebookEntry.id` is `entry_<n>` counted per player and `clueFound.entryId` carries it.
> Footprints decay after `clues.clues.footprints.decay.seconds` (`runDecay`, the stub in `sim/Clues.ts`),
> Thread never; above `balance.clues.capPerScene` the oldest claimed clue goes first. At the first
> placement spawn the teaching clue at the `ov.teaching_clue` prop (Footprints, value tall). Collect
> (`sim/Hold.ts`): `act.hold {action: "collect", targetId, on}` starts a hold kept in `PlayerSim.hold`,
> re-validated every tick (a world phase, alive, same scene, within `balance.doors.reachTiles` of the
> clue, not busy; leaving a world phase cancels it); after `abilities.abilities.collect.castS` the clue is
> `claimed`, a `NotebookEntry` is pushed to the collector's `priv.notebook` (`clueKind`, `value`,
> `sceneId`, `tick`, `status`: `verified` for a role with `inspect`, `teaching` for `clue_teaching`,
> else `claimed`) and private `clueFound {entryId}` is sent; several players may collect the same clue;
> releasing or moving cancels. Report and bell push `{reason, callerId, bodyOf}` to
> `sim.meetingRequests` (K drains): `act.reportBody {bodyId}` from a living player within
> `abilities.abilities.report.rangeTiles` of a body in its scene during a world phase and not yet
> reported (L keeps `RoomSim.reportedBodies` and refuses a second report with 422); `act.bell` from a
> living player on the overworld within `abilities.abilities.bell.rangeTiles` of `ov.bell` during day,
> dusk or night, at most `roles.roles[role].bellPulls` times per match (room memory). Bandage
> (`act.ability {abilityId: "bandage", targetId}`): a role with `bandage`, target alive, not self, same
> scene, within its `rangeTiles`, cooldown `cooldownS`, consumes one `bandage` from the inventory, sets
> the target's `bandagedUntilTick` for `params.protectS`; knockback, blackout and witness entries are
> M4(c). Ghosts (`dead`): move at walk speed, skip collision and the lock and busy checks of portals; a
> ghost's crossing updates only `PlayerSim.sceneIdx` (the base `enterScene` already freezes the public
> `sceneId` while the death is private), swings no door and emits no noise; every verb refuses a ghost
> (422). Fill `PlayerSim.resetForLobby()` and `RoomSim.resetForLobby()` with every field you add
> (`reportedBodies`, bell pulls, collectors per clue, the teaching flag). Death by ejection is K's.
> Tests (helpers in `test/killHelpers.ts`, importing `simHelpers` unchanged, with its white-box roles):
> kill range with and without the ring slack; grace, immunity and cooldown refusals; the bandaged
> target; the body and both clues appear in the scene state and nowhere else; a client outside the
> scene never receives the body or the clue; the ARCHITECTURE 5.4 fuzz test scoped to M3 (over a
> scripted kill a non-Cabal client outside the kill scene receives no field change at all, and a client
> inside the scene receives only the `bodies` and `clues` additions of that scene and `statusBits` bit 2
> on the killer); collect timing, cancel on move and on phase change, Detective `verified`; report and
> bell push a request, a second report of the same body is refused, the bell count; a ghost walks
> through a locked door, leaves `Door.swingUntilTick` untouched and sends no `noise`. Do not touch
> `rooms/**`, `sim/Visibility.ts`, `sim/Phases.ts`, `test/simHelpers.ts` or the schema.
>
> **M. Screens: meeting, game over, chat, theme (client).** Follow-up 1 first: give `NetworkService` a
> `room` getter (null until wired) and a `room` bus event; the router attaches both feeds from it with no
> cast and no interval. The room's `sceneEnter` handler stays in N's `ColyseusWorldFeed`: remove
> `sceneEnter` from `NetworkService.SERVER_MESSAGES` and let the router re-emit the feed's `sceneEnter`
> on `net.bus` for `RoleReveal`, so it is registered once. Then the theme (follow-up 2, screens part):
> import `ui/theme/tokens.css` and `components.css` once in `main.ts`, `class="wdi-root"` on `#overlay`,
> and move Landing, Lobby and the role card to the theme classes per `docs/UI.md` 11, keeping every
> `data-testid`. Meeting feed (`net/meeting.ts`, `meetingColyseus.ts`, `mock/meetingMock.ts`): the
> public roster (`id`, `name`, `traits`, `alive`, `hasVoted`), `MeetingState`, the clock, own vote, chat
> lines, events `meetingStart`, `voteResult`, `gameOver`, `chat.msg`, `phaseChange`; `vote(target)`
> sends `meeting.vote {targetId}` (`"skip"` for Skip), `say(text)` sends `chat.say`. Router: a
> `sceneEnter` that arrives while no `Meeting` is active is today's World restart; on `meetingStart`
> sleep `World` and launch `Meeting`; only a `sceneEnter` received after `meetingStart` stops `Meeting`
> and starts `World`; on `gameOver` stop both and start `GameOver`; when the phase returns to `lobby`
> start `Lobby` (the roster still flows from `NetworkService`). In mock mode only, the router forwards
> the world feed's `meetingRequest` event to `MockNetwork.openMeeting(req)`, which emits `meetingStart`,
> runs discussion -> vote -> reveal (bots vote at random, the player's vote counts), emits `voteResult`
> and then either `gameOver` or calls `resume()` on the published world feed, which re-emits
> `sceneEnter`. `Meeting` (DOM, `docs/UI.md` 6 and the `mockups/meeting.html`): the reason line ("Hana
> reported Gus's body", "Hana rang the bell"), the portrait grid (name, trait icons, `is-dead`,
> `is-self`, the vote chip from `hasVoted`, `is-selected` for own vote; the picture is the villager
> atlas drawn to a canvas from the public traits, an initial on slate when the atlas is absent), tap a
> portrait or Skip to vote (living only; a ghost sees the grid and the chat but cannot vote), the
> discussion and vote timers from `phaseEndsTick`, tabs Report and Chat (the Notebook tab is wired at
> integration with `new NotebookPanel(tabElement, feed)` from N, `update()` and `destroy()`), the chat
> log and form (a ghost's form posts to the ghost channel; `chat.msg` lines show their channel), and the
> reveal: tally numbers on the portraits, the stamp on the ejected portrait, the role line. The scene
> stays until the `sceneEnter` that follows the reveal. `GameOver` (DOM): winner banner, every seat's
> role and faction, the summary, a countdown to the lobby. Frozen `data-testid`s for O: `meeting`,
> `meeting-reason`, `portrait-<playerId>`, `vote-skip`, `vote-count-<playerId>`, `stamp`, `reveal-role`,
> `chat-log`, `chat-input`, `gameover`, `gameover-winner`, `gameover-role-<playerId>`. Mock: `?mock=1`
> must reach the meeting, the reveal, game over and back to the lobby without a server. e2e
> (`meeting.spec.ts`, mock): vote, early end, stamp, game over, lobby. `party.spec.ts` keeps passing
> against the real server (it locates the HUD by `hud-clock`). Do not touch `scenes/World.ts`,
> `view/**`, `input/**`, `net/world*.ts` or `net/mock/worldMock.ts`.
>
> **N. World actions (client).** Extend `net/world.ts` (and both feeds) with `bodies()`, `clues()`,
> `notebook()` (own entries), `dead()`, `kill(targetId)`, `ability(id, targetId)`, `hold(action,
> targetId, on)`, `reportBody(bodyId)`, `bell()`, and the events `killed`, `clueFound`, `phaseChange`.
> `dead()` turns true on `killed` or when your own roster `alive` is false, is held in the feed (never in
> the scene) so it survives World restarts, and resets when `clock().phase` returns to `lobby`. In
> `World`: a prompt (`data-testid="prompt"`) and the E key act on the nearest target in reach (a body:
> "Report", a clue: "Hold E to collect" with a 2 s ring, the bell on the overworld: "Ring the bell", a
> door: "Enter"); the Q/R/F keys send `act.ability` for the card's ability rows (`ABILITY_KEYS`,
> `getNet(this).roleCard.abilities`; `REG_ROLE_CHIP` stays `{team, goal}`) with the nearest living
> player as target; a hold starts on keydown and ends on keyup, and on touch the Use disc sends `on:
> true` on `pointerdown` and `on: false` on `pointerup` or `pointercancel`, Report, Enter and Ring the
> bell fire on `pointerdown`, a release before `castS` is a cancelled hold. Draw bodies (`BodyView`: the
> last `die` frame of `char_villager` with the dead player's overlays from the public traits), clues
> (`ClueView`: `clue_footprint_<s|m|t>_mid` five times along `dir` from the tile,
> `clue_thread_<red|green|blue>`; keys from `docs/SPRITES.md` 8), the overworld props of
> `scenes/overworld.json` (`PropView`: `ov.bell`, `ov.pump`, `ov.board`, `ov.chest`, the lantern posts
> by key `prop_<kind>` from the `props` atlas), the Blood overlay (`PlayerView` shows the `blood` pass
> while `statusBits & StatusBit.bloody` and the player is within `clues.clues.blood.params.visibleTiles`
> of you), the night mask (`Lighting`: a radius of `vision.dayTiles` by day and `vision.nightTiles` at
> night around you, a "Night falls" toast at dusk), the phase on the HUD clock, and ghost mode after
> `killed` (your sprite translucent, "You are a ghost", prompts hidden except doors, movement kept). A
> greybox mark stands in for any key the manifest lacks (`textures.exists`). `Body.x/y` and `Clue.x/y`
> are pixel centres, used unscaled. On `clueFound` the Notebook opens on the new entry (GDD 2 step 5);
> during grace show the three toasts of GDD 2 step 5 (the bell one reads "E at the bell calls a
> meeting"; ids from UI.md 14 once it exists, the GDD lines until then). The HUD adopts the theme
> (follow-up 2, World part): `view/Hud.ts` and `hud.css` move to `.wdi-hud` with
> `__tl/__tc/__tr/__bl/__br`, `.wdi-hud-chip`, `.wdi-hud-clock` (`--night`), `.wdi-log` lines,
> `.wdi-toast` and `.wdi-edge-cue` for noise; import the theme CSS from the module (`hud.css` after it,
> so N's overrides win; the global import lands with M) and put `wdi-root` on the HUD root element so
> the fonts apply before M's `#overlay` change; the `wdi-world-*` namespace disappears; the touch
> cluster uses `.wdi-stick`, `.wdi-touch-cluster` and `.wdi-touch-btn` with Use (E), Act (Q), Run and
> Sneak; the Notebook opens from the N key and a button beside the chip. Frozen `data-testid`s:
> `hud`, `hud-clock` (already on the clock), `hud-fps`, `prompt`, `notebook`, `notebook-entry`,
> `touch-use`, `touch-act`. `World` hides the HUD, the prompt and the touch cluster on
> `Phaser.Scenes.Events.SLEEP` and shows them on `WAKE`, so M's `Meeting` never touches `view/**`.
> `NotebookPanel` (`new NotebookPanel(parent, feed)`, `update()`, `destroy()`, `.wdi-notebook`): one
> row per entry with the clue icon, the trait value, the scene name and `m:ss` from `tick -
> startTick`, and the status chip (claimed, verified, teaching). `AudioBus`: loads
> `assets/audio/manifest.json` when it exists and plays `footstep`, `door_open`, `door_close`,
> `door_locked` (error 423 or 428), `pickup`, `scream`, `bell` and `ambient` by key, silent otherwise (Q
> supplies the files). Mock (`MockWorldFeed`): the player kills the nearest bot (body and both clues
> appear), collects, opens the Notebook, sees the night mask; `reportBody` and `bell` emit the
> `meetingRequest` event on the feed bus; `resume()` re-emits `sceneEnter` for the current scene; the
> mock never emits `meetingStart`, `voteResult` or `gameOver`. e2e (`world.spec.ts`): the existing door
> flow plus kill -> body -> collect -> one Notebook entry on the mock. Do not touch `ui/**` except
> reading `ui/dom.ts` and the theme CSS, `net/{NetworkService,worldRouter,mock}.ts`,
> `net/mock/meetingMock.ts`, `main.ts` or `manifest.json`.
>
> **O. Bots, match e2e, soak (tooling).** `tools/bots`: `swarm.ts` gains `vote: "skip" | "leader" |
> "random" | <player name>` (cast as soon as a meeting starts), `report: boolean` (report a body in
> reach), `walk: boolean` (default true for walkers, false keeps a bot on its spawn), and keeps
> `SwarmOptions` `code`, `count`, `url` and `ready` with today's defaults so `party.spec.ts` runs
> unchanged; `walk.ts` walkers step toward a body they see and report it, vote per option, and, when
> their own card holds `kill` and `--killer` is set, strike the nearest player in reach once the
> cooldown allows; `soak.ts` reaches play through `debug.deal` from the leader bot and `lobby.start`
> (every bot sends `lobby.ready {ready: true}` on `roleReveal` as `swarm.ts` does; `debug.play` stays
> for L's tests) and runs 6 walkers with one killer and reporters so bodies, clues and meetings exist
> during the 30 minutes, still failing on a presence leak, a dropped bot, a protocol error beyond
> refusals or p95 tick above 15 ms. `apps/client/e2e/match.spec.ts` against the real server (the
> Playwright `webServer` runs the server with `WDI_DEBUG=1` on port 2570; `e2e/env.ts` keeps exporting
> `E2E_SERVER_PORT` and `E2E_SERVER_URL`): host and guest in two browsers plus three bots, `debug.deal`
> makes the host the Killer, `debug.clock {phase: "day", clearCooldowns: true}`, the host walks to the
> guest and presses Q, reports the body with E, everyone votes the host, the stamp lands, Village wins,
> the game-over screen shows every role, and the lobby comes back with the same code; a second test at 4
> seats (host, guest, two bots with `walk: false` standing on `square_2` and `square_3`): the host is the
> Killer, kills the first bot, reports it, the host and the guest vote the second bot while the bots
> vote skip, and the Cabal game-over screen shows. The spec locates screens by the frozen ids in M's and
> N's briefs and the lobby ids that exist today. `tools/grid/test/reach.test.ts` adds the widow cottage
> (both rooms), the forest and the cave entry. `docs/ARCHITECTURE.md` 5.12 and ROADMAP 7.5's bot row
> describe the new bots. Write the spec against the contracts in this file and A30; run it once K, L, M
> and N have merged (the orchestrator re-runs it at integration).
>
> **P. Art: props, clues, VFX, body (Opus).** Rebuild the villager masters from
> `tools/blender/build_villager.py` (they existed only in Session H's container), record their hashes in
> `assets/source/MANIFEST.md`, run `prettier --write` on it and remove the `assets/source` line from
> `.prettierignore` (follow-up 5). Through the rig: the real clue sprites under the existing `clues`
> atlas keys (SPRITES 8: footprints x3 heights x3 mud, thread x3, felt x3, smear, print, wet bucket,
> fur, claw, drag) replacing the placeholder entry in the real manifest; the square props as a `props`
> atlas (`prop_bell`, `prop_pump`, `prop_noticeBoard`, `prop_kitChest`, `prop_lanternPost` with `_lit`
> and `_unlit`, keyed by the `kind` of `scenes/overworld.json`, origin at the base); a `vfx` atlas
> (`vfx_blood_pool` 8 f, `vfx_blood_splat` 12 f, `vfx_vote_stamp` 10 f, `vfx_dust_step` 6 f); and a
> contact sheet of the `die` clip's last frame in all 8 directions with the hat and scarf overlays, since
> it is the body sprite. New keys go to `docs/SPRITES.md` 8 and `manifest.json`; CC0 rows in
> `CREDITS.md` with catalog ids where Higgsfield is used (ASSETS 6.5, A17). Nothing here touches client
> code: N draws a greybox mark for any key the manifest lacks.
>
> **Q. Playtest kit, audio, copy (Opus).** `docs/PLAYTESTS/`: `README.md` (how a session runs: the Pages
> link, the server, Discord, the host's script for a 5-player M3 session, three matches, timing, and the
> owner prerequisites above), `FORM.md` (the ROADMAP 7.5 feedback form, ready to paste into a Google
> Form), `SCORECARD.md` (the fun-or-stop sheet for the M3 exit: three 5-player matches end in a Village
> or Cabal win in 10-18 min, vote accuracy from the match log, "would play again" 1-10, the decision
> line), `TEMPLATE.md` for one session's notes, and `2026-xx-xx-m2.md` as the M2 playtest entry stub.
> Audio: eight CC0 SFX and one ambient loop from Kenney or Freesound CC0, OGG q5 under
> `apps/client/public/assets/audio/` with `audio/manifest.json` entries `{key, url, gain}` (`url`
> relative to `assets/audio/`, keys exactly `footstep`, `door_open`, `door_close`, `door_locked`,
> `pickup`, `scream`, `bell`, `stamp`, `ambient`), their `CREDITS.md` rows, and any licence text under
> `LICENSES/`; N plays them by key and M plays `stamp` at the reveal. Copy: `docs/UI.md` 14, the M3 copy
> deck: every toast, prompt, meeting line, ghost line, reveal and game-over line with an id, consistent
> with GDD 2 (the bell toast reads "E at the bell calls a meeting", since the bell is the E prompt); M and
> N paste from it, and GDD 2 is touched only for wording.
>
> ### Seams in round 3
>
> | From | To | Contract |
> |---|---|---|
> | L | K | L pushes `{reason: "body" \| "bell", callerId, bodyOf?}` to `simOf(room).meetingRequests` and `{playerId, cause, killerId?, tick}` to `simOf(room).deaths`; K drains both in `runPhases`. L sets `PlayerSim.dead` and keeps `sceneIdx` through `enterScene`; K flips the public `alive` at meeting start and on ejection and keys `Visibility.ts` on `dead` and `sceneIdx`. Neither imports a function the other adds in round 3; the exports that exist at the base (`enterScene`, `placeNewPlayers`, `reconcileViews`, `isWorldPhase`, `sceneKey`, `simOf`) keep their signatures. |
> | K | L | K keeps `isWorldPhase` as the gate for movement and portals and writes the Knife's first `cooldownEndTick` at day; L refuses kills outside day, dusk and night and every verb in `immunity`. `debug.clock` clears cooldowns and bandages through the seam fields. |
> | K, L | M, N | The wire: the pre-seeded schema fields and payloads (A30). `killed {sceneId, cause, roles}` is the ghost switch on the client; `clueFound {entryId}` points at a `priv.notebook` entry; at meeting start the placements send no `sceneEnter` and `meetingStart` follows them; at the start of `immunity` K re-places everyone with an announced `enterScene`, and that `sceneEnter` is the router's cue to stop `Meeting`; on a winner `gameOver` comes with no `sceneEnter`. |
> | M | N | The router (M) constructs N's `ColyseusWorldFeed(room)` and `MockWorldFeed` unchanged, publishes them under `REG_WORLD`, and starts, sleeps and stops `World`; N never starts a scene; `World` hides its DOM on SLEEP. Mock handoff: N's mock emits `meetingRequest` and exposes `resume()`; M's `MockNetwork.openMeeting` runs the meeting and calls `resume()`; `meetingMock.ts` never edits `worldMock.ts` and vice versa. M mounts N's `NotebookPanel(parent, feed)` on the meeting's Notebook tab at integration. The HUD (N) and the screens (M) adopt the theme separately: M's theme fixes never touch the HUD, log, edge-cue, toast, stick, touch or notebook rules; N overrides those only in `view/hud.css`. N reads the card from `getNet(this).roleCard`; `REG_ROLE_CHIP` stays `{team, goal}`. The e2e suites locate the HUD by `hud-clock`, never by class. |
> | N | P | Keys only, never paths: `clues`, `props`, `vfx` atlas keys from `docs/SPRITES.md` 8; N draws a greybox mark when `textures.exists(key)` is false. |
> | N, M | Q | `assets/audio/manifest.json` entries `{key, url, gain}` with the nine keys above; a missing key is silent. M and N paste copy from `docs/UI.md` 14 once it exists; until then the GDD 2 lines. |
> | O | K | `debug.deal`, `debug.clock` and the unchanged `debug.play` (K) are what the bots and `match.spec.ts` drive; the soak and the spec start play through `debug.deal` then `lobby.start`; `runDebugStart` sets `startTick` like `beginPlay`. O writes against the A30 contract and the frozen ids and runs after the merges. |
>
> ### Clarifications recorded before the round (DECISIONS A30)
>
> See the A30 row; in short: death is private until the next meeting (`alive` flips there, the victim
> gets `killed`, a ghost's public `sceneId` is frozen); ghosts walk, see everyone in their scene, are
> seen only by other ghosts, and chat on their own channel; M3 spawns Footprints toward the nearest
> portal and a Thread beside it, both readable in the world and logged on collect; Blood is a presence
> bit with a client-side 3-tile mask and is the one role-correlated field V1 accepts; kills only in day,
> dusk and night, with the ring slack and a straight-line check; a meeting moves everyone to the square
> silently, votes are secret counts, plain plurality with Skip, the reveal lasts its full time before a
> win; the win check runs after deaths and ejections only; after game over the room returns to the lobby
> with the same code; a disconnected player is a ghost at once (M7 adds reconnection and the body) and a
> lobby seat survives a dropped connection for the disconnect window; `WDI_DEBUG=1` adds `debug.deal`
> and `debug.clock` beside `debug.play`.
>
> ### Round 3 log: L
>
> **Landed** (`claude/m3-kill`): `validateKill`, `segmentBlocked`, `trailDir`, `besideTile`, `evictOverCap` in `packages/shared/src/rules/{kill,clues}.ts` (pure, randomized property tests in `packages/shared/test/kill.test.ts`); on the server `sim/{Actions,Kill,Death,Bodies,Hold,Noise}.ts`, the filled `Clues.ts` (`spawnClue`, `spawnKillClues`, `spawnTeachingClue`, `runDecay`), ghosts in `Movement.ts` and `Portals.ts`, the new fields in `RoomSim.ts` (all reset in both `resetForLobby()`), and `reject`, `isKillPhase`, `isVerbPhase` in `World.ts`. Tests: `test/killHelpers.ts` and `test/{kill,clue,hold,report,ghost}.test.ts`, including the ARCHITECTURE 5.4 diff test scoped to M3. GDD 3.2 and 3.4 got their "(M3)" sentences, ARCHITECTURE 5.6 a note, DECISIONS A32 the small calls.
>
> **For K and the orchestrator.**
>
> - The tests set `room.state.phase` white-box through `setPhase`, which also pushes `phaseEndsTick` out an hour. If K's `runPhases` derives a phase from `startTick`, `debug.play` and the cooldown rather than from `phaseEndsTick`, those tests need `debug.clock` instead.
> - `record()` in `killHelpers.ts` wraps `sim.meetingRequests` and `sim.deaths` so the report and bell tests still see requests once K drains them. The kill test reads `sim.deaths` through it too.
> - The fuzz test tolerates the victim's presence disappearing from a witness view (K's `Visibility.ts` change); it does not require it. After the merge, add an assertion that the living stop receiving the victim.
> - The kill cooldown is read from `priv.cooldownEndTick.kill` only; with no entry (a `debug.play` match before K's day transition) the Knife is ready but the grace phase still refuses (425).
> - Death by ejection, flipping the public `alive`, and clearing `scenes.*.bodies/clues` at the lobby reset are K's; `RoomSim.resetForLobby()` clears `clueMeta`, `reportedBodies` and the teaching flag, so K only has to delete the schema entries.
> - The Killer's scream is not sent to the Killer; every other placed player in the scene within `noise.killScream` hears it, ghosts included.
>
> **Not done.** Kill does not require the Knife item in the inventory (the Knife is bound; the role list decides). No ack message exists for Bandage; the Doctor sees the stock and cooldown change in the private state. Felt, prints, the 2-of-3 choice, knockback, blackout and witness entries are M4.
> ### Round 3 log: K (match flow, server)
>
> **Landed** (`claude/m3-flow`): `resolveVotes` and `checkWin` in `@wdi/shared` rules with tests (property loop over seeded votes); `sim/{Flow,Phases,Meeting,Chat,Win}.ts` and `services/MatchLog.ts`: the phase loop (grace -> day -> dusk -> night -> day, `round` + 1 on every day, Knife first cooldown at day), meetings (square placement without `sceneEnter`, `meetingStart`, discussion, vote, early end, reveal, announced `sceneEnter` at immunity), secret plurality votes, the win check on a drained death and at the end of an ejection's reveal, `gameOver` with one match-log JSON line, the reset to the lobby, chat by channel, ghost-aware reconcile, lobby reconnection (`onDrop`, `onReconnect`, `onLeave`), the vanished death during play, and `debug.deal` / `debug.clock`. Tests: `flow`, `meeting`, `win`, `chat`, `visibility` and the new reconnection block of `lobby`, with helpers in `flowHelpers.ts`. Choices are in DECISIONS A31.
>
> **For the orchestrator and the next sessions.** L's `report` and `bell` only need to push to `sim.meetingRequests` and the kill to `sim.deaths`; my tests stand in for both white-box (`request`, `murder` in `flowHelpers.ts`), so run K's and L's suites together after the merge. `debug.play` now broadcasts `phaseChange` and stamps the grace clock, so a debug match leaves grace after `graceS` seconds like a real one: tests that need a day call `debug.clock {phase: "day"}`. Ghost presence is hidden by `PlayerSim.dead`, which L sets on a kill; nothing else changes the view code. A bot or e2e that leaves during play ends the match for the Cabal when the Village falls to its limit, because a leaver is a ghost at once. **Not done:** the missing-person roll-call, the suspect set and `meeting.board` (M4), the anti-stall rules and the wrong-ejection bonus (off in M3), reconnection and the body for a player who drops during play (M7).
> ### Round 3 log: N (World actions, client)
>
> **Landed** on `claude/m3-world` (one draft PR; it is over 400 lines because the HUD move, the feeds and
> the views only make sense together): `net/world.ts` and both feeds with `bodies()`, `clues()`,
> `notebook()`, `dead()`, `kill`, `ability`, `hold`, `reportBody`, `bell` and the `killed`, `clueFound`,
> `phaseChange` events (`clock()` also returns `startTick`; `PlayerSnap` gains the roster `alive`);
> `World` with the one prompt (`data-testid="prompt"`), E, Q/R/F, N and the touch Use and Act discs, the
> 2 s collect ring, `BodyView`, `ClueView`, `PropView`, the Blood pass, `Lighting`, ghost mode, the grace
> toasts and the Night falls toast, `NotebookPanel` (+ the `NotebookSheet` that opens it over the world),
> `AudioBus`, and the HUD on the theme (`.wdi-hud`, `.wdi-log`, `.wdi-toast`, `.wdi-edge-cue`,
> `.wdi-stick`, `.wdi-touch-*`; the `wdi-world-*` namespace is gone). `InputController` gained `bind`,
> `unbindAll` and `setSink`. Unit tests for the mock verbs and the pure view helpers; `world.spec.ts`
> keeps the door flow (now polling the prompt instead of fixed sleeps, and asserting no page errors) and
> adds kill -> body -> collect -> one Notebook entry, the night mask and the ghost. DECISIONS A34.
>
> **For L (server).** The client breaks a tie between a body and a clue in reach in favour of the body
> ("Report"), so Footprints must not sit on the victim's own tile or the clue cannot be collected; the
> mock puts them one tile along the trail. `NotebookEntry.sceneId` is read as an index into `SCENE_IDS`.
> A hold ends client-side without a message when the player moves or leaves reach, and `on: false` is sent
> only for a release. `noise` kinds are matched loosely: anything containing "scream" is the scream
> (magenta ring, log line, edge cue, sound), `doorMuffled` is the muffled door, the rest a creaking door.
>
> **For M and the orchestrator.** `World` hides its HUD, the prompt, the night mask and the touch cluster on
> `SLEEP`, closes the Notebook sheet and releases its keys, and restores them on `WAKE`; it never starts a
> scene. The mock's `resume()` re-emits `sceneEnter` for the current scene; it emits `meetingRequest` for
> the report and the bell and nothing from the meeting. The mock reads `?phase=day|dusk|night`,
> `?bots=still` and `?ghost=1` (documented in A34); the `?fps=1` readout now also prints `at x,y`,
> `bodies n` and `clues n`, which the e2e and the bots can read. Importing the theme CSS from `Hud.ts` is
> enough for the fonts; the theme's `.wdi-hud__*` groups anchor with `inherit`, which ignores the
> safe-area padding, so `view/hud.css` sets the offsets itself (M may fix the theme and drop that block).
> `NotebookPanel` (`new NotebookPanel(parent, feed)`, `update()`, `destroy()`) takes the same `WorldFeed`
> the Meeting gets from the router.
>
> **Not done.** Toast and prompt ids from `docs/UI.md` 14 (it did not exist; the GDD 2 lines are used,
> with the bell hint reading "E at the bell" as briefed, while GDD 2 step 5 still says "B", which is Q's
> wording to fix). The real `props`, `vfx` and audio files are P's and Q's: until then props draw as
> labelled greybox blocks and the game is silent. Hold abilities (`inspect`, `dragBody`, `autopsy`) and
> the passive rows are M4. The night mask is a DOM vignette with one soft edge; line-of-sight shadows are
> not attempted. Not run: a real-server kill (L's server was not on the base), so the real feed's
> `bodies()`/`clues()`/`notebook()` reads are covered by types and review only.
> ### Round 3 log: M
>
> **Landed** (`claude/m3-meeting`): `NetworkService.room` (getter and `room` bus event) with `sceneEnter` removed
> from its message list; the router attaches `ColyseusWorldFeed` and the new `ColyseusMeetingFeed` from the
> room with no cast and no interval, re-emits the feed's `sceneEnter` on `net.bus`, and owns every start of
> `World`, `Meeting`, `GameOver` and the return to `Lobby` (ARCHITECTURE 5.9); the theme on Landing, Lobby and
> the role card with every `data-testid` kept (`ui/styles.css` is page chrome plus five layout classes); the
> `Meeting` and `GameOver` scenes and screens with the frozen test ids (`meeting`, `meeting-reason`,
> `portrait-<id>`, `vote-skip`, `vote-count-<id>`, `stamp`, `reveal-role`, `chat-log`, `chat-input`,
> `gameover`, `gameover-winner`, `gameover-role-<id>`; extras `voted-<id>`, `meeting-clock`,
> `gameover-summary`, `gameover-countdown`); the mock meeting (`net/mock/meetingMock.ts`,
> `MockNetwork.openMeeting`) and `e2e/meeting.spec.ts` (body: vote, early end, stamp, game over, lobby; bell:
> nobody ejected, back to the village). DECISIONS A33.
>
> **For the integration**
> - `World` must hide its DOM on SLEEP (N's side of the seam): until it does, the HUD chip and clock sit on
>   top of the meeting.
> - Notebook tab: `meetingScene.tabs?.addTab('notebook', 'Notebook', (panel) => new NotebookPanel(panel, worldFeed))`
>   (`Meeting.tabs` is the screen; the panel needs `update()` and `destroy()`).
> - The mock world should emit `meetingRequest` itself and implement `resume()`; until it does, `MockNetwork`
>   re-emits the same `sceneEnter` as the stand-in, and the e2e uses the mock-only hook
>   `window.__wdiMock.requestMeeting('body' | 'bell')`, which sends the same event.
> - N's `InputController` is kept in the registry for the whole page and a second mock match (after the mock
>   game over) would reuse it with the old feed; real rooms keep one feed, so only `?mock=1` is affected.
>   Chat keystrokes also reach it while `World` sleeps: it should ignore typing (`isTyping` in `ui/dom.ts`).
> - `phaseChange` and `gameOver` are registered on the room by both `NetworkService` and the meeting feed
>   (the SDK allows several handlers); only `sceneEnter` had to be single.
>
> **Not done**: the `stamp` sound (no `AudioBus` or audio manifest at the base); a real-server meeting e2e
> (O's `match.spec.ts` covers it after the merges); the ghost channel form is exercised by unit-level reading
> only, since the mock has no ghost; the Report tab is a short facts list until the copy deck (UI.md 14)
> lands, and all meeting copy lives in `ui/meetingText.ts` so the deck replaces it in one file.
> ### Round 3 log: O (Bots, match e2e, soak)
>
> - **Landed.** `tools/bots/walk.ts` is now the one bot brain: `walk`, `vote` (`skip`, `leader`, `random` or a player name, cast as soon as a meeting opens and repeated until the server records it), `report` (steps toward a body it sees, reports once per body, a Killer never reports) and `killer` (hunts the nearest player and strikes in reach past the cooldown when its own card holds `kill`). `swarm.ts` keeps `code`, `count`, `url`, `ready` and today's behaviour (stands still, votes Skip) so `party.spec.ts` is unchanged. `soak.ts` plays matches back to back through `debug.deal` (rotating Killer) and `lobby.start` from the leader bot, and additionally fails on a protocol error beyond refusals, or on a 5-minute-plus run with no kill or no meeting. `tools/grid/test/reach.test.ts` covers the widow cottage, the forest and the cave entry (they pass). ARCHITECTURE 5.12, ROADMAP 7.5 and DECISIONS A35 updated. `playwright.config.ts` starts the server with `WDI_DEBUG=1`.
> - **`match.spec.ts` is written against the contracts but skipped.** It runs only with `WDI_E2E_MATCH=1` (5-seat Village win with a lobby return, and 4-seat Cabal win). It could not be run here: `debug.deal`, `debug.clock`, the kill, report, meeting and game-over screens do not exist on the base branch. The orchestrator should run `WDI_E2E_MATCH=1 CI=1 pnpm --filter @wdi/client test:e2e` at integration and expect to adjust timings and the exact `prompt` text ("Report") and `vote-count-*` text.
> - **Soak against the base branch.** A 30-second run passed plumbing (`debug.deal` is ignored without K, so no kill or meeting occurs); the full 30 minutes needs K and L merged. Run `pnpm --filter @wdi/server build && pnpm bots:soak`.
> - **Assumptions to check at integration.** The Killer's body id is `body_<playerId>` (L's brief); `Player.sceneId` indexes `Object.keys(scenes)`; a ghost's own `sceneId` may be frozen, so ghost bots skip the leak monitor; the spec's kill needs the host within about 1.1 tiles of the victim, found from the observer bot's public presence.
> ### Round 3 log: P (art)
>
> Done on `claude/m3-art` (PR #12). Blender runs headless here as the `bpy` 5.2.0 wheel with Mesa EGL
> (`tools/blender/README.md`); the calibration sheet re-renders byte-identical to the committed one.
> Higgsfield was not used, so every new asset is CC BY 4.0 hand-made art (DECISIONS A36).
>
> - **Villager masters** rebuilt by `build_villager.py` into git-ignored `assets/external/villager/`:
>   the GLB matches Session H's hash byte for byte, the `.blend` differs only by save-time data, and
>   a `die` render from the rebuilt `.blend` matches all 320 shipped `die` frames exactly. Hashes are in
>   `assets/source/MANIFEST.md`, now prettier-formatted with its `.prettierignore` line removed
>   (follow-up 5). Copy both files to ROSW `studio/assets/who-did-it/character/villager/` on the
>   owner's laptop; the studio note is still to be written by the studio pipeline.
> - **Real keys** in `apps/client/public/assets/manifest.json`: `clues` (all 21 keys, now real art at
>   `clues/`), `props` (`prop_bell`, `prop_pump`, `prop_noticeBoard`, `prop_kitChest`,
>   `prop_lanternPost_lit` / `_unlit`, base pivots), `vfx` with `anims_vfx` (`vfx_blood_pool` 8,
>   `vfx_blood_splat` 12, `vfx_vote_stamp` 10, `vfx_dust_step` 6; 12 fps, played once). Each is one
>   page. The body is the last `die` frame (no new key); review sheet
>   `assets/source/review/villager-body-contact.png`.
> - **Still placeholder** in the real manifest: the four `bld_*_ext` exteriors and the six `tiles_*`
>   sets. The placeholder manifest has no `props` or `vfx`, so `?art=placeholder` shows N's greybox
>   marks for them.
> - **For N**: props are placed at the tile centre and their frame pivot puts the base there;
>   footprints and the drag segment point screen-up, so rotate by `Clue.dir`; drag segments chain
>   top to bottom; the stamp's frames 0 and 5 run off the cell on purpose.
> - **Rebuild**: `python tools/blender/build_props.py -- --out build/render`, `python
>   tools/blender/build_vfx.py -- --out build/render`, then `pnpm --filter @wdi/sprites pack:static
>   ../../build/render/<atlas> ../../apps/client/public/assets/<atlas>` for `clues`, `props`, `vfx`; the
>   atlases rebuild byte-identical. The body sheet: a `batch_render.py --anims die` run, then
>   `pnpm --filter @wdi/sprites contact:body`.
> ### Round 3 log: Q
>
> **Landed** (PR #14, `claude/m3-playtest`): nine CC0 OGG Vorbis q5 files under
> `apps/client/public/assets/audio/`, one per key (`footstep`, `door_open`, `door_close`,
> `door_locked`, `pickup`, `scream`, `bell`, `stamp`, `ambient`). Seven are from Kenney's RPG Audio and
> Impact Sounds; the scream and the wind loop are from Freesound CC0. `audio/manifest.json` is
> `{version: 1, entries: [{key, url, gain}]}`, the art manifest's wrapper (A37), so N's `AudioBus`
> reads `entries`. `CREDITS.md` has one row per file. `docs/UI.md` 14 is the M3 copy deck: every line
> has an id, and values are placeholders. GDD 2 step 5 now has the E bell toast. `docs/PLAYTESTS/`
> holds the run sheet, the form, the scorecard, the notes template and the M2 stub. ROADMAP 7.5 has one
> paragraph pointing to the kit, and DECISIONS A37 records the choices.
>
> **Owner, before the first M3 playtest** (`docs/PLAYTESTS/README.md` 1): merge round 3; create the
> Railway Hobby service with `WDI_DEBUG` unset and check `/health`; set the Actions variable
> `VITE_SERVER_URL` to the Railway URL and re-run `pages`; set Pages source = GitHub Actions; confirm
> the build matches on both sides; do a solo smoke run the day before; build the Google Form from
> `FORM.md`; write the two bars at the top of `SCORECARD.md` before anyone plays.
>
> **Not done or left open:**
> - The Freesound pair are the site's HQ previews rather than the originals, because downloading
>   originals needs an account. They are CC0 either way; swap in the originals if a cleaner master is
>   ever wanted.
> - The sharp-attack SFX land below -16 LUFS, because the limiter allows at most 6 dB of gain
>   reduction. The manifest gains balance them; tune them by ear at the first session.
> - Four things outside Q's paths for the orchestrator:
>   - `docs/UI.md` 6 still uses "B at the bell calls a meeting" as its toast example.
>   - `docs/README.md` does not index `docs/PLAYTESTS/`.
>   - The Killer's `goal` in `roles.json` speaks of parity, while at 4-5 players the win is
>     `villageAtMostOne` (GDD 3.8).
>   - The match-log field names are described from K's brief; README 4 says the log line wins if they
>     differ.
>
> ## Integration log, round 3 (2026-10-16)
>
> All seven sessions finished their briefs inside half an hour and opened green draft PRs (#12 to #18),
> none of them asking for a missing contract. The orchestrator merged L, K, N, M, O, P, Q in that order
> (conflicts only in `docs/DECISIONS.md` and `docs/SESSIONS.md`, both appended by every session and kept
> as unions), ran lint, typecheck, the unit suites, the build and every Playwright flow, including O's
> real-server match test with `WDI_E2E_MATCH=1`: the kill -> body -> report -> meeting -> vote -> win
> loop ran end to end on the first merged tree, Village win and Cabal win. Fixes made at integration
> (DECISIONS A38):
>
> - Footprints spawn one tile along the trail from the kill tile, never on the body's tile, since the
>   client's prompt prefers the body there and the clue could not be collected (L's `Clues.ts`, test).
> - The meeting's Notebook tab mounts N's `NotebookPanel` on the world feed (M's `Meeting` scene).
> - L's report and bell tests return to a world phase beside the target after each accepted request,
>   because K's meeting now really opens on the first request and moves everyone to the square.
> - Wording: the Killer's card goal names the 4-5 player rule, the UI.md 6 toast example reads "E at
>   the bell", `docs/README.md` indexes `docs/PLAYTESTS/`.
>
> ### Follow-ups for round 4
>
> 1. **M3 exit (owner)**: Railway Hobby service, `VITE_SERVER_URL`, Pages source (Q's
>    `docs/PLAYTESTS/README.md` 1), then three 5-player sessions with the scorecard and the
>    fun-or-stop decision recorded in `docs/PLAYTESTS/`.
> 2. **M3b quick mode** and **M3c NPC fill** (ROADMAP), in that order, as the next build round.
> 3. **Copy deck adoption**: N's toasts and prompts and M's `ui/meetingText.ts` still carry the GDD 2
>    lines; replace them with the ids of `docs/UI.md` 14.
> 4. **Placeholder manifest**: `?art=placeholder` has no `props` or `vfx` entries (greybox marks show);
>    the four `bld_*_ext` exteriors and six `tiles_*` sets are still stand-ins in the real manifest.
> 5. **Client small**: `InputController` stays in the registry across a second `?mock=1` match and keeps
>    the old feed; the `stamp` sound at the reveal is not played yet (M has no `AudioBus`); the ghost
>    chat form is covered by unit reads only; `view/hud.css` sets HUD corner offsets because the theme's
>    `.wdi-hud__*` anchors ignore the safe area (fix in the theme, drop the block).
> 6. **Server small**: Kill does not require the Knife item (the role list decides); no ack for Bandage;
>    the missing-person roll-call, suspect sets, `meeting.board`, the anti-stall rules and the
>    wrong-ejection bonus are M4; in-play reconnection and the vanished body are M7.
> 7. **Soak**: run the full 30-minute `pnpm bots:soak` with the merged server (kills and meetings now
>    occur); O ran 30 s against the base only.
> 8. **Art masters**: copy the rebuilt `villager.blend` and `villager.glb` from `assets/external/villager/`
>    into the ROSW checkout (`studio/assets/who-did-it/character/villager/`); the two Freesound files
>    are HQ previews, swap in the originals if a cleaner master is wanted.
>
> ## Round 4 (started 2026-10-16, after round 3 landed at 2f829e2)
>
> Eight sessions build **M3b, quick mode** (One Night Ultimate Baguette, GDD 3.11, ARCHITECTURE 5.14,
> ROADMAP M3b) and **M3c, NPC fill** (GDD 3.12, ROADMAP M3c) in one round, plus the round-3 follow-ups 3
> to 7 above (the copy deck in code, the placeholder manifest, the client and server smalls, the
> 30-minute soak). Follow-ups 1 (the owner's M3 playtests) and 8 (the art masters on the owner's laptop)
> stay the owner's and run beside this round: the site and the server are live. Same rules as rounds 1
> to 3: draft PRs against `claude/zen-turing-m1jnw0`, under 400 lines where the work allows (split by
> step, each PR green), `pnpm lint && pnpm typecheck && pnpm test` clean before every push, pinned
> versions only, no model identifiers in committed files, `docs/GDD.md` changes in the same PR as a
> behaviour change, numbers only in `docs/GDD.md` and `packages/content/data`. Code and tooling run on
> Sonnet 5.5; art, content and design run on Opus 5.5. The decisions of this round are DECISIONS A39; a
> session never re-decides them.
>
> **Pre-seeded on the base branch** (the "Round 4 contract" commits, DECISIONS A39), so no two sessions
> add the same thing. Shared: the constants `LOFT_SCENE_ID`, `LOFT_SCENE_INDEX` (255),
> `ONUB_ACT_PREFIX`, `ONUB_SET_PLATE` and `NpcLevel` (`@wdi/shared/constants`); the schema `Prop.of`
> (the owner's seat id of a quick-mode plate, empty otherwise), `NightReveal {slot, of, roleId}` and
> `Private.nightReveal`, `Claim {from, roleId, targetId, sawRoleId}` with `MeetingState.claims` and
> `MeetingState.traces`, `Settings.npcDifficulty` and `Settings.npcSeats`; the protocol `lobby.settings
> {mode?, npcDifficulty?}`, `lobby.addNpc`, `lobby.removeNpc` (no payload: it removes the most recently
> added NPC seat, so it never tells a seat apart), `meeting.claim {roleId, targetId?, sawRoleId?}` (all
> 2/s, all routed to `PartyRoom.lobbyCommands` and drained by `runLobbyCommands`, `meeting.claim`
> already calling `handleClaim` in `sim/Meeting.ts`), the private `nightWake {windowRole, endsTick,
> spawn}`, `nightReveal {entries}` and `nightSleep`, `MeetingReason` `dawn`, `voteResult.outs`,
> `voteResult.roles` and `voteResult.abstained`, `gameOver.onub` (`OnubGameOver`: `dealt`, `final`,
> `center`, `swapLog`, `votes`, `outs`, `plates` (plate prop id -> seat id), `rowId`, `winnerIds`), the
> types `NightRevealEntry` and `SwapLogEntry` (`docs/PROTOCOL.md` regenerated); the rules module
> `packages/shared/src/rules/onub.ts` with the signatures `dealOnub`, `nightScript`, `applyNightAct`,
> `resolveDawn` (`DawnOutcome {tally, outs, abstained}`) and `onubWinners` (bodies throw until R fills
> them) and `rules/npc.ts` with `pickNpcNames` (implemented, tested), both exported by `rules/index.ts`.
> Content: `packages/content/data/names.json` (40 names, schema `NamesFile`, validated: lobby-legal,
> unique, no role token, at least `players.max`) exported as `names` from the server-only entry
> `@wdi/content/server` (`packages/content/src/{names,server}.ts`, tested in
> `packages/content/test/names.test.ts`; an eslint rule forbids that entry under `apps/client`, so the
> pool never ships in the client bundle); the `balance.json` rows `npc.wander {stepMinS, stepMaxS,
> portalSteerChance, portalChance}` and `npc.vote {delayMinS, delayMaxS}` with their GDD 3.12 line;
> `balance.onub.json` `targetLengthMin {min, max}` with its GDD 3.11 line; the `storm` winners row
> reworded to the seat holding the Hireling loaf (GDD 3.11). Server: the stages `runNpcs(room)`
> (`sim/Npc.ts`, after `syncRoster`, before `applyInputs`) and `runConductor(room)` (`sim/Conductor.ts`,
> after `runPortals`, before the views reconcile), both empty, with `isNpcSeat(room, id)` and
> `resetNpcsForLobby(room)` beside the first; `sim/Onub.ts` with `isOnub(room)`, `startOnubMatch(room,
> ids, rng)` (called by `startMatch` before the main deal, with `ids = [...room.state.players.keys()]`)
> and `beginOnubPlay(room)` (called first by `beginPlay`), both returning false outside quick mode,
> `handleOnubAbility` (every `act.ability` whose id starts with `onub.` reaches it from
> `handleAbility`), `plateOf(room, seatId)` and `onubNpcPlan(room, seatId)` (null until R fills them)
> and `resetOnubForLobby`; the loft guards: `isLoft(idx)` in `sim/World.ts`, `applyInputs` and
> `moveAndCollide` skipping loft players, `runPortals`, `livingActor` (every `act.*` verb) and
> `holdProblem` refusing a loft player 425, `reconcileViews` giving a loft viewer no scene and no
> presence and never sharing a loft player, `PlayerSim.sceneHidden` honoured by `enterScene` and reset
> for the lobby; the quick-mode seal: `runPortals` refuses every portal 425 (nobody leaves the bakery,
> GDD 3.11) and `placeNewPlayers` places nobody, so no quick-mode seat ever stands in the overworld;
> `MeetingRequest.reason: MeetingReason` (`sim/RoomSim.ts`); `resetToLobby` clearing `nightReveal`,
> `claims`, `traces` and every scene's `props`, then calling `resetOnubForLobby` and
> `resetNpcsForLobby`; `endMatch` writing `players[].isNpc` from `isNpcSeat`; `MatchRecord.winner`
> widened with `mode` and `players[].isNpc`. Client: the `?mode=onub` flag (`flags/index.ts`),
> `REG_AUDIO` in `scenes/registry.ts`, the copy modules
> `apps/client/src/ui/copy/{index,world,meeting,lobby}.ts` (one per client session, `fill()` for
> placeholders), an empty `Loft` scene (`scenes/Loft.ts`, T's) registered in `main.ts` after `World`,
> the `AUDIO_KEYS` `storm`, `creak`, `stamp` and `loaf_crack` (silent until `audio/manifest.json` lists
> them), and `meetingRequest.reason` accepting `dawn` in `net/world.ts` and `MockMeetingRequest`.
>
> **Nobody edits** `packages/shared/src/{schema,protocol,rules}/index.ts`,
> `packages/shared/src/index.ts`, `packages/shared/src/constants.ts`, `packages/content/src/**` (the
> schemas, `index.ts`, `names.ts`, `server.ts`, `validate.ts`),
> `apps/server/src/sim/{Actions,Bodies,Clues,Commands,Death,Hold,Kill,Movement,Noise,PortalQueue,Portals,RoomSim,Step,Visibility,World,constants}.ts`,
> `apps/server/test/{simHelpers,killHelpers}.ts`, `eslint.config.js`, `balance.json`,
> `balance.onub.json` or `roles.onub.json`: a session that needs another contract writes it in its PR
> description and carries on with a local stand-in; the orchestrator adds it to the base branch. Every
> `*Tick` field is in ticks (`secondsToTicks`); content paths are the whole path:
> `onubBalance.timers.duskS`, `onubBalance.acts[id].holdS`, `onubBalance.windows.find((w) => w.role ===
> role)` (an array), `onubBalance.vote.minVotesToTurnOut`, `onubBalance.targetLengthMin.min`,
> `onubFor(n).discussionS`, `balance.npc.difficulty[level]`, `balance.npc.wander.portalSteerChance`,
> `abilities.abilities.kill.rangeTiles`, `names.pool` (`@wdi/content/server`, the server only).
>
> | Session | Model | Track | Branch | Owns |
> |---|---|---|---|---|
> | **R. Quick mode, server** | Sonnet 5.5 | Code | `claude/m3b-server` | `apps/server/src/sim/{Conductor,Onub,Phases,Meeting,Win,Flow,Chat}.ts`, `apps/server/src/services/MatchLog.ts`, `packages/shared/src/rules/onub.ts` and `packages/shared/test/onub*.test.ts`, new `apps/server/test/onubHelpers.ts` and `apps/server/test/onub*.test.ts`, `apps/server/test/{flowHelpers.ts,flow,meeting,chat,win,visibility}.test.ts` (edits only where the mode branch needs them), `docs/GDD.md` 3.11 (one sentence per behaviour the PR changes, marked "(M3b)"), `docs/ARCHITECTURE.md` 5.14 |
> | **S. NPC fill, server** | Sonnet 5.5 | Code | `claude/m3c-npc` | `apps/server/src/sim/Npc.ts`, new `apps/server/src/sim/npc/**`, `apps/server/src/rooms/PartyRoom.ts`, `apps/server/src/rooms/handlers/{lobby,debug,movement}.ts`, `packages/shared/src/rules/npc.ts` and `packages/shared/test/npc.test.ts`, new `apps/server/test/npcHelpers.ts` and `apps/server/test/npc*.test.ts`, `apps/server/test/{lobby,party,sim-movement,sim-portal,throttle}.test.ts`, `docs/GDD.md` 3.12 (marked "(M3c)"), `docs/ARCHITECTURE.md` 5.3 (the start flow) and 5.4 (the NPC line) |
> | **T. Quick mode, client world** | Sonnet 5.5 | Code | `claude/m3b-world` | `apps/client/src/scenes/{World,RoleReveal,Loft,registry}.ts`, `apps/client/src/view/**` (except `hud.css`), `apps/client/src/input/**`, `apps/client/src/flags/**`, `apps/client/src/net/{world,worldColyseus,worldRouter}.ts` and `worldRouter.test.ts`, `apps/client/src/net/mock/worldMock.ts` and its test, `apps/client/src/ui/copy/world.ts`, `apps/client/e2e/world.spec.ts`, `docs/SPRITES.md` 5 (loading notes only) |
> | **U. Quick mode, client meeting and end** | Sonnet 5.5 | Code | `claude/m3b-meeting` | `apps/client/src/scenes/{Meeting,GameOver}.ts`, `apps/client/src/ui/{Meeting,GameOver,meetingText,portrait,RoleCard}.ts` and their tests, `apps/client/src/net/{meeting,meetingColyseus}.ts`, `apps/client/src/net/mock/meetingMock.ts` and its test, `apps/client/src/ui/copy/meeting.ts`, `apps/client/src/ui/theme/components.css` (new rules appended at the end under a "Round 4 (U
>
> [truncated: 355760 more characters]
>

### Source file: docs/ROADMAP.md

> # Production Plan
>
> > Generated from `docs/MASTER_PLAN.md` (v0.1, 2026-10-10). Milestones, parallel tracks, placeholder strategy, risks, playtests, workflow and the day-by-day schedule for M0-M2.
>
> ## 7. Production plan
>
> Effort is in focused solo-dev days with AI coding sessions; code uses placeholders until M6. The order is M0 -> M1 -> M2 -> M3 (first playable, "fun or stop") -> M3b (quick mode) -> M3c (NPC fill) -> M5a (Living World) and ONUB v2 (round 5) -> M5b (resources, mobs, quests; round 6) -> M4 -> M5 -> M6 -> M7; the owner's round-5 brief (2026-10-17) pulled the living world ahead of deduction depth. M3b can be pulled ahead of M3 if the owner wants the quick mode as the first playtest: it needs no kills, clues or ghosts (see DECISIONS.md, open questions).
>
> ### 7.0 Status (2026-11-19)
>
> Evidence is the merge history of the base branch `claude/zen-turing-m1jnw0` and the integration logs in `docs/SESSIONS.md`. No session of the milestones' playtest column is written up in `docs/PLAYTESTS/` yet (only the M2 stub); the owner's own playtests of the round-8 build are recorded in DECISIONS A168, A196 and A222.
>
> | Milestone | Status |
> |---|---|
> | M0, M1, M2 | Built and merged in rounds 1 and 2 (SESSIONS integration logs of 2026-10-10 and 2026-10-15). |
> | M3, M3c | Built and merged in rounds 3 and 4 (integration logs of 2026-10-16 and 2026-10-17). The fun-or-stop scorecard is not filed. |
> | M3b, ONUB v2 | Built in rounds 4 and 5, then removed in round 7 (DECISIONS A115). |
> | M5a | Built and merged in round 5 (landed at `a60d855`). |
> | M5b, M5c, M5d | Built and merged in round 6 (#81, `11168d1`). |
> | R7, R7b | Built and merged in round 7 (#128, `6e5a91b`). |
> | R8 | Built and merged in round 8 (SESSIONS Round 8). |
> | R9 | Design merged (#313, `72f1b69`). |
> | R10 | In part. Paused on 2026-10-30; the pull requests open at the pause merged between 2026-11-07 and 2026-11-12, and story mode's part 2 merged with #538. Still to build: `docs/round10/part2.md`, "Each session's remaining steps" (B6b, B6c, B7, W1a2 to W8, C6, C7, the final sweep 10Z and the rest). |
> | R11 | Re-scoped by A256 (its gameplay items move to round 10), then re-planned by A616 for A615's sprite world: the plan is `docs/round11/round11-plan-v2.md` (approved 2026-11-19, #551), which replaces `round11-plan.md` (#374, A236). Not started. Beside it, HollowMere was built in 3D from the owner's Meshy models (#539) and the V2 walk-through `apps/walk` began (#540, #541, #543; A610 to A614). |
> | R12 | Not started. |
> | M4, M5, M6, M7 | Not closed as milestones. Much of their scope landed in other rounds (round 10's evidence verbs, cover-up and hiding, DECISIONS A239, A555, A576, A578; M5b's wolves and lanterns; the round-5 and round-8 art; the Playwright suite), but no exit check has been run against these rows. |
>
> ### 7.1 Milestones
>
> | M | Goal | Deliverables | Definition of done | Days | Playtest |
> |---|---|---|---|---|---|
> | **M0 Scaffold** | Monorepo, two workflows, hello-world on Pages and Render Free | pnpm workspaces, tsconfig / eslint / prettier / vitest; `ci.yml`, `pages.yml`; Render Free web service from the GitHub repo (Railway Hobby at the M3 exit); `/health`; `BUILD_VERSION` handshake; `metrics.json`, `palette.json`, `constants.ts`; `.gitattributes`; `docs/` seeded from this plan plus `SPRITES.md` conventions; Day-2 spike proving custom 5-char `roomId` + `joinById`, one `.view()` field hidden from other clients, and `setFixedTimestep`; calibration render of the checker cube | Pages URL shows a Phaser canvas connected to the hosted server printing `{ok, build}`; CI green; spike results recorded in `DECISIONS.md` | 3 | Smoke |
> | **M1 Lobby + role cards** | Create / Join by code, Start, private role card | `PartyRoom` create / join / start; `CodeRegistry`; generic join error; phase machine lobby -> roleReveal; `assignRoles` + `dealTraits` with property tests; `Private` view privacy; DOM Landing, Lobby, RoleCard (CSS flip, 12 s, Ready, Tab); deep link `#/join/CODE`; `swarm.ts` join-only bots. Content: `roles.json`, `traits.json`, `items.json` card text | Two browsers create / join; 11th refused; server test proves other players' `priv` is absent on the wire; card read in 20 s by a first-time tester | 4 | 2 people, one on a phone |
> | **M2 Movement + one house** | Authoritative movement, scene-scoped sync, portal into a 2-room interior | 20 Hz fixed step with the `step()` order above; one input per tick; command queue; swept AABB; 150 ms lerp; `Visibility.ts` scene-scoped `presence` and `scenes` views; synchronous `Portals.ts` with transit; `World` restart; ASCII grid exporter; 40x30 overworld greybox + tavern bar + back room; keyboard + one touch stick + 3 buttons; HUD chip + timer | 2 humans + 6 bots walk, enter and leave both rooms; test proves outsiders receive no interior data and no cross-scene positions; 60 fps desktop, >= 45 fps on a 2022 mid-range Android; 30 min bot soak clean | 6 | 2-4 people: movement feel, phone controls |
> | **M3 First playable: kill -> body -> vote** | The deduction loop, minimal; at exit, move the server to Railway Hobby before friends play | Kill (CD, range slack, grace, busy), body entity, Blood tint 60 s, Thread + Footprints with hold-E collect, Notebook, Detective auto-Verified; report body / square bell; Meeting scene with portraits, chat, secret vote, early end, eject + reveal; `resolveVotes` plurality + Skip; `checkWin` (all Killers out, parity, practice rule); ghosts + ghost chat; phases grace / day / dusk / night; widow cottage (2 rooms), forest, cave entry greybox; roles Killer / Detective / Doctor (Bandage only) / Townsfolk | Three 5-player matches in a row end in a Village or Cabal win in 10-18 min; vote accuracy and "would play again" logged; **fun-or-stop decision recorded** | 6 | 4-5 humans, two sessions |
> | **M3b Quick mode** (removed in round 7, DECISIONS A115) | One Night Ultimate Baguette playable end to end | `Settings.mode`; bakery greybox with plates, ledge and ledger; dusk plate-setting; dark loft view (static bedrolls, client-side pulses) and night Conductor with per-window wake and validated acts; `loft` pseudo-scene; the pure `onub.ts` rules with property tests; Meeting reuse with no Skip and claim chips; `resolveDawn` and the winner table; the reveal with the swap log. Content: `roles.onub.json`, `balance.onub.json`, bakery scene JSON | Three 6-player matches in a row finish in 5-7 min; a sleeper's client provably receives no presence during the night; the Hireling, Sin-Eater, Cutpurse, Busybody, Sot and Lamplighter acts each verified in a server test; players name their final role correctly at the reveal in at least half the matches | 4 | 4-6 humans, two sessions; compare "would play again" against M3 |
> | **M3c NPC fill** | Play below 4 humans with server-side NPC villagers (GDD 3.12) | NPC seats as ordinary `players` with `isNpc` in room memory only and names from an NPC name pool in `@wdi/content`; lobby auto-fill to 4 and "Add NPC" up to 10; `Settings.npcDifficulty` (Easy / Normal / Hard, enabled at 4+ NPC seats); scripted wander / task / hide / report / vote behaviours inside `step()`; Killer and Accomplice NPC policies; quick-mode NPC sleepers resolved by the Conductor; `balance.json` `npc` difficulty rows | 1 human + 3 NPCs completes a main match and a quick-mode match; the NPC Killer wins at least 1 of 5 scripted matches at Normal; no field a client receives distinguishes an NPC seat; p95 tick stays under 15 ms with 9 NPCs | 4 | 1-3 humans, two sessions |
> | **M5a Living World** (round 5, 2026-10-17) | The owner's round-5 brief: a world worth walking, a deck worth reading | Isometric client (projection client-only, server cartesian) with a lighting layer; map manifests and the lobby map choice; Hollowmere's `forest_deep` and `cave_gallery`; the new **Blackpine** map (logging camp, woods, tin mine); every map has a forest and a cave; NPC routines (work, idle, stroll) in place of the endless wander; the n+2 public deck with professions, public role looks, covers with the undealt hint, Impersonate; the Knife after dark only, Hunger and Final Night; Vicar, Watchman, Herbalist, Gamekeeper; avatars under opaque handles, `Player.sceneId` private; isometric environment and character art, one character per look id. Content: `looks.json`, `maps/*.json`, `routines.json`, new scenes, `roles.json` decks | A 6-player match on each map ends (Final Night at the latest) with every role's character on screen and a cover found or not by evidence; server tests prove no field tells a cover, an impersonation or an NPC seat apart; NPCs stand still at least 40% of a day; 45 fps on the test Android in the isometric view; 30 min soak clean | 1 round (13 sessions). Sessions: 5A-5M, docs/SESSIONS.md Round 5 | 5-6 humans on each map |
> | **ONUB v2** (round 5, 2026-10-17; removed in round 7, DECISIONS A115) | The owner's One Night Ultimate Baguette spec end to end | Two cards per seat (Role, Location) and a Pantry of 3 + 3; Evening Prep over the four station rooms with one mini-game each and the ingredient and sabotage cards; the crime-scene board (thermostat, under-mix flag, net weight, ruin, proofing perk); 13 night windows played over the owner's role-scene art with a card table and the Iron Cloche; the 300 s Morning Rush with structured claims; CRUST with the Pantry vote and Restaurant Shutdown; the winners table; the act timeline at game over; the deck editor. Content: `roles.onub.json`, `balance.onub.json` v2 | Three 6-player matches in a row finish in 8-10 min (A50); a sleeper's client provably receives no wake, reveal or presence; every night act verified in a server test; the quick-mode soak passes with the ruin rate reported per party size | 1 round (5 of the 13 sessions). Sessions: 5A-5M, docs/SESSIONS.md Round 5 | 4-8 humans, two sessions |
> | **M5b Resources, mobs and quests** (round 6, 2026-10-22) | The rest of the owner's round-5 brief, on M5a's maps | Resource nodes and gathering as a hold; a 5-slot inventory; recipes and tool crafting at stations (Lantern, Crowbar, Lockpicks, Snare, Torch, Spade); random mobs (wolves, boars, bats, rats) from the scenes' spawners with a server FSM on keyed streams; server-side dark visibility (radius and line of sight, lanterns both ways); fetch quests from NPC givers; main-mode mini-games at task stations with the fake Cabal list. Content: `resources.json`, `recipes.json`, `mobs.json`, `quests.json`, `minigames.json`, the scenes' `nodes`, `spawners`, `givers` | A 6-player match on each map in which a lantern is crafted, a quest turned in, a wolf kill reported as `wolf` and a station mini-game played and checked by the server (main-mode task assignment, which would fill `Private.tasks` and the task bar, did not land in round 6 and moves to M4: the 6E/6H gap, DECISIONS A97); server tests prove a living seat in a dark scene receives no avatar beyond its sight and that a fake task never moves the task bar; 10 NPC seats plus 3 wolves at p95 tick < 15 ms; `pnpm auto -- --matches 50` clean on both maps | 1 round (6 of the 15 sessions). Sessions: 6E-6I, 6M, docs/SESSIONS.md Round 6 | 5-6 humans on each map: is gathering worth the walk; do mobs read as danger or noise |
> | **M5c Cinematics and music** (round 6) | The owner's round-6 brief: opening and death cutscenes, music playlists, a start-screen trailer, loading and transition animations | Data-driven in-engine cutscenes (`cutscenes/*.json`, captions as copy ids, the HollowMere opening lengthens grace by `phases.openingS`, a `killed` carries its cutscene id); a loading screen with tips; fade, iris and wipe transitions on the router's scene starts; a muted landing trailer loop (`landing_loop.webm`, <= 2 MB); music playlists per map and phase class, lazy-loaded under their own budget (<= 12 MB, <= 4 MB per map), with a settings panel; the owner's tracks, the stingers and ambiences fetched by id from the ROSW sound library, and the `video-shot` videos mastered and credited. Content: `cutscenes/`, `music.json`, `balance.phases.openingS`, `balance.ui.transitionS` | A 6-player HollowMere match shows the opening, a death cutscene, music that follows the phases, the loading screen and every transition; Skip works; reduce-motion removes every pan and transition; `media.test.ts` passes with the real tracks and the trailer; first load stays under 12 MB | 1 round (4 sessions: 6J, 6K, 6L, 6N) | 4-6 humans: does the opening overstay its welcome; does the music tell the phase |
> | **M5d Admin auto-mode** (round 6) | The owner's round-6 brief: an owner-only admin section that runs a match with every seat an NPC, on several screens at 10x, to find bugs | A sim clock (1x, 2x, 5x, 10x, pause, step) in `PartyRoom`'s fixed step, a `party` room never leaving 1x; an all-NPC match with NPC prey and no leader; a headless harness and `pnpm auto` (deterministic from seed words, one line per match, exit 1 on an invariant failure); an event bus and an invariant registry (privacy, stuck NPCs, phase overrun, match end, clue drops); GitHub login on the Colyseus server (allowlisted logins, signed token, `WDI_ADMIN=1`) and an `admin` room that joins without a seat; the admin page at `#/admin` with up to six scene viewports, controls, a seat inspector and a log pane | The admin page refuses without the GitHub login on Railway and runs a 10-seat match at 10x with six viewports; `pnpm auto -- --matches 50` clean on both maps, both modes and every difficulty; two runs with the same seeds hash the same; `party.test.ts` still proves no `admin` room and no debug handlers without env; the weekly soak gains an `auto` leg | 1 round (4 sessions: 6A, 6B, 6C, 6D) | The owner alone, watching a 10x match; bots as load |
> | **R7 Vendettas and memorials** (round 7, 2026-10-23) | The Bible's Book I.3 and I.6 on HollowMere | The four killer vendettas (conversion, sabotage, heist, contract) as triggers and consequences on the round-6 event bus; the Daily Train as the master clock with its station; the Vicar's martyrdom memorial with its video and the Ascended Vicar; vendetta invariants. Content: `vendettas.json`, `balance.json` `vendettas` and `train` (the Port-au-Levain opening moves to R8 with its map, DECISIONS A105). Also this round, by the owner's decisions of 2026-10-23: the quick mode is removed (A115, session 7J, `docs/round7/quick-mode-removal.md`), and Crumb's Ovens gains four rooms from the owner's station pictures (A116, session 7K) | `pnpm auto -- --matches 50` on HollowMere clean with the vendetta invariants on; a 6-player match in which the Train arrives, a contract is accepted and the memorial plays; nothing public carries a vendetta kind | 1 round (7H, 7I; `docs/round7/vendettas.md`) | 5-6 humans: does a vendetta read as pressure or as noise |
> | **R7b Re-skin, parties and profiles** (round 7, 2026-10-23) | The owner's two Claude Design mockups and the three answers of DECISIONS A103 | Every screen in the mockups' night palette, pixel type and frosted glass (`docs/round7/ui-reskin.md`); open and private parties, the party list, invites, the device profile, friends and Quit (`parties.md`); the three intro tracks played whole over longer cinematic openings that visit the rooms and the caves (`map-intros.md`) | The opt-in e2e suites and both screenshot sets green; no id, rule, number or wire changed by a re-skin PR; an invited profile sees a private party and a stranger does not; each opening runs its track's length once | 1 round (7A to 7G; `docs/round7/`) | The owner by eye on each screen; 5-6 humans joining through the list |
> | **R8 Bodies, coin, motion and art** (round 8, 2026-10-23) | The owner's round-8 requests and answers (DECISIONS A134) and the Bible's Book IV on today's maps | Health, stamina and the effects with their signs and cures, fists for every card, the knockout, inspect and the relations table (GDD 3.22); the Scrip purse, wages, shops, the bank, rent and quota, Indebted, Faith, rumours and the black market, HQ tiers (GDD 3.23); needs and moods, ambient townsfolk and mugging (GDD 3.24); every new animation (characters, the wolf's attack, creatures, resource breaks, VFX, transport, the interface's motion); characters redesigned and drawn larger; the HD art style; every room of both maps re-dressed under placement tests. Content: `effects.json`, `relations.json`, `economy.json` | `pnpm auto -- --matches 50` clean with `bodyBounds`, `scripConserved` and `figureNotSeat`; the owner signs off the character scale, the looks and HD by eye; both screenshot sets | 1 round | Owner, by eye |
> | **R9 World mode, the design** (round 9, 2026-10-24; DECISIONS A222) | The owner's world-mode brief (`docs/round9/owner-brief.md`) | Design only: world mode, the full-screen phases, the logic table, the refusal reasons, the living world, emergent play, the GDD map and the round-10 build plan (`docs/round9/`), the owner's answers and follow-ups; the admin Studio (`docs/round9/admin-studio.md`) | The owner approves the docs; no rule changes in code | 1 round | Done |
> | **R10 World mode, the build** (round 10, 2026-10-29; DECISIONS A223, A224) | `docs/round9/round10-plan.md` with `followup-4.md` | Refusal reasons, the 480 s day, weaker mobs, sleeping, the logic table and tools on piles, the slotted inventory and the crafting grid (the playtest slice); the law, petitions, the jail and the Tribunal in place of voting; the train's returns, Owing the line, the Hitman, Paint The Town Red; never-idle NPC seats, depletion, dishes, the lock-pick, armour; achievements and story mode. Content: `interactions.json`, `laws.json`, `achievements.json`, `story.json` | Every step's tests and `pnpm auto` at 50 green; the owner's playtest after A13; every `gdd-map.md` row landed | 1 round (`docs/round10/`) | Owner's playtest after A13 |
> | **R11 The sprite world** (re-planned by A616, 2026-11-19; re-scoped by A256, 2026-10-30; was "Evolutions, law, Port-au-Levain", R9 until A224, R8 until A135) | `docs/round11/round11-plan-v2.md` (approved, A616; it replaces A236's `round11-plan.md`) | The build of A615's sprite world: S0 (Three.js in the client), H1, the renderer R1 to R6 behind a flag, figure sprites, props and tiles, the look gate, the map, the budget, the cut-over and the sweep. The gameplay this row once held moved to round 10 by A256: role evolutions are `docs/round10/scope.md` I32, the law's pending pieces I44 to I47 (forced labour, the heresy trial, trespass, theft from an owned shelf) and the Company Clerk I30. The Port-au-Levain campaign map is in no round's plan yet (owner to place) | Approved, not started (7.0) | 1 round | A236, A256, A616 |
> | **R12 World events, propagation, BlackPine industry** (was R10 until A224, R9 until A135; story mode moved to R10) | The Bible's Book III, V and VI | The NPC propagation matrix (gossip, letters, emotional states, predators, enforcers) from `events.json` on the event bus; BlackPine's soot, steam network, roll call (the tally rack is built in R8); the admin matrix inspector. Content: `events.json` | Planned after round 10 | 1 round | Decided then |
> | **M4 Deduction depth** | Everything that makes the vote smarter, one feature per playtest | Four PR-sized sub-goals: (a) clues 2-of-3 + prints, Lens charges, Dust / Compare, Autopsy, Rag, Bucket + Wet Bucket, drag smear, Corroborated; (b) Case Board with auto-Verified, Present 1, summary rows, suspect sets, structured accusations; (c) Butler Lock / Ledger, Child Witness, Accomplice Plant + inheritance, Drifter, Bandage knockback rules; (d) tasks (6 incl. 1 co-op, fetched tools, fake Cabal list, bar), Hunger, Final Night vote, missing-person roll-call, no-eject plurality rule. Content: `clues.json`, `abilities.json`, `tasks.json`, `balance.json` | Every V1 mechanic in 3.10 toggled on and tested in at least one session; suspect sets correct in server tests; vote accuracy tracked per feature | 12 | 5-6 humans after each sub-goal |
> | **M5 World, stealth, items, PvE** | All V1 scenes and the stealth layer | 14 V1 scenes as grids with profiles and boarded doors; door state machine, keys, Skeleton Key, Crowbar; hiding + body spots, Burst Out, Check evidence; 5-slot inventory; noise with portal halving; sneak / run; lanterns and candles; quick-chat + pings; wolves, fence task, Wounded; 10-player rules and snowball guard; clue GC and tick budget gate | Full loop square -> house -> forest -> cave -> square with locks and hiding; 10 bots + 3 wolves at p95 tick < 15 ms; 8-player match with wolves reports "wolf" kills correctly | 11 | 6-8 humans: stealth and night |
> | **M6 Art pass** | Replace placeholders with Blender renders | `batch_render.py`, `pack.ts`, `gen-anims.ts`, per-frame pivots; overlays and tint; Tiled maps replacing grids with decor and occluder layers; building and interior renders; UI from Illustrator; VFX; CREDITS complete | Every placeholder key resolved by a shipped atlas; first load <= 12 MB; <= 6 pages resident; 45 fps on the test Android; contact sheet reviewed | 10 code + Tier B art hours | 4-6 humans: trait and Blood readability at night |
> | **M7 Polish + beta** | Reconnection everywhere, mobile, balance, public link | 60 s mid-match reconnection with notebook resync; "vanished" bodies; leader handoff, kick, transfer; profanity; rate limits; UI scale 200%, colour-blind check, reduce-motion; tutorial toasts; telemetry JSON lines; balance pass from data; Playwright e2e; README | Three consecutive 8-10 player public sessions without a room crash; reconnect success >= 95%; "would play again" >= 7/10 | 8 | 10-person stress, two public betas |
>
> Total about 68 focused code days (17 weeks at 4 days per week, M3b and M3c included) with the first roles-on playtest at day 19 and Tier A art (60 h) in parallel from day 1; Tier B art (119 h) starts only after the M3 verdict.
>
> ### 7.2 Parallel tracks
>
> | Track | Starts | Blocks on | Day-1 items |
> |---|---|---|---|
> | Code | Day 1 | nothing | scaffold, spike, lobby |
> | Content (JSON) | Day 1 | GDD only | `roles.json`, `traits.json`, `items.json`, `scenes/*.json` ids, `tasks.json`, `clues.json`, `balance.json`; rules tests consume these before any map exists |
> | Art | Day 1 | `metrics.json`, `SPRITES.md`, palette | calibration render, Illustrator kit, faction / trait icons, hero concept, base body |
>
> Rule: art lands in `apps/client/public/assets` under keys the placeholder manifest already uses; code imports manifest keys, never paths; `?art=placeholder` keeps playtests running if a render breaks.
>
> ### 7.3 Placeholder strategy
>
> Characters: a generated placeholder atlas (`tools/sprites/placeholder.ts`) with all 8 directions and the final animation keys, drawn as a capsule scaled by height, a scarf rectangle tinted R/G/B, a hat shape, a nameplate with the scarf shape icon; `PlayerView` logic is final from M2. World: Kenney Roguelike / Tiny Town 16 px tiles scaled x4 with nearest filtering set per key from the manifest `filter` field; doors as four-state coloured rectangles. Clues and bodies: coloured circles with a letter plus the final `clue_<id>` key. UI: DOM + CSS with palette tokens and Oswald / Inter. Audio: Kenney UI packs under the final SFX keys.
>
> ### 7.4 Risk register
>
> | # | Risk | L | I | Mitigation |
> |---|---|---|---|---|
> | 1 | Hosting cold start ruins the first impression | H | M | Render Free only until the M3 exit, with the `/health` "waking" landing state; Railway Hobby always-on from the first friends playtest |
> | 2 | WebSocket blocked on school / corporate networks | M | H | wss on 443 only; hotspot advice in the error; documented limit |
> | 3 | Role or position leak via synced state | M | H | Four privacy classes, view-scoped presence, fuzz test, no roles in logs or metadata |
> | 4 | Scope creep (12 roles, 14 scenes) | H | H | M3 gate; V1.5 list frozen; one new mechanic requires one removal or a GDD change entry |
> | 5 | Art style drift across Higgsfield / Blender / Kenney | H | M | Hero reference + calibration cube in every prompt; `palettize.py`; auto contact sheet from `pack.ts` |
> | 6 | Cannot gather testers | H | M | Game designed to be fun at 4-5 humans; bots are load clients only; Discord playtest channel |
> | 7 | Mobile performance | M | H | Baked lighting, 2048² pages, FPS overlay, real Android test each milestone |
> | 8 | Licensing (Synty, Mixamo raw, NC, Pixabay) | M | H | Policy in `ASSETS.md`; CREDITS row in the PR template; masters outside the repo |
> | 9 | Framework APIs behave differently from the write-up | M | M | Day-2 spike; in-memory role Map fallback; lerp-only netcode |
> | 10 | Browser audio autoplay | H | L | Unlock on the Create / Join click; visual twin for every sound |
> | 11 | Rubber-banding | M | M | 150 ms lerp, no prediction, swarm bot tick metrics |
> | 12 | Deduction too certain or too weak | M | H | 2-of-3 clues, Lens charges, suspect sets; metrics from M3; all knobs in `balance.json` |
> | 13 | Reconnection edge cases | M | M | State-driven UI; server tests per phase; 60 s window |
> | 14 | Pages bandwidth / size | L | M | Budgets in 6.8; CI size report |
> | 15 | Burnout in M4 | M | H | Four demoable sub-goals; each shipped behind a toggle |
> | 16 | Tick budget on a shared vCPU | M | M | int16 positions, uint8 enums, 5 Hz view reconcile, clue GC, p95 gate before M4 |
>
> ### 7.5 Playtest plan
>
> | Tier | When | Setup | Goal |
> |---|---|---|---|
> | Bot-only | every PR from M2 | `pnpm bots --n 9`; from M3 `pnpm bots:soak` (6 walkers, one Killer, reporters and random voters play matches back to back) (the quick mode's `bots:soak:onub` left with the mode, A115); the `soak` workflow runs it for 30 minutes by hand and weekly, never on push | crashes, tick p95, patch size, memory over 1 h; bodies, clues and meetings occur; no presence or night leak |
> | 2-person | M1, M2 | owner + 1 friend, one on a phone | onboarding, controls, portal feel |
> | 4-5 humans | M3, each M4 sub-goal | friends via Discord | is the vote fun; clue readability; meeting length |
> | 4-6 humans | M3b (removed in round 7, A115) | friends via Discord, two sessions of quick mode | does one night and one vote land in the target length; do players know their final role at the reveal; "would play again" against M3 |
> | 1-3 humans | M3c | the owner alone, then with one or two friends; NPCs fill the party | does a match finish with NPC seats in both modes; do the NPC seats pass as villagers; does the NPC Killer threaten |
> | 5-6 humans | M5b, M5c | friends via Discord, on each map | is gathering worth the walk; do mobs read as danger; does the opening overstay its welcome; does the music tell the phase |
> | Owner alone | M5d, every round from 6 | `#/admin` on Railway, a 10-seat all-NPC match at 10x; `pnpm auto -- --matches 50` before every integration | invariant failures, stuck NPCs, phase overruns, matches that never end |
> | 6-8 humans | M5, M6 | friends + bots as load only | stealth, night, PvE |
> | 10-person | M7 | 6 humans + 4 bots, then 10 humans | suspect sets in 2-Killer games, chat spam, load |
>
> Metrics per match (server JSON lines): phase durations; kill -> report time; unreported bodies; clues collected per player; Inspect / Compare uses; vote accuracy; suspect-set correctness; chat lines per player; disconnects and reconnect success; FPS percentiles by device class; match length and winner by player count. Feedback form after each session: role played; "understood my role in 20 s" 1-5; "I knew where to go"; "the vote felt fair"; most confusing moment; phone or desktop; would play again 1-10; one thing to add, one to remove.
>
> The playtest kit lives in `docs/PLAYTESTS/`: `README.md` is the run sheet (owner prerequisites, the session plan, the host's script), `FORM.md` is the feedback form above built question by question for Google Forms, `SCORECARD.md` is the M3 fun-or-stop sheet with the decision line, and `TEMPLATE.md` is one session's notes, copied to `YYYY-MM-DD-<milestone>.md`.
>
> ### 7.6 Workflow
>
> The default branch (`claude/zen-turing-m1jnw0`; there is no `main`) is always deployable and protected by CI. One branch per milestone task (`m4a/clues-and-lenses`), one AI session per branch scoped to a single task prompt from `ROADMAP.md`, PRs under 400 lines with tests for rules changes and a GDD note when behaviour changes. Squash-merge; tag `v0.<milestone>.<n>` at milestone exit. `pnpm docs:balance` (planned, not built: there is no such script and no `BALANCE.md`) would regenerate `BALANCE.md` from `balance.json`, beside a PR template with a "docs updated" checkbox (not built either); there is no CI grep gate, no changelog automation and no preview deployments until a second contributor exists. Sessions never upgrade dependencies.
>
> ### 7.7 Day 1 to Day 14
>
> | Day | Work |
> |---|---|
> | 1 | Repo init, `.gitattributes`, pnpm workspaces, tsconfig / eslint / prettier / vitest, `@wdi/shared` with `version.ts`, `constants.ts`, `metrics.ts`; `@wdi/content` with `palette.json`, `metrics.json`, zod; `docs/` seeded; LICENSE files. Art: pin palette, write the hero prompt, start the rig `.blend` |
> | 2 | Spike package: custom `roomId` + `joinById`, hidden `.view()` field, `setFixedTimestep`; record results. `apps/server` with `defineServer`, `/health`; `apps/client` from the official Phaser 4 Vite + TypeScript template (Vite bumped to 8, `-nolog` scripts) with a Boot scene; `ci.yml` |
> | 3 | `pages.yml`; Render Free web service from the GitHub repo (Railway Hobby at the M3 exit); CORS; version handshake; calibration render. **M0 exit** |
> | 4 | Schemas (`Player`, `Private`, `Presence`, `GameState`, `Settings`); `PartyRoom` create / join; `CodeRegistry`; generic join error; tests for 11th join and version mismatch |
> | 5 | Landing + Lobby DOM; join by code and deep link; Start gating with the confirm dialog |
> | 6 | `roles.json`, `traits.json`; `assignRoles` + `dealTraits` with property tests; privacy test |
> | 7 | Role card: `roleReveal` payload, DOM card with CSS flip, trait line, 12 s, Ready, Tab; join-only bots. 2-person test. **M1 exit**, tag `v0.1.0` |
> | 8 | ASCII grid exporter -> tilemap + nav bitmap; 40x30 overworld greybox; collision loader shared by both sides |
> | 9 | Fixed step with the `step()` order; one input per tick; command queue; swept AABB; client input at 20 Hz; placeholder atlas generator |
> | 10 | `EntityView` / `PlayerView`, 150 ms lerp, teleport on view add; nameplates; HUD chip + timer |
> | 11 | `Portals.ts` synchronous with transit; `Visibility.ts` scene-scoped views; `sceneEnter`; `World` restart; tavern bar + back room |
> | 12 | Touch stick + 3 buttons, resize; FPS overlay; test "outsider never sees interior or cross-scene positions" |
> | 13 | 30 min bot soak; Android check; fixes |
> | 14 | 2-4 person test; **M2 exit**, tag `v0.2.0`; `PLAYTESTS/` entry; M3 task prompts |
>
> ### 7.8 V2 outline
>
> V2 is the sequel **"Who Did It Too?"**: first person will never be this game (owner, A168). Since 2026-11-16 the owner's word is two modes of one game, 2.5D and 3D (A611, A613), and V2's first step is `apps/walk`, a single-player first-person walk-through with no server (A610, A614). It keeps the frozen ids, the shared server, the rules and the world data. The R8 and R9 work runs in the owner's build order: town moods, then the law, then evolutions and vendetta dilemmas, then the economy, then Port-au-Levain, then story mode. The owner rates them all equally, so this is sequencing, not priority. Each round's contract opens with an intent brief: what the round should feel like, what the owner likes, and what it must never do.
>
> After the V1 beta: (1) 3D `ISceneCollider` from Blender navmesh exports; (2) `input.move` uses `yaw`; (3) cone + occlusion visibility predicate; (4) Three.js or Babylon.js renderer loading the same GLB sources used for the sprite renders; (5) Medium, the Beast, bats, spatial audio, voice chat. Gate: V1 rules tests green and content JSON frozen behind `schemaVersion`.
>

### Source file: docs/PLAYTESTS/README.md

> # Playtests
>
> How a playtest session of Who Did It runs, and where its record goes. Written for the M3 exit
> (`docs/ROADMAP.md` 7.1, the M3 row): three 5-player matches in a row end in a Village or Cabal win
> in 10-18 minutes, vote accuracy and "would play again" are logged, and the **fun-or-stop decision**
> is recorded. The tiers, the metrics and the feedback form are ROADMAP 7.5. Every rule and number a
> player meets is in `docs/GDD.md` and `packages/content/data/balance.json`; this folder cites them.
>
> | File | What it is |
> |---|---|
> | `README.md` | This run sheet: prerequisites, the session plan, the host's script, what to do when something breaks |
> | `FORM.md` | The feedback form, question by question, ready to build in Google Forms |
> | `SCORECARD.md` | The fun-or-stop sheet for the M3 exit, one per M3 session, with the decision line |
> | `TEMPLATE.md` | One session's notes; copy it to `YYYY-MM-DD-<milestone>.md` |
> | `2026-xx-xx-m2.md` | The M2 playtest entry (a stub until that session is written up) |
> | `README.md` 8 and 9 | The M3b quick-mode evening (the mode was removed in round 7, A115; kept as a record) and the M3c NPC session |
>
> One file per session, named `YYYY-MM-DD-<milestone>.md` (`2026-11-02-m3.md`; a second session the
> same day adds `-b`). The scorecard is filled in a copy too: `YYYY-MM-DD-m3-scorecard.md`, and for
> the later milestones `-m3b-scorecard.md` and `-m3c-scorecard.md` (`SCORECARD.md` 6 and 7).
>
> **Status, 2026-11-19.** No session file has been written here yet beyond the M2 stub. The owner's own playtests of the
> round-8 build are recorded in `docs/DECISIONS.md` (A168, A196, A222), and `docs/ROADMAP.md` 7.0 gives each milestone's
> status.
>
> ## 1. Owner prerequisites (before inviting anyone)
>
> These are the owner's, recorded in `docs/SESSIONS.md` Round 3 and ARCHITECTURE 5.10. None of them
> is done by a build session.
>
> 1. **Round 3 merged.** Sessions K, L, M, N, O, P and Q merged into the default branch
>    (`claude/zen-turing-m1jnw0` until it is renamed `main`), CI green, and `match.spec.ts` (Session
>    O) passing against the real server.
> 2. **Railway Hobby service** (DECISIONS A6, ARCHITECTURE 5.10). New project from the GitHub repo,
>    branch `claude/zen-turing-m1jnw0`, root directory left at the repo root; `railway.json` supplies
>    the build and start commands and the `/health` check, so leave those fields empty in the UI. No
>    variables are needed (`PORT` is Railway's), and **`WDI_DEBUG` must not be set** (the debug
>    handlers must not exist on a server friends play on; CLAUDE.md). Generate a public domain under
>    Networking, open `https://<service>.up.railway.app/health` and check it answers
>    `{ok: true, build: ...}`.
> 3. **The server URL in the client.** `apps/client/.env.production` holds the Railway service's
>    `https://` URL and every `pages` run builds with it; change the file and push if the service ever
>    moves. (An Actions variable `VITE_SERVER_URL` overrides it, see the comment at the top of
>    `.github/workflows/pages.yml`.)
> 4. **Pages source.** Settings > Pages > Build and deployment > Source = **GitHub Actions**.
> 5. **Same build on both sides.** The `build` on `/health` equals the first 8 characters of the commit
>    the `pages` run deployed. Every push to the default branch redeploys both, at different speeds:
>    Pages is live about a minute after the push, while Railway waits for that commit's CI run to pass
>    and then builds, about seven minutes in all. Until the server catches up every join fails with
>    "refresh to update" (ARCHITECTURE 5.10), so after a push wait for `/health` to show the new
>    commit before testing. A red CI run leaves the server on the previous commit until the next green
>    push; do not push to the default branch during a session.
> 6. **Smoke run, alone, the day before.** First from a terminal in the repo:
>    `pnpm bots:live -- --url https://who-did-it-production.up.railway.app` creates a party on the live
>    server with five bots, starts it and reports the role cards and the overworld entry (exit code 1
>    on any failure). Then open `https://groot99-droid.github.io/Who-Did-It/` in two browsers (one a
>    phone), create a party, join it, start, walk through a door. If the landing shows "Waking the
>    village..." for more than a moment, the page is not reaching the server: check step 3 and the
>    service's logs.
> 7. **Server logs.** Railway > the service > Logs open in a tab. Each finished match prints one JSON
>    line (the match log, 4); the scorecard needs it.
> 8. **The form.** Build the Google Form from `FORM.md` and keep its link ready to paste.
> 9. **Discord.** One voice channel and one text channel for the session; the invite sent with the
>    date and "bring a laptop or a phone, headphones on".
>
> ## 2. Who and what
>
> - **Five players**, the host among them (the 5-player row of GDD 3.1: Killer, Detective, Doctor and
>   two Townsfolk). A sixth person would change the roster and the win rule (GDD 3.8, 3.9); if a
>   sixth friend comes, they watch the host's screen for the first match and swap in for the second,
>   and the scorecard notes the swap.
> - At least one player on a phone, so the form's device question has both answers.
> - Two M3 sessions on different days (ROADMAP 7.1, the Playtest column). The decision line is
>   signed after the second one.
> - The host plays, reads the script, keeps the time and fills the scorecard between matches. Nobody
>   else needs to read anything before the session.
>
> ## 3. Session plan
>
> Clock times from the start of the call. The matches are the only part that can run long; protect
> the form and the debrief at the end even if that means fewer matches.
>
> | From | Step | Who |
> |---|---|---|
> | -0:30 | Prerequisites 2 to 7 checked again; `/health` answers; logs tab open | Host |
> | 0:00 | Everyone in Discord voice; sound check; the Pages link pasted in the text channel | All |
> | 0:05 | Host creates the party and pastes the invite link; everyone joins and types a name | All |
> | 0:10 | The script, part A (rules and controls) | Host |
> | 0:15 | Match 1 | All |
> | after each match | The script, part B (between matches); the match-log line copied; scorecard row filled | Host |
> | | Match 2, then match 3 | All |
> | after match 3 | The form link pasted; everyone fills it before talking | All |
> | then | Debrief, the script part C | Host |
> | end | Scorecard totals; notes file committed within a day | Host |
>
> The time a match takes in play is set by the phases in GDD 3.3 (`balance.json` `phases`) and the
> 5-player row of GDD 3.9; a cycle and the length of a typical match are given there. Plan for about
> an hour of play for the three matches, plus the meeting screen and lobby between them.
>
> ## 4. The match log
>
> At game over the server prints one JSON line to stdout (Session K, `services/MatchLog.ts`; ROADMAP
> 7.5): the players, the match duration, the winner, the kills, the meetings, whether each ejection
> was correct, the vote accuracy of each meeting, and the clues collected by each player. In the
> Railway logs it is the only line of a match that holds all of these; search the logs for the
> `winner` key. Paste the whole line into the session notes under the match it belongs to, and copy
> the duration, winner and per-meeting vote accuracy into the scorecard. The field names are the
> ones `MatchLog.ts` writes; if they differ from the words here, the line wins and the notes say so.
>
> ## 5. The host's script
>
> Read it aloud. Words in brackets are for the host only.
>
> ### Part A, before match 1
>
> > Thanks for coming. This is Who Did It, a hidden-role game in a village called Hollowmere. It is
> > an early build: the art is half done, things will break, and that is what we are here to find.
> >
> > Everyone gets a secret role card. One of you is the **Killer**. The rest are the village: a
> > **Detective**, a **Doctor**, and **Townsfolk**. Keep your card to yourself: no streaming, no
> > screen sharing, no showing the person next to you.
> >
> > **Controls.** WASD or the arrows to walk, Space to run, Shift to sneak. E uses whatever is in
> > front of you: a door, a clue, a body, the bell. Q is your first ability on the card, R and F the
> > next ones. N opens your Notebook, Tab your role card. On a phone: the stick on the left, and the
> > buttons on the right are Use, Act, Run and Sneak. Some rows on your card are not built yet; if a
> > key does nothing, that is why.
> >
> > **The Killer** kills with Q when nobody is looking, and the knife has a cooldown. A kill leaves a
> > body where it happened, footprints that show the killer's height, and a thread that shows their
> > scarf colour. The Killer also looks bloody for a while, but only up close.
> >
> > **Everyone else** hunts clues: hold E on a clue to put it in your Notebook. The Detective's clues
> > are marked Verified; anyone else's are Claimed, so you have to trust them. The Doctor can bandage
> > someone with Q, and that person survives the next attack on them.
> >
> > **Meetings.** Find a body and press E to report it, or ring the bell on the square with E. Everyone
> > is pulled to the square. The bell has a limited number of pulls per person, and Townsfolk get an
> > extra one. You talk, then vote for someone or Skip. Votes are secret until the
> > reveal. Most votes is out, and their role is shown. A tie or a Skip means nobody goes.
> >
> > **Dying.** If you are killed, you are a ghost. Nobody knows until the next meeting, so don't say
> > it. You can walk around and see everyone's role, and chat with the other ghosts, but you cannot
> > vote or talk to the living.
> >
> > **Winning.** The village wins when the Killer is voted out. The Killer wins when only one
> > villager is left alive.
> >
> > **Discord.** Mics off while you are walking around. Mics on during a meeting, as soon as the
> > meeting screen opens, and off again when you are back in the village. Ghosts stay muted until the
> > game-over screen. Don't react out loud to anything you see on screen outside a meeting.
> >
> > We play three matches. After the last one there is a short form; please fill it in before we
> > talk, so we don't steer each other. Any questions? Press Ready.
>
> [The host presses Start when all five are Ready. If someone is not Ready the confirm dialog lists
> them; wait for them.]
>
> ### Part B, between matches
>
> [As the game-over screen counts down to the lobby: note the end time. In the Railway logs copy the
> match-log line. Fill the scorecard row: length, winner, why, vote accuracy. Then say:]
>
> > That was match {n}. Quick round, ten seconds each, no spoilers about strategy: what was the moment
> > you remember? [Write one line per person in the notes.] Press Ready when you are back.
>
> [The lobby keeps the same code and seats (A30); roles are dealt again at Start.]
>
> ### Part C, the debrief (after the form)
>
> > Thanks. Five questions, then we're done.
> >
> > 1. When did you first know what you were supposed to do?
> > 2. Was there a meeting where you felt you had nothing to go on?
> > 3. Did the clues ever point at the right person? Did you read them in the world or in the
> >    Notebook?
> > 4. Killers: did you ever feel you had no chance to strike, or that it was too easy?
> > 5. If we played again tomorrow, would you come? What would make you bring a friend?
>
> [Write the answers as quotes where you can. Don't defend the game; ask "what made you feel that?"]
>
> ## 6. When something goes wrong
>
> - **A player drops during a match.** In M3 they become a ghost at once, with no body and no way
>   back (GDD 3.8, A30). Let the match finish. On the scorecard mark it **void (drop)**; they rejoin
>   the lobby with the same link before the next match.
> - **The server stops or restarts.** Everyone is sent back to the landing. Note the time and the
>   last thing that happened, copy the log lines around it, mark the match **void (crash)**, create a
>   new party and continue. Two crashes in a session: stop playing, run the form and the debrief.
> - **A bug that doesn't stop play** (a wrong prompt, a sprite in a wall, a line that makes no sense).
>   Say "bug" in voice; the host writes the time and one line; play on. A screenshot after the match
>   is welcome.
> - **A match runs past the time target.** M3 has no Final Night (it is M4, A30), so nothing forces an
>   end. Let it play to a win unless the group agrees to stop; a stopped match has no winner and fails
>   the timing line. Either way write down when it stopped feeling like a game.
> - **Someone breaks the Discord rule.** No penalty; mark the match "voice leak" in the notes, since
>   it bends vote accuracy.
>
> A void match doesn't count for or against the exit test; the next three valid matches in a row do.
> If the session runs out of time first, the scorecard says so and the second session repeats the
> test.
>
> ## 7. After the session
>
> Within a day: copy `TEMPLATE.md` to the dated notes file and fill it, copy `SCORECARD.md` to its
> dated copy and fill it, export the form responses into the notes (a summary, not names), and commit
> both on a branch with a pull request. After the second M3 session the owner signs the decision line
> and records the decision as a row in `docs/DECISIONS.md`; ROADMAP 7.6 tags the milestone exit.
>
> ## 8. Quick mode evening (M3b)
>
> Removed in round 7 with the quick mode (DECISIONS A115); kept as the record of the plan.
>
> The M3b exit (ROADMAP 7.1, the M3b row; the tier is ROADMAP 7.5 `4-6 humans`): three 6-player
> quick-mode matches in a row finish in the target length, players name their final role at the reveal
> in at least half the matches, and "would play again" is compared with M3. The rules are GDD 3.11 and
> `balance.onub.json`; the lines on screen are `docs/UI.md` 14.12. Two sessions on different days.
>
> **Prerequisites.** Section 1 unchanged, with "Round 4 merged" in place of round 3 in step 1 and a
> quick-mode smoke run in step 6 (two browsers, the mode chip toggled, one match through to the end
> screen; with fewer than four humans the NPCs fill the rest, so this needs no friends).
>
> **Who.** Six players, the host among them (the 6-player row of GDD 3.11: two Poisoners, the
> Hireling, the Sin-Eater, the Cutpurse, the Busybody, two Mourners and the Debtor among nine loaves).
> A seventh friend changes the deck: they watch the host's screen for a match, then swap in, and the
> scorecard notes it. Four or five is a valid evening but not the exit test.
>
> | From | Step | Who |
> |---|---|---|
> | -0:30 | Prerequisites checked; `/health` answers; logs tab open | Host |
> | 0:00 | Discord voice, sound check, the Pages link in the text channel | All |
> | 0:05 | The party created, everyone joined; the leader toggles the mode chip to quick mode | All |
> | 0:10 | The script, part A (below) | Host |
> | 0:15 | Match 1; at the vote, each player DMs the host the role they think they hold | All |
> | after each match | Part B; the match-log line copied; the scorecard row (`SCORECARD.md` 6) | Host |
> | | Matches 2 to 5 (a short match leaves time for more; the test needs three valid in a row) | All |
> | then | The form (`FORM.md`, item 9 included); then the debrief, part C below | All |
>
> **Voice rule.** Mics off from the role card until the dawn meeting opens: a sleeper who hears "oh,
> I'm up" learns who woke. Mics on in the dawn meeting and on the end screen. The in-game chat and
> claim chips stay the record; say a claim out loud and tap it too.
>
> **Part A, before match 1.**
>
> > Tonight is the short game: one night, one vote, done in minutes. The night before the will is
> > read, the baker bakes a loaf for each of you and three for the dead, with a token inside. Your
> > role card shows the token you were handed. At dusk you walk into the bakery and hold E on your
> > plate to set your loaf down. Then everyone goes to sleep in the loft. You cannot move and there is
> > no clock; just listen to the storm.
> >
> > Some roles get woken up, one at a time, and come down to the bakery to tamper: peek at a loaf,
> > take one, swap two, read the ledger. You act as the role you were dealt, even if someone has
> > already swapped your loaf. So by morning you may not be what your card said.
> >
> > At dawn there is one meeting. Use the claim chips to say what you were and what you saw, argue,
> > then vote. No Skip, and you cannot vote for yourself. Whoever gets the most votes is turned out;
> > a tie turns them all out. Winners are judged on the loaf you hold at dawn, not the card. The two
> > Poisoners want nobody of theirs turned out; the Debtor wants to be turned out. When the vote
> > closes, DM me the role you think you hold now. Then the end screen shows what really happened.
>
> **Part B, between matches.** As in 5, plus: read the end screen's swap log aloud once ("the Cutpurse
> took Hana's loaf ...") and tick each DM'd guess right or wrong against the final roles.
>
> **Part C, the debrief.** Five questions: (1) Was the night tense or just a wait? (2) Did you
> believe your own card at dawn, and why? (3) Did the claim chips help, or did you talk past them? (4)
> Did the swap log on the end screen make sense of the match? (5) Would you play this before or
> instead of the long game?
>
> ## 9. NPC session (M3c)
>
> The M3c exit (ROADMAP 7.1, the M3c row; the tier is ROADMAP 7.5 `1-3 humans`): one human with three
> NPCs finishes a main match (the quick-mode match left with the mode, A115), and the NPC Killer wins at least one of five
> scripted matches at Normal. The rules are GDD 3.12 and `balance.json` `npc`; the lobby lines are
> `docs/UI.md` 14.13. Two sessions on different days.
>
> **Prerequisites.** Section 1 unchanged ("Round 4 merged" in step 1). The scripted matches are the
> bot harness's (ARCHITECTURE 5.12), run from a terminal and logged by the host before session 1.
>
> **Who.** Session 1 is the owner alone; session 2 the owner with one or two friends. Nobody is told
> which seats are NPCs; with two or three humans each guesses on the form (item 10).
>
> | From | Step | Who |
> |---|---|---|
> | -0:30 | Prerequisites checked; the five scripted Normal matches run and logged (`SCORECARD.md` 7) | Host |
> | 0:00 | The party created; NPCs fill at Start, or the leader adds them with Add NPC | Host |
> | 0:05 | Main match, one human with three NPCs (session 1) or the humans with NPCs to four (session 2) | All |
> | after it | The match-log line copied; the scorecard row | Host |
> | | Optional: the difficulty at Hard with enough NPC seats, one more main match | All |
> | then | The form (item 10 included); notes within a day | All |
>
> **Script.** Part A of 5 for the main match, minus the Discord rule
> when the owner plays alone. Add once: "Some seats may be computer villagers. They never chat. Play
> everyone the same."
>

### Source file: docs/round11/questions.md

> # Round 11: questions for the owner
>
> Round 11's two planning sessions have finished their designs:
>
> - 11A, the render pipeline: [`pipeline.md`](pipeline.md);
> - 11B, the materials, styles and budgets: [`look.md`](look.md).
>
> These are their questions, 22 in all, in one list. Each has a proposed answer. You can answer **default** (take the
> proposal) or **different** (with a note in your own words), in the form at
> https://claude.ai/artifact/KTRrtfV3aRGprcyspSMM1E, which saves your answers, or in the chat. The plan, `round11-plan.md`, is written from your answers.
> A question still unanswered by then takes its default and is marked _proposed_.
>
> Where both documents asked the same thing, the question is asked once and names both sources. They disagreed twice
> (SC1, SC2): those questions say so, and the default is 6Z's.
>
> Nothing outside `docs/round11/` changes until you approve the plan. The asset list (`assets.md`) comes at round 10's
> content freeze.
>
> ## Scope: what the makeover covers
>
> ### SC1. Which art stays outside Blender? (11A P9, 11B Q10)
>
> Some things in the world are still drawn in code, not modelled: the creatures, the resource nodes, the quest givers,
> the tools, and round 10's greybox frames (the beds, the tools, the logs). The round-11 brief reads the makeover as
> "every world asset made in Blender". 11A proposes moving the code-drawn classes into the rig last, after the world and
> the figures. 11B's draft kept the creatures, nodes and givers in code.
>
> - **Proposed default:** everything that stands in the world is made in Blender, and the code-drawn classes come last.
>   These stay outside Blender: the UI icons (their SVG masters), the card portraits and concepts (Higgsfield), the
>   screens, and the run-time particle effects (A162).
>
> ### SC2. Models from Meshy (your ROSW `asset-3d` pipeline) in the shipped art? (11A P7, 11B Q8)
>
> Your ROSW `asset-3d` pipeline turns a prompt or an image into a 3D model through Meshy. ASSETS 6.4 leaves open whether
> a generated mesh is yours to ship. 11A's draft allowed props and creatures, and 11B's props, furniture and machinery.
>
> - **Proposed default:** yes for props, furniture and machinery, once you confirm that Meshy's output on your plan is
>   yours to ship. Each one is a master in ROSW with its run id and a `CREDITS.md` row, and it is re-dressed in the
>   game's own materials when it is imported. Never the figures or the creatures: they stay on the repo's own rig.
> - **If you don't answer:** no Meshy model ships in round 11.
>
> ### SC3. Export every master for V2, the first-person version? (11B Q13)
>
> V2 is to load the same models as the sprite renders. Each master would also export a GLB with materials named by role,
> the rig, and two lighter versions (LODs at a half and a quarter of the triangles).
>
> - **Proposed default:** yes (`look.md` 8).
>
> ## Camera and light
>
> ### CL1. Keep the camera and the scale exactly as they are? (11A P1)
>
> The isometric camera, the display scale, the figures' height cap and the pivots stay. Every image key and page the
> game loads stays valid, so the client does not change: the makeover is new art in today's frames.
>
> - **Proposed default:** yes (`pipeline.md` 2).
>
> ### CL2. One light for every style? (11A P2)
>
> The key light keeps today's direction in all three styles. The renders bake ambient occlusion (the soft darkening in
> corners and under eaves) and the figures' contact shadows, each style in its own amount (`look.md` 4.4). Buildings
> cast no shadow on the ground: under this light about 98% of a building's shadow falls under its own roof anyway, and
> the shadow is the most expensive part of a render. Day, night and the lamps stay the game's own lighting.
>
> - **Proposed default:** yes (`pipeline.md` 3).
>
> ### CL3. Long shadows from buildings, as a ground layer that fades at dusk? (11A P3)
>
> - **Proposed default:** no, not in round 11. Under today's light they are mostly hidden (`pipeline.md` 4.3).
>
> ### CL4. Lamps that light the walls as you carry them? (11A P4, 11B Q14)
>
> This needs normal maps or depth for every sprite: a second page for every page of art, which breaks the memory cap for
> the figures in every style.
>
> - **Proposed default:** no. Light stays baked into the art, with today's lighting layer on top (`pipeline.md` 4.3,
>   `look.md` 5.3).
>
> ## Styles and figures
>
> ### ST1. Keep all three styles: 8-bit, low poly and HD? (11B Q1)
>
> Each style is a finish of one shared set of models, not a separate set of art. The alternatives are to merge 8-bit
> and low poly into one style, or to keep one look only.
>
> - **Proposed default:** yes, three finishes of one master set (`look.md` 4.3).
>
> ### ST2. 8-bit figures: flat colour or textured? (11B Q5)
>
> Textures cost no bytes, but at 64 px a cloth texture reads as speckle on a coat and darkens the skin and the hands.
> The sample sheet shows both: [`samples/look/figure-styles.png`](samples/look/figure-styles.png).
>
> - **Proposed default:** flat figures. The world stays textured.
>
> ### ST3. Low-poly figures: flat colour or textured? (11B Q6)
>
> Textures cost nothing here either, but low poly's posterising moves a look's colours off its palette: the baker's blue
> coat turns green-grey.
>
> - **Proposed default:** flat figures. Textured garments are kept for HD.
>
> ### ST4. HD figures: how do they fit? (11B Q2)
>
> At HD size each figure takes about 16 times today's memory. Fifteen looks would need about 1.5 GB of video memory and
> 264 MB of downloads, far past every budget. The ways out:
>
> 1. **HD-1:** the HD world with the low-poly figures in it.
> 2. **HD-2:** HD figures at half the HD size, in a compressed GPU format. This needs a test on your desktop first, so it
>    would come in a later round.
> 3. **HD-3:** a much larger memory cap. Not proposed, because a 4 GB device has no room for it beside the browser.
>
> - **Proposed default:** HD-1. Where an HD image is missing, the game falls back to low poly, then to 8-bit. HD-2 stays
>   open for a later round.
>
> ### ST5. Render the HD figures under the sky light? (11B Q15)
>
> A164 left open whether HD figures should be lit by the PBR sky. Measured, it barely changes them.
>
> - **Proposed default:** no. Figures render without it, and the question closes.
>
> ### ST6. Texture sizes: 1k maps for every sprite render, with the 2k maps kept for V2? (11B Q11)
>
> - **Proposed default:** yes, with the rock face at 2k in HD only (`look.md` 3.2).
>
> ### ST7. A colour check for low poly and HD? (11B Q12)
>
> 8-bit art is checked pixel by pixel against the palette, and low poly and HD cannot be. The new check keeps their main
> colours near the palette, saturated colour under 10% of a frame, and nothing darker than the ink.
>
> - **Proposed default:** yes (`look.md` 3.3).
>
> ## Budgets
>
> ### BU1. A memory cap for HD alone? (11B Q3)
>
> Nothing at HD's density fits today's cap of 9 page-equivalents.
>
> - **Proposed default:** an HD-only cap of 18 page-equivalents (288 MiB), behind the HD device gate, checked once HD art
>   exists.
>
> ### BU2. The HD download budget? (11B Q4)
>
> - **Proposed default:** keep 80 MB. With HD-1, the HD set comes to about 18 MB.
>
> ### BU3. The first load: keep the 12 MiB cap, and leave the 8 MiB target for later? (11B Q7)
>
> - **Proposed default:** yes. The makeover adds almost nothing to the 8-bit first load.
>
> ### BU4. The test phone and the frame-rate floor? (11B Q9)
>
> No test device is written down today.
>
> - **Proposed default:** your own Android, at 30 fps or more in the busiest scene with ten players, in 8-bit and low
>   poly, measured on every art drop. Please say which phone it is.
>
> ## Where and how the renders run
>
> ### RN1. Where do the renders run? (11A P5)
>
> Measured in a cloud session, the 8-bit and low-poly figures take about 9 hours on one session.
>
> - **Proposed default:** cloud sessions in parallel: four for the figures and one for each map's world. Your laptop is
>   used only if one test frame there shows that it is much faster.
>
> ### RN2. HD render quality: 8 samples instead of 32? (11A P5, 11B Q16)
>
> 8 anti-aliasing samples render HD 3.6 times faster than today's 32, with no visible difference (a mean difference of
> 0.44 out of 255 on a figure). With HD-1 (ST4), this applies to the HD world only.
>
> - **Proposed default:** 8, raised to 16 if the first HD sheet shows noise in the soft edges or the shadows.
>
> ### RN3. May the cloud environment install Blender for every session? (11A P6)
>
> The environment's setup script would install Blender's `bpy` 5.2.0 and three graphics packages, adding about a minute
> to each session's start. It is a setting you change on the environment's settings page; no session can change it.
>
> - **Proposed default:** yes.
>
> ### RN4. Keep a copy of the free Kenney model packs as a release download of this repo? (11A P8)
>
> On 2026-10-29 the link to Kenney's Fantasy Town pack returned a web page instead of the zip, so the kit pieces built
> from it cannot be re-made from a fresh checkout. Either way, a hash lock records each pack.
>
> - **Proposed:** yes, keep a copy, with the hash lock.
> - **If you don't answer:** the hash lock only.
>

### Source file: docs/round11/owner-answers.md

> # Round 11: the owner's answers
>
> The owner answered all 22 questions of [`questions.md`](questions.md) in the form
> (https://claude.ai/artifact/KTRrtfV3aRGprcyspSMM1E) and submitted it at 2026-10-30T03:37:26.649Z. **Default** means
> the owner took the proposed default in `questions.md`. The one **different** answer quotes the owner's note verbatim,
> and it replaces the default. These answers win over `pipeline.md` and `look.md` wherever they disagree.
>
> Totals: 21 defaults, 1 different (CL3).
>
> | Question | Answer | Saved (UTC) |
> |---|---|---|
> | SC1. Which art stays outside Blender? | default | 01:28:09 |
> | SC2. Models from Meshy (your ROSW `asset-3d` pipeline) in the shipped art? | default | 01:54:03 |
> | SC3. Export every master for V2, the first-person version? | default | 03:01:04 |
> | CL1. Keep the camera and the scale exactly as they are? | default | 03:01:19 |
> | CL2. One light for every style? | default | 03:01:26 |
> | CL3. Long shadows from buildings, as a ground layer that fades at dusk? | **different** | 03:02:50 |
> | CL4. Lamps that light the walls as you carry them? | default | 03:03:11 |
> | ST1. Keep all three styles: 8-bit, low poly and HD? | default | 03:03:16 |
> | ST2. 8-bit figures: flat colour or textured? | default | 03:35:53 |
> | ST3. Low-poly figures: flat colour or textured? | default | 03:36:01 |
> | ST4. HD figures: how do they fit? | default | 03:36:11 |
> | ST5. Render the HD figures under the sky light? | default | 03:36:26 |
> | ST6. Texture sizes: 1k maps for every sprite render, with the 2k maps kept for V2? | default | 03:36:36 |
> | ST7. A colour check for low poly and HD? | default | 03:36:41 |
> | BU1. A memory cap for HD alone? | default | 03:36:43 |
> | BU2. The HD download budget? | default | 03:36:52 |
> | BU3. The first load: keep the 12 MiB cap, and leave the 8 MiB target for later? | default | 03:36:54 |
> | BU4. The test phone and the frame-rate floor? | default | 03:36:56 |
> | RN1. Where do the renders run? | default | 03:37:05 |
> | RN2. HD render quality: 8 samples instead of 32? | default | 03:37:08 |
> | RN3. May the cloud environment install Blender for every session? | default | 03:37:21 |
> | RN4. Keep a copy of the free Kenney model packs as a release download of this repo? | default | 03:37:22 |
>
> ## CL3: the long shadows come in round 11
>
> The proposed default was "no, not in round 11". The owner, verbatim:
>
> > yes
>
> So the buildings' long shadows are part of round 11, as the shadow layer of `pipeline.md` 4.3: a ground sprite that
> the client draws under every y-sorted sprite and fades at dusk. The default had left them out because today's key
> light hides most of them (`pipeline.md` 3.2), and CL2 keeps that key. `round11-plan.md` says which light casts the long
> shadows and what the layer costs.
>
> ## The plan approved (2026-10-30)
>
> The owner approved `round11-plan.md` (A236). In 11A's session, after 11A said the plan had gone to the owner for
> approval, the owner wrote, verbatim:
>
> > yes merge
>
> In 6Z's session, answering 6Z's numbered list, where item 3 was the plan's approval with CL3a's default (item 6 was
> round 10's Herb Bread question), the owner wrote, verbatim:
>
> > 3. confirm, 6. dawn. im off for tonight
>
> So CL3a takes its default: the long shadows fall from a sun at 25°, turned 45° from today's key (`round11-plan.md` 9).
> The look gate shows them again in every style. Round 11 builds after round 10's final sweep (10Z) has merged.
>
> ## What three defaults still need from the owner
>
> - **SC2.** The default allows Meshy models "once you confirm that Meshy's output on your plan is yours to ship". Until
>   the owner confirms, no Meshy model ships, which is the question's own fallback.
> - **BU4.** The default names "your own Android". The owner has not yet said which phone it is.
> - **RN3.** The setup script is a setting that only the owner can change, on the environment's settings page. Until it
>   changes, a session that renders installs `bpy` itself (README, "Sample renders").
>

### Source file: docs/story/questions.md

> # Story mode: the owner's questionnaire
>
> Written 2026-11-06 after #463 merged (four chapters on HollowMere). Every question has a proposed default and says
> where the answer lands. A default holds until you answer. Mark each **Yes**, **No** or write your own.
>
> ## A. What shipped, to confirm
>
> **A1. Chapter 3 is the Bandit, the outlaw.** The Killer card with the `bandit` heist vendetta; the strongbox crack is
> the chapter's turn (DECISIONS A430).
>
> - Default: yes.
>
> **A2. Chapter 4 is the Activist.** The Killer card with the `activist` sabotage vendetta, on day 3. Chosen because it
> needs no second card and no train timing.
>
> - Default: yes. Alternatives: the Zealot (needs a Vicar dealt) or the Hitman (arrives on days 3 to 5).
>
> **A3. Four chapters, in this order.** Baker, Watchman, Bandit, Activist. Chapters play in order; a finished chapter can
> be replayed from the menu.
>
> - Default: yes.
>
> **A4. The chapter looks.** The Bandit walks as the `drifter` look and the Activist as the `tinner` look, whatever the
> Killer card's own look is.
>
> - Default: yes. The alternative is the Killer's own look in both.
>
> ## B. Rules to settle
>
> **B1. A dead player.** A death inside a chapter ends it as failed, shows the failed line, and the next chapter still
> starts, so a story is always finishable.
>
> - Default: keep. Alternative: a failed chapter replays once before the story moves on.
>
> **B2. Pausing.** The world pauses only while a story card is up (there is no second human to wrong). Multiplayer never
> pauses (rolecards Q-D2).
>
> - Default: keep.
>
> **B3. Saving.** None. A story is one sitting of about 25 minutes of play; leaving ends it.
>
> - Default: keep. Alternative: save at each chapter break and resume from the menu.
>
> **B4. The handover moves the card, not the seat** (DECISIONS A415). The player keeps their seat, purse, body and
> position across a break; the card, kit, look and traits change hands.
>
> - Default: keep. Alternative: the player walks to the new role's seat and position, which needs more engine work.
>
> **B5. The story's end.** After chapter 4 the room ends as a Village win.
>
> - Default: keep. Alternative: an end screen of its own, with the four chapters' summaries.
>
> ## C. Content and scope
>
> **C1. A fifth Killer chapter.** The Zealot (the Skin-Walk, needs a Vicar) or the Hitman (the contract, arrives days 3 to
> 5).
>
> - Default: no, until chapters 3 and 4 have been played through.
>
> **C2. A heist-man chapter on the Thief card.** The Thief card is never dealt in a story room today, so the Thief-targeted
> NPC beats in chapters 1 and 2 do nothing. A heist-man chapter needs the deal fixed first.
>
> - Default: later, as its own task. Say if chapters 1 and 2 should also get their stranger back.
>
> **C3. NPC dialogue.** Beats show narration only; the NPCs speak through the existing talk and lore files.
>
> - Default: keep. Alternative: scripted NPC lines inside beats.
>
> **C4. Other towns.** Port-au-Levain and BlackPine stories (Bible V.1) are out of scope.
>
> - Default: out, until the maps themselves are built.
>
> ## D. Process
>
> **D1. Playtest.** Chapters 3 and 4 ask the player to stand still beside a target unseen. No human has played them; the
> bot only answers cards. Do you want a playtest before more is built on them?
>
> - Default: yes. Notes go to the session that fixes them.
>
> **D2. Achievements.** Each chapter end emits `story.chapterEnd` for round 10's E1 (achievements on the device), which
> is not built.
>
> - Default: leave the hook, build E1 with the rest of round 10 part 2.
>
> **D3. The check I did not run.** `pnpm auto` at 50 ran on the head before the Killer chapters, and the full server and
> client suites did not run locally (CI ran them green on the merge).
>
> - Default: run `pnpm auto` at 50 once more on the base, after the next batch.
>
> **D4. Production.** The base deploys to Railway on every push, so story mode is live.
>
> - Default: leave it live. Alternative: hide the title screen's Story entry behind a flag until the playtest.
>
> ## Answers (owner, 2026-11-06)
>
> | Q | Answer |
> | --- | --- |
> | A1, A2 | Default |
> | A3 | Default, with the note: "we need a full story mode, every role. the lore fully plays out" |
> | A4 | Change: the Killer's own look in both chapters |
> | B1 | Change: a failed chapter replays once before the story moves on |
> | B2 | Default |
> | B3 | Change: save at each chapter break, resume from the menu |
> | B4 | Default |
> | B5 | Change: a dedicated end screen with the chapter summaries |
> | C1 | Change: yes, the Zealot. "for chapters with roles like the vicar and the zealot the player must play both sides of the holy war in sections" |
> | C2 | Change: also bring the stranger back into chapters 1 and 2. "a single chapter shouldnt just be one role it should be based around the lore and how the story unfolds" |
> | C3 | Change: scripted NPC lines inside beats |
> | C4 | Change: plan them now. "HollowMere-Port Au Levin-Black pine-etc" |
> | D1 | Change: no playtest first, keep building |
> | D2 | Change: build achievements now |
> | D3, D4 | Default |
>
> The build plan these answers set is `docs/story/part2.md`.
>

### Source file: docs/story/orchestrator-handoff.md

> # Story mode part 2: orchestrator handoff
>
> > **Status, 2026-11-19:** Kept as written on 2026-11-10 to 2026-11-12. Since then `claude/story-part2` merged into the base
> > with #538 (2026-11-12), so "nothing from `claude/story-part2` has gone to the production base" no longer holds; the round-10
> > pull requests it lists as open all merged by 2026-11-12, and #245 was closed. `docs/SESSIONS.md`, "After round 11's plan", has the lanes since.
>
> Written 2026-11-10 (updated 2026-11-12 after #521 and the finisher's third grant) by the orchestrator (session `session_01M5mAcY1JPqjhPmoZ8CZDFp`, "Story mode") so any later
> session can resume without the chat. It restates no rule or number: those stay in `docs/GDD.md` and
> `packages/content/data/balance.json`. Decisions the owner makes belong in `docs/DECISIONS.md`.
>
> ## Standing rules from the owner
>
> - Design is approved through questionnaires published as artifacts.
> - Merging into the production base `claude/zen-turing-m1jnw0` needs green CI and the owner's explicit say-so.
>   Only the round-10 PRs the owner named count as authorised. Merging deploys the base.
> - The story branch is `claude/story-part2`. It merges into the base only when the owner asks and CI is green.
> - The map and gameplay rebuild comes before more content building (P5 content, P6 other towns).
> - Finished sessions are archived automatically (see "Archival routine").
>
> ## Open decisions (owner only)
>
> | # | Decision | Where it waits |
> |---|---|---|
> | 1 | ANSWERED. Vicar / Medium rule: #499 merged; the buff list is speed, health and the conversion aura. Rite brief `docs/story/rite.md` (#501); the owner took the defaults on R-Q1 to R-Q8 | done |
> | 2 | Medium hideout location: Fenwood (`forest_deep`) or a new location (own building, deep woods). The rite site is data, so it can move without code | design |
> | 3 | ANSWERED. Seance is retired with the Medium card | done |
> | 4 | Anti-theme wording (Bandit = detective/police, Activist = post office; each role gets its own building) | design |
> | 5 | `story.read` (GDD 3.26): build or drop | design |
> | 6 | Witness, pickpocket and smoke: build or not | design |
> | 7 | Player accounts plan Q1 to Q14 (Q4 Node >= 22.13, Q12 Google OAuth client) | draft PR #472, session `session_01M5mAcXu65m2U47WM1R6aso` |
> | 8 | Asset list questions: camera, roof and interior cutaway, other role buildings, palette, trees, train, characters | asset list artifact |
> | 9 | Mark which of the 223 asset items could use Poly Haven models instead of Meshy (offered, no answer) | asset list |
> | 10 | Investigate the base's unexplained e2e flakes (world-entry, hud-clock)? | CI |
>
> ## The Vicar design that was agreed
>
> The martyr dies. An unkillable NPC Medium gate in the Zealot's hideout (deep woods, its own building,
> anti-theme of the Vicar's chapel) resurrects him for free and uninterruptibly. He returns the next day of the
> same match, strong enough that he could win that day, with area-spread conversion plus speed and health buffs.
> The martyr weight in GDD 3.20 is gated by the same condition. The NPC replaces the dealt Medium card.
> Against the Zealot first. The GDD change ships in the same PR as the behaviour.
>
> ## Merges that wait for the owner
>
> - PR #471 (UI renumber 14.54 to 14.61): open, unmerged, deploys the base.
> - `claude/story-part2` into the base.
> - P2's E14 PR (#497) is merged into `claude/story-part2` (seen 2026-11-10; the orchestrator did not merge it).
>   Still owed: P2 sends one summary of what the engine can do for P5 and what is blocked.
> - PR #499 (P0's Medium / 10x Vicar docs) is merged into `claude/story-part2` on the owner's word. Still open from it:
>   whether "deep woods" is the existing `forest_deep` (the Fenwood), and the Bandit's and Activist's anti-theme buildings.
> - Session R's PRs are all merged into `claude/story-part2` on the owner's word (confirmed to the orchestrator 2026-11-10):
>   #502 (R1), #505 (R2), #507 (R3), #508 (R4), #509 (R5), #510 (R7) and #511 (status log). R6 (conversion aura) was waiting on I9, which has since merged (#515);
>   R8 (story section) waits on the map revamp. R fixed three e2e/server races on the way (`skipOpening` helper, `npc.spec`
>   NPC-vote assumption, `figuresInView.test.ts`), which bears on open decision 10.
> - #513, #516 and #519 (the previous handoffs) and S3's #512 are merged into `claude/story-part2`. R's I9 (#515, `9990a4b`), I9b
>   (#518, `8b62147`) and R6 (#521, `535b56f`) are merged there too, per R's reports (R1 to R7, I9 and I9b are all in the story branch;
>   R6 started on the owner's word, 2026-11-12). The owner chose option (a), keep the listener's once-a-day Faith (A606). The aura is
>   the dealt Vicar's (`rite.aura.tiles` 4, `faithPerS` 3, A607). The owner's default (2026-11-12) keeps the aura at these values. The rate is about ten times a sermon
>   listener's, so one return day could convert many seats, and it merged at those values (a change is a follow-up PR); a seat next
>   to a returned cover gains no Faith (accepted in R-Q3). R's status-log line for #521 is a one-line docs PR, merged by R when green.
> - The owner granted, after the fact (2026-11-12), R's one existing-test edit in #515: `apps/client/e2e/screens.spec.ts` lock-pick
>   snap wait 5 s to 20 s (assertion unchanged). Any other existing-test edit still needs a grant asked of the orchestrator first.
> - #245 (old round-8 canon PR, no shared history with the base) was closed by the owner's word; its branch still exists.
> - I9 (conversion: Faith, `conversion.faithAt`, sermon hold at the bell) was built by R on `claude/story-i9-conversion`
>   (DECISIONS A606), now merged. The owner wants the Vicar to ring the bell every 60 s; the number belongs in `balance.json` and GDD 3.23 only.
> - The finisher holds three owner grants, all for #441 only: the `invariants.test.ts` seed offset, the `npcChores.test.ts`
>   `heldBySnare` edit and the `npcChores.test.ts` line 75 `+ 2` to `+ 3` (the `walkCap` source change was refused). It reported
>   `npcChores` 12/12 runs passing; its full server suite was still running, and #441 is not merged. S3's work is done; S3 was told to target `claude/story-part2`, not this branch. Nothing is archived unasked.
> - Nothing from `claude/story-part2` has gone to the production base. Merging it there deploys and needs the owner's say-so.
> - 25 PRs were open on 2026-11-12 (22 drafts into the production base). Triage (git only, nothing changed): the finisher's #435, #437,
>   #440, #441 are current; seven are clean but old (#444, #430, #431, #425, #422, #397, #442); seven conflict (#447, #445, #443, #432,
>   #429, #428, #426); #245 has no shared history with the base; #464 duplicates the story branch. On 2026-11-12 the owner answered "default on all questions", read as: change nothing. #245 was closed earlier; the other 21
>   stay as they are, and the finisher keeps its four.
> - R's status-log PR #523 for #521 is merged; R has no open PRs and waits only on R8 (the map revamp). "Default on all questions" does
>   not authorise merging `claude/story-part2` into the production base: that still needs the owner's explicit word and green CI.
> - The finisher reports it squash-merged #438 (x16, `act()` tick wait) into the production base as `0c3550b` on
>   what it describes as the owner's direct "merge" instruction; the orchestrator did not do or see that
>   instruction. Confirm it was intended.
>
> ## Round-10 lanes the orchestrator owns (2026-11-12)
>
> The owner asked the orchestrator to find archived sessions with unmerged PRs, bring them back until the map revamp, and
> "become the owner" of them, answering their questions with its own decisions. Unarchived and briefed (bring the PR up to
> the base, CI green, list owner sign-offs in the PR description, merge nothing into the base, no existing-test edits without a
> grant asked of the orchestrator, report by message): 10S `session_01M5mAcWM6iFP4icHHeKca4Z` (#447), 10T
> `session_01M5mAcUmmE2mPSi934vv6Gw` (#445), 10F `session_01M5mAcUJforvFMyeRQoDBwy` (#429, plus GDD 3.14 and A286), 10H
> `session_01M5mAcVEtsFr2jS1mBpRknV` (#444, #430), 10D `session_01M5mAcXTCbXtKaAJRgkS8ow` (#422), 10C
> `session_01M5mAcVzBNTaHxVatNhaVLo` (#426, #432), 10X `session_01M5mAcXMS5b7bZYzzwMzzpW` (#425, #431, #442, #397, and the
> ownerless #443), 10Y `session_01M5mAcWwzvbuS9YxojFNVor` (#428). Left archived: 10K, 10N and 10M (the finisher holds #440,
> #441, #435, #437). The orchestrator owns #471 itself. The delegation covers the lanes' questions; merging into the production
> base still deploys and still needs the owner's explicit word.
>
> The map revamp (owner, 2026-11-12) is the Blender work from the owner's local "Blender tools setup" session: the 3D
> HollowMere built from the owner's Meshy models on `overworld.json` (`tools/blender/`, first commit `753b563d`), and next the
> forest, Fenwood, Tin Gallery and Flooded Gallery from the scene JSONs. Anything that "waits on the map revamp" (R8, P5, P6)
> waits on that work.
>
> Grants and calls the orchestrator made under that delegation:
> - 2026-11-12, 10S #447: a test-helper grant. `npcHelpers.ts` `Human.id` resolves through `seatOf` (seat ids are fresh at Start), and
>   `flow.test.ts` lines 121 and 140 map session ids to seat ids. No assertion, value or timeout changes.
> - 2026-11-12, 10C #432: append `hardship` to `STORY_STREAMS` and fixed seed words to `hollowmere_winter.seedWords`. This is data,
>   and the orchestrator owns story mode. Carry the same two lines into `claude/story-part2` when it next takes the base.
> - 2026-11-12, Blender tools session (`session_01M5mAcVgjse9A6XHwQQXcDr`, runs on the owner's laptop): the orchestrator sent it
>   canon answers, and the owner OVERRULED all of them and withdrew them. The owner works with that session directly. The orchestrator
>   makes no canon calls for the map revamp. The sea door opens on a frozen lake; the village mere stays open water. Every Meshy model is HollowMere's (none BlackPine's); the interiors plan is #531. That session builds the woods and the rest of the map, and
>   uses the Meshy models by what they are (several are mislabelled, such as the "Tycoon's Manor").
>   Its commit `753b563d` (tools/blender only) was pushed straight to the production base; the owner was told and has not asked for a
>   revert. Its later builders go on their own branch with a PR.
>
> ## Sessions
>
> | Session | Id | State | Rule |
> |---|---|---|---|
> | Orchestrator | `session_01M5mAcY1JPqjhPmoZ8CZDFp` | running | never archive |
> | P0 design | `session_01M5mAcXYe29zVwSB7eQSKQ5` | #499 and #501 merged; waiting on owner for the open items above | keep until the open items are answered; check live status before archiving (an archive on 2026-11-10 was reversed) |
> | Story R: the Medium's rite and the 10X Vicar | `session_01M5mAcVS17U3fpdfpYurWpn` | spawned by P0; R1 to R5 and R7 built and merged (#502 to #511), R1 to R7, I9 and I9b are merged (#502 to #521); only R8 (story section) is left and waits on the map revamp | keep until R8 unblocks; never archive unasked |
> | P2 sections engine | `session_01M5mAcVG1b3xhGH76C6nUHz` | review-ready (E14) | keep until merged and summarised |
> | Skipped-PR finisher (#437, #438, #435, #440, #441, K6b) | `session_01M5mAcY9qbhZ1CAniTBr7xH` | everything pushed (2026-11-10). #438 merged into the base (see above). #437 not merged: `e2e` failed twice on `match.spec.ts:169` (hud-clock hidden at startMatch), re-run spent, needs the base's e2e history or the trace (artifact 13597323394, run 42422463137). #435, #440, #441 not merged: each needs a base re-merge, the full server suite, `pnpm auto` at 50 and CI. #440 also has the Handcuffs prices/grant (owner) and an npcStuck failure in match 30 (forest near wall (9,14)) needing a nav fix or routing to 10F/10X. #441 is about 680 lines, over the 400-line rule: owner decides split or accept | keep until these are resolved; never archive unasked |
> | Accounts plan | `session_01M5mAcXu65m2U47WM1R6aso` | draft docs PR #472 | keep while #472 is open; account PR sessions A2+ spawn after Q1 to Q14 |
> | S3 protocol and client cards | `session_01M5mAcVBQXcEMEdJztvpJ1j` | review-ready, status unchecked | check before archiving |
>
> Archived and done: S1, S2, S4, P3, P4, V1b, V2, V3, B6d2, the merge queue. The Farway sessions (tag `farway-now`,
> parent `session_01M5mAcXthXUMxUcnHeznJEZ`) are another project: leave them.
>
> ## Archival routine
>
> STOPPED on 2026-11-10 at the owner's request (disabled, not deleted; re-enable with `update_trigger enabled=true`).
> Scheduled task `trig_01GJNA6wgCRBQ5otxwnCgZaB`, hourly, fires into the orchestrator session. First routine
> `trig_01RZfT2Cp4tdespASrPWEx5o` is disabled: it had no connectors, so its sessions lacked the session tools.
> Rule: archive a session only if idle, untouched for over an hour, status bucket completed, work merged or
> nothing open, and not waiting on anything. Report in one line what was archived; stay silent if none.
>
> ## On hold
>
> P5 content and P6 other towns until the map revamp; section 5.4 until B6b to B6d; the final `pnpm auto` at 50.
>
> ## Art
>
> - 223-item asset list for Meshy (published artifact): https://claude.ai/artifact/YNbWzdECDePjFZua2BeEKd
>   (the artifact is the durable copy).
> - Poly Haven: `tools/blender/materials/polyhaven.lock.json` pins 49 textures and 1 HDRI, no 3D models. It covers
>   surfaces, not objects. Poly Haven models may stand in for props (`docs/round8/art.md` 5), each credited in
>   `CREDITS.md`.
>
> ## Resuming
>
> Read this file, `docs/story/status.md`, `docs/story/part2.md` and `docs/SESSIONS.md`, then list sessions
> (`list_sessions`, mine) before acting.
>

### Source file: docs/story/status.md

> # Story mode: status
>
> Each session appends to its own section only. Newest line last.
>
> > **Status, 2026-11-19:** `claude/story-part2` merged into the base with #538 (2026-11-12), so every pull request
> > logged below as merged into `claude/story-part2` is on the base. Still waiting: R8's `story.json` entry, P5 and P6, on
> > the map revamp (`docs/map-revamp/interiors-plan.md`); player sign-in (`docs/accounts/plan.md`) is not built.
>
> ## S1. Story content
>
> - 2026-11-06 S1: schema `story.ts`, `validateStory.ts`, wired into `validate.ts`, tests and a one-chapter `story.json` (Baker) ready; seams addendum 1a in README. Chapters 2 and 3 and `script.md` next.
> - 2026-11-06 S1: PR #450 now holds the schema, all three chapters and docs/story/script.md (the S4 fixture test needs three chapters); local checks green; merging on green CI.
> - 2026-11-06 S1: PR #450 MERGED into the integration branch (schema, validator, all three chapters, script.md). Merged on the green run of the previous head plus a clean merge of S4's suites; local content and story tests green on the final head. Open for the owner: Q-S1 (Killer chapter, default no) and the Thief-as-Bandit mapping (DECISIONS A401). S2 owes `story.enter` / `story.pickup` events (README 1a).
>
> ## S2. Story engine
>
> - 2026-11-06 S2 started. `enableStory`, fixed seeds and NPC ids, chapter-one fixed deal, title-card pause, `story.continue` as a queued command and the `storyOneHuman` invariant are written on `claude/story-s2-enable-story` (draft PR to follow once the suite is green). Seat handover and the beat runner come next; the runner waits for S1's schema, so it is coded against the README section 1 shapes (`sim/story/types.ts`).
> - 2026-11-06 S2 PR #452 merged: `enableStory` (one human seat, fixed seeds and NPC ids, chapter-one fixed deal, title-card pause, `story.continue` queued and consumed in `step()`), invariant `storyOneHuman`, GDD 3.34.
> - 2026-11-06 S2 PR #456 open (draft): beat runner, seat handover, chapter flow, `storyBeatsOnce`; S4's handover, death, full-story, replay and leak suites pass against it. `story.enter` / `story.pickup` and `story.start` from the lobby are in. Open gaps: item `spawn`, NPC `goTo` across scenes unverified, `cutscene`/`questStep` only emit bus events, end-card counters approximated.
> - 2026-11-06 S2 PR #456 MERGED: beat runner, `switchRole` seat handover, chapter flow, `story.start` from the lobby, `story.enter`/`story.pickup`, invariants `storyOneHuman` and `storyBeatsOnce`, GDD 3.34, ARCHITECTURE 5.13a, DECISIONS A415 to A417. `pnpm auto` at 50 was clean after PR #452. Open questions for the owner: none new; the handover moves the card, not the seat or its position (A415).
>
> ## S3. Wire and client
>
> - 2026-11-06: read the contract; branch `claude/story-s3-protocol-cards`. Protocol messages `story.start`, `story.continue`, `story.card`, `story.goals` added with `PROTOCOL.md` regenerated; story layer, chapter list, goals strip, mock server path (`?mock=1`), UI.md 14.61, DECISIONS A420, unit tests and `e2e/screens-story.spec.ts` at 390x844 and 1280x720 (screens written to the spec output). Contract additions: optional `chapterId` on `story.start` (replay); the end card's summary rows are the counter keys spelled out. Needs from others: S2 handles `story.start`/`story.continue` in `PartyRoom` and sends `story.card`/`story.goals` to the player's own client only; S1's `story.json` is read by `ui/story/catalog.ts` once it merges (the real title screen has no Story entry until then).
> - 2026-11-06: PR #453 merged (wire, cards, goals strip, Story entry, mock path). Next PR `claude/story-s3-catalog`: the title screen's Story reads `story.json` through `@wdi/content` (the real entry now shows); summary labels split camelCase counters. S2's `story.card` payload matches the wire type.
> - 2026-11-06: PR #457 merged (the title screen lists `story.json`). Against S2's merged start I ran the real flow: Story, Begin, the title card, the opening beat, the map cutscene, then the Baker's world with the goals strip. Found and fixed in `claude/story-s3-live`: the goals strip was mid-screen (`.wdi-glass` forced `position: relative`) and crowded the phone's top band (now one line at 600 px and under). New `e2e/screens-story-live.spec.ts` (real server, 390x844 and 1280x720). The role card is never drawn in a story room (the client skips the Lobby scene). Not yet exercised by me: chapters 2 and 3 and the end cards on the real server (S4's e2e owns that).
> - 2026-11-10: PR #459 merged (7b0faad0; CI green on 26ed246f, one unrelated `match.spec.ts` flake passed on re-run). The real-server spec `e2e/screens-story-live.spec.ts` is in the integration branch with the goals strip fix and the phone layout; the base's typecheck break in S4's fixture was fixed by #458. Nothing of S3's is open. Notes for whoever continues (corrected 2026-11-11, see the last line of this section): S2 honours `chapterId` on `story.start` since `19045d4e` (2026-11-08): `handleStoryStart` passes it to `replayFrom`, which replays a finished chapter of the save it is given (my earlier note here that S2 ignored it was true only on 2026-11-06); the client was not sending the save with a replay, which I fixed in #514. I verified only the start of chapter 1 on the real server in a browser (S4's `story-live.spec.ts` and bot cover the rest); the role card the server still sends is never drawn, by design, because story rooms skip the Lobby scene.
> - 2026-11-10 S3 FINAL HANDOFF (written 2026-11-10, with the later PRs added). Merged into the integration branch: #453 (protocol `story.start`, `story.continue`, `story.card`, `story.goals` with `PROTOCOL.md`; title, beat, end cards and the goals strip with all copy from the server message; the mock server path `?mock=1`; UI.md 14.54; DECISIONS A420), #457 (the title screen's Story reads `story.json` through `@wdi/content`), #459 (the real-server spec `e2e/screens-story-live.spec.ts`, the goals strip pinned top-left, the one-line phone strip at 600 px and under), #504 (status); #506 (this handoff), #512 (a status correction) and #514 (the Replay fix) followed on 2026-11-11. Checks: `pnpm lint`, `pnpm typecheck`, `pnpm --filter @wdi/client test` (1044 pass) after the last base merge; `screens-story.spec.ts` and `screens-story-live.spec.ts` at 390x844 and 1280x720 with `--trace off`; CI green on every merged head. Not done, for whoever picks it up: (1) Replay from the chapter list: done 2026-11-11 (#514), see the last line; the earlier version of this item, that S2 ignores `chapterId`, was wrong, and the first correction, that it only needed checking, missed that the client did not send the save; (2) in a browser I verified only the start of chapter 1 (title card, opening beat, map cutscene, the world with the goals strip); chapters 2 and 3 and the end cards on the real server are covered by S4's `story-live.spec.ts` and bot, not by a screenshot of mine; (3) the role card the server still sends is never drawn, by design, because story rooms skip the Lobby scene. No contract request of mine is unanswered and no Q-S question is open. One unrelated CI flake seen once on #459 (`match.spec.ts` 5-seat match, `hud-clock` hidden) passed on re-run and locally.
> - 2026-11-11 S3: ran Replay in a browser against the real server (a seeded save with `act1_line` and `act2_score` finished, Replay on `act2_score`). It started chapter 1: the menu sent `story.start { storyId, chapterId }` without the save, and for a guest the server replays only a chapter of the save it is sent back (`DeviceSaveStore.get` reads `resume`), so `chapterId` did nothing. Fixed in `StoryMenu.ts` (Replay sends `saves.read(storyId)` as `resume`); new `e2e/story-replay-live.spec.ts` fails without the fix (got `act1_line`) and passes with it. This corrects my 2026-11-10 notes, which blamed S2: S2's `replayFrom` was right, the client was not sending the save. Signed-in accounts (a server-side store) were not exercised.
> - 2026-11-12 S3: Replay for signed-in accounts could not be checked, because there is nothing to run: `saveStoreFor` (`apps/server/src/accounts/saves.ts`) returns the device store for every connection, there is no `AccountSaveStore` and no player sign-in on `claude/story-part2` (only the admin and Studio sign-in, which is unrelated), and `docs/accounts/plan.md` (draft PR #472) lists the account store as step A9, not built. For whoever builds A9: the plan has the server read the account's row on `story.start {resume: true}`, so a replay (`chapterId`) has to work through that store too, and the client's save seam (`StorySaveStore` in `ui/story/save.ts`) needs an account-aware `read`; my Replay fix (#514) sends the device save object as `resume`, which is right for guests only, and `e2e/story-replay-live.spec.ts` covers guests only, so an account-path bug would not fail it.
> - 2026-11-12 S3: full local e2e on `claude/story-part2` at 535b56f7 (which includes R6's #521): 93 passed, 1 skipped (`admin.spec.ts`, the opt-in live room), exit 0; every story spec passed, `story-replay-live.spec.ts` among them. Merged since (#523 to #526: R's status and A607 lines, the orchestrator's handoff, R8a's `arc.md` 3.4 draft) is docs only; #521 changes server rite logic and sends no new message, so nothing of S3's needs changing. When 3.4 reaches `story.json` (after P5's chapter 3 and R's E15 to E17), the client's chapter list and cards read it like any chapter; a new card kind or goals field would be a protocol change and needs an S3-style PR. Nothing else of S3's is open.
>
> ## S4. Tests and the bot
>
> ## Session ids (2026-11-06, from 6Z's spawn)
>
> | Session | Id |
> |---|---|
> | S1 content | `session_01M5mAcYksWgzPsPm5YnLFiq` |
> | S2 engine | `session_01M5mAcXF8pDpNfm2RgZDdpP` |
> | S3 wire and client | `session_01M5mAcVBQXcEMEdJztvpJ1j` |
> | S4 tests | `session_01M5mAcVY2kkDKs5HnxDqZRT` |
> | Orchestrator (this contract's author, not watching) | `session_01M5mAcY1JPqjhPmoZ8CZDFp` |
> - 2026-11-06 S4 started. Fixture (`apps/server/test/story/fixture.ts`) and `docs/story/test-plan.md` written against README 1 to 3; PR open as claude/story-s4-fixture. The fixture reads `enableStory` off `sim/auto/Auto.ts` by name and `story.json` off disk, so it compiles and the story suites skip until S1 and S2 merge. `WDI_STORY_REQUIRED=1` makes a missing engine a failure.
> - 2026-11-06 S4: PR #449 (fixture, test plan) merged. PR for the replay/full-story/death/handover/leak suites and the story bot opened as draft (claude/story-s4-suites); the suites skip until S1 and S2 merge. E2E specs wait on S3's UI.
> - 2026-11-06 S4: S1's story.json merged (3 chapters). Added the STORY_STREAMS = AUTO_STREAMS equality test (A401) and a seed-word coverage test, claude/story-s4-streams. The play suites still skip until S2's `enableStory` merges.
> - 2026-11-06 S4: S2's `enableStory` is merged (it lives in `sim/story/Story.ts`, stories come from a registry; the fixture registers story.json's story). Fixture now drives it directly and steps the way the room's clock does (a card pauses the world). `replay` and `leak` now run for real over the opening (title card, pause, 3 simulated minutes) and pass; `fullStory`, `death` and `handover` skip until the beat runner (`story.chapterEnd`) and `switchRole` land (feature-detected in `chaptersReady`). Event data key is `chapter` (not `chapterId`); noted in test-plan.
> - 2026-11-06 S4: #455 merged (stream equality, fixture on S2's engine; replay and leak run over the opening). New PR claude/story-s4-e2e: `apps/client/e2e/story-live.spec.ts` (390x844 and 1280x720, real server, --trace off) skips until PartyRoom handles `story.start` (S2), then runs by itself. S3's mock spec `screens-story.spec.ts` passes at both viewports here. Waiting on S2 #456 (beat runner, switchRole) for fullStory/death/handover.
> - 2026-11-06 S4: with S2 #456 merged, ALL story server suites run and pass (18 tests, none skipped): full three-chapter story, replay (same seed words, same digest), death in chapter 1 (chapter ends `failed`, chapter 2 starts), death in the last chapter, handover, leak (story.card/goals private, no public field names a chapter/goal). Fixture follows S2's API (`enableStory` queues the start). The fixture self-test now fails if the engine or content go missing. Remaining: live e2e (needs a browser run against a server that handles story.start, now merged: PR #458), the bot against a live server, `pnpm auto` at 50.
> - 2026-11-06 S2: fixed the integration-branch typecheck: `sim/story/types.ts` (re-exports Story/Chapter) and `queueStoryStart` (no double start) so S4's fixture compiles. `pnpm auto` at 50 after #456: 50/50 clean.
> - 2026-11-06 S4: `pnpm auto --matches 50 --seed 1` with the story code merged: 37 matches played, 0 failures in each (stopped by my 900 s timeout before match 50). The story bot, smoke-tested against a live server, saw chapter 1's title card and then hit its timeout (a full story is about 25 min of real time at 1x). #458 CI green on its head; merging after the integration-branch merge (S2's #460 supplies the types module and queueStoryStart; the fixture no longer needs either).
> - 2026-11-06 S4: #458 MERGED (live e2e at both viewports, fixture on S2's engine, bot fix). Full-story bot run against a live local server (`tools/bots/story.ts --chapters 3`, real time, no cheats): `{"ok":true,"started":[ch1_baker,ch2_watchman,ch3_bandit],"ended":[all three],"problems":[],"cards":18,"reason":"finished"}`, exit 0, about 18 min. The live e2e continues past the title card only to the world; a failed-chapter end card is covered by the server death test, not in a browser.
> - 2026-11-06 S4 FINAL HANDOFF (all assigned work is merged; stopping early, nothing is waiting on S4). In the integration branch: `apps/server/test/story/` (fixture, replay, fullStory, death, handover, leak, streams, fixture self-test; 18 tests, none skipped, they fail if S1's content or S2's engine go missing), `apps/client/e2e/story-live.spec.ts` (real server, 390x844 and 1280x720, `--trace off`; S3's mock spec `screens-story.spec.ts` also passes at both), `tools/bots/story.ts` with `pnpm bots:story` (exit 0 = all three chapters finished; a full run took about 18 min real time), and `docs/story/test-plan.md`. Checks run: `pnpm lint`, `pnpm typecheck`, story suites, the live e2e locally, CI green on #458 and #461, `pnpm auto --matches 50 --seed 1` clean for the 37 matches played, the bot against a live server through all three chapters. Not done, for whoever picks it up: a browser run through a failed-chapter end card (the server death test covers it); a browser run past the title card through the beats; the bot plays by answering cards only, not by chapter goals (it needs no goals to finish). No bugs found in S1, S2 or S3 paths that remain open. The flaky `figuresInView.test.ts:77` CI failure seen once on an older head of #458 is not S4's and passed alone and on re-run. No DECISIONS rows were needed (A430 to A439 unused).
>
> ## P4. Achievements (E1)
>
> - 2026-11-06 P4 started (branch `claude/story-p4-content` from `claude/story-part2`). Read part2.md, questions.md, round10-plan 10E/E1, owner-brief, seams, GDD 3.28 (stub), the bus, `sim/story/`, the protocol and the client storage. Plan, three PRs: (1) content: `achievements.json`, zod schema, `checkAchievements`, GDD 3.28, DECISIONS A440 to A443; (2) server: `sim/achievements/` (a bus subscriber, one Step line), the private `achv` message, PROTOCOL.md, the per-message leak test; (3) client: the device record, a toast and a small view, e2e at both viewports with `--trace off`.
> - Waiting on B6 (not built, not in `achievements.json`): the Tribunal steps, for example `tribunal.open` (stand in the dock), `tribunal.verdict` with a dismissed finding (cleared), with a proven finding (convicted), the same as the accuser; B6b's theft fine and goods returned; B6d's end trial filing a murder charge. They are added when B6b to B6d merge. `petition.passed` and `manhunt.cuffed` exist today but name the accused, not a seat to credit, so they wait with the trial.
>
> ## P0. The arc (part 2)
>
> - 2026-11-06 P0: read part2.md, questions.md, part 1 (README, script), the Bible (Part 0, Book I, Book V.1), world-mode 9, the content files and `sim/story/`. Branch `claude/story-p0-arc` from `claude/story-part2`.
> - 2026-11-06 P0: `docs/story/arc.md` written: five chapters (the line, the stranger's score, the holy war, the works, the letter), sixteen sections on fourteen cards, the six other cards as scripted NPCs, the four part-1 chapters kept as sections, engine needs E1 to E14 for P2, the section schema for P1, questions Q-A1 to Q-A12. Draft PR against `claude/story-part2`.
> - 2026-11-06 P0 HANDOFF (stopping at the merge of PR #465, as briefed; P1 and P5 not started). For the owner: read `arc.md` sections 0 to 3 and answer Q-A1 to Q-A12 (each has a default). For P1: section 5 is the schema shape (chapter `cast`, `sections[]` with `roleId`, `vendetta`, `npcVendetta`, `startWhen`, `hitman.mark`, `end`; a spoken `line` action). For P2: section 4.2, E1 to E14; the ones that block act 1 are E1 (sections), E2 (the cast: the Thief and most of the cards are not in the 8-seat deck) and E7 (lines); E3 (no early win) blocks act 3. For P6: the arc's format is section 2's per-section list. Open risk: the Zealot's consequence rides on the meeting vote, which B6 retires (E13).
> - 2026-11-06 P4: PR #466 (content, GDD 3.28, A440 to A443) MERGED into `claude/story-part2` (one server test flaked, `constableFile.test.ts:104`, passed on the single re-run). Next PR `claude/story-p4-server`: `sim/achievements/run.ts` (a bus subscriber after `runEvents`, one Step line), the private `achv` message and its PROTOCOL.md row, `test/achievements.test.ts`, the A168 per-message audit extended in `leak.test.ts`. Contract note: `sim/Step.ts` gained one stage line (`runAchievements`), a locked file; the P4 brief owns `sim/achievements/` only, so the line is called out in the PR.
> - 2026-11-06 P4: PR #467 (server evaluator, private `achv`, leak audit) MERGED. Last PR `claude/story-p4-client`: the device record (`wdi:achv`, guarded), the toast layer, the Trophies view on the title screen, `e2e/achievements.spec.ts` at 390w and 1280x720 (`--trace off`).
> - 2026-11-06 P4 FINAL HANDOFF. In `claude/story-part2`: `achievements.json` (27 achievements, 4 trees: story, work, rest, trouble) with its zod schema and `checkAchievements`; `sim/achievements/run.ts` (a bus subscriber, one Step line); the private `achv` message and its PROTOCOL.md row; the client record, toasts and Trophies view; GDD 3.28; DECISIONS A440 to A443. Checks run: lint, typecheck, content, server and client suites, the leak audit with an `achv` case, e2e. For P3: the end screen's earned achievements can read `readEarned()` from `apps/client/src/ui/achievements/store.ts` (ids to day earned) and titles from `@wdi/content/data/achievements.json`. For P5: a chapter id rename breaks `checkAchievements` on purpose (story steps name `ch1_baker` and so on); update `achievements.json` with it. Waiting on B6 (not built): `tribunal.open` (stand in the dock), `tribunal.verdict` with a dismissed, proven or murder finding, B6b's theft fine and goods returned, B6d's end-trial filing; `petition.passed` and `manhunt.cuffed` name the accused, not a seat to credit, so they wait with the trial. Open: whether an account should gate a node on its parents server-side (A440). Not done: a browser run of the toast against a live server (unit-tested on the bus; the mock path has no `achv`).
>
> ## P1. The section schema
>
> - 2026-11-06 P1 started on branch `claude/story-p1-schema` from `claude/story-part2`. The owner took the defaults on Q-A1 to Q-A12. Built: `ArcStory`/`ArcChapter`/`Section` and the `say` action (spoken line, arc E7) in `schemas/story.ts`; `story.json` moved to chapters of sections (act1_line = ch1_baker + ch2_watchman, act2_score = ch3_bandit, act4_works = ch4_activist; the text is unchanged except the new chapter setups and summaries); `validateStory.ts` on the arc (cast fit and membership, vendetta ownership with the mail's exception, `npcVendetta`, `needsCard`/`needsScene`/maps, `hitman.mark`, ids unique across the story, `say` by, and the coverage of every card behind `full: true`). The engine still reads `story`: `storyPlays()` gives it one part-1 chapter per section, which P2 retires. Server fixture `loadStoryFile` reads that view instead of the raw file (a one-function change in S4's path). Checks: content 280/280, server story 18 (16 passed and 2 skipped when the files run together; handover and leak pass alone, the same EADDRINUSE port clash as on the base), client 1027/1027, lint, typecheck.
>
> ## P2. Engine (part 2)
>
> - 2026-11-07 P2 started (owner answers A515/A517: a failure replays the section once; the Vicar's ghost may be played briefly; no Medium resurrection; the save is a device save behind an interface an account can replace). PR 1 `claude/story-p2-sections` (E1 sections, E7 `say`): `sim/story/units.ts`, `Story.ts` reads the arc, `actions.ts` speaks lines, GDD 3.34, A589 (renumbered from A555 at the base merge), `test/story/sections.test.ts`. Next: replay-once of a section, the save interface, the cast (E2), the NPC Killer's vendetta (E4), then E3, E5, E6, E8 to E10.
>
> - 2026-11-08 P2: #479 (sections, `say`) MERGED. PR 2 `claude/story-p2-replay`: a failed section replays once in place (A579, GDD 3.34), `replayUsed` and the `replay` flag on the chapter events, death tests for the replay and the second failure. Next: the save port (accounts plan 5), then E2 the cast.
>
> - 2026-11-08 P2: PR #481 (replay-once) open, CI green, waiting on `pnpm auto` at 50. PR 3 `claude/story-p2-save` (stacked on #481): the save port (`accounts/saves.ts`: `StorySave`, `SaveStore`, `DeviceSaveStore`), `story.saved` at each arc chapter's break and `story.start {resume}`, GDD 3.34, A577. P3's client half is #477; the wire shapes match #477's `StorySaveWire`.
>
> - 2026-11-08 P2: #485 (save port) MERGED. DECISIONS: the production base took A576, so the replay row is renumbered A579 (A578 is V3's). PR 4 `claude/story-p2-cast`: E2 the cast (`castTable`, GDD 3.34, A580). Next: E3 no early win, E4 the NPC Killer's vendetta.
>
> ## P3. Story client (part 2)
>
> - 2026-11-07 P3 started (branch claude/story-p3-cards off claude/story-part2). Read the brief, part2.md, arc.md 5, the client story UI, A515-A517 (in open #470). No P2 PR or branch exists yet, so the new wire is proposed here. Plan, three PRs: (1) section and NPC-line cards (`story.card` kinds `section` and `line`, fields `sectionId`, `speaker`); (2) save and resume behind a `StorySaveStore` interface with a device implementation, the menu Continue; (3) the end screen with the five chapter summaries and the achievements earned. Map-bound content and the Medium rule: nothing built.
> - 2026-11-07 P3: PR #476 (section and NPC-line cards) open, CI running. PR 2/3 on `claude/story-p3-save` (stacked on #476): `story.saved`, `story.start.resume`, `StorySaveStore` + device store, Continue row, mock path, tests, e2e at both viewports, UI.md 14.54, A519. Read the accounts plan (#472) section 5 and 8 A1: the server half (SaveStore, DeviceSaveStore) is P2 and the accounts session. The Medium rule and map content: nothing built.
> - 2026-11-07 P3: #476 and #477 open (#476 CI green but e2e running; do not merge until P2 acknowledges the wire). PR 3/3 on `claude/story-p3-endscreen` (stacked on #477): the end screen (chapter summaries, counters, Lost mark, story achievements earned), A520. Next: wait on P2 and CI.
> - 2026-11-07 P3: PR #476 MERGED into claude/story-part2 (CI green; orchestrator granted merge). #477 and #478 wait on CI and the orchestrator. Follow-up owed once P2's engine lands: the catalog moves from per-section plays to arc chapters (card chapterId is the arc chapter id).
> - 2026-11-08 P3: #476, #477 and #478 MERGED into claude/story-part2. P2 #479 merged; follow-up branch `claude/story-p3-arc-catalog`: the menu and end screen list arc chapters (card chapterId is the arc chapter id), live e2e updated. Not built: the Medium rule, map content. Waiting on P2 for replay-once and the save server half.
> - 2026-11-08 P3 FINAL HANDOFF (everything I can build without P2 is merged; stopping until P2's engine PRs land). **Merged into `claude/story-part2`:** #476 section and NPC-line cards (`story.card` kinds `section` and `line`, `sectionId`, `speaker`; A518); #477 save and resume, client half (`story.saved`, `story.start.resume`, `StorySaveStore` + the device store `localStorage['wdi:story:save']`, the "Continue from Chapter N" row; A519); #478 the end screen (`story-finale`: chapters in order with summary, counters, Lost mark, story-tree achievements earned; A520); #482 the menu and end screen list arc chapters (A556). All with unit tests and e2e at 390w and 1280x720; `pnpm lint`, `typecheck` and `test` were clean before each. **What P2 must still emit or accept:** (1) `story.saved` `{ save }` at `story.chapterEnd` of a chapter's last section, the whole save (`StorySaveWire` in `@wdi/shared/protocol`: `v, storyId, nextChapterId|null, finished, handOn, replayUsed, summaries, rev, savedAt`), private to the player; the client keeps it and never rolls a slot back to an older `rev`. (2) `story.start { storyId, resume }`: re-validate `resume` server-side (the accounts plan, section 5) and start at its `nextChapterId`; the client sends the save untouched. (3) `story.start { storyId, chapterId }` for a replay: the engine ignores `chapterId` today. (4) `summaries` entries `{ chapterId, failed?, counters? }` so the end screen can mark a lost chapter and fill counters (the client also uses the counters of this session's end cards, so it works without them). (5) The final end card must have no `next` (it does today); that is what opens the end screen. **Known edges:** a section that names its own break `endCard` makes the client mark the whole arc chapter finished on the device (menu marks only; the save is the truth); the end screen shows all story-tree achievements earned on the device, not only this run's (the device record has no per-run mark; DECISIONS A520). **Not built, as instructed:** the Medium's resurrection rule, map content. The accounts session can replace the device store by implementing `StorySaveStore` (`apps/client/src/ui/story/save.ts`).
> - 2026-11-08 P2: E4 NPC Killer vendetta on `claude/story-p2-npcvendetta`: `npcVendetta` set per section, GDD 3.34, A582, `test/story/npcvendetta.test.ts`. E3 is PR #487 (Complete, awaiting merge).
> - 2026-11-08 P2: E3 no early win on `claude/story-p2-nowin`: `endMatch` holds a win before the last section (`holdMatch`, `story.win`), the section ends done. GDD 3.34, A581, `test/story/nowin.test.ts`.
> - 2026-11-08 P2: #487 (E3) and #488 (E4) merged. E5 fixed Hitman on `claude/story-p2-hitman`: `hitman: {mark}` turns the player at section start, GDD 3.34, A583, `test/story/hitman.test.ts`.
> - 2026-11-08 P2: #489 (E5) merged; #490 (E6) Complete awaiting merge. E8 night-power events on `claude/story-p2-nightpower`: `nightPower` from `applyPower`, GDD 3.34, A585, `test/story/nightpower.test.ts`.
> - 2026-11-08 P2: #489 (E5) merged. E6 heir section on `claude/story-p2-heir`: `startWhen` waits after the previous section, `inherit` event from `runInherit`, GDD 3.34, A584, `test/story/heir.test.ts`.
> - 2026-11-08 P2: #490 (E6) merged, #491 (E8) Complete awaiting merge. E9 on `claude/story-p2-readpick`: `story.picked` built; `story.read` NOT built (no reader exists server or client; A586 says why). `test/story/picked.test.ts`, a case in `test/lockpick.test.ts`.
> - 2026-11-08 P2: #491 (E8) and #492 (E9) merged. E10 company trigger on `claude/story-p2-company`: `story.company {with}` after `story.companyS` of shared scene time, GDD 3.34, A587, `test/story/company.test.ts`. **Open owner question (from the orchestrator, 2026-11-08): `story.read` is not built and GDD 3.26 is not changed.** The reader has no client or server code, and 3.26 says the server keeps nothing of what a seat read. A read event needs a new client-to-server message and a rule change, which is the owner's to decide. Until then a goal like "read the Clerk's columns" ends on a pick (`story.picked`) or an item (`story.pickup`).
> - 2026-11-08 P2: #493 (E10) merged. E11 NOT built: the server has no hiding mechanic (no hide spots, Check or Burst Out) and none of silentHide, witness, pickpocket, smoke, plantClue or crowbar-on-doors is in `handleAbility`; each is a main-game rules change, so it waits on the orchestrator or owner. E12 on `claude/story-p2-cutscene`: `cutscene` action plays, `meeting: true` rings the bell, GDD 3.34, A588, `test/story/cutscene.test.ts`.
> - 2026-11-08 P2: E14 staging on `claude/story-p2-staging`: `npcOrder goTo` gains `args.spawn`, the validator checks order, scene and spawn, GDD 3.34, A591, `test/story/staging.test.ts`. E10, E12 and E13 are in; E11's witness, pickpocket and smoke wait on the owner. E1 to E14 are done or held.
> - 2026-11-08 P2: #494 (base merge) and #495 (E12) merged. E13 on `claude/story-p2-e13`: GDD 3.20 prose corrected to `shareS` 160 s (data wins), A590. The silenced-vote consequence follows B6c (voting retires); the Zealot section's goal (arc.md 3.2) waits on it. Nothing to build.
>
> ## R. The rite
>
> - 2026-11-10 R started (brief `docs/story/rite.md`, PR #501; the owner took every default of R-Q1 to R-Q8). R takes DECISIONS rows A600 to A607. R1 (`claude/story-r-medium-card`): the Medium card, Seance and Seance Chalk retired (`retired: "A600"`), validators and `storyCoverage` skip them; GDD 3.1, 3.2, 3.10.
> - 2026-11-10 R2 (`claude/story-r-shade`, stacked on R1): the martyr is a shade from its death (A601): no roles, a living view, no ghost channel, until the next day. **Question R-Q9** (proposed default built): R-Q4 says a shade becomes a ghost at the next dawn, R-Q5 says no rite by the end of that day means no return. R2 reads the wait as ending when the next day (or the Final Night) begins, so the rite must be done the night of the death and the return is that morning. If the owner meant the end of the next day, only `rite/shade.ts` `DAWNS` and the return phase change.
> - 2026-11-10 R3 (`claude/story-r-rite`, stacked on R2): the Medium stands at `balance.json` `rite.site` (test site `forest_deep.wood_side`), an avatar with no seat; the shade begins the rite with `act.hold rite` within reach; it runs `rite.holdS`, uninterruptible; private `S2C.rite` (A602). The return is R4.
> - 2026-11-10 R4 (`claude/story-r-return`, stacked on R3): the return at the next day (or the Final Night) at the rite site on the Train's respawn path; the martyr due opens at the return; `flow.ascendedVicarCandidate` removed (A603).
> - 2026-11-10 R5 (`claude/story-r-buff`, stacked on R4): the 10X buff, the private effect `ascended` from the return to dusk: `rite.buff.speedFactor` speed, `rite.buff.maxHpFactor` maximum health (A604). Open R-Q10: a Final Night return keeps the buff to the end.
> - 2026-11-10 R7 (`claude/story-r-client`, stacked on R5): the client's rite: the shade's chip and toast, the banner, the prompt and hold at the Medium, the done and returned toasts; mock `?ghost=shade`; e2e at 390x844 and 1280x720 (A605). R6 waits on I9, R8 on the map revamp.
> - 2026-11-11 merged: #502 (R1) squash-merged into `claude/story-part2` on the owner's go, all checks green.
> - 2026-11-11 merged: #505 (R2) squash-merged into `claude/story-part2`, all checks green after two e2e races older than R were fixed in it (`skipOpening` waits for the HUD; `npc.spec` takes the Village's ejection of the Killer).
> - 2026-11-11 merged: #507 (R3) squash-merged into `claude/story-part2`, all checks green.
> - 2026-11-11 merged: #508 (R4) squash-merged into `claude/story-part2`, all checks green.
> - 2026-11-11 merged: #509 (R5) squash-merged into `claude/story-part2`, all checks green after a race older than R was fixed in it (`figuresInView` waits for the arriving figures too).
> - 2026-11-11 merged: #510 (R7) squash-merged into `claude/story-part2`, all checks green. R1 to R5 and R7 are all in `claude/story-part2`; R6 (waits on I9) and R8 (waits on the map revamp) stay open.
> - 2026-11-11 I9 (`claude/story-i9-conversion`, built by R on the owner's word): conversion at `conversion.faithAt`, the Vicar's sermon as its own hold at the bell (owner: a new verb), `Private.converted`, the Peaceful route recorded only (owner) (A606). Then R6.
> - 2026-11-12 merged: #515 (I9) squash-merged into `claude/story-part2`, all checks green; the sermon repeats after `conversion.sermonCooldownS` (owner), a listener gains once a day (owner); the lock-pick e2e snap wait widened for a starved CI renderer.
> - 2026-11-11 I9b (`claude/story-i9b-client`, stacked on I9): the sermon prompt at the bell (a tap of E still rings), its countdown, the toasts, and the dealt Vicar's converted count as a pill; mock `?vicar=bell`; e2e at 390x844 and 1280x720 (UI.md 14.63).
> - 2026-11-12 merged: #518 (I9b) squash-merged into `claude/story-part2`, all checks green. The owner granted, after the fact, the one existing-test edit of #515 (the lock-pick snap wait in `screens.spec.ts`, 5 s to 20 s, assertion unchanged).
> - 2026-11-12 R6 (`claude/story-r6-aura`, from `claude/story-part2` after #515): the dealt Vicar's conversion aura on the return day, `rite.aura.*`, private Faith through I9's `addFaith` (A607).
> - 2026-11-12 merged: #521 (R6) squash-merged into `claude/story-part2`, all checks green. R1 to R7, I9 and I9b are all in `claude/story-part2`; R8 waits on the map revamp. The aura's `rite.aura.*` numbers wait on the owner.
> - 2026-11-12 the owner kept the aura's `rite.aura.*` numbers as built (A607).
> - 2026-11-12 R8a (`claude/story-r8-section`, on the owner's word): `arc.md` 3.4 "The Strength of Ten" drafted after the Doctor's 3.3, engine needs E15 to E17, questions R8-Q1 to R8-Q6 with defaults (A608). The engine needs come next; the `story.json` entry waits on P5's chapter 3.
> - 2026-11-12 merged: #526 (R8a) squash-merged into `claude/story-part2`, all checks green.
> - 2026-11-12 R8b (`claude/story-r8b-shade`, stacked on R8a): E16 and the rite half of E17: a section's `shade: true` (the player's death as the waiting martyr is no failure; after the return it is), and the rite's stages on the bus (`rite.open`, `.begun`, `.done`, `.returned`, `.lapsed`); GDD 3.20 and 3.34. E15 (the shade handover) and E17's skipped section next.
> - 2026-11-12 merged: #527 (R8b) squash-merged into `claude/story-part2`, all checks green.
> - 2026-11-12 R8c (`claude/story-r8c-handover`, stacked on R8b; the owner chose "swap the two bodies"): E15, the shade handover (`story/shadeHandover.ts`): after the card handover the player's seat and the martyr's exchange places, life, health, corpse, figure and the shade's mark; GDD 3.34. E17's skipped section next.
> - 2026-11-12 merged: #529 (R8c) squash-merged into `claude/story-part2`, all checks green.
> - 2026-11-12 R8d (`claude/story-r8d-skip`, stacked on R8c): E17's skipped section: `onlyIf: 'shade'` on a section skips it, ended at once and not failed (`story.skip`), when no shade waits as it starts; GDD 3.34. R8's engine needs E15 to E17 are all built; 3.4's `story.json` entry waits on P5's chapter 3.
> - 2026-11-12 merged: #532 (R8d) squash-merged into `claude/story-part2`, all checks green. R8's engine needs E15 to E17 are all in; 3.4's `story.json` entry waits on P5's chapter 3.
>

### Source file: docs/round10/README.md

> # Round 10: world mode, the build
>
> > **Status, 2026-11-19:** Historical record, kept as written on 2026-10-29. Current state: round 10 paused on 2026-10-30; the pull requests open then merged between 2026-11-07 and 2026-11-12, and the steps still to build are in `docs/round10/part2.md`. `docs/SESSIONS.md`, "After round 11's plan", lists the lanes since.
>
> ## Context
>
> Round 9 designed world mode and wrote no code (`docs/round9/README.md`). The owner approved it, answered the
> questionnaire (`docs/round9/owner-answers.md`) and the follow-up form (`docs/round9/followup-4.md`), and on
> 2026-10-29 asked 6Z to start the round (DECISIONS A223):
>
> > start round 10s sessions, opus, sonnet, and fable towards the end to fix all other issues. autocompact the
> > sessions at 500k for all precise work, 800k on sessions that need more context, and 300k for testing, fixing,
> > organizing, etc.
>
> Round 10 builds the round-9 design. The pull requests, their files, tests and dependencies are
> `docs/round9/round10-plan.md`, as amended by `followup-4.md`, which wins where they disagree. This folder adds only
> what the plan leaves to the round: who builds what, on which model, at which context size, and the seams the
> sessions share (`seams.md`).
>
> ## The sessions
>
> There are eighteen sessions and 6Z. The owner added 10R (which builds its own design), 10S and
> 10V on 2026-10-30, and 10S's plan added 10N, 10K, 10T and 10M the same day (A276); 10S builds world mode once its plan
> merges. The plan's sessions 10A to 10E keep their pull requests (A1 to E2). 10A and 10D are split by
> model, because a session runs on one model and the plan gives them both.
>
> | Session | Model | Compaction | Pull requests | Starts |
> |---|---|---|---|---|
> | **10A. The slice's contracts** | Opus | 500k | A1 refusal reasons, A12 inventory slots, A7 sleeping (server); then K1 weapons and T4 town work (`scope.md` 4) | now |
> | **10F. The logic table** | Opus | 500k | A9 schema and validator, A10 the resolver, then D1 never-idle NPC seats | now |
> | **10H. The slice's rules** | Sonnet | 500k | A5 pacing, A6 weaker mobs; then A11 tools on piles, A13 inventory screen, A8 sleeping screen | now |
> | **10G. The refusal sweep** | Sonnet | 300k | A2 `rooms/` codemod, A3 `sim/` codemod (two parts), A4 refusal display | when A1 merges |
> | **10B. The law** | Opus | 800k | B1 to B8; then T5, crimes and the heresy trial (`scope.md` 4.5) | when A3, A6 and A10 merge |
> | **10C. Death's cost and arrivals** | Opus | 800k | C1 to C5 and C7; C6 after B6; then V1 to V4, the vendettas' steps (`scope.md` 4.7) | when A6 merges |
> | **10D. The living world** | Sonnet | 500k | D2 to D9 | when A11 and D1 merge |
> | **10E. Achievements and story** | Sonnet | 500k | E1, E2 | when B6 merges |
> | **10X. Fixes: server and rules** | Fable | 300k | every open issue left on the server, rules and content side | early, on 2026-10-30 (below) |
> | **10Y. Fixes: client and screens** | Fable | 300k | every open issue left on the client, copy and art side | early, on 2026-10-30 (below) |
> | **10Z. The final sweep** | Fable | 800k | S6: `DECISIONS.md`, the `gdd-map.md` check, cross-references, `PROTOCOL.md`, the integration log | last |
> | **10R. Role cards and the dashboard** | Opus | 800k | the design: `rolecards.md` and a clickable mock; then the build, R1 to R6 (`rolecards.md` 9 and 12) | 2026-10-30, at the owner's request (below) |
> | **10S. The scope census** | Opus | 800k | `scope.md`: every gameplay feature not yet built or assigned, its design, its wire rows and its pull requests; then world mode, W1a, W1b, W2 to W8 and M5 (`scope.md` 4.2) | 2026-10-30, at the owner's request (below) |
> | **10V. The missing verbs** | Opus | 500k | V1 the evidence verbs, V2 the cover-up verbs, V3 the hiding spots (`rolecards.md` 11.3) | 2026-10-30, at the owner's request (below) |
> | **10N. The new roles** | Opus | 800k | K6 snares, N2 the Child, T1 the Trades, N1 the Butler, N3 the Ranger, N4 the Thief, N5 the Medium, N6 the toggles, M2 the Wisp (`scope.md` 4) | 2026-10-30, wave 2 |
> | **10K. Kit and the wild** | Sonnet | 500k | K2 to K5, K7, K8 (`scope.md` 4.4) | 2026-10-30, wave 2 |
> | **10T. The town** | Sonnet | 500k | T2, T3, T6 (`scope.md` 4.5) | 2026-10-30, wave 2 |
> | **10M. Ghosts, talk and modes** | Sonnet | 500k | M1, M3, M4 (`scope.md` 4.6) | 2026-10-30, wave 2 |
> | **6Z. Orchestrator** | Opus | 300k | this contract, merges, spawning, the owner's questions | throughout |
>
> **Toward the end.** 10X and 10Y start when 10B, 10C and 10D have each opened their last pull request, and they keep
> going while those merge. Their work is everything the build leaves open: a review finding a session parked, a
> flaky or skipped test, an `NFY` tag whose system has since shipped, a "still waits" line in `GDD.md`, a failing
> `pnpm auto` invariant, the owner's playtest notes, the round-9 leftovers (the Studio NPC editor's save, verified
> end to end), and the stale draft #245. 10Z starts when every other round-10 pull request has merged.
>
> **Started early.** The owner started 10X and 10Y on 2026-10-30, while 10B, 10C and 10D were still building. Until
> those three finish, a fix in a path a live session owns, or in a file an open pull request touches, goes to 6Z first,
> and 6Z hands it to the owning session or grants it.
>
> **Role cards and the dashboard.** After playing on production on 2026-10-30, the owner asked for new role cards. On
> a desktop the card is a trifold that fills the screen; on a phone it flips panel by panel. It maps every button and
> every action, with each role's win conditions and lore. The owner also asked for a private dashboard for the chores,
> the inventory and everything a player doesn't need at a glance, in the style of round 11's questionnaire. 10R
> designs both, in `docs/round10/rolecards.md` (the owner's words open it) and a clickable mock. The owner answered on
> 2026-10-30 (`rolecards.md` 12):
> - 10R builds it in round 10.
> - The dashboard is the Satchel.
> - The paper covers the card and the Satchel only.
> - R1 and R2 start at once, and R3 follows them and B6c.
>
> **Every gameplay feature, in round 10.** On 2026-10-30 the owner wrote (A256):
>
> > Real quick how many rounds are you trying to stretch everything, for me round 11 is blender only really, every
> > gameplay feature (except bosses) should be added
>
> Asked which lists that covers, the owner chose "Also V1.5 and V2 gameplay". So round 10 builds every gameplay
> feature that is not built yet:
> - what V1 and world mode planned;
> - everything tagged round 11, NFY or "not yet";
> - the V1.5 list (GDD 3.10);
> - V2's gameplay: the Medium, bats, the bog lurker, crows and poison.
>
> The Beast boss with the Cave Gate, the first-person renderer and voice chat stay out. So do cosmetics, which are not
> gameplay, unless the owner adds them.
> - **10S** writes the census and the plan in `scope.md`. Its waves go to sessions whose lists have ended (10B, 10C, 10D)
>   or to new ones. Wave 1 went to 10F, 10H, 10D and 10Y; wave 2 to 10S itself (world mode), 10N, 10K, 10T, 10M, 10A,
>   10B and 10C (`docs/SESSIONS.md`, A276).
> - **10V** builds the verbs a role card shows that have no server behind them (`rolecards.md` 11.3).
> - Round 11 stays the Blender makeover (`docs/round11/README.md`).
>
> **Models.** The plan's rule holds: Opus for a pull request that sets a contract, touches role secrecy or needs
> judgement across systems; Sonnet for one that follows a merged contract; Fable, by the owner's call, for the
> fixes and the sweep at the end. A session may fan out Sonnet subagents for repetitive passes and keeps the design
> in the lead.
>
> ## Compaction
>
> The owner's three sizes (A223), by the kind of work:
>
> | Size | Work | Sessions |
> |---|---|---|
> | 500k | precise work: contracts and rules | 10A, 10F, 10H, 10D, 10E, 10V, 10K, 10T, 10M |
> | 800k | work that needs more context across systems or documents | 10B, 10C, 10Z, 10R, 10S, 10N |
> | 300k | testing, fixing and organizing | 10G, 10X, 10Y, 6Z |
>
> `autoCompactWindow` is read when a session's worker starts; editing a settings file mid-session changes nothing
> until the next start (6Z tested it on 2026-10-29). A worker restarts several times in a long session and reads
> whatever branch is checked out, so the size is set in two places:
>
> - `.claude/settings.json` on `claude/zen-turing-m1jnw0` holds **500000**, the default.
> - `claude/r10-tier-300k` and `claude/r10-tier-800k` are that branch plus one commit that sets the window. 6Z
>   spawns a 300k or 800k session from its tier branch, so its first worker starts at its size.
> - **A tiered session's first action is to put its window in `.claude/settings.local.json`**: it creates the file
>   as `{"autoCompactWindow": 800000}` (or 300000), or adds the key and keeps any keys already there. The file is
>   git-ignored and overrides `.claude/settings.json`, so the size survives a restart on a pull request branch.
>   Without it, 10G (spawned at 300k) read 500k after a restart on an A3 branch. After a container restart, the
>   session checks the file and writes it again if it is gone.
> - **A session never opens a pull request from its spawn branch.** Every pull request branch starts from
>   `origin/claude/zen-turing-m1jnw0`, so no tier commit reaches the base.
> - Compaction triggers at the window less 33k: 467k at 500k (10G's `autocompact_state` on 2026-10-29 reads
>   `effective_window` 480000, `threshold` 467000), so about 267k at 300k and 767k at 800k.
>
> The compaction summary keeps what `CLAUDE.md` "Compact instructions" lists. A session that resumes re-reads its
> brief and `seams.md` before its next edit.
>
> ## How a session works
>
> - **The spawn prompt** is "You are session 10X of docs/SESSIONS.md Round 10 (model, compaction size). Read your
>   brief there, then docs/round10/README.md, docs/round10/seams.md, docs/round9/round10-plan.md and
>   docs/round9/followup-4.md, and the design sections your pull requests name." 6Z adds the session's spawn
>   branch and its first pull request.
> - **One pull request per plan step**, a draft against `claude/zen-turing-m1jnw0`, under 400 lines, on a branch
>   `claude/r10-<step>-<slug>` (for example `claude/r10-a1-refusals`). `pnpm lint && pnpm typecheck && pnpm test`
>   clean before every push.
> - **The session drives its pull request to green**: it subscribes to it, fixes its CI, answers review, merges the
>   base when it falls behind, and writes "Complete" at the top of the description when it is ready. Then it sends
>   6Z one line through `send_message` to `@parent`: "10X: #NNN (step) complete".
> - **6Z merges**, in the order of `seams.md` 7, and messages each session whose gate opened. A session never starts
>   a step before the steps it depends on have merged; it may read and plan meanwhile.
> - **`GDD.md` changes in the same pull request** as the behaviour, in the section the plan names (the default of
>   plan 7, question 1, which A224 settles). 10Z only sweeps.
> - **Questions to the owner** go to 6Z in the pull request description or a message; 6Z asks the owner. A session
>   in doubt takes the design document's proposed default, says so in its description and carries on.
>
> ## The playtest gate
>
> After A13 merges, 6Z tells the owner the build is ready for the next playtest (plan 3). The owner's notes go to the
> balance lab and to 10X and 10Y. 10B, 10C and 10D build on, and none of them tunes a number the playtest is
> measuring.
>
> ## Status (2026-10-29)
>
> - The contract: this folder, the Round 10 section of `docs/SESSIONS.md`, A223 and A224, the GDD stubs 3.27 to
>   3.33, and the compaction default.
> - 10A, 10F and 10H start now. The rest start at their gates.
>
> ## Status (2026-10-30): paused
>
> Part 1 stopped on 2026-10-30 at the owner's request, and every session was archived. `part2.md` is the pickup list:
> - the state at the stop;
> - the open pull requests and the merge queue;
> - each session's remaining steps, handoff and id;
> - the owner's open questions;
> - how to resume.
>
> `wave2-briefs.md` keeps the four wave-2 briefs.
>

## 12. Full commit log (date, hash, subject)

Every commit, oldest first. Merge commits are shown with their subjects.


### 2026-10

- 2026-10-10 383e9633 Add master plan and design docs for Who Did It
- 2026-10-10 7eaefb23 Add quick mode, plugin-repo connection and owner decisions
- 2026-10-10 c3a56726 Record owner decisions: Phaser 4, hosting order, first playable, marketplace
- 2026-10-10 c95c8953 Add root monorepo scaffold and the parallel-session contract
- 2026-10-10 b3bf7f18 Add root tooling: eslint flat config, prettier, vitest base, CI workflow
- 2026-10-10 2118d176 Add Phaser 4 client scaffold with Boot scene and /health poll
- 2026-10-10 c1395812 Add SPRITES.md: atlas keys, directions, pivot manifest and placeholder key list
- 2026-10-10 2d7858b0 Add @wdi/shared: constants, metrics, dirFromVector, schema, protocol, rules
- 2026-10-10 6f70f179 Add NetworkService over @colyseus/sdk with typed protocol and reconnection token
- 2026-10-10 dc419dab Scaffold apps/server package
- 2026-10-10 989af6a9 Add DOM overlay: Landing, Lobby, RoleCard, mock network and self-hosted fonts
- 2026-10-10 b275a0d3 Add Pages deploy workflow and @types/node for the Playwright config
- 2026-10-10 4ca09292 Treat an empty VITE_SERVER_URL like an unset one and warn in the Pages build
- 2026-10-10 aa117add Add PartyRoom, /health, matchmake guard and @colyseus/testing tests
- 2026-10-10 d77449ed Record M0 spike results; correct ARCHITECTURE 5.1, 5.4, 5.5 where code forced it
- 2026-10-10 3ddcc295 Drop the optional uWebSockets transport so CI installs without SSH git access
- 2026-10-10 3739b201 docs: GDD calls made while encoding the content data; package README
- 2026-10-10 d01e3533 content: One Night Ultimate Baguette roles, decks, windows and winner table
- 2026-10-10 c5d1c1d1 content: the 15 scenes of WORLD 4.3 with frozen ids and ASCII grids
- 2026-10-10 24e5be47 content: palette, metrics, traits, roles, abilities, items, clues, tasks, balance
- 2026-10-10 38f9151f content: @wdi/content package skeleton, zod schemas and cross-file validator
- 2026-10-10 5b711b8c Add the Blender render rig, batch renderer, palettizer and calibration sheet
- 2026-10-10 6e6df6ea Add the sprite packer, anim generator and placeholder atlas
- 2026-10-10 92394668 Add Higgsfield prompt sheets, source manifest, credits, vendor terms list and the hero concept
- 2026-10-10 d129aab1 Add faction and trait icons as hand-written SVG
- 2026-10-10 0e83ea24 Merge branch 'claude/content-data': content data (Session C), PR #3 [merge]
- 2026-10-10 1b4d6af3 Merge branch 'claude/m0-server': server and shared (Session A), PR #1 [merge]
- 2026-10-10 178417a9 Merge branch 'claude/art-pipeline': art pipeline (Session D), PR #4 [merge]
- 2026-10-10 8ce00df0 Merge branch 'claude/m0-client': client and Pages (Session B), PR #2 [merge]
- 2026-10-10 50ceb45a Integrate the four session branches: seam fixes from the review
- 2026-10-10 a7357690 Record owner decisions: quick mode length accepted, NPC fill approved
- 2026-10-10 8ece52cd Open-source the AI art under CC0 and restore the Higgsfield concepts
- 2026-10-10 984d9d30 Register the decisions-round session in the coordination contract
- 2026-10-10 7e3a4cc8 Close open questions 1-15 (decisions round 3)
- 2026-10-10 5a85dac9 Calibration: toon ramp stops 0.30 / 0.70 and a die frame on the smoke sheet
- 2026-10-10 7829e0e8 Record the toon ramp stop change from PR #6 as decision A27
- 2026-10-10 0d74cf6f Register round 2 sessions: M1 finish, M2 movement, character art, UI design system, ROSW studio
- 2026-10-10 be49e81a Cite catalog ids and record ROSW studio status
- 2026-10-10 2ad7aae9 Format CREDITS.md with Prettier
- 2026-10-10 ec81813e Grid exporter, shared nav and collision, server movement, portals and scene-scoped views
- 2026-10-10 6881402b Finish M1: real Start, role cards from the server, shared protocol, swarm bots, e2e
- 2026-10-10 e41e2521 Sprite tooling: Feet pivots on every pass, tsx scripts, alpha bleed, contact sheet
- 2026-10-10 2a6f9d64 Villager: three concept passes and a hand-built 3-heads-tall block-out body
- 2026-10-10 f2bf3e77 Real-art asset manifest with the placeholder's keys
- 2026-10-10 103ff48e style.json: ui block (type scale, spacing, radii, grid) with schema; ASSETS 6.1 points at docs/UI.md
- 2026-10-10 5d31dcc9 UI mockups: Landing, Lobby, role card, HUD, Meeting and the dark loft with 1280x720 and 390 px screenshots
- 2026-10-10 dfef6d8c UI SVG assets: faction card frames (nine-slice, 24 px), vote stamp, bell, notebook tab, plate and loaf marks, glyphs
- 2026-10-10 f56e93c0 Client theme: tokens.css and components.css from palette.json, README, frame generator, theme-preview page and tests
- 2026-10-10 aed97137 UI design system: docs/UI.md (principles, tokens, components, frames, motion, contrast table)
- 2026-10-10 ca661a4b Client World scene, input, HUD, mock world feed, bot soak
- 2026-10-11 49398722 Art drop: villager body and overlay atlases replace the placeholder keys
- 2026-10-11 8d7ca1f4 Close the transit view window exactly, attach the world feed on room wire, greybox reachability test
- 2026-10-15 a98cc3ff Integrate round 2: one scene entry, one world start, numbers into content, review fixes
- 2026-10-15 8c163125 Merge branch 'claude/rosw-studio': catalog ids and ROSW studio status (Session J), PR #7 [merge]
- 2026-10-15 824c6d8a Merge branch 'claude/art-villager': villager character art and sprite tooling (Session H), PR #10 [merge]
- 2026-10-15 67c095ea Merge branch 'claude/ui-design-system': UI design system, tokens, frames, mockups (Session I), PR #11 [merge]
- 2026-10-15 b1136f0c Merge branch 'claude/m2-movement': M2 movement, scene sync and the first house (Session G), PR #8 [merge]
- 2026-10-16 80e607d5 Round 3 contract: pre-seed the M3 shared contracts, decide A30, brief seven sessions
- 2026-10-16 2f83d005 Round 3 contract: fold the verification findings, pre-seed the remaining seams
- 2026-10-16 c34d622e Rules: resolveVotes and checkWin as pure functions with tests
- 2026-10-16 5b1090ee World feed: bodies, clues, notebook, dead and the action verbs on both feeds and the mock
- 2026-10-16 c2e0eab8 Client: NetworkService room getter and event, meeting feed, router for Meeting and GameOver
- 2026-10-16 dfc7d251 Rebuild the villager masters, record their hashes, prettier-format assets/source
- 2026-10-16 f61fedea Add the M3 audio: eight CC0 SFX, one ambient loop, the audio manifest
- 2026-10-16 d74b841e SPRITES 8: real clue orientation, the props and vfx keys, the body frame
- 2026-10-16 efa049af Match flow: phases, meetings, votes, chat, win, game over, lobby reconnection, debug helpers
- 2026-10-16 18a783b4 Add the M3 copy deck (UI.md 14) and fix the bell toast in GDD 2
- 2026-10-16 40bc737b Bots: vote, report and kill behaviours, match soak, match e2e spec
- 2026-10-16 3f924dac Render the square props and the clue sprites through the rig
- 2026-10-16 e8beb792 Match flow: tests, docs (GDD marks, ARCHITECTURE 5.7/5.8, A31, Round 3 log K)
- 2026-10-16 8ae634df Add the playtest kit for the M3 exit; record A37
- 2026-10-16 252113dd Render the four M3 VFX sheets through the rig
- 2026-10-16 bae79f4d Shared rules: validateKill, segmentBlocked and the clue placement helpers
- 2026-10-16 0db4646b Docs: GDD 3.2 and 3.4 M3 lines, ARCHITECTURE 5.6 note, A32, Round 3 log L
- 2026-10-16 c2866681 Server tests for kill, clues, holds, report, bell and ghosts
- 2026-10-16 dfc10b28 Sim: kill, bodies, clues with decay and cap, Collect holds, report, bell and bandage
- 2026-10-16 0b70eeab Sim: ghosts walk through walls and locked doors, emitNoise moves to Noise.ts, new RoomSim fields
- 2026-10-16 67c3a6a8 Add the Round 3 log for Session Q to SESSIONS.md
- 2026-10-16 aca42b73 Pack the real clues, props and vfx atlases; point the manifest at them
- 2026-10-16 54a82c65 Body review sheet, docs and credits for the M3 art
- 2026-10-16 191a7a71 SESSIONS: round 3 log for P
- 2026-10-16 3f4bdb11 Client: meeting and game-over screens, the theme on Landing, Lobby and the role card
- 2026-10-16 850e2d0e World actions: prompt, hold, bodies, clues, props, night mask, ghost mode, Notebook, audio bus, themed HUD
- 2026-10-16 f73a551e Integrate round 3: footprints off the body tile, the Notebook tab, test fixes, wording
- 2026-10-16 7365c15a Merge branch 'claude/m3-playtest': M3 playtest kit, audio set, copy deck (Session Q), PR #14 [merge]
- 2026-10-16 fc5f17d5 Merge branch 'claude/m3-art': M3 art, rebuilt villager masters, clue sprites, props, VFX, body sheet (Session P), PR #12 [merge]
- 2026-10-16 4affea8d Merge branch 'claude/m3-bots': M3 bots that kill, report and vote, the match e2e, the soak (Session O), PR #13 [merge]
- 2026-10-16 8eb80b52 Merge branch 'claude/m3-meeting': M3 meeting, game over and chat screens, themed lobby screens (Session M), PR #17 [merge]
- 2026-10-16 c476cd6e Merge branch 'claude/m3-world': M3 world actions, bodies and clues on screen, night mask, themed HUD, Notebook (Session N), PR #18 [merge]
- 2026-10-16 58f8e1a8 Merge branch 'claude/m3-flow': M3 phases, meetings, votes, chat, win, game over, lobby reconnection (Session K), PR #16 [merge]
- 2026-10-16 5649abfa Merge branch 'claude/m3-kill': M3 kill, bodies, clues, Notebook, report, bell, Bandage, ghosts (Session L), PR #15 [merge]
- 2026-10-16 8581f3b4 Pages: build the client's workspace dependencies before the client
- 2026-10-16 8cad714f Railway: config-as-code for the server, build version from the host's commit
- 2026-10-16 975edcd9 Client: point the published site at the Railway server
- 2026-10-16 be332d88 Bots: a live smoke of a deployed server (pnpm bots:live)
- 2026-10-16 2f829e24 Server tests: voteAll waits for every client to receive the reveal
- 2026-10-16 c3c4ab00 Round 4 contract: the shared seams for quick mode and NPC fill
- 2026-10-16 d29b088b Round 4 contract: the Round 4 section, DECISIONS A39 and the last hooks
- 2026-10-16 d2af1183 Round 4 contract: verification fixes before the sessions start
- 2026-10-16 c00dcd67 Quick-mode audio: storm loop, creak and loaf_crack (CC0) with credits and saved licences
- 2026-10-16 d0ac57f6 Name pool review: two names out of register, register and cast rules in the test
- 2026-10-16 a93d5f24 Bots: a quick-mode brain (plate, sleep, window act, claim, other vote) with leak counters
- 2026-10-16 51914451 Quick mode rules: deal, night script, acts, dawn vote and winners (M3b)
- 2026-10-16 eaa22bea Bots: soak and live play quick mode (--mode onub)
- 2026-10-16 542c05a4 Copy deck: UI.md 14.12 quick mode and 14.13 NPC lobby
- 2026-10-16 cc76dd9d Lobby: mode chip, NPC seats and difficulty, settings sync, copy deck
- 2026-10-16 15795a72 Theme: HUD anchors carry the safe area, drop the hud.css override block
- 2026-10-16 5262e34f Name pool: Bert Hale shared the barn's name; the cast list gains the named places
- 2026-10-16 b61424a8 WORLD.md: the bakery row's plates, dead loaves and ledger, and the loft note
- 2026-10-16 8f117a97 GDD 2 lobby wording (practice line, settings panel) and ROADMAP 7.5 rows for M3b and M3c
- 2026-10-16 6f7a61d8 Quick mode server: deal, dusk, night Conductor, acts, dawn vote, winners and match log (M3b)
- 2026-10-16 329ea393 Playtest kit: M3b and M3c run sheets, scorecard sections, two form questions, a template note
- 2026-10-16 77aa0e19 SESSIONS.md: Round 4 log: Y
- 2026-10-16 9d495717 Quick mode client: dawn meeting, claims, plural reveal and end screen
- 2026-10-16 f27b24aa NPC fill: seats, lobby commands, scripted brain, tests and docs (M3c)
- 2026-10-16 28ef1fc5 Art: bakery props atlas, dark-loft images and their manifest entries
- 2026-10-16 a29fc48f Quick mode tests: rules against content, deal, dusk, night privacy and acts (M3b)
- 2026-10-16 eaa32dfd Round 4 log: S
- 2026-10-16 25d84844 Art: placeholder manifest gains props, vfx and the loft images
- 2026-10-16 1b77dba4 Client world: World adopts the deck, quick-mode prompts and holds; ?mode=onub mock script; world.spec covers the plate and the loft
- 2026-10-16 a5bc4753 Client world: the loft, the bakery props, the plate and window acts (quickMode helpers, LoftView, PropView, mates)
- 2026-10-16 023db27b Client world: quick-mode feeds and router (nightWake, nightSleep, nightReveal, props, mates, mode) and the Loft route; stop the input timer between screens
- 2026-10-16 68d5581d Client world: the copy deck of UI 14 in code (ui/copy/world.ts) and the Notebook, HUD and touch literals
- 2026-10-16 51ef27fa Restore ui/theme/README.md (not owned by this session; a formatter pass touched it)
- 2026-10-17 63013699 Docs: DECISIONS A42, SPRITES 5 loading notes for quick mode, Round 4 log: T
- 2026-10-17 6d84d3de Round 4 W: quick-mode and NPC e2e specs, soak workflow, CI timeout, grid reach test, docs
- 2026-10-17 1de2a9f2 Quick mode docs: GDD 3.11 (M3b) sentences, ARCHITECTURE 5.14 modules, DECISIONS A40, round 4 log R
- 2026-10-17 83da72c2 Art: rendered stand-ins for the four building exteriors and six tilesets
- 2026-10-17 1ed2656c Art: masters script, credits, manifest rows and docs for the round-4 art
- 2026-10-17 7cc7745f Docs: DECISIONS A46 and the round-4 log for the art session
- 2026-10-17 e7f92ce3 Round 4 log: W (bots, e2e, soak, CI), with the 30-minute main-mode soak result
- 2026-10-17 90197368 Merge branch 'claude/m3b-server': M3b quick mode on the server (Session R), PR #25 [merge]
- 2026-10-17 fdfa5f1b Merge branch 'claude/m3c-npc': M3c NPC fill on the server (Session S), PR #22 [merge]
- 2026-10-17 58dd9767 Merge branch 'claude/m3b-world': M3b quick mode, client world (Session T), PR #23 [merge]
- 2026-10-17 b6522687 Merge branch 'claude/m3b-meeting': M3b quick mode, client meeting and end (Session U), PR #21 [merge]
- 2026-10-17 14128453 Merge branch 'claude/m3c-lobby': lobby settings, NPC seats, network edge (Session V), PR #19 [merge]
- 2026-10-17 0cb2ec38 Merge branch 'claude/r4-bots': bots, e2e, soak and CI for both modes (Session W), PR #24 [merge]
- 2026-10-17 0c39ad92 Merge branch 'claude/r4-art': bakery props, loft art, placeholder manifest, stand-ins (Session X), PR #26 [merge]
- 2026-10-17 a2b15445 Merge branch 'claude/r4-content': quick-mode and NPC copy, audio, playtest kit (Session Y), PR #20 [merge]
- 2026-10-17 b3495d24 Integrate round 4: record A45 and A47, tick the vendor licence rows
- 2026-10-17 a0850ba8 Integration fix 2: run the quick-mode and NPC e2e specs against the real server
- 2026-10-17 281cc769 Round 4 integration log, round 5 owner decisions, independent match streams
- 2026-10-17 265bda93 Round 5 pre-seed: ONUB v2 contract and quick-mode compile cut
- 2026-10-18 34146e17 Round 5 contract: additive pre-seed, docs and session briefs (A50)
- 2026-10-18 e1b3b2b4 ONUB v2 (5A): fill the pure prep rules, with onubPrep.test.ts
- 2026-10-18 071c4176 5D: Night scene, lights-out screen, narrator and night sound (PR 1)
- 2026-10-18 0956fd4b ONUB v2 (5B): the pure night rules, acts, wake view, vote and winners
- 2026-10-18 99c5d1be 5I step 1: isometric projection, input and camera
- 2026-10-18 73d72191 ONUB v2 NPC seats: pure planner and runOnubNpc (prep, acts, claims, votes)
- 2026-10-18 d76403c7 ONUB v2 (5A): the quick-mode deal, role card and Evening Prep start
- 2026-10-18 00439834 5I step 2: depth and occlusion for static world sprites
- 2026-10-18 2b5357cb 5J (1/4): Hollowmere's Fenwood and Flooded Gallery, door moves, materials and lights
- 2026-10-18 66551085 L1: IsoCam rig, world-palette palettize, calibration sheet, palette and budget tests
- 2026-10-18 589a92ef 5I step 3: isometric tilemap reader, ground and static defs, manifest maps and modes
- 2026-10-18 0b89447d Deal the public main deck: dealMainDeck, dealDeck tests, deck-aware debug.deal
- 2026-10-18 03650a6d 5I step 3: keep manifest loading rules pure so they test without Phaser
- 2026-10-18 64513d2b 5F step 1: scene-scoped avatars under opaque handles
- 2026-10-18 a832ae79 5D: card table, night acts and what a waker learned (PR 2)
- 2026-10-18 25c94925 ONUB v2 (5B): the night Conductor, the act handler and onubClock
- 2026-10-18 cf31233c Round 5 (5C): the quick-mode kitchen, station room, hand and commit on the prep mock
- 2026-10-18 95958604 5J (2/4): Blackpine, the second map
- 2026-10-18 658531bb NPC routines: keyed streams, persona, stations, strolls, idles, reactions, night, votes and ready delays
- 2026-10-18 1a128fe2 5I step 4: the lighting layer
- 2026-10-18 3ce1e798 Round 5 (5C): the crates and pour mini-games
- 2026-10-18 9a535320 ONUB v2 bots: quick-mode planner, night leak monitor and ruin report
- 2026-10-18 63118937 Round 5 (5C): the slide and stoke mini-games
- 2026-10-18 b14f35fc 5D: Morning Rush, claims, Pantry vote, CRUST countdown and the Final Bake lines (PR 3)
- 2026-10-18 b76b27be ONUB v2 e2e, soak and docs: onub.spec rewrite, NPC quick case, ruin Monte Carlo
- 2026-10-18 f1b5a4cf 5K K1: isometric ground tilesets for both themes
- 2026-10-18 4a23137a 5J (3/4): the isometric tilemap exporter (SPRITES 10.12)
- 2026-10-18 2cb35b3f ONUB v2 (5B): the Morning Rush, CRUST, the reveal and game over
- 2026-10-18 f3b091de Knife after dark, Bell in grace and day, the Final Night hunt and forced meeting
- 2026-10-18 29d305ce ONUB v2 (5A): Evening Prep commit, clock and reveal; GDD, ARCHITECTURE, DECISIONS A52, log
- 2026-10-18 1acd0ed3 NPC tests, presence tests, the tell detector, the server CI job and the 5H docs
- 2026-10-18 43c79f24 5F step 2: cover pick, private card Ready, public looks
- 2026-10-18 56d5e48e Round 5 (5C): the lobby deck editor, bug #126, kitchen e2e, UI.md 14.12, A54 and the 5C log
- 2026-10-18 73b28a9d 5D: end screen, act log, ColyseusOnubFeed, night e2e, deletions and docs (PR 4)
- 2026-10-18 48d1e65e Restore the theme README that Prettier reflowed
- 2026-10-18 0e2b454b 5I step 5: interact pose, look ids, hunger prints, world.spec, docs and log
- 2026-10-18 76036668 5J (4/4): the map choice, A61 and the 5J log
- 2026-10-18 96bf587c 5J log: name PR #44
- 2026-10-18 bf957233 5M: credits and masters for 78 generations, SPRITES 11, ASSETS 6.3, A64, round-5 log
- 2026-10-18 cfde383a 5M: Gate C, Brick Oven candidates and ONUB review sheets
- 2026-10-18 ebff0e61 5M (M1-M4 art): ONUB rooms, kitchen, cards, cloche, portraits, onub_mini; loft removed
- 2026-10-18 40a52016 5M (M1-M3 tools): ONUB image build, card template, mini-game atlas, batch file, onub.test.ts
- 2026-10-18 4b50be20 5K K2: isometric kits for both themes, review-world.ts, style boards
- 2026-10-18 fd240c82 L2: base body, 22-bone armature and five clips, looks_spec, three-pass packing, placeholder looks
- 2026-10-18 8f8c890b 5F step 3: Impersonate changes the face only unseen
- 2026-10-18 cc6cb98b NPC stage: persona and night-power draws are main-mode only
- 2026-10-18 53858b3b Night powers, protections, Nightshade, Last Shot, Inherit and Hunger
- 2026-10-18 9169882b Main-mode screens: lobby deck list, HUD deck chip, look tags, reveal line, end panel, shot toast
- 2026-10-18 9958a257 Contract phase: remove the roster deal (rosters, standIn, assignRoles, rosterFor), cover and look required
- 2026-10-18 65a7ea05 5F step 4: client feed, avatar sprites, cover picker, seat picker
- 2026-10-18 849a35b3 Record 5G decisions (A58) and the round 5 log
- 2026-10-18 b317d46d 5K K3: props, props_hollowmere, spots, portals and clues for the isometric world
- 2026-10-18 6ce0190f 5M: retake the Champignon and Commis portraits and the mini-game cart
- 2026-10-18 a3808327 L3-L5 progress: costume pieces for all ten looks, 13 portraits, six ability icons, vfx with vfx_disguise
- 2026-10-18 f1989f21 5F step 5: contract phase, no public scene index and no foreign presence
- 2026-10-18 8e175051 Pack without extrude only frames that are finished, so unfinished art packs byte for byte as before
- 2026-10-18 6fc5fb70 Merge 5A (PR #27): ONUB v2 rules, server deal and prep [merge]
- 2026-10-18 fae3e60e Merge 5B (PR #28): ONUB v2 server night and morning [merge]
- 2026-10-18 22bb8c42 Merge 5G (PR #34): Main deck and Werewolf roles [merge]
- 2026-10-18 6d688f02 Merge 5H (PR #42): NPC routines and fixes [merge]
- 2026-10-18 d474fad7 Merge 5J (PRs #32, #38, #41, #44): Maps [merge]
- 2026-10-18 bd9e620e Merge 5I (PR #29): Isometric client and lighting [merge]
- 2026-10-18 1f69e7b1 Merge 5C (PR #37): ONUB v2 client prep, mini-games, deck editor [merge]
- 2026-10-18 05c06cb4 Merge 5D (PRs #31, #36, #39, #43): ONUB v2 client night, morning and results [merge]
- 2026-10-18 48db8941 5K K4: bld_hollowmere sliced buildings, slice.ts, the Gate A renders
- 2026-10-18 da68e1a1 Merge 5E (PR #30): ONUB v2 bots, NPC brains, e2e and soak (PRs 1-3) [merge]
- 2026-10-18 97f956e1 Tighten the kneel, lower the raised arm and the top swing key so every look stays in its cell
- 2026-10-18 9c2b7120 Integration seam: Lobby reads the final NPC skill and mode toggle ids (S1, 5C)
- 2026-10-18 13799337 Integration seam: the ONUB mock keeps the proofing perk in reveals() (S2, 5C)
- 2026-10-18 f3a15b8f Integration seam: a live room gets 5D's ColyseusOnubFeed (S3, 5D)
- 2026-10-18 336270fb Integration seam: a quick match loads its modes ['onub'] art (S8, 5M)
- 2026-10-18 70785c7c Integration seam: placeholder ManifestEntry carries maps and modes (S7, 5K)
- 2026-10-18 91236991 Integration seam: balance.onub.json npc.stepS for the Tourrier's second step (S4, 5E)
- 2026-10-18 d319a9d1 Shift the kneel back and lower the raise and the swing keys further so no frame leaves its cell
- 2026-10-18 7de10710 5K K5: props_blackpine and bld_blackpine
- 2026-10-18 f0e8a447 Integration seam: an ejected Gamekeeper aims before its killed; gameOver carries undealt and alsoWon (S5, 5G)
- 2026-10-18 528269a7 NPC Killer hunt ignores the scene dwell and the work draw
- 2026-10-18 073b987e Integration seam: isKillPhase reads abilities.json kill.phases (S6, 5H)
- 2026-10-18 dcce3a84 Keep the kneeling boot on the ground, move the magnifier to the left hand and lower the lamplighter's raise
- 2026-10-18 50d23fd3 Lower the toque crown so the baker's swing stays inside the cell
- 2026-10-18 d9aa8a60 5K K6: thumbnails, ambient loops, masters, docs, A62 and the log
- 2026-10-18 42d36d00 Integration seam: world.spec walks to the moved tavern doors; PropView drops the overworld fallback (S9, 5I/5J)
- 2026-10-18 0ce8db5b A63: the magnifier hand, the kneel and raise numbers, and the 400-credit share
- 2026-10-18 2aa57ac3 Art styles: ship 8-bit and low poly, HD reserved; ONUB image provenance (A79)
- 2026-10-18 d26f8fb6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r5-world-art [merge]
- 2026-10-18 15d5eb26 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r5-onub-art [merge]
- 2026-10-18 92022d87 Integration: an NPC Gamekeeper fires lastShotS after its aim starts (5G and 5H)
- 2026-10-18 a591858c Pack the Baker: char_baker and ovl_baker leave LEGACY
- 2026-10-18 5ab2341d Pack the Detective; contact sheets for the Baker and the Detective
- 2026-10-18 e4fa8884 Merge claude/zen-turing-m1jnw0 (art styles, A79) into the round-5 integration [merge]
- 2026-10-18 706ef950 Merge 5H follow-up (PR #42): NPC Killer hunt ignores the scene dwell and the work draw [merge]
- 2026-10-18 9790c8b6 Integration: prettier table alignment in CREDITS.md
- 2026-10-18 f61bb4df Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r5-char-art [merge]
- 2026-10-18 95cbde54 5M: low-poly ONUB style (art plan 1.9, A79); Google terms row
- 2026-10-18 b3c5267f 5K: low-poly art style for every world key (A79)
- 2026-10-18 3426cf47 L4: pack the other eight looks; the real villager leaves the real manifest
- 2026-10-18 83d28688 Low poly: every 5L key in assets/lowpoly (art plan 1.9, A79)
- 2026-10-18 9742f6eb Merge claude/zen-turing-m1jnw0 (round-5 integration) into claude/r5-world-art [merge]
- 2026-10-18 acc37d18 Review sheets for every look, the lineup, silhouettes and Gate B; the 5L log
- 2026-10-18 02024a0e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r5-char-art [merge]
- 2026-10-18 10fe7b79 5K: building footprints come from 5J's scene buildings[] only
- 2026-10-18 a7cc3db9 5M: Brick Oven pick D (99cad74c), rebuilt in both styles
- 2026-10-18 2d5730c5 5F: merge the round-5 integration base; extend the contract phase to 5G, 5H and 5J [merge]
- 2026-10-18 68d9d0c8 5F: Last Shot aim handler: S2C aim in the net layer, mock openAim, SeatPicker in World
- 2026-10-18 2d11ad87 Merge 5K (PR #40): world art, both art styles [merge]
- 2026-10-18 313f89a8 Merge 5L (PR #33): character art, ten looks in both art styles [merge]
- 2026-10-18 ba6d9038 Merge 5M (PR #45): ONUB art in both art styles, Brick Oven pick D [merge]
- 2026-10-18 712ada1c Integration: the ONUB DOM byte caps in budget.test.ts are MiB, as SPRITES 11 states
- 2026-10-18 12391101 Merge 5F (PR #35): avatars, public looks, covers, Impersonate, Last Shot aim [merge]
- 2026-10-19 a9152e60 Integration: three racy server tests wait for the message they assert
- 2026-10-19 bcb0e0ea Integration: a Last Shot announces the role at a reveal only for an ejected Gamekeeper
- 2026-10-19 d23d96d5 Integration: the opt-in e2e specs follow round 5 (avatars, night kills, the deck)
- 2026-10-20 db8a55fd Client: an 8-bit / Low poly art-style button on the landing screen (A79)
- 2026-10-20 687b5af4 ONUB: the dawn panel follows the phaseChange message; bots resend a refused claim
- 2026-10-20 06571303 Lobby: offer the quick-mode toggle in every live lobby (ONUB v2 is merged)
- 2026-10-20 f0554f19 Art-style switch: 8-bit and low poly at the click of a button (A79, A80)
- 2026-10-21 03d506fc Merge claude/zen-turing-m1jnw0: the art-style switch replaces the landing toggle (A79, A80) [merge]
- 2026-10-21 a60d855f Merge pull request #46 from groot99-droid/claude/r5-art-style [merge]
- 2026-10-22 2ddd766c Round 6 contract: docs/round6, SESSIONS round 6, ROADMAP M5b-M5d, DECISIONS A81, compact settings
- 2026-10-22 b04fc0c6 Pre-seed step 3: the server stubs and locked call sites (A81)
- 2026-10-22 128ab5d0 Pre-seed step 2: the round-6 content stubs (A81)
- 2026-10-22 f83f4198 Pre-seed step 1: the round-6 wire and schema (A81)
- 2026-10-22 9ede8c81 Pre-seed step 6: the soak workflow's auto job (A81)
- 2026-10-22 e9fee71c Pre-seed step 5: the tools/auto skeleton and the harness stubs (A81)
- 2026-10-22 bc21222b Pre-seed step 4: the client stubs and mount lines (A81)
- 2026-10-22 ac0409c2 Round 6 seams landed: seams.md reads as landed, the 6Z log lists the six commits
- 2026-10-22 0531dabc Round 6 audio: every sound comes from the ROSW sound library (A81)
- 2026-10-22 b0bbb051 Round 6 media: the owner's answers, the loading music class, the two release batches (A81)
- 2026-10-22 8252487d Merge pull request #47 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-22 ca4359d5 6A step 1: the sim clock (budget guard, carry, pause, effective scale) and its writer test
- 2026-10-22 3308ca90 Round 6 (6K): scene transitions with transitionS seconds
- 2026-10-22 2e090d27 Round 6 (6L) PR 1: music bus, audio settings and the sound settings panel
- 2026-10-22 168c47ea 6E step 1: resources, recipes, material items and the M5b craft checks
- 2026-10-22 20d75657 Round 6 (6K): loading screen with tips and the loading.* balance rows
- 2026-10-22 1cf39479 Round 6 (6L) step 2: music director, music.json mapping, GDD 3.18 music paragraph
- 2026-10-22 192ac5ac Make the standard NPC party's tick timeline independent of wall time
- 2026-10-22 dab4ef05 6A step 2: enableAuto, the auto command queue, the headless harness and a one-day match per mode
- 2026-10-22 acc79c3f Round 6 (6L) step 3: slot list for the owner, beds waiting on the library release
- 2026-10-22 50e134fe Round 6 (6L) step 3: CC0 beds for the lobby and the end screen
- 2026-10-22 1f5d068f Round 6 (6K): landing trailer, media budget test, manifest shapes, docs
- 2026-10-22 93ba3d06 6E steps 2 and 3: mobs, quest npcs and quests, mini-games, their checks
- 2026-10-22 4e44791c Cutscenes: rules, HollowMere and Blackpine openings, content checks, openingS (6J PR 1)
- 2026-10-22 035bdc7f Round 6 seams: balance.resources carries stackMax, not gatherHoldS (6E deviation 1)
- 2026-10-22 f9129601 6A step 3: determinism and clientless-dispose tests, the pnpm auto runner, GDD 3.19 and A83
- 2026-10-22 480993ed 6E step 4: small-profile nodes, per-profile craft check, GDD 3.14-3.16
- 2026-10-22 99edd21f Merge pull request #48: Round 6 (6L) music bus, director, settings panel, slot list [merge]
- 2026-10-22 d00b3d55 Merge pull request #50: make the standard NPC party's tick timeline independent of wall time [merge]
- 2026-10-22 e70c7970 Cutscenes: sequencer, caption layer and player on the mock (6J PR 2)
- 2026-10-22 357e7b8a Merge pull request #53: 6Z seams.md and m5b-data.md say stackMax, not gatherHoldS [merge]
- 2026-10-22 5cbd4b67 6M step 1: M5b nodes, held tools, glows and item icons in both styles (SPRITES 12, A95)
- 2026-10-22 7ba07f8a Round 6 (6K): merge the base, wire the trailer music and the Kitchen loading screen [merge]
- 2026-10-22 34d3b3e9 Cutscenes: the five death cutscenes, mock kill, e2e handoff spec and GDD lines (6J PR 3)
- 2026-10-22 3bfd4e5a Merge pull request #51: Round 6 (6K) loading screen, transitions, landing trailer, media budgets [merge]
- 2026-10-22 cefa63af Merge base into claude/r6-cutscenes [merge]
- 2026-10-22 115543d8 Merge cutscene data and base; mount the match loading screen in World preload [merge]
- 2026-10-22 c9a00186 Merge player branch into death cutscenes [merge]
- 2026-10-22 9e36ee25 Merge pull request #49: 6E M5b content (resources, recipes, mobs, quests, mini-games) and GDD 3.14-3.16 [merge]
- 2026-10-22 edb6e44f Merge pull request #54: Round 6 (6A) sim clock, all-NPC auto match, headless harness, pnpm auto [merge]
- 2026-10-22 05dc9eb1 Hold the ghost view until the death cutscene ends
- 2026-10-22 83a5dbdc Merge base into claude/r6-cutscenes [merge]
- 2026-10-22 101b06e1 6M step 2: M5b mobs (wolf, boar, bat, rat) in both styles (SPRITES 12, A95)
- 2026-10-22 cb2698d9 Round 6 (6G): creatures from the spawners, the FSM, the wolf's bite and kill, the NPC flee hook
- 2026-10-22 c1e5b7be Round 6 (6C): adminAuth, the GitHub login gate (config, signed state and token, routes)
- 2026-10-22 8f7e85b3 Round 6 (6H): the pure mini-game rules
- 2026-10-22 ba338795 Merge branch 'claude/r6-cutscenes' into claude/r6-cutscenes-player [merge]
- 2026-10-22 d3974302 Merge branch 'claude/r6-cutscenes-player' into claude/r6-cutscenes-deaths [merge]
- 2026-10-22 627cc5fb Round 6 (6B) step 1: the sim event bus, its emitters and the match event log
- 2026-10-22 ef0d49bf Round 6 (6H): quests, accept and turn-in through the command queue
- 2026-10-22 f354c75f 6M step 3: M5b quest givers in both styles (SPRITES 12, A95)
- 2026-10-22 3944cdd2 Round 6 (6G): dark sight, the lantern bit, the scene-entry fix, GDD 3.7/3.15, A89, log
- 2026-10-22 26d29b6f Round 6 (6H): station-task mini-games, the task hold, GDD 3.16 and A90
- 2026-10-22 6f7b9277 Round 6 (6H): lint, an if instead of a ternary statement
- 2026-10-22 ccfbdf8c Merge pull request #52: 6J PR 1 cutscene rules, openings and openingS [merge]
- 2026-10-22 48d1d3a0 Log the answered contract requests and close the 6J log
- 2026-10-22 12f5c7c9 Round 6 (6B) step 2: the seven invariants of auto-admin.md 5
- 2026-10-22 b42cda8a Merge pull request #56: 6M M5b art (nodes, held tools, glows, icons, mobs, givers) [merge]
- 2026-10-22 df0cccd8 Round 6 (6C): AdminRoom, the god view and the admin room tests
- 2026-10-22 1588bb2b Merge pull request #55: 6J PR 2 cutscene sequencer, captions and player [merge]
- 2026-10-22 5410078e Round 6 (6F): inventory, node pool, gather and craft holds
- 2026-10-22 a53bc516 Fix wire-timing race in onubNight test: wait for the error count before asserting
- 2026-10-22 ec6b18eb Merge pull request #57: 6J PR 3 death cutscenes, handoff spec and GDD lines [merge]
- 2026-10-22 b30b4ff6 Round 6 (6B) step 3: tools/auto checks and report, the soak auto leg, A84
- 2026-10-22 d17415de Wait for the quick-mode role cards before asserting them (CI load flake)
- 2026-10-22 492d45e3 Round 6 (6C): admin handlers, the per-tick snapshot, invariant and event feed, docs
- 2026-10-22 cf1650fb Merge pull request #62: onubNight wire-timing race, wait for the 422 before asserting [merge]
- 2026-10-22 e52198d1 Merge pull request #59: 6G mobs, the wolf kill, dark visibility [merge]
- 2026-10-22 0f48cf24 Merge the base (6G, #62) into the 6F branch; R17 allows npcNames, nodes and mobs [merge]
- 2026-10-22 e7fcab80 Wait for the wire message before reading it in the onub quick-mode tests
- 2026-10-22 161326fa Round 6 follow-up: act.light, the NPC creature flee line, the minigame stream, the quests reset
- 2026-10-22 e462842c auto: run.ts imports the round-6 checks (6B, confirmed by 6Z)
- 2026-10-22 da53645a R9 keeps the creatures idle: the night-leave test is not about the wolf flee
- 2026-10-22 ba499927 Merge base into claude/r6-admin-server [merge]
- 2026-10-22 b60d1f16 Merge pull request #63: 6B sim event bus, match event log, the seven invariants, soak auto leg [merge]
- 2026-10-22 071c50d3 Merge pull request #61: 6F inventory, resource nodes, gather and craft holds [merge]
- 2026-10-22 b059e596 Merge pull request #65: 6Z follow-up, act.light, NPC creature flee line, minigame stream, quests reset [merge]
- 2026-10-22 e09dbb28 Merge claude/zen-turing-m1jnw0 into the onub wire-timing fix [merge]
- 2026-10-22 b6130b97 Drain queued commands from a paused clock in stepsThisTick; drop grantDrainStep
- 2026-10-22 4100eb0c Merge base; quests and mini-games use sim/Inventory, stand-in removed [merge]
- 2026-10-22 5f3ec881 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-quests-minigames [merge]
- 2026-10-22 654dda2a Merge claude/zen-turing-m1jnw0 into the onub wire-timing fix [merge]
- 2026-10-22 1a87f7e2 Merge base (6B bus); feed hears ANY_SIM; admin.event test [merge]
- 2026-10-22 07ee0486 Keep the admin feed per kind (ADMIN_EVENT_KINDS); admin.event test emits a clue
- 2026-10-22 582c9eca Mini-games draw from the minigame stream; Win.ts owns the quest reset
- 2026-10-22 87358fec Merge pull request #64: fix wire-timing races in the onub quick-mode tests [merge]
- 2026-10-22 28480bb0 Merge pull request #60: 6H quests and station-task mini-games [merge]
- 2026-10-22 fd919bc6 Merge pull request #58: 6C GitHub login gate, AdminRoom, admin handlers and snapshot [merge]
- 2026-10-22 c449418d Round 6 (6D): admin route, sign-in, controls and the mock feed
- 2026-10-22 9666e8e6 Round 6 (6D): viewport grid, seat inspector, log pane, admin e2e, UI.md 14.23
- 2026-10-22 430b3cf6 Round 6 (6I): m5b e2e, UI.md 14.19, session log and A91
- 2026-10-22 ba341168 Round 6 (6I): M5b views, panels, quest log, mini-game modal and mock
- 2026-10-22 e0a00554 Round 6 docs: the sound library's release is SFX_2026_01; first-wave integration log
- 2026-10-22 2542ee11 Round 6 (6D): read the admin route with its callback token (flags), callback e2e
- 2026-10-22 e8761370 Merge pull request #68: 6Z docs, the sound library's release tag and the first-wave integration log [merge]
- 2026-10-22 53f922f7 6N step 1: stingers, narration bed, ambiences and music beds from the ROSW sound library
- 2026-10-22 4a377e2c Merge pull request #66: 6D admin client [merge]
- 2026-10-22 72445bca Round 6 (6I): land the granted contract requests, no stand-ins
- 2026-10-22 5f6b13fb Merge pull request #69: 6N step 1, library stingers, narration bed, ambiences and music beds [merge]
- 2026-10-22 8a1e348d Merge origin/claude/zen-turing-m1jnw0 into claude/r6-m5b-client [merge]
- 2026-10-22 1156a758 Merge pull request #67: 6I M5b client [merge]
- 2026-10-22 89401f80 Round 6 (6Z): the owner's opening cinematic, loop and theme; session 6Q; DECISIONS A98
- 2026-10-22 bac7e128 Round 6 (6Z): the owner's second cinematic replaces the first (Dreamina, 29 s)
- 2026-10-22 ff210446 6N step 2: the owner's tracks and field recordings from the ROSW sound library
- 2026-10-22 9bcc3fd4 media.md: the owner's sounds carry the catalog ids 6N's ingest gave them
- 2026-10-23 b83fd40d 6Q step 1: Intro scene, session flag and the intro video budget line
- 2026-10-23 183c4757 6Q step 2: intro e2e, UI.md 14.24 and the 6Q log
- 2026-10-23 e8a3ee16 A98: the lobby and trailer playlists are a pre-match music bucket
- 2026-10-23 b73ce0d4 6Q: live-server specs skip the opening cinematic
- 2026-10-23 18c8fd01 Round 6 (6Z): the owner's opening cinematic, loop and theme; session 6Q; DECISIONS A98 (#70) [merge]
- 2026-10-23 a95dca18 Round 6 (6P): NPC work visit walks back after a reaction; wire-wait hardening of three tests
- 2026-10-23 e530b1da 6N step 2: the four field-recording keys in AUDIO_KEYS
- 2026-10-23 ec0e8ed0 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 060b88c6 Round 6 (6P): the lobby and trailer playlists are a pre-match music bucket (A98); one budget constant for both music checks
- 2026-10-23 f6ff2b21 Guides: how to play, quick mode, host, admin; a help page beside the game; README says playable
- 2026-10-23 beb74525 ROADMAP M5b: the definition of done names the station mini-game, not an assigned task
- 2026-10-23 f74ab229 Guides: how to play, quick mode, host and admin manuals; a help page beside the game (#74) [merge]
- 2026-10-23 7b1a13e5 Merge origin/claude/zen-turing-m1jnw0 into claude/r6-intro [merge]
- 2026-10-23 38649b35 Round 6 (6P): pin every stream a day of play draws from in the standard NPC party; wait for the lobby roster in the NPC seat tests
- 2026-10-23 a46437b6 Round 6 (6P): standard NPC party pins every stream; NPC seat tests wait for the roster (as #75)
- 2026-10-23 48b67e51 Round 6 (6P): NPC test flakes, R3 and D3 (#75) [merge]
- 2026-10-23 617caf70 6N: ROSW media (step 2: the owner's tracks and field recordings) (#71) [merge]
- 2026-10-23 ba7f88ae Round 6 (6Q): opening cinematic (#72) [merge]
- 2026-10-23 18e3c8ce Merge origin/claude/zen-turing-m1jnw0 (ba7f88a: #75, #71, #72) into the integration branch [merge]
- 2026-10-23 e6551d0b Round 6 (6N): the Vicar's memorial video
- 2026-10-23 72b1e4fe Merge pull request #76 from groot99-droid/claude/r6-rosw-media-3 [merge]
- 2026-10-23 e8b649e8 Merge origin/claude/zen-turing-m1jnw0 (72b1e4f: #76) into the integration branch [merge]
- 2026-10-23 924c96c0 Round 6 (6N): the opening cinematic, intro.webm
- 2026-10-23 6a4445b7 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-rosw-media-4 [merge]
- 2026-10-23 5dbe879b Merge pull request #77 from groot99-droid/claude/r6-rosw-media-4 [merge]
- 2026-10-23 c10597a4 Merge origin/claude/zen-turing-m1jnw0 (5dbe879: #77) into the integration branch [merge]
- 2026-10-23 be71e973 Round 6 (6N): the Vicar's final words, voiced (A99)
- 2026-10-23 5bd6f223 Merge pull request #78 from groot99-droid/claude/r6-vicar-voice [merge]
- 2026-10-23 b400c5a6 Bots: the main-mode walker hunts through scene avatars, the quick monitor ignores the seat's own presence
- 2026-10-23 620261e9 Merge origin/claude/zen-turing-m1jnw0 (5bd6f22: #78) into the integration branch [merge]
- 2026-10-23 f145da05 Round 6 (6N): an explosion where the Vicar blows up in the intro
- 2026-10-23 bc8ab096 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-intro-explosion [merge]
- 2026-10-23 ed0d5a79 Merge pull request #79 from groot99-droid/claude/r6-intro-explosion [merge]
- 2026-10-23 e8473c72 Merge origin/claude/zen-turing-m1jnw0 (ed0d5a7: #79) into the integration branch [merge]
- 2026-10-23 d3b87406 Hotfix: the M5b layer painted the page background over the world
- 2026-10-23 80e61ab2 Intro: end the sound at once on Skip, and take a tap on the video
- 2026-10-23 e98b8880 Merge pull request #80 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 ef65ff96 e2e: the opt-in live specs follow rounds 5 and 6
- 2026-10-23 c827051c Merge origin/claude/zen-turing-m1jnw0 (e98b888: #80) into the integration branch [merge]
- 2026-10-23 c676964a e2e: party and smoke mark the intro seen and skip the opening
- 2026-10-23 a242dc25 The Killer NPC's kill-opportunity timer (A100)
- 2026-10-23 11168d19 Merge pull request #81 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 d1ab78ca Bots: a quick-mode card that lands before the lobby patch keeps its role
- 2026-10-23 349b7581 Music: the maps' intro tracks play once, in a new `opening` class (A101)
- 2026-10-23 d2d0be71 Merge origin/claude/zen-turing-m1jnw0 (11168d1: #80, #81) into the integration branch [merge]
- 2026-10-23 95cc94b9 Round 7 contract: the re-skin, parties and profiles, map intros, vendettas
- 2026-10-23 9bf592e0 Test: give the invariants ghost-case test an explicit 20 s timeout under full-gate load
- 2026-10-23 1b6d9943 Merge pull request #82 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 8f49dd2b Merge base into r7-parties-server [merge]
- 2026-10-23 75f99271 Round 7 (7D): party create options, device profile on the roster, party balance numbers
- 2026-10-23 a99d35f3 Trim the opening cinematic after the explosion and ship the landing loop (A102)
- 2026-10-23 08017855 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-intro-trim [merge]
- 2026-10-23 d9fbe468 Round 7 (7D): A108 and the 7D log
- 2026-10-23 e242da5a Length: each opening runs its intro track's measured length (A101)
- 2026-10-23 7c6f5f75 Merge the base after #82 [merge]
- 2026-10-23 c5258bad Theme pieces 1: pixel fonts, the night set, the gate on every stylesheet (7B, A106)
- 2026-10-23 efb641a3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 b2dc19a5 Round 7 (7D): the party list, GET /parties and the swarm's private party
- 2026-10-23 3864c1a2 The Daily Train: HollowMere's platform and the train events (A113)
- 2026-10-23 7c0927dc Vendettas PR 1: the four rows, the vendetta stream and the draw (GDD 3.20, A112)
- 2026-10-23 a314860d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-train [merge]
- 2026-10-23 69e91a41 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 e006abc9 Merge pull request #85 from groot99-droid/claude/r7-parties-server [merge]
- 2026-10-23 6f0abcab Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-intro-trim [merge]
- 2026-10-23 d916fafe Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 e8913efd Merge pull request #86 from groot99-droid/claude/r7-theme [merge]
- 2026-10-23 2e3eff97 The World scene plays the Train's pulses as sounds (A113)
- 2026-10-23 2e5c1de3 Theme pieces 2: the night glass components and the title (7B, UI.md 6)
- 2026-10-23 91130250 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-train [merge]
- 2026-10-23 81fd3ce5 Match screens PR 1: role card, HUD and log, notebook, settings on the night theme (7F, A110)
- 2026-10-23 c19981de Merge pull request #88 from groot99-droid/claude/r7-vendettas [merge]
- 2026-10-23 620b60bf Merge pull request #84 from groot99-droid/claude/r6-intro-trim [merge]
- 2026-10-23 bbc0e2a9 Cinema (2/2): HollowMere and BlackPine openings visit the rooms and caves (A101)
- 2026-10-23 cb13f1f8 Cinema (1/2): the cutscene player films other scenes on a stage (A101)
- 2026-10-23 ac86150f Match screens PR 2: loading screen, transitions, cutscene captions and Skip, the intro's Skip (7F)
- 2026-10-23 f0e90046 Lobby re-skin 1: columns A and C of the mockup (7E, A109)
- 2026-10-23 ea9fc404 Match screens PR 1: surfaces over the world use a night scrim measured against white (7F)
- 2026-10-23 2415c544 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into r7-pr1 [merge]
- 2026-10-23 f300474f Merge pull request #89 from groot99-droid/claude/r7-parties-server [merge]
- 2026-10-23 f5a68eab Lobby re-skin 2: column B, the map cards, art-style segment and deck editor (7E, A109)
- 2026-10-23 cbf9af5f Match screens PR 3: the M5b layer, pockets, crafting, quests and the mini-game modal (7F)
- 2026-10-23 97e22742 Test determinism: NPC work visit walks back after a reaction; wire waits in npc, onubNight, onubDeal; invariants ghost-case timeout
- 2026-10-23 01664247 Match screens PR 1: numbers stay Inter, Pixelify's 2, 5 and 8 blur at 12 to 16 px (7F)
- 2026-10-23 444ebde2 Vendettas: conversion and sabotage (GDD 3.20)
- 2026-10-23 6fb30604 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-train [merge]
- 2026-10-23 f51a3ef9 SESSIONS: the 7A round-7 log, PR 1
- 2026-10-23 95df4959 Merge the base into claude/r7-lobby [merge]
- 2026-10-23 0ca6e23a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-match-ui [merge]
- 2026-10-23 a2d1d175 Merge pull request #93 from groot99-droid/claude/r6-test-determinism [merge]
- 2026-10-23 393894f0 Menu of the mockup: Start dialog, code box, Settings, fixture (7C PR 1, A107)
- 2026-10-23 8fa22ca3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-match-ui [merge]
- 2026-10-23 054d48e4 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 b5c2192b Merge the base into r7-menu [merge]
- 2026-10-23 9b00c546 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-train [merge]
- 2026-10-23 69511658 e2e: the ONUB match's reveal no longer depends on the fast bots' votes
- 2026-10-23 22e3a639 Table screens 1: the meeting and the game over in the night theme (7G, A111)
- 2026-10-23 941a5702 Table screens 2: the seat picker, look tags, shot toast and over lists in the night theme (7G)
- 2026-10-23 fa38eb7e Vendettas: the doubted Vicar abstains, its note, Private.vendetta, the NPC goal hook
- 2026-10-23 3974760d Merge pull request #83 from groot99-droid/claude/r7-map-intros [merge]
- 2026-10-23 ef9001ac Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-match-ui [merge]
- 2026-10-23 08b8ad63 Merge pull request #91 from groot99-droid/claude/r7-lobby [merge]
- 2026-10-23 114b0efb Theme pieces 3: the DOM loop backdrop replaces the canvas one (7B)
- 2026-10-23 1419a5d3 Merge the base after #86 [merge]
- 2026-10-23 278676e9 Merge the base into claude/r7-lobby-b [merge]
- 2026-10-23 8031c552 Merge the base into r7-menu [merge]
- 2026-10-23 973ab9cc Merge base 08b8ad6 into claude/r7-match-ui [merge]
- 2026-10-23 45515cb6 Round 6 (6P): integration log entry and A97 (soak and e2e figures to follow)
- 2026-10-23 fd7f2989 Vendettas: sabotage moves to its own PR (2b) to keep PR 2 under 400 lines
- 2026-10-23 ec40d67b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 6aba257b Video: the cutscene player shows a manifest video full frame under the captions (A101)
- 2026-10-23 5500d714 Merge pull request #92 from groot99-droid/claude/r7-lobby-b [merge]
- 2026-10-23 e8fd0cc0 Merge pull request #87 from groot99-droid/claude/r7-train [merge]
- 2026-10-23 5f4c0a94 Merge pull request #90 from groot99-droid/claude/r7-match-ui [merge]
- 2026-10-23 855506cd Merge the base into r7-menu [merge]
- 2026-10-23 62876ca5 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 11def2af Menu: the profile, the friends list and Add friend for seat rows
- 2026-10-23 d22c8adb Merge pull request #96 from groot99-droid/claude/r7-theme [merge]
- 2026-10-23 2d46382a Merge base d22c8ad into claude/r7-match-ui [merge]
- 2026-10-23 96e720ae Bring in the backdrop commit (7B PR 3) [merge]
- 2026-10-23 86f10762 Table screens 3: the quick mode in the night theme (7G, A111)
- 2026-10-23 df9d494f Match screens PR 2: Skip, Begin and the notebook on 7B's glass classes (7F)
- 2026-10-23 431227f2 Merge pull request #98 from groot99-droid/claude/r7-match-ui [merge]
- 2026-10-23 aa273f94 Match screens PR 3: log entry (7F)
- 2026-10-23 a7818611 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 2e1557c1 Merge base 431227f into the table screens (7G) [merge]
- 2026-10-23 7624018f Merge the base (431227f) [merge]
- 2026-10-23 2b72230d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 b951a8dc Merge pull request #94 from groot99-droid/claude/r7-menu [merge]
- 2026-10-23 b49c499a Merge base b951a8d into claude/r7-match-ui [merge]
- 2026-10-23 0a1a88a4 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 f39c8c9b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 280fe1d6 Lobby: dress the three columns in 7B's glass classes
- 2026-10-23 3703e7cc Lobby: use 7C's addFriendButton, drop the stand-in
- 2026-10-23 7540f6fc The Vicar's memorial and the Ascended Vicar candidate (A113)
- 2026-10-23 e5268c18 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-train [merge]
- 2026-10-23 6e55983a Merge the base (b951a8d, 7C's menu) [merge]
- 2026-10-23 478f2177 UI.md 14.26: Change Mode goes with the quick mode (A115)
- 2026-10-23 2c640ab2 Round 7: the quick mode's removal and Crumb's Ovens' rooms (A115, A116; 7J, 7K)
- 2026-10-23 b962b596 Merge pull request #101 from groot99-droid/claude/r7-map-intros [merge]
- 2026-10-23 ad66e3df Merge pull request #99 from groot99-droid/claude/r7-match-ui [merge]
- 2026-10-23 553c2f43 Merge base into claude/r7-lobby-3 [merge]
- 2026-10-23 4e08472d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 0a1bedd7 Merge pull request #97 from groot99-droid/claude/r7-vendettas [merge]
- 2026-10-23 06d80e37 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r6-integration [merge]
- 2026-10-23 5aa6a5bb Vendettas: sabotage, the Activist against the company (GDD 3.20)
- 2026-10-23 595f1a75 Menu: Quit, the help page in the night palette, and the menu on the glass classes
- 2026-10-23 607ce71c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-menu [merge]
- 2026-10-23 d5ddd549 Help page: drop the quick-mode guide link (A115)
- 2026-10-23 b5c1927b The memorial adds no quick-mode reference (A115)
- 2026-10-23 701b7ef7 Merge pull request #104 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 af0336cb 7K PR 1: Crumb's Ovens' four station rooms as scenes (A116, A118)
- 2026-10-23 5edc593f Table screens: build the meeting and game over panels on 7B's wdi-glass-panel; wait for the Voted chip before voting (7G)
- 2026-10-23 7e718abd Revert the quick-mode re-skin (owner decision: the quick mode is removed, A115)
- 2026-10-23 9e393e01 The memorial follows the public look; runMemorial after runVendettas (A113) [merge]
- 2026-10-23 a2021c3b Remove the quick mode from the client (DECISIONS A115, PR 1 of 3)
- 2026-10-23 9a5a5957 NPC Killers walk toward their vendetta's place (GDD 3.20, 7H's hook)
- 2026-10-23 75c2e244 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-remove-quick [merge]
- 2026-10-23 9ae9711e Archive the quick-mode night-glass re-skin for a future quick mode (7G)
- 2026-10-23 3fb9de8f Fix: the match load no longer cuts off the map's intro track (A101)
- 2026-10-23 22cae1ba Lighting: the darkness layer follows a canvas resize (the owner's "shadow")
- 2026-10-23 bcac5873 7K PR 2: Crumb's Ovens' station props and hiding spots in both art styles (A118)
- 2026-10-23 1a089e63 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-ovens [merge]
- 2026-10-23 aeaecc9e e2e: the darkness layer covers the canvas after the opening is skipped
- 2026-10-23 87d41e61 Merge pull request #100 from groot99-droid/claude/r7-theme [merge]
- 2026-10-23 bfcad62a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 8684aae3 Vendettas: run a vendetta only while its seat holds the Killer card
- 2026-10-23 de4c7845 Merge pull request #102 from groot99-droid/claude/r7-lobby-3 [merge]
- 2026-10-23 ab1d0b7b Merge pull request #106 from groot99-droid/claude/r7-menu [merge]
- 2026-10-23 5b0ab8f1 adminRoom test: the tampered signature is always tampered
- 2026-10-23 d28aac23 Merge origin/claude/zen-turing-m1jnw0 into claude/r7-map-intros [merge]
- 2026-10-23 927221f8 7K PR 1: A118 and the round-7 log line, with the round-8 kitchen seed
- 2026-10-23 4d7f357c Mini-games: the board comment names their new folder
- 2026-10-23 25b85f23 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-ovens [merge]
- 2026-10-23 3c3217f9 Merge pull request #108 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 94c7ca7e The Vicar's martyrdom pays the task bar; a full bar wins (A131)
- 2026-10-23 b71264de Menu: the party list on Join Game and the invite pick on Start
- 2026-10-23 fb6a1470 Merge origin/claude/zen-turing-m1jnw0 into claude/r7-map-intros [merge]
- 2026-10-23 746a683f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-train [merge]
- 2026-10-23 054e6163 Vendettas: heist, the Bandit against the strongbox (GDD 3.20)
- 2026-10-23 f253d06f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 341656e0 Merge the base into the table screens: addFriendButton for the game over, quick mode out (7G) [merge]
- 2026-10-23 855476ab Menu: drop the landing trailer; the loop is 7B's backdrop and the menu starts the theme on the first tap
- 2026-10-23 8f419480 7K PR 1: Hollowmere's scene list in mapSites.test gains the four rooms (6Z's exception)
- 2026-10-23 1ce8e345 7K PR 2: a scene change cancels a hold on the same tick (6Z's answer)
- 2026-10-23 5578fffd Merge base ab1d0b7 (7E's lobby glass #102) into claude/r7-remove-quick [merge]
- 2026-10-23 1c4663d7 Archive the quick-mode night-glass re-skin for a future quick mode (7G)
- 2026-10-23 0a655d0d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-table-ui [merge]
- 2026-10-23 d8800c3b Revert "Archive the quick-mode night-glass re-skin for a future quick mode (7G)"
- 2026-10-23 011abd9c Point the 7G log and A111 at the archive branch (7G)
- 2026-10-23 4d45cb42 7K PR 3: the four stations as task nodes, and e2e/ovens.spec.ts (A118)
- 2026-10-23 3a07fc02 The martyr follows the public look; full-bar end tested (A131)
- 2026-10-23 ebe4fbfd e2e: enterWorld waits for the opening's Skip or the HUD clock
- 2026-10-23 4b9bd331 Merge pull request #105 from groot99-droid/claude/r7-map-intros [merge]
- 2026-10-23 67af0606 Merge pull request #107 from groot99-droid/claude/r7-vendettas [merge]
- 2026-10-23 1b2a9845 Merge pull request #111 from groot99-droid/claude/r7-ovens [merge]
- 2026-10-23 44d6a2b7 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-ovens [merge]
- 2026-10-23 9506b844 Merge pull request #95 from groot99-droid/claude/r7-table-ui [merge]
- 2026-10-23 136dca7f Merge pull request #110 from groot99-droid/claude/r7-menu [merge]
- 2026-10-23 c10525e1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-train [merge]
- 2026-10-23 031c2937 Merge pull request #112 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 5c6c1125 Theme: drop the landing trailer's unused rules
- 2026-10-23 591b60e1 Merge pull request #113 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 d10755c5 test(e2e): walk to the nearest footprint clue by position in world.spec collect
- 2026-10-23 22d2a112 Merge base 136dca7 (7G's table screens #95) into claude/r7-remove-quick [merge]
- 2026-10-23 adfc8f1b Vendettas: contract, the Hitman's mail (GDD 3.20)
- 2026-10-23 4c0214ec NPC routine: the vendetta goal keeps the dwell and the one-hop rule
- 2026-10-23 dfc94f9c Point sessions at the game's teardown in ROSW (udgt plugin)
- 2026-10-23 63441e2c Merge pull request #116 from groot99-droid/claude/r7-map-intros [merge]
- 2026-10-23 a71476f6 Merge pull request #103 from groot99-droid/claude/r7-train [merge]
- 2026-10-23 55de6514 Merge pull request #109 from groot99-droid/claude/r7-remove-quick [merge]
- 2026-10-23 2e2e4ba8 Vendettas: the contract's Accept button on its Notebook entry (GDD 3.20)
- 2026-10-23 d2e2ea77 Merge pull request #117 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 1ff7e98d Merge base d2e2ea7 (#116, #103, #109, #117) into claude/r7-ovens [merge]
- 2026-10-23 80e5a015 Vendettas: GDD 3.20 notes the contract button's roster gap
- 2026-10-23 c4871a6c Admin page in the night theme (7G, A111)
- 2026-10-23 f583427f Remove the quick mode from server, shared, content and tools (A115, PR 2)
- 2026-10-23 c518da89 Drop the quick-mode options from auto.test.ts (granted by 6Z)
- 2026-10-23 64f1eb20 Drop the quick-mode assertions of coverPick, invariants and train tests (granted by 6Z)
- 2026-10-23 c4c2d570 Merge pull request #120 from groot99-droid/claude/r7-table-ui [merge]
- 2026-10-23 2f8fba07 test(e2e): npc.spec follows the NPCs in sight and stops when the match ends early
- 2026-10-23 019036b8 style(e2e): prettier on npc.spec
- 2026-10-23 0ba524e7 Merge base into the integration branch (drops e2e/onub.spec.ts with the quick mode) [merge]
- 2026-10-23 55e8b82f docs: integration log with the soak results (e2e result pending)
- 2026-10-23 ddb6228c Merge pull request #114 from groot99-droid/claude/r7-ovens [merge]
- 2026-10-23 72dc851f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 1db51c69 Drop mode from the party listing assertions in parties.test.ts (quick-mode only)
- 2026-10-23 a41e0893 Merge base ddb6228 (#114, #120) into claude/r7-remove-quick [merge]
- 2026-10-23 95ef9098 Test: standardParty fixes the vendetta stream, so E1 is one day per set
- 2026-10-23 ccadc07d The martyr's boost lasts ten minutes; the day haze is softened (A121)
- 2026-10-23 925d02fc Merge branch 'claude/zen-turing-m1jnw0' of https://github.com/groot99-droid/Who-Did-It into claude/r6-integration [merge]
- 2026-10-23 2d051f18 Merge pull request #115 from groot99-droid/claude/r7-vendettas [merge]
- 2026-10-23 b72eb6c6 Merge pull request #122 from groot99-droid/claude/r7-ovens [merge]
- 2026-10-23 de48ae80 Merge pull request #119 from groot99-droid/claude/r7-map-intros [merge]
- 2026-10-23 1cb83440 Merge pull request #123 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 91722c6a test(e2e): party.spec waits for the second browser to boot (about 25 s under software GL)
- 2026-10-23 1cf2255c Merge pull request #121 from groot99-droid/claude/r7-remove-quick [merge]
- 2026-10-23 62c4068c Merge origin/claude/zen-turing-m1jnw0 into claude/r7-map-intros [merge]
- 2026-10-23 4c98818d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 3b34d252 Merge base 1cf2255 (#121, the quick mode removed) into the integration branch [merge]
- 2026-10-23 ff0b1059 docs: note the quick-bot fixes left with quick.ts
- 2026-10-23 0121b345 Remove the quick mode's music, loft tooling and sprite modes (A115, PR 3)
- 2026-10-23 9e7651e1 Merge pull request #124 from groot99-droid/claude/r7-map-intros [merge]
- 2026-10-23 d7611675 Merge pull request #125 from groot99-droid/claude/r7-vendettas [merge]
- 2026-10-23 18cea076 Docs: the 7A log lines in SESSIONS and A101's Open cell closed
- 2026-10-23 6b5a9a33 Record the quick mode's removal in the documents and asset records (A115, A117)
- 2026-10-23 bb63a1a4 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-remove-quick [merge]
- 2026-10-23 2f76dc7f test(e2e): admin.setup no longer carries a mode; the integration log's e2e result
- 2026-10-23 757b7df9 Merge pull request #126 from groot99-droid/claude/r7-map-intros [merge]
- 2026-10-23 55d0809a Remove the quick mode's rules from components.css (A117, 6Z's grant)
- 2026-10-23 9898fea2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-remove-quick [merge]
- 2026-10-23 6f3bc5d2 Vendettas PR 4: the four vendetta invariants, auto-50 clean on HollowMere
- 2026-10-23 96387a7d Merge pull request #73 from groot99-droid/claude/r6-integration [merge]
- 2026-10-23 9090c6a9 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-vendettas [merge]
- 2026-10-23 16ea76b1 Merge pull request #127 from groot99-droid/claude/r7-remove-quick [merge]
- 2026-10-23 6e5a91bc Merge pull request #128 from groot99-droid/claude/r7-vendettas [merge]
- 2026-10-23 c061fd58 Deal every seat its tasks at Start (7M PR 1, GDD 3.5, A133)
- 2026-10-23 05c1c853 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-minigames [merge]
- 2026-10-23 fb01754d 7M log: the sim/Npc import-order seam found in PR 1
- 2026-10-23 9a98fa15 PR 1: clear dealt lists in minigames.test.ts world() (granted by 6Z); round-7 seams.md
- 2026-10-23 d9459195 Round 8 contract: bodies, coin, motion and art (A134, A135)
- 2026-10-23 05fef43c Round 8 contract: Poly Haven materials for all three styles (A155)
- 2026-10-23 10c06478 Pick the deliverable up at a task's source (7M PR 2a, GDD 3.5, A133 (8))
- 2026-10-23 39a7aa9c Merge pull request #129 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-23 ef5abf68 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 766f8bd7 Round 8 ids: schema version 6, Private.body, death causes, status bits, anim and effect ids (8A)
- 2026-10-23 f055d106 Economy data for rent, quota, Faith, notices and HQ tiers (8D PR 1, GDD 3.23)
- 2026-10-23 edcd73a1 client: task spots, chore rows and the work-bar accessor (7M, PR 2b)
- 2026-10-23 34555682 client: the chores panel, the task prompts and the village's work bar (7M, PR 2c)
- 2026-10-23 9ff64b81 Placement test for HollowMere (8J step 1, art.md 4.1)
- 2026-10-23 73d35e37 Rumour ledger, the mailbag and Blackmail Notices (8D PR 2, GDD 3.23)
- 2026-10-23 00b1b500 Merge pull request #130 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 2ee7b466 8G step 1: creature hit points and the bite, hurt, death and flee clips
- 2026-10-23 feb89af1 8C: the purse, the stake and movePurse with scripConserved (GDD 3.23)
- 2026-10-23 02ac2888 Merge base into claude/r8-scrip [merge]
- 2026-10-23 a55cc20e Merge base (contract #130) into r8-hollowmere-rooms [merge]
- 2026-10-23 754569a1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic [merge]
- 2026-10-23 07296d27 8H: motion tokens with their reduced-motion zero, hover and press on every control
- 2026-10-23 323d86f9 8D: DECISIONS A139, the civic data calls (GDD 3.23)
- 2026-10-23 e8b23a66 Merge branch 'claude/r8-civic' into claude/r8-civic-rumours [merge]
- 2026-10-23 296e6d8f 8D: GDD 3.23 Rumours paragraph (the ledger, the mailbag, notices, the Gazette)
- 2026-10-23 ae5b24fa 8G step 2: a break for every resource node, played backwards on regrowth
- 2026-10-23 17dddaa0 8H: panels open and close, lists stagger in
- 2026-10-23 76ca41af 8I: the material library (roles, lock, fetcher, per-style materials)
- 2026-10-23 99610345 Inspect and the relations table, server side (8B PR 1, GDD 3.22, A137)
- 2026-10-23 1fc31a14 8H: activation motion: press flash, refused shake, pop, cooldown sweep, the E fill
- 2026-10-23 67f1fae7 Merge branch 'claude/r8-ui-motion' into claude/r8-ui-motion-panels [merge]
- 2026-10-23 02d4ba01 Merge the base (round-8 contract) into 8H [merge]
- 2026-10-23 59d9ad12 Merge branch 'claude/r8-ui-motion-panels' into claude/r8-ui-motion-activation [merge]
- 2026-10-23 7880da34 Placement: east-facing classes; HollowMere baseline screenshots (8J step 1)
- 2026-10-23 6bf5ce80 Needs for NPC seats: four needs on the bus and the tick (8E PR 1a, GDD 3.24, A140)
- 2026-10-23 ee1e6320 8C: the granted invariant-list line and the seams.md grant notes
- 2026-10-23 16c69e5c DECISIONS A145: HollowMere's rooms placed by rule (8J)
- 2026-10-23 9a320dd8 Add the dressing prop kind to the routines' ignore list (contract request, granted)
- 2026-10-23 66acbc77 Resolve multi-tile and numbered props by id tail and stem (contract request, granted)
- 2026-10-23 fb65fc2c Placement test for BlackPine (8K step 1, art.md 4.1)
- 2026-10-23 4431e36f DECISIONS A146 and BlackPine before shots
- 2026-10-23 4e7ff60c Characters drawn at the designed size, with the figureScale knob and the scale screenshots (8F, A141)
- 2026-10-23 cd302514 The taskDone sim event for round 8's wages (7M PR 2a, A133 (9))
- 2026-10-23 6ccee8fb 8G step 3: the round-8 effects as runtime particles
- 2026-10-23 1dc6549c 8H: scene transitions per portal kind, the station and climb covers
- 2026-10-23 006b4810 8D: drop the civic prop rows until their art lands (6Z); validate named props by prefix
- 2026-10-23 25cc22c1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx [merge]
- 2026-10-23 c598aeb7 Merge branch 'claude/r8-civic' into claude/r8-civic-rumours [merge]
- 2026-10-23 07cc1f4e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-breaks [merge]
- 2026-10-23 b32ffa85 Round 8 body: health, stamina, effects, the damage table, knockout and wake (8A)
- 2026-10-23 7a71614f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-body [merge]
- 2026-10-23 5f525fe1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-fx [merge]
- 2026-10-23 2dfc229c 8C: wages on taskDone (fake paid as real) and quest scrip (GDD 3.23)
- 2026-10-23 70707d43 presence.test: extend the AnimId table to the round-8 ids (6Z grant)
- 2026-10-23 ac5a5cb0 Merge remote-tracking branch 'origin/claude/r8-creatures-vfx' into claude/r8-creatures-vfx-breaks [merge]
- 2026-10-23 8b1f6546 docs(DECISIONS): A142, the 8A contract request is approved
- 2026-10-23 ef4af2f4 Merge branch 'claude/r8-creatures-vfx' of https://github.com/groot99-droid/Who-Did-It into claude/r8-creatures-vfx-breaks [merge]
- 2026-10-23 d61a0a7d 8D: rumour tests stand the mailbag in a fixture of their own; regenerate PROTOCOL.md
- 2026-10-23 3d98452d Add the tap mini-game kind for Deliver a letter (A151, GDD 3.16)
- 2026-10-23 20995910 8C: runEconomy takes 8D's one runCivic line (6Z's ruling)
- 2026-10-23 3f25ac4c Merge branch 'claude/r8-scrip' into claude/r8-scrip-wages [merge]
- 2026-10-23 aa5cee51 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-minigames [merge]
- 2026-10-23 0485c835 The BlackPine dressing kit: 30 props of kind dressing, in both styles
- 2026-10-23 e2b67c46 Place and dress all eight BlackPine rooms (art.md 4.1)
- 2026-10-23 021dac00 Merge pull request #131 from groot99-droid/claude/r8-body [merge]
- 2026-10-23 0d7275c6 8C: A138 records 8D's one runCivic line
- 2026-10-23 aa9830cd Merge branch 'claude/r8-scrip' into claude/r8-scrip-wages [merge]
- 2026-10-23 85da55e0 8B: inspect prompt, card and copy (UI.md 14.33)
- 2026-10-23 c4942868 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic [merge]
- 2026-10-23 850690c2 Merge branch 'claude/r8-civic' into claude/r8-civic-rumours [merge]
- 2026-10-23 bcf5db1a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-blackpine-rooms [merge]
- 2026-10-23 8f34cdcf Merge branch 'claude/r8-blackpine-kit' into claude/r8-blackpine-placed [merge]
- 2026-10-23 07b6167e Merge branch 'claude/r8-blackpine-rooms' into claude/r8-blackpine-kit [merge]
- 2026-10-23 a82bce44 The taskBar invariant (7M PR 2a-bis, A133 (10))
- 2026-10-23 aeda8609 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r7-minigames [merge]
- 2026-10-23 ae3b56c9 St Brannock's: dress the chapel by rule (8J, art.md 4.2)
- 2026-10-23 e8cdd52e Merge the round-8 base (021dac0, #131) into 8B inspect [merge]
- 2026-10-23 56e8720e Merge branch 'claude/r8-inspect' into claude/r8-inspect-ui [merge]
- 2026-10-23 a551de98 8B: the inspect card carries 8H's wdi-anim-panel and wdi-anim-list classes
- 2026-10-23 badad5c7 feat(sprites): node breaks on a 512 x 256 page, resident cap 6.1 (A142)
- 2026-10-23 a84609f6 feat(client): transport motion, doors, hatches, ladders, veils and the Train (8G step 4)
- 2026-10-23 fff7ab16 8H: shake the showing E prompt on a server refusal (granted World.ts line)
- 2026-10-23 6054f50a Merge branch 'claude/r8-ui-motion-activation' into claude/r8-ui-motion-transitions [merge]
- 2026-10-23 6138704d Round 8 body: the fists, the slingshot and the curing items go live (8A)
- 2026-10-23 03c90d51 Merge pull request #135 from groot99-droid/claude/r8-creatures-vfx [merge]
- 2026-10-23 1ce46887 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-ui-motion [merge]
- 2026-10-23 a028e08b Merge branch 'claude/r8-ui-motion-panels' into claude/r8-ui-motion-activation [merge]
- 2026-10-23 aa2ab31a Merge branch 'claude/r8-ui-motion' into claude/r8-ui-motion-panels [merge]
- 2026-10-23 ccf99bc3 Merge branch 'claude/r8-ui-motion-activation' into claude/r8-ui-motion-transitions [merge]
- 2026-10-23 080bb72e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into r8-pr2 [merge]
- 2026-10-23 a4233c31 Ambient townsfolk figures: spawn, routes, streams, figureNotSeat (8E PR 2a, GDD 3.24, A160)
- 2026-10-23 2885edbd Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-fx [merge]
- 2026-10-23 9283de1f The four-heads character base, layered costume pieces and signature props (8F, A161)
- 2026-10-23 57dbdfc3 8C: shops, the shop hold, act.buy and act.sell through movePurse (GDD 3.23)
- 2026-10-23 da3c3663 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters [merge]
- 2026-10-23 76da2529 8C: the shop panel, its rows and the Scrip copy (UI.md 14.34)
- 2026-10-23 a3878d83 Merge pull request #133 from groot99-droid/claude/r8-hollowmere-rooms [merge]
- 2026-10-23 bcf9140d Draw the BlackPine economy props: the tally rack, wayside altar and black market
- 2026-10-23 0cf3c92f Merge base a3878d8 (#133) into claude/r8-blackpine-rooms; placement.ts comes from the base [merge]
- 2026-10-23 ec0e29c1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-breaks [merge]
- 2026-10-23 c82806b3 Merge pull request #136 from groot99-droid/claude/r8-ui-motion [merge]
- 2026-10-23 cb3a11dd Merge branch 'claude/r8-characters' into claude/r8-characters-2a [merge]
- 2026-10-23 d92d3cb3 Moods for NPC seats: the mood, its idle and the routine weights (8E PR 1b, GDD 3.24, A140)
- 2026-10-23 83a5a6ee The cap probe, the four-heads metric and the ASSETS round-8 paragraph (8F, A161)
- 2026-10-23 389e88af Merge branch 'claude/r8-blackpine-rooms' into claude/r8-blackpine-kit [merge]
- 2026-10-23 ae3b1172 Merge branch 'claude/r8-blackpine-kit' into claude/r8-blackpine-placed [merge]
- 2026-10-23 80650f1d Merge the base (a3878d8, #133 and #135) into 8B inspect [merge]
- 2026-10-23 995bbc27 Merge branch 'claude/r8-inspect' into claude/r8-inspect-ui [merge]
- 2026-10-23 2d6109e7 Share a task's completion between the stations and the co-op hold (7M PR 4a)
- 2026-10-23 68a1cc6c The co-op hold: Shutter the windows joins the deal (7M PR 4b, GDD 3.5, A133 (11))
- 2026-10-23 2eda3cdd Merge pull request #145 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-23 a5b21208 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-transport [merge]
- 2026-10-23 917b9692 8C: the bank, act.bank and the heist's take into the strongbox (GDD 3.23)
- 2026-10-23 072b4145 Merge pull request #118 from groot99-droid/claude/sweet-maxwell-lmsiw3 [merge]
- 2026-10-23 f1397878 Round 8 body: the body seed stream, the knockout gates and the granted mobs tests (8A)
- 2026-10-23 64365f99 8I: the HD render path (--style hd, --textured, materials/hd.py, retexture)
- 2026-10-23 8f24a9e2 8I: pack HD renders unhalved (hd.ts) and the look-proposal sheet tooling
- 2026-10-23 16f140ab Merge branch 'claude/r8-blackpine-placed' into claude/r8-blackpine-economy [merge]
- 2026-10-23 d8687f3b Merge pull request #144 from groot99-droid/claude/r8-characters [merge]
- 2026-10-23 c7abf2cf refactor(client): TransportView box and square helpers
- 2026-10-23 21f83f71 Vane Manor art: library, Tin Co. cases, hearth and bedroom (8J, art.md 4.2)
- 2026-10-23 afdc5305 Vane Manor art: the new frames on one sheet, for review
- 2026-10-23 7c4fbf29 Vane Manor: the hall and upstairs placed by rule (8J, art.md 4.2)
- 2026-10-23 11aa035b Merge the round-8 base; Private.purse and bank follow Private.body (seams.md 1) [merge]
- 2026-10-23 c4b85805 Merge branch 'claude/r8-scrip' into claude/r8-scrip-wages [merge]
- 2026-10-23 fb6ecfb1 Merge branch 'claude/r8-scrip-shops' into claude/r8-scrip-bank [merge]
- 2026-10-23 2b8226d7 Merge branch 'claude/r8-scrip-wages' into claude/r8-scrip-shops [merge]
- 2026-10-23 363ecef9 Merge branch 'claude/r8-scrip-shops' into claude/r8-scrip-shop-panel [merge]
- 2026-10-23 d0b564cf The co-op hold on screen: hold E at the shutters, together (7M PR 4c, UI.md 14.38)
- 2026-10-23 2161e584 Ambient townsfolk: the creature-only death and the meeting line (8E PR 2b, GDD 3.24, A160, UI 14.36)
- 2026-10-23 d79dddbf Shared counter and bank frames for 8C; leave the altar and black market to 8J
- 2026-10-23 980fb5a7 Merge pull request #139 from groot99-droid/claude/r8-inspect [merge]
- 2026-10-23 d4a2b3f1 Round-8 addendum: the owner's teardown answers (A168, A169), sessions 8L, 8M, 8N
- 2026-10-23 c7e522d1 Merge 8C's scrip branch into the mugging branch (local, for PR 3) [merge]
- 2026-10-23 70281d91 Merge pull request #137 from groot99-droid/claude/r8-ui-motion-panels [merge]
- 2026-10-23 21961648 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-fx [merge]
- 2026-10-23 5f03a315 All five economy frames in props_blackpine, none in the shared atlas
- 2026-10-23 428927f4 Round 8 body: the bat test stays on the bat (8A)
- 2026-10-23 c28b600a St Brannock's: one `dressing` kind, art by id tail (8J, 6Z's ruling)
- 2026-10-23 a722ba9b Shops: the locked markers on the granted hooks; the apothecary note in economy.md 2
- 2026-10-23 8cbe4ba0 Merge pull request #165 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-23 838bfaed Merge pull request #140 from groot99-droid/claude/r8-ui-motion-activation [merge]
- 2026-10-23 56fed48d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-breaks [merge]
- 2026-10-23 8d3e0a37 Merge branch 'claude/r8-scrip-shops' into claude/r8-scrip-bank [merge]
- 2026-10-23 0e442235 Bank: the cracker pockets the heist's loot (6Z's ruling), GDD 3.23 and A138
- 2026-10-23 38267acd 8I: the HD art style in the client (texels, device gate, switch)
- 2026-10-23 7da23ae4 Anti-cheat 1: Blood reaches only the clients within range, and ghosts (8L)
- 2026-10-23 ebf0b084 Round 8 (8N, step 2): the first icon sheet for the owner's look sign-off
- 2026-10-23 fc4fa5cb Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-anticheat [merge]
- 2026-10-23 9197f6bb 8I: the HD manifest builder and the HD budget row
- 2026-10-23 93687747 Merge the chapel's `dressing` re-key; Vane Manor's frames go snake_case [merge]
- 2026-10-23 a0fa986b Merge branch 'claude/r8-hollowmere-manor-art' into claude/r8-hollowmere-manor [merge]
- 2026-10-23 dc72cb96 Merge branch 'claude/r8-scrip-shops' into claude/r8-scrip-shop-panel [merge]
- 2026-10-23 e64c6a8a Merge base into the material library; mirror test for env/kits.py [merge]
- 2026-10-23 ad81a9ed Merge claude/r8-hd into claude/r8-hd-render (base 838bfae via the stack) [merge]
- 2026-10-23 00456f84 Merge claude/r8-hd-render into claude/r8-hd-proposal (base 838bfae via the stack) [merge]
- 2026-10-23 9de73d00 Shop panel: the shop layer at a counter, the feed's purse, buy, sell and shopOpen, mounted in the World
- 2026-10-23 72309e27 Merge claude/r8-hd-proposal into claude/r8-hd-client (base 838bfae via the stack) [merge]
- 2026-10-23 da986ad7 Vane Manor rooms: one `dressing` kind, art by id tail (8J, 6Z's ruling)
- 2026-10-23 ba4f816a Merge claude/r8-hd-client into claude/r8-hd-budgets (base 838bfae via the stack) [merge]
- 2026-10-23 390e288b Round 8 (8E): the mugging roll (GDD 3.24, step 1 of 3)
- 2026-10-23 85ffff5f Mock world: ?scene=&spawn= starts the own seat in any scene (8J)
- 2026-10-23 7c3add69 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-fx [merge]
- 2026-10-23 fc2911f6 Rules step 1: matches of 20 to 25 minutes (phases.dayS 120 s, A171)
- 2026-10-23 f7701aaa A171: the dayS 135 medians timed from grace
- 2026-10-23 f6cae2ba Purse HUD: the own purse and its changes under the goal chip (UI.md 14.34.2)
- 2026-10-23 f8827b30 Round 8 (8E): the mugging, part one (GDD 3.24, step 2 of 3)
- 2026-10-23 8e628077 Round 8 (8E): the mugging prompt (UI 14.37, step 3 of 3)
- 2026-10-23 ffabe0a5 Anti-cheat 2: night sight on the server in every scene (8L)
- 2026-10-23 77e6d3ce 8D: Faith at the altar, the Indulgence and the Parish Seal (GDD 3.23, A139)
- 2026-10-23 1fe3ded2 The look sheet's tooling: the rough PBR + HDRI path, the `look` review mode, the texture strip
- 2026-10-23 f55b0dc6 8D: fence a notice at the black market for Scrip (GDD 3.23)
- 2026-10-23 59a6bed9 Round 8 body: the death cutscenes, the body HUD and the invariant bodyBounds (8A)
- 2026-10-23 31a0e6fb Merge pull request #150 from groot99-droid/claude/r8-inspect-ui [merge]
- 2026-10-23 7c99782f Merge pull request #147 from groot99-droid/claude/r8-ui-motion-transitions [merge]
- 2026-10-23 ea4adc7b Merge pull request #153 from groot99-droid/claude/r8-creatures-vfx-breaks [merge]
- 2026-10-23 07a4d540 Merge pull request #161 from groot99-droid/claude/r8-creatures-vfx-transport [merge]
- 2026-10-23 fcb08c23 Merge pull request #143 from groot99-droid/claude/r8-blackpine-rooms [merge]
- 2026-10-23 e525e97d Merge pull request #149 from groot99-droid/claude/r8-blackpine-kit [merge]
- 2026-10-23 18efffaf Merge pull request #151 from groot99-droid/claude/r8-blackpine-placed [merge]
- 2026-10-23 519949ba The eleven looks re-rendered on the four-heads base, with the review sheets and the cap of 8
- 2026-10-23 9e894a96 Rules step 2: the Final Night is a 45 s hunt, then the trial (finalNight.trialS 120 s, A191)
- 2026-10-23 fe17306f Coins on the ground: dropCoins, the pickup through the gather hold, economy.coinPickupS, GDD 3.23 and A138
- 2026-10-23 7abdd278 Round 8 body: the bat test stays put when the bat is over rock (8A)
- 2026-10-23 b8eaeff0 Anti-cheat 3: the vote delay, meeting.minVoteS (8L)
- 2026-10-23 4b39b578 Merge claude/r8-body-2 (the bat test fix) into claude/r8-body-3 [merge]
- 2026-10-23 71bd0d7f Merge claude/r8-body-3 into the body HUD branch [merge]
- 2026-10-23 f4d3f642 HollowMere's single-tile props pack with its buildings (8J, budget)
- 2026-10-23 17296716 Review shots: the chapel and manor drawn from bld_hollowmere (8J, budget)
- 2026-10-23 58a669ff Merge pull request #172 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-23 11f437ee Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-fx [merge]
- 2026-10-23 9339ad66 Format the placement test (Prettier)
- 2026-10-23 314a0a8a Merge the Prettier fix from claude/r8-hollowmere-chapel [merge]
- 2026-10-23 830e7035 Merge the Prettier fix from claude/r8-hollowmere-manor-art [merge]
- 2026-10-23 040b8b6c Merge the Prettier fix from claude/r8-hollowmere-manor [merge]
- 2026-10-23 2fde3017 The villager family: four townsfolk variants on the plain base, their data, manifest rows and docs
- 2026-10-23 ea76dbd0 Round 8 (8E): `ClueKind.scuffle` (granted by 6Z)
- 2026-10-23 a395d79b Round 8 body: the body check registers on import, and the World wears the body panel (8A)
- 2026-10-23 3593b5ee Rules step 3: the card-text drift test (A171)
- 2026-10-23 a898a403 Anti-cheat 1: apply 6Z's grants, byte-level Blood test, seams row (8L)
- 2026-10-23 5e285894 Coins in the M5b hold: the coins prompt and economy.coinPickupS cast, not resources.json
- 2026-10-23 9912de69 Merge branch 'claude/r8-scrip-shop-panel' into claude/r8-scrip-purse-hud [merge]
- 2026-10-23 332ce00c Rules step 4: card numbers generated from the data (A171)
- 2026-10-23 930b17f6 A171 and GDD 3.9: the Final Night share is measured on human playtests (6Z)
- 2026-10-23 2bae771c Round 8 body: the strike key and the pockets' Use buttons (8A)
- 2026-10-23 1debb965 Per-row PNG filters in the packer's encoder, and the character pages re-encoded once
- 2026-10-23 d9997b11 Merge the base (58a669f, #172) into claude/r8-body-2 [merge]
- 2026-10-23 4a29c74f Coins: the seat-free econ.coinsTaken bus event on a finished pickup (granted)
- 2026-10-23 4ee70769 Merge branch 'claude/r8-characters-2a' into claude/r8-characters-2b [merge]
- 2026-10-23 b95db850 Merge claude/r8-body-2 (the base at 58a669f) into claude/r8-body-3 [merge]
- 2026-10-23 1aa25378 Anti-cheat 2: apply 6Z's test grants; a new day part re-runs the views at once (8L)
- 2026-10-23 09e935d6 content: spelled-out card counts are tokens too (8M step 4, A171)
- 2026-10-23 d85f3486 Merge remote-tracking branch 'origin/claude/r8-anticheat-sight' into claude/r8-anticheat-replay [merge]
- 2026-10-23 31fd4131 Merge claude/r8-body-3 (the base at 58a669f) into claude/r8-body-4 [merge]
- 2026-10-23 002e91b9 Merge claude/r8-body-4 (the base at 58a669f) into claude/r8-body-5 [merge]
- 2026-10-23 e64cda66 Draw node_coins in both styles and play its break on pickup
- 2026-10-23 19ac974e Merge the base into 8C step 1 (A137 and A138 kept, taskBar beside scripConserved) [merge]
- 2026-10-23 acdfaeac Merge branch 'claude/r8-scrip' into claude/r8-scrip-wages [merge]
- 2026-10-23 90f30fad Merge branch 'claude/r8-scrip-wages' into claude/r8-scrip-shops [merge]
- 2026-10-23 bfd64e9f docs(round8): fold tonight's seam rulings into seams.md and teardown.md
- 2026-10-23 2a39a4fb Play the coins break only for a pickup in view
- 2026-10-23 93c2ca9d The Drowned Lantern and its back room, dressed by rule (8J, art.md 4.2)
- 2026-10-23 e89a4102 Merge branch 'claude/r8-scrip-shops' into claude/r8-scrip-bank [merge]
- 2026-10-23 9ef825be Merge branch 'claude/r8-scrip-shops' into claude/r8-scrip-shop-panel [merge]
- 2026-10-23 bb1e20a7 Merge branch 'claude/r8-scrip-shop-panel' into claude/r8-scrip-purse-hud [merge]
- 2026-10-23 cf3c7e48 Merge branch 'claude/r8-scrip-bank' into claude/r8-scrip-coins [merge]
- 2026-10-23 ac152671 The villager family rendered in both styles, with its sheets and the elder's cane
- 2026-10-23 8190f43b Low poly's posterise rounds in display space
- 2026-10-23 a203d465 Merge claude/r8-hd into claude/r8-hd-render (the posterise fix) [merge]
- 2026-10-23 76cd4556 HD: the shadow catcher stays out of the tile map and clears lit ground
- 2026-10-23 853b6ae5 HD packing: slices cropped to their box, static pivots scaled, look sheets at the right size
- 2026-10-23 3b30e528 Merge claude/r8-hd-render into claude/r8-hd-proposal (the posterise and catcher fixes) [merge]
- 2026-10-23 10a92084 Merge base into the material library (decisions log: A144 kept beside A146 and A166) [merge]
- 2026-10-23 30ea32f8 Anti-cheat 2: re-run the views only when night starts or ends (8L)
- 2026-10-23 dc1d3b9f Anti-cheat 4: a per-message leak audit, and seeds and build in the match log (8L)
- 2026-10-23 9518f35f Merge claude/r8-hd into claude/r8-hd-render (base 58a669f via the stack) [merge]
- 2026-10-23 19fc5002 Merge remote-tracking branch 'origin/claude/r8-anticheat-sight' into claude/r8-anticheat-replay [merge]
- 2026-10-23 0c0be69b Merge claude/r8-hd-render into claude/r8-hd-proposal (base 58a669f via the stack) [merge]
- 2026-10-23 8a3fbbf9 Merge claude/r8-hd-proposal into claude/r8-hd-client (base 58a669f via the stack) [merge]
- 2026-10-23 50363b75 Merge claude/r8-hd-client into claude/r8-hd-budgets (base 58a669f via the stack) [merge]
- 2026-10-23 4cb77935 Widow Vane's parlour and bedroom, dressed by rule (8J, art.md 4.2)
- 2026-10-23 44fa2616 A145: record the BLD_PROPS_MAPS props budget and 6Z's grants (8J)
- 2026-10-23 6b64e342 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters-2a [merge]
- 2026-10-23 86dea1d7 Merge branch 'claude/r8-characters-2a' into claude/r8-characters-2b [merge]
- 2026-10-23 eec875a9 balance: finalNight.afterCycle 4 -> 5 (8M step 1, A171; 6Z)
- 2026-10-23 2328c016 test(npc): T6 ignores a crossing on the tick the brain turns home
- 2026-10-23 b3e3df22 Anti-cheat 4: no seed word on stdout before game over; mark the Flow line (8L)
- 2026-10-23 2478691f HD: the rim is for figures; world statics take none
- 2026-10-23 1b48a67e Merge claude/r8-hd-render into claude/r8-hd-proposal (the world rim fix) [merge]
- 2026-10-23 4b658b73 Merge claude/r8-hd-proposal into claude/r8-hd-client (the world rim fix) [merge]
- 2026-10-23 87022682 Merge claude/r8-hd-client into claude/r8-hd-budgets (the world rim fix) [merge]
- 2026-10-24 40da008b Anti-cheat 4: a per-file test timeout for the leak and replay suites (8L)
- 2026-10-24 995272d7 The look folder's README and A164's pointer to it
- 2026-10-24 0b3d10e7 Round 8 (8F): the sixteen clips of motion.md 1 in the rig, the round-8 clip table and the probe's side margins
- 2026-10-24 092e771b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic [merge]
- 2026-10-24 c9f095e0 The HD look sheet: five columns, three subjects, under 1 MB each
- 2026-10-24 e5380e96 Merge claude/r8-hd-proposal into claude/r8-hd-client (the HD look sheet) [merge]
- 2026-10-24 14c4ab44 Merge claude/r8-hd-proposal into claude/r8-hd-budgets (the HD look sheet) [merge]
- 2026-10-24 973dc761 Merge the base into claude/r8-rules (DECISIONS: A168 and A169 above A171) [merge]
- 2026-10-24 f23289b9 Merge branch 'claude/r8-civic' into claude/r8-civic-rumours [merge]
- 2026-10-24 1b0016da The villager family's schema, manifest rule and honest budget count (6Z's grants on #184, A161)
- 2026-10-24 558e9cf7 SPRITES 3: the round-8 clip table (directions, pages, frame counts)
- 2026-10-24 d2375764 Merge branch 'claude/r8-characters-2b' into claude/r8-characters-3 [merge]
- 2026-10-24 193c2ab4 Merge pull request #190 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 ae23057e The round-8 clip picking: gaits from speed and bits, the four-direction rounding and the fallbacks
- 2026-10-24 937a8bf1 PlayerView plays the round-8 clips: the status bits, the drawn speed and the four-direction clips
- 2026-10-24 aa4fbbd8 The physical signs drawn over any clip: bleeding, poisoned, dazed and stunned
- 2026-10-24 7d99425b Merge pull request #146 from groot99-droid/claude/r8-creatures-vfx-fx [merge]
- 2026-10-24 56d20a75 Merge pull request #189 from groot99-droid/claude/r8-creatures-vfx-coins [merge]
- 2026-10-24 b95aa6dc Merge pull request #141 from groot99-droid/claude/r8-scrip [merge]
- 2026-10-24 08c878fd Merge pull request #148 from groot99-droid/claude/r8-scrip-wages [merge]
- 2026-10-24 3cc7bde7 Merge pull request #155 from groot99-droid/claude/r8-scrip-shops [merge]
- 2026-10-24 773b5fea Merge pull request #158 from groot99-droid/claude/r8-scrip-bank [merge]
- 2026-10-24 9b08bd32 Merge pull request #180 from groot99-droid/claude/r8-scrip-coins [merge]
- 2026-10-24 dded5e1e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic [merge]
- 2026-10-24 9899ce7b Merge the base (9b08bd3, #141 to #190) into 8E PR 1a (needs) [merge]
- 2026-10-24 f9797492 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters-2a [merge]
- 2026-10-24 e9938d19 Merge branch 'claude/r8-characters-2a' into claude/r8-characters-2b [merge]
- 2026-10-24 0f6abb3a Merge branch 'claude/r8-characters-2b' into claude/r8-characters-3 [merge]
- 2026-10-24 4187f3b0 The character atlas json on one line, the committed atlases rewritten through it, and the budget figures of the round-8 base
- 2026-10-24 f740676a Merge the base into the shop panel (one economy block: heistShare and coinPickupS) [merge]
- 2026-10-24 20257575 Merge branch 'claude/r8-scrip-shop-panel' into claude/r8-scrip-purse-hud [merge]
- 2026-10-24 e1d05b88 Merge 8E PR 1a (needs, with the base at 9b08bd3) into PR 1b (moods) [merge]
- 2026-10-24 6a7a9687 Merge pull request #152 from groot99-droid/claude/r8-hollowmere-chapel [merge]
- 2026-10-24 a008ed95 Merge pull request #162 from groot99-droid/claude/r8-hollowmere-manor-art [merge]
- 2026-10-24 821ce1f0 Merge the base into claude/r8-hollowmere-budget [merge]
- 2026-10-24 906f452f Merge branch 'claude/r8-civic' into claude/r8-civic-rumours [merge]
- 2026-10-24 270647aa Merge pull request #163 from groot99-droid/claude/r8-hollowmere-manor [merge]
- 2026-10-24 906127e9 Merge branch 'claude/r8-hollowmere-budget' into claude/r8-hollowmere-tavern [merge]
- 2026-10-24 354b76f6 Merge pull request #175 from groot99-droid/claude/r8-hollowmere-shot-hook [merge]
- 2026-10-24 9c0d7846 Merge pull request #138 from groot99-droid/claude/r8-hd [merge]
- 2026-10-24 33360f7f Merge the base (9b08bd3; 8G's effects and coins, 8C's purse, wages, shops, bank, coins) into claude/r8-body-2 [merge]
- 2026-10-24 c9858995 Merge pull request #160 from groot99-droid/claude/r8-hd-render [merge]
- 2026-10-24 74f802e0 Merge pull request #167 from groot99-droid/claude/r8-anticheat [merge]
- 2026-10-24 64d56342 Merge pull request #192 from groot99-droid/claude/r8-anticheat-replay [merge]
- 2026-10-24 5586f46d Merge pull request #171 from groot99-droid/claude/r8-icons [merge]
- 2026-10-24 0a70ef59 Merge pull request #183 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-24 0c0cba73 Merge pull request #156 from groot99-droid/claude/r8-blackpine-economy [merge]
- 2026-10-24 191800e8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-anticheat-vote [merge]
- 2026-10-24 967b8794 Merge base 0c0cba7 into claude/r8-hd-proposal (#138 and #160 merged; packSmallest at the texel factor) [merge]
- 2026-10-24 198c330a Merge claude/r8-hd-proposal into claude/r8-hd-client (base 0c0cba7 via the stack) [merge]
- 2026-10-24 377d09f4 Merge claude/r8-hd-client into claude/r8-hd-budgets (base 0c0cba7 via the stack) [merge]
- 2026-10-24 d703eb2a Merge branch 'claude/r8-characters-2b' into claude/r8-characters-3 [merge]
- 2026-10-24 4b896d71 Merge 8E PR 1b (moods, with the base at 9b08bd3) into PR 2a (figures) [merge]
- 2026-10-24 cf981319 Merge claude/r8-body-2 (the base at 9b08bd3) into claude/r8-body-3 [merge]
- 2026-10-24 6eabd557 Merge branch 'claude/r8-hollowmere-tavern' into claude/r8-hollowmere-widow [merge]
- 2026-10-24 7bb49d73 8K: BlackPine's shop counters and bank counter (8C's rows from #155)
- 2026-10-24 e4a0588c docs(round8): the living-world contract (living.md, A173, A174, 8Q-8U)
- 2026-10-24 d374b281 Merge 8E PR 2a (figures, with the base at 9b08bd3) into PR 2b (death) [merge]
- 2026-10-24 1a94a24d 8D: run the civic loops at the end of runEconomy (seams.md 5)
- 2026-10-24 ee2be288 Merge claude/r8-body-3 (the base at 9b08bd3) into claude/r8-body-4 [merge]
- 2026-10-24 d8e8fe1f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic [merge]
- 2026-10-24 0e2a7dc7 Merge claude/r8-body-4 (the base at 9b08bd3) into claude/r8-body-5 [merge]
- 2026-10-24 539c64b6 Merge pull request #200 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 91bf2591 Merge 8E PR 2b (death, with the base at 9b08bd3) into PR 3a (the mugging roll) [merge]
- 2026-10-24 5b4fd96d Merge branch 'claude/r8-civic-rumours' into claude/r8-civic-faith [merge]
- 2026-10-24 7a1d1248 Merge branch 'claude/r8-civic' into claude/r8-civic-rumours [merge]
- 2026-10-24 76a3a46f Merge 8E PR 3a (the roll, with the base at 9b08bd3) into PR 3b (the mugging) [merge]
- 2026-10-24 587a4388 Merge 8E PR 3b (the mugging, with the base at 9b08bd3) into PR 3c (the prompt) [merge]
- 2026-10-24 8da00292 feat(talk): meeting notes, a channel with no speaker, with NPC template notes (8T PR 1a)
- 2026-10-24 ef9492de Merge pull request #154 from groot99-droid/claude/r8-characters-2a [merge]
- 2026-10-24 26bd92ac Merge pull request #198 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-24 8abeedbe Merge pull request #195 from groot99-droid/claude/r8-characters-4 [merge]
- 2026-10-24 fbbac89a Merge pull request #196 from groot99-droid/claude/r8-characters-5 [merge]
- 2026-10-24 ce613a49 Merge pull request #197 from groot99-droid/claude/r8-characters-6 [merge]
- 2026-10-24 632bbb31 EntityView passes the whole status word to PlayerView.pose (6Z's grant, motion.md 1)
- 2026-10-24 1abb4192 8I: the owner's HD pick in A164 (PBR for buildings and the kit, toon HD elsewhere); the sky HDRI locked, fetched and credited
- 2026-10-24 75bc6bc7 8I: WDI_HD_SKY puts the PBR sky under the toon HD figures (the A164 ambient test)
- 2026-10-24 18bfc873 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hd-proposal [merge]
- 2026-10-24 d82a22da Merge branch 'claude/r8-hd-proposal' into claude/r8-hd-client [merge]
- 2026-10-24 f0a7c30a Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 ff3361c8 Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 7b894a7f 8I: keep the HD looks sentence of ASSETS 6.3 beside 8F's round-8 paragraph (merge fix)
- 2026-10-24 9616aa78 Merge branch 'claude/r8-hd-budgets' into HEAD [merge]
- 2026-10-24 96af16cf Merge pull request #181 from groot99-droid/claude/r8-anticheat-vote [merge]
- 2026-10-24 c6932406 Merge pull request #199 from groot99-droid/claude/r8-blackpine-shops [merge]
- 2026-10-24 6f825b02 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic-rumours [merge]
- 2026-10-24 673407ba Merge the base (c693240) into claude/r8-hollowmere-budget [merge]
- 2026-10-24 9d08c190 Merge claude/r8-hollowmere-budget (base c693240) into claude/r8-hollowmere-tavern [merge]
- 2026-10-24 bd8421a6 Merge claude/r8-hollowmere-tavern (base c693240) into claude/r8-hollowmere-widow [merge]
- 2026-10-24 864b37f6 feat(client): the meeting notes tab (8T PR 1b)
- 2026-10-24 161ece9b feat(hive): the public blackboard and hiveNoSecrets (8R step 1a, A176)
- 2026-10-24 b6c7b8ec Merge the base (c693240) into 8E PR 1a (needs) [merge]
- 2026-10-24 832b1372 Merge branch 'claude/r8-civic-rumours' into claude/r8-civic-faith [merge]
- 2026-10-24 17266653 Merge the base (c693240) into claude/r8-rules [merge]
- 2026-10-24 9e523bdf Merge pull request #132 from groot99-droid/claude/r8-civic [merge]
- 2026-10-24 a6dbd909 Merge pull request #168 from groot99-droid/claude/r8-hd-proposal [merge]
- 2026-10-24 4e643390 Merge the base into the shop panel (beside 7M's task bar and chores) [merge]
- 2026-10-24 066c792c Merge the base (c693240; 8F's characters and client, 7M's chores, 8L's vote delay, 8K's counters) into claude/r8-body-2 [merge]
- 2026-10-24 50a38666 Merge branch 'claude/r8-scrip-shop-panel' into claude/r8-scrip-purse-hud [merge]
- 2026-10-24 10a93961 Merge 8E PR 1a (needs, with the base at c693240) into PR 1b (moods) [merge]
- 2026-10-24 cb112f6c Merge remote-tracking branch 'origin/claude/r8-hd-client' into claude/r8-hd-client [merge]
- 2026-10-24 b468e5f5 Merge branch 'claude/r8-hd-budgets' into HEAD [merge]
- 2026-10-24 e08c4b9b Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 6e231ed8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hd-client [merge]
- 2026-10-24 afb252c1 Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 425f4207 Merge branch 'claude/r8-hd-budgets' into HEAD [merge]
- 2026-10-24 d5a97daa feat(hive): the trigger registry and fair senses (8R step 1b, A174, A176)
- 2026-10-24 8c9b8e98 feat(talk): the Messages API transport, the line filter and the card-blind prompt (8T PR 2a)
- 2026-10-24 d94f1364 feat(talk): NPC notes from the model, off the tick, capped and replayable (8T PR 2b)
- 2026-10-24 8f5c55ec Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic-rumours [merge]
- 2026-10-24 807e77de Merge the base (c693240) into claude/r8-rules-2 [merge]
- 2026-10-24 b2c1da1d Merge claude/r8-body-2 (the base at c693240) into claude/r8-body-3 [merge]
- 2026-10-24 952075e4 Merge 8E PR 1b (moods, with the base at c693240) into PR 2a (figures) [merge]
- 2026-10-24 5fc8e2da Merge pull request #205 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-24 402c5272 Resident cap 9 by the owner's option B (A161)
- 2026-10-24 3a32e10b Merge branch 'claude/r8-characters-2b' into claude/r8-characters-3 [merge]
- 2026-10-24 7a40bb72 Merge branch 'claude/r8-civic-rumours' into claude/r8-civic-faith [merge]
- 2026-10-24 a0bb8bb4 feat(talk): red herrings and small talk in the NPC notes (8T PR 3)
- 2026-10-24 27546cb4 Steady two base tests that race a loaded runner
- 2026-10-24 62b0204c Steady two base tests that race a loaded runner
- 2026-10-24 cd4eff86 Merge claude/r8-body-3 (the base at c693240) into claude/r8-body-4 [merge]
- 2026-10-24 2d245195 Merge claude/r8-body-4 (the base at c693240) into claude/r8-body-5 [merge]
- 2026-10-24 4f484ff6 Merge 8E PR 2a (figures, with the base at c693240) into PR 2b (death) [merge]
- 2026-10-24 ab9364ae Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters-3 [merge]
- 2026-10-24 611679dd 8K: BlackPine's altar, black market and quota rack (8D's rows from #132)
- 2026-10-24 42d28ff7 Merge pull request #174 from groot99-droid/claude/r8-scrip-shop-panel [merge]
- 2026-10-24 040b3053 Merge pull request #177 from groot99-droid/claude/r8-scrip-purse-hud [merge]
- 2026-10-24 cce2048c Merge the base (5fc8e2d) into claude/r8-body-2 [merge]
- 2026-10-24 07fe6878 Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 c5216a5f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hd-client [merge]
- 2026-10-24 af8fd281 Merge branch 'claude/r8-hd-budgets' into HEAD [merge]
- 2026-10-24 98fc16fd Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-talk [merge]
- 2026-10-24 af9e8b96 Shop panel answers a trade with 8H's motion (UI.md 14.34.1)
- 2026-10-24 c3d87aaa 8H step 5a: purse HUD motion (roll, label, coins in and out) by 8C's hooks
- 2026-10-24 1d7afcb3 8E: the mugging decision is A180, not A161 (8F's second row)
- 2026-10-24 a9cac25e 8E: the mugging decision is A180, not A161 (8F's second row)
- 2026-10-24 a1574afc 8E: the mugging decision is A180, not A161 (8F's second row)
- 2026-10-24 aa2c5d0f Merge 8E PR 2b (death, with the base at c693240) into PR 3a (the mugging roll) [merge]
- 2026-10-24 996569bf Merge 8E PR 3a (the roll, with the base at c693240) into PR 3b (the mugging) [merge]
- 2026-10-24 64df1554 Merge 8E PR 3b (the mugging, with the base at c693240) into PR 3c (the prompt) [merge]
- 2026-10-24 984fcda0 Merge claude/r8-body-2 (the base at 5fc8e2d) into claude/r8-body-3 [merge]
- 2026-10-24 251bd767 Merge branch 'claude/r8-hollowmere-tavern' into claude/r8-hollowmere-widow [merge]
- 2026-10-24 9c458469 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-budget [merge]
- 2026-10-24 07096cb2 Merge branch 'claude/r8-hollowmere-budget' into claude/r8-hollowmere-tavern [merge]
- 2026-10-24 3b75a5d2 Merge pull request #211 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 e29e38c4 Merge pull request #184 from groot99-droid/claude/r8-characters-2b [merge]
- 2026-10-24 f74e7a18 Merge pull request #203 from groot99-droid/claude/r8-characters-7 [merge]
- 2026-10-24 669a3165 Merge pull request #213 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-24 2400ea46 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hd-client [merge]
- 2026-10-24 39419fce Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 6082c378 6Z: the leak audit waits on its patch count, not a fixed half second
- 2026-10-24 4d461468 Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 8c2acfac 8I: the villager-family and one-line-atlas checks skip a style whose manifest lists no characters yet (merge fix)
- 2026-10-24 a13584a4 8F: the round-8 clip table at option B, the lazy pair per look and the client's lazy loader (PR 3)
- 2026-10-24 1f9bffeb Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters-3 [merge]
- 2026-10-24 78fa77b2 Merge claude/r8-body-3 (the base at 5fc8e2d) into claude/r8-body-4 [merge]
- 2026-10-24 1fb42886 8F: format the MANIFEST.md rows of the 15 looks
- 2026-10-24 102d4e6d Merge pull request #134 from groot99-droid/claude/r8-civic-rumours [merge]
- 2026-10-24 8c09628f Merge pull request #201 from groot99-droid/claude/r8-civic-faith [merge]
- 2026-10-24 f2151c21 Merge pull request #202 from groot99-droid/claude/r8-talk [merge]
- 2026-10-24 1ffee36e Merge pull request #216 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 1662c7e8 8I: the sprites manifest guard asserts that every style it skips is still rendering its characters (6Z's grant)
- 2026-10-24 9bbadd04 Merge the base (with #216's leak.test fix) into 8C shop feedback [merge]
- 2026-10-24 3442aa03 Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 37778b3a 8F: the villager re-rendered with the round-8 clips, both styles (resident pair and lazy pair)
- 2026-10-24 ccad7f7e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hd-client [merge]
- 2026-10-24 a34aa0bf Merge branch 'claude/r8-hd-client' into claude/r8-hd-budgets [merge]
- 2026-10-24 78b470ea Merge branch 'claude/r8-hd-budgets' into HEAD [merge]
- 2026-10-24 373b42a8 Merge claude/r8-body-4 (the base at 5fc8e2d) into claude/r8-body-5 [merge]
- 2026-10-24 9f1e0355 Merge the base (1ffee36e, #132 in) into 8E PR 1a (needs) [merge]
- 2026-10-24 d8b95178 Audit every station for the hands-on widgets and log the owner's ask (A200, 7M S0)
- 2026-10-24 ab16c297 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-budget [merge]
- 2026-10-24 112d2cff Merge branch 'claude/r8-hollowmere-budget' into claude/r8-hollowmere-tavern [merge]
- 2026-10-24 0ed27f2b Merge branch 'claude/r8-hollowmere-tavern' into claude/r8-hollowmere-widow [merge]
- 2026-10-24 9e480b7e feat(hive): the body bands, pull and report, with fair sight (8R step 2a, A174, A176, A196)
- 2026-10-24 3e4cf389 Merge the base (669a316) into claude/r8-rules-2 [merge]
- 2026-10-24 f9758b39 Merge the base (1ffee36) into claude/r8-rules-2 [merge]
- 2026-10-24 fc681c19 Merge pull request #214 from groot99-droid/claude/r8-scrip-feedback [merge]
- 2026-10-24 c2713cf2 Merge pull request #215 from groot99-droid/claude/r8-ui-motion-hud [merge]
- 2026-10-24 11a25ff7 Merge 8E PR 1a (needs, with the base at 1ffee36e) into PR 1b (moods) [merge]
- 2026-10-24 e6f10ece Record the owner's round-2 answers on the reader and the well (A200)
- 2026-10-24 a12af6d8 Merge the base (1ffee36) into claude/r8-rules-3 [merge]
- 2026-10-24 2813ba68 Rent, quota and Indebted, with the curfew door (8D, GDD 3.23)
- 2026-10-24 37b01073 8F: the detective re-rendered with the round-8 clips; character pages pack tight with the finish off
- 2026-10-24 ea9c76f0 Merge the base (c2713cf) into claude/r8-body-2 [merge]
- 2026-10-24 debbc52c 8F: a low-poly body that spills at the clip table takes one 1024 x 2048 page (6Z's decision), ASSETS 6.3 line
- 2026-10-24 5a4ae1ae feat(hive): the shout, the bell run and the night bell (8R step 2b, A174, A176, A196)
- 2026-10-24 6cdf1a1d Merge pull request #176 from groot99-droid/claude/r8-rules [merge]
- 2026-10-24 687e6773 HQ tiers: GameState.hq and act.hq behind the owner's gate (8D, GDD 3.23)
- 2026-10-24 d75ef49a Merge the base (6cdf1a1, #176 #214 #215 in) into 8E PR 1a (needs) [merge]
- 2026-10-24 00512e82 Merge the base (1ffee36) into claude/r8-rules-4 [merge]
- 2026-10-24 12afd440 6Z: A201 and session 8V, the canon pass now the lore is in
- 2026-10-24 8e32db6b The body writer leaves foreign effect rows alone; reserve the charm id (6Z's notes)
- 2026-10-24 83905d90 Merge claude/r8-body-2 (the base at c2713cf, the foreign-row rule, the charm id) into claude/r8-body-3 [merge]
- 2026-10-24 3d2e634a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hive [merge]
- 2026-10-24 bd130820 Merge branch 'claude/r8-hive' into claude/r8-hive-senses [merge]
- 2026-10-24 f672c175 art(characters): doctor at the round-8 clip table, both styles
- 2026-10-24 51ecb604 Merge 8E PR 1a (needs, base 6cdf1a1) into PR 1b (moods) [merge]
- 2026-10-24 6b7108bc fix(client): the Final Night meeting's reason line (8T, 6Z's grant)
- 2026-10-24 70b6994d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic-rent [merge]
- 2026-10-24 6ffa2722 8K: the black market moves to bp_lodge 16,3, in the bunk bay (8D's ask)
- 2026-10-24 b90ed932 Merge pull request #220 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 e6f1ad2b Bar the curfew only on the door from outdoors
- 2026-10-24 c430f9b4 Merge the base (b90ed93, with #176) into claude/r8-rules-2 [merge]
- 2026-10-24 54f0ddc5 docs(ui): the shout copy is UI.md 14.41 (14.40 is 8T's)
- 2026-10-24 64e192e6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters-3 [merge]
- 2026-10-24 6a813b7c feat(sprites): indexed 8-bit character pages and one-line anims json (6Z's grant on #194)
- 2026-10-24 e740ab79 Merge pull request #218 from groot99-droid/claude/r8-talk [merge]
- 2026-10-24 f684be10 Merge pull request #169 from groot99-droid/claude/r8-hd-client [merge]
- 2026-10-24 8a23d252 Merge pull request #170 from groot99-droid/claude/r8-hd-budgets [merge]
- 2026-10-24 19019f6a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-talk [merge]
- 2026-10-24 c2025675 art(characters): vicar in both styles; tight character sets pack at padding 1 in either style
- 2026-10-24 b9d24307 Merge the base (b90ed93) into claude/r8-rules-3 [merge]
- 2026-10-24 f603dfdf Merge the base (b90ed93) into claude/r8-rules-4 [merge]
- 2026-10-24 9f5a0828 Merge pull request #221 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-24 95cd9b5d Merge pull request #212 from groot99-droid/claude/r8-blackpine-altar [merge]
- 2026-10-24 db55ba32 Merge pull request #182 from groot99-droid/claude/r8-hollowmere-budget [merge]
- 2026-10-24 f7a8753e Merge pull request #191 from groot99-droid/claude/r8-hollowmere-tavern [merge]
- 2026-10-24 19644a1e Merge pull request #193 from groot99-droid/claude/r8-hollowmere-widow [merge]
- 2026-10-24 dae287ba Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-stations [merge]
- 2026-10-24 16b240ea Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic-rent [merge]
- 2026-10-24 b6a1b3cc art(characters): watchman, herbalist, gamekeeper and lamplighter at the round-8 clip table, both styles
- 2026-10-24 5075e542 feat(looks): the Baker carries a basket of loaves on her forearm (owner's ruling); A141 closed on "after"
- 2026-10-24 02d51bf6 Use BlackPine's real tally rack in the quota test
- 2026-10-24 34774f58 Open HQ buying: the owner approved the tiers and perks
- 2026-10-24 8524075c 6Z: the 18 round-8 sound effects for 8G (owner-approved)
- 2026-10-24 82f3aee8 6Z: A202, the round-8 sounds
- 2026-10-24 dedcb0f5 Mallory's apothecary, shop and loft, dressed by rule (8J, art.md 4.2)
- 2026-10-24 c9bbd747 Civic feed, copy and rows for the ui/econ panels (8D, GDD 3.23)
- 2026-10-24 6471e018 The civic panels: altar, mailbag, rack, back room, HQ and bank (8D, GDD 3.23)
- 2026-10-24 a19a96f7 Apothecary: a mat at the door, sacks and a barrel by the west wall; review shots (8J)
- 2026-10-24 df7c083c Sound the round-8 creatures, breaks, effects and transport
- 2026-10-24 81a84a44 Merge pull request #217 from groot99-droid/claude/r8-stations [merge]
- 2026-10-24 a44b2848 Merge pull request #223 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-24 61191591 Merge pull request #219 from groot99-droid/claude/r8-civic-rent [merge]
- 2026-10-24 14cdc831 Merge pull request #224 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 904e9237 C3 knows the counter and bank kinds (granted by 6Z); HollowMere's building pages re-encoded losslessly (8J)
- 2026-10-24 7943cf9d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-sounds [merge]
- 2026-10-24 6366cb08 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-civic-hq [merge]
- 2026-10-24 36743a24 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hive [merge]
- 2026-10-24 30eba78b Merge branch 'claude/r8-hive' into claude/r8-hive-senses [merge]
- 2026-10-24 ca4f388d packCapped re-encodes its pages with encodePng, losslessly (8J, granted by 6Z)
- 2026-10-24 f12d7991 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-apothecary [merge]
- 2026-10-24 96dd520e Merge the base (14cdc83) into claude/r8-rules-2 [merge]
- 2026-10-24 82fa3db2 Merge pull request #222 from groot99-droid/claude/r8-civic-hq [merge]
- 2026-10-24 337c5b24 Merge pull request #208 from groot99-droid/claude/r8-hive [merge]
- 2026-10-24 c22c370a Merge remote-tracking branch 'origin/claude/r8-hive-senses' into claude/r8-hive [merge]
- 2026-10-24 c21fe094 Merge branch 'claude/r8-hive-bands' into claude/r8-hive [merge]
- 2026-10-24 28d1d5cb Merge pull request #227 from groot99-droid/claude/r8-creatures-vfx-sounds [merge]
- 2026-10-24 69feca74 Merge pull request #210 from groot99-droid/claude/r8-hive-senses [merge]
- 2026-10-24 7083c14e Merge pull request #225 from groot99-droid/claude/r8-civic-ui-feed [merge]
- 2026-10-24 e54fd7b3 Merge pull request #226 from groot99-droid/claude/r8-civic-ui [merge]
- 2026-10-24 90cf8516 A139 (12): the seams 8D leaves for R9
- 2026-10-24 4044a486 DECISIONS A171: the card-text token syntax (steps 3 and 4)
- 2026-10-24 951d8667 Crumb's Ovens and its four rooms dressed by rule (8J, art.md 4.2)
- 2026-10-24 88481bec The Crumb station test skips set dressing (granted by 6Z)
- 2026-10-24 707710d2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hive [merge]
- 2026-10-24 138667cd Merge pull request #228 from groot99-droid/claude/r8-hollowmere-apothecary [merge]
- 2026-10-24 50f84b50 Merge pull request #185 from groot99-droid/claude/r8-rules-3 [merge]
- 2026-10-24 87b184d6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-bakery [merge]
- 2026-10-24 87a116ea Merge the base (50f84b5, with #185) into claude/r8-rules-4 [merge]
- 2026-10-24 fb61315e The shops test moves a placed counter onto its fixture tile (granted by 6Z)
- 2026-10-24 ecd68d3f 8G: HQ tier props, the 12 hq_ rows and HqView (motion.md 2, step 5)
- 2026-10-24 81bcba3f 8G: prettier on the CREDITS row of #231
- 2026-10-24 dc52fd8e Merge pull request #187 from groot99-droid/claude/r8-rules-4 [merge]
- 2026-10-24 85dcd734 Merge pull request #179 from groot99-droid/claude/r8-rules-2 [merge]
- 2026-10-24 ad1270c8 Merge pull request #229 from groot99-droid/claude/r8-civic-seams [merge]
- 2026-10-24 f5447c79 8G: MANIFEST hashes of the two props masters re-saved with the HQ tiers (#231)
- 2026-10-24 2de63dd4 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-creatures-vfx-hq [merge]
- 2026-10-24 64903eff Pennock's barn and the cellar dressed by rule, with the tavern and chapel economy rows (8J, art.md 4)
- 2026-10-24 b684e8d9 Retry the party create once or twice on ECONNRESET in startMatch
- 2026-10-24 9b2afbcb Retry the party create once or twice on ECONNRESET in startMatch
- 2026-10-24 05c4d4bd Merge pull request #232 from groot99-droid/claude/r8-hollowmere-bakery [merge]
- 2026-10-24 d82fa0d4 8G: as.hq_surgery on 16,4 in place of as.bottle_crate_0 (8J's pick); 16,6 back to floor
- 2026-10-24 416f8676 Merge base 05c4d4b: bk.hq_ovens stays on the 13,3 wall stub of 8J's re-dressed bakery [merge]
- 2026-10-24 46734b64 The barn and cellar props, packed, with before and after shots
- 2026-10-24 a6ab51c2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-barn [merge]
- 2026-10-24 9437f2db Steady the leak audit's Blood self-test: pause the sim clock
- 2026-10-24 e5427e7f Pause only after the audit's settled tick
- 2026-10-24 69886291 Merge pull request #231 from groot99-droid/claude/r8-creatures-vfx-hq [merge]
- 2026-10-24 7158e01e Merge pull request #233 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 2cca8da1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hive [merge]
- 2026-10-24 3a83debb 8D: hq.test uses 8G's real tier props (ov.hq_chapel, bk.hq_ovens)
- 2026-10-24 b5c4552b The wood beyond the gate, the deep wood and Vane's gallery dressed by rule, with the gamekeeper's stall (8J, art.md 4)
- 2026-10-24 1acb94f2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-barn [merge]
- 2026-10-24 975a945a Leave the bld props fixture room for the wood and gallery frames
- 2026-10-24 ba812dd5 Merge branch 'claude/r8-hollowmere-barn' into claude/r8-hollowmere-forest [merge]
- 2026-10-24 5ee7d435 Dress the village square, the house fronts, the platform and the quay by rule (WIP: atlas to follow)
- 2026-10-24 76b548ee Merge pull request #230 from groot99-droid/claude/r8-hive [merge]
- 2026-10-24 c004e86f Merge pull request #234 from groot99-droid/claude/r8-hollowmere-barn [merge]
- 2026-10-24 ca31a440 Merge pull request #235 from groot99-droid/claude/r8-hq-real-props [merge]
- 2026-10-24 21d549d9 test(hive): the shout cue waits for the scene name instead of 50 ms
- 2026-10-24 152ac497 Pack the village's mail crane, set settles in the square and on the platform, and add the review shots
- 2026-10-24 bf33c14d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-forest [merge]
- 2026-10-24 f1b53ed3 Merge pull request #236 from groot99-droid/claude/r8-hollowmere-forest [merge]
- 2026-10-24 b5858852 Merge pull request #237 from groot99-droid/claude/r8-hive [merge]
- 2026-10-24 0887ac51 Merge branch 'claude/r8-hollowmere-forest' into claude/r8-hollowmere-overworld [merge]
- 2026-10-24 edb5c572 Stand the wayside shrine and the mail crane on the tiles 8D's tests reserved for them
- 2026-10-24 3837825b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-hollowmere-overworld [merge]
- 2026-10-24 14ac577d Merge pull request #238 from groot99-droid/claude/r8-hollowmere-overworld [merge]
- 2026-10-24 14333154 hiveBands: count both reactions in the scream test's deadline
- 2026-10-24 4e5746cc hiveBands: keep the forest's creatures idle in the scream test
- 2026-10-24 b562561e Merge pull request #239 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 09cbeddd Merge the base (b562561) into 8E PR 1a [merge]
- 2026-10-24 2125034b Merge the base (b562561) into claude/r8-body-2; effects.json in canonical layout [merge]
- 2026-10-24 b0526d24 Merge commit 'b562561' into claude/r8-hd-renders [merge]
- 2026-10-24 cb090248 The shared schema test lists the reserved charm id (12)
- 2026-10-24 cc79b301 Merge claude/r8-body-2 (the base at b562561) into claude/r8-body-3 [merge]
- 2026-10-24 8afd058c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters-3 [merge]
- 2026-10-24 2d98b2a0 C1: docs/round8/canon.md, the canon map of A201, and DECISIONS A221
- 2026-10-24 77b33a76 C2: HollowMere wording to the canon (1893, the drowned mere, no lighthouse)
- 2026-10-24 ae460e74 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-talk [merge]
- 2026-10-24 75774cfb C3: BlackPine wording to the canon (Harrow's coal camp, 1893)
- 2026-10-24 ee8f27d9 8I: --webp on the HD static packer and encodeWebp beside the PNG encoder (6Z's grant, A164 option 1)
- 2026-10-24 fda531e0 feat(sprites): character atlases leave the unrotated flag out (6Z's grant on #194)
- 2026-10-24 a4143e8c Merge 8E PR 1a (with the base at b562561) into PR 1b [merge]
- 2026-10-24 133928b7 Merge 8E PR 1b (with the base at b562561) into PR 2a [merge]
- 2026-10-24 7aaa1307 needs test: keep the seat standing while hunger rises
- 2026-10-24 3b3e7e84 R1: map and scene display names in the owner's casing, HollowMere and BlackPine
- 2026-10-24 0844bcae R2: the Thief escapes by the sea door at the back of the cave
- 2026-10-24 4866a3f7 Merge claude/r8-body-3 (the base at b562561) into claude/r8-body-4 [merge]
- 2026-10-24 11d5e0ef R3: crumb_cold's compressor retired for an ice chest (canon.md K11)
- 2026-10-24 454db7d8 C1b: the owner's answers to Q1 and Q2 in canon.md and A221
- 2026-10-24 28d2d718 C1b: the owner's answers to Q1 and Q2 in canon.md and A221
- 2026-10-24 3f1392e6 Icons: SVG masters, generated rasters, the effect set and the client helper
- 2026-10-24 dc5a86a6 8I: A164's open cell records the owner's PBR multi-tile props and WebP option 1 pending the owner
- 2026-10-24 ae786916 Mini-games drawn as their own stations, with the teardown's polish (7M PR 5, A151 (4))
- 2026-10-24 04f616e1 docs(talk): the meeting facts come from the meeting state, not the hive board (8T PR 2b)
- 2026-10-24 d0cecdf9 Merge pull request #142 from groot99-droid/claude/r8-townsfolk [merge]
- 2026-10-24 f2556d88 Merge the needs test fix (7aaa130, after #142 merged) into 8E PR 1b [merge]
- 2026-10-24 2f06a18e Merge the base (d0cecdf, #142 in) into 8E PR 1b [merge]
- 2026-10-24 5c546e1b Icons: the bloodied mark over a figure shows the bleeding icon
- 2026-10-24 16d7439f Merge claude/r8-body-4 (the base at b562561) into claude/r8-body-5 [merge]
- 2026-10-24 a8daf729 art(characters): fisher at the round-8 clip table, both styles
- 2026-10-24 ebfada4a Draw the round-8 HUD icons: economy, body, talk and hive (8N)
- 2026-10-24 a36cda83 Merge 8E PR 1b (f2556d8, the base at d0cecdf) into PR 2a [merge]
- 2026-10-24 af637bed Fix the review sheet's regenerate command in the round-8 icons README (8N)
- 2026-10-24 1c62914a Merge branch 'claude/r8-icons' into claude/r8-icons-mark [merge]
- 2026-10-24 33c63630 Merge branch 'claude/r8-icons-mark' into claude/r8-icons-hud [merge]
- 2026-10-24 d28522ec Merge 8E PR 2a (with the base at d0cecdf) into PR 2b [merge]
- 2026-10-24 17893aa3 Write the icon line's handover: the PR C to G plan and the 8C, 8D and 8H lists (8N)
- 2026-10-24 47314bee The lore data for the shelf reader (7M S1, GDD 3.26, A200)
- 2026-10-24 467ecd27 minigames.json in the data lint's canonical layout
- 2026-10-24 cff1b9c7 Type the skin test's rows as MinigameKind (7M PR 5, CI typecheck)
- 2026-10-24 21d4fecd Widen the lore test's scene list for includes (7M S1, CI typecheck)
- 2026-10-24 f572b931 Merge pull request #240 from groot99-droid/claude/r8-canon [merge]
- 2026-10-24 cd07f8e7 Merge pull request #241 from groot99-droid/claude/r8-canon-c2 [merge]
- 2026-10-24 bd3e8b81 Merge pull request #242 from groot99-droid/claude/r8-canon-c3 [merge]
- 2026-10-24 e49d1aae Merge pull request #157 from groot99-droid/claude/r8-townsfolk-moods [merge]
- 2026-10-24 cb1149de Merge 8E PR 2b (with the base at d0cecdf) into PR 3a [merge]
- 2026-10-24 e7a267ca Merge 8E PR 3a (with the base at d0cecdf) into PR 3b [merge]
- 2026-10-24 59e201eb PROTOCOL.md: regenerate for act.mug and mugPrompt (pnpm docs:protocol)
- 2026-10-24 73ba3627 act.mug: its rate row (5/s, seams.md 3) and PROTOCOL.md regenerated
- 2026-10-24 bf878f61 Merge 8E PR 3b (with the base at d0cecdf) into PR 3c [merge]
- 2026-10-24 5b6e3fe9 UI 14.36.1: the mugging prompt under 8E's 14.36 (14.37 is 8H's, SESSIONS Round 8)
- 2026-10-24 95b8b3c4 Merge the base (e49d1aa, #157 in) into 8E PR 2a [merge]
- 2026-10-24 f7d19d96 hive test: check each sighting in its own scene (granted by 6Z, hive.test.ts:68-69)
- 2026-10-24 e4ee8eb1 Merge pull request #247 from groot99-droid/claude/r8-talk [merge]
- 2026-10-24 d3005fb9 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-talk-pr2-new [merge]
- 2026-10-24 d0dde34c Merge r8-townsfolk-mug (the base at e49d1aa, the hive test fix) into r8-townsfolk-mug-run [merge]
- 2026-10-24 24de152a Merge r8-townsfolk-death (the base at e49d1aa, the hive test fix) into r8-townsfolk-mug [merge]
- 2026-10-24 df1d01c7 Merge r8-townsfolk-figures (the base at e49d1aa, the hive test fix) into r8-townsfolk-death [merge]
- 2026-10-24 20e9bc65 Merge r8-townsfolk-mug-run (the base at e49d1aa, the hive test fix) into r8-townsfolk-mug-ui [merge]
- 2026-10-24 ea387943 Round 8 body: the well's charm, spent by a killing Knife strike (8A)
- 2026-10-24 0a942600 Merge the base (e4ee8eb) into claude/r8-body-2 [merge]
- 2026-10-24 b9de1687 Merge claude/r8-body-2 (the base at e4ee8eb) into claude/r8-body-3 [merge]
- 2026-10-24 24773933 Merge claude/r8-body-4 (the base at e4ee8eb) into claude/r8-body-5 [merge]
- 2026-10-24 1dc1d587 Merge claude/r8-body-3 (the base at e4ee8eb) into claude/r8-body-4 [merge]
- 2026-10-24 69cd4ead 8I: the HD slice factor in meta.texels, read by hd-manifest.ts; the PNG and WebP q90 crop for the owner
- 2026-10-24 e4bbb78f 8I: the HD buildings pass: bld_blackpine and props_hollowmere in PBR as WebP q90, the HD manifest, the WebP crop
- 2026-10-24 02553bf8 Merge pull request #249 from groot99-droid/claude/r7-minigames [merge]
- 2026-10-24 19a72a05 Merge pull request #248 from groot99-droid/claude/r8-icons [merge]
- 2026-10-24 48efc5f2 Merge pull request #250 from groot99-droid/claude/r8-icons-mark [merge]
- 2026-10-24 473bbcc8 Merge pull request #251 from groot99-droid/claude/r8-icons-hud [merge]
- 2026-10-24 bae70852 art(characters): tinner, villagerclerk and villagerelder at the round-8 clip table, both styles
- 2026-10-24 a53dec99 8I staging: raw HD renders of bld_hollowmere and the BlackPine multi-tile props (PBR), to pack after the props pass
- 2026-10-24 7a04d954 Merge the base at 473bbcc into r8-townsfolk-figures [merge]
- 2026-10-24 a91f7d40 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-talk-pr2-new [merge]
- 2026-10-24 206e767a Merge pull request #204 from groot99-droid/claude/r8-hd-renders [merge]
- 2026-10-24 5d5a0c4e Townsfolk: keep a figure's path until its goal changes, cache the first portal per route
- 2026-10-24 18cadaf6 npcRoutine.test: record the held day in a beforeAll with its own 20 s (granted by 6Z)
- 2026-10-24 5b4206f6 Merge r8-townsfolk-figures (the base at 473bbcc, the townsfolk speed-up, the npcRoutine beforeAll) into r8-townsfolk-death [merge]
- 2026-10-24 f9d5d896 Merge the round-8 base into r8-body-2 and draw the charm icon [merge]
- 2026-10-24 368baf9e Merge r8-townsfolk-death (the base at 473bbcc, the townsfolk speed-up) into r8-townsfolk-mug [merge]
- 2026-10-24 12102fe6 DECISIONS A164: the owner's WebP rule (large objects WebP, detail-critical pages PNG)
- 2026-10-24 adc7465e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-shelf-pages [merge]
- 2026-10-24 93b22ebb art(characters): goodwife, lass and baker at the round-8 clip table, both styles; the packed figures
- 2026-10-24 015c52e8 Require a source line range for every shelf page
- 2026-10-24 e8f55cc0 Merge r8-body-2 (the round-8 base and the charm icon) into r8-body-3 [merge]
- 2026-10-24 a08df105 Merge r8-townsfolk-mug (the base at 473bbcc, the townsfolk speed-up) into r8-townsfolk-mug-run [merge]
- 2026-10-24 6e843ba5 Fill every shelf page from the cited vault works
- 2026-10-24 55b46813 Replace the Intake pages with undated camp rules
- 2026-10-24 09c344f2 Merge pull request #255 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-24 e1aba3b6 Merge pull request #159 from groot99-droid/claude/r8-townsfolk-figures [merge]
- 2026-10-24 ef994759 Merge the base at e1aba3b (#159 merged) into r8-townsfolk-death [merge]
- 2026-10-24 2e41af71 Merge r8-body-3 (the round-8 base and the charm icon) into r8-body-4 [merge]
- 2026-10-24 61baba3e Merge r8-townsfolk-mug-run (the base at 473bbcc, the townsfolk speed-up) into r8-townsfolk-mug-ui [merge]
- 2026-10-24 391f1f30 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r8-characters-3 [merge]
- 2026-10-24 e0e539a7 Merge r8-body-4 (the round-8 base and the charm icon) into r8-body-5 [merge]
- 2026-10-24 0f726000 Merge r8-townsfolk-death (the base at e1aba3b, #159 merged) into r8-townsfolk-mug [merge]
- 2026-10-24 29fde047 Merge r8-townsfolk-mug-run (the base at e1aba3b, #159 merged) into r8-townsfolk-mug-ui [merge]
- 2026-10-24 54dfc74b Merge r8-townsfolk-mug (the base at e1aba3b, #159 merged) into r8-townsfolk-mug-run [merge]
- 2026-10-24 d27bfa4c Merge pull request #254 from groot99-droid/claude/r8-talk [merge]
- 2026-10-24 06891266 Merge pull request #194 from groot99-droid/claude/r8-characters-3 [merge]
- 2026-10-24 a39cbcdf Merge the round-8 base (0689126) into r8-body-2 [merge]
- 2026-10-24 4e6b8880 Round 8 body: the bat test checks the lowest health across its first window (8A)
- 2026-10-24 9c3b9027 Merge pull request #166 from groot99-droid/claude/r8-body-2 [merge]
- 2026-10-24 0c802245 Merge the round-8 base (with #166) into r8-body-3 [merge]
- 2026-10-24 2f89eac3 Merge the base at 9c3b902 (#166 merged) into r8-townsfolk-death [merge]
- 2026-10-24 0dbca2b6 Round 8 townsfolk: a figure's health lives in its reduced body (8E)
- 2026-10-24 e43b4964 Merge pull request #173 from groot99-droid/claude/r8-body-3 [merge]
- 2026-10-24 c8b2ad8b Merge the round-8 base (with #166 and #173) into r8-body-4 [merge]
- 2026-10-24 fa0ccab7 Merge pull request #164 from groot99-droid/claude/r8-townsfolk-death [merge]
- 2026-10-24 ba870e5c Merge the base at fa0ccab (#164 merged) into r8-townsfolk-mug [merge]
- 2026-10-24 cb010bba Merge the round-8 base (with #164) into r8-body-4 [merge]
- 2026-10-24 42f5318b Register figureNotSeat before bodyBounds from the body stage
- 2026-10-24 3404f63b tools/auto lists figureNotSeat among the round-8 checks
- 2026-10-24 9d9f4468 bodyBounds.test counts the figures' bodies beside the seats'
- 2026-10-24 62aa9cf7 Merge pull request #186 from groot99-droid/claude/r8-body-4 [merge]
- 2026-10-24 73fe36a7 Merge the base at 62aa9cf (#186 merged) into r8-townsfolk-mug [merge]
- 2026-10-24 6f4dc8bb Merge the round-8 base (with #186) into r8-body-5 [merge]
- 2026-10-24 e5042bc2 Merge pull request #206 from groot99-droid/claude/r8-townsfolk-mug [merge]
- 2026-10-24 94e1adff Merge the base at e5042bc (#206 merged) into r8-townsfolk-mug-run [merge]
- 2026-10-24 a832a923 Merge the round-8 base (with #206) into r8-body-5 [merge]
- 2026-10-24 21f4422c Merge pull request #188 from groot99-droid/claude/r8-body-5 [merge]
- 2026-10-24 6ee921a3 Merge the base at 21f4422 (#188 merged) into r8-townsfolk-mug-run [merge]
- 2026-10-24 f21b12c9 Test: one retry on a reset matchmake request in the NPC helpers' connect
- 2026-10-24 d3f81718 Merge claude/zen-turing-m1jnw0 into claude/r8-body-6 [merge]
- 2026-10-24 7075c5d3 Merge pull request #256 from groot99-droid/claude/r8-shelf-pages [merge]
- 2026-10-24 a38960cb Merge pull request #207 from groot99-droid/claude/r8-townsfolk-mug-run [merge]
- 2026-10-24 b057dcfe A knockout drops coins; the bakery sells the Wake Loaf (GDD 3.23)
- 2026-10-24 e3a76e9f Compare the round-tripped page's pixels natively, not with toEqual
- 2026-10-24 8779afb1 Merge the base at a38960c (#207 merged) into r8-townsfolk-mug-ui [merge]
- 2026-10-24 155701cd 8D: the meeting's Papers tab: present a Seal or an Indulgence, show or burn a notice
- 2026-10-24 ba3d5f26 Pin the bat's roam in the bat kill test; the unpinned roam can trap it in a wall
- 2026-10-24 e0a517ae Merge zen-turing base; HollowMere/BlackPine in the HUD scene label, landing eyebrow, end-of-match lines, Butler and Vicar cards, README [merge]
- 2026-10-24 c19bedb1 Test: R17 allows the body stream (granted by 6Z)
- 2026-10-24 c337c1d5 8H step 5: body HUD motion (bar easing, hit flash, fresh and cured chips, bleeding vignette, Dazed blur)
- 2026-10-24 8337203b Turn off the NPC test server's keep-alive timeout
- 2026-10-24 10e6538b Turn off the NPC test server's keep-alive timeout
- 2026-10-24 ba49e688 Turn off the NPC test server's keep-alive timeout
- 2026-10-24 4e3d2a90 8H body motion: read-only on 8A's panel (cured copies in an own layer), stops when the panel unmounts
- 2026-10-24 e0086f74 Merge pull request #259 from groot99-droid/claude/r8-seal-meeting [merge]
- 2026-10-24 23d3090e Merge pull request #209 from groot99-droid/claude/r8-townsfolk-mug-ui [merge]
- 2026-10-24 e0853ac7 Merge pull request #262 from groot99-droid/claude/r8-ui-motion-body [merge]
- 2026-10-24 6324eb11 Merge pull request #258 from groot99-droid/claude/r8-scrip-ko [merge]
- 2026-10-24 7388d020 Merge pull request #253 from groot99-droid/claude/r8-body-6 [merge]
- 2026-10-24 449bd478 Merge pull request #257 from groot99-droid/claude/r8-talk [merge]
- 2026-10-24 f0f8b99d Merge pull request #243 from groot99-droid/claude/r8-canon-r1 [merge]
- 2026-10-24 c285e472 Merge pull request #244 from groot99-droid/claude/r8-canon-r2 [merge]
- 2026-10-24 b6ea1d47 Round 9: record the owner's world-mode brief verbatim (DECISIONS A222)
- 2026-10-24 33ccb2d5 Round 9: the owner's follow-up answers and the approved design-round plan
- 2026-10-25 88453d91 Merge pull request #264 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 04a1f4c1 Round 9 (9C): living world and emergent play design
- 2026-10-25 dd42d03f Round 9 (9B): failure messages design and prop census script
- 2026-10-25 6106134e Round 9 (9B): logic table, interactions.json schema and prop audit
- 2026-10-25 af7487ba Round 9 (9A): world mode and phases design
- 2026-10-25 0105768d Round 9 (9C): reconcile with 9B's logic table
- 2026-10-25 c90d5316 Round 9 (9B): neutral skinning tool, secrecy check, berries, game and stew rows, curfew lock note
- 2026-10-25 cc8306e5 Merge pull request #267 from groot99-droid/claude/r9-world-mode [merge]
- 2026-10-25 703e7a96 Merge pull request #265 from groot99-droid/claude/r9-living-world [merge]
- 2026-10-25 ef7fa70a Merge pull request #266 from groot99-droid/claude/r9-logic-table [merge]
- 2026-10-25 5938aa0f Round 9: the owner's second follow-up, verbatim, with 6Z's reading (sleep, busy NPCs, jail, armour, accounts, rent)
- 2026-10-25 c1eb40ff Merge pull request #268 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 48bf2525 Round 9: the owner's clarification, the world works without the Killer (answers WM1)
- 2026-10-25 d4f6f76d Merge pull request #269 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 f16a6cb0 Round 9: the owner's questionnaire answers, verbatim (42 defaults, 12 changes); README status
- 2026-10-25 ae1ed5db Round 9 (9D): fold the owner answers into world-mode.md
- 2026-10-25 51f1d5dc Round 9 (9D): fold the owner answers into phases.md
- 2026-10-25 212fead9 Merge pull request #270 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 52a66760 Round 9 (9D): fold the owner answers into logic-table.md
- 2026-10-25 cb2813aa docs(round9): fold owner answers into failures and living-world (9D)
- 2026-10-25 4d91be89 docs(round9): fold owner answers into emergent-play (9D)
- 2026-10-25 f8d6bf77 docs(round9): add the GDD map (9D)
- 2026-10-25 ddc9d7e2 docs(round9): add the round-10 build plan (9D)
- 2026-10-25 ad712e84 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-gdd-map [merge]
- 2026-10-25 97a692b2 Merge pull request #271 from groot99-droid/claude/r9-gdd-map [merge]
- 2026-10-25 3a8ff4cd docs(round9): the admin Studio contract (creative mode, room editor, reports)
- 2026-10-25 3be69129 Merge pull request #263 from groot99-droid/claude/lucid-dijkstra-8kvpkz-keepalive [merge]
- 2026-10-25 669ffff8 Merge pull request #260 from groot99-droid/claude/lucid-dijkstra-8kvpkz [merge]
- 2026-10-25 13490196 Merge pull request #261 from groot99-droid/claude/lucid-dijkstra-8kvpkz-mobs [merge]
- 2026-10-25 3b79f9b4 Merge pull request #272 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 c3c6b391 feat(server): StudioRoom behind the admin gate, creative mode (9S, S1)
- 2026-10-25 4d2e3693 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server [merge]
- 2026-10-25 01b8d1da sim/Mobs: a creature no longer walks into a wall corner on its way to a roam goal
- 2026-10-25 2aa241f4 Merge pull request #274 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 a24eedf4 feat(server): Studio GitHub client and report routes (9S, S2)
- 2026-10-25 6fb8f997 feat(shared): the Studio wire types (9S, S1 split, part 1)
- 2026-10-25 803ea890 refactor(server): trim S1 to the room, the gate and the walk (9S)
- 2026-10-25 a08df12d Studio S1b: noclip, teleport, doors and profile in the Studio sim
- 2026-10-25 8c3c091d Studio S1c: time of day, clock, stand-ins and give
- 2026-10-25 f16bba01 Merge pull request #276 from groot99-droid/claude/r9-studio-protocol [merge]
- 2026-10-25 6338e2fc Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server-s2 [merge]
- 2026-10-25 ca12621c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server [merge]
- 2026-10-25 afe34991 Merge branch 'claude/r9-studio-server' into claude/r9-studio-server-s1b [merge]
- 2026-10-25 6b485113 Merge remote-tracking branch 'origin/claude/r9-studio-server-s1b' into claude/r9-studio-server-s1c [merge]
- 2026-10-25 4a6c4f6e feat(client): the Studio page at #/studio, creative-mode HUD over the studio room (9T, T1)
- 2026-10-25 4efa7351 Move the grid-to-nav function into @wdi/shared (navFromGrid)
- 2026-10-25 6121b080 Merge remote-tracking branch 'origin/claude/r9-studio-server-nav' into claude/r9-studio-server-s3 [merge]
- 2026-10-25 180bae02 refactor(client): split the Studio PR: T1a keeps the route, sign-in, network layer and scene
- 2026-10-25 05cb0734 feat(client): the Studio creative-mode HUD and the ?mock=1 feed (9T, T1b)
- 2026-10-25 f7bcdd96 fix(client): a refused Studio command stays on screen until the next command
- 2026-10-25 92892bb1 Studio S3: POST /studio/save re-checks a scene and opens a draft PR
- 2026-10-25 0f1bd004 fix(client): resend a held Studio move every tick
- 2026-10-25 e21c57f3 Merge claude/r9-studio-client into claude/r9-studio-client-t1b [merge]
- 2026-10-25 62baeff1 Merge pull request #275 from groot99-droid/claude/r9-studio-server-s2 [merge]
- 2026-10-25 62a6026d Merge pull request #273 from groot99-droid/claude/r9-studio-server [merge]
- 2026-10-25 440ad300 feat(client): the Studio overlays: collision, walkable links, cursor tile, ids, lights, sight, footprints, gating (9T, T2)
- 2026-10-25 83156d46 Merge pull request #280 from groot99-droid/claude/r9-studio-server-nav [merge]
- 2026-10-25 6af58309 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t3 [merge]
- 2026-10-25 6e632a99 wip
- 2026-10-25 b816bc68 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server-s3 [merge]
- 2026-10-25 4fdbd04e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server-s1b [merge]
- 2026-10-25 3b233752 Merge pull request #279 from groot99-droid/claude/r9-studio-client [merge]
- 2026-10-25 cf6f8866 Merge branch 'claude/r9-studio-server-s1b' into claude/r9-studio-server-s1c [merge]
- 2026-10-25 1531c4c2 feat(client): the Studio report tool and Inbox: screenshot with arrow and circle, note, auto context, F8 (9T, T3)
- 2026-10-25 2b18b171 Merge base into claude/r9-studio-client-t1b [merge]
- 2026-10-25 219285c1 Merge claude/r9-studio-client-t1b into claude/r9-studio-client-t2 [merge]
- 2026-10-25 852692c5 Merge claude/r9-studio-client-t2 into claude/r9-studio-client-t3 [merge]
- 2026-10-25 5fa420c8 feat(client): the Studio editor's core: scene edits, undo and redo, diff, picking, frozen-id references (9T, T4a)
- 2026-10-25 0c240425 Studio S4: live stand-ins run their kind's brain on the Studio clock
- 2026-10-25 22a3ab02 feat(client): the Studio editor view and panel: Edit toggle, palette, selection, drag to move, undo and redo, diff (9T, T4b)
- 2026-10-25 39c68d4a Merge pull request #277 from groot99-droid/claude/r9-studio-server-s1b [merge]
- 2026-10-25 a0202625 Merge pull request #281 from groot99-droid/claude/r9-studio-client-t1b [merge]
- 2026-10-25 82001cc9 Merge branch 'claude/zen-turing-m1jnw0' into claude/r9-studio-client-t2 [merge]
- 2026-10-25 b4886a5e Merge remote-tracking branch 'origin/claude/r9-studio-client-t2' into claude/r9-studio-client-t3 [merge]
- 2026-10-25 427fba05 Merge remote-tracking branch 'origin/claude/r9-studio-client-t3' into claude/r9-studio-client-t4a [merge]
- 2026-10-25 f28b70ac Merge remote-tracking branch 'origin/claude/r9-studio-client-t4a' into claude/r9-studio-client-t4b [merge]
- 2026-10-25 c93540ee Move the tilemap builder into @wdi/content/tilemap for the Studio save
- 2026-10-25 cfa94eca Merge remote-tracking branch 'origin/claude/r9-studio-server-tilemap' into claude/r9-studio-server-s3 [merge]
- 2026-10-25 bc500f05 Studio T5a: grid paint (brush, rectangle, fill) and resize with the list of ids a shrink would cut
- 2026-10-25 5ec5aaee Studio S3: commit the regenerated tilemap with a save and refuse unknown keys
- 2026-10-25 f0dc2bf7 Format the save route test
- 2026-10-25 3bfbbd31 Studio T5b: gates and paths in the editor, grid and route lines in the diff
- 2026-10-25 785c0d86 Studio T5c: live checks in the editor (schema, checkGrid, checkSceneWorld, validateContent with the edited scene swapped in, reachability)
- 2026-10-25 e0387f91 Merge pull request #278 from groot99-droid/claude/r9-studio-server-s1c [merge]
- 2026-10-25 5cc374dd Merge pull request #282 from groot99-droid/claude/r9-studio-client-t2 [merge]
- 2026-10-25 459c171e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server-s4 [merge]
- 2026-10-25 1569dc63 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t3 [merge]
- 2026-10-25 cb349e1a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t4a [merge]
- 2026-10-25 cb3b0429 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t4b [merge]
- 2026-10-25 f0982401 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5a [merge]
- 2026-10-25 83694160 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 76b7e903 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 3ae7e339 Merge pull request #288 from groot99-droid/claude/r9-studio-server-tilemap [merge]
- 2026-10-25 2f680da6 Studio T5d: Save sends the edited scene to POST /studio/save and shows the draft PR or the problems list
- 2026-10-25 8fa773da Studio S4: give the client mock and figure test the new stand-in fields
- 2026-10-25 a0cbed45 Merge pull request #284 from groot99-droid/claude/r9-studio-client-t3 [merge]
- 2026-10-25 e9cff10c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t4a [merge]
- 2026-10-25 f243f696 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server-s3 [merge]
- 2026-10-25 fc840141 Merge branch 'claude/r9-studio-client-t4a' into claude/r9-studio-client-t4b [merge]
- 2026-10-25 64acd349 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t4b [merge]
- 2026-10-25 7c6283c1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5a [merge]
- 2026-10-25 2b86dffd Merge branch 'claude/r9-studio-client-t4b' into claude/r9-studio-client-t5a [merge]
- 2026-10-25 e9f974b0 Merge branch 'claude/r9-studio-client-t5a' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 a6de0616 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 2412ee62 Merge branch 'claude/r9-studio-client-t5b' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 83c5bb50 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 d0425da7 Merge branch 'claude/r9-studio-client-t5c' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 5e5a154b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 4e0e9cd2 Merge remote-tracking branch 'origin/claude/r9-studio-server-s4' into claude/r9-studio-server-s5 [merge]
- 2026-10-25 93c18dd4 Studio S5: walk an unsaved draft of a scene (POST /studio/draft)
- 2026-10-25 7f27be28 Studio T5e: Walk it
- 2026-10-25 718e89bf Merge pull request #285 from groot99-droid/claude/r9-studio-client-t4a [merge]
- 2026-10-25 4c0c975a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t4b [merge]
- 2026-10-25 43892182 Merge branch 'claude/r9-studio-client-t4b' into claude/r9-studio-client-t5a [merge]
- 2026-10-25 6d034296 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5a [merge]
- 2026-10-25 25f03fae Merge branch 'claude/r9-studio-client-t5a' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 6ed27eae Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 4c9ab0cf Merge branch 'claude/r9-studio-client-t5b' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 1fa73fcd Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 db2ad181 Merge branch 'claude/r9-studio-client-t5c' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 0b23b8a6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 304e1af0 Merge branch 'claude/r9-studio-client-t5d' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 46a51364 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 983a8032 Merge pull request #283 from groot99-droid/claude/r9-studio-server-s3 [merge]
- 2026-10-25 3324c800 Merge pull request #287 from groot99-droid/claude/r9-studio-server-s4 [merge]
- 2026-10-25 f87e8e10 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-server-s5 [merge]
- 2026-10-25 7aeb86ee Merge pull request #286 from groot99-droid/claude/r9-studio-client-t4b [merge]
- 2026-10-25 941a4f74 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5a [merge]
- 2026-10-25 ba1d14a4 Merge branch 'claude/r9-studio-client-t5a' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 9a5b8d8d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 1ba5f105 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 4e433f1d Merge branch 'claude/r9-studio-client-t5b' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 0e317426 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 c1ce5217 Merge branch 'claude/r9-studio-client-t5c' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 16302ae0 Merge branch 'claude/r9-studio-client-t5d' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 8f325631 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 0e8fe858 Studio client: saveApi uses the shared S3 protocol types
- 2026-10-25 96f1a6fa Merge branch 'claude/r9-studio-client-t5d' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 52c41be8 Studio client: smooth stand-ins from px/py/yaw/moving, mob sense rings under the sight overlay
- 2026-10-25 75fc2eda Merge pull request #289 from groot99-droid/claude/r9-studio-client-t5a [merge]
- 2026-10-25 ca1c064f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5b [merge]
- 2026-10-25 71999ee0 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 094a030c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 c246b8f3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 89717e19 Merge branch 'claude/r9-studio-client-t5b' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 1c2816d9 Merge branch 'claude/r9-studio-client-t5c' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 812c3248 Merge branch 'claude/r9-studio-client-t5d' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 3b332fe4 Merge pull request #294 from groot99-droid/claude/r9-studio-server-s5 [merge]
- 2026-10-25 c8285a31 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 5cc4f7bd Studio client: draftApi uses the shared S5 protocol types
- 2026-10-25 51a6e599 Merge pull request #290 from groot99-droid/claude/r9-studio-client-t5b [merge]
- 2026-10-25 564bf1e5 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5c [merge]
- 2026-10-25 eca4399f Merge branch 'claude/r9-studio-client-t5c' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 2588010f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 f3b9b371 Merge branch 'claude/r9-studio-client-t5d' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 4263201f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 6a2aa77b server tests: stop two wall-clock flakes (npcRoutine timeout, coverPick waits)
- 2026-10-25 dc4f282e Merge pull request #291 from groot99-droid/claude/r9-studio-client-t5c [merge]
- 2026-10-25 ad5cc474 Merge pull request #295 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 f5f139ae Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5d [merge]
- 2026-10-25 7b144495 Merge branch 'claude/r9-studio-client-t5d' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 d37eef69 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 b5cb738a Merge pull request #292 from groot99-droid/claude/r9-studio-client-t5d [merge]
- 2026-10-25 ce7eba31 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-client-t5e [merge]
- 2026-10-25 fd43b563 Merge pull request #293 from groot99-droid/claude/r9-studio-client-t5e [merge]
- 2026-10-25 46290dc7 Studio editor: the world art follows the edited scene
- 2026-10-25 79058edc docs(round9): Studio modes - Overview, World, Room and NPC editors (owner, 2026-10-25)
- 2026-10-25 7935b6fe Studio editor: a material palette for the grid brush
- 2026-10-25 529bf2cf Studio: prettier on Studio.ts
- 2026-10-25 834c41a6 Merge branch 'claude/r9-studio-editor-art' into claude/r9-studio-editor-materials [merge]
- 2026-10-25 a12ebaff Merge pull request #296 from groot99-droid/claude/r9-studio-editor-art [merge]
- 2026-10-25 3bcb20c6 Merge pull request #297 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-25 c8c41b44 Studio editor: buildings and multi-tile props are movable, deletable and duplicable
- 2026-10-25 22441706 feat(studio): Overview mode, the zoomed-out map of a map's scenes with door links (M2)
- 2026-10-25 90830a02 Merge base into the materials branch [merge]
- 2026-10-25 2fb6012e Merge the materials branch into the buildings branch [merge]
- 2026-10-25 748fae2c feat(studio): Overview graph, auto layout and door re-target logic (M2a)
- 2026-10-25 3814e761 N2: NPC meeting-note lines move into talk.json, unchanged; N1 wire types
- 2026-10-25 09d81da5 Studio editor: givers, nodes, spawners, gates and paths are selectable and movable
- 2026-10-25 be2c47df Studio: NPC editor 1, routines over the world with a phase scrubber (N3)
- 2026-10-25 9b0346c6 Merge pull request #298 from groot99-droid/claude/r9-studio-editor-materials [merge]
- 2026-10-25 d3d707e0 Studio: NPC editor 1a, route geometry and routines.json edit reducers (N3a)
- 2026-10-25 4b5bb4d2 Studio editor: turn props, buildings, spawns and givers; turned art with a mirrored fallback
- 2026-10-25 6da31c6e Merge pull request #301 from groot99-droid/claude/r9-studio-overview-a [merge]
- 2026-10-25 0a1f390e Studio: a mode toggle (Overview, World editor, Room editor, NPC editor) with a registry other modes plug into
- 2026-10-25 c414b56c Merge claude/zen-turing-m1jnw0 into claude/r9-studio-editor-buildings [merge]
- 2026-10-25 dd46e0f2 Studio: frame the NPC route in the camera and fix the panel layout
- 2026-10-25 d582737d Merge pull request #303 from groot99-droid/claude/r9-studio-npc-server [merge]
- 2026-10-25 be5c7dc2 Studio: NPC editor 2a, giver, quest NPC and talk-line edits (N4a)
- 2026-10-25 b0d25df8 Studio: NPC editor 2a, giver, quest NPC and talk-line edits (N4a)
- 2026-10-25 f51da652 Merge branch 'claude/r9-studio-npc-people-pure' into claude/r9-studio-npc-people [merge]
- 2026-10-25 0b69a266 N1: generalised Studio save for the content allowlist, and the NPC-data draft
- 2026-10-25 0faf74ba Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r9-studio-npc-server-n1 [merge]
- 2026-10-25 cbd2d86d Studio: NPC editor 2b, givers, quest NPCs and talk lines in the NPC panel (N4b)
- 2026-10-25 53190415 N1: the NPC draft takes routines and quests only; looks.json is never edited
- 2026-10-25 274fc945 Merge pull request #299 from groot99-droid/claude/r9-studio-editor-buildings [merge]
- 2026-10-25 770ce180 Merge pull request #305 from groot99-droid/claude/r9-studio-npc-routes-a [merge]
- 2026-10-25 02a38d5b Merge pull request #308 from groot99-droid/claude/r9-studio-npc-people-pure [merge]
- 2026-10-25 27aa3ee9 Merge claude/zen-turing-m1jnw0 into claude/r9-studio-editor-movables [merge]
- 2026-10-25 72ae5304 Merge claude/zen-turing-m1jnw0 into claude/r9-studio-overview [merge]
- 2026-10-25 3e2367dd Close the last Overview rule in studio.css after the merge
- 2026-10-25 0ecc2934 N1: a quest NPC wears the villager family only, never a card's look
- 2026-10-25 5978cd38 Merge pull request #300 from groot99-droid/claude/r9-studio-overview [merge]
- 2026-10-25 9e527235 Merge pull request #302 from groot99-droid/claude/r9-studio-editor-movables [merge]
- 2026-10-25 68242fa3 Merge claude/zen-turing-m1jnw0 into claude/r9-studio-editor-rotation [merge]
- 2026-10-25 4f38557f Merge pull request #309 from groot99-droid/claude/r9-studio-npc-server-n1 [merge]
- 2026-10-25 010faeab Merge claude/zen-turing-m1jnw0 into claude/r9-studio-npc-routes [merge]
- 2026-10-25 72e50a19 Merge claude/r9-studio-npc-routes into claude/r9-studio-npc-people [merge]
- 2026-10-25 e071b9ec Merge pull request #306 from groot99-droid/claude/r9-studio-editor-rotation [merge]
- 2026-10-25 63bc5615 Merge claude/zen-turing-m1jnw0 into claude/r9-studio-modes [merge]
- 2026-10-25 78479623 Merge pull request #304 from groot99-droid/claude/r9-studio-npc-routes [merge]
- 2026-10-25 5ced9d61 Merge claude/zen-turing-m1jnw0 into claude/r9-studio-npc-people [merge]
- 2026-10-25 8e34e0f2 Merge pull request #310 from groot99-droid/claude/r9-studio-npc-people [merge]
- 2026-10-25 42a6b5f8 Merge claude/zen-turing-m1jnw0 into claude/r9-studio-modes [merge]
- 2026-10-25 e6d84d88 Studio: Overview and NPC open through registerMode
- 2026-10-25 2223d7a5 Merge pull request #307 from groot99-droid/claude/r9-studio-modes [merge]
- 2026-10-26 dc99a110 Bandage: a struck survivor's screen blacks out and the witnesses write Claimed entries
- 2026-10-26 ad20e42e Merge pull request #311 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-26 50fde85b Round 9: the owner's follow-up calls, recorded and folded into the design
- 2026-10-27 debd4eac Merge pull request #312 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-27 2d6303f3 Inventory: 24 slots instead of 5
- 2026-10-27 fd2ce5b3 Test: the task pick-up refusal fills the real pack size
- 2026-10-27 72f1b69d Merge pull request #313 from groot99-droid/claude/game-features-admin-planning-v43tvq [merge]
- 2026-10-29 876357b5 Round 10: the contract, the sessions by model and the compaction sizes
- 2026-10-29 e0fa7fa6 Spawn branch: compaction at 300k (docs/round10/README.md, Compaction)
- 2026-10-29 f107d04e Spawn branch: compaction at 800k (docs/round10/README.md, Compaction)
- 2026-10-29 580e5d9a Merge pull request #314 from groot99-droid/claude/laughing-planck-vt4dcs [merge]
- 2026-10-29 01d02268 A9: the logic table's schema and validator
- 2026-10-29 0d9ac9bd A1: refusal reasons, the error frame and the copy lines
- 2026-10-29 274d6aa4 A5: pacing for world mode, 810 s cycle and 12 cycles
- 2026-10-29 4cce53f3 Merge pull request #315 from groot99-droid/claude/r10-a9-interactions [merge]
- 2026-10-29 edf0f9d8 A5: adapt the server tests to the 810 s cycle
- 2026-10-29 2a7e68e3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a1-refusals [merge]
- 2026-10-29 9aab0387 Round 10 seams: the prop-state wire row and the schema bump, on 10F's request
- 2026-10-29 6ff90e3d A5: run the long auto-match tests on the old 230 s clocks
- 2026-10-29 a19125e6 A5: R9 completes its isolation by restoring health
- 2026-10-29 ad1ebf39 Round 10 seams: the prop-state wire row and the schema bump (#318) [merge]
- 2026-10-29 513d75d2 A5: the body invariant leaves foreign rows alone on a dead seat
- 2026-10-29 6654e426 Round 10 A1: refusal reasons, the error frame and the copy lines (10A) (#316) [merge]
- 2026-10-29 4b310887 Spawn branch: merge the base at 6654e42 (A1 merged) before spawning 10G [merge]
- 2026-10-29 7a2ec178 Round 10 seams: the inventory messages and fields for A12, on 10A's request
- 2026-10-29 1f6fa150 A10: the logic table's resolver behind act.hold {action: 'interact'}
- 2026-10-29 70614aff Round 10 A2: rooms/ refusals carry a reason (10G)
- 2026-10-29 8982e7bf Merge base into A5 [merge]
- 2026-10-29 8b61e1b6 A10: regenerate docs/PROTOCOL.md for the interact hold and PropState
- 2026-10-29 cc202792 Round 10 seams: the inventory messages and fields for A12 (#319) [merge]
- 2026-10-29 6038b182 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a6-mobs [merge]
- 2026-10-29 a7da8eec A6: weaker mobs; Bleeding and Poisoned stop at 1 health
- 2026-10-29 9756d305 A6: format damage.ts
- 2026-10-29 fb115aa9 A12: the inventory's slots on the server (GDD 3.30, DECISIONS A245)
- 2026-10-29 24e2dfef Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a10-resolver [merge]
- 2026-10-29 04863db0 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a2-rooms [merge]
- 2026-10-29 6f2816ca A6: the townsfolk test bites until the figure is at one hit point
- 2026-10-29 fc1be704 A5: pacing, the day and night clocks (8 min days, 5 min nights, 12 cycles) (#317) [merge]
- 2026-10-29 8ff5bbb7 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-a2-rooms [merge]
- 2026-10-29 ec9fe45b A12: move inv.move and inv.select to their own PR (6Z's split)
- 2026-10-29 a6cfe6e1 A12b: inv.move and inv.select, consumed in step() (GDD 3.30, DECISIONS A245)
- 2026-10-29 9874d348 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a10-resolver [merge]
- 2026-10-29 41485d73 Merge the round-10 base into A6 [merge]
- 2026-10-29 aa2b3cbe Round 10 A2: rooms/ refusals carry a reason (10G) (#320) [merge]
- 2026-10-29 409f2e18 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a12-inventory [merge]
- 2026-10-29 aaf014b3 Round 10 A3a: economy, body and neighbouring sim refusals carry a reason (10G)
- 2026-10-29 8b9a0b33 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a10-resolver [merge]
- 2026-10-29 212e92d7 Merge branch 'claude/r10-a12-inventory' into claude/r10-a12b-moves [merge]
- 2026-10-29 b7fb805a Round 10 seams: Private.home for A7a and A7b's exhausted row
- 2026-10-29 b1373ca0 Round 10 seams: the sleeper's fields in wire row 5, and the homes stream
- 2026-10-29 5bdfd0c5 A10: the logic table's resolver behind act.hold interact (10F) (#321) [merge]
- 2026-10-29 637f43c5 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a12-inventory [merge]
- 2026-10-29 7345b10a Round 10 seams: a session's nth decision row, and the sleeper's count fields named
- 2026-10-29 d644a26d Round 10 A3b: top-level sim refusals carry a reason; the legacy form goes (10G)
- 2026-10-29 b9ed4ddf Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a3-sim [merge]
- 2026-10-29 df9d89ae Merge claude/r10-a3-sim into claude/r10-a3-sim2 [merge]
- 2026-10-29 78097d83 Merge the round-10 base into A6; note the retired death causes [merge]
- 2026-10-29 1e80f2bf A11: tools on piles (axe, pickaxe, hammer, the walls of the logic table)
- 2026-10-29 e9a08889 A11: prettier on the validator and its test
- 2026-10-29 c069f134 Merge pull request #326 from groot99-droid/claude/laughing-planck-vt4dcs [merge]
- 2026-10-29 1290e83c A11: art ids for the new tools and Logs, atlases rebuilt (m5b only)
- 2026-10-29 84bf4849 Merge pull request #322 from groot99-droid/claude/r10-a6-mobs [merge]
- 2026-10-29 e8719f69 Merge pull request #325 from groot99-droid/claude/r10-a3-sim [merge]
- 2026-10-29 42ac34c4 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a3-sim2 [merge]
- 2026-10-29 9e74503f Spawn branch: merge the base (A6, A3a and the contract updates) into the 800k tier [merge]
- 2026-10-29 fc17b415 Round 10 README: a tiered session keeps its window in settings.local.json
- 2026-10-29 cdcfec33 Round 10 A4: the client shows the server's refusal reason (10G)
- 2026-10-29 502a9ad8 Round 10 seams: wire row 6, the seat on the line (C1)
- 2026-10-29 d6c97092 A7a: greybox frames for the bed, the cot and the inn bed (6Z's grant)
- 2026-10-29 70521800 Merge pull request #323 from groot99-droid/claude/r10-a12-inventory [merge]
- 2026-10-29 e9b2335d Merge pull request #327 from groot99-droid/claude/r10-a11-tools [merge]
- 2026-10-29 1d14a255 Merge the base (A12a, A10, A6, A3a) into A12b [merge]
- 2026-10-29 ac4614d6 Merge base into r10-a3-sim2 [merge]
- 2026-10-29 159caaac Merge pull request #329 from groot99-droid/claude/laughing-planck-vt4dcs [merge]
- 2026-10-29 c5ef4f77 Merge base into r10-a4-display [merge]
- 2026-10-29 a9079c8d Merge pull request #331 from groot99-droid/claude/r10-a7a-bed-frames [merge]
- 2026-10-29 558d05f6 Merge pull request #324 from groot99-droid/claude/r10-a12b-moves [merge]
- 2026-10-29 57ef7a8c Merge base into r10-a3-sim2 [merge]
- 2026-10-29 f3379838 Merge pull request #328 from groot99-droid/claude/r10-a3-sim2 [merge]
- 2026-10-29 292eda4e Spawn branch: merge the base (A3b, A12b and the contract) into the 800k tier [merge]
- 2026-10-29 e35e514f Merge base into r10-a4-display [merge]
- 2026-10-29 b8716881 B1 (WIP): guard figures, the Constables and the Clerk: data, Guards.ts, tests, GDD and A229
- 2026-10-29 c47115bf Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-d1-npc-seats
- 2026-10-29 86e84225 Merge pull request #330 from groot99-droid/claude/r10-a4-display
- 2026-10-29 2372e814 B1: guard hooks in the townsfolk and the fists; schemas, validator and the townsfolk test's counts (6Z's grants)
- 2026-10-29 7ddb9701 A7a: R17 allows the homes stream (6Z's grant, line 901 only)
- 2026-10-29 63416794 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a7a-sleep [merge]
- 2026-10-29 551e61e9 Merge pull request #334 from groot99-droid/claude/laughing-planck-vt4dcs
- 2026-10-29 b5c11ffa Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b1-constables [merge]
- 2026-10-29 4aa365b8 Merge pull request #333 from groot99-droid/claude/r10-d1-npc-seats [merge]
- 2026-10-29 7cc19198 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b1-constables [merge]
- 2026-10-29 18bd6e22 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a13a-grid
- 2026-10-29 f1632f83 Draw townsfolk figures: avatars wearing a figure look
- 2026-10-29 ff0ae9e2 Merge the base (D1, #334) into A7a [merge]
- 2026-10-29 42a162a7 Merge remote-tracking branch 'origin/claude/r10-a13a-grid' into claude/r10-a13b-screen
- 2026-10-29 ab1430e8 Merge pull request #338 from groot99-droid/claude/r10-fix-figures
- 2026-10-29 eabd2c0d Round 11 contract: questions in each document, the planners talk directly
- 2026-10-29 203206df Merge pull request #332: A13a, the crafting grid on the server (craft.grid) [merge]
- 2026-10-29 144dea2f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a13b-screen [merge]
- 2026-10-29 72e1454d Merge base into r10-d2-depletion [merge]
- 2026-10-29 77173804 D2: no free NPC tool (6Z); NPC tools wait for D2b
- 2026-10-29 b7a9ce09 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a7a-sleep [merge]
- 2026-10-29 cccd1605 Merge pull request #336: B1, the Constables and the Clerk as guard figures
- 2026-10-29 65c28519 Merge pull request #339: the round-11 planning contract (the pipeline half) [merge]
- 2026-10-29 14da786d seams.md 3 row 8: the Constables' briefing, a public system line per clue (B2)
- 2026-10-29 4a8e70fd Merge pull request #335: A13b, the inventory screen and the crafting square [merge]
- 2026-10-29 08ddb211 Merge the base at 4a8e70f (A13 merged, the playtest gate) into the 800k tier branch [merge]
- 2026-10-29 91cec1ce B2: the Constables' briefing (runLaw, laws.json lines, law.speedMult and briefingAfterS, GDD 3.31 and 3.4, A249, UI 14.46)
- 2026-10-29 c3169d63 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-29 c6313508 Merge the base (B1, A13b) into A7a [merge]
- 2026-10-29 f75e3bee The 6Z logs: the playtest gate opened (A13 merged), and 11A and 11B started
- 2026-10-29 d94c0681 Merge base into r10-d2-depletion [merge]
- 2026-10-29 3ce455c3 D3: A251 owner cell
- 2026-10-29 f38dfa0b Merge pull request #342: seams.md row 8 (the briefing) and the 6Z logs at the playtest gate [merge]
- 2026-10-29 d0827c4e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-29 97ea566f B2: prefer-const
- 2026-10-29 0094684e Merge pull request #340: D2, depletion (the store sells the tools) [merge]
- 2026-10-29 21ffc728 D3: A231 owner cell (6Z's nit)
- 2026-10-29 934f7a26 Merge base into r10-d3-mill [merge]
- 2026-10-29 447d7222 seams.md 3 row 9: the lock-pick (D5a), and the 6Z log for D2 to D5
- 2026-10-29 564b5af8 A7b: what a bed restores, and Exhaustion for the last one awake
- 2026-10-29 528dd51c Round 10 D5a: the lock-pick rules and server (study door)
- 2026-10-29 cef2c116 Round 11, 11A: the render pipeline (draft)
- 2026-10-29 703a1e10 D3: make the NPC chop test independent of the routine's re-chop
- 2026-10-29 22b9616b D5a: prettier
- 2026-10-29 648cfcb4 pipeline.md: the figures' toon-group defect, pass costs by reference to look.md, HD-1
- 2026-10-29 3398ec60 D5a: regenerate PROTOCOL.md (the lockpick kind)
- 2026-10-29 e7b8f943 seams.md 3 row 10: Walk with me (B8a), and the pairing stream
- 2026-10-29 f56f3d48 Merge pull request #337: A7a, sleeping (homes, beds and the night skip) [merge]
- 2026-10-29 a6dbc76e Merge the base (A7a and the rest) into A7b [merge]
- 2026-10-29 a5a69719 Merge base into r10-d3-mill [merge]
- 2026-10-29 db701fb8 pipeline.md 5.4: 10Y's round-10 remap, kept and tested by the re-render plan
- 2026-10-29 31529e28 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-29 ebed2192 Merge the base (A7a, D2) into C1a; the sleep count reads isOnLine
- 2026-10-29 352f5016 B8a (WIP): Walk with me, the pairing state and the wire
- 2026-10-29 8265d6b6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b8a-pairing [merge]
- 2026-10-29 c7fdf9f0 C1a: rewrap the Sleep.ts note
- 2026-10-29 b415f9e5 pipeline.md 2.2: the HD packed cell is 256 px, as the code and art.md 3 have it
- 2026-10-29 7aa67437 C1a: the sleep count calls isOnLine at call time (import cycle)
- 2026-10-29 6b6da80c docs(round11): 11B look.md draft: materials, styles, budgets, V2, measured figure costs
- 2026-10-29 b2206ce0 pipeline.md: 11B's answers (emit cap, taaSamples 8 with its condition, AO per style) by reference to look.md
- 2026-10-29 9c2343ab docs(round11): 11B samples, 11A's answers, figure-role finding, cross-references
- 2026-10-29 a7f00e76 D5a: a picked lock stays open in the depletion test
- 2026-10-29 807ca30f Merge pull request #345: seams.md rows 9 and 10 (the lock-pick, Walk with me) and the 6Z log [merge]
- 2026-10-29 708c886f Merge the base (#345, seams rows 9 and 10) into C1a [merge]
- 2026-10-29 abee2ee1 A8: the sleeping screen (bed prompt, asleep overlay, You slept through)
- 2026-10-29 f24c3132 Merge pull request #346: round 11, 11A, the render pipeline (design) [merge]
- 2026-10-30 8d397ff1 docs(round11): 11B Q10 per 6Z's ruling (M5b art into the rig last, pipeline.md P9); constable art is 10Y's
- 2026-10-30 a40b1bc6 Merge base into r10-d5-lockpick [merge]
- 2026-10-30 c9df36a3 A7b: the shared schema test lists exhausted: 13
- 2026-10-30 a5d1475c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-a7b-rest [merge]
- 2026-10-30 7e691dec Merge the base (#346, round 11 design docs) into C1a [merge]
- 2026-10-30 6725ef41 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-30 5c5c924a B8a: Walk with me on the server (pairing, the follow, the shield; GDD 3.31, A269)
- 2026-10-30 b99360c0 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b8a-pairing [merge]
- 2026-10-30 713d172e Round 11: the owner's questionnaire (questions.md), assembled from 11A and 11B
- 2026-10-30 805ebebf Merge pull request #348: A8, the bed prompt and the asleep screen [merge]
- 2026-10-30 0a737a61 Merge the base (A8, #348) into A7b; GDD 3.32 keeps both paragraphs [merge]
- 2026-10-30 233709b9 Merge pull request #343: D3, the mill and timber (head saw, saw horse) [merge]
- 2026-10-30 e0cd310f C1b: the On-the-line screen, the ghost flag that clears on the return, and the You-are-back toast
- 2026-10-30 ba3ca8c8 Merge the base (D3, A8) into C1a [merge]
- 2026-10-30 8af5fef6 Merge pull request #347: round 11, 11B, materials, styles and budgets (look.md) [merge]
- 2026-10-30 e05c0b37 Merge C1a (with the base at D3) into C1b [merge]
- 2026-10-30 e02ed7e3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-30 771c0204 Merge base into r10-d5-lockpick [merge]
- 2026-10-30 66b5d88c Merge pull request #350: round 11, the owner's questionnaire (questions.md) [merge]
- 2026-10-30 15c40345 seams.md 5: A8 took UI.md 14.46, so 10B's copy moves to 14.50; the Round 10 log
- 2026-10-30 5fdf32df C1a: a seat on the line hears no meeting (phases.md 4), with its test
- 2026-10-30 8aa596cf Merge C1a (the meeting line) into C1b [merge]
- 2026-10-30 78576bbc C1b: 6Z's review: no meeting on the line, the true kept line, the clock through a meeting
- 2026-10-30 42b8e196 Merge pull request #352: seams.md 5, 10B's copy moves to UI.md 14.50; the Round 10 log [merge]
- 2026-10-30 8af3bf9f Split the npcDepletion chop assertion per condition so a flake names its cause
- 2026-10-30 1f4df773 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-d5-lockpick [merge]
- 2026-10-30 6a7d2a53 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-30 d61e7654 Merge pull request #349: A7b, what a bed restores, and Exhaustion [merge]
- 2026-10-30 ec42d8cd B8a: the pairing stream in the auto runner's list
- 2026-10-30 dbb32b9d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b8a-pairing [merge]
- 2026-10-30 5285b2b6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-30 b2298e5a Merge the base (A7b) into C1a [merge]
- 2026-10-30 55f4712b Merge C1a (with the base at A7b) into C1b [merge]
- 2026-10-30 1e62f156 Lock-pick: refuse a trace faster than the clock, keep NFY for other mini-game kinds, test the leak
- 2026-10-30 5530bc5e B8a: regenerate docs/PROTOCOL.md (pair.ask, pair.answer)
- 2026-10-30 fd7e954f Merge the round 10 base into the lock-pick branch [merge]
- 2026-10-30 9426f9eb Merge pull request #341: C1a, the train returns the day's dead, and the Dusk Train [merge]
- 2026-10-30 5d362b8c Merge pull request #351: C1b, the On-the-line screen and the return [merge]
- 2026-10-30 55a35d9b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b2-briefing [merge]
- 2026-10-30 b046fd1c Round 10 seams: wire rows 11 (C2, Owing the line) and 12 (D5c, the scratch)
- 2026-10-30 ea8b5a87 C2a: Owing the line: the fare per return, the pay cut while it is owed, paid at the bank after the rent
- 2026-10-30 8e10105c C2a: halves with the fraction carried (6Z), not rounded down
- 2026-10-30 d1013d3e Round 10 D4a: the bakery's parts and the Herb Bread
- 2026-10-30 791cc77b Merge pull request #353: D5a, the lock-pick, rules and server [merge]
- 2026-10-30 d438d4a0 D4a: the Resistant icon in palette, its SPRITES line, and no held-tool art for foods
- 2026-10-30 6af4aa87 D4a: the client recipe list names the bakery's recipes
- 2026-10-30 36881d35 Merge pull request #354: seams rows 11 (C2) and 12 (D5c) [merge]
- 2026-10-30 1061da18 Merge the base (D5a, seams row 11) into C2a [merge]
- 2026-10-30 40f664f2 Merge pull request #344: B2, the Constables' briefing [merge]
- 2026-10-30 16bdac41 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b8a-pairing [merge]
- 2026-10-30 c61e83a9 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b8a-pairing [merge]
- 2026-10-30 919d16ba Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-d4a-food [merge]
- 2026-10-30 286c1341 Round 10 seams: wire row 13 (B3a, petitions) and the log since #354
- 2026-10-30 39b4ac4f B3a: petitions on the server (wire row 13, warrants, the Constable's signature; GDD 3.31, A289)
- 2026-10-30 38b05fb2 Round 10 D5b: the lock-pick screen
- 2026-10-30 9d7840c5 Round 10 D5c: the scratch clue and the trespass fine
- 2026-10-30 ed5e79ca Merge pull request #356: seams row 13 (B3a, petitions) and the log [merge]
- 2026-10-30 01a2c9cf Merge pull request #357: Round 10 D4a, the bakery's parts and the Herb Bread [merge]
- 2026-10-30 b29fff6f Merge the base (B2, seams row 13) into C2a [merge]
- 2026-10-30 cada555a Merge the round 10 base into the lock-pick screen branch [merge]
- 2026-10-30 8e865850 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b8a-pairing [merge]
- 2026-10-30 756ce5a3 B8a: the pair payloads below inv.select's line (6Z's nit)
- 2026-10-30 a4981fde Round 10 seams: row 10 gains declined; log D4a and the D5b grants
- 2026-10-30 d860d995 B8a: regenerate docs/PROTOCOL.md
- 2026-10-30 896080aa Merge the base (D4a) into C2a [merge]
- 2026-10-30 84a15c4a Merge the round 10 base into the scratch branch [merge]
- 2026-10-30 f930ae4a Merge pull request #358: Round 10 D5b, the lock-pick screen [merge]
- 2026-10-30 f681cace Merge the round 10 base into the scratch branch; the Notebook line in UI.md 14.48 [merge]
- 2026-10-30 9fee056f Merge pull request #360: Round 10 seams, row 10 gains declined; log D4a and the D5b grants [merge]
- 2026-10-30 468fcc0b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3-petition [merge]
- 2026-10-30 26766e82 Round 10 D6a: armour with properties
- 2026-10-30 10083ca4 Merge pull request #355: B8a, Walk with me on the server (10B) [merge]
- 2026-10-30 17033076 Merge the base (B8a) into C2a: Private keeps pair and fare after onLine [merge]
- 2026-10-30 8fad1900 Round 10 D6a: armour with properties
- 2026-10-30 3b86afe5 B3a: an accused's grace and an opener's grace kept apart
- 2026-10-30 3097ec78 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3-petition [merge]
- 2026-10-30 dd118ef7 B3a: regenerate docs/PROTOCOL.md (petition.open, petition.sign)
- 2026-10-30 2e074407 Merge pull request #361: Round 10 D5c, the scratch clue and the trespass fine [merge]
- 2026-10-30 1c889c50 Round 10 seams: row 12 matches D5c; log D5b, B8a, D5c and the D6 ruling
- 2026-10-30 e9e1a328 Round 10 D6a: armour to the tier table, body and head slots, cap
- 2026-10-30 cf07a65e Merge pull request #362: Round 10 seams, row 12 matches D5c; log D5b, B8a, D5c and the D6 ruling [merge]
- 2026-10-30 52350970 Merge base into D6a [merge]
- 2026-10-30 9622c32b B3a: the A170 leak test over petition.open and petition.sign
- 2026-10-30 56ea4996 Merge the base (D5c) into C2a [merge]
- 2026-10-30 58c56463 Round 10 D6b: the skinning knife, hide and game (wip, docs follow)
- 2026-10-30 3e66aa11 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3-petition [merge]
- 2026-10-30 4269a03b Round 10 D6a: only a creature's bite takes the Lodge perk
- 2026-10-30 ef339a3f Round 10 D6a: drop two stray node_modules links
- 2026-10-30 9b1bbfdc Round 10 D6b: skinning docs, client and sprite test lists
- 2026-10-30 a51e0d18 Merge pull request #359: C2a, owing the line (10C) [merge]
- 2026-10-30 83fcf615 Round 10 seams: row 14, the manhunt; log C2a, the D6a review and the B4 ruling
- 2026-10-30 ef4a3853 Merge base into D6a [merge]
- 2026-10-30 30d8d8f9 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3-petition [merge]
- 2026-10-30 f0f6c079 C2b: the Clerk's labour errand, the dear stall, an NPC seat's errand, the fare on the purse, the two-day check
- 2026-10-30 8fc59719 Merge pull request #365: Round 10 seams, row 14 (the manhunt); log C2a, the D6a review and the B4 ruling [merge]
- 2026-10-30 5af75d20 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3-petition [merge]
- 2026-10-30 1291357e Petitions: count every free human in the bar, fix it at open, keep a signature once given (6Z review)
- 2026-10-30 6a44dfeb Petitions: fix the Constables' gate at open, like the bar (6Z review)
- 2026-10-30 f7ee6d91 Merge the base (#365, seams row 14) into C2b [merge]
- 2026-10-30 b1e45179 C2b: regenerate PROTOCOL.md for the errand hold
- 2026-10-30 38765933 Round 10 D6a: drop a stray node_modules link
- 2026-10-30 6c70f991 Merge D6a into D6b [merge]
- 2026-10-30 473f2330 Spawn branch: merge the base at 8fc5971 before spawning 10X and 10Y [merge]
- 2026-10-30 0d61d02d Round 10: 10X and 10Y start early, with their copy sections; log the owner's B5 ruling
- 2026-10-30 8769956a C2b: npcRoutine P1 and P1b know the errand hold (6Z's grant)
- 2026-10-30 2d855434 x1: the refusal words 10G's sweep left (A233)
- 2026-10-30 93ed6374 Round 10 D7: rent in kind, goods taken at dusk, the boarded house and its boards
- 2026-10-30 a09a9f62 Petitions: the balance schema's comment says the bar counts every seat and is fixed at open
- 2026-10-30 5f6f9ea0 B4: the manhunt (warrant queue, the cuff by face, huntScene, the Constables' cuff, the timeout)
- 2026-10-30 add4ded2 B4: a seat killed while cuffed walks free; warrants signed by two others in the tests
- 2026-10-30 f47203f0 Round 10 seams: row 15, the stall's stock (C3); log the reviews and rulings during the owner's game
- 2026-10-30 ab3b90c6 Round 10 D9a: quest chains for Mother Moll and Ada Kerrow
- 2026-10-30 b792a727 Round 10 seams: row 16, Talk (D9c); log D7's review and the D9 split
- 2026-10-30 44fa10c5 Round 10 D9a: format
- 2026-10-30 48a6b860 10Y y1: refusal lines on a phone, the greyed prompt and the second-refusal hint
- 2026-10-30 d9ecc8a0 x2: chop and smash sound at the tool walls (A253)
- 2026-10-30 b448fcf4 Round 11: the owner's questionnaire answers (21 defaults; CL3 brings the long shadows in); 11A writes the plan
- 2026-10-30 68483714 docs(round11): 11B budget for the long-shadow layer (CL3): one shared mask at half density
- 2026-10-30 87d99037 docs(round11): cite the owner's answers on PR #366
- 2026-10-30 1524b09b C3a: what breaks when I'm gone (townWork, stall stock, the chapel altar)
- 2026-10-30 9f6f46dc docs(round11): 5.3's pass-list paragraph names the CL3 shadow layer and its worst case
- 2026-10-30 38d044d7 C3b: the shop panel shows a stall's stock (n left today, sold out)
- 2026-10-30 d193d548 docs(round11): rewrap 5.3's paragraph
- 2026-10-30 1bff609f x4: the Logs tooltip names the saws (A293)
- 2026-10-30 48283040 C3a: the dear-stall test keeps its owner look's wearer alive (its stall at work)
- 2026-10-30 1d1a0b85 x3: talk.test.ts reads the call count before the answer (A273)
- 2026-10-30 71ce03f6 docs(round11): 5.3.1 on 11A's measurement (94% trimmed), hard 8-bit mask, soft low-poly mask, HD by fallback
- 2026-10-30 eaaf3caf Round 10 D9a: chains wording, round 11 branches
- 2026-10-30 36ef2712 C3a: economyShops reads the bakery's left (6Z's grant, one field)
- 2026-10-30 93a08eb6 Round 11: the build plan (11A), with the long-shadow measurement for CL3
- 2026-10-30 b68a9aa4 Merge pull request #363: Round 10 D6a, armour with properties [merge]
- 2026-10-30 d149cf9f Merge pull request #367: Round 10 D6b, the skinning knife, hide and game [merge]
- 2026-10-30 15d0867b Round 10 D7: merge base, whole goods note in GDD 3.23 [merge]
- 2026-10-30 7c11199d round11-plan.md: 11B's answers (shd_ budget per look.md 5.3.1, section 5's order and models, the gate's shadow crop)
- 2026-10-30 fdbcf290 10Y y2: a log line per noise kind, and never the door's for an unknown kind
- 2026-10-30 c2e0582f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c2b-errand [merge]
- 2026-10-30 1c094134 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3-petition [merge]
- 2026-10-30 9f98b809 Merge pull request #366: Rounds 10 and 11 docs: 10X and 10Y early start, seams rows 15 and 16, the B5 ruling, the round-11 answers [merge]
- 2026-10-30 b5a995be Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x4-logs-tooltip [merge]
- 2026-10-30 cc09ecf1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x2-chop-smash-noise [merge]
- 2026-10-30 fc7929de Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x3-talk-flake [merge]
- 2026-10-30 64c5252b x5: the grindstone restores a worn tool (A313)
- 2026-10-30 6105dcc7 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y1-refusal-lines [merge]
- 2026-10-30 56bca4d2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y2-noise-lines [merge]
- 2026-10-30 9cad8475 Round 10 D9c: talk to a figure
- 2026-10-30 826e1a7c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x5-grindstone [merge]
- 2026-10-30 4bd0e7a7 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x3-talk-flake [merge]
- 2026-10-30 56d57616 Merge pull request #371: Round 11 (11B): budget for the long-shadow layer (CL3) [merge]
- 2026-10-30 e23ef571 Merge pull request #374: Round 11: the build plan (11A) [merge]
- 2026-10-30 c5f0127a Merge pull request #369: Round 10 D7: rent in kind and the boarded house [merge]
- 2026-10-30 079aaea6 Merge claude/r10-b3-petition (B3a's final head) into claude/r10-b4-manhunt [merge]
- 2026-10-30 11ee4e4b Round 10 D9a: merge base after D7 [merge]
- 2026-10-30 edeb858d Add back the avatar after a tagged view.remove so figures stop freezing on the client
- 2026-10-30 ceb69aa3 Merge pull request #364: B3a: petitions on the server (10B) [merge]
- 2026-10-30 4f88f15d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b4-manhunt [merge]
- 2026-10-30 397d95b7 Merge pull request #377: Round 10 x3: talk.test.ts reads the call count before the answer (10X) [merge]
- 2026-10-30 482a3c83 B4: a seat on a running manhunt is spared Exhaustion (SleepRest.ts, 6Z's grant)
- 2026-10-30 0a942e4e Merge pull request #368: C2b: Owing the line: the Clerk's errand, the dear stall, NPC parity, the two-day check [merge]
- 2026-10-30 03774ba0 Merge branch 'claude/r10-c3-townwork' into claude/r10-c3b-stockview [merge]
- 2026-10-30 dddee124 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c3-townwork [merge]
- 2026-10-30 0b4038a3 Merge pull request #373: Round 10 D9a: quest chains [merge]
- 2026-10-30 c9116853 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y2-noise-lines [merge]
- 2026-10-30 faba3b27 C3a: a look is gone only when the roster shows no wearer alive (6Z's review)
- 2026-10-30 f6c6f092 Merge branch 'claude/r10-c3-townwork' into claude/r10-c3b-stockview [merge]
- 2026-10-30 def8677e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c3-townwork [merge]
- 2026-10-30 4d05282d Merge branch 'claude/r10-c3-townwork' into claude/r10-c3b-stockview [merge]
- 2026-10-30 b3cc73c0 Round 10 y3: the round's new screens on a phone and a desktop (10Y)
- 2026-10-30 612ff188 Merge pull request #372: Round 10 y1: refusal lines on a phone, the greyed prompt and the second-refusal hint (10Y) [merge]
- 2026-10-30 0be178af Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y3-new-screens [merge]
- 2026-10-30 befc204d Round 10 D9c: pin the ledger in the tip test, merge base after D9a [merge]
- 2026-10-30 2420cecf Round 10 docs: row 15 reads the roster, row 17 (figures in views), 10R, the game report
- 2026-10-30 2b82306a Round 10 (10R): the role-card and Daybook mock
- 2026-10-30 0e6f6d8b Round 10 docs: seams row 18 (Paint The Town Red) and the C5 rulings
- 2026-10-30 220e1e25 Round 10 (10R): the role cards design
- 2026-10-30 013e8606 Merge the base into 10R [merge]
- 2026-10-30 a023cb75 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x1-refusals [merge]
- 2026-10-30 e8903361 Round 10 (10R): the card in each mode, the keys that move, the mock rebuilt
- 2026-10-30 3bf863f3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x4-stuck-figures [merge]
- 2026-10-30 3a798305 Show living figures in the seats' views under the same dark rule as seats
- 2026-10-30 f3d51055 Merge branch 'claude/r10-x4-stuck-figures' into claude/r10-x5-figures-in-views [merge]
- 2026-10-30 2202c16c Round 11 plan approved (A236); Herb Bread until dawn; 10X's steps logged
- 2026-10-30 781725d4 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x2-chop-smash-noise [merge]
- 2026-10-30 5daffc02 Round 10 (10R): world mode is the card's default; the mock's Mode select
- 2026-10-30 cee875a7 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b4-manhunt [merge]
- 2026-10-30 181533e9 Merge pull request #382: Round 10 docs: seams rows 15, 17 and 18, 10R, the C5 rulings and the game report [merge]
- 2026-10-30 fb79ea39 Round 10 (10R): the Paint The Town Red target as a match token
- 2026-10-30 cc135c54 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 e7a8abcd Bandage knockback on a voided strike (x10, A393)
- 2026-10-30 f880d9c6 One patch per tick and a ten-tick input hold (x7, A373)
- 2026-10-30 c3cd9642 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 c0297746 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x7-patch-per-tick [merge]
- 2026-10-30 57708e47 C5a: Paint The Town Red, the mode (deal, returns, counts, win)
- 2026-10-30 135d0ffb Merge pull request #385: Round 11 plan approved (A236); Herb Bread until dawn; 10X's steps logged [merge]
- 2026-10-30 bd20368d Merge pull request #376: Round 10 y2: a log line per noise kind, never the door's for an unknown kind (10Y) [merge]
- 2026-10-30 1c46ffd7 Merge pull request #383: Round 10 (10R): the role cards design and the Daybook [merge]
- 2026-10-30 794ae4fc Merge pull request #378: C3a: what breaks when I'm gone (10C) [merge]
- 2026-10-30 8eed1240 Merge pull request #379: C3b: the shop panel shows a stall's stock (10C) [merge]
- 2026-10-30 089afd8e Round 10 (10R): the ability census and the unbuilt abilities
- 2026-10-30 ca5235c1 The Herb Bread's Resistant lasts until the dawn (x11, A413)
- 2026-10-30 c9f53947 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 117a3556 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x7-patch-per-tick [merge]
- 2026-10-30 8b4d228f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 29d02f0f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 39769a1e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 c0c26a04 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 9b45a078 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x4-stuck-figures [merge]
- 2026-10-30 7c728bdd Round 10 (10R): label 11.2 Q-A4; dedupe the mock's chore scenes
- 2026-10-30 29cdfdfa Merge branch 'claude/r10-x4-stuck-figures' into claude/r10-x5-figures-in-views [merge]
- 2026-10-30 c2ca62d7 x5: the figures-in-view tests use the granted seatAvatarsHeld helper
- 2026-10-30 e0392473 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y4-tick-stamps [merge]
- 2026-10-30 bbd082d8 Round 10 y4: interpolation samples stamped by the server tick (10Y)
- 2026-10-30 14564283 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y3-new-screens [merge]
- 2026-10-30 05c20b93 x10: every voided strike parts the pair, and GDD 3.2's cooldown cells catch up (A393)
- 2026-10-30 debfab93 C5a: A310 logs the swap order as a review change; the leak keys say why
- 2026-10-30 d5a6a9f3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c5a-painttown [merge]
- 2026-10-30 07cdda37 x12: the studio draft route's rate-limit test gets the 30 s budget its peers use
- 2026-10-30 b4ae34a9 Merge pull request #381: B4: the manhunt (10B) [merge]
- 2026-10-30 6625eb80 Merge pull request #387: Round 10 (10R): the ability census and the unbuilt abilities [merge]
- 2026-10-30 e4ab96d4 B3c: the Constables file their own petition on briefings that fit one figure (Paint The Town Red; A329)
- 2026-10-30 cbc22fb5 Round 10 y5: the Studio NPC editor's save verified end to end (10Y)
- 2026-10-30 f7c332f2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y5-studio-npc-save [merge]
- 2026-10-30 35330551 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y3-new-screens [merge]
- 2026-10-30 08a5b904 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y4-tick-stamps [merge]
- 2026-10-30 ddc5df60 x13: NPC night baking, the R6 audit's first cut (A433, proposed)
- 2026-10-30 8b9fb135 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x7-patch-per-tick [merge]
- 2026-10-30 14d1bce8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x5-figures-in-views [merge]
- 2026-10-30 04e1d7ab Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x4-stuck-figures [merge]
- 2026-10-30 1e30fc1c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 fabed294 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-10-30 bb55ead7 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 e00b9844 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 ae3bd9af Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 55530e14 x8: A293 in number order
- 2026-10-30 59b918f8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x1-refusals [merge]
- 2026-10-30 f3ffba9e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3c-constable-petitions [merge]
- 2026-10-30 a39f9465 Round 10 y6: one disc per ability on a phone (10Y, A334)
- 2026-10-30 9ff8c45c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c5a-painttown [merge]
- 2026-10-30 4448fbce Round 10 y7: the vendetta on the role card (10Y, A354)
- 2026-10-30 11467492 C5b: Paint The Town Red's screens (the card's goal, the end tally)
- 2026-10-30 fd557c6d client: the Craft panel points the hand recipes to the crafting square (A374)
- 2026-10-30 825a843d docs: the ability discs go under UI.md 14.51 as 14.51.1 (6Z, seams.md 5)
- 2026-10-30 e65b4fbf docs: the vendetta on the card goes under UI.md 14.51 as 14.51.2 (6Z, seams.md 5)
- 2026-10-30 446af1e9 docs: the hand recipes go under UI.md 14.51 as 14.51.3 (6Z, seams.md 5)
- 2026-10-30 1a4a4e2c Merge pull request #388: Round 10 y4: samples stamped by the server tick (10Y) [merge]
- 2026-10-30 332f05bc Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y5-studio-npc-save [merge]
- 2026-10-30 dee187be Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y3-new-screens [merge]
- 2026-10-30 cb8547de Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y6-phone-discs [merge]
- 2026-10-30 58bd4745 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y7-vendetta-goal [merge]
- 2026-10-30 0b2c5d0a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y8-hand-craft [merge]
- 2026-10-30 f9185bea C5a: the Vicar is always dealt in Paint The Town Red (6Z's ruling)
- 2026-10-30 e0bc84b6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x2-chop-smash-noise [merge]
- 2026-10-30 2b7bae4f Round 10 docs: the morning's merges and rulings, the C5a review, the C5b grant
- 2026-10-30 73c857b9 C5a: format the Paint deal test
- 2026-10-30 9890011b Merge branch 'claude/r10-c5a-painttown' into claude/r10-c5b-paintview [merge]
- 2026-10-30 8b6a240d Round 10 docs: seams row 19, the county jail (B5), and the x14 invariant
- 2026-10-30 49241a1c x13: the bake test's day case, a baker works the same stations by day
- 2026-10-30 f76c6b12 Merge pull request #386 from groot99-droid/claude/r10-y3-new-screens [merge]
- 2026-10-30 d81ca1e1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y5-studio-npc-save [merge]
- 2026-10-30 fac90a3e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y7-vendetta-goal [merge]
- 2026-10-30 e496cf40 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y8-hand-craft [merge]
- 2026-10-30 f879d8c6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y6-phone-discs [merge]
- 2026-10-30 e8f39739 B5a: the county jail's cell, a jail scene outside every map's graph (A369)
- 2026-10-30 133f3912 B5a: WORLD 4.3 says the cell borrows the default map's look on every map
- 2026-10-30 30cf9b4e Merge pull request #391 from groot99-droid/claude/r10-c5a-painttown [merge]
- 2026-10-30 560c85fa Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c5b-paintview [merge]
- 2026-10-30 2b34d674 C5b: paintTarget sits above the locked purse section comment (6Z's note)
- 2026-10-30 2e91090b Merge pull request #395 from groot99-droid/claude/laughing-planck-vt4dcs [merge]
- 2026-10-30 b3b66616 Round 10 log: the B5 split and its grants; y3, C5a and the docs merged
- 2026-10-30 57fd7c1a x14: the decoded-view invariant behind pnpm auto -- --views (A453)
- 2026-10-30 1c7d7581 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x4-stuck-figures [merge]
- 2026-10-30 9d14581e B5a: the grid exporter's map test leaves the jail scene out
- 2026-10-30 33029cbf Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3c-constable-petitions [merge]
- 2026-10-30 c9e5823b Merge pull request #389 from groot99-droid/claude/r10-y5-studio-npc-save [merge]
- 2026-10-30 5b3cb595 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y6-phone-discs [merge]
- 2026-10-30 9fc7e203 B3c: the Constables file only in Paint The Town Red, through C5a's isPaintTown; a real Paint match files
- 2026-10-30 bdf64e58 seams.md 1: a Complete may stand on an older base; 6Z reruns on the true merge
- 2026-10-30 813bb0bd Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y7-vendetta-goal [merge]
- 2026-10-30 cbdded1e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y8-hand-craft [merge]
- 2026-10-30 7a436234 B3c: prettier
- 2026-10-30 b581f714 Merge pull request #393 from groot99-droid/claude/r10-c5b-paintview [merge]
- 2026-10-30 fbdd613b Merge pull request #396 from groot99-droid/claude/laughing-planck-vt4dcs [merge]
- 2026-10-30 bbdce354 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y7-vendetta-goal [merge]
- 2026-10-30 b808c391 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y8-hand-craft [merge]
- 2026-10-30 6ce6f1c7 C5c: the Knife on the guards; Paint mode returns them on the morning train
- 2026-10-30 e5f140ef Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b5a-cell [merge]
- 2026-10-30 ec160a47 C5c: record the guard's no-clue, no-protection default and 6Z's conditions
- 2026-10-30 4754f403 Merge pull request #384 from groot99-droid/claude/r10-x4-stuck-figures [merge]
- 2026-10-30 7e462970 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y6-phone-discs [merge]
- 2026-10-30 2642a8b8 x5: the seen helpers of visibility and sim-portal count seat avatars only
- 2026-10-30 38a0032e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x5-figures-in-views [merge]
- 2026-10-30 18228e99 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x14-decoded-views [merge]
- 2026-10-30 0be3b9ce Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y8-hand-craft [merge]
- 2026-10-30 d6afdfda Merge pull request #390 from groot99-droid/claude/r10-y6-phone-discs [merge]
- 2026-10-30 6989f548 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b5a-cell [merge]
- 2026-10-30 bd7b92d7 Round 10 docs: seams row 20 (the Hitman's arrival); x4, y6, C5c and C4 rulings
- 2026-10-30 6263fcd7 x14: register the decoded-view check when the shadows attach, not on import
- 2026-10-30 9a24ce99 B5b: the county jail holds the cuffed seat until the morning train, its face pinned (A349)
- 2026-10-30 cc33e16a x5: assert a figure's row carries no near or ghost tag in a seat's view
- 2026-10-30 4a2c0422 B5b: lint
- 2026-10-30 acfe311f Round 10 docs: B5b's two calls in seams row 19; the x5, B5 and C4a test grants
- 2026-10-30 f8708476 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b3c-constable-petitions [merge]
- 2026-10-30 4be0413b B5b: a jailed seat's Knife is refused IN_JAIL; a death mid-walk frees the ghost; the manhunt test's hold is the jail; the pin tests
- 2026-10-30 0c962e17 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y7-vendetta-goal [merge]
- 2026-10-30 b75fa292 x5: a figure's row never takes the near tag
- 2026-10-30 f0aa889c x5: the granted kill and nightSight test helpers (6Z, 2026-10-30)
- 2026-10-30 fe4e930d C4a: the Hitman's arrival (draw, turning, sign, dormant stall)
- 2026-10-30 eff74dd5 C4a: tighten the arrival tests
- 2026-10-30 2cf09f77 Round 10 y9: the phone's top rows, the band's floor and the out slot
- 2026-10-30 65b06cdb Merge pull request #394 from groot99-droid/claude/r10-b3c-constable-petitions [merge]
- 2026-10-30 a654a312 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b5b-jail [merge]
- 2026-10-30 90baed57 C4a: move the dormant stall to C4c; fallback, map and systemLine (6Z review)
- 2026-10-30 2875271d Round 10 docs: seams row 21 (C4b), row 20 amended; log B3c, C4a's review, C4b's rulings
- 2026-10-30 6df8fdbf Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x1-refusals [merge]
- 2026-10-30 cbbbdc18 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x2-chop-smash-noise [merge]
- 2026-10-30 7383dcf9 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 e33d95bc Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 4d17b686 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x13-npc-night-bake [merge]
- 2026-10-30 fb6c5149 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-10-30 ec937e74 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 0288790b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 0d0a3c51 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b5a-cell [merge]
- 2026-10-30 52646c7a test(server): give the studio draft-limit test a 20 s timeout (6Z's grant)
- 2026-10-30 c16ac90d Merge pull request #392 from groot99-droid/claude/r10-y7-vendetta-goal [merge]
- 2026-10-30 a949d963 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b5a-cell [merge]
- 2026-10-30 10789c2c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x5-figures-in-views [merge]
- 2026-10-30 919c8d9f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x2-chop-smash-noise [merge]
- 2026-10-30 3ab6179f x5: the P15 night-power diff ignores the figures' rows too
- 2026-10-30 8ba7e3c5 x7: ARCHITECTURE.md's quiet-input sentence says ten ticks
- 2026-10-30 9f4a8e21 Merge branch 'claude/r10-b5a-cell' into claude/r10-b5b-jail [merge]
- 2026-10-30 a183c22c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y8-hand-craft [merge]
- 2026-10-30 c2b7441b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y9-phone-band [merge]
- 2026-10-30 e17d9478 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y10-copy-drift [merge]
- 2026-10-30 2875718d Round 10 y10: UI.md 14 against the copy modules
- 2026-10-30 f19544ff Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c4a-arrival [merge]
- 2026-10-30 d12cc0ee Round 10 y10: the deck test leaves the sibling tests out of its glob
- 2026-10-30 a2d2251e C4a: merge the base; the turned card reads as the holder (y7's vendetta lines)
- 2026-10-30 6101bf06 Round 10 docs: rows 19 and 21 amended (jail at meetings and on BlackPine, the departed vote); log y7, B5a's timeout, x5's grant, the B5b review
- 2026-10-30 c68e0384 B5b: a meeting keeps the prisoner in the cell; no-station maps release at dawn (6Z's review)
- 2026-10-30 0317e912 C4b: the Derringer, the Dusk Train and the Contract victory (WIP)
- 2026-10-30 709720b2 Merge C4a into C4b (stacked) [merge]
- 2026-10-30 96865634 C4b: the target test reads the drawn face (Avatar.lookOf is a seat); wait on the bus steps
- 2026-10-30 67ddf540 Merge pull request #403 from groot99-droid/claude/r10-x5-figures-in-views [merge]
- 2026-10-30 225fe5d6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x2-chop-smash-noise [merge]
- 2026-10-30 dc91b4f3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 53ab42f5 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 4233f2c3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x13-npc-night-bake [merge]
- 2026-10-30 9f08f1f0 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-10-30 3bfe0f70 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 b394f086 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 dda46e68 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-d9c-talk [merge]
- 2026-10-30 b771467e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x1-refusals [merge]
- 2026-10-30 b3c4dcfe Round 10 D9c: merge base after x5, ask a Constable by a handle read off the seat's view
- 2026-10-30 c1d9b109 x15: rent.test.ts waits on the shift's bookkeeping, not the wall clock
- 2026-10-30 404b686d Round 10 D9c: type the briefing the test posts
- 2026-10-30 5b4f9bee x15: rentInKind.test.ts waits on the shift's bookkeeping too
- 2026-10-30 ec56b501 C4b: format the protocol and regenerate PROTOCOL.md
- 2026-10-30 d3f86374 Round 10 y11: the imported look's toon group is remapped onto the rig's
- 2026-10-30 53a46425 C4b: never turn a seat with no room for the Derringer (6Z review)
- 2026-10-30 f39002ea Round 10 y12: a figure's nameplate is keyed by the look on the wire
- 2026-10-30 6aad1f57 Merge pull request #399 from groot99-droid/claude/r10-b5a-cell [merge]
- 2026-10-30 0ba7fb03 Merge pull request #405 from groot99-droid/claude/r10-b5b-jail [merge]
- 2026-10-30 644dfeb7 Merge pull request #404 from groot99-droid/claude/r10-x7-patch-per-tick [merge]
- 2026-10-30 7cd8cd1a Merge pull request #370 from groot99-droid/claude/r10-x1-refusals [merge]
- 2026-10-30 951f031e x15: settled() waits for the tick after the bookkeeping
- 2026-10-30 640575df Round 10 docs: log x5, B5a, B5b, x7 and x1; the B5c grant, the C4b review, the C4c hardship rulings; row 21's lookOf
- 2026-10-30 59937d60 B5c: the rumour ledger never samples the county jail's cell (6Z's grant)
- 2026-10-30 927b65d1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 b2e24579 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 a1857dcb Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 05079bdb Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-10-30 5c6ab5a8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x13-npc-night-bake [merge]
- 2026-10-30 4ffa25ce Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 289c65f3 C4b: the ejection test calls the meeting from a living seat and never shoots the only Killer
- 2026-10-30 f511ffa8 C4c: the dormant role and the hardships (one thin, dear sign)
- 2026-10-30 7a620559 D8: the county jail's mini-games (gym, yard fight, scrubbing)
- 2026-10-30 690ee326 D8: scrubbing pays a wage only; one Strength; slingshot adds it too
- 2026-10-30 3d6ca1b0 Round 10 docs: seams row 22 (B6a, the Tribunal); rows 15 and 19 name it; log the sign-off
- 2026-10-30 65d78204 Round 10 docs: row 22's fines come from the charge alone in B6a; B6b's goods-priced theft fine comes to 6Z first
- 2026-10-30 89c98216 C4b: the Derringer's id is a literal in dayWeapon.ts (no import cycle reads it early)
- 2026-10-30 18b1088d Merge branch 'claude/r10-c4b-dusktrain' into claude/r10-c4c-hardships [merge]
- 2026-10-30 abcaf7a8 C4b: pin the Derringer's literal id to a real role-bound items.json row
- 2026-10-30 8bfce2ff Merge branch 'claude/r10-c4b-dusktrain' into claude/r10-c4c-hardships [merge]
- 2026-10-30 ad8d2e2e C4c: a fixed number of hardship draws per delivery; R17 lists the hardship stream (6Z grant)
- 2026-10-30 a5862a86 C4c: A390 records the fixed draws and the R17 grant
- 2026-10-30 bdd3573a Merge the base into C5c (x1 #370 and B5b landed): the jail check runs before the Knife on a guard [merge]
- 2026-10-30 69c90370 test(server): act() waits for the room's tick, not the wall clock (x16)
- 2026-10-30 bc65d79f Merge pull request #380 from groot99-droid/claude/r10-d9c-talk [merge]
- 2026-10-30 010bf75f Merge pull request #375 from groot99-droid/claude/r10-x2-chop-smash-noise [merge]
- 2026-10-30 66ea62b8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x15-rent-flake [merge]
- 2026-10-30 1ddba160 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x16-act-tick-wait [merge]
- 2026-10-30 dbe02307 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-10-30 363380a5 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 408461e2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 c6c51271 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x13-npc-night-bake [merge]
- 2026-10-30 34139453 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 18f20e1a Round 10 docs: log the D9c and x2 merges, B5c's standing Complete and the D8 review
- 2026-10-30 00c62bd5 D8: review fixes (inspect whole, unanswered yard board, refusal and hint wording)
- 2026-10-30 fd58aa81 Merge the base into C4b (D9c, x2, x1, B5b): the jail bars the turning and the Derringer [merge]
- 2026-10-30 56028874 Merge the base (D9c, x2) into D8 [merge]
- 2026-10-30 e19b90a6 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 c2643fd8 B6a: the Tribunal, the verdict and the death, jail and fine sentences
- 2026-10-30 d0c4e3e9 Round 10 y13: On the line names the place, shows the book and counts to the bells (10Y)
- 2026-10-30 f01e0f69 B6a: regenerate docs/PROTOCOL.md for tribunalVerdict
- 2026-10-30 50904875 Round 10 y8: merge base 010bf75, craft.square row gives the line alone [merge]
- 2026-10-30 ac273ce2 Round 10 y9: merge y8 (base 010bf75, hand recipes to the square) [merge]
- 2026-10-30 5885ae5f Round 10 y10: merge y9 (base 010bf75) [merge]
- 2026-10-30 22d40d15 Round 10 y11: merge y10 (base 010bf75) [merge]
- 2026-10-30 2b2de2dc Round 10 y12: merge y11 (base 010bf75) [merge]
- 2026-10-30 007eb951 Round 10 y13: merge y12 (base 010bf75) [merge]
- 2026-10-30 89af8f17 x8: the fix's label follows 6Z's numbering (x4 became x8)
- 2026-10-30 f12061a9 x9: the fix's label follows 6Z's numbering (x5 became x9)
- 2026-10-30 eeb50eb3 Merge pull request #411 from groot99-droid/claude/r10-b5c-cell-rumours [merge]
- 2026-10-30 62548d77 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b6a-tribunal [merge]
- 2026-10-30 3dff8842 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y14-stale-e2e [merge]
- 2026-10-30 a216b35d Merge remote-tracking branch 'origin/claude/r10-y13-line-extras' into claude/r10-y14-stale-e2e [merge]
- 2026-10-30 1baec576 C5c: the paint win check after a guard's death runs in the step; no import cycle through Win
- 2026-10-30 fc0af366 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c5c-knifeguards [merge]
- 2026-10-30 0846ec72 B6a: the held seats' release ticks follow the Tribunal's pause (6Z's condition)
- 2026-10-30 3ba16dc4 Round 10 y14: the stale e2e specs, attributed and fixed (10Y, A494)
- 2026-10-30 89a94d29 B6a: jail and manhunt tests finish the Tribunal the cell opens (6Z's grant)
- 2026-10-30 98f34881 Merge pull request #413 from groot99-droid/claude/r10-x10-bandage-knockback [merge]
- 2026-10-30 7f4aa7e2 Merge pull request #410 from groot99-droid/claude/r10-d8-jail-games [merge]
- 2026-10-30 6c9bb79c Merge pull request #414 from groot99-droid/claude/r10-x15-rent-flake [merge]
- 2026-10-30 d722a951 B6a: manhunt test puts the opener back at the board after the Tribunal's gathering (6Z's grant)
- 2026-10-30 3f889c55 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b6a-tribunal [merge]
- 2026-10-30 1bfdca6f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 cef0c31d Merge the base into C4b (D8, x10, x15 landed): both sides' balance keys kept [merge]
- 2026-10-30 38a0f530 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 d09b50d8 Merge the base at 6c9bb79 (x10, D8, x15) into the 800k tier branch before spawning 10S [merge]
- 2026-10-30 699a4747 Round 10 (10R): the owner's answers to the role cards design
- 2026-10-30 bc38a865 x9: the grindstone test steps until the hold is taken and ends it on its tick
- 2026-10-30 50b7d5a2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x13-npc-night-bake [merge]
- 2026-10-30 06d48659 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y8-hand-craft [merge]
- 2026-10-30 97a39c8a Merge branch 'claude/r10-y8-hand-craft' into claude/r10-y9-phone-band [merge]
- 2026-10-30 db07efaf Merge branch 'claude/r10-y9-phone-band' into claude/r10-y10-copy-drift [merge]
- 2026-10-30 3f8a9f8b Merge branch 'claude/r10-y10-copy-drift' into claude/r10-y11-toon-remap [merge]
- 2026-10-30 873c226a Merge branch 'claude/r10-y11-toon-remap' into claude/r10-y12-figure-names [merge]
- 2026-10-30 b0949a28 Merge branch 'claude/r10-y12-figure-names' into claude/r10-y13-line-extras [merge]
- 2026-10-30 d675dbfa Merge branch 'claude/r10-y13-line-extras' into claude/r10-y14-stale-e2e [merge]
- 2026-10-30 b856ac9a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x13-npc-night-bake [merge]
- 2026-10-30 030ecaa1 Merge the base (6c9bb79) into the round 10 docs branch [merge]
- 2026-10-30 7a4f42cb Round 10 docs: every gameplay feature in round 10 (A256), sessions 10S and 10V, and the merge log
- 2026-10-30 9d07f41a Round 10, R1: the action table
- 2026-10-30 dac4b658 Round 10 (10S): the scope census, docs/round10/scope.md
- 2026-10-30 3ab8b2dc V1a: the Lens Inspect and Plant Clue (10V, A239)
- 2026-10-30 9dfb8a0c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c5c-knifeguards [merge]
- 2026-10-30 1629cb1f Round 10 docs: seams rows 23 and 24 (10V's evidence verbs) and wave 1 of the scope census
- 2026-10-30 d0cc4c1e 10S scope: the world-mode deal written out (today and what changes, row 25); rows after 10V's 23 and 24; readings as NoteKinds; the grindstone left S3
- 2026-10-30 26ee5650 V1a: 6Z's row 23 changes (thread beside a portal, Lens once a day, status only)
- 2026-10-30 97003a72 Merge pull request #398 from groot99-droid/claude/r10-y8-hand-craft [merge]
- 2026-10-30 fa719b89 Merge pull request #402 from groot99-droid/claude/r10-y9-phone-band [merge]
- 2026-10-30 4ce9e72b Merge pull request #406 from groot99-droid/claude/r10-y10-copy-drift [merge]
- 2026-10-30 7f444c9e Merge pull request #407 from groot99-droid/claude/r10-y11-toon-remap [merge]
- 2026-10-30 d6929534 Merge pull request #409 from groot99-droid/claude/r10-y12-figure-names [merge]
- 2026-10-30 f9d36dd0 Merge pull request #412 from groot99-droid/claude/r10-y13-line-extras [merge]
- 2026-10-30 e2b95036 S4: the mugging's Flee and Fight
- 2026-10-30 312dc120 Merge the base (10Y's six) into the round-10 docs [merge]
- 2026-10-30 78f3dc0e Round 10 docs: 10Y's six merged, the UI.md 14 guard in seams 1, R1's grants
- 2026-10-30 e30cb4bc Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-r1-actions [merge]
- 2026-10-30 a3a2188e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b6a-tribunal [merge]
- 2026-10-30 e9aaca3e Berries, game and stew: the berries node, the stew recipe and its eatStew verb (S2)
- 2026-10-30 38643267 Merge pull request #416 from groot99-droid/claude/r10-r2-answers [merge]
- 2026-10-30 7df955a2 B6a: shared tribunalHelpers for the tests that jail a seat; D8's jailGames setup meets the Tribunal (6Z's grant)
- 2026-10-30 c8657a5f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b6a-tribunal [merge]
- 2026-10-30 5e6856cb S1a: containers and loot tables in the logic table (content)
- 2026-10-30 eee0da0c Round 10, R2: the dossier paper and its three faces
- 2026-10-30 d7ed05c5 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-r2-paper [merge]
- 2026-10-30 56a1dee0 Round 10 y15: the whole Playwright suite in CI on every client pull request (10Y, A514)
- 2026-10-30 21cbba9e Merge the base f9d36dd (10Y's six) into claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 0a47d9b7 Merge the base into S4 [merge]
- 2026-10-30 822f7e83 10S scope: 6Z's six secrecy fixes (hidden seats and names, every worn card withdrawn, disjoint cover lists, NPC ghosts in seances and wisps, the spectator's live and delayed parts); W1 split into W1a and W1b
- 2026-10-30 40b658de Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 231bd89a Round 10 docs: wave 2 of the scope plan and the review of #420 (A276)
- 2026-10-30 c27cf468 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c4b-dusktrain [merge]
- 2026-10-30 b4369eb6 x17: the Constables' briefing test keeps the NPC seats off its clues
- 2026-10-30 2dc9e83f Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-10-30 df3ea562 Round 10 docs: seams 6, nothing a seat does marks it human
- 2026-10-30 c74fd44b Merge C4b's final head into C4c (the base through 3864326) [merge]
- 2026-10-30 86f3dc67 Round 10 docs: seams rows 25 to 34 from 10S's plan (#420)
- 2026-10-30 8909da4d Round 10 docs: W1 is W1a (hidden seats) and W1b (the deal) in the wave-2 briefs
- 2026-10-30 fc767ac3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-v1-evidence [merge]
- 2026-10-30 22014778 S4: an NPC seat target draws pay, flee or fight on its own stream (GDD 3.24)
- 2026-10-30 2dce7d3e Merge pull request #420 from groot99-droid/claude/r10-s1-scope [merge]
- 2026-10-30 931676f6 Merge the base (#420, scope.md) into the round 10 docs; scope.md 4 names who builds each step [merge]
- 2026-10-30 f4faf23e V1a: Plant Clue's cast runs as a hold (no transit bit), and the test of what the figure shows
- 2026-10-30 7d73e5e8 x9 review: the grindstone is an NPC chore station
- 2026-10-30 0dc62cf2 V1a: UI.md 14.54 as a proposed list for 10Y (the deck test reads only keys the client holds)
- 2026-10-30 71128ae9 Round 10 S5: the art style in the menu only
- 2026-10-30 1dc825b9 Merge pull request #415 from groot99-droid/claude/r10-x8-logs-tooltip [merge]
- 2026-10-30 cd82ea27 Merge pull request #417 from groot99-droid/claude/r10-y14-stale-e2e [merge]
- 2026-10-30 cdef1136 Merge pull request #418 from groot99-droid/claude/r10-x11-herb-bread-dawn [merge]
- 2026-10-30 0c2aaf0f S1a: containers stay open in the depletion test (6Z's grant)
- 2026-10-30 b41ad44d Merge pull request #424 from groot99-droid/claude/r10-y15-e2e-ci [merge]
- 2026-10-30 7d7f4162 Merge base [merge]
- 2026-10-30 b449951c Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x17-constable-file-npc [merge]
- 2026-10-30 c8521e21 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-10-30 9a4ee852 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x9-grindstone [merge]
- 2026-10-30 23cf829d Merge pull request #400 from groot99-droid/claude/laughing-planck-vt4dcs [merge]
- 2026-10-30 1ddab4a6 Merge the base at 23cf829 (#400, the wave-2 briefs and seams rows 25 to 34) into the 800k tier branch before spawning 10N [merge]
- 2026-10-30 2c105b85 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x13-npc-night-bake [merge]
- 2026-10-30 fea6340d B6d: the Final Night's end trial replaces the forced vote
- 2026-10-30 c3bd71b3 The forge chain: tin ingot, iron tools, fine pick, tin armour and the first tier-2 wall (S3)
- 2026-10-30 be52e149 Regenerate the smithy and woods tilemaps for the station kinds (S3)
- 2026-10-30 c237b41a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-s1-containers [merge]
- 2026-10-30 10f2680e Round 10 K6a: snares on the server (10N)
- 2026-10-30 b3551379 Round 10 (6Z): seams rows 35 and 36, the snare and departure amendments, A296, the log
- 2026-10-30 798d0038 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-v1-evidence [merge]
- 2026-10-30 772b5e28 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-r2-paper [merge]
- 2026-10-30 303644b6 T6a: the fisher cottage, the sea door's cave and the south-east light (A242)
- 2026-10-30 9ad0f589 S4: an NPC seat's mugging answer lands at a drawn tick, or stays silent
- 2026-10-30 c95f07d8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-s4-mugging [merge]
- 2026-10-30 035ff6ff T6b: the mood hooks' station narrowing and its balance block, not yet wired (A242)
- 2026-10-30 346a6afa M1a: barks, the server side (chat.quick, S2C.bark, NPC and figure barks)
- 2026-10-30 ae8fca12 Revert "T6b: the mood hooks' station narrowing and its balance block, not yet wired (A242)"
- 2026-10-30 b2e9eb67 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x14-decoded-views [merge]
- 2026-10-30 1eab7bee Round 10 (6Z): seams row 37 (the Clerk's ledger), row 30's Hitman props, A296 (6) to (8), the log
- 2026-10-30 4f7aafe6 T6b: the mood hooks, wired into the seats' and villagers' station choice (A262)
- 2026-10-30 daffd2e8 B6d: the end trial in flow, trial and invariants tests (6Z's grant); the harness and admin feed hear endTrial kinds
- 2026-10-30 b92973fe Round 10 K3: candles for all, Handcuffs, the NPC seats' light rule (10K, A241)
- 2026-10-30 3f34b5cb C4d: the Clerk's rent ledger (looks only), and NPC seats read it too
- 2026-10-30 e2f1a4f1 T6a: Hollowmere's expected scene list gains the two new scenes (6Z's grant)
- 2026-10-30 6d7feb41 T6a: R17 allows the room's loot stream for an NPC seat's gather work (6Z's grant)
- 2026-10-30 f2eeb1a2 x14: keep the shadows' full-frame buffer whole; plant the stale tick
- 2026-10-30 703cbfeb Round 10 y16: the stale e2e gates go, match and npc specs fixed, apps/server in the e2e job's paths (10Y, A554)
- 2026-10-30 e7cf026e ci: give the server job 25 minutes
- 2026-10-30 8fc6fd23 WIP Round 10 K6b: Rope and NPC seats with snares (10N; held for part 2, tests not yet run)
- 2026-10-30 91a54863 M1a: R17 lists the barks stream (6Z's grant)
- 2026-10-30 dacc288d Merge base [merge]
- 2026-10-30 e9265a2a Merge pull request #408 from groot99-droid/claude/r10-c4b-dusktrain [merge]
- 2026-10-30 a4917308 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c4c-hardships [merge]
- 2026-10-30 851dd58b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c5c-knifeguards [merge]
- 2026-10-30 8a56faac x18: herbBreadDawn.test.ts gets the day timeout
- 2026-10-30 856d1a07 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into b6a-merge [merge]
- 2026-10-30 376b573b x16: read the bot's tick through stateOf()
- 2026-10-30 4a72fcf7 W1a1: fresh seat ids at Start in a world match, the session-to-seat boundary, Private.seatId
- 2026-10-30 5671fae3 Merge pull request #427 from groot99-droid/claude/r10-b6a-tribunal [merge]
- 2026-10-30 6ac53f62 Merge pull request #419 from groot99-droid/claude/r10-r1-actions [merge]
- 2026-10-30 1a1e494a Merge pull request #423 from groot99-droid/claude/r10-r2-paper [merge]
- 2026-10-30 d6a9ade7 test(server): give actWait.test.ts the 20 s budget startMatch needs under load
- 2026-10-30 04d76d35 Merge pull request #439 from groot99-droid/claude/r10-y17-ci-timeout [merge]
- 2026-10-30 8b03b36a Merge pull request #446 from groot99-droid/claude/r10-x18-herb-bread-timeout [merge]
- 2026-10-30 633fa960 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-b6d-end-trial [merge]
- 2026-10-30 c4b8ac38 Merge commit '8b03b36a5765c436b730e34947d8d8e37ff9f72e' into claude/laughing-planck-vt4dcs [merge]
- 2026-10-30 6e4c7816 Round 10 (6Z): the stop: part2.md, the wave-2 briefs, 10A's plans, the stop log
- 2026-10-30 39c4323d K3: Handcuffs sold at the general stores (6Z's grant)
- 2026-10-30 54c3f168 Round 10 (6Z): the stop: handoffs from 10S, 10T, 10X and 10F, the rulings at the stop
- 2026-10-30 af67ec72 Round 10 (6Z): the stop: 10B's and 10K's handoffs, the K3 ruling; every session archived
- 2026-10-30 43f5e698 Merge pull request #433 from groot99-droid/claude/laughing-planck-vt4dcs [merge]

### 2026-11

- 2026-11-06 ac5879ea Story mode: the build contract for four parallel sessions
- 2026-11-06 e448a06f Story mode: session ids in status.md
- 2026-11-06 2f4e329b Story S4: the story test fixture, its self-test and the test plan
- 2026-11-06 0ff7b85c Story S4: replay, full-story, death, handover and leak suites (skipped until S1 and S2 land)
- 2026-11-06 6e04fa03 Story S4: the story bot and its tracker test
- 2026-11-06 c963cda7 Story mode (S1): the story schema, validator and chapter 1
- 2026-11-06 fede34c7 Merge pull request #449 from groot99-droid/claude/story-s4-fixture [merge]
- 2026-11-06 b49ac819 Merge integration branch [merge]
- 2026-11-06 774da6af Story S4: status line
- 2026-11-06 d8eaf6d0 Story mode (S1): chapters 2 and 3 and the readable script
- 2026-11-06 3c56601c Merge integration into story-s1-schema [merge]
- 2026-11-06 6e18b05a Merge chapters 2 and 3 and the script into the schema PR [merge]
- 2026-11-06 0438bee4 Story mode (S1): status line
- 2026-11-06 4b56d013 Story mode (S2): enableStory with one human seat, fixed seeds, chapter-one deal, card pause
- 2026-11-06 7702b625 Story mode: wire messages, chapter cards, goals strip, title-screen entry, mock path
- 2026-11-06 4fd564d3 Story mode (S2): register the story invariant before the vendettas' pinned tail
- 2026-11-06 4ac72b3d Merge pull request #451 from groot99-droid/claude/story-s4-suites [merge]
- 2026-11-06 8a29e512 Merge remote-tracking branch 'origin/claude/elegant-archimedes-ybxzlj' into claude/story-s3-protocol-cards [merge]
- 2026-11-06 9134e29c Story mode (S2): seat handover (switchRole), untested draft
- 2026-11-06 8c6cd952 Merge remote-tracking branch 'origin/claude/elegant-archimedes-ybxzlj' into claude/story-s2-enable-story [merge]
- 2026-11-06 9f782555 Merge integration into story-s1-schema [merge]
- 2026-11-06 8b292408 Merge pull request #450 from groot99-droid/claude/story-s1-schema [merge]
- 2026-11-06 ffbbcf78 Story mode (S1): status: schema and chapters merged
- 2026-11-06 b8f8c37b Merge remote-tracking branch 'origin/claude/elegant-archimedes-ybxzlj' into claude/story-s2-seat-handover [merge]
- 2026-11-06 8e95d6f3 Story S4: STORY_STREAMS equals AUTO_STREAMS (A401), seed-word coverage
- 2026-11-06 e92ee3d6 Merge integration branch into story-s3-protocol-cards [merge]
- 2026-11-06 44321497 Merge PR 452 branch [merge]
- 2026-11-06 a8cba436 Story mode (S2): the beat runner, seat handover on S1's schema, chapter flow
- 2026-11-06 19245b8f Merge pull request #452 from groot99-droid/claude/story-s2-enable-story [merge]
- 2026-11-06 e5ce691b Merge pull request #454 from groot99-droid/claude/story-s1-status [merge]
- 2026-11-06 b259d1cf Merge remote-tracking branch 'origin/claude/elegant-archimedes-ybxzlj' into claude/story-s4-streams [merge]
- 2026-11-06 b892118d Story S4: run the suites on S2's engine (replay and leak over the opening); gate chapter suites on the beat runner
- 2026-11-06 f07abef1 Merge integration branch [merge]
- 2026-11-06 a082f4d6 Merge pull request #453 from groot99-droid/claude/story-s3-protocol-cards [merge]
- 2026-11-06 fa301d9e Story mode (S2): story.enter and story.pickup events, status
- 2026-11-06 4a176a07 Story mode (S2): chapter events carry chapter and chapterId
- 2026-11-06 5453daf1 Merge integration branch [merge]
- 2026-11-06 8ff036ab Story S3: the title screen's Story reads story.json through @wdi/content
- 2026-11-06 7f57f748 Story mode (S2): story.start from the title screen, story.continue through runCommands
- 2026-11-06 92e09f3b Story mode (S2): GDD 3.34 beats and break, ARCHITECTURE story paragraph, DECISIONS A415-A417
- 2026-11-06 ac6b95a7 Merge pull request #455 from groot99-droid/claude/story-s4-streams [merge]
- 2026-11-06 10c29217 Merge remote-tracking branch 'origin/claude/story-s4-streams' into claude/story-s4-e2e [merge]
- 2026-11-06 a4748ed0 Story S4: live-server story e2e at 390x844 and 1280x720 (skips until story.start is wired)
- 2026-11-06 b81018bd Merge pull request #456 from groot99-droid/claude/story-s2-seat-handover [merge]
- 2026-11-06 76984893 Merge pull request #457 from groot99-droid/claude/story-s3-catalog [merge]
- 2026-11-06 b15d83d6 Story mode (S2): status after PR 456
- 2026-11-06 dc112dfd Merge remote-tracking branch 'origin/claude/elegant-archimedes-ybxzlj' into claude/story-s4-e2e [merge]
- 2026-11-06 c42ccba0 Story S4: fixture follows S2's enableStory (start queued), death asserts failed, self-test requires the engine
- 2026-11-06 cc1a1dfe Story S4: the live-server story e2e no longer skips (story.start is wired)
- 2026-11-06 3d5baa8d Story S3: live-server spec, goals strip placement and phone layout
- 2026-11-06 611e11e5 Story bot: ignore the world's other messages
- 2026-11-06 e1ff1c4d Story S2: types module and queueStoryStart for the S4 fixture; status line
- 2026-11-06 c9b22107 Merge integration branch [merge]
- 2026-11-06 8ceb2755 Merge pull request #460 from groot99-droid/claude/story-s2-seat-handover [merge]
- 2026-11-06 c77438dd Merge integration branch into story-s4-e2e; S4 status [merge]
- 2026-11-06 eb088c2e Story live e2e: continue closes the title card (a queued card may follow)
- 2026-11-06 64f82487 Merge pull request #458 from groot99-droid/claude/story-s4-e2e [merge]
- 2026-11-06 f01037d6 S4 status: full-story bot run finished all three chapters
- 2026-11-06 a60efd53 Merge pull request #461 from groot99-droid/claude/story-s4-bot-run [merge]
- 2026-11-06 b359852c S4 final handoff
- 2026-11-06 9fd35f3a Merge pull request #462 from groot99-droid/claude/story-s4-handoff [merge]
- 2026-11-06 20ffb761 Story mode: the Bandit is the outlaw; a Killer chapter (the Activist) added
- 2026-11-06 cf83b361 Story mode: a vendetta that changes hands takes its recorded steps with it
- 2026-11-06 9c9bcd74 Story mode: story.json in the canonical data layout
- 2026-11-06 bf71326b Story e2e: the live menu lists four chapters
- 2026-11-06 d94e67fe Story mode: four chapters (Baker, Watchman, Bandit, Activist) (#463) [merge]
- 2026-11-06 24c73ea6 Story mode: the owner's questionnaire
- 2026-11-06 d91f5df8 Story mode part 2: the owner's answers and the build plan
- 2026-11-06 d0a59498 Achievements (E1): achievements.json, schema, validator, GDD 3.28, A440-A443
- 2026-11-06 917c3ce1 docs(story): P0 arc for part 2, HollowMere in five chapters of sections
- 2026-11-06 e4f2bbb2 docs(story): P0 handoff in status.md
- 2026-11-06 6a7dfe2c Merge pull request #465 from groot99-droid/claude/story-p0-arc [merge]
- 2026-11-06 64285c45 Merge claude/story-part2 into story-p4-content [merge]
- 2026-11-06 5a51712e Achievements (E1): achievements.json, schema, validator, GDD 3.28, A440-A443 (#466)
- 2026-11-06 95c5c523 Achievements (E1) 2/3: server evaluator and the private achv message
- 2026-11-06 d6080140 Achievements (E1) 3/3: device record, toasts and the Trophies view
- 2026-11-06 76844497 story P1: story.json as chapters of sections, the say action, the arc validator
- 2026-11-06 5cbd3979 Achievements (E1) 2/3: server evaluator and the private achv message (#467)
- 2026-11-06 cd9fa0ca P4: status handoff
- 2026-11-06 627a171f Achievements (E1) 3/3: device record, toasts and the Trophies view (#469)
- 2026-11-06 3a4cd14a Merge remote-tracking branch 'origin/claude/story-part2' into claude/story-p1-schema [merge]
- 2026-11-07 6e432afe Story mode: the owner's arc review answers (A515), A431 duplicate renumbered to A516
- 2026-11-07 18dd7de1 Merge base into y16: keep both DECISIONS rows [merge]
- 2026-11-07 f92de618 Merge pull request #468 from groot99-droid/claude/story-p1-schema [merge]
- 2026-11-07 ccd59e0f Round 10 y16: the stale e2e gates go, match and npc specs fixed, apps/server in the e2e job's paths (10Y, A554) (#436)
- 2026-11-07 7c804a1d Merge branch 'claude/zen-turing-m1jnw0' into claude/r10-t6-places [merge]
- 2026-11-07 b7c2669a T6: new places (fisher cottage, sea door, south-east light) and mood-hook module (#434)
- 2026-11-07 c4601d94 Merge base into V1a: keep both DECISIONS rows and both UI.md 14.54 blocks [merge]
- 2026-11-07 8088bdde V1a: the Lens Inspect and Plant Clue (10V) (#421)
- 2026-11-07 a43e7a1e Merge base into B6d: keep trial.file and the story rate limits [merge]
- 2026-11-07 2f70cb5b Round 10 B6d: the Final Night's end trial (10B) (#448)
- 2026-11-07 4d07e6ae Story mode: part 2 build decisions (A517)
- 2026-11-07 fb347b6b Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x12-flaky-tests [merge]
- 2026-11-07 1573eac3 docs: the story cards copy moves to UI.md 14.61 (14.54 is 10V's evidence verbs)
- 2026-11-07 6a1b79d4 docs(accounts): player accounts plan
- 2026-11-07 8c3c611a V2: the cover-up verbs: Drag body, Clean, Wash, the Skeleton Key and the Crowbar (10V)
- 2026-11-07 f32755f5 Story engine: sections (E1) and spoken lines (E7)
- 2026-11-07 45c4f98a B6d2: NPC seats present at the Tribunal and file at the end trial (A575)
- 2026-11-07 d8348e94 V3: the hiding spots, Chalk, Act Shifty and Fake Blood (10V, A555)
- 2026-11-07 cdcf5a76 story P3 1/3: section and NPC-line cards
- 2026-11-07 fdf5d6f7 story P3 2/3: save and resume, client half
- 2026-11-07 e121d7f0 Story engine: section and line cards on the part-2 wire
- 2026-11-07 1f11c9ab V2: seams.md 3 row 38
- 2026-11-07 9b11a980 Merge pull request #470 from groot99-droid/claude/story-answers [merge]
- 2026-11-07 fe545800 B6d2: story seed words for the trial streams
- 2026-11-07 5e4d9fc2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-x16-act-tick-wait [merge]
- 2026-11-07 e6d14530 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-m1-barks [merge]
- 2026-11-07 0869c4a8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-k3-candles [merge]
- 2026-11-07 970bc21e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-k6-snares [merge]
- 2026-11-07 fde896cb Merge remote-tracking branch 'origin/claude/r10-k6b-snares-npc' into claude/r10-k6-snares [merge]
- 2026-11-07 c6abdb5c DECISIONS: A260 in number order
- 2026-11-07 c3f16d75 V1b part a: the Doctor's Autopsy (10V, A555)
- 2026-11-07 816225af V1b part b: Dust and Compare (10V, A555)
- 2026-11-07 7264c1da story P3 3/3: the end screen
- 2026-11-07 eaa0adb8 Merge pull request #476 from groot99-droid/claude/story-p3-cards [merge]
- 2026-11-07 c5088b93 story P3: status log, #476 merged
- 2026-11-07 f438960d Merge pull request #477 from groot99-droid/claude/story-p3-save [merge]
- 2026-11-07 bd22f203 B6d2: NPC seats present at the Tribunal and file at the end trial (#474)
- 2026-11-07 ac07c403 Merge claude/story-part2 into claude/story-p2-sections [merge]
- 2026-11-07 ef89619f Merge base into V2 [merge]
- 2026-11-07 018249f9 Merge claude/story-part2 into story-p3-endscreen [merge]
- 2026-11-07 6c7f37ec V1b part b: drop an unneeded export
- 2026-11-07 f7185689 V3: merge the base, row 39, A576 and the hiding leak test [merge]
- 2026-11-08 241e279d Merge pull request #479 from groot99-droid/claude/story-p2-sections [merge]
- 2026-11-08 8b20de84 Story engine: a failed section replays once
- 2026-11-08 761b72cb Merge pull request #478 from groot99-droid/claude/story-p3-endscreen [merge]
- 2026-11-08 40caffe7 story P3: the menu and end screen list arc chapters
- 2026-11-08 c7b141a4 Merge base into V1b part a: both stream lists, DECISIONS A576 [merge]
- 2026-11-08 88eeed20 V3: NoteKind.checked 14, ClueKind.chalk 13 and A577 after V1b's numbers
- 2026-11-08 34d37f64 Merge pull request #482 from groot99-droid/claude/story-p3-arc-catalog [merge]
- 2026-11-08 516aeb60 story P3: final handoff in status.md
- 2026-11-08 655c3625 Story engine: the save port, story.saved at each chapter break, story.start resume
- 2026-11-08 a54d3761 Merge claude/story-part2 into claude/story-p2-replay [merge]
- 2026-11-08 37fea5e0 story P0: W1 clarified, the Medium's rite gates the 10X Vicar (arc 8.1, A517 addendum)
- 2026-11-08 b27885cb story P0: W1 owner answers folded in (against the Zealot, the area-spread buff)
- 2026-11-08 2c127e78 story P0: the rite, the buff's day, and a building for every role (arc 8.1, 8.2)
- 2026-11-08 6d27ae31 story P3: final handoff in status.md (#484)
- 2026-11-08 fe6bdb15 story P0: cite the Vicar's designed conversion power; next day or next match is open
- 2026-11-08 ed62cc88 story P0: same-match return, candidate buff list, martyr weight gated
- 2026-11-08 bd69f0a4 story P0: the Medium is an NPC gate at the hideout
- 2026-11-08 75b6e954 Merge pull request #481 from groot99-droid/claude/story-p2-replay [merge]
- 2026-11-08 ae5ac409 Merge part a into V1b part b: DECISIONS A576 [merge]
- 2026-11-08 1935ffb9 Merge claude/story-part2 into claude/story-p2-save [merge]
- 2026-11-08 46fd51ba story P0: the hideout in the deep woods; the Bandit's and Activist's own buildings
- 2026-11-08 5d01eb46 story P0: the NPC gate replaces the Medium card; the knock-on list
- 2026-11-08 19045d4e Story engine: story.start chapterId replays a finished chapter of the save
- 2026-11-08 3ce6de97 V1b part a: the Doctor's Autopsy (10V, A555) (#480)
- 2026-11-08 1548669e Merge the base (part a squashed in) into V1b part b [merge]
- 2026-11-08 c36a1685 Merge base into V2 (after #480) [merge]
- 2026-11-08 d2ade76e Merge pull request #485 from groot99-droid/claude/story-p2-save [merge]
- 2026-11-08 f001cddf V3: DECISIONS A578 (A577 is story P2's)
- 2026-11-08 a208b5d1 Story engine: the chapter's cast (E2)
- 2026-11-08 c11c467e V1b part b: Dust and Compare (10V) (#483)
- 2026-11-08 97edf0af Merge base into V2 (after #483) [merge]
- 2026-11-08 a8fe3f95 Merge pull request #486 from groot99-droid/claude/story-p2-cast
- 2026-11-08 9dd82911 Story engine E3: no early win, a win before the last section ends the running section
- 2026-11-08 e36a2b7d V2: the cover-up verbs: Drag body, Clean, Wash, Skeleton Key, Crowbar (10V) (#473)
- 2026-11-08 a1e4b4c8 Merge base (V2 #473) into V3; keep both sides, regenerate PROTOCOL.md [merge]
- 2026-11-08 f0b2ed77 Story engine E4: the NPC Killer holds the section's vendetta
- 2026-11-08 04a133b5 Merge pull request #487 from groot99-droid/claude/story-p2-nowin [merge]
- 2026-11-08 617030bb Merge claude/story-part2 into claude/story-p2-npcvendetta [merge]
- 2026-11-08 3046ece1 Merge pull request #488 from groot99-droid/claude/story-p2-npcvendetta [merge]
- 2026-11-08 aae7eaf8 Story engine E5: a section can turn the player into the Hitman, with a named mark
- 2026-11-08 58a6e973 V3: the hiding spots, Chalk, Act Shifty and Fake Blood (10V) (#475)
- 2026-11-08 dfe2f649 Merge pull request #489 from groot99-droid/claude/story-p2-hitman [merge]
- 2026-11-08 f68ac41b Story engine E6: the heir section waits for startWhen, runInherit emits inherit
- 2026-11-08 77bdc583 Story engine E8: night powers emit nightPower on the bus
- 2026-11-08 bb66a4ea Merge pull request #490 from groot99-droid/claude/story-p2-heir [merge]
- 2026-11-08 60eedd7f Merge claude/story-part2 into claude/story-p2-nightpower [merge]
- 2026-11-08 da2f5986 Story engine E9: story.picked when the player opens a lock
- 2026-11-08 14aa3374 Merge pull request #491 from groot99-droid/claude/story-p2-nightpower [merge]
- 2026-11-08 5e7af217 Merge claude/story-part2 into claude/story-p2-readpick [merge]
- 2026-11-08 b1bf130b Merge pull request #492 from groot99-droid/claude/story-p2-readpick [merge]
- 2026-11-08 72e6c324 Story engine E10: company trigger (story.company after shared time with a card)
- 2026-11-08 992cea18 Story engine E10: company trigger (story.company after shared time with a card) (#493)
- 2026-11-08 73b854d4 Story engine E12: cutscene action plays, meeting action rings the bell
- 2026-11-08 2920b48a Merge claude/zen-turing-m1jnw0 into claude/story-part2 [merge]
- 2026-11-08 98f411bd Merge pull request #494 from groot99-droid/claude/story-p2-basemerge [merge]
- 2026-11-08 4b8d1ce5 Merge remote-tracking branch 'origin/claude/story-part2' into claude/story-p2-cutscene [merge]
- 2026-11-08 e0d0dc60 Story engine E12: cutscene action plays, meeting action rings the bell (#495)
- 2026-11-08 12fac5bb Story engine E13: GDD 3.20 conversion time follows the data (160 s)
- 2026-11-08 bd9bccc5 Story engine E14: staging at a break (goTo spawn, validated orders)
- 2026-11-08 059461eb Story engine E13: GDD 3.20 conversion time follows the data (160 s) (#496)
- 2026-11-08 4416ac09 Merge claude/story-part2 into claude/story-p2-staging [merge]
- 2026-11-10 435ce12f Story mode: orchestrator handoff (open decisions, sessions, routine, art)
- 2026-11-10 e52ac6dd Story mode handoff: archival routine stopped
- 2026-11-10 0c3550be x16: act() waits for the room's tick, not the wall clock (#438)
- 2026-11-10 3a9ca585 Story engine E14: staging at a break (goTo spawn, validated orders) (#497)
- 2026-11-10 26ed246f Merge integration branch into story-s3-live [merge]
- 2026-11-10 ba7ebd91 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-m1-barks [merge]
- 2026-11-10 c68b11ac Story mode: orchestrator handoff (docs only) (#498)
- 2026-11-10 d97c2056 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k6-snares [merge]
- 2026-11-10 b1ea1641 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k3-candles [merge]
- 2026-11-10 a2c3627e Merge remote-tracking branch 'origin/claude/story-part2' into claude/story-p0-w1-medium [merge]
- 2026-11-10 b2915ba8 Merge remote-tracking branch 'origin/claude/story-part2' into claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-10 df55be90 Story mode handoff: P0 pushed (#499), E14 merged, finisher status
- 2026-11-10 959247b8 story P0: brief for the Medium's rite and the 10X Vicar (docs only)
- 2026-11-10 c604bfa7 story P0: W1 clarified, the Medium's rite gates the 10X Vicar (arc 8.1, 8.2, A517 addendum) (#499)
- 2026-11-10 29cec5a2 Merge claude/story-part2 into claude/story-p0-rite-brief [merge]
- 2026-11-10 12bf4871 story P0: rite brief, owner took the defaults on R-Q1 to R-Q8
- 2026-11-10 c923b2c3 M1: the barks stream joins STORY_STREAMS and every story's seed words
- 2026-11-10 d9e08735 Story mode handoff: P0 pushed, E14 merged, finisher status (docs only) (#500)
- 2026-11-10 edb62f3d story R1: retire the Medium card, Seance and Seance Chalk (A600)
- 2026-11-10 a32eb780 story P0: brief for the Medium's rite and the 10X Vicar (docs only) (#501)
- 2026-11-10 7b0faad0 Merge pull request #459 from groot99-droid/claude/story-s3-live [merge]
- 2026-11-10 a5656949 story R2: the martyr is a shade, not a ghost (A601)
- 2026-11-10 1f859ead Merge remote-tracking branch 'origin/claude/story-part2' into claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-10 de16d4cb Story handoff: #499 and #501 merged, Session R spawned, decisions 1 and 3 answered
- 2026-11-10 f48a933d Merge remote-tracking branch 'origin/claude/elegant-archimedes-ybxzlj' into claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-10 31295e66 Story S3: status after #459
- 2026-11-10 92dfc283 Merge pull request #504 from groot99-droid/claude/story-s3-status [merge]
- 2026-11-10 ab3ec7fb story R3: the Medium at the rite site, and the rite (A602)
- 2026-11-10 5523252a Story S3: final handoff
- 2026-11-10 b4b52eaf Merge pull request #506 from groot99-droid/claude/story-s3-handoff [merge]
- 2026-11-10 f494780e story R4: the martyr's return, the gated due, the candidacy gone (A603)
- 2026-11-10 2f128dc4 story R5: the 10X Vicar's buff until dusk (A604)
- 2026-11-10 fe0f3dc6 K6: the snare memory and heldBySnare move to body/snareHold.ts; the K6b tests await their sends and open the shop
- 2026-11-10 64d26d33 Story mode handoff: #499 and #501 merged, Session R, decisions 1 and 3 (#503)
- 2026-11-10 145f6e04 story R7: the rite on the client (A605)
- 2026-11-10 cc27c2ca story R5: the Ascended icon in the world palette, listed in SPRITES.md 9.1
- 2026-11-10 1225f898 Merge branch 'claude/story-r-buff' into claude/story-r-client [merge]
- 2026-11-11 37b46495 story R1: retire the Medium card, Seance and Seance Chalk (A600) (#502)
- 2026-11-11 c8ab7067 Merge claude/story-part2 (R1 squashed) into R2; log the #502 merge [merge]
- 2026-11-11 d63d9a2d Merge remote-tracking branch 'origin/claude/story-r-shade' into claude/story-r-rite [merge]
- 2026-11-11 dbd42013 e2e: wait for the World before skipping the opening; npc.spec takes the Village's ejection of the Killer
- 2026-11-11 ff7eb9c4 story R2: the martyr is a shade, not a ghost (A601) (#505)
- 2026-11-11 f787a001 Merge claude/story-part2 (R2 squashed) into R3; log the #505 merge [merge]
- 2026-11-11 a1212577 story R3: the Medium at the rite site, and the rite (A602) (#507)
- 2026-11-11 d3e6489e Merge claude/story-part2 (R3 squashed) into R4; log the #507 merge [merge]
- 2026-11-11 79ad4daf story R4: the martyr's return, the gated due, the candidacy gone (A603) (#508)
- 2026-11-11 408be426 Merge claude/story-part2 (R4 squashed) into R5; log the #508 merge [merge]
- 2026-11-11 bbf23658 test: wait for a scene change's arriving figures as well as the leaving ones
- 2026-11-11 122c9134 story R5: the 10X Vicar's buff until dusk (A604) (#509)
- 2026-11-11 70acdede Merge claude/story-part2 (R5 squashed) into R7; log the #509 merge [merge]
- 2026-11-11 103cb6e4 story R7: the rite on the client (A605) (#510)
- 2026-11-11 800c0e3c story R: log the #510 merge in status.md
- 2026-11-11 458608f0 story R: log the #510 merge in status.md (#511)
- 2026-11-11 59b06adf Story S3: status, S2 honours chapterId
- 2026-11-11 54a1028c Merge remote-tracking branch 'origin/claude/story-part2' into claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-11 ad862996 Story handoff: R's PRs merged (#502 to #511), R idle, R6 and R8 on hold
- 2026-11-11 11767e83 story I9: conversion, the Vicar's sermon at the bell, the Peaceful route recorded (A606)
- 2026-11-11 02fb7a21 Merge pull request #512 from groot99-droid/claude/story-s3-fixnote [merge]
- 2026-11-11 ef4f14f3 K6b: a snare-only shop visit ends at once; invariants.test.ts fixedSeeds offset 1 to 2 (owner's grant, 2026-11-11)
- 2026-11-11 fa14b508 story I9b: the sermon prompt at the bell, the conversion toasts, the Vicar's count
- 2026-11-11 0c0309ef Story handoff: I9 on R, 60 s bell, finisher grants, S3 retargeted
- 2026-11-11 bbb5e595 Story S3: Replay sends the device's save so the server replays the chosen chapter
- 2026-11-11 0aedd911 story I9: the sermon repeats after conversion.sermonCooldownS, not once a day (owner, A606)
- 2026-11-11 c13abd7a story I9b: the sermon prompt returns after conversion.sermonCooldownS (A606)
- 2026-11-11 097c7fb2 story I9b: A606 records the owner's answer, the listener gains once a day
- 2026-11-11 b08b9873 Story mode handoff: R's PRs merged (#502 to #511), R idle (#513)
- 2026-11-11 17d02f67 Merge claude/story-part2 into claude/story-s3-replay [merge]
- 2026-11-11 21ef2b3c story I9: conversion, the Vicar's sermon at the bell, the Peaceful route recorded (A606) (#515)
- 2026-11-11 fcb0fe77 Merge claude/story-part2 (#513) into story I9 [merge]
- 2026-11-11 ca989275 Merge pull request #514 from groot99-droid/claude/story-s3-replay [merge]
- 2026-11-12 1fbe5af7 Story handoff: #513 merged, I9 draft #515 (option a), finisher's third #441 grant [merge]
- 2026-11-12 93e42a08 Story S3: tidy two status lines after the Replay fix
- 2026-11-12 f96f32c3 e2e: the lock-pick snap waits on frames, not a 5 s wall clock (CI renderer starved)
- 2026-11-12 b676429e Merge pull request #517 from groot99-droid/claude/story-s3-tidy [merge]
- 2026-11-12 9990a4bb story I9: conversion, the Vicar's sermon at the bell, the Peaceful route recorded (A606) (#515)
- 2026-11-12 561b7e20 story R: log the #515 merge in status.md
- 2026-11-12 c71fbdff Story mode handoff: #513 merged, I9 draft #515, finisher's third #441 grant (#516)
- 2026-11-12 df728a75 Merge story-part2 into handoff branch [merge]
- 2026-11-12 026f88b8 Story handoff: #515 merged, I9b #518, R6 unblocked, PR triage
- 2026-11-12 1779e4e4 Story handoff: move the PR triage note next to the finisher notes
- 2026-11-12 4569d524 K6: npcChores.test.ts counts a snare-held seat as not idle and allows one tick of slack on the walkCap stand (owner's grants, 2026-11-11)
- 2026-11-12 dc2d67dd Story S3: status, replay for signed-in accounts is for A9
- 2026-11-12 b4ff3968 story R6: the dealt Vicar's conversion aura on the return day (A607)
- 2026-11-12 687109da Story handoff: R6 #521, the #515 test grant, #245 closed
- 2026-11-12 8b621474 story I9b: the sermon prompt at the bell, the conversion toasts, the Vicar's count (A606) (#518)
- 2026-11-12 5c481a9b Merge claude/story-part2 (#518) into story R6; log the #518 merge [merge]
- 2026-11-12 cb515739 Merge pull request #520 from groot99-droid/claude/story-s3-acctnote [merge]
- 2026-11-12 438f4df7 Story S3: tidy the wording of the final handoff line
- 2026-11-12 585379c5 Story mode handoff: #515 merged, I9b #518, R6 unblocked, PR triage (#519)
- 2026-11-12 886b3020 Merge pull request #522 from groot99-droid/claude/story-s3-tidy2 [merge]
- 2026-11-12 535b56f7 story R6: the dealt Vicar's conversion aura on the return day (A607) (#521)
- 2026-11-12 088d663e story R: log the #521 merge in status.md
- 2026-11-12 09027753 Merge story-part2 into handoff branch [merge]
- 2026-11-12 1066e4d8 Story handoff: R6, I9b and I9 merged; R left with R8 only
- 2026-11-12 0dfaaab7 story R: log the #521 merge in status.md (#523)
- 2026-11-12 7a129d62 story R6: A607 records the owner keeping the aura's numbers
- 2026-11-12 bb171c41 Merge story-part2 into handoff branch [merge]
- 2026-11-12 69589f71 Story handoff: the owner's defaults, #523 merged
- 2026-11-12 539656d7 story R6: A607 records the owner keeping the aura's numbers (#525)
- 2026-11-12 e2b1ccbb Story mode handoff: R6, I9b and I9 merged; R left with R8 only (#524)
- 2026-11-12 cfbcb6b1 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-s4-mugging [merge]
- 2026-11-12 4fc7800c Merge the base claude/zen-turing-m1jnw0 (0c3550be) into claude/r10-x9-grindstone [merge]
- 2026-11-12 bedcb094 Merge the base claude/zen-turing-m1jnw0 (0c3550be) into claude/r10-x14-decoded-views [merge]
- 2026-11-12 803520d7 Merge the base claude/zen-turing-m1jnw0 (0c3550be) into claude/r10-x17-constable-file-npc [merge]
- 2026-11-12 4b8d7c57 Merge the base claude/zen-turing-m1jnw0 (0c3550be) into claude/r10-x13-npc-night-bake [merge]
- 2026-11-12 b52b771f Merge base [merge]
- 2026-11-12 475489fd Merge base into r10-t6b-moods [merge]
- 2026-11-12 9199790a Merge claude/zen-turing-m1jnw0 into W1a1; route the new verbs' clueFound through clientOf [merge]
- 2026-11-12 a8d0f907 Merge base [merge]
- 2026-11-12 f09d0291 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c5c-knifeguards [merge]
- 2026-11-12 76698727 W1a1 test: the role card's Ready lands on the fresh seat
- 2026-11-12 540bb413 docs(story): orchestrator owns the round-10 lanes brought back from archive
- 2026-11-12 9b7ebf72 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-c4c-hardships [merge]
- 2026-11-12 753b563d Build the 3D HollowMere village from the owner's Meshy models
- 2026-11-12 85668f6f C4c: the story seed words cover the hardship stream (STORY_STREAMS equals AUTO_STREAMS, A401)
- 2026-11-12 26d7f809 docs(story): log the orchestrator's grants and canon calls
- 2026-11-12 9f490c8a docs(story): the map revamp is the owner's Blender 3D work
- 2026-11-12 6cf9071e W1a1 tests: Human.id resolves to the seat id after Start (test-helper grant from the orchestrator, 2026-11-12)
- 2026-11-12 98b4c984 Merge the base into S1a; GDD 3.14 containers paragraph [merge]
- 2026-11-12 9bcdd6db Merge branch 'claude/r10-c4c-hardships' into claude/r10-c4d-ledger [merge]
- 2026-11-12 e5cd70f1 story R8a: draft arc.md 3.4, the martyr's section (A608)
- 2026-11-12 fdb98b67 Merge base into S5: keep both DECISIONS rows and UI.md sections [merge]
- 2026-11-12 f3aeb4ee docs(story): the owner overruled the orchestrator's Blender canon answers
- 2026-11-12 840ae865 story R8b: the martyr's shade in a story section, and the rite on the bus
- 2026-11-12 e18535f9 style: prettier on the Blender tool files so the base's check passes
- 2026-11-12 ef4badfc story R8c: the shade handover, the player takes the martyr's body (E15)
- 2026-11-12 57b093e0 Format the HollowMere village files with Prettier
- 2026-11-12 3fe4ed9d Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-s5-artstyle [merge]
- 2026-11-12 2355f6e8 Format the Meshy village files so prettier --check passes; ignore the tool-written model lock
- 2026-11-12 cefceb12 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k6-snares [merge]
- 2026-11-12 760af9fb docs(map-revamp): the interiors plan for the owner and the Blender session
- 2026-11-12 b7bce510 Bots find their own seat by Private.seatId (row 25): a world match re-keys the seats at Start
- 2026-11-12 334c84c9 story R8a: draft arc.md 3.4, the martyr's section (A608) (#526)
- 2026-11-12 1347159e docs(map-revamp): the owner's decisions: every Meshy model is HollowMere's; the draft outskirts
- 2026-11-12 34a7ee67 Merge remote-tracking branch 'origin/claude/story-part2' into claude/story-r8b-shade [merge]
- 2026-11-12 f99de166 Merge branch 'claude/story-r8b-shade' into claude/story-r8c-handover [merge]
- 2026-11-12 9c6883be docs(story): the owner's lake and Meshy-model decisions
- 2026-11-12 2c1ed59e style: prettier on the Blender tool files so the base's check passes (#528)
- 2026-11-12 00e4042d Merge the base (#528) [merge]
- 2026-11-12 8b586d08 Merge the base (#528) [merge]
- 2026-11-12 ed8e8c07 docs(map-revamp): the owner picks option (a) for interior scale
- 2026-11-12 08be3d2f Merge the base (2c1ed59) into C4c: the Meshy files' formatting fix [merge]
- 2026-11-12 6dd5e8f3 Merge base into r10-t6b-moods [merge]
- 2026-11-12 b0d9c805 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-x12-flaky-tests [merge]
- 2026-11-12 ff2498c9 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-m1-barks [merge]
- 2026-11-12 9bbc6d21 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k3-candles [merge]
- 2026-11-12 a9e7d0b8 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-s4-mugging [merge]
- 2026-11-12 85a1c57b Merge base claude/zen-turing-m1jnw0 (prettier fix #528) [merge]
- 2026-11-12 6b2c500e Merge base claude/zen-turing-m1jnw0 (prettier fix #528) [merge]
- 2026-11-12 7feb135d Merge the base claude/zen-turing-m1jnw0 (2c1ed59e) into claude/r10-x9-grindstone [merge]
- 2026-11-12 4e6344d5 Merge the base claude/zen-turing-m1jnw0 (2c1ed59e) into claude/r10-x13-npc-night-bake [merge]
- 2026-11-12 749e751a Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-w1a1-seat-ids [merge]
- 2026-11-12 48361a1d Merge the base claude/zen-turing-m1jnw0 (2c1ed59e) into claude/r10-x17-constable-file-npc [merge]
- 2026-11-12 2fa52aeb Merge the base (Prettier on the village files) into S1a [merge]
- 2026-11-12 e57d263a story R8d: a shade's section is skipped with no shade waiting (E17)
- 2026-11-12 82fd76ac Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k6-snares [merge]
- 2026-11-12 b1a353ee Merge the base (#528, Prettier on the Blender files) into S1a [merge]
- 2026-11-12 628e2500 docs(map-revamp): the net loft stays exterior only
- 2026-11-12 ea6505fd Merge C4c (08be3d2, carrying the base 2c1ed59) into C4d [merge]
- 2026-11-12 5d5f93f7 docs(map-revamp): record owner answer to Q4 (3D interiors replace interior art)
- 2026-11-12 f92ed04b docs(map-revamp): owner answers part of Q2 (hideout, post office)
- 2026-11-12 ec504c8a story S3: log the full local e2e run and the merges since #522 in status.md
- 2026-11-12 850166ee Merge the base (2c1ed59) into C5c: the Meshy village files and their formatting fix [merge]
- 2026-11-12 a973aa5c Ignore the Poly Haven model lock in Prettier, as its sibling lock is (#530)
- 2026-11-12 13f93583 C4b client half: the Derringer's slot, the Departed screen and the Hitman's end-panel line
- 2026-11-12 435daaa6 Merge the base claude/zen-turing-m1jnw0 (2c1ed59e) into claude/r10-x14-decoded-views [merge]
- 2026-11-12 60417560 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-s5-artstyle [merge]
- 2026-11-12 8a59c606 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y1-refusal-lines [merge]
- 2026-11-12 b711d4c8 story R8b: the martyr's shade in a story section, and the rite on the bus (#527)
- 2026-11-12 f755f848 Merge claude/story-part2 (#527 merged) into claude/story-r8c-handover [merge]
- 2026-11-12 2ff7ca38 Merge branch 'claude/story-r8c-handover' into claude/story-r8d-skip [merge]
- 2026-11-12 a1731ae9 Merge pull request #472 from groot99-droid/claude/accounts-plan [merge]
- 2026-11-12 ec78918e Merge base into claude/ui-renumber [merge]
- 2026-11-12 005645ee Merge pull request #444 from groot99-droid/claude/r10-s3-forge [merge]
- 2026-11-12 4580a77f Merge base claude/zen-turing-m1jnw0 (S3 forge chain, #444) [merge]
- 2026-11-12 373ef3f4 Merge the base (S3's forge chain, #444) into S1a [merge]
- 2026-11-12 270a67e8 Merge pull request #428 from groot99-droid/claude/r10-s5-artstyle [merge]
- 2026-11-12 e0d723fc e2e: skipOpening waits for the HUD clock, not a 10 s cutscene window
- 2026-11-12 0c0654fc e2e: skipOpening waits for the HUD clock, not a 10 s cutscene window
- 2026-11-12 9a01ace6 e2e: skipOpening waits for the HUD clock, not a 10 s cutscene window
- 2026-11-12 1a8903d8 e2e: skipOpening waits for the HUD clock, not a 10 s cutscene window
- 2026-11-12 85198490 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-y1-refusal-lines [merge]
- 2026-11-12 6973e658 Merge base claude/zen-turing-m1jnw0 (270a67e8) into x13 [merge]
- 2026-11-12 12d038d4 Merge pull request #422 from groot99-droid/claude/r10-s4-mugging [merge]
- 2026-11-12 4aab123f Merge pull request #533 from groot99-droid/claude/story-s3-status-e2e [merge]
- 2026-11-12 51839cdd Merge base into claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-12 b9e88097 Merge pull request #437 from groot99-droid/claude/r10-x12-flaky-tests [merge]
- 2026-11-12 4abd6dc2 Merge pull request #443 from groot99-droid/claude/r10-c4d-ledger [merge]
- 2026-11-12 e86a68f1 Merge the base (4abd6dc, with C4c and C4d) into C5c [merge]
- 2026-11-12 53b770aa D4b: the bakery's pastry dishes (Game Pie, Berry Tart, Miner's Pasty)
- 2026-11-12 e44c09c9 Merge pull request #471 from groot99-droid/claude/ui-renumber [merge]
- 2026-11-12 de881b1a D4b: the Heartened and Tireless icons, the client recipe list
- 2026-11-12 e9b951de Merge origin/claude/zen-turing-m1jnw0 into the C4b client half [merge]
- 2026-11-12 e0103c2a Merge origin/claude/zen-turing-m1jnw0 into claude/r10-m1-barks [merge]
- 2026-11-12 a2b000ee Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k6-snares; npcSnares reads the Rope gap at the freeing [merge]
- 2026-11-12 79e22939 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k3-candles [merge]
- 2026-11-12 ec677146 docs(story): the orchestrator handoff, docs only (replaces #464)
- 2026-11-12 62318b55 story R8c: the shade handover, the player takes the martyr's body (E15) (#529)
- 2026-11-12 b9113df5 Merge claude/story-part2 (#529 merged) into claude/story-r8d-skip [merge]
- 2026-11-12 4ebdccbf Merge pull request #445 from groot99-droid/claude/r10-t6b-moods [merge]
- 2026-11-12 654f6da4 Merge pull request #397 from groot99-droid/claude/r10-x14-decoded-views [merge]
- 2026-11-12 69aa710f x17: the NPC collect test stands the NPC seats through the hold
- 2026-11-12 8e92cb59 Merge pull request #430 from groot99-droid/claude/r10-s2-berries [merge]
- 2026-11-12 d94ade0d Merge pull request #425 from groot99-droid/claude/r10-x9-grindstone [merge]
- 2026-11-12 1871a9eb Merge claude/zen-turing-m1jnw0 at d94ade0d (#397, #425) into claude/r10-x13-npc-night-bake [merge]
- 2026-11-12 e6774c89 Merge claude/zen-turing-m1jnw0 at d94ade0d (#397, #425) into claude/r10-x17-constable-file-npc [merge]
- 2026-11-12 d5a4385a W1a1: merge the base; the ledger answer goes to the seat's client [merge]
- 2026-11-12 69393ff0 Merge pull request #429 from groot99-droid/claude/r10-s1-containers [merge]
- 2026-11-12 707e2631 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-m1-barks [merge]
- 2026-11-12 c305a560 Merge base into D4b (S2 merged; GDD 3.14 resolved) [merge]
- 2026-11-12 9b74a035 Merge pull request #531 from groot99-droid/claude/interiors-plan [merge]
- 2026-11-12 c1f784d5 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k6-snares; NPC routine: no idle after a counter sale, holdTries reset at a visit end [merge]
- 2026-11-12 ecbab033 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k3-candles [merge]
- 2026-11-12 719970b9 Merge pull request #535 from groot99-droid/claude/story-handoff-docs [merge]
- 2026-11-12 067b7917 Merge pull request #442 from groot99-droid/claude/r10-x17-constable-file-npc [merge]
- 2026-11-12 e258238b Merge pull request #426 from groot99-droid/claude/r10-c5c-knifeguards [merge]
- 2026-11-12 afd32484 Merge pull request #534 from groot99-droid/claude/r10-y1-refusal-lines [merge]
- 2026-11-12 1d3b0d67 story R8d: a shade's section is skipped with no shade waiting (E17) (#532)
- 2026-11-12 2ed421c1 story R8: log the #532 merge in status.md
- 2026-11-12 787b3bb1 Merge pull request #536 from groot99-droid/claude/r10-d4b-dishes [merge]
- 2026-11-12 3467f9ef Merge pull request #431 from groot99-droid/claude/r10-x13-npc-night-bake [merge]
- 2026-11-12 b2977b80 Merge pull request #441 from groot99-droid/claude/r10-k6-snares [merge]
- 2026-11-12 8b3ca017 Merge pull request #537 from groot99-droid/claude/story-r8-log [merge]
- 2026-11-12 9989c4c5 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-k3-candles [merge]
- 2026-11-12 f1af726a W1a1: merge the base; the snare views key on the seat id [merge]
- 2026-11-12 5b29ae0d Merge pull request #440 from groot99-droid/claude/r10-k3-candles [merge]
- 2026-11-12 54f13871 W1a1: a body in reach wins the E prompt, unless the player stands on a clue (A579)
- 2026-11-12 f5e915e2 Merge origin/claude/zen-turing-m1jnw0 into claude/r10-m1-barks [merge]
- 2026-11-12 42e7c331 Test fixes for two base flakes: needs.test's seat holds no light, npc.spec kills the watcher out of the NPCs' sight
- 2026-11-12 873d1184 W1a: break the seatIds -> Flow import cycle; seat-id test edits (grant)
- 2026-11-13 3647236b Merge pull request #435 from groot99-droid/claude/r10-m1-barks [merge]
- 2026-11-13 9534cd61 W1a: lobby fuzz pairs Start snapshots by seat name (owner grant)
- 2026-11-13 580daa3e Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r10-w1a1-seat-ids [merge]
- 2026-11-13 ad2fdedf W1a: barks reach a client through its seat (seatOf)
- 2026-11-13 5d6f597b Merge pull request #447 from groot99-droid/claude/r10-w1a1-seat-ids [merge]
- 2026-11-13 629e8bab Merge remote-tracking branch 'origin/claude/story-part2' into claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-13 f18946a1 Merge the base into the story branch for its merge into the base [merge]
- 2026-11-13 89c2095c docs: the owner's sign-off on the round-10 proposals (A609)
- 2026-11-13 1aef5801 Merge pull request #538 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-13 5f55f83d Build HollowMere's woods, mine and outskirts in 3D from the owner's Meshy models
- 2026-11-13 57d98d08 Merge pull request #539 from groot99-droid/claude/blender-hollowmere-3d [merge]
- 2026-11-13 e9467db4 walk: V2 first-person walk-through app (skeleton, loader, controls, collision)
- 2026-11-13 38fc4caf Merge pull request #540 from groot99-droid/claude/v2-walk [merge]
- 2026-11-13 5925876d pages: serve the walk-through at /Who-Did-It/walk/
- 2026-11-14 1e6112eb walk: handle the real HollowMere GLB (look, areas, spawn labels, instanced collision)
- 2026-11-14 56d93df2 docs(map-revamp): interiors at 1 m per tile and the room-art delivery
- 2026-11-14 8c4983e3 docs(map-revamp): the rooms go first person; the iso room renders are on hold
- 2026-11-14 f7d3b9dc Merge pull request #542 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-14 2133a969 Merge pull request #541 from groot99-droid/claude/v2-walk [merge]
- 2026-11-14 e981fa45 walk: rooms and portals (per-area look, indoor areas, grouped picker, doors)
- 2026-11-14 15ff938a walk: keep real-time speed on slow frames (frame clamp 0.1 s -> 0.25 s)
- 2026-11-15 c7246d31 walk: handle the v1.2 baked rooms and doors with no target
- 2026-11-15 410480bd docs: two views, the 2.5D game stays and a 3D HD first-person view is added (A611)
- 2026-11-15 509df801 walk: host the world GLB as a release asset fetched at deploy time
- 2026-11-15 d880b934 Merge pull request #544 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-16 f32f5ffc test(server): wait on the server's messages, not on wall time
- 2026-11-16 7bff2279 test(server): act() sleeps until its floor has passed
- 2026-11-16 001e0fef test(e2e): renew the dusk while the host walks to its victim
- 2026-11-16 a85ab6bc test(e2e): sidestep when the host is blocked on its way to the victim
- 2026-11-16 f8a197e6 bots: the walker timer tolerates a state that has no players yet
- 2026-11-16 59ed2e32 Merge pull request #543 from groot99-droid/claude/v2-walk [merge]
- 2026-11-16 3a3d07a3 Merge pull request #545 from groot99-droid/claude/nice-davinci-b9wlz6 [merge]
- 2026-11-16 71a5191f docs: every map-revamp building gets an interior (A612)
- 2026-11-16 eb91c24b docs: two modes only, 2.5D and 3D; the three styles become one (A613)
- 2026-11-16 5f8cd1d3 Merge pull request #546 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-16 f2f5dbff Walk export and the first first-person room for HollowMere
- 2026-11-16 78c07271 docs: each room its own GLB, the village cut into sections joined by portals (A614)
- 2026-11-16 64461cb2 Merge pull request #548 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-17 957a02b3 Room checks, the Blender lock, room files and a regression gate
- 2026-11-17 8c10094f docs: the merged 2.5D look, a sprite world with depth (A615)
- 2026-11-17 acacbcbc docs: the owner's answers on the sprite world (A615)
- 2026-11-17 6bd427a0 docs: the figure cell is 64 px (A615)
- 2026-11-17 23ab40f0 docs: tidy the sprite-world answers
- 2026-11-17 6d61de49 Walk areas: the contract for one GLB per area, its checkers and a test world
- 2026-11-19 a576f5e5 docs: CLAUDE.md and README describe the repo as built
- 2026-11-19 6d29df54 docs: index, roadmap status, architecture and world catch up
- 2026-11-19 ab605ade docs(sessions): the lanes after round 11's plan
- 2026-11-19 68d3dec0 docs: assets, the content package and the vendor terms match the tree
- 2026-11-19 05a67589 docs: status notes for story mode, accounts and the playtest kit
- 2026-11-19 d03546cf docs: dated banners on the frozen plan and the round contracts
- 2026-11-19 131270cd docs(ui): the menu rows for Join Game and Friends describe the landed screens
- 2026-11-19 36b24e8b docs(licenses): the help pages' own font copies are named
- 2026-11-19 34ca393a docs: status lines on round 10's pickup list and the story handoff
- 2026-11-19 27bae687 docs: CLAUDE.md and README point at ROADMAP 7.0 for the status
- 2026-11-19 8533d599 Merge pull request #550 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
- 2026-11-19 b0837ef2 Merge base into the A615 branch: keep the round12 index row beside the new rows [merge]
- 2026-11-19 f100f276 Merge pull request #549 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 aaa5bd2e docs: round 11 revised for the sprite world of A615 (draft for the owner)
- 2026-11-19 0f7e8d78 docs: round 11's revised plan approved with every default (A616)
- 2026-11-19 1d7ff0a4 Blender lock on a signal and at take-over, its tests, room check fixes
- 2026-11-19 3bea3433 docs: CREDITS row for the 75 Meshy models in the walk GLB; A616 records the open questions the code has settled
- 2026-11-19 2a3e0ef0 docs: WORLD 4.9 gives the 3D view's two scales; R11 is the Blender makeover; the 2.5D mode presents isometrically
- 2026-11-19 55b83c96 Merge pull request #551 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 809e69e0 docs: round 11 opens: the session rows, the seams and the handoff indexes
- 2026-11-19 caaaaa75 Merge the base into the docs PR; renumber the settled-questions row to A617 and follow A616 [merge]
- 2026-11-19 85a82512 docs: S0, three 0.186.1 for the client's sprite world, measured and budgeted (A617)
- 2026-11-19 f1fd460c T1: the bpy job, setup.sh and the bpy tests
- 2026-11-19 76237403 Round 11 P1: the prop list
- 2026-11-19 865252ae T3: the 25 MB art-drop warning
- 2026-11-19 9ac09f9a tools/blender/models: H1, the model releases' lock, fetcher and ASSETS 6.12
- 2026-11-19 a1538161 T1: eslint ignores the bpy venv
- 2026-11-19 f4c827fe T4: render locks, the writer
- 2026-11-19 0d5bed8f T1: setup.sh gets Python 3.13 from uv when the system python is not 3.13
- 2026-11-19 68c726bd T5: render locks, the check
- 2026-11-19 8637bf84 Merge pull request #552 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
- 2026-11-19 b1b0957e Merge pull request #553 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 3123bc98 Round 11 P1: the handoff is on the base now
- 2026-11-19 d411b605 Merge the base; renumber the S0 row to A618 (A617 was taken) [merge]
- 2026-11-19 8abdde02 Keep the bpy GLB fixture as base64 text so the LFS pattern does not turn it into a pointer
- 2026-11-19 e8274f7a Round 11 P1: owner answered Q-P1 to Q-P4
- 2026-11-19 8aa4373c Merge pull request #557 from groot99-droid/claude/r11-d-h1-models [merge]
- 2026-11-19 17e7224e Record the owner's CC0 answer for Meshy models (A616 Q1)
- 2026-11-19 9f61dd35 Merge pull request #558 from groot99-droid/claude/r11-t-art-drop-warning [merge]
- 2026-11-19 f160c76c Merge base into render locks writer [merge]
- 2026-11-19 b6fc8310 Merge base into claude/r11-t-bpy-job [merge]
- 2026-11-19 4b060435 Merge base into claude/r11-t-render-lock-check [merge]
- 2026-11-19 ff96ec82 Blender lock: fail closed at take-over, close two signal gaps
- 2026-11-19 0132a27d test(server): fix the mugFlight and manhunt flakes at their random sources
- 2026-11-19 0e125413 Merge pull request #554 from groot99-droid/claude/r11-d-s0-three [merge]
- 2026-11-19 66075aba docs: round 11, 11R starts: its seams row and the orchestrator log
- 2026-11-19 d121de02 Merge the production base into the walk export branch [merge]
- 2026-11-19 e259a71e test(server): the briefing test waits on the server's messages, not on wall time
- 2026-11-19 57154da7 R1a: the sprite world's scene build (world3/frame, world3/build)
- 2026-11-19 efe686f4 R1b: the sprite world draws under Phaser with ?render=sprite
- 2026-11-19 db91df87 R1c: the three chunk budget check (A618) and the static-import test
- 2026-11-19 a4e0afa0 Merge pull request #555 from groot99-droid/claude/r11-t-bpy-job [merge]
- 2026-11-19 f91b7cd8 Merge pull request #561 from groot99-droid/claude/r11-d-h1-meshy-licence [merge]
- 2026-11-19 3e166bdc Merge pull request #556 from groot99-droid/claude/r11-p-prop-list [merge]
- 2026-11-19 b019dea8 Merge base into the render lock writer branch [merge]
- 2026-11-19 f5db6e79 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r11-t-render-lock-check [merge]
- 2026-11-19 1bff20de Merge pull request #563 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 340efebc Merge pull request #562 from groot99-droid/claude/focused-cori-c2owsz [merge]
- 2026-11-19 1e606019 Merge pull request #564 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
- 2026-11-19 dbde07d3 docs: round 11, 11F starts: its seams row and the orchestrator log
- 2026-11-19 0b3a870f docs(round11): P2 tiles and wall textures brief and proposed seams row
- 2026-11-19 371776ac test(server): queued waits on lobby commands and moves too
- 2026-11-19 2ae1601a test(server): the hold and refusal helpers wait on the server's messages, not on wall time
- 2026-11-19 d5121f47 Fix the 390w screens e2e: a leaning row overflows, the 3x3 square leaves view
- 2026-11-19 f556ad71 Merge pull request #568 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 e221c76c F1: the figure rig, a character GLB to 64 px figure frames
- 2026-11-19 6b4d4ce5 test(server): commands sent before a paused step are queued, not slept on
- 2026-11-19 276ef686 test(server): wait on the server's messages and the queue, not on wall time
- 2026-11-19 a94c5fa9 Merge pull request #565 from groot99-droid/claude/r11-r-r1-scene [merge]
- 2026-11-19 51c5a6c4 Merge pull request #566 from groot99-droid/claude/r11-r-r1-render [merge]
- 2026-11-19 23c65979 Merge pull request #559 from groot99-droid/claude/r11-t-render-lock-writer [merge]
- 2026-11-19 7b8f4f6b Merge pull request #567 from groot99-droid/claude/r11-r-r1-budget [merge]
- 2026-11-19 3897a440 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r11-t-render-lock-check [merge]
- 2026-11-19 96fc08f2 Merge pull request #569 from groot99-droid/claude/r11-p-p2-brief [merge]
- 2026-11-19 d333da19 docs: round 11, 11P's P2 paths in the seams and the orchestrator log
- 2026-11-19 6aae45e7 Deal the humans a turnable card in the hitman turning test
- 2026-11-19 a2f647c9 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r11-f-figure-rig [merge]
- 2026-11-19 8ab35185 test(server): direct handler calls and paused steps flush before the clients are read
- 2026-11-19 37ef0432 feat(world3): P2a ground tiles for the sprite world
- 2026-11-19 65c0470e F1: write the figure's render lock now that T4 has merged
- 2026-11-19 06dec225 F1: a cover card is never a figure
- 2026-11-19 b24c0a3c P2b: wall and roof textures for the sprite world
- 2026-11-19 ebff2bfc F1: shrink a figure taller than 1.75 m to fit the 112 px cap
- 2026-11-19 74a1f085 P2b: fit the CREDITS row to the table so prettier passes
- 2026-11-19 883c2b3e F2: the figure batch, the drop script and the figure tests (atlases to follow)
- 2026-11-19 1c4f2a8a F2: the figure batch, the drop script and the figure tests (atlases to follow)
- 2026-11-19 7754c763 test(server): the same races under other names: wait(), setTimeout and send's own sleep
- 2026-11-19 e34375ce F1: fit the figure to the cell by its projected top, not its height alone
- 2026-11-19 c5874140 F2: type the tone check's k-means sums as tuples
- 2026-11-19 8a090c1a Merge remote-tracking branch 'origin/claude/r11-f-f2-higgsfield-1' into claude/r11-f-f2-higgsfield-1 [merge]
- 2026-11-19 7aa0e3b4 R2: the sprite world's camera turns in quarter turns, and input turns with it
- 2026-11-19 ced953f3 Run the bpy figure tests in the blender job
- 2026-11-19 77821006 Merge pull request #560 from groot99-droid/claude/r11-t-render-lock-check [merge]
- 2026-11-19 05565a50 F2: the first five Higgsfield figures (baker, constable, detective, doctor, fisher)
- 2026-11-19 4c6bdc04 F2: the ink floor for figure pages (proposed)
- 2026-11-19 e4a667b2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into local/sleep-races [merge]
- 2026-11-19 ee843288 test(server): wait on the queue and on messages in the paused-clock send-only tests
- 2026-11-19 10534734 Merge pull request #570 from groot99-droid/claude/r11-r-m5b-list-nudge [merge]
- 2026-11-19 5e89d43e Merge pull request #574 from groot99-droid/claude/r11-r-hitman-flake [merge]
- 2026-11-19 72c18459 Merge pull request #573 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 0df774c0 F2b: the CREDITS and MANIFEST rows for the next five Higgsfield figures (atlases to follow)
- 2026-11-19 99ee5da6 docs(round11): 11P's tile test lives in apps/client/src/
- 2026-11-19 1fa4facc Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r11-p-p2a-ground [merge]
- 2026-11-19 d3e68660 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r11-p-p2b-walls [merge]
- 2026-11-19 be4f3c87 F2b: the next five Higgsfield figures (gamekeeper, herbalist, lamplighter, tinner, watchman)
- 2026-11-19 a388adb9 Merge pull request #571 from groot99-droid/claude/r11-f-figure-rig [merge]
- 2026-11-19 e1a081b2 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r11-f-f2-higgsfield-1 [merge]
- 2026-11-19 3934e060 Merge branch 'claude/r11-f-f2-higgsfield-1' into claude/r11-f-f2-higgsfield-2 [merge]
- 2026-11-19 646efc4a test(server): seatIds waits for the seat to show disconnected after leave(), not 200 ms
- 2026-11-19 e7f928c0 Merge pull request #581 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 8eb33323 Merge pull request #576 from groot99-droid/claude/r11-p-p2b-walls [merge]
- 2026-11-19 bdf23fc3 Merge remote-tracking branch 'origin/claude/zen-turing-m1jnw0' into claude/r11-p-p2a-ground [merge]
- 2026-11-19 8113c08f docs(round11): 11P's P2b walls generator and test in its seams row
- 2026-11-19 4e5774e0 Walk-areas contract 1.1: caves, walk-only scenes, roofed seams, mouths
- 2026-11-19 66745afa Merge branch 'claude/zen-turing-m1jnw0' of https://github.com/groot99-droid/who-did-it into claude/gallant-goodall-k95p1k [merge]
- 2026-11-19 3f09d4a7 Merge pull request #584 from groot99-droid/claude/elegant-archimedes-ybxzlj [merge]
- 2026-11-19 7ea8dc55 Merge branch 'claude/gallant-goodall-k95p1k' into claude/gallant-goodall-k95p1k-send-waits [merge]
- 2026-11-19 aa53d68e Merge pull request #575 from groot99-droid/claude/r11-p-p2a-ground [merge]
- 2026-11-19 e1de9fd9 walk: crawl, sidle and climb modes driven by Trav_ zones
- 2026-11-19 45cf0b91 Merge pull request #572 from groot99-droid/claude/gallant-goodall-k95p1k [merge]
- 2026-11-19 91d5b81a Record the owner's questionnaire (A619); the Vicar's model joins char-models
- 2026-11-20 eed6ab70 Merge pull request #577 from groot99-droid/claude/r11-t-blender-figures-step [merge]
- 2026-11-20 26317e04 A619: mallory's look is Doc Mallory, the apothecary NPC (owner, 2026-11-20)
- 2026-11-20 90f644cf F2c: mallory gets a figure look; the batch maps it (11F)
- 2026-11-20 881460d2 F2c: villager, villagerlass and Doc Mallory figure atlases (11F)
- 2026-11-20 36e08ecd F2c: a nameplate line for Doc Mallory (11F)
- 2026-11-20 f8580f6e Merge the production base into the walk export branch [merge]
- 2026-11-20 9911b129 Merge the production base (#572) into the paused-clock waits [merge]
- 2026-11-20 4e3ca796 Merge the base into the PR branch, keeping only what 276ef686 does not already cover [merge]
- 2026-11-20 466ca5f2 Merge remote-tracking branch 'origin/claude/inspiring-cori-juqfrm' into claude/inspiring-cori-juqfrm [merge]
- 2026-11-20 909c3aa1 Merge pull request #579 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
