# Session 13: make solo_test deterministic (find the real cause first)

| Field | Value |
|---|---|
| Session ID | `session_01M5mAcXtEFAXRMEyVH2g6yi` |
| State | Archived |
| Outcome bucket | Completed |
| Started from | Spawned by another Claude session |
| Environment | anthropic_cloud |
| Created | 2026-11-11 00:55 UTC |
| Last activity | 2026-11-12 15:45 UTC |
| Span between created and last activity | 1.6 days |
| Tags | farway-tests, session-13 |
| Group | Who Did It, numbered Session series (8 to 15 Nov) |
| Label in title | Session 13 |
| Likely repositories [inference from the title] | Who-Did-It |

## What the session itself reported

- **Last action it recorded:** All 16 other browser tests pass on main ff5bd1d (PR #21) with no failed checks; solo_test and mp_test were not rerun on that commit.

## Items named in the session's own summary

- Pull request numbers: #21
- Commit hashes: ff5bd1d

## Items linked to this session

How items were matched: (1) by the label in the session title appearing in a commit subject; (2) by time, meaning commits and new documents dated inside the session window (created minus 10 minutes to last activity plus 45 minutes) in the repositories this session likely touched. Parallel sessions overlap in time, and commit dates in some repositories cluster on integration days, so time matches are suggestions, not proof. Session transcripts were not read.

### Matched by label (stronger evidence): 0 commits

None found.

### Documents and questionnaires added in the window: 0

None found.

### Pull requests merged in the window: 5

- 2026-11-11 Who-Did-It #512 `groot99-droid/claude/story-s3-fixnote`
- 2026-11-11 Who-Did-It #514 `groot99-droid/claude/story-s3-replay`
- 2026-11-12 Who-Did-It #517 `groot99-droid/claude/story-s3-tidy`
- 2026-11-12 Who-Did-It #520 `groot99-droid/claude/story-s3-acctnote`
- 2026-11-12 Who-Did-It #522 `groot99-droid/claude/story-s3-tidy2`

### Other commits in the window: 57

By repository: Who-Did-It 57

- 2026-11-11 00:52 Who-Did-It `37b46495` story R1: retire the Medium card, Seance and Seance Chalk (A600) (#502)
- 2026-11-11 02:05 Who-Did-It `dbd42013` e2e: wait for the World before skipping the opening; npc.spec takes the Village's ejection of the Killer
- 2026-11-11 03:00 Who-Did-It `ff7eb9c4` story R2: the martyr is a shade, not a ghost (A601) (#505)
- 2026-11-11 03:30 Who-Did-It `a1212577` story R3: the Medium at the rite site, and the rite (A602) (#507)
- 2026-11-11 04:01 Who-Did-It `79ad4daf` story R4: the martyr's return, the gated due, the candidacy gone (A603) (#508)
- 2026-11-11 04:21 Who-Did-It `bbf23658` test: wait for a scene change's arriving figures as well as the leaving ones
- 2026-11-11 04:48 Who-Did-It `122c9134` story R5: the 10X Vicar's buff until dusk (A604) (#509)
- 2026-11-11 05:18 Who-Did-It `103cb6e4` story R7: the rite on the client (A605) (#510)
- 2026-11-11 05:18 Who-Did-It `800c0e3c` story R: log the #510 merge in status.md
- 2026-11-11 05:38 Who-Did-It `458608f0` story R: log the #510 merge in status.md (#511)
- 2026-11-11 21:52 Who-Did-It `59b06adf` Story S3: status, S2 honours chapterId
- 2026-11-11 21:53 Who-Did-It `ad862996` Story handoff: R's PRs merged (#502 to #511), R idle, R6 and R8 on hold
- 2026-11-11 22:06 Who-Did-It `11767e83` story I9: conversion, the Vicar's sermon at the bell, the Peaceful route recorded (A606)
- 2026-11-11 22:20 Who-Did-It `ef4f14f3` K6b: a snare-only shop visit ends at once; invariants.test.ts fixedSeeds offset 1 to 2 (owner's grant, 2026-11-11)
- 2026-11-11 22:22 Who-Did-It `fa14b508` story I9b: the sermon prompt at the bell, the conversion toasts, the Vicar's count
- 2026-11-11 22:24 Who-Did-It `0c0309ef` Story handoff: I9 on R, 60 s bell, finisher grants, S3 retargeted
- 2026-11-11 22:24 Who-Did-It `bbb5e595` Story S3: Replay sends the device's save so the server replays the chosen chapter
- 2026-11-11 22:26 Who-Did-It `0aedd911` story I9: the sermon repeats after conversion.sermonCooldownS, not once a day (owner, A606)
- 2026-11-11 22:30 Who-Did-It `c13abd7a` story I9b: the sermon prompt returns after conversion.sermonCooldownS (A606)
- 2026-11-11 22:39 Who-Did-It `097c7fb2` story I9b: A606 records the owner's answer, the listener gains once a day
- 2026-11-11 22:46 Who-Did-It `b08b9873` Story mode handoff: R's PRs merged (#502 to #511), R idle (#513)
- 2026-11-11 23:11 Who-Did-It `21ef2b3c` story I9: conversion, the Vicar's sermon at the bell, the Peaceful route recorded (A606) (#515)
- 2026-11-12 00:19 Who-Did-It `93e42a08` Story S3: tidy two status lines after the Replay fix
- 2026-11-12 00:19 Who-Did-It `f96f32c3` e2e: the lock-pick snap waits on frames, not a 5 s wall clock (CI renderer starved)
- 2026-11-12 00:49 Who-Did-It `9990a4bb` story I9: conversion, the Vicar's sermon at the bell, the Peaceful route recorded (A606) (#515)
- ... and 32 more (see the repository document for the full log)

## Neighbours in the same group

- Previous: Session 9: City v0 on Hallam Row (street, apartment, day clock) (2026-11-10_session-9-city-v0-on-hallam-row-street-apartment_gJUWCQk2.md)
- Next: Session 14: make mp_test deterministic and measure room frame cost (2026-11-12_session-14-make-mp-test-deterministic-and-measur_KuLZay2b.md)

## Limits

This file is built from the session list (title, dates, origin, outcome, end-of-session summary) and from the repository history. It does not contain the conversation. Items inside the session that never reached a repository (answers given in chat, artifacts published on claude.ai, files kept on the owner's machine) are not visible here.
