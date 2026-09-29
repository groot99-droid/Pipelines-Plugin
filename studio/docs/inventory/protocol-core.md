# Routing protocol and its checkers

Subsystem `protocol-core` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.9 · 19 entries · 27 corrections made to the first reading.

## Summary

protocol-core is the routing contract (Router.md v1.1) plus the files that copy it or render it. dashboard.json holds live state and the gate registry. router.js and control_room.html are a read-only browser view of that state with a stubbed routing layer. tools/verify_system.py checks that the copies of the contract are internally consistent, and .github/workflows/verify.yml runs it in CI. DECISIONS.md (D1-D10, plus a 'D6 addendum' placed inside D7 and a D9 addendum) records the decisions in force.

SPEC vs CODE. Router.md specifies:
- a dual-trigger intercept (Trigger A = request intent verbs and nouns; Trigger B = asset file types plus dashboard phase state), followed by an 8-step sequence: MODE, RESOLVE, LADDER, RECALL, VERIFY, STATE, EXECUTE, WRITEBACK;
- a §3 table mapping each of the 9 skills to mandatory brand contexts, plus 'also load if flagged' contexts;
- a §4 mode read (manual / supervised / autonomous) and a §5 ladder: L0 authored, L1 recalled, L2 derived (needs at least 3 notes), L3 unresolved, with a per-mode gate;
- a §6 attestation block printed before any tool call;
- §7 Content MD read/write, the §8 flush and §9 writeback rules;
- six mode-invariant hard refusals (§10).

No code implements the protocol. README says so directly: 'Router.md is a contract an agent reads and obeys; it is not code, and no code implements it'.

What router.js actually implements:
- a 5 s poll of dashboard.json that renders control_room.html (a header plus 6 panels);
- a hard-coded copy of the §3 mandatory column (resolveGates);
- routeSkill: an L0-only check triggered by a skill chip click. The result is only an in-memory log row, and the caller discards the return value.

Stubbed or absent in router.js: dispatchAPICall and writeDashboard (never called), the agent POST (TODO), L1/L2, the mode gate, both triggers, attestation, Content MD, the host_kinds and hardware gates, and the flagged column.

routeSkill fails closed for unauthored or unknown roles but fails open for an unknown skill file: resolveGates returns [] and the route reports ok:true.

verify_system.py has 13 check_* functions plus load_dashboard. It exits 0 when consistent and 1 on any FAIL or an unparseable dashboard. Its checks validate that names are valid roles and that files and flags agree. They do not compare the per-skill skill-to-context mapping across Router.md §3, router.js, the skill headers and dashboard gates_skills. Today all copies agree on the mandatory column, except that dashboard gates_skills includes one flagged-column pair: pipeline_ethics → local_rag_orchestration.

CI has one job with 10 steps. It runs verify_system twice (plain, then under EncodingWarning-as-error), plus test_gate, probe extraction and parse, an evaluate_gate dry run, node --check, a dashboard parse, encoding smoke tests and vault_rag unit asserts.

Current state per dashboard.json: mode autonomous; state DEGRADED; 3 of 10 gates authored (visual_identity, typography_system, color_science); 1 counted vault Content MD.

By §3 and router.js logic, TWO skills have every mandatory gate authored: ui_ux_intelligence and adobe_firefly (visual_identity + color_science). D9 and dashboard blocked_reason name only ui_ux_intelligence.

Code outside this subsystem does write dashboard.json:
- tools/reconcile_models.py --write updates hardware.local_llm.tiers[*].model and _tiers_note;
- tools/vault_rag.py ask --write-dashboard updates hardware.local_llm.context_used_pct and loaded_tier.

Nothing in code writes pipeline phases, event_log or system_status.

Stale docs:
- README says ten gates are unauthored and the state is BLOCKED; says eight headers; says 'Four tabs' but lists five.
- DECISIONS D8 says ten gates are unauthored; D2 says eight skills.

## Tools

### Studio Router protocol (Router.md v1.1)

`protocol` · status `specified-not-implemented`

Paths: `Router.md`

Execution contract that, when loaded into an agent's context, makes the agent act as the 'Studio Router' and run the intercept before touching any skill file, tool, API or local script. Prime Rule: 'NO SKILL EXECUTES WITHOUT ITS CONTEXT RESOLVED, ATTESTED, AND SOURCED.'

**Entry points**

- `No executable entry point. Header: 'Core File 1/4 · Load Priority: ABSOLUTE FIRST'; the agent loads it first on every task.`
  - does: Binds the agent to the §2 intercept. If neither trigger fires, the task routes to general_chat and no skill may execute.
  - changes: Nothing directly. The sequence it mandates writes dashboard.json (§9) and exactly one vault Content MD per routed task (§7).

**Inputs**

- user request text (Trigger A)
- file types of referenced or attached assets (Trigger B.1)
- dashboard.json system_status.mode and pipeline.phases[] (Trigger B.2, §4)
- context/brand/<name>.context.md (L0)
- vault Content MDs: frontmatter context_brand, kind, status and '## Decisions in Force' (L1/L2)
- current shell / host_kind (§1)

**Outputs**

- ROUTER INTERCEPT attestation block (§6)
- one Content MD, created with status: seed or updated (§7)
- dashboard.json phase status write plus an event_log entry per transition (§9)
- PARKED / PROVISIONAL / INTERCEPT_VIOLATION event_log entries carrying the context name and Content MD path
- route to general_chat when no trigger fires

**Reads**

- dashboard.json
- context/brand/*.context.md
- context/brand/README.md
- vault/**/*.md
- vault/_templates/content-md.md
- vault/SCHEMA.md
- skills/*.skill.md (opened at step 7)

**Writes**

- dashboard.json (pipeline.phases[].status, event_log, system_status.last_heartbeat)
- vault/<note>.md (the task's Content MD)

**Depends on**

- an agent that obeys the contract (§1: Claude Code desktop on Windows, Lenovo Yoga Book 9i)
- skills/*.skill.md (Four-Part Artifact Architecture)
- vault/SCHEMA.md and vault/_templates/content-md.md
- skills/hardware_compute.skill.md and a PASS token for compute-heavy work

**Gates and checkpoints**

- §2: engages if Trigger A OR Trigger B fires; if neither fires, no skill execution at all
- §2: any tool call, script run or generative payload before step 5 completes is an INTERCEPT_VIOLATION: abort, log it to event_log, restart the sequence
- §1: a skill whose host_kinds excludes the current host_kind is not routable; park per §5 rather than improvise a bridge
- §1: compute-heavy work goes through hardware_compute first; single-flight, one heavy job at a time
- §3: every mandatory context must resolve; context/domain/ never satisfies a mandatory slot; 'L0 means authored, not complete'
- §5: L3 parks in every mode, including autonomous
- §6: an attestation missing any required context is itself an intercept violation
- §10: hard refusals (mode-invariant)

**Invoked by**

- a Claude agent session with Router.md loaded

**Invokes**

- skills/<routed>.skill.md (step 7)
- skills/hardware_compute.skill.md (first, for compute-heavy routes)
- verify_compute.sh PASS token (§10 wording)

**Notes**

Sections:
- §0 binding directive
- §1 topology and execution surface
- §2 dual-trigger intercept
- §3 routing table
- §4 execution mode
- §5 ladder and mode gate
- §6 attestation
- §7 Content MD emission
- §8 context flush
- §9 writeback
- §10 hard refusals

§1 topology:
- /skills/ holds 9 files.
- /context/brand/ holds 10 gates: 3 authored, 7 pending.
- /context/domain/ holds 10 libraries; each has a routing glossary at '## 1' and categories at '## 2.A'…'## 2.J'.
- /agents/ holds 9 sub-executors; 9 files confirmed on disk.
- /tools/brush-designer/ is 'Not yet routed — see DECISIONS.md'.
- /tools/ui-ux-pro-max/ is vendored.
- /vault/ is 'THE SOURCE OF TRUTH'.
- /archive/ 'Indexes the vault. Never owns it.'

§1 shell table:
- Git Bash/MSYS reports 'windows'.
- WSL2 reports 'wsl'. There /proc/meminfo describes the WSL VM, localhost is the VM, and Windows apps cannot open WSL paths.
- Native Linux reports 'linux'. It has no Adobe bridge; adobe_suite_uxp declares host_kinds [windows, wsl], confirmed in the skill header.

§1 names tools/verify_system.py as the enforcer of host_kinds. That is a reference, not an invocation.

Discrepancies:
- Header v1.1 vs dashboard system_status.router_version '1.0'.
- §10 attributes the PASS token to verify_compute.sh. README and D8 say tools/hw/evaluate_gate.py mints it at state/compute_gate.json and that verify_compute.sh 'mutates nothing'.
- Step 7 lists three parts under 'Four-Part Architecture'. Skill files define four: Part 1 ROUTING HEADER, Part 2 PREREQUISITES & STATE VERIFICATION, Part 3 EXECUTION PROCESS, Part 4 EMBEDDED ARTIFACTS (skills/hardware_compute.skill.md). Step 7 omits the routing header, which is consumed during routing.

### Router §2 dual-trigger intercept and 8-step sequence

`protocol` · status `specified-not-implemented`

Paths: `Router.md`

Decides whether a task is routed and fixes the order of operations for a routed task.

**Entry points**

- `Every task passes through Trigger A and Trigger B; if either fires: [HALT] → 1 MODE → 2 RESOLVE → 3 LADDER → 4 RECALL → 5 VERIFY → 6 STATE → 7 EXECUTE → 8 WRITEBACK`
  - does: Selects the candidate skill(s) and enforces the pre-execution order
  - changes: Step 6 writes phase → in_progress to dashboard.json; step 8 writes the Content MD and then dashboard.json

**Inputs**

- request text
- asset file extensions
- dashboard.json pipeline.phases[] status

**Outputs**

- candidate skill set
- attestation (step 5)
- phase status writes
- INTERCEPT_VIOLATION log on out-of-order calls

**Reads**

- dashboard.json

**Writes**

- dashboard.json
- vault Content MD

**Depends on**

- §3 routing table
- §4 mode
- §5 ladder
- §6 attestation
- §7 Content MD
- §9 writeback

**Gates and checkpoints**

- Both triggers firing raises confidence; neither firing → general_chat, no skill execution
- Trigger B.2: a phase whose status is awaiting_render, compositing, queued or blocked and whose domain matches the task forces that phase's skill into the candidate set
- Step 3: park if any context hits L3
- Step 5 must finish before any tool call, script or generative payload (else INTERCEPT_VIOLATION: abort, log, restart)
- Step 6: confirm no phase conflict before writing in_progress

**Invoked by**

- Studio Router protocol

**Invokes**

- Router §3 routing table
- Router §4-5 mode + ladder + mode gate
- Router §7-8 Content MD emission
- Router §6 attestation block
- skills/*.skill.md
- Router §9 writeback

**Notes**

TRIGGER A (intent pattern → skill):
- 'generate video / motion / animate shot / camera move' + AI gen → higgsfield_api
- 'music / track / score / stem / drop / verse' → suno_audio
- 'generate image / concept art / style ref / firefly' → adobe_firefly
- 'photoshop / premiere / after effects / comp / batch edit' → adobe_suite_uxp
- '3D / blender / camera path / low-poly / procedural / rig' → blender_python
- 'UI / dashboard / component / landing page / DOM' → css_html_ui
- 'search my docs / recall / summarize corpus / RAG / local model' → local_rag_orchestration
- 'render locally / GPU / heavy compute / batch process / thermals / on battery' → hardware_compute
- 'design system / palette / font pairing / style direction / UX review / accessibility audit' → ui_ux_intelligence

TRIGGER B.1 (file type → skill):
- .mp4/.mov → higgsfield or adobe_suite
- .wav/.mp3/.stem → suno
- .psd/.aep/.prproj/.jsx → adobe_suite_uxp
- .blend/.fbx/.obj → blender_python
- .html/.css/.jsx(web) → css_html_ui
- .pdf/.md corpus → local_rag
- design-system/*/MASTER.md, tokens/design_tokens.json → ui_ux_intelligence

TRIGGER B.2: dashboard phase state, as in the gates.

STEPS:
1. MODE: read system_status.mode.
2. RESOLVE: map candidate skill → context via §3.
3. LADDER: resolve each context via §5, apply the mode gate, park on L3.
4. RECALL: locate or create the Content MD; read Overview, Next Steps, Decisions in Force and Method in full.
5. VERIFY: emit the attestation.
6. STATE: confirm no phase conflict; write in_progress.
7. EXECUTE: open .skill.md; Prerequisites → Execution Process → Embedded Artifacts.
8. WRITEBACK: Content MD (§7), then dashboard.json (§9).

With the current dashboard, B.2 would force (on domain match): higgsfield_api (ph_03 blocked), blender_python (ph_04 queued), adobe_suite_uxp (ph_05 compositing), css_html_ui (ph_06 queued).

CODE: neither trigger is implemented. router.js routeSkill starts only from a manual chip click.

### Router §3 routing table (skill → mandatory context)

`data` · status `partial`

Paths: `Router.md`, `dashboard.json`, `router.js`, `skills/*.skill.md`

Maps each of the 9 skills to the brand constants it must load before execution, plus contexts to also load 'if flagged in dashboard'.

**Entry points**

- `Looked up at intercept step 2 (RESOLVE); the mandatory column is mirrored in router.js resolveGates(skillFile)`
  - does: Returns the mandatory context names for a skill
  - changes: nothing

**Inputs**

- skill name

**Outputs**

- mandatory context roles, each resolving to context/brand/<name>.context.md at L0

**Reads**

- context/brand/<name>.context.md

**Gates and checkpoints**

- A name resolves only to context/brand/<name>.context.md; context/domain/ files never satisfy a mandatory slot
- 'L0 means authored, not complete': visual_identity §7 (imagery motifs) and color_science §5 (working space, LUTs, grading) are declared gaps; routes needing them treat those constraints as unresolved
- Multi-skill tasks: union all mandatory sets, load once, deduplicate

**Invoked by**

- Router §2 step 2
- router.js routeSkill → resolveGates

**Notes**

TABLE (skill: mandatory | also load if flagged):
- higgsfield_api: motion_language, narrative_continuity, visual_identity | color_science
- suno_audio: sound_identity, brand_voice | narrative_continuity
- adobe_firefly: visual_identity, color_science | typography_system
- adobe_suite_uxp: render_philosophy, color_science | visual_identity
- blender_python: render_philosophy, motion_language | visual_identity
- css_html_ui: typography_system, visual_identity, brand_voice | —
- local_rag_orchestration: memory_discipline | pipeline_ethics
- hardware_compute: pipeline_ethics, render_philosophy | —
- ui_ux_intelligence: visual_identity, typography_system, color_science | —

AUTHORED ON DISK: visual_identity, typography_system, color_science (context/brand/ also holds README.md).
UNAUTHORED: motion_language, sound_identity, brand_voice, narrative_continuity, render_philosophy, pipeline_ethics, memory_discipline.

FULLY-AUTHORED MANDATORY SETS: ui_ux_intelligence AND adobe_firefly. D9 and dashboard blocked_reason mention only ui_ux_intelligence.

COPIES:
- Router.md §3.
- router.js resolveGates, mandatory column only.
- The 9 skill headers' 'mandatory_context:' lines. All 9 match §3 (grep confirmed).
- dashboard.json registries.context_brand_gates[].gates_skills, an inverse map. It matches the mandatory column EXCEPT that pipeline_ethics also lists local_rag_orchestration, a flagged-column pairing. The other flagged pairings are absent (color_science→higgsfield, narrative_continuity→suno, typography_system→firefly, visual_identity→adobe_suite_uxp/blender).

verify_system.py does not compare these per-skill mappings with one another.

No dashboard field expresses 'flagged', so the right-hand column has no trigger anywhere.

### Router §4-5 execution mode, context resolution ladder (L0-L3) and mode gate

`protocol` · status `specified-not-implemented`

Paths: `Router.md`

Defines behaviour when a required constraint has no authored file. The ladder descends L0→L3 and stops at the first level that resolves; the mode then decides proceed, ask or park.

**Entry points**

- `Intercept steps 1 (MODE) and 3 (LADDER)`
  - does: Reads system_status.mode, resolves each context through the ladder, then applies the mode gate
  - changes: On park or provisional proceed: the Content MD ('## Next Steps' / '## Decisions in Force', status: blocked) and event_log (PARKED / PROVISIONAL)

**Inputs**

- system_status.mode ∈ {manual, supervised, autonomous} (current: autonomous)
- context/brand/<name>.context.md
- vault Content MDs with frontmatter context_brand, kind and status

**Outputs**

- per-context level, confidence and sources
- proceed / proceed-flag / proceed-provisionally / ask / park

**Reads**

- dashboard.json
- context/brand/*.context.md
- vault/**/*.md

**Writes**

- vault Content MD
- dashboard.json event_log

**Depends on**

- vault Content MDs as the precedent corpus

**Gates and checkpoints**

- L0 AUTHORED: file exists → load in full, confidence 1.0
- L1 RECALLED: a vault note whose frontmatter context_brand includes <name> has a '## Decisions in Force' entry directly stating the constraint → confidence 0.9, cite the note id
- L2 DERIVED: inferred from precedent across Content MDs of related kind, weighting status: complete over in-progress and recent over old → confidence 0.3-0.8, cite every note. Needs at least 3 notes
- L3 UNRESOLVED: nothing to ground on → no confidence
- Mode gate L0/L1: proceed in all modes
- Mode gate L2 ≥0.70: manual ask; supervised proceed+flag; autonomous proceed+flag
- Mode gate L2 <0.70: manual ask; supervised ask; autonomous proceed provisionally, flag hard
- Mode gate L3: manual ask; supervised ask; autonomous park
- Provisional: execute and record the derived constraint with its confidence and sources in '## Decisions in Force'
- Park: do not execute; write the gap as the first '## Next Steps' item; set status: blocked; log PARKED; route the next task; do not ask, wait or guess

**Invoked by**

- Router §2 steps 1 and 3

**Invokes**

- Router §7-8 Content MD emission
- Router §9 writeback

**Notes**

§4 modes:
- manual: stop and ask.
- supervised: ask on low confidence; proceed flagged on high confidence.
- autonomous: never wait; proceed on anything derivable, or park with a written reason and move on.

The modes differ only in how they handle unresolved constraints. Introduced by D7.

CODE: none. router.js reports L0 only (comment: 'needs vault access this page does not have'), and routeSkill ignores the mode. No code computes L1/L2 confidence.

Current state: 1 counted Content MD (vault/studio-os/ui/ui-ux-intelligence-integration.md), which is fewer than 3, so routes needing the 7 unauthored gates park at L3 (dashboard blocked_reason).

verify_system.check_context_loaded counts *.md under vault/. It excludes any path part starting with '_' and files named README.md or SCHEMA.md.

### Router §6 Context Attestation Block

`protocol` · status `specified-not-implemented`

Paths: `Router.md`

Required printed readout, before the first tool call of a routed task, showing that every mandatory context was resolved and sourced.

**Entry points**

- `Printed by the agent at intercept step 5 (VERIFY)`
  - does: Emits the ROUTER INTERCEPT box
  - changes: nothing

**Inputs**

- mode
- trigger results
- route
- ladder results
- Content MD path

**Outputs**

- Box with fields: MODE; TRIGGER A <fired/none> → <pattern>; TRIGGER B <fired/none> → <asset or vault state>; ROUTE <skill file>; CONTEXT RESOLUTION (one line per context: name, L0 AUTHORED / L1 RECALLED / L2 DERIVED, confidence, source path or [[note ids]], '⚠ PROVISIONAL' on L2); KEY CONSTRAINTS EXTRACTED (one line per resolved context); CONTENT MD <path> → <created|updating>

**Depends on**

- Router §4-5 ladder output

**Gates and checkpoints**

- Every §3 context for the routed skill appears with level, confidence and source
- L2 lines carry ⚠
- A missing required context is itself an intercept violation

**Invoked by**

- Router §2 step 5

**Notes**

CODE: nothing emits this block.

router.js's renderContext comment calls the Brand Gates panel the attestation readout and cites 'Router.md §4'; the attestation is actually §6. The panel's section aria-label is 'Context attestation'. It shows per-gate authored and loaded state only: no levels, confidence, sources or triggers.

### Router §7-8 Content MD emission and context flush

`protocol` · status `specified-not-implemented`

Paths: `Router.md`

Every routed task reads and writes exactly one vault Content MD, which is the persistent memory and 'how the next session exists'.

**Entry points**

- `Intercept step 4 (RECALL) at start; step 8 (WRITEBACK) at end; flush points defined inside skill files ('⟪ CONTEXT FLUSH №1/№2 ⟫')`
  - does: Loads the note as binding context, then revises it with what was actually done
  - changes: vault/<note>.md

**Inputs**

- vault/_templates/content-md.md
- the existing Content MD for the thing being worked on

**Outputs**

- new Content MD (status: seed) or updated Content MD

**Reads**

- vault/**/*.md
- vault/_templates/content-md.md
- vault/SCHEMA.md

**Writes**

- vault/<note>.md

**Depends on**

- vault/SCHEMA.md

**Gates and checkpoints**

- Start: read '## Overview', '## Next Steps', '## Decisions in Force' and '## Method' in full. A decision in force binds exactly as a brand constant does
- End: (1) append one '## Timeline' entry, never a step not taken; (2) rewrite '## Next Steps' in full; (3) add '## Decisions in Force', marking derived ones; (4) move answered '## Open Questions' into Decisions in Force and delete them; (5) record '## Contradictions', naming each file; (6) update '## Method' if parameters changed; (7) bump 'updated' and set 'status'
- §8 flush: (1) persist to the Content MD; (2) discard raw payloads; (3) keep only the attestation constraints and the Content MD path. If the note would lose something, fix the note first

**Invoked by**

- Router §2 steps 4 and 8
- Router §4-5 park / provisional

**Notes**

State lives in the Content MD, not in the conversation or the dashboard. dashboard.json is disposable run state (§8, D6).

CODE: no tool in this subsystem creates or updates Content MDs. README: 'no skill has a Content MD step wired in'.

Vault .md files on disk:
- vault/studio-os/ui/ui-ux-intelligence-integration.md (the only counted one);
- vault/README.md and vault/SCHEMA.md (excluded by name);
- vault/_examples/example-stipple-brush.md, vault/_migration/GAP-ANALYSIS.md and vault/_templates/content-md.md (excluded by '_' prefix).

### Router §9 writeback rules

`protocol` · status `specified-not-implemented`

Paths: `Router.md`

How the router records state changes in dashboard.json and Content MDs.

**Entry points**

- `On every phase transition and writeback (intercept steps 6 and 8)`
  - does: Writes dashboard.json and appends to event_log
  - changes: dashboard.json, vault Content MD

**Inputs**

- phase transition
- park / provisional / violation events

**Outputs**

- event_log entry {ts, actor:'router', event, detail}
- system_status.last_heartbeat update

**Writes**

- dashboard.json
- vault/<note>.md

**Gates and checkpoints**

- Each phase transition = one dashboard.json write + one event_log entry
- Content MD writes are append-and-revise, never destructive; '## Timeline' is append-only, and corrections are made by a new dated entry
- system_status.last_heartbeat updates on every writeback
- PARKED, PROVISIONAL and INTERCEPT_VIOLATION are logged with the context name and Content MD path

**Invoked by**

- Router §2 steps 6 and 8

**Notes**

CODE: router.js writeDashboard(patch) is a console.info stub and is never called (grep confirms only its definition and a TODO). The comment reads 'the headless agent owns dashboard.json'.

Event names in dashboard.json event_log: TOKENS_COMMITTED, GATE_AUTHORED, SKILL_REGISTERED, PARKED, HEARTBEAT, RENDER_SUBMITTED, CONTEXT_LOADED, INTERCEPT, COMP_STARTED. No enum is defined.

The log departs from §9 in two ways:
- Actors include ui_ux_intelligence, higgsfield_api and adobe_suite_uxp, not only 'router'.
- system_status.last_heartbeat is still 2026-08-23T18:30:00Z although three entries dated 2026-08-31 were added after it.

verify_system.check_event_log enforces only newest-first order and the four keys.

### Router §10 hard refusals

`protocol` · status `specified-not-implemented`

Paths: `Router.md`

Refusals that hold in every mode; autonomy relaxes only §5's gate.

**Entry points**

- `Applied throughout routing, in every mode`
  - does: Blocks the listed actions
  - changes: nothing

**Depends on**

- skills/
- hardware_compute
- PASS token

**Gates and checkpoints**

- Refuse to execute a skill absent from /skills/
- Refuse to present a derived constraint as authored (L2 is always marked provisional with confidence and sources)
- Refuse to execute at L3 in any mode
- Refuse to record a Timeline step that was not taken
- Refuse to skip hardware verification when hardware_compute is in the route chain
- Refuse to run compute-heavy work without a fresh PASS token from verify_compute.sh

**Invoked by**

- Studio Router protocol

**Invokes**

- skills/hardware_compute.skill.md
- tools/hw/verify_compute.sh (generated; per README the token is minted by tools/hw/evaluate_gate.py)

**Notes**

Partial enforcement in code:
- verify_system.check_skill_registry FAILs if a registered skill is missing on disk. Its message cites 'Router §7 refusal'; the refusal is §10.
- router.js routeSkill parks for unauthored or unknown roles, at L0 only. It does NOT refuse an unknown skill file: resolveGates returns [] and routeSkill returns ok:true.

evaluate_gate.py docstring: exit 0 = PASS (token minted unless --dry-run), 1 = DENY, 2 = could not evaluate.

### dashboard.json (live system state, schema 2.0.0)

`data` · status `runs-today`

Paths: `dashboard.json`

Live run state and gate registry: mode, system state, hardware, pipeline phases, run-scoped variables, skill and context registries, event log.

**Entry points**

- `GET dashboard.json?t=<Date.now()> with cache: 'no-store', every 5000 ms (router.js fetchDashboard)`
  - does: Supplies all control_room.html content
  - changes: nothing
- `python3 tools/verify_system.py`
  - does: Loads and cross-checks it
  - changes: nothing

**Inputs**

- writes by the agent acting as router (§9, spec)
- tools/reconcile_models.py --write (hardware.local_llm.tiers[*].model, _tiers_note)
- tools/vault_rag.py ask --write-dashboard (hardware.local_llm.context_used_pct, loaded_tier)

**Outputs**

- state consumed by router.js, verify_system.py, bootstrap.sh, reconcile_models.py, vault_rag.py and the Router protocol

**Gates and checkpoints**

- system_status.mode is read at the start of every routed task (§4)
- pipeline.phases[] with status awaiting_render / compositing / queued / blocked drive Trigger B.2
- registries.context_brand_gates[].authored must equal file existence (check_brand_gates)
- event_log must be newest-first with ts, actor, event and detail (check_event_log)
- complete ⇒ progress_pct 100; queued ⇒ 0 (check_pipeline)
- hardware.gpu.cuda false ⇒ no skill may set cycles.device = "GPU" (check_host_portability)

**Invoked by**

- router.js fetchDashboard
- tools/verify_system.py
- Studio Router protocol
- tools/reconcile_models.py
- tools/vault_rag.py
- tools/bootstrap.sh (reads local_llm.endpoint)

**Notes**

meta: schema_version 2.0.0, system_name 'STUDIO HEADLESS OS', operator 'Studio Lead', generated 2026-07-01, file_count_target 23. Nothing checks file_count_target.

system_status:
- state DEGRADED (state_enum NOMINAL / DEGRADED / BLOCKED / OFFLINE)
- mode autonomous (mode_enum autonomous / supervised / manual)
- last_heartbeat 2026-08-23T18:30:00Z
- router_version '1.0'
- intercept_violations_24h 0
- active_skill null
- context_loaded []
- blocked_reason

hardware:
- host: Lenovo Yoga Book 9i, Windows 11, host_kind windows, enum [windows, wsl, linux]
- memory: memory_gb 16, soldered; memory_pressure green; memory_available_gb null
- gpu: integrated Intel, cuda false, vram_gb null by design
- power.source null; thermal readings null
- local_llm: endpoint http://localhost:11434; loaded_tier null; context_used_pct 0; embed_model nomic-embed-text
- tiers (PROVISIONAL note): sm = llama3.1:8b Q4_K_M 8192 ctx; md = mistral-nemo:12b Q4_K_M 4096 ctx
- workload_classes: llm_local_sm, llm_local_md, render_3d_cpu, batch_2d; single_flight true

pipeline: PROJECT_AURORA, current_phase_id ph_03.
- ph_01 adobe_firefly: complete 100
- ph_02 suno_audio: complete 100
- ph_03 higgsfield_api: blocked 62
- ph_04 blender_python: queued 0
- ph_05 adobe_suite_uxp: compositing 18
- ph_06 css_html_ui: queued 0
- status_enum (7 values)

active_variables (run-scoped per D6): content_md, resolved_context, provisional_constraints.

registries:
- 9 skills, all 'ready';
- 10 context_brand_gates, 3 authored;
- 10 context_domain_libraries, all 10 present on disk.

event_log: 9 entries, newest 2026-08-31T16:45:00Z.

verify_system does NOT check state, mode or host_kind against their own enums.

### router.js poll and render layer (Logic Bridge, 'Core File 4/4')

`library` · status `runs-today`

Paths: `router.js`

Fetches dashboard.json on load and on an interval, and renders every control_room.html region from that single state object.

**Entry points**

- `<script src="router.js"></script> in control_room.html; on load runs fetchDashboard() then startPolling()`
  - does: Polls every CONFIG.POLL_MS = 5000 ms. On visibilitychange: hidden stops polling; visible fetches immediately and restarts polling
  - changes: DOM only; toggles body class 'offline'; console messages
- `node --check router.js (CI)`
  - does: Syntax check
  - changes: nothing

**Inputs**

- dashboard.json over HTTP (CONFIG.DASHBOARD_URL = 'dashboard.json')

**Outputs**

- DOM content for ids sys-state, sys-mode, sys-skill, sys-project, heartbeat, lamp, rail, phase-count, vars, hw-host, hw-meters, hw-facts, log, skills, skill-count, ctx-violations, ctx-list

**Reads**

- dashboard.json

**Depends on**

- browser fetch API
- an HTTP origin (the offline note suggests python3 -m http.server when opened via file://)

**Gates and checkpoints**

- On fetch failure: add body.offline and re-render the last good STATE if one exists (nothing renders if the first fetch fails)
- esc() HTML-escapes dashboard strings (null/undefined → '—'); master_palette swatches only accept /^#[0-9a-fA-F]{3,8}$/ as a style value

**Invoked by**

- control_room.html

**Invokes**

- dashboard.json (GET)
- routeSkill (skill chip click)

**Notes**

Render functions:
- renderHeader: state, mode, active_skill or 'idle', project, heartbeat time. The lamp gets 'warn' on DEGRADED and 'alert' on BLOCKED/OFFLINE.
- renderPipeline: a station per phase with class s-<status>, label, skill, status word, bar; 'N/M complete'. statusColor maps complete / in_progress / compositing → c-cyan, awaiting_render / review → c-amber, blocked → c-alert, queued → c-queued, else c-dim.
- renderVariables: skips keys ending in _prev; master_palette is drawn as swatches; arrays are joined or shown as '—'; null shows '—'. Note: the '_note' key is rendered as a row ('_note' → ' note').
- renderHardware meters: Memory (measured if memory_available_gb is a number, else memory_pressure projected green 30 / yellow 65 / red 90, labelled '(unprobed)'); CPU throttling (100 - cpu_perf_pct, or 100 with 'unreadable — gate closed'); LLM context window (context_used_pct of the loaded tier's context_window_tokens, falling back to local_llm.context_window_tokens, then 0).
- renderHardware facts: Host, Graphics, Power, Thermal, Memory, Local model, Endpoint, plus 'Legacy compute node' if compute_node or egpu is present.
- renderLog: merges LOCAL_EVENTS with event_log, sorts by ts descending, caps at LOG_LIMIT 40; names containing VIOLATION, ERROR or FAIL render c-alert.
- renderSkills: a button chip per registry skill, with data-status set from s.status; a click calls routeSkill(file).
- renderContext: 'N of M unresolved at L0' if any gate is unauthored; otherwise the violation count or 'all gates authored (L0) · 0 violations / 24h'. Row class is 'on' if authored and in context_loaded, '' if authored but not loaded, 'missing' if unauthored ('not authored — §5 ladder, L3 parks').

With the current dashboard:
- lamp amber (warn);
- '2/6 complete';
- '7 of 10 unresolved at L0', with the 3 authored rows neutral because context_loaded is empty;
- Memory 30% 'green · 16 GB total (unprobed)';
- CPU throttling 100% 'unreadable — gate closed';
- LLM context window '0% of 0k tokens';
- Power 'unreadable', Thermal 'no readable sensor', Local model 'none resident'.

The layer never writes.

### router.js routing layer (routeSkill / resolveGates / brandPath / isAuthoredL0 / dispatchAPICall / writeDashboard / logLocal)

`library` · status `stub`

Paths: `router.js`

Placeholder 'seam where the headless agent / local services attach': a UI-initiated route that mirrors resolve context → verify → dispatch.

**Entry points**

- `Click a skill chip → routeSkill('skills/<name>.skill.md')`
  - does: Gets the gates from resolveGates and checks each with isAuthoredL0 (STATE.registries.context_brand_gates, role match and authored === true). If any gate fails: logLocal PARKED and return {ok:false, parked:true, unresolvedAtL0:[paths]}. Otherwise: logLocal INTERCEPT '(stub)' and return {ok:true, skill, gates, paths}. The click handler discards the return value.
  - changes: In-memory LOCAL_EVENTS (capped at 40) and the rendered log; console. Nothing persisted.
- `dispatchAPICall(service, endpoint, payload)`
  - does: Stub. Registry: higgsfield → https://platform.higgsfield.ai, deepseek → http://localhost:11434/api/generate, agent → http://localhost:8787. Returns {ok:true, stub:true, would_call} or {ok:false, error:'unregistered service: …'}. No fetch. Referenced only in TODO comments; never called.
  - changes: nothing
- `writeDashboard(patch)`
  - does: Stub: console.info only. Never called.
  - changes: nothing

**Inputs**

- skill file path from the chip
- STATE (last fetched dashboard.json)

**Outputs**

- return objects (ignored by the caller)
- console messages
- local PARKED / INTERCEPT log rows with actor 'control_room'

**Reads**

- dashboard.json (via STATE)

**Depends on**

- router.js poll and render layer

**Gates and checkpoints**

- Unknown role, or authored !== true → parked (fails closed)
- Unknown skill file → resolveGates returns [] → no unresolved gates → ok:true (fails OPEN)
- Never builds a context/domain/ path (checked by verify_system on comment-stripped code)
- L0 only; L1/L2 are deferred to the agent

**Invoked by**

- router.js renderSkills chip click handler

**Invokes**

- resolveGates
- isAuthoredL0
- logLocal

**Notes**

IMPLEMENTED:
- resolveGates: identical to §3's mandatory column for all 9 skills.
- brandPath(role) → 'context/brand/<role>.context.md'.
- isAuthoredL0: reads dashboard state rather than a second list.
- logLocal.

STUB OR ABSENT:
- the agent POST ('TODO: POST to local agent runner', e.g. '/route') and the '/dashboard/patch' writeback;
- auth headers ('TODO(agent)');
- services listed in the comment but missing from the registry: suno, firefly, adobe_uxp, blender;
- the mode gate, L1/L2, both triggers, attestation, Content MD, host_kinds and hardware gates;
- the flagged column;
- the declared-gap nuance of partial L0 gates.

With the current dashboard, the ui_ux_intelligence AND adobe_firefly chips return ok:true. The other 7 park.

### control_room.html (Control Room UI)

`web-app` · status `runs-today`

Paths: `control_room.html`

Human-facing live view of dashboard.json; README: 'it does not drive anything yet'.

**Entry points**

- `python3 -m http.server 8347 (.claude/launch.json 'hub-static-server'), then open control_room.html on that origin, e.g. http://localhost:8347/control_room.html`
  - does: Serves the page over HTTP so router.js can fetch dashboard.json. The control_room URL is inferred: README gives only http://localhost:<port>/hub/, and launch.json declares no cwd.
  - changes: nothing
- `python3 -m http.server (the offline note's suggestion for file:// use)`
  - does: Any static server
  - changes: nothing

**Inputs**

- dashboard.json via router.js

**Outputs**

- rendered page: a header plus 6 panels

**Reads**

- router.js
- dashboard.json (via router.js)
- https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;800

**Depends on**

- router.js
- Google Fonts (fonts.googleapis.com, fonts.gstatic.com preconnect)
- a static HTTP server

**Gates and checkpoints**

- :root tokens must mirror css_html_ui ARTIFACT A (check_palette_parity: --bg, --bg-raise, --bg-panel, --amber, --cyan, --alert, --queued)
- Every c-* class and $("id") router.js uses must exist here (check_router_js)
- body.offline shows the amber note: 'dashboard.json unreachable — showing last known state. If opened via file://, run a local server'

**Invoked by**

- operator's browser

**Invokes**

- router.js

**Notes**

REGIONS:
- header (hd): brand 'STUDIO//HEADLESS'; System (lamp + #sys-state); Mode #sys-mode; Active skill #sys-skill; Project #sys-project; #heartbeat.
- Pipeline Rail (pl): #rail (tabindex 0, role group, horizontal scroll), #phase-count, and the offline note.
- Active Variables (vr): #vars, tick 'continuity locks'.
- Compute (hw): #hw-host in the tick, #hw-meters, #hw-facts.
- Event Log (lg): #log (tabindex 0, role region), spans 3 grid rows on desktop, tick 'router writeback'.
- Skill Registry (sk): #skills, #skill-count. Chip dot is cyan by default, amber for data-status busy, alert for error.
- Brand Gates (cx): section aria-label 'Context attestation'; #ctx-violations; #ctx-list rows (dot + path + gated skills or 'not authored').

TOKENS (HARD MONO, D10): bg #000000, bg-raise #0B0B0B, bg-panel #141414, line #383838, ink #FFFFFF, ink-dim #9E9E9E (commented 6.88:1 on panel), amber #FFC400, cyan #00E5FF, alert #FF3B30, queued #8A8AFF. Zero radius; JetBrains Mono only.

Layout: breakpoints at 980px and 640px; a global :focus-visible ring; prefers-reduced-motion turns off the lamp blink and bar transitions.

The only interaction is skill chip clicks, which call the stubbed routeSkill.

### tools/verify_system.py (protocol integrity checker)

`cli` · status `runs-today`

Paths: `tools/verify_system.py`

Checks structural consistency between the protocol files: registry vs disk, gate flags vs disk, roles named in headers, Router.md and router.js, UI ids, classes and tokens, pipeline coherence, host portability and the extracted probe. It does not compare per-skill skill→context mappings across the copies.

**Entry points**

- `python3 tools/verify_system.py`
  - does: Runs every check; prints PASS / WARN / FAIL lines (ANSI coloured) and 'N passed · N warnings · N failures'
  - changes: nothing
- `python3 tools/verify_system.py --quiet`
  - does: Exit code only ('--quiet' in sys.argv; no argparse). The dashboard-parse FAIL line still prints
  - changes: nothing
- `PYTHONWARNDEFAULTENCODING=1 python3 -W error::EncodingWarning tools/verify_system.py --quiet`
  - does: CI variant; implicit-encoding file access becomes fatal
  - changes: nothing

**Inputs**

- repository files (ROOT = parent of tools/)
- argv '--quiet'

**Outputs**

- stdout report
- exit 0 = consistent; 1 = at least one FAIL or dashboard.json unparseable. A missing dashboard key raises an uncaught KeyError (traceback) rather than a FAIL

**Reads**

- dashboard.json
- Router.md
- router.js
- control_room.html
- skills/*.skill.md
- skills/css_html_ui.skill.md (ARTIFACT A tokens)
- skills/hardware_compute.skill.md (ARTIFACT A bash, only if the extracted probe exists)
- context/brand/<role>.context.md (existence)
- context/domain/*_context.md (glob and declared paths)
- vault/**/*.md (count)
- tools/hw/verify_compute.sh (if present)

**Depends on**

- Python 3 stdlib only: json, re, sys, pathlib
- module-level list[str] annotations imply Python 3.9+ (inferred); CI uses 3.11

**Gates and checkpoints**

- Exit 1 on any FAIL; WARNs do not fail
- An unparseable dashboard.json short-circuits with exit 1
- Used as a CI gate twice (verify.yml)

**Invoked by**

- developer after editing a protocol file (README, BOOT.md, docstring)
- .github/workflows/verify.yml steps 'Protocol integrity' and 'Tools declare their encodings'
- tools/bootstrap.sh (prints it as a next step)
- tools/reconcile_models.py --write (prompts a re-run)

**Notes**

CHECKS, in main() order:
- load_dashboard: dashboard.json must parse.
- check_protocol_files: Router.md, dashboard.json, control_room.html and router.js exist. Skills and domain-library counts are reported only.
- check_skill_registry: every registries.skills file exists (FAIL message cites 'Router §7 refusal'), and every on-disk skill is registered. The OK line appears only if FAILS is globally empty.
- check_brand_gates: no duplicate roles; path == context/brand/<role>.context.md; authored == file exists; gates_skills entries are registered. Returns the role set.
- check_domain_libraries: declared libraries exist (FAIL); undeclared on-disk libraries WARN; gate paths must not overlap libraries (FAIL).
- check_skill_headers: each skill has '^mandatory_context: [..]' whose roles are all gate roles (FAIL text says 'not one of the ten brand gates').
- check_host_portability: host_kind_enum must be non-empty (otherwise FAIL and return early). Each skill needs '^host_kinds: [..]' within the enum. In fenced code only: no command-position osascript, vm_stat, sysctl, afplay or pbcopy; no '/Applications/'; and if gpu.cuda is False, no '(scn|scene).cycles.device = "GPU"'.
- check_extracted_probe: only if tools/hw/verify_compute.sh exists; it must equal the ARTIFACT A bash block after strip().
- check_router_md: each role appears in backticks (WARN). The whitespace-flattened text must contain '/skills/', '/context/' and 'context/brand/<name>.context.md' (FAIL).
- check_router_js: must contain 'STATE?.registries?.context_brand_gates'. Comment-stripped code must contain 'context/brand/' and not 'context/domain/'. Each role must appear somewhere (WARN). Each "c-xxx" string needs '.c-xxx' in control_room.html. Each $("id") needs id="id".
- check_palette_parity: ARTIFACT A bg {base, raise, panel} and accent {amber, cyan, alert, queued} (6-digit hex) vs control_room.html --bg, --bg-raise, --bg-panel, --amber, --cyan, --alert, --queued. WARN if nothing parses.
- check_pipeline: unique ids; current_phase_id exists; skills registered; status in status_enum; 0 ≤ pct ≤ 100; complete ⇒ 100; queued ⇒ 0.
- check_context_loaded: context_loaded roles must be gates and authored. State must be BLOCKED only when there are unauthored gates AND 0 counted vault notes. With 1 note, as now, no state assertion is made.
- check_event_log: newest-first; ts, actor, event and detail present. Entries are indexed by e['ts'] first, so a missing ts crashes the script.

PASS lines are emitted unconditionally in most checks even when that check also FAILed. The exceptions are check_skill_registry, check_skill_headers, check_extracted_probe, check_palette_parity and the first check_router_js line.

NOT CHECKED:
- that the per-skill mapping in Router §3, router.js resolveGates, the skill headers and dashboard gates_skills agree;
- the flagged column;
- state, mode and host_kind vs their enums;
- meta.file_count_target;
- the VENDOR.md hash (D9 proposes check_vendor_hash).

Stale text:
- The docstring says 'eight skill headers' and '(§7)' halts.
- check_protocol_files' docstring says '22 protocol files'.
- check_brand_gates' docstring says the gates are 'not yet authored'.
- The check_router_md comment describes discounting a 'denying' sentence that the code does not do.

Recorded runs: D8 says 8 failures on pre-port files; D9 addendum and D10 record exit 0. Not executed for this inventory.

### .github/workflows/verify.yml (CI workflow 'verify')

`ci` · status `runs-today`

Paths: `.github/workflows/verify.yml`

Runs the protocol checks and tool smoke tests on GitHub Actions so they do not depend on local runs.

**Entry points**

- `on: push (branches: [main]) | pull_request | workflow_dispatch`
  - does: Triggers job 'verify' on ubuntu-latest
  - changes: runner workspace only
- `uses: actions/checkout@v4`
  - does: step 1
  - changes: runner workspace
- `uses: actions/setup-python@v5 with python-version: "3.11"`
  - does: step 2
  - changes: runner
- `python3 tools/verify_system.py`
  - does: step 'Protocol integrity'. verify_compute.sh is gitignored and not yet extracted here, so check_extracted_probe is a no-op
  - changes: nothing
- `python3 tools/hw/test_gate.py`
  - does: step 'Gate logic'
  - changes: not determined from this file
- `mkdir -p tools/hw; python3 - skills/hardware_compute.skill.md > tools/hw/verify_compute.sh <<'PY' … PY; bash -n tools/hw/verify_compute.sh; chmod +x tools/hw/verify_compute.sh; ./tools/hw/verify_compute.sh generic > /tmp/probe.json; python3 -c "import json;json.load(open('/tmp/probe.json'))"; echo "probe emitted valid JSON on $(uname -s)"`
  - does: step 'Probe extracts and parses': extracts ARTIFACT A with regex '### ARTIFACT A.*?\n```bash\n(.*?)\n```', syntax-checks it, runs it with 'generic' and validates the JSON
  - changes: runner: tools/hw/verify_compute.sh, /tmp/probe.json
- `python3 tools/hw/evaluate_gate.py --all --dry-run --probe /tmp/probe.json || true; python3 tools/hw/evaluate_gate.py --all --dry-run --probe /tmp/probe.json | grep -qE "— (PASS|DENY)" || { echo "evaluator produced no verdict"; exit 1; }`
  - does: step 'Evaluator runs against a live probe'. The first run is display-only (evaluate_gate exits 1 on DENY); the second requires a verdict line. evaluate_gate prints ' <cls> — PASS|DENY', and its flags --all, --dry-run and --probe exist in its argparse
  - changes: nothing (--dry-run: no token written)
- `node --check router.js`
  - does: step 'UI logic parses'
  - changes: nothing
- `python3 -c "import json;json.load(open('dashboard.json',encoding='utf-8'));print('dashboard.json ok')"`
  - does: step 'Dashboard parses'
  - changes: nothing
- `env PYTHONWARNDEFAULTENCODING=1: python3 -W error::EncodingWarning tools/verify_system.py --quiet; python3 -W error::EncodingWarning tools/reconcile_models.py --help > /dev/null; python3 -W error::EncodingWarning tools/vault_rag.py --help > /dev/null`
  - does: step 'Tools declare their encodings'. The extracted probe now exists, so check_extracted_probe compares here
  - changes: nothing
- `env PYTHONWARNDEFAULTENCODING=1: python3 -W error::EncodingWarning - <<'EOF' … EOF (imports tools/vault_rag.py via importlib)`
  - does: step 'vault_rag core logic': chunk() output within CHUNK_TOKENS*CHARS_PER_TOKEN*1.5; normalize → pack → unpack keeps unit length (dot within 1e-5); strip_frontmatter splits meta and body and leaves a note without frontmatter intact
  - changes: nothing

**Inputs**

- repository at the pushed or PR commit

**Outputs**

- pass/fail of job 'verify'

**Reads**

- tools/verify_system.py
- tools/hw/test_gate.py
- tools/hw/evaluate_gate.py
- skills/hardware_compute.skill.md
- router.js
- dashboard.json
- tools/reconcile_models.py
- tools/vault_rag.py

**Writes**

- (runner only) tools/hw/verify_compute.sh
- (runner only) /tmp/probe.json

**Depends on**

- GitHub Actions ubuntu-latest
- actions/checkout@v4
- actions/setup-python@v5 (Python 3.11)
- node from the runner image (no setup-node step)
- bash

**Environment and secret names (names only)**

- PYTHONWARNDEFAULTENCODING

**Gates and checkpoints**

- Any failing step fails the job
- The evaluator step accepts DENY; it fails only if no PASS/DENY line appears
- EncodingWarning is promoted to an error in the last two steps

**Invoked by**

- push to main
- pull_request
- workflow_dispatch

**Invokes**

- tools/verify_system.py
- tools/hw/test_gate.py
- tools/hw/verify_compute.sh (extracted)
- tools/hw/evaluate_gate.py
- node --check router.js
- tools/reconcile_models.py --help
- tools/vault_rag.py --help / import

**Notes**

One job, 'verify', with 10 steps: checkout, setup-python, Protocol integrity, Gate logic, Probe extracts and parses, Evaluator runs against a live probe, UI logic parses, Dashboard parses, Tools declare their encodings, vault_rag core logic.

git log shows commits 4217342 'Add CI workflow…', e06599e 'Scope the push trigger to main' and 266ec99 'Declare UTF-8…'.

README ('every push and pull request') and D8 ('every push and PR') predate the main-only push scope.

Run history and pass status are not visible in the repo.

### DECISIONS.md (architecture decisions D1-D10)

`doc` · status `runs-today`

Paths: `DECISIONS.md`

Decisions in force: what was chosen, what it rules out, and what it obliges the next pass to do.

**Entry points**

- `Read before changing direction (README)`
  - does: Reference for the agent and humans; cited by Router.md, dashboard.json, router.js and control_room.html
  - changes: nothing

**Environment and secret names (names only)**

- GROQ_API_KEY (named in D5 as passed through by archive docker-compose.yml; name only)

**Gates and checkpoints**

- D7: L3 parks in every mode; derived is never presented as authored
- D9/D10: ARTIFACT A mutation_policy 'operator-approval only; agent proposes, never commits' also governs the three gates
- D6 addendum: do not repopulate active_variables to satisfy stale skill gates

**Invoked by**

- agent / operator reading

**Notes**

EVERY DECISION:

D1 — The memory layer is local-first. Chooses Ollama plus an on-disk vector index in a single process. Rejects the archive's seven-service cloud stack (Groq, Neo4j, Pinecone, Postgres, Redis, Celery). The hardware it cites is superseded by D8. NOT DONE: ai_engine.py still on Groq; graph_store.py (Neo4j) and vector_store.py (Pinecone) need local equivalents; app/tasks/reorganization.py holds two stub Celery tasks; pinecone is commented out in requirements.txt.

D2 — The brush generator becomes a routed executable skill. Plan: a thin adapter over editor/BrushState.js (0 DOM refs), generators/ShapeGenerator.js and GrainGenerator.js (1 each) and export/BrushExporter.js (5), plus skills/brush_designer.skill.md; the UI stays manual. NOT DONE: no adapter or skill file; runs standalone at tools/brush-designer/. Stale: 'skills/ still holds eight files'.

D3 — Living Archive's canonical source is crispy-engine. 27 shared files are byte-identical. crispy-engine adds nine files, including five core modules. Everything under archive/ came from crispy-engine.

D4 — Directory structure was derived, not invented. archive/ was rebuilt from the import graph, render.yaml and docker-compose.yml. archive/backend/Dockerfile and requirements.txt were newly written and never installed or run.

D5 — A third-party Groq key was scrubbed. A gsk_ key in DEPLOY.md was redacted (not the owner's key; inactive; no rotation needed). Secrets come only from the environment and .env; .gitignore covers it.

D6 — The unit of memory is the Content MD, not a live variable ledger. active_variables become run-scoped; the '_prev' supersede rule is removed; the vault is the source of truth and the archive indexes it; self-learning = corpus growth; the cosmos view is the vault rendered.

D7 — The Router is mode-aware; autonomous never waits on a human. Adds the §4 mode read and the §5 L0-L3 ladder with a per-mode gate. L3 parks in every mode; derived is never presented as authored.

'D6 addendum' (a heading placed inside D7): five skills (adobe_firefly, higgsfield_api, blender_python, css_html_ui, suno_audio) carry MIGRATION PENDING banners for stale active_variables gates. Their rewrite is deferred until brush_designer exists as the reference implementation.

D8 — The studio is one Windows laptop, not a Mac host plus a CUDA node. Probe rewritten (hardware_compute v2.0); classes llm_local_sm, llm_local_md, render_3d_cpu, batch_2d; single-flight law; Adobe via PowerShell COM; Blender EEVEE default with CPU-only Cycles at 1920×823; LLM chosen by tier and verified via /api/tags; keep_alive '5m' with eviction; dashboard schema 2.0.0. Enforced by check_host_portability (8 failures pre-port, 0 after). The follow-up pass added tools/bootstrap.sh, tools/hw/evaluate_gate.py, tools/hw/test_gate.py, tools/reconcile_models.py (--write), verify.yml, the verify_compute.sh drift check and BOOT.md. NOT DONE: provisional model tags; Windows/WSL probe branches and the bootstrap COM probe never run on target; 'remains BLOCKED' with 'ten brand gates unauthored' (stale since D9); archive Docker competes for 16 GB; Premiere has no COM path.

D9 — ui-ux-pro-max is vendored as a routed skill and authors three brand gates. tools/ui-ux-pro-max/ (search.py argparse CLI with --json; stdlib; offline; host_kinds [windows, wsl, linux]); skills/ui_ux_intelligence.skill.md. visual_identity, typography_system and color_science were transcribed from css_html_ui ARTIFACT A. Token-authority split: on studio surfaces ARTIFACT A governs and ui_ux_intelligence proposes; on product work ui_ux_intelligence is sole authority via a per-project MASTER.md. 'L0 now means authored, not complete.' State BLOCKED → DEGRADED; claims ui_ux_intelligence is the first fully-L0 skill; css_html_ui parks on brand_voice. Rejected: a context/domain/ library; referencing the payload in place. NOT DONE: no end-to-end product design system; VENDOR.md sha256 unverified (check_vendor_hash suggested); no pipeline phase.

D9 addendum: first regeneration. WCAG fixes: accent.queued 2.23→5.55, ink.dim 3.78→6.34, accent.alert 4.64→5.78, line 1.21→1.71. Four layout bugs fixed. Verified at 375/768/1265 px with verify_system exit 0.

D10 — HARD MONO. Brutalist-minimal, JetBrains Mono only, inversion instead of glow; operator-directed mutation_policy event; Designer Pro tab corpus rows named (styles.csv brutalism, minimalism-and-swiss-style; google-fonts.csv JetBrains Mono). Rejected: light mode; renaming accent tokens (debt left deliberately); retheming brush-designer artwork. Fixed: status-word CSS specificity; Hub rail keyboard access. New rule: inversion is for a live condition only. Obliges: new surfaces read visual_identity §§2–6 and typography_system §§2–4. tokens/design_tokens.json and tokens/tokens.css still absent; css_html_ui P2 reports INIT:P2. Verified: exit 0, 7 tokens green, 375/1000/1440 px on five Hub tabs and control_room.html.

CALLOUTS:
- BRUSH DESIGNER ROUTING STATUS: D2 (not routed; no adapter; no skills/brush_designer.skill.md); D6 addendum under D7 (to be written first as the reference implementation); D9 (cites D2's 'a capability, not a bookmark'); D10 (chrome rethemed, artwork untouched). Router.md §1 says 'Not yet routed'. No brush_designer entry in the dashboard registry or router.js.
- VAULT: D6 (Content MD is the unit of memory; the vault is the source of truth); D7 (the ladder derives from the vault); D8 not-done ('vault is empty' — now stale, 1 note).
- ARCHIVE: D1 (cloud stack; local-first rewrite not done); D3 (source is crispy-engine); D4 (derived tree; Dockerfile and requirements never run); D5 (key scrub; env-only secrets); D6 (archive indexes the vault); D8 not-done (docker-compose vs 16 GB).
- SINGLE-HOST PORT: D8, plus router.js legacy-node display and verify_system check_host_portability.
- UI-UX-PRO-MAX: D9 and its addendum; D10 (Designer Pro corpus rows); .gitattributes (-text) keeps the payload byte-identical.

### README.md (Studio Headless OS overview)

`doc` · status `runs-today`

Paths: `README.md`

Layout, what runs today versus not, how to verify the protocol, the machine, hardware gating, provenance, and 'the loop'.

**Entry points**

- `python3 tools/verify_system.py # exits non-zero on any drift`
  - does: Documented protocol check
  - changes: nothing
- `python3 tools/hw/test_gate.py # pins the gate's verdicts against ARTIFACT B`
  - does: Documented gate test
  - changes: not stated
- `python3 tools/vault_manifest.py`
  - does: Documented: regenerates state/vault_manifest.json for the hub Library tab
  - changes: state/vault_manifest.json
- `python3 -m http.server 8347 (.claude/launch.json hub-static-server), then open http://localhost:<port>/hub/`
  - does: Documented static serving for hub/
  - changes: nothing
- `open tools/brush-designer/index.html from a static server`
  - does: Documented standalone brush designer
  - changes: nothing stated
- `copy agents/ into ~/.claude/agents/ and run claude --agent <name>`
  - does: Documented use of the 9 agent definitions
  - changes: ~/.claude/agents/ (user copy)

**Environment and secret names (names only)**

- OLLAMA_ORIGINS (hub Ask tab; see OBSIDIAN.md)

**Gates and checkpoints**

- Hardware gating as documented: a fresh PASS token at state/compute_gate.json; 30-minute TTL; one token per job (consumed_by); an unreadable metric is null and fails; AC required except llm_local_sm; thermal re-probe every 5 min with checkpoint-pause after two consecutive denials; single flight

**Invoked by**

- humans / agent orientation

**Notes**

'What does not run yet' lists archive/ and any routed task: no vault indexer, no Content MD step wired in, router.js dispatch still stubs. It adds: 'The loop is specified, not built.'

Stale or conflicting statements:
- 'The ten context/brand/ constants are still unauthored', which contradicts its own layout ('3 authored').
- verify_system 'passes with all ten gates reported as pending and the state declared BLOCKED'; the state is DEGRADED, and check_context_loaded asserts nothing when the vault has notes.
- 'eight mandatory_context headers'; there are 9.
- 'There is no vault indexer', although its layout lists tools/vault_rag.py as one.
- 'Four tabs', but it lists five: Library, Ask, Designer Pro, Brushes, Pipeline.
- CI on 'every push'; push is scoped to main.

### .gitignore

`context` · status `runs-today`

Paths: `.gitignore`

Keeps secrets, runtime state, the generated probe, Obsidian plugin state and embedding caches out of git.

**Entry points**

- `Applied automatically by git`
  - does: Ignores the listed patterns
  - changes: nothing

**Depends on**

- git

**Gates and checkpoints**

- .env and .env.* ignored; !.env.example kept
- state/ ('runtime state written by the router') and .task_scratch/
- tools/hw/verify_compute.sh ('generated by tools/bootstrap.sh from hardware_compute ARTIFACT A — never edit in place')
- vault/.obsidian/plugins/*/data.json, workspace.json, workspace-mobile.json, cache, graph.json; vault/.trash/
- vault/.smart-env/, vault/.smart-connections/, *.faiss, *.embeddings.json
- *.key, *.pem, *.p12, *.pfx, secrets/, credentials.json, *.token, .netrc, tools/**/config.local.*
- __pycache__/, *.py[cod], .venv/, venv/, node_modules/, dist/, .DS_Store, ._*, Thumbs.db, desktop.ini, *~, *.swp, .idea/, .vscode/

**Invoked by**

- git

**Notes**

compute_gate.json is not named in .gitignore; it falls under state/ by path (README names state/compute_gate.json). On disk, state/ currently holds rag_index/ and vault_manifest.json.

git ls-files shows only evaluate_gate.py and test_gate.py tracked in tools/hw. The extracted probe is absent locally, so check_extracted_probe is a no-op on this machine now.

### .gitattributes

`context` · status `runs-today`

Paths: `.gitattributes`

Stops EOL normalisation of the vendored ui-ux-pro-max payload so it stays byte-identical to upstream (LF).

**Entry points**

- `tools/ui-ux-pro-max/** -text`
  - does: Disables text/EOL conversion for the vendored payload
  - changes: nothing

**Depends on**

- git

**Gates and checkpoints**

- Keeps the sha256 in tools/ui-ux-pro-max/VENDOR.md comparable with an upstream checkout

**Invoked by**

- git

**Notes**

Supports D9's 'no local edits' guarantee. Nothing verifies the hash on a run (D9 not-done).

### hub-static-server launcher (.claude/launch.json)

`launcher` · status `runs-today`

Paths: `.claude/launch.json`

Static HTTP server configuration so pages that fetch local JSON (hub/, control_room.html) work over http rather than file://.

**Entry points**

- `python3 -m http.server 8347`
  - does: Serves the working directory on port 8347 (configuration name 'hub-static-server', port 8347)
  - changes: nothing

**Outputs**

- HTTP origin http://localhost:8347

**Reads**

- repository files

**Depends on**

- python3

**Invoked by**

- Claude Code preview (launch.json)
- operator

**Notes**

Outside the assigned file list; included because README cites it. It declares no cwd; the served directory is whatever the launcher uses (assumed to be the repo root).

## Usage flows

### Routed task per Router.md (specification; carried out by an agent, no code)

1. The agent has Router.md loaded and receives a task.
2. Trigger A scans the request for intent verbs and nouns. Trigger B checks asset file types and dashboard.json pipeline.phases[] statuses (awaiting_render / compositing / queued / blocked). If neither fires, route to general_chat and execute no skill.
3. HALT. Step 1 MODE: read system_status.mode (currently autonomous).
4. Step 2 RESOLVE: map each candidate skill to its §3 mandatory contexts; for multiple skills, take the union and deduplicate.
5. Step 3 LADDER: resolve each context L0 → L1 → L2 → L3 and apply the mode gate. Park on L3.
6. Step 4 RECALL: locate the Content MD, or create it from vault/_templates/content-md.md with status: seed. Read Overview, Next Steps, Decisions in Force and Method in full.
7. Step 5 VERIFY: print the ROUTER INTERCEPT attestation (every §3 context with level, confidence and source; ⚠ PROVISIONAL on L2). Any tool call before this point is an INTERCEPT_VIOLATION: abort, log, restart.
8. Step 6 STATE: confirm no phase conflict; write the phase as in_progress in dashboard.json, plus an event_log entry.
9. Step 7 EXECUTE: open skills/<skill>.skill.md and follow Prerequisites → Execution Process → Embedded Artifacts. Compute-heavy work goes through hardware_compute and needs a fresh PASS token (single-flight).
10. Step 8 WRITEBACK: Timeline entry, Next Steps rewrite, Decisions in Force, Open Questions moved, Contradictions, Method, 'updated' and status. Then write dashboard.json: event_log entry and last_heartbeat.

### Park at L3 (autonomous mode)

1. The ladder finds no authored file, no L1 decision and fewer than 3 related notes.
2. Do not execute.
3. Write the gap as the first '## Next Steps' item, naming the missing context and what would resolve it (e.g. author context/brand/<name>.context.md).
4. Set the Content MD's status to blocked.
5. Log PARKED to event_log with the context name and Content MD path.
6. Route the next task without asking or waiting. Precedent: the 2026-08-23 event_log entry parked ph_03 higgsfield_api with content_md null.

### Proceed provisionally at L2 below 0.70 (autonomous only)

1. Derive the constraint from at least 3 related-kind Content MDs, weighting complete and recent notes.
2. Show it in the attestation as 'L2 DERIVED <conf> [[sources]] ⚠ PROVISIONAL'.
3. Execute.
4. Record the derived constraint in the Content MD's '## Decisions in Force' with its confidence and sources.
5. Log PROVISIONAL with the context name and Content MD path. A later authored file may overturn it.

### Watch the control room

1. Start a static server, e.g. python3 -m http.server 8347 (launch.json hub-static-server) or any static server.
2. Open control_room.html over HTTP. Under file:// the fetch fails and the offline note appears.
3. router.js fetches dashboard.json?t=<now> with no-store, renders the header, pipeline rail, variables, compute meters and facts, event log, skill registry and brand gates, then re-polls every 5 s while the tab is visible.
4. If a fetch fails, the page adds body.offline, shows the amber note and keeps the last good state if one exists.

### UI-initiated route (skill chip click)

1. Click a chip in the Skill Registry.
2. routeSkill(file) gets the mandatory gates from resolveGates (the §3 mirror). An unknown file yields [] gates.
3. isAuthoredL0 checks each gate against dashboard registries.context_brand_gates[].authored === true.
4. If any gate is unauthored, log a local PARKED row (actor control_room) and return {ok:false, parked:true}. Currently 7 of 9 chips park.
5. If all gates are authored (currently ui_ux_intelligence and adobe_firefly, or any unknown file), log a local INTERCEPT row marked '(stub)' and return ok:true. There is no dispatch (TODO) and no dashboard write, and the caller ignores the return value.
6. Local rows live only in memory, capped at 40, and are lost on reload.

### Protocol drift check after editing a protocol file

1. Edit Router.md, dashboard.json, router.js, control_room.html, a skill header, a context/brand file or css_html_ui ARTIFACT A.
2. Run python3 tools/verify_system.py, or add --quiet for the exit code only.
3. Fix every FAIL (exit 1) until it exits 0. WARNs are advisory. It will not catch a skill mapped to the wrong but valid gate in one copy.
4. Push to main or open a PR; CI job 'verify' re-runs it along with the other checks.

### CI job 'verify'

1. Triggered by push to main, pull_request or workflow_dispatch; runs on ubuntu-latest.
2. actions/checkout@v4, then actions/setup-python@v5 with 3.11.
3. python3 tools/verify_system.py (the probe has not been extracted yet).
4. python3 tools/hw/test_gate.py.
5. Extract ARTIFACT A from skills/hardware_compute.skill.md to tools/hw/verify_compute.sh; bash -n; chmod +x; run it with 'generic' into /tmp/probe.json; json.load it.
6. python3 tools/hw/evaluate_gate.py --all --dry-run --probe /tmp/probe.json, and require a '— PASS' or '— DENY' line.
7. node --check router.js.
8. Parse dashboard.json as UTF-8.
9. With PYTHONWARNDEFAULTENCODING=1 and -W error::EncodingWarning: verify_system.py --quiet (now comparing the extracted probe), reconcile_models.py --help, vault_rag.py --help.
10. Run the vault_rag core-logic asserts: chunk size cap, pack/unpack unit length, strip_frontmatter.

### Promote a brand gate from L3 to L0

1. Author context/brand/<name>.context.md. Brand constants encode taste (context/brand/README.md, Router §3, D9). For studio-surface gates, the D9/D10 mutation_policy applies: operator approval only.
2. Set dashboard.json registries.context_brand_gates[role=<name>].authored to true. check_brand_gates FAILs if the flag and the disk disagree.
3. Log GATE_AUTHORED (precedent 2026-08-31) and update blocked_reason and state as appropriate.
4. Run python3 tools/verify_system.py.
5. The Brand Gates row stops showing 'missing'. routeSkill passes L0 for skills whose mandatory gates are now all authored.

## Relationships

| From | Relation | To |
|---|---|---|
| router.js poll and render layer (Logic Bridge, 'Core File 4/4') | GET every 5000 ms, cache-busted, read-only | dashboard.json (live system state, schema 2.0.0) |
| control_room.html (Control Room UI) | loads via <script src=router.js>; router.js writes into its element ids | router.js poll and render layer (Logic Bridge, 'Core File 4/4') |
| router.js poll and render layer (Logic Bridge, 'Core File 4/4') | skill chip click calls routeSkill (return value discarded) | router.js routing layer (routeSkill / resolveGates / brandPath / isAuthoredL0 / dispatchA… |
| router.js routing layer (routeSkill / resolveGates / brandPath / isAuthoredL0 / dispatchA… | resolveGates is a hard-coded mirror of the mandatory column only | Router §3 routing table (skill → mandatory context) |
| router.js routing layer (routeSkill / resolveGates / brandPath / isAuthoredL0 / dispatchA… | implements the L0 check only; ignores the mode; defers L1/L2 to the agent | Router §4-5 execution mode, context resolution ladder (L0-L3) and mode gate |
| router.js routing layer (routeSkill / resolveGates / brandPath / isAuthoredL0 / dispatchA… | isAuthoredL0 reads registries.context_brand_gates[].authored from STATE | dashboard.json (live system state, schema 2.0.0) |
| Studio Router protocol (Router.md v1.1) | reads mode and phases; writes phase status, event_log and heartbeat (spec) | dashboard.json (live system state, schema 2.0.0) |
| Router §2 dual-trigger intercept and 8-step sequence | Trigger B.2 reads pipeline.phases[].status | dashboard.json (live system state, schema 2.0.0) |
| Router §7-8 Content MD emission and context flush | reads and writes exactly one Content MD per routed task (spec); cross-subsystem | vault/ (Content MDs, SCHEMA.md, _templates/content-md.md) |
| Router §4-5 execution mode, context resolution ladder (L0-L3) and mode gate | L0 source; cross-subsystem | context/brand/*.context.md |
| Router §4-5 execution mode, context resolution ladder (L0-L3) and mode gate | L1 recall and L2 derivation (at least 3 notes) | vault/ (Content MDs, SCHEMA.md, _templates/content-md.md) |
| Router §10 hard refusals | requires hardware verification and a fresh PASS token; cross-subsystem | skills/hardware_compute.skill.md and tools/hw/* (evaluate_gate.py, test_gate.py, verify_c… |
| Studio Router protocol (Router.md v1.1) | opened at intercept step 7 (Parts 2-4 of the Four-Part architecture) | skills/*.skill.md |
| Router §3 routing table (skill → mandatory context) | copied in each skill's 'mandatory_context:' header; all 9 match | skills/*.skill.md |
| Router §3 routing table (skill → mandatory context) | inverse copy in registries.context_brand_gates[].gates_skills; includes one flagged pairing (pipeline_ethics… | dashboard.json (live system state, schema 2.0.0) |
| tools/verify_system.py (protocol integrity checker) | parses and cross-checks registries, pipeline, context_loaded, event_log and host_kind_enum | dashboard.json (live system state, schema 2.0.0) |
| tools/verify_system.py (protocol integrity checker) | check_router_md: role mentions and path strings only | Studio Router protocol (Router.md v1.1) |
| tools/verify_system.py (protocol integrity checker) | check_router_js: STATE gate read, context/brand/ present, context/domain/ absent, role names present | router.js routing layer (routeSkill / resolveGates / brandPath / isAuthoredL0 / dispatchA… |
| tools/verify_system.py (protocol integrity checker) | check_router_js ids and c-* classes; check_palette_parity on 7 tokens vs css_html_ui ARTIFACT A | control_room.html (Control Room UI) |
| tools/verify_system.py (protocol integrity checker) | check_skill_headers, check_host_portability, check_palette_parity (css_html_ui), check_extracted_probe (hardw… | skills/*.skill.md |
| tools/verify_system.py (protocol integrity checker) | counts notes for the BLOCKED-state rule | vault/ (Content MDs, SCHEMA.md, _templates/content-md.md) |
| tools/verify_system.py (protocol integrity checker) | check_extracted_probe compares tools/hw/verify_compute.sh with ARTIFACT A when present | skills/hardware_compute.skill.md and tools/hw/* (evaluate_gate.py, test_gate.py, verify_c… |
| .github/workflows/verify.yml (CI workflow 'verify') | runs twice: plain, then --quiet under -W error::EncodingWarning | tools/verify_system.py (protocol integrity checker) |
| .github/workflows/verify.yml (CI workflow 'verify') | runs test_gate.py; extracts and runs verify_compute.sh generic; evaluate_gate.py --all --dry-run --probe /tmp… | skills/hardware_compute.skill.md and tools/hw/* (evaluate_gate.py, test_gate.py, verify_c… |
| .github/workflows/verify.yml (CI workflow 'verify') | node --check router.js | router.js poll and render layer (Logic Bridge, 'Core File 4/4') |
| .github/workflows/verify.yml (CI workflow 'verify') | 'Dashboard parses' step | dashboard.json (live system state, schema 2.0.0) |
| .github/workflows/verify.yml (CI workflow 'verify') | --help encoding smoke tests; vault_rag imported for core-logic asserts; cross-subsystem | tools/reconcile_models.py and tools/vault_rag.py |
| tools/reconcile_models.py and tools/vault_rag.py | reconcile_models --write rewrites hardware.local_llm.tiers[*].model and _tiers_note; vault_rag ask --write-da… | dashboard.json (live system state, schema 2.0.0) |
| DECISIONS.md (architecture decisions D1-D10) | D8 adds check_host_portability and the probe drift check; D9 proposes check_vendor_hash (absent) | tools/verify_system.py (protocol integrity checker) |
| DECISIONS.md (architecture decisions D1-D10) | D7 introduced the mode read and the ladder | Router §4-5 execution mode, context resolution ladder (L0-L3) and mode gate |
| DECISIONS.md (architecture decisions D1-D10) | D2: planned routed skill, not routed (no adapter, no skills/brush_designer.skill.md) | tools/brush-designer/ |
| DECISIONS.md (architecture decisions D1-D10) | D9's vendored ui-ux-pro-max byte-identity relies on '-text' | .gitattributes |
| .gitignore | ignores the generated tools/hw/verify_compute.sh and state/ (compute_gate.json location per README) | skills/hardware_compute.skill.md and tools/hw/* (evaluate_gate.py, test_gate.py, verify_c… |
| hub-static-server launcher (.claude/launch.json) | serves files over HTTP so router.js can fetch dashboard.json | control_room.html (Control Room UI) |
| dashboard.json (live system state, schema 2.0.0) | registries.context_brand_gates[].authored must equal file existence (check_brand_gates) | context/brand/*.context.md |
| Studio Router protocol (Router.md v1.1) | §1 topology: 'Not yet routed' | tools/brush-designer/ |

**Open questions the files could not settle**

- Is adobe_firefly meant to route at L0? Its §3 mandatory set (visual_identity, color_science) is fully authored and router.js passes it, yet D9 and dashboard blocked_reason say only ui_ux_intelligence routes fully. Perhaps color_science §5's declared gaps or the D6-addendum MIGRATION PENDING banner are meant to hold it back; no file says so.
- Which agent or process wrote the 2026-08-31 event_log entries with actor 'router'? Nothing in code writes event_log, pipeline or system_status. Also, why was last_heartbeat not bumped as §9 requires?
- How is a context 'flagged in dashboard' for §3's right-hand column? No field expresses it. Is the dashboard's pipeline_ethics → local_rag_orchestration gates_skills entry (a flagged-column pairing) intended?
- Which tool issues the compute PASS token? Router §10 says verify_compute.sh; README and D8 say tools/hw/evaluate_gate.py mints it at state/compute_gate.json.
- dashboard.json system_status.router_version is '1.0' while Router.md is v1.1. Should it be updated?
- Are the 2026-07-01 event_log entries (INTERCEPT, CONTEXT_LOADED, RENDER_SUBMITTED hf_a91x, COMP_STARTED, HEARTBEAT) real runs or sample data? D6 calls the matching active_variables sample values but does not classify the log.
- How is an L2 confidence in the 0.3-0.8 range computed? Router.md gives weighting rules but no formula.
- Does a local agent runner at http://localhost:8787 (router.js dispatch registry) exist anywhere? None is found in these files.
- Has CI job 'verify' run and passed on main? No run results are in the repo; D9 and D10 record local exit 0.
- check_context_loaded makes no state assertion when the vault holds between 1 and 2 notes. Should DEGRADED with 7 unauthored gates be machine-checked?
- Is meta.file_count_target 23 (and the '22 protocol files' docstring) meant to be enforced? Only 4 core files are checked.
- Should verify_system also check that every registered skill appears in router.js resolveGates? Today an unregistered file passes routeSkill and an unmapped registered skill would route with zero gates.

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: ui_ux_intelligence is the only skill whose mandatory context all resolves at L0; 'With the current dashboard, only skills/ui_ux_intelligence.skill.md returns ok:true; every other chip parks' (summary, routing layer notes, UI route flow)
  - evidence: router.js L299 maps adobe_firefly to [visual_identity, color_science]; dashboard.json L237 and L247 mark both authored:true. routeSkill therefore returns ok:true for adobe_firefly too. D9 L398 and dashboard blocked_reason name only ui_ux_intelligence, so the docs disagree with the table.
- **corrected**: router.js routing layer 'Fails closed: an unknown role or authored !== true parks'
  - evidence: router.js L307 returns [] for an unknown skill file. L279-L291: an empty unresolved list falls through to logLocal INTERCEPT and returns ok:true. It fails closed for roles and fails open for unknown skill files.
- **corrected**: routeSkill outputs 'return objects as described'
  - evidence: router.js L229: the only caller is chip.addEventListener('click', () => routeSkill(s.file)), which discards the return value.
- **corrected**: DECISIONS 'D7 addendum' (five skills with MIGRATION PENDING; brush_designer first)
  - evidence: DECISIONS.md L203: the heading is '### D6 addendum — five skill files carry stale state references', placed inside the D7 section.
- **corrected**: verify_system.py 'Catches drift between the copies of the routing contract'
  - evidence: tools/verify_system.py L122-134 only checks that header roles are valid gates. L225-227 and L257-259 only WARN if a role string is absent. L96-99 only checks that gates_skills are registered. No function compares per-skill skill→context mappings across Router.md §3, router.js, the headers and dashboard gates_skills.
- **added**: dashboard context_brand_gates is an inverse map of §3 (implied to be the mandatory column)
  - evidence: dashboard.json L302-L310: pipeline_ethics gates_skills includes local_rag_orchestration, which is in Router.md §3 L158's 'Also load if flagged' column, not the mandatory column. The other flagged pairings are absent. Unchecked by verify_system.
- **corrected**: No code writes dashboard.json; 'presumably' tools/reconcile_models.py --write applies tier drift (not verified)
  - evidence: tools/reconcile_models.py L136-L150 (--write) writes hardware.local_llm.tiers[*].model and _tiers_note. tools/vault_rag.py L490-L494 (ask --write-dashboard, L576) writes hardware.local_llm.context_used_pct and loaded_tier. Nothing writes phases, event_log or system_status.
- **corrected**: Step 7 'Four-Part Architecture' lists three parts; the fourth is unknown (open question)
  - evidence: skills/hardware_compute.skill.md L6 'ROUTING HEADER (Part 1 of 4)', L46 'PREREQUISITES & STATE VERIFICATION (Part 2 of 4)', L105 'EXECUTION PROCESS (Part 3 of 4)', L133 'EMBEDDED ARTIFACTS (Part 4 of 4)'. Step 7 omits Part 1.
- **corrected**: Router §3 routing table status 'runs-today'
  - evidence: Router.md §3 is spec. Only the mandatory column is mirrored and used (router.js L295-L308), and the 'Also load if flagged' column has no implementation anywhere. Status changed to 'partial'.
- **corrected**: Router protocol 'invokes tools/verify_system.py'
  - evidence: Router.md L93-94 only names verify_system.py as the enforcer of host_kinds. The protocol does not invoke it. Moved to notes.
- **corrected**: .gitignore ignores 'state/ (router runtime state, including state/compute_gate.json, rag_index and rag_traces)'
  - evidence: .gitignore L17 'state/' with the comment 'runtime state written by the router'. rag_index/rag_traces are named in the L39 comment; compute_gate.json is not named (README L179 gives that path). ls state/ shows rag_index and vault_manifest.json only.
- **unverifiable**: dashboard event_log entries with actor 'router' dated 2026-08-31 are agent writebacks
  - evidence: dashboard.json L341-L351 show actor 'router', but no file records who or what wrote them. Kept only as an open question.
- **added**: Router §9: last_heartbeat updates on every writeback (implied to hold in current data)
  - evidence: dashboard.json L23 last_heartbeat is 2026-08-23T18:30:00Z, while event_log L335-L351 has three entries dated 2026-08-31. Actors also include ui_ux_intelligence, higgsfield_api and adobe_suite_uxp, not only 'router'.
- **unverifiable**: control_room.html URL http://localhost:8347/control_room.html
  - evidence: .claude/launch.json declares only 'python3 -m http.server 8347' with no cwd. README L89-91 gives only /hub/. control_room.html L276 suggests a generic 'python3 -m http.server'.
- **unverifiable**: verify_system requires Python 3.9+
  - evidence: Inferred from module-level 'FAILS: list[str] = []' (tools/verify_system.py L22). No version is stated in the files. CI pins 3.11 (verify.yml L23).
- **added**: verify_system exit codes: 0 consistent, 1 any FAIL or unparseable dashboard
  - evidence: tools/verify_system.py L373-L401 confirm this. Additionally, direct key indexing (e.g. L58, L76, L363 e['ts']) raises an uncaught exception instead of a FAIL for a structurally incomplete dashboard.
- **added**: verify_system PASS output reflects check outcome
  - evidence: tools/verify_system.py: ok() is called unconditionally in check_brand_gates L92/L100, check_domain_libraries L119, check_host_portability L196, check_router_md L235, check_router_js L255/L266/L272, check_pipeline L334, check_context_loaded L344 and check_event_log L370, so PASS lines can co-exist with FAILs from the same check.
- **added**: verify_system checks (implicit completeness)
  - evidence: No check validates system_status.state ∈ state_enum, mode ∈ mode_enum, or hardware.host_kind ∈ host_kind_enum, and nothing checks meta.file_count_target (tools/verify_system.py, whole file).
- **added**: verify_system invoked_by: developer, CI
  - evidence: tools/bootstrap.sh L191 lists 'python3 tools/verify_system.py' as a next step. tools/reconcile_models.py L150 prompts a re-run after --write. BOOT.md L10 lists it as 'must exit 0'.
- **added**: CI evaluator step (flags and grep pattern)
  - evidence: tools/hw/evaluate_gate.py L236-L238 define --all, --probe and --dry-run. L209 prints ' {cls} — PASS|DENY', matching the grep. L17 gives exit 0 PASS / 1 DENY / 2 could not evaluate, which explains the '|| true'.
- **added**: README entry points
  - evidence: README.md L102-103 'copy into ~/.claude/agents/ and invoke with claude --agent <name>'. L93 'tools/brush-designer/ — open index.html from a static server'.
- **added**: README stale statements
  - evidence: README.md L60 says 'Four tabs:' but L62-L87 list five (Library, Ask, Designer Pro, Brushes, Pipeline). L138 'every push' vs verify.yml L10-11 push branches [main]; D8 L308 'every push and PR' is also stale.
- **added**: router.js renderContext row classes ('on' if authored and loaded, 'missing' if unauthored)
  - evidence: router.js L249-L250: an authored-but-not-loaded row gets class '' (the neutral queued-colour dot per control_room.html L243). With context_loaded [] (dashboard.json L27), all 3 authored rows are neutral.
- **added**: LLM context window meter
  - evidence: router.js L135-L136 with dashboard loaded_tier null (L79) and no local_llm.context_window_tokens: ctxTokens = 0, so it renders '0% of 0k tokens'.
- **added**: Brand Gates panel labelling
  - evidence: control_room.html L300 aria-label="Context attestation".
- **added**: CI run history unknown
  - evidence: git log for verify.yml: 4217342 'Add CI workflow and make first boot executable', e06599e 'Scope the push trigger to main', 266ec99 'Declare UTF-8 on every file read and write; keep console output ASCII'. Run results are still not visible.
- **corrected**: Skill headers match §3 exactly; adobe_suite_uxp host_kinds [windows, wsl]
  - evidence: Confirmed by grep of skills/*.skill.md ('mandatory_context:' and 'host_kinds:' lines). All 9 match Router.md §3 L152-L160; adobe_suite_uxp L14 is [windows, wsl] and all others are [windows, wsl, linux]. Retained as verified.
