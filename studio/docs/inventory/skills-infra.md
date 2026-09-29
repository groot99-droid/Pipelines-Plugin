# Infrastructure skills: compute gate, local RAG, UI intelligence

Subsystem `skills-infra` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.87 · 23 entries · 28 corrections made to the first reading.

## Summary

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

## Tools

### hardware_compute (skill)

`skill` · status `partial`

Paths: `skills/hardware_compute.skill.md`

Compute verification and allocation gate (the 'hardware bouncer'). It probes the single 16 GB laptop, checks the probe against per-workload thresholds, and mints or denies a 30-minute gate token that compute-heavy skills must hold. It never launches compute itself.

**Entry points**

- `grep -q "ROUTER INTERCEPT" ./.task_scratch/attestation.txt || echo "FAIL:P1"`
  - does: P1: check that the attestation exists
  - changes: nothing
- `case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) STUDIO_HOST_KIND=windows ;; Linux) (WSL_DISTRO_NAME set or /proc/version contains microsoft => wsl, else linux) ;; Darwin) macos ;; *) unknown ;; esac; export STUDIO_HOST_KIND`
  - does: P2: detect the shell kind. Prints OK:P2 for windows|wsl|linux, otherwise 'FAIL:P2 unsupported host kind'
  - changes: exports STUDIO_HOST_KIND in the calling shell
- `for t in $REQ; do command -v "$t" >/dev/null 2>&1 || echo "FAIL:P3 missing $t"; done; echo "OK:P3" (REQ="awk df grep" for windows|wsl|linux)`
  - does: P3: check required tools, never nvidia-smi. REQ is unset for macos/unknown, so OK:P3 still prints
  - changes: nothing
- `(only if STUDIO_HOST_KIND=wsl) command -v powershell.exe || command -v pwsh.exe && echo "OK:P4 windows bridge reachable" || echo "FAIL:P4 no powershell.exe on PATH ..."`
  - does: P4 WSL law: the PowerShell bridge must be reachable
  - changes: nothing
- `./tools/hw/verify_compute.sh {{workload_class}} > state/hw_probe_latest.json`
  - does: Step 2 RUN VERIFICATION: run the extracted ARTIFACT A probe
  - changes: state/hw_probe_latest.json

**Inputs**

- workload_class declared by the requesting skill: llm_local_sm | llm_local_md | render_3d_cpu | batch_2d
- probe JSON from ARTIFACT A
- existing state/compute_gate.json (single-flight check)

**Outputs**

- state/hw_probe_latest.json
- state/compute_gate.json. Step 5 text shows PASS as {verdict, workload, ts_epoch, probe:{...}}; ARTIFACT C shows the fuller schema. DENY is {verdict:'DENY', reasons:[...]}
- on DENY (skill text only): the requesting pipeline phase is set to blocked, dashboard system_status.state is set to DEGRADED, and remediation is logged from ARTIFACT B remedies
- dashboard.json hardware.* block (CONTEXT FLUSH 1)

**Reads**

- .task_scratch/attestation.txt
- state/hw_probe_latest.json
- state/compute_gate.json
- ARTIFACT B (embedded)
- mandatory_context pipeline_ethics and render_philosophy (context/brand/pipeline_ethics.context.md and context/brand/render_philosophy.context.md; both authored:false in dashboard.json and absent on disk)

**Writes**

- tools/hw/verify_compute.sh (step 1 UNPACK, chmod +x)
- state/hw_probe_latest.json
- state/compute_gate.json
- dashboard.json hardware.* and system_status.state (writes_dashboard_keys)

**Depends on**

- bash
- awk
- df
- grep
- uname
- powershell.exe or pwsh.exe (Windows/WSL)

**Environment and secret names (names only)**

- STUDIO_HOST_KIND (exported by P2)
- WSL_DISTRO_NAME (read)

**Gates and checkpoints**

- P1: the attestation must contain 'ROUTER INTERCEPT'
- P2: host kind must be windows|wsl|linux; macOS is recognised only so it can be refused
- P3: awk, df and grep present
- P4: in WSL the PowerShell bridge is required
- V1: read the requester's workload class; there is no generic 'probably fine'
- V2: pipeline_ethics governs preemption. An in-flight render is never killed for a new job without operator approval
- Step 3: every metric for the class must pass; no partial credit
- Step 4 single-flight: an unexpired PASS token whose consumed_by is null or names a still-running skill means DENY, naming the holder
- Step 6 CONTEXT FLUSH 1: dashboard writeback, drop the raw probe, keep the verdict line
- Step 7 HANDBACK: the requesting skill re-checks the token itself ('trust the file, not the conversation')
- Step 8 CONTINUOUS MODE: for jobs over ~5 min, repeat steps 2-6 every 5 minutes; two consecutive DENYs tell the running skill to checkpoint and pause
- gate_ttl_seconds: 1800

**Invoked by**

- Router: trigger_a phrases, or trigger_b 'ANY task where another skill declares danger_class: LOCAL_COMPUTE_HEAVY'; Router.md §2 Trigger A row 'render locally / GPU / heavy compute / batch process / thermals / on battery'
- blender_python (danger_class LOCAL_COMPUTE_HEAVY, depends_on_skill)
- local_rag_orchestration (danger_class LOCAL_COMPUTE_HEAVY, depends_on_skill)
- adobe_suite_uxp through depends_on_skill with workload_class batch_2d only. Its danger_class is LOCAL_DESTRUCTIVE, so trigger_b does not literally match it

**Invokes**

- tools/hw/verify_compute.sh (ARTIFACT A)
- ARTIFACT B (evaluated by tools/hw/evaluate_gate.py in practice, though the skill text does not name it)
- Router (HANDBACK)

**Notes**

ROUTING HEADER (verbatim): skill_id: hardware_compute | version: 2.0 | trigger_a: ["render locally", "GPU", "heavy compute", "batch process", "out of memory", "thermals", "on battery"] | trigger_b: ["ANY task where another skill declares danger_class: LOCAL_COMPUTE_HEAVY"] | mandatory_context: [pipeline_ethics, render_philosophy] | host_kinds: [windows, wsl, linux] | version_note: v2.0 — single-host port. One laptop (Lenovo Yoga Book 9i, 16 GB shared, Intel iGPU), three shells (Windows/Git Bash, WSL2, Linux). Replaces the v1.x macOS-host + CUDA-node split. | writes_dashboard_keys: [hardware.*, system_status.state] | danger_class: GATEKEEPER # this skill blocks other skills; it never launches compute itself | gate_token_path: state/compute_gate.json | gate_ttl_seconds: 1800.

EXECUTION PROCESS: 1 UNPACK, 2 RUN VERIFICATION, 3 EVALUATE, 4 SINGLE-FLIGHT CHECK, 5 MINT/DENY TOKEN, 6 CONTEXT FLUSH 1, 7 HANDBACK, 8 CONTINUOUS MODE.

Internal inconsistency: step 5 names the snapshot field 'probe', while ARTIFACT C and evaluate_gate.py use 'probe_snapshot' plus ttl_seconds, memory_budget_gb, consumed_by and law.

Implementation status: steps 3-5 (token only) exist in tools/hw/evaluate_gate.py. UNPACK exists in tools/bootstrap.sh and in CI. No code implements step 6, step 8, or the DENY-side dashboard and phase writes; tools/hw never touches dashboard.json.

Router.md §10 says compute-heavy work needs a PASS token 'from verify_compute.sh', but that script only probes; evaluate_gate.py mints the token.

This checkout has none of the skill's runtime files: the probe, probe output, token and .task_scratch/ are all absent. The dashboard registry lists the skill as 'ready'.

### verify_compute.sh (hardware_compute ARTIFACT A, 'hardware probe v4')

`cli` · status `generated`

Paths: `skills/hardware_compute.skill.md`, `tools/hw/verify_compute.sh`

Self-extracting bash probe. It reports shell kind, machine identity, GPU, memory, page-file use, power, thermal and performance headroom, and disk as one JSON object on stdout. The header says it never mutates system state.

**Entry points**

- `./tools/hw/verify_compute.sh <workload_class>`
  - does: Header usage line. One optional positional WORKLOAD (default 'generic') is echoed into the JSON 'workload' field and used for nothing else
  - changes: nothing (stdout only)
- `./tools/hw/verify_compute.sh generic > state/hw_probe_latest.json`
  - does: How tools/bootstrap.sh section 5 calls it (PROBE_OUT)
  - changes: state/hw_probe_latest.json (via the redirect)
- `./tools/hw/verify_compute.sh generic > /tmp/probe.json`
  - does: How CI calls it on ubuntu-latest
  - changes: /tmp/probe.json on the runner
- `./tools/hw/verify_compute.sh generic | python3 -m json.tool`
  - does: Manual inspection form given in BOOT.md 'Known unknowns'
  - changes: nothing

**Inputs**

- positional workload class (optional, default 'generic')

**Outputs**

- JSON on stdout: {workload, ts_epoch, host{name, kind: windows|wsl|linux|unknown, machine}, gpu{status: integrated|discrete, name, vram_total_gb: null, memory_shared_with_system}, memory{total_gb, available_gb, free_pct, swap_used_mb, dynamic_claim_limit_gb}, power{source: "ac"|"battery"|null, battery_pct}, thermal{cpu_temp_c, cpu_perf_pct}, disk{free_gb, system_free_gb}}

**Reads**

- uname -s, hostname, /proc/version, WSL_DISTRO_NAME
- Windows/WSL through PowerShell CIM (psq helper: -NoProfile -NonInteractive -Command "try { ... } catch { '' }"):
  - Win32_ComputerSystem.TotalPhysicalMemory and .Model
  - Win32_PerfFormattedData_PerfOS_Memory.AvailableMBytes, falling back to Win32_OperatingSystem.FreePhysicalMemory
  - Win32_PageFileUsage.CurrentUsage (sum)
  - Win32_ComputerSystemProduct.Version
  - Win32_VideoController.Name
  - Win32_Battery BatteryStatus, EstimatedChargeRemaining and count
  - root/wmi MSAcpi_ThermalZoneTemperature
  - Win32_PerfFormattedData_Counters_ProcessorInformation(_Total).PercentProcessorPerformance
  - Win32_LogicalDisk C: FreeSpace
- Linux:
  - /proc/meminfo (MemTotal, MemAvailable, SwapTotal/SwapFree)
  - /sys/class/dmi/id/product_version, then product_name
  - lspci
  - /sys/class/power_supply/A{C,DP}*/online and BAT*/capacity
  - /sys/class/thermal/thermal_zone0/temp, or sensors
  - /proc/cpuinfo 'cpu MHz' and /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq
- df -Pk . for disk.free_gb on every host; df -Pk / for system_free_gb on linux only (Windows/WSL use Win32_LogicalDisk C:)
- nvidia-smi if present, which sets gpu.status=discrete

**Depends on**

- bash
- awk
- df
- grep
- tr
- date
- hostname
- cut
- sed
- head
- cat
- ls
- powershell.exe | pwsh.exe | pwsh (Windows and WSL)
- optional: lspci, sensors, nvidia-smi

**Environment and secret names (names only)**

- WSL_DISTRO_NAME

**Gates and checkpoints**

- Unreadable metrics are emitted as null through jnum(), never as a fake 0, so null_law can close the gate. Exception: disk.free_gb (and system_free_gb on linux) go through num(), so they become 0 rather than null
- WSL memory comes only through the PowerShell bridge, never /proc/meminfo
- dynamic_claim_limit_gb = 60% of available_gb, reduced so at least 4 GB of total_gb remains, floored at 0
- vram_total_gb is always null by design
- Darwin maps to host.kind 'unknown', not 'macos'; evaluate_gate host_law still denies it

**Invoked by**

- hardware_compute step 2
- tools/bootstrap.sh section 5
- CI .github/workflows/verify.yml step 'Probe extracts and parses'

**Invokes**

- PowerShell CIM queries through psq()

**Notes**

Extracted with the regex '### ARTIFACT A.*?\n```bash\n(.*?)\n```' by tools/bootstrap.sh and CI. The extracted copy is gitignored (.gitignore line 24). tools/verify_system.py check_extracted_probe fails if it drifts from ARTIFACT A.

Absent from this checkout.

BOOT.md 'Known unknowns' and DECISIONS.md D8 'Not yet done' both say the Windows and WSL branches (every psq query) have never run on the target laptop. Only the Linux branch has been exercised, in CI.

The JSON is built with a heredoc and no escaping, so a machine or GPU name containing a double quote would produce invalid JSON.

### ARTIFACT B — threshold matrix, laws and remedies

`data` · status `runs-today`

Paths: `skills/hardware_compute.skill.md`

The gate's law table: thresholds per workload class, six laws and remediation text. tools/hw/evaluate_gate.py parses it at runtime, so the skill file stays the single source of truth.

**Outputs**

- thresholds consumed by tools/hw/evaluate_gate.py
- remedy text printed by evaluate_gate.py on DENY

**Gates and checkpoints**

- llm_local_sm (≤8B at Q4_K_M, num_ctx ≤ 8192): memory.available_gb_min 6, memory.free_pct_min 30, memory.swap_used_mb_max 6144, power.source_in [ac, battery], thermal.cpu_temp_c_max 90, thermal.cpu_perf_pct_min 65, disk.free_gb_min 12
- llm_local_md (12–14B at Q4_K_M, num_ctx ≤ 4096): available_gb_min 10, free_pct_min 45, swap_used_mb_max 3072, power [ac], cpu_temp_c_max 85, cpu_perf_pct_min 80, disk.free_gb_min 20
- render_3d_cpu (Blender EEVEE, or Cycles on CPU): gpu.status any, available_gb_min 8, free_pct_min 40, swap_used_mb_max 3072, power [ac], cpu_temp_c_max 80, cpu_perf_pct_min 85, disk.free_gb_min 20
- batch_2d (Adobe batch export/grade via the COM bridge): gpu.status any, available_gb_min 5, free_pct_min 25, swap_used_mb_max 6144, power [ac], cpu_temp_c_max 90, cpu_perf_pct_min 65, disk.free_gb_min 10
- evaluation_law: ALL named metrics must pass. dynamic_claim_limit_gb becomes the hard memory budget for the requesting skill (Blender tile/scene budget, Ollama num_ctx and tier, Adobe batch size)
- null_law: an unreadable metric that the class names means FAIL. gpu.vram_total_gb is null as a fact, not a failure
- thermal_law: at least one of cpu_temp_c and cpu_perf_pct must be readable, and every readable one must pass
- host_law: host.kind must be windows, wsl or linux. macOS, or a discrete CUDA GPU, means refuse (DECISIONS.md § D8)
- single_flight_law: one heavy job at a time. An unexpired PASS token that is unconsumed or held by a running skill denies a new request
- wsl_memory_law: inside WSL2, memory must come through the PowerShell bridge; otherwise it is null and the gate closes

**Invoked by**

- tools/hw/evaluate_gate.py load_law(), regex '### ARTIFACT B.*?\n```json\n(.*?)\n```'

**Notes**

'machine' string: Lenovo Yoga Book 9i · 16 GB shared · Intel integrated graphics · no CUDA.

The 9 remedy keys: 'on battery', 'low battery on ac', 'thermal unreadable (both null)', 'cpu_perf_pct low', 'low available_gb', 'swap rising', 'gpu discrete unexpectedly', 'low disk', 'single-flight deny'.

Commands the remedies cite:
- powershell.exe -NoProfile -Command '(Get-CimInstance Win32_PerfFormattedData_Counters_ProcessorInformation | Where-Object Name -eq "_Total").PercentProcessorPerformance'
- ollama stop <model>
- ollama rm
- delete state/compute_gate.json and re-probe, if the token holder died

Not enforced by code:
- No class names power.battery_pct, and evaluate_gate's REMEDY_FOR never maps 'low battery on ac', so that remedy is never printed.
- The 'swap rising' rule (DENY stands until CurrentUsage stabilises across two probes) is not implemented; the evaluator looks at one probe.
- A host_law failure on host.kind has no remedy mapping.

### Compute gate token (ARTIFACT C, state/compute_gate.json)

`protocol` · status `partial`

Paths: `skills/hardware_compute.skill.md`, `state/compute_gate.json`

File-based authorisation token: one token, one workload. A heavy skill must find a fresh, unconsumed PASS token for its own workload, then write its skill_id into consumed_by.

**Inputs**

- probe snapshot
- workload class

**Outputs**

- PASS: {verdict:'PASS', workload, ts_epoch, ttl_seconds:1800, memory_budget_gb, probe_snapshot{gpu, available_gb, power, cpu_perf_pct, thermal_c}, consumed_by:null, law}
- DENY from evaluate_gate.py: {verdict:'DENY', workload, ts_epoch, reasons:[...]}

**Gates and checkpoints**

- TTL 1800 s
- a consumed token cannot authorise a second job
- a live token blocks minting for any OTHER workload

**Invoked by**

- tools/hw/evaluate_gate.py (writer)
- blender_python P4 (reader: requires PASS, age < ttl, workload == render_3d_cpu, consumed_by None) and its step 2 CLAIM THE GATE (writes consumed_by: blender_python)
- local_rag_orchestration P3 (reader: requires workload llm_local_sm, or llm_local_md when RAG_TIER=md, and consumed_by None); its step 8 stamps consumed_by
- tools/hw/test_gate.py (writes temporarily, then restores or deletes)

**Notes**

Absent from this checkout.

The PASS 'law' string minted by evaluate_gate.py omits ARTIFACT C's single-flight sentence.

Skill vs code on single-flight: the skill denies only while consumed_by is null or names a running skill. evaluate_gate.py denies any live PASS token held by a different workload, whatever consumed_by says (unless --force), and allows re-minting for the same workload.

Re-minting overwrites consumed_by with null (or with the --consume value), so a token already spent on one job of a class becomes usable again.

'evaluate_gate.py <cls> --consume <skill>' (documented in BOOT.md) writes consumed_by at mint time. That makes the consuming skill's own P3/P4 check fail with 'already consumed by ...'.

### tools/hw/evaluate_gate.py

`cli` · status `runs-today`

Paths: `tools/hw/evaluate_gate.py`

Runs hardware_compute's evaluate, single-flight and mint steps. It reads a probe JSON and checks it against ARTIFACT B parsed from the skill file, applying the host, null, thermal and single-flight laws. It prints per-check ok/FAIL lines and remedies, then writes a PASS or DENY token.

**Entry points**

- `python3 tools/hw/evaluate_gate.py llm_local_sm`
  - does: evaluate one class and mint a token (docstring example)
  - changes: state/compute_gate.json
- `python3 tools/hw/evaluate_gate.py --all --dry-run`
  - does: survey every class without writing a token (docstring example)
  - changes: nothing
- `python3 tools/hw/evaluate_gate.py render_3d_cpu --consume blender_python`
  - does: mint and stamp consumed_by (docstring example)
  - changes: state/compute_gate.json
- `python3 tools/hw/evaluate_gate.py [workload] [--all] [--probe PATH] [--dry-run] [--consume SKILL_ID] [--force]`
  - does: Full argparse surface: - --probe defaults to state/hw_probe_latest.json - --force overrides a live token held by another workload - --all without --dry-run is refused (die, exit 2) - giving neither a workload nor --all is an argparse error
  - changes: state/compute_gate.json (creating state/ if needed) unless --dry-run

**Inputs**

- workload class (positional) or --all
- probe JSON (default state/hw_probe_latest.json)

**Outputs**

- stdout: a probe line (age, host, machine), per-check ok/FAIL lines, '<cls>  —  PASS|DENY', the token line, and remedies
- exit 0 = PASS, 1 = DENY, 2 = could not evaluate (missing skill or probe, bad JSON, unknown class, --all without --dry-run, argparse errors)

**Reads**

- skills/hardware_compute.skill.md (ARTIFACT B)
- state/hw_probe_latest.json or the --probe path
- state/compute_gate.json (single-flight)

**Writes**

- state/compute_gate.json

**Depends on**

- python3 stdlib

**Gates and checkpoints**

- warns when the probe is more than 1800 s old
- host.kind must be in {windows, wsl, linux}
- gpu.status=discrete means DENY
- the thermal pair follows thermal_law
- single-flight is skipped under --dry-run; refreshing the same workload is allowed
- the probe's own 'workload' field is ignored; the class comes from the CLI

**Invoked by**

- operator or agent (BOOT.md §4)
- tools/bootstrap.sh section 6 (--all --dry-run --probe state/hw_probe_latest.json)
- CI verify.yml step 'Evaluator runs against a live probe'
- tools/hw/test_gate.py

**Notes**

Does not write dashboard.json.

REMEDY_FOR is ordered from most to least specific. When the probe is missing, the error message points to tools/bootstrap.sh or 'tools/hw/verify_compute.sh <class> > <probe path>'.

No read_text()/write_text() call passes an explicit encoding, and the script is not in CI's 'Tools declare their encodings' step.

### tools/hw/test_gate.py

`cli` · status `runs-today`

Paths: `tools/hw/test_gate.py`

Regression cases that pin evaluate_gate.py verdicts. Nine dry-run cases:
- healthy sm → PASS
- one readable thermal reading → PASS
- both thermal readings null → DENY
- battery → DENY for render, PASS for sm
- throttling → DENY
- md on a loaded 16 GB → DENY
- discrete GPU → DENY
- macOS → DENY
One single-flight case: a live token blocks a second workload.

**Entry points**

- `python3 tools/hw/test_gate.py`
  - does: runs 9 --dry-run subprocess cases plus the single-flight case (render_3d_cpu without --dry-run against a planted llm_local_sm token)
  - changes: writes a fake PASS token to state/compute_gate.json; evaluate_gate then overwrites it with a DENY. The prior content is restored in finally, or the file deleted. Creates state/ if missing. Temp probe files in the system temp dir are removed

**Outputs**

- ok/FAIL per case and 'N passed, M failed'; exit 0 when all pass, 1 otherwise

**Reads**

- tools/hw/evaluate_gate.py (run through subprocess)
- state/compute_gate.json (backup)

**Writes**

- state/compute_gate.json (transient)

**Depends on**

- python3 stdlib

**Invoked by**

- CI .github/workflows/verify.yml step 'Gate logic'

**Invokes**

- tools/hw/evaluate_gate.py

**Notes**

DECISIONS.md D8 counts these as 'ten cases'. File I/O has no explicit encodings.

### tools/bootstrap.sh

`launcher` · status `never-exercised`

Paths: `tools/bootstrap.sh`

First-boot script. For this subsystem it performs hardware_compute UNPACK and survey:
- extracts ARTIFACT A into tools/hw/verify_compute.sh and syntax-checks it
- runs the probe into state/hw_probe_latest.json
- runs evaluate_gate --all --dry-run
It also checks Ollama reachability for local_rag. It mints no gate token.

**Entry points**

- `bash tools/bootstrap.sh`
  - does: Full first boot: 1 host 2 prerequisites (python3 curl awk df grep, plus the PowerShell bridge on windows/wsl) 3 Ollama reachability, with a WSL gateway retry and reconcile_models.py report 4 native bridges (PowerShell Test-Path on HKLM Classes for Photoshop, Illustrator and AfterFX; Blender --version) 5 probe extraction and run 6 class survey
  - changes: creates state/, tools/hw/, .task_scratch/; writes tools/hw/verify_compute.sh and state/hw_probe_latest.json
- `bash tools/bootstrap.sh --probe`
  - does: Re-probe only. Runs the section 1 host check, then sections 5-6; skips sections 2-4 (prerequisites, Ollama and native bridges)
  - changes: tools/hw/verify_compute.sh, state/hw_probe_latest.json

**Inputs**

- skills/hardware_compute.skill.md
- dashboard.json hardware.local_llm.endpoint

**Outputs**

- tools/hw/verify_compute.sh
- state/hw_probe_latest.json
- console summary
- exit 0 = ready; 1 = hard prerequisite failed or the probe emitted invalid JSON; 2 = not run from <repo>/tools (no Router.md or skills/)

**Reads**

- skills/hardware_compute.skill.md
- dashboard.json
- Router.md (existence landmark)
- /proc/version

**Writes**

- tools/hw/verify_compute.sh
- state/hw_probe_latest.json

**Depends on**

- bash
- python3
- curl
- ip (WSL)
- powershell.exe/pwsh.exe/pwsh (optional bridge)
- Ollama HTTP /api/tags
- Blender (optional)

**Environment and secret names (names only)**

- BLENDER_BIN
- WSL_DISTRO_NAME

**Gates and checkpoints**

- exits 1 on HARD_FAIL before running the probe
- bash -n syntax check of the extracted probe
- macOS and unknown hosts count as HARD_FAIL
- a missing Ollama is a warning, not fatal

**Invoked by**

- operator (BOOT.md: 'bash tools/bootstrap.sh')

**Invokes**

- tools/hw/verify_compute.sh generic
- python3 tools/hw/evaluate_gate.py --all --dry-run --probe state/hw_probe_latest.json
- python3 tools/reconcile_models.py --endpoint <reached> (report mode, no --write)
- curl <endpoint>/api/tags
- "$PWSH" -NoProfile -NonInteractive -Command "if (Test-Path 'HKLM:\\SOFTWARE\\Classes\\<app>') ..."
- <blender> --version

**Notes**

Read in full. This checkout shows no sign of a run: .task_scratch/, tools/hw/verify_compute.sh and state/hw_probe_latest.json are absent, and mkdir -p would have created .task_scratch/. DECISIONS.md D8 says the COM-registration probe has never run on the target machine. The inline extractor calls open() without an encoding.

### local_rag_orchestration (skill)

`skill` · status `partial`

Paths: `skills/local_rag_orchestration.skill.md`

Local RAG over the Obsidian vault using tiered Ollama models on a 16 GB laptop. It:
- resolves endpoint and tier from dashboard.json
- requires a hardware_compute PASS token
- routes the task to INDEX, QUERY or SYNTHESIS
- enforces tier-scoped budgets with flush checkpoints
- evicts the model before handback

**Entry points**

- `RAG_ENDPOINT=$(python3 -c "import json;print(json.load(open('dashboard.json'))['hardware']['local_llm']['endpoint'])"); RAG_TIER=${RAG_TIER:-sm}; RAG_MODEL=$(python3 -c "import json,os;print(json.load(open('dashboard.json'))['hardware']['local_llm']['tiers'][os.environ.get('RAG_TIER','sm')]['model'])")`
  - does: P2: resolve endpoint and tier model from dashboard.json, never from a literal
  - changes: shell variables
- `if grep -qi microsoft /proc/version; then if ! curl -s --max-time 3 "$RAG_ENDPOINT/api/tags"; then WIN_HOST=$(ip route show default | awk '{print $3; exit}'); RAG_ENDPOINT=$(echo "$RAG_ENDPOINT" | sed "s#//[^:/]*#//$WIN_HOST#"); fi; fi`
  - does: P2a WSL bridge: rewrite the host to the WSL default gateway when localhost is unreachable. Prints a note that the Windows side needs OLLAMA_HOST=0.0.0.0 and a firewall rule for 11434
  - changes: RAG_ENDPOINT shell variable
- `curl -s --max-time 6 "$RAG_ENDPOINT/api/tags" | RAG_MODEL="$RAG_MODEL" python3 -c "...family match on name.split(':')[0]..." && echo "OK:P2 serving $RAG_MODEL" || echo "FAIL:P2 $RAG_MODEL not served — 'ollama pull $RAG_MODEL'"`
  - does: P2b: check that the resolved tag's family is served
  - changes: nothing
- `python3 - <<'PY' (loads state/compute_gate.json) PY`
  - does: P3 hardware gate: verdict PASS, age < ttl_seconds (default 1800), workload == llm_local_md if RAG_TIER=md else llm_local_sm, consumed_by is None. Prints OK:P3 or FAIL:P3 <reasons>
  - changes: nothing
- `python3 - <<'PY' (reads dashboard.json hardware.local_llm.context_used_pct) PY`
  - does: P4 context budget: OK if under 50, else 'FAIL:P4 window already N% — flush first'
  - changes: nothing
- `python3 tools/vault_rag.py status | grep -qE "index +[0-9]+ chunks" && (python3 tools/vault_rag.py status | grep -q "changed since" && echo WARN:P5 ... || echo OK:P5) || echo "WARN:P5 no index — python3 tools/vault_rag.py index"`
  - does: P5: the index exists and is fresher than the corpus (WARN only)
  - changes: nothing
- `curl -s "$RAG_ENDPOINT/api/generate" -d "{\"model\":\"$RAG_MODEL\",\"keep_alive\":0}" >/dev/null`
  - does: Step 8 EVICT, followed by stamping consumed_by on the gate token
  - changes: Ollama resident-model state; state/compute_gate.json consumed_by

**Inputs**

- task text or question
- RAG_TIER (sm by default; md only when the task declares it and the gate agrees)
- dashboard.json hardware.local_llm (endpoint, tiers, context_used_pct)
- vault corpus (vault/, or whatever --vault was indexed)

**Outputs**

- answers citing chunk ids like [c_0412]
- ≤300-token MAP notes and a REDUCE report (SYNTHESIS)
- dashboard hardware.local_llm.context_used_pct and loaded_tier
- event_log entries (answer plus source chunk ids)
- state/rag_flush_ledger.json entries

**Reads**

- .task_scratch/attestation.txt
- dashboard.json
- state/compute_gate.json
- state/rag_index/
- mandatory_context memory_discipline (context/brand/memory_discipline.context.md; authored:false and absent)
- Router.md §3 also names pipeline_ethics as 'load if flagged in dashboard'

**Writes**

- state/rag_index/ (INDEX mode; shard persisted at CHECKPOINT-F1 every 20 chunks)
- state/rag_traces/ (think blocks, audit only)
- state/rag_notes/{doc}.md (SYNTHESIS MAP, CHECKPOINT-F3)
- state/rag_flush_ledger.json (ARTIFACT C)
- dashboard.json hardware.local_llm.context_used_pct, hardware.local_llm.loaded_tier, event_log
- state/compute_gate.json consumed_by

**Depends on**

- Ollama HTTP API (/api/tags, /api/generate, /api/embeddings)
- python3
- curl
- ip
- awk
- sed
- grep
- tools/vault_rag.py

**Environment and secret names (names only)**

- RAG_TIER (read from the environment)
- RAG_MODEL (passed as an env var to the P2b python)
- OLLAMA_HOST (Windows side, must be 0.0.0.0 for WSL access)
- Shell-only variables, not env: RAG_ENDPOINT, WIN_HOST
- {{EMBED_MODEL}}, {{RAG_ENDPOINT}} and {{RAG_MODEL}} are template placeholders in ARTIFACT A, not env vars

**Gates and checkpoints**

- P1: attestation contains 'ROUTER INTERCEPT'
- P2/P2b: the tier model must be served
- P3: fresh, unconsumed, workload-matched PASS token
- P4: context_used_pct < 50
- P5: index present and fresh (WARN only)
- V1: load memory_discipline before answering
- V2: exactly one mode per session (INDEX | QUERY | SYNTHESIS)
- V3: tier md only with AC power and a near-idle desktop
- Session ceiling of 60% of the tier's num_ctx forces a CHECKPOINT-F immediately
- CHECKPOINT-F1 every 20 chunks (INDEX)
- CHECKPOINT-F2 after each answered question: event_log write, then purge the retrieval block and think trace
- CHECKPOINT-F3 after each MAP call
- CHECKPOINT-F4 final
- EVICT before handback; a model still resident afterwards is a protocol violation

**Invoked by**

- Router trigger_a: 'search my docs', 'recall', 'summarize corpus', 'RAG', 'local model', 'what did we decide', 'project memory'
- Router trigger_b: corpus dirs and pipeline research phases
- Router.md §2 Trigger B file-type rule '.pdf/.md corpus → local_rag'

**Invokes**

- hardware_compute (depends_on_skill; must PASS before any model call)
- Ollama endpoint
- tools/vault_rag.py (P5 status; the 'Implementation' paragraph)

**Notes**

ROUTING HEADER (verbatim): skill_id: local_rag_orchestration | version: 2.0 | trigger_a: ["search my docs", "recall", "summarize corpus", "RAG", "local model", "what did we decide", "project memory"] | trigger_b: ["corpus dirs: ./project/docs ./project/notes", "pipeline research phases"] | mandatory_context: [memory_discipline] | host_kinds: [windows, wsl, linux] | writes_dashboard_keys: [hardware.local_llm.context_used_pct, hardware.local_llm.loaded_tier] | danger_class: LOCAL_COMPUTE_HEAVY | depends_on_skill: hardware_compute.skill.md # must PASS before any model call | workload_class: llm_local_sm # llm_local_md only when the task declares it and the gate agrees | target_model: resolved at runtime from dashboard.json → hardware.local_llm.tiers (see §1 P2) | version_note: v2.0 — retargeted from DeepSeek-R1-671B on a 192 GB host to tiered local models on a 16 GB laptop. Model identity is now registry-driven, never hardcoded.

MODEL TIERS (§2 table):
- sm (≤8B Q4): num_ctx 8192, retrieval payload ≤3,000 tok per hop, reasoning reserve ≥2,500 tok, num_predict 800
- md (12–14B Q4): num_ctx 4096, payload ≤1,200, reserve ≥1,500, num_predict 600
dashboard.json values: endpoint http://localhost:11434; sm = llama3.1:8b (Q4_K_M, 8192, llm_local_sm, approx_resident_gb 6); md = mistral-nemo:12b (Q4_K_M, 4096, llm_local_md, approx_resident_gb 10); embed_model nomic-embed-text; _tiers_note marks the tags PROVISIONAL.

RETRIEVAL RULES: 800-token chunks with 120 overlap; top-k 8, reranked to 4 within the payload cap; drop the lowest-ranked chunks first.

Declared deviations in the implementation: the index is stdlib JSON (normalised float32, base64, dot product) rather than FAISS, and 'rerank' is similarity order rather than a cross-encoder.

PROMPT RULES:
- no system field for reasoning models
- temperature 0.5–0.7 (0.6 default; 0.3 for the router call); top_p 0.95
- never few-shot
- keep_alive '5m' on every call
- strip <think>…</think> before storing or displaying, and archive it to state/rag_traces/
- never raise num_ctx beyond the tier

EXECUTION PROCESS:
1 UNPACK
2 MODE ROUTE (ROUTER_SUBPROMPT, num_predict 400)
3 INDEX (F1)
4 QUERY: a retrieve, b build from QUERY_SUBPROMPT, c call + strip + archive (F2)
5 SYNTHESIS map-reduce (F3)
6 WINDOW REPORT (prompt_eval_count or chars/4 against the tier's num_ctx)
7 F4 final
8 EVICT and stamp consumed_by

No code outside the skill implements P3, the consumed_by stamp, MODE ROUTE, SYNTHESIS, the flush ledger, rag_notes or event_log writes.

trigger_b still names ./project/docs and ./project/notes, which the skill's own P5 says have never existed. The dashboard registry still labels the domain 'Local RAG / DeepSeek-R1'.

### tools/vault_rag.py

`cli` · status `runs-today`

Paths: `tools/vault_rag.py`

The executable counterpart of local_rag_orchestration: it connects an Obsidian vault to local Ollama. Subcommands are status, index (chunk and embed into a stdlib JSON index), ask (QUERY mode with tier caps, think stripping, trace archival and eviction) and evict.

**Entry points**

- `python3 tools/vault_rag.py [--endpoint URL] status`
  - does: Reports: - endpoint reachability and served models - each tier model and the embed model: ok, or 'MISSING -- ollama pull <tag>' - index as 'index N chunks from <vault>' - build time and a PARTIAL flag - notes changed since the build ('N note(s) changed since -- reindex') or 'fresh'
  - changes: nothing
- `python3 tools/vault_rag.py index [--vault DIR] [--embed-model TAG]`
  - does: Chunks every *.md in the vault (default <repo>/vault), skipping dirs starting with _ or . plus SCHEMA.md and README.md. - chunks are 800 tokens with 120 overlap, paragraph-aligned, at chars/4 - reuses vectors of unchanged files by sha256[:16] - embeds through /api/embeddings with keep_alive 5m - saves a partial index every 20 new chunks - on embedding failure, saves a partial index and exits 1 - evicts the embed model on success
  - changes: state/rag_index/index.json (atomic, via index.json.tmp); Ollama resident-model state
- `python3 tools/vault_rag.py index --vault ../Creative-Writing`
  - does: index an external vault (docstring example)
  - changes: state/rag_index/index.json
- `python3 tools/vault_rag.py ask "<question>" [--tier sm|md] [--model TAG] [--top-k 8] [--rerank-to 4] [--max-words 250] [--json] [--write-dashboard]`
  - does: 1. Embeds the question with the index's embed_model, then evicts it 2. Takes the top-k by dot product and keeps up to rerank-to chunks within the tier payload cap (oversized chunks are skipped; if none fit, the best chunk is truncated) 3. Generates with QUERY_SUBPROMPT: no system field, temperature 0.6, top_p 0.95, tier num_ctx/num_predict, keep_alive 5m 4. Evicts the generator 5. Strips <think> and the 'ANSWER:' label 6. Reports window % and prints a notice at 60% or more
  - changes: state/rag_traces/<YYYYmmddTHHMMSSZ>.txt when a think block exists; dashboard.json hardware.local_llm.context_used_pct and loaded_tier only with --write-dashboard
- `python3 tools/vault_rag.py evict`
  - does: sends keep_alive:0 for every tier model and the embed model
  - changes: Ollama resident-model state
- `python3 tools/vault_rag.py --endpoint <URL> <subcommand>`
  - does: global override of the dashboard endpoint; also disables the WSL gateway auto-rewrite
  - changes: nothing extra

**Inputs**

- dashboard.json hardware.local_llm (endpoint, tiers[*].model, embed_model)
- vault directory (index)
- question text (ask)

**Outputs**

- answer text, or JSON {question, answer, model, tier, sources[{id, file, title, score}], context_used_pct}
- exit 0 = ok; 1 = index or answer problem, or model not served; 2 = endpoint unreachable (argparse usage errors also exit 2)

**Reads**

- dashboard.json
- vault/**/*.md (or --vault)
- state/rag_index/index.json
- /proc/version
- ip route show default

**Writes**

- state/rag_index/index.json
- state/rag_traces/*.txt
- dashboard.json (only with --write-dashboard)

**Depends on**

- python3 stdlib (no numpy or faiss)
- Ollama HTTP API

**Gates and checkpoints**

- require_model: exits 1 when the tag family is not served, suggesting 'ollama pull <tag>' or 'python3 tools/reconcile_models.py --write'
- warns when the index is partial
- prints a notice when the window reaches 60% or more
- never keeps the embed model and the generator resident together
- status calls resolve_endpoint first, so an unreachable Ollama exits 2 before the index is reported. The skill's P5 grep then says 'no index' even when one exists

**Invoked by**

- local_rag_orchestration P5 (status); operator directly (BOOT.md, OBSIDIAN.md)
- CI verify.yml ('--help' under -W error::EncodingWarning, plus the core-logic test of chunk, pack/unpack/normalize/dot and strip_frontmatter)

**Invokes**

- Ollama /api/tags, /api/embeddings and /api/generate (including the keep_alive 0 eviction)
- ip route show default (under WSL)

**Notes**

The existing state/rag_index/index.json: vault C:\Users\utopi\Creative-Writing (outside this repo), embed_model nomic-embed-text, built 2026-09-01T00:22:35Z, partial:false, 173 chunks, dims 768, about 1.18 MB. state/rag_traces/ is absent.

Not implemented: the gate-token check or stamp, the INDEX/QUERY/SYNTHESIS router, SYNTHESIS, the flush ledger and event_log writes.

TIER_LIMITS hardcodes num_ctx 8192/4096, payload 3000/1200 and num_predict 800/600 instead of reading dashboard tiers[*].context_window_tokens. The reasoning-reserve column is not enforced.

'ask' takes no --vault; it uses whatever vault the index was built from.

### state/rag_index/index.json (RAG vector index)

`data` · status `generated`

Paths: `state/rag_index/index.json`

Stdlib JSON vector index written by vault_rag.py index and read by ask and status.

**Outputs**

- {vault, embed_model, built, partial, chunks[{id c_NNNN, file, title, kind, file_hash, text, vec (base64 float32, normalised)}], dims}

**Invoked by**

- tools/vault_rag.py

**Notes**

Present and gitignored (state/). Built 2026-09-01T00:22:35Z from C:\Users\utopi\Creative-Writing with nomic-embed-text: 173 chunks, 768 dims, partial:false. It shows nomic-embed-text was served by the local Ollama on that date.

### Ollama local endpoint

`service` · status `runs-today`

Paths: `dashboard.json`

Local model server used for embeddings and generation, running on the Windows side of the laptop.

**Entry points**

- `GET {endpoint}/api/tags`
  - does: list served models
  - changes: nothing
- `POST {endpoint}/api/generate {model, prompt, stream:false, keep_alive:'5m', options{temperature 0.6, top_p 0.95, num_ctx, num_predict}}`
  - does: generation
  - changes: loads the model into memory
- `POST {endpoint}/api/embeddings {model, prompt, keep_alive:'5m'}`
  - does: embedding
  - changes: loads the embed model
- `POST {endpoint}/api/generate {model, keep_alive:0}`
  - does: evict a model
  - changes: unloads the model
- `ollama pull <tag> | ollama stop <model> | ollama rm | ollama serve | ollama list`
  - does: CLI actions cited in P2b, ARTIFACT B remedies, vault_rag error text and the dashboard _tiers_note
  - changes: model store or resident state

**Depends on**

- Ollama

**Environment and secret names (names only)**

- OLLAMA_HOST
- OLLAMA_ORIGINS (for Obsidian and hub clients, per OBSIDIAN.md; outside this subsystem)

**Gates and checkpoints**

- the tag must be served (P2b / require_model)
- WSL access needs OLLAMA_HOST=0.0.0.0 and an inbound firewall rule for 11434

**Invoked by**

- local_rag_orchestration
- tools/vault_rag.py
- tools/bootstrap.sh (/api/tags reachability)

**Notes**

dashboard.json hardware.local_llm.endpoint = http://localhost:11434. The existing index shows the service answered on 2026-09-01. Whether it is available now cannot be confirmed from the files.

### local_rag ARTIFACT A — Ollama request payloads

`protocol` · status `partial`

Paths: `skills/local_rag_orchestration.skill.md`

Canonical request bodies for generate, router_call and embed, and the laws that govern them.

**Inputs**

- {{RAG_ENDPOINT}}
- {{RAG_MODEL}}
- {{EMBED_MODEL}}
- {{subprompt_with_task_and_retrieval}}
- {{chunk_or_query}}

**Depends on**

- Ollama

**Gates and checkpoints**

- model and num_ctx come from dashboard tiers; the concrete values shown are the sm defaults and must not be hardcoded
- never raise num_ctx beyond the tier table
- keep_alive '5m' on every call
- no system field
- temperature 0.5–0.7
- never few-shot
- strip <think>
- router_call overrides: temperature 0.3, num_predict 400
- the embed model is a second resident model: index in one pass, evict it, then query

**Invoked by**

- local_rag_orchestration steps 1-5

**Invokes**

- Ollama endpoint

**Notes**

generate and embed are implemented in tools/vault_rag.py. No code found uses router_call.

### local_rag ARTIFACT B — routing sub-prompts

`data` · status `partial`

Paths: `skills/local_rag_orchestration.skill.md`

Five zero-shot prompts with described output formats:
- ROUTER_SUBPROMPT: final line 'MODE: <INDEX|QUERY|SYNTHESIS>'
- QUERY_SUBPROMPT: answer only from <RETRIEVAL>, cite [c_NNNN], at most {{max_words}} words, after an 'ANSWER:' line
- MAP_SUBPROMPT: ≤300-token note with DECISIONS, OPEN_QUESTIONS, FACTS, QUOTE_CANDIDATES
- REDUCE_SUBPROMPT: SUMMARY ≤150 words, TIMELINE, DECISIONS_IN_FORCE, CONTRADICTIONS, NEXT_ACTIONS, from the notes only
- FLUSH_SELFCHECK_SUBPROMPT: 'FLUSH: yes|no' at 60% of num_ctx, using chars/4

**Inputs**

- task_text
- question
- ranked_chunks_with_ids
- max_words
- doc_id
- doc_text
- n
- all_map_notes
- num_ctx
- char_count

**Invoked by**

- local_rag_orchestration

**Notes**

Only QUERY_SUBPROMPT is implemented: copied into tools/vault_rag.py with '--' in place of the em dash and {retrieval} in place of {{ranked_chunks_with_ids}}. vault_rag.py mentions FLUSH_SELFCHECK only in a comment.

### local_rag ARTIFACT C — flush checkpoint ledger (state/rag_flush_ledger.json)

`data` · status `specified-not-implemented`

Paths: `skills/local_rag_orchestration.skill.md`, `state/rag_flush_ledger.json`

Per-session ledger of every checkpoint (id, ts, purged, retained, window_pct_after) and the final eviction. Its law: every checkpoint writes an entry here BEFORE purging.

**Outputs**

- {session_id, mode, tier, num_ctx, checkpoints[], evicted{ts, model, keep_alive:0}, law}

**Gates and checkpoints**

- an unlogged flush never happened
- a session that ends with the model still resident has not ended

**Invoked by**

- local_rag_orchestration checkpoints F1-F4

**Notes**

The file is absent, and no code outside the skill writes it.

### ui_ux_intelligence (skill)

`skill` · status `runs-today`

Paths: `skills/ui_ux_intelligence.skill.md`

Design-system generation and UX audit over a vendored offline corpus: 79 searchable UI styles (50 active), 192 product palettes and reasoning profiles, 74 font pairings, 119 UX guidelines, 105 icons, 17 GSAP presets, 25 chart types and 22 stacks. It decides what a thing should look like; css_html_ui builds it. It is the sole author for product work, and for studio surfaces an upstream generator that needs operator approval.

**Entry points**

- `python3 --version >/dev/null 2>&1 && echo "OK:P2" || { python --version >/dev/null 2>&1 && echo "OK:P2 (use 'python')" || echo "FAIL:P2 Python 3 not on PATH"; }`
  - does: P2: Python present. Never install Python
  - changes: nothing
- `python3 -c "import csv,sys; sys.exit(0 if sum(1 for _ in csv.DictReader(open('tools/ui-ux-pro-max/data/ux-guidelines.csv',encoding='utf-8')))==119 else 1)"`
  - does: P3: vendored payload intact (exactly 119 UX rows)
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "keyboard focus modal" --domain ux -n 1 --json | python3 -c "...print('OK:P4' if d.get('results') else 'FAIL:P4 engine returned nothing')"`
  - does: P4: the locked smoke test
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n 1-20] [--full]`
  - does: Step 2 QUERY CONTRACT: one intent, 2-5 terms, one constraint; retry once
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system -p "Project Name" [--variance 1-10] [--motion 1-10] [--density 1-10]`
  - does: Step 3 GENERATE (product work only)
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --output-dir "<project-root>" [--page "dashboard"]`
  - does: Step 5 PERSIST (product work only). An existing MASTER.md is skipped unless --force is operator-authorised
  - changes: <project-root>/design-system/<slug>/MASTER.md and pages/<page>.md
- `python3 tools/ui-ux-pro-max/scripts/search.py "contrast ratio text legibility" --domain ux`
  - does: Step 7 AUDIT (accessibility)
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<stack keyword>" --stack <stack>`
  - does: Step 7 AUDIT (stack guidelines)
  - changes: nothing

**Inputs**

- design request or brief
- consumer classification: studio surface or product work
- detected stack (package.json deps, pubspec.yaml, *.xcodeproj/Package.swift, composer.json, React Native markers)
- existing design-system/<slug>/MASTER.md

**Outputs**

- resolved design system (pattern, style, palette, typography, effects, anti-patterns) with source_identities and source_derivations
- product work: design-system/<slug>/MASTER.md plus per-page overrides
- studio: a proposed diff against the token dictionary plus an impact statement, with no commit
- Content MD sections ## Method (Flush 1), ## Decisions in Force and ## Next Steps (Flush 2)
- dashboard.json: one phase write (pipeline.phases[*].progress_pct) and one event_log entry

**Reads**

- .task_scratch/attestation.txt
- tools/ui-ux-pro-max/data/*.csv
- design-system/<slug>/MASTER.md
- context/brand/visual_identity.context.md (§6 off-limits), typography_system.context.md (§3 scale, §6 scope), color_science.context.md. These are the mandatory_context files, authored:true and present
- skills/css_html_ui.skill.md ARTIFACT A (studio token authority; mutation_policy)
- control_room.html (impact analysis)
- vault/SCHEMA.md (Method rule)
- project manifests for stack detection

**Writes**

- <project-root>/design-system/<slug>/MASTER.md and pages/*.md (product only, via --persist --output-dir; --force needs explicit operator authorisation)
- Content MD in vault/ (## Method, ## Decisions in Force, ## Next Steps)
- dashboard.json pipeline.phases[*].progress_pct and one event_log entry
- Only after operator approval at ARTIFACT D step 4: context/brand/*.context.md, skills/css_html_ui.skill.md, control_room.html

**Depends on**

- python3 stdlib
- tools/ui-ux-pro-max (vendored, offline, no network)

**Gates and checkpoints**

- P1: attestation 'ROUTER INTERCEPT' (Router.md §6)
- P2: Python present. Never run winget, apt or brew; report the gap per the Router.md §4 mode gate and fall back to the three brand gates
- P3: payload has 119 UX rows
- P4: the smoke test returns results
- Anti-fabrication law: every recommendation must come from a returned search result. On 0 results, retry once; after that, label any fallback a built-in default
- Step 1 CLASSIFY, recorded in the attestation's KEY CONSTRAINTS EXTRACTED line
- V2: detect the stack, never assume it; ask if it cannot be detected
- V3: read an existing MASTER.md; --force requires operator authorisation
- Studio surfaces: css_html_ui ARTIFACT A mutation_policy 'operator-approval only; agent proposes, never commits token changes', enforced by check_palette_parity
- Audit against visual_identity §6 and, for studio surfaces, typography_system §3. The corpus 16px body minimum does not override the studio's 13px scale
- CONTEXT FLUSH 1 (step 4) and CONTEXT FLUSH 2 (step 8)

**Invoked by**

- Router trigger_a: 'design system', 'palette', 'colour scheme', 'font pairing', 'typography scale', 'style direction', 'UX review', 'accessibility audit', 'what should this look like', 'spacing scale', 'chart type', 'icon set'
- Router trigger_b: design-system/*/MASTER.md, tokens/design_tokens.json, pipeline phase skill=ui_ux_intelligence

**Invokes**

- tools/ui-ux-pro-max/scripts/search.py
- css_html_ui (downstream consumer of the ARTIFACT B handoff)
- operator (ARTIFACT D step 4)

**Notes**

ROUTING HEADER (verbatim): skill_id: ui_ux_intelligence | version: 1.0 | trigger_a: ["design system", "palette", "colour scheme", "font pairing", "typography scale", "style direction", "UX review", "accessibility audit", "what should this look like", "spacing scale", "chart type", "icon set"] | trigger_b: ["design-system/*/MASTER.md", "tokens/design_tokens.json", "pipeline phase skill=ui_ux_intelligence"] | mandatory_context: [visual_identity, typography_system, color_science] | host_kinds: [windows, wsl, linux] # stdlib Python 3, no network, no host bridge | writes_dashboard_keys: [pipeline.phases[*].progress_pct] | danger_class: LOW # reads a local corpus; the risk is a wrong recommendation, not a wrong write.

EXECUTION PROCESS: 1 CLASSIFY, 2 QUERY CONTRACT, 3 GENERATE (product), 4 CONTEXT FLUSH 1, 5 PERSIST (product), 6 PROPOSE (studio), 7 AUDIT, 8 CONTEXT FLUSH 2.

ARTIFACTS: A = domain routing table, B = design-system output contract, C = zero-result contract, D = gate regeneration protocol.

Evidence of use:
- dashboard event_log 2026-08-31T16:45:00Z: TOKENS_COMMITTED by ui_ux_intelligence 'under operator authorisation (ARTIFACT D loop)'
- vault/studio-os/ui/ui-ux-intelligence-integration.md records the smoke tests being run
- scripts/__pycache__/*.cpython-313.pyc exist, so the engine has executed on this machine

The same vault note lists the first product-work --persist run as 'Still untested'. No pipeline phase exists for this skill, so its writes_dashboard_keys target is currently unphased. design-system/ and tokens/design_tokens.json are both absent at the repo root. .task_scratch/ is absent, so P1 currently fails.

### tools/ui-ux-pro-max/scripts/search.py

`cli` · status `vendored`

Paths: `tools/ui-ux-pro-max/scripts/search.py`, `tools/ui-ux-pro-max/scripts/core.py`, `tools/ui-ux-pro-max/scripts/design_system.py`, `tools/ui-ux-pro-max/VENDOR.md`

Vendored BM25 search engine over the UI/UX CSV corpus, plus a design-system generator with optional Master + Overrides persistence.

**Entry points**

- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" [--domain|-d style|color|chart|landing|product|ux|typography|icons|gsap|react|web|google-fonts] [--max-results|-n 1-20 (default 3)] [--json] [--full]`
  - does: Domain search. When --domain is omitted the domain is auto-detected and the runner-up reported. Text output with 0 results prints 'No matches. This is not a match with an empty value -- ...' plus 'Closest known terms'. A legacy style label prints a cross-domain redirect instead. Icons queries containing 'lucide' abstain.
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --stack|-s <stack> [-n N] [--json] [--full]`
  - does: Stack guidelines. Filters rows to current or legacy status, and handles shadcn base variants
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --design-system|-ds [-p|--project-name NAME] [-f|--format ascii|markdown] [--json] [--variance 1-10] [--motion 1-10] [--density 1-10]`
  - does: Generate a full design-system recommendation. --json emits {design_system, persistence}. The design system takes priority over --stack and --domain
  - changes: nothing unless --persist
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist [-p NAME] [--output-dir|-o DIR] [--page NAME] [--force]`
  - does: Write <DIR or cwd>/design-system/<safe_slug(project_name)>/MASTER.md, plus pages/<slug>.md when --page is given. An existing MASTER.md returns status 'skipped_exists' unless --force. With --page, the page file is still written and status is 'success'. --force also overwrites the page file.
  - changes: <output-dir or cwd>/design-system/<slug>/ (the directories are created even when the write is skipped)

**Inputs**

- query string
- flags as listed

**Outputs**

- text or JSON results: {domain, query, file, count, results, auto_detected?, runner_up_domain?, redirect?, suggestions?, error?}
- design_system dict (ARTIFACT B keys plus 'reasoning_default')
- persistence {status, design_system_dir, master_file, created_files, message?}

**Reads**

- tools/ui-ux-pro-max/data/*.csv: styles, colors, charts, landing, products, ux-guidelines, typography, icons, motion, react-performance, app-interface, google-fonts, ui-reasoning
- tools/ui-ux-pro-max/data/stacks/*.csv (22 files)

**Writes**

- design-system/<slug>/MASTER.md and pages/*.md (only with --persist; atomic temp file, then link/replace)

**Depends on**

- python3 stdlib
- scripts/reasoning_contract.py (imported by design_system.py)

**Gates and checkpoints**

- --force is needed to overwrite an existing MASTER.md
- the dials are argparse-validated 1-10 and only apply with --design-system
- safe_slug prevents path traversal through project or page names

**Invoked by**

- ui_ux_intelligence skill (P4, steps 2, 3, 5, 7, ARTIFACT D step 1)
- context/brand/typography_system.context.md and color_science.context.md (cite search.py commands as evidence)
- hub/designer-pro.js (displays a search.py command string only; it does not run it)

**Invokes**

- core.search / core.search_stack
- design_system.generate_design_system / persist_design_system

**Notes**

Upstream nextlevelbuilder/ui-ux-pro-max-skill v2.13.0, MIT licence, 44 files, 3.11 MB. The payload sha256 is recorded in VENDOR.md, but no check verifies it.

LF line endings are kept byte-identical to upstream (.gitattributes 'tools/ui-ux-pro-max/** -text'). VENDOR.md says 'Local edits: None'.

AVAILABLE_STACKS (core.py STACK_CONFIG) has 22 entries: react, nextjs, vue, svelte, astro, swiftui, react-native, flutter, nuxtjs, nuxt-ui, html-tailwind, shadcn, jetpack-compose, threejs, angular, laravel, javafx, wpf, winui, avalonia, uno, uwp.

Without -p, project_name defaults to query.upper(). The generator fills built-in defaults when nothing matches (#2563EB, Inter, 'minimalism-and-swiss-style', 'Hero + Features + CTA'); source_identities/reasoning_default show when this happened.

### tools/ui-ux-pro-max/scripts/validate_data.py

`cli` · status `vendored`

Paths: `tools/ui-ux-pro-max/scripts/validate_data.py`

Upstream data-integrity guardrail for the vendored corpus. For each file it checks that the CSV exists, has every configured column, has no duplicate primary keys and has valid decision-rule JSON. It also checks the catalog and provenance JSON files.

**Entry points**

- `python validate_data.py (run from tools/ui-ux-pro-max/scripts/; it imports core and reasoning_contract by module name)`
  - does: validate every domain/stack CSV and the catalog, licence and provenance JSON
  - changes: nothing

**Outputs**

- exit 0 with no output on success; exit 1 with every problem printed

**Reads**

- tools/ui-ux-pro-max/data/*.csv
- tools/ui-ux-pro-max/data/stacks/*.csv
- tools/ui-ux-pro-max/data/catalog-summary.json
- tools/ui-ux-pro-max/data/google-font-licenses.json
- tools/ui-ux-pro-max/data/phosphor-icons-upstream.json
- tools/ui-ux-pro-max/data/data-provenance.json

**Depends on**

- python3 stdlib
- core.py
- reasoning_contract.py

**Notes**

Nothing outside the vendored directory references it: not the skill, not CI, not verify_system.py.

### tools/ui-ux-pro-max/scripts/reasoning_contract.py

`library` · status `vendored`

Paths: `tools/ui-ux-pro-max/scripts/reasoning_contract.py`

A closed, non-executable grammar for the design-system decision rules (CONDITION_SIGNALS such as if_dashboard or if_health). It provides parse_decision_rules and apply_decision_rules.

**Depends on**

- python3 stdlib

**Invoked by**

- scripts/design_system.py
- scripts/validate_data.py

### tools/ui-ux-pro-max/data (vendored corpus)

`data` · status `vendored`

Paths: `tools/ui-ux-pro-max/data/`

The CSV corpus and JSON catalogs behind search.py.
- 13 domain CSVs: styles, colors, charts, landing, products, ux-guidelines, typography, icons, motion, react-performance, app-interface, google-fonts, ui-reasoning
- 22 stack CSVs under stacks/
- catalog-summary.json, data-provenance.json, google-font-licenses.json, phosphor-icons-upstream.json

**Gates and checkpoints**

- ui_ux_intelligence P3 requires ux-guidelines.csv to have exactly 119 rows. The file is 120 lines, header plus 119

**Invoked by**

- search.py (the CSVs)
- validate_data.py (the CSVs and the 4 JSON files)
- hub/designer-pro.js (reads the CSVs over HTTP)

**Notes**

catalog-summary.json (verifiedAt 2026-08-26) matches the skill's counts: styles 88 total, 79 searchable, 50 active; products, palettes and reasoning profiles 192 each; font pairings 74; google fonts 1934; curated icons 105; UX guidelines 119; motion presets 17; chart types 25; stacks 22; stack guidelines 1260.

### ui_ux ARTIFACT A/B/C — domain routing table, output contract, zero-result contract

`protocol` · status `runs-today`

Paths: `skills/ui_ux_intelligence.skill.md`

A maps each need to a domain with an example query, and lists stacks.

B defines the --design-system --json handoff shape that css_html_ui consumes for product work: project_name, category, pattern, style, colors, typography, key_effects, anti_patterns, decision_rules, activated_rules, constraints, source_identities, source_derivations, severity, dials, motion_snippet, spacing_scale.

C: on 'Found: 0 results', retry once with a narrower query or an explicit --domain/--stack. If still empty, say there was no database match and label the fallback a built-in default. Never present a 0-result search as data.

**Gates and checkpoints**

- verify category before using anything else in B
- carry source_identities and source_derivations into the Content MD (Router.md §0 provenance)

**Invoked by**

- ui_ux_intelligence

**Notes**

Example queries in A:
- "entertainment social" --domain product
- "glassmorphism dark" --domain style
- "fintech trust" --domain color
- "playful modern" --domain typography
- "JetBrains Mono" --domain google-fonts
- "hero social-proof" --domain landing
- "real-time dashboard" --domain chart
- "error summary validation" --domain ux
- "decorative icon aria hidden" --domain icons
- "scroll reveal stagger" --domain gsap
- "rerender memo list" --domain react
- "accessibilityLabel safe-areas" --domain web

A's stack list names 21 stacks and omits jetpack-compose, which the engine supports; the skill intro says 22.

The real design_system dict also includes 'reasoning_default', which B does not list.

### ui_ux ARTIFACT D — gate regeneration protocol (studio surfaces)

`protocol` · status `runs-today`

Paths: `skills/ui_ux_intelligence.skill.md`

A four-step operator-approval loop for regenerating the three brand gates (visual_identity, typography_system, color_science). Those gates were transcribed from css_html_ui ARTIFACT A, and this skill is their declared regeneration path (DECISIONS.md § D9).

**Entry points**

- `python3 tools/ui-ux-pro-max/scripts/search.py "<studio brief>" --design-system --json`
  - does: Step 1 GENERATE: --design-system, --json, no --persist. The command is assembled from the flags ARTIFACT D names. Recorded runs used "studio creative tooling dark" (smoke test), then "creative studio control room dashboard dark instrumentation" and "internal operations monitoring dashboard telemetry"
  - changes: nothing

**Inputs**

- studio brief
- context/brand/*.context.md
- css_html_ui ARTIFACT A
- control_room.html

**Outputs**

- the generated system, a diff and an impact list, handed to the operator

**Reads**

- context/brand/*.context.md
- skills/css_html_ui.skill.md
- control_room.html

**Depends on**

- tools/ui-ux-pro-max/scripts/search.py
- check_palette_parity (tools/verify_system.py)

**Gates and checkpoints**

- 1 GENERATE: --design-system, --json, no --persist
- 2 DIFF against context/brand/*.context.md AND css_html_ui ARTIFACT A
- 3 IMPACT: name every control_room.html value that would move, and confirm whether check_palette_parity would still pass
- 4 PROPOSE: hand steps 1-3 to the operator and stop. 'Do not write any of the four files'
- Writing context/brand/*.context.md, skills/css_html_ui.skill.md or control_room.html from a search result without completing step 4 is an intercept violation

**Invoked by**

- ui_ux_intelligence step 6 (PROPOSE, studio surfaces)

**Invokes**

- search.py
- operator approval

**Notes**

One completed loop is recorded (dashboard event_log 2026-08-31T16:45:00Z, and the vault note):
- the control room was rethemed under operator authorisation
- WCAG fixes: accent.queued 2.23:1 to 5.55:1, ink.dim 3.78:1 to 6.34:1
- a contrast_floor block was added to css_html_ui ARTIFACT A
- check_palette_parity was green

check_palette_parity reads only control_room.html, not hub/.

### tools/verify_system.py

`cli` · status `runs-today`

Paths: `tools/verify_system.py`

Protocol integrity checker. For this subsystem it:
- checks each skill's mandatory_context and host_kinds headers, and scans fenced code for macOS-only invocations (all three skills)
- runs check_extracted_probe (extracted verify_compute.sh against ARTIFACT A)
- runs check_palette_parity (control_room.html --bg, --bg-raise, --bg-panel, --amber, --cyan, --alert, --queued against css_html_ui ARTIFACT A)

**Entry points**

- `python3 tools/verify_system.py`
  - does: run every check with human-readable output
  - changes: nothing
- `python3 tools/verify_system.py --quiet`
  - does: exit code only
  - changes: nothing

**Outputs**

- PASS/WARN/FAIL lines; exit 0 = consistent, 1 = at least one FAIL

**Reads**

- dashboard.json
- skills/*.skill.md
- skills/hardware_compute.skill.md (ARTIFACT A)
- tools/hw/verify_compute.sh (only if present)
- skills/css_html_ui.skill.md
- control_room.html
- Router.md
- router.js
- context/brand/
- context/domain/
- vault/

**Depends on**

- python3 stdlib

**Gates and checkpoints**

- fails on token drift
- fails when the extracted probe differs from ARTIFACT A (only when tools/hw/verify_compute.sh exists)
- fails when a skill's mandatory_context names an unknown gate or its host_kinds falls outside hardware.host_kind_enum

**Invoked by**

- CI verify.yml 'Protocol integrity' and 'Tools declare their encodings' (--quiet)
- ui_ux_intelligence ARTIFACT D step 3 (conceptually)
- tools/bootstrap.sh 'Next' hint
- BOOT.md

**Notes**

Read in full.

### .github/workflows/verify.yml (subsystem-relevant steps)

`ci` · status `runs-today`

Paths: `.github/workflows/verify.yml`

CI on push to main, pull_request and workflow_dispatch (ubuntu-latest, Python 3.11). Exercises protocol integrity, gate logic, probe extraction and execution, evaluator verdicts, and vault_rag help and core logic without Ollama.

**Entry points**

- `python3 tools/verify_system.py`
  - does: 'Protocol integrity'
  - changes: nothing
- `python3 tools/hw/test_gate.py`
  - does: 'Gate logic'
  - changes: transient state/compute_gate.json on the runner
- `python3 - skills/hardware_compute.skill.md > tools/hw/verify_compute.sh <<'PY' (regex extract) PY; bash -n tools/hw/verify_compute.sh; chmod +x; ./tools/hw/verify_compute.sh generic > /tmp/probe.json; python3 -c json.load`
  - does: 'Probe extracts and parses'
  - changes: runner workspace
- `python3 tools/hw/evaluate_gate.py --all --dry-run --probe /tmp/probe.json | grep -qE "— (PASS|DENY)"`
  - does: 'Evaluator runs against a live probe' (DENY is expected on CI)
  - changes: nothing
- `PYTHONWARNDEFAULTENCODING=1 python3 -W error::EncodingWarning tools/vault_rag.py --help (plus verify_system.py --quiet and reconcile_models.py --help)`
  - does: 'Tools declare their encodings'. evaluate_gate.py and test_gate.py are not included
  - changes: nothing
- `python3 -W error::EncodingWarning - <<'EOF' (imports tools/vault_rag.py; asserts on chunk(), pack/unpack/normalize/dot and strip_frontmatter) EOF`
  - does: 'vault_rag core logic'
  - changes: nothing

**Depends on**

- GitHub Actions
- actions/checkout@v4
- actions/setup-python@v5

**Environment and secret names (names only)**

- PYTHONWARNDEFAULTENCODING

**Invoked by**

- git push to main, pull_request, workflow_dispatch

**Invokes**

- tools/verify_system.py
- tools/hw/test_gate.py
- tools/hw/verify_compute.sh
- tools/hw/evaluate_gate.py
- tools/vault_rag.py
- tools/reconcile_models.py (--help only)

**Notes**

Nothing in CI exercises ui-ux-pro-max. Whether the workflow has actually run on GitHub cannot be confirmed from the checkout.

## Usage flows

### Compute gate cycle (hardware_compute guarding a heavy skill)

1. A heavy skill is routed: blender_python or local_rag_orchestration (danger_class LOCAL_COMPUTE_HEAVY, which fires trigger_b), or adobe_suite_uxp batch work (only through depends_on_skill and batch_2d; its danger_class is LOCAL_DESTRUCTIVE)
2. P1: grep .task_scratch/attestation.txt for 'ROUTER INTERCEPT'. No code writes this file
3. P2: detect STUDIO_HOST_KIND (windows|wsl|linux)
4. P3: awk, df and grep present
5. P4: under WSL, the PowerShell bridge must exist
6. V1: read the requester's workload class (llm_local_sm | llm_local_md | render_3d_cpu | batch_2d)
7. V2: pipeline_ethics governs preemption
8. UNPACK: extract ARTIFACT A to tools/hw/verify_compute.sh (bash tools/bootstrap.sh, or the agent) and chmod +x
9. ./tools/hw/verify_compute.sh <workload_class> > state/hw_probe_latest.json
10. python3 tools/hw/evaluate_gate.py <workload_class> (documented in BOOT.md, not named in the skill): checks the probe against ARTIFACT B (host, null and thermal laws), then single-flight against any existing state/compute_gate.json
11. PASS writes {verdict, workload, ts_epoch, ttl_seconds 1800, memory_budget_gb = dynamic_claim_limit_gb, probe_snapshot, consumed_by null, law}, exit 0. DENY writes {verdict, workload, ts_epoch, reasons}, prints remedies, exit 1. The skill's DENY side effects (phase blocked, system_status DEGRADED) are not implemented anywhere
12. CONTEXT FLUSH 1: dashboard hardware.* writeback. Agent-only; no code does it
13. HANDBACK to the Router. The consuming skill re-reads the token (consumed_by must be None) and then stamps consumed_by itself. Minting with --consume would make that re-check fail
14. CONTINUOUS MODE (skill only): for jobs over ~5 min, re-probe and re-evaluate every 5 minutes; two consecutive DENYs mean checkpoint and pause. No implementation exists

### Local RAG QUERY (as implemented by tools/vault_rag.py)

1. Skill prerequisites: - P1 attestation - P2 resolve endpoint and tier model from dashboard.json - P2a WSL gateway rewrite - P2b tag served - P3 fresh llm_local_sm (or llm_local_md) PASS token - P4 context_used_pct < 50 - P5 python3 tools/vault_rag.py status shows a fresh index
2. python3 tools/vault_rag.py ask "<question>" [--tier sm|md] [--json] [--write-dashboard]
3. Load state/rag_index/index.json (exit 1 if none), resolve the endpoint (exit 2 if unreachable), and require both the embed model and the tier model to be served (exit 1 if not)
4. Embed the question with the index's embed_model, then evict the embed model
5. Dot-product retrieve top-k 8 and keep up to 4 chunks within the tier payload cap (sm 3000 tok, md 1200 tok, at chars/4)
6. POST /api/generate with QUERY_SUBPROMPT: temperature 0.6, top_p 0.95, num_ctx 8192/4096, num_predict 800/600, keep_alive 5m, no system field. Evict the generator in finally
7. Strip <think> and archive it to state/rag_traces/<stamp>.txt; strip the 'ANSWER:' label; print the answer with [c_NNNN] sources and the window %
8. With --write-dashboard, write hardware.local_llm.context_used_pct and loaded_tier
9. Steps in the skill that the CLI does not do: CHECKPOINT-F2 event_log write, flush-ledger entry, consumed_by stamp on state/compute_gate.json

### Local RAG INDEX

1. python3 tools/vault_rag.py index [--vault <dir>] [--embed-model <tag>]
2. Resolve the endpoint (WSL rewrite if needed) and require the embed model (dashboard embed_model by default) to be served
3. Walk the vault's *.md, skipping _*/.* dirs and SCHEMA.md/README.md. Reuse vectors of unchanged files (sha256[:16]) when the vault and embed model match the old index
4. Chunk into 800-token paragraph-aligned pieces with 120-token overlap, and embed through /api/embeddings with keep_alive 5m
5. CHECKPOINT-F1: save a partial index every 20 newly embedded chunks. On embedding failure, save a partial index and exit 1
6. Write the final state/rag_index/index.json atomically (partial:false, dims), then evict the embed model

### Local RAG status and evict

1. python3 tools/vault_rag.py status: endpoint, served models, tier and embed presence, index chunk count, build time, PARTIAL flag, notes changed since the build. Exits 2 before reporting the index if Ollama is unreachable
2. python3 tools/vault_rag.py evict: keep_alive:0 for every tier model and the embed model

### Local RAG SYNTHESIS (specified only)

1. MODE ROUTE with ROUTER_SUBPROMPT (temperature 0.3, num_predict 400) returns 'MODE: SYNTHESIS'
2. MAP: one call per document with MAP_SUBPROMPT, producing a ≤300-token note in state/rag_notes/{doc}.md. CHECKPOINT-F3 evicts the source document
3. REDUCE: a single call with REDUCE_SUBPROMPT over the notes only
4. WINDOW REPORT, F4 final, EVICT with keep_alive 0, stamp consumed_by, and a ledger entry per checkpoint in state/rag_flush_ledger.json
5. Nothing outside the skill file implements this flow

### ui_ux_intelligence product-work design system

1. P1 attestation
2. P2 python3 present (never install it)
3. P3 ux-guidelines.csv has 119 rows
4. P4 smoke test: search.py "keyboard focus modal" --domain ux -n 1 --json returns results
5. Step 1 CLASSIFY as product work and record it in the attestation's KEY CONSTRAINTS EXTRACTED line
6. V2 detect the stack from project manifests
7. V3 read any existing design-system/<slug>/MASTER.md
8. Domain queries: search.py "<query>" --domain <domain> [-n N] [--full]. On 0 results, retry once per ARTIFACT C
9. GENERATE: search.py "<product_type> <industry> <keywords>" --design-system -p "Project Name" [--variance/--motion/--density 1-10]
10. CONTEXT FLUSH 1: write the resolved system and the query into the Content MD ## Method; discard the raw payloads
11. PERSIST: search.py "<query>" --design-system --persist -p "Project Name" --output-dir "<project-root>" [--page "dashboard"]. Use --force only with operator authorisation. This path is recorded as untested
12. AUDIT: search.py "contrast ratio text legibility" --domain ux, and search.py "<stack keyword>" --stack <stack>. Check against visual_identity §6
13. CONTEXT FLUSH 2: Content MD ## Decisions in Force and ## Next Steps, one dashboard phase write and one event_log entry. Hand the ARTIFACT B-shaped system to css_html_ui

### ui_ux_intelligence studio-surface change (ARTIFACT D loop)

1. CLASSIFY as a studio surface (control_room.html, hub/, HQ tooling); css_html_ui ARTIFACT A is the token authority
2. GENERATE: search.py "<studio brief>" --design-system --json (no --persist)
3. DIFF against context/brand/*.context.md and css_html_ui ARTIFACT A
4. IMPACT: list every control_room.html value that would move, and confirm whether check_palette_parity (python3 tools/verify_system.py) would still pass
5. PROPOSE to the operator and stop. Only after operator authorisation are context/brand/*.context.md, skills/css_html_ui.skill.md or control_room.html changed (one such run recorded on 2026-08-31)

### Bootstrap and CI verification

1. bash tools/bootstrap.sh (or --probe) runs: 1 host check 2 prerequisites 3 Ollama reachability and reconcile_models report 4 COM and Blender checks 5 extract ARTIFACT A to tools/hw/verify_compute.sh, bash -n, run the probe into state/hw_probe_latest.json 6 python3 tools/hw/evaluate_gate.py --all --dry-run --probe state/hw_probe_latest.json It mints no token
2. python3 tools/verify_system.py [--quiet]: check_skill_headers, check_host_portability, check_extracted_probe and check_palette_parity
3. CI (verify.yml): - verify_system.py - test_gate.py - probe extraction, bash -n and run on ubuntu - evaluator reaches a verdict - EncodingWarning checks (vault_rag --help among them) - vault_rag core-logic test

## Relationships

| From | Relation | To |
|---|---|---|
| local_rag_orchestration (skill) | depends_on_skill: needs a fresh, unconsumed PASS token for llm_local_sm, or llm_local_md when RAG_TIER=md (P3) | hardware_compute (skill) |
| hardware_compute (skill) | embeds it as ARTIFACT A; UNPACK writes it to tools/hw/verify_compute.sh | verify_compute.sh (hardware_compute ARTIFACT A, 'hardware probe v4') |
| hardware_compute (skill) | embeds | ARTIFACT B — threshold matrix, laws and remedies |
| hardware_compute (skill) | embeds the schema; mints and denies per steps 4-5 | Compute gate token (ARTIFACT C, state/compute_gate.json) |
| tools/hw/evaluate_gate.py | parses it at runtime from skills/hardware_compute.skill.md | ARTIFACT B — threshold matrix, laws and remedies |
| tools/hw/evaluate_gate.py | writes PASS/DENY; enforces single_flight_law by workload only | Compute gate token (ARTIFACT C, state/compute_gate.json) |
| tools/hw/evaluate_gate.py | consumes its JSON output (state/hw_probe_latest.json or --probe) | verify_compute.sh (hardware_compute ARTIFACT A, 'hardware probe v4') |
| tools/hw/test_gate.py | regression-tests it through subprocess | tools/hw/evaluate_gate.py |
| tools/bootstrap.sh | extracts it from the skill file and runs it with 'generic' | verify_compute.sh (hardware_compute ARTIFACT A, 'hardware probe v4') |
| tools/bootstrap.sh | runs --all --dry-run --probe state/hw_probe_latest.json | tools/hw/evaluate_gate.py |
| tools/bootstrap.sh | runs it in report mode with --endpoint <reached> (other subsystem) | tools/reconcile_models.py |
| tools/bootstrap.sh | checks reachability through /api/tags, retrying the WSL gateway | Ollama local endpoint |
| local_rag_orchestration (skill) | reads it at P3 and stamps consumed_by at step 8. vault_rag.py implements neither | Compute gate token (ARTIFACT C, state/compute_gate.json) |
| local_rag_orchestration (skill) | its declared implementation of status/index/ask/evict; P5 calls 'python3 tools/vault_rag.py status' | tools/vault_rag.py |
| tools/vault_rag.py | calls /api/tags, /api/embeddings and /api/generate (including the keep_alive 0 eviction) | Ollama local endpoint |
| tools/vault_rag.py | writes it (index) and reads it (ask, status) | state/rag_index/index.json (RAG vector index) |
| tools/vault_rag.py | reads hardware.local_llm endpoint, tiers and embed_model; with --write-dashboard, writes context_used_pct and… | dashboard.json |
| tools/vault_rag.py | suggests 'python3 tools/reconcile_models.py --write' when a model is not served (other subsystem) | tools/reconcile_models.py |
| local_rag_orchestration (skill) | embeds | local_rag ARTIFACT A — Ollama request payloads |
| local_rag_orchestration (skill) | embeds; only QUERY_SUBPROMPT is copied into vault_rag.py | local_rag ARTIFACT B — routing sub-prompts |
| local_rag_orchestration (skill) | specifies it; not implemented | local_rag ARTIFACT C — flush checkpoint ledger (state/rag_flush_ledger.json) |
| hub/ollama.js | browser-side mirror of the chunk/retrieve/QUERY prompt, calling Ollama directly with no gate check (hub subsy… | tools/vault_rag.py |
| router.js | reads and renders hardware.* including local_llm.loaded_tier and context_used_pct; never writes the DENY-side… | dashboard.json |
| ui_ux_intelligence (skill) | issues every search, design-system, persist and audit command | tools/ui-ux-pro-max/scripts/search.py |
| tools/ui-ux-pro-max/scripts/search.py | BM25 search over the CSVs | tools/ui-ux-pro-max/data (vendored corpus) |
| tools/ui-ux-pro-max/scripts/search.py | design_system.py imports apply_decision_rules and parse_decision_rules | tools/ui-ux-pro-max/scripts/reasoning_contract.py |
| tools/ui-ux-pro-max/scripts/validate_data.py | validates the CSVs and JSON catalogs | tools/ui-ux-pro-max/data (vendored corpus) |
| hub/designer-pro.js | reads the CSVs over HTTP (token overlap, not BM25) and shows search.py commands (hub subsystem) | tools/ui-ux-pro-max/data (vendored corpus) |
| ui_ux_intelligence (skill) | embeds it; it governs studio-surface changes | ui_ux ARTIFACT D — gate regeneration protocol (studio surfaces) |
| ui_ux ARTIFACT D — gate regeneration protocol (studio surfaces) | step 3 IMPACT must confirm check_palette_parity would still pass | tools/verify_system.py |
| ui_ux_intelligence (skill) | embeds | ui_ux ARTIFACT A/B/C — domain routing table, output contract, zero-result contract |
| ui_ux_intelligence (skill) | Upstream generator. It hands the ARTIFACT B design_system to css_html_ui for product work. css_html_ui ARTIFA… | css_html_ui skill (skills/css_html_ui.skill.md) |
| ui_ux_intelligence (skill) | mandatory_context (authored:true); ARTIFACT D is their declared regeneration path; typography_system and colo… | context/brand/visual_identity, typography_system, color_science |
| hardware_compute (skill) | gates it (render_3d_cpu). blender P4 re-checks the token; step 2 CLAIM THE GATE writes consumed_by: blender_p… | blender_python skill (skills/blender_python.skill.md) |
| hardware_compute (skill) | declared dependency (depends_on_skill, workload_class batch_2d). adobe_suite_uxp has danger_class LOCAL_DESTR… | adobe_suite_uxp skill (skills/adobe_suite_uxp.skill.md) |
| hardware_compute (skill) | HANDBACK target. The Router's Trigger A table and §10 refusal 'skip hardware verification' route to it. P1 ex… | Router (Router.md) |
| tools/verify_system.py | check_extracted_probe fails if the extracted copy drifts from ARTIFACT A | verify_compute.sh (hardware_compute ARTIFACT A, 'hardware probe v4') |
| tools/verify_system.py | check_skill_headers and check_host_portability validate mandatory_context and host_kinds (all three in-scope… | hardware_compute (skill) |
| .github/workflows/verify.yml (subsystem-relevant steps) | runs it | tools/hw/test_gate.py |
| .github/workflows/verify.yml (subsystem-relevant steps) | extracts it, runs bash -n, and runs it on ubuntu (Linux branch only) | verify_compute.sh (hardware_compute ARTIFACT A, 'hardware probe v4') |
| .github/workflows/verify.yml (subsystem-relevant steps) | smoke-tests --help and the core logic | tools/vault_rag.py |

**Open questions the files could not settle**

- No code writes .task_scratch/attestation.txt: Router.md §6 only says to 'print' the attestation block. Is P1 meant to be satisfied by the agent writing that file by hand? As things stand, P1 fails in every skill.
- No script implements hardware_compute step 8 (continuous mode), the dashboard hardware.* writeback, system_status.state=DEGRADED, or phase=blocked on DENY. router.js only renders. Are these agent-only duties?
- tools/vault_rag.py and hub/ollama.js load models without checking or stamping state/compute_gate.json. Is the gate meant to apply only when an agent follows the skill?
- Single-flight differs between skill and code. The skill allows minting once the live token has been consumed by a finished skill; evaluate_gate.py denies any live PASS token held by another workload whatever consumed_by says, and silently re-mints (clearing consumed_by) for the same workload. Which is authoritative?
- 'evaluate_gate.py <cls> --consume <skill>' (documented in BOOT.md) conflicts with blender_python P4 and local_rag P3, which both require consumed_by to be None. Which side should change?
- adobe_suite_uxp declares depends_on_skill hardware_compute and workload_class batch_2d, but its danger_class is LOCAL_DESTRUCTIVE and it has no token-check code. Does the gate actually apply to it?
- Has bootstrap.sh ever run on this machine? tools/hw/verify_compute.sh, state/hw_probe_latest.json, state/compute_gate.json and .task_scratch/ are all absent. Per BOOT.md and DECISIONS D8, the probe's Windows/WSL branches have never run on the target laptop.
- The mandatory contexts pipeline_ethics, render_philosophy and memory_discipline are authored:false and absent. Per Router §5 and dashboard blocked_reason, can hardware_compute or local_rag_orchestration route at all today (L3 park), or only through L1/L2 vault derivation?
- evaluate_gate.py and test_gate.py read and write files without an explicit encoding and are left out of CI's EncodingWarning step. On Windows (cp1252) this may garble or fail when reading the UTF-8 skill file; it has not been verified on the target.
- ui_ux_intelligence has no pipeline phase in dashboard.json, yet writes_dashboard_keys names pipeline.phases[*].progress_pct. Which phase should its flush write to?
- ARTIFACT D step 4 says 'Do not write any of the four files', but the following paragraph lists context/brand/*.context.md (three gate files), skills/css_html_ui.skill.md and control_room.html. Which four are meant?
- The skill numbering is inconsistent: local_rag '7/8', hardware_compute '8/8', ui_ux_intelligence '9/9'. The dashboard registry still labels local_rag 'Local RAG / DeepSeek-R1', and local_rag trigger_b names ./project/docs and ./project/notes, which the skill itself says never existed.
- The dashboard tier tags (llama3.1:8b, mistral-nemo:12b) are PROVISIONAL, and DECISIONS D8 says reconcile_models.py has only been run against a stub. Are the generator models actually served? Only nomic-embed-text is evidenced, by the index.
- The VENDOR.md payload sha256 is never verified by verify_system.py; the vault note proposes a check_vendor_hash. The vendored scripts/__pycache__ currently exists despite VENDOR.md's exclusion note.

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: A requesting skill with danger_class LOCAL_COMPUTE_HEAVY (blender_python, local_rag_orchestration, batch adobe_suite_uxp) triggers hardware_compute via the Router (trigger_b)
  - evidence: skills/adobe_suite_uxp.skill.md lines 16-18 declare danger_class: LOCAL_DESTRUCTIVE, depends_on_skill: hardware_compute.skill.md and workload_class: batch_2d. Trigger_b ('declares danger_class: LOCAL_COMPUTE_HEAVY') therefore does not match it. The file also contains no compute_gate token check (grep finds no PASS/token/compute_gate).
- **corrected**: Usage flow: the requesting skill writes consumed_by, or equivalently runs evaluate_gate.py --consume <skill_id>
  - evidence: tools/hw/evaluate_gate.py mint() writes consumed_by at mint time. skills/blender_python.skill.md P4 (lines 90-104) and local_rag_orchestration P3 (lines 73-88) both fail when consumed_by is not None. A token minted with --consume, as documented in BOOT.md §4, therefore fails the consuming skill's own precheck.
- **added**: evaluate_gate.py 'Refreshing a token for the same workload is allowed' (with no further consequence stated)
  - evidence: tools/hw/evaluate_gate.py single_flight() returns None when tok.workload == cls, and mint() rewrites the whole token with consumed_by=None (or the --consume value). Re-minting therefore clears a previous consumer's stamp, which contradicts ARTIFACT C's 'a consumed token cannot authorize a second job'.
- **corrected**: Skill step 5 PASS token {verdict, workload, ts_epoch, probe...}
  - evidence: skills/hardware_compute.skill.md line 121 uses a 'probe' field, while ARTIFACT C (lines 405-415) and evaluate_gate.py use 'probe_snapshot' plus ttl_seconds, memory_budget_gb, consumed_by and law. The skill is internally inconsistent.
- **corrected**: verify_compute.sh host.kind values / 'macos is recognised'
  - evidence: In ARTIFACT A, the probe's uname case (skills/hardware_compute.skill.md lines 145-154) has no Darwin branch, so macOS reports host.kind 'unknown'. Only the P2 prerequisite block and bootstrap.sh map Darwin to 'macos'.
- **corrected**: verify_compute.sh reads 'df -Pk . and df -Pk /'
  - evidence: ARTIFACT A lines 303-309: df -Pk . is used for disk.free_gb on every host, and df -Pk / only on the linux branch. Windows and WSL read system_free_gb from Win32_LogicalDisk C:. disk.free_gb goes through num(), so an unreadable value becomes 0 rather than null.
- **added**: verify_compute.sh status (implicitly working on the target machine)
  - evidence: BOOT.md 'Known unknowns' and DECISIONS.md D8 'Not yet done' both say the Windows and WSL branches (every psq query) have never run on the target laptop. Only the Linux branch has been exercised, in CI.
- **corrected**: tools/bootstrap.sh status runs-today; invokes only verify_compute.sh and evaluate_gate.py; exits 1 on hard prerequisite failure
  - evidence: tools/bootstrap.sh read in full. - It also invokes 'python3 tools/reconcile_models.py --endpoint "$REACHED"' (report-only), curl <endpoint>/api/tags, PowerShell Test-Path on HKLM Classes for Photoshop/Illustrator/AfterFX, and <blender> --version. - It exits 2 when not run under the repo (no Router.md or skills/) and exits 1 when the probe emits invalid JSON. - --probe skips sections 2-4 (prerequisites, Ollama and native bridges). - There are no run artefacts in this checkout, and DECISIONS D8 says the COM probe has never run on the target, so status is set to never-exercised.
- **corrected**: verify_system.py: 'Only lines 195-305 were read'; entry point takes no flags
  - evidence: tools/verify_system.py read in full. - It supports --quiet and exits 0 or 1. - check_skill_headers validates mandatory_context and check_host_portability validates host_kinds and fenced code for all three in-scope skills. - check_palette_parity compares --bg, --bg-raise, --bg-panel, --amber, --cyan, --alert and --queued.
- **corrected**: Open question: the authoritative AVAILABLE_STACKS (core.py STACK_CONFIG) was not read
  - evidence: tools/ui-ux-pro-max/scripts/core.py lines 89-112 and 195: STACK_CONFIG has 22 keys, including jetpack-compose. The skill's ARTIFACT A lists 21 stacks and omits jetpack-compose. The search.py docstring lists 16.
- **corrected**: search.py --persist: 'skips an existing MASTER.md (status skipped_exists) unless --force'
  - evidence: design_system.py persist_design_system (lines 995-1073): - It creates design-system/<slug>/ and pages/ before writing. - With --page and an existing MASTER.md, it still writes pages/<page>.md and returns status 'success'. - --force also overwrites the page file. - The slug is safe_slug(project_name), and project_name defaults to query.upper() when -p is omitted (line 522).
- **added**: ARTIFACT B lists the complete design_system key set
  - evidence: design_system.py generate() (lines 521-604) also returns 'reasoning_default'. When nothing matches, it silently fills built-in defaults: #2563EB, Inter, minimalism-and-swiss-style, 'Hero + Features + CTA'.
- **added**: Tool inventory for tools/ui-ux-pro-max is search.py/core.py/design_system.py/data
  - evidence: On disk there is also scripts/validate_data.py (a standalone data validator, 'python validate_data.py', exit 0 or 1, referenced nowhere outside the vendored directory) and scripts/reasoning_contract.py (imported by design_system.py and validate_data.py). data/ also holds catalog-summary.json, data-provenance.json, google-font-licenses.json and phosphor-icons-upstream.json, which only validate_data.py reads.
- **added**: ui_ux_intelligence runs today (evidence limited to the dashboard event_log)
  - evidence: tools/ui-ux-pro-max/scripts/__pycache__/ holds core, design_system and reasoning_contract .cpython-313.pyc files (VENDOR.md says __pycache__ was excluded when vendoring). vault/studio-os/ui/ui-ux-intelligence-integration.md records the smoke-test commands, and its Next Steps say the product-work '--design-system --persist --output-dir' path is 'Still untested'.
- **added**: ui_ux_intelligence trigger_b targets exist
  - evidence: There is no design-system/ and no tokens/ directory at the repo root, so neither trigger_b file target (design-system/*/MASTER.md, tokens/design_tokens.json) exists. css_html_ui ARTIFACT A is titled '→ tokens/design_tokens.json'.
- **added**: P1 attestation fails because .task_scratch/ is absent
  - evidence: No file in the repo writes .task_scratch/attestation.txt. Nine skills grep it, and bootstrap.sh only does mkdir -p .task_scratch. Router.md §6 tells the agent to 'print' the ROUTER INTERCEPT block, not write it to that file.
- **added**: vault_rag.py uses 'same tier table' as the skill/dashboard
  - evidence: tools/vault_rag.py lines 70-73: TIER_LIMITS hardcodes num_ctx 8192/4096, payload 3000/1200 and num_predict 800/600. It never reads dashboard tiers[*].context_window_tokens and does not enforce the reasoning-reserve column.
- **corrected**: vault_rag exit codes 0/1/2
  - evidence: tools/vault_rag.py docstring gives 0 ok, 1 index/answer problem, 2 endpoint unreachable. argparse usage errors also exit 2, so 2 is ambiguous.
- **added**: RAG index exists, built 2026-09-01
  - evidence: state/rag_index/index.json head and tail: vault C:\Users\utopi\Creative-Writing, embed_model nomic-embed-text, built 2026-09-01T00:22:35.909751+00:00, partial false, dims 768, 173 chunk ids.
- **added**: ARTIFACT B remedies are applied on DENY
  - evidence: tools/hw/evaluate_gate.py REMEDY_FOR has no mapping for 'low battery on ac', and no threshold names power.battery_pct. The 'swap rising' two-probe rule is not implemented. A host_law (host.kind) failure gets no remedy.
- **added**: evaluate_gate.py / test_gate.py encoding discipline
  - evidence: evaluate_gate.py calls SKILL.read_text(), TOKEN.read_text(), path.read_text() and TOKEN.write_text() without an encoding, and test_gate.py does the same for its token I/O. CI's 'Tools declare their encodings' step covers only verify_system.py, reconcile_models.py and vault_rag.py.
- **added**: Router: PASS token comes from verify_compute.sh
  - evidence: Router.md §10 line 355 says 'run compute-heavy work without a fresh PASS token from verify_compute.sh', but verify_compute.sh only probes. evaluate_gate.py (or the agent following steps 3-5) mints the token.
- **added**: local_rag_orchestration mandatory context is only memory_discipline
  - evidence: Router.md §3 routing table (line 158) also lists pipeline_ethics under 'Also load if flagged in dashboard' for local_rag_orchestration.
- **added**: hardware_compute P3 prints FAIL on unsupported hosts
  - evidence: skills/hardware_compute.skill.md lines 74-80: REQ is set only for windows|wsl|linux. For macos or unknown the loop body never runs and 'OK:P3' still prints.
- **corrected**: env_and_secrets for local_rag includes 'EMBED_MODEL' and RAG_ENDPOINT/WIN_HOST as env
  - evidence: In the skill, {{EMBED_MODEL}}, {{RAG_ENDPOINT}} and {{RAG_MODEL}} are ARTIFACT A template placeholders. RAG_ENDPOINT and WIN_HOST are plain shell variables. Only RAG_TIER (read from the environment) and RAG_MODEL (passed as an env var to the P2b python) are real env inputs.
- **unverifiable**: Ollama endpoint status runs-today
  - evidence: Kept, with a note. The index proves the embed model was served on 2026-09-01. Current availability cannot be checked from the files, and DECISIONS.md D8 says reconcile_models.py was only run against a stub endpoint.
- **unverifiable**: CI verify.yml status runs-today
  - evidence: Kept. The workflow file exists and is well formed, but whether it has run on GitHub cannot be determined from the checkout.
- **added**: Cross-subsystem consumers of this subsystem
  - evidence: hub/ollama.js mirrors vault_rag.py's chunking, retrieval and prompt in the browser (lines 3, 11, 104, 142) and does no gate check. hub/designer-pro.js reads tools/ui-ux-pro-max/data/ CSVs over HTTP and displays search.py commands. router.js renderHardware reads hardware.local_llm.loaded_tier and context_used_pct and writes nothing.
