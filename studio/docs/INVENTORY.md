# Inventory of Creative-Headquarters

What Creative-Headquarters contains and how each part is used. Extracted on
2026-09-28 from the working tree of `C:\Users\utopi\Creative-Headquarters`
(branch `claude/hub-taskbar-launcher`, last commit `05ccb93`, with uncommitted
changes present).

What each idea became in this repo is in [IDEAS.md](IDEAS.md).

## How this was made, and what that means

Thirteen read-only agents each read one subsystem in full. A second agent then
re-checked every command, flag, path and status claim against source and
corrected the first reading. Eleven of those subsystems describe
Creative-Headquarters and are recorded here; the other two described this repo.

**No project script was executed.** A status below is a reading of the code,
with on-disk evidence where the detail file says so. It is not an observation
of the tool running.

| Status | Meaning |
|---|---|
| `runs-today` | implemented; nothing in the files says it cannot run |
| `partial` | some of it is implemented, or it runs with a known defect |
| `never-exercised` | written, with no evidence it has ever run on the target machine |
| `specified-not-implemented` | described in a document; no code does it |
| `stub` | a placeholder that returns or shows fixed values |
| `vendored` | copied from another repository |
| `generated` | produced by another tool |

226 entries in all: 99 `runs-today`, 45 `partial`, 40 `never-exercised`, 15 `vendored`, 13 `specified-not-implemented`, 8 `generated`, 6 `stub`.

`inventory/graph.json` holds the same entries as nodes and their relationships as
edges (226 nodes, 489 edges), for drawing the map.

## Contents

| Subsystem | Entries | Detail |
|---|---|---|
| Routing protocol and its checkers | 19 | [inventory/protocol-core.md](inventory/protocol-core.md) |
| Generative skills: video, music, image | 3 | [inventory/skills-generative.md](inventory/skills-generative.md) |
| Local-application skills: Adobe, Blender, front-end | 13 | [inventory/skills-local-apps.md](inventory/skills-local-apps.md) |
| Infrastructure skills: compute gate, local RAG, UI intelligence | 23 | [inventory/skills-infra.md](inventory/skills-infra.md) |
| Hardware gate toolchain | 11 | [inventory/hw-gate.md](inventory/hw-gate.md) |
| Vault and its indexers | 13 | [inventory/vault-rag.md](inventory/vault-rag.md) |
| Hub and launcher | 11 | [inventory/hub-launcher.md](inventory/hub-launcher.md) |
| Brush designer | 34 | [inventory/brush-designer.md](inventory/brush-designer.md) |
| Agents, brand gates, domain libraries | 24 | [inventory/agents-context.md](inventory/agents-context.md) |
| ui-ux-pro-max, and how it became plugins/ui-design | 48 | [inventory/ui-ux-pro-max-vs-plugin.md](inventory/ui-ux-pro-max-vs-plugin.md) |
| Archive engine | 27 | [inventory/archive.md](inventory/archive.md) |

## Routing protocol and its checkers

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

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| Studio Router protocol (Router.md v1.1) | protocol | `specified-not-implemented` | Execution contract that, when loaded into an agent's context, makes the agent act as the 'Studio Router' and run the intercept before touching any skill file, tool, API or local script. Prime Rule: 'NO SKILL EXECUTES WITHOUT ITS CONTEXT RESOLVED, ATTESTED, AN… |
| Router §2 dual-trigger intercept and 8-step sequence | protocol | `specified-not-implemented` | Decides whether a task is routed and fixes the order of operations for a routed task. |
| Router §3 routing table (skill → mandatory context) | data | `partial` | Maps each of the 9 skills to the brand constants it must load before execution, plus contexts to also load 'if flagged in dashboard'. |
| Router §4-5 execution mode, context resolution ladder (L0-L3) and mode gate | protocol | `specified-not-implemented` | Defines behaviour when a required constraint has no authored file. The ladder descends L0→L3 and stops at the first level that resolves; the mode then decides proceed, ask or park. |
| Router §6 Context Attestation Block | protocol | `specified-not-implemented` | Required printed readout, before the first tool call of a routed task, showing that every mandatory context was resolved and sourced. |
| Router §7-8 Content MD emission and context flush | protocol | `specified-not-implemented` | Every routed task reads and writes exactly one vault Content MD, which is the persistent memory and 'how the next session exists'. |
| Router §9 writeback rules | protocol | `specified-not-implemented` | How the router records state changes in dashboard.json and Content MDs. |
| Router §10 hard refusals | protocol | `specified-not-implemented` | Refusals that hold in every mode; autonomy relaxes only §5's gate. |
| dashboard.json (live system state, schema 2.0.0) | data | `runs-today` | Live run state and gate registry: mode, system state, hardware, pipeline phases, run-scoped variables, skill and context registries, event log. |
| router.js poll and render layer (Logic Bridge, 'Core File 4/4') | library | `runs-today` | Fetches dashboard.json on load and on an interval, and renders every control_room.html region from that single state object. |
| router.js routing layer (routeSkill / resolveGates / brandPath / isAuthoredL0 /… | library | `stub` | Placeholder 'seam where the headless agent / local services attach': a UI-initiated route that mirrors resolve context → verify → dispatch. |
| control_room.html (Control Room UI) | web-app | `runs-today` | Human-facing live view of dashboard.json; README: 'it does not drive anything yet'. |
| tools/verify_system.py (protocol integrity checker) | cli | `runs-today` | Checks structural consistency between the protocol files: registry vs disk, gate flags vs disk, roles named in headers, Router.md and router.js, UI ids, classes and tokens, pipeline coherence, host portability and the extracted probe. It does not compare per-… |
| .github/workflows/verify.yml (CI workflow 'verify') | ci | `runs-today` | Runs the protocol checks and tool smoke tests on GitHub Actions so they do not depend on local runs. |
| DECISIONS.md (architecture decisions D1-D10) | doc | `runs-today` | Decisions in force: what was chosen, what it rules out, and what it obliges the next pass to do. |
| README.md (Studio Headless OS overview) | doc | `runs-today` | Layout, what runs today versus not, how to verify the protocol, the machine, hardware gating, provenance, and 'the loop'. |
| .gitignore | context | `runs-today` | Keeps secrets, runtime state, the generated probe, Obsidian plugin state and embedding caches out of git. |
| .gitattributes | context | `runs-today` | Stops EOL normalisation of the vendored ui-ux-pro-max payload so it stays byte-identical to upstream (LF). |
| hub-static-server launcher (.claude/launch.json) | launcher | `runs-today` | Static HTTP server configuration so pages that fetch local JSON (hub/, control_room.html) work over http rather than file://. |

Full detail: [inventory/protocol-core.md](inventory/protocol-core.md)

## Generative skills: video, music, image

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

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| higgsfield_api | skill | `never-exercised` | Agent-followed instructions for AI video generation (image-to-video / text-to-video) through the Higgsfield REST API. Character, environment and seed persistence across chained shots is enforced through an on-disk Continuity State-Machine (ARTIFACT C). |
| suno_audio | skill | `never-exercised` | Agent-followed instructions for AI music generation through a Suno API. Prompts are built from fixed bracket-tag 'fixture' skeletons (ARTIFACT B), and key/BPM act as musical continuity locks. |
| adobe_firefly | skill | `never-exercised` | Agent-followed instructions for AI image generation through the Adobe Firefly API, using OAuth server-to-server auth. Responses are parsed only with an embedded regex set, and a style-reference ledger (state/style_ledger.json) serves as the style-continuity r… |

Full detail: [inventory/skills-generative.md](inventory/skills-generative.md)

## Local-application skills: Adobe, Blender, front-end

Three agent-executed skill files, each in the Four-Part Artifact Architecture (§0 routing header, §1 prerequisites and state verification, §2 execution process, §3 embedded artifacts). Each reaches its local tool a different way. adobe_suite_uxp (v2.0) drives Photoshop, Illustrator and After Effects through PowerShell COM (New-Object -ComObject plus DoJavaScriptFile, or DoScriptFile for AfterFX). It self-extracts parameterized ExtendScript to a Windows-visible temp dir ($STUDIO_TMP), runs it through the ARTIFACT D wrapper run_jsx.sh under a timeout (default 600s), and deletes the temp file. Its host_kinds are [windows, wsl]. Premiere (ARTIFACT C) has no COM and depends on an undefined CEP/UXP panel endpoint. blender_python (v2.0) runs fixed bpy templates headless (blender -b -P script -- params.json). EEVEE is the default engine and Cycles is CPU-only with a sample ceiling. P4 requires a fresh, unconsumed render_3d_cpu PASS token in state/compute_gate.json, and step 2 claims it. css_html_ui (v1.0) has no host bridge. It is a token-only front-end build discipline. Its ARTIFACT A token dictionary (HARD MONO, 2026-09-01) is the source that control_room.html, hub/styles.css, tools/brush-designer/styles.css and three brand context files transcribe, and tools/verify_system.py regex-checks 7 of its colour values against control_room.html. None of the extraction targets exist on disk: run_jsx.sh, tools/bpy/*, tokens/*, state/compute_gate.json, .task_scratch/, project/, backups/, renders/ and build/ are all absent. DECISIONS.md D10 states that tokens/ has never existed. All three routes currently park at Router L3 on unauthored brand gates: render_philosophy for adobe; render_philosophy and motion_language for blender; brand_voice for css. Every prerequisite block only echoes OK, FAIL, WARN or INIT and never exits non-zero, so enforcement is left to the agent reading the output.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| adobe_suite_uxp (skill) | skill | `never-exercised` | Agent-executed skill that automates Photoshop, Illustrator and After Effects on Windows. It writes a parameterized ExtendScript artifact to a Windows-visible temp dir, runs it through PowerShell COM, parses the single result line and deletes the temp file. Pr… |
| adobe_suite_uxp ARTIFACT A — Photoshop batch layer → PNG exporter | library | `never-exercised` | ExtendScript (#target photoshop). It opens SRC_PSD and, if SCALE_PCT is not 100, resizes the width by SCALE_PCT with BICUBICSHARPER (height null). For each top-level layer it shows only that layer and exports a transparent PNG-24 via Save for Web to OUT_DIR/<… |
| adobe_suite_uxp ARTIFACT B — Photoshop batch grade + export | library | `never-exercised` | ExtendScript (#target photoshop). For every png/tif/tiff/psd/jpg in SRC_DIR it applies adjustLevels(BLACK_IN, WHITE_IN, GAMMA, 0, 255) to the active layer, converts to 'sRGB IEC61966-2.1' (Intent.RELATIVECOLORIMETRIC), flattens, and saves a copy as JPEG (qual… |
| adobe_suite_uxp ARTIFACT C — Premiere Pro shot-ledger markers + offline relink… | library | `never-exercised` | ExtendScript for Premiere, run 'via bridge'. It reads a marker JSON array [{seconds, name, comment}], creates markers on the active sequence, lists offline project items at the root level of the project, and writes a report to REPORT_PATH. |
| adobe_suite_uxp ARTIFACT D — run_jsx.sh extraction/cleanup wrapper (bash + COM) | cli | `never-exercised` | The 'ONLY sanctioned runner'. It resolves STUDIO_TMP, copies the parameterized artifact to $STUDIO_TMP/studio_uxp_<task_id>.jsx, refuses unresolved {{ tokens, picks DoJavaScriptFile or DoScriptFile by ProgID, and runs it through PowerShell COM under a timeout… |
| blender_python (skill) | skill | `never-exercised` | Agent-executed skill for 3D inserts and previz. It unpacks fixed bpy templates to tools/bpy/, drives them from a JSON params sidecar and runs them headless (blender -b -P). It requires a fresh, unconsumed render_3d_cpu PASS token from hardware_compute. EEVEE… |
| blender_python ARTIFACT A — camera_path.py (rigid bezier camera pathing) | cli | `never-exercised` | Headless bpy script. It resets to factory settings (use_empty=True), sets fps, resolution and frame range, and picks the engine: EEVEE (BLENDER_EEVEE_NEXT) by default, or Cycles with device CPU, capped samples and denoising. It optionally imports a GLB and bu… |
| blender_python ARTIFACT B — lowpoly_gen.py (low-poly procedural terrain + scatt… | cli | `never-exercised` | Headless bpy script. It builds deterministic low-poly terrain: a grid, CLOUDS displace, decimate, modifiers applied, flat shading. It applies a flat Principled BSDF material from base_color_rgba (roughness 0.9), scatters seeded icospheres (subdivisions 1, rad… |
| blender_python ARTIFACT C — params sidecar schema (tools/bpy/params.json) | data | `never-exercised` | The single per-task parameter file shared by camera_path.py and lowpoly_gen.py. The .py bodies are never edited per task. It is also the reproducibility record. |
| css_html_ui (skill) | skill | `partial` | Agent-executed front-end construction skill. Every colour, font, size, radius, shadow, spacing step and status meaning in generated markup or DOM mutation must resolve to a key in the ARTIFACT A token dictionary, and CSS may reference only var(--…) properties… |
| css_html_ui ARTIFACT A — Design Token Dictionary | data | `partial` | The 'ABSOLUTE SOURCE OF TRUTH' for studio-surface tokens (HARD MONO, DECISIONS.md D10). control_room.html, hub/styles.css, tools/brush-designer/styles.css and the three brand gate files (visual_identity, typography_system, color_science) are transcribed from… |
| css_html_ui ARTIFACT B — CSS projection (tokens/tokens.css) | data | `partial` | The :root custom-property projection of ARTIFACT A, meant to be 'imported by every page'. It also adds a prefers-reduced-motion override and a global :focus-visible rule. Its header says 'GENERATED FROM design_tokens.json. Edit the JSON, never this file.' |
| css_html_ui ARTIFACT C — DOM Mutation Contract | protocol | `partial` | Rules for router.js and any future JS. JS toggles token-backed classes (c-cyan, c-amber, c-alert, c-dim) or sets custom properties from tokens.css, and never sets literal colours. The status-to-class mapping equals ARTIFACT A semantic.*, with router.js status… |

Full detail: [inventory/skills-local-apps.md](inventory/skills-local-apps.md)

## Infrastructure skills: compute gate, local RAG, UI intelligence

Three "four-part artifact" skill files, meant to be executed by an agent. Each has a YAML routing header, bash prerequisite checks, a numbered execution process and embedded ARTIFACTs.

(1) skills/hardware_compute.skill.md (v2.0, danger_class GATEKEEPER, title "Skill 8/8") is the compute gate.
- ARTIFACT A is the bash probe "hardware probe v4". tools/bootstrap.sh and CI extract it with a regex into the gitignored tools/hw/verify_compute.sh.
- ARTIFACT B is the threshold matrix for 4 workload classes, plus evaluation, null, thermal, host, single_flight and wsl_memory laws and 9 remedies. tools/hw/evaluate_gate.py parses it at runtime.
- ARTIFACT C is the gate token schema at state/compute_gate.json (ttl_seconds 1800, memory_budget_gb, probe_snapshot, consumed_by).
- The skill text itself never names evaluate_gate.py; BOOT.md and README.md document it as the mechanism.
- Code implements the evaluate, single-flight and mint steps. No code implements continuous mode, the dashboard hardware.* writeback, DEGRADED, or phase=blocked on DENY. router.js only reads and renders dashboard hardware.

(2) skills/local_rag_orchestration.skill.md (v2.0, LOCAL_COMPUTE_HEAVY, workload llm_local_sm, "Skill 7/8") runs RAG over local Ollama.
- The endpoint (http://localhost:11434) and tier model come from dashboard.json hardware.local_llm: sm=llama3.1:8b with num_ctx 8192, md=mistral-nemo:12b with num_ctx 4096, embed nomic-embed-text. The tags are marked PROVISIONAL.
- It includes a WSL gateway rewrite, a served-tag check and a gate-token check. Modes are INDEX, QUERY and SYNTHESIS. It strips <think> blocks and evicts the model with keep_alive:0.
- tools/vault_rag.py implements status, index, ask (QUERY) and evict. It has no gate check or consumed_by stamp, no MODE ROUTE, no SYNTHESIS, no flush ledger and no event_log write.
- An index exists: state/rag_index/index.json, 173 chunks, 768 dims, nomic-embed-text, built 2026-09-01T00:22:35Z from C:\Users\utopi\Creative-Writing.

(3) skills/ui_ux_intelligence.skill.md (v1.0, danger_class LOW, "Skill 9/9") drives the vendored offline engine tools/ui-ux-pro-max/scripts/search.py (upstream v2.13.0).
- Commands: the P4 smoke test, domain searches, --design-system with dials, --persist --output-dir for product work only (--force needs operator authorisation), and audit searches with --domain ux and --stack.
- On studio surfaces it may only propose, through the ARTIFACT D four-step operator-approval loop. It must never write context/brand/*.context.md, skills/css_html_ui.skill.md or control_room.html from a search result.
- One ARTIFACT D run is recorded (dashboard event_log, 2026-08-31). The PERSIST path is recorded as "still untested".

State of this checkout:
- Absent: tools/hw/verify_compute.sh, state/compute_gate.json, state/hw_probe_latest.json, .task_scratch/, design-system/ and tokens/design_tokens.json.
- No code anywhere writes .task_scratch/attestation.txt. P1 in every skill therefore fails today.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| hardware_compute (skill) | skill | `partial` | Compute verification and allocation gate (the 'hardware bouncer'). It probes the single 16 GB laptop, checks the probe against per-workload thresholds, and mints or denies a 30-minute gate token that compute-heavy skills must hold. It never launches compute i… |
| verify_compute.sh (hardware_compute ARTIFACT A, 'hardware probe v4') | cli | `generated` | Self-extracting bash probe. It reports shell kind, machine identity, GPU, memory, page-file use, power, thermal and performance headroom, and disk as one JSON object on stdout. The header says it never mutates system state. |
| ARTIFACT B — threshold matrix, laws and remedies | data | `runs-today` | The gate's law table: thresholds per workload class, six laws and remediation text. tools/hw/evaluate_gate.py parses it at runtime, so the skill file stays the single source of truth. |
| Compute gate token (ARTIFACT C, state/compute_gate.json) | protocol | `partial` | File-based authorisation token: one token, one workload. A heavy skill must find a fresh, unconsumed PASS token for its own workload, then write its skill_id into consumed_by. |
| tools/hw/evaluate_gate.py | cli | `runs-today` | Runs hardware_compute's evaluate, single-flight and mint steps. It reads a probe JSON and checks it against ARTIFACT B parsed from the skill file, applying the host, null, thermal and single-flight laws. It prints per-check ok/FAIL lines and remedies, then wr… |
| tools/hw/test_gate.py | cli | `runs-today` | Regression cases that pin evaluate_gate.py verdicts. Nine dry-run cases: - healthy sm → PASS - one readable thermal reading → PASS - both thermal readings null → DENY - battery → DENY for render, PASS for sm - throttling → DENY - md on a loaded 16 GB → DENY -… |
| tools/bootstrap.sh | launcher | `never-exercised` | First-boot script. For this subsystem it performs hardware_compute UNPACK and survey: - extracts ARTIFACT A into tools/hw/verify_compute.sh and syntax-checks it - runs the probe into state/hw_probe_latest.json - runs evaluate_gate --all --dry-run It also chec… |
| local_rag_orchestration (skill) | skill | `partial` | Local RAG over the Obsidian vault using tiered Ollama models on a 16 GB laptop. It: - resolves endpoint and tier from dashboard.json - requires a hardware_compute PASS token - routes the task to INDEX, QUERY or SYNTHESIS - enforces tier-scoped budgets with fl… |
| tools/vault_rag.py | cli | `runs-today` | The executable counterpart of local_rag_orchestration: it connects an Obsidian vault to local Ollama. Subcommands are status, index (chunk and embed into a stdlib JSON index), ask (QUERY mode with tier caps, think stripping, trace archival and eviction) and e… |
| state/rag_index/index.json (RAG vector index) | data | `generated` | Stdlib JSON vector index written by vault_rag.py index and read by ask and status. |
| Ollama local endpoint | service | `runs-today` | Local model server used for embeddings and generation, running on the Windows side of the laptop. |
| local_rag ARTIFACT A — Ollama request payloads | protocol | `partial` | Canonical request bodies for generate, router_call and embed, and the laws that govern them. |
| local_rag ARTIFACT B — routing sub-prompts | data | `partial` | Five zero-shot prompts with described output formats: - ROUTER_SUBPROMPT: final line 'MODE: <INDEX\|QUERY\|SYNTHESIS>' - QUERY_SUBPROMPT: answer only from <RETRIEVAL>, cite [c_NNNN], at most {{max_words}} words, after an 'ANSWER:' line - MAP_SUBPROMPT: ≤300-t… |
| local_rag ARTIFACT C — flush checkpoint ledger (state/rag_flush_ledger.json) | data | `specified-not-implemented` | Per-session ledger of every checkpoint (id, ts, purged, retained, window_pct_after) and the final eviction. Its law: every checkpoint writes an entry here BEFORE purging. |
| ui_ux_intelligence (skill) | skill | `runs-today` | Design-system generation and UX audit over a vendored offline corpus: 79 searchable UI styles (50 active), 192 product palettes and reasoning profiles, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types and 22 stacks. It decides w… |
| tools/ui-ux-pro-max/scripts/search.py | cli | `vendored` | Vendored BM25 search engine over the UI/UX CSV corpus, plus a design-system generator with optional Master + Overrides persistence. |
| tools/ui-ux-pro-max/scripts/validate_data.py | cli | `vendored` | Upstream data-integrity guardrail for the vendored corpus. For each file it checks that the CSV exists, has every configured column, has no duplicate primary keys and has valid decision-rule JSON. It also checks the catalog and provenance JSON files. |
| tools/ui-ux-pro-max/scripts/reasoning_contract.py | library | `vendored` | A closed, non-executable grammar for the design-system decision rules (CONDITION_SIGNALS such as if_dashboard or if_health). It provides parse_decision_rules and apply_decision_rules. |
| tools/ui-ux-pro-max/data (vendored corpus) | data | `vendored` | The CSV corpus and JSON catalogs behind search.py. - 13 domain CSVs: styles, colors, charts, landing, products, ux-guidelines, typography, icons, motion, react-performance, app-interface, google-fonts, ui-reasoning - 22 stack CSVs under stacks/ - catalog-summ… |
| ui_ux ARTIFACT A/B/C — domain routing table, output contract, zero-result contr… | protocol | `runs-today` | A maps each need to a domain with an example query, and lists stacks. B defines the --design-system --json handoff shape that css_html_ui consumes for product work: project_name, category, pattern, style, colors, typography, key_effects, anti_patterns, decisi… |
| ui_ux ARTIFACT D — gate regeneration protocol (studio surfaces) | protocol | `runs-today` | A four-step operator-approval loop for regenerating the three brand gates (visual_identity, typography_system, color_science). Those gates were transcribed from css_html_ui ARTIFACT A, and this skill is their declared regeneration path (DECISIONS.md § D9). |
| tools/verify_system.py | cli | `runs-today` | Protocol integrity checker. For this subsystem it: - checks each skill's mandatory_context and host_kinds headers, and scans fenced code for macOS-only invocations (all three skills) - runs check_extracted_probe (extracted verify_compute.sh against ARTIFACT A… |
| .github/workflows/verify.yml (subsystem-relevant steps) | ci | `runs-today` | CI on push to main, pull_request and workflow_dispatch (ubuntu-latest, Python 3.11). Exercises protocol integrity, gate logic, probe extraction and execution, evaluator verdicts, and vault_rag help and core logic without Ollama. |

Full detail: [inventory/skills-infra.md](inventory/skills-infra.md)

## Hardware gate toolchain

Hardware gating toolchain for "Studio Headless OS", which runs on one laptop (Lenovo Yoga Book 9i, 16 GB soldered shared memory, Intel integrated graphics, no CUDA). The single source of truth is skills/hardware_compute.skill.md (v2.0, danger_class GATEKEEPER). It embeds three artifacts: ARTIFACT A, a bash probe ("hardware probe v4"); ARTIFACT B, a JSON threshold matrix with laws and remedies; and ARTIFACT C, the gate token schema.

tools/bootstrap.sh does the first boot:
- detects the shell: MINGW/MSYS/CYGWIN is windows; Linux with WSL_DISTRO_NAME set or "microsoft" in /proc/version is wsl; other Linux is linux; Darwin (macos) and anything unknown are refused through HARD_FAIL.
- checks hard prerequisites (python3, curl, awk, df, grep, plus PowerShell on windows/wsl) and soft ones (Ollama, COM ProgIDs, Blender).
- extracts ARTIFACT A with the regex `### ARTIFACT A.*?\n```bash\n(.*?)\n```` into the gitignored tools/hw/verify_compute.sh, then checks it with bash -n.
- runs the probe with "generic" into state/hw_probe_latest.json.
- surveys every workload class with evaluate_gate.py --all --dry-run. It never mints a token.

tools/hw/evaluate_gate.py parses ARTIFACT B out of the skill file at run time with the regex `### ARTIFACT B.*?\n```json\n(.*?)\n```` followed by json.loads. It applies host_law, null_law, thermal_law and single_flight_law. Unless --dry-run is given, it always writes state/compute_gate.json: either a PASS token (ttl 1800 s, memory_budget_gb taken from probe dynamic_claim_limit_gb, optional consumed_by) or a DENY record. Exit codes: 0 PASS, 1 DENY, 2 could not evaluate.

tools/hw/test_gate.py pins 10 verdicts: 9 dry-run cases plus 1 single-flight case, which temporarily overwrites the real state/compute_gate.json and then restores or deletes it. tools/reconcile_models.py compares dashboard.json hardware.local_llm.tiers and embed_model against Ollama /api/tags. With --write it rewrites the tier model tags and _tiers_note. Exit codes: 0 match, 1 drift (also after a successful --write), 2 unreachable.

Token lifecycle:
- Mint: evaluate_gate.py <class>.
- TTL: 1800 s, counted from mint time, not probe time. A stale probe only prints a warning.
- Consume: the consuming skill writes consumed_by. This is specified in the blender_python and local_rag_orchestration markdown only. No script does it, and tools/vault_rag.py (the executable form of local_rag_orchestration) has no token check.
- Single flight: enforced only inside evaluate_gate at mint time. A denied non-dry-run request overwrites the file with a DENY record, including one that replaces another workload's live PASS token.

CI (.github/workflows/verify.yml) runs test_gate, extracts ARTIFACT A and checks it with bash -n, runs the probe and the evaluator on ubuntu-latest, and runs an encoding check that covers reconcile_models only through --help.

Known unknowns, per BOOT.md and DECISIONS.md: the Windows and WSL branches of the probe (every psq PowerShell query), the WSL gateway rewrite, the wslpath handoff and bootstrap's COM-registration check have never run on the target laptop. reconcile_models has only run against a stub endpoint.

On disk now: state/ holds only rag_index/ and vault_manifest.json. state/hw_probe_latest.json, state/compute_gate.json, tools/hw/verify_compute.sh and .task_scratch/ are all absent.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| bootstrap.sh | launcher | `never-exercised` | First-boot and re-probe script. It identifies the shell (host kind), checks hard and soft prerequisites, checks Ollama reachability (retargeting to the WSL gateway when needed), checks Adobe COM registrations and Blender, extracts the probe from ARTIFACT A, r… |
| verify_compute.sh (ARTIFACT A hardware probe) | cli | `generated` | Read-only hardware probe that emits one JSON object describing the host/shell kind, machine identity, GPU, memory (with a dynamic claim limit), power, thermal readings and disk headroom. Its source of truth is the ```bash block under '### ARTIFACT A' in the s… |
| evaluate_gate.py | cli | `runs-today` | Turns a probe JSON into a PASS/DENY verdict per workload class, using thresholds parsed at run time from ARTIFACT B in skills/hardware_compute.skill.md. It enforces host_law, null_law, thermal_law and single_flight_law, and writes the gate token (PASS) or a D… |
| test_gate.py | cli | `runs-today` | Regression test that pins evaluate_gate.py verdicts against the current ARTIFACT B. It covers: AC required for sustained work, throttling denied, one readable thermal reading enough, both unreadable denied, the md tier denied under memory pressure, a discrete… |
| reconcile_models.py | cli | `partial` | Compares dashboard.json hardware.local_llm.tiers (sm/md model tags) and embed_model with what Ollama serves at /api/tags and reports drift. With --write it rewrites the tier model tags in dashboard.json to in-range candidates. |
| hardware_compute skill | skill | `partial` | Agent-facing 'hardware bouncer' skill (v2.0, danger_class GATEKEEPER). It specifies prerequisites P1-P4 and the execution process (unpack, probe, evaluate, single-flight, mint/deny, dashboard flush, handback, continuous mode). It embeds ARTIFACT A (probe), AR… |
| ARTIFACT B threshold matrix | data | `runs-today` | JSON law table parsed at run time by evaluate_gate.py: per-class thresholds, the laws and the remedies. |
| compute gate token protocol (ARTIFACT C) | protocol | `never-exercised` | Single-slot file token that authorises one heavy local job, covering mint, TTL, consume and single-flight. |
| verify.yml CI (gate steps) | ci | `runs-today` | GitHub Actions job 'verify' that runs on push to main, pull_request and workflow_dispatch (ubuntu-latest, Python 3.11) and runs the protocol and gate checks. |
| verify_system.py (probe drift and portability checks) | cli | `runs-today` | Protocol integrity checker, outside the core hw-gate scope. Two checks are relevant here. check_extracted_probe fails if tools/hw/verify_compute.sh differs from ARTIFACT A; it is skipped when the file is absent. check_host_portability fails if a skill declare… |
| BOOT.md runbook | doc | `runs-today` | First-boot runbook. It covers shell choice (Git Bash vs WSL2), prerequisites, Ollama setup including WSL networking, what bootstrap does, gate usage, why the system still says BLOCKED, and known unknowns. |

Full detail: [inventory/hw-gate.md](inventory/hw-gate.md)

## Vault and its indexers

The vault-rag subsystem has three parts. (1) An Obsidian vault at vault/ that follows the Content MD spec in vault/SCHEMA.md. It also holds a template, a worked example and a migration gap analysis. (2) Two stdlib-only Python indexers that can read any vault directory. tools/vault_rag.py has the subcommands status, index, ask and evict, plus a global --endpoint flag that must come before the subcommand. It chunks notes (800 tokens with 120 overlap, at chars/4), embeds them through local Ollama into a single JSON index at state/rag_index/index.json, and answers using only the retrieved chunks, citing [c_NNNN] ids. tools/vault_manifest.py (flags --vault and --out) writes state/vault_manifest.json, a one-row-per-note index with no embeddings that includes each note's full body. The hub Library tab reads it, and the hub's separate browser-side Ask index is built from it. (3) OBSIDIAN.md describes two connections. A is an Obsidian community plugin talking to Ollama: Copilot, Smart Connections or Text Generator are listed and none is chosen, and it needs OLLAMA_ORIGINS=app://obsidian.md. B is vault_rag.py. WHICH VAULT THE STATE FILES CAME FROM: neither generated state file was built from this repo's vault/. Both headers record vault C:\Users\utopi\Creative-Writing, the sibling 'Living Archive'. The manifest (built 2026-09-01T04:30:49Z, 413,578 bytes) has count 64: 63 works plus Creative-Writing's own root OBSIDIAN.md with kind 'other'. It is large because every row embeds the full note body. The RAG index (built 2026-09-01T00:22:35Z, 1,183,899 bytes, one JSON line) has embed_model nomic-embed-text, partial=false, 173 chunks (c_0000..c_0172) from 65 files including 00_INDEX.md, and dims 768. Its chunk paths use Windows backslashes, so it was built by Windows-native Python. NEW FINDINGS: C:\Users\utopi\Creative-Writing no longer exists on disk. Both state files are therefore orphaned and cannot be rebuilt from their source, and `vault_rag.py status` would print 'vault path no longer exists'. The only .obsidian/ folder is at the REPO ROOT; vault/ has none. So Obsidian has been pointed at Creative-Headquarters/, not vault/ as the docs instruct, and the .gitignore Obsidian rules, which are scoped to vault/.obsidian/, do not cover it. By both tools' file rules, this repo's vault/ holds exactly one corpus note: vault/studio-os/ui/ui-ux-intelligence-integration.md. The Creative-Writing to Content MD migration exists only as an assessment (GAP-ANALYSIS.md, now partly stale). There is no migration script and no files have been migrated. vault/README.md says 'the archive indexes these files', but no code under archive/ references the vault.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| vault_rag.py | cli | `runs-today` | Local RAG over an Obsidian vault using Ollama. It chunks and embeds every eligible note into a stdlib JSON vector index, then answers questions using only the retrieved chunks, with chunk-id citations. It is the executable form of skills/local_rag_orchestrati… |
| vault_manifest.py | cli | `runs-today` | Writes state/vault_manifest.json, a small one-row-per-note index of a vault with no embeddings, for the static hub UI (hub/index.html Library tab; the Ask tab's browser-side index is built from it). Each row carries the note's full body so the browser never h… |
| state/rag_index/index.json (RAG vector index) | data | `generated` | The single on-disk vector index that vault_rag.py index writes and ask/status read. It holds one vault at a time. |
| state/vault_manifest.json (hub note manifest) | data | `generated` | Browser-loadable note index that hub/app.js fetches for the Library tab. The hub Ask tab chunks and embeds the notes' bodies from it into its own browser-side index. |
| state/rag_traces/ (think-trace archive) | data | `never-exercised` | Audit archive for <think> blocks stripped from ask answers: one timestamped .txt per answer that contained a trace. |
| Obsidian vault (vault/) | data | `partial` | The studio's source of truth for creative work: plain-markdown Content MDs meant to be edited in Obsidian. The indexers only read it. |
| Content MD schema | protocol | `partial` | The Content MD spec: the durable, cold-readable record of one made thing (character, design, audio piece, shot, brush...). It is the unit of memory; resuming work means reading it cold. |
| Content MD Obsidian template | data | `runs-today` | Skeleton for a new Content MD, for Obsidian core Templates or Templater. It pre-fills the frontmatter and all eight sections in schema order. |
| Worked example Content MD (dry stipple brush) | doc | `runs-today` | Reference example of a fully filled Content MD (kind brush, status in-progress, project [[Brush Kit v1]], skills [brush_designer]) showing every section, including a Method block of Procreate brush parameters. |
| Creative-Writing -> Vault migration (GAP-ANALYSIS) | doc | `specified-not-implemented` | Assessment of what separates the 63 works in groot99-droid/Creative-Writing from routable Content MDs, and which decisions the author must make before migrating. |
| Obsidian -> Ollama plugin connection (connection A) | protocol | `specified-not-implemented` | In-app writing assistance: an Obsidian community plugin calls the local Ollama server to chat in the sidebar, rewrite a selection or continue a paragraph, and it sees the open note. OBSIDIAN.md says to set it up first. |
| Repo-root Obsidian vault state (.obsidian/ and stray note) | data | `generated` | On-disk evidence of how Obsidian is actually being used: the repo root, not vault/, holds the Obsidian vault configuration, plus an empty note named after an unresolved wikilink. |
| CI: vault_rag smoke and core-logic test | ci | `partial` | Checks that vault_rag.py parses --help with UTF-8-explicit I/O, and unit-checks chunking, the vector pack/unpack round trip and frontmatter stripping without an Ollama server. |

Full detail: [inventory/vault-rag.md](inventory/vault-rag.md)

## Hub and launcher

THE HUB (hub/index.html, title 'THE HUB — Studio Headless OS') is a static browser app with no build step and five tabs: Library, Ask, Designer Pro, Brushes and Pipeline. It needs an HTTP origin because it fetch()es '../dashboard.json', '../state/vault_manifest.json' and '../tools/ui-ux-pro-max/data/<file>.csv'.

It calls a local Ollama server directly (default http://localhost:11434) through hub/ollama.js (HubOllama), using:
- GET /api/tags (6 s timeout)
- POST /api/embeddings {model, prompt, keep_alive:'5m'}
- POST /api/generate {stream:false, keep_alive:'5m', options}
- POST /api/generate {model, keep_alive:0} to evict a model

The hub's only persisted state is browser localStorage: hub:tab, hub:endpoint, hub:tier, hub:overview:<content_hash> and hub:index:v1. It writes no files and starts no routed tasks.

Tabs:
- **Library** renders cards from the manifest. It writes an AI overview only when the user clicks.
- **Ask** is RAG done in the browser: chunk, embed, cosine top-k, fit to a budget, generate with chunk citations. It mirrors the constants in tools/vault_rag.py.
- **Designer Pro** does CSV search and conflict checks without a model. Its optional Ollama 'blend' always uses the sm tier. It fetches styles.csv at page load, whichever tab is showing.
- **Brushes** only shows tools/brush-designer/index.html in an iframe.
- **Pipeline** is a hard-coded preview of five stations. It does not fetch, poll or act. The live rail is control_room.html + router.js, which polls dashboard.json every 5000 ms. Nothing writes dashboard.json.pipeline. tools/verify_system.py (run in CI) sets the constraints any writer of that block must meet.

Launchers:
- **tools/launcher/Start-Hub.ps1** serves the whole repo root. It probes 127.0.0.1:8765-8774 by default, reuses a running hub (found by 'Studio Headless OS' in /hub/index.html), and otherwise spawns `python.exe -m http.server <port> --bind 127.0.0.1 --directory <root>`. Params: -Port, -PortSearch, -Stop, -NoBrowser.
- **tools/launcher/Install-Shortcut.ps1** writes tools/launcher/hub.ico and 'Studio Hub.lnk' to the Desktop folder and to Start Menu\Programs. Only the Programs copy gets the CTRL+ALT+H hotkey. Params: -Name, -Hotkey, -NoHotkey. Both .lnk files exist on this machine: C:/Users/utopi/OneDrive/Desktop and %APPDATA%/Microsoft/Windows/Start Menu/Programs.

Port disagreement:
- Start-Hub.ps1 and tools/launcher/README.md use 8765 (range 8765-8774).
- .claude/launch.json and the root README.md use 8347.
- The file:// note in hub/index.html says http://localhost:8000/hub/.

These are three separate browser origins, each with its own localStorage.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| THE HUB (hub web app) | web-app | `runs-today` | Static browser front-end over the studio repo: five tabs (Library, Ask, Designer Pro, Brushes, Pipeline), plus a header chip and a <dialog> for the local Ollama connection. |
| HubOllama (hub/ollama.js) | library | `runs-today` | Ollama client and RAG helpers that run in the browser, shared by the hub tabs. It mirrors tools/vault_rag.py's constants, tier limits and 'answer only from the retrieval block' prompt. |
| Library tab | web-app | `runs-today` | One card per note in the last-indexed vault, built from state/vault_manifest.json. Each card shows the authored overview, plus an AI overview the local model writes only when the user clicks. |
| Ask tab | web-app | `runs-today` | Retrieval-augmented Q&A over the manifest's notes, run in the browser. It keeps an embedding index in localStorage, retrieves chunks by cosine similarity, and has the tier model answer only from those chunks with chunk-id citations. |
| Designer Pro tab | web-app | `runs-today` | Style generation and mixing over the vendored ui-ux-pro-max CSV corpus. Search and conflict checks run without a model and pick 'ingredients'. An optional local-model blend then proposes one design direction from those rows only. |
| Brushes tab | web-app | `runs-today` | Shows the standalone Procreate brush designer in an iframe. The designer itself has shape and grain generators, stroke preview and .brush/.brushset export. |
| Pipeline tab | web-app | `stub` | A static preview of the pipeline 'transit rail' layout that is not wired to anything. It is the placeholder for a live pipeline view and the natural place to connect an external Pipelines tool. |
| Start-Hub.ps1 | launcher | `runs-today` | One-press launcher. It starts, or reuses, a Python static server bound to 127.0.0.1 and rooted at the repo root, then opens THE HUB in the default browser. It can also stop that background server. |
| Install-Shortcut.ps1 | cli | `runs-today` | Generates the hub icon from the HARD MONO palette and writes Desktop and Start Menu .lnk shortcuts that run Start-Hub.ps1 in a hidden window. The Start Menu copy carries a global hotkey. |
| Studio Hub.lnk shortcuts (generated) | launcher | `generated` | The daily entry point: a click or Ctrl+Alt+H runs Start-Hub.ps1 in a hidden window. |
| hub-static-server (.claude/launch.json) | launcher | `runs-today` | Claude Code preview launch configuration that serves files over HTTP so the hub can fetch its data files. |

Full detail: [inventory/hub-launcher.md](inventory/hub-launcher.md)

## Brush designer

tools/brush-designer/ is a browser-only single-page app titled "Procreate Brush Designer". It has no build step, no CLI and no server of its own. It holds a 52-parameter brush state, generates a 512x512 shape texture and a 1024x1024 grain texture on canvas, and previews strokes on a sheet you can draw on. It has five exports, and each one reaches disk only as a browser download: Procreate .brush, Procreate .brushset (the UI only ever packs the current brush), GIMP/Krita .gbr, a "Universal Kit" zip (ink/mask PNGs, a .gbr, stroke-preview.png and a markdown recipe for Photoshop, Affinity, Clip Studio, Krita, GIMP and others), and a "Download Source" zip.

Reading export/PlistEncoder.js shows a serious problem that was not run to confirm. For arrays and dicts, addObject reserves an index before encoding the children but pushes the container after them. Every container's object reference (including the trailer's root index) therefore points at the wrong object. The Brush.archive and brushset.plist bytes are most likely not valid bplists.

The AI Assist tab talks to local Ollama (default http://localhost:11434). It sends GET /api/tags, then a non-streaming POST /api/generate with model llama3.1:8b (tier sm) or mistral-nemo:12b (tier md), then POST /api/generate {keep_alive:0} to unload the model. The prompt carries the current values of the 43 exportable brush* tunables and asks for a JSON patch {changes, summary}. Every key is validated and clamped, and the result is applied as one undoable step. Name, author, notes, shapeSource, grainSource and the pressure curves are rejected.

Presets live in localStorage (brushPresets) and IndexedDB (ProcreateBrushDesigner v1 / presetImages). Five built-ins are seeded once, users can add their own, and there is no delete UI. The only code CDN dependency is fflate@0.8.2 (UMD global) from cdn.jsdelivr.net; styles.css also @imports JetBrains Mono from Google Fonts. The app needs an HTTP origin: .claude/launch.json 'hub-static-server' (python3 -m http.server 8347) or tools/launcher/Start-Hub.ps1 (loopback, ports 8765-8774). The hub's Brushes tab embeds it through a same-origin iframe (../tools/brush-designer/index.html) and nothing else; the only shared state is the localStorage keys hub:endpoint and hub:tier.

Module map (exports -> class):
- DOM-free (no browser API references):
  - editor/BrushState.js: DEFAULT_BRUSH_STATE, BRUSH_PROPERTY_RANGES, BLENDING_MODES, BrushState, default BrushState.
  - editor/HistoryManager.js: HistoryManager.
  - export/PlistEncoder.js: PlistEncoder, encodePlist.
  - export/BrushArchive.js: BrushArchive.
- Near-core, fetch plus localStorage only in its getters/setters: ai/OllamaAssist.js exports the OllamaAssist object.
- Needs a Canvas 2D implementation (each calls document.createElement('canvas')):
  - generators/ShapeGenerator.js: ShapeGenerators, generateShape, getShapeGeneratorNames.
  - generators/GrainGenerator.js: GrainGenerators, generateGrain, getGrainGeneratorNames.
  - export/GbrEncoder.js: GbrEncoder.
- Canvas plus toBlob plus the global fflate (and URL/anchor for the download):
  - export/BrushExporter.js: BrushExporter.
  - export/UniversalKitExporter.js: UniversalKitExporter.
- Browser-bound UI:
  - app.js: default ProcreateBrushDesigner, which also sets window.app.
  - editor/PresetLibrary.js: localStorage, IndexedDB and canvas.
  - panels/PanelComponents.js: BasePanel plus 10 panel classes; the default export is an object of the 10.
  - panels/AIAssistPanel.js.
  - preview/StrokeRenderer.js.
  - preview/StrokeInput.js.
  - ui/Slider.js, ui/CurveEditor.js, ui/Section.js (Section, createSectionToolbar), ui/Modal.js, ui/Toast.js (Toast, getToast).

Nothing routes to it. DECISIONS.md D2 specifies a headless adapter plus skills/brush_designer.skill.md; neither exists. skills/ holds 9 files, none of them brush_designer. Unimplemented or stubbed: .brush/.brushset import, the Color Dynamics tab, custom texture upload (CSS only), tilt, and any way to change the generator seed. README calls it '~4,000 lines'; the files are about 5,700 lines of JS and HTML, or 7,129 counting styles.css. Git working-tree state (untracked or modified files) could not be checked with the allowed tools. The root wet-stipple-brush.md exists and is empty.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| Procreate Brush Designer (web app shell) | web-app | `runs-today` | Manual browser tool for editing a 52-parameter brush plus generated shape and grain textures. You test the brush on a drawable preview sheet and download it in Procreate, GIMP/Krita or multi-app formats. |
| BrushState (parameter model) | library | `runs-today` | The single source of truth for brush configuration: defaults, numeric ranges, the blend-mode table, and an observable state object. |
| HistoryManager (undo/redo) | library | `runs-today` | Keeps a 50-step undo/redo stack of BrushState snapshots. |
| PresetLibrary (+ Presets sidebar) | library | `runs-today` | Stores and loads named brush presets. Settings and a thumbnail go to localStorage; shape/grain PNG data URLs go to IndexedDB. |
| ShapeGenerator | library | `runs-today` | Procedurally draws grayscale brush-tip shape textures (white = mark, black = transparent). |
| GrainGenerator | library | `runs-today` | Procedurally draws grayscale grain (paper/texture) images using Perlin fBm and seeded random strokes. |
| PlistEncoder (bplist00) | library | `partial` | Pure-JS binary property list (bplist00) encoder used for Brush.archive and brushset.plist. |
| BrushArchive (Brush.archive encoder) | library | `runs-today` | Builds the NSKeyedArchiver-shaped MCBrush object from brush state and encodes it as a binary plist, which becomes the Brush.archive entry of a .brush. |
| Export .brush (Procreate) | library | `runs-today` | Packages one brush as a Procreate .brush ZIP. |
| Export .brushset (Procreate) | library | `partial` | Packages one or more brushes as a Procreate .brushset ZIP. |
| Export .gbr (GIMP / Krita) | library | `runs-today` | Writes the shape texture as a GIMP brush version 2 (.gbr) grayscale file, which Krita can also import as a brush tip. |
| Export Universal Kit (.zip) | library | `runs-today` | Multi-app kit for brush engines whose native formats are undocumented: image-based brush tips plus a recipe. |
| Export: Download Source | web-app | `partial` | Zips the app's own source files, fetched over HTTP, for download. |
| Import .brush / .brushset | web-app | `stub` | Intended to import an existing Procreate brush. |
| OllamaAssist (local-model JSON-patch client) | protocol | `runs-today` | Client for the local Ollama REST API, plus the prompt and validation contract for AI edits to brush parameters. |
| AI Assist tab | web-app | `runs-today` | Conversational editing: you describe a change, a local model proposes a validated parameter patch, and it is applied as one undoable step. |
| Stroke Path tab | web-app | `runs-today` | Sliders for spacing, smoothing and jitter. |
| Taper tab | web-app | `runs-today` | Taper size and opacity controls. |
| Shape tab | web-app | `runs-today` | Picks the shape generator and sets stamp placement and orientation. |
| Grain tab | web-app | `runs-today` | Picks the grain generator and sets grain transform, depth and behaviour. |
| Dynamics tab | web-app | `runs-today` | Size and opacity ranges, and bleed. |
| Pencil tab (Apple Pencil pressure curves) | web-app | `partial` | Bezier pressure-to-size and pressure-to-opacity response curves. |
| Wet Mix tab | web-app | `runs-today` | Wet-mix parameters. |
| Color Dynamics tab | web-app | `stub` | Placeholder for Procreate's colour dynamics. |
| Rendering tab | web-app | `runs-today` | Blend mode selection. |
| About This Brush tab | web-app | `runs-today` | Author and notes metadata, a read-only spec sheet, and reset. |
| Stroke preview / test sheet | web-app | `runs-today` | Canvas approximation of the brush engine. It draws sample S-curve strokes at light, medium and heavy pressure, and gives you a surface to draw on with pen pressure or a speed-based substitute. |
| UI component kit | library | `runs-today` | DOM widgets used by the panels and the app shell. |
| Hub Brushes tab (embedding) | web-app | `runs-today` | Embeds the brush designer inside THE HUB as an iframe. |
| Start-Hub.ps1 launcher | launcher | `runs-today` | Serves the repo root on loopback and opens the hub. This is the documented one-press way to reach the embedded brush designer. |
| hub-static-server launch config | launcher | `runs-today` | Claude preview/launch configuration that serves the repo root, from which both /hub/ and /tools/brush-designer/index.html load. |
| brush_designer skill + headless adapter | skill | `specified-not-implemented` | Planned programmatic API over the DOM-free core, so the Router and agents can run the brush designer and emit a Content MD. |
| Worked-example Content MD: Dry Stipple brush | data | `never-exercised` | Worked example of a vault Content MD with kind: brush that records brush_designer work. |
| wet-stipple-brush.md (root) | data | `stub` | Presumably the target of the [[wet-stipple-brush]] wikilink in the example note. |

Full detail: [inventory/brush-designer.md](inventory/brush-designer.md)

## Agents, brand gates, domain libraries

Three kinds of markdown file make up this subsystem. None is executable, and no code reads the content of any of them.

(1) agents/ holds nine Claude Code sub-agent persona files: business-analyst, code-reviewer, content-strategist, debugger, documentation-writer, frontend-developer, project-manager, test-expert and ux-consultant. README.md says they were vendored from the "Claude-Code" repo. Each frontmatter holds only `name` and `description`; no file declares `tools` or `model`. README.md says to install them by copying into ~/.claude/agents/ and to invoke them with `claude --agent <name>`. Nothing in the repo confirms that flag exists. They are generic software-engineering personas. They are not registered in dashboard.json and are not in the Router.md §3 routing table. They never mention brand gates, the vault or Content MDs. Nothing in the repo invokes them. Router.md §1 and README.md list them as "9 sub-executor definitions", and ~/.claude/agents/ does not exist on this machine.

(2) context/brand/ is for the ten brand-gate constants that Router.md §3 makes mandatory or conditional for the nine skills. Three are authored at L0: visual_identity, typography_system and color_science. They were transcribed from skills/css_html_ui.skill.md ARTIFACT A (DECISIONS.md D9) and rewritten for HARD MONO on 2026-09-01 (D10). Two of them declare their own gaps:
- visual_identity §7: generated-imagery motifs, framing and texture.
- color_science §5: working space, LUTs and grading.

The other seven are not on disk: motion_language, sound_identity, brand_voice, narrative_continuity, render_philosophy, pipeline_ethics and memory_discipline. Router.md §5 resolves an unauthored gate in three steps:
- L1: recall from a vault Content MD whose `context_brand` names the gate (confidence 0.9).
- L2: derive from at least 3 notes (confidence 0.3-0.8).
- L3: nothing found. Manual and supervised modes ask the operator; autonomous mode parks the task.

dashboard.json sets the mode to autonomous. Today the vault holds one real Content MD, whose context_brand is [visual_identity, typography_system, color_science]. So none of the seven can resolve at L1 or L2, and all seven land at L3. context/brand/README.md defines the contract: which skills each gate gates, what each must answer, and the format. Nothing implements the ladder in code. README.md says "no code implements" the Router, and router.js reports only whether a gate is authored at L0.

(3) context/domain/ holds ten general reference libraries, each 216 lines with the same structure:
- §1 is a routing glossary: ten categories A-J with ten "Subcategory Triggers" each. It points to "## 2.X", but the headings on disk are "### 2.X".
- §2.A-2.J hold ten numbered nodes each (2.X.1-2.X.10).
- §3 "EXECUTION VARIABLES (The Hand-off Payload)" defines primary_domain_bias, system_exclusion_tokens and hardware_render_overrides.

§3 says the payload is "passed to corresponding `.skill.md` scripts", but no skill file names any library or payload key. The libraries are retrieval material only. Router.md §3 forbids a library from satisfying a brand gate. router.js enforces this by resolving only to context/brand/, and tools/verify_system.py check_domain_libraries enforces it for the dashboard registry. vault/SCHEMA.md lists `context_domain` as an optional frontmatter field without defining it. One real note uses it: vault/studio-os/ui/ui-ux-intelligence-integration.md, with [typography_ad_arts].

Machine checks: tools/verify_system.py runs in CI (.github/workflows/verify.yml) and exits 1 on any failure and 0 otherwise. The checks that touch this subsystem are:
- check_brand_gates: authored flag against disk, the path pattern, and gates_skills against registered skills.
- check_domain_libraries: declared libraries exist; none doubles as a gate.
- check_skill_headers: mandatory_context names only declared gates.
- check_context_loaded: only authored gates may be claimed as loaded.
- check_router_js and check_router_md: gate roles are mentioned; router.js builds no context/domain/ path.
- check_palette_parity: compares only 7 hex tokens between ARTIFACT A and control_room.html.

The §0 provenance of visual_identity and typography_system says they are "machine-enforced" by check_palette_parity. That overstates it: no typography value and no line/ink/ink-dim/spacing/radius/motion/focus value is checked, and the gate files themselves are never read. Several documents are stale about gate state: BOOT.md, README.md lines 119-121 and 158-159, vault/_migration/GAP-ANALYSIS.md §6, and the check_brand_gates docstring. dashboard.json matches the files on disk.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| business-analyst | agent | `vendored` | Claude Code sub-agent persona: a technical business analyst who turns stakeholder goals into requirements, user stories with acceptance criteria, process maps, feasibility/impact assessments and decision documents. |
| code-reviewer | agent | `vendored` | Claude Code sub-agent persona: a senior code reviewer checking a change for correctness, security, design, readability, performance and testing. |
| content-strategist | agent | `vendored` | Claude Code sub-agent persona for messaging and positioning, content architecture, voice and tone, copy and microcopy, and content planning. |
| debugger | agent | `vendored` | Claude Code sub-agent persona for systematic debugging: reproduce, isolate, understand, fix the root cause, verify, and add a regression test. |
| documentation-writer | agent | `vendored` | Claude Code sub-agent persona for READMEs, API docs, guides and tutorials, architecture docs, and code comments or docstrings. |
| frontend-developer | agent | `vendored` | Claude Code sub-agent persona for clean, performant, accessible UI code (React/Vue/Svelte), state management, performance and accessibility. |
| project-manager | agent | `vendored` | Claude Code sub-agent persona for task breakdown, scope control, risk and dependency identification, status updates and planning. |
| test-expert | agent | `vendored` | Claude Code sub-agent persona for writing tests, reviewing existing tests for false confidence and brittleness, and advising on test strategy. |
| ux-consultant | agent | `vendored` | Claude Code sub-agent persona for reviewing UI components, flows and designs for accessibility, information architecture, interaction design and consistency. |
| visual_identity (brand gate) | context | `partial` | L0-authored brand constant for interface identity: dark-ground instrumentation, flat grounds, hard rules, sharp corners, a closed four-accent state vocabulary, and elevation by inversion. An agent following Router.md loads it in full before running any skill… |
| typography_system (brand gate) | context | `runs-today` | L0-authored brand constant for the studio's own surfaces: one family (JetBrains Mono) in two weights plus a single 500 step, a fixed six-step size scale, tracking values, and a hierarchy carried by weight, size, tracking and case (never colour). |
| color_science (brand gate) | context | `partial` | L0-authored brand constant: the complete 10-value studio palette, the semantic binding of the four accents to states, and three measured contrast floors. It explicitly declares that it is not a colour-managed pipeline. |
| unauthored brand gates (7) | context | `specified-not-implemented` | Seven brand constants that Router.md §3 names as mandatory or conditional gates but that do not exist on disk (glob confirms; dashboard.json authored:false). Until they are authored, each resolves through the Router §5 vault ladder (L1 recall / L2 derivation)… |
| brand-gate contract (context/brand/README.md) | doc | `partial` | Explains why context/brand/ exists and how it differs from context/domain/. Lists the ten required gate files (which skills each gates and what each must answer), the file format, and how routes run while gates are unauthored. |
| ai_creative_strategies_context (domain library) | context | `partial` | General reference library on AI/LLM creative strategy: latent space, context windows, multi-model orchestration, prompting, hallucination, fine-tuning, evaluation, handoffs, intent alignment and agentic behaviour. Retrieval material only; never a brand gate. |
| cinematic_videography_context (domain library) | context | `partial` | General reference library on cinematography: optics, sensors, lighting, colour science, blocking, camera movement, editing, auteur method, VFX, texture and noise. Retrieval material only. |
| classical_illustration_context (domain library) | context | `partial` | General reference library on classical illustration: composition math, light and value, colour systems, anatomy, perspective, edges, traditional media, materials, line and atmospheric perspective. Retrieval material only. |
| creative_analytical_writing_context (domain library) | context | `partial` | General reference library on narrative and analytical writing: macro structure, scene beats, character, dialogue, prose cadence, rhetoric, exposition, screenplay/Fountain format, emotional resonance and editing. Retrieval material only. |
| digital_3d_motion_context (domain library) | context | `partial` | General reference library on 3D and motion: PBR shading, topology, rigging, simulation, animation curves, virtual cameras, GI lighting, modelling workflows, compositing passes and real-time asset optimisation. Retrieval material only. |
| multimedia_fusion_context (domain library) | context | `partial` | General reference library on transmedia and interactive-media engineering: story distribution, interoperability, containers and codecs, real-time DOM logic, streaming, multi-sensory UX, state engines, cross-hardware deployment, telemetry and build pipelines.… |
| music_ambience_context (domain library) | context | `partial` | General reference library on music and sound: harmony, rhythm, psychoacoustics, spatial audio, synthesis, acoustic instruments, foley and ambience, arrangement, leitmotif, and mixing and mastering. Retrieval material only. |
| social_media_marketing_context (domain library) | context | `partial` | General reference library on social media marketing: algorithms, consumer psychology, funnels, hooks and editing, analytics, community, copywriting, trends, influencers and the content lifecycle. Retrieval material only. |
| typography_ad_arts_context (domain library) | context | `partial` | General reference library on typography and advertising arts: grids, micro-typography, hierarchy, brand psychology, ad layout, signage, print production, interface ergonomics, type history and WCAG legibility. Retrieval material only. |
| world_building_context (domain library) | context | `partial` | General reference library on worldbuilding: geopolitics, socio-economics, resources, anthropology, history and continuity, architecture, biomes, technology grounding, conlangs and factions. Retrieval material only. |

Full detail: [inventory/agents-context.md](inventory/agents-context.md)

## ui-ux-pro-max, and how it became plugins/ui-design

This tool is the only Creative-Headquarters (CHQ) tool that has already been carried into Pipelines, so it is the model for moving the others. CHQ keeps a vendored copy of upstream nextlevelbuilder/ui-ux-pro-max-skill v2.13.0 (MIT) in tools/ui-ux-pro-max/. The copy has 44 payload files: 5 scripts (search.py, core.py, design_system.py, reasoning_contract.py, validate_data.py) and 39 data files (13 CSVs, 4 JSONs and 22 stack CSVs). VENDOR.md records a payload sha256 and forbids local edits, but nothing checks the hash. On disk the scripts folder also holds 3 gitignored .pyc files. Around the copy, CHQ has:
- a routed skill, skills/ui_ux_intelligence.skill.md, which Router.md, router.js and dashboard.json reach through the dual-trigger intercept;
- three brand gates, with ARTIFACT D (a four-step loop that needs operator approval);
- the hub Designer Pro tab, which fetches 9 of the CSVs over HTTP and blends them with local Ollama.

In Pipelines the tool is the Claude Code plugin plugins/ui-design (v0.1.0, marked Unreleased; plugin.json names author groot99-droid). The payload now sits in plugins/ui-design/catalog/{data,scripts}. All 39 data files and all 5 original scripts keep their names; nothing was dropped or renamed.

How the code changed:
- core.py: the gsap output_cols gain Spring Params, CSS Snippet and Reduced Motion, and UNTRUNCATED_COLS gains CSS Snippet. This accounts for the full 65-byte size difference.
- design_system.py: adds a 'contrast' key built from contrast.py, the dtcg and shadcn formats, and writes tokens.json and theme.css on persist. Its ascii, markdown and MASTER.md formatters still do not show the three new motion columns.
- search.py: adds --diagnostics, --strict-contrast and -f dtcg|shadcn.
- validate_data.py: the only difference found is the docstring word 'ui-ux-pro-max' changed to 'ui-design', which accounts for the full 4-byte size difference.
- reasoning_contract.py: same byte size.

How the data changed:
- motion.csv went from 12 to 15 columns.
- 15 accessibility rows were added to the stack CSVs: angular 8, nextjs 4, astro 3. stackGuidelines went from 1260 to 1275.
- The astro 'Default to zero JS' row was reworded.
- catalog-summary.json was regenerated (verifiedAt 2026-09-20).

New in Pipelines:
- Six catalog scripts: contrast.py, oklch.py, tokens.py, shadcn_theme.py, route.py, merge_parts.py.
- A declared contract, spec.yaml.
- maintenance/, the only half allowed pyyaml, the network or GOOGLE_FONTS_API_KEY. It holds validate-contract, validate-csv, generate-catalog-summary, generate-index, evaluate-relevance with relevance_metrics, smoke, refresh-google-fonts, refresh-icon-catalog, harvest-site-tokens, and verify.py, which runs 10 gates.
- Staged stack-accessibility candidates.
- Two generated INDEX.md files: the plugin's and the Pipelines root one.
- 3 skills, 3 agents, ROUTER.md and references/.
- Packaging: .claude-plugin/plugin.json and marketplace.json, a plugin-local .gitignore and .gitattributes, and .github/workflows/verify.yml.
- Licence and provenance files: LICENSE (two copyright lines), NOTICE, CHANGELOG.md and SOURCE-RESEARCH.md.

Pipelines replaces CHQ's single payload hash, which nothing verifies, with hashes the gates enforce: catalog-summary.json snapshot sha256 values and the relevance runtime and oracle fingerprints. It also edits data locally. None of CHQ's studio wiring came across: the Router intercept and attestation, the dashboard writeback, the token-authority split between studio and product work, ARTIFACT D and Designer Pro.

The files do not show that Pipelines was copied from the CHQ copy rather than from upstream. NOTICE names upstream as the origin, and Pipelines carries upstream-derived tests and maintenance tooling that CHQ excluded.

Verification method: I opened and read the source for every script, the spec, all skills and agents, the packaging and licence files, and the relevant CHQ skill, router, brand-gate, hub and DECISIONS passages. I ran no project script. One read-only directory listing (ls) supplied the byte sizes; everything else came from Read, Glob and Grep.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| CHQ search.py | cli | `runs-today` | Vendored upstream CLI. It runs BM25 search over the corpus by domain or by stack, and runs the --design-system generator, optionally saving a Master file plus page overrides. |
| CHQ core.py | library | `runs-today` | The BM25 engine and its registries: CSV_CONFIG (12 domains), STACK_CONFIG and AVAILABLE_STACKS (22), MAX_RESULTS=3, UNTRUNCATED_COLS, per-domain thresholds, synonyms, domain auto-detection, style identity and deprecation redirects, and suggestions. |
| CHQ design_system.py | library | `runs-today` | DesignSystemGenerator. It combines the product, style, color, landing and typography searches, applies the ui-reasoning.csv decision rules and the dials, formats ASCII or markdown output, and saves MASTER.md plus page overrides. |
| CHQ reasoning_contract.py | library | `runs-today` | A closed, non-executable grammar for the Decision_Rules column of ui-reasoning.csv. Condition keys (must_have and if_* signals) map to actions that use the constraint:, style:, pattern: and mode: prefixes. |
| CHQ validate_data.py | cli | `vendored` | A standard-library data-integrity guardrail. It checks every domain and stack CSV, ui-reasoning.csv, the catalog JSONs, the catalog-summary counts and snapshot sha256 values, and data-provenance.json. |
| CHQ vendored data corpus | data | `vendored` | The upstream corpus. 13 CSVs: styles, colors, charts, landing, products, ux-guidelines, typography, icons, motion, react-performance, app-interface, google-fonts, ui-reasoning. 4 JSONs: catalog-summary, data-provenance, google-font-licenses, phosphor-icons-up… |
| CHQ VENDOR.md vendoring protocol | protocol | `partial` | Records the upstream identity and the re-vendor procedure: upstream nextlevelbuilder/ui-ux-pro-max-skill, src/ui-ux-pro-max/{data,scripts}, v2.13.0, MIT, 44 files, 3.11 MB, and a payload sha256. The rule is no local edits. |
| CHQ ui_ux_intelligence skill | skill | `partial` | Skill 9 of 9 in CHQ's Four-Part Artifact Architecture. It wraps search.py for design-system generation and UX audits. It sets the anti-fabrication law and splits token authority: on studio surfaces it only proposes, and on product or client work it is the sol… |
| CHQ Router intercept (Router.md / router.js / dashboard.json) | protocol | `partial` | The studio-wide dual-trigger intercept. It routes design-system, palette, font-pairing, UX-review and accessibility-audit intents, plus MASTER.md and design_tokens.json assets, to ui_ux_intelligence after resolving the skill's three mandatory brand gates. |
| CHQ brand gates + ARTIFACT D regeneration loop | context | `partial` | Three L0 brand constants, transcribed from css_html_ui ARTIFACT A. They are ui_ux_intelligence's mandatory context, and ui_ux_intelligence is their declared regeneration path, but only through a four-step operator-approval loop: GENERATE with --json and no --… |
| CHQ hub Designer Pro tab | web-app | `runs-today` | A style-mixing assistant with two layers. Grounding is deterministic: it fetches 9 corpus CSVs over HTTP, scores rows by token overlap and runs conflict checks from corpus fields. Synthesis uses local Ollama to blend the chosen rows into a proposal, which nev… |
| Pipelines search.py | cli | `runs-today` | The migrated search CLI. It keeps every CHQ flag and adds a diagnostics view, a WCAG 2.2 contrast gate and two token export formats. |
| Pipelines core.py | library | `runs-today` | The migrated BM25 engine and registries. spec.yaml declares the registries and validate-contract.py enforces them. |
| Pipelines design_system.py | library | `runs-today` | The migrated generator. It now carries a WCAG 2.2 contrast report in the payload, emits the dtcg and shadcn formats, and saves three artifacts. |
| Pipelines reasoning_contract.py | library | `runs-today` | The migrated Decision_Rules grammar. |
| Pipelines validate_data.py | cli | `runs-today` | The migrated data-integrity validator. It is now verify gate 2 and the refresh preflight. |
| Pipelines contrast.py | library | `runs-today` | New. WCAG 2.2 contrast evaluation of a palette. Text pairs are enforced at 4.5:1; border and ring pairs are advisory at 3.0:1 (success criterion 1.4.11). |
| Pipelines oklch.py | library | `runs-today` | New. Standard-library conversion from sRGB hex to OKLCH (Ottosson), plus the inverse, used for the oklch() values in the shadcn output. |
| Pipelines tokens.py | library | `runs-today` | New. DTCG exporter that turns a design_system dict into W3C Design Tokens JSON: color, font.family, space, radius, shadow and motion groups, plus $extensions['cc.uupm']. |
| Pipelines shadcn_theme.py | library | `runs-today` | New. Emits a shadcn/ui :root CSS block (Tailwind v4, compatible with tweakcn) in oklch() or hex, with contrast notes. |
| Pipelines route.py | cli | `runs-today` | New. A brief router. It cross-checks the product domain three ways (the raw brief, a variant query using the catalog's own spellings, and stem-keyword overlap), fuses them with RRF and warns when they disagree. It then emits a design-system command and a mani… |
| Pipelines merge_parts.py | cli | `runs-today` | New. Merges and cross-checks the output of multipart agents. Search mode checks PART/QUERY/RETRIED/VERDICT/ROWS blocks against the manifest. Review mode checks AREA/FINDINGS/NOT-CHECKED blocks, and every rule-id must exist in references/quick-reference.md. |
| Pipelines catalog data | data | `runs-today` | The migrated corpus: the same 39 file names as CHQ (13 CSVs, 4 JSONs, 22 stack CSVs), edited locally. |
| Pipelines staged stack-accessibility candidates | data | `partial` | Candidate accessibility rows staged on 2026-09-20: nextjs 4 (No 61-64), astro 3 (No 54-56), angular 8 (No 51-58), laravel 0. REVIEW.md separates the text sourced from official docs from the authored text, and records probe results for the router's shared a11y… |
| Pipelines spec.yaml contract | protocol | `runs-today` | New. The declared contract. It declares: - catalog_root 'catalog' and entry_point 'catalog/scripts/search.py'; - stdlib_only (root 'catalog', exception 'maintenance/'); - the 12 domains and 22 stacks; - the dials (variance, motion, density) and the formats (a… |
| Pipelines validate-contract.py | cli | `runs-today` | New. Checks that spec.yaml agrees with the code, skills, agents, docs and packaging. It checks: - frontmatter keys, and that each name matches its folder or file; - agent tool bans (Write, Edit, Agent, Bash, NotebookEdit), with Bash allowed only through agent… |
| Pipelines validate-csv.py | cli | `runs-today` | New in the plugin. A structural CSV check for blank or duplicate headers, field-count mismatches and blank rows. |
| Pipelines generate-catalog-summary.py | cli | `runs-today` | New in the plugin. Generates or checks catalog-summary.json (counts, raw-byte sha256 snapshots of 4 files, the promotion policy and pending candidates from excludedFamilies) and the bold count tokens in README.md. |
| Pipelines generate-index.py | cli | `runs-today` | New. Generates the plugin INDEX.md: catalog vocabulary (products and keywords, style ids, font pairings, landing pattern ids, stacks), plus the data files and references. When the plugin sits inside the monorepo as plugins/<name>/ with CLAUDE.md at the root,… |
| Pipelines generated INDEX.md files | data | `generated` | Generated vocabulary indexes, with a 'do not edit by hand' header. The plugin index lists data files with row counts (stack guidelines 1275), products, searchable styles, font pairings, landing patterns, other vocabularies, stacks and references. The Pipeline… |
| Pipelines evaluate-relevance.py | cli | `runs-today` | New in the plugin. A deterministic relevance gate over judged cases. It reports routingAccuracy, precisionAt1, precisionAt3, mrrAt3, ndcgAt3, negativeAbstention, typoRecoveryAt3 and designSystemCoherence. Two fingerprints bind the run: the runtime fingerprint… |
| Pipelines smoke.py | cli | `runs-today` | New. Every registered domain or stack must answer a focused probe through the real search.py, and the registry size must equal spec.yaml. |
| Pipelines verify.py | ci | `runs-today` | New. The single health command. It runs 10 gates in order from the plugin root, stops at the first failure and prints the exact command to re-run that gate. |
| Pipelines test suites | ci | `runs-today` | Unit tests. - Engine: test_core, test_core_data_quality, test_data_contracts, test_style_taxonomy, test_text_layout_resilience, test_native_desktop_stack_freshness, test_web_stack_freshness, test_search_cli, test_route, test_merge_parts, test_tokens, test_con… |
| Pipelines refresh-google-fonts.py | cli | `partial` | New in the plugin. Rebuilds google-fonts.csv and google-font-licenses.json from the Google Fonts Developer API (or offline snapshots) plus google/fonts METADATA.pb, and prints a JSON change report. |
| Pipelines refresh-icon-catalog.py | cli | `partial` | New in the plugin. Normalises the pinned Phosphor catalog (@phosphor-icons/core 2.1.1, react 2.1.10) into phosphor-icons-upstream.json and validates the curated icons.csv against it. |
| Pipelines harvest-site-tokens.py | cli | `runs-today` | New. Maintainer-only tooling. It prints a browser extractor script that reads computed styles and canonicalises colours through a 1x1 canvas, then normalises the saved captures into a review report. It never writes the CSVs. |
| Pipelines ui-design-catalog skill | skill | `runs-today` | The user-facing catalog skill. It covers the search modes, the query contract, design-system generation, persist, the dials, domains and stacks, zero-result handling, output formats and the contrast gate. Every path starts from ${CLAUDE_PLUGIN_ROOT}. |
| Pipelines ui-design-multipart skill | skill | `runs-today` | New. Orchestrates two workflows: (A) a search fan-out for wide briefs and (B) a four-area page review. A script splits the work, one agent handles each part, and merge_parts.py merges the results. |
| Pipelines ui-design-catalog-refresh skill | skill | `partial` | New. A human-run replacement for the upstream weekly refresh workflow: fetch upstream, generate candidates under maintenance/candidates/, diff them against live data, have an agent review them, report, then stop for the maintainer. |
| Pipelines ui-design-search-part agent | agent | `runs-today` | New. Runs exactly one manifest search part and returns a PART/QUERY/RETRIED/VERDICT/ROWS block. |
| Pipelines ui-design-page-reviewer agent | agent | `runs-today` | New. A read-only review of one area of one built page (a11y+touch, layout, type-color-style or motion) against the quick-reference rule-ids. |
| Pipelines ui-design-catalog-reviewer agent | agent | `partial` | New. A read-only review of one refresh candidate (google-fonts.csv, google-font-licenses.json or phosphor-icons-upstream.json) against the live data. |
| Pipelines ROUTER.md | doc | `runs-today` | New. A query-routing guide for the catalog: choosing the mode, the domain table, using the catalog's own words, what to do when a match looks wrong (route.py and the --diagnostics fields), the fan-out threshold and guardrails. |
| Pipelines references | doc | `runs-today` | New in the plugin. Prose rule sets. quick-reference.md has 10 numbered sections of rule-ids (Accessibility through Charts & Data), used by the page reviewers and merge_parts. pro-rules.md holds the native/mobile app rules and the canonical pre-delivery checkl… |
| Pipelines plugin packaging | launcher | `partial` | New. The Claude Code plugin manifest (name ui-design, version 0.1.0, MIT, author groot99-droid, homepage and repository github.com/groot99-droid/ui-design-plugin) and a one-plugin marketplace (ui-design-plugin, source './'). It carries its own ignore and LF-p… |
| Pipelines licence and attribution files | doc | `runs-today` | New. These take over VENDOR.md's provenance role. - LICENSE: MIT, with two copyright lines (Next Level Builder 2024 and groot99-droid 2026). - NOTICE: the upstream sources (ui-ux-pro-max-skill, Phosphor core 2.1.1 and react 2.1.10, Google Fonts metadata, publ… |
| Pipelines verify.yml workflow | ci | `never-exercised` | New. A GitHub Actions matrix (ubuntu, windows and macos, Python 3.10 and 3.13) that installs the maintenance requirements and runs maintenance/verify.py. |

Full detail: [inventory/ui-ux-pro-max-vs-plugin.md](inventory/ui-ux-pro-max-vs-plugin.md)

## Archive engine

archive/ holds the "Living Archive Engine", a self-organizing knowledge system brought in unchanged from the external crispy-engine repo (DECISIONS.md D3; README.md line 213 maps archive/ to crispy-engine). Ingest is the one real pipeline. A React SPA sends raw text to POST /api/ingest (Bearer JWT required). FastAPI then (1) sends the text to Groq through the synchronous OpenAI Python client (primary model llama-3.3-70b-versatile, fallback llama3-8b-8192), which returns a 2-4 level taxonomy path, a confidence score, suggested links, alternative paths, entities, a one-sentence summary and key phrases. (2) It builds a 1536-dimension embedding: OpenAI text-embedding-3-small when OPENAI_API_KEY is set, otherwise a flat md5-derived pseudo-vector. Steps 1 and 2 go through asyncio.gather, but both coroutines make blocking sync calls with no await points, so in practice they run one after the other. (3) If Pinecone is configured, it queries Pinecone for the top 5 similar nodes. (4) It writes a row to PostgreSQL. (5) As FastAPI BackgroundTasks, it upserts the vector to Pinecone and writes Concept nodes with PARENT_OF and RELATES_TO edges to Neo4j. Read paths: GET /api/nodes (all nodes, Bearer token required), GET /api/nodes/{node_id} (no auth) and GET /api/search (ILIKE text search, no auth, no vector search). GET /health returns a static JSON body. Auth is JWT (HS256) with register and token endpoints. main.py mounts the auth router at /api/auth and auth.py also declares APIRouter(prefix='/auth'), so the routes as written are /api/auth/auth/register and /api/auth/auth/token, while ENGINE-README and the frontend use /api/auth/*. The Neo4j graph is write-only: no route reads it, and the frontend Graph tab is a d3 force layout of the node list with links=[] (no edges). The Pinecone store is off by default because the package is commented out of requirements.txt. The Celery reorganization tasks are stubs that return literals; celery beat schedules one of them every 86400 s. There is no WebSocket server: the frontend WebSocketManager exists, but its instantiation (ws://localhost:8000/ws) is commented out, and the backend has no /ws route. Deployment config: docker-compose.yml defines 7 services (postgres 5432, neo4j 7474/7687, redis 6379, backend 8000, celery_worker, celery_beat, frontend 3000->80). render.yaml defines 6 services (3 pserv, 2 web, 1 worker, no beat). There are also setup.sh and two Dockerfiles. No .env and no package-lock.json exist anywhere under archive/. The repo's own statements on run status: README.md lines 107-111 say "this has not been installed, built, or started", and that backend/requirements.txt and backend/Dockerfile "were newly written from the import graph in this pass and have never been exercised. Treat first boot as debugging, not as a smoke test." DECISIONS.md D4 says of those two files "Neither has been installed or run". requirements.txt line 2 reads "NOT yet exercised: no install or run has been performed against this file." DECISIONS.md D1 rejects this seven-service cloud stack in favour of a local-first design (an Ollama model plus an on-disk vector index) that has not been built. D6 says the planned "cosmos view" is GraphVisualization.jsx and NodeDetail.jsx rendering vault notes, which is also not implemented.

| Entry | Kind | Status | Purpose |
|---|---|---|---|
| Living Archive backend (FastAPI app) | service | `never-exercised` | FastAPI application titled from settings.PROJECT_NAME (default 'Living Archive Engine'). It mounts the auth router at API_V1_STR+'/auth' and the ingest, nodes and search routers at API_V1_STR (default '/api'), serves GET /health, creates all SQLAlchemy tables… |
| Auth API (/api/auth) | service | `never-exercised` | Account registration and OAuth2 password-flow login that issues HS256 JWTs. It also provides the get_current_user dependency that protects POST /api/ingest and GET /api/nodes. |
| Ingest API (POST /api/ingest) | service | `never-exercised` | The core pipeline. It classifies and embeds submitted text, merges link suggestions from the LLM and from vector neighbours, saves the node to Postgres, and schedules background writes to the vector store and the Neo4j graph. |
| Nodes API (GET /api/nodes, GET /api/nodes/{node_id}) | service | `never-exercised` | Lists all archived nodes and fetches a single node by id from Postgres. |
| Search API (GET /api/search) | service | `never-exercised` | Case-insensitive substring search over node content, summary and title. |
| AI engine (Groq classification + embeddings) | library | `never-exercised` | Uses an LLM to classify text into a 2-4 level path with confidence, suggested links and alternative paths. It also extracts entities (labels CONCEPT, PERSON, ORG, TECH, THEORY, FIELD), writes a one-sentence summary and key phrases, and generates 1536-dimensio… |
| Relational store (PostgreSQL via SQLAlchemy async) | data | `never-exercised` | System of record for users and knowledge nodes. |
| Graph store (Neo4j) | library | `never-exercised` | Writes each node's classification path into Neo4j as a chain of :Concept nodes joined by PARENT_OF edges, plus RELATES_TO edges to suggested concepts. |
| Vector store (Pinecone, optional) | library | `never-exercised` | Optional semantic-similarity index used to suggest links during ingest. |
| Reorganization tasks (Celery worker + beat) | service | `stub` | Intended background maintenance: daily tree-health analysis and batch re-embedding. |
| WebSocket protocol (WebSocketManager) | protocol | `specified-not-implemented` | Client-side real-time event channel, intended for live updates from the backend. |
| Living Archive frontend SPA (React + Vite) | web-app | `never-exercised` | Browser UI for signing in, ingesting text and browsing archived knowledge as a tree, graph or list, with search and a node detail modal. |
| Frontend API client (api.js) | library | `never-exercised` | fetch wrapper that attaches the Bearer token and talks to the backend. |
| AuthModal tab (Sign In / Create Account) | web-app | `never-exercised` | Login and registration screen shown when there is no stored token. |
| Ingest Knowledge panel | web-app | `never-exercised` | Text area plus a 'Process & Archive' button that submits text for classification. |
| Tree view tab | web-app | `never-exercised` | Hierarchical browser. It builds a folder tree under 'Knowledge Root' from each node's classification path. |
| Graph view tab | web-app | `partial` | d3 force-directed view of nodes. |
| List view tab | web-app | `never-exercised` | Flat card list of nodes. |
| SearchBar | web-app | `never-exercised` | Header search box ('Search knowledge...'). |
| NodeDetail modal | web-app | `never-exercised` | Overlay showing one node's classification path, summary, extracted entities, creation time and id. |
| setup.sh (stack launcher) | launcher | `never-exercised` | One-shot bash script that checks prerequisites, brings up the docker-compose stack, then prints service status and access URLs. |
| docker-compose stack | launcher | `never-exercised` | Full local orchestration of the 7 services. |
| render.yaml (Render Blueprint) | ci | `never-exercised` | Cloud deployment blueprint for Render.com (DEPLOY.md Option 1: create a Blueprint from render.yaml, add env vars from .env, deploy). |
| Backend container image (Dockerfile + requirements.txt) | launcher | `never-exercised` | Python 3.11 image for the API, the celery worker and celery beat. |
| Frontend container image (Dockerfile + nginx.conf) | launcher | `never-exercised` | Multi-stage build of the SPA, served by nginx on port 80 with an /api reverse proxy. |
| ENGINE-README.md | doc | `partial` | Engine overview: features, quick start, architecture diagram, API endpoint list, data flow, environment variable table, ports, troubleshooting, dev and test commands, production checklist. |
| DEPLOY.md | doc | `partial` | Deployment guide: local Docker quick deploy, cloud options (Render, AWS ECS, DigitalOcean App Platform), verification steps, service diagram, troubleshooting. |

Full detail: [inventory/archive.md](inventory/archive.md)
