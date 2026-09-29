# Local-application skills: Adobe, Blender, front-end

Subsystem `skills-local-apps` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.9 · 13 entries · 22 corrections made to the first reading.

## Summary

Three agent-executed skill files, each in the Four-Part Artifact Architecture (§0 routing header, §1 prerequisites and state verification, §2 execution process, §3 embedded artifacts). Each reaches its local tool a different way. adobe_suite_uxp (v2.0) drives Photoshop, Illustrator and After Effects through PowerShell COM (New-Object -ComObject plus DoJavaScriptFile, or DoScriptFile for AfterFX). It self-extracts parameterized ExtendScript to a Windows-visible temp dir ($STUDIO_TMP), runs it through the ARTIFACT D wrapper run_jsx.sh under a timeout (default 600s), and deletes the temp file. Its host_kinds are [windows, wsl]. Premiere (ARTIFACT C) has no COM and depends on an undefined CEP/UXP panel endpoint. blender_python (v2.0) runs fixed bpy templates headless (blender -b -P script -- params.json). EEVEE is the default engine and Cycles is CPU-only with a sample ceiling. P4 requires a fresh, unconsumed render_3d_cpu PASS token in state/compute_gate.json, and step 2 claims it. css_html_ui (v1.0) has no host bridge. It is a token-only front-end build discipline. Its ARTIFACT A token dictionary (HARD MONO, 2026-09-01) is the source that control_room.html, hub/styles.css, tools/brush-designer/styles.css and three brand context files transcribe, and tools/verify_system.py regex-checks 7 of its colour values against control_room.html. None of the extraction targets exist on disk: run_jsx.sh, tools/bpy/*, tokens/*, state/compute_gate.json, .task_scratch/, project/, backups/, renders/ and build/ are all absent. DECISIONS.md D10 states that tokens/ has never existed. All three routes currently park at Router L3 on unauthored brand gates: render_philosophy for adobe; render_philosophy and motion_language for blender; brand_voice for css. Every prerequisite block only echoes OK, FAIL, WARN or INIT and never exits non-zero, so enforcement is left to the agent reading the output.

## Tools

### adobe_suite_uxp (skill)

`skill` · status `never-exercised`

Paths: `skills/adobe_suite_uxp.skill.md`

Agent-executed skill that automates Photoshop, Illustrator and After Effects on Windows. It writes a parameterized ExtendScript artifact to a Windows-visible temp dir, runs it through PowerShell COM, parses the single result line and deletes the temp file. Premiere is addressed only through a CEP/UXP panel endpoint (ARTIFACT C), not COM.

**Entry points**

- `if grep -qi microsoft /proc/version 2>/dev/null; then STUDIO_TMP=$(wslpath -u "$(powershell.exe -NoProfile -Command '$env:TEMP' | tr -d '\r')"); towin() { wslpath -w "$1"; }; else STUDIO_TMP="${TEMP:-/tmp}"; towin() { cygpath -w "$1" 2>/dev/null || echo "$1"; }; fi; export STUDIO_TMP`
  - does: Resolves, once per Adobe task, a temp dir that Windows can address (under WSL, the Windows %TEMP% converted with wslpath; under Git Bash, $TEMP falling back to /tmp). Defines towin() to convert a path to C:\ form.
  - changes: exports STUDIO_TMP in the shell
- `grep -q "ROUTER INTERCEPT" ./.task_scratch/attestation.txt || echo "FAIL:P1"`
  - does: P1: checks that the Router attestation exists
  - changes: nothing
- `powershell.exe -NoProfile -Command "if (Get-Process Photoshop -ErrorAction SilentlyContinue) {'true'} else {'false'}" | tr -d '\r' | grep -q true && echo "OK:P2 PS running" || echo "WARN:P2 PS not running (COM will launch it)"`
  - does: P2: reports whether Photoshop is running. It checks the Photoshop process only, whichever app the task targets, and it does not check that the app is installed, although its comment says 'installed'.
  - changes: nothing
- `powershell.exe -NoProfile -Command "([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)" | tr -d '\r' | grep -q False && echo "OK:P2a non-elevated" || echo "FAIL:P2a shell is elevated — COM will not bind to the user's Photoshop"`
  - does: P2a: refuses an elevated shell. COM binds to a running app only at a matching integrity level; otherwise it silently starts a second instance.
  - changes: nothing
- `[ -d "./project/psd" ] && ls ./project/psd/*.psd >/dev/null 2>&1 && echo "OK:P3" || echo "FAIL:P3 no source PSDs"`
  - does: P3: checks that source PSDs exist. Its comment also says 'NOT open unsaved elsewhere', but nothing checks that.
  - changes: nothing
- `echo 'alert' > "$STUDIO_TMP/studio_uxp_canary.jsx" && towin "$STUDIO_TMP/studio_uxp_canary.jsx" | grep -q '^[A-Za-z]:' && rm "$STUDIO_TMP/studio_uxp_canary.jsx" && echo "OK:P4" || echo "FAIL:P4 temp dir is not addressable as a Windows drive path"`
  - does: P4: writes a canary .jsx and confirms its path converts to a drive-letter path
  - changes: creates and deletes $STUDIO_TMP/studio_uxp_canary.jsx. If the towin check fails, the rm is skipped and the canary is orphaned.
- `[ -d "./backups/$(date +%Y%m%d)" ] && echo "OK:P5" || echo "FAIL:P5 run backup first"`
  - does: P5: backup gate that requires a same-day snapshot directory
  - changes: nothing
- `grep -c '{{' /tmp/…jsx`
  - does: Step 2 PARAMETERIZE check, which must return 0. As written it names /tmp rather than $STUDIO_TMP, and it runs before step 3 writes the file.
  - changes: nothing
- `cat > "$STUDIO_TMP/studio_uxp_{{task_id}}.jsx" <<'JSX_EOF' {{artifact body verbatim}} JSX_EOF`
  - does: Step 3 EXTRACT: writes the parameterized artifact to the temp dir
  - changes: writes $STUDIO_TMP/studio_uxp_<task_id>.jsx
- `powershell.exe -NoProfile -Command "\$app = New-Object -ComObject Photoshop.Application; \$app.DoJavaScriptFile('$(towin "$STUDIO_TMP/studio_uxp_{{task_id}}.jsx")')"`
  - does: Step 4 EXECUTE: runs the .jsx in Photoshop over COM. The other ProgIDs named are Illustrator.Application (DoJavaScriptFile) and AfterFX.Application (DoScriptFile).
  - changes: launches or drives the Adobe app; the artifact writes output files
- `rm -f "$STUDIO_TMP/studio_uxp_{{task_id}}.jsx" && echo "temp jsx removed"; ls "$STUDIO_TMP"/studio_uxp_*.jsx 2>/dev/null | wc -l`
  - does: Step 7 CLEANUP ('finally-guaranteed'), then a check that the count of leftover temp jsx files is 0
  - changes: deletes the temp .jsx

**Inputs**

- task_id
- exactly ONE artifact: A (layer batch export), B (batch grade + export) or C (Premiere marker/relink shim)
- {{params}}: SRC_PSD, OUT_DIR, SCALE_PCT (A); SRC_DIR, OUT_DIR, BLACK_IN, WHITE_IN, GAMMA, JPG_QUALITY (B); MARKER_JSON_PATH, REPORT_PATH (C)
- Router attestation at ./.task_scratch/attestation.txt
- pipeline phase status (V1)
- mandatory context: render_philosophy, color_science. Router §3 adds visual_identity 'if flagged in dashboard'.

**Outputs**

- the script's last line: one result object {ok, count|markers, offline, err}
- exported PNG/JPG files in OUT_DIR, plus OUT_DIR/_result.json
- Premiere markers plus a report at REPORT_PATH (ARTIFACT C)
- dashboard event_log entry and pipeline.phases[*].progress_pct (step 6)
- phase set to blocked when the exported file count does not match result.count (step 8)

**Reads**

- /proc/version
- ./.task_scratch/attestation.txt
- ./project/psd/*.psd
- ./backups/<YYYYMMDD>/ (existence only)
- $STUDIO_TMP
- dashboard.json (pipeline phase status)
- context/brand/color_science.context.md
- context/brand/render_philosophy.context.md (not on disk)

**Writes**

- $STUDIO_TMP/studio_uxp_<task_id>.jsx (temporary, deleted)
- $STUDIO_TMP/studio_uxp_canary.jsx (temporary, deleted)
- OUT_DIR/*.png, OUT_DIR/*_graded.jpg, OUT_DIR/_result.json
- REPORT_PATH
- dashboard.json pipeline.phases[*].progress_pct and event_log

**Depends on**

- powershell.exe
- Windows COM ProgIDs Photoshop.Application, Illustrator.Application, AfterFX.Application
- Adobe Photoshop / Illustrator / After Effects (ExtendScript engine)
- Premiere Pro CEP/UXP panel endpoint (ARTIFACT C only; not defined in the repo; unverified per D8)
- wslpath (WSL) or cygpath (Git Bash)
- bash, grep, tr, date, wc, timeout (ARTIFACT D)

**Environment and secret names (names only)**

- STUDIO_TMP
- TEMP

**Gates and checkpoints**

- host_kinds: [windows, wsl]. Router.md §1 says the skill does not route on native linux, and a skill whose host_kinds excludes the current host parks per §5.
- P1: attestation must contain 'ROUTER INTERCEPT'
- P2a: refuses an elevated shell
- P3: source PSDs must exist
- P4: temp dir must be addressable as a Windows drive path
- P5: a same-day backup dir must exist
- All prerequisites only echo OK/FAIL/WARN. None exits non-zero, so the agent enforces them.
- V1: phase must be compositing or in_progress. Phase review is read-only: export scripts allowed, mutation scripts forbidden.
- V2: the export colour profile must match color_science (studio default: export sRGB IEC61966-2.1 for web; working files stay in their original profile)
- danger_class LOCAL_DESTRUCTIVE ('originals are sacred')
- hardware gate: depends_on_skill hardware_compute with workload_class batch_2d ('batch runs need a PASS token'). hardware_compute §0 lists 'batch adobe_suite_uxp' as gated, but no prerequisite or step in this file reads or claims state/compute_gate.json.
- batch_2d thresholds (hardware_compute ARTIFACT B): gpu.status any, memory.available_gb_min 5, memory.free_pct_min 25, memory.swap_used_mb_max 6144, power.source_in [ac], thermal.cpu_temp_c_max 90, thermal.cpu_perf_pct_min 65, disk.free_gb_min 10. Token TTL 1800s, single-flight.
- no '{{' may remain before execution (step 2; ARTIFACT D exits 1 with unresolved params)
- run ONE artifact at a time, with a flush between artifacts
- app.displayDialogs = DialogModes.NO in ARTIFACTS A and B; ARTIFACT D timeout (default 600s)
- on ok:false, do not retry blind: read err, fix params, re-extract
- CONTEXT FLUSH №1 (step 6): log the result JSON to event_log, update progress_pct, drop the script body
- CONTEXT FLUSH №2 (step 9): writeback; keep only output paths and the result summary
- cleanup: the temp .jsx count must be 0; an orphaned .jsx counts as a protocol violation
- Router §3: render_philosophy is unauthored (L3 park). color_science is authored at L0, but its §5 says it gives a palette, not a colour pipeline (no working space, LUT or grading).

**Invoked by**

- Router.md intercept step 7 EXECUTE (Trigger A: photoshop / premiere / after effects / comp / batch edit; Trigger B: .psd/.aep/.prproj/.jsx, .mp4/.mov ('higgsfield or adobe_suite'), or dashboard-state detection of phase status compositing)
- dashboard.json pipeline ph_05 'Compositing' (status compositing, 18%)
- router.js routeSkill() via a UI chip (for this skill it logs PARKED, because render_philosophy is not authored)

**Invokes**

- ARTIFACT A / B / C (.jsx)
- ARTIFACT D run_jsx.sh (the 'ONLY sanctioned runner')
- PowerShell COM
- hardware_compute (declared dependency only)

**Notes**

ROUTING HEADER (verbatim): skill_id: adobe_suite_uxp | version: 2.0 | trigger_a: ["photoshop", "premiere", "after effects", "comp", "batch edit", "export layers", "grade"] | trigger_b: [".psd", ".psb", ".aep", ".prproj", ".jsx", "pipeline phase status: compositing"] | mandatory_context: [render_philosophy, color_science] | host_kinds: [windows, wsl] | writes_dashboard_keys: [pipeline.phases[*].progress_pct] | danger_class: LOCAL_DESTRUCTIVE   # scripts mutate real project files — originals are sacred | depends_on_skill: hardware_compute.skill.md   # batch runs need a PASS token | workload_class: batch_2d | version_note: v2.0 — Windows port. The execution bridge moved from macOS `osascript` to Windows COM automation via PowerShell. The ExtendScript artifacts in §3 are unchanged: they run identically on either host.

FOUR PARTS: §0 Routing Header (Part 1); §1 Prerequisites & State Verification: P1, P2, P2a, P3, P4, P5 and V1, V2 (Part 2); §2 Execution Process (Part 3): 1 UNPACK, 2 PARAMETERIZE, 3 EXTRACT, 4 EXECUTE via PowerShell COM, 5 CAPTURE, 6 CONTEXT FLUSH №1, 7 CLEANUP (finally-guaranteed), 8 VERIFY OUTPUT, 9 CONTEXT FLUSH №2; §3 Embedded Artifacts A–D (Part 4).

SELF-EXTRACTION PROTOCOL (binding): write the artifact byte-for-byte to $STUDIO_TMP/studio_uxp_{task_id}.jsx, inject {{params}}, execute through PowerShell COM (ARTIFACT D), capture the JSON result line, and delete the temp file in a finally step even on failure. The temp dir is not /tmp because Photoshop, a Windows process, cannot open WSL paths, and ExtendScript File() refuses or mangles \\wsl$ UNC paths.

BRIDGE: Windows COM through powershell.exe. ProgIDs: Photoshop.Application and Illustrator.Application use DoJavaScriptFile; AfterFX.Application uses DoScriptFile. Premiere has no COM on Windows and stays on its CEP/UXP panel endpoint. BOOT.md says Premiere 'has no COM automation and is not driveable'. DECISIONS.md D8 says ARTIFACT C's path is unverified on this host.

DEFECTS SEEN IN SOURCE: (1) The ```bash fence opened at line 30 for the STUDIO_TMP resolver is never closed. The next column-0 fence is line 45 '```bash', so the §1 heading renders inside a code block. A side effect in verify_system.py check_host_portability: its fenced() regex pairs fences 30→45, 72→121, 146→149, 174→177 and 200→203, so the P1–P5 code and the ARTIFACT A–D bodies are never scanned for osascript or /Applications/, and prose is scanned instead. This follows from reading the regex; it was not executed. (2) Step 2 greps a /tmp path, and does so before step 3 writes the file. (3) The header declares a hardware gate, but no prerequisite checks the token.

STATUS EVIDENCE: nothing is extracted on disk (.task_scratch/, project/, backups/ and run_jsx.sh are absent; .task_scratch/ and state/ are gitignored). dashboard.json event_log has a 2026-07-01T09:12:20Z entry (actor adobe_suite_uxp, event COMP_STARTED, 'Timeline v3 → compositing 18%'), the same date as dashboard meta.generated. D8 says the Windows/WSL branches and bootstrap's COM probe 'have never been run on the target machine'. dashboard blocked_reason warns to read color_science §5 before routing adobe_suite_uxp.

### adobe_suite_uxp ARTIFACT A — Photoshop batch layer → PNG exporter

`library` · status `never-exercised`

Paths: `skills/adobe_suite_uxp.skill.md`

ExtendScript (#target photoshop). It opens SRC_PSD and, if SCALE_PCT is not 100, resizes the width by SCALE_PCT with BICUBICSHARPER (height null). For each top-level layer it shows only that layer and exports a transparent PNG-24 via Save for Web to OUT_DIR/<sanitized layer name>.png. It then closes without saving.

**Entry points**

- `run_jsx.sh <parameterized layer_export.jsx> Photoshop.Application <task_id> [timeout_seconds]`
  - does: Runs through ARTIFACT D over COM (DoJavaScriptFile)
  - changes: writes OUT_DIR/*.png and OUT_DIR/_result.json; creates OUT_DIR if missing

**Inputs**

- {{SRC_PSD}}
- {{OUT_DIR}}
- {{SCALE_PCT}} (100 = no resize)

**Outputs**

- OUT_DIR/<layer name with [^\w\-] replaced by _>.png, one per top-level layer
- OUT_DIR/_result.json containing result.toSource() {ok, count, err}
- result.toSource() as the last expression (the captured result line)

**Reads**

- SRC_PSD

**Writes**

- OUT_DIR/*.png
- OUT_DIR/_result.json

**Depends on**

- Adobe Photoshop ExtendScript DOM (ExportOptionsSaveForWeb, SaveDocumentType.PNG, ExportType.SAVEFORWEB, ResampleMethod.BICUBICSHARPER)

**Gates and checkpoints**

- app.displayDialogs = DialogModes.NO
- doc.close(SaveOptions.DONOTSAVECHANGES) with the comment 'source is never mutated'

**Invoked by**

- adobe_suite_uxp step 4 / ARTIFACT D

**Notes**

Iterates doc.layers, which are top-level layers only. Params are substituted textually as {{...}} tokens. The skill calls the result 'JSON', but the script emits ExtendScript toSource() output. doc.close sits inside the try after the loop, so an exception mid-loop leaves the document open in Photoshop, unsaved and with visibility and size changed. _result.json is written into OUT_DIR, the same directory whose files step 8 counts against result.count.

### adobe_suite_uxp ARTIFACT B — Photoshop batch grade + export

`library` · status `never-exercised`

Paths: `skills/adobe_suite_uxp.skill.md`

ExtendScript (#target photoshop). For every png/tif/tiff/psd/jpg in SRC_DIR it applies adjustLevels(BLACK_IN, WHITE_IN, GAMMA, 0, 255) to the active layer, converts to 'sRGB IEC61966-2.1' (Intent.RELATIVECOLORIMETRIC), flattens, and saves a copy as JPEG (quality JPG_QUALITY, embedded profile) to OUT_DIR/<basename>_graded.jpg. It closes each file without saving.

**Entry points**

- `run_jsx.sh <parameterized batch_grade.jsx> Photoshop.Application <task_id> [timeout_seconds]`
  - does: Runs through ARTIFACT D over COM
  - changes: writes OUT_DIR/*_graded.jpg and OUT_DIR/_result.json

**Inputs**

- {{SRC_DIR}}
- {{OUT_DIR}}
- {{BLACK_IN}}
- {{WHITE_IN}}
- {{GAMMA}}
- {{JPG_QUALITY}}

**Outputs**

- OUT_DIR/<name>_graded.jpg
- OUT_DIR/_result.json {ok, count, err}
- result.toSource() result line

**Reads**

- SRC_DIR/*.(png|tif|tiff|psd|jpg), case-insensitive; .jpeg is not matched

**Writes**

- OUT_DIR/*_graded.jpg
- OUT_DIR/_result.json

**Depends on**

- Adobe Photoshop ExtendScript DOM (adjustLevels, convertProfile, JPEGSaveOptions)

**Gates and checkpoints**

- inline comment: levels values come 'from color_science context ONLY'
- app.displayDialogs = DialogModes.NO
- sources are closed with DONOTSAVECHANGES; saveAs is called with asCopy=true

**Invoked by**

- adobe_suite_uxp step 4 / ARTIFACT D

**Notes**

The heading says 'curves preset + sRGB convert', but the code applies Levels (adjustLevels), not Curves. color_science.context.md §5 says it supplies no working space, LUT or grading rules, so the source for BLACK_IN, WHITE_IN and GAMMA is currently unresolved. An exception mid-loop leaves the current document open.

### adobe_suite_uxp ARTIFACT C — Premiere Pro shot-ledger markers + offline relink report

`library` · status `never-exercised`

Paths: `skills/adobe_suite_uxp.skill.md`

ExtendScript for Premiere, run 'via bridge'. It reads a marker JSON array [{seconds, name, comment}], creates markers on the active sequence, lists offline project items at the root level of the project, and writes a report to REPORT_PATH.

**Entry points**

- `(no command given in source) Premiere CEP/UXP panel endpoint`
  - does: The only path the skill documents. ARTIFACT D's usage comment lists no Premiere ProgID, and step 4 says Premiere exposes no COM.
  - changes: adds markers to the active sequence; writes REPORT_PATH

**Inputs**

- {{MARKER_JSON_PATH}}: format [{"seconds": 12.5, "name": "sht_04", "comment": "hf_a91x seed 448811"}]
- {{REPORT_PATH}}
- an open Premiere project with an active sequence

**Outputs**

- sequence markers
- REPORT_PATH containing toSource() of {ok, markers, offline[], err}

**Reads**

- MARKER_JSON_PATH (parsed with eval)
- app.project.rootItem.children (root level only; bins are not recursed)

**Writes**

- REPORT_PATH
- Premiere project markers (in-app)

**Depends on**

- Adobe Premiere Pro
- a CEP/UXP panel endpoint (not defined anywhere in the repo)

**Gates and checkpoints**

- throws 'no active sequence' if there is none

**Invoked by**

- adobe_suite_uxp step 1 (artifact choice C)

**Notes**

Premiere has no COM automation on Windows. BOOT.md says it is 'not driveable'. DECISIONS.md D8 says ARTIFACT C still assumes the CEP/UXP panel endpoint from the macOS era and that path is unverified here. It has no #target directive and does not set displayDialogs. The example comment 'hf_a91x seed 448811' matches the dashboard event_log higgsfield_api RENDER_SUBMITTED entry 'job hf_a91x, seed 448811', which suggests a Higgsfield shot ledger (inferred from the example value).

### adobe_suite_uxp ARTIFACT D — run_jsx.sh extraction/cleanup wrapper (bash + COM)

`cli` · status `never-exercised`

Paths: `skills/adobe_suite_uxp.skill.md`

The 'ONLY sanctioned runner'. It resolves STUDIO_TMP, copies the parameterized artifact to $STUDIO_TMP/studio_uxp_<task_id>.jsx, refuses unresolved {{ tokens, picks DoJavaScriptFile or DoScriptFile by ProgID, and runs it through PowerShell COM under a timeout. An EXIT trap deletes the temp file.

**Entry points**

- `run_jsx.sh <artifact_body_file> <progid> <task_id> [timeout_seconds]`
  - does: The usage comment names Photoshop.Application, Illustrator.Application and AfterFX.Application as progids; AfterFX uses DoScriptFile, the others DoJavaScriptFile. timeout_seconds defaults to 600. The script does not validate progid; any string is passed to New-Object.
  - changes: creates $STUDIO_TMP/studio_uxp_<task_id>.jsx and removes it through trap EXIT; drives the Adobe app, which writes the artifact outputs
- `timeout "${4:-600}" powershell.exe -NoProfile -NonInteractive -Command "try { \$app = New-Object -ComObject '$2'; \$app.$METHOD('$WINPATH') } catch { '{\"ok\":false,\"err\":\"' + \$_.Exception.Message.Replace('\"','') + '\"}' }" | tr -d '\r' || echo '{"ok":false,"err":"COM call timed out — check for a modal dialog in the app"}'`
  - does: The internal COM call. It returns the script result, a JSON ok:false on COM exception, or the timeout message when the pipeline fails.
  - changes: drives the Adobe app

**Inputs**

- $1 artifact_body_file (already parameterized)
- $2 progid
- $3 task_id
- $4 timeout_seconds (optional)

**Outputs**

- stdout: the script's result line, or {"ok":false,"err":"unresolved params"} (exit 1), {"ok":false,"err":<COM exception message>}, or {"ok":false,"err":"COM call timed out — check for a modal dialog in the app"}
- stderr: '[cleanup] <tmp> removed'

**Reads**

- $1
- /proc/version
- Windows $env:TEMP via powershell.exe (WSL branch)

**Writes**

- $STUDIO_TMP/studio_uxp_<task_id>.jsx (temporary)

**Depends on**

- bash (set -euo pipefail)
- powershell.exe
- wslpath or cygpath
- timeout
- Windows COM-registered Adobe apps

**Environment and secret names (names only)**

- STUDIO_TMP
- TEMP

**Gates and checkpoints**

- exits 1 if the copied file still contains '{{'
- timeout (default 600s), because 'a modal dialog in the target app blocks COM indefinitely'
- trap 'rm -f "$TMP"' EXIT guarantees deletion

**Invoked by**

- adobe_suite_uxp step 4 (EXECUTE) and the self-extraction protocol step (3)

**Invokes**

- powershell.exe New-Object -ComObject <progid>
- ARTIFACT A or B (.jsx)

**Notes**

No run_jsx.sh exists on disk, and the skill names no extraction path for it. Skill step 3 writes directly to $STUDIO_TMP/studio_uxp_<task_id>.jsx, the same path ARTIFACT D copies $1 into, and the file does not reconcile the two. tools/bootstrap.sh separately checks COM registration with Test-Path 'HKLM:\SOFTWARE\Classes\<ProgID>' for the same three ProgIDs, not New-Object, so it does not launch the app.

### blender_python (skill)

`skill` · status `never-exercised`

Paths: `skills/blender_python.skill.md`

Agent-executed skill for 3D inserts and previz. It unpacks fixed bpy templates to tools/bpy/, drives them from a JSON params sidecar and runs them headless (blender -b -P). It requires a fresh, unconsumed render_3d_cpu PASS token from hardware_compute. EEVEE is the default engine; Cycles is CPU-only with a sample ceiling.

**Entry points**

- `if [ -z "${BLENDER_BIN:-}" ]; then if command -v blender >/dev/null 2>&1; then BLENDER_BIN=$(command -v blender); else for root in "/c/Program Files/Blender Foundation" "/mnt/c/Program Files/Blender Foundation"; do for cand in "$root"/Blender*/blender.exe; do [ -x "$cand" ] && BLENDER_BIN="$cand" && break 2; done; done; fi; fi; BLENDER="${BLENDER_BIN:-blender}"; "$BLENDER" --version 2>/dev/null | head -1 | grep -qE "Blender (4|5)\." && echo "OK:P2 ($BLENDER)" || echo "FAIL:P2 need Blender 4+ — set BLENDER_BIN"`
  - does: P2: locates the Blender binary (BLENDER_BIN override, then PATH, then the Program Files glob for Git Bash and WSL) and requires version 4.x or 5.x
  - changes: sets shell vars BLENDER_BIN and BLENDER
- `DEVS=$("$BLENDER" -b --python-expr "import bpy;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.get_devices();print('DEV:',[(d.name,d.type) for d in prefs.devices])" 2>/dev/null | grep "^DEV:"); [ -n "$DEVS" ] && echo "OK:P3 $DEVS" || echo "FAIL:P3 cycles devices not enumerable"; echo "$DEVS" | grep -qE "OPTIX|CUDA" && echo "WARN:P3 discrete GPU present — this skill assumes CPU/EEVEE (D8)"`
  - does: P3: enumerates Cycles devices headless. It fails if none can be enumerated and warns if OPTIX or CUDA appears.
  - changes: nothing
- `python3 - <<'PY' import json, time try: t = json.load(open("state/compute_gate.json")) age = time.time() - t["ts_epoch"] ttl = t.get("ttl_seconds", 1800) reasons = [] if t.get("verdict") != "PASS": reasons.append("verdict=%s" % t.get("verdict")) if age >= ttl: reasons.append("stale (%ds > %ds TTL)" % (age, ttl)) if t.get("workload") != "render_3d_cpu": reasons.append("wrong workload=%s" % t.get("workload")) if t.get("consumed_by") is not None: reasons.append("already consumed by %s" % t["consumed_by"]) except Exception as e: reasons = ["unreadable token: %s" % e] print("OK:P4" if not reasons else "FAIL:P4 " + "; ".join(reasons)) PY`
  - does: P4 HARDWARE GATE: validates the gate token for this workload
  - changes: nothing
- `mkdir -p renders/3d tools/bpy && echo "OK:P5"`
  - does: P5: creates the output and tools dirs
  - changes: creates renders/3d and tools/bpy
- `"$BLENDER" -b -P tools/bpy/camera_path.py -- tools/bpy/params.json`
  - does: Step 6 RENDER with "render": true. Step 4 DRY RUN is the same invocation with "render": false; the file gives no separate command for it.
  - changes: with render:true, renders PNG frames using the out_dir/<shot_id>_ filepath prefix

**Inputs**

- tools/bpy/params.json (schema in ARTIFACT C)
- state/compute_gate.json PASS token for render_3d_cpu
- optional import_glb asset
- mandatory context: render_philosophy, motion_language. Router §3 adds visual_identity 'if flagged in dashboard'.
- Content MD '## Decisions in Force' / '## Method' in place of dashboard.active_variables (MIGRATION PENDING banner)

**Outputs**

- stdout 'MANIFEST::{json}' (shot_id, frames, res, cam_checksum) and 'RENDER_DONE::<shot_id>'
- PNG frames under out_dir (render.filepath = out_dir + '/' + shot_id + '_'; default out_dir renders/3d/sht_3d_01)
- .blend from lowpoly_gen (out_blend), if it is run
- consumed_by stamp in state/compute_gate.json
- dashboard progress_pct updated every 10% from 'Fra:' lines; manifest logged to event_log

**Reads**

- ./.task_scratch/attestation.txt
- state/compute_gate.json
- tools/bpy/params.json
- import_glb path

**Writes**

- tools/bpy/camera_path.py
- tools/bpy/lowpoly_gen.py
- tools/bpy/params.json
- state/compute_gate.json (consumed_by: blender_python)
- renders/3d/
- out_blend (default project/blend/lowpoly_env_v1.blend)
- dashboard.json pipeline.phases[*].progress_pct and event_log

**Depends on**

- Blender 4.x or 5.x (blender / blender.exe)
- bpy (inside Blender), Cycles add-on, glTF importer
- python3 on the host (P4)
- bash, grep, head, mkdir

**Environment and secret names (names only)**

- BLENDER_BIN

**Gates and checkpoints**

- host_kinds: [windows, wsl, linux]
- P1: attestation must contain 'ROUTER INTERCEPT'
- P2: Blender major version 4 or 5
- P3: FAIL if Cycles devices cannot be enumerated; WARN if a CUDA/OPTIX device is present ('stop and re-read DECISIONS.md § D8')
- P4: verdict PASS, age < ttl_seconds (default 1800), workload == render_3d_cpu, consumed_by null ('one token, one workload'; single-flight)
- All prerequisites only echo OK/FAIL/WARN and never exit non-zero
- render_3d_cpu thresholds (hardware_compute ARTIFACT B): gpu.status any, memory.available_gb_min 8, memory.free_pct_min 40, memory.swap_used_mb_max 3072, power.source_in [ac], thermal.cpu_temp_c_max 80, thermal.cpu_perf_pct_min 85, disk.free_gb_min 20
- Step 2 CLAIM THE GATE: write "consumed_by": "blender_python" immediately before the first render call
- V1: fps and aspect_ratio must equal dashboard.active_variables (24 fps, 21:9, e.g. 2688×1152). This is stale per the D6 banner; read it from the Content MD instead.
- V2: camera moves must map to a named motion_language preset (the bpy path template mirrors the Higgsfield motion library)
- Step 4 DRY RUN (render:false) before step 6 RENDER
- CONTEXT FLUSH №1 (step 5): log the manifest to event_log; drop scene-construction reasoning
- Step 7 VERIFY: frame count on disk == manifest count; spot-check first, middle and last frames against render_philosophy (no default grey world, no unset film exposure)
- CONTEXT FLUSH №2 (step 8): writeback paths and the manifest summary. Delete params.json only if the operator marks the shot final; archiving is preferred.
- Cycles: device forced to CPU, samples = min(samples, samples_ceiling) (defaults 64/128), denoising on
- danger_class LOCAL_COMPUTE_HEAVY; Router §10 refuses heavy work 'without a fresh PASS token from verify_compute.sh'
- Router §3: render_philosophy and motion_language are both unauthored (L3 park)
- The skill cites hardware_compute §2.8 (continuous re-probe every 5 minutes; two consecutive DENYs mean checkpoint-and-pause) only in prose. Neither the skill steps nor ARTIFACT A implement a re-probe or a checkpoint.

**Invoked by**

- Router.md intercept step 7 (Trigger A: 3D / blender / camera path / low-poly / procedural / rig; Trigger B: .blend/.fbx/.obj, or dashboard-state detection of a queued matching phase)
- dashboard.json pipeline ph_04 '3D Insert Shots' (queued, 0%)
- router.js routeSkill() UI chip (logs PARKED for this skill, since its gates are not authored)

**Invokes**

- ARTIFACT A camera_path.py
- ARTIFACT B lowpoly_gen.py (unpacked in step 1, but no numbered step runs it)
- hardware_compute gate token (reads it and claims it)

**Notes**

ROUTING HEADER (verbatim): skill_id: blender_python | version: 2.0 | trigger_a: ["3D", "blender", "camera path", "low-poly", "procedural", "insert shot", "previz"] | trigger_b: [".blend", ".fbx", ".obj", ".glb", "pipeline phase skill=blender_python"] | mandatory_context: [render_philosophy, motion_language] | host_kinds: [windows, wsl, linux] | writes_dashboard_keys: [pipeline.phases[*].progress_pct] | danger_class: LOCAL_COMPUTE_HEAVY   # rendering — hardware_compute gate REQUIRED first | depends_on_skill: hardware_compute.skill.md   # must PASS before any render step | workload_class: render_3d_cpu | version_note: v2.0 — single-host port. The CUDA node is gone; this renders on a 14" laptop with Intel integrated graphics. EEVEE is the default engine and Cycles is CPU-only.

FOUR PARTS: §0 header plus the MIGRATION PENDING banner (DECISIONS.md D6); §1 P1–P5 plus V1, V2; §2 steps 1 UNPACK, 2 CLAIM THE GATE, 3 PARAMETERIZE, 4 DRY RUN, 5 CONTEXT FLUSH №1, 6 RENDER, 7 VERIFY, 8 CONTEXT FLUSH №2; §3 ARTIFACT A camera_path.py, B lowpoly_gen.py, C params sidecar schema.

BRIDGE: headless Blender CLI (blender -b -P <script> -- <params.json>, and blender -b --python-expr for P3). The templates are 'localized tools'; the skill forbids improvising bpy line-by-line in an interactive session.

INCONSISTENCIES IN SOURCE: V1 cites 2688×1152, but ARTIFACT C defaults to 1920×823 and says 2688 is 'the deliberate, gated exception' (D8 item 5 confirms the drop). BOOT.md §4 and the evaluate_gate.py docstring mint with 'render_3d_cpu --consume blender_python', which sets consumed_by at mint time, and P4 then fails with 'already consumed by blender_python'. P5 does not create project/blend/, the default out_blend dir. None of tools/bpy/, renders/ or state/compute_gate.json exist on disk; state/ exists, holding only rag_index and vault_manifest.json.

### blender_python ARTIFACT A — camera_path.py (rigid bezier camera pathing)

`cli` · status `never-exercised`

Paths: `skills/blender_python.skill.md`, `tools/bpy/camera_path.py (extraction target; not on disk)`

Headless bpy script. It resets to factory settings (use_empty=True), sets fps, resolution and frame range, and picks the engine: EEVEE (BLENDER_EEVEE_NEXT) by default, or Cycles with device CPU, capped samples and denoising. It optionally imports a GLB and builds a 3D bezier path (AUTO handles, path_duration = frames). It adds a camera (lens_mm) with FOLLOW_PATH and TRACK_TO constraints targeting an empty at look_at, keyframes the path offset with SINE EASE_IN_OUT, adds a three-point AREA light rig, prints a manifest, and renders the animation if render is true.

**Entry points**

- `blender -b -P camera_path.py -- params.json`
  - does: Builds the scene and prints MANIFEST::. With "render": true it runs bpy.ops.render.render(animation=True) and prints RENDER_DONE::<shot_id>.
  - changes: with render:true, writes PNG frames with the filepath prefix out_dir/<shot_id>_

**Inputs**

- params.json (argv after '--'). Required keys: fps, resolution, frames, out_dir, shot_id, path_points, look_at. Optional: engine (default BLENDER_EEVEE_NEXT), samples (64), samples_ceiling (128), lens_mm (35), import_glb, render (False).

**Outputs**

- stdout MANIFEST::{shot_id, frames, res, cam_checksum = round(sum of all path_points coords, 4)}
- stdout RENDER_DONE::<shot_id>
- PNG frames

**Reads**

- params.json
- import_glb file

**Writes**

- out_dir/<shot_id>_* PNG frames

**Depends on**

- Blender bpy
- glTF importer (bpy.ops.import_scene.gltf)

**Gates and checkpoints**

- if the engine is CYCLES: scn.cycles.device = 'CPU', samples = min(samples, samples_ceiling), use_denoising True; otherwise eevee.taa_render_samples = samples
- render defaults to False, so a dry run is the default

**Invoked by**

- blender_python steps 4 and 6

**Notes**

Light rig: key (4,-4,5) energy 1000, fill (-5,-2,3) 300, rim (0,6,4) 600, all AREA ('values from render_philosophy defaults', a context file that is not authored). The follow-path offset is keyframed from 0 at frame 1 to -frames at the last frame. Track axes are TRACK_NEGATIVE_Z / UP_Y. The file format is PNG. The comment on the easing ties it to the 'dolly_in_slow' grammar.

### blender_python ARTIFACT B — lowpoly_gen.py (low-poly procedural terrain + scatter)

`cli` · status `never-exercised`

Paths: `skills/blender_python.skill.md`, `tools/bpy/lowpoly_gen.py (extraction target; not on disk)`

Headless bpy script. It builds deterministic low-poly terrain: a grid, CLOUDS displace, decimate, modifiers applied, flat shading. It applies a flat Principled BSDF material from base_color_rgba (roughness 0.9), scatters seeded icospheres (subdivisions 1, radius 0.1–0.5, z 0.3), saves a .blend and prints a manifest.

**Entry points**

- `blender -b -P lowpoly_gen.py -- params.json`
  - does: Generates the environment and saves it to out_blend
  - changes: writes the out_blend .blend file

**Inputs**

- params.json. Required keys: seed, grid, size, base_color_rgba, out_blend. Optional: noise_scale (default 2.5), relief (1.6), facet_ratio (0.12), scatter_count (40).

**Outputs**

- out_blend .blend
- stdout MANIFEST::{seed, polys, blend}

**Reads**

- params.json

**Writes**

- out_blend (default project/blend/lowpoly_env_v1.blend)

**Depends on**

- Blender bpy

**Gates and checkpoints**

- random.seed(seed) for deterministic geometry (comment: 'dashboard seed_lock')
- 'LOW-POLY LAW: flat shading, always'

**Invoked by**

- no numbered step in blender_python §2 runs it; step 1 UNPACK only extracts it

**Notes**

It has no render or dry-run switch and always writes the .blend. Its material comment says 'from dashboard master_palette', a key that no longer exists (D6). noise_scale is read but absent from the ARTIFACT C schema.

### blender_python ARTIFACT C — params sidecar schema (tools/bpy/params.json)

`data` · status `never-exercised`

Paths: `skills/blender_python.skill.md`, `tools/bpy/params.json (target; not on disk)`

The single per-task parameter file shared by camera_path.py and lowpoly_gen.py. The .py bodies are never edited per task. It is also the reproducibility record.

**Gates and checkpoints**

- archive rather than delete; delete only if the operator marks the shot final (step 8)

**Invoked by**

- blender_python step 3 PARAMETERIZE

**Notes**

Default values: shot_id sht_3d_01; fps 24; resolution [1920, 823]; _resolution_note '21:9 at 1920 wide. The v1.x default was 2688x1152, sized for a 48 GB render node; at 16 GB shared with the compositor this is the working size and 2688 is the deliberate, gated exception.'; frames 120; engine BLENDER_EEVEE_NEXT; _engine_enum [BLENDER_EEVEE_NEXT, CYCLES]; samples 64; samples_ceiling 128; lens_mm 35; path_points [[8,-8,3],[5,-5,2.5],[2.5,-2.5,2]]; look_at [0,0,1]; import_glb null; out_dir renders/3d/sht_3d_01; render false; seed 448811; grid 64; size 20; relief 1.6; facet_ratio 0.12; base_color_rgba [0.043,0.055,0.09,1.0]; scatter_count 40; out_blend project/blend/lowpoly_env_v1.blend. There is no noise_scale key.

### css_html_ui (skill)

`skill` · status `partial`

Paths: `skills/css_html_ui.skill.md`

Agent-executed front-end construction skill. Every colour, font, size, radius, shadow, spacing step and status meaning in generated markup or DOM mutation must resolve to a key in the ARTIFACT A token dictionary, and CSS may reference only var(--…) properties from ARTIFACT B. There is no host-native bridge.

**Entry points**

- `python3 -c "import json;json.load(open('tokens/design_tokens.json'))" 2>/dev/null && echo "OK:P2" || echo "INIT:P2 extract ARTIFACT A → tokens/design_tokens.json first"`
  - does: P2: checks that the extracted token file exists and parses
  - changes: nothing
- `python3 - <<'PY' import json t=json.load(open('tokens/design_tokens.json'))["color"] d=json.load(open('dashboard.json'))["active_variables"]["master_palette"] core=[t["bg"]["base"],t["accent"]["amber"],t["accent"]["cyan"],t["accent"]["alert"],t["ink"]["base"]] print("OK:P3" if [c.upper() for c in core]==[c.upper() for c in d] else "FAIL:P3 token/palette drift") PY`
  - does: P3: checks token/palette parity against dashboard active_variables.master_palette. It has no try/except. Today it raises FileNotFoundError on the tokens file; after extraction it would raise KeyError on master_palette (stale per D6).
  - changes: nothing
- `if [ -z "${TARGET_FILE:-}" ] || [ -f "${TARGET_FILE}" ]; then echo "OK:P4"; else echo "FAIL:P4 target missing: $TARGET_FILE"; fi`
  - does: P4: an edit target must exist (passes when TARGET_FILE is unset)
  - changes: nothing
- `grep -nE '#[0-9a-fA-F]{3,8}\b' build/*.css build/*.html | grep -v "tokens.css" && echo "FAIL: raw hex found" || echo "OK: no raw hex"`
  - does: Step 6 AUDIT: finds raw hex outside tokens.css
  - changes: nothing
- `grep -nE 'font-family:(?!.*var\().' -P build/*.css && echo "FAIL: un-tokened font" || echo "OK: fonts tokened"`
  - does: Step 6 AUDIT: finds font-family declarations that do not use var()
  - changes: nothing

**Inputs**

- component/page request
- TARGET_FILE (when editing)
- ARTIFACT A tokens / ARTIFACT B CSS vars
- mandatory context: typography_system, visual_identity, brand_voice
- control_room.html as the reference implementation (V1)
- for product work: the ui_ux_intelligence ARTIFACT B design_system handoff (untested per D9)

**Outputs**

- tokens/design_tokens.json and tokens/tokens.css (step 1 extraction)
- markup and CSS that reference only var(--…) (the audit targets build/*.css and build/*.html)
- audit results
- per-component component name plus tokens consumed, logged to the dashboard (step 5)
- legacy hard-coded values reported as debt, not rewritten (step 2)

**Reads**

- ./.task_scratch/attestation.txt
- tokens/design_tokens.json
- dashboard.json (P3)
- TARGET_FILE
- control_room.html
- build/*.css
- build/*.html

**Writes**

- tokens/design_tokens.json
- tokens/tokens.css
- markup/CSS files (location not declared; the audit implies build/)
- dashboard.json pipeline.phases[*].progress_pct and event log

**Depends on**

- python3
- grep (step 6 passes both -E and -P)
- JetBrains Mono font (named in the token stacks; the skill does not say how it is loaded. The existing surfaces load it from the Google Fonts CDN: control_room.html, hub/index.html, tools/brush-designer/styles.css)

**Environment and secret names (names only)**

- TARGET_FILE

**Gates and checkpoints**

- host_kinds: [windows, wsl, linux] ('network/API skill — no host-native bridge'). There is no depends_on_skill and no workload_class, so no hardware gate applies.
- Anti-hallucination law: a value with no token is proposed to the operator and the skill waits. Hex literals, arbitrary px values and un-tokened font stacks in output count as a protocol violation.
- P1: attestation
- P2: token file must parse (reports INIT otherwise)
- P3: parity with master_palette (stale)
- P4: target file must exist
- All prerequisites only echo OK/FAIL/INIT and never exit non-zero
- V1: check against control_room.html (same tokens, same grid discipline)
- V2: copy follows brand_voice: sentence case, plain verbs, controls named for what they do
- Step 3 PLAN: a component whose plan contains a non-token value stops
- Step 6 AUDIT: no raw hex, no un-tokened fonts
- Step 7: verify at --bp-* breakpoints, visible :focus-visible (focus.ring), prefers-reduced-motion for motion.* tokens
- CONTEXT FLUSH №1 (step 5, after each component): log the component name and tokens consumed; drop construction reasoning
- CONTEXT FLUSH №2 (step 8): writeback file paths and audit results; keep only the token-consumption summary
- ARTIFACT A mutation_policy: operator approval only
- danger_class LOW ('but style drift is BRAND damage — tokens are law')
- Router §3: typography_system and visual_identity are authored at L0; brand_voice is unauthored, so the route parks (DECISIONS.md D9)

**Invoked by**

- Router.md intercept step 7 (Trigger A: UI / dashboard / component / landing page / DOM; Trigger B: .html/.css/.jsx(web), or a matching queued phase). Router Trigger B sends tokens/design_tokens.json to ui_ux_intelligence, not to this skill.
- dashboard.json pipeline ph_06 'Delivery UI Page' (queued, 0%)
- ui_ux_intelligence (upstream: 'This skill decides what a thing should look like. css_html_ui builds it.')
- router.js routeSkill() UI chip (logs PARKED, because brand_voice is not authored)

**Invokes**

- ARTIFACT A (extract)
- ARTIFACT B (extract)
- ARTIFACT C (rules for JS)

**Notes**

ROUTING HEADER (verbatim): skill_id: css_html_ui | version: 1.0 | trigger_a: ["UI", "dashboard", "component", "landing page", "DOM", "front-end", "panel", "widget"] | trigger_b: [".html", ".css", ".jsx(web)", "pipeline phase skill=css_html_ui"] | mandatory_context: [typography_system, visual_identity, brand_voice] | host_kinds: [windows, wsl, linux]   # network/API skill — no host-native bridge | writes_dashboard_keys: [pipeline.phases[*].progress_pct] | danger_class: LOW   # but style drift is BRAND damage — tokens are law.

FOUR PARTS: §0 header plus the anti-hallucination law; §1 P1–P4 plus V1, V2; §2 steps 1 UNPACK, 2 READ TARGET, 3 PLAN, 4 BUILD, 5 CONTEXT FLUSH №1, 6 AUDIT, 7 RESPONSIVE + A11Y PASS, 8 CONTEXT FLUSH №2; §3 ARTIFACT A token dictionary, B tokens.css projection, C DOM mutation contract.

The file carries a MIGRATION PENDING banner (DECISIONS.md D6). P3 reads active_variables.master_palette, which no longer exists: dashboard.json active_variables holds only _note, content_md, resolved_context and provisional_constraints. DECISIONS.md D10 records that tokens/design_tokens.json and tokens/tokens.css still do not exist on disk and that P2 'still reports INIT:P2 on every run'. Audit quirks: step 6 passes both -E and -P to grep. Its 'grep -v tokens.css' filter only excludes a tokens.css inside build/, while step 1 writes tokens/tokens.css. The law names 'shadow' as a tokened category, but ARTIFACT A defines no shadow token (elevation.model: 'There is no glow, no shadow'). STATUS 'partial': the numbered process has never produced its extraction targets. ARTIFACT A itself is live, being hand-transcribed into three surfaces and machine-checked. The vault Content MD vault/studio-os/ui/ui-ux-intelligence-integration.md lists skills [ui_ux_intelligence, css_html_ui] and records the 2026-08-31 and 2026-09-01 token and retheme edits.

### css_html_ui ARTIFACT A — Design Token Dictionary

`data` · status `partial`

Paths: `skills/css_html_ui.skill.md`, `tokens/design_tokens.json (extraction target; not on disk)`

The 'ABSOLUTE SOURCE OF TRUTH' for studio-surface tokens (HARD MONO, DECISIONS.md D10). control_room.html, hub/styles.css, tools/brush-designer/styles.css and the three brand gate files (visual_identity, typography_system, color_science) are transcribed from it. verify_system.py check_palette_parity parses it in place.

**Entry points**

- `python3 tools/verify_system.py`
  - does: check_palette_parity regex-parses color.bg.{base,raise,panel} and color.accent.{amber,cyan,alert,queued} (7 values) from this artifact and compares them with the --bg, --bg-raise, --bg-panel, --amber, --cyan, --alert and --queued vars in control_room.html. Run by BOOT.md and by .github/workflows/verify.yml on push to main and on PRs.
  - changes: nothing

**Gates and checkpoints**

- mutation_policy: 'operator-approval only; agent proposes, never commits token changes'
- contrast_floor (verbatim in notes)

**Invoked by**

- css_html_ui step 1 UNPACK
- tools/verify_system.py check_palette_parity
- ui_ux_intelligence ARTIFACT D gate regeneration protocol (step 2 DIFF against it)

**Notes**

FULL CONTENT (in-string line breaks normalized to spaces): $schema 'studio-os/design-tokens/v1'; revision '2026-09-01 — HARD MONO retheme (DECISIONS.md § D10)'; mutation_policy 'operator-approval only; agent proposes, never commits token changes'.
contrast_floor.rule: 'every ink.* and accent.* value clears 4.5:1 on all three bg.* grounds; every accent used as a status dot, node, or progress fill clears 3.0:1 on its own ground, line.base included; and bg.base printed on an accent fill — the inversion elevation model — clears 4.5:1 on that fill'. contrast_floor.verified: '2026-09-01 — worst text case accent.alert 5.19:1 on bg.panel; worst non-text case accent.alert 3.31:1 on line.base; worst inversion case bg.base on accent.alert 5.92:1; ink.dim 6.88:1 on bg.panel'. contrast_floor.why: 'the pre-2026-08-31 palette failed twice (accent.queued 2.23:1, ink.dim 3.78:1) and the fix is not allowed to be undone by a later retheme. The HARD MONO palette raises every floor rather than trading any of them, and it adds a third floor the previous palette did not need: elevation is now a solid accent fill carrying ground-coloured ink, so an accent too dark to print black on is rejected even if it reads fine as text.'
color.bg: base #000000, raise #0B0B0B, panel #141414. color.line: base #383838. color.ink: base #FFFFFF, dim #9E9E9E. color.accent: amber #FFC400, cyan #00E5FF, alert #FF3B30, queued #8A8AFF.
semantic: status.nominal {color: '{color.accent.cyan}', meaning 'active / healthy / complete'}; status.waiting {'{color.accent.amber}', 'awaiting_render / review / warning'}; status.blocked {'{color.accent.alert}', 'blocked / error / violation'}; status.idle {'{color.accent.queued}', 'queued / idle / disabled'}.
font.policy 'one family, two weights. There is no second typeface and no third weight.'; font.display {stack "'JetBrains Mono', ui-monospace, monospace", weight 800, use 'brand mark, headings, phase names, numerals'}; font.mono {same stack, weight 400, use 'body, data, labels, logs'}.
type_scale: xs 10px, sm 11px, base 13px, md 14px, lg 20px, xl 30px; xl_rule 'xl is the brand mark and nothing else — one oversized voice per surface'; weight.body 400, weight.mid 500, weight.display 800; tracking.label 0.18em, tracking.display 0.08em, tracking.brand 0.02em.
space: 1 4px, 2 8px, 3 16px, 4 24px, 5 32px. radius: panel '0', chip '0', bar '0', pill '0'.
border: hairline '1px solid {color.line.base}', heavy '2px solid {color.line.base}', state '2px solid <the accent already carrying that element's state>', rule 'structure is a line in line.base; selection and state are a line in the accent that element is already signalling. Weight, not colour, separates the two.'
elevation: model 'inversion. A live element fills solid with its state accent and prints bg.base on top of it. There is no glow, no shadow, and no gradient — nothing in this system is softened to imply depth.'; fill.nominal '{color.accent.cyan}', fill.waiting '{color.accent.amber}', fill.blocked '{color.accent.alert}', fill.idle '{color.accent.queued}', fill.ink '{color.bg.base}'.
motion: bar_fill 'width .12s linear', blink '1.2s steps(1, end) infinite', hover 'none — state changes are instant; there is no eased hover', reduced_motion_rule 'all motion.* tokens null out under prefers-reduced-motion'.
focus: ring '2px solid {color.accent.cyan}', offset '2px'.
There are no grid, breakpoint or shadow keys.
OBSERVATIONS: contrast_floor.rule, .verified and .why, border.rule and elevation.model contain literal line breaks inside JSON string values, so a byte-for-byte extraction would not pass P2's json.load. font.policy says 'no third weight', but type_scale defines three weights (400/500/800), D10 cites '400 / 500 / 800', and all surfaces load those three weights. check_palette_parity machine-checks only 7 values, only against control_room.html; hub/styles.css and brush-designer are not machine-checked (the vault Content MD's Next Steps list this).

### css_html_ui ARTIFACT B — CSS projection (tokens/tokens.css)

`data` · status `partial`

Paths: `skills/css_html_ui.skill.md`, `tokens/tokens.css (extraction target; not on disk)`

The :root custom-property projection of ARTIFACT A, meant to be 'imported by every page'. It also adds a prefers-reduced-motion override and a global :focus-visible rule. Its header says 'GENERATED FROM design_tokens.json. Edit the JSON, never this file.'

**Inputs**

- ARTIFACT A

**Outputs**

- CSS vars: --bg --bg-raise --bg-panel --line --ink --ink-dim --amber --cyan --alert --queued --font-disp --font-mono --fw-body --fw-mid --fw-disp --fs-xs --fs-sm --fs-base --fs-md --fs-lg --fs-xl --track-label --track-display --track-brand --sp-1..--sp-5 --r-panel --r-chip --r-bar --r-pill --grid-cols:12 --grid-gap:16px --grid-max:1440px --bp-tablet:980px --bp-mobile:640px --rule --rule-heavy --fill-ink --m-bar-fill --m-blink --focus-ring --focus-offset

**Gates and checkpoints**

- @media (prefers-reduced-motion: reduce) sets --m-bar-fill and --m-blink to none, and forces animation-duration and transition-duration to .001ms !important, animation-iteration-count to 1 and scroll-behavior to auto on every element
- global :focus-visible { outline: var(--focus-ring); outline-offset: var(--focus-offset) }
- Step 4 BUILD may reference only var(--…) from this file

**Invoked by**

- css_html_ui step 1 UNPACK and step 4 BUILD

**Notes**

No generator script exists; the projection is hand-written. --grid-* and --bp-* have no source key in ARTIFACT A. These ARTIFACT A keys are not projected: semantic.*, elevation.fill.nominal/waiting/blocked/idle, border.state, contrast_floor and font.policy. control_room.html and hub/styles.css carry in-page copies of this :root block that lack --grid-cols and the --bp-* vars. tools/brush-designer/styles.css uses a different variable naming scheme and adds values that are not in ARTIFACT A: --bg-panel-hover #1F1F1F, --text-muted #6E6E6E, --bg-canvas #F5F0E8 (called an artwork surface) and a color-mix() accent-dim.

### css_html_ui ARTIFACT C — DOM Mutation Contract

`protocol` · status `partial`

Paths: `skills/css_html_ui.skill.md`

Rules for router.js and any future JS. JS toggles token-backed classes (c-cyan, c-amber, c-alert, c-dim) or sets custom properties from tokens.css, and never sets literal colours. The status-to-class mapping equals ARTIFACT A semantic.*, with router.js statusColor() as its projection. New DOM regions are grid areas. Every innerHTML write goes through an escape function (router.js esc()).

**Gates and checkpoints**

- 'Any innerHTML write passes through an escape function (see router.js esc()) — no exceptions'
- 'Status → class mapping is EXACTLY the semantic.* table in ARTIFACT A'

**Invoked by**

- router.js (statusColor, esc)
- control_room.html

**Notes**

router.js statusColor() maps complete, in_progress and compositing to c-cyan, awaiting_render and review to c-amber, blocked to c-alert and queued to c-queued, with c-dim as the fallback. It emits c-queued, which ARTIFACT C's class list does not name; control_room.html defines .c-queued, so verify_system.py check_router_js (every c-* class router.js emits must be defined in control_room.html) passes. router.js renderVariables writes inline style='background:<hex>' for legacy master_palette swatches (regex-validated hex) and style='width:<pct>%' for progress bars. ARTIFACT C's literal-colour rule has no carve-out for either.

## Usage flows

### Adobe batch job (e.g. Photoshop layer export)

1. Router intercept: Trigger A/B fires (phase ph_05 is compositing). Resolve render_philosophy and color_science by the §5 ladder; render_philosophy is unauthored and the vault has 1 Content MD, so L3 parks today. Emit the attestation (Router §6 prints it; nothing in the repo writes ./.task_scratch/attestation.txt). Set the phase to in_progress (step 6).
2. (Declared, not enforced by this skill) obtain a batch_2d PASS token: python3 tools/hw/evaluate_gate.py batch_2d
3. Resolve STUDIO_TMP and towin() (WSL: the Windows %TEMP% through wslpath; Git Bash: $TEMP)
4. P1 attestation, P2 Photoshop process, P2a non-elevated shell, P3 ./project/psd/*.psd, P4 temp canary, P5 ./backups/<today>; V1 phase compositing or in_progress (review = export-only); V2 export profile against color_science
5. Pick ONE artifact (A, B or C) and replace every {{param}}; grep for '{{' must return 0
6. Write the .jsx to $STUDIO_TMP/studio_uxp_<task_id>.jsx
7. Run run_jsx.sh <body> Photoshop.Application <task_id> [600], i.e. timeout + powershell.exe New-Object -ComObject + DoJavaScriptFile (DoScriptFile for AfterFX)
8. Parse the last-line result {ok,count,err}; on ok:false, fix params rather than retrying blind
9. CONTEXT FLUSH №1: log the result to event_log and update progress_pct
10. Cleanup: rm the temp .jsx (the ARTIFACT D EXIT trap also does this); confirm the count of studio_uxp_*.jsx is 0
11. Verify the exported file count equals result.count; on mismatch the phase becomes blocked
12. CONTEXT FLUSH №2: writeback of output paths and summary to the Content MD (Router §7), then dashboard.json

### Adobe Premiere markers (ARTIFACT C)

1. Same intercept and prerequisites as above (P3 still requires ./project/psd/*.psd)
2. Parameterize MARKER_JSON_PATH and REPORT_PATH
3. Execute through a CEP/UXP panel endpoint. None is defined in the repo, ARTIFACT D has no Premiere ProgID, and BOOT.md says Premiere is 'not driveable'.
4. Read REPORT_PATH {ok, markers, offline[], err}

### Blender 3D insert render

1. Router intercept; resolve render_philosophy and motion_language (both unauthored, so L3 parks today)
2. hardware_compute mints a render_3d_cpu PASS token at state/compute_gate.json: python3 tools/hw/evaluate_gate.py render_3d_cpu (exit 0 PASS, 1 DENY, 2 could not evaluate). BOOT.md shows '--consume blender_python', which pre-stamps consumed_by and makes P4 fail.
3. P1 attestation; P2 locate Blender 4/5 (BLENDER_BIN, PATH or Program Files glob); P3 Cycles device enumeration (warn on CUDA/OPTIX); P4 token PASS, fresh, workload render_3d_cpu, unconsumed; P5 mkdir -p renders/3d tools/bpy
4. Step 1: write camera_path.py and lowpoly_gen.py to tools/bpy/ verbatim (skip if byte-identical)
5. Step 2: write "consumed_by": "blender_python" into state/compute_gate.json immediately before the first render call
6. Step 3: write tools/bpy/params.json (ARTIFACT C schema)
7. Step 4 dry run: "$BLENDER" -b -P tools/bpy/camera_path.py -- tools/bpy/params.json with render:false; inspect MANIFEST::
8. CONTEXT FLUSH №1: log the manifest to event_log
9. Step 6 render: the same command with render:true; watch 'Fra:' lines and update progress_pct every 10% (hardware_compute §2.8 continuous re-probe is recommended but not implemented here)
10. Step 7: frames on disk == manifest frames; spot-check first, middle and last frames against render_philosophy
11. CONTEXT FLUSH №2: writeback of paths and manifest; archive params.json unless the operator marks the shot final

### Blender low-poly environment generation

1. Write params (seed, grid, size, relief, facet_ratio, base_color_rgba, scatter_count, out_blend; optional noise_scale) to params.json
2. Ensure the out_blend directory exists (P5 does not create project/blend/)
3. blender -b -P lowpoly_gen.py -- params.json (the command from the artifact's header comment; no numbered skill step invokes it)
4. Read the MANIFEST::{seed, polys, blend} line; the .blend is saved at out_blend

### css_html_ui component build

1. Router intercept; typography_system and visual_identity resolve at L0, brand_voice is unauthored, so the route parks today (D9)
2. P1 attestation; P2 tokens/design_tokens.json parses (else INIT, so extract ARTIFACT A); P3 palette parity (stale; raises today); P4 TARGET_FILE exists
3. Step 1: extract ARTIFACT A to tokens/design_tokens.json and ARTIFACT B to tokens/tokens.css (the in-string line breaks in A would break json.load)
4. Step 2: read the full target; list token-mapped classes; report hard-coded values as debt
5. Step 3: plan components and the exact tokens each uses; stop and propose a token to the operator if any value is not tokened
6. Step 4: build markup and CSS with var(--…) only; grids use --grid-*; status colours come from semantic.*
7. CONTEXT FLUSH №1 per component: log the component and the tokens it consumed
8. Step 6: audit greps for raw hex and un-tokened font-family in build/*.css and build/*.html
9. Step 7: check the --bp-tablet 980px and --bp-mobile 640px breakpoints, :focus-visible and prefers-reduced-motion
10. CONTEXT FLUSH №2: writeback of paths, audit results and the token summary

### Studio token change (ARTIFACT A mutation)

1. ui_ux_intelligence ARTIFACT D: 1 GENERATE (--design-system against the studio brief, --json, no --persist), 2 DIFF against context/brand/*.context.md and css_html_ui ARTIFACT A, 3 IMPACT (name every control_room.html value that would move)
2. Operator approval (mutation_policy: agent proposes, never commits)
3. Edit ARTIFACT A in skills/css_html_ui.skill.md, then hand-update ARTIFACT B and the transcriptions (control_room.html :root, hub/styles.css, tools/brush-designer/styles.css, the three brand context files)
4. python3 tools/verify_system.py; check_palette_parity must be green for its 7 checked tokens (CI re-runs it on push and PR)

## Relationships

| From | Relation | To |
|---|---|---|
| Router.md | routes to it at intercept step 7 through Trigger A/B (§2) and the §3 routing table; the skill's P1 requires t… | adobe_suite_uxp (skill) |
| Router.md | routes to it at intercept step 7; P1 requires the attestation; §10 refuses heavy work without a fresh PASS to… | blender_python (skill) |
| Router.md | routes to it at intercept step 7; P1 requires the attestation | css_html_ui (skill) |
| adobe_suite_uxp (skill) | depends_on_skill; workload_class batch_2d PASS token (declared, not checked in the skill; hardware_compute §0… | hardware_compute (skills/hardware_compute.skill.md) |
| blender_python (skill) | depends_on_skill; P4 reads state/compute_gate.json (render_3d_cpu); step 2 writes consumed_by; hardware_compu… | hardware_compute (skills/hardware_compute.skill.md) |
| tools/hw/evaluate_gate.py | mints the state/compute_gate.json token that P4 validates. --consume SKILL_ID stamps consumed_by at mint time… | blender_python (skill) |
| adobe_suite_uxp (skill) | executes artifacts only through this runner | adobe_suite_uxp ARTIFACT D — run_jsx.sh extraction/cleanup wrapper (bash + COM) |
| adobe_suite_uxp ARTIFACT D — run_jsx.sh extraction/cleanup wrapper (bash + COM) | runs it over COM (Photoshop.Application.DoJavaScriptFile) | adobe_suite_uxp ARTIFACT A — Photoshop batch layer → PNG exporter |
| adobe_suite_uxp ARTIFACT D — run_jsx.sh extraction/cleanup wrapper (bash + COM) | runs it over COM | adobe_suite_uxp ARTIFACT B — Photoshop batch grade + export |
| adobe_suite_uxp ARTIFACT C — Premiere Pro shot-ledger markers + offline relink report | the example marker comment 'hf_a91x seed 448811' matches the higgsfield_api RENDER_SUBMITTED event in dashboa… | higgsfield_api (skills/higgsfield_api.skill.md) |
| adobe_suite_uxp (skill) | mandatory_context (authored L0; §5 says it supplies no working space, LUT or grading) | context/brand/color_science.context.md |
| adobe_suite_uxp (skill) | mandatory_context (file not on disk; dashboard authored:false, so L3 parks) | context/brand/render_philosophy.context.md |
| blender_python (skill) | mandatory_context (unauthored); step 7 spot-check and the ARTIFACT A light-rig defaults cite it | context/brand/render_philosophy.context.md |
| blender_python (skill) | mandatory_context (unauthored); V2 camera moves must map to its named presets | context/brand/motion_language.context.md |
| blender_python (skill) | extracts it to tools/bpy/ and runs it headless | blender_python ARTIFACT A — camera_path.py (rigid bezier camera pathing) |
| blender_python ARTIFACT A — camera_path.py (rigid bezier camera pathing) | reads params | blender_python ARTIFACT C — params sidecar schema (tools/bpy/params.json) |
| blender_python ARTIFACT B — lowpoly_gen.py (low-poly procedural terrain + scatter) | reads params (plus noise_scale, which the schema lacks) | blender_python ARTIFACT C — params sidecar schema (tools/bpy/params.json) |
| blender_python (skill) | V2: 'the bpy path template mirrors the Higgsfield motion library so 3D inserts and AI shots share one grammar' | higgsfield_api (skills/higgsfield_api.skill.md) |
| css_html_ui (skill) | mandatory_context (unauthored, so the route parks); V2 copy rules | context/brand/brand_voice.context.md |
| css_html_ui (skill) | mandatory_context (authored L0, transcribed from ARTIFACT A) | context/brand/typography_system.context.md, context/brand/visual_identity.context.md |
| css_html_ui ARTIFACT A — Design Token Dictionary | B is the CSS projection of A, hand-maintained, and adds --grid-* and --bp-* with no source in A | css_html_ui ARTIFACT B — CSS projection (tokens/tokens.css) |
| css_html_ui ARTIFACT A — Design Token Dictionary | transcribed into the :root token block; enforced by check_palette_parity (7 colours) | control_room.html |
| css_html_ui ARTIFACT A — Design Token Dictionary | mirrors ARTIFACT A (HARD MONO); not machine-checked | hub/styles.css |
| css_html_ui ARTIFACT A — Design Token Dictionary | mirrors ARTIFACT A chrome colours under different var names, plus extra un-tokened values; not machine-checked | tools/brush-designer/styles.css |
| css_html_ui ARTIFACT A — Design Token Dictionary | the three brand gates were transcribed from it (each §0 PROVENANCE; DECISIONS.md D9/D10) | context/brand/visual_identity.context.md, context/brand/typography_system.context.md, con… |
| tools/verify_system.py | check_palette_parity regex-parses 7 colour tokens and compares them with control_room.html | css_html_ui ARTIFACT A — Design Token Dictionary |
| tools/verify_system.py | check_host_portability: host_kinds must be within dashboard hardware.host_kind_enum; no macOS binary or /Appl… | adobe_suite_uxp (skill) |
| tools/verify_system.py | check_host_portability: forbids scn.cycles.device = "GPU" while hardware.gpu.cuda is false | blender_python (skill) |
| .github/workflows/verify.yml | runs it on push to main, on pull_request and on workflow_dispatch | tools/verify_system.py |
| css_html_ui ARTIFACT C — DOM Mutation Contract | statusColor() is the projection of semantic.* (it adds c-queued); esc() is the required escape function; chec… | router.js |
| ui_ux_intelligence (skills/ui_ux_intelligence.skill.md) | upstream: decides the look; its ARTIFACT B design_system JSON is the product-work handoff (untested); its ART… | css_html_ui (skill) |
| dashboard.json | pipeline ph_04 '3D Insert Shots' (queued, 0%) | blender_python (skill) |
| dashboard.json | pipeline ph_05 'Compositing' (status compositing, 18%); Trigger B dashboard-state detection; event_log COMP_S… | adobe_suite_uxp (skill) |
| dashboard.json | pipeline ph_06 'Delivery UI Page' (queued, 0%) | css_html_ui (skill) |
| tools/bootstrap.sh | preflight checks COM registration of the Photoshop/Illustrator/AfterFX ProgIDs with Test-Path HKLM:\SOFTWARE\… | adobe_suite_uxp (skill) |
| tools/bootstrap.sh | preflight uses the same Blender detection (BLENDER_BIN, PATH, Program Files glob) and warns 'blender_python w… | blender_python (skill) |
| router.js | routeSkill() UI chip resolves gates through its resolveGates table and logs PARKED for all three (unauthored… | adobe_suite_uxp (skill), blender_python (skill), css_html_ui (skill) |
| DECISIONS.md | the D6 addendum adds the MIGRATION PENDING banners (stale active_variables gates) | blender_python (skill), css_html_ui (skill) |
| DECISIONS.md | D8 Windows port: osascript replaced by COM, P2a and the ARTIFACT D timeout; EEVEE by default, Cycles on CPU,… | adobe_suite_uxp (skill), blender_python (skill) |
| DECISIONS.md | D9 addendum (contrast_floor, WCAG fixes) and D10 HARD MONO rewrite; D10 says tokens/ has never existed on disk | css_html_ui ARTIFACT A — Design Token Dictionary |
| vault/studio-os/ui/ui-ux-intelligence-integration.md | the only Content MD naming css_html_ui (frontmatter skills); its timeline records the token and retheme edits… | css_html_ui (skill) |

**Open questions the files could not settle**

- Where should run_jsx.sh (adobe ARTIFACT D) be extracted? The skill names no path, and no copy exists on disk.
- Adobe step 3 writes the parameterized script to $STUDIO_TMP/studio_uxp_<task_id>.jsx, and ARTIFACT D then runs cp "$1" to that same path. If the step-3 file is passed as $1, source and destination are the same file (under set -e, cp likely fails and the trap deletes it). Where should the body file live when D is used?
- adobe_suite_uxp declares a batch_2d hardware dependency, but none of its prerequisites or steps reads or claims state/compute_gate.json. Is enforcement expected to come only from Router §10, which names verify_compute.sh rather than evaluate_gate.py as the token source?
- What writes ./.task_scratch/attestation.txt? Every skill's P1 greps it. Router §6 only says the block is printed, and bootstrap.sh only creates the directory.
- What creates the same-day ./backups/<YYYYMMDD>/ snapshot that adobe P5 requires? No backup tool is named in the repo.
- Adobe P3 requires ./project/psd/*.psd even for ARTIFACT B (SRC_DIR) and ARTIFACT C (Premiere) tasks. Is that intended?
- Does DoJavaScriptFile return the script's last expression, and does ExtendScript toSource() output parse as the 'JSON result line' the skill expects? Nothing in the repo confirms either.
- What is the Premiere CEP/UXP panel endpoint that ARTIFACT C depends on? It is not defined anywhere in the repo, and D8 marks it unverified.
- BOOT.md and the evaluate_gate.py docstring mint with 'render_3d_cpu --consume blender_python', which sets consumed_by at mint time, but blender P4 fails on any non-null consumed_by. Which sequence is intended? A continuous-mode re-mint without --consume would also reset consumed_by to null.
- Is BLENDER_EEVEE_NEXT a valid engine enum on every version P2 accepts (Blender 4.x and 5.x)? The repo does not verify this.
- blender_python step 1 unpacks lowpoly_gen.py, but no numbered step runs it, and P5 does not create project/blend/, the default out_blend directory. Is lowpoly generation part of this skill's flow?
- Who performs the hardware_compute §2.8 continuous re-probe and checkpoint-and-pause during a long Blender render? camera_path.py has no checkpoint mechanism.
- css_html_ui ARTIFACT A has literal line breaks inside several JSON string values. Should extraction normalize them? As written, P2's json.load would fail on a byte-for-byte copy.
- css_html_ui P3 still reads dashboard.json active_variables.master_palette, which no longer exists. What should replace it: the Content MD per the banner, or check_palette_parity?
- Where does css_html_ui write its output? The BUILD step names no directory, while the AUDIT step greps build/*.css and build/*.html (build/ does not exist), and its 'grep -v tokens.css' exclusion does not match the tokens/tokens.css extraction path.
- The css step 6 font audit passes both -E and -P to grep. Its behaviour on the Git Bash and WSL grep builds is not verified in the repo.
- ARTIFACT A font.policy says 'no third weight', but type_scale, ARTIFACT B, D10 and every surface's font load use three weights (400/500/800). Which is authoritative?
- ARTIFACT B declares --grid-* and --bp-* values that have no source key in ARTIFACT A, although B says it is generated from A. Should they be added to A?
- dashboard.json event_log has a 2026-07-01 COMP_STARTED entry from actor adobe_suite_uxp, the same date as meta.generated. Is it from a real run or seed data, and on which host?

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: The ```bash fence opened for the STUDIO_TMP resolver is at line 31
  - evidence: skills/adobe_suite_uxp.skill.md: line 30 is '```bash' and line 31 is the '# resolve once' comment. The next column-0 fence is line 45 '```bash', so the fence is unclosed until line 72.
- **added**: (missing) effect of the unclosed fence on verify_system.py
  - evidence: tools/verify_system.py check_host_portability.fenced() uses re.findall(r"^```[a-z]*\n(.*?)^```", S|M). In adobe_suite_uxp.skill.md this pairs fences 30→45, 72→121, 146→149, 174→177 and 200→203, so the P1–P5 code and the ARTIFACT A–D bodies are never scanned for osascript or /Applications/. Derived by reading the regex, not by running it.
- **corrected**: router.js routeSkill() for these skills 'resolves gates and logs INTERCEPT'
  - evidence: router.js lines 269-292: if any gate is not authored at L0 (isAuthoredL0 reads dashboard context_brand_gates), it logs PARKED and returns {ok:false, parked:true}. render_philosophy, motion_language and brand_voice are authored:false in dashboard.json, so all three skills log PARKED, not INTERCEPT.
- **corrected**: css_html_ui P3 as written would raise KeyError
  - evidence: skills/css_html_ui.skill.md lines 48-54 have no try/except, and it opens tokens/design_tokens.json first. That file is not on disk, so today the check raises FileNotFoundError. KeyError on active_variables.master_palette would come only after extraction (dashboard.json active_variables has no master_palette).
- **corrected**: ARTIFACT D 'does not accept a Premiere ProgID'
  - evidence: skills/adobe_suite_uxp.skill.md lines 205-231: ARTIFACT D does not validate $2. The usage comment lists only Photoshop/Illustrator/AfterFX ProgIDs, and step 4 prose says Premiere exposes no COM.
- **corrected**: css ARTIFACT A contrast_floor.rule and .why as paraphrased in the inventory
  - evidence: skills/css_html_ui.skill.md lines 96-108. Replaced with verbatim text (line breaks normalized), because the brief asks for ARTIFACT A to be captured precisely.
- **added**: (missing) Router Trigger B .mp4/.mov and Router §3 'also load if flagged' context for adobe and blender
  - evidence: Router.md line 125: '.mp4/.mov → higgsfield or adobe_suite'. Router.md §3 table: visual_identity is 'Also load if flagged in dashboard' for adobe_suite_uxp and blender_python.
- **added**: (missing) Router §10 names the token source
  - evidence: Router.md line 355: 'run compute-heavy work without a fresh PASS token from verify_compute.sh'. The token is actually minted by tools/hw/evaluate_gate.py, per BOOT.md §4 and D8.
- **added**: (missing) ARTIFACT B heading versus code
  - evidence: skills/adobe_suite_uxp.skill.md line 148 heading says 'curves preset + sRGB convert', but line 161 calls doc.activeLayer.adjustLevels (Levels, not Curves).
- **added**: (missing) adobe prerequisite and step-ordering gaps
  - evidence: skills/adobe_suite_uxp.skill.md: P2 checks only the Photoshop process, whatever app is targeted, and does not check installation. P3's 'NOT open unsaved elsewhere' is not checked. Step 2's grep runs before step 3 writes the file.
- **added**: (missing) prerequisites are advisory in shell terms
  - evidence: The §1 blocks of all three skill files only echo OK/FAIL/WARN/INIT; none uses exit or set -e, so the agent must enforce the results.
- **added**: (missing) blender does not implement continuous-mode re-probe or checkpoint
  - evidence: skills/blender_python.skill.md cites hardware_compute §2.8 only in prose (line 47). skills/hardware_compute.skill.md lines 125-129 define continuous mode, and no blender step or ARTIFACT A code re-probes or checkpoints.
- **added**: (missing) lowpoly_gen noise_scale is not in the schema, and there is a stale master_palette comment
  - evidence: skills/blender_python.skill.md line 225 reads P.get('noise_scale', 2.5), which ARTIFACT C lines 250-272 lack. Line 231 has the comment 'flat-color material from dashboard master_palette'.
- **added**: (missing) brush-designer carries values that are not in ARTIFACT A
  - evidence: tools/brush-designer/styles.css lines 9-21 define --bg-panel-hover #1F1F1F, --text-muted #6E6E6E, --bg-canvas #F5F0E8 and a color-mix() accent-dim. hub/styles.css lines 4-33 mirror ARTIFACT A without --grid-cols or --bp-*.
- **added**: (missing) CI runs the checks that read these skills
  - evidence: .github/workflows/verify.yml runs python3 tools/verify_system.py (including check_palette_parity and check_host_portability) on push to main, on pull_request and on workflow_dispatch.
- **added**: (missing) JetBrains Mono loading
  - evidence: control_room.html line 9, hub/index.html line 9 and tools/brush-designer/styles.css line 1 load JetBrains Mono weights 400;500;800 from fonts.googleapis.com. The skill itself does not specify loading.
- **added**: (missing) css audit exclusion path and shadow token
  - evidence: skills/css_html_ui.skill.md line 79 greps build/*.css build/*.html then 'grep -v tokens.css', but step 1 writes tokens/tokens.css. The line 33 law names 'shadow', and ARTIFACT A has no shadow key (elevation.model forbids shadow).
- **added**: (missing) router.js inline style literals
  - evidence: router.js lines 81 and 105-108 write style='width:..%' and style='background:<hex>' for master_palette swatches, and ARTIFACT C line 216 forbids literal colours without an exception.
- **added**: (missing) vault Content MD for css_html_ui
  - evidence: vault/studio-os/ui/ui-ux-intelligence-integration.md has frontmatter skills: [ui_ux_intelligence, css_html_ui] and Timeline entries on 2026-08-31 and 2026-09-01 tagged css_html_ui (token and retheme edits). Its Next Steps name brand_voice as the last gate blocking css_html_ui.
- **unverifiable**: ExtendScript result.toSource() output is the 'JSON result line' and DoJavaScriptFile returns the last expression
  - evidence: The skill asserts it (adobe step 5, ARTIFACT A comment 'last expression = captured result line'). Nothing in the repo demonstrates it, and D8 says the COM path was never run on the target machine.
- **unverifiable**: BLENDER_EEVEE_NEXT is valid on every Blender version P2 accepts (4.x and 5.x)
  - evidence: skills/blender_python.skill.md line 153 and ARTIFACT C use BLENDER_EEVEE_NEXT, and P2 accepts 'Blender (4|5)\.'. No file in the repo verifies the enum.
- **unverifiable**: All other inventory claims (headers, commands, thresholds, token values, dashboard phases, evaluate_gate --consume behaviour, bootstrap Test-Path COM probe, D6/D8/D9/D10 statements)
  - evidence: Not a change: each was re-read in source and matched (skills/*.skill.md, dashboard.json, Router.md, DECISIONS.md, BOOT.md, tools/hw/evaluate_gate.py, tools/bootstrap.sh, tools/verify_system.py, router.js, control_room.html). Listed here only because the schema has no 'confirmed' verdict.
