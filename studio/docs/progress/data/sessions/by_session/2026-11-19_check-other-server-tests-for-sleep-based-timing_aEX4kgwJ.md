# Check other server tests for sleep-based timing races

| Field | Value |
|---|---|
| Session ID | `session_01M5mAcWY8jd19bqaEX4kgwJ` |
| State | Active (idle) |
| Outcome bucket | Completed |
| Started from | Claude desktop app |
| Environment | anthropic_cloud |
| Created | 2026-11-19 19:16 UTC |
| Last activity | 2026-11-20 01:59 UTC |
| Span between created and last activity | 6.7 h |
| Group | Who Did It, game planning and fixes |
| Likely repositories [inference from the title] | Who-Did-It |

## What the session itself reported

- **Last action it recorded:** #580 is fully superseded by #579 on the default branch, so no rework is needed; it remains open as a draft and can be closed on your word.

## Items named in the session's own summary

- Pull request numbers: #579, #580

## Items linked to this session

How items were matched: (1) by the label in the session title appearing in a commit subject; (2) by time, meaning commits and new documents dated inside the session window (created minus 10 minutes to last activity plus 45 minutes) in the repositories this session likely touched. Parallel sessions overlap in time, and commit dates in some repositories cluster on integration days, so time matches are suggestions, not proof. Session transcripts were not read.

### Matched by label (stronger evidence): 0 commits

This session has no label in its title to match on.

### Documents and questionnaires added in the window: 1

- [document] 2026-11-19 Who-Did-It `docs/round11/tiles-brief.md`

### Pull requests merged in the window: 24

- 2026-11-19 Who-Did-It #555 `groot99-droid/claude/r11-t-bpy-job`
- 2026-11-19 Who-Did-It #561 `groot99-droid/claude/r11-d-h1-meshy-licence`
- 2026-11-19 Who-Did-It #556 `groot99-droid/claude/r11-p-prop-list`
- 2026-11-19 Who-Did-It #563 `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 Who-Did-It #562 `groot99-droid/claude/focused-cori-c2owsz`
- 2026-11-19 Who-Did-It #564 `groot99-droid/claude/inspiring-cori-juqfrm`
- 2026-11-19 Who-Did-It #568 `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 Who-Did-It #565 `groot99-droid/claude/r11-r-r1-scene`
- 2026-11-19 Who-Did-It #566 `groot99-droid/claude/r11-r-r1-render`
- 2026-11-19 Who-Did-It #559 `groot99-droid/claude/r11-t-render-lock-writer`
- 2026-11-19 Who-Did-It #567 `groot99-droid/claude/r11-r-r1-budget`
- 2026-11-19 Who-Did-It #569 `groot99-droid/claude/r11-p-p2-brief`
- 2026-11-19 Who-Did-It #560 `groot99-droid/claude/r11-t-render-lock-check`
- 2026-11-19 Who-Did-It #570 `groot99-droid/claude/r11-r-m5b-list-nudge`
- 2026-11-19 Who-Did-It #574 `groot99-droid/claude/r11-r-hitman-flake`
- 2026-11-19 Who-Did-It #573 `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 Who-Did-It #571 `groot99-droid/claude/r11-f-figure-rig`
- 2026-11-19 Who-Did-It #581 `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 Who-Did-It #576 `groot99-droid/claude/r11-p-p2b-walls`
- 2026-11-19 Who-Did-It #584 `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 Who-Did-It #575 `groot99-droid/claude/r11-p-p2a-ground`
- 2026-11-19 Who-Did-It #572 `groot99-droid/claude/gallant-goodall-k95p1k`
- 2026-11-20 Who-Did-It #577 `groot99-droid/claude/r11-t-blender-figures-step`
- 2026-11-20 Who-Did-It #579 `groot99-droid/claude/inspiring-cori-juqfrm`

### Other commits in the window: 44

By repository: Who-Did-It 44

- 2026-11-19 19:07 Who-Did-It `66075aba` docs: round 11, 11R starts: its seams row and the orchestrator log
- 2026-11-19 19:10 Who-Did-It `e259a71e` test(server): the briefing test waits on the server's messages, not on wall time
- 2026-11-19 19:20 Who-Did-It `57154da7` R1a: the sprite world's scene build (world3/frame, world3/build)
- 2026-11-19 19:22 Who-Did-It `efe686f4` R1b: the sprite world draws under Phaser with ?render=sprite
- 2026-11-19 19:24 Who-Did-It `db91df87` R1c: the three chunk budget check (A618) and the static-import test
- 2026-11-19 19:43 Who-Did-It `dbde07d3` docs: round 11, 11F starts: its seams row and the orchestrator log
- 2026-11-19 19:43 Who-Did-It `0b3a870f` docs(round11): P2 tiles and wall textures brief and proposed seams row
- 2026-11-19 19:55 Who-Did-It `371776ac` test(server): queued waits on lobby commands and moves too
- 2026-11-19 19:55 Who-Did-It `2ae1601a` test(server): the hold and refusal helpers wait on the server's messages, not on wall time
- 2026-11-19 19:59 Who-Did-It `d5121f47` Fix the 390w screens e2e: a leaning row overflows, the 3x3 square leaves view
- 2026-11-19 20:12 Who-Did-It `e221c76c` F1: the figure rig, a character GLB to 64 px figure frames
- 2026-11-19 20:27 Who-Did-It `6b4d4ce5` test(server): commands sent before a paused step are queued, not slept on
- 2026-11-19 20:31 Who-Did-It `276ef686` test(server): wait on the server's messages and the queue, not on wall time
- 2026-11-19 20:33 Who-Did-It `d333da19` docs: round 11, 11P's P2 paths in the seams and the orchestrator log
- 2026-11-19 20:33 Who-Did-It `6aae45e7` Deal the humans a turnable card in the hitman turning test
- 2026-11-19 20:35 Who-Did-It `8ab35185` test(server): direct handler calls and paused steps flush before the clients are read
- 2026-11-19 20:35 Who-Did-It `37ef0432` feat(world3): P2a ground tiles for the sprite world
- 2026-11-19 20:36 Who-Did-It `65c0470e` F1: write the figure's render lock now that T4 has merged
- 2026-11-19 20:38 Who-Did-It `06dec225` F1: a cover card is never a figure
- 2026-11-19 20:39 Who-Did-It `b24c0a3c` P2b: wall and roof textures for the sprite world
- 2026-11-19 20:42 Who-Did-It `ebff2bfc` F1: shrink a figure taller than 1.75 m to fit the 112 px cap
- 2026-11-19 20:43 Who-Did-It `74a1f085` P2b: fit the CREDITS row to the table so prettier passes
- 2026-11-19 20:43 Who-Did-It `883c2b3e` F2: the figure batch, the drop script and the figure tests (atlases to follow)
- 2026-11-19 20:43 Who-Did-It `1c4f2a8a` F2: the figure batch, the drop script and the figure tests (atlases to follow)
- 2026-11-19 20:47 Who-Did-It `7754c763` test(server): the same races under other names: wait(), setTimeout and send's own sleep
- ... and 19 more (see the repository document for the full log)

## Neighbours in the same group

- Previous: Flake fix for manhunt test (2026-11-19_flake-fix-for-manhunt-test_kGFpNChT.md)
- Next: none

## Limits

This file is built from the session list (title, dates, origin, outcome, end-of-session summary) and from the repository history. It does not contain the conversation. Items inside the session that never reached a repository (answers given in chat, artifacts published on claude.ai, files kept on the owner's machine) are not visible here.
