# ROSW Items: questionnaires, handoffs, plans, decision logs and other work products

Generated 20 November 2026 from the eleven repositories. Each entry shows the file, when it first appeared and last changed (git dates, UTC), its size, its title and opening sections, and the sessions it likely belongs to. Session links come from the label in the file path (for example `round11`, `story`) and from time overlap with a session window in the likely repository; they are suggestions, not proof. Session file names refer to `sessions/by_session/`.

Items made on the claude.ai side (published artifacts, forms, chat answers) are not in the repositories and are not listed. The round-11 questionnaire, for example, was answered in a form on claude.ai; its answers were written back to the repo as `owner-answers.md`.

## Questionnaires (3)

### Juniper-Collective: `docs/OPEN-QUESTIONS.md`

- First added: 2026-10-29 03:47; last changed: 2026-10-29 16:55; 721 words
- Title: Open questions
- Sections: The firm and its story; Clients and promise; Offer and money; Launch; Portal (see PORTAL-SPEC.md)
- Questions: 0
- Mentions of "default" (each question carries a proposed default): 0
- Opening: Questions the owner has not answered yet, kept so they can be settled later. Answer them in the two live briefs (answers save there and are read back from them), or tell Claude directly.  - Round one: https://claude.ai/artifact/KcvHi9fw3Vb55a6iKBw7LH - Round two: https://claude.ai/artifact/PxTXeY4ipU1T6owjFomNED  Answered items are not repeated here. Each question says what it unlocks.

### Who-Did-It: `docs/round11/questions.md`

- First added: 2026-10-30 00:08; last changed: 2026-11-08 02:56; 1562 words
- Title: Round 11: questions for the owner
- Sections: Scope: what the makeover covers; Camera and light; Styles and figures; Budgets; Where and how the renders run
- Questions: 22
  - SC1 Which art stays outside Blender? (11A P9, 11B Q10)
  - SC2 Models from Meshy (your ROSW `asset-3d` pipeline) in the shipped art? (11A P7, 11B Q8)
  - SC3 Export every master for V2, the first-person version? (11B Q13)
  - CL1 Keep the camera and the scale exactly as they are? (11A P1)
  - CL2 One light for every style? (11A P2)
  - CL3 Long shadows from buildings, as a ground layer that fades at dusk? (11A P3)
  - CL4 Lamps that light the walls as you carry them? (11A P4, 11B Q14)
  - ST1 Keep all three styles: 8-bit, low poly and HD? (11B Q1)
  - ST2 8-bit figures: flat colour or textured? (11B Q5)
  - ST3 Low-poly figures: flat colour or textured? (11B Q6)
  - ST4 HD figures: how do they fit? (11B Q2)
  - ST5 Render the HD figures under the sky light? (11B Q15)
  - ST6 Texture sizes: 1k maps for every sprite render, with the 2k maps kept for V2? (11B Q11)
  - ST7 A colour check for low poly and HD? (11B Q12)
  - BU1 A memory cap for HD alone? (11B Q3)
  - BU2 The HD download budget? (11B Q4)
  - BU3 The first load: keep the 12 MiB cap, and leave the 8 MiB target for later? (11B Q7)
  - BU4 The test phone and the frame-rate floor? (11B Q9)
  - RN1 Where do the renders run? (11A P5)
  - RN2 HD render quality: 8 samples instead of 32? (11A P5, 11B Q16)
  - RN3 May the cloud environment install Blender for every session? (11A P6)
  - RN4 Keep a copy of the free Kenney model packs as a release download of this repo? (11A P8)
- Mentions of "default" (each question carries a proposed default): 24
- Opening: Round 11's two planning sessions have finished their designs:  - 11A, the render pipeline: [`pipeline.md`](pipeline.md); - 11B, the materials, styles and budgets: [`look.md`](look.md).  These are their questions, 22 in all, in one list. Each has a proposed answer. You can answer **default** (take the
- Sessions that likely produced or used it: 10A (Opus): the slice's contracts (`2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md`); 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10G (Sonnet): the refusal sweep (`2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10B (Opus): the law (`2026-10-29_10b-opus-the-law_B4Hq1Uae.md`); 3D asset production pipeline (`2026-10-29_3d-asset-production-pipeline_9jLDDV7q.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); 11D: round 11 decisions (Three.js, model locks) (`2026-11-19_11d-round-11-decisions-three-js-model-locks_D3d3fjEo.md`); 11T: round 11 tooling (Blender CI, render locks) (`2026-11-19_11t-round-11-tooling-blender-ci-render-locks_E8SszT7j.md`) ...

### Who-Did-It: `docs/story/questions.md`

- First added: 2026-11-06 18:57; last changed: 2026-11-08 02:56; 910 words
- Title: Story mode: the owner's questionnaire
- Sections: A. What shipped, to confirm; B. Rules to settle; C. Content and scope; D. Process; Answers (owner, 2026-11-06)
- Questions: 17
  - A1 Chapter 3 is the Bandit, the outlaw. The Killer card with the `bandit` heist vendetta; the strongbox crack is
  - A2 Chapter 4 is the Activist. The Killer card with the `activist` sabotage vendetta, on day 3. Chosen because it
  - A3 Four chapters, in this order. Baker, Watchman, Bandit, Activist. Chapters play in order; a finished chapter can
  - A4 The chapter looks. The Bandit walks as the `drifter` look and the Activist as the `tinner` look, whatever the
  - B1 A dead player. A death inside a chapter ends it as failed, shows the failed line, and the next chapter still
  - B2 Pausing. The world pauses only while a story card is up (there is no second human to wrong). Multiplayer never
  - B3 Saving. None. A story is one sitting of about 25 minutes of play; leaving ends it.
  - B4 The handover moves the card, not the seat (DECISIONS A415). The player keeps their seat, purse, body and
  - B5 The story's end. After chapter 4 the room ends as a Village win.
  - C1 A fifth Killer chapter. The Zealot (the Skin-Walk, needs a Vicar) or the Hitman (the contract, arrives days 3 to
  - C2 A heist-man chapter on the Thief card. The Thief card is never dealt in a story room today, so the Thief-targeted
  - C3 NPC dialogue. Beats show narration only; the NPCs speak through the existing talk and lore files.
  - C4 Other towns. Port-au-Levain and BlackPine stories (Bible V.1) are out of scope.
  - D1 Playtest. Chapters 3 and 4 ask the player to stand still beside a target unseen. No human has played them; the
  - D2 Achievements. Each chapter end emits `story.chapterEnd` for round 10's E1 (achievements on the device), which
  - D3 The check I did not run. `pnpm auto` at 50 ran on the head before the Killer chapters, and the full server and
  - D4 Production. The base deploys to Railway on every push, so story mode is live.
- Mentions of "default" (each question carries a proposed default): 24
- Opening: Written 2026-11-06 after #463 merged (four chapters on HollowMere). Every question has a proposed default and says where the answer lands. A default holds until you answer. Mark each **Yes**, **No** or write your own.  ## A. What shipped, to confirm  **A1. Chapter 3 is the Bandit, the outlaw.** The Killer card with the `bandit` heist vendetta; the strongbox crack is
- Sessions that likely produced or used it: 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10S (Opus): The scope census (`2026-10-30_10s-opus-the-scope-census_HHeKca4Z.md`); 10T: the town (round 10, wave 2) (`2026-10-30_10t-the-town-round-10-wave-2_934vv6Gw.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`) ...

## Owner answers (2)

### Who-Did-It: `docs/round9/owner-answers.md`

- First added: 2026-10-25 02:42; last changed: 2026-11-08 02:56; 2873 words
- Title: Round 9: the owner's questionnaire answers
- Sections: World mode: dealing, the Killer and the train; The logic table: tools, objects and chests; Failure messages and NFY; The living world: NPCs, systems, gear and achievements; Playing your own way (the rogue); Your newest rules: sleep and busy NPCs
- Answers recorded: 0 ()
- Opening: The owner answered all 54 questions in the round-9 questionnaire (https://claude.ai/artifact/NxXS7U23xjanKdN6paFaNB), saved 2026-10-25T02:40:57.978Z. The answers are reproduced exactly as saved. **Default** means the owner accepted the proposed default. Where the owner chose **Different**, their note is quoted verbatim and replaces the default. These answers override the round-9 design docs wherever the two disagree.  Totals: 42 defaults accepted, 12 answered differently.
- Sessions that likely produced or used it: 6Z: Who-Did-It orchestrator (round 8) (`2026-10-24_6z-who-did-it-orchestrator-round-8_ikPFcTsY.md`); 9A (Opus): world mode and phases design (`2026-10-25_9a-opus-world-mode-and-phases-design_F7m4Q4q3.md`); 9B (Sonnet): logic table and failure messages design (`2026-10-25_9b-sonnet-logic-table-and-failure-messages-desig_VqastJW4.md`); 9C (Sonnet): living world and emergent play design (`2026-10-25_9c-sonnet-living-world-and-emergent-play-design_L3C1yKcZ.md`); 9D (Opus): fold the owner's answers, GDD map and round-10 plan (`2026-10-25_9d-opus-fold-the-owner-s-answers-gdd-map-and-rou_eULqTHCR.md`); 9S (Opus): admin Studio server (`2026-10-25_9s-opus-admin-studio-server_WNiGeGNN.md`); 9T (Sonnet): admin Studio client (`2026-10-25_9t-sonnet-admin-studio-client_snhP4uMS.md`); 9U (Sonnet): Studio editor live redraw and material painting (`2026-10-25_9u-sonnet-studio-editor-live-redraw-and-material_7Fpud5aa.md`); 9V (Opus): Studio content save and NPC lines as data (`2026-10-25_9v-opus-studio-content-save-and-npc-lines-as-dat_cXWGZc9e.md`); 9W (Sonnet): Studio Overview and NPC editor client (`2026-10-25_9w-sonnet-studio-overview-and-npc-editor-client_YzfkEGXi.md`)

### Who-Did-It: `docs/round11/owner-answers.md`

- First added: 2026-10-30 04:28; last changed: 2026-11-20 00:40; 708 words
- Title: Round 11: the owner's answers
- Sections: CL3: the long shadows come in round 11; The plan approved (2026-10-30); What three defaults still need from the owner
- Answers recorded: 22 (default 21, different 1)
- Opening: The owner answered all 22 questions of [`questions.md`](questions.md) in the form (https://claude.ai/artifact/KTRrtfV3aRGprcyspSMM1E) and submitted it at 2026-10-30T03:37:26.649Z. **Default** means the owner took the proposed default in `questions.md`. The one **different** answer quotes the owner's note verbatim, and it replaces the default. These answers win over `pipeline.md` and `look.md` wherever they disagree.
- Sessions that likely produced or used it: 10A (Opus): the slice's contracts (`2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md`); 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10G (Sonnet): the refusal sweep (`2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10B (Opus): the law (`2026-10-29_10b-opus-the-law_B4Hq1Uae.md`); 3D asset production pipeline (`2026-10-29_3d-asset-production-pipeline_9jLDDV7q.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`) ...

## Orchestrator handoffs (19)

### Earth_Worldbuild: `_Museum/blender/scripts/V2_HANDOFF.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:53; 1115 words
- Title: Hyper-Realism Pass v2: handoff (updated 2026-09-28 09:05)
- Sections: Why we stopped; Done; Findings to carry forward; Next steps (in order)
- Opening: # Hyper-Realism Pass v2: handoff (updated 2026-09-28 09:05)  The plan: the pasted "Hyper-Realism Pass — Chronicle Museum (v2)" (Phases 0–5, with a user review gate after Phase 2). **The agent contract, `V2_CONTRACT.md` (same folder), is the spec.** Read it first. This file records state and next steps.

### Earth_Worldbuild: `_RAG/HANDOFF.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 19:56; 2845 words
- Title: Handoff: Earth Chronicle source re-read (Tiers 1-5 done, Tier 6 next)
- Sections: Current state (2026-11-19, after Tier 5); Why this exists; State; Policy A (agreed with the user on 2026-09-26, use it for Tiers 4-6); Tier 5 plan (mixed reference sites); Tier 6 plan; Working loop per tier; Tool reference (`_RAG/tools/`, documented in `_RAG/README.md`); Rules and gotchas that cost time; Report format at the end of each tier; Tier 5 progress (historical: the 2026-09-28 state of the first pass; Tier 5 was applied on 2026-11-19, see _RAG/HANDOFF_Tier5.md)
- Opening: Updated 2026-09-27 about 11:10 EDT; current state checked against the files and git log on 2026-11-19 (section below).  ## Current state (2026-11-19, after Tier 5) - **Tier 5 is applied** (2026-11-19, a second pass in a cloud sandbox, because the first pass's cache stayed on the owner's machine). Result and what is left: `_RAG/HANDOFF_Tier5.md`. In short: of the 126 Tier 5 queue entries, 77 were re-read and updated, 40 could not be read and are `summary-only` with a `blocked` Caveat, 7 were left

### Earth_Worldbuild: `_RAG/HANDOFF_Tier5.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 19:56; 2314 words
- Title: Handoff: Tier 5 of the source re-read (written 2026-09-28; applied 2026-11-19)
- Sections: Result (2026-11-19): Tier 5 is applied; To finish Tier 5 where the pages can be read; The first pass (2026-09-28), kept for the record; Current state before the apply (checked 2026-11-19, superseded by the Result above); State in one paragraph; What exists now; The main finding; Remaining steps, in order; Judgment calls already made (say them in the report); Gotchas hit this session
- Opening: ## Result (2026-11-19): Tier 5 is applied The first pass's cache (2026-09-27/28) never left the owner's machine, so a second pass re-fetched everything in a cloud sandbox and applied the patch. `helpers/tier5_manual.py` keeps the first pass's patch unchanged and adds a section "the second pass, 2026-11-19" that filters it to the pages this pass actually read; nothing written rests on a page this pass did not read. - **Network this time.** worldhistory.org answered HTTP 403 (Cloudflare) and the W

### Earth_Worldbuild: `_RAG/handoff/Brief1_Handoff.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 6212 words
- Title: Handoff: Earth Chronicle Brief 1 (People + Peoples & Cultures)
- Sections: 0. Where things stand; 1. Message to paste; 2. Ledger; 3. Batch procedure (run after every batch of 8); 4. Decisions already taken (stay consistent); 5. House rules digest (full text is in the original brief); 6. Plan; 7. Watch-outs; 8. Done criteria; 9. Live Cultures plan (written 2026-09-27 evening; supersedes 2.3 and the candidate lists above)
- Opening: # Handoff: Earth Chronicle Brief 1 (People + Peoples & Cultures)  Prepared 2026-09-26; ledger updated after People Batch 6 (2026-09-26 14:15). Section 1 is the message to paste into the new chat. The rest is reference the new chat will read from this file.  **Batch 6 and Batch 7 are DONE.** Batch 7 (2026-09-27, ~14:40): Frida Kahlo, Kate Sheppard, Sacagawea, Ho Chi Minh, Sukarno, Kamehameha I, Vitus Bering, Sun Yat-sen. Validated at 0 errors, hubs and index already current (another session had r

### Earth_Worldbuild: `_RAG/handoff/Brief3_Handoff.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 1744 words
- Title: Brief 3 (Technologies and Themes) - handoff, written 2026-09-27
- Sections: State; Per-batch procedure that worked (Batches 3-6); Conventions settled; Part B remaining (columns: title | date_start | era | region | themes | confidence | key facts and cautions); Part C: 18 essays in `05_Observer_Notes/`, batches 4, 4, 4, 4, 2
- Opening: # Brief 3 (Technologies and Themes) - handoff, written 2026-09-27  The earlier Desktop bundle (`EarthChronicle_Brief3_Handoff\`) no longer exists (not deleted by Claude; the Desktop copy of Brief 4's briefs is gone too). This file replaces it. House rules: `EarthChronicle_Brief3_Technologies_and_Themes.md` (copied beside this file if the temp copy survived; otherwise ask the user to re-attach it). Scripts: `brief3_tools\`.  ## State

### Earth_Worldbuild: `_RAG/handoff/EarthChronicle_Brief1_People_and_Peoples-Cultures.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3426 words
- Title: BRIEF 1 of 4: People and Peoples & Cultures
- Sections: MISSION; WHAT IS THIN TODAY (measured); COVERAGE RULES; CANDIDATES (suggestions; choose about 100 per category, add others if a gap remains, skip anything under EXISTING TITLES); AUTHORING NOTES; EXAMPLE 1 (person; match this length and tone); Summary; Facts; Context & Connections; Observer's Reading; Open Questions; EXAMPLE 2 (culture)
- Opening: # BRIEF 1 of 4: People and Peoples & Cultures  Paste this whole brief into a new Claude chat, then send: "Start batch 1."  ## MISSION

### Earth_Worldbuild: `_RAG/handoff/EarthChronicle_Brief2_Places_and_Species.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3144 words
- Title: BRIEF 2 of 4: Places and Species
- Sections: MISSION; WHAT IS THIN TODAY (measured); COVERAGE RULES; CANDIDATES (suggestions; choose about 70 places and about 40 species, add others if a gap remains, skip anything under EXISTING TITLES); AUTHORING NOTES; EXAMPLE 1 (place); Summary; Facts; Context & Connections; Observer's Reading; Open Questions; EXAMPLE 2 (species; structure only. Deep-time species like this one belong to Brief 4, so do not write it)
- Opening: # BRIEF 2 of 4: Places and Species  Paste this whole brief into a new Claude chat, then send: "Start batch 1."  ## MISSION

### Earth_Worldbuild: `_RAG/handoff/EarthChronicle_Brief3_Technologies_and_Themes.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3837 words
- Title: BRIEF 3 of 4: Technologies and Themes
- Sections: MISSION; WHAT IS THIN TODAY (measured); PART A: HUB REWRITE RULES; PART B: TECHNOLOGY COVERAGE RULES; PART B CANDIDATES (suggestions; choose about 65, skip anything under EXISTING TITLES); PART C: ESSAY RULES; EXAMPLE 1 (technology); Summary; Facts; Context & Connections; Observer's Reading; Open Questions
- Opening: # BRIEF 3 of 4: Technologies and Themes  Paste this whole brief into a new Claude chat, then send: "Start Part A."  ## MISSION

### Earth_Worldbuild: `_RAG/handoff/HANDOFF_Art_Section_Expansion.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 2971 words
- Title: Art Section Expansion: handoff
- Sections: READ FIRST; CURRENT STATE (checked 2026-11-19); STATE (2026-09-28); WHAT IS LEFT (in order); DECISIONS (settled; do not reopen); WORKFLOW; CONVENTIONS; CAUTIONS; DO NOT; END-STATE WORK (near the end of the project); BACKLOG OF CLAIMS WRITTEN FROM MEMORY; RESUME MESSAGE (paste-ready)
- Opening: You are continuing the expansion of the vault's named-artist section from 53 to about 203 `artist` notes (about +150), plus about 25 movement notes. Work directly in the vault. Do NOT re-derive decisions recorded below.  ## READ FIRST 1. This file, then `_RAG/handoff/art_expansion_ledger.csv` (the candidate pool, statuses, batches; source of truth for progress). 2. Project memory `art-section-expansion.md` (auto-loaded) and `art-talk-integration.md` (how the original 53 were built).

### Earth_Worldbuild: `_RAG/handoff/HANDOFF_Brief1_Cultures_Remaining.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 2285 words
- Title: Handoff: Brief 1 Peoples & Cultures, what is left (written 2026-09-28)
- Sections: 1. State right now; 2. What the pilot taught (use before launching the rest); 3. The reusable script; 4. Remaining batches (78 planned minus 8 done = 70 titles; re-check every title with `find . -iname "Title.md" -not -path "./_RAG/*"` at write time); 5. After the batches; 6. Standing rules and cautions (unchanged)
- Opening: # Handoff: Brief 1 Peoples & Cultures, what is left (written 2026-09-28)  Stopped on the user's request after the Batch 3 pilot finished. **Nothing is running** (no background agents, no open workflow). Read this file first, then `Brief1_Handoff.md` sections 4, 5 and 9 for the house rules and the batch plan. This file supersedes section 9's status lines.  ## 1. State right now

### Earth_Worldbuild: `_RAG/handoff/HANDOFF_Brief2_Places_and_Species.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3853 words
- Title: (none)
- Opening: READ FIRST 1. _RAG/handoff/EarthChronicle_Brief2_Places_and_Species.md: authoritative house rules (Two-Layer Rule, Observer voice and the 14 allowed Observer terms, file format, dates, truthfulness, allowed sources, existing-titles lists). Where this prompt and the brief differ, this prompt wins on workflow (below); the brief wins on content rules. 2. Project memory earth-chronicle-expansion-briefs.md (auto-loaded) for the four-brief partition and the -11,700 ownership rule.  CURRENT STATE (chec

### Earth_Worldbuild: `_RAG/handoff/factcheck_sweep_status.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 1538 words
- Title: Handoff: fact-check + image sweep (stopped 2026-09-28 by the user's request)
- Sections: Goal and decisions already made by the user; Current state (checked 2026-11-19); State at stop (2026-09-28); Tools (`_RAG/tools/`); Recipe for one batch (about 30 minutes wall clock); Lessons and hazards; Frontmatter dates deliberately left for the user's decision; Not part of this sweep; Final numbers
- Opening: Paths are relative to the vault root `C:\Users\utopi\OneDrive\Desktop\Earth _WorldBuilding`. Use `_RAG/.venv/Scripts/python.exe` for every script and set `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` (accented titles crash cp1252). Memory note: `factcheck-image-sweep`.  ## Goal and decisions already made by the user Give every entity/era/region note a cited `fact_checks` list (fixing any wrong or unsupported text found), give every content note at least one credited image, then push to the site (`_Site/

### Earth_Worldbuild: `_Rewrite/HANDOFF.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:53; 588 words
- Title: Rewrite layer handoff (stopped 2026-09-28; state updated 2026-11-19)
- Sections: Where it stands (2026-11-19); How to resume; Voice mix (2026-11-19); Things to know
- Opening: ## Where it stands (2026-11-19)  | Target | Rewritten | Left | |---|---|---| | Site notes | **1,660 of 1,660, done** | none; 0 stale |

### Who-Did-It: `docs/round10/handoffs/10A-plans.md`

- First added: 2026-10-30 16:41; last changed: 2026-11-08 02:56; 1050 words
- Title: 10A's plans for K1 and T4, with 6Z's answers
- Sections: K1. Weapons (I24), after C6; T4. Town work, windows, stations and silhouettes (I37, I38, I39; row 30), after C4c and C4d; Code read at 23cf829d; Branches
- Opening: 10A wrote these plans on 2026-10-30, before the stop, and sent them to 6Z in its handoff; nothing here is built. They were read on the base at 23cf829d against: - `scope.md` 0, 2.5, 2.6, 3 and 4; - `seams.md` 3, rows 25 to 34, and 6; - `docs/round9/logic-table.md` 8.3;
- Sessions that likely produced or used it: 10A (Opus): the slice's contracts (`2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md`); 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10G (Sonnet): the refusal sweep (`2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10B (Opus): the law (`2026-10-29_10b-opus-the-law_B4Hq1Uae.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10R: role cards and the player dashboard (design) (`2026-10-30_10r-role-cards-and-the-player-dashboard-design_CAKKzVuL.md`) ...

### Who-Did-It: `docs/story/orchestrator-handoff.md`

- First added: 2026-11-10 19:20; last changed: 2026-11-19 15:49; 2116 words
- Title: Story mode part 2: orchestrator handoff
- Sections: Standing rules from the owner; Open decisions (owner only); The Vicar design that was agreed; Merges that wait for the owner; Round-10 lanes the orchestrator owns (2026-11-12); Sessions; Archival routine; On hold; Art; Resuming
- Opening: > **Status, 2026-11-19:** Kept as written on 2026-11-10 to 2026-11-12. Since then `claude/story-part2` merged into the base > with #538 (2026-11-12), so "nothing from `claude/story-part2` has gone to the production base" no longer holds; the round-10 > pull requests it lists as open all merged by 2026-11-12, and #245 was closed. `docs/SESSIONS.md`, "After round 11's plan", has the lanes since.  Written 2026-11-10 (updated 2026-11-12 after #521 and the finisher's third grant) by the orchestrator 
- Sessions that likely produced or used it: 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10S (Opus): The scope census (`2026-10-30_10s-opus-the-scope-census_HHeKca4Z.md`); 10T: the town (round 10, wave 2) (`2026-10-30_10t-the-town-round-10-wave-2_934vv6Gw.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`) ...

### Who-Did-It: `docs/round11/handoff/prop-models.md`

- First added: 2026-11-19 17:51; last changed: 2026-11-19 17:51; 457 words
- Title: Who Did It: 3D asset index
- Sections: Contents; Conventions; Props: what each is for; Known gaps and flags
- Opening: For the local Blender session. Machine-readable version: `index.json`.  ## Contents  | Folder | Count | What |
- Sessions that likely produced or used it: 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`); Story P0: the HollowMere arc (design) (`2026-11-06_story-p0-the-hollowmere-arc-design_B7eQSKQ5.md`); Session 2: gate return fix, links from the manifest (`2026-11-08_session-2-gate-return-fix-links-from-the-manifes_WrLpinA4.md`); Creative writing to game adaptation (`2026-11-12_creative-writing-to-game-adaptation_rkcmWq1a.md`); Session 18: rules for the arsenal, consumables, dealer items and food (`2026-11-15_session-18-rules-for-the-arsenal-consumables-dea_dfok53Yk.md`); 11D: round 11 decisions (Three.js, model locks) (`2026-11-19_11d-round-11-decisions-three-js-model-locks_D3d3fjEo.md`); 11T: round 11 tooling (Blender CI, render locks) (`2026-11-19_11t-round-11-tooling-blender-ci-render-locks_E8SszT7j.md`); 11P: round 11 prop list (`2026-11-19_11p-round-11-prop-list_sgQGbvMg.md`); Fix two flaky server tests (mugFlight, manhunt) (`2026-11-19_fix-two-flaky-server-tests-mugflight-manhunt_e4njLyha.md`)

### Earth_Worldbuild: `_RAG/handoff/tier5-sandbox-2026-11-19/README.md`

- First added: 2026-11-19 19:56; last changed: 2026-11-19 19:56; 110 words
- Title: Tier 5 logs from the cloud session of 2026-11-19
- Opening: Tier 5 was re-fetched and applied in a cloud session, where `_RAG/source_cache/` (git-ignored) started empty. These are that session's logs, kept here because the cache does not survive the session:  - `discrepancies.md`: the Tier 5 entries only (10). - `unresolved.md`: the Tier 5 entries (61) and the "Tier 5 deferred" list.

### Earth_Worldbuild: `_RAG/handoff/tier5-sandbox-2026-11-19/discrepancies.md`

- First added: 2026-11-19 19:56; last changed: 2026-11-19 19:56; 548 words
- Title: Discrepancies found while re-reading sources
- Sections: 2026-11-19
- Opening: ## 2026-11-19 - **Alexander the Great** vs [Wikipedia on Alexander the Great]: was: died 13 June 323 BCE | source text: The article gives 20 or 21 July 356 BC to 10 or 11 June 323 BC. | action: Check corrected to 10 or 11 June 323 BC and re-pointed to the article; the note body gives no day. - **Maurya Empire** vs [National Geographic on the Mauryan Empire]: was: Maurya Empire 322-185 BCE | source text: The page says the empire was founded around 321 BCE and was 321-185 BCE. | action: Check narr

### Earth_Worldbuild: `_RAG/handoff/tier5-sandbox-2026-11-19/unresolved.md`

- First added: 2026-11-19 19:56; last changed: 2026-11-19 19:56; 2353 words
- Title: Unresolved claims
- Sections: Tier 5 (2026-11-19)
- Opening: Claims that stay in a note although the page cited for them does not contain them. This file was started fresh on 2026-11-19 in a cloud sandbox; the Tier 1-4 sections are in the copy on the owner's machine.  ## Tier 5 (2026-11-19) - **Iron Age; Alphabet**: Proto-Sinaitic about 1800 BCE [cited to Wikipedia on the Phoenician Alphabet] - **Neolithic; The Agricultural Revolution**: Independent centers of agriculture in China, Mesoamerica and South America; the 'Southwest Asia' wording [cited to EBSC

## Status logs (1)

### Who-Did-It: `docs/story/status.md`

- First added: 2026-11-06 04:10; last changed: 2026-11-19 15:47; 5270 words
- Title: Story mode: status
- Sections: S1. Story content; S2. Story engine; S3. Wire and client; S4. Tests and the bot; Session ids (2026-11-06, from 6Z's spawn); P4. Achievements (E1); P0. The arc (part 2); P1. The section schema; P2. Engine (part 2); P3. Story client (part 2); R. The rite
- Opening: Each session appends to its own section only. Newest line last.  > **Status, 2026-11-19:** `claude/story-part2` merged into the base with #538 (2026-11-12), so every pull request > logged below as merged into `claude/story-part2` is on the base. Still waiting: R8's `story.json` entry, P5 and P6, on > the map revamp (`docs/map-revamp/interiors-plan.md`); player sign-in (`docs/accounts/plan.md`) is not built.
- Sessions that likely produced or used it: 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10S (Opus): The scope census (`2026-10-30_10s-opus-the-scope-census_HHeKca4Z.md`); 10T: the town (round 10, wave 2) (`2026-10-30_10t-the-town-round-10-wave-2_934vv6Gw.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`) ...

## Session contracts, plans, briefs, seams and scope documents (35)

### Earth_Worldbuild: `03_Entities/Artifacts-Technologies/Microscope.md`

- First added: 2026-09-28 13:21; last changed: 2026-09-28 13:21; 316 words
- Title: (none)
- Sections: Summary; Facts; Context & Connections; Observer's Reading; Open Questions

### Earth_Worldbuild: `03_Entities/Artifacts-Technologies/Seismoscope.md`

- First added: 2026-09-28 13:21; last changed: 2026-09-28 13:21; 331 words
- Title: (none)
- Sections: Summary; Facts; Context & Connections; Observer's Reading; Open Questions

### Earth_Worldbuild: `03_Entities/Artifacts-Technologies/Telescope.md`

- First added: 2026-09-28 13:21; last changed: 2026-09-28 13:21; 325 words
- Title: (none)
- Sections: Summary; Facts; Context & Connections; Observer's Reading; Open Questions

### Earth_Worldbuild: `_RAG/handoff/Brief1_Handoff.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 6212 words
- Title: Handoff: Earth Chronicle Brief 1 (People + Peoples & Cultures)
- Sections: 0. Where things stand; 1. Message to paste; 2. Ledger; 3. Batch procedure (run after every batch of 8); 4. Decisions already taken (stay consistent); 5. House rules digest (full text is in the original brief); 6. Plan; 7. Watch-outs; 8. Done criteria; 9. Live Cultures plan (written 2026-09-27 evening; supersedes 2.3 and the candidate lists above)

### Earth_Worldbuild: `_RAG/handoff/Brief3_Handoff.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 1744 words
- Title: Brief 3 (Technologies and Themes) - handoff, written 2026-09-27
- Sections: State; Per-batch procedure that worked (Batches 3-6); Conventions settled; Part B remaining (columns: title | date_start | era | region | themes | confidence | key facts and cautions); Part C: 18 essays in `05_Observer_Notes/`, batches 4, 4, 4, 4, 2

### Earth_Worldbuild: `_RAG/handoff/EarthChronicle_Brief1_People_and_Peoples-Cultures.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3426 words
- Title: BRIEF 1 of 4: People and Peoples & Cultures
- Sections: MISSION; WHAT IS THIN TODAY (measured); COVERAGE RULES; CANDIDATES (suggestions; choose about 100 per category, add others if a gap remains, skip anything under EXISTING TITLES); AUTHORING NOTES; EXAMPLE 1 (person; match this length and tone); Summary; Facts; Context & Connections; Observer's Reading; Open Questions; EXAMPLE 2 (culture)

### Earth_Worldbuild: `_RAG/handoff/EarthChronicle_Brief2_Places_and_Species.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3144 words
- Title: BRIEF 2 of 4: Places and Species
- Sections: MISSION; WHAT IS THIN TODAY (measured); COVERAGE RULES; CANDIDATES (suggestions; choose about 70 places and about 40 species, add others if a gap remains, skip anything under EXISTING TITLES); AUTHORING NOTES; EXAMPLE 1 (place); Summary; Facts; Context & Connections; Observer's Reading; Open Questions; EXAMPLE 2 (species; structure only. Deep-time species like this one belong to Brief 4, so do not write it)

### Earth_Worldbuild: `_RAG/handoff/EarthChronicle_Brief3_Technologies_and_Themes.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3837 words
- Title: BRIEF 3 of 4: Technologies and Themes
- Sections: MISSION; WHAT IS THIN TODAY (measured); PART A: HUB REWRITE RULES; PART B: TECHNOLOGY COVERAGE RULES; PART B CANDIDATES (suggestions; choose about 65, skip anything under EXISTING TITLES); PART C: ESSAY RULES; EXAMPLE 1 (technology); Summary; Facts; Context & Connections; Observer's Reading; Open Questions

### Earth_Worldbuild: `_RAG/handoff/HANDOFF_Brief1_Cultures_Remaining.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 2285 words
- Title: Handoff: Brief 1 Peoples & Cultures, what is left (written 2026-09-28)
- Sections: 1. State right now; 2. What the pilot taught (use before launching the rest); 3. The reusable script; 4. Remaining batches (78 planned minus 8 done = 70 titles; re-check every title with `find . -iname "Title.md" -not -path "./_RAG/*"` at write time); 5. After the batches; 6. Standing rules and cautions (unchanged)

### Earth_Worldbuild: `_RAG/handoff/HANDOFF_Brief2_Places_and_Species.md`

- First added: 2026-09-28 13:21; last changed: 2026-11-19 15:52; 3853 words
- Title: (none)

### Who-Did-It: `docs/MASTER_PLAN.md`

- First added: 2026-10-10 00:29; last changed: 2026-11-19 15:47; 13401 words
- Title: Who Did It — Master Plan (V1 top-down 2.5D, V2 first-person)
- Sections: 1. Vision & pillars; 2. Player experience: the first 10 minutes; 3. Game design; 4. World bible; 5. Technical architecture; 6. Asset pipeline & style guide; 7. Production plan; 8. Decisions & changes from review; 9. Open questions for the owner
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`)

### Who-Did-It: `docs/ROADMAP.md`

- First added: 2026-10-10 00:29; last changed: 2026-11-19 17:37; 5329 words
- Title: Production Plan
- Sections: 7. Production plan
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`)

### Who-Did-It: `docs/SESSIONS.md`

- First added: 2026-10-10 19:04; last changed: 2026-11-19 23:58; 65796 words
- Title: Parallel sessions (started 2026-10-10)
- Sections: Branches and pull requests; Interfaces between sessions; Briefs; Integration log (2026-10-10); Round 2 (started 2026-10-10, after PRs #1 to #6 merged); Integration log, round 2 (2026-10-15); Round 3 (started 2026-10-16, after round 2 landed at a98cc3f); Integration log, round 3 (2026-10-16); Round 4 (started 2026-10-16, after round 3 landed at 2f829e2); Integration log, round 4 (2026-10-17); Round 5 (started 2026-10-17, after round 4 landed at a0850ba); Round 6 (started 2026-10-22, after round 5 landed at a60d855)
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI A: server and shared (Sonnet) (`2026-10-10_wdi-a-server-and-shared-sonnet_35fr1sDn.md`); WDI B: client and Pages (Sonnet) (`2026-10-10_wdi-b-client-and-pages-sonnet_3xczv45i.md`); WDI C: content data and rules JSON (Opus) (`2026-10-10_wdi-c-content-data-and-rules-json-opus_PNGDvr2H.md`); WDI D: art direction and asset pipeline (Opus) (`2026-10-10_wdi-d-art-direction-and-asset-pipeline-opus_4PUsGq3H.md`)

### Who-Did-It: `docs/PROTOCOL.md`

- First added: 2026-10-10 23:46; last changed: 2026-11-11 23:11; 4989 words
- Title: Wire protocol
- Sections: Client to server; Server to client; Payload types; Admin (WDI_ADMIN only); Studio (WDI_ADMIN only); Error codes; Refusal reasons; Join errors
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI E: decide the 15 open questions (Opus, plan mode) (`2026-10-10_wdi-e-decide-the-15-open-questions-opus-plan-mod_zB8M67nc.md`); Re-render calibration sheet with ramp fix (`2026-10-10_re-render-calibration-sheet-with-ramp-fix_TSu8a5sD.md`); WDI F: M1 finish, shared protocol and Start deals roles (Sonnet) (`2026-10-10_wdi-f-m1-finish-shared-protocol-and-start-deals_2QDQKJDy.md`); WDI G: M2 movement, scene sync and the first house (Sonnet) (`2026-10-10_wdi-g-m2-movement-scene-sync-and-the-first-house_w7ymx3Ab.md`); WDI H: villager character art through the render rig (Opus) (`2026-10-10_wdi-h-villager-character-art-through-the-render_DwoyNhwh.md`); WDI I: UI design system, role cards, lobby and HUD (Fable) (`2026-10-10_wdi-i-ui-design-system-role-cards-lobby-and-hud_jjiZozRk.md`); WDI J: who-did-it studio project in the ROSW repo (Sonnet) (`2026-10-10_wdi-j-who-did-it-studio-project-in-the-rosw-repo_JzHw9dat.md`)

### Who-Did-It: `docs/round5/owner-brief.md`

- First added: 2026-10-17 19:00; last changed: 2026-11-19 15:47; 2999 words
- Title: Round 5: the owner's brief and ONUB spec (2026-10-17, verbatim)
- Sections: The brief; The ONUB spec
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI 5A: ONUB v2 rules, server deal and prep (Sonnet) (`2026-10-18_wdi-5a-onub-v2-rules-server-deal-and-prep-sonnet_Z1vSLdZ1.md`); WDI 5B: ONUB v2 server night and morning (Sonnet) (`2026-10-18_wdi-5b-onub-v2-server-night-and-morning-sonnet_oBDxMbRQ.md`); WDI 5C: ONUB v2 client prep, mini-games, deck editor (Sonnet) (`2026-10-18_wdi-5c-onub-v2-client-prep-mini-games-deck-edito_ZsrCwyaj.md`); WDI 5D: ONUB v2 client night, morning and results (Sonnet) (`2026-10-18_wdi-5d-onub-v2-client-night-morning-and-results_ZCVGvCem.md`); WDI 5E: ONUB v2 bots, NPC brains, e2e and soak (Sonnet) (`2026-10-18_wdi-5e-onub-v2-bots-npc-brains-e2e-and-soak-sonn_eAxjQMH2.md`); WDI 5F: Avatars, public looks, covers, Impersonate (Sonnet) (`2026-10-18_wdi-5f-avatars-public-looks-covers-impersonate-s_RU6tDKSs.md`); WDI 5G: Main deck and Werewolf roles (Sonnet) (`2026-10-18_wdi-5g-main-deck-and-werewolf-roles-sonnet_89i5n6pV.md`); WDI 5H: NPC routines and fixes (Sonnet) (`2026-10-18_wdi-5h-npc-routines-and-fixes-sonnet_V4W1hNxi.md`); WDI 5I: Isometric client and lighting (Sonnet) (`2026-10-18_wdi-5i-isometric-client-and-lighting-sonnet_5ESH86KS.md`); WDI 5J: Maps (Opus) (`2026-10-18_wdi-5j-maps-opus_3horF2Bn.md`); WDI 5K: World art (Opus) (`2026-10-18_wdi-5k-world-art-opus_syVMk7J3.md`) ...

### Who-Did-It: `docs/round5/seams.md`

- First added: 2026-10-18 00:13; last changed: 2026-11-08 02:56; 4576 words
- Title: Round-5 seams
- Sections: 1. Pre-seeded hooks; 2. Producer -> consumer; 3. Loose ends the pre-seed left outside its paths
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI 5A: ONUB v2 rules, server deal and prep (Sonnet) (`2026-10-18_wdi-5a-onub-v2-rules-server-deal-and-prep-sonnet_Z1vSLdZ1.md`); WDI 5B: ONUB v2 server night and morning (Sonnet) (`2026-10-18_wdi-5b-onub-v2-server-night-and-morning-sonnet_oBDxMbRQ.md`); WDI 5C: ONUB v2 client prep, mini-games, deck editor (Sonnet) (`2026-10-18_wdi-5c-onub-v2-client-prep-mini-games-deck-edito_ZsrCwyaj.md`); WDI 5D: ONUB v2 client night, morning and results (Sonnet) (`2026-10-18_wdi-5d-onub-v2-client-night-morning-and-results_ZCVGvCem.md`); WDI 5E: ONUB v2 bots, NPC brains, e2e and soak (Sonnet) (`2026-10-18_wdi-5e-onub-v2-bots-npc-brains-e2e-and-soak-sonn_eAxjQMH2.md`); WDI 5F: Avatars, public looks, covers, Impersonate (Sonnet) (`2026-10-18_wdi-5f-avatars-public-looks-covers-impersonate-s_RU6tDKSs.md`); WDI 5G: Main deck and Werewolf roles (Sonnet) (`2026-10-18_wdi-5g-main-deck-and-werewolf-roles-sonnet_89i5n6pV.md`); WDI 5H: NPC routines and fixes (Sonnet) (`2026-10-18_wdi-5h-npc-routines-and-fixes-sonnet_V4W1hNxi.md`); WDI 5I: Isometric client and lighting (Sonnet) (`2026-10-18_wdi-5i-isometric-client-and-lighting-sonnet_5ESH86KS.md`); WDI 5J: Maps (Opus) (`2026-10-18_wdi-5j-maps-opus_3horF2Bn.md`); WDI 5K: World art (Opus) (`2026-10-18_wdi-5k-world-art-opus_syVMk7J3.md`) ...

### Who-Did-It: `docs/round6/bible-seams.md`

- First added: 2026-10-22 17:31; last changed: 2026-11-08 02:56; 1095 words
- Title: Round-6 contract: the Bible's seams, rounds 6 to 9
- Sections: 1. What round 6 pre-seeds for the Bible (6Z lands, nobody fills in round 6); 2. The staging; 3. What the Bible asks for that stays out
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 6A: time scale, auto mode, headless harness, CLI (`2026-10-22_6a-time-scale-auto-mode-headless-harness-cli_nzD4bsJD.md`); 6E: M5b content and GDD 3.14 to 3.16 (`2026-10-22_6e-m5b-content-and-gdd-3-14-to-3-16_A9guEQLm.md`); 6J: cutscenes (`2026-10-22_6j-cutscenes_QUhJyxKv.md`); 6K: loading, transitions, trailer, budgets (`2026-10-22_6k-loading-transitions-trailer-budgets_9tKHMakv.md`); 6L: music (`2026-10-22_6l-music_38ikwjEt.md`); 6M: M5b art (`2026-10-22_6m-m5b-art_YgH8yL5r.md`); 6B: event bus and invariants (`2026-10-22_6b-event-bus-and-invariants_mqHumgPx.md`); 6C: GitHub auth and AdminRoom (`2026-10-22_6c-github-auth-and-adminroom_Z72yR4XT.md`); 6F: gathering and crafting (`2026-10-22_6f-gathering-and-crafting_PvGmsMhD.md`); 6G: mobs and dark visibility (`2026-10-22_6g-mobs-and-dark-visibility_ZhArcC2h.md`); 6H: quests and mini-games (`2026-10-22_6h-quests-and-mini-games_KFerTAbi.md`) ...

### Who-Did-It: `docs/round6/owner-brief.md`

- First added: 2026-10-22 17:31; last changed: 2026-11-19 15:47; 15208 words
- Title: Round 6: the owner's brief
- Sections: 1. The request; 2. The Bible; 3. What the Bible names that the code does not have
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 6A: time scale, auto mode, headless harness, CLI (`2026-10-22_6a-time-scale-auto-mode-headless-harness-cli_nzD4bsJD.md`); 6E: M5b content and GDD 3.14 to 3.16 (`2026-10-22_6e-m5b-content-and-gdd-3-14-to-3-16_A9guEQLm.md`); 6J: cutscenes (`2026-10-22_6j-cutscenes_QUhJyxKv.md`); 6K: loading, transitions, trailer, budgets (`2026-10-22_6k-loading-transitions-trailer-budgets_9tKHMakv.md`); 6L: music (`2026-10-22_6l-music_38ikwjEt.md`); 6M: M5b art (`2026-10-22_6m-m5b-art_YgH8yL5r.md`); 6B: event bus and invariants (`2026-10-22_6b-event-bus-and-invariants_mqHumgPx.md`); 6C: GitHub auth and AdminRoom (`2026-10-22_6c-github-auth-and-adminroom_Z72yR4XT.md`); 6F: gathering and crafting (`2026-10-22_6f-gathering-and-crafting_PvGmsMhD.md`); 6G: mobs and dark visibility (`2026-10-22_6g-mobs-and-dark-visibility_ZhArcC2h.md`); 6H: quests and mini-games (`2026-10-22_6h-quests-and-mini-games_KFerTAbi.md`) ...

### Who-Did-It: `docs/round6/seams.md`

- First added: 2026-10-22 17:31; last changed: 2026-11-08 02:56; 2152 words
- Title: Round-6 seams
- Sections: 1. Pre-seeded hooks; 2. Producer -> consumer; 3. Loose ends
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 6A: time scale, auto mode, headless harness, CLI (`2026-10-22_6a-time-scale-auto-mode-headless-harness-cli_nzD4bsJD.md`); 6E: M5b content and GDD 3.14 to 3.16 (`2026-10-22_6e-m5b-content-and-gdd-3-14-to-3-16_A9guEQLm.md`); 6J: cutscenes (`2026-10-22_6j-cutscenes_QUhJyxKv.md`); 6K: loading, transitions, trailer, budgets (`2026-10-22_6k-loading-transitions-trailer-budgets_9tKHMakv.md`); 6L: music (`2026-10-22_6l-music_38ikwjEt.md`); 6M: M5b art (`2026-10-22_6m-m5b-art_YgH8yL5r.md`); 6B: event bus and invariants (`2026-10-22_6b-event-bus-and-invariants_mqHumgPx.md`); 6C: GitHub auth and AdminRoom (`2026-10-22_6c-github-auth-and-adminroom_Z72yR4XT.md`); 6F: gathering and crafting (`2026-10-22_6f-gathering-and-crafting_PvGmsMhD.md`); 6G: mobs and dark visibility (`2026-10-22_6g-mobs-and-dark-visibility_ZhArcC2h.md`); 6H: quests and mini-games (`2026-10-22_6h-quests-and-mini-games_KFerTAbi.md`) ...

### Who-Did-It: `docs/round7/seams.md`

- First added: 2026-10-23 19:06; last changed: 2026-11-08 02:56; 183 words
- Title: Round-7 seams
- Sections: 1. Module evaluation order
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 7A: map intro tracks and cinematic openings (`2026-10-23_7a-map-intro-tracks-and-cinematic-openings_6DEemceU.md`); 7B: theme pieces (night palette, pixel fonts, glass, backdrop) (`2026-10-23_7b-theme-pieces-night-palette-pixel-fonts-glass_7wrq33wV.md`); 7D: parties server (open/private, listing, profiles) (`2026-10-23_7d-parties-server-open-private-listing-profiles_3EHPoYgh.md`); 7H: vendettas (data, server, invariants, GDD 3.20) (`2026-10-23_7h-vendettas-data-server-invariants-gdd-3-20_SiWgJRDt.md`); 7I: the Daily Train, the memorial, the Ascended Vicar (`2026-10-23_7i-the-daily-train-the-memorial-the-ascended-vic_oqxDJXUC.md`); 7C: menu, profile, friends, Quit, party list (`2026-10-23_7c-menu-profile-friends-quit-party-list_RSG1j4r2.md`); 7E: lobby re-skin (three columns) (`2026-10-23_7e-lobby-re-skin-three-columns_HKGQCyzx.md`); 7F: match screens re-skin (HUD, role card, notebook, M5b, loading) (`2026-10-23_7f-match-screens-re-skin-hud-role-card-notebook_6maL417d.md`); 7G: meeting, game over, quick-mode and admin screens re-skin (`2026-10-23_7g-meeting-game-over-quick-mode-and-admin-screen_MazRQTw2.md`); 7J: the quick mode's removal (`2026-10-23_7j-the-quick-mode-s-removal_HkWFT75u.md`); 7K: Crumb's Ovens' rooms from the owner's station pictures (`2026-10-23_7k-crumb-s-ovens-rooms-from-the-owner-s-station_SNd15GSm.md`) ...

### Who-Did-It: `docs/round8/seams.md`

- First added: 2026-10-23 19:18; last changed: 2026-11-08 02:56; 2675 words
- Title: Round 8 seams: what the sessions share
- Sections: 1. The wire: schema version 6; 2. Ids; 3. Protocol; 4. The bus (`sim/events/bus.ts`); 5. The locked one-line hooks; 6. Who owns which path; 7. Merge order
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); Who Did It narrative worldbuilding (`2026-10-23_who-did-it-narrative-worldbuilding_sLCiiWHd.md`); Who Did It UDGT teardown (`2026-10-23_who-did-it-udgt-teardown_vc5Z1F2F.md`); 7M: every mini-game and main-mode task assignment (`2026-10-23_7m-every-mini-game-and-main-mode-task-assignment_1sdsHATT.md`); 8A: Bodies (health, stamina, effects, fists) (`2026-10-23_8a-bodies-health-stamina-effects-fists_VEobzSXD.md`); 8B: Inspect and the relations table (`2026-10-23_8b-inspect-and-the-relations-table_HsqMYbtr.md`); 8C: Scrip (purses, wages, shops, bank, coins) (`2026-10-23_8c-scrip-purses-wages-shops-bank-coins_DN9DHzMN.md`); 8D: Rent, Faith, rumours, HQ tiers (`2026-10-23_8d-rent-faith-rumours-hq-tiers_tFC3c3To.md`); 8E: Moods, townsfolk, mugging (`2026-10-23_8e-moods-townsfolk-mugging_A71DZxk2.md`); 8F: Characters (redesign, scale, clips) (`2026-10-23_8f-characters-redesign-scale-clips_a5u3HL3T.md`); 8G: Creatures, resource breaks, VFX, transport (`2026-10-23_8g-creatures-resource-breaks-vfx-transport_KkGzgnRP.md`); 8H: Interface motion (`2026-10-23_8h-interface-motion_JPbsyWeE.md`) ...

### Who-Did-It: `docs/round9/owner-brief.md`

- First added: 2026-10-24 23:37; last changed: 2026-11-19 15:47; 2543 words
- Title: Round 9: the owner's brief (2026-10-24)
- Sections: The owner's words, verbatim; The brief broken into workstreams (6Z's reading, for the owner to correct); Follow-up answers (2026-10-24, verbatim where quoted); Second follow-up (2026-10-25, verbatim); Third follow-up: "function without the killer" (2026-10-25, verbatim)
- Sessions that likely produced or used it: 6Z: Who-Did-It orchestrator (round 8) (`2026-10-24_6z-who-did-it-orchestrator-round-8_ikPFcTsY.md`); 9A (Opus): world mode and phases design (`2026-10-25_9a-opus-world-mode-and-phases-design_F7m4Q4q3.md`); 9B (Sonnet): logic table and failure messages design (`2026-10-25_9b-sonnet-logic-table-and-failure-messages-desig_VqastJW4.md`); 9C (Sonnet): living world and emergent play design (`2026-10-25_9c-sonnet-living-world-and-emergent-play-design_L3C1yKcZ.md`); 9D (Opus): fold the owner's answers, GDD map and round-10 plan (`2026-10-25_9d-opus-fold-the-owner-s-answers-gdd-map-and-rou_eULqTHCR.md`); 9S (Opus): admin Studio server (`2026-10-25_9s-opus-admin-studio-server_WNiGeGNN.md`); 9T (Sonnet): admin Studio client (`2026-10-25_9t-sonnet-admin-studio-client_snhP4uMS.md`); 9U (Sonnet): Studio editor live redraw and material painting (`2026-10-25_9u-sonnet-studio-editor-live-redraw-and-material_7Fpud5aa.md`); 9V (Opus): Studio content save and NPC lines as data (`2026-10-25_9v-opus-studio-content-save-and-npc-lines-as-dat_cXWGZc9e.md`); 9W (Sonnet): Studio Overview and NPC editor client (`2026-10-25_9w-sonnet-studio-overview-and-npc-editor-client_YzfkEGXi.md`)

### Who-Did-It: `docs/round9/round10-plan.md`

- First added: 2026-10-25 03:01; last changed: 2026-11-08 02:56; 3004 words
- Title: Round 9 (9D): the round-10 build plan
- Sections: 1. Rules for every pull request; 2. Sessions; 3. The next-playtest slice (session 10A); 4. The rest of round 10; 5. What breaks when I'm gone (owner answer WM1); 6. Dependencies at a glance; 7. Questions for 6Z
- Sessions that likely produced or used it: 6Z: Who-Did-It orchestrator (round 8) (`2026-10-24_6z-who-did-it-orchestrator-round-8_ikPFcTsY.md`); 9A (Opus): world mode and phases design (`2026-10-25_9a-opus-world-mode-and-phases-design_F7m4Q4q3.md`); 9B (Sonnet): logic table and failure messages design (`2026-10-25_9b-sonnet-logic-table-and-failure-messages-desig_VqastJW4.md`); 9C (Sonnet): living world and emergent play design (`2026-10-25_9c-sonnet-living-world-and-emergent-play-design_L3C1yKcZ.md`); 9D (Opus): fold the owner's answers, GDD map and round-10 plan (`2026-10-25_9d-opus-fold-the-owner-s-answers-gdd-map-and-rou_eULqTHCR.md`); 9S (Opus): admin Studio server (`2026-10-25_9s-opus-admin-studio-server_WNiGeGNN.md`); 9T (Sonnet): admin Studio client (`2026-10-25_9t-sonnet-admin-studio-client_snhP4uMS.md`); 9U (Sonnet): Studio editor live redraw and material painting (`2026-10-25_9u-sonnet-studio-editor-live-redraw-and-material_7Fpud5aa.md`); 9V (Opus): Studio content save and NPC lines as data (`2026-10-25_9v-opus-studio-content-save-and-npc-lines-as-dat_cXWGZc9e.md`); 9W (Sonnet): Studio Overview and NPC editor client (`2026-10-25_9w-sonnet-studio-overview-and-npc-editor-client_YzfkEGXi.md`)

### Who-Did-It: `docs/round10/seams.md`

- First added: 2026-10-29 17:12; last changed: 2026-11-08 03:51; 9418 words
- Title: Round 10 seams: what the sessions share
- Sections: 1. Shared files; 2. Ids the plan already fixes; 3. The wire; 4. Paths each session owns; 5. Reserved rows; 6. Invariants and checks; 7. Merge order
- Sessions that likely produced or used it: 10A (Opus): the slice's contracts (`2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md`); 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10G (Sonnet): the refusal sweep (`2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10B (Opus): the law (`2026-10-29_10b-opus-the-law_B4Hq1Uae.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10R: role cards and the player dashboard (design) (`2026-10-30_10r-role-cards-and-the-player-dashboard-design_CAKKzVuL.md`); 10V (Opus): The missing verbs (`2026-10-30_10v-opus-the-missing-verbs_QJz2QNAq.md`); 10S (Opus): The scope census (`2026-10-30_10s-opus-the-scope-census_HHeKca4Z.md`) ...

### Who-Did-It: `docs/round11/round11-plan.md`

- First added: 2026-10-30 04:37; last changed: 2026-11-19 17:28; 3424 words
- Title: Round 11: the build plan (the full Blender makeover)
- Sections: 1. Rules for every pull request; 2. Sessions; 3. The long shadows (CL3); 4. Tooling and passes; 5. Session 11M: materials and styles (11B's half); 6. The look gate; 7. The art drops; 8. Merge order; 9. Question for the owner
- Sessions that likely produced or used it: 10A (Opus): the slice's contracts (`2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md`); 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10G (Sonnet): the refusal sweep (`2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10B (Opus): the law (`2026-10-29_10b-opus-the-law_B4Hq1Uae.md`); 3D asset production pipeline (`2026-10-29_3d-asset-production-pipeline_9jLDDV7q.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`) ...

### Who-Did-It: `docs/round10/scope.md`

- First added: 2026-10-30 14:15; last changed: 2026-11-11 23:11; 13872 words
- Title: Round 10: the scope census (10S)
- Sections: 0. The brief; 1. The inventory; 2. The missing design; 3. The wire; 4. The build plan; 5. Questions for the owner
- Sessions that likely produced or used it: 10A (Opus): the slice's contracts (`2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md`); 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10G (Sonnet): the refusal sweep (`2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10B (Opus): the law (`2026-10-29_10b-opus-the-law_B4Hq1Uae.md`); 3D asset production pipeline (`2026-10-29_3d-asset-production-pipeline_9jLDDV7q.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`) ...

### Who-Did-It: `docs/round10/wave2-briefs.md`

- First added: 2026-10-30 16:41; last changed: 2026-11-19 15:47; 3430 words
- Title: Round 10, wave 2: the spawn briefs
- Sections: 10N; 10K; 10T; 10M; Common to the four
- Sessions that likely produced or used it: 10A (Opus): the slice's contracts (`2026-10-29_10a-opus-the-slice-s-contracts_KNqrN8j6.md`); 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10G (Sonnet): the refusal sweep (`2026-10-29_10g-sonnet-the-refusal-sweep_PNLNW4EC.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10B (Opus): the law (`2026-10-29_10b-opus-the-law_B4Hq1Uae.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10R: role cards and the player dashboard (design) (`2026-10-30_10r-role-cards-and-the-player-dashboard-design_CAKKzVuL.md`) ...

### Pipelines-Plugin: `ROADMAP.md`

- First added: 2026-10-31 05:03; last changed: 2026-11-19 23:48; 5409 words
- Title: ROSW (Pipelines-Plugin) — Audit & Expansion Roadmap (2026-10-30)
- Sections: Context; Author decisions (2026-11-01); ComfyUI 3D (2026-11-01); Wave 1 status and review checklist (2026-11-01); Part A — Fixes; Part B — Generalize single-vendor / single-use pieces; Part C — Optimize existing skills & agents; Part D — New pipelines to build; Part E — Graphic-design toolkit plan; Part F — Local/cloud split (Railway) — added 2026-11-01; Phasing (when work resumes); Verification (for each phase when executed)
- Sessions that likely produced or used it: OneDrive to Google Drive migration (`2026-10-31_onedrive-to-google-drive-migration_pNFK4anv.md`); Sonnet sessions from roadmap (`2026-10-31_sonnet-sessions-from-roadmap_1DJmy7hz.md`)

### Who-Did-It: `docs/story/test-plan.md`

- First added: 2026-11-06 04:14; last changed: 2026-11-08 02:56; 636 words
- Title: Story mode: test plan (S4)
- Sections: The fixture (`apps/server/test/story/fixture.ts`); Server suites (`apps/server/test/story/`); E2E (`apps/client/e2e/story*.spec.ts`); The bot (`tools/bots/`); Bugs found in other sessions' paths
- Sessions that likely produced or used it: 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10S (Opus): The scope census (`2026-10-30_10s-opus-the-scope-census_HHeKca4Z.md`); 10T: the town (round 10, wave 2) (`2026-10-30_10t-the-town-round-10-wave-2_934vv6Gw.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`) ...

### Look_Over_There: `docs/SESSIONS.md`

- First added: 2026-11-06 20:17; last changed: 2026-11-19 21:55; 4191 words
- Title: Sessions: how the work is split
- Sections: Status; Order; Rules for every session; Briefs
- Sessions that likely produced or used it: Game scenes and level connections (`2026-11-04_game-scenes-and-level-connections_nHeznJEZ.md`)

### Who-Did-It: `docs/story/orchestrator-handoff.md`

- First added: 2026-11-10 19:20; last changed: 2026-11-19 15:49; 2116 words
- Title: Story mode part 2: orchestrator handoff
- Sections: Standing rules from the owner; Open decisions (owner only); The Vicar design that was agreed; Merges that wait for the owner; Round-10 lanes the orchestrator owns (2026-11-12); Sessions; Archival routine; On hold; Art; Resuming
- Sessions that likely produced or used it: 10F (Opus): the logic table (`2026-10-29_10f-opus-the-logic-table_eRQoDBwy.md`); 10H (Sonnet): the slice's rules (`2026-10-29_10h-sonnet-the-slice-s-rules_1mBpRknV.md`); 10C (Opus): death's cost and arrivals (`2026-10-29_10c-opus-death-s-cost-and-arrivals_atNhaVLo.md`); 10D (Sonnet): the living world (`2026-10-29_10d-sonnet-the-living-world_JRgkS8ow.md`); 10X (Fable): fixes, server and rules (`2026-10-30_10x-fable-fixes-server-and-rules_zzwMzzpW.md`); 10Y (Fable): fixes, client and screens (`2026-10-30_10y-fable-fixes-client-and-screens_xojFNVor.md`); 10S (Opus): The scope census (`2026-10-30_10s-opus-the-scope-census_HHeKca4Z.md`); 10T: the town (round 10, wave 2) (`2026-10-30_10t-the-town-round-10-wave-2_934vv6Gw.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`) ...

### esc-ZINE99: `games/man-eater/CONSULTATION_BRIEF.md`

- First added: 2026-11-16 14:32; last changed: 2026-11-19 15:49; 1860 words
- Title: Project: Man Eater — brief for the cultural consultant
- Sections: 1. What the game is; 2. What the game does, and does not do, with the Windigo tradition; 3. Everything that touches the figure or the word; 4. Questions; 5. Terms; 6. What you will be shown first

### Who-Did-It: `docs/round11/round11-plan-v2.md`

- First added: 2026-11-19 16:57; last changed: 2026-11-19 17:28; 2213 words
- Title: Round 11, revised: building the sprite world (A615)
- Sections: 1. What carries over from the approved plan; 2. Rules for every pull request; 3. Sessions; 4. The pull requests; 5. Merge order; 6. Questions for the owner; 7. What it costs, roughly
- Sessions that likely produced or used it: 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`); Story P0: the HollowMere arc (design) (`2026-11-06_story-p0-the-hollowmere-arc-design_B7eQSKQ5.md`); Session 2: gate return fix, links from the manifest (`2026-11-08_session-2-gate-return-fix-links-from-the-manifes_WrLpinA4.md`); Creative writing to game adaptation (`2026-11-12_creative-writing-to-game-adaptation_rkcmWq1a.md`); Session 18: rules for the arsenal, consumables, dealer items and food (`2026-11-15_session-18-rules-for-the-arsenal-consumables-dea_dfok53Yk.md`); 11D: round 11 decisions (Three.js, model locks) (`2026-11-19_11d-round-11-decisions-three-js-model-locks_D3d3fjEo.md`); 11T: round 11 tooling (Blender CI, render locks) (`2026-11-19_11t-round-11-tooling-blender-ci-render-locks_E8SszT7j.md`); 11P: round 11 prop list (`2026-11-19_11p-round-11-prop-list_sgQGbvMg.md`)

### Who-Did-It: `docs/round11/seams.md`

- First added: 2026-11-19 17:51; last changed: 2026-11-19 22:00; 499 words
- Title: Round 11 seams: who owns what (the sprite world, A616)
- Sections: 1. The first sessions (started 2026-11-19); 2. Shared files; 3. What no session touches in round 11
- Sessions that likely produced or used it: 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`); Story P0: the HollowMere arc (design) (`2026-11-06_story-p0-the-hollowmere-arc-design_B7eQSKQ5.md`); Session 2: gate return fix, links from the manifest (`2026-11-08_session-2-gate-return-fix-links-from-the-manifes_WrLpinA4.md`); Creative writing to game adaptation (`2026-11-12_creative-writing-to-game-adaptation_rkcmWq1a.md`); Session 18: rules for the arsenal, consumables, dealer items and food (`2026-11-15_session-18-rules-for-the-arsenal-consumables-dea_dfok53Yk.md`); 11D: round 11 decisions (Three.js, model locks) (`2026-11-19_11d-round-11-decisions-three-js-model-locks_D3d3fjEo.md`); 11T: round 11 tooling (Blender CI, render locks) (`2026-11-19_11t-round-11-tooling-blender-ci-render-locks_E8SszT7j.md`); 11P: round 11 prop list (`2026-11-19_11p-round-11-prop-list_sgQGbvMg.md`); Fix two flaky server tests (mugFlight, manhunt) (`2026-11-19_fix-two-flaky-server-tests-mugflight-manhunt_e4njLyha.md`)

### Who-Did-It: `docs/round11/tiles-brief.md`

- First added: 2026-11-19 19:43; last changed: 2026-11-19 23:58; 1013 words
- Title: 11P P2: tiles and wall textures (brief, draft)
- Sections: 1. What P2 delivers; 2. Format (proposed, R1 must confirm); 3. Sources, in order; 4. Where it lives; 5. Done, and the tests; 6. Proposed `seams.md` row (for the orchestrator); 7. Open questions (proposed defaults, owner or orchestrator)
- Sessions that likely produced or used it: 11A (Opus): the render pipeline (`2026-10-29_11a-opus-the-render-pipeline_vVuqkw6V.md`); 11B (Opus): materials, styles and budgets (`2026-10-29_11b-opus-materials-styles-and-budgets_AAcwSByb.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Session 2: gate return fix, links from the manifest (`2026-11-08_session-2-gate-return-fix-links-from-the-manifes_WrLpinA4.md`); Creative writing to game adaptation (`2026-11-12_creative-writing-to-game-adaptation_rkcmWq1a.md`); Session 18: rules for the arsenal, consumables, dealer items and food (`2026-11-15_session-18-rules-for-the-arsenal-consumables-dea_dfok53Yk.md`); 11D: round 11 decisions (Three.js, model locks) (`2026-11-19_11d-round-11-decisions-three-js-model-locks_D3d3fjEo.md`); 11T: round 11 tooling (Blender CI, render locks) (`2026-11-19_11t-round-11-tooling-blender-ci-render-locks_E8SszT7j.md`); 11P: round 11 prop list (`2026-11-19_11p-round-11-prop-list_sgQGbvMg.md`); Fix two flaky server tests (mugFlight, manhunt) (`2026-11-19_fix-two-flaky-server-tests-mugflight-manhunt_e4njLyha.md`)

## Decision logs (1)

### Who-Did-It: `docs/DECISIONS.md`

- First added: 2026-10-10 00:29; last changed: 2026-11-20 00:40; 75255 words
- Title: Decisions Log
- Sections: Decisions locked with the owner (2026-10-09); 8. Decisions & changes from review; 9. Open questions for the owner; Amendments (2026-10-10); Spike results (M0); Open questions added at integration (2026-10-10)
- Numbered decision rows: 293 (first A1, last A618)
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`)

## Playtest kit (5)

### Who-Did-It: `docs/PLAYTESTS/2026-xx-xx-m2.md`

- First added: 2026-10-16 04:40; last changed: 2026-11-08 02:56; 331 words
- Title: 2026-xx-xx, M2 playtest
- Sections: Setup; What M2 checks; Bugs; What we learned; Actions
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI K: M3 match flow, meetings, votes, win (Sonnet) (`2026-10-16_wdi-k-m3-match-flow-meetings-votes-win-sonnet_xDYzVTkf.md`); WDI L: M3 kill, bodies, clues, Notebook (Sonnet) (`2026-10-16_wdi-l-m3-kill-bodies-clues-notebook-sonnet_qscgm6uS.md`); WDI M: M3 meeting, game over, chat, theme screens (Sonnet) (`2026-10-16_wdi-m-m3-meeting-game-over-chat-theme-screens-so_MnTboRjB.md`); WDI N: M3 world actions, clues, HUD theme (Sonnet) (`2026-10-16_wdi-n-m3-world-actions-clues-hud-theme-sonnet_raEw1Nfr.md`); WDI O: M3 bots, match e2e, soak (Sonnet) (`2026-10-16_wdi-o-m3-bots-match-e2e-soak-sonnet_qyWQF69y.md`); WDI P: M3 art, props, clues, VFX, body sprite (Opus) (`2026-10-16_wdi-p-m3-art-props-clues-vfx-body-sprite-opus_tYimDxQw.md`); WDI Q: M3 playtest kit, audio, copy deck (Opus) (`2026-10-16_wdi-q-m3-playtest-kit-audio-copy-deck-opus_GDhqLxqB.md`)

### Who-Did-It: `docs/PLAYTESTS/FORM.md`

- First added: 2026-10-16 04:40; last changed: 2026-11-08 02:56; 611 words
- Title: Feedback form
- Sections: Reading the responses; Questions for the later milestones
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI K: M3 match flow, meetings, votes, win (Sonnet) (`2026-10-16_wdi-k-m3-match-flow-meetings-votes-win-sonnet_xDYzVTkf.md`); WDI L: M3 kill, bodies, clues, Notebook (Sonnet) (`2026-10-16_wdi-l-m3-kill-bodies-clues-notebook-sonnet_qscgm6uS.md`); WDI M: M3 meeting, game over, chat, theme screens (Sonnet) (`2026-10-16_wdi-m-m3-meeting-game-over-chat-theme-screens-so_MnTboRjB.md`); WDI N: M3 world actions, clues, HUD theme (Sonnet) (`2026-10-16_wdi-n-m3-world-actions-clues-hud-theme-sonnet_raEw1Nfr.md`); WDI O: M3 bots, match e2e, soak (Sonnet) (`2026-10-16_wdi-o-m3-bots-match-e2e-soak-sonnet_qyWQF69y.md`); WDI P: M3 art, props, clues, VFX, body sprite (Opus) (`2026-10-16_wdi-p-m3-art-props-clues-vfx-body-sprite-opus_tYimDxQw.md`); WDI Q: M3 playtest kit, audio, copy deck (Opus) (`2026-10-16_wdi-q-m3-playtest-kit-audio-copy-deck-opus_GDhqLxqB.md`)

### Who-Did-It: `docs/PLAYTESTS/README.md`

- First added: 2026-10-16 04:40; last changed: 2026-11-19 15:47; 3413 words
- Title: Playtests
- Sections: 1. Owner prerequisites (before inviting anyone); 2. Who and what; 3. Session plan; 4. The match log; 5. The host's script; 6. When something goes wrong; 7. After the session; 8. Quick mode evening (M3b); 9. NPC session (M3c)
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI K: M3 match flow, meetings, votes, win (Sonnet) (`2026-10-16_wdi-k-m3-match-flow-meetings-votes-win-sonnet_xDYzVTkf.md`); WDI L: M3 kill, bodies, clues, Notebook (Sonnet) (`2026-10-16_wdi-l-m3-kill-bodies-clues-notebook-sonnet_qscgm6uS.md`); WDI M: M3 meeting, game over, chat, theme screens (Sonnet) (`2026-10-16_wdi-m-m3-meeting-game-over-chat-theme-screens-so_MnTboRjB.md`); WDI N: M3 world actions, clues, HUD theme (Sonnet) (`2026-10-16_wdi-n-m3-world-actions-clues-hud-theme-sonnet_raEw1Nfr.md`); WDI O: M3 bots, match e2e, soak (Sonnet) (`2026-10-16_wdi-o-m3-bots-match-e2e-soak-sonnet_qyWQF69y.md`); WDI P: M3 art, props, clues, VFX, body sprite (Opus) (`2026-10-16_wdi-p-m3-art-props-clues-vfx-body-sprite-opus_tYimDxQw.md`); WDI Q: M3 playtest kit, audio, copy deck (Opus) (`2026-10-16_wdi-q-m3-playtest-kit-audio-copy-deck-opus_GDhqLxqB.md`)

### Who-Did-It: `docs/PLAYTESTS/SCORECARD.md`

- First added: 2026-10-16 04:40; last changed: 2026-11-08 02:56; 1307 words
- Title: M3 scorecard: fun or stop
- Sections: 0. The bar, set before session 1; 1. Session; 2. Matches; 3. From the form; 4. Session read; 5. Decision line (second session only); 6. M3b, quick mode; 7. M3c, NPC fill
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI K: M3 match flow, meetings, votes, win (Sonnet) (`2026-10-16_wdi-k-m3-match-flow-meetings-votes-win-sonnet_xDYzVTkf.md`); WDI L: M3 kill, bodies, clues, Notebook (Sonnet) (`2026-10-16_wdi-l-m3-kill-bodies-clues-notebook-sonnet_qscgm6uS.md`); WDI M: M3 meeting, game over, chat, theme screens (Sonnet) (`2026-10-16_wdi-m-m3-meeting-game-over-chat-theme-screens-so_MnTboRjB.md`); WDI N: M3 world actions, clues, HUD theme (Sonnet) (`2026-10-16_wdi-n-m3-world-actions-clues-hud-theme-sonnet_raEw1Nfr.md`); WDI O: M3 bots, match e2e, soak (Sonnet) (`2026-10-16_wdi-o-m3-bots-match-e2e-soak-sonnet_qyWQF69y.md`); WDI P: M3 art, props, clues, VFX, body sprite (Opus) (`2026-10-16_wdi-p-m3-art-props-clues-vfx-body-sprite-opus_tYimDxQw.md`); WDI Q: M3 playtest kit, audio, copy deck (Opus) (`2026-10-16_wdi-q-m3-playtest-kit-audio-copy-deck-opus_GDhqLxqB.md`)

### Who-Did-It: `docs/PLAYTESTS/TEMPLATE.md`

- First added: 2026-10-16 04:40; last changed: 2026-11-08 02:56; 385 words
- Title: YYYY-MM-DD, <milestone> playtest
- Sections: Setup; Matches; Bugs; Form summary; Debrief; What we learned; Actions
- Sessions that likely produced or used it: Who Did It multiplayer game plan (`2026-10-09_who-did-it-multiplayer-game-plan_ehmFeqEN.md`); WDI K: M3 match flow, meetings, votes, win (Sonnet) (`2026-10-16_wdi-k-m3-match-flow-meetings-votes-win-sonnet_xDYzVTkf.md`); WDI L: M3 kill, bodies, clues, Notebook (Sonnet) (`2026-10-16_wdi-l-m3-kill-bodies-clues-notebook-sonnet_qscgm6uS.md`); WDI M: M3 meeting, game over, chat, theme screens (Sonnet) (`2026-10-16_wdi-m-m3-meeting-game-over-chat-theme-screens-so_MnTboRjB.md`); WDI N: M3 world actions, clues, HUD theme (Sonnet) (`2026-10-16_wdi-n-m3-world-actions-clues-hud-theme-sonnet_raEw1Nfr.md`); WDI O: M3 bots, match e2e, soak (Sonnet) (`2026-10-16_wdi-o-m3-bots-match-e2e-soak-sonnet_qyWQF69y.md`); WDI P: M3 art, props, clues, VFX, body sprite (Opus) (`2026-10-16_wdi-p-m3-art-props-clues-vfx-body-sprite-opus_tYimDxQw.md`); WDI Q: M3 playtest kit, audio, copy deck (Opus) (`2026-10-16_wdi-q-m3-playtest-kit-audio-copy-deck-opus_GDhqLxqB.md`)

## Guides (4)

### Who-Did-It: `docs/guides/ADMIN_GUIDE.md`

- First added: 2026-10-23 00:25; last changed: 2026-11-08 02:56; 409 words
- Title: Admin guide: auto-mode
- Sections: Turning it on; The page; Replaying a failure; The headless runner
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 6N: ROSW media (both repos) (`2026-10-22_6n-rosw-media-both-repos_gVG9ebNw.md`); 6P: round-6 integration (`2026-10-22_6p-round-6-integration_t9v4N6oc.md`); 6Q: opening cinematic (`2026-10-22_6q-opening-cinematic_veWdRCed.md`)

### Who-Did-It: `docs/guides/HOST_GUIDE.md`

- First added: 2026-10-23 00:25; last changed: 2026-11-08 02:56; 489 words
- Title: Host guide
- Sections: Making a party; Lobby settings; When something sticks; Running your own server
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 6N: ROSW media (both repos) (`2026-10-22_6n-rosw-media-both-repos_gVG9ebNw.md`); 6P: round-6 integration (`2026-10-22_6p-round-6-integration_t9v4N6oc.md`); 6Q: opening cinematic (`2026-10-22_6q-opening-cinematic_veWdRCed.md`)

### Who-Did-It: `docs/guides/HOW_TO_PLAY.md`

- First added: 2026-10-23 00:25; last changed: 2026-11-08 02:56; 945 words
- Title: How to play Who Did It
- Sections: Getting in; Controls; Your role card; The loop of a match; Clues and the Notebook; Gathering, crafting, quests, creatures; Winning; Tips for a first game
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 6N: ROSW media (both repos) (`2026-10-22_6n-rosw-media-both-repos_gVG9ebNw.md`); 6P: round-6 integration (`2026-10-22_6p-round-6-integration_t9v4N6oc.md`); 6Q: opening cinematic (`2026-10-22_6q-opening-cinematic_veWdRCed.md`)

### Who-Did-It: `docs/guides/README.md`

- First added: 2026-10-23 00:25; last changed: 2026-11-08 02:56; 112 words
- Title: Guides
- Sessions that likely produced or used it: Game features and admin tools planning (`2026-10-21_game-features-and-admin-tools-planning_vc1w4Qwu.md`); 6N: ROSW media (both repos) (`2026-10-22_6n-rosw-media-both-repos_gVG9ebNw.md`); 6P: round-6 integration (`2026-10-22_6p-round-6-integration_t9v4N6oc.md`); 6Q: opening cinematic (`2026-10-22_6q-opening-cinematic_veWdRCed.md`)

## Game designs (esc-ZINE99 DESIGN.md files and deep dives) (20)

### esc-ZINE99: `games/behind-the-peephole/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3950 words
- Title: Behind the Peephole: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/behind-the-peephole/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 27669 words
- Title: Behind the Peephole: design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/endless-temple/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3944 words
- Title: The Endless Temple: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/endless-temple/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 25198 words
- Title: The Endless Temple: design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/heartstream/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3986 words
- Title: A Journey Into the Heartstream: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/heartstream/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 25917 words
- Title: A Journey Into the Heartstream
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/lira-calyx/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3736 words
- Title: The Redacted Testament of Lira Calyx: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/lira-calyx/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-16 14:44; 22717 words
- Title: The Redacted Testament of Lira Calyx: design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/lord-of-the-sea/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3888 words
- Title: The Lord of the Sea: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/lord-of-the-sea/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 26533 words
- Title: The Lord of the Sea: design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/man-eater/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3871 words
- Title: Project: Man Eater — deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/man-eater/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 29267 words
- Title: Project: Man Eater — design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/missing-campsites/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3959 words
- Title: Missing Campsites: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/missing-campsites/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 24245 words
- Title: Missing Campsites: design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/people-of-the-bark/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3984 words
- Title: People of the Bark — Deep Dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/people-of-the-bark/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 28231 words
- Title: People of the Bark — Design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/stuffed-ones/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3944 words
- Title: The Stuffed Ones: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/stuffed-ones/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 24944 words
- Title: The Stuffed Ones: design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

### esc-ZINE99: `games/wrymwretch/DEEP_DIVE.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 3811 words
- Title: WrymWretch: deep dive
- Sections: 1. Where it stands; 2. The story, developed; 3. Obstacles and puzzles; 4. Art plan; 5. Roadmap; 6. Additions register

### esc-ZINE99: `games/wrymwretch/DESIGN.md`

- First added: 2026-11-15 21:36; last changed: 2026-11-19 15:49; 28140 words
- Title: WrymWretch: design
- Sections: 1. Summary; 2. Why this game; 3. Source fidelity; 4. Investment; 5. Lore bible; 6. Characters; 7. Structure and pacing; 8. Levels; 9. 3D scenes; 10. 2D modes; 11. 1D games; 12. Core systems

## Studio notes (one per made thing) (11)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/following-the-sheep.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 988 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/heartstream.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 999 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/low-in-the-water.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 991 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/melting-away.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 985 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/missing-campsites.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 985 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/trip-tracker.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 989 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/wrymwretch.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 982 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/yellow-drop.md`

- First added: 2026-10-01 00:50; last changed: 2026-10-01 00:50; 1003 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links
- Sessions that likely produced or used it: Creative-Headquarters migration plan (`2026-09-30_creative-headquarters-migration-plan_JWPzuC4u.md`)

### Pipelines-Plugin: `studio/vault/writing-museum/3d/architecture-of-being.md`

- First added: 2026-10-01 00:52; last changed: 2026-10-01 00:52; 1034 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links

### Pipelines-Plugin: `studio/vault/writing-museum/3d/endless-temple.md`

- First added: 2026-10-01 00:52; last changed: 2026-10-01 00:52; 1035 words
- Title: (none)
- Sections: Overview; Timeline; Method; Decisions in Force; Open Questions; Contradictions; Links

### Pipelines-Plugin: `studio/vault/who-did-it/video/memorial-vicar.md`

- First added: 2026-10-23 03:33; last changed: 2026-10-23 03:33; 778 words
- Title: (none)
- Sections: Overview; Next Steps; Timeline; Method; Decisions in Force; Links

## Teardown chapters (25)

### Pipelines-Plugin: `teardowns/who-did-it/chapters/00-overview.md`

- First added: 2026-10-23 15:53; last changed: 2026-10-23 20:01; 1388 words
- Title: Overview and pillars
- Sections: The four pillars; Dread, then suspicion; For friends on a Friday night; What the teardown will help decide; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/who-did-it/chapters/01-ui.md`

- First added: 2026-10-23 16:36; last changed: 2026-10-23 20:51; 1335 words
- Title: UI and frontend
- Sections: One design system, enforced by tests; Glass for the world, paper for what you hold; Pixel type: menus, not matches; What you know about places you are not in; Phone and desktop, equally; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/who-did-it/chapters/02-datasets.md`

- First added: 2026-10-23 17:00; last changed: 2026-10-23 20:01; 1952 words
- Title: Datasets and content
- Sections: One source of rules, checked twice; Every number is a guess, for now; The data wins: card text should follow it; Content by you and your friends; The round-8 seams; Smaller findings; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/who-did-it/chapters/03-gameplay.md`

- First added: 2026-10-23 18:16; last changed: 2026-10-23 18:16; 1902 words
- Title: Gameplay and mechanics
- Sections: Three ways to play, one table; How long a match runs; The end: a short hunt, then a trial; The world as a second layer; Smaller mechanics; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/who-did-it/chapters/04-backend.md`

- First added: 2026-10-23 19:16; last changed: 2026-10-23 20:01; 1735 words
- Title: Backend, netcode and protocol
- Sections: One step, in a fixed order; Secrets, by construction; Capacity for friends; Full anti-cheat; The balance lab; Smaller findings; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/who-did-it/chapters/05-world.md`

- First added: 2026-10-23 19:29; last changed: 2026-10-23 20:51; 2499 words
- Title: World and the Bible
- Sections: Three Hollowmeres; Book V: killer dilemmas, state-aware NPCs, the environment; Each map plays differently; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/who-did-it/chapters/06-art-audio.md`

- First added: 2026-10-23 19:41; last changed: 2026-10-23 19:41; 1675 words
- Title: Art, audio and the asset pipeline
- Sections: Three styles, one set of assets; Generated art, as long as it looks good; Music-led; Smaller findings; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/who-did-it/chapters/07-history.md`

- First added: 2026-10-23 19:46; last changed: 2026-10-23 20:51; 1621 words
- Title: How it was made: history and reversals
- Sections: Seven rounds; The quick mode: directions misunderstood; A105 and the round-6 scope; The decision log as a record; Owner's word; Open threads
- Sessions that likely produced or used it: Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`); Story S4: tests, replay and bot (`2026-11-06_story-s4-tests-replay-and-bot_HnxDqZRT.md`); Story P0: the HollowMere arc (design) (`2026-11-06_story-p0-the-hollowmere-arc-design_B7eQSKQ5.md`); Story P4: achievements on the device (`2026-11-06_story-p4-achievements-on-the-device_SSXYJkcQ.md`); Story merge queue: round 10 PRs into the base (`2026-11-07_story-merge-queue-round-10-prs-into-the-base_YdYTm2cA.md`); Story P2: sections engine (`2026-11-07_story-p2-sections-engine_76C6nUHz.md`); Story P3: client, saves and end screen (`2026-11-07_story-p3-client-saves-and-end-screen_cVJ9rsJZ.md`); Story R: the Medium's rite and the 10X Vicar (`2026-11-10_story-r-the-medium-s-rite-and-the-10x-vicar_fpYurWpn.md`)

### Pipelines-Plugin: `teardowns/who-did-it/chapters/08-future.md`

- First added: 2026-10-23 20:01; last changed: 2026-10-23 20:01; 1908 words
- Title: The future: rounds 8 and 9, and after
- Sections: All equally; Five playtests, and the curve from idea to story; V2 is a sequel, not a version; When it ends; Owner's word; Open threads

### Pipelines-Plugin: `teardowns/right-door-wrong-exit/chapters/00-overview.md`

- First added: 2026-10-25 04:11; last changed: 2026-10-25 04:11; 1681 words
- Title: Overview and the loop
- Sections: The loop is the ending; A walkthrough, with games inside it; Seven rooms, one descent, one voice; Made for one person; Toward Ninety-Nine; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/right-door-wrong-exit/chapters/01-ui.md`

- First added: 2026-10-25 13:29; last changed: 2026-10-25 13:29; 1462 words
- Title: Screens, glitches and the paper card
- Sections: The loading screen as a room; SKIP: a safety net with the door left open; The paper card and the room title; The phone; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/right-door-wrong-exit/chapters/02-walk.md`

- First added: 2026-10-25 13:42; last changed: 2026-10-25 13:42; 1641 words
- Title: The walk, the exits and the mini games
- Sections: The walk to the exit; The dining room, the best walk; Gating the exit with every game; A game in every room; The trampoline park, unfinished; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/right-door-wrong-exit/chapters/03-rooms.md`

- First added: 2026-10-25 13:50; last changed: 2026-10-25 13:50; 1326 words
- Title: The seven rooms and the story they tell
- Sections: The voice; The clock that breaks; Phases, and adding rooms; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/right-door-wrong-exit/chapters/04-art-audio.md`

- First added: 2026-10-25 13:53; last changed: 2026-10-25 13:53; 1327 words
- Title: Video, procedural rooms and sound
- Sections: The pair: clip and room; The rooms built from code; The media; The sound of a room at rest; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/right-door-wrong-exit/chapters/05-engine.md`

- First added: 2026-10-25 13:56; last changed: 2026-10-25 13:56; 1230 words
- Title: Engine, phones and tests
- Sections: The runtime, and a phone as the floor; The test, on every push; The file names; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/right-door-wrong-exit/chapters/06-history.md`

- First added: 2026-10-25 14:11; last changed: 2026-10-25 14:11; 1224 words
- Title: How it was made, and what is next
- Sections: The shell, 22 to 25 August; The walk, 30 September to 9 October; What Ninety-Nine carried over; Never finished; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`); Story S4: tests, replay and bot (`2026-11-06_story-s4-tests-replay-and-bot_HnxDqZRT.md`); Story P0: the HollowMere arc (design) (`2026-11-06_story-p0-the-hollowmere-arc-design_B7eQSKQ5.md`); Story P4: achievements on the device (`2026-11-06_story-p4-achievements-on-the-device_SSXYJkcQ.md`); Story merge queue: round 10 PRs into the base (`2026-11-07_story-merge-queue-round-10-prs-into-the-base_YdYTm2cA.md`); Story P2: sections engine (`2026-11-07_story-p2-sections-engine_76C6nUHz.md`); Story P3: client, saves and end screen (`2026-11-07_story-p3-client-saves-and-end-screen_cVJ9rsJZ.md`); Story R: the Medium's rite and the 10X Vicar (`2026-11-10_story-r-the-medium-s-rite-and-the-10x-vicar_fpYurWpn.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/00-overview.md`

- First added: 2026-10-26 05:20; last changed: 2026-10-26 05:20; 1737 words
- Title: Overview and the argument
- Sections: The argument: no correct answer, no escape; The word "you"; Made for one person; The old sets, and the merge; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/01-ui.md`

- First added: 2026-10-26 20:10; last changed: 2026-10-26 20:10; 1328 words
- Title: The interface that is not there
- Sections: EXIT, the one button; Truthful labels in a lying building; The walk hint and the captions; Desktop first; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/02-datasets.md`

- First added: 2026-10-29 19:40; last changed: 2026-10-29 19:40; 1206 words
- Title: Sets, scenes and endings as data
- Sections: Two files, one scene; Writing a scene from the data alone; The beat vocabulary; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Cloning video-use and clipify repos (`2026-10-29_cloning-video-use-and-clipify-repos_rvo4p5Pg.md`); Session autocompact strategy (`2026-10-29_session-autocompact-strategy_PTi8ZPYa.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/03-gameplay.md`

- First added: 2026-10-29 20:17; last changed: 2026-10-29 20:17; 1957 words
- Title: Spine, render and the walked choice
- Sections: The spine and the render; The mini-games, and what replaced them; Duplicate rooms as corrupted copies; Screen effects instead of the overlays; Telling the player, once; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Cloning video-use and clipify repos (`2026-10-29_cloning-video-use-and-clipify-repos_rvo4p5Pg.md`); Session autocompact strategy (`2026-10-29_session-autocompact-strategy_PTi8ZPYa.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/04-engine.md`

- First added: 2026-10-29 21:39; last changed: 2026-10-29 21:39; 1298 words
- Title: Engine, audio and tests
- Sections: Tests, and the CI the specs already promised; The drone that "could go"; Phones too; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Cloning video-use and clipify repos (`2026-10-29_cloning-video-use-and-clipify-repos_rvo4p5Pg.md`); Session autocompact strategy (`2026-10-29_session-autocompact-strategy_PTi8ZPYa.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/05-world.md`

- First added: 2026-10-29 21:55; last changed: 2026-10-29 21:55; 1479 words
- Title: The building and the canon
- Sections: Real, wrong, downward; C1 lifted: from PS1 to "low to mid poly"; C4, defended; Harlowe, the previous 99; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Cloning video-use and clipify repos (`2026-10-29_cloning-video-use-and-clipify-repos_rvo4p5Pg.md`); Session autocompact strategy (`2026-10-29_session-autocompact-strategy_PTi8ZPYa.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/06-art-audio.md`

- First added: 2026-10-29 22:04; last changed: 2026-10-29 22:04; 1356 words
- Title: Art, audio and the asset pipelines
- Sections: Props: a mix, with one finishing pass; The stills, the transitions and the ending films, edited by hand; Sound: building moments from music, effects and room tone; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Cloning video-use and clipify repos (`2026-10-29_cloning-video-use-and-clipify-repos_rvo4p5Pg.md`); Session autocompact strategy (`2026-10-29_session-autocompact-strategy_PTi8ZPYa.md`)

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/07-history.md`

- First added: 2026-10-29 22:14; last changed: 2026-10-29 22:14; 1287 words
- Title: How it was made: history and reversals
- Sections: A necessary sketch; Three regrets; The specs as a record of growth; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Cloning video-use and clipify repos (`2026-10-29_cloning-video-use-and-clipify-repos_rvo4p5Pg.md`); Session autocompact strategy (`2026-10-29_session-autocompact-strategy_PTi8ZPYa.md`); Story mode (`2026-11-06_story-mode_oZ8CZDFp.md`); Story S1: story content and schema (`2026-11-06_story-s1-story-content-and-schema_m5YnLFiq.md`); Story S2: story engine and seat handover (`2026-11-06_story-s2-story-engine-and-seat-handover_2RgZDdpP.md`); Story S3: protocol and client cards (`2026-11-06_story-s3-protocol-and-client-cards_JztvpJ1j.md`); Story S4: tests, replay and bot (`2026-11-06_story-s4-tests-replay-and-bot_HnxDqZRT.md`); Story P0: the HollowMere arc (design) (`2026-11-06_story-p0-the-hollowmere-arc-design_B7eQSKQ5.md`); Story P4: achievements on the device (`2026-11-06_story-p4-achievements-on-the-device_SSXYJkcQ.md`); Story merge queue: round 10 PRs into the base (`2026-11-07_story-merge-queue-round-10-prs-into-the-base_YdYTm2cA.md`); Story P2: sections engine (`2026-11-07_story-p2-sections-engine_76C6nUHz.md`) ...

### Pipelines-Plugin: `teardowns/ninety-nine/chapters/08-future.md`

- First added: 2026-10-29 22:51; last changed: 2026-10-29 22:51; 1141 words
- Title: Future: what is stale and what is next
- Sections: What is stale; One programme, in the order the work depends on; The merge, in three steps; Never finished; Owner's word; Open threads
- Sessions that likely produced or used it: Teardown tool configuration (`2026-10-25_teardown-tool-configuration_kmQrd4JH.md`); Session autocompact strategy (`2026-10-29_session-autocompact-strategy_PTi8ZPYa.md`)

## Round packets (docs/roundN and docs/story in Who-Did-It)

### docs/ui (30 files; first added 2026-10-10)

- `docs/ui/asleep-1280x720.png`
- `docs/ui/asleep-390w.png`
- `docs/ui/band-1280x720.png`
- `docs/ui/band-390w.png`
- `docs/ui/crafting-1280x720.png`
- `docs/ui/crafting-390w.png`
- `docs/ui/hud-1280x720.png`
- `docs/ui/hud-390w.png`
- `docs/ui/inventory-1280x720.png`
- `docs/ui/inventory-390w.png`
- `docs/ui/landing-1280x720.png`
- `docs/ui/landing-390w.png`
- `docs/ui/line-1280x720.png`
- `docs/ui/line-390w.png`
- `docs/ui/lobby-1280x720.png`
- `docs/ui/lobby-390w.png`
- `docs/ui/lobby-mockup-1280x720.png`
- `docs/ui/lockpick-1280x720.png`
- `docs/ui/lockpick-390w.png`
- `docs/ui/meeting-1280x720.png`
- `docs/ui/meeting-390w.png`
- `docs/ui/menu-mockup-1280x720.png`
- `docs/ui/refusal-1280x720.png`
- `docs/ui/refusal-390w.png`
- `docs/ui/rolecard-back-1280x720.png`
- `docs/ui/rolecard-back-390w.png`
- `docs/ui/rolecard-front-1280x720.png`
- `docs/ui/rolecard-front-390w.png`
- `docs/ui/studio-npc-1280x720.png`
- `docs/ui/touch-390w.png`

### docs/round5 (10 files; first added 2026-10-17)

- `docs/round5/README.md` (592 words): Round 5: the contract documents
- `docs/round5/art-index.md` (261 words): The owner's ONUB room images (supplied 2026-10-17)
- `docs/round5/art-plan.md` (24647 words): Round-5 art plan: Sessions 5K, 5L and 5M
- `docs/round5/deck-data.md` (5509 words): Deck data: the main deck, the new roles, Impersonate and the look catalogue (round 5, 5F and 5G)
- `docs/round5/deck-wire.md` (10012 words): Deck wire: public looks, avatars, covers and Impersonate (round 5, 5F; with 5G's rules wire)
- `docs/round5/npc.md` (10561 words): NPC routines and the NPC tells (round 5, Session 5H)
- `docs/round5/onub-contract.md` (19337 words): ONUB v2: the round-5 contract for Sessions 5A to 5E
- `docs/round5/owner-brief.md` (2999 words): Round 5: the owner's brief and ONUB spec (2026-10-17, verbatim)
- `docs/round5/seams.md` (4576 words): Round-5 seams
- `docs/round5/world.md` (15443 words): Schemas, maps and scene outlines (round 5)

### docs/round6 (8 files; first added 2026-10-22)

- `docs/round6/README.md` (540 words): Round 6: the contract documents
- `docs/round6/auto-admin.md` (2470 words): Round-6 contract: the admin auto-mode
- `docs/round6/bible-seams.md` (1095 words): Round-6 contract: the Bible's seams, rounds 6 to 9
- `docs/round6/cutscene-music.md` (1772 words): Round-6 contract: cutscenes, loading, transitions, the trailer, music
- `docs/round6/m5b-data.md` (1364 words): Round-6 contract: M5b, resources, crafting, mobs, quests, mini-games
- `docs/round6/media.md` (2839 words): Round-6 media: the owner's audio, the two videos, the ROSW route
- `docs/round6/owner-brief.md` (15208 words): Round 6: the owner's brief
- `docs/round6/seams.md` (2152 words): Round-6 seams

### docs/guides (4 files; first added 2026-10-23)

- `docs/guides/ADMIN_GUIDE.md` (409 words): Admin guide: auto-mode
- `docs/guides/HOST_GUIDE.md` (489 words): Host guide
- `docs/guides/HOW_TO_PLAY.md` (945 words): How to play Who Did It
- `docs/guides/README.md` (112 words): Guides

### docs/round7 (8 files; first added 2026-10-23)

- `docs/round7/README.md` (551 words): Round 7: the contract documents
- `docs/round7/map-intros.md` (477 words): Map intro tracks and cinematic openings (7A)
- `docs/round7/minigames.md` (778 words): Mini-games: the stations and the polish (7M, round 7)
- `docs/round7/parties.md` (1199 words): Parties, profiles, friends and Quit
- `docs/round7/quick-mode-removal.md` (1394 words): The quick mode leaves; Crumb's Ovens gains its rooms
- `docs/round7/seams.md` (183 words): Round-7 seams
- `docs/round7/ui-reskin.md` (1537 words): The re-skin: the owner's two mockups, every screen
- `docs/round7/vendettas.md` (1082 words): Vendettas, the Daily Train and the Vicar's memorial (7H, 7I)

### docs/round8 (99 files; first added 2026-10-23)

- `docs/round8/README.md` (1263 words): Round 8: the contract documents
- `docs/round8/art.md` (2966 words): Art: characters, scale, HD and the rooms (8F, 8I, 8J, 8K)
- `docs/round8/body.md` (1543 words): Bodies: health, stamina, effects, fists, inspect (8A, 8B)
- `docs/round8/canon.md` (3811 words): Round 8 addendum C: the canon pass (8V)
- `docs/round8/economy.md` (1266 words): The economy: Book IV on today's maps and roles (8C, 8D)
- `docs/round8/hd-look/README.md` (658 words): The HD look sheet (8I, DECISIONS A164)
- `docs/round8/hd-look/building-8bit.png`
- `docs/round8/hd-look/building-hd.png`
- `docs/round8/hd-look/building-hdtex.png`
- `docs/round8/hd-look/building-lowpoly.png`
- `docs/round8/hd-look/building-pbr.png`
- `docs/round8/hd-look/contact-building.png`
- `docs/round8/hd-look/contact-figure.png`
- `docs/round8/hd-look/contact-room.png`
- `docs/round8/hd-look/figure-8bit.png`
- `docs/round8/hd-look/figure-hd.png`
- `docs/round8/hd-look/figure-hdtex.png`
- `docs/round8/hd-look/figure-lowpoly.png`
- `docs/round8/hd-look/figure-pbr.png`
- `docs/round8/hd-look/room-8bit.png`
- `docs/round8/hd-look/room-hd.png`
- `docs/round8/hd-look/room-hdtex.png`
- `docs/round8/hd-look/room-lowpoly.png`
- `docs/round8/hd-look/room-pbr.png`
- `docs/round8/hd-look/texture-strip.png`
- `docs/round8/hd-look/webp-q90.png`
- `docs/round8/icons/README.md` (914 words): Round 8 icons (8N): the review sheets
- `docs/round8/icons/icon_effect_bleeding.8bit.png`
- `docs/round8/icons/icon_effect_bleeding.hd.png`
- `docs/round8/icons/icon_effect_bleeding.lowpoly.png`
- `docs/round8/icons/icon_effect_dazed.8bit.png`
- `docs/round8/icons/icon_effect_dazed.hd.png`
- `docs/round8/icons/icon_effect_dazed.lowpoly.png`
- `docs/round8/icons/icon_effect_knockedOut.8bit.png`
- `docs/round8/icons/icon_effect_knockedOut.hd.png`
- `docs/round8/icons/icon_effect_knockedOut.lowpoly.png`
- `docs/round8/icons/icon_effect_poisoned.8bit.png`
- `docs/round8/icons/icon_effect_poisoned.hd.png`
- `docs/round8/icons/icon_effect_poisoned.lowpoly.png`
- `docs/round8/icons/icon_effect_stunned.8bit.png`
- `docs/round8/icons/icon_effect_stunned.hd.png`
- `docs/round8/icons/icon_effect_stunned.lowpoly.png`
- `docs/round8/icons/icon_effect_wounded.8bit.png`
- `docs/round8/icons/icon_effect_wounded.hd.png`
- `docs/round8/icons/icon_effect_wounded.lowpoly.png`
- `docs/round8/icons/sheet-01.png`
- `docs/round8/living.md` (2116 words): Round 8 addendum B: the living world (8Q, 8R, 8S, 8T, 8U)
- `docs/round8/motion.md` (1007 words): Motion: every new animation (8F, 8G, 8H)
- `docs/round8/seams.md` (2675 words): Round 8 seams: what the sessions share
- `docs/round8/shots/blackpine/after-bp_lodge-unlit.png`
- `docs/round8/shots/blackpine/after-bp_smithy-unlit.png`
- `docs/round8/shots/blackpine/altar-camp.png`
- `docs/round8/shots/blackpine/before-bp_camp-overview.png`
- `docs/round8/shots/blackpine/before-bp_camp-yard_0-play.png`
- `docs/round8/shots/blackpine/before-bp_deep-overview.png`
- `docs/round8/shots/blackpine/before-bp_deep-winze-play.png`
- `docs/round8/shots/blackpine/before-bp_lodge-front-play.png`
- `docs/round8/shots/blackpine/before-bp_lodge-overview.png`
- `docs/round8/shots/blackpine/before-bp_mill-door-play.png`
- `docs/round8/shots/blackpine/before-bp_mill-overview.png`
- `docs/round8/shots/blackpine/before-bp_mine-adit-play.png`
- `docs/round8/shots/blackpine/before-bp_mine-unlit.png`
- `docs/round8/shots/blackpine/before-bp_office-door-play.png`
- `docs/round8/shots/blackpine/before-bp_office-overview.png`
- `docs/round8/shots/blackpine/before-bp_smithy-overview.png`
- `docs/round8/shots/blackpine/before-bp_smithy-play.png`
- `docs/round8/shots/blackpine/before-bp_woods-camp-play.png`
- `docs/round8/shots/blackpine/before-bp_woods-overview.png`
- `docs/round8/shots/blackpine/black-market-lodge.png`
- `docs/round8/shots/blackpine/economy-props.png`
- `docs/round8/shots/blackpine/placed-bp_camp-overview.png`
- `docs/round8/shots/blackpine/placed-bp_camp-unlit.png`
- `docs/round8/shots/blackpine/placed-bp_camp-yard_0-play.png`
- `docs/round8/shots/blackpine/placed-bp_deep-overview.png`
- `docs/round8/shots/blackpine/placed-bp_deep-unlit.png`
- `docs/round8/shots/blackpine/placed-bp_deep-winze-play.png`
- `docs/round8/shots/blackpine/placed-bp_lodge-front-play.png`
- `docs/round8/shots/blackpine/placed-bp_lodge-overview.png`
- `docs/round8/shots/blackpine/placed-bp_lodge-unlit.png`
- `docs/round8/shots/blackpine/placed-bp_mill-door-play.png`
- `docs/round8/shots/blackpine/placed-bp_mill-overview.png`
- `docs/round8/shots/blackpine/placed-bp_mill-unlit.png`
- `docs/round8/shots/blackpine/placed-bp_mine-adit-play.png`
- `docs/round8/shots/blackpine/placed-bp_mine-unlit.png`
- `docs/round8/shots/blackpine/placed-bp_office-door-play.png`
- `docs/round8/shots/blackpine/placed-bp_office-overview.png`
- `docs/round8/shots/blackpine/placed-bp_office-unlit.png`
- `docs/round8/shots/blackpine/placed-bp_smithy-overview.png`
- `docs/round8/shots/blackpine/placed-bp_smithy-play.png`
- `docs/round8/shots/blackpine/placed-bp_smithy-unlit.png`
- `docs/round8/shots/blackpine/placed-bp_woods-camp-play.png`
- `docs/round8/shots/blackpine/placed-bp_woods-overview.png`
- `docs/round8/shots/blackpine/placed-bp_woods-unlit.png`
- `docs/round8/shots/blackpine/rack-mill.png`
- `docs/round8/shots/blackpine/shops-lodge.png`
- `docs/round8/shots/blackpine/shops-office.png`
- `docs/round8/stations.md` (3061 words): Stations: the hands-on widgets (7M, round 8 addendum C)
- `docs/round8/teardown.md` (1266 words): Round 8 addendum: the teardown answers (8L, 8M, 8N, 6Z)
- `docs/round8/townsfolk.md` (928 words): Moods, mugging and ambient townsfolk (8E)

### docs/round9 (14 files; first added 2026-10-24)

- `docs/round9/README.md` (1770 words): Round 9: the world-mode design round (design only, no code)
- `docs/round9/admin-studio.md` (2064 words): Admin Studio: creative mode, the room editor and reports (owner request, 2026-10-25)
- `docs/round9/emergent-play.md` (3978 words): Round 9: emergent play (9C)
- `docs/round9/failures.md` (7650 words): Round 9 (9B): failure messages
- `docs/round9/followup-4.md` (2933 words): Round 9: the follow-up calls (owner, 2026-10-26)
- `docs/round9/gdd-map.md` (3074 words): Round 9 (9D): the GDD map
- `docs/round9/living-world.md` (8659 words): Round 9: the living world (9C)
- `docs/round9/logic-table.md` (11394 words): Round 9 (9B): the logic table
- `docs/round9/owner-answers.md` (2873 words): Round 9: the owner's questionnaire answers
- `docs/round9/owner-brief.md` (2543 words): Round 9: the owner's brief (2026-10-24)
- `docs/round9/phases.md` (5235 words): Round 9 (9A): the phase screens
- `docs/round9/round10-plan.md` (3004 words): Round 9 (9D): the round-10 build plan
- `docs/round9/tools/prop-census.mjs`
- `docs/round9/world-mode.md` (13464 words): Round 9 (9A): world mode

### docs/round10 (10 files; first added 2026-10-29)

- `docs/round10/README.md` (2067 words): Round 10: world mode, the build
- `docs/round10/handoffs/10A-plans.md` (1050 words): 10A's plans for K1 and T4, with 6Z's answers
- `docs/round10/part2.md` (5551 words): Round 10, part 2: what is left
- `docs/round10/rolecards.md` (14167 words): Round 10 (10R): the role cards and the Satchel
- `docs/round10/samples/rolecards/build-mock.mjs`
- `docs/round10/samples/rolecards/index.html`
- `docs/round10/samples/rolecards/index.src.html`
- `docs/round10/scope.md` (13872 words): Round 10: the scope census (10S)
- `docs/round10/seams.md` (9418 words): Round 10 seams: what the sessions share
- `docs/round10/wave2-briefs.md` (3430 words): Round 10, wave 2: the spawn briefs

### docs/round11 (24 files; first added 2026-10-29)

- `docs/round11/README.md` (1631 words): Round 11: the full Blender makeover (planning, design only)
- `docs/round11/handoff/interior-props.json`
- `docs/round11/handoff/models-index.json`
- `docs/round11/handoff/models.lock.draft.json`
- `docs/round11/handoff/prop-models.md` (457 words): Who Did It: 3D asset index
- `docs/round11/handoff/prop_models_overview.jpg`
- `docs/round11/handoff/sheet_tavern_interior.png`
- `docs/round11/handoff/sheet_village_props.png`
- `docs/round11/look.md` (7931 words): Round 11: materials, styles and budgets (11B)
- `docs/round11/owner-answers.md` (708 words): Round 11: the owner's answers
- `docs/round11/pipeline.md` (5765 words): Round 11, 11A: the render pipeline
- `docs/round11/props.md` (5472 words): Round 11: the prop list (P1)
- `docs/round11/questions.md` (1562 words): Round 11: questions for the owner
- `docs/round11/round11-plan-v2.md` (2213 words): Round 11, revised: building the sprite world (A615)
- `docs/round11/round11-plan.md` (3424 words): Round 11: the build plan (the full Blender makeover)
- `docs/round11/samples/look/figure-styles.png`
- `docs/round11/samples/pipeline/lighting.png`
- `docs/round11/samples/pipeline/long-shadows.png`
- `docs/round11/samples/pipeline/long_shadows.py`
- `docs/round11/samples/pipeline/make_samples.py`
- `docs/round11/samples/pipeline/passes.png`
- `docs/round11/samples/pipeline/shadow-layer.png`
- `docs/round11/seams.md` (499 words): Round 11 seams: who owns what (the sprite world, A616)
- `docs/round11/tiles-brief.md` (1013 words): 11P P2: tiles and wall textures (brief, draft)

### docs/story (9 files; first added 2026-11-06)

- `docs/story/README.md` (2517 words): Story mode: the build contract
- `docs/story/arc.md` (7978 words): Story mode, part 2: the HollowMere arc
- `docs/story/orchestrator-handoff.md` (2116 words): Story mode part 2: orchestrator handoff
- `docs/story/part2.md` (1000 words): Story mode, part 2: the full story
- `docs/story/questions.md` (910 words): Story mode: the owner's questionnaire
- `docs/story/rite.md` (1847 words): Brief: the Medium's rite and the 10X Vicar
- `docs/story/script.md` (2425 words): Story mode: the script of A Winter in HollowMere
- `docs/story/status.md` (5270 words): Story mode: status
- `docs/story/test-plan.md` (636 words): Story mode: test plan (S4)

### docs/accounts (1 files; first added 2026-11-07)

- `docs/accounts/plan.md` (4373 words): Player accounts: the plan

### docs/map-revamp (1 files; first added 2026-11-12)

- `docs/map-revamp/interiors-plan.md` (2356 words): Map revamp: the interiors plan

### docs/round12 (1 files; first added 2026-11-17)

- `docs/round12/sprite-world.md` (1066 words): The sprite world: the merged 2.5D look (A615)
