# Hardware gate toolchain

Subsystem `hw-gate` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.92 · 11 entries · 24 corrections made to the first reading.

## Summary

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

## Tools

### bootstrap.sh

`launcher` · status `never-exercised`

Paths: `tools/bootstrap.sh`

First-boot and re-probe script. It identifies the shell (host kind), checks hard and soft prerequisites, checks Ollama reachability (retargeting to the WSL gateway when needed), checks Adobe COM registrations and Blender, extracts the probe from ARTIFACT A, runs it, and prints a dry-run gate survey of every workload class.

**Entry points**

- `bash tools/bootstrap.sh`
  - does: Full first boot. Runs these sections: 1 Host, 2 Prerequisites, 3 Local models (Ollama), 4 Native bridges, 5 Probe (extract ARTIFACT A, chmod +x, bash -n, run the probe, print a summary), 6 Workload classes (evaluate_gate --all --dry-run). It then prints a 'Next' block.
  - changes: mkdir -p state tools/hw .task_scratch. Overwrites tools/hw/verify_compute.sh (truncated or empty if extraction fails) and runs chmod +x on it. Overwrites state/hw_probe_latest.json (only if HARD_FAIL is 0). Mints no token. Calls reconcile_models.py without --write, so dashboard.json is not written.
- `bash tools/bootstrap.sh --probe`
  - does: Re-probe only. Sets PROBE_ONLY=1 and skips sections 2-4 (prerequisites, Ollama/reconcile, native bridges). Still runs host detection, extraction, the probe and the dry-run survey. Only the first argument is tested (`[ "${1:-}" = "--probe" ]`); any other argument is silently ignored.
  - changes: state/, tools/hw/ and .task_scratch/ directories; tools/hw/verify_compute.sh; state/hw_probe_latest.json

**Inputs**

- optional first argument --probe
- env WSL_DISTRO_NAME
- env BLENDER_BIN
- output of uname -s
- /proc/version

**Outputs**

- coloured ok/warn/FAIL console report, one section per step
- probe summary lines (machine, memory, power, thermal, gpu)
- evaluate_gate --all --dry-run output with stdout and stderr merged (2>&1), each line indented by one space by sed
- reconcile_models.py stdout report (its stderr is discarded)
- 'Next' block recommending python3 tools/verify_system.py and authoring context/brand or vault Content MDs
- Exit codes. 0 = reached the end: the last command is `echo`, so this holds even when every class is DENY. `set -o pipefail` is on but there is no `set -e` and the pipeline status is never checked. 1 = HARD_FAIL (checked after section 5) or the probe emitted invalid JSON. 2 = the cd failed, or the Router.md / skills/ landmark is missing. The header comment only documents 0 and 1.

**Reads**

- Router.md (existence landmark only)
- skills/ (existence landmark)
- skills/hardware_compute.skill.md (ARTIFACT A via regex r"### ARTIFACT A.*?\n```bash\n(.*?)\n```" with re.S; open() with no encoding)
- dashboard.json -> hardware.local_llm.endpoint (python3 -c with open(), no encoding)
- state/hw_probe_latest.json (json.load for validation and summary)
- Windows registry HKLM:\SOFTWARE\Classes\{Photoshop.Application, Illustrator.Application, AfterFX.Application} via PowerShell Test-Path, only when a PowerShell binary is found, on any host kind
- {endpoint}/api/tags via curl -s --max-time 4
- default gateway via `ip route show default | awk '{print $3; exit}'` (only on wsl, and only after the first curl fails)

**Writes**

- tools/hw/verify_compute.sh (generated, gitignored)
- state/hw_probe_latest.json
- directories state/, tools/hw/, .task_scratch/

**Depends on**

- bash
- python3
- curl
- awk
- df (checked as a prerequisite; used by the probe)
- grep
- sed
- wc
- tr
- head
- chmod
- ip (iproute2; WSL gateway lookup)
- powershell.exe | pwsh.exe | pwsh (first found on PATH)
- Ollama HTTP API (endpoint from dashboard.json, currently http://localhost:11434)
- Blender binary (optional; runs `<blender> --version`)
- Photoshop/Illustrator/After Effects COM ProgIDs (optional; registry check only)

**Environment and secret names (names only)**

- WSL_DISTRO_NAME
- BLENDER_BIN

**Gates and checkpoints**

- Repo-root landmark: cd "${0%/*}/.." (SELF_DIR falls back to '.'). Exits 2 if the cd fails or Router.md / skills/ are absent.
- Host refusal: macos (Darwin) calls bad() with a message citing DECISIONS.md § D8; unknown uname calls bad(). HARD_FAIL is only checked after section 5. In full mode, sections 2-4 (including reconcile_models if Ollama is reachable) and the ARTIFACT A extraction still run on a refused host before it exits 1, and the probe itself does not run.
- Hard prerequisites (full mode only): python3, curl, awk, df, grep. On windows/wsl a PowerShell bridge is also required (the message cites wsl_memory_law).
- Soft checks (warn only): Ollama reachability; COM ProgID registration via Test-Path on the registry, deliberately not New-Object, which would launch Photoshop; Blender presence.
- Extraction: a missing skill file, an empty extraction (for example ARTIFACT A not found) or a bash -n failure calls bad(), which sets HARD_FAIL and leads to exit 1.
- The probe output must parse as JSON; otherwise bad() is called and the script exits 1.
- Mints no gate token: the evaluator is always called with --dry-run.

**Invoked by**

- operator per BOOT.md (bash tools/bootstrap.sh; bash tools/bootstrap.sh --probe)
- README.md and DECISIONS.md § D8 (documented)
- evaluate_gate.py die() message when the probe is missing
- verify_system.py check_extracted_probe drift message ('re-run tools/bootstrap.sh')

**Invokes**

- python3 tools/reconcile_models.py --endpoint "$REACHED" (stderr discarded; any nonzero exit, including 1 = drift, prints 'could not reconcile the model registry')
- inline python3 heredoc extractor for ARTIFACT A
- bash -n tools/hw/verify_compute.sh
- ./tools/hw/verify_compute.sh generic > state/hw_probe_latest.json 2>/dev/null
- python3 tools/hw/evaluate_gate.py --all --dry-run --probe state/hw_probe_latest.json 2>&1 | sed 's/^/ /'
- <PWSH> -NoProfile -NonInteractive -Command "if (Test-Path 'HKLM:\SOFTWARE\Classes\<ProgID>') {'yes'} else {'no'}"
- <blender> --version

**Notes**

Shell detection is identical to skill P2 and differs from the probe: bootstrap maps Darwin to macos, the probe maps it to unknown. WSL Ollama retarget: the host part of the endpoint URL is replaced with sed "s#//[^:/]*#//$GW#", and warnings mention OLLAMA_HOST=0.0.0.0 and an inbound rule for port 11434. Blender search order: $BLENDER_BIN, then `command -v blender`, then /c/Program Files/Blender Foundation/Blender*/blender.exe, then /mnt/c/Program Files/Blender Foundation/Blender*/blender.exe (first executable match). The header says it 'mutates nothing outside state/ and tools/hw/' (BOOT.md repeats this), but it also runs mkdir -p .task_scratch, which is gitignored. In --probe mode the PowerShell prerequisite is not checked, so a missing bridge only shows up as null probe fields and DENY verdicts. If extraction fails, a truncated or empty (or bash -n-broken) tools/hw/verify_compute.sh is left on disk. All inline Python uses open() with no explicit encoding. Git history shows the UTF-8 commit 266ec99 did not touch this file. Status: DECISIONS.md says bootstrap's COM-registration probe has never run on the target machine. No file records bootstrap as a whole having run anywhere, and none of its outputs exist on disk.

### verify_compute.sh (ARTIFACT A hardware probe)

`cli` · status `generated`

Paths: `tools/hw/verify_compute.sh`, `skills/hardware_compute.skill.md`

Read-only hardware probe that emits one JSON object describing the host/shell kind, machine identity, GPU, memory (with a dynamic claim limit), power, thermal readings and disk headroom. Its source of truth is the ```bash block under '### ARTIFACT A' in the skill file.

**Entry points**

- `./tools/hw/verify_compute.sh generic > state/hw_probe_latest.json`
  - does: Probe as run by bootstrap.sh (stderr discarded)
  - changes: nothing itself; the redirect writes state/hw_probe_latest.json
- `./tools/hw/verify_compute.sh {{workload_class}} > state/hw_probe_latest.json`
  - does: Probe as specified in skill §2 step 2 (RUN VERIFICATION), agent-executed
  - changes: state/hw_probe_latest.json via the redirect
- `./tools/hw/verify_compute.sh generic | python3 -m json.tool`
  - does: Debug view given in BOOT.md Known unknowns
  - changes: nothing
- `./tools/hw/verify_compute.sh generic > /tmp/probe.json`
  - does: CI 'Probe extracts and parses' step (Linux branch)
  - changes: /tmp/probe.json on the runner

**Inputs**

- $1 workload class (default 'generic'); only echoed into the 'workload' field and does not change what is probed
- env WSL_DISTRO_NAME

**Outputs**

- stdout JSON: {workload, ts_epoch, host{name,kind,machine}, gpu{status,name,vram_total_gb:null,memory_shared_with_system}, memory{total_gb,available_gb,free_pct,swap_used_mb,dynamic_claim_limit_gb}, power{source,battery_pct}, thermal{cpu_temp_c,cpu_perf_pct}, disk{free_gb,system_free_gb}}
- Unreadable metrics are emitted as null via jnum(), never as a fake 0. Exceptions: disk.free_gb (all hosts) and disk.system_free_gb (non-windows/wsl) use num(), which defaults to 0.

**Reads**

- uname -s, /proc/version, hostname, date +%s
- windows/wsl via PowerShell CIM through the psq() helper (`try { ... } catch { '' }`, first non-empty line):
- - Win32_ComputerSystem.TotalPhysicalMemory and .Model
- - Win32_PerfFormattedData_PerfOS_Memory.AvailableMBytes, falling back to Win32_OperatingSystem.FreePhysicalMemory
- - Win32_PageFileUsage.CurrentUsage (sum)
- - Win32_ComputerSystemProduct.Version
- - Win32_VideoController.Name (first)
- - Win32_Battery: BatteryStatus, EstimatedChargeRemaining and device count
- - root/wmi MSAcpi_ThermalZoneTemperature.CurrentTemperature
- - Win32_PerfFormattedData_Counters_ProcessorInformation where Name='_Total': PercentProcessorPerformance
- - Win32_LogicalDisk DeviceID='C:' FreeSpace
- linux/unknown:
- - /proc/meminfo (MemTotal, MemAvailable, SwapTotal, SwapFree)
- - /sys/class/dmi/id/product_version, falling back to product_name
- - lspci (vga|3d controller)
- - /sys/class/power_supply/A{C,DP}*/online
- - /sys/class/power_supply/BAT*/capacity
- - /sys/class/thermal/thermal_zone0/temp, or sensors (Tctl|Tdie|Package id 0)
- - /proc/cpuinfo 'cpu MHz' and /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq
- - df -Pk /
- all hosts: nvidia-smi presence (switches gpu.status to 'discrete'); df -Pk . for the repo volume

**Writes**

- stdout only (header: 'Never mutates system state')

**Depends on**

- bash
- awk
- grep
- sed
- cut
- head
- tr
- cat
- ls
- df
- hostname
- date
- powershell.exe | pwsh.exe | pwsh (windows/wsl)
- lspci (optional)
- sensors (optional)
- nvidia-smi (only as a detector)

**Environment and secret names (names only)**

- WSL_DISTRO_NAME

**Gates and checkpoints**

- wsl_memory_law: on windows or wsl, memory is read only through PowerShell and /proc/meminfo is never used; with no bridge the memory fields are null.
- dynamic_claim_limit_gb = floor(60% of available_gb), reduced so that total_gb - claim >= 4, floored at 0; null if either input is null. free_pct = available*100/total, or null.
- Power on windows/wsl: BatteryStatus 1 gives 'battery'. Any other all-digit value (0, 2-11, or higher) gives 'ac'. Empty with a Win32_Battery count of 0 gives 'ac'. Empty with an unreadable count, or a non-numeric value, gives null. On linux the first readable A{C,DP}*/online decides; with no BAT* device it is 'ac'.
- bootstrap.sh and CI run bash -n on the extracted file. verify_system.py check_extracted_probe fails if the extracted file differs from ARTIFACT A (compared after strip(); skipped when the file is absent).
- CI extracts it, runs bash -n, runs it with 'generic' on ubuntu-latest, and validates the JSON.

**Invoked by**

- tools/bootstrap.sh
- hardware_compute skill §2 steps 1-2 (agent-executed UNPACK + RUN)
- .github/workflows/verify.yml (CI extracts its own copy and runs it with generic)
- operator (BOOT.md debug command)

**Invokes**

- PowerShell CIM queries via psq()
- nvidia-smi --query-gpu=name --format=csv,noheader (only if present)

**Notes**

Header: 'studio-os :: hardware probe v4 :: usage: verify_compute.sh <workload_class>'. The probe's own host detection has no Darwin branch, so macOS reports host.kind 'unknown', not 'macos'. bootstrap.sh and skill P2 map Darwin to macos. gpu.vram_total_gb is always null by design. String fields (host.name, host.machine, gpu.name, workload) are interpolated into the heredoc JSON without escaping, so a value containing a double quote or backslash would produce invalid JSON, which bootstrap then reports as exit 1. The file is gitignored and absent on disk. BOOT.md and DECISIONS.md say the Windows and WSL branches (every psq query) have never run on the target laptop. DECISIONS.md says the probe was 'syntax-checked and exercised on Linux'. CI would also run the Linux branch, but no CI run history is visible in the files.

### evaluate_gate.py

`cli` · status `runs-today`

Paths: `tools/hw/evaluate_gate.py`

Turns a probe JSON into a PASS/DENY verdict per workload class, using thresholds parsed at run time from ARTIFACT B in skills/hardware_compute.skill.md. It enforces host_law, null_law, thermal_law and single_flight_law, and writes the gate token (PASS) or a DENY record to state/compute_gate.json.

**Entry points**

- `python3 tools/hw/evaluate_gate.py <workload>`
  - does: Evaluate one class from ARTIFACT B (currently llm_local_sm | llm_local_md | render_3d_cpu | batch_2d), apply the single-flight check, and write the token
  - changes: state/compute_gate.json (always, when not --dry-run): a PASS token, or a DENY record {verdict, workload, ts_epoch, reasons}. Creates state/ if missing.
- `python3 tools/hw/evaluate_gate.py --all --dry-run`
  - does: Survey every class in ARTIFACT B without writing a token; the single-flight check is skipped. If a positional workload is also given, --all takes precedence and the positional is ignored.
  - changes: nothing
- `python3 tools/hw/evaluate_gate.py render_3d_cpu --consume blender_python`
  - does: Evaluate and, on PASS, mint with consumed_by pre-stamped to SKILL_ID (docstring and BOOT.md example)
  - changes: state/compute_gate.json
- `python3 tools/hw/evaluate_gate.py <workload> --force`
  - does: Override a live PASS token held by another workload; prints ' WARNING: --force overrides a live token held by <workload>' to stderr
  - changes: state/compute_gate.json
- `python3 tools/hw/evaluate_gate.py (<workload> | --all --dry-run) --probe PATH`
  - does: Use an alternate probe JSON. The default is the absolute <repo>/state/hw_probe_latest.json; a given PATH is resolved relative to the CWD.
  - changes: state/compute_gate.json unless --dry-run
- `python3 tools/hw/evaluate_gate.py -h`
  - does: argparse help (the description is the module docstring)
  - changes: nothing

**Inputs**

- positional workload (nargs='?'): workload class from ARTIFACT B
- --all (store_true): evaluate every class; requires --dry-run
- --probe PATH (default str(ROOT/state/hw_probe_latest.json))
- --dry-run (store_true): evaluate without writing a token
- --consume SKILL_ID: stamp consumed_by on a minted PASS token
- --force (store_true): override a live token held by another workload

**Outputs**

- stdout: '  probe: <file name>, <age>s old, host=<kind>, machine=<machine>'
- stdout: '  WARNING: probe is older than the 30-minute TTL — hardware truths go stale' when age > 1800 s. This goes to stdout, not stderr, and is a warning only.
- stdout per class: a blank line, then '  <cls>  —  PASS|DENY', then one '    ok  ' / '    FAIL' line per check
- stdout when not --dry-run: '    token: state/compute_gate.json -> <verdict>[, budget N GB]' (relative path with OS separator)
- stdout on DENY: a 'remedies:' block mapped from ARTIFACT B
- stderr: 'ERROR: ...' from die(); the --force WARNING
- Exit codes: 0 = every evaluated class PASS; 1 = any DENY; 2 = die() or an argparse error

**Reads**

- skills/hardware_compute.skill.md (ARTIFACT B via regex r"### ARTIFACT B.*?\n```json\n(.*?)\n```" with re.S, then json.loads; Path.read_text() with no encoding)
- probe JSON (default state/hw_probe_latest.json)
- state/compute_gate.json (single-flight check; only when not --dry-run)

**Writes**

- state/compute_gate.json (Path.write_text, no encoding; creates state/). PASS token: {verdict:'PASS', workload, ts_epoch:<mint time>, ttl_seconds:1800, memory_budget_gb:<probe memory.dynamic_claim_limit_gb>, probe_snapshot{gpu, available_gb, power, cpu_perf_pct, thermal_c}, consumed_by:<--consume or null>, law}. DENY: {verdict:'DENY', workload, ts_epoch, reasons:[failure strings]}.

**Depends on**

- python3 (stdlib: argparse, json, re, sys, time, pathlib)

**Gates and checkpoints**

- Refuses with exit 2 on any of these: no workload and no --all (ap.error); a missing skill file; ARTIFACT B missing or invalid JSON; a missing probe file; malformed probe JSON; --all without --dry-run ('single_flight_law forbids', checked after the probe loads); an unknown workload class (checked inside evaluate(); no token is written).
- host_law: host.kind must be in {windows, wsl, linux}. gpu.status == 'discrete' adds an explicit FAIL.
- Threshold key semantics:
- - *_min: got >= want
- - *_max: got <= want
- - *_in: membership
- - otherwise: equality, except that the value 'any' always passes
- - keys starting with '_' are skipped
- null_law: a null metric named by a _min/_max/_in threshold fails ('an unverifiable gate is closed').
- thermal_law: thermal.cpu_temp_c_max and thermal.cpu_perf_pct_min are handled together. A null reading is allowed if the other is readable, every readable reading must pass, and if both are null the gate fails.
- single_flight_law (skipped under --dry-run): an existing token with verdict PASS, age < its ttl_seconds (default 1800; a missing ts_epoch counts as 0, so the token is treated as expired) and a different workload DENIES the request, whether or not consumed_by is set. The same workload may re-mint (continuous-mode refresh). --force bypasses the check with a stderr warning. An unreadable or non-PASS token is ignored.
- Probe age over 1800 s only prints a warning. A stale probe can still mint a fresh 1800 s token, because the TTL counts from mint time.

**Invoked by**

- tools/bootstrap.sh (--all --dry-run --probe state/hw_probe_latest.json)
- tools/hw/test_gate.py (subprocess)
- .github/workflows/verify.yml (--all --dry-run --probe /tmp/probe.json)
- operator per BOOT.md § 4 and README.md

**Notes**

Thresholds are never duplicated in the script. REMEDY_FOR maps failure-text substrings to ARTIFACT B remedy keys; the first match per failure wins, and each remedy is shown at most once:
1. single_flight_law -> 'single-flight deny'
2. thermal_law -> 'thermal unreadable (both null)'
3. gpu.status=discrete -> 'gpu discrete unexpectedly'
4. thermal.cpu_perf_pct -> 'cpu_perf_pct low'
5. power.source -> 'on battery'
6. memory.available_gb -> 'low available_gb'
7. memory.free_pct -> 'low available_gb'
8. memory.swap_used_mb -> 'swap rising'
9. disk.free_gb -> 'low disk'

Gaps in that mapping: the remedy 'low battery on ac' is never selected. A thermal.cpu_temp_c failure and a host.kind failure have no mapped remedy. Null-valued metrics map to the same remedy as a threshold miss, so an unreadable power.source prints the 'on battery' remedy.

Other behaviours derived from the source:
(1) Without --dry-run, mint() writes whatever the verdict is. A denied request, including one denied by single_flight_law itself, overwrites a live PASS token held by another workload with the DENY record.
(2) A consumed PASS token still blocks other workloads until its TTL expires.
(3) Skill §2 step 5 also calls for pipeline phase -> blocked and dashboard system_status.state -> DEGRADED, and §2 step 6 for a hardware.* writeback; this script does not touch dashboard.json.
(4) The minted 'law' string omits ARTIFACT C's final sentence about single_flight_law.
(5) Files are read and written without an explicit encoding. The UTF-8 commit 266ec99 did not touch this file, and stdout contains non-ASCII (em dash, middle dot).

### test_gate.py

`cli` · status `runs-today`

Paths: `tools/hw/test_gate.py`

Regression test that pins evaluate_gate.py verdicts against the current ARTIFACT B. It covers: AC required for sustained work, throttling denied, one readable thermal reading enough, both unreadable denied, the md tier denied under memory pressure, a discrete GPU and macOS refused, and a live token blocking a second workload.

**Entry points**

- `python3 tools/hw/test_gate.py`
  - does: Runs 9 --dry-run cases against synthetic probes, then 1 single-flight case against a synthetic live token
  - changes: Creates and deletes temp *.json probe files in the system temp dir. Creates state/ if missing. Overwrites state/compute_gate.json with a synthetic PASS token {verdict PASS, workload llm_local_sm, ts_epoch now, ttl_seconds 1800, consumed_by null}. The non-dry-run evaluate_gate then overwrites it with a DENY record. A finally block restores the prior contents, or deletes the file if none existed.

**Inputs**

- no CLI arguments
- Built-in HEALTHY probe:
- - host: name YOGA, kind windows, machine 'Yoga Book 9 14IMU9'
- - gpu: integrated, 'Intel Arc Graphics', vram null, shared true
- - memory: total 16, available 11, free_pct 68, swap 1800 MB, claim 6
- - power: ac, battery 88
- - thermal: temp null, perf 94
- - disk: 180 / 180
- - ts_epoch is added per run

**Outputs**

- per case: '  ok  ' or '  FAIL' followed by '  <name>  [<workload> -> <verdict>]'; on failure, also 'expected <want>' and the indented evaluator output
- 'ERROR(rc=N)' as the verdict if neither the PASS nor the DENY line is found
- summary: '  N passed, M failed'
- exit 0 = all 10 cases as specified; 1 = any failure

**Reads**

- state/compute_gate.json (backup before the single-flight case)
- stdout of evaluate_gate.py: matches '  <workload>  —  PASS' or '  <workload>  —  DENY'; single-flight is detected by the substring 'single_flight_law'

**Writes**

- temp *.json probe files (unlinked after use)
- state/compute_gate.json (transient, then restored or deleted)

**Depends on**

- python3 (stdlib: json, subprocess, sys, tempfile, time, pathlib)
- tools/hw/evaluate_gate.py
- skills/hardware_compute.skill.md (indirectly, through the evaluator)

**Gates and checkpoints**

- Cases:
- 1. healthy -> llm_local_sm PASS
- 2. one readable thermal reading -> render_3d_cpu PASS
- 3. both thermal readings null -> llm_local_sm DENY
- 4. battery -> render_3d_cpu DENY
- 5. battery -> llm_local_sm PASS
- 6. throttling (91 C / 58%) -> render_3d_cpu DENY
- 7. low memory (4 GB available / 25% free / 7000 MB swap) -> llm_local_md DENY
- 8. discrete RTX 4070 -> render_3d_cpu DENY
- 9. host.kind macos -> llm_local_sm DENY
- 10. live llm_local_sm token -> render_3d_cpu blocked (single_flight_law)
- The single-flight case runs the evaluator WITHOUT --dry-run, because --dry-run skips the check. The finally block restores the prior token.

**Invoked by**

- .github/workflows/verify.yml step 'Gate logic'
- operator per README.md ('pins the gate's verdicts against ARTIFACT B') and BOOT.md § 4

**Invokes**

- sys.executable tools/hw/evaluate_gate.py <workload> --probe <tmp> --dry-run
- sys.executable tools/hw/evaluate_gate.py render_3d_cpu --probe <tmp> (non-dry-run)

**Notes**

DECISIONS.md describes it as 'ten cases' (9 CASES + 1 single-flight). Running it is not side-effect free: it touches the real state/compute_gate.json. If the process is killed between the token write and the finally block, it leaves a synthetic live PASS token for llm_local_sm with consumed_by null. local_rag_orchestration's P3 check would accept that token, and it would block other workloads for 1800 s. It does not assert that a prior token survives a denied request, which is the DENY-overwrite behaviour in evaluate_gate. Token read/write uses read_text()/write_text() without an explicit encoding, and the CI encoding step does not cover this file.

### reconcile_models.py

`cli` · status `partial`

Paths: `tools/reconcile_models.py`

Compares dashboard.json hardware.local_llm.tiers (sm/md model tags) and embed_model with what Ollama serves at /api/tags and reports drift. With --write it rewrites the tier model tags in dashboard.json to in-range candidates.

**Entry points**

- `python3 tools/reconcile_models.py`
  - does: Report drift against the dashboard endpoint. If that is unreachable, it falls back to the WSL gateway when /proc/version contains 'microsoft'.
  - changes: nothing
- `python3 tools/reconcile_models.py --write`
  - does: Apply the suggested tier model changes (first in-range candidate per drifting tier)
  - changes: dashboard.json: hardware.local_llm.tiers.<tier>.model, and hardware.local_llm._tiers_note replaced with a 'RECONCILED ...' note (only when changes is non-empty)
- `python3 tools/reconcile_models.py --endpoint http://172.24.0.1:11434`
  - does: Use an explicit endpoint; this disables the WSL gateway fallback
  - changes: nothing unless --write
- `python3 tools/reconcile_models.py --help`
  - does: argparse help (used by the CI encoding check; exits before any file read)
  - changes: nothing

**Inputs**

- --endpoint URL (overrides dashboard hardware.local_llm.endpoint)
- --write (store_true)

**Outputs**

- stdout: '  note: reachable at <alt>, not <endpoint> ...' when the WSL fallback succeeds
- stdout: '  <endpoint> serves N model(s): <names or (none)>'
- stdout per tier: 'ok' (exact tag), 'drift' (same family served; not counted as drift), or 'DRIFT' (with in-range candidates, or an 'ollama pull <want>' hint)
- stdout: a DRIFT line for embed_model if its family is not served
- stdout with --write: 'wrote tier <t> -> <pick>' and 'dashboard.json updated — re-run tools/verify_system.py'
- stdout without --write: 're-run with --write to apply, or pull the declared tags instead' when there are changes
- stderr: '  Ollama not reachable at <endpoint>'
- Exit codes: 0 = no drift (same-family matches count as a match); 1 = drift, including after a successful --write, because drift is never reset; 2 = endpoint unreachable

**Reads**

- dashboard.json (encoding utf-8): hardware.local_llm.endpoint, tiers, embed_model
- GET {endpoint}/api/tags (urllib, timeout 6 s)
- /proc/version (utf-8; WSL detection)
- `ip route show default` (subprocess, timeout 5; third token taken as the gateway)

**Writes**

- dashboard.json (only with --write and non-empty changes): utf-8, indent=2, ensure_ascii=False, trailing newline

**Depends on**

- python3 stdlib (argparse, json, re, subprocess, sys, urllib)
- Ollama HTTP API
- ip (WSL only)

**Gates and checkpoints**

- TIER_RANGE: sm 0-8.9 B params, md 9.0-14.9 B (hardcoded; the comment says the ceilings come from ARTIFACT B). Models outside the range are never candidates. A tier key other than sm/md would raise KeyError when it drifts.
- Parameter count comes from details.parameter_size (regex '([\d.]+)\s*B'), falling back to a tag suffix matching '[:\-](\d+(?:\.\d+)?)b\b'.
- A tier is 'ok' on an exact tag match and 'drift' (not failing) on a same-family match. Otherwise it is DRIFT, and cands[0] is proposed and applied with --write.
- With --write only tier model tags change. embed_model drift is reported but never written.
- The WSL gateway retarget is attempted only when --endpoint is not given, the first fetch failed, and /proc/version contains 'microsoft'. It does not check WSL_DISTRO_NAME, unlike bootstrap.

**Invoked by**

- tools/bootstrap.sh (--endpoint "$REACHED", no --write, stderr discarded)
- operator per BOOT.md § 2 and OBSIDIAN.md (troubleshooting table)
- .github/workflows/verify.yml ('Tools declare their encodings': --help only, under -W error::EncodingWarning with PYTHONWARNDEFAULTENCODING=1)
- tools/vault_rag.py error hint ('python3 tools/reconcile_models.py --write')

**Invokes**

- urllib GET {endpoint}/api/tags
- ip route show default

**Notes**

The docstring says it 'will not pick a model for you silently'. In practice --write applies the first in-range candidate after printing the list. After writing it prints 're-run tools/verify_system.py'. DECISIONS.md says it 'has only been run against a stub endpoint; the real inventory is unknown'. The dashboard tiers are still PROVISIONAL: sm llama3.1:8b, md mistral-nemo:12b, embed nomic-embed-text, endpoint http://localhost:11434. The CI encoding check runs only --help; argparse exits before DASH.read_text, so the encoding of the real code path is not exercised by CI, although the source does declare utf-8.

### hardware_compute skill

`skill` · status `partial`

Paths: `skills/hardware_compute.skill.md`

Agent-facing 'hardware bouncer' skill (v2.0, danger_class GATEKEEPER). It specifies prerequisites P1-P4 and the execution process (unpack, probe, evaluate, single-flight, mint/deny, dashboard flush, handback, continuous mode). It embeds ARTIFACT A (probe), ARTIFACT B (thresholds, laws and remedies) and ARTIFACT C (token schema). It is the single source that bootstrap.sh, evaluate_gate.py, verify_system.py and CI extract from.

**Entry points**

- `trigger_a: ["render locally", "GPU", "heavy compute", "batch process", "out of memory", "thermals", "on battery"]`
  - does: Routing-header trigger phrases (Router.md §2 Trigger A table routes them here)
  - changes: per spec: state/compute_gate.json, state/hw_probe_latest.json, dashboard hardware.* and system_status.state
- `trigger_b: ["ANY task where another skill declares danger_class: LOCAL_COMPUTE_HEAVY"]`
  - does: Mandatory pre-step for compute-heavy skills (blender_python and local_rag_orchestration declare LOCAL_COMPUTE_HEAVY)
  - changes: same
- `§1 prerequisite bash block (P1-P4)`
  - does: Agent-run preflight that prints OK:/FAIL: lines and exports STUDIO_HOST_KIND
  - changes: nothing (exports an env var in the agent's shell)

**Inputs**

- requesting skill's workload_class (V1): llm_local_sm, llm_local_md, render_3d_cpu or batch_2d
- mandatory_context: pipeline_ethics, render_philosophy

**Outputs**

- gate token at state/compute_gate.json (gate_token_path), gate_ttl_seconds 1800
- writes_dashboard_keys: hardware.*, system_status.state

**Reads**

- ./.task_scratch/attestation.txt (P1 grep for 'ROUTER INTERCEPT')
- existing state/compute_gate.json (§2 step 4)

**Writes**

- tools/hw/verify_compute.sh (§2 step 1 UNPACK)
- state/hw_probe_latest.json (§2 step 2)
- state/compute_gate.json (§2 step 5)
- dashboard.json hardware.*; system_status.state -> DEGRADED on deny; requesting pipeline phase -> blocked (§2 steps 5-6; spec only, no script does this)

**Depends on**

- awk, df, grep (P3)
- powershell.exe or pwsh.exe on WSL (P4; does not accept 'pwsh', unlike bootstrap and the probe)

**Environment and secret names (names only)**

- STUDIO_HOST_KIND (exported by the P2 block)
- WSL_DISTRO_NAME

**Gates and checkpoints**

- P1: the attestation exists
- P2: host kind is windows, wsl or linux
- P3: required tools are present. The spec always echoes OK:P3 after the loop, even when FAIL lines were printed.
- P4: on WSL, the PowerShell bridge is reachable
- V2: pipeline_ethics governs preemption; an in-flight render is never killed without operator approval.
- §2 step 3: every metric must pass; there is no partial credit.
- §2 step 4 single-flight: deny if an existing token is PASS, unexpired, and consumed_by is null or names a still-running skill.
- §2 step 6 CONTEXT FLUSH №1: dashboard writeback of hardware.*
- §2 step 7 HANDBACK: the requesting skill re-checks the token itself.
- §2 step 8 CONTINUOUS MODE: re-run steps 2-6 every 5 minutes for jobs over ~5 minutes. Two consecutive DENYs signal the running skill to checkpoint-and-pause.
- Laws in ARTIFACT B: evaluation_law, null_law, thermal_law, host_law, single_flight_law, wsl_memory_law

**Invoked by**

- Router.md: §2 Trigger A table; §1 'Compute-heavy work goes through hardware_compute first'; refusal list lines 354-355 (never skip hardware verification, never run compute-heavy work without a fresh PASS token)
- router.js (mandatory_context map entry)
- blender_python, local_rag_orchestration and adobe_suite_uxp (depends_on_skill: hardware_compute.skill.md)

**Invokes**

- tools/hw/verify_compute.sh (ARTIFACT A)

**Notes**

Of the executable steps, 1-5 are partly implemented. bootstrap.sh does step 1 and step 2, running the probe with 'generic' rather than {{workload_class}}. evaluate_gate.py does steps 3-5 but without step 5's dashboard and pipeline side effects. No script implements step 6 (dashboard writeback) or step 8 (the continuous-mode loop).

Schema mismatches: §2 step 5 shows the PASS shape with a 'probe' key, while ARTIFACT C and evaluate_gate use 'probe_snapshot'. Its DENY shape omits the workload and ts_epoch that evaluate_gate writes.

Router.md line 355 says the PASS token comes 'from verify_compute.sh', but the token is minted by evaluate_gate.py; the probe only emits JSON.

The §1 P2 block, bootstrap and the probe share detection logic, but only the probe lacks a Darwin case.

### ARTIFACT B threshold matrix

`data` · status `runs-today`

Paths: `skills/hardware_compute.skill.md`

JSON law table parsed at run time by evaluate_gate.py: per-class thresholds, the laws and the remedies.

**Entry points**

- `regex r"### ARTIFACT B.*?\n```json\n(.*?)\n```" (re.S) in evaluate_gate.load_law()`
  - does: Extraction point
  - changes: nothing

**Outputs**

- top-level machine: 'Lenovo Yoga Book 9i · 16 GB shared · Intel integrated graphics · no CUDA'
- thresholds.llm_local_sm (≤8B Q4_K_M, num_ctx ≤ 8192): memory.available_gb_min 6, memory.free_pct_min 30, memory.swap_used_mb_max 6144, power.source_in [ac, battery], thermal.cpu_temp_c_max 90, thermal.cpu_perf_pct_min 65, disk.free_gb_min 12
- thresholds.llm_local_md (12-14B Q4_K_M, num_ctx ≤ 4096): 10 / 45 / 3072 / [ac] / 85 / 80 / 20
- thresholds.render_3d_cpu (EEVEE or CPU Cycles): gpu.status 'any', 8 / 40 / 3072 / [ac] / 80 / 85 / 20
- thresholds.batch_2d (Adobe COM batch): gpu.status 'any', 5 / 25 / 6144 / [ac] / 90 / 65 / 10
- laws: evaluation_law, null_law, thermal_law, host_law, single_flight_law, wsl_memory_law (prose strings, not interpreted by code)
- remedies keys (9): on battery, low battery on ac, thermal unreadable (both null), cpu_perf_pct low, low available_gb, swap rising, gpu discrete unexpectedly, low disk, single-flight deny

**Gates and checkpoints**

- Edits are validated by tools/hw/test_gate.py (BOOT.md: 'Edit them there and tools/hw/test_gate.py will tell you what you changed') and by CI

**Invoked by**

- tools/hw/evaluate_gate.py

**Notes**

The laws are prose. The behaviour of host_law, null_law, thermal_law and single_flight_law is hardcoded in evaluate_gate.py; only the thresholds and remedies are data-driven. The llm_local_* classes have no gpu.status key, but evaluate_gate still fails a discrete GPU under host_law. reconcile_models.py's TIER_RANGE comment says the tier ceilings come from here, but the ranges are hardcoded in that script.

### compute gate token protocol (ARTIFACT C)

`protocol` · status `never-exercised`

Paths: `state/compute_gate.json`, `skills/hardware_compute.skill.md`

Single-slot file token that authorises one heavy local job, covering mint, TTL, consume and single-flight.

**Entry points**

- `python3 tools/hw/evaluate_gate.py <class> [--consume SKILL_ID] [--force]`
  - does: Mint (PASS) or record a DENY
  - changes: state/compute_gate.json
- `write "consumed_by": "<skill_id>" into state/compute_gate.json`
  - does: Consume. Specified for blender_python §2 step 2 (before the first render) and local_rag_orchestration §2 step 8 (after model eviction). This is agent-performed per the skill markdown; no script implements it.
  - changes: state/compute_gate.json
- `delete state/compute_gate.json and re-probe`
  - does: Manual release of a token orphaned by a dead job (BOOT.md § 4; ARTIFACT B 'single-flight deny' remedy)
  - changes: removes state/compute_gate.json

**Inputs**

- probe memory.dynamic_claim_limit_gb -> memory_budget_gb

**Outputs**

- schema: verdict, workload, ts_epoch, ttl_seconds (1800), memory_budget_gb, probe_snapshot{gpu, available_gb, power, cpu_perf_pct, thermal_c}, consumed_by, law

**Environment and secret names (names only)**

- RAG_TIER (read by the local_rag_orchestration P3 check to choose llm_local_md vs llm_local_sm)

**Gates and checkpoints**

- TTL: 1800 s, hardcoded at mint and measured from mint time. Checkers honour the token's own ttl_seconds.
- Consumer prechecks (inline python in skill markdown: blender_python §1 P4, local_rag_orchestration §1 P3) fail on any of: verdict != PASS; age >= ttl; a workload mismatch; consumed_by not null; an unreadable token. The expected workload is render_3d_cpu for blender_python, and llm_local_md if env RAG_TIER == 'md', otherwise llm_local_sm, for local_rag_orchestration.
- Single-flight is enforced only in evaluate_gate at mint time (see the evaluate_gate entry).
- One token, one workload: a consumed token cannot authorise a second job.

**Invoked by**

- evaluate_gate.py (writer)
- blender_python and local_rag_orchestration prerequisite blocks (readers, spec)
- test_gate.py (transient writer)

**Notes**

The file does not exist on disk; state/ holds only rag_index/ and vault_manifest.json, and state/ is gitignored.

The documented consume paths conflict. BOOT.md and the evaluate_gate docstring give 'render_3d_cpu --consume blender_python', which pre-stamps consumed_by, but blender_python P4 then fails with 'already consumed by ...'.

Under evaluate_gate's implementation a denied mint attempt overwrites the file with a DENY record.

Enforcement gaps on the executable side:
- tools/vault_rag.py, the executable implementation of local_rag_orchestration, contains no compute_gate reference (grep).
- adobe_suite_uxp declares depends_on_skill hardware_compute with workload_class batch_2d, but its text has no token check (grep).

The skills read the relative path 'state/compute_gate.json' from the CWD, while evaluate_gate always writes <repo>/state/compute_gate.json.

### verify.yml CI (gate steps)

`ci` · status `runs-today`

Paths: `.github/workflows/verify.yml`

GitHub Actions job 'verify' that runs on push to main, pull_request and workflow_dispatch (ubuntu-latest, Python 3.11) and runs the protocol and gate checks.

**Entry points**

- `python3 tools/verify_system.py`
  - does: Step 'Protocol integrity' (includes check_extracted_probe, which is a no-op on CI because the file is absent at that point)
  - changes: nothing
- `python3 tools/hw/test_gate.py`
  - does: Step 'Gate logic'
  - changes: state/compute_gate.json in the CI workspace (transient)
- `mkdir -p tools/hw; python3 - skills/hardware_compute.skill.md > tools/hw/verify_compute.sh (same heredoc regex as bootstrap); bash -n tools/hw/verify_compute.sh; chmod +x; ./tools/hw/verify_compute.sh generic > /tmp/probe.json; python3 -c json.load`
  - does: Step 'Probe extracts and parses' (Linux branch only)
  - changes: CI workspace tools/hw/verify_compute.sh, /tmp/probe.json
- `python3 tools/hw/evaluate_gate.py --all --dry-run --probe /tmp/probe.json || true; python3 tools/hw/evaluate_gate.py --all --dry-run --probe /tmp/probe.json | grep -qE "— (PASS|DENY)"`
  - does: Step 'Evaluator runs against a live probe': asserts that a verdict is reached, not that it passes
  - changes: nothing
- `PYTHONWARNDEFAULTENCODING=1 python3 -W error::EncodingWarning tools/verify_system.py --quiet; ... tools/reconcile_models.py --help; ... tools/vault_rag.py --help`
  - does: Step 'Tools declare their encodings'
  - changes: nothing

**Outputs**

- job pass/fail

**Reads**

- skills/hardware_compute.skill.md
- tools/hw/evaluate_gate.py
- tools/hw/test_gate.py
- tools/verify_system.py
- tools/reconcile_models.py
- dashboard.json
- router.js

**Writes**

- runner workspace only (tools/hw/verify_compute.sh, state/compute_gate.json transiently, /tmp/probe.json)

**Depends on**

- actions/checkout@v4
- actions/setup-python@v5 (python 3.11)
- node (router.js --check; not installed by the workflow)
- bash

**Environment and secret names (names only)**

- PYTHONWARNDEFAULTENCODING

**Gates and checkpoints**

- Other, non-gate steps: 'UI logic parses' (node --check router.js), 'Dashboard parses', 'vault_rag core logic'

**Invoked by**

- GitHub: push to main, pull_request, workflow_dispatch

**Invokes**

- tools/verify_system.py
- tools/hw/test_gate.py
- tools/hw/evaluate_gate.py
- tools/reconcile_models.py --help
- tools/vault_rag.py --help

**Notes**

The encoding step does not cover evaluate_gate.py, test_gate.py or bootstrap's inline Python. For reconcile_models.py it only runs --help, which exits before any file I/O. Only the Linux probe branch is exercised. No run history is visible in the repository, so 'runs-today' means the workflow is defined and runnable, not that runs were observed.

### verify_system.py (probe drift and portability checks)

`cli` · status `runs-today`

Paths: `tools/verify_system.py`

Protocol integrity checker, outside the core hw-gate scope. Two checks are relevant here. check_extracted_probe fails if tools/hw/verify_compute.sh differs from ARTIFACT A; it is skipped when the file is absent. check_host_portability fails if a skill declares host_kinds outside dashboard hardware.host_kind_enum, invokes osascript, vm_stat, sysctl, afplay or pbcopy at command position inside a code fence, carries an /Applications/ path in a fence, or sets cycles.device="GPU" while hardware.gpu.cuda is false.

**Entry points**

- `python3 tools/verify_system.py`
  - does: Full protocol check; BOOT.md says it must exit 0
  - changes: nothing (a grep found no write_text, open(), dump, mkdir, unlink or .write calls)
- `python3 tools/verify_system.py --quiet`
  - does: Exit code only (docstring line 11; '--quiet' in sys.argv). Used in the CI encoding step.
  - changes: nothing

**Inputs**

- --quiet (checked via sys.argv)

**Outputs**

- ok/fail lines; nonzero exit on drift

**Reads**

- tools/hw/verify_compute.sh (utf-8)
- skills/hardware_compute.skill.md (utf-8)
- skills/*.skill.md
- dashboard.json
- Router.md
- router.js

**Depends on**

- python3

**Gates and checkpoints**

- The drift comparison strips whitespace from both sides and compares exact text. A missing ARTIFACT A is also a fail.

**Invoked by**

- operator (BOOT.md, after bootstrap)
- bootstrap.sh 'Next' block (printed recommendation)
- CI
- reconcile_models.py --write output hint

**Notes**

Only lines 120-250 and a grep of the rest were read; the other checks are not inventoried here.

### BOOT.md runbook

`doc` · status `runs-today`

Paths: `BOOT.md`

First-boot runbook. It covers shell choice (Git Bash vs WSL2), prerequisites, Ollama setup including WSL networking, what bootstrap does, gate usage, why the system still says BLOCKED, and known unknowns.

**Entry points**

- `bash tools/bootstrap.sh`
  - does: Documented first boot (first line of the top code block)
  - changes: see bootstrap.sh
- `python3 tools/verify_system.py`
  - does: Documented protocol integrity check (second line of the same block; must exit 0)
  - changes: nothing
- `ollama pull llama3.1:8b ; ollama pull nomic-embed-text`
  - does: Documented Ollama model pulls (PowerShell block)
  - changes: Ollama model store
- `python3 tools/reconcile_models.py ; python3 tools/reconcile_models.py --write`
  - does: Documented registry reconcile (§ 2)
  - changes: dashboard.json with --write
- `setx OLLAMA_HOST "0.0.0.0" ; New-NetFirewallRule -DisplayName "Ollama from WSL" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow`
  - does: Documented one-time Windows-side WSL enablement, which the scripts cannot do
  - changes: user environment variable, Windows firewall
- `python3 tools/hw/evaluate_gate.py --all --dry-run ; python3 tools/hw/evaluate_gate.py llm_local_sm ; python3 tools/hw/evaluate_gate.py render_3d_cpu --consume blender_python`
  - does: Documented gate usage (§ 4)
  - changes: state/compute_gate.json (the latter two)
- `./tools/hw/verify_compute.sh generic | python3 -m json.tool ; bash tools/bootstrap.sh --probe`
  - does: Documented probe debugging loop (Known unknowns)
  - changes: see bootstrap.sh
- `export BLENDER_BIN=/c/path/to/blender.exe`
  - does: Documented Blender override
  - changes: shell environment
- `python3 tools/vault_rag.py status | index | ask "..."`
  - does: Documented vault RAG follow-on (outside this subsystem)
  - changes: state/rag_index

**Depends on**

- Python 3 as python3
- powershell.exe
- curl, awk, df, grep
- optional: Ollama, Photoshop / Illustrator / After Effects (COM), Blender 4+

**Environment and secret names (names only)**

- OLLAMA_HOST
- BLENDER_BIN
- OLLAMA_ORIGINS (referenced; details in OBSIDIAN.md)

**Gates and checkpoints**

- Three expected denials: on battery (every class except llm_local_sm requires AC); thermal unreadable (both readings null); another job holds the token (delete state/compute_gate.json and re-probe).
- Known unknowns: the Windows and WSL branches of the probe (every PowerShell query), the WSL gateway rewrite and the wslpath handoff to Photoshop were syntax-checked and exercised on Linux but 'have never run on the target laptop'. First boot should be treated as debugging, not a smoke test.

**Invoked by**

- operator
- README.md ('Setting it up on the machine')

**Invokes**

- tools/bootstrap.sh
- tools/verify_system.py
- tools/reconcile_models.py
- tools/hw/evaluate_gate.py
- tools/hw/test_gate.py
- tools/hw/verify_compute.sh
- tools/vault_rag.py

**Notes**

BOOT.md is stale or imprecise in five places:
- It says the dashboard still declares system_status.state BLOCKED after a clean bootstrap. The current dashboard.json says DEGRADED, and its blocked_reason says three brand gates (visual_identity, typography_system, color_science) are authored, while BOOT.md says none is.
- It says nothing outside state/ and tools/hw/ is touched, but bootstrap also creates .task_scratch/.
- It lists PowerShell 'as powershell.exe' as required. bootstrap also accepts pwsh.exe or pwsh, and only requires it on windows/wsl.
- It shows the 'render_3d_cpu --consume blender_python' example, which conflicts with blender_python P4.
- It says 'bootstrap.sh fails without these' prerequisites, but in --probe mode they are not checked.

DECISIONS.md adds further known unknowns: bootstrap's COM-registration probe has not run on the target, and reconcile_models has only run against a stub endpoint.

## Usage flows

### First boot

1. Pick one shell (Git Bash = windows, or WSL2 = wsl) and stay in it (BOOT.md § 0).
2. Run bash tools/bootstrap.sh. It detects the host (macOS and unknown are refused with exit 1 after sections 2-5), then checks prerequisites (python3, curl, awk, df, grep, plus PowerShell on windows/wsl).
3. Ollama reachability: bootstrap tries curl <endpoint>/api/tags, then the WSL gateway, and if reachable runs reconcile_models.py --endpoint <reached> (report only).
4. It checks the COM ProgIDs via registry Test-Path and looks for Blender.
5. It runs mkdir -p state tools/hw .task_scratch, extracts ARTIFACT A to tools/hw/verify_compute.sh, and runs chmod +x and bash -n.
6. It runs ./tools/hw/verify_compute.sh generic > state/hw_probe_latest.json and validates the JSON.
7. It runs evaluate_gate.py --all --dry-run --probe state/hw_probe_latest.json. This is a survey only, and bootstrap exits 0 regardless of the verdicts.
8. Run python3 tools/verify_system.py; it must exit 0, and it includes the extracted-probe drift check.
9. Expect routes that depend on unauthored brand gates to park at L3 until more gates are authored or the vault has enough Content MDs.

### Mint and consume a gate token for a render job

1. Get a fresh probe: bash tools/bootstrap.sh --probe, or ./tools/hw/verify_compute.sh render_3d_cpu > state/hw_probe_latest.json per skill §2 step 2.
2. Run python3 tools/hw/evaluate_gate.py render_3d_cpu. On PASS it writes state/compute_gate.json with verdict PASS, ts_epoch = mint time, ttl_seconds 1800, memory_budget_gb from dynamic_claim_limit_gb and consumed_by null. On DENY it writes a DENY record.
3. blender_python §1 P4 (agent-run inline Python) reads the token and requires verdict PASS, age < ttl, workload == render_3d_cpu and consumed_by null.
4. blender_python §2 step 2 writes consumed_by: 'blender_python' immediately before the first render.
5. Until the TTL expires, any other workload's non-dry-run mint attempt is denied by single_flight_law. Per the source, that denied attempt then overwrites the file with a DENY record.
6. Documented alternative (BOOT.md, evaluate_gate docstring): evaluate_gate.py render_3d_cpu --consume blender_python pre-stamps consumed_by, which then fails blender_python's P4 'already consumed' check.

### Mint and consume for a local LLM job

1. Run python3 tools/hw/evaluate_gate.py llm_local_sm (or llm_local_md, which requires AC and more free memory).
2. local_rag_orchestration §1 P3 checks the token for workload llm_local_sm, or llm_local_md if env RAG_TIER=md.
3. Model calls use keep_alive '5m'.
4. §2 step 8: evict the model (POST /api/generate with keep_alive 0), then stamp consumed_by on the token.
5. Note: tools/vault_rag.py, the executable form of this skill, does not check or stamp the token.

### Survey what can run now

1. Run python3 tools/hw/evaluate_gate.py --all --dry-run [--probe PATH].
2. Read the PASS/DENY lines and the remedies block. No token is written and single-flight is not checked. Exit is 0 only if every class passes.

### Recover from an orphaned token

1. Symptom: a DENY with 'single_flight_law: <workload> holds a live token (<holder>, Ns left)'.
2. Wait for the TTL to expire (1800 s from mint), or delete state/compute_gate.json (BOOT.md; ARTIFACT B 'single-flight deny' remedy).
3. Re-probe with bash tools/bootstrap.sh --probe, then re-evaluate one class.
4. Alternatively, run python3 tools/hw/evaluate_gate.py <class> --force, which prints a WARNING to stderr.

### Change thresholds

1. Edit the ARTIFACT B JSON block in skills/hardware_compute.skill.md, never evaluate_gate.py.
2. Run python3 tools/hw/test_gate.py to see which pinned verdicts changed (exit 1 on any mismatch). This briefly overwrites and then restores state/compute_gate.json.
3. CI re-runs test_gate on push to main and on PRs.

### Fix the probe

1. Debug with ./tools/hw/verify_compute.sh generic | python3 -m json.tool.
2. Edit ARTIFACT A in skills/hardware_compute.skill.md, not the generated file.
3. Run bash tools/bootstrap.sh --probe to re-extract, run bash -n and re-probe.
4. Run python3 tools/verify_system.py; check_extracted_probe confirms the extracted copy matches ARTIFACT A.

### Reconcile the local model registry

1. On Windows: ollama pull <model>, and ollama pull nomic-embed-text.
2. Run python3 tools/reconcile_models.py (exit 0 match / 1 drift / 2 unreachable).
3. Run python3 tools/reconcile_models.py --write to rewrite the dashboard.json tier model tags to the first in-range candidate and replace _tiers_note. It still exits 1.
4. Run python3 tools/verify_system.py.

### WSL2 enablement

1. On Windows, once: setx OLLAMA_HOST "0.0.0.0"; New-NetFirewallRule -DisplayName "Ollama from WSL" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow; restart Ollama.
2. bootstrap.sh (WSL_DISTRO_NAME or 'microsoft' in /proc/version) and reconcile_models.py ('microsoft' in /proc/version only) retarget localhost to the default-route gateway.
3. The probe reads memory, power, thermal and the C: disk through PowerShell (powershell.exe | pwsh.exe | pwsh). Without it those fields are null and the gate closes.

### Continuous mode (specified, not implemented)

1. For jobs over ~5 minutes, re-run probe, evaluate, single-flight and flush (skill §2 steps 2-6) every 5 minutes.
2. evaluate_gate allows a same-workload re-mint as a refresh.
3. Two consecutive DENYs should signal the running skill to checkpoint-and-pause at its next safe frame.
4. No scheduler or script implements this loop.

### CI verification

1. Push to main, open a PR, or trigger workflow_dispatch; the job runs on ubuntu-latest with Python 3.11.
2. python3 tools/verify_system.py
3. python3 tools/hw/test_gate.py
4. Extract ARTIFACT A, run bash -n, run the probe with generic > /tmp/probe.json, and validate the JSON.
5. evaluate_gate.py --all --dry-run --probe /tmp/probe.json must print a PASS or DENY verdict line.
6. Encoding check under -W error::EncodingWarning: verify_system.py --quiet, reconcile_models.py --help and vault_rag.py --help.

## Relationships

| From | Relation | To |
|---|---|---|
| tools/bootstrap.sh | extracts ARTIFACT A by regex into tools/hw/verify_compute.sh | skills/hardware_compute.skill.md |
| tools/bootstrap.sh | generates it, runs chmod +x and bash -n, and runs it with 'generic' into state/hw_probe_latest.json | tools/hw/verify_compute.sh |
| tools/bootstrap.sh | invokes --all --dry-run --probe state/hw_probe_latest.json (never mints; exit code ignored) | tools/hw/evaluate_gate.py |
| tools/bootstrap.sh | invokes --endpoint <reached endpoint> without --write when Ollama is reachable (full mode only) | tools/reconcile_models.py |
| tools/bootstrap.sh | reads hardware.local_llm.endpoint | dashboard.json |
| tools/bootstrap.sh | existence check used as the repo-root landmark | Router.md |
| tools/hw/evaluate_gate.py | parses ARTIFACT B thresholds and remedies at run time | skills/hardware_compute.skill.md |
| tools/hw/evaluate_gate.py | reads the probe (default --probe path) | state/hw_probe_latest.json |
| tools/hw/evaluate_gate.py | reads it for single-flight; writes a PASS token or DENY record whenever --dry-run is absent | state/compute_gate.json |
| tools/hw/test_gate.py | runs it as a subprocess with synthetic probes; pins 10 verdicts | tools/hw/evaluate_gate.py |
| tools/hw/test_gate.py | temporarily writes a synthetic live token, then restores or deletes it | state/compute_gate.json |
| tools/reconcile_models.py | reads hardware.local_llm; --write rewrites tiers.<tier>.model and _tiers_note | dashboard.json |
| tools/reconcile_models.py | HTTP GET to list served models | Ollama /api/tags |
| tools/verify_system.py | check_extracted_probe fails if it drifts from ARTIFACT A | tools/hw/verify_compute.sh |
| .github/workflows/verify.yml | runs on push to main, PRs and workflow_dispatch | tools/hw/test_gate.py |
| .github/workflows/verify.yml | extracts ARTIFACT A, runs bash -n, runs it on Linux | skills/hardware_compute.skill.md |
| .github/workflows/verify.yml | asserts a verdict is produced against the live CI probe | tools/hw/evaluate_gate.py |
| .github/workflows/verify.yml | --help under -W error::EncodingWarning | tools/reconcile_models.py |
| skills/blender_python.skill.md | P4 (spec) requires a fresh, unconsumed PASS token with workload render_3d_cpu; §2 step 2 stamps consumed_by:… | state/compute_gate.json |
| skills/local_rag_orchestration.skill.md | P3 (spec) requires a fresh, unconsumed PASS token for llm_local_sm (llm_local_md if RAG_TIER=md); §2 step 8 s… | state/compute_gate.json |
| skills/adobe_suite_uxp.skill.md | depends_on_skill with workload_class batch_2d (no compute_gate.json check in its text) | skills/hardware_compute.skill.md |
| Router.md | routes compute-heavy triggers to it; refuses to skip hardware verification or run compute-heavy work without… | skills/hardware_compute.skill.md |
| router.js | mandatory_context map entry [pipeline_ethics, render_philosophy] | skills/hardware_compute.skill.md |
| BOOT.md | documents the first boot and the --probe re-run | tools/bootstrap.sh |
| tools/vault_rag.py | error hint suggests reconcile_models.py --write (vault_rag.py has no compute_gate reference) | tools/reconcile_models.py |
| .gitignore | ignores the generated probe; also ignores state/ and .task_scratch/ | tools/hw/verify_compute.sh |

**Open questions the files could not settle**

- Is it intended that a denied non-dry-run evaluate_gate call overwrites state/compute_gate.json with a DENY record, replacing another workload's live PASS token? Per source, mint() always writes. Single-flight therefore blocks only the first competing attempt; the next attempt finds a DENY file and is not blocked, and the running consumer's token is gone.
- The skill spec says single-flight denies when consumed_by is null or 'names a still-running skill'. evaluate_gate blocks on any live PASS token for another workload, consumed or not, and has no notion of whether the consumer is still running. Which behaviour is intended?
- BOOT.md and the evaluate_gate docstring give `render_3d_cpu --consume blender_python`, which pre-stamps consumed_by, but blender_python P4 fails on a non-null consumed_by. Which consume path is canonical?
- Skill §2 step 5 (on DENY: pipeline phase -> blocked and dashboard system_status.state -> DEGRADED), step 6 (dashboard writeback of hardware.*) and step 8 (5-minute continuous mode) are not implemented by any script read. Is some other component, such as an agent, expected to do them?
- evaluate_gate.py, test_gate.py and bootstrap.sh's inline Python read and write files without an explicit encoding, and the UTF-8 commit 266ec99 did not touch them. The CI encoding step does not cover them, and covers reconcile_models only via --help. Their behaviour on the Windows target, given the non-ASCII content of the skill file, is not demonstrated.
- The probe (ARTIFACT A) maps Darwin to host.kind 'unknown', while bootstrap.sh and skill P2 map it to 'macos'. Is that intentional? Both are refused by host_law.
- Should a probe older than the 1800 s TTL be allowed to mint a fresh 1800 s token? evaluate_gate only warns.
- Who writes ./.task_scratch/attestation.txt, which skill P1 requires? No file in this subsystem produces it; bootstrap only creates the directory.
- adobe_suite_uxp declares depends_on_skill hardware_compute (batch_2d), and tools/vault_rag.py implements local_rag_orchestration, but a grep finds no compute_gate.json token check in either. Is the gate enforced for those routes?
- ARTIFACT B's 'low battery on ac' remedy is never selected by REMEDY_FOR. cpu_temp_c and host.kind failures have no mapped remedy, and an unreadable power.source prints the 'on battery' remedy. Is that intended?
- bootstrap.sh treats reconcile_models.py exit 1 (drift) the same as a failure ('could not reconcile the model registry'). Is that intended?
- bootstrap.sh exits 0 even when every workload class is DENY. Is 'ready' meant to be independent of the gate verdicts?
- None of the gate state files (state/hw_probe_latest.json, state/compute_gate.json, tools/hw/verify_compute.sh, .task_scratch/) exist on disk. It cannot be determined from the files whether bootstrap has ever run on this machine and its state was cleaned, or has never run.

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: evaluate_gate.py outputs: stderr gets 'a probe-age WARNING if older than 1800 s'
  - evidence: tools/hw/evaluate_gate.py:260-261: the WARNING is printed with plain print(), so it goes to stdout. Only the --force WARNING (lines 165-166) and die() go to stderr.
- **corrected**: bootstrap.sh exits 0 when every class is DENY 'since the evaluator's exit code is piped through sed and ignored'
  - evidence: tools/bootstrap.sh:19 sets `set -uo pipefail`, so the pipeline status does carry the evaluator's exit code. It is ignored because there is no `set -e` and the status is never checked; the script's final command is `echo` (line 196), so it exits 0.
- **corrected**: verify_compute power mapping: 'BatteryStatus 1 -> battery; 2..11 -> ac'
  - evidence: skills/hardware_compute.skill.md:256-264: `*) POWER_SOURCE='"ac"'` catches ANY all-digit value other than 1 (including 0 and 12+). Empty with a Win32_Battery count of 0 gives ac; an empty or unreadable count gives null (`${HAS_BAT:-1}`).
- **corrected**: BOOT.md entry point 'bash tools/bootstrap.sh && python3 tools/verify_system.py'
  - evidence: BOOT.md:8-11 shows them as two separate lines in one code block, not chained with &&.
- **refuted**: BOOT.md tool entry field invoked_by_note: 'n/a'
  - evidence: Not a schema field and carries no information; removed.
- **corrected**: verify_system.py mutates 'not determined'
  - evidence: A grep of tools/verify_system.py for write_text, open(, .dump(, mkdir, unlink and .write( returns no matches, so it performs no file writes. --quiet is confirmed at lines 11 and 374.
- **corrected**: verify_compute: 'Only the Linux branch has been exercised (CI, per DECISIONS.md)'
  - evidence: DECISIONS.md:322 says 'syntax-checked and exercised on Linux' and does not name CI. verify.yml would run the Linux branch, but no CI run history is visible in the repository.
- **corrected**: bootstrap host refusal: 'Execution continues to the HARD_FAIL check and exits 1 before the probe runs'
  - evidence: tools/bootstrap.sh:65-160 run before the HARD_FAIL check at line 162. On a refused host in full mode, sections 2-4 (including reconcile_models if Ollama is reachable) and the ARTIFACT A extraction to tools/hw/verify_compute.sh, plus mkdir of state/, tools/hw/ and .task_scratch/, all still happen before exit 1.
- **added**: (missing) evaluate_gate with both a positional workload and --all
  - evidence: tools/hw/evaluate_gate.py:264 `classes = list(law["thresholds"]) if args.all else [args.workload]`: --all takes precedence and the positional is ignored.
- **added**: (missing) a stale probe can mint a fresh token
  - evidence: tools/hw/evaluate_gate.py:257-261 only warns when probe age exceeds 1800. mint() at line 174 sets ts_epoch = now, so the token TTL is measured from mint time, not probe time.
- **added**: (missing) remedy mapping for null metrics and host.kind failures
  - evidence: tools/hw/evaluate_gate.py:41-51 and 86-97: the null message for power.source contains 'power.source', so it maps to the 'on battery' remedy. host.kind and thermal.cpu_temp_c failure texts match no REMEDY_FOR signature, so no remedy is printed.
- **added**: (missing) reconcile_models --write exit code
  - evidence: tools/reconcile_models.py:119,154: drift=True is never reset after a successful write, so --write returns exit 1 even when dashboard.json was updated.
- **added**: (missing) reconcile_models WSL detection differs from bootstrap
  - evidence: tools/reconcile_models.py:42-49 checks only /proc/version for 'microsoft'. tools/bootstrap.sh:48 also accepts WSL_DISTRO_NAME.
- **corrected**: CI encoding check covers reconcile_models.py
  - evidence: .github/workflows/verify.yml:75 runs only `reconcile_models.py --help`. argparse exits before DASH.read_text (tools/reconcile_models.py:82-84), so no file I/O is exercised. The same step also runs verify_system.py --quiet and vault_rag.py --help.
- **added**: (missing) the UTF-8 hardening commit did not cover the gate scripts
  - evidence: `git show --stat 266ec99` ('Declare UTF-8 on every file read and write; keep console output ASCII') touched verify.yml, reconcile_models.py, vault_rag.py and verify_system.py only, not evaluate_gate.py, test_gate.py or bootstrap.sh. evaluate_gate still prints non-ASCII (em dash, middle dot).
- **added**: (missing) probe JSON string fields are not escaped
  - evidence: skills/hardware_compute.skill.md:311-333: $HOST_NAME, $MACHINE, $GPU_NAME and $WORKLOAD are interpolated into a heredoc with no escaping. A quote or backslash in any of them yields invalid JSON, which bootstrap.sh:169-182 turns into exit 1.
- **added**: (missing) a failed extraction leaves a broken file on disk
  - evidence: tools/bootstrap.sh:144 redirects stdout to tools/hw/verify_compute.sh before Python runs, so a missing ARTIFACT A (sys.exit with a message) leaves an empty file. A bash -n failure leaves a chmod +x file that does not parse.
- **corrected**: Summary: 'Consumer skills (blender_python, local_rag_orchestration) check the token themselves and stamp consumed_by'
  - evidence: These checks exist only as inline Python in skill markdown (skills/blender_python.skill.md:86-104,119; skills/local_rag_orchestration.skill.md:69-88,165) for an agent to run. A grep shows that tools/vault_rag.py (the executable local_rag) has no compute_gate reference, and neither does skills/adobe_suite_uxp.skill.md.
- **added**: (missing) Router.md attributes the token to the probe
  - evidence: Router.md:355 says 'without a fresh `PASS` token from `verify_compute.sh`', but tokens are minted only by tools/hw/evaluate_gate.py:173-197.
- **added**: (missing) the minted law string differs from ARTIFACT C
  - evidence: tools/hw/evaluate_gate.py:190-191 omits ARTIFACT C's final sentence 'Under single_flight_law a live token also blocks minting a token for any OTHER workload.' (skills/hardware_compute.skill.md:414).
- **added**: (missing) skill P4 and P3 quirks
  - evidence: skills/hardware_compute.skill.md:87 accepts only powershell.exe or pwsh.exe (not pwsh, which bootstrap.sh:74 and the probe accept). Line 80 echoes 'OK:P3' unconditionally after printing any FAIL:P3 lines.
- **added**: (missing) test_gate crash-window risk
  - evidence: tools/hw/test_gate.py:95-97 writes a live PASS llm_local_sm token with consumed_by null to the real state/compute_gate.json. If the process is killed before the finally block (lines 111-115), that token would satisfy local_rag_orchestration P3 and block other workloads for 1800 s.
- **unverifiable**: bootstrap.sh status never-exercised
  - evidence: DECISIONS.md:325 says only that bootstrap's COM-registration probe has never run on the target. No file records whether bootstrap ran anywhere. Its outputs (tools/hw/verify_compute.sh, state/hw_probe_latest.json, .task_scratch/) are absent on disk. The status is kept as never-exercised on the target.
- **corrected**: All other flags, exit codes, paths, regexes, thresholds, test cases and the TTL
  - evidence: Re-read in full: tools/bootstrap.sh, tools/hw/evaluate_gate.py, tools/hw/test_gate.py, tools/reconcile_models.py, BOOT.md, skills/hardware_compute.skill.md, .github/workflows/verify.yml and .gitignore. The argparse definitions (workload nargs='?', --all, --probe, --dry-run, --consume SKILL_ID, --force; --endpoint, --write) and exit codes 0/1/2 match the source. The ARTIFACT B values match. The 10 test cases match. The ttl of 1800 matches. tools/hw/ contains only evaluate_gate.py and test_gate.py. The verdict field is 'corrected' only because this is an aggregate row; nothing in it needed changing.
