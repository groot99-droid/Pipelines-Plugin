# 11T: round 11 tooling (Blender CI, render locks)

| Field | Value |
|---|---|
| Session ID | `session_01M5mAcYbuG588nPE8SszT7j` |
| State | Archived |
| Outcome bucket | Completed |
| Started from | Spawned by another Claude session |
| Environment | anthropic_cloud |
| Created | 2026-11-19 17:53 UTC |
| Last activity | 2026-11-19 21:40 UTC |
| Span between created and last activity | 3.8 h |
| Tags | 11T, who-did-it:round11 |
| Group | Who Did It, round 11 |
| Label in title | 11T |
| Likely repositories [inference from the title] | Who-Did-It |

## What the session itself reported

- **Last action it recorded:** PR #577 is marked ready for review with all four CI checks green; the orchestrator merges next

**Part of:** Round 11 (29 Oct): the render pipeline and materials, styles and budgets.

## Items named in the session's own summary

- Pull request numbers: #577

## Items linked to this session

How items were matched: (1) by the label in the session title appearing in a commit subject; (2) by time, meaning commits and new documents dated inside the session window (created minus 10 minutes to last activity plus 45 minutes) in the repositories this session likely touched. Parallel sessions overlap in time, and commit dates in some repositories cluster on integration days, so time matches are suggestions, not proof. Session transcripts were not read.

### Matched by label (stronger evidence): 0 commits

None found.

### Documents and questionnaires added in the window: 6

- [document] 2026-11-19 Who-Did-It `docs/round11/handoff/prop-models.md`
- [document] 2026-11-19 Who-Did-It `docs/round11/seams.md`
- [document] 2026-11-19 Who-Did-It `docs/round11/props.md`
- [plan / contract] 2026-11-19 Who-Did-It `tools/blender/models/README.md`
- [plan / contract] 2026-11-19 Who-Did-It `assets/source/renders/README.md`
- [document] 2026-11-19 Who-Did-It `docs/round11/tiles-brief.md`

### Pull requests merged in the window: 26

- 2026-11-19 Who-Did-It #551 `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 Who-Did-It #552 `groot99-droid/claude/inspiring-cori-juqfrm`
- 2026-11-19 Who-Did-It #553 `groot99-droid/claude/elegant-archimedes-ybxzlj`
- 2026-11-19 Who-Did-It #557 `groot99-droid/claude/r11-d-h1-models`
- 2026-11-19 Who-Did-It #558 `groot99-droid/claude/r11-t-art-drop-warning`
- 2026-11-19 Who-Did-It #554 `groot99-droid/claude/r11-d-s0-three`
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

### Other commits in the window: 54

By repository: Who-Did-It 54

- 2026-11-19 17:51 Who-Did-It `809e69e0` docs: round 11 opens: the session rows, the seams and the handoff indexes
- 2026-11-19 17:54 Who-Did-It `85a82512` docs: S0, three 0.186.1 for the client's sprite world, measured and budgeted (A617)
- 2026-11-19 17:56 Who-Did-It `f1fd460c` T1: the bpy job, setup.sh and the bpy tests
- 2026-11-19 17:58 Who-Did-It `76237403` Round 11 P1: the prop list
- 2026-11-19 17:58 Who-Did-It `865252ae` T3: the 25 MB art-drop warning
- 2026-11-19 17:59 Who-Did-It `9ac09f9a` tools/blender/models: H1, the model releases' lock, fetcher and ASSETS 6.12
- 2026-11-19 17:59 Who-Did-It `a1538161` T1: eslint ignores the bpy venv
- 2026-11-19 18:02 Who-Did-It `f4c827fe` T4: render locks, the writer
- 2026-11-19 18:04 Who-Did-It `0d5bed8f` T1: setup.sh gets Python 3.13 from uv when the system python is not 3.13
- 2026-11-19 18:05 Who-Did-It `68c726bd` T5: render locks, the check
- 2026-11-19 18:17 Who-Did-It `3123bc98` Round 11 P1: the handoff is on the base now
- 2026-11-19 18:19 Who-Did-It `8abdde02` Keep the bpy GLB fixture as base64 text so the LFS pattern does not turn it into a pointer
- 2026-11-19 18:21 Who-Did-It `e8274f7a` Round 11 P1: owner answered Q-P1 to Q-P4
- 2026-11-19 18:26 Who-Did-It `17e7224e` Record the owner's CC0 answer for Meshy models (A616 Q1)
- 2026-11-19 18:45 Who-Did-It `ff96ec82` Blender lock: fail closed at take-over, close two signal gaps
- 2026-11-19 18:45 Who-Did-It `0132a27d` test(server): fix the mugFlight and manhunt flakes at their random sources
- 2026-11-19 19:07 Who-Did-It `66075aba` docs: round 11, 11R starts: its seams row and the orchestrator log
- 2026-11-19 19:10 Who-Did-It `e259a71e` test(server): the briefing test waits on the server's messages, not on wall time
- 2026-11-19 19:20 Who-Did-It `57154da7` R1a: the sprite world's scene build (world3/frame, world3/build)
- 2026-11-19 19:22 Who-Did-It `efe686f4` R1b: the sprite world draws under Phaser with ?render=sprite
- 2026-11-19 19:24 Who-Did-It `db91df87` R1c: the three chunk budget check (A618) and the static-import test
- 2026-11-19 19:43 Who-Did-It `dbde07d3` docs: round 11, 11F starts: its seams row and the orchestrator log
- 2026-11-19 19:43 Who-Did-It `0b3a870f` docs(round11): P2 tiles and wall textures brief and proposed seams row
- 2026-11-19 19:55 Who-Did-It `371776ac` test(server): queued waits on lobby commands and moves too
- 2026-11-19 19:55 Who-Did-It `2ae1601a` test(server): the hold and refusal helpers wait on the server's messages, not on wall time
- ... and 29 more (see the repository document for the full log)

## Neighbours in the same group

- Previous: 11D: round 11 decisions (Three.js, model locks) (2026-11-19_11d-round-11-decisions-three-js-model-locks_D3d3fjEo.md)
- Next: 11P: round 11 prop list (2026-11-19_11p-round-11-prop-list_sgQGbvMg.md)

## Limits

This file is built from the session list (title, dates, origin, outcome, end-of-session summary) and from the repository history. It does not contain the conversation. Items inside the session that never reached a repository (answers given in chat, artifacts published on claude.ai, files kept on the owner's machine) are not visible here.
