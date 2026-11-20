# 9V (Opus): Studio content save and NPC lines as data

| Field | Value |
|---|---|
| Session ID | `session_014WsqL6RpXR7eaHcXWGZc9e` |
| State | Archived |
| Outcome bucket | Completed |
| Started from | Spawned by another Claude session |
| Environment | anthropic_cloud |
| Created | 2026-10-25 13:47 UTC |
| Last activity | 2026-10-25 15:13 UTC |
| Span between created and last activity | 1.4 h |
| Tags | who-did-it:round9 |
| Group | Who Did It, round 9 |
| Label in title | 9V |
| Model named in title | Opus |
| Likely repositories [inference from the title] | Who-Did-It |

## What the session itself reported

- **Last action it recorded:** #309 merged as 4f38557 after #303; Studio NPC save covers routines, quests, lore, talk; 715 server tests pass

**Part of:** Round 9 (25 Oct): world-mode design sessions and the admin Studio.

## Items named in the session's own summary

- Pull request numbers: #303, #309
- Commit hashes: 4f38557

## Items linked to this session

How items were matched: (1) by the label in the session title appearing in a commit subject; (2) by time, meaning commits and new documents dated inside the session window (created minus 10 minutes to last activity plus 45 minutes) in the repositories this session likely touched. Parallel sessions overlap in time, and commit dates in some repositories cluster on integration days, so time matches are suggestions, not proof. Session transcripts were not read.

### Matched by label (stronger evidence): 0 commits

None found.

### Documents and questionnaires added in the window: 0

None found.

### Pull requests merged in the window: 14

- 2026-10-25 Who-Did-It #296 `groot99-droid/claude/r9-studio-editor-art`
- 2026-10-25 Who-Did-It #297 `groot99-droid/claude/game-features-admin-planning-v43tvq`
- 2026-10-25 Who-Did-It #298 `groot99-droid/claude/r9-studio-editor-materials`
- 2026-10-25 Who-Did-It #301 `groot99-droid/claude/r9-studio-overview-a`
- 2026-10-25 Who-Did-It #303 `groot99-droid/claude/r9-studio-npc-server`
- 2026-10-25 Who-Did-It #299 `groot99-droid/claude/r9-studio-editor-buildings`
- 2026-10-25 Who-Did-It #305 `groot99-droid/claude/r9-studio-npc-routes-a`
- 2026-10-25 Who-Did-It #308 `groot99-droid/claude/r9-studio-npc-people-pure`
- 2026-10-25 Who-Did-It #300 `groot99-droid/claude/r9-studio-overview`
- 2026-10-25 Who-Did-It #302 `groot99-droid/claude/r9-studio-editor-movables`
- 2026-10-25 Who-Did-It #309 `groot99-droid/claude/r9-studio-npc-server-n1`
- 2026-10-25 Who-Did-It #306 `groot99-droid/claude/r9-studio-editor-rotation`
- 2026-10-25 Who-Did-It #304 `groot99-droid/claude/r9-studio-npc-routes`
- 2026-10-25 Who-Did-It #310 `groot99-droid/claude/r9-studio-npc-people`

### Other commits in the window: 22

By repository: Who-Did-It 22

- 2026-10-25 13:44 Who-Did-It `46290dc7` Studio editor: the world art follows the edited scene
- 2026-10-25 13:46 Who-Did-It `79058edc` docs(round9): Studio modes - Overview, World, Room and NPC editors (owner, 2026-10-25)
- 2026-10-25 13:48 Who-Did-It `7935b6fe` Studio editor: a material palette for the grid brush
- 2026-10-25 13:49 Who-Did-It `529bf2cf` Studio: prettier on Studio.ts
- 2026-10-25 14:02 Who-Did-It `c8c41b44` Studio editor: buildings and multi-tile props are movable, deletable and duplicable
- 2026-10-25 14:03 Who-Did-It `22441706` feat(studio): Overview mode, the zoomed-out map of a map's scenes with door links (M2)
- 2026-10-25 14:04 Who-Did-It `748fae2c` feat(studio): Overview graph, auto layout and door re-target logic (M2a)
- 2026-10-25 14:08 Who-Did-It `3814e761` N2: NPC meeting-note lines move into talk.json, unchanged; N1 wire types
- 2026-10-25 14:08 Who-Did-It `09d81da5` Studio editor: givers, nodes, spawners, gates and paths are selectable and movable
- 2026-10-25 14:15 Who-Did-It `be2c47df` Studio: NPC editor 1, routines over the world with a phase scrubber (N3)
- 2026-10-25 14:16 Who-Did-It `d3d707e0` Studio: NPC editor 1a, route geometry and routines.json edit reducers (N3a)
- 2026-10-25 14:16 Who-Did-It `4b5bb4d2` Studio editor: turn props, buildings, spawns and givers; turned art with a mirrored fallback
- 2026-10-25 14:20 Who-Did-It `0a1f390e` Studio: a mode toggle (Overview, World editor, Room editor, NPC editor) with a registry other modes plug into
- 2026-10-25 14:24 Who-Did-It `dd46e0f2` Studio: frame the NPC route in the camera and fix the panel layout
- 2026-10-25 14:26 Who-Did-It `be5c7dc2` Studio: NPC editor 2a, giver, quest NPC and talk-line edits (N4a)
- 2026-10-25 14:26 Who-Did-It `b0d25df8` Studio: NPC editor 2a, giver, quest NPC and talk-line edits (N4a)
- 2026-10-25 14:27 Who-Did-It `0b69a266` N1: generalised Studio save for the content allowlist, and the NPC-data draft
- 2026-10-25 14:32 Who-Did-It `cbd2d86d` Studio: NPC editor 2b, givers, quest NPCs and talk lines in the NPC panel (N4b)
- 2026-10-25 14:42 Who-Did-It `53190415` N1: the NPC draft takes routines and quests only; looks.json is never edited
- 2026-10-25 14:45 Who-Did-It `3e2367dd` Close the last Overview rule in studio.css after the merge
- 2026-10-25 14:46 Who-Did-It `0ecc2934` N1: a quest NPC wears the villager family only, never a card's look
- 2026-10-25 15:47 Who-Did-It `e6d84d88` Studio: Overview and NPC open through registerMode

## Neighbours in the same group

- Previous: 9U (Sonnet): Studio editor live redraw and material painting (2026-10-25_9u-sonnet-studio-editor-live-redraw-and-material_7Fpud5aa.md)
- Next: 9W (Sonnet): Studio Overview and NPC editor client (2026-10-25_9w-sonnet-studio-overview-and-npc-editor-client_YzfkEGXi.md)

## Limits

This file is built from the session list (title, dates, origin, outcome, end-of-session summary) and from the repository history. It does not contain the conversation. Items inside the session that never reached a repository (answers given in chat, artifacts published on claude.ai, files kept on the owner's machine) are not visible here.
