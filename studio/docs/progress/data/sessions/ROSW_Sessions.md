# ROSW Sessions: every Claude Code session, active and archived

Generated 20 November 2026. 257 sessions, from 06 March 2026 to 20 November 2026: 239 archived and 18 active. Each session also has its own Markdown file in `by_session/` (file names are in the tables below).

## 1. Method and limits

- **Source.** The Claude Code session list for the owner's account (title, ID, state, outcome, origin, created and last-activity times, tags, and the end-of-session summary where one exists), plus the git history of the eleven repositories.
- **Not included.** Session transcripts, messages, tool calls, and anything the owner did in a chat without a repository change. Sessions run in the claude.ai chat product are not in this list.
- **Items.** For each session the file lists commits matched by the label in the title, documents and questionnaires added during its window, pull requests merged and other commits. Matching by time is approximate because many sessions ran in parallel and some repositories show commits dated on integration days. Who-Did-It's clone has no commits dated before 29 October 2026, although its decision log starts on 9 October, so sessions from 10 to 28 October show few or no commits there.
- **States.** "Active" is any session the list shows as idle or running. "Archived" is everything else. Outcome buckets (completed, failed, blocked, review ready, working) are the list's own.
- **Times** are UTC.

## 2. Totals

| Measure | Count |
|---|---|
| All sessions | 257 |
| Archived | 239 |
| Active (idle or running) | 18 |
| Outcome: Completed | 233 |
| Outcome: Failed | 13 |
| Outcome: Review ready | 6 |
| Outcome: Blocked | 3 |
| Outcome: Working | 2 |

| Started from | Sessions |
|---|---|
| Spawned by another Claude session | 163 |
| Claude desktop app | 52 |
| Claude on iOS (phone) | 21 |
| Claude Code CLI (remote control on the owner's computer) | 21 |

| Month | Sessions |
|---|---|
| 2026-03 | 4 |
| 2026-08 | 8 |
| 2026-09 | 23 |
| 2026-10 | 165 |
| 2026-11 | 57 |

| Busiest days | Sessions |
|---|---|
| 2026-10-23 | 30 |
| 2026-10-22 | 19 |
| 2026-10-16 | 15 |
| 2026-10-18 | 15 |
| 2026-10-24 | 15 |
| 2026-10-10 | 13 |
| 2026-10-29 | 13 |
| 2026-10-30 | 11 |
| 2026-11-19 | 11 |
| 2026-10-25 | 10 |

## 3. Active sessions (18)

- **Game scenes and level connections** (Idle, last activity 2026-11-20 01:33 UTC, file `2026-11-04_game-scenes-and-level-connections_nHeznJEZ.md`). 
- **Story mode** (Idle, last activity 2026-11-20 01:51 UTC, file `2026-11-06_story-mode_oZ8CZDFp.md`). 
- **Session 2: gate return fix, links from the manifest** (Idle, last activity 2026-11-19 20:03 UTC, file `2026-11-08_session-2-gate-return-fix-links-from-the-manifes_WrLpinA4.md`). Slice 2 is in draft PR #55 at b081930; CI finished with no failures. Slice 3 is not started, and the agent asked whether to begin it.
- **Session 4: modes and parties (rooms by mode, party key, size 10)** (Idle, last activity 2026-11-10 21:32 UTC, file `2026-11-10_session-4-modes-and-parties-rooms-by-mode-party_S2g8sQiT.md`). 
- **Blender tools setup** (Idle, last activity 2026-11-20 02:11 UTC, file `2026-11-10_blender-tools-setup_HwQQXcDr.md`). Work paused at your request and the keep-awake helper is stopped; say "continue" to resume.
- **Creative writing to game adaptation** (Idle, last activity 2026-11-20 02:07 UTC, file `2026-11-12_creative-writing-to-game-adaptation_rkcmWq1a.md`). 
- **Session 18: rules for the arsenal, consumables, dealer items and food** (Idle, last activity 2026-11-20 00:45 UTC, file `2026-11-15_session-18-rules-for-the-arsenal-consumables-dea_dfok53Yk.md`). PR #62 was marked ready and merged
- **ROSW progress report part 3** (Running, last activity 2026-11-20 02:36 UTC, file `2026-11-17_rosw-progress-report-part-3_s3WHs2uN.md`). 
- **Documentation audit plan** (Idle, last activity 2026-11-20 01:18 UTC, file `2026-11-17_documentation-audit-plan_GJBqs7XT.md`). 
- **11P: round 11 prop list** (Idle, last activity 2026-11-19 23:59 UTC, file `2026-11-19_11p-round-11-prop-list_sgQGbvMg.md`). 
- **Round 11 · 11R The renderer** (Idle, last activity 2026-11-19 22:41 UTC, file `2026-11-19_round-11-11r-the-renderer_hjDrA2Hw.md`). 
- **Check other server tests for sleep-based timing races** (Idle, last activity 2026-11-20 01:59 UTC, file `2026-11-19_check-other-server-tests-for-sleep-based-timing_aEX4kgwJ.md`). #580 is fully superseded by #579 on the default branch, so no rework is needed; it remains open as a draft and can be closed on your word.
- **Round 11 · 11F Figure sprites** (Idle, last activity 2026-11-20 02:26 UTC, file `2026-11-19_round-11-11f-figure-sprites_RXNaUHaC.md`). PR #578 (F2a) is green and ready for review; #582 and #586 stay drafts until gate G. No further check-ins scheduled.
- **Higgsfield Assets release upload** (Idle, last activity 2026-11-20 00:40 UTC, file `2026-11-19_higgsfield-assets-release-upload_NkVwWYfa.md`). 
- **Rhino documentary short film** (Idle, last activity 2026-11-20 01:21 UTC, file `2026-11-19_rhino-documentary-short-film_qYQAuiN8.md`). PR #39 merged to main with the video-editor frame-cut fix and films/she-does-not-run; release v5 is public; 6 CI jobs still running on main
- **AI MCP tool for pipeline applications** (Idle, last activity 2026-11-20 01:02 UTC, file `2026-11-19_ai-mcp-tool-for-pipeline-applications_ZVDTwEPL.md`). Delivered vast plugin setup steps to the local session: load plugin, check SSH key, run /vast-status, then a cheap 12-minute test rental
- **Public SSH key location** (Idle, last activity 2026-11-20 01:46 UTC, file `2026-11-20_public-ssh-key-location_F1kW8xwZ.md`). 
- **Vast GPU: Dr. Tox build, 1 hour** (Running, last activity 2026-11-20 02:21 UTC, file `2026-11-20_vast-gpu-dr-tox-build-1-hour_rj85qwRk.md`). 

## 4. Sessions that did not complete

- 2026-09-28 Museum walkthrough refinement: **Failed** (Archived) `2026-09-28_museum-walkthrough-refinement_oAJPvD6J.md`
- 2026-09-30 Room refinement and video animations: **Failed** (Archived) `2026-09-30_room-refinement-and-video-animations_QKnNRnHB.md`
- 2026-10-01 GitHub Pages file not found: **Failed** (Archived) `2026-10-01_github-pages-file-not-found_CSTG56UG.md`
- 2026-10-03 Game scene polish and mechanics: **Failed** (Archived) `2026-10-03_game-scene-polish-and-mechanics_oXh7y2me.md`
- 2026-10-18 WDI 5E: ONUB v2 bots, NPC brains, e2e and soak (Sonnet): **Failed** (Archived) `2026-10-18_wdi-5e-onub-v2-bots-npc-brains-e2e-and-soak-sonn_eAxjQMH2.md`
- 2026-10-18 WDI 5H: NPC routines and fixes (Sonnet): **Failed** (Archived) `2026-10-18_wdi-5h-npc-routines-and-fixes-sonnet_V4W1hNxi.md`
- 2026-10-23 7M: every mini-game and main-mode task assignment: **Failed** (Archived) `2026-10-23_7m-every-mini-game-and-main-mode-task-assignment_1sdsHATT.md`
- 2026-10-23 8A: Bodies (health, stamina, effects, fists): **Failed** (Archived) `2026-10-23_8a-bodies-health-stamina-effects-fists_VEobzSXD.md`
- 2026-10-23 8E: Moods, townsfolk, mugging: **Failed** (Archived) `2026-10-23_8e-moods-townsfolk-mugging_A71DZxk2.md`
- 2026-10-23 8F: Characters (redesign, scale, clips): **Failed** (Archived) `2026-10-23_8f-characters-redesign-scale-clips_a5u3HL3T.md`
- 2026-10-23 8I: HD art style: **Failed** (Archived) `2026-10-23_8i-hd-art-style_FKkSwuTW.md`
- 2026-10-23 8N Icons (Who Did It round 8): **Failed** (Archived) `2026-10-23_8n-icons-who-did-it-round-8_jMT2Tmma.md`
- 2026-10-24 8V: Canon (the lore into the game's names and text): **Failed** (Archived) `2026-10-24_8v-canon-the-lore-into-the-game-s-names-and-text_ovC7362T.md`
- 2026-11-04 Game scenes and level connections: **Review ready** (Idle) `2026-11-04_game-scenes-and-level-connections_nHeznJEZ.md`
- 2026-11-06 Story mode: **Review ready** (Idle) `2026-11-06_story-mode_oZ8CZDFp.md`
- 2026-11-10 Session 4: modes and parties (rooms by mode, party key, size 10): **Review ready** (Idle) `2026-11-10_session-4-modes-and-parties-rooms-by-mode-party_S2g8sQiT.md`
- 2026-11-12 Creative writing to game adaptation: **Review ready** (Idle) `2026-11-12_creative-writing-to-game-adaptation_rkcmWq1a.md`
- 2026-11-17 ROSW progress report part 3: **Working** (Running) `2026-11-17_rosw-progress-report-part-3_s3WHs2uN.md`
- 2026-11-17 Documentation audit plan: **Review ready** (Idle) `2026-11-17_documentation-audit-plan_GJBqs7XT.md`
- 2026-11-19 11P: round 11 prop list: **Blocked** (Idle) `2026-11-19_11p-round-11-prop-list_sgQGbvMg.md`
- 2026-11-19 Round 11 · 11R The renderer: **Review ready** (Idle) `2026-11-19_round-11-11r-the-renderer_hjDrA2Hw.md`
- 2026-11-19 Higgsfield Assets release upload: **Blocked** (Idle) `2026-11-19_higgsfield-assets-release-upload_NkVwWYfa.md`
- 2026-11-20 Public SSH key location: **Blocked** (Idle) `2026-11-20_public-ssh-key-location_F1kW8xwZ.md`
- 2026-11-20 Vast GPU: Dr. Tox build, 1 hour: **Working** (Running) `2026-11-20_vast-gpu-dr-tox-build-1-hour_rj85qwRk.md`

## 5. Sessions by group

### Early builds (March) (4 sessions, 2026-03-06 to 2026-03-21)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-03-06 | Set up Claude code agents locally | Archived | Completed | Claude on iOS |  | `2026-03-06_set-up-claude-code-agents-locally_qHmTWpcn.md` |
| 2026-03-07 | Build Procreate brush creation and editing tools | Archived | Completed | Claude on iOS |  | `2026-03-07_build-procreate-brush-creation-and-editing-tools_ZXTY7kzA.md` |
| 2026-03-07 | Build SSCC.inc fiber optics company website | Archived | Completed | Claude on iOS |  | `2026-03-07_build-sscc-inc-fiber-optics-company-website_KRuT6dhz.md` |
| 2026-03-21 | Procreate Brush Designer Web Application | Archived | Completed | Claude on iOS |  | `2026-03-21_procreate-brush-designer-web-application_GeMh6m18.md` |

### Knowledge vaults, Creative-Headquarters and the studio (14 sessions, 2026-08-22 to 2026-10-01)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-08-22 | Repo strengths and improvements | Archived | Completed | Claude on iOS |  | `2026-08-22_repo-strengths-and-improvements_iXGxvBZV.md` |
| 2026-08-27 | Unzip and add files | Archived | Completed | Claude on iOS |  | `2026-08-27_unzip-and-add-files_kh9TkLUS.md` |
| 2026-08-27 | Creative-Writing MD migration gap analysis | Archived | Completed | Claude desktop app |  | `2026-08-27_creative-writing-md-migration-gap-analysis_yiPByf9F.md` |
| 2026-08-27 | Obsidian and Ollama integration | Archived | Completed | Claude desktop app |  | `2026-08-27_obsidian-and-ollama-integration_5iRqVizC.md` |
| 2026-08-31 | HTML and navigation JavaScript | Archived | Completed | Claude Code CLI |  | `2026-08-31_html-and-navigation-javascript_4FuQTz9h.md` |
| 2026-08-31 | Ollama library HTML pages | Archived | Completed | Claude Code CLI |  | `2026-08-31_ollama-library-html-pages_XcZfRPCV.md` |
| 2026-09-01 | Taskbar shortcut for application | Archived | Completed | Claude Code CLI |  | `2026-09-01_taskbar-shortcut-for-application_6E3qm42c.md` |
| 2026-09-01 | Skill file assessment | Archived | Completed | Claude Code CLI |  | `2026-09-01_skill-file-assessment_8Tohf9Nn.md` |
| 2026-09-03 | Application remake technical review | Archived | Completed | Claude Code CLI |  | `2026-09-03_application-remake-technical-review_jejCHha1.md` |
| 2026-09-14 | Folder checkout | Archived | Completed | Claude Code CLI |  | `2026-09-14_folder-checkout_y1oQ11Fo.md` |
| 2026-09-14 | elijahs-pc-groovy-wozniak | Archived | Completed | Claude Code CLI |  | `2026-09-14_elijahs-pc-groovy-wozniak_qonf7dEr.md` |
| 2026-09-30 | Creative-Headquarters migration plan | Archived | Completed | Claude desktop app |  | `2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md` |
| 2026-10-01 | Library explore page | Archived | Completed | Claude on iOS | Site ready at https://groot99-droid.github.io/Pipelines-Plugin/ (museum + library + docs) once Pages source switched to GitHub Actions | `2026-10-01_library-explore-page_fk3FxMyu.md` |
| 2026-10-01 | Creative headquarters deletion | Archived | Completed | Claude on iOS | Creative HQ safe to delete after: (1) brush-designer to studio/hub/brush/, (2) ui-ux-intelligence-integration.md to vault, (3) domain libraries backed up | `2026-10-01_creative-headquarters-deletion_xYjv4W23.md` |

### The Intern, Right Door and early games (8 sessions, 2026-08-24 to 2026-10-03)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-08-24 | Interactive loading screen sequence | Archived | Completed | Claude on iOS |  | `2026-08-24_interactive-loading-screen-sequence_HRU551Nf.md` |
| 2026-09-14 | Mini games plans | Archived | Completed | Claude Code CLI |  | `2026-09-14_mini-games-plans_nzMrSeeR.md` |
| 2026-09-30 | Game bugs and scene revisions | Archived | Completed | Claude desktop app | Third option (WALK THE ROOM) implemented across all S1 scenes; procedural rooms with first-person controls; PR #2 merged to main | `2026-09-30_game-bugs-and-scene-revisions_fAgmfSDY.md` |
| 2026-09-30 | Games choice logic and video playback | Archived | Completed | Claude desktop app | Fixed renderer race (videos stall) and transition flips (wrong choice). PR #3 merged to main. Manual QA: verify STAY STANDING to RUN join at 3.04s in browser. | `2026-09-30_games-choice-logic-and-video-playback_gvjKvyA7.md` |
| 2026-09-30 | Hold to run video loop bug | Archived | Completed | Claude desktop app | PR #4 merged; identified hold-to-run video loop, low-quality 3D rooms, post-garage connection drop as separate issues for triage | `2026-09-30_hold-to-run-video-loop-bug_e2Y2HCzL.md` |
| 2026-09-30 | Room refinement and video animations | Archived | Failed | Claude desktop app |  | `2026-09-30_room-refinement-and-video-animations_QKnNRnHB.md` |
| 2026-10-03 | Game scene polish and mechanics | Archived | Failed | Claude desktop app |  | `2026-10-03_game-scene-polish-and-mechanics_oXh7y2me.md` |
| 2026-10-03 | Interactive 3D scenes and room-specific items | Archived | Completed | Claude desktop app | PR #11 merged: mini games and pile cleanup now on main in dining, flooded, grocery | `2026-10-03_interactive-3d-scenes-and-room-specific-items_UTxuzKCA.md` |

### Strategy-Planner (3 sessions, 2026-08-31 to 2026-10-01)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-08-31 | Leader Markdown documentation | Archived | Completed | Claude desktop app |  | `2026-08-31_leader-markdown-documentation_BS6SFjbR.md` |
| 2026-10-01 | Civilization profiles interface redesign | Archived | Completed | Claude desktop app | PR merged and subscription closed | `2026-10-01_civilization-profiles-interface-redesign_w6YtsTyR.md` |
| 2026-10-01 | Leader-specific strategy guides | Archived | Completed | Claude on iOS | PR #2 merged; 551 plan-review notes in leadership-focus/PLAN-REVIEW-NOTES.md | `2026-10-01_leader-specific-strategy-guides_MoTURNRu.md` |

### Blender, Higgsfield and 3D tooling (7 sessions, 2026-09-16 to 2026-11-19)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-09-16 | Blender render | Archived | Completed | Claude desktop app | 16 linked tile duplicates in 4x4 grid, render_grid.png + scene_grid.blend | `2026-09-16_blender-render_j7UoMsWu.md` |
| 2026-10-10 | Gemini-Blender API integration | Archived | Completed | Claude desktop app |  | `2026-10-10_gemini-blender-api-integration_jz27C5sH.md` |
| 2026-10-10 | Blender skills plugin | Archived | Completed | Claude desktop app | PR #9 merged to main. Install with /plugin marketplace add groot99-droid/Pipelines-Plugin, then /plugin install blender@rosw | `2026-10-10_blender-skills-plugin_hiZKStdx.md` |
| 2026-10-10 | Re-render calibration sheet with ramp fix | Archived | Completed | Claude desktop app | Merged Who-Did-It PR #6 (0.30/0.70 ramp stops, re-rendered calibration sheet); DECISIONS.md row still needed. | `2026-10-10_re-render-calibration-sheet-with-ramp-fix_TSu8a5sD.md` |
| 2026-10-30 | Backrooms game level Blender blockout | Archived | Completed | Claude Code CLI | Ceilings closed on every level, stair doors show the hallway without a walkable passage, and 237 duplicate props removed on B1/L1/L2; all 8 doors tested. | `2026-10-30_backrooms-game-level-blender-blockout_x5infvvw.md` |
| 2026-11-10 | Blender tools setup | Active | Completed | Claude Code CLI | Work paused at your request and the keep-awake helper is stopped; say "continue" to resume. | `2026-11-10_blender-tools-setup_HwQQXcDr.md` |
| 2026-11-19 | Higgsfield Assets release upload | Active | Blocked | Claude Code CLI |  | `2026-11-19_higgsfield-assets-release-upload_NkVwWYfa.md` |

### Earth_Worldbuild and Art-Talk (4 sessions, 2026-09-25 to 2026-09-29)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-09-25 | Artist timeline design | Archived | Completed | Claude desktop app | Artist timeline with 5+ artworks per artist, RAG index built and deployed on main | `2026-09-25_artist-timeline-design_wYzjsLo1.md` |
| 2026-09-26 | Broadening artist scope | Archived | Completed | Claude desktop app | PR #2 merged; Art-Talk now covers architecture, design, film, literature with 53 profiles and 299 works | `2026-09-26_broadening-artist-scope_hY4eLjjX.md` |
| 2026-09-28 | Handoff checklist review | Archived | Completed | Claude desktop app | merge event confirmed; handoff work complete and merged | `2026-09-28_handoff-checklist-review_iLRULoWN.md` |
| 2026-09-29 | Bluetooth Xbox controller museum navigation | Archived | Completed | Claude desktop app | Xbox controller movement wired in; merged to main, Pages deploying | `2026-09-29_bluetooth-xbox-controller-museum-navigation_gdgftZM2.md` |

### Other (4 sessions, 2026-09-26 to 2026-11-17)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-09-26 | HTML redesign with responsive design | Archived | Completed | Claude desktop app | HTML redesign live on main with controlled palette, user features, responsive navigation, full phone/desktop compatibility | `2026-09-26_html-redesign-with-responsive-design_TyrVwvJb.md` |
| 2026-09-28 | Museum walkthrough refinement | Archived | Failed | Claude desktop app |  | `2026-09-28_museum-walkthrough-refinement_oAJPvD6J.md` |
| 2026-10-09 | Import HiggsField assets to AI library | Archived | Completed | Claude desktop app | Higgsfield library merged to main via PR #7; browse it locally with http.server on studio/library. | `2026-10-09_import-higgsfield-assets-to-ai-library_HrHQAvdx.md` |
| 2026-11-17 | ROSW progress report part 3 | Active | Working | Claude on iOS |  | `2026-11-17_rosw-progress-report-part-3_s3WHs2uN.md` |

### GitHub Pages and the 404 problem (6 sessions, 2026-09-28 to 2026-10-23)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-09-28 | 404 error investigation | Archived | Completed | Claude desktop app |  | `2026-09-28_404-error-investigation_CFr8mnY3.md` |
| 2026-09-30 | 404 error on site run | Archived | Completed | Claude desktop app | PR merged; configure Pages: Deploy from branch (main, root), then check the Pages URL | `2026-09-30_404-error-on-site-run_sBiE9JAj.md` |
| 2026-10-01 | GitHub Pages file not found | Archived | Failed | Claude on iOS |  | `2026-10-01_github-pages-file-not-found_CSTG56UG.md` |
| 2026-10-02 | GitHub Pages build error | Archived | Completed | Claude on iOS |  | `2026-10-02_github-pages-build-error_9JpktRqh.md` |
| 2026-10-02 | 404 error fix options | Archived | Completed | Claude on iOS | Pages source is set to Deploy from a branch; GitHub's Jekyll build overwrites the workflow deploy. Change to GitHub Actions in Settings > Pages, then re-run the | `2026-10-02_404-error-fix-options_3NYm8nnX.md` |
| 2026-10-23 | ROSW cleanup: Pages workflow failures, open PRs, stale branches | Archived | Completed | Spawned by another Claude session | PR #15 merged per user's 'merge it' request | `2026-10-23_rosw-cleanup-pages-workflow-failures-open-prs-st_DD9ThHLv.md` |

### Who Did It, round 3 (5 sessions, 2026-09-28 to 2026-10-29)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-09-28 | 3D museum walkthrough | Archived | Completed | Claude desktop app | PR #5 merged and cleaned up; all queued work complete | `2026-09-28_3d-museum-walkthrough_wE6mBqwr.md` |
| 2026-09-30 | 3D dining room scene with mobile optimization | Archived | Completed | Claude desktop app |  | `2026-09-30_3d-dining-room-scene-with-mobile-optimization_435FS5Rs.md` |
| 2026-09-30 | 3D scenes from creative writing vault | Archived | Completed | Claude on iOS | 10 studio notes committed to studio/vault/writing-museum/; PR #2 merged to main with CI green | `2026-09-30_3d-scenes-from-creative-writing-vault_ZKXLhErU.md` |
| 2026-10-01 | 3D game environment with Highfield scenes | Archived | Completed | Claude desktop app | PR #5 (3D build, Higgsfield scene-builder, Blender renders) merged to main | `2026-10-01_3d-game-environment-with-highfield-scenes_rY9Pqttg.md` |
| 2026-10-29 | 3D asset production pipeline | Archived | Completed | Claude desktop app | PR #19 in groot99-droid/Pipelines-Plugin merged; nothing further pending | `2026-10-29_3d-asset-production-pipeline_9jLDDV7q.md` |

### Who Did It, game planning and fixes (18 sessions, 2026-10-09 to 2026-11-19)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-09 | Who Did It multiplayer game plan | Archived | Completed | Claude desktop app | Playable now at groot99-droid.github.io/Who-Did-It; hard-refresh and create a new party. Main mode needs 4+ players. | `2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md` |
| 2026-10-21 | Game features and admin tools planning | Archived | Completed | Claude on iOS |  | `2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md` |
| 2026-10-22 | Make the R18 NPC determinism test robust to real clock ticks | Archived | Completed | Claude desktop app | PR #50 merged into claude/zen-turing-m1jnw0: standard party tick timeline fixed from lobby, R18 compares start tick, sim untouched | `2026-10-22_make-the-r18-npc-determinism-test-robust-to-real_guQLzART.md` |
| 2026-10-22 | Make onubNight's wire assertions wait for the 422 | Archived | Completed | Claude desktop app | Wire-timing fix merged as PR #62: every errorsOf assertion in onubNight.test.ts now waits for the error count. Original failure was not reproduced. | `2026-10-22_make-onubnight-s-wire-assertions-wait-for-the-42_rDB2zXFW.md` |
| 2026-10-22 | Make the quick-mode tests wait for wire replies | Archived | Completed | Claude desktop app | PR #64 (groot99-droid/Who-Did-It) at 654dda2; CI pending, orchestrator merges when green | `2026-10-22_make-the-quick-mode-tests-wait-for-wire-replies_jk3w756G.md` |
| 2026-10-23 | Railway connection setup | Archived | Completed | Claude desktop app |  | `2026-10-23_railway-connection-setup_gzA46giv.md` |
| 2026-10-23 | Who Did It narrative worldbuilding | Archived | Completed | Claude desktop app | Lore integration delegated to 8V Canon under decision A201 (Who-Did-It PR #220); 8V will write docs/round8/canon.md and send new mechanics for sign-off. | `2026-10-23_who-did-it-narrative-worldbuilding_sLCiiWHd.md` |
| 2026-10-23 | Who Did It UDGT teardown | Archived | Completed | Claude desktop app |  | `2026-10-23_who-did-it-udgt-teardown_vc5Z1F2F.md` |
| 2026-10-24 | Fix two intermittent test failures | Archived | Completed | Claude desktop app | Three PRs (#260, #261, #263) pass CI with no conflicts and await reviewers; check-ins stopped. | `2026-10-24_fix-two-intermittent-test-failures_LBErtX7U.md` |
| 2026-11-06 | Local gaming chat application | Archived | Completed | Claude Code CLI |  | `2026-11-06_local-gaming-chat-application_zChTDnuG.md` |
| 2026-11-07 | Player accounts: plan first | Archived | Completed | Spawned by another Claude session | Player-accounts plan opened as draft docs PR #472; CI and Railway preview green, not merged. | `2026-11-07_player-accounts-plan-first_WM1R6aso.md` |
| 2026-11-12 | Creative writing to game adaptation | Active | Review ready | Claude desktop app |  | `2026-11-12_creative-writing-to-game-adaptation_rkcmWq1a.md` |
| 2026-11-12 | Fix timing races in tools/mp_test.mjs | Archived | Completed | Claude desktop app |  | `2026-11-12_fix-timing-races-in-tools-mp-test-mjs_ZwLy8n6S.md` |
| 2026-11-15 | Game chat download and setup | Archived | Completed | Claude Code CLI | Installer works on this PC (2.1.0 tested, 2.2.0 released). Phone version is a web page at https://<pc-ip>:7778; phone mic/audio still untested. | `2026-11-15_game-chat-download-and-setup_49fW3EFg.md` |
| 2026-11-16 | Fix timing-dependent waits in server tests | Archived | Completed | Claude desktop app |  | `2026-11-16_fix-timing-dependent-waits-in-server-tests_6njEoAap.md` |
| 2026-11-19 | Fix two flaky server tests (mugFlight, manhunt) | Archived | Completed | Claude desktop app |  | `2026-11-19_fix-two-flaky-server-tests-mugflight-manhunt_e4njLyha.md` |
| 2026-11-19 | Flake fix for manhunt test | Archived | Completed | Claude Code CLI | Branch claude/focused-cori-c2owsz pushed (0132a27d) with manhunt and mugFlight tests; open draft PR against claude/zen-turing-m1jnw0 | `2026-11-19_flake-fix-for-manhunt-test_kGFpNChT.md` |
| 2026-11-19 | Check other server tests for sleep-based timing races | Active | Completed | Claude desktop app | #580 is fully superseded by #579 on the default branch, so no rework is needed; it remains open as a draft and can be closed on your word. | `2026-11-19_check-other-server-tests-for-sleep-based-timing_aEX4kgwJ.md` |

### Who Did It, rounds 1 to 4 (WDI A to Y) (25 sessions, 2026-10-10 to 2026-10-16)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-10 | WDI A: server and shared (Sonnet) | Archived | Completed | Spawned by another Claude session |  | `2026-10-10_wdi-a-server-and-shared-sonnet_35fr1sDn.md` |
| 2026-10-10 | WDI B: client and Pages (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #2 opened for the client session; waiting on CI or review events, nothing for the user to do | `2026-10-10_wdi-b-client-and-pages-sonnet_3xczv45i.md` |
| 2026-10-10 | WDI C: content data and rules JSON (Opus) | Archived | Completed | Spawned by another Claude session |  | `2026-10-10_wdi-c-content-data-and-rules-json-opus_PNGDvr2H.md` |
| 2026-10-10 | WDI D: art direction and asset pipeline (Opus) | Archived | Completed | Spawned by another Claude session |  | `2026-10-10_wdi-d-art-direction-and-asset-pipeline-opus_4PUsGq3H.md` |
| 2026-10-10 | WDI E: decide the 15 open questions (Opus, plan mode) | Archived | Completed | Spawned by another Claude session | All 15 decisions in docs/DECISIONS merged via PR #5; Q14 calibration re-render left as a suggested task card. | `2026-10-10_wdi-e-decide-the-15-open-questions-opus-plan-mod_zB8M67nc.md` |
| 2026-10-10 | WDI F: M1 finish, shared protocol and Start deals roles (Sonnet) | Archived | Completed | Spawned by another Claude session | M1 merged via PR #9 on 2026-10-15; the agent has stopped watching it. Individual CI checks were not opened. | `2026-10-10_wdi-f-m1-finish-shared-protocol-and-start-deals_2QDQKJDy.md` |
| 2026-10-10 | WDI G: M2 movement, scene sync and the first house (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #8 merged into claude/zen-turing-m1jnw0; 30-min soak clean (229 portal crossings, 0 leaks); Android fps and 2-4 person playtest still open | `2026-10-10_wdi-g-m2-movement-scene-sync-and-the-first-house_w7ymx3Ab.md` |
| 2026-10-10 | WDI H: villager character art through the render rig (Opus) | Archived | Completed | Spawned by another Claude session | PR #10 merged into claude/zen-turing-m1jnw0 with villager art and tooling fixes | `2026-10-10_wdi-h-villager-character-art-through-the-render_DwoyNhwh.md` |
| 2026-10-10 | WDI I: UI design system, role cards, lobby and HUD (Fable) | Archived | Completed | Spawned by another Claude session | PR #11 merged into claude/zen-turing-m1jnw0; docs/UI.md, theme tokens, components, mockups, and style.json extension are on the base branch | `2026-10-10_wdi-i-ui-design-system-role-cards-lobby-and-hud_jjiZozRk.md` |
| 2026-10-10 | WDI J: who-did-it studio project in the ROSW repo (Sonnet) | Archived | Completed | Spawned by another Claude session | Who-Did-It #7 merged; ROSW #10 open as draft, not yet reviewed or merged | `2026-10-10_wdi-j-who-did-it-studio-project-in-the-rosw-repo_JzHw9dat.md` |
| 2026-10-16 | WDI K: M3 match flow, meetings, votes, win (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #16 merged, completing Round 3 Session K (match flow server); details in docs/SESSIONS.md and DECISIONS A31 | `2026-10-16_wdi-k-m3-match-flow-meetings-votes-win-sonnet_xDYzVTkf.md` |
| 2026-10-16 | WDI L: M3 kill, bodies, clues, Notebook (Sonnet) | Archived | Completed | Spawned by another Claude session | Session L merged as PR #15 (kill, bodies, clues, Collect, report, bell, bandage, ghosts); M4 pieces left out. | `2026-10-16_wdi-l-m3-kill-bodies-clues-notebook-sonnet_qscgm6uS.md` |
| 2026-10-16 | WDI M: M3 meeting, game over, chat, theme screens (Sonnet) | Archived | Completed | Spawned by another Claude session | Round 3 Session M merged as PR #17 on claude/zen-turing-m1jnw0; integration notes in docs/SESSIONS.md | `2026-10-16_wdi-m-m3-meeting-game-over-chat-theme-screens-so_MnTboRjB.md` |
| 2026-10-16 | WDI N: M3 world actions, clues, HUD theme (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #18 merged; round 3 World actions work is in claude/zen-turing-m1jnw0, session auto-unsubscribed | `2026-10-16_wdi-n-m3-world-actions-clues-hud-theme-sonnet_raEw1Nfr.md` |
| 2026-10-16 | WDI O: M3 bots, match e2e, soak (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #13 merged with match.spec.ts, the bot soak and grid reach tests; match e2e runs at integration once K-N merge | `2026-10-16_wdi-o-m3-bots-match-e2e-soak-sonnet_qyWQF69y.md` |
| 2026-10-16 | WDI P: M3 art, props, clues, VFX, body sprite (Opus) | Archived | Completed | Spawned by another Claude session | PR #12 merged: villager masters, clues/props/vfx atlases, body sheet. Copy villager.blend and villager.glb from assets/external/villager/ to your laptop's ROSW  | `2026-10-16_wdi-p-m3-art-props-clues-vfx-body-sprite-opus_tYimDxQw.md` |
| 2026-10-16 | WDI Q: M3 playtest kit, audio, copy deck (Opus) | Archived | Completed | Spawned by another Claude session | PR #14 merged to default branch; M3 playtest kit in place, with user setup still pending (Railway, VITE_SERVER_URL, Pages, form, scorecard) | `2026-10-16_wdi-q-m3-playtest-kit-audio-copy-deck-opus_GDhqLxqB.md` |
| 2026-10-16 | WDI R: quick mode server (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #25 merged: quick-mode server (M3b, Session R) landed on claude/zen-turing-m1jnw0; round 4 log in docs/SESSIONS.md | `2026-10-16_wdi-r-quick-mode-server-sonnet_voJupQM5.md` |
| 2026-10-16 | WDI S: NPC fill server (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #22 (M3c NPC fill, server) merged; WDI_SLOW tests never run and two R-dependent tests still unwritten. | `2026-10-16_wdi-s-npc-fill-server-sonnet_PSuYffwM.md` |
| 2026-10-16 | WDI T: quick mode client world (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #23 (quick mode, client world) merged; real-server check and UI.md 14.12 copy remain in docs/SESSIONS.md | `2026-10-16_wdi-t-quick-mode-client-world-sonnet_LQm7XsG5.md` |
| 2026-10-16 | WDI U: quick mode meeting and end (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #21 merged into claude/zen-turing-m1jnw0; server paths and swap log still need checking at round integration | `2026-10-16_wdi-u-quick-mode-meeting-and-end-sonnet_ZVQjHvwA.md` |
| 2026-10-16 | WDI V: lobby, settings, network edge (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #19 merged into claude/zen-turing-m1jnw0; Session V brief complete, with the round 4 log in docs/SESSIONS.md | `2026-10-16_wdi-v-lobby-settings-network-edge-sonnet_GpkumYmd.md` |
| 2026-10-16 | WDI W: bots, e2e, soak, CI (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #24 merged into claude/zen-turing-m1jnw0; quick-mode onub/npc runs and 30-min soak remain open for the orchestrator | `2026-10-16_wdi-w-bots-e2e-soak-ci-sonnet_aMXtY7zi.md` |
| 2026-10-16 | WDI X: art, bakery, loft, placeholders (Opus) | Archived | Completed | Spawned by another Claude session | PR #26 merged into claude/zen-turing-m1jnw0; round-4 art brief complete, user copies two .blend masters into ROSW | `2026-10-16_wdi-x-art-bakery-loft-placeholders-opus_oyJk3Tfi.md` |
| 2026-10-16 | WDI Y: content, copy, audio, playtest kit (Opus) | Archived | Completed | Spawned by another Claude session | PR #20 merged into claude/zen-turing-m1jnw0; brief Y finished, with log items left for the orchestrator | `2026-10-16_wdi-y-content-copy-audio-playtest-kit-opus_LowbnyX8.md` |

### Who Did It, round 5 (WDI 5A to 5M) (14 sessions, 2026-10-18 to 2026-10-18)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-18 | WDI 5A: ONUB v2 rules, server deal and prep (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #27 merged: onub prep rules, server deal, and Evening Prep landed as three commits; nothing further needed | `2026-10-18_wdi-5a-onub-v2-rules-server-deal-and-prep-sonnet_Z1vSLdZ1.md` |
| 2026-10-18 | WDI 5B: ONUB v2 server night and morning (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #28 merged: night rules, night run, dawn, Morning Rush, CRUST Pantry vote, Restaurant Shutdown, reveal and game over. | `2026-10-18_wdi-5b-onub-v2-server-night-and-morning-sonnet_oBDxMbRQ.md` |
| 2026-10-18 | WDI 5C: ONUB v2 client prep, mini-games, deck editor (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #37 merged from claude/zen-turing-m1jnw0; remaining 5C items belong to 5A, 5M, and the orchestrator | `2026-10-18_wdi-5c-onub-v2-client-prep-mini-games-deck-edito_ZsrCwyaj.md` |
| 2026-10-18 | WDI 5D: ONUB v2 client night, morning and results (Sonnet) | Archived | Completed | Spawned by another Claude session | All four 5D branches integrated into claude/zen-turing-m1jnw0; PRs #36, #39, #43 closed unmerged. | `2026-10-18_wdi-5d-onub-v2-client-night-morning-and-results_ZCVGvCem.md` |
| 2026-10-18 | WDI 5E: ONUB v2 bots, NPC brains, e2e and soak (Sonnet) | Archived | Failed | Spawned by another Claude session |  | `2026-10-18_wdi-5e-onub-v2-bots-npc-brains-e2e-and-soak-sonn_eAxjQMH2.md` |
| 2026-10-18 | WDI 5F: Avatars, public looks, covers, Impersonate (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #35 merged to base with the full 5F brief; one red server check (onubNight quick-mode test) judged flaky and not re-run | `2026-10-18_wdi-5f-avatars-public-looks-covers-impersonate-s_RU6tDKSs.md` |
| 2026-10-18 | WDI 5G: Main deck and Werewolf roles (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #34 merged; session 5G finished, follow-ups recorded in decision A58 and the PR description | `2026-10-18_wdi-5g-main-deck-and-werewolf-roles-sonnet_89i5n6pV.md` |
| 2026-10-18 | WDI 5H: NPC routines and fixes (Sonnet) | Archived | Failed | Spawned by another Claude session |  | `2026-10-18_wdi-5h-npc-routines-and-fixes-sonnet_V4W1hNxi.md` |
| 2026-10-18 | WDI 5I: Isometric client and lighting (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #29 merged and 5I brief finished; closed-profile gate fence, 45 fps check, and Child vision delta left open for the orchestrator | `2026-10-18_wdi-5i-isometric-client-and-lighting-sonnet_5ESH86KS.md` |
| 2026-10-18 | WDI 5J: Maps (Opus) | Archived | Completed | Spawned by another Claude session | Session 5J PRs #32, #38, #41, #44 merged; check-ins stopped, nothing left to watch | `2026-10-18_wdi-5j-maps-opus_3horF2Bn.md` |
| 2026-10-18 | WDI 5K: World art (Opus) | Archived | Completed | Spawned by another Claude session | PR #40 merged at 10fe7b7 into claude/zen-turing-m1jnw0; one server CI job failed (likely flaky onubDeal test), not investigated; 300-credit budget unused | `2026-10-18_wdi-5k-world-art-opus_syVMk7J3.md` |
| 2026-10-18 | WDI 5L: Character art (Opus) | Archived | Completed | Spawned by another Claude session | PR #33 merged to complete 5L; one unrelated server test flake left for a maintainer to re-run | `2026-10-18_wdi-5l-character-art-opus_dJpHu7sr.md` |
| 2026-10-18 | WDI 5M: ONUB art (Opus) | Archived | Completed | Spawned by another Claude session | PR #45 merged: ONUB art complete in 8-bit and low-poly, with Brick Oven pick D and the Google terms licence row. | `2026-10-18_wdi-5m-onub-art-opus_Y4efdd72.md` |
| 2026-10-18 | WDI 5N: Art-style switch, 8-bit / Low poly (Sonnet) | Archived | Completed | Spawned by another Claude session | PR #46 merged; art-style switch landed. Server onubNight flake left red, judged unrelated to the diff | `2026-10-18_wdi-5n-art-style-switch-8-bit-low-poly-sonnet_L588482M.md` |

### The progress reports (1 sessions, 2026-10-18 to 2026-10-18)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-18 | Progress report part 2 and Claude usage patterns | Archived | Completed | Claude on iOS | /home/user/Progress_Report_Part2.pdf (attached to chat) | `2026-10-18_progress-report-part-2-and-claude-usage-patterns_wE8hiKoB.md` |

### ROSW tooling, housekeeping and planning (14 sessions, 2026-10-21 to 2026-11-17)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-21 | Plugin sound effects upload | Archived | Completed | Claude on iOS |  | `2026-10-21_plugin-sound-effects-upload_mKAHUT6m.md` |
| 2026-10-25 | Teardown tool configuration | Archived | Completed | Claude desktop app | Draft PR The-Intern#8 corrects the out-of-date CI notes in the docs and state.js; CI is green. Not merged. | `2026-10-25_teardown-tool-configuration_kmQrd4JH.md` |
| 2026-10-28 | Tailwind CSS configuration | Archived | Completed | Claude desktop app | PR #6 merged; agent unsubscribed from its notifications | `2026-10-28_tailwind-css-configuration_5ALedxEP.md` |
| 2026-10-29 | Agent reach in plugins repo | Archived | Completed | Claude desktop app | All code is merged via PR #20 and repos are clean; the research notes exist only in the session scratch folder and will be lost when it ends unless copied. | `2026-10-29_agent-reach-in-plugins-repo_NarAL3pu.md` |
| 2026-10-29 | Cloning video-use and clipify repos | Archived | Completed | Claude desktop app | PR #21 merged into Pipelines-Plugin main; open items: first live ve publish, first /plugin install, archive old Video-Editor repo | `2026-10-29_cloning-video-use-and-clipify-repos_rvo4p5Pg.md` |
| 2026-10-29 | Session autocompact strategy | Archived | Completed | Claude desktop app | PR #433 marked ready and merged; nothing scheduled; round 10 (part 2) paused until you message to start | `2026-10-29_session-autocompact-strategy_PTi8ZPYa.md` |
| 2026-10-30 | Pipelines plugin review and expansion plan | Archived | Completed | Claude Code CLI | Reviewed the pipelines plugin: fixes, 13 new pipelines, 8 chains, and a graphic-design plugin plan with 4 open decisions. | `2026-10-30_pipelines-plugin-review-and-expansion-plan_usUTW6nL.md` |
| 2026-10-31 | OneDrive to Google Drive migration | Archived | Completed | Claude Code CLI | Recycled 176 files (~820 MB) after confirming same-size copies in Drive; backrooms4.blend skipped. Check Drive sync before emptying the Recycle Bin. | `2026-10-31_onedrive-to-google-drive-migration_pNFK4anv.md` |
| 2026-10-31 | PR 23 review | Archived | Completed | Claude desktop app |  | `2026-10-31_pr-23-review_HXipS4yY.md` |
| 2026-10-31 | Sonnet sessions from roadmap | Archived | Completed | Claude desktop app | PR #30 merged; PRs #25 to #28 remain open and unmerged | `2026-10-31_sonnet-sessions-from-roadmap_1DJmy7hz.md` |
| 2026-10-31 | MCP server installation issue | Archived | Completed | Claude Code CLI | Meshy MCP server added; restart coding agent, then confirm `meshy` appears in /mcp | `2026-10-31_mcp-server-installation-issue_rrMTmo2j.md` |
| 2026-10-31 | Duplicate folders investigation | Archived | Completed | Claude Code CLI | Left GPU machine, ComfyUI provider wiring, and real-server test open; ComfyUI client merged but untested. Blender, printer check, and branch cleanup remain as l | `2026-10-31_duplicate-folders-investigation_8JE62Qju.md` |
| 2026-11-02 | Delete remote branches | Archived | Completed | Claude desktop app | Explained all additions (audio, controls, main merge, tests, tooling) and listed what remains unverified. | `2026-11-02_delete-remote-branches_pabnbG9S.md` |
| 2026-11-17 | Documentation audit plan | Active | Review ready | Claude on iOS |  | `2026-11-17_documentation-audit-plan_GJBqs7XT.md` |

### Who Did It, round 6 (17 sessions, 2026-10-22 to 2026-10-24)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-22 | 6A: time scale, auto mode, headless harness, CLI | Archived | Completed | Spawned by another Claude session | PR #54 (6A) merged into claude/zen-turing-m1jnw0 as edb6e44; onubNight.test.ts timing race remains on base | `2026-10-22_6a-time-scale-auto-mode-headless-harness-cli_nzD4bsJD.md` |
| 2026-10-22 | 6E: M5b content and GDD 3.14 to 3.16 | Archived | Completed | Spawned by another Claude session | M5b content (resources, recipes, mobs, quests, mini-games) and GDD 3.14–3.16 merged in PR #49; Lockpicks/Snare craftability is open decision A87 in DECISIONS.md | `2026-10-22_6e-m5b-content-and-gdd-3-14-to-3-16_A9guEQLm.md` |
| 2026-10-22 | 6J: cutscenes | Archived | Completed | Spawned by another Claude session | Session 6J complete: HollowMere opening, Blackpine pan, cutscene player, and five death cutscenes merged via #52, #55, #57. | `2026-10-22_6j-cutscenes_QUhJyxKv.md` |
| 2026-10-22 | 6K: loading, transitions, trailer, budgets | Archived | Completed | Spawned by another Claude session |  | `2026-10-22_6k-loading-transitions-trailer-budgets_9tKHMakv.md` |
| 2026-10-22 | 6L: music | Archived | Completed | Spawned by another Claude session | PR #48 merged into claude/zen-turing-m1jnw0 as 99edd21; music bus, CC0 lobby/end-screen beds landed, other slots silent pending files | `2026-10-22_6l-music_38ikwjEt.md` |
| 2026-10-22 | 6M: M5b art | Archived | Completed | Spawned by another Claude session |  | `2026-10-22_6m-m5b-art_YgH8yL5r.md` |
| 2026-10-22 | 6B: event bus and invariants | Archived | Completed | Spawned by another Claude session |  | `2026-10-22_6b-event-bus-and-invariants_mqHumgPx.md` |
| 2026-10-22 | 6C: GitHub auth and AdminRoom | Archived | Completed | Spawned by another Claude session | PR #58 merged into claude/zen-turing-m1jnw0; owner must set five WDI_ADMIN_* vars on Railway | `2026-10-22_6c-github-auth-and-adminroom_Z72yR4XT.md` |
| 2026-10-22 | 6F: gathering and crafting | Archived | Completed | Spawned by another Claude session |  | `2026-10-22_6f-gathering-and-crafting_PvGmsMhD.md` |
| 2026-10-22 | 6G: mobs and dark visibility | Archived | Completed | Spawned by another Claude session | PR #59 (session 6G: mobs, wolf kill, dark visibility) merged at 3944cdd; follow-up PR to carry flee line and light command | `2026-10-22_6g-mobs-and-dark-visibility_ZhArcC2h.md` |
| 2026-10-22 | 6H: quests and mini-games | Archived | Completed | Spawned by another Claude session |  | `2026-10-22_6h-quests-and-mini-games_KFerTAbi.md` |
| 2026-10-22 | 6I: M5b client | Archived | Completed | Spawned by another Claude session | PR #67 head is now 8a1e348 with zen-turing merged in; lint, typecheck and tests pass locally; CI pending, 6Z merges on green | `2026-10-22_6i-m5b-client_aXeSfTEt.md` |
| 2026-10-22 | 6D: admin client | Archived | Completed | Spawned by another Claude session |  | `2026-10-22_6d-admin-client_ywBpUrQ1.md` |
| 2026-10-22 | 6N: ROSW media (both repos) | Archived | Completed | Spawned by another Claude session | PR #84 merged: opening cinematic trimmed to 1.17s, 6.3s landing loop added, first tap plays lobby music | `2026-10-22_6n-rosw-media-both-repos_gVG9ebNw.md` |
| 2026-10-22 | 6P: round-6 integration | Archived | Completed | Spawned by another Claude session | #73 merged (96387a7); new 7M session (Fable 5.1, Ultracode) builds all mini-games and main-mode task assignment; WDI_ADMIN_* not needed | `2026-10-22_6p-round-6-integration_t9v4N6oc.md` |
| 2026-10-22 | 6Q: opening cinematic | Archived | Completed | Spawned by another Claude session |  | `2026-10-22_6q-opening-cinematic_veWdRCed.md` |
| 2026-10-24 | 6Z: Who-Did-It orchestrator (round 8) | Archived | Completed | Spawned by another Claude session | PR #313 was marked ready and merged, with no follow-up left on it | `2026-10-24_6z-who-did-it-orchestrator-round-8_ikPFcTsY.md` |

### Who Did It, round 7 (13 sessions, 2026-10-23 to 2026-10-24)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-23 | 7A: map intro tracks and cinematic openings | Archived | Completed | Spawned by another Claude session |  | `2026-10-23_7a-map-intro-tracks-and-cinematic-openings_6DEemceU.md` |
| 2026-10-23 | 7B: theme pieces (night palette, pixel fonts, glass, backdrop) | Archived | Completed | Spawned by another Claude session | Backdrop PR #100 is green in CI and handed to 6Z to merge; party test flake flagged for 7A's #101 cutscene length. | `2026-10-23_7b-theme-pieces-night-palette-pixel-fonts-glass_7wrq33wV.md` |
| 2026-10-23 | 7D: parties server (open/private, listing, profiles) | Archived | Completed | Spawned by another Claude session | PR #85 (wire) and PR #89 (listing, f300474) merged to base; SESSIONS log and A108 on base | `2026-10-23_7d-parties-server-open-private-listing-profiles_3EHPoYgh.md` |
| 2026-10-23 | 7H: vendettas (data, server, invariants, GDD 3.20) | Archived | Completed | Spawned by another Claude session | PR #128 (four vendetta checks) merged into the base; 7H reported done to 6Z; nothing needs the user | `2026-10-23_7h-vendettas-data-server-invariants-gdd-3-20_SiWgJRDt.md` |
| 2026-10-23 | 7I: the Daily Train, the memorial, the Ascended Vicar | Archived | Completed | Spawned by another Claude session |  | `2026-10-23_7i-the-daily-train-the-memorial-the-ascended-vic_oqxDJXUC.md` |
| 2026-10-23 | 7C: menu, profile, friends, Quit, party list | Archived | Completed | Spawned by another Claude session | 7C brief complete on base 136dca7 across #94, #106, #110 and docs; trailer CSS leftover left for 7B | `2026-10-23_7c-menu-profile-friends-quit-party-list_RSG1j4r2.md` |
| 2026-10-23 | 7E: lobby re-skin (three columns) | Archived | Completed | Spawned by another Claude session | PR #102 (lobby re-skin, incl. Add friend swap) merged; lint, typecheck, and client tests pass; e2e specs not run on final branch. | `2026-10-23_7e-lobby-re-skin-three-columns_HKGQCyzx.md` |
| 2026-10-23 | 7F: match screens re-skin (HUD, role card, notebook, M5b, loading) | Archived | Completed | Spawned by another Claude session |  | `2026-10-23_7f-match-screens-re-skin-hud-role-card-notebook_6maL417d.md` |
| 2026-10-23 | 7G: meeting, game over, quick-mode and admin screens re-skin | Archived | Completed | Spawned by another Claude session |  | `2026-10-23_7g-meeting-game-over-quick-mode-and-admin-screen_MazRQTw2.md` |
| 2026-10-23 | 7J: the quick mode's removal | Archived | Completed | Spawned by another Claude session | PR #127 merged, so 7J's PRs #109, #121, and #127 are all in the base branch; quick mode removed and nothing else open. | `2026-10-23_7j-the-quick-mode-s-removal_HkWFT75u.md` |
| 2026-10-23 | 7K: Crumb's Ovens' rooms from the owner's station pictures | Archived | Completed | Spawned by another Claude session | Four Crumb's Ovens rooms shipped across PRs #111, #114, #122; nothing unpushed, kitchen art set aside for round 8 | `2026-10-23_7k-crumb-s-ovens-rooms-from-the-owner-s-station_SNd15GSm.md` |
| 2026-10-23 | 7M: every mini-game and main-mode task assignment | Archived | Failed | Spawned by another Claude session |  | `2026-10-23_7m-every-mini-game-and-main-mode-task-assignment_1sdsHATT.md` |
| 2026-10-24 | 7M (Opus): mini-games and stations | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_7m-opus-mini-games-and-stations_qgL3vNAn.md` |

### Who Did It, round 8 (26 sessions, 2026-10-23 to 2026-10-24)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-23 | 8A: Bodies (health, stamina, effects, fists) | Archived | Failed | Spawned by another Claude session |  | `2026-10-23_8a-bodies-health-stamina-effects-fists_VEobzSXD.md` |
| 2026-10-23 | 8B: Inspect and the relations table | Archived | Completed | Spawned by another Claude session | Sent 8N the inspect text that needs icons; 6Z moved to session_01JAtrwjzsMybVeFikPFcTsY; merges frozen at 58a669f. | `2026-10-23_8b-inspect-and-the-relations-table_HsqMYbtr.md` |
| 2026-10-23 | 8C: Scrip (purses, wages, shops, bank, coins) | Archived | Completed | Spawned by another Claude session |  | `2026-10-23_8c-scrip-purses-wages-shops-bank-coins_DN9DHzMN.md` |
| 2026-10-23 | 8D: Rent, Faith, rumours, HQ tiers | Archived | Completed | Spawned by another Claude session |  | `2026-10-23_8d-rent-faith-rumours-hq-tiers_tFC3c3To.md` |
| 2026-10-23 | 8E: Moods, townsfolk, mugging | Archived | Failed | Spawned by another Claude session |  | `2026-10-23_8e-moods-townsfolk-mugging_A71DZxk2.md` |
| 2026-10-23 | 8F: Characters (redesign, scale, clips) | Archived | Failed | Spawned by another Claude session |  | `2026-10-23_8f-characters-redesign-scale-clips_a5u3HL3T.md` |
| 2026-10-23 | 8G: Creatures, resource breaks, VFX, transport | Archived | Completed | Spawned by another Claude session | All round-8 PRs (1–6, #231) and node_coins art merged; HQ HD frames pending 8I, masters pending owner re-run. | `2026-10-23_8g-creatures-resource-breaks-vfx-transport_KkGzgnRP.md` |
| 2026-10-23 | 8H: Interface motion | Archived | Completed | Spawned by another Claude session |  | `2026-10-23_8h-interface-motion_JPbsyWeE.md` |
| 2026-10-23 | 8I: HD art style | Archived | Failed | Spawned by another Claude session |  | `2026-10-23_8i-hd-art-style_FKkSwuTW.md` |
| 2026-10-23 | 8J: HollowMere rooms (placement and detail) | Archived | Completed | Spawned by another Claude session | All HollowMere room PRs merged at 14ac577d; no open PRs. hiveBands flake is with 6Z. | `2026-10-23_8j-hollowmere-rooms-placement-and-detail_HouX1Q4o.md` |
| 2026-10-23 | 8K: BlackPine rooms (placement and detail) | Archived | Completed | Spawned by another Claude session | PR #212 confirmed merged and brief complete; on-screen name stays 'BlackPine' with no rename; session being archived. | `2026-10-23_8k-blackpine-rooms-placement-and-detail_TvUqRSzn.md` |
| 2026-10-23 | 8L Anti-cheat (Who Did It round 8) | Archived | Completed | Spawned by another Claude session | All four anti-cheat plan steps merged (PRs #167, #178, #181, #192); nothing unpushed or scheduled. | `2026-10-23_8l-anti-cheat-who-did-it-round-8_8A2pocnR.md` |
| 2026-10-23 | 8M Rules (Who Did It round 8) | Archived | Completed | Spawned by another Claude session | #187 merged; #179 still merges cleanly on new base, no further merge needed | `2026-10-23_8m-rules-who-did-it-round-8_XhMSjNX1.md` |
| 2026-10-23 | 8N Icons (Who Did It round 8) | Archived | Failed | Spawned by another Claude session |  | `2026-10-23_8n-icons-who-did-it-round-8_jMT2Tmma.md` |
| 2026-10-24 | 8R: the NPC hive (living world, round 8) | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8r-the-npc-hive-living-world-round-8_gysm1Brf.md` |
| 2026-10-24 | 8T: meeting notes and NPC talk (living world, round 8) | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8t-meeting-notes-and-npc-talk-living-world-round_d4RngbEA.md` |
| 2026-10-24 | 8V: Canon (the lore into the game's names and text) | Archived | Failed | Spawned by another Claude session |  | `2026-10-24_8v-canon-the-lore-into-the-game-s-names-and-text_ovC7362T.md` |
| 2026-10-24 | 8A (Opus): Bodies (health, stamina, effects, fists) | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8a-opus-bodies-health-stamina-effects-fists_NaHfWqP2.md` |
| 2026-10-24 | 8E (Opus): Moods, townsfolk, mugging | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8e-opus-moods-townsfolk-mugging_k6KW9vJp.md` |
| 2026-10-24 | 8F (Opus): Characters (redesign, scale, clips) | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8f-opus-characters-redesign-scale-clips_ndmRqEDP.md` |
| 2026-10-24 | 8I (Opus): HD art style | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8i-opus-hd-art-style_3hUcCvas.md` |
| 2026-10-24 | 8N (Opus): Icons | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8n-opus-icons_WQJS2LXf.md` |
| 2026-10-24 | 8V (Opus): Canon (the lore into the game's names and text) | Archived | Completed | Spawned by another Claude session |  | `2026-10-24_8v-opus-canon-the-lore-into-the-game-s-names-and_GYmpwkP6.md` |
| 2026-10-24 | 8W (Sonnet): shelf pages from the vault | Archived | Completed | Spawned by another Claude session | PR #256 merged into claude/zen-turing-m1jnw0; #252 can close | `2026-10-24_8w-sonnet-shelf-pages-from-the-vault_jcK7ek42.md` |
| 2026-10-24 | 8Y (Sonnet): #243 HollowMere/BlackPine display names | Archived | Completed | Spawned by another Claude session | PR #243 unchanged at head e0a517a, local checks green; SHA reported to orchestrator 6Z | `2026-10-24_8y-sonnet-243-hollowmere-blackpine-display-names_cmRdL8nJ.md` |
| 2026-10-24 | 8Z (Sonnet): #253 charm save base merge | Archived | Completed | Spawned by another Claude session | PR #253 retargeted to claude/zen-turing-m1jnw0 and merged at head d3f8171; lint, typecheck and tests clean; still draft. | `2026-10-24_8z-sonnet-253-charm-save-base-merge_1PbJZec9.md` |

### Who Did It, round 9 (9 sessions, 2026-10-25 to 2026-10-25)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-25 | 9A (Opus): world mode and phases design | Archived | Completed | Spawned by another Claude session |  | `2026-10-25_9a-opus-world-mode-and-phases-design_F7m4Q4q3.md` |
| 2026-10-25 | 9B (Sonnet): logic table and failure messages design | Archived | Completed | Spawned by another Claude session |  | `2026-10-25_9b-sonnet-logic-table-and-failure-messages-desig_VqastJW4.md` |
| 2026-10-25 | 9C (Sonnet): living world and emergent play design | Archived | Completed | Spawned by another Claude session |  | `2026-10-25_9c-sonnet-living-world-and-emergent-play-design_L3C1yKcZ.md` |
| 2026-10-25 | 9D (Opus): fold the owner's answers, GDD map and round-10 plan | Archived | Completed | Spawned by another Claude session |  | `2026-10-25_9d-opus-fold-the-owner-s-answers-gdd-map-and-rou_eULqTHCR.md` |
| 2026-10-25 | 9S (Opus): admin Studio server | Archived | Completed | Spawned by another Claude session | Pushed claude/r9-studio-server as a fast-forward; branch now matches its base, so no PR is needed. S3, S4 and S5 are already merged. | `2026-10-25_9s-opus-admin-studio-server_WNiGeGNN.md` |
| 2026-10-25 | 9T (Sonnet): admin Studio client | Archived | Completed | Spawned by another Claude session | All five Studio client PRs (T1–T5) are merged; #293 passed local typecheck, lint, and 808 client tests, though CI on the final head was not seen. | `2026-10-25_9t-sonnet-admin-studio-client_snhP4uMS.md` |
| 2026-10-25 | 9U (Sonnet): Studio editor live redraw and material painting | Archived | Completed | Spawned by another Claude session | Studio mode toggle, editor features, and rotation shipped via #298-#307 on claude/zen-turing-m1jnw0; no queued PRs left | `2026-10-25_9u-sonnet-studio-editor-live-redraw-and-material_7Fpud5aa.md` |
| 2026-10-25 | 9V (Opus): Studio content save and NPC lines as data | Archived | Completed | Spawned by another Claude session | #309 merged as 4f38557 after #303; Studio NPC save covers routines, quests, lore, talk; 715 server tests pass | `2026-10-25_9v-opus-studio-content-save-and-npc-lines-as-dat_cXWGZc9e.md` |
| 2026-10-25 | 9W (Sonnet): Studio Overview and NPC editor client | Archived | Completed | Spawned by another Claude session | Studio PRs #300, #301, #305, #304, #308, #310 merged; NPC editor Save not yet verified end-to-end | `2026-10-25_9w-sonnet-studio-overview-and-npc-editor-client_YzfkEGXi.md` |

### Who Did It, round 10 (16 sessions, 2026-10-29 to 2026-10-30)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-29 | 10A (Opus): the slice's contracts | Archived | Completed | Spawned by another Claude session | All PRs through A7b (#349) merged; K1 and T4 planned but not started. Plans handed to 6Z for round 10 part 2. | `2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md` |
| 2026-10-29 | 10F (Opus): the logic table | Archived | Completed | Spawned by another Claude session | PR #429 was marked ready for review and then merged; no further action needed. | `2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md` |
| 2026-10-29 | 10H (Sonnet): the slice's rules | Archived | Completed | Spawned by another Claude session |  | `2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md` |
| 2026-10-29 | 10G (Sonnet): the refusal sweep | Archived | Completed | Spawned by another Claude session | PR #330 confirmed merged at 86e8422, both lists recorded, nothing unpushed; done line sent to 6Z | `2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md` |
| 2026-10-29 | 10C (Opus): death's cost and arrivals | Archived | Completed | Spawned by another Claude session |  | `2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md` |
| 2026-10-29 | 10B (Opus): the law | Archived | Completed | Spawned by another Claude session | B6d (#448) complete on 633fa96; one red e2e check judged unrelated, re-run deferred to part 2 | `2026-10-29_10b-opus-the-law_B4Hq1Uae.md` |
| 2026-10-29 | 10D (Sonnet): the living world | Archived | Completed | Spawned by another Claude session | PR #536 is merged; the ready-for-review and merged notifications were the last events, so no further action is needed | `2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md` |
| 2026-10-30 | 10X (Fable): fixes, server and rules | Archived | Completed | Spawned by another Claude session | All four PRs (#397, #425, #442, #431) merged to main by Story mode after CI passed; no scheduled tasks remain; local worktrees hold nothing unpushed | `2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md` |
| 2026-10-30 | 10Y (Fable): fixes, client and screens | Archived | Completed | Spawned by another Claude session | #534 merged into base, landing the client half of C4b (Derringer ability slot, Departed screen, Hitman end-panel line); no open PRs or unpushed work | `2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md` |
| 2026-10-30 | 10R: role cards and the player dashboard (design) | Archived | Completed | Spawned by another Claude session | R1 and R2 merged (#423 landed the paper); no open PRs or unpushed work. R1b and R3-R6 are in the handoff sent to 6Z for part 2. | `2026-10-30_10r-role-cards-and-the-player-dashboard-design_CAKKzVuL.md` |
| 2026-10-30 | 10V (Opus): The missing verbs | Archived | Completed | Spawned by another Claude session | V1a PR #421 marked Complete, CI green at 798d0038; V1b held until round 10 part 2 messages to resume | `2026-10-30_10v-opus-the-missing-verbs_QJz2QNAq.md` |
| 2026-10-30 | 10S (Opus): The scope census | Archived | Completed | Spawned by another Claude session |  | `2026-10-30_10s-opus-the-scope-census_HHeKca4Z.md` |
| 2026-10-30 | 10N: the new roles (round 10, wave 2) | Archived | Completed | Spawned by another Claude session | Draft PR #441 (K6a snares) pushed, marked WIP with CI still queued; K6b on WIP branch claude/r10-k6b-snares-npc; handoff sent to 6Z. | `2026-10-30_10n-the-new-roles-round-10-wave-2_xUZtSknf.md` |
| 2026-10-30 | 10K: kit and the wild (round 10, wave 2) | Archived | Completed | Spawned by another Claude session | Draft PR #440 at 49/50 auto matches; match 30 npcStuck failure, options sent to 6Z; holding before K7 | `2026-10-30_10k-kit-and-the-wild-round-10-wave-2_4mziWaC7.md` |
| 2026-10-30 | 10T: the town (round 10, wave 2) | Archived | Completed | Spawned by another Claude session |  | `2026-10-30_10t-the-town-round-10-wave-2_934vv6Gw.md` |
| 2026-10-30 | 10M: ghosts, talk and modes (round 10, wave 2) | Archived | Completed | Spawned by another Claude session |  | `2026-10-30_10m-ghosts-talk-and-modes-round-10-wave-2_zqSoYSUx.md` |

### Who Did It, round 11 (7 sessions, 2026-10-29 to 2026-11-19)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-29 | 11A (Opus): the render pipeline | Archived | Completed | Spawned by another Claude session | Owner approved the round-11 build plan with the default shadow direction (A236); session archives until round 11 opens. | `2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md` |
| 2026-10-29 | 11B (Opus): materials, styles and budgets | Archived | Completed | Spawned by another Claude session | look.md (#347), long-shadow budget (#371), and build-plan half (#374) merged; project paused, session archived | `2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md` |
| 2026-11-19 | 11D: round 11 decisions (Three.js, model locks) | Archived | Completed | Spawned by another Claude session | 11D finished for Round 11: S0 (#554), H1 (#557) and Meshy CC0 follow-up (#561, f91b7cd8) all merged | `2026-11-19_11d-round-11-decisions-three-js-model-locks_D3d3fjEo.md` |
| 2026-11-19 | 11T: round 11 tooling (Blender CI, render locks) | Archived | Completed | Spawned by another Claude session | PR #577 is marked ready for review with all four CI checks green; the orchestrator merges next | `2026-11-19_11t-round-11-tooling-blender-ci-render-locks_E8SszT7j.md` |
| 2026-11-19 | 11P: round 11 prop list | Active | Blocked | Spawned by another Claude session |  | `2026-11-19_11p-round-11-prop-list_sgQGbvMg.md` |
| 2026-11-19 | Round 11 · 11R The renderer | Active | Review ready | Spawned by another Claude session |  | `2026-11-19_round-11-11r-the-renderer_hjDrA2Hw.md` |
| 2026-11-19 | Round 11 · 11F Figure sprites | Active | Completed | Spawned by another Claude session | PR #578 (F2a) is green and ready for review; #582 and #586 stay drafts until gate G. No further check-ins scheduled. | `2026-11-19_round-11-11f-figure-sprites_RXNaUHaC.md` |

### ROSW Wave 1 hardening (31 Oct) (4 sessions, 2026-10-31 to 2026-10-31)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-10-31 | W1-A: studio safety (Meshy, hub, compute gate) | Archived | Completed | Spawned by another Claude session | PR #28 (https://github.com/groot99-droid/Pipelines-Plugin/pull/28) merged; Lane A complete. Open decisions left to user: CDN link policy, discrete-GPU setting,  | `2026-10-31_w1-a-studio-safety-meshy-hub-compute-gate_uKuiRvEW.md` |
| 2026-10-31 | W1-B: plugins and tooling (blender, video-editor, CI) | Archived | Completed | Spawned by another Claude session | PR #26 merged after full verify matrix (Linux/Windows/macOS, Py 3.10/3.13) went green on fbaf966; add-on tools still need enabling in build_manifests.py | `2026-10-31_w1-b-plugins-and-tooling-blender-video-editor-ci_8BuAcFL7.md` |
| 2026-10-31 | W1-C: truth pass and writing pipeline | Archived | Completed | Spawned by another Claude session | PR #25 merged: llm.py hardening, run_pipeline.py guards, doc truth pass. Three open decisions remain in the PR body. | `2026-10-31_w1-c-truth-pass-and-writing-pipeline_eTpfkTkG.md` |
| 2026-10-31 | W1-D: skills and agents optimization | Archived | Completed | Spawned by another Claude session | PR #27 merged after CI went green on 5ea3c91; two follow-ups left for the author. | `2026-10-31_w1-d-skills-and-agents-optimization_muEk4Toa.md` |

### Look Over There (2 sessions, 2026-11-01 to 2026-11-04)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-11-01 | Left trigger controller shift | Archived | Completed | Claude desktop app | Left-trigger crouch change merged to main; agent unsubscribed from the PR and has nothing further to do. | `2026-11-01_left-trigger-controller-shift_zE7pK5Sj.md` |
| 2026-11-04 | Game scenes and level connections | Active | Review ready | Claude on iOS |  | `2026-11-04_game-scenes-and-level-connections_nHeznJEZ.md` |

### Writing and brands (1 sessions, 2026-11-03 to 2026-11-03)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-11-03 | Stop asking for it chapter | Archived | Completed | Claude on iOS | PR #33 merged after being marked ready for review | `2026-11-03_stop-asking-for-it-chapter_8WFzr4wy.md` |

### Who Did It, Story mode (11 sessions, 2026-11-06 to 2026-11-10)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-11-06 | Story mode | Active | Review ready | Claude desktop app |  | `2026-11-06_story-mode_oZ8CZDFp.md` |
| 2026-11-06 | Story S1: story content and schema | Archived | Completed | Spawned by another Claude session | PR #454 merged; agent has no open PRs and nothing further to act on | `2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md` |
| 2026-11-06 | Story S2: story engine and seat handover | Archived | Completed | Spawned by another Claude session | Pushed the pending #460 merge commit to claude/story-s2-seat-handover; branch now matches remote. The commit adds nothing new since #460 was already merged. | `2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md` |
| 2026-11-06 | Story S3: protocol and client cards | Archived | Completed | Spawned by another Claude session | No merges into claude/story-part2 since 8b3ca017 (#537); no changes in apps/client, packages/shared or packages/content; no open PRs. | `2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md` |
| 2026-11-06 | Story S4: tests, replay and bot | Archived | Completed | Spawned by another Claude session | PR #462 marked ready and merged; session unsubscribed, no further action | `2026-11-06_story-s4-tests-replay-and-bot_HnxDqZRT.md` |
| 2026-11-06 | Story P0: the HollowMere arc (design) | Archived | Completed | Spawned by another Claude session | Orchestrator is mid-turn editing the A615 row in docs/DECISIONS.md; no PRs open into claude/story-part2. | `2026-11-06_story-p0-the-hollowmere-arc-design_B7eQSKQ5.md` |
| 2026-11-06 | Story P4: achievements on the device | Archived | Completed | Spawned by another Claude session | Round 10 E1 achievements complete; PR #469 merged; final handoff in docs/story/status.md | `2026-11-06_story-p4-achievements-on-the-device_SSXYJkcQ.md` |
| 2026-11-07 | Story merge queue: round 10 PRs into the base | Archived | Completed | Spawned by another Claude session | Merged #421 and #448 among others; skipped #437, #438, #435, #441, #440 pending owner sign-off. Duplicate ### 14.54 in docs/UI.md needs fixing. | `2026-11-07_story-merge-queue-round-10-prs-into-the-base_YdYTm2cA.md` |
| 2026-11-07 | Story P2: sections engine | Archived | Completed | Spawned by another Claude session | PR #497 merged; agent standing by with no open PRs | `2026-11-07_story-p2-sections-engine_76C6nUHz.md` |
| 2026-11-07 | Story P3: client, saves and end screen | Archived | Completed | Spawned by another Claude session | PR #484 merged; no open PRs remaining for P3 story client | `2026-11-07_story-p3-client-saves-and-end-screen_cVJ9rsJZ.md` |
| 2026-11-10 | Story R: the Medium's rite and the 10X Vicar | Archived | Completed | Spawned by another Claude session | All five R8 PRs merged and the tree is clean; only the 3.4 story.json entry remains, waiting on P5 chapter 3. | `2026-11-10_story-r-the-medium-s-rite-and-the-10x-vicar_fpYurWpn.md` |

### Who Did It, round 10 later slices (7 Nov) (5 sessions, 2026-11-07 to 2026-11-07)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-11-07 | Round 10 B6d2: NPC present-and-file rule | Archived | Completed | Spawned by another Claude session | B6d2 shipped via PR #474, which was merged by someone other than the agent; no further work pending | `2026-11-07_round-10-b6d2-npc-present-and-file-rule_yikzL16Z.md` |
| 2026-11-07 | Round 10 V3: hiding spots (Hide, Check, Burst Out) | Archived | Completed | Spawned by another Claude session | V3 merged into base as 58a6e97; NPC seat hiding logged in DECISIONS A578, client work left to 10Y | `2026-11-07_round-10-v3-hiding-spots-hide-check-burst-out_Gc9thv76.md` |
| 2026-11-07 | Round 10 V1b: Dust, Compare and Autopsy | Archived | Completed | Spawned by another Claude session | Clean server run passed (147 test files, 970 tests, no failures); V1b has nothing left to do. | `2026-11-07_round-10-v1b-dust-compare-and-autopsy_GGzqrMup.md` |
| 2026-11-07 | Round 10 V2: cover-up verbs | Archived | Completed | Spawned by another Claude session | PR #473 merged as e36a2b7; nothing open on the V2 session side | `2026-11-07_round-10-v2-cover-up-verbs_6pa4Ngpn.md` |
| 2026-11-07 | Round 10 finish: five skipped PRs | Archived | Completed | Spawned by another Claude session | Pushed 42e7c331 to #435 fixing two flaky tests (needs.test.ts fixture, npc.spec.ts watcher walk-over); CI running, Story mode merges once green. | `2026-11-07_round-10-finish-five-skipped-prs_niTBr7xH.md` |

### Who Did It, numbered Session series (8 to 15 Nov) (14 sessions, 2026-11-08 to 2026-11-15)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-11-08 | Session 2: gate return fix, links from the manifest | Active | Completed | Spawned by another Claude session | Slice 2 is in draft PR #55 at b081930; CI finished with no failures. Slice 3 is not started, and the agent asked whether to begin it. | `2026-11-08_session-2-gate-return-fix-links-from-the-manifes_WrLpinA4.md` |
| 2026-11-08 | Session 3: results v2 (local), deaths, revives, score | Archived | Completed | Spawned by another Claude session | PR #9 merged, session 6 Overworld v0 complete; sessions 8 and 9 unblocked but not started | `2026-11-08_session-3-results-v2-local-deaths-revives-score_ry1HRc4T.md` |
| 2026-11-08 | Session 12: tune the Original, starting with B1 | Archived | Completed | Spawned by another Claude session | PR #6 merged and description updated; local branch deleted. Remote claude/tune-original still exists but is harmless. | `2026-11-08_session-12-tune-the-original-starting-with-b1_J5WtLYwC.md` |
| 2026-11-10 | Session 6: Overworld v0 (parking lot, store doors, options screen) | Archived | Completed | Spawned by another Claude session |  | `2026-11-10_session-6-overworld-v0-parking-lot-store-doors-o_hd4UNAn6.md` |
| 2026-11-10 | Session 7: physics decision and playground prototype | Archived | Completed | Spawned by another Claude session | Nothing to push: the flagged commit was PR #9's merge already on origin/main. Local claude/overworld-v0 deleted; checkout is detached at origin/main. | `2026-11-10_session-7-physics-decision-and-playground-protot_UVfvWcCy.md` |
| 2026-11-10 | Session 4: modes and parties (rooms by mode, party key, size 10) | Active | Review ready | Spawned by another Claude session |  | `2026-11-10_session-4-modes-and-parties-rooms-by-mode-party_S2g8sQiT.md` |
| 2026-11-10 | Session 8: Going back in prototype (one floor, chambers, crossbow) | Archived | Completed | Spawned by another Claude session | PR #23 merged into main at b89b6e1; nothing left running | `2026-11-10_session-8-going-back-in-prototype-one-floor-cham_yjjxNjDH.md` |
| 2026-11-10 | Session 9: City v0 on Hallam Row (street, apartment, day clock) | Archived | Completed | Spawned by another Claude session | PRs #36–#39 are merged and main passes unit tests and manifest check; #39 was marked ready 8s before merge; no PRs are being watched | `2026-11-10_session-9-city-v0-on-hallam-row-street-apartment_gJUWCQk2.md` |
| 2026-11-11 | Session 13: make solo_test deterministic (find the real cause first) | Archived | Completed | Spawned by another Claude session | All 16 other browser tests pass on main ff5bd1d (PR #21) with no failed checks; solo_test and mp_test were not rerun on that commit. | `2026-11-11_session-13-make-solo-test-deterministic-find-the_yVH2g6yi.md` |
| 2026-11-12 | Session 14: make mp_test deterministic and measure room frame cost | Archived | Completed | Spawned by another Claude session |  | `2026-11-12_session-14-make-mp-test-deterministic-and-measur_KuLZay2b.md` |
| 2026-11-14 | Session 15: mp_test, the L4 finale switch race | Archived | Completed | Spawned by another Claude session | PR #43 merged; mp_test output now logs page and server health for Xia and players. CI on main not checked. | `2026-11-14_session-15-mp-test-the-l4-finale-switch-race_YxHzNPeB.md` |
| 2026-11-14 | Session 16: Going back in in rooms | Archived | Completed | Spawned by another Claude session | PR #41 is ready for review and no longer a draft; the owner merges it | `2026-11-14_session-16-going-back-in-in-rooms_XahBCYdb.md` |
| 2026-11-14 | Session 17: Overworld and City in rooms, and go to a friend | Archived | Completed | Spawned by another Claude session |  | `2026-11-14_session-17-overworld-and-city-in-rooms-and-go-to_HyS1mPgB.md` |
| 2026-11-15 | Session 18: rules for the arsenal, consumables, dealer items and food | Active | Completed | Spawned by another Claude session | PR #62 was marked ready and merged | `2026-11-15_session-18-rules-for-the-arsenal-consumables-dea_dfok53Yk.md` |

### Who Did It, V2 first-person walk (1 sessions, 2026-11-13 to 2026-11-13)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-11-13 | W3D: walk HollowMere in first person (V2 start) | Archived | Completed | Spawned by another Claude session | #543 adds map hosting from a walk-glb release; merge it, attach hollowmere_walk.glb to that release, then re-run pages | `2026-11-13_w3d-walk-hollowmere-in-first-person-v2-start_98NeMKH7.md` |

### Local sessions on the owner machine (19 to 20 Nov) (4 sessions, 2026-11-19 to 2026-11-20)

| Date | Title | State | Outcome | Started from | Last thing it recorded | File |
|---|---|---|---|---|---|---|
| 2026-11-19 | Rhino documentary short film | Active | Completed | Claude Code CLI | PR #39 merged to main with the video-editor frame-cut fix and films/she-does-not-run; release v5 is public; 6 CI jobs still running on main | `2026-11-19_rhino-documentary-short-film_qYQAuiN8.md` |
| 2026-11-19 | AI MCP tool for pipeline applications | Active | Completed | Claude desktop app | Delivered vast plugin setup steps to the local session: load plugin, check SSH key, run /vast-status, then a cheap 12-minute test rental | `2026-11-19_ai-mcp-tool-for-pipeline-applications_ZVDTwEPL.md` |
| 2026-11-20 | Public SSH key location | Active | Blocked | Claude Code CLI |  | `2026-11-20_public-ssh-key-location_F1kW8xwZ.md` |
| 2026-11-20 | Vast GPU: Dr. Tox build, 1 hour | Active | Working | Claude Code CLI |  | `2026-11-20_vast-gpu-dr-tox-build-1-hour_rj85qwRk.md` |

## 6. All sessions in time order

| # | Created (UTC) | Title | State | Outcome | Items: label matches / docs / PRs / other commits |
|---|---|---|---|---|---|
| 1 | 2026-03-06 03:04 UTC | Set up Claude code agents locally | Archived | Completed | 0 / 0 / 0 / 0 |
| 2 | 2026-03-07 13:31 UTC | Build Procreate brush creation and editing tools | Archived | Completed | 0 / 0 / 0 / 0 |
| 3 | 2026-03-07 19:53 UTC | Build SSCC.inc fiber optics company website | Archived | Completed | 0 / 0 / 0 / 0 |
| 4 | 2026-03-21 17:01 UTC | Procreate Brush Designer Web Application | Archived | Completed | 0 / 0 / 0 / 0 |
| 5 | 2026-08-22 20:56 UTC | Repo strengths and improvements | Archived | Completed | 0 / 0 / 2 / 6 |
| 6 | 2026-08-24 22:32 UTC | Interactive loading screen sequence | Archived | Completed | 0 / 0 / 5 / 12 |
| 7 | 2026-08-27 18:40 UTC | Unzip and add files | Archived | Completed | 0 / 65 / 1 / 4 |
| 8 | 2026-08-27 19:43 UTC | Creative-Writing MD migration gap analysis | Archived | Completed | 0 / 1 / 1 / 1 |
| 9 | 2026-08-27 20:19 UTC | Obsidian and Ollama integration | Archived | Completed | 0 / 1 / 1 / 1 |
| 10 | 2026-08-31 20:02 UTC | Leader Markdown documentation | Archived | Completed | 0 / 0 / 1 / 2 |
| 11 | 2026-08-31 21:02 UTC | HTML and navigation JavaScript | Archived | Completed | 0 / 0 / 0 / 0 |
| 12 | 2026-08-31 21:09 UTC | Ollama library HTML pages | Archived | Completed | 0 / 0 / 0 / 0 |
| 13 | 2026-09-01 02:31 UTC | Taskbar shortcut for application | Archived | Completed | 0 / 0 / 0 / 0 |
| 14 | 2026-09-01 02:54 UTC | Skill file assessment | Archived | Completed | 0 / 0 / 0 / 1 |
| 15 | 2026-09-03 22:38 UTC | Application remake technical review | Archived | Completed | 0 / 0 / 0 / 0 |
| 16 | 2026-09-14 02:42 UTC | Folder checkout | Archived | Completed | 0 / 0 / 0 / 0 |
| 17 | 2026-09-14 14:30 UTC | elijahs-pc-groovy-wozniak | Archived | Completed | 0 / 0 / 0 / 0 |
| 18 | 2026-09-14 16:59 UTC | Mini games plans | Archived | Completed | 0 / 0 / 0 / 0 |
| 19 | 2026-09-16 18:34 UTC | Blender render | Archived | Completed | 0 / 0 / 0 / 0 |
| 20 | 2026-09-25 18:32 UTC | Artist timeline design | Archived | Completed | 0 / 0 / 0 / 0 |
| 21 | 2026-09-26 04:20 UTC | Broadening artist scope | Archived | Completed | 0 / 0 / 0 / 0 |
| 22 | 2026-09-26 23:46 UTC | HTML redesign with responsive design | Archived | Completed | 0 / 0 / 0 / 0 |
| 23 | 2026-09-28 15:28 UTC | Handoff checklist review | Archived | Completed | 0 / 429 / 5 / 54 |
| 24 | 2026-09-28 15:30 UTC | 404 error investigation | Archived | Completed | 0 / 266 / 4 / 38 |
| 25 | 2026-09-28 15:31 UTC | 3D museum walkthrough | Archived | Completed | 7 / 0 / 0 / 0 |
| 26 | 2026-09-28 18:25 UTC | Museum walkthrough refinement | Archived | Failed | 0 / 199 / 4 / 20 |
| 27 | 2026-09-29 01:36 UTC | Bluetooth Xbox controller museum navigation | Archived | Completed | 0 / 0 / 3 / 2 |
| 28 | 2026-09-30 12:49 UTC | 404 error on site run | Archived | Completed | 0 / 0 / 0 / 5 |
| 29 | 2026-09-30 13:02 UTC | Game bugs and scene revisions | Archived | Completed | 0 / 2 / 3 / 4 |
| 30 | 2026-09-30 13:42 UTC | 3D dining room scene with mobile optimization | Archived | Completed | 7 / 0 / 0 / 0 |
| 31 | 2026-09-30 14:06 UTC | Games choice logic and video playback | Archived | Completed | 0 / 0 / 4 / 4 |
| 32 | 2026-09-30 14:13 UTC | Creative-Headquarters migration plan | Archived | Completed | 0 / 10 / 1 / 16 |
| 33 | 2026-09-30 18:19 UTC | Hold to run video loop bug | Archived | Completed | 0 / 0 / 3 / 2 |
| 34 | 2026-09-30 18:23 UTC | 3D scenes from creative writing vault | Archived | Completed | 7 / 0 / 0 / 0 |
| 35 | 2026-09-30 23:50 UTC | Room refinement and video animations | Archived | Failed | 0 / 0 / 1 / 1 |
| 36 | 2026-10-01 00:08 UTC | Civilization profiles interface redesign | Archived | Completed | 0 / 2 / 1 / 17 |
| 37 | 2026-10-01 01:09 UTC | 3D game environment with Highfield scenes | Archived | Completed | 7 / 0 / 0 / 0 |
| 38 | 2026-10-01 17:58 UTC | Library explore page | Archived | Completed | 0 / 0 / 3 / 3 |
| 39 | 2026-10-01 19:52 UTC | Leader-specific strategy guides | Archived | Completed | 0 / 1 / 1 / 11 |
| 40 | 2026-10-01 22:35 UTC | GitHub Pages file not found | Archived | Failed | 0 / 0 / 1 / 1 |
| 41 | 2026-10-01 22:36 UTC | Creative headquarters deletion | Archived | Completed | 0 / 0 / 1 / 1 |
| 42 | 2026-10-02 04:27 UTC | GitHub Pages build error | Archived | Completed | 0 / 0 / 0 / 0 |
| 43 | 2026-10-02 04:36 UTC | 404 error fix options | Archived | Completed | 0 / 0 / 0 / 0 |
| 44 | 2026-10-03 01:00 UTC | Game scene polish and mechanics | Archived | Failed | 0 / 2 / 2 / 83 |
| 45 | 2026-10-03 01:06 UTC | Interactive 3D scenes and room-specific items | Archived | Completed | 0 / 2 / 1 / 39 |
| 46 | 2026-10-09 20:22 UTC | Import HiggsField assets to AI library | Archived | Completed | 0 / 1 / 1 / 14 |
| 47 | 2026-10-09 23:04 UTC | Who Did It multiplayer game plan | Archived | Completed | 0 / 51 / 0 / 215 |
| 48 | 2026-10-10 19:03 UTC | Gemini-Blender API integration | Archived | Completed | 0 / 13 / 2 / 6 |
| 49 | 2026-10-10 19:05 UTC | WDI A: server and shared (Sonnet) | Archived | Completed | 0 / 20 / 0 / 22 |
| 50 | 2026-10-10 19:05 UTC | WDI B: client and Pages (Sonnet) | Archived | Completed | 0 / 20 / 0 / 22 |
| 51 | 2026-10-10 19:05 UTC | WDI C: content data and rules JSON (Opus) | Archived | Completed | 0 / 20 / 0 / 22 |
| 52 | 2026-10-10 19:05 UTC | WDI D: art direction and asset pipeline (Opus) | Archived | Completed | 0 / 20 / 0 / 22 |
| 53 | 2026-10-10 19:58 UTC | Blender skills plugin | Archived | Completed | 0 / 11 / 2 / 5 |
| 54 | 2026-10-10 22:39 UTC | WDI E: decide the 15 open questions (Opus, plan mode) | Archived | Completed | 0 / 1 / 0 / 14 |
| 55 | 2026-10-10 23:03 UTC | Re-render calibration sheet with ramp fix | Archived | Completed | 0 / 3 / 0 / 17 |
| 56 | 2026-10-10 23:28 UTC | WDI F: M1 finish, shared protocol and Start deals roles (Sonnet) | Archived | Completed | 0 / 3 / 0 / 18 |
| 57 | 2026-10-10 23:28 UTC | WDI G: M2 movement, scene sync and the first house (Sonnet) | Archived | Completed | 0 / 3 / 0 / 18 |
| 58 | 2026-10-10 23:29 UTC | WDI H: villager character art through the render rig (Opus) | Archived | Completed | 0 / 3 / 0 / 18 |
| 59 | 2026-10-10 23:29 UTC | WDI I: UI design system, role cards, lobby and HUD (Fable) | Archived | Completed | 0 / 3 / 0 / 18 |
| 60 | 2026-10-10 23:29 UTC | WDI J: who-did-it studio project in the ROSW repo (Sonnet) | Archived | Completed | 0 / 3 / 0 / 17 |
| 61 | 2026-10-16 04:26 UTC | WDI K: M3 match flow, meetings, votes, win (Sonnet) | Archived | Completed | 0 / 5 / 0 / 26 |
| 62 | 2026-10-16 04:26 UTC | WDI L: M3 kill, bodies, clues, Notebook (Sonnet) | Archived | Completed | 0 / 5 / 0 / 26 |
| 63 | 2026-10-16 04:27 UTC | WDI M: M3 meeting, game over, chat, theme screens (Sonnet) | Archived | Completed | 0 / 5 / 0 / 26 |
| 64 | 2026-10-16 04:27 UTC | WDI N: M3 world actions, clues, HUD theme (Sonnet) | Archived | Completed | 0 / 5 / 0 / 26 |
| 65 | 2026-10-16 04:28 UTC | WDI O: M3 bots, match e2e, soak (Sonnet) | Archived | Completed | 0 / 5 / 0 / 26 |
| 66 | 2026-10-16 04:28 UTC | WDI P: M3 art, props, clues, VFX, body sprite (Opus) | Archived | Completed | 0 / 5 / 0 / 26 |
| 67 | 2026-10-16 04:28 UTC | WDI Q: M3 playtest kit, audio, copy deck (Opus) | Archived | Completed | 0 / 5 / 0 / 26 |
| 68 | 2026-10-16 23:40 UTC | WDI R: quick mode server (Sonnet) | Archived | Completed | 0 / 1 / 0 / 35 |
| 69 | 2026-10-16 23:40 UTC | WDI S: NPC fill server (Sonnet) | Archived | Completed | 0 / 1 / 0 / 35 |
| 70 | 2026-10-16 23:40 UTC | WDI T: quick mode client world (Sonnet) | Archived | Completed | 0 / 1 / 0 / 35 |
| 71 | 2026-10-16 23:40 UTC | WDI U: quick mode meeting and end (Sonnet) | Archived | Completed | 0 / 1 / 0 / 35 |
| 72 | 2026-10-16 23:40 UTC | WDI V: lobby, settings, network edge (Sonnet) | Archived | Completed | 0 / 1 / 0 / 35 |
| 73 | 2026-10-16 23:40 UTC | WDI W: bots, e2e, soak, CI (Sonnet) | Archived | Completed | 0 / 1 / 0 / 35 |
| 74 | 2026-10-16 23:40 UTC | WDI X: art, bakery, loft, placeholders (Opus) | Archived | Completed | 0 / 1 / 0 / 35 |
| 75 | 2026-10-16 23:40 UTC | WDI Y: content, copy, audio, playtest kit (Opus) | Archived | Completed | 0 / 1 / 0 / 35 |
| 76 | 2026-10-18 00:15 UTC | WDI 5A: ONUB v2 rules, server deal and prep (Sonnet) | Archived | Completed | 4 / 9 / 0 / 87 |
| 77 | 2026-10-18 00:15 UTC | WDI 5B: ONUB v2 server night and morning (Sonnet) | Archived | Completed | 4 / 9 / 0 / 87 |
| 78 | 2026-10-18 00:15 UTC | WDI 5C: ONUB v2 client prep, mini-games, deck editor (Sonnet) | Archived | Completed | 7 / 9 / 0 / 87 |
| 79 | 2026-10-18 00:15 UTC | WDI 5D: ONUB v2 client night, morning and results (Sonnet) | Archived | Completed | 10 / 9 / 0 / 87 |
| 80 | 2026-10-18 00:15 UTC | WDI 5E: ONUB v2 bots, NPC brains, e2e and soak (Sonnet) | Archived | Failed | 2 / 9 / 0 / 87 |
| 81 | 2026-10-18 00:15 UTC | WDI 5F: Avatars, public looks, covers, Impersonate (Sonnet) | Archived | Completed | 8 / 9 / 0 / 91 |
| 82 | 2026-10-18 00:16 UTC | WDI 5G: Main deck and Werewolf roles (Sonnet) | Archived | Completed | 5 / 9 / 0 / 87 |
| 83 | 2026-10-18 00:16 UTC | WDI 5H: NPC routines and fixes (Sonnet) | Archived | Failed | 6 / 9 / 0 / 87 |
| 84 | 2026-10-18 00:16 UTC | WDI 5I: Isometric client and lighting (Sonnet) | Archived | Completed | 8 / 9 / 0 / 87 |
| 85 | 2026-10-18 00:16 UTC | WDI 5J: Maps (Opus) | Archived | Completed | 9 / 9 / 0 / 87 |
| 86 | 2026-10-18 00:16 UTC | WDI 5K: World art (Opus) | Archived | Completed | 10 / 9 / 1 / 95 |
| 87 | 2026-10-18 00:16 UTC | WDI 5L: Character art (Opus) | Archived | Completed | 3 / 9 / 0 / 91 |
| 88 | 2026-10-18 00:16 UTC | WDI 5M: ONUB art (Opus) | Archived | Completed | 9 / 9 / 0 / 91 |
| 89 | 2026-10-18 05:25 UTC | Progress report part 2 and Claude usage patterns | Archived | Completed | 0 / 1 / 0 / 26 |
| 90 | 2026-10-18 14:07 UTC | WDI 5N: Art-style switch, 8-bit / Low poly (Sonnet) | Archived | Completed | 0 / 0 / 1 / 16 |
| 91 | 2026-10-21 17:29 UTC | Game features and admin tools planning | Archived | Completed | 0 / 35 / 118 / 335 |
| 92 | 2026-10-21 19:38 UTC | Plugin sound effects upload | Archived | Completed | 0 / 2 / 3 / 26 |
| 93 | 2026-10-22 18:24 UTC | Make the R18 NPC determinism test robust to real clock ticks | Archived | Completed | 0 / 0 / 5 / 20 |
| 94 | 2026-10-22 18:40 UTC | 6A: time scale, auto mode, headless harness, CLI | Archived | Completed | 4 / 0 / 12 / 38 |
| 95 | 2026-10-22 18:41 UTC | 6E: M5b content and GDD 3.14 to 3.16 | Archived | Completed | 5 / 0 / 12 / 38 |
| 96 | 2026-10-22 18:41 UTC | 6J: cutscenes | Archived | Completed | 7 / 0 / 16 / 43 |
| 97 | 2026-10-22 18:41 UTC | 6K: loading, transitions, trailer, budgets | Archived | Completed | 5 / 0 / 7 / 23 |
| 98 | 2026-10-22 18:41 UTC | 6L: music | Archived | Completed | 5 / 0 / 5 / 19 |
| 99 | 2026-10-22 19:24 UTC | 6M: M5b art | Archived | Completed | 4 / 0 / 15 / 32 |
| 100 | 2026-10-22 20:24 UTC | Make onubNight's wire assertions wait for the 422 | Archived | Completed | 0 / 0 / 11 / 26 |
| 101 | 2026-10-22 20:24 UTC | 6B: event bus and invariants | Archived | Completed | 6 / 0 / 13 / 26 |
| 102 | 2026-10-22 20:24 UTC | 6C: GitHub auth and AdminRoom | Archived | Completed | 4 / 0 / 14 / 31 |
| 103 | 2026-10-22 20:24 UTC | 6F: gathering and crafting | Archived | Completed | 3 / 0 / 14 / 26 |
| 104 | 2026-10-22 20:24 UTC | 6G: mobs and dark visibility | Archived | Completed | 4 / 0 / 12 / 26 |
| 105 | 2026-10-22 20:24 UTC | 6H: quests and mini-games | Archived | Completed | 5 / 0 / 14 / 30 |
| 106 | 2026-10-22 20:28 UTC | Make the quick-mode tests wait for wire replies | Archived | Completed | 0 / 0 / 14 / 27 |
| 107 | 2026-10-22 22:05 UTC | 6I: M5b client | Archived | Completed | 4 / 0 / 6 / 13 |
| 108 | 2026-10-22 22:07 UTC | 6D: admin client | Archived | Completed | 4 / 0 / 6 / 8 |
| 109 | 2026-10-22 22:43 UTC | 6N: ROSW media (both repos) | Archived | Completed | 10 / 10 / 22 / 68 |
| 110 | 2026-10-22 23:31 UTC | 6P: round-6 integration | Archived | Completed | 6 / 13 / 54 / 126 |
| 111 | 2026-10-22 23:47 UTC | 6Q: opening cinematic | Archived | Completed | 6 / 5 / 0 / 15 |
| 112 | 2026-10-23 00:42 UTC | ROSW cleanup: Pages workflow failures, open PRs, stale branches | Archived | Completed | 0 / 0 / 1 / 2 |
| 113 | 2026-10-23 04:25 UTC | Railway connection setup | Archived | Completed | 0 / 0 / 1 / 0 |
| 114 | 2026-10-23 07:10 UTC | 7A: map intro tracks and cinematic openings | Archived | Completed | 2 / 8 / 48 / 99 |
| 115 | 2026-10-23 07:24 UTC | 7B: theme pieces (night palette, pixel fonts, glass, backdrop) | Archived | Completed | 8 / 7 / 23 / 66 |
| 116 | 2026-10-23 07:24 UTC | 7D: parties server (open/private, listing, profiles) | Archived | Completed | 3 / 5 / 13 / 36 |
| 117 | 2026-10-23 07:24 UTC | 7H: vendettas (data, server, invariants, GDD 3.20) | Archived | Completed | 1 / 9 / 47 / 101 |
| 118 | 2026-10-23 07:24 UTC | 7I: the Daily Train, the memorial, the Ascended Vicar | Archived | Completed | 0 / 8 / 30 / 78 |
| 119 | 2026-10-23 07:53 UTC | 7C: menu, profile, friends, Quit, party list | Archived | Completed | 3 / 3 / 29 / 69 |
| 120 | 2026-10-23 07:53 UTC | 7E: lobby re-skin (three columns) | Archived | Completed | 3 / 3 / 22 / 64 |
| 121 | 2026-10-23 07:53 UTC | 7F: match screens re-skin (HUD, role card, notebook, M5b, loading) | Archived | Completed | 7 / 2 / 21 / 53 |
| 122 | 2026-10-23 07:53 UTC | 7G: meeting, game over, quick-mode and admin screens re-skin | Archived | Completed | 12 / 3 / 39 / 82 |
| 123 | 2026-10-23 13:13 UTC | 7J: the quick mode's removal | Archived | Completed | 1 / 3 / 32 / 60 |
| 124 | 2026-10-23 13:13 UTC | 7K: Crumb's Ovens' rooms from the owner's station pictures | Archived | Completed | 7 / 3 / 28 / 54 |
| 125 | 2026-10-23 13:35 UTC | Who Did It narrative worldbuilding | Archived | Completed | 0 / 15 / 97 / 242 |
| 126 | 2026-10-23 13:58 UTC | Who Did It UDGT teardown | Archived | Completed | 0 / 11 / 41 / 138 |
| 127 | 2026-10-23 18:16 UTC | 7M: every mini-game and main-mode task assignment | Archived | Failed | 17 / 13 / 88 / 208 |
| 128 | 2026-10-23 19:20 UTC | 8A: Bodies (health, stamina, effects, fists) | Archived | Failed | 13 / 12 / 89 / 215 |
| 129 | 2026-10-23 19:20 UTC | 8B: Inspect and the relations table | Archived | Completed | 5 / 12 / 68 / 187 |
| 130 | 2026-10-23 19:20 UTC | 8C: Scrip (purses, wages, shops, bank, coins) | Archived | Completed | 16 / 14 / 127 / 281 |
| 131 | 2026-10-23 19:20 UTC | 8D: Rent, Faith, rumours, HQ tiers | Archived | Completed | 22 / 14 / 127 / 281 |
| 132 | 2026-10-23 19:20 UTC | 8E: Moods, townsfolk, mugging | Archived | Failed | 42 / 14 / 99 / 247 |
| 133 | 2026-10-23 19:20 UTC | 8F: Characters (redesign, scale, clips) | Archived | Failed | 14 / 12 / 85 / 204 |
| 134 | 2026-10-23 19:20 UTC | 8G: Creatures, resource breaks, VFX, transport | Archived | Completed | 11 / 14 / 104 / 254 |
| 135 | 2026-10-23 19:20 UTC | 8H: Interface motion | Archived | Completed | 13 / 14 / 127 / 281 |
| 136 | 2026-10-23 19:21 UTC | 8I: HD art style | Archived | Failed | 15 / 14 / 99 / 247 |
| 137 | 2026-10-23 19:21 UTC | 8J: HollowMere rooms (placement and detail) | Archived | Completed | 24 / 12 / 98 / 224 |
| 138 | 2026-10-23 19:21 UTC | 8K: BlackPine rooms (placement and detail) | Archived | Completed | 5 / 12 / 77 / 199 |
| 139 | 2026-10-23 21:16 UTC | 8L Anti-cheat (Who Did It round 8) | Archived | Completed | 11 / 4 / 44 / 95 |
| 140 | 2026-10-23 21:16 UTC | 8M Rules (Who Did It round 8) | Archived | Completed | 3 / 5 / 80 / 146 |
| 141 | 2026-10-23 21:16 UTC | 8N Icons (Who Did It round 8) | Archived | Failed | 5 / 7 / 90 / 178 |
| 142 | 2026-10-24 02:03 UTC | 6Z: Who-Did-It orchestrator (round 8) | Archived | Completed | 101 / 17 / 161 / 225 |
| 143 | 2026-10-24 02:58 UTC | 8R: the NPC hive (living world, round 8) | Archived | Completed | 4 / 2 / 57 / 81 |
| 144 | 2026-10-24 02:58 UTC | 8T: meeting notes and NPC talk (living world, round 8) | Archived | Completed | 8 / 4 / 74 / 126 |
| 145 | 2026-10-24 05:03 UTC | 8V: Canon (the lore into the game's names and text) | Archived | Failed | 1 / 2 / 36 / 74 |
| 146 | 2026-10-24 13:11 UTC | 8A (Opus): Bodies (health, stamina, effects, fists) | Archived | Completed | 13 / 2 / 23 / 52 |
| 147 | 2026-10-24 13:11 UTC | 8E (Opus): Moods, townsfolk, mugging | Archived | Completed | 42 / 2 / 29 / 57 |
| 148 | 2026-10-24 13:11 UTC | 8F (Opus): Characters (redesign, scale, clips) | Archived | Completed | 14 / 2 / 16 / 42 |
| 149 | 2026-10-24 13:11 UTC | 8I (Opus): HD art style | Archived | Completed | 15 / 2 / 13 / 41 |
| 150 | 2026-10-24 13:11 UTC | 8N (Opus): Icons | Archived | Completed | 5 / 2 / 11 / 36 |
| 151 | 2026-10-24 13:11 UTC | 7M (Opus): mini-games and stations | Archived | Completed | 17 / 2 / 26 / 57 |
| 152 | 2026-10-24 13:11 UTC | 8V (Opus): Canon (the lore into the game's names and text) | Archived | Completed | 1 / 2 / 10 / 34 |
| 153 | 2026-10-24 15:19 UTC | 8W (Sonnet): shelf pages from the vault | Archived | Completed | 0 / 0 / 15 / 21 |
| 154 | 2026-10-24 19:21 UTC | Fix two intermittent test failures | Archived | Completed | 0 / 0 / 9 / 11 |
| 155 | 2026-10-24 19:39 UTC | 8Y (Sonnet): #243 HollowMere/BlackPine display names | Archived | Completed | 0 / 0 / 8 / 11 |
| 156 | 2026-10-24 19:39 UTC | 8Z (Sonnet): #253 charm save base merge | Archived | Completed | 0 / 0 / 6 / 11 |
| 157 | 2026-10-25 00:08 UTC | 9A (Opus): world mode and phases design | Archived | Completed | 1 / 6 / 6 / 8 |
| 158 | 2026-10-25 00:08 UTC | 9B (Sonnet): logic table and failure messages design | Archived | Completed | 4 / 6 / 6 / 8 |
| 159 | 2026-10-25 00:08 UTC | 9C (Sonnet): living world and emergent play design | Archived | Completed | 2 / 6 / 6 / 8 |
| 160 | 2026-10-25 02:42 UTC | 9D (Opus): fold the owner's answers, GDD map and round-10 plan | Archived | Completed | 7 / 3 / 2 / 8 |
| 161 | 2026-10-25 03:41 UTC | Teardown tool configuration | Archived | Completed | 0 / 91 / 2 / 35 |
| 162 | 2026-10-25 04:37 UTC | 9S (Opus): admin Studio server | Archived | Completed | 4 / 1 / 26 / 35 |
| 163 | 2026-10-25 05:35 UTC | 9T (Sonnet): admin Studio client | Archived | Completed | 6 / 0 / 22 / 29 |
| 164 | 2026-10-25 13:36 UTC | 9U (Sonnet): Studio editor live redraw and material painting | Archived | Completed | 0 / 0 / 15 / 22 |
| 165 | 2026-10-25 13:47 UTC | 9V (Opus): Studio content save and NPC lines as data | Archived | Completed | 0 / 0 / 14 / 22 |
| 166 | 2026-10-25 13:47 UTC | 9W (Sonnet): Studio Overview and NPC editor client | Archived | Completed | 0 / 0 / 15 / 22 |
| 167 | 2026-10-28 19:55 UTC | Tailwind CSS configuration | Archived | Completed | 0 / 89 / 3 / 32 |
| 168 | 2026-10-29 03:45 UTC | Agent reach in plugins repo | Archived | Completed | 0 / 19 / 1 / 11 |
| 169 | 2026-10-29 03:54 UTC | Cloning video-use and clipify repos | Archived | Completed | 0 / 131 / 1 / 28 |
| 170 | 2026-10-29 16:56 UTC | Session autocompact strategy | Archived | Completed | 0 / 61 / 2 / 14 |
| 171 | 2026-10-29 17:27 UTC | 10A (Opus): the slice's contracts | Archived | Completed | 3 / 1401 / 104 / 309 |
| 172 | 2026-10-29 17:27 UTC | 10F (Opus): the logic table | Archived | Completed | 3 / 1766 / 159 / 523 |
| 173 | 2026-10-29 17:27 UTC | 10H (Sonnet): the slice's rules | Archived | Completed | 0 / 1766 / 162 / 523 |
| 174 | 2026-10-29 18:28 UTC | 10G (Sonnet): the refusal sweep | Archived | Completed | 7 / 1401 / 102 / 302 |
| 175 | 2026-10-29 20:22 UTC | 10C (Opus): death's cost and arrivals | Archived | Completed | 3 / 1766 / 164 / 500 |
| 176 | 2026-10-29 21:20 UTC | 10B (Opus): the law | Archived | Completed | 7 / 1401 / 95 / 280 |
| 177 | 2026-10-29 21:34 UTC | 3D asset production pipeline | Archived | Completed | 7 / 1398 / 74 / 227 |
| 178 | 2026-10-29 22:00 UTC | 10D (Sonnet): the living world | Archived | Completed | 0 / 1370 / 153 / 489 |
| 179 | 2026-10-29 22:53 UTC | 11A (Opus): the render pipeline | Archived | Completed | 9 / 509 / 88 / 267 |
| 180 | 2026-10-29 22:53 UTC | 11B (Opus): materials, styles and budgets | Archived | Completed | 10 / 509 / 88 / 267 |
| 181 | 2026-10-30 03:48 UTC | 10X (Fable): fixes, server and rules | Archived | Completed | 13 / 372 / 122 / 414 |
| 182 | 2026-10-30 03:48 UTC | 10Y (Fable): fixes, client and screens | Archived | Completed | 24 / 372 / 122 / 414 |
| 183 | 2026-10-30 05:16 UTC | 10R: role cards and the player dashboard (design) | Archived | Completed | 13 / 5 / 57 / 168 |
| 184 | 2026-10-30 14:03 UTC | 10V (Opus): The missing verbs | Archived | Completed | 14 / 4 / 22 / 59 |
| 185 | 2026-10-30 14:03 UTC | 10S (Opus): The scope census | Archived | Completed | 7 / 369 / 87 / 281 |
| 186 | 2026-10-30 15:32 UTC | 10N: the new roles (round 10, wave 2) | Archived | Completed | 3 / 3 / 11 / 31 |
| 187 | 2026-10-30 15:34 UTC | 10K: kit and the wild (round 10, wave 2) | Archived | Completed | 2 / 3 / 12 / 31 |
| 188 | 2026-10-30 15:35 UTC | 10T: the town (round 10, wave 2) | Archived | Completed | 1 / 367 / 59 / 241 |
| 189 | 2026-10-30 15:35 UTC | 10M: ghosts, talk and modes (round 10, wave 2) | Archived | Completed | 0 / 3 / 11 / 31 |
| 190 | 2026-10-30 20:32 UTC | Backrooms game level Blender blockout | Archived | Completed | 0 / 4 / 0 / 15 |
| 191 | 2026-10-30 20:39 UTC | Pipelines plugin review and expansion plan | Archived | Completed | 0 / 70 / 0 / 2 |
| 192 | 2026-10-31 01:44 UTC | OneDrive to Google Drive migration | Archived | Completed | 0 / 10 / 1 / 23 |
| 193 | 2026-10-31 02:01 UTC | PR 23 review | Archived | Completed | 0 / 0 / 1 / 0 |
| 194 | 2026-10-31 04:57 UTC | Sonnet sessions from roadmap | Archived | Completed | 0 / 10 / 2 / 33 |
| 195 | 2026-10-31 05:17 UTC | W1-A: studio safety (Meshy, hub, compute gate) | Archived | Completed | 0 / 9 / 3 / 33 |
| 196 | 2026-10-31 05:17 UTC | W1-B: plugins and tooling (blender, video-editor, CI) | Archived | Completed | 0 / 9 / 3 / 33 |
| 197 | 2026-10-31 05:17 UTC | W1-C: truth pass and writing pipeline | Archived | Completed | 0 / 9 / 3 / 33 |
| 198 | 2026-10-31 05:17 UTC | W1-D: skills and agents optimization | Archived | Completed | 0 / 9 / 3 / 33 |
| 199 | 2026-10-31 15:43 UTC | MCP server installation issue | Archived | Completed | 0 / 0 / 0 / 0 |
| 200 | 2026-10-31 16:01 UTC | Duplicate folders investigation | Archived | Completed | 0 / 8 / 5 / 13 |
| 201 | 2026-11-01 21:52 UTC | Left trigger controller shift | Archived | Completed | 0 / 0 / 0 / 1 |
| 202 | 2026-11-02 00:12 UTC | Delete remote branches | Archived | Completed | 0 / 0 / 2 / 2 |
| 203 | 2026-11-03 06:27 UTC | Stop asking for it chapter | Archived | Completed | 0 / 0 / 1 / 1 |
| 204 | 2026-11-04 18:37 UTC | Game scenes and level connections | Active | Review ready | 0 / 15 / 55 / 122 |
| 205 | 2026-11-06 04:03 UTC | Story mode | Active | Review ready | 0 / 376 / 106 / 322 |
| 206 | 2026-11-06 04:10 UTC | Story S1: story content and schema | Archived | Completed | 0 / 4 / 9 / 26 |
| 207 | 2026-11-06 04:10 UTC | Story S2: story engine and seat handover | Archived | Completed | 1 / 4 / 10 / 30 |
| 208 | 2026-11-06 04:10 UTC | Story S3: protocol and client cards | Archived | Completed | 10 / 375 / 77 / 272 |
| 209 | 2026-11-06 04:10 UTC | Story S4: tests, replay and bot | Archived | Completed | 9 / 4 / 13 / 32 |
| 210 | 2026-11-06 04:18 UTC | Local gaming chat application | Archived | Completed | 0 / 0 / 0 / 0 |
| 211 | 2026-11-06 19:33 UTC | Story P0: the HollowMere arc (design) | Archived | Completed | 12 / 369 / 64 / 234 |
| 212 | 2026-11-06 19:34 UTC | Story P4: achievements on the device | Archived | Completed | 0 / 1 / 1 / 10 |
| 213 | 2026-11-07 14:55 UTC | Story merge queue: round 10 PRs into the base | Archived | Completed | 0 / 0 / 1 / 5 |
| 214 | 2026-11-07 22:37 UTC | Round 10 B6d2: NPC present-and-file rule | Archived | Completed | 0 / 1 / 5 / 21 |
| 215 | 2026-11-07 22:37 UTC | Round 10 V3: hiding spots (Hide, Check, Burst Out) | Archived | Completed | 0 / 352 / 12 / 45 |
| 216 | 2026-11-07 22:38 UTC | Round 10 V1b: Dust, Compare and Autopsy | Archived | Completed | 0 / 235 / 9 / 41 |
| 217 | 2026-11-07 22:38 UTC | Round 10 V2: cover-up verbs | Archived | Completed | 0 / 352 / 10 / 42 |
| 218 | 2026-11-07 22:38 UTC | Round 10 finish: five skipped PRs | Archived | Completed | 0 / 358 / 48 / 166 |
| 219 | 2026-11-07 22:38 UTC | Story P2: sections engine | Archived | Completed | 1 / 355 / 16 / 64 |
| 220 | 2026-11-07 22:38 UTC | Story P3: client, saves and end screen | Archived | Completed | 7 / 1 / 8 / 37 |
| 221 | 2026-11-07 22:38 UTC | Player accounts: plan first | Archived | Completed | 0 / 1 / 3 / 18 |
| 222 | 2026-11-08 00:36 UTC | Session 2: gate return fix, links from the manifest | Active | Completed | 0 / 368 / 74 / 228 |
| 223 | 2026-11-08 00:37 UTC | Session 3: results v2 (local), deaths, revives, score | Archived | Completed | 0 / 355 / 14 / 51 |
| 224 | 2026-11-08 00:37 UTC | Session 12: tune the Original, starting with B1 | Archived | Completed | 0 / 355 / 13 / 50 |
| 225 | 2026-11-10 20:26 UTC | Session 6: Overworld v0 (parking lot, store doors, options screen) | Archived | Completed | 0 / 2 / 3 / 14 |
| 226 | 2026-11-10 20:26 UTC | Session 7: physics decision and playground prototype | Archived | Completed | 0 / 2 / 3 / 14 |
| 227 | 2026-11-10 20:26 UTC | Session 4: modes and parties (rooms by mode, party key, size 10) | Active | Review ready | 0 / 2 / 3 / 14 |
| 228 | 2026-11-10 20:28 UTC | Blender tools setup | Active | Completed | 0 / 11 / 5 / 14 |
| 229 | 2026-11-10 20:50 UTC | Story R: the Medium's rite and the 10X Vicar | Archived | Completed | 32 / 4 / 43 / 127 |
| 230 | 2026-11-10 21:33 UTC | Session 8: Going back in prototype (one floor, chambers, crossbow) | Archived | Completed | 0 / 0 / 7 / 52 |
| 231 | 2026-11-10 21:33 UTC | Session 9: City v0 on Hallam Row (street, apartment, day clock) | Archived | Completed | 0 / 2 / 33 / 98 |
| 232 | 2026-11-11 00:55 UTC | Session 13: make solo_test deterministic (find the real cause first) | Archived | Completed | 0 / 0 / 5 / 57 |
| 233 | 2026-11-12 01:24 UTC | Session 14: make mp_test deterministic and measure room frame cost | Archived | Completed | 0 / 0 / 2 / 11 |
| 234 | 2026-11-12 13:01 UTC | Creative writing to game adaptation | Active | Review ready | 0 / 13 / 67 / 147 |
| 235 | 2026-11-12 15:25 UTC | Fix timing races in tools/mp_test.mjs | Archived | Completed | 0 / 2 / 26 / 46 |
| 236 | 2026-11-13 21:19 UTC | W3D: walk HollowMere in first person (V2 start) | Archived | Completed | 0 / 1 / 5 / 10 |
| 237 | 2026-11-14 18:48 UTC | Session 15: mp_test, the L4 finale switch race | Archived | Completed | 0 / 0 / 4 / 10 |
| 238 | 2026-11-14 18:49 UTC | Session 16: Going back in in rooms | Archived | Completed | 0 / 0 / 3 / 8 |
| 239 | 2026-11-14 18:49 UTC | Session 17: Overworld and City in rooms, and go to a friend | Archived | Completed | 0 / 0 / 3 / 8 |
| 240 | 2026-11-15 05:11 UTC | Session 18: rules for the arsenal, consumables, dealer items and food | Active | Completed | 0 / 10 / 36 / 92 |
| 241 | 2026-11-15 20:48 UTC | Game chat download and setup | Archived | Completed | 0 / 1 / 0 / 3 |
| 242 | 2026-11-16 03:44 UTC | Fix timing-dependent waits in server tests | Archived | Completed | 0 / 0 / 2 / 5 |
| 243 | 2026-11-17 13:48 UTC | ROSW progress report part 3 | Active | Working | 0 / 268 / 56 / 158 |
| 244 | 2026-11-17 20:21 UTC | Documentation audit plan | Active | Review ready | 0 / 7 / 4 / 12 |
| 245 | 2026-11-19 17:53 UTC | 11D: round 11 decisions (Three.js, model locks) | Archived | Completed | 0 / 6 / 13 / 27 |
| 246 | 2026-11-19 17:53 UTC | 11T: round 11 tooling (Blender CI, render locks) | Archived | Completed | 0 / 6 / 26 / 54 |
| 247 | 2026-11-19 17:53 UTC | 11P: round 11 prop list | Active | Blocked | 3 / 6 / 29 / 57 |
| 248 | 2026-11-19 17:58 UTC | Fix two flaky server tests (mugFlight, manhunt) | Archived | Completed | 0 / 6 / 13 / 27 |
| 249 | 2026-11-19 18:45 UTC | Flake fix for manhunt test | Archived | Completed | 0 / 0 / 2 / 7 |
| 250 | 2026-11-19 19:06 UTC | Round 11 · 11R The renderer | Active | Review ready | 1 / 1 / 21 / 38 |
| 251 | 2026-11-19 19:16 UTC | Check other server tests for sleep-based timing races | Active | Completed | 0 / 1 / 24 / 44 |
| 252 | 2026-11-19 19:42 UTC | Round 11 · 11F Figure sprites | Active | Completed | 4 / 1 / 20 / 39 |
| 253 | 2026-11-19 21:20 UTC | Higgsfield Assets release upload | Active | Blocked | 0 / 7 / 2 / 3 |
| 254 | 2026-11-19 21:56 UTC | Rhino documentary short film | Active | Completed | 0 / 7 / 2 / 3 |
| 255 | 2026-11-19 22:52 UTC | AI MCP tool for pipeline applications | Active | Completed | 0 / 7 / 2 / 3 |
| 256 | 2026-11-20 00:00 UTC | Public SSH key location | Active | Blocked | 0 / 2 / 2 / 2 |
| 257 | 2026-11-20 01:39 UTC | Vast GPU: Dr. Tox build, 1 hour | Active | Working | 0 / 0 / 0 / 0 |

## 7. Questionnaires, handoffs and other items

Every questionnaire, owner-answers file, handoff, status log, round packet and decision log found in the repositories, with the sessions they link to, is in `ROSW_Items.md`.

## 9. Update, 20 November: local sessions and what changed since 17 November

The five sessions below run on the owner's own computer through Remote Control (origin `claude_code_cli`, environment `bridge`). They are the owner-side sessions: the cloud sessions in the earlier sections run in Anthropic containers. All five were rechecked on 20 November by reading their recent events, not only their summaries. The weekly rate-limit info on every one of them reads `allowed_warning` with a reset of 26 November 16:00 UTC, and the owner reports 42% weekly usage.

### Vast GPU: Dr. Tox build, 1 hour (`2026-11-20_vast-gpu-dr-tox-build-1-hour_rj85qwRk.md`)

- State: Running when first checked, finished by the next morning. Model: claude-fable-5-2. Created 2026-11-20 01:39 UTC, last activity 2026-11-20 02:21 UTC.
- What it did: The first live use of the vast plugin. Two one-hour rentals of an RTX 3090 (listed at about nineteen cents an hour) rendered all 370 Blender scenes of the 13 esc-ZINE99 games: 144 build files, 152 blend files and 543 PNG renders, about 1.1 GB, now on the owner's machine, with an HTML gallery. It also opened PR #41, which fixed the faults the live run exposed (merged 20 November, 05:31 UTC). The account was charged $0.54 for about $0.42 of metered hours, because bandwidth and stopped-disk storage are not metered. Instance 61558327 was stopped and kept, which still bills storage until it is destroyed. Another session asked it to push a branch of JPEG contact sheets (renders/vast-first-pass); it was waiting for the owner's go-ahead. [Evidence: its events, the SSH key session's relays, PR #41]
- Spend meter at the first check: $0.02 after five minutes. Budget band up to $1 an hour: 99 of 100 hours left at that point.

### Public SSH key location (`2026-11-20_public-ssh-key-location_F1kW8xwZ.md`)

- State: Idle, waiting on the owner. Model: claude-fable-5-2. Created 2026-11-20 00:00 UTC, last activity 2026-11-20 01:46 UTC.
- What it did: Titled as a question about where the public SSH key lives, it became the coordinator for the Dr. Tox Blender work on the owner's machine. It prepared the hospital-room job on its own branch (claude/hospital-room-blockout), started the Vast GPU sessions, and relayed the esc-ZINE99 queue of 154 locations and 370 scenes across 13 games. The owner told it to scale the building up: if the hospital room would only take a minute, build more scenes. On keys: the owner had set VAST_API_KEY as a Windows environment variable themselves. The first Vast session reported the key as not set only because the Claude app had been running when it was added. The fix offered was to restart the app, or to run docs/setup_keys.py and enter the key on its local page. No key value appears in anything the session recorded; the sessions only reported whether the key was set.
- Its last report: a push of the render contact sheets was waiting for the owner. Context used: 235k of 1M tokens when first checked.

### Rhino documentary short film (`2026-11-19_rhino-documentary-short-film_qYQAuiN8.md`)

- State: Idle, completed. Model: claude-opus-5-5. Created 2026-11-19 21:56 UTC, last activity 2026-11-20 01:21 UTC.
- What it did: Made She Does Not Run, a 2:20 rhino short film, with the video editor, and put its edit in the repository. It fixed a video-editor bug so that every cut is a whole number of frames, which keeps sound and picture in sync. PR #39 merged to Pipelines-Plugin main (main has no required checks, so it merged immediately). The repo gained a films/ folder holding the cut list, finish script and cue sheet, narration script, subtitles, title and end cards, and a README with rebuild steps, with local paths rewritten to relative ones. Release film-she-does-not-run-v5 is public: the 1080p film (92 MB), a 720p copy, subtitles and a zip of the 12 narration lines. The raw clips and edit versions 1 to 4 stay on the owner's machine. Local checks passed: ui-design verify, 180 video-editor tests, 13 docs tests.
- Context used: 533k of 1M tokens when first checked.

### Higgsfield Assets release upload (`2026-11-19_higgsfield-assets-release-upload_NkVwWYfa.md`)

- State: Idle, waiting on the owner. Model: claude-sonnet-5-5. Created 2026-11-19 21:20 UTC, last activity 2026-11-20 00:40 UTC.
- What it did: Published the owner's Higgsfield material as GitHub releases. Six new zips of Greek-god 3D assets (Morpheus, Hypnos, Selene, Nyx, Thanatos, Oneiros, about 4.3 GB) went onto a Higgsfield Assets release on Pipelines-Plugin, with a lookbook PDF and three images, ten assets in all. The 78 GLB models (13 per god) went onto a greek-gods-glb release on Look_Over_There; they are meant to become the Greek-gods rooms in Right Door Wrong Exit. Both repositories are public, so these files are world-readable. A request from the Who-Did-It orchestrator to replace char-models.zip on that repo's char-models release was blocked. The owner gave the go-ahead, but the new zip (126,221,678 bytes) is not on the machine; it is presumably behind a claude.ai file link the session cannot open.
- Context used: 165k of 1M tokens when first checked.

### Blender tools setup (`2026-11-10_blender-tools-setup_HwQQXcDr.md`)

- State: Active again (was paused earlier). Model: claude-opus-5-5. Created 2026-11-10 20:28 UTC, last activity 2026-11-20 02:11 UTC.
- What it did: Working on the HollowMere caves for Who Did It. Its cave-carving tool passed an independent check after five fix rounds and is committed and pushed with 26 passing tests. From a cave section's plan the tool builds the rock, the collision and the crawl, squeeze and climb zones, then walks the result at the player's true body widths and reports traps, unguarded drops, rock too thin between passages, and forced moves that could be skipped. Open items: cracks 0.42 to 0.6 metres wide are not flagged, a crawl ending in a low dome is one-way, and one large test section has too much collision mesh. The cave design is running two more repair rounds, and five cave calls are waiting for the owner to accept or answer one by one. It was created on 10 November and resumed 18 times.
- Context used: 215k of 1M tokens when first checked.

### Counts after the 20 November recheck

- Sessions: 257 (243 on 17 November, 14 new). Archived 239, active 18.
- Archived since 17 November: Flake fix for manhunt test; Fix two flaky server tests (mugFlight, manhunt); 11T round 11 tooling; 11D round 11 decisions; Story P0 (HollowMere arc design); Story S3 (protocol and client cards); Fix timing-dependent waits in server tests.
- New since 17 November: the five local sessions above, AI MCP tool for pipeline applications, Round 11 11F figure sprites, Round 11 11R the renderer, 11P round 11 prop list, Check other server tests for sleep-based timing races, Documentation audit plan, and the two flake-fix sessions.
- Repository activity since 17 November 12:00 UTC: 131 commits in Who-Did-It (56 merges, PR #579 latest), 29 in Earth_Worldbuild, 32 in Look_Over_There, 24 in esc-ZINE99 (Dr. Tox Fall and Dr. Tox Finale built, with 199 code-drawn assets and seven web modes), 18 in Pipelines-Plugin (documentation audit; the vast plugin, PR #38; film She Does Not Run, PR #39).
- Vast.ai: the plugin (`plugins/vast/`) was added with biweekly per-price-band GPU-hour budgets (up to $1/hr 100 h, $1.50 50 h, $2.50 30 h, $5 10 h, $10 4 h per rolling 14 days). Its first live use was on 19 November (two one-hour rentals that rendered 370 scenes); PR #41 then fixed what that run broke. This is the start of the owner's hourly-GPU plan, ahead of the 70 to 80 percent crawl.
