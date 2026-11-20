# Make the R18 NPC determinism test robust to real clock ticks

| Field | Value |
|---|---|
| Session ID | `session_01MFM1XhKpMDUYYyguQLzART` |
| State | Archived |
| Outcome bucket | Completed |
| Started from | Claude desktop app |
| Environment | anthropic_cloud |
| Created | 2026-10-22 18:24 UTC |
| Last activity | 2026-10-22 19:26 UTC |
| Span between created and last activity | 1.0 h |
| Group | Who Did It, game planning and fixes |
| Likely repositories [inference from the title] | Who-Did-It |

## What the session itself reported

- **Last action it recorded:** PR #50 merged into claude/zen-turing-m1jnw0: standard party tick timeline fixed from lobby, R18 compares start tick, sim untouched

## Items named in the session's own summary

- Pull request numbers: #50

## Items linked to this session

How items were matched: (1) by the label in the session title appearing in a commit subject; (2) by time, meaning commits and new documents dated inside the session window (created minus 10 minutes to last activity plus 45 minutes) in the repositories this session likely touched. Parallel sessions overlap in time, and commit dates in some repositories cluster on integration days, so time matches are suggestions, not proof. Session transcripts were not read.

### Matched by label (stronger evidence): 0 commits

This session has no label in its title to match on.

### Documents and questionnaires added in the window: 0

None found.

### Pull requests merged in the window: 5

- 2026-10-22 Who-Did-It #47 `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-22 Who-Did-It # `Merge pull request #48: Round 6 (6L) music bus, director, settings panel, slot l`
- 2026-10-22 Who-Did-It # `Merge pull request #50: make the standard NPC party's tick timeline independent `
- 2026-10-22 Who-Did-It # `Merge pull request #53: 6Z seams.md and m5b-data.md say stackMax, not gatherHold`
- 2026-10-22 Who-Did-It # `Merge pull request #51: Round 6 (6K) loading screen, transitions, landing traile`

### Other commits in the window: 20

By repository: Who-Did-It 20

- 2026-10-22 18:29 Who-Did-It `b0bbb051` Round 6 media: the owner's answers, the loading music class, the two release batches (A81)
- 2026-10-22 18:51 Who-Did-It `ca4359d5` 6A step 1: the sim clock (budget guard, carry, pause, effective scale) and its writer test
- 2026-10-22 18:52 Who-Did-It `3308ca90` Round 6 (6K): scene transitions with transitionS seconds
- 2026-10-22 18:53 Who-Did-It `2e090d27` Round 6 (6L) PR 1: music bus, audio settings and the sound settings panel
- 2026-10-22 18:55 Who-Did-It `168c47ea` 6E step 1: resources, recipes, material items and the M5b craft checks
- 2026-10-22 19:03 Who-Did-It `20d75657` Round 6 (6K): loading screen with tips and the loading.* balance rows
- 2026-10-22 19:03 Who-Did-It `1cf39479` Round 6 (6L) step 2: music director, music.json mapping, GDD 3.18 music paragraph
- 2026-10-22 19:04 Who-Did-It `192ac5ac` Make the standard NPC party's tick timeline independent of wall time
- 2026-10-22 19:04 Who-Did-It `dab4ef05` 6A step 2: enableAuto, the auto command queue, the headless harness and a one-day match per mode
- 2026-10-22 19:05 Who-Did-It `acc79c3f` Round 6 (6L) step 3: slot list for the owner, beds waiting on the library release
- 2026-10-22 19:10 Who-Did-It `50e134fe` Round 6 (6L) step 3: CC0 beds for the lobby and the end screen
- 2026-10-22 19:14 Who-Did-It `1f5d068f` Round 6 (6K): landing trailer, media budget test, manifest shapes, docs
- 2026-10-22 19:15 Who-Did-It `93ba3d06` 6E steps 2 and 3: mobs, quest npcs and quests, mini-games, their checks
- 2026-10-22 19:15 Who-Did-It `4e44791c` Cutscenes: rules, HollowMere and Blackpine openings, content checks, openingS (6J PR 1)
- 2026-10-22 19:24 Who-Did-It `035bdc7f` Round 6 seams: balance.resources carries stackMax, not gatherHoldS (6E deviation 1)
- 2026-10-22 19:26 Who-Did-It `f9129601` 6A step 3: determinism and clientless-dispose tests, the pnpm auto runner, GDD 3.19 and A83
- 2026-10-22 19:26 Who-Did-It `480993ed` 6E step 4: small-profile nodes, per-profile craft check, GDD 3.14-3.16
- 2026-10-22 19:30 Who-Did-It `e70c7970` Cutscenes: sequencer, caption layer and player on the mock (6J PR 2)
- 2026-10-22 19:43 Who-Did-It `5cbd4b67` 6M step 1: M5b nodes, held tools, glows and item icons in both styles (SPRITES 12, A95)
- 2026-10-22 19:52 Who-Did-It `34d3b3e9` Cutscenes: the five death cutscenes, mock kill, e2e handoff spec and GDD lines (6J PR 3)

## Neighbours in the same group

- Previous: Game features and admin tools planning (2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md)
- Next: Make onubNight's wire assertions wait for the 422 (2026-10-22_make-onubnight-s-wire-assertions-wait-for-the-42_rDB2zXFW.md)

## Limits

This file is built from the session list (title, dates, origin, outcome, end-of-session summary) and from the repository history. It does not contain the conversation. Items inside the session that never reached a repository (answers given in chat, artifacts published on claude.ai, files kept on the owner's machine) are not visible here.
