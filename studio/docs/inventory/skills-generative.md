# Generative skills: video, music, image

Subsystem `skills-generative` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.93 · 3 entries · 19 corrections made to the first reading.

## Summary

Three markdown "skill" files cover generative AI: skills/higgsfield_api.skill.md (video), skills/suno_audio.skill.md (music) and skills/adobe_firefly.skill.md (image). Each calls itself a "self-extracting executable" and uses the Four-Part Artifact Architecture. Part 1 is the §0 Routing Header (YAML). Part 2 is §1 Prerequisites & State Verification: a bash block P1..Pn plus agent-level checks V1/V2. Part 3 is the numbered §2 Execution Process with two CONTEXT FLUSH points. Part 4 is §3 Embedded Artifacts: JSON payload templates, fixtures, a regex set and state-file schemas.

They are instructions for an agent acting as the "Studio Router" (Router.md §0). The agent is meant to follow them at Router.md intercept step 7 (EXECUTE). No code in the repo executes any of them. router.js routeSkill() only checks the gates against dashboard.json and writes to an in-browser LOCAL_EVENTS log. router.js dispatchAPICall() and writeDashboard() are defined but never called (the calls exist only in commented-out TODOs). dispatchAPICall's registry has higgsfield, deepseek and agent. It has no suno or firefly entry, although its own comment lists them as intended services. CI (tools/verify_system.py via .github/workflows/verify.yml) only checks the files statically:
- the skill is registered and on disk
- mandatory_context names a declared brand gate
- host_kinds is inside the dashboard enum
- no macOS-only binary or /Applications/ path appears inside fenced code
- pipeline phases point to registered skills with coherent progress.

README.md says, under "What does not run yet → Any routed task", that "no skill has a Content MD step wired in" and that router.js dispatch "is still stubs".

None of the state or output locations the skills use exist on disk: state/continuity_sm.json, state/style_ledger.json, state/suno_pending.lock, state/frames/, renders/ and .task_scratch/. state/ itself exists and holds rag_index/ and vault_manifest.json. .gitignore covers state/ and .task_scratch/ but not renders/. tools/bootstrap.sh creates state/ and .task_scratch/ but nothing writes .task_scratch/attestation.txt, which every P1 greps.

All three files carry a MIGRATION PENDING banner (DECISIONS.md "D6 addendum", which sits under the D7 heading). It says the dashboard.json → active_variables.* gates are stale. They must be read against the task's Content MD (vault/SCHEMA.md) `## Decisions in Force` / `## Method`, and "ask the operator" means the Router.md §5 mode gate. The current dashboard.json active_variables holds only _note, content_md, resolved_context and provisional_constraints. None of the keys these skills read or write is present (character_uuid, aspect_ratio, seed_lock, audio_bpm, audio_key, style_ref_id, master_palette, etc.).

The Content MD is read at Router intercept step 4 and written at step 8, outside the skill's own numbered steps. None of the three processes contains a Content MD step. Router.md §8 says flushes write to the Content MD, but the flushes in these files do not:
- higgsfield flushes 1 and 2 write dashboard.json
- suno flush 1 writes the dashboard event_log; flush 2 names no write target at all
- firefly flush 1 writes state/style_ledger.json + dashboard; flush 2 writes the dashboard.

D6 defers rewriting them: brush_designer "should be written first as the reference implementation", and skills/brush_designer.skill.md does not exist yet.

Routability today (dashboard.json + vault):
- **higgsfield_api:** parks at L3. motion_language and narrative_continuity are unauthored. The single vault Content MD's context_brand is [visual_identity, typography_system, color_science], so L1 cannot resolve them, and 1 note is below the ≥3 that L2 needs. The logged PARKED event (2026-08-23) also named visual_identity, but that gate was authored on 2026-08-31.
- **suno_audio:** would park the same way (sound_identity and brand_voice unauthored).
- **adobe_firefly:** both gates (visual_identity, color_science) are authored at L0, but both declare gaps: visual_identity §7 (generated-imagery motifs, framing, texture) and color_science §5 (working space, LUTs, grading).

## Tools

### higgsfield_api

`skill` · status `never-exercised`

Paths: `skills/higgsfield_api.skill.md`, `state/continuity_sm.json`, `state/frames/`, `dashboard.json`

Agent-followed instructions for AI video generation (image-to-video / text-to-video) through the Higgsfield REST API. Character, environment and seed persistence across chained shots is enforced through an on-disk Continuity State-Machine (ARTIFACT C).

**Entry points**

- `Router.md §2 intercept step 7: "EXECUTE Only now open the .skill.md and follow its Four-Part Architecture: Prerequisites → Execution Process → Embedded Artifacts." (an agent reads skills/higgsfield_api.skill.md after intercept steps 1-6)`
  - does: Runs the skill: the agent follows the §1 prerequisites, then the §2 numbered process, using the §3 artifacts.
  - changes: state/continuity_sm.json, state/frames/{shot_id}_last.png, dashboard.json, remote Higgsfield credits
- `control_room.html skill chip click → router.js renderSkills listener → routeSkill('skills/higgsfield_api.skill.md')`
  - does: resolveGates() returns [motion_language, narrative_continuity, visual_identity]. isAuthoredL0() checks each one against STATE.registries.context_brand_gates. motion_language and narrative_continuity are authored:false, so it calls logLocal('PARKED', ...) and returns {ok:false, parked:true, unresolvedAtL0:[context/brand/<role>.context.md ...]}. It fails closed (parks) if dashboard.json has not loaded. It does not execute the skill.
  - changes: the in-browser LOCAL_EVENTS array and console only (no file writes)
- `grep -q "ROUTER INTERCEPT" ./.task_scratch/attestation.txt || echo "FAIL:P1 no attestation"`
  - does: P1: checks that the Router intercept attestation exists for this task
  - changes: nothing
- `[ -n "${HIGGSFIELD_API_KEY:-}" ] && echo "OK:P2" || echo "FAIL:P2 missing HIGGSFIELD_API_KEY"`
  - does: P2: checks the credential is present (the file comment says never echo the key itself)
  - changes: nothing
- `HIGGSFIELD_BASE_URL="${HIGGSFIELD_BASE_URL:-https://platform.higgsfield.ai}" curl -s -o /dev/null -w "%{http_code}" --max-time 8 "$HIGGSFIELD_BASE_URL/health" | grep -qE "200|401" && echo "OK:P3" || echo "FAIL:P3 endpoint unreachable"`
  - does: P3: endpoint reachability. HTTP 200 or 401 counts as reachable. The file comment says the default is the same origin router.js registers for 'higgsfield'.
  - changes: nothing locally (outbound network call)
- `python3 -c "import json;json.load(open('state/continuity_sm.json'))" && echo "OK:P4" || echo "FAIL:P4"`
  - does: P4: checks the Continuity State-Machine exists and parses. The comment says to create it from ARTIFACT C on first run; the command itself creates nothing.
  - changes: nothing
- `df -Pk . | awk 'NR==2 {exit (int($4/1048576) < 20)}' && echo "OK:P5 disk" || echo "FAIL:P5 <20GB free"`
  - does: P5: requires at least 20 GB free disk for i2v frame extraction
  - changes: nothing
- `POST {HIGGSFIELD_BASE_URL}/v1/image2video (or /v1/text2video) with the ARTIFACT A payload`
  - does: Step 5 SUBMIT: submits a generation job and captures job_id
  - changes: remote job creation; spends Higgsfield credits (danger_class EXTERNAL_API_SPEND)
- `GET /v1/jobs/{job_id} every 20s, max 30 polls`
  - does: Step 7 POLL until a terminal state: completed | failed | nsfw_blocked. The file gives no base URL for this path.
  - changes: nothing

**Inputs**

- Task text matching trigger_a: "generate video", "motion", "animate shot", "camera move", "shot gen", "img2vid"
- trigger_b: .mp4 / .mov, or "pipeline phase status: awaiting_render on skill=higgsfield_api"
- Mandatory context: context/brand/motion_language.context.md, narrative_continuity.context.md, visual_identity.context.md (plus color_science 'if flagged in dashboard', per Router.md §3)
- state/continuity_sm.json: entities.*.uuid, entities.*.anchor_prompt, seed_lock, shot_ledger[last], last_frame_ref, continuity_mode, shot_index
- dashboard.json active_variables.character_uuid (V1), active_variables.aspect_ratio (step 4 / ARTIFACT A), pipeline.project (ARTIFACT A metadata). The two active_variables keys are absent from the current dashboard.json and are stale per D6: read them from the Content MD `## Decisions in Force` / `## Method` instead. pipeline.project is 'PROJECT_AURORA'.
- Shot-specific action (motion_language vocabulary only), motion_vector_preset (one of the ARTIFACT A library keys), model_id, character_ref_media_uuid, shot_id

**Outputs**

- Remote job id (hf_*) mapped to shot uuid (sht_*) in continuity_sm.json → job_map (ARTIFACT B remote_mapping)
- Downloaded generated video (the file gives no destination path)
- state/frames/{shot_id}_last.png (final frame extracted at step 8)
- Mutated state/continuity_sm.json: shot_ledger append, last_frame_ref, shot_index++, drift_check.due every 3rd shot, machine_state transitions
- dashboard.json writes: job_id, payload hash and seed (flush 1); 'complete dashboard state' (flush 2); continuity_drift flag (step 10); phase 'blocked' plus an event_log entry on any prerequisite failure

**Reads**

- skills/higgsfield_api.skill.md
- .task_scratch/attestation.txt
- state/continuity_sm.json
- dashboard.json
- context/brand/motion_language.context.md
- context/brand/narrative_continuity.context.md
- context/brand/visual_identity.context.md
- task Content MD under vault/ (per the MIGRATION PENDING banner and Router.md §7)

**Writes**

- state/continuity_sm.json
- state/frames/{shot_id}_last.png
- dashboard.json (writes_dashboard_keys: active_variables.character_uuid, active_variables.environment_uuid, active_variables.seed_lock, active_variables.motion_vector_preset; job_id / payload hash / seed; continuity_drift; pipeline phase; event_log)

**Depends on**

- POSIX shell (bash) with grep, curl, awk, df (tools/bootstrap.sh checks python3 curl awk df grep as 'required by every skill's prerequisite block')
- python3
- Higgsfield API (default base https://platform.higgsfield.ai)
- network access
- an unnamed frame-extraction tool (step 8 'Extract final frame' names none)

**Environment and secret names (names only)**

- HIGGSFIELD_API_KEY
- HIGGSFIELD_BASE_URL (optional; default https://platform.higgsfield.ai)

**Gates and checkpoints**

- The Router.md intercept must complete first; P1 greps for 'ROUTER INTERCEPT'. Router.md §2 defines an intercept violation as any tool call, script execution, or generative API payload issued before step 5 completes.
- Router.md §3/§5 ladder: L3 on any of motion_language / narrative_continuity / visual_identity parks the task in every mode. The dashboard.json event_log records ph_03 PARKED at L3 on 2026-08-23 naming all three. visual_identity was promoted to L0 on 2026-08-31 (GATE_AUTHORED), so motion_language and narrative_continuity remain unresolved.
- visual_identity §7: generated-imagery motifs, framing and texture are declared unresolved; the attestation must say so
- §1: 'Any failure → set pipeline phase to blocked, log to event_log, HALT' (the shell checks themselves only echo FAIL)
- P5: ≥20 GB free disk
- V1: dashboard active_variables.character_uuid must equal continuity_sm.json entities.character.uuid. A mismatch is a continuity fault → HALT and ask the operator which is canonical (per the banner, read as the Router §5 mode gate).
- V2: a continuation shot (shot_index > 1) requires last_frame_ref; otherwise route back to the operator
- Step 3: motion_language vocabulary only; custom motion vectors require operator sign-off; the seed is never randomized on continuation shots
- Step 4 DRY VALIDATE: print the full payload; no null UUIDs; aspect ratio matches the dashboard; duration ≤ 'policy max' (the value is not defined in the file)
- danger_class EXTERNAL_API_SPEND: 'every call costs credits — no speculative submissions'
- Step 10: if drift is detected, do NOT regenerate autonomously; flag continuity_drift and request operator review
- ARTIFACT C: ANY→BLOCKED on UUID mismatch, API 4xx, or 3 consecutive failed jobs
- ARTIFACT B: this skill NEVER mints chr_/env_ UUIDs; a UUID mismatch → HALT

**Invoked by**

- Router.md intercept step 7 (agent)
- Router.md §2 Trigger A row: 'generate video / motion / animate shot / camera move' + AI gen
- Router.md §2 Trigger B file-type: .mp4/.mov → 'higgsfield or adobe_suite'
- Router.md §2 Trigger B dashboard-state: a phase in this domain with status awaiting_render, compositing, queued or blocked
- dashboard.json pipeline.phases ph_03 'Shot Generation' (status blocked, progress_pct 62)
- router.js routeSkill via a control_room.html chip (gate check only)

**Invokes**

- Higgsfield REST: GET {base}/health (P3), POST {base}/v1/image2video, POST {base}/v1/text2video, GET /v1/jobs/{job_id}
- Router.md §5 mode gate (for every 'ask the operator', per the banner)

**Notes**

ROUTING HEADER (verbatim YAML): skill_id: higgsfield_api | version: 1.0 | trigger_a: ["generate video", "motion", "animate shot", "camera move", "shot gen", "img2vid"] | trigger_b: [".mp4", ".mov", "pipeline phase status: awaiting_render on skill=higgsfield_api"] | mandatory_context: [motion_language, narrative_continuity, visual_identity] | host_kinds: [windows, wsl, linux]   # network/API skill — no host-native bridge | writes_dashboard_keys: [active_variables.character_uuid, active_variables.environment_uuid, active_variables.seed_lock, active_variables.motion_vector_preset] | danger_class: EXTERNAL_API_SPEND   # every call costs credits — no speculative submissions.

Subtitle: 'Studio Headless OS · Skill 1/8 · Four-Part Artifact Architecture'. The repo now registers 9 skills.

FOUR PARTS: §0 Routing Header (Part 1); §1 Prerequisites & State Verification, P1-P5 plus V1-V2 (Part 2); §2 Execution Process, steps 1-11 (Part 3); §3 Embedded Artifacts A-C (Part 4). The file says: 'Do not summarize it. Unpack §3 artifacts, follow §2 in order, and mutate ARTIFACT C ... as the single source of truth'.

ARTIFACT A: the generation payload template. Fields: model {{model_id}}; prompt '{{character_anchor}} :: {{environment_anchor}} :: {{shot_action}}'; negative_prompt; seed {{seed_lock}}; duration_s 5; fps 24; aspect_ratio {{dashboard.active_variables.aspect_ratio}}; medias [start_image, character_reference]; motion {vector, strength 0.65}; webhook null; metadata {shot_id, project}. It also holds a motion_vector_library of 6 presets, each with vector / ease / use: dolly_in_slow_02, dolly_out_slow_01, truck_left_med_01, pedestal_up_slow, orbit_cw_15deg, static_breathe.

ARTIFACT B: the UUID handling protocol. Format prefix_[0-9a-f]{8}-slug; prefixes chr_ / env_ / prp_ / sht_ / hf_; rules for creation, propagation, collision_policy and remote_mapping.

ARTIFACT C: the Continuity State-Machine JSON, $schema 'studio-os/continuity-sm/v1'. It is a 'LIVE FILE' to copy to state/continuity_sm.json on first run. States: READY / GENERATING / VALIDATING / DRIFT_REVIEW / BLOCKED, with 5 transitions. Sample values: seed_lock 448811; continuity_mode 'chain'; entities chr_7f3a9d2e-aurora-lead and env_c4b81f00-neon-harbor, each with anchor_prompt and locked_attributes; shot_index 0; shot_ledger []; ledger_entry_schema; last_frame_ref null; job_map {}; drift_check {every_n_shots 3, due false, last_result null}.

THRESHOLDS: disk ≥20 GB; P3 timeout 8 s; poll 20 s × max 30; drift check every 3rd shot; BLOCKED after 3 consecutive failed jobs; motion strength 0.65.

CONTEXT FLUSH №1 (step 6): write job_id, payload hash and seed to dashboard.json; discard the raw payload; retain job_id, the state-machine handle and the attestation constraints. CONTEXT FLUSH №2 (step 11): write back the complete dashboard state; keep a state-machine summary of ≤10 lines; end, or chain to step 2.

CONTENT MD: the skill has no Content MD step. The Content MD is read at Router intercept step 4 and written at step 8, around skill step 7. Router §8 says flushes should write survivors to the Content MD, but this file's flushes still target dashboard.json (stale per D6).

The file never shows how HIGGSFIELD_API_KEY is sent: there is no auth header in ARTIFACT A or step 5. router.js registers higgsfield as 'https://platform.higgsfield.ai' with the comment '// via MCP in production', but dispatchAPICall is never called.

EXECUTION STATUS: instructions for an agent only. No script executes the skill. The state files and renders are absent. dashboard.json has an event_log RENDER_SUBMITTED 'Shot 07 → job hf_a91x, seed 448811' (2026-07-01), but D6 says the old active_variables were sample values, and no matching state exists. The DECISIONS.md D6 addendum lists these stale gates: V1 character_uuid vs. the state machine, seed_lock, aspect_ratio.

### suno_audio

`skill` · status `never-exercised`

Paths: `skills/suno_audio.skill.md`, `state/suno_pending.lock`, `renders/audio/`, `dashboard.json`

Agent-followed instructions for AI music generation through a Suno API. Prompts are built from fixed bracket-tag 'fixture' skeletons (ARTIFACT B), and key/BPM act as musical continuity locks.

**Entry points**

- `Router.md §2 intercept step 7 EXECUTE (agent opens skills/suno_audio.skill.md)`
  - does: Runs the §1 prerequisites and §2 steps 1-11
  - changes: renders/audio/, state/suno_pending.lock, dashboard.json, remote Suno credits
- `control_room.html skill chip click → router.js routeSkill('skills/suno_audio.skill.md')`
  - does: Resolves gates [sound_identity, brand_voice]. Both are authored:false in dashboard.json, so it logs PARKED locally and returns {ok:false, parked:true, unresolvedAtL0:[...]}.
  - changes: in-browser LOCAL_EVENTS only
- `grep -q "ROUTER INTERCEPT" ./.task_scratch/attestation.txt || echo "FAIL:P1"`
  - does: P1: the attestation exists
  - changes: nothing
- `[ -n "${SUNO_API_KEY:-}" ] && echo "OK:P2" || echo "FAIL:P2 missing SUNO_API_KEY"`
  - does: P2: the credential is present
  - changes: nothing
- `SUNO_BASE_URL="${SUNO_BASE_URL:-https://studio-api.suno.ai}" curl -s --max-time 8 -H "Authorization: Bearer ${SUNO_API_KEY:-}" "$SUNO_BASE_URL/api/get_limit" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('credits_left',0) >= 10 else 1)" && echo "OK:P3" || echo "FAIL:P3 insufficient credits"`
  - does: P3: quota check before any spend (credits_left ≥ 10). An unreachable endpoint or unparsable JSON also reports 'insufficient credits'.
  - changes: nothing locally (outbound network call)
- `mkdir -p renders/audio || echo "FAIL:P4 cannot create renders/audio" [ ! -f state/suno_pending.lock ] && echo "OK:P4" || echo "FAIL:P4 pending job lock exists"`
  - does: P4: creates the output directory and checks there is no orphan pending-job lock
  - changes: creates renders/audio/
- `POST {SUNO_BASE_URL}/api/custom_generate (headers Authorization: Bearer {SUNO_API_KEY}, Content-Type: application/json)`
  - does: Step 6 SUBMIT a custom generation; the returned ids are written to state/suno_pending.lock
  - changes: remote job; spends credits; writes state/suno_pending.lock
- `GET {SUNO_BASE_URL}/api/get?ids={{id1}},{{id2}} every 15s, max 40 polls (step 8 writes it as GET /api/get?ids={ids})`
  - does: Step 8 POLL until status 'complete' (ARTIFACT A terminal states: complete | error). Two clips per job are downloaded to renders/audio/.
  - changes: writes the downloaded clips to renders/audio/
- `POST {SUNO_BASE_URL}/api/extend_audio with body {audio_id, prompt, continue_at, tags}`
  - does: ARTIFACT A extend_clip. It is defined in the artifact but not referenced in the numbered process.
  - changes: remote job; spends credits

**Inputs**

- Task text matching trigger_a: "music", "track", "score", "stem", "theme", "drop", "verse", "soundtrack"
- trigger_b: .wav / .mp3 / .stem, or "pipeline phase skill=suno_audio"
- Mandatory context: context/brand/sound_identity.context.md, context/brand/brand_voice.context.md (plus narrative_continuity if flagged, per Router.md §3). Neither mandatory file exists on disk.
- Fixture family choice (grunge_92 | electronic_festival | score_ambient), resolved from sound_identity
- dashboard active_variables.audio_bpm / audio_key (V1, step 4). Both are absent from the current dashboard.json and stale per D6: read them from the Content MD instead.
- project, cue_id, cue spec (make_instrumental), lyric/texture lines. The file does not say where these come from.

**Outputs**

- Two clips per job in renders/audio/
- {cue_id}_master.mp3 (the selected clip) and the other clip archived as '_alt' (the exact name and location are not specified)
- state/suno_pending.lock, created at submit (step 6) and deleted at state write (step 10)
- dashboard.json: audio_bpm and audio_key (if first cue), phase progress, event_log (job ids + fixture id at flush 1)

**Reads**

- skills/suno_audio.skill.md
- .task_scratch/attestation.txt
- state/suno_pending.lock
- dashboard.json
- context/brand/sound_identity.context.md
- context/brand/brand_voice.context.md
- task Content MD under vault/ (per the banner)

**Writes**

- renders/audio/
- renders/audio/{cue_id}_master.mp3
- state/suno_pending.lock
- dashboard.json (writes_dashboard_keys: active_variables.audio_bpm, active_variables.audio_key; event_log; phase progress)

**Depends on**

- POSIX shell (bash) with grep, curl, mkdir
- python3
- Suno API (default base https://studio-api.suno.ai; model 'chirp-v4')
- network access

**Environment and secret names (names only)**

- SUNO_API_KEY
- SUNO_BASE_URL (optional; default https://studio-api.suno.ai)

**Gates and checkpoints**

- Router.md intercept attestation (P1)
- Router.md §5 ladder: sound_identity and brand_voice are unauthored. The single vault Content MD does not list either in context_brand, so L1 cannot resolve them, and 1 note is below the ≥3 that L2 needs. The route parks at L3.
- P3: credits_left ≥ 10 before any spend
- P4: an existing state/suno_pending.lock blocks a new submission (single pending job)
- §1 has no 'any failure → blocked/HALT' line (unlike higgsfield_api); the shell checks only echo FAIL
- V1: new cues MUST match the existing audio_bpm / audio_key, or be an approved modulation with operator sign-off (per the banner, read as the Router §5 mode gate)
- V2: the target pipeline phase must be queued or in_progress; never generate over a phase marked review
- Step 2: exactly ONE fixture family per generation; never blend
- Step 3: copy the bracket skeleton verbatim; do not add, remove or reorder tags
- 'Free-prose prompts are a protocol violation — always build from ARTIFACT B fixtures'
- Step 5 DRY VALIDATE: prompt ≤ 3000 chars, tags ≤ 200 chars, make_instrumental matches the cue spec, no key/BPM conflict with V1
- Step 9 A/B SELECT against the fixture pass_criteria
- extend_clip rule: tags MUST be byte-identical to the source clip
- danger_class EXTERNAL_API_SPEND

**Invoked by**

- Router.md intercept step 7 (agent)
- Router.md §2 Trigger A row: 'music / track / score / stem / drop / verse'
- Router.md §2 Trigger B file-type: .wav/.mp3/.stem → suno
- dashboard.json pipeline.phases ph_02 'Score & Stems' (status complete, 100)
- router.js routeSkill via a control_room.html chip (gate check only)

**Invokes**

- Suno REST: GET {base}/api/get_limit, POST {base}/api/custom_generate, GET {base}/api/get?ids=, POST {base}/api/extend_audio (artifact only)
- Router.md §5 mode gate (per the banner)

**Notes**

ROUTING HEADER (verbatim YAML): skill_id: suno_audio | version: 1.0 | trigger_a: ["music", "track", "score", "stem", "theme", "drop", "verse", "soundtrack"] | trigger_b: [".wav", ".mp3", ".stem", "pipeline phase skill=suno_audio"] | mandatory_context: [sound_identity, brand_voice] | host_kinds: [windows, wsl, linux]   # network/API skill — no host-native bridge | writes_dashboard_keys: [active_variables.audio_bpm, active_variables.audio_key] | danger_class: EXTERNAL_API_SPEND.

Subtitle: 'Studio Headless OS · Skill 2/8 · Four-Part Artifact Architecture'.

FOUR PARTS: §0 Routing Header; §1 Prerequisites P1-P4 + V1-V2; §2 Execution Process, steps 1-11; §3 Embedded Artifacts A-B (there is no ARTIFACT C).

ARTIFACT A: 'API Request Payloads (exact wire format)'.
- custom_generate: endpoint and headers as above; body prompt ({{bracket_structured_lyrics_or_[Instrumental]_tags}}), tags '{{fixture.style_tags}}, {{bpm}} bpm, {{key}}', title '{{project}}_{{cue_id}}', make_instrumental false, model 'chirp-v4', wait_audio false.
- poll_status: endpoint GET {SUNO_BASE_URL}/api/get?ids={{id1}},{{id2}}; terminal_states [complete, error]; response_fields_of_interest [id, status, audio_url, metadata.duration, metadata.tags].
- extend_clip: POST /api/extend_audio with the rule that tags must be byte-identical.

ARTIFACT B: 'Fixtures: Mathematically Perfect Structural Prompting'. Each family has style_tags, a bracket_skeleton and pass_criteria.
- grunge_92: default 112 bpm, E minor. pass_criteria: distortion present bar 1; dynamic drop at bridge ≥ 6dB; no synthetic sheen.
- electronic_festival: 128 bpm, F minor. pass_criteria: drop lands within ±1 bar of build end; sidechain audible; hook intelligible.
- score_ambient: 70 bpm, F minor; its skeleton begins '[Instrumental]'. pass_criteria: no percussive transients; sits under dialogue at -18 LUFS; matches project key F minor.
- structural_laws (4): one family per generation; bracket tags are load-bearing; Verse 2 syllable-count match ±1; tags = timbre, skeleton = structure.

THRESHOLDS: credits ≥ 10; P3 timeout 8 s; prompt ≤ 3000; tags ≤ 200; poll 15 s × max 40; 2 clips per job.

CONTEXT FLUSH №1 (step 7): persist job ids + fixture id to the dashboard event_log; discard lyric drafts and rejected variants. CONTEXT FLUSH №2 (step 11): reduce working memory to cue id, file path and key/BPM; chain to step 2 or end. It names no write target. The dashboard write happens at step 10 STATE WRITE.

CONTENT MD: the skill has no Content MD step. The Content MD sits at Router intercept steps 4 and 8. Flush 1 still targets the dashboard (stale per D6).

EXECUTION STATUS: instructions for an agent only. router.js dispatchAPICall has no 'suno' registry entry. If called it would return {ok:false, error:'unregistered service: suno'}, but it is never called. No renders/ directory or lock file exists. dashboard.json marks ph_02 complete with no artifacts on disk. The DECISIONS.md D6 addendum lists the V1 audio_bpm/audio_key continuity locks as stale. vault/_migration/GAP-ANALYSIS.md §6 says that, after a hypothetical complete migration of the prose corpus (which would serve brand_voice), suno_audio is 'one authored file away' from routing: sound_identity.

### adobe_firefly

`skill` · status `never-exercised`

Paths: `skills/adobe_firefly.skill.md`, `state/style_ledger.json`, `renders/stills/`, `.task_scratch/ff_resp_{ts}.json`, `dashboard.json`

Agent-followed instructions for AI image generation through the Adobe Firefly API, using OAuth server-to-server auth. Responses are parsed only with an embedded regex set, and a style-reference ledger (state/style_ledger.json) serves as the style-continuity record.

**Entry points**

- `Router.md §2 intercept step 7 EXECUTE (agent opens skills/adobe_firefly.skill.md)`
  - does: Runs the §1 prerequisites and §2 steps 1-9
  - changes: state/style_ledger.json, renders/stills/, .task_scratch/ff_resp_{ts}.json, dashboard.json, remote Firefly usage
- `control_room.html skill chip click → router.js routeSkill('skills/adobe_firefly.skill.md')`
  - does: Resolves gates [visual_identity, color_science]. Both are authored:true, so it logs INTERCEPT 'UI-initiated route → skills/adobe_firefly.skill.md · L0 context: ... (stub)' and returns {ok:true, skill, gates, paths}. Nothing is dispatched; the dispatchAPICall('agent','/route',...) line is a commented-out TODO.
  - changes: in-browser LOCAL_EVENTS only
- `grep -q "ROUTER INTERCEPT" ./.task_scratch/attestation.txt || echo "FAIL:P1"`
  - does: P1: the attestation exists
  - changes: nothing
- `[ -n "$FIREFLY_CLIENT_ID" ] && [ -n "$FIREFLY_CLIENT_SECRET" ] && echo "OK:P2" || echo "FAIL:P2"`
  - does: P2: the OAuth server-to-server credentials are present
  - changes: nothing
- `TOKEN=$(curl -s -X POST "https://ims-na1.adobelogin.com/ims/token/v3" -d "client_id=$FIREFLY_CLIENT_ID&client_secret=$FIREFLY_CLIENT_SECRET&grant_type=client_credentials&scope=openid,AdobeID,firefly_api" | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))") [ -n "$TOKEN" ] && echo "OK:P3" || echo "FAIL:P3 token mint failed"`
  - does: P3: mints an access token into the shell variable TOKEN. The comment says it expires in ~24h and must never be cached across days. ARTIFACT A's header placeholder is {ACCESS_TOKEN}.
  - changes: remote token issuance; shell variable only
- `python3 -c "import json;json.load(open('state/style_ledger.json'))" 2>/dev/null && echo "OK:P4" || { echo '{"refs":[]}' > state/style_ledger.json && echo "OK:P4 (initialized)"; }`
  - does: P4: checks that the style-ref ledger exists and parses; otherwise initializes an empty one. A malformed existing ledger is overwritten. There is no mkdir: it relies on state/ existing (it does exist on disk, and tools/bootstrap.sh creates it).
  - changes: may create or overwrite state/style_ledger.json with {"refs":[]}
- `POST https://firefly-api.adobe.io/v3/images/generate (headers Authorization: Bearer {ACCESS_TOKEN}, x-api-key: {FIREFLY_CLIENT_ID}, Content-Type: application/json)`
  - does: Step 3 SUBMIT. The raw response body is saved to ./.task_scratch/ff_resp_{ts}.json BEFORE any parsing.
  - changes: remote generation; writes .task_scratch/ff_resp_{ts}.json
- `POST https://firefly-api.adobe.io/v2/storage/image (headers_override Content-Type: image/png; body = raw PNG bytes)`
  - does: Step 7 STYLE-REF MINT upload, run only when the operator marks an output 'canon'. The upload id is parsed with RX_UPLOAD_ID (the returns field is images[0].id).
  - changes: remote upload; a state/style_ledger.json entry; dashboard style_ref_id / style_ref_id_prev
- `POST https://firefly-api.adobe.io/v3/images/expand`
  - does: ARTIFACT A expand_image: body image.source.uploadId, size 3840x1646, edge continuation prompt. It is defined in the artifact but not referenced in the numbered process.
  - changes: remote generation

**Inputs**

- Task text matching trigger_a: "generate image", "concept art", "style frame", "style ref", "firefly", "key art"
- trigger_b: ".png reference", ".jpg reference", "pipeline phase skill=adobe_firefly"
- Mandatory context: context/brand/visual_identity.context.md, context/brand/color_science.context.md (plus typography_system if flagged, per Router.md §3)
- dashboard active_variables.style_ref_id (V1) and master_palette (V2). Both are absent from the current dashboard.json and stale per D6: read them from the Content MD. color_science §2 holds the 10-value UI palette in sRGB hex.
- state/style_ledger.json refs[]
- Prompt composed from visual_identity vocabulary; optional named preset; style_ref upload handle; optional composition ref; explicit seeds; shot_or_frame_id
- Operator 'canon' marking (triggers step 7)

**Outputs**

- .task_scratch/ff_resp_{ts}.json (the raw response, kept on disk for audit)
- renders/stills/{shot_or_frame_id}_{seed}.png
- state/style_ledger.json entries in the ARTIFACT C schema: id sref_ff_{yyyymmdd}_{4hex}, upload_id, source_png, seed, minted_ts, canon, palette_check, supersedes
- dashboard.json: style_ref_id / style_ref_id_prev supersede and the parsed fields (flush 1); pass/fail per image is logged in the ledger entry (step 8)

**Reads**

- skills/adobe_firefly.skill.md
- .task_scratch/attestation.txt
- state/style_ledger.json
- .task_scratch/ff_resp_{ts}.json
- dashboard.json
- context/brand/visual_identity.context.md
- context/brand/color_science.context.md
- task Content MD under vault/ (per the banner)

**Writes**

- state/style_ledger.json
- .task_scratch/ff_resp_{ts}.json
- renders/stills/{shot_or_frame_id}_{seed}.png
- dashboard.json (writes_dashboard_keys: active_variables.style_ref_id, active_variables.style_ref_id_prev)

**Depends on**

- POSIX shell (bash) with grep, curl
- python3 (json; the re module for the ARTIFACT B regexes, which are labelled 'Python re')
- Adobe IMS token endpoint https://ims-na1.adobelogin.com/ims/token/v3
- Adobe Firefly API https://firefly-api.adobe.io
- network access

**Environment and secret names (names only)**

- FIREFLY_CLIENT_ID
- FIREFLY_CLIENT_SECRET
- TOKEN (runtime shell variable minted at P3; ARTIFACT A calls it {ACCESS_TOKEN}; not a stored env var)

**Gates and checkpoints**

- Router.md intercept attestation (P1)
- Router.md §3: the gates visual_identity and color_science are both authored (L0). visual_identity §7 declares generated-imagery motifs, framing and texture unresolved. color_science §5 declares working space, LUTs and grading unresolved ('adobe_firefly ... get a palette, not a colour pipeline'). A route needing those must say so in its attestation.
- §1 has no 'any failure → blocked/HALT' line (unlike higgsfield_api); the shell checks only echo FAIL
- V1: dashboard style_ref_id must exist in state/style_ledger.json refs[]; otherwise HALT
- V2: palette lock. The request's color intent must map into master_palette per color_science; off-palette requests need an operator override (per the banner, read as the Router §5 mode gate).
- Step 3: the raw body must be saved to disk BEFORE parsing
- Step 4 PARSE: required captures are image_url, seed and content_class (optional: style_ref_upload_id). A miss is a malformed response → retry once, then 'blocked'.
- ARTIFACT B parse_law: the regexes run on the SAVED raw body file only; zero matches on a required capture is a hard failure
- RX_ERROR_CODE: rate_limited → back off 30s; validation → fix the payload, do not retry blind
- Step 5: download presigned URLs immediately (they expire)
- Step 7 runs only when the operator marks an output 'canon'
- Step 8 VALIDATE against the visual_identity constraints and the V2 palette lock
- 'eyeballing JSON responses and hand-copying IDs is a protocol violation'
- danger_class EXTERNAL_API_SPEND

**Invoked by**

- Router.md intercept step 7 (agent)
- Router.md §2 Trigger A row: 'generate image / concept art / style ref / firefly'
- dashboard.json pipeline.phases ph_01 'Concept & Style Frames' (status complete, 100)
- router.js routeSkill via a control_room.html chip (gate check only; returns an ok:true stub)
- Not in Router.md §2 Trigger B: its file-type list has no .png/.jpg mapping, although the skill's own trigger_b lists them

**Invokes**

- Adobe IMS POST /ims/token/v3
- Firefly POST /v3/images/generate, POST /v2/storage/image, POST /v3/images/expand (artifact only)
- Router.md §5 mode gate (per the banner)

**Notes**

ROUTING HEADER (verbatim YAML): skill_id: adobe_firefly | version: 1.0 | trigger_a: ["generate image", "concept art", "style frame", "style ref", "firefly", "key art"] | trigger_b: [".png reference", ".jpg reference", "pipeline phase skill=adobe_firefly"] | mandatory_context: [visual_identity, color_science] | host_kinds: [windows, wsl, linux]   # network/API skill — no host-native bridge | writes_dashboard_keys: [active_variables.style_ref_id, active_variables.style_ref_id_prev] | danger_class: EXTERNAL_API_SPEND.

Subtitle: 'Studio Headless OS · Skill 3/8 · Four-Part Artifact Architecture'.

FOUR PARTS: §0 Routing Header; §1 Prerequisites P1-P4 + V1-V2; §2 Execution Process, steps 1-9; §3 Embedded Artifacts A-C.

ARTIFACT A: payload structures.
- auth_headers: Authorization Bearer {ACCESS_TOKEN}, x-api-key {FIREFLY_CLIENT_ID}, Content-Type application/json.
- generate_images body: prompt; negativePrompt 'text, watermark, logo, oversaturation'; numVariations 2; seeds [448811, 448812]; size 2688x1152; contentClass 'photo'; visualIntensity 6; style {presets, strength 60, imageReference.source.uploadId}; structure {strength 40, imageReference}.
- upload_reference: returns images[0].id.
- expand_image: 3840x1646.

ARTIFACT B: a 'Surgical Regex Set' for Python re, each entry with pattern / mode / capture / purpose:
- RX_IMAGE_URL (findall, capture 1)
- RX_SEED (findall, 1)
- RX_UPLOAD_ID (search, 1; 36-char hex/dash id)
- RX_CONTENT_CLASS (search, 1; photo|art)
- RX_STYLE_REF_LEDGER_ID (findall, capture 0; \bsref_ff_(\d{8})_([0-9a-f]{4})\b)
- RX_ERROR_CODE (search, 1)
- parse_law.

ARTIFACT C: the style ledger entry schema for state/style_ledger.json. Sample entry: id sref_ff_20260630_114a, source_png renders/stills/anchor_448811.png, supersedes sref_ff_20260628_09c1.

THRESHOLDS: 2 variations; retry once on a parse miss; 30 s back-off on rate_limited; token ~24h.

CONTEXT FLUSH №1 (step 6): write the parsed fields to state/style_ledger.json and the dashboard; drop the raw response from working memory (the file stays on disk). CONTEXT FLUSH №2 (step 9): reduce working memory to the ledger entry summary + file paths; write back the dashboard; end or chain.

CONTENT MD: the skill has no Content MD step. The Content MD sits at Router intercept steps 4 and 8. The flushes still target the dashboard and ledger (stale per D6). The step 7 '_prev' supersede conflicts with D6, which removed Router's old 'supersede with _prev' rule. router.js renderVariables skips keys ending in '_prev'.

EXECUTION STATUS: instructions for an agent only. router.js dispatchAPICall has no 'firefly' registry entry and is never called. state/style_ledger.json, renders/stills/ and .task_scratch/ are absent. dashboard.json marks ph_01 complete with no artifacts on disk. The D6 addendum lists V1, V2 and §2.7 as stale. This is the only one of the three whose mandatory gates are both authored at L0, but both are partial by declaration. The vault Content MD vault/studio-os/ui/ui-ux-intelligence-integration.md lists 'Author visual_identity §7' as a Next Step affecting adobe_firefly and higgsfield_api.

## Usage flows

### Router intercept wrapping any generative skill (Router.md §2)

1. Trigger A (an intent phrase from the Router §2 table) or Trigger B (asset file type, or a dashboard.json pipeline phase in awaiting_render / compositing / queued / blocked in the task domain) fires for higgsfield_api, suno_audio or adobe_firefly
2. 1 MODE: read dashboard.json system_status.mode (currently 'autonomous')
3. 2 RESOLVE: map the skill to its mandatory context via Router.md §3 (mirrored in router.js resolveGates and in the skill's mandatory_context header)
4. 3 LADDER: resolve each context at L0 authored / L1 recalled / L2 derived (≥3 notes) / L3 unresolved; apply the mode gate. L3 parks in every mode.
5. 4 RECALL: locate or create the task Content MD (vault/_templates/content-md.md, status seed); read Overview, Next Steps, Decisions in Force and Method in full. Per the MIGRATION PENDING banner, this is where the migrated gate values live.
6. 5 VERIFY: print the ROUTER INTERCEPT attestation block (§6). The skill's P1 greps ./.task_scratch/attestation.txt for this text, but nothing in the repo writes that file.
7. 6 STATE: confirm there is no phase conflict; write the phase → in_progress
8. 7 EXECUTE: open the .skill.md; run the §1 Prerequisites, then the §2 Execution Process, using the §3 Embedded Artifacts
9. 8 WRITEBACK: update the Content MD (Timeline, Next Steps, Decisions in Force, Method, updated/status), then dashboard.json + event_log

### higgsfield_api shot generation / chaining

1. P1-P5 prerequisite shell checks (any failure → phase blocked, event_log, HALT); V1 character_uuid match; V2 last_frame_ref for continuation shots
2. 1 UNPACK ARTIFACT A (payload + motion vectors), B (UUID protocol), C (state machine)
3. 2 STATE READ state/continuity_sm.json: entity uuids, anchor_prompts, seed_lock, shot_ledger[last]
4. 3 PAYLOAD BUILD: prompt = character anchor + environment anchor + shot action (motion_language vocabulary only); seed = seed_lock; motion.vector from the library; start_image = last_frame_ref when continuity_mode is 'chain'
5. 4 DRY VALIDATE: print the payload; no null UUIDs; aspect ratio matches; duration ≤ policy max
6. 5 SUBMIT POST {HIGGSFIELD_BASE_URL}/v1/image2video or /v1/text2video → job_id (state READY→GENERATING)
7. 6 CONTEXT FLUSH №1: job_id, payload hash and seed → dashboard.json; drop the raw payload
8. 7 POLL GET /v1/jobs/{job_id} every 20s, ≤30 polls; terminal states completed | failed | nsfw_blocked
9. 8 VALIDATE OUTPUT: download; check duration/fps/aspect; save the final frame to state/frames/{shot_id}_last.png (GENERATING→VALIDATING)
10. 9 STATE WRITE: append to shot_ledger, update last_frame_ref, shot_index++, set drift_check.due every 3rd shot (VALIDATING→READY)
11. 10 DRIFT CHECK every 3rd shot against the shot 1 anchor frame; on drift, flag continuity_drift and request operator review (VALIDATING→DRIFT_REVIEW)
12. 11 CONTEXT FLUSH №2: write back the dashboard; keep a ≤10-line state summary; end, or loop to step 2 for the next shot

### suno_audio cue generation with A/B select

1. P1-P4 prerequisite checks: attestation; SUNO_API_KEY; credits_left ≥ 10 via /api/get_limit; mkdir renders/audio; no suno_pending.lock. Then V1 key/BPM lock and V2 phase queued/in_progress.
2. 1 UNPACK ARTIFACT A payloads + ARTIFACT B fixtures
3. 2 STYLE RESOLVE: pick ONE fixture family from sound_identity (grunge_92 | electronic_festival | score_ambient)
4. 3 STRUCTURE BUILD: copy the bracket skeleton verbatim; replace only lyric/texture lines
5. 4 PAYLOAD BUILD custom_generate: tags = fixture style_tags + BPM/key from the dashboard; title = {project}_{cue_id}
6. 5 DRY VALIDATE: prompt ≤3000, tags ≤200, make_instrumental matches the cue spec, no key/BPM conflict
7. 6 SUBMIT POST {SUNO_BASE_URL}/api/custom_generate; write the returned ids to state/suno_pending.lock
8. 7 CONTEXT FLUSH №1: job ids + fixture id → dashboard event_log; discard drafts
9. 8 POLL GET /api/get?ids= every 15s, ≤40 polls; download both clips to renders/audio/
10. 9 A/B SELECT against the fixture pass_criteria; rename the winner {cue_id}_master.mp3 and archive the other as _alt
11. 10 STATE WRITE: dashboard audio_bpm/audio_key (first cue), phase progress, event log; delete suno_pending.lock
12. 11 CONTEXT FLUSH №2: keep cue id, file path and key/BPM (no write target named); chain to step 2 or end

### adobe_firefly still generation and canon style-ref mint

1. P1-P4 prerequisite checks: attestation; FIREFLY_CLIENT_ID/SECRET; mint the IMS token into TOKEN; ensure state/style_ledger.json exists (initialize/overwrite if missing or unparsable). Then V1 style_ref_id in the ledger and V2 palette lock.
2. 1 UNPACK ARTIFACT A payloads + ARTIFACT B regex set
3. 2 PAYLOAD BUILD generate_images: prompt from visual_identity; style.imageReference = the current style_ref upload handle when continuity is required; explicit seeds
4. 3 SUBMIT POST https://firefly-api.adobe.io/v3/images/generate; save the raw body to ./.task_scratch/ff_resp_{ts}.json before parsing
5. 4 PARSE with the ARTIFACT B regexes on the saved file; image_url, seed and content_class are required (miss → retry once → blocked)
6. 5 DOWNLOAD the presigned image_url(s) to renders/stills/{shot_or_frame_id}_{seed}.png
7. 6 CONTEXT FLUSH №1: parsed fields → state/style_ledger.json + dashboard
8. 7 STYLE-REF MINT (only when the operator marks 'canon'): POST /v2/storage/image; parse RX_UPLOAD_ID; mint sref_ff_{yyyymmdd}_{4hex}; the dashboard's current style_ref_id → style_ref_id_prev, and the new id → style_ref_id
9. 8 VALIDATE the images against visual_identity + the palette lock; log pass/fail in the ledger entry
10. 9 CONTEXT FLUSH №2: keep the ledger summary + paths; write back the dashboard; end or chain

### Control room chip click (the only in-repo code path that touches these skills)

1. Open control_room.html (it loads router.js via <script src="router.js">). router.js fetches dashboard.json on load and every 5000 ms (POLL_MS), pausing while the tab is hidden.
2. renderSkills builds one button chip per registries.skills entry; all 9 are status 'ready'
3. Click a chip → routeSkill(file) → resolveGates(file) (a hard-coded table mirroring Router.md §3) → isAuthoredL0(role) against STATE.registries.context_brand_gates
4. higgsfield_api / suno_audio: unresolved gates → logLocal PARKED; returns {ok:false, parked:true, unresolvedAtL0}
5. adobe_firefly: both gates authored → logLocal INTERCEPT '(stub)'; returns {ok:true, skill, gates, paths}. The dispatchAPICall('agent','/route',...) line is a commented-out TODO.
6. No API call, no file write, no skill execution. dispatchAPICall and writeDashboard are never invoked anywhere.

### PROJECT_AURORA pipeline ordering declared in dashboard.json

1. ph_01 'Concept & Style Frames' → adobe_firefly (complete, 100%)
2. ph_02 'Score & Stems' → suno_audio (complete, 100%)
3. ph_03 'Shot Generation' → higgsfield_api (blocked, 62%). event_log 2026-08-23: PARKED at L3 on motion_language, narrative_continuity, visual_identity; visual_identity was authored on 2026-08-31.
4. ph_04 blender_python (queued) → ph_05 adobe_suite_uxp (status compositing, 18%) → ph_06 css_html_ui (queued)
5. The skill files define no data handoff between phases

### CI static checks touching these skill files

1. .github/workflows/verify.yml runs on push to main, pull_request and workflow_dispatch (ubuntu-latest, Python 3.11)
2. python3 tools/verify_system.py runs: - check_skill_registry: each skill is on disk and registered in dashboard registries.skills - check_brand_gates: gates_skills name registered skills - check_skill_headers: mandatory_context names a declared brand gate - check_host_portability: host_kinds ⊆ dashboard host_kind_enum; no osascript/vm_stat/sysctl/afplay/pbcopy at command position, and no /Applications/, inside fenced code - check_router_js: every gate role appears in router.js - check_pipeline: ph_01-ph_06 skills are registered, statuses are in the enum, and progress is coherent
3. The step is repeated as python3 -W error::EncodingWarning tools/verify_system.py --quiet; node --check router.js; dashboard.json parse
4. Nothing in CI executes the skills' bash prerequisites or API calls

## Relationships

| From | Relation | To |
|---|---|---|
| Router.md | invokes at intercept step 7 EXECUTE; Trigger A row 'generate video / motion / animate shot / camera move'; Tr… | higgsfield_api |
| Router.md | invokes at intercept step 7 EXECUTE; Trigger A row 'music / track / score / stem / drop / verse'; Trigger B .… | suno_audio |
| Router.md | invokes at intercept step 7 EXECUTE; Trigger A row 'generate image / concept art / style ref / firefly'; no T… | adobe_firefly |
| higgsfield_api | mandatory_context gate (unauthored; not on disk) | context/brand/motion_language.context.md |
| higgsfield_api | mandatory_context gate (unauthored; not on disk) | context/brand/narrative_continuity.context.md |
| higgsfield_api | mandatory_context gate (authored L0 since 2026-08-31; §7 generated-imagery motifs/framing/texture declared un… | context/brand/visual_identity.context.md |
| higgsfield_api | conditional context 'if flagged in dashboard' (Router.md §3; context/brand/README.md marks it with *) | context/brand/color_science.context.md |
| suno_audio | mandatory_context gate (unauthored; not on disk) | context/brand/sound_identity.context.md |
| suno_audio | mandatory_context gate (unauthored; not on disk) | context/brand/brand_voice.context.md |
| suno_audio | conditional context 'if flagged in dashboard' (Router.md §3) | context/brand/narrative_continuity.context.md |
| adobe_firefly | mandatory_context gate (authored L0; partial by its own §7) | context/brand/visual_identity.context.md |
| adobe_firefly | mandatory_context gate (authored L0; gives a 10-value sRGB UI palette, 'not a colour pipeline', per its §5) | context/brand/color_science.context.md |
| adobe_firefly | conditional context 'if flagged in dashboard' (Router.md §3) | context/brand/typography_system.context.md |
| router.js | resolveGates table mirrors mandatory_context; routeSkill gate-checks only; the dispatchAPICall registry has h… | higgsfield_api |
| router.js | resolveGates mirror; no 'suno' entry in the dispatchAPICall registry, although its comment lists it | suno_audio |
| router.js | resolveGates mirror; no 'firefly' entry in the dispatchAPICall registry; renderVariables skips '_prev' keys | adobe_firefly |
| control_room.html | loads router.js; the skill chips it renders call routeSkill(file) | router.js |
| tools/verify_system.py | static checks: registry, mandatory_context, host_kinds, macOS binaries in fenced code, pipeline phase ph_03 (… | higgsfield_api |
| tools/verify_system.py | static checks (same; pipeline phase ph_02) | suno_audio |
| tools/verify_system.py | static checks (same; pipeline phase ph_01) | adobe_firefly |
| dashboard.json | pipeline phase ph_01 skill; registries.skills entry status ready; context_brand_gates gates_skills (visual_id… | adobe_firefly |
| dashboard.json | pipeline phase ph_02 skill; registries.skills entry status ready; gates_skills (sound_identity, brand_voice) | suno_audio |
| dashboard.json | pipeline phase ph_03 skill (blocked); event_log PARKED 2026-08-23 and INTERCEPT / CONTEXT_LOADED / RENDER_SUB… | higgsfield_api |
| adobe_firefly | precedes in dashboard.json pipeline order (ph_01 → ph_02); no data handoff defined | suno_audio |
| suno_audio | precedes in dashboard.json pipeline order (ph_02 → ph_03); no data handoff defined | higgsfield_api |
| higgsfield_api | share Router.md Trigger B file types .mp4/.mov ('higgsfield or adobe_suite') | adobe_suite_uxp |
| DECISIONS.md | D6 addendum: stale gates (V1 character_uuid vs. the state machine, seed_lock, aspect_ratio); MIGRATION PENDIN… | higgsfield_api |
| DECISIONS.md | D6 addendum: stale V1 audio_bpm/audio_key locks | suno_audio |
| DECISIONS.md | D6 addendum: stale V1 style_ref_id ledger check, V2 master_palette lock, §2.7 _prev supersede; D6 removed the… | adobe_firefly |
| higgsfield_api | durable state destination per the banner (Content MD ## Decisions in Force / ## Method); read at intercept st… | vault/SCHEMA.md |
| suno_audio | durable state destination per the banner | vault/SCHEMA.md |
| adobe_firefly | durable state destination per the banner; SCHEMA.md example frontmatter lists skills: [adobe_firefly, brush_d… | vault/SCHEMA.md |
| vault/studio-os/ui/ui-ux-intelligence-integration.md | the only vault Content MD; its Next Steps says adobe_firefly and higgsfield_api find the visual_identity imag… | adobe_firefly |
| vault/_migration/GAP-ANALYSIS.md | §6 table: after a hypothetical complete corpus migration suno_audio is 'one authored file away' (sound_identi… | suno_audio |
| context/brand/README.md | gate table lists which brand files gate firefly / higgsfield / suno_audio, with * for conditional; the file s… | higgsfield_api |
| tools/bootstrap.sh | mkdir -p state tools/hw .task_scratch (the directories P1/P4 read); checks python3 curl awk df grep as 'requi… | higgsfield_api |
| tools/bootstrap.sh | same directory creation and prerequisite-binary check | suno_audio |
| tools/bootstrap.sh | same; creates state/ (which the P4 ledger init needs) and .task_scratch/ (which the step 3 raw-response save… | adobe_firefly |
| .gitignore | ignores state/ and .task_scratch/ (the runtime state these skills write); renders/ is NOT ignored | higgsfield_api |

**Open questions the files could not settle**

- Nothing in the repo writes .task_scratch/attestation.txt. Router.md §6 says the attestation is 'printed', yet every skill's P1 greps that file. What is supposed to write it?
- higgsfield_api never shows how HIGGSFIELD_API_KEY is sent: there is no auth header in ARTIFACT A or step 5. router.js also says higgsfield goes 'via MCP in production'. Which transport is intended?
- higgsfield_api leaves several things undefined: the download path for the generated video, the tool for final-frame extraction, the value of 'policy max' duration, and where model_id comes from.
- dashboard.json marks ph_01 (adobe_firefly) and ph_02 (suno_audio) complete. It also logs a higgsfield_api INTERCEPT / CONTEXT_LOADED / RENDER_SUBMITTED sequence on 2026-07-01 (job hf_a91x, seed 448811), with context_loaded naming gates that were unauthored at the time. No state/continuity_sm.json, state/style_ledger.json, renders/ or Content MD exists for these runs, and D6 calls the old values sample values. Are these events sample data?
- The skill flush points write to dashboard.json (suno flush №2 names no target at all), while Router.md §8 says flushes write to the Content MD. Until the D6 rewrite, what exactly should an agent persist at each flush?
- dashboard.json active_variables no longer contains any key these skills gate on or write (character_uuid, aspect_ratio, seed_lock, audio_bpm, audio_key, style_ref_id, master_palette). On a first run, with the only Content MD unrelated, where do V1/V2 get their values?
- suno_audio: where do cue_id, the 'cue spec' (make_instrumental) and project come from, given sound_identity is unauthored and the fixture choice depends on it?
- The Suno endpoints (studio-api.suno.ai /api/custom_generate, /api/get, /api/get_limit, /api/extend_audio; model chirp-v4) and the Firefly/IMS/Higgsfield endpoints appear only in the skill text. The repo has no evidence they were ever called or validated.
- No .env.example exists. The env var names (HIGGSFIELD_API_KEY, HIGGSFIELD_BASE_URL, SUNO_API_KEY, SUNO_BASE_URL, FIREFLY_CLIENT_ID, FIREFLY_CLIENT_SECRET) are documented only inside the skill files.
- Several labels are stale:
  - The skill subtitles say 'Skill 1/8', '2/8' and '3/8', while Router.md and the dashboard register 9 skills.
  - context/brand/README.md opens with 'Status: NOT YET AUTHORED', and README.md says 'The ten context/brand/ constants are still unauthored' and refers to 'the eight mandatory_context headers', although 3 gates are authored.
- adobe_firefly writes_dashboard_keys includes active_variables.style_ref_id_prev, and step 7 supersedes via _prev, a rule D6 removed. Should the canon-mint supersede history move to state/style_ledger.json 'supersedes' only?
- ARTIFACT A extend_clip (suno) and expand_image (firefly) are defined but never used in the numbered processes. When are they meant to run?
- The skill trigger_a lists contain phrases missing from the Router.md §2 Trigger A table: 'shot gen' and 'img2vid' (higgsfield), 'theme' and 'soundtrack' (suno), 'style frame' and 'key art' (firefly). Router §2 Trigger B also has no .png/.jpg → adobe_firefly mapping, although the skill's trigger_b lists it. Which copy is authoritative?
- In adobe_firefly ARTIFACT B, RX_STYLE_REF_LEDGER_ID pairs mode 'findall' with 'capture: 0' on a pattern that has two groups. The file does not say how the whole-match capture is obtained in findall mode.
- D6 defers the rewrite until brush_designer exists as the reference implementation, but skills/brush_designer.skill.md is not on disk (D2 marks it 'Not yet done'). Is there a timeline?

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: tools/verify_system.py (run in CI) only lints their headers: mandatory_context, host_kinds, no macOS-only binaries
  - evidence: tools/verify_system.py also runs check_skill_registry (on disk + registered), check_brand_gates (gates_skills name registered skills), check_router_js (roles present in router.js) and check_pipeline (ph_01-ph_03 route to registered skills with coherent progress). The macOS-binary / /Applications/ scan reads fenced code (fenced()), not headers.
- **corrected**: router.js dispatchAPICall: only 'higgsfield' has a registered base URL; stub returns {stub:true, would_call}
  - evidence: router.js lines 320-333: the registry also holds deepseek (http://localhost:11434/api/generate) and agent (http://localhost:8787); the return value is {ok:true, stub:true, would_call}. Grep shows dispatchAPICall and writeDashboard are never called; the only call sites are commented TODOs (lines 289, 339). Its comment lists 'suno' and 'firefly' as intended services.
- **corrected**: Their flush points still say to write to dashboard.json
  - evidence: skills/suno_audio.skill.md step 11 (CONTEXT FLUSH №2) only reduces working memory and names no write target. adobe_firefly flush №1 writes state/style_ledger.json as well as the dashboard.
- **corrected**: adobe_firefly P3 entry point = TOKEN=$(curl ... | python3 ...) only
  - evidence: skills/adobe_firefly.skill.md line 50 adds the check line: [ -n "$TOKEN" ] && echo "OK:P3" || echo "FAIL:P3 token mint failed"
- **corrected**: Unlike higgsfield_api, suno_audio does not state 'any failure → blocked/HALT' (implied to be unique to suno)
  - evidence: skills/adobe_firefly.skill.md §1 (lines 37-59) also lacks that line. Only higgsfield_api line 40 has it.
- **corrected**: higgsfield_api invoked_by Trigger B: 'a dashboard phase awaiting_render/queued/blocked in this domain'
  - evidence: Router.md line 126 lists awaiting_render, compositing, queued, or blocked.
- **corrected**: D6 defers rewriting these skills until one skill (brush_designer, as the reference) has been run end to end
  - evidence: DECISIONS.md lines 221-224 say that rewriting 'before one skill has been run end to end would be guessing', and 'brush_designer should be written first as the reference implementation'. skills/brush_designer.skill.md does not exist (Glob of skills/ lists 9 files without it; D2 says 'Not yet done').
- **corrected**: GAP-ANALYSIS.md rates suno_audio 'one authored file away' (sound_identity) from routing
  - evidence: The file is vault/_migration/GAP-ANALYSIS.md, lines 207-219. The statement is conditional on 'a complete, perfect migration' of the prose corpus serving brand_voice. The same table predates the gate authoring (it shows adobe_firefly still blocked by both gates).
- **corrected**: higgsfield_api: dashboard.json event_log shows ph_03 PARKED at L3 (implying current state)
  - evidence: dashboard.json event_log: PARKED 2026-08-23 names motion_language, narrative_continuity and visual_identity. GATE_AUTHORED 2026-08-31 promoted visual_identity (with color_science and typography_system) to L0, so only motion_language and narrative_continuity remain unresolved.
- **added**: (implicit) dashboard active_variables keys read by V1/V2/steps exist, only stale
  - evidence: dashboard.json lines 172-177: active_variables holds only _note, content_md, resolved_context and provisional_constraints. character_uuid, aspect_ratio, seed_lock, audio_bpm, audio_key, style_ref_id and master_palette are all absent.
- **added**: Router Trigger B coverage for adobe_firefly and trigger_a phrase parity
  - evidence: Router.md line 125: the file-type list has no .png/.jpg mapping, although adobe_firefly trigger_b lists '.png reference' and '.jpg reference'. The Router §2 Trigger A rows (lines 111-113) omit 'shot gen', 'img2vid', 'theme', 'soundtrack', 'style frame' and 'key art', which appear in the skill headers.
- **added**: suno_audio / higgsfield_api park because the vault holds only 1 Content MD (<3 for L2)
  - evidence: vault/studio-os/ui/ui-ux-intelligence-integration.md is the only note outside _-prefixed dirs. Its frontmatter context_brand is [visual_identity, typography_system, color_science], so L1 recall cannot resolve motion_language, narrative_continuity, sound_identity or brand_voice either.
- **added**: tools/bootstrap.sh creates the directories only for higgsfield_api
  - evidence: tools/bootstrap.sh line 140 'mkdir -p state tools/hw .task_scratch' serves all three skills. Line 70 checks python3 curl awk df grep as 'required by every skill's prerequisite block'.
- **added**: state/ and .task_scratch/ are gitignored
  - evidence: .gitignore lines 17-18 confirm this. renders/ (renders/audio, renders/stills) is not ignored. state/ exists on disk holding rag_index/ and vault_manifest.json but none of the skill state files.
- **added**: adobe_firefly P4 may create/overwrite state/style_ledger.json
  - evidence: skills/adobe_firefly.skill.md lines 53-54: a malformed existing ledger fails json.load and is overwritten with {"refs":[]}. There is no mkdir, so it depends on state/ existing.
- **added**: vault Content MD cross-link to the generative skills
  - evidence: vault/studio-os/ui/ui-ux-intelligence-integration.md line 54-56, Next Steps: 'Author visual_identity §7 ... adobe_firefly and higgsfield_api load the gate at L0 and find the interface constraints real and the imagery constraints absent.'
- **corrected**: D6 addendum location
  - evidence: DECISIONS.md line 203: the '### D6 addendum' heading sits structurally under '## D7' (line 174), not under D6 (line 142).
- **corrected**: All P1-P5 command strings, env var names, endpoints, thresholds, artifact contents and routing headers for the three skills
  - evidence: Re-read skills/higgsfield_api.skill.md, skills/suno_audio.skill.md and skills/adobe_firefly.skill.md in full. Every quoted command, endpoint, env name and threshold matches. The two-line P3 (higgsfield, suno) and P4 (suno) commands are now shown with their original line break instead of '; '.
- **corrected**: README.md states nothing executes the protocol, 'no skill has a Content MD step wired in', router.js dispatch is still stubs
  - evidence: Confirmed at README.md lines 113-117. The only change is the added note that README.md lines 119 and 129 are stale ('ten ... still unauthored', 'eight mandatory_context headers').
