# ui-ux-pro-max, and how it became plugins/ui-design

Subsystem `ui-ux-pro-max-vs-plugin` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.86 · 48 entries · 25 corrections made to the first reading.

## Summary

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

## Tools

### CHQ search.py

`cli` · status `runs-today`

Paths: `tools/ui-ux-pro-max/scripts/search.py`

Vendored upstream CLI. It runs BM25 search over the corpus by domain or by stack, and runs the --design-system generator, optionally saving a Master file plus page overrides.

**Entry points**

- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" [--domain|-d style|color|chart|landing|product|ux|typography|icons|gsap|react|web|google-fonts] [--max-results|-n 1-20] [--json] [--full]`
  - does: Domain search; the domain is auto-detected when --domain is omitted. Text output cuts non-code fields at 300 characters unless --full is given.
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --stack|-s <react|nextjs|vue|svelte|astro|swiftui|react-native|flutter|nuxtjs|nuxt-ui|html-tailwind|shadcn|jetpack-compose|threejs|angular|laravel|javafx|wpf|winui|avalonia|uno|uwp> [-n 1-20] [--json] [--full]`
  - does: Stack guideline search.
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --design-system|-ds [-p|--project-name NAME] [-f|--format ascii|markdown] [--variance 1-10] [--motion 1-10] [--density 1-10] [--json]`
  - does: Generates a design system. With --json it prints {design_system, persistence}.
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist [-p NAME] [--output-dir|-o <project-root>] [--page NAME] [--force]`
  - does: Also writes the Master file and the page override.
  - changes: <output-dir or cwd>/design-system/<slug>/MASTER.md, and pages/<page>.md when --page is given (the pages/ dir is always created)

**Inputs**

- query string
- flags

**Outputs**

- Text headed '## UI Pro Max Search Results' or '## UI Pro Max Stack Guidelines', or JSON. With zero results: 'No matches...' plus a 'Closest known terms' line.
- An ASCII box or markdown design system.
- A persistence banner on stdout.

**Reads**

- tools/ui-ux-pro-max/data/*.csv
- tools/ui-ux-pro-max/data/stacks/*.csv

**Writes**

- only with --persist: design-system/<slug>/MASTER.md and design-system/<slug>/pages/<page>.md, under --output-dir or the cwd

**Depends on**

- Python 3 standard library
- core.py
- design_system.py

**Gates and checkpoints**

- --persist is skipped (status skipped_exists) when MASTER.md exists, unless --force is given.
- argparse rejects an unknown domain or stack, and -n outside 1-20 (exit 2).
- An empty result exits 0; the text tells the caller to retry and to label any fallback.

**Invoked by**

- CHQ ui_ux_intelligence skill
- CHQ brand gates + ARTIFACT D regeneration loop
- operator

**Invokes**

- core.search
- core.search_stack
- design_system.generate_design_system

**Notes**

It never passes diagnostics=True, although core.search and search_stack accept it. It has no contrast gate and no dtcg or shadcn format, and it does not import persist_design_system (generate_design_system calls it). The docstring lists 16 stacks; the registry has 22. The vault note (vault/studio-os/ui/ui-ux-intelligence-integration.md) records locked smoke tests run from this path on 2026-08-31. DECISIONS.md D9 says no product-work design system has been generated end to end.

### CHQ core.py

`library` · status `runs-today`

Paths: `tools/ui-ux-pro-max/scripts/core.py`

The BM25 engine and its registries: CSV_CONFIG (12 domains), STACK_CONFIG and AVAILABLE_STACKS (22), MAX_RESULTS=3, UNTRUNCATED_COLS, per-domain thresholds, synonyms, domain auto-detection, style identity and deprecation redirects, and suggestions.

**Entry points**

- `from core import search, search_stack, CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, UNTRUNCATED_COLS`
  - does: search(query, domain=None, max_results=3, diagnostics=False); search_stack(query, stack, max_results=3, diagnostics=False)
  - changes: nothing (in-process caches only)

**Inputs**

- query
- domain or stack
- max_results 1-20

**Outputs**

- A result dict: domain or stack, query, file, count, results, auto_detected, runner_up_domain, redirect, suggestions, and diagnostics when requested (includes calibration_version, abstained and reason).

**Reads**

- DATA_DIR = Path(__file__).parent.parent / 'data' (every CSV)

**Depends on**

- Python 3 standard library

**Gates and checkpoints**

- Per-domain score floors and coverage thresholds make the search abstain (reason low-confidence).
- Icon queries that mention 'lucide' abstain (reason unsupported-library).

**Invoked by**

- CHQ search.py
- CHQ design_system.py
- CHQ validate_data.py

**Notes**

_SEARCH_CALIBRATION_VERSION is 2026-08-12-v1. gsap output_cols: Category, Intensity Tier, Trigger, Duration, Easing, GSAP Snippet, Framework Notes, Do, Don't, Performance Notes. UNTRUNCATED_COLS does not include 'CSS Snippet'.

### CHQ design_system.py

`library` · status `runs-today`

Paths: `tools/ui-ux-pro-max/scripts/design_system.py`

DesignSystemGenerator. It combines the product, style, color, landing and typography searches, applies the ui-reasoning.csv decision rules and the dials, formats ASCII or markdown output, and saves MASTER.md plus page overrides.

**Entry points**

- `python3 tools/ui-ux-pro-max/scripts/design_system.py "<query>" [--project-name|-p NAME] [--format|-f ascii|markdown]`
  - does: Standalone generator CLI, with no persist, dial or json flags.
  - changes: nothing
- `generate_design_system(query, project_name=None, output_format='ascii', persist=False, page=None, output_dir=None, variance=None, motion=None, density=None, force=False)`
  - does: Returns {text, design_system, persistence}. output_format accepts only 'markdown' or ASCII (anything else).
  - changes: design-system/<slug>/ when persist=True
- `persist_design_system(design_system, page=None, output_dir=None, page_query=None, force=False)`
  - does: Writes MASTER.md and an optional page override. Returns status success or skipped_exists.
  - changes: <output_dir or cwd>/design-system/<slug>/MASTER.md, pages/<page>.md

**Inputs**

- query
- project name
- dials 1-10

**Outputs**

- design_system dict with these keys: project_name, category, pattern, style, colors, typography, key_effects, anti_patterns, decision_rules, activated_rules, constraints, reasoning_default, source_identities, source_derivations, severity, dials, motion_snippet, spacing_scale

**Reads**

- tools/ui-ux-pro-max/data/ui-reasoning.csv
- tools/ui-ux-pro-max/data/styles.csv
- tools/ui-ux-pro-max/data/landing.csv
- other CSVs via core.search

**Writes**

- design-system/<slug>/MASTER.md
- design-system/<slug>/pages/<page>.md

**Depends on**

- core.py
- reasoning_contract.py
- Python 3 standard library

**Gates and checkpoints**

- Atomic write: a temp file, then os.link (no overwrite) or os.replace (with force).
- safe_slug keeps only [a-z0-9_-], which prevents path traversal.

**Invoked by**

- CHQ search.py

**Invokes**

- core.search
- reasoning_contract.parse_decision_rules
- reasoning_contract.apply_decision_rules

**Notes**

It defines its own _relative_luminance (line 129) and _contrast_ratio (line 153). The payload has no 'contrast' key.

### CHQ reasoning_contract.py

`library` · status `runs-today`

Paths: `tools/ui-ux-pro-max/scripts/reasoning_contract.py`

A closed, non-executable grammar for the Decision_Rules column of ui-reasoning.csv. Condition keys (must_have and if_* signals) map to actions that use the constraint:, style:, pattern: and mode: prefixes.

**Entry points**

- `parse_decision_rules(raw); apply_decision_rules(rules, query)`
  - does: Validates the rule JSON; returns the activated conditions, style ids, constraints, pattern and mode.
  - changes: nothing

**Inputs**

- Decision_Rules JSON string
- query

**Outputs**

- rules dict
- application result dict

**Depends on**

- Python 3 standard library

**Gates and checkpoints**

- Raises ValueError on an unknown condition or action, or on a duplicate key or action.

**Invoked by**

- CHQ design_system.py
- CHQ validate_data.py

**Notes**

5,824 bytes, the same size as the Pipelines copy. Byte identity was not proven.

### CHQ validate_data.py

`cli` · status `vendored`

Paths: `tools/ui-ux-pro-max/scripts/validate_data.py`

A standard-library data-integrity guardrail. It checks every domain and stack CSV, ui-reasoning.csv, the catalog JSONs, the catalog-summary counts and snapshot sha256 values, and data-provenance.json.

**Entry points**

- `python3 tools/ui-ux-pro-max/scripts/validate_data.py`
  - does: Prints 'OK: validated N domain files, M stack files, and ui-reasoning.csv' and exits 0, or prints 'FAILED: n data integrity issue(s) found:' with a list and exits 1.
  - changes: nothing

**Outputs**

- stdout report
- exit 0 or 1

**Reads**

- tools/ui-ux-pro-max/data/** including catalog-summary.json, data-provenance.json, google-font-licenses.json and phosphor-icons-upstream.json
- the presence of tools/ui-ux-pro-max/data/.google-font-refresh.incomplete.json (a tripwire)

**Depends on**

- core.py
- reasoning_contract.py
- Python 3 standard library

**Gates and checkpoints**

- Fails when the catalog-summary counts or the snapshot sha256 values (raw-byte digest) are stale.
- Fails when the incomplete-refresh marker exists.

**Invoked by**

- no CHQ caller found (grep for validate_data matches only the file itself)

**Invokes**

- core registries
- reasoning_contract.parse_decision_rules

**Notes**

The docstring says it 'Exits 0 with no output on success', but the code prints an OK line. No CHQ document records running it. VENDOR.md points re-vendoring at tools/verify_system.py, and that file has no ui-ux-pro-max reference.

### CHQ vendored data corpus

`data` · status `vendored`

Paths: `tools/ui-ux-pro-max/data/`, `tools/ui-ux-pro-max/data/stacks/`, `tools/ui-ux-pro-max/data/catalog-summary.json`, `tools/ui-ux-pro-max/data/data-provenance.json`

The upstream corpus. 13 CSVs: styles, colors, charts, landing, products, ux-guidelines, typography, icons, motion, react-performance, app-interface, google-fonts, ui-reasoning. 4 JSONs: catalog-summary, data-provenance, google-font-licenses, phosphor-icons-upstream. 22 stack CSVs.

**Gates and checkpoints**

- .gitattributes 'tools/ui-ux-pro-max/** -text' keeps the files byte-identical with LF endings.

**Invoked by**

- CHQ core.py
- CHQ design_system.py
- CHQ validate_data.py
- CHQ hub Designer Pro tab (HTTP fetch of 9 CSVs)

**Notes**

catalog-summary.json (verifiedAt 2026-08-26) counts: styles 88 total, 79 searchable, 50 active, 29 supplemental, 9 deprecated; products 192; palettes 192; reasoningProfiles 192; fontPairings 74; googleFonts 1934; curatedIcons 105; upstreamPhosphorIcons 1512; uxGuidelines 119; motionPresets 17; chartTypes 25; stacks 22; stackGuidelines 1260. It also lists 8 pending font candidates and snapshot sha256 values for google-fonts.csv, google-font-licenses.json, icons.csv and phosphor-icons-upstream.json. data-provenance.json (generatedAt 2026-08-13) has 51 records. google-font-licenses source.revision is 038b637da7b3fd956a4ed93ffc607c3d5e4ce172. The motion.csv header has 12 columns.

### CHQ VENDOR.md vendoring protocol

`protocol` · status `partial`

Paths: `tools/ui-ux-pro-max/VENDOR.md`, `.gitattributes`

Records the upstream identity and the re-vendor procedure: upstream nextlevelbuilder/ui-ux-pro-max-skill, src/ui-ux-pro-max/{data,scripts}, v2.13.0, MIT, 44 files, 3.11 MB, and a payload sha256. The rule is no local edits.

**Entry points**

- `SRC=<path-to-upstream>/src/ui-ux-pro-max; rm -rf tools/ui-ux-pro-max/{data,scripts}; cp -r "$SRC/data" "$SRC/scripts" tools/ui-ux-pro-max/; rm -rf tools/ui-ux-pro-max/scripts/tests; find tools/ui-ux-pro-max -name __pycache__ -type d -exec rm -rf {} +`
  - does: Replaces the payload from an upstream checkout. The next step is to recompute the hash and re-run python3 tools/verify_system.py.
  - changes: tools/ui-ux-pro-max/data, tools/ui-ux-pro-max/scripts

**Inputs**

- upstream checkout

**Outputs**

- refreshed payload

**Reads**

- upstream src/ui-ux-pro-max

**Writes**

- tools/ui-ux-pro-max/**

**Depends on**

- bash

**Gates and checkpoints**

- Do not normalize line endings.
- Fix upstream and re-vendor rather than patching locally.

**Invoked by**

- operator

**Invokes**

- tools/verify_system.py (as instructed)

**Notes**

Excluded from the copy: scripts/tests, __pycache__ and *.pyc. The working tree now holds tools/ui-ux-pro-max/scripts/__pycache__/{core,design_system,reasoning_contract}.cpython-313.pyc; they are gitignored, but a directory hash would differ. No LICENSE file was vendored; only VENDOR.md states MIT. DECISIONS.md D9 says nothing verifies the sha256, and the proposed check_vendor_hash in verify_system.py does not exist. The vault note gives 3.3 MB; VENDOR.md gives 3.11 MB.

### CHQ ui_ux_intelligence skill

`skill` · status `partial`

Paths: `skills/ui_ux_intelligence.skill.md`

Skill 9 of 9 in CHQ's Four-Part Artifact Architecture. It wraps search.py for design-system generation and UX audits. It sets the anti-fabrication law and splits token authority: on studio surfaces it only proposes, and on product or client work it is the sole author.

**Entry points**

- `grep -q "ROUTER INTERCEPT" ./.task_scratch/attestation.txt || echo "FAIL:P1"`
  - does: P1: the Router attestation must exist before any tool call.
  - changes: nothing
- `python3 --version (fallback: python --version)`
  - does: P2: checks that Python 3 is present. The skill never installs it.
  - changes: nothing
- `python3 -c "import csv,sys; sys.exit(0 if sum(1 for _ in csv.DictReader(open('tools/ui-ux-pro-max/data/ux-guidelines.csv',encoding='utf-8')))==119 else 1)"`
  - does: P3: checks the payload is intact (119 UX rows).
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "keyboard focus modal" --domain ux -n 1 --json`
  - does: P4: the locked smoke test.
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<product_type> <industry> <keywords>" --design-system -p "Project Name" [--variance 1-10] [--motion 1-10] [--density 1-10]`
  - does: Step 3 GENERATE (product work only).
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --output-dir "<project-root>" [--page "dashboard"]`
  - does: Step 5 PERSIST (product work only).
  - changes: design-system/<slug>/ in the project
- `python3 tools/ui-ux-pro-max/scripts/search.py "contrast ratio text legibility" --domain ux; python3 tools/ui-ux-pro-max/scripts/search.py "<stack keyword>" --stack <stack>`
  - does: Step 7 AUDIT.
  - changes: nothing

**Inputs**

- task brief
- detected stack
- consumer class (studio surface or product work)

**Outputs**

- the resolved design system, written into the Content MD ## Method section
- the ARTIFACT B handoff JSON shape for css_html_ui
- a proposed diff (studio surfaces)

**Reads**

- ./.task_scratch/attestation.txt
- context/brand/visual_identity.context.md
- context/brand/typography_system.context.md
- context/brand/color_science.context.md
- an existing design-system/<slug>/MASTER.md
- project manifests for stack detection

**Writes**

- the vault Content MD
- dashboard.json pipeline.phases[*].progress_pct and one event_log entry
- design-system/<slug>/ (product work, via --persist)

**Depends on**

- Python 3 (the skill never installs it)
- CHQ search.py

**Gates and checkpoints**

- the Router intercept and attestation (P1)
- V1: classify studio or product before the first search
- V2: detect the stack; never assume it
- V3: read an existing MASTER.md first; --force needs explicit operator authorisation
- retry once on 0 results, then label the fallback
- studio surfaces: the ARTIFACT D four-step approval loop, and never persist
- two context flushes

**Invoked by**

- CHQ Router intercept (Router.md / router.js / dashboard.json)

**Invokes**

- CHQ search.py

**Notes**

Routing header:
- trigger_a: 12 phrases (design system, palette, colour scheme, font pairing, typography scale, style direction, UX review, accessibility audit, and others).
- trigger_b: design-system/*/MASTER.md, tokens/design_tokens.json, and 'pipeline phase skill=ui_ux_intelligence'.
- mandatory_context: visual_identity, typography_system, color_science.
- host_kinds: windows, wsl, linux. danger_class: LOW.

ARTIFACT B lists the JSON keys without 'contrast' and without 'reasoning_default'. The ARTIFACT A stack list names 21 stacks and omits jetpack-compose, although the header claims 22. The skill has no pipeline phase; ph_06 lists only css_html_ui. DECISIONS.md D9 says the product-work path and the ARTIFACT B handoff are unproven end to end.

### CHQ Router intercept (Router.md / router.js / dashboard.json)

`protocol` · status `partial`

Paths: `Router.md`, `router.js`, `dashboard.json`

The studio-wide dual-trigger intercept. It routes design-system, palette, font-pairing, UX-review and accessibility-audit intents, plus MASTER.md and design_tokens.json assets, to ui_ux_intelligence after resolving the skill's three mandatory brand gates.

**Entry points**

- `Router.md §2 intercept: 1 MODE -> 2 RESOLVE -> 3 LADDER -> 4 RECALL -> 5 VERIFY (attestation) -> 6 STATE -> 7 EXECUTE -> 8 WRITEBACK`
  - does: The mandatory sequence before any skill tool call.
  - changes: dashboard.json, vault Content MD
- `router.js routeSkill('skills/ui_ux_intelligence.skill.md') -> resolveGates() returns ['visual_identity','typography_system','color_science']`
  - does: Resolves the gates. The agent-runner dispatch and the writeback are TODO stubs that only log.
  - changes: nothing (logs locally)

**Inputs**

- user request
- referenced assets
- dashboard.json state

**Outputs**

- route decision
- attestation block

**Reads**

- dashboard.json registries.skills and brand-gate entries
- context/brand/*.context.md

**Writes**

- dashboard.json event_log (INTERCEPT_VIOLATION on a breach)

**Depends on**

- a browser (router.js)
- an agent following Router.md

**Gates and checkpoints**

- Any tool call before step 5 VERIFY is an intercept violation.
- A gate at L3 parks the task.

**Invoked by**

- every incoming task

**Invokes**

- CHQ ui_ux_intelligence skill

**Notes**

dashboard.json registers the skill as 'Design-system generation & UX audit', status ready. The event_log has a SKILL_REGISTERED entry (2026-08-31T14:05) and a TOKENS_COMMITTED entry (2026-08-31T16:45, the ARTIFACT D loop). Router.md is written as a binding contract addressed to an agent; it is described here, not followed.

### CHQ brand gates + ARTIFACT D regeneration loop

`context` · status `partial`

Paths: `context/brand/visual_identity.context.md`, `context/brand/typography_system.context.md`, `context/brand/color_science.context.md`, `DECISIONS.md`

Three L0 brand constants, transcribed from css_html_ui ARTIFACT A. They are ui_ux_intelligence's mandatory context, and ui_ux_intelligence is their declared regeneration path, but only through a four-step operator-approval loop: GENERATE with --json and no --persist, DIFF, IMPACT, PROPOSE, then stop.

**Entry points**

- `python3 tools/ui-ux-pro-max/scripts/search.py "JetBrains Mono" --domain google-fonts`
  - does: typography_system: verifies the licence against the vendored catalog.
  - changes: nothing
- `python3 tools/ui-ux-pro-max/scripts/search.py "contrast ratio text legibility" --domain ux`
  - does: color_science: verifies the colour pairings.
  - changes: nothing

**Inputs**

- generated design system (evidence only)

**Outputs**

- token changes the operator approves

**Reads**

- tools/ui-ux-pro-max/data/google-font-licenses.json
- skills/css_html_ui.skill.md ARTIFACT A

**Writes**

- nothing from a query result; the operator commits

**Depends on**

- tools/verify_system.py check_palette_parity

**Gates and checkpoints**

- mutation_policy: operator approval only; the agent proposes and never commits
- ARTIFACT A contrast_floor: 4.5:1 for text, 3.0:1 for status and non-text
- the studio's 13px/10px scale is not to be 'corrected' to the corpus 16px minimum

**Invoked by**

- CHQ ui_ux_intelligence skill
- CHQ Router intercept (Router.md / router.js / dashboard.json)

**Invokes**

- CHQ search.py

**Notes**

visual_identity §7 and color_science §5 declare their own gaps. The D9 addendum records an operator-authorised ARTIFACT D run. D10 says the direction came from the Designer Pro tab, with corpus rows named.

### CHQ hub Designer Pro tab

`web-app` · status `runs-today`

Paths: `hub/designer-pro.js`, `hub/index.html`, `hub/ollama.js`, `.claude/launch.json`

A style-mixing assistant with two layers. Grounding is deterministic: it fetches 9 corpus CSVs over HTTP, scores rows by token overlap and runs conflict checks from corpus fields. Synthesis uses local Ollama to blend the chosen rows into a proposal, which never becomes a token.

**Entry points**

- `python3 -m http.server 8347 (the .claude/launch.json entry 'hub-static-server'), then open http://localhost:8347/hub/ and choose the 'Designer Pro' tab`
  - does: Serves the hub. The tab fetches ../tools/ui-ux-pro-max/data/{styles,colors,typography,ux-guidelines,charts,landing,products,icons,motion}.csv.
  - changes: browser localStorage key 'hub:endpoint' (the Ollama endpoint setting)

**Inputs**

- query text
- chosen ingredient rows

**Outputs**

- conflict findings (deprecated, accessibility risk, mode clash, complexity stacking)
- an Ollama-generated blended direction
- CLI hint: python3 tools/ui-ux-pro-max/scripts/search.py "<q>" --domain <id>

**Reads**

- tools/ui-ux-pro-max/data/*.csv (9 files)
- dashboard.json hardware.local_llm.tiers.sm (model override)

**Depends on**

- static HTTP server
- Ollama at http://localhost:11434 by default (/api/tags, /api/generate)
- browser

**Gates and checkpoints**

- banner: retrieval is token overlap, and the CLI wins when the two disagree
- checks the model is served before generating
- conflict findings go into the prompt as facts

**Invoked by**

- operator

**Invokes**

- Ollama /api/generate via HubOllama

**Notes**

Covers 9 domains: no google-fonts, react or web, and no stacks. Its 'motion' domain maps to motion.csv. The vault note measured 137s for a 3-ingredient blend on llama3.1:8b, CPU only. The Pipelines plugin has nothing like it.

### Pipelines search.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/search.py`

The migrated search CLI. It keeps every CHQ flag and adds a diagnostics view, a WCAG 2.2 contrast gate and two token export formats.

**Entry points**

- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<query>" [--domain|-d <12 domains>] [--max-results|-n 1-20] [--json] [--full] [--diagnostics]`
  - does: Domain search. --diagnostics (new) adds a line with top_score, margin, token_coverage and reason; with --json the full core diagnostics dict is included.
  - changes: nothing
- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<query>" --stack|-s <22 stacks> [-n 1-20] [--json] [--full] [--diagnostics]`
  - does: Stack search.
  - changes: nothing
- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<query>" --design-system|-ds [-p NAME] [-f|--format ascii|markdown|dtcg|shadcn] [--variance 1-10] [--motion 1-10] [--density 1-10] [--strict-contrast] [--json]`
  - does: Design system. dtcg is W3C tokens JSON and shadcn is a :root oklch CSS block (both new). --strict-contrast (new) exits 1 and persists nothing when any text pair is below the WCAG 2.2 minimum. --diagnostics is ignored in this mode.
  - changes: nothing
- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<query>" --design-system --persist -p NAME --output-dir "<project-root>" [--page NAME] [--force] [--strict-contrast]`
  - does: Saves MASTER.md, tokens.json, theme.css and pages/<page>.md. With --strict-contrast it saves only after the gate passes.
  - changes: <output-dir>/design-system/<slug>/

**Inputs**

- query
- flags

**Outputs**

- Text or JSON as in CHQ, plus a Diagnostics line.
- In text mode, contrast advisories go to stderr.
- The persist banner goes to stderr for dtcg and shadcn, stdout otherwise.

**Reads**

- plugins/ui-design/catalog/data/**

**Writes**

- only with --persist: design-system/<slug>/{MASTER.md,tokens.json,theme.css,pages/<page>.md}

**Depends on**

- Python 3 standard library
- core.py
- design_system.py
- contrast.py

**Gates and checkpoints**

- spec.yaml exit codes: 0 ok (an empty result included), 1 contrast gate, 2 usage
- --strict-contrast: failing text pairs block persistence
- the skills require an explicit --output-dir that the user has confirmed

**Invoked by**

- Pipelines ui-design-catalog skill
- Pipelines ui-design-search-part agent
- Pipelines route.py (printed commands)
- Pipelines smoke.py
- Pipelines validate-contract.py

**Invokes**

- core.search
- core.search_stack
- design_system.generate_design_system
- design_system.persist_design_system
- contrast.failures
- contrast.advisories
- contrast.format_report

**Notes**

Flag by flag against CHQ:
- Unchanged: query, --domain/-d, --stack/-s, --max-results/-n, --json, --full, --design-system/-ds, --project-name/-p, --persist, --page, --output-dir/-o, --force, --variance, --motion, --density.
- Added, with no short forms: --diagnostics and --strict-contrast.
- Changed: --format/-f goes from {ascii,markdown} to {ascii,markdown,dtcg,shadcn}.

The docstring still lists 16 stacks and adds a --diagnostics usage line. The output headings still say 'UI Pro Max'.

### Pipelines core.py

`library` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/core.py`

The migrated BM25 engine and registries. spec.yaml declares the registries and validate-contract.py enforces them.

**Entry points**

- `from core import search, search_stack, CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, UNTRUNCATED_COLS, DATA_DIR`
  - does: Same API as CHQ.
  - changes: nothing

**Inputs**

- query
- domain or stack

**Outputs**

- result dicts, with diagnostics when requested

**Reads**

- plugins/ui-design/catalog/data/** (DATA_DIR = parent.parent/'data')

**Depends on**

- Python 3 standard library

**Gates and checkpoints**

- same thresholds and calibration version (2026-08-12-v1) as CHQ

**Invoked by**

- Pipelines search.py
- Pipelines route.py
- Pipelines design_system.py
- Pipelines validate_data.py
- Pipelines smoke.py
- Pipelines evaluate-relevance.py
- Pipelines validate-contract.py
- Pipelines generate-index.py

**Notes**

There are two differences from CHQ, which together explain the 41,299 vs 41,234 byte sizes (65 bytes):
- The gsap output_cols add 'Spring Params', 'CSS Snippet' and 'Reduced Motion'.
- UNTRUNCATED_COLS adds 'CSS Snippet'.

Function line numbers are identical. catalog/data and catalog/scripts must stay siblings.

### Pipelines design_system.py

`library` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/design_system.py`

The migrated generator. It now carries a WCAG 2.2 contrast report in the payload, emits the dtcg and shadcn formats, and saves three artifacts.

**Entry points**

- `python plugins/ui-design/catalog/scripts/design_system.py "<query>" [-p NAME] [-f ascii|markdown]`
  - does: The standalone CLI, unchanged from CHQ. It does not expose dtcg or shadcn.
  - changes: nothing
- `generate_design_system(..., output_format='ascii'|'markdown'|'dtcg'|'shadcn', ...); persist_design_system(design_system, page, output_dir, page_query, force)`
  - does: dtcg lazily imports tokens.dumps_dtcg; shadcn lazily imports shadcn_theme.to_shadcn_css.
  - changes: design-system/<slug>/ when saving

**Inputs**

- query
- dials

**Outputs**

- the design_system dict plus a 'contrast' list
- the persistence dict adds tokens_file and theme_file, and tokens_error or theme_error when a write fails

**Reads**

- plugins/ui-design/catalog/data/ui-reasoning.csv
- plugins/ui-design/catalog/data/styles.csv
- plugins/ui-design/catalog/data/landing.csv
- other CSVs via core.search

**Writes**

- design-system/<slug>/MASTER.md
- design-system/<slug>/tokens.json
- design-system/<slug>/theme.css
- design-system/<slug>/pages/<page>.md

**Depends on**

- core.py
- reasoning_contract.py
- contrast.py
- tokens.py (lazy)
- shadcn_theme.py (lazy)

**Gates and checkpoints**

- the no-overwrite atomic write also covers tokens.json and theme.css
- a failure writing tokens or theme is reported, not raised

**Invoked by**

- Pipelines search.py
- Pipelines tokens.py
- Pipelines evaluate-relevance.py

**Invokes**

- core.search
- reasoning_contract
- contrast.evaluate_palette
- tokens.dumps_dtcg
- shadcn_theme.to_shadcn_css

**Notes**

_relative_luminance and _contrast_ratio are now aliases of the contrast.py functions. resolved_colors is built once, so the payload and the gate see the same colours. format_ascii_box, format_markdown and format_master_md render only the GSAP-era motion fields (Category, Tier, Trigger, Duration, Easing, GSAP Snippet, Framework Notes, Do, Don't, Performance Notes). Spring Params, CSS Snippet and Reduced Motion reach output only through --json, -f dtcg (spring and reduced motion) and --domain gsap searches. The file is 72,490 bytes against CHQ's 70,937; no full diff was run.

### Pipelines reasoning_contract.py

`library` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/reasoning_contract.py`

The migrated Decision_Rules grammar.

**Entry points**

- `parse_decision_rules(raw); apply_decision_rules(rules, query)`
  - does: Same as CHQ.
  - changes: nothing

**Depends on**

- Python 3 standard library

**Invoked by**

- Pipelines design_system.py
- Pipelines validate_data.py

**Notes**

The same byte size as CHQ (5,824). It is part of the relevance runtime fingerprint.

### Pipelines validate_data.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/validate_data.py`

The migrated data-integrity validator. It is now verify gate 2 and the refresh preflight.

**Entry points**

- `python catalog/scripts/validate_data.py`
  - does: Exit 0 with an OK line, or exit 1 with the FAILED list.
  - changes: nothing

**Outputs**

- stdout report

**Reads**

- plugins/ui-design/catalog/data/**

**Depends on**

- core.py
- reasoning_contract.py

**Gates and checkpoints**

- the incomplete-refresh tripwire
- stale summary counts or snapshot hashes

**Invoked by**

- Pipelines verify.py
- Pipelines ui-design-catalog-refresh skill

**Invokes**

- core registries
- reasoning_contract.parse_decision_rules

**Notes**

The file is 52,060 bytes against CHQ's 52,064. The 4-byte difference is fully explained by line 4 of the docstring, which reads 'Data integrity guardrail for ui-design' instead of 'for ui-ux-pro-max'.

### Pipelines contrast.py

`library` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/contrast.py`

New. WCAG 2.2 contrast evaluation of a palette. Text pairs are enforced at 4.5:1; border and ring pairs are advisory at 3.0:1 (success criterion 1.4.11).

**Entry points**

- `evaluate_palette(colors); failures(report); advisories(report); format_report(report, indent=''); contrast_ratio(a, b); relative_luminance(hex)`
  - does: Builds the report over 9 CONTRAST_PAIRS (7 text, 2 advisory).
  - changes: nothing

**Inputs**

- design_system colors dict

**Outputs**

- a list of {pair, label, foreground, background, ratio, wcag22Minimum, nonText, advisory, passes}

**Depends on**

- Python 3 standard library

**Gates and checkpoints**

- --strict-contrast acts on failures()

**Invoked by**

- Pipelines search.py
- Pipelines design_system.py
- Pipelines tokens.py
- Pipelines shadcn_theme.py

**Notes**

The docstring cites an audit in which all 192 palettes pass the text pairs and 173 of 192 have a border below 3:1. It says validate_data.py keeps its own luminance helper deliberately.

### Pipelines oklch.py

`library` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/oklch.py`

New. Standard-library conversion from sRGB hex to OKLCH (Ottosson), plus the inverse, used for the oklch() values in the shadcn output.

**Entry points**

- `hex_to_rgb(hex); hex_to_oklch(hex); format_oklch(hex, precision=4); oklab_to_hex(L, a, b); oklch_to_hex(L, C, H)`
  - does: Colour conversion. The inverse returns (hex, clipped).
  - changes: nothing

**Inputs**

- hex, or Oklab/OKLCH values

**Outputs**

- tuples or CSS strings

**Depends on**

- Python 3 standard library (math)

**Invoked by**

- Pipelines shadcn_theme.py

**Notes**

A comment motivates the inverse with harvesting computed styles, but harvest-site-tokens.py does not import oklch (it canonicalises colours in the browser through a canvas). The inverse functions are exercised only by the tests.

### Pipelines tokens.py

`library` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/tokens.py`

New. DTCG exporter that turns a design_system dict into W3C Design Tokens JSON: color, font.family, space, radius, shadow and motion groups, plus $extensions['cc.uupm'].

**Entry points**

- `to_dtcg(design_system); dumps_dtcg(design_system, indent=2)`
  - does: Builds the token tree using string value encoding ('string-legacy'). Known GSAP eases map to cubicBezier; unmapped eases become a string token. Also emits: - motion.spring.default: a number token (stiffness) with the full spring model in $extensions['cc.uupm'].spring; - motion.reducedMotion.default: a plain $type string token; - motion.duration.default: the lower bound of the range; - the contrast report in the document-level $extensions['cc.uupm'].contrast.
  - changes: nothing

**Inputs**

- design_system dict

**Outputs**

- DTCG JSON string

**Depends on**

- contrast.py
- design_system.py (DIAL_TIERS, SEMANTIC_COLOR_ENTRIES)

**Gates and checkpoints**

- spec.yaml dtcg_extension_key 'cc.uupm' must equal tokens.EXTENSION_KEY (validate-contract checks this)

**Invoked by**

- Pipelines design_system.py (-f dtcg, and tokens.json on --persist)
- Pipelines validate-contract.py (imports EXTENSION_KEY)

**Invokes**

- contrast.evaluate_palette

**Notes**

The radius and shadow scales are fixed constants that mirror MASTER.md. CSS Snippet is not emitted. The description string still says 'generated by UI UX Pro Max'. SOURCE-RESEARCH.md says spring params and the reduced-motion fallback are both emitted under $extensions; the code puts reducedMotion in a regular string token.

### Pipelines shadcn_theme.py

`library` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/shadcn_theme.py`

New. Emits a shadcn/ui :root CSS block (Tailwind v4, compatible with tweakcn) in oklch() or hex, with contrast notes.

**Entry points**

- `to_shadcn_css(design_system, color_format='oklch'|'hex')`
  - does: Maps 19 variables (popover, popover-foreground and input are aliases) and sets --radius to 0.625rem. It deliberately omits chart-1..5 and sidebar-*.
  - changes: nothing

**Inputs**

- design_system dict

**Outputs**

- CSS text

**Depends on**

- contrast.py
- oklch.py

**Gates and checkpoints**

- raises ValueError on an unsupported color_format

**Invoked by**

- Pipelines design_system.py (-f shadcn, and theme.css on --persist)

**Invokes**

- oklch.format_oklch
- contrast.evaluate_palette
- contrast.failures
- contrast.advisories

### Pipelines route.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/route.py`

New. A brief router. It cross-checks the product domain three ways (the raw brief, a variant query using the catalog's own spellings, and stem-keyword overlap), fuses them with RRF and warns when they disagree. It then emits a design-system command and a manifest of supplemental parts, probing stack parts first.

**Entry points**

- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/route.py" "<brief>" [--stack|-s <22 stacks>] [--top 1-10 (default 5)] [--json]`
  - does: Prints the candidates, warnings (no-match, ambiguous, close-call, low-confidence), inline commands and the manifest. The JSON has brief, stack, variant_query, candidates, warnings, commands, manifest, not_covered and fan_out.
  - changes: nothing

**Inputs**

- a brief in the user's own words
- an optional stack

**Outputs**

- a report or JSON manifest; fan_out.recommended when there are 4 or more parts

**Reads**

- plugins/ui-design/catalog/data/products.csv
- stack CSVs via core.search_stack probes

**Depends on**

- core.py
- Python 3 standard library

**Gates and checkpoints**

- FAN_OUT_MIN_PARTS=4
- CLOSE_RATIO=0.85
- LOW_COVERAGE=0.5
- stack parts below 0.5 coverage go to not_covered and are never dispatched

**Invoked by**

- Pipelines ui-design-catalog skill
- Pipelines ui-design-multipart skill
- Pipelines ROUTER.md

**Invokes**

- core.search
- core.search_stack

**Notes**

CONCERNS covers forms, charts, motion, nav and icons, plus the a11y BASELINE, which is always present. STACK_QUERY_OVERRIDES covers (nextjs, a11y) and (astro, a11y), per CHANGELOG. Printed commands point at the script's own directory, for example python "<abs>/search.py" "<q>" --domain <d> -n 3 --json --diagnostics, and the design-system command python "<abs>/search.py" "<query>" --design-system -p "<chosen>".

### Pipelines merge_parts.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/merge_parts.py`

New. Merges and cross-checks the output of multipart agents. Search mode checks PART/QUERY/RETRIED/VERDICT/ROWS blocks against the manifest. Review mode checks AREA/FINDINGS/NOT-CHECKED blocks, and every rule-id must exist in references/quick-reference.md.

**Entry points**

- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/merge_parts.py" --mode search --manifest <route.json> --results <file...|-> [--json]`
  - does: Fails on a missing, duplicate, unknown or malformed part, or on a query change that was not declared.
  - changes: nothing
- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/merge_parts.py" --mode review --results <file...|-> [--areas a11y+touch,layout,type-color-style,motion] [--json]`
  - does: Validates findings of the form 'rule-id | severity | evidence | fix' and checks each rule-id against its area's sections.
  - changes: nothing

**Inputs**

- route.py JSON
- concatenated agent blocks (from a file or stdin)

**Outputs**

- a merged report ending 'RESULT: OK' or 'RESULT: FAIL', or JSON

**Reads**

- plugins/ui-design/references/quick-reference.md (Path(__file__).parents[2])

**Depends on**

- Python 3 standard library

**Gates and checkpoints**

- exit 0: every part came back exactly once and well formed
- exit 1: errors
- exit 2: argparse usage errors, including --mode search without --manifest and an unknown --areas value

**Invoked by**

- Pipelines ui-design-multipart skill

**Notes**

AREA_SECTIONS maps a11y+touch to sections 1 and 2, layout to 5, type-color-style to 4 and 6, and motion to 7.

### Pipelines catalog data

`data` · status `runs-today`

Paths: `plugins/ui-design/catalog/data/`, `plugins/ui-design/catalog/data/stacks/`, `plugins/ui-design/catalog/data/catalog-summary.json`, `plugins/ui-design/catalog/data/data-provenance.json`

The migrated corpus: the same 39 file names as CHQ (13 CSVs, 4 JSONs, 22 stack CSVs), edited locally.

**Gates and checkpoints**

- plugins/ui-design/.gitattributes '* text=auto eol=lf' (the relevance gate fingerprints raw bytes)
- the validate-csv, validate_data and generate-catalog-summary --check gates

**Invoked by**

- all Pipelines catalog scripts

**Notes**

Differences from CHQ:
- motion.csv adds Spring Params, CSS Snippet and Reduced Motion between Easing and GSAP Snippet (15 columns against 12).
- The astro row 'Default to zero JS' now mentions JavaScript and the browser.
- 15 accessibility rows were added: angular 8, nextjs 4, astro 3. Docs URL counts confirm this (astro has 5 hits, 2 of which already exist in CHQ).
- catalog-summary.json verifiedAt is 2026-09-20 and stackGuidelines is 1275 (CHQ 1260). All four snapshot sha256 values differ from CHQ.

Unchanged from CHQ:
- google-font-licenses source.revision (038b637d...).
- data-provenance.json keeps 51 records and the same generatedAt.
- All data files other than motion.csv and the angular, nextjs and astro stack files have the same byte sizes as CHQ.

### Pipelines staged stack-accessibility candidates

`data` · status `partial`

Paths: `plugins/ui-design/maintenance/candidates/stack-accessibility/REVIEW.md`, `plugins/ui-design/maintenance/candidates/stack-accessibility/angular.csv`, `plugins/ui-design/maintenance/candidates/stack-accessibility/nextjs.csv`, `plugins/ui-design/maintenance/candidates/stack-accessibility/astro.csv`

Candidate accessibility rows staged on 2026-09-20: nextjs 4 (No 61-64), astro 3 (No 54-56), angular 8 (No 51-58), laravel 0. REVIEW.md separates the text sourced from official docs from the authored text, and records probe results for the router's shared a11y stack query.

**Gates and checkpoints**

- REVIEW.md: promotion means appending the rows, then regenerating the relevance fingerprints and generate-index

**Invoked by**

- maintainer

**Notes**

REVIEW.md still says 'not promoted' and 'Nothing here is live', but the live stack CSVs contain these rows. Its finding that the nextjs and astro a11y parts land in not_covered was later addressed by route.py STACK_QUERY_OVERRIDES (CHANGELOG). The files sit under a path that the plugin .gitignore excludes ('candidates/'), so whether git tracks them is not shown.

### Pipelines spec.yaml contract

`protocol` · status `runs-today`

Paths: `plugins/ui-design/spec.yaml`

New. The declared contract. It declares:
- catalog_root 'catalog' and entry_point 'catalog/scripts/search.py';
- stdlib_only (root 'catalog', exception 'maintenance/');
- the 12 domains and 22 stacks;
- the dials (variance, motion, density) and the formats (ascii, markdown, dtcg, shadcn);
- default_max_results 3 and dtcg_extension_key 'cc.uupm';
- exit_codes: ok 0, contrast_gate 1, usage 2;
- persistence: dir_name design-system, output_dir_required true;
- counts_contract carriers: skills/ui-design-catalog/SKILL.md and README.md;
- agent_tool_exceptions: ui-design-search-part gets Bash;
- a list of 13 consumers.

**Depends on**

- pyyaml (only for its readers in maintenance/)

**Gates and checkpoints**

- spec.yaml wins over the skills and docs
- core.py cannot read it; validate-contract.py enforces agreement

**Invoked by**

- Pipelines validate-contract.py
- Pipelines smoke.py
- Pipelines skills and agents (read first)

**Notes**

CHQ has no equivalent. There the registries live only in core.py and are restated in the skill's prose.

### Pipelines validate-contract.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/maintenance/validate-contract.py`

New. Checks that spec.yaml agrees with the code, skills, agents, docs and packaging. It checks:
- frontmatter keys, and that each name matches its folder or file;
- agent tool bans (Write, Edit, Agent, Bash, NotebookEdit), with Bash allowed only through agent_tool_exceptions and only when the agent's body states its boundary;
- ${CLAUDE_PLUGIN_ROOT} portability in the skills, agents, ROUTER.md and references;
- the live count claims in the carriers;
- that documented search.py commands in the ui-design-catalog skill use real flags, domains and stacks, and that --persist always has --output-dir;
- that catalog/ imports only the standard library;
- the .gitignore and .gitattributes rules;
- release files, plus agreement between plugin.json, marketplace.json and CHANGELOG;
- 3 locked examples and 2 exit codes.

**Entry points**

- `python maintenance/validate-contract.py`
  - does: Exit 0 when the contract holds, 1 with failures listed on stderr, 2 on an environment problem (no pyyaml, unreadable spec, or Python older than 3.10).
  - changes: nothing

**Outputs**

- a pass summary or a failure list

**Reads**

- plugins/ui-design/spec.yaml
- plugins/ui-design/skills/ui-design-*/SKILL.md
- plugins/ui-design/agents/ui-design-*.md
- plugins/ui-design/ROUTER.md
- plugins/ui-design/references/*.md
- plugins/ui-design/README.md
- plugins/ui-design/.gitignore
- plugins/ui-design/.gitattributes
- plugins/ui-design/.claude-plugin/plugin.json
- plugins/ui-design/.claude-plugin/marketplace.json
- plugins/ui-design/CHANGELOG.md
- LICENSE and NOTICE (existence only)
- plugins/ui-design/catalog/scripts/search.py argparse calls (via AST)
- plugins/ui-design/catalog/**/*.py (import scan)
- plugins/ui-design/catalog/data

**Depends on**

- pyyaml
- Python >= 3.10

**Environment and secret names (names only)**

- PYTHONIOENCODING, PYTHONDONTWRITEBYTECODE (set for its subprocesses)

**Gates and checkpoints**

- verify gate 3
- plugin.json name must be 'ui-design' and version MAJOR.MINOR.PATCH
- the marketplace must list exactly 'ui-design' with source './'
- the newest CHANGELOG heading must equal the plugin.json version
- GUIDE_REQUIREMENTS phrases must appear in the ui-design-catalog SKILL.md
- the house command is 'python', not 'python3'

**Invoked by**

- Pipelines verify.py

**Invokes**

- Pipelines search.py subprocesses:
  - "beauty spa wellness service" --design-system --json (must resolve Beauty/Spa/Wellness Service);
  - "keyboard focus modal" --domain ux --json;
  - "virtualized list" --stack react-native --json;
  - "zzzqqq nonexistent" --domain ux --json (must exit 0);
  - "x" --domain nosuchdomain (must exit 2).
- imports core and tokens

### Pipelines validate-csv.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/maintenance/validate-csv.py`

New in the plugin. A structural CSV check for blank or duplicate headers, field-count mismatches and blank rows.

**Entry points**

- `python maintenance/validate-csv.py`
  - does: Exit 0 on pass, 1 on errors (listed on stderr), 2 when the data directory is missing.
  - changes: nothing

**Outputs**

- a report on stdout or stderr

**Reads**

- plugins/ui-design/catalog/data/**/*.csv

**Depends on**

- Python 3 standard library

**Gates and checkpoints**

- verify gate 1

**Invoked by**

- Pipelines verify.py

**Notes**

A comment mentions the removed upstream files design.csv and draft.csv, which suggests origin in upstream repo-level tooling.

### Pipelines generate-catalog-summary.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/maintenance/generate-catalog-summary.py`

New in the plugin. Generates or checks catalog-summary.json (counts, raw-byte sha256 snapshots of 4 files, the promotion policy and pending candidates from excludedFamilies) and the bold count tokens in README.md.

**Entry points**

- `python maintenance/generate-catalog-summary.py --verified-at YYYY-MM-DD`
  - does: Writes catalog/data/catalog-summary.json.
  - changes: plugins/ui-design/catalog/data/catalog-summary.json
- `python maintenance/generate-catalog-summary.py --check`
  - does: Checks that the summary is current (using its stored verifiedAt when none is given) and that README.md carries the count tokens. Exits 2 when stale or on any error.
  - changes: nothing

**Inputs**

- --verified-at date

**Outputs**

- catalog-summary.json

**Reads**

- plugins/ui-design/catalog/data/*.csv
- plugins/ui-design/catalog/data/stacks/*.csv
- plugins/ui-design/catalog/data/google-font-licenses.json
- plugins/ui-design/catalog/data/phosphor-icons-upstream.json
- plugins/ui-design/README.md

**Writes**

- plugins/ui-design/catalog/data/catalog-summary.json

**Depends on**

- Python 3 standard library

**Gates and checkpoints**

- verify gate 4
- rejects dates in the future, or in 1970 or earlier

**Invoked by**

- Pipelines verify.py
- Pipelines ui-design-catalog-refresh skill (after approval)

**Notes**

CHQ ships a catalog-summary.json but has no generator script.

### Pipelines generate-index.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/maintenance/generate-index.py`

New. Generates the plugin INDEX.md: catalog vocabulary (products and keywords, style ids, font pairings, landing pattern ids, stacks), plus the data files and references. When the plugin sits inside the monorepo as plugins/<name>/ with CLAUDE.md at the root, it also generates the Pipelines root INDEX.md (tools, skills and agents, taken from frontmatter).

**Entry points**

- `python maintenance/generate-index.py`
  - does: Writes the index or indexes.
  - changes: plugins/ui-design/INDEX.md and, in the monorepo, INDEX.md at the Pipelines root
- `python maintenance/generate-index.py --check`
  - does: Checks without writing. Exits 2 when stale or missing, or when a skill or agent is absent from the root index.
  - changes: nothing

**Outputs**

- INDEX.md files

**Reads**

- plugins/ui-design/catalog/data/*.csv and *.json
- plugins/ui-design/catalog/data/stacks/*.csv
- plugins/ui-design/references/*.md
- core.CSV_CONFIG and AVAILABLE_STACKS
- monorepo only: .claude/skills/*/SKILL.md, .claude/agents/*.md, plugins/*/skills/*/SKILL.md, plugins/*/agents/*.md, and the top-level folder names

**Writes**

- plugins/ui-design/INDEX.md
- INDEX.md (Pipelines root, monorepo only)

**Depends on**

- Python 3 standard library
- pyyaml (only for the root index in the monorepo)

**Gates and checkpoints**

- verify gate 5
- every data file needs a DATA_PURPOSE entry, every reference a REFERENCE_PURPOSE entry, and every top-level folder a TOOL_PURPOSE entry

**Invoked by**

- Pipelines verify.py
- maintainer

**Invokes**

- core (import)

**Notes**

TOOL_PURPOSE knows two top-level folders: creative-writing and plugins.

### Pipelines generated INDEX.md files

`data` · status `generated`

Paths: `plugins/ui-design/INDEX.md`, `INDEX.md`

Generated vocabulary indexes, with a 'do not edit by hand' header. The plugin index lists data files with row counts (stack guidelines 1275), products, searchable styles, font pairings, landing patterns, other vocabularies, stacks and references. The Pipelines root index lists the tools, skills and agents.

**Gates and checkpoints**

- generate-index.py --check (verify gate 5)

**Invoked by**

- Pipelines ui-design-catalog skill
- Pipelines ui-design-search-part agent (retry words)
- Pipelines ROUTER.md
- Pipelines route.py (warning text)

**Notes**

CHQ has no equivalent.

### Pipelines evaluate-relevance.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/maintenance/evaluate-relevance.py`, `plugins/ui-design/maintenance/relevance_metrics.py`, `plugins/ui-design/catalog/scripts/tests/fixtures/relevance-cases.json`, `plugins/ui-design/catalog/scripts/tests/fixtures/relevance-thresholds.json`, `plugins/ui-design/catalog/scripts/tests/fixtures/relevance-baseline.json`

New in the plugin. A deterministic relevance gate over judged cases. It reports routingAccuracy, precisionAt1, precisionAt3, mrrAt3, ndcgAt3, negativeAbstention, typoRecoveryAt3 and designSystemCoherence. Two fingerprints bind the run: the runtime fingerprint covers core.py, design_system.py, reasoning_contract.py and every *.csv under catalog/data; the oracle fingerprint covers evaluate-relevance.py, relevance_metrics.py and relevance-cases.json.

**Entry points**

- `python maintenance/evaluate-relevance.py [--cases PATH] [--thresholds PATH] [--baseline PATH] [--split all|calibration|held_out] [--write-baseline PATH] [--no-thresholds]`
  - does: Prints the metrics, samples and splits as JSON. Fails through SystemExit (exit 1) on an invalid fixture, a fingerprint mismatch with the thresholds manifest, or a threshold breach, listing the problem cases.
  - changes: only the --write-baseline file

**Inputs**

- fixture JSONs

**Outputs**

- JSON metrics
- a non-zero exit with the problem cases

**Reads**

- plugins/ui-design/catalog/scripts/{core,design_system,reasoning_contract}.py
- plugins/ui-design/catalog/data/**/*.csv
- the fixture JSONs

**Writes**

- the baseline file, when --write-baseline is given

**Depends on**

- Python 3 standard library
- core.py
- design_system.py
- relevance_metrics.py

**Gates and checkpoints**

- verify gate 8
- any change to data or runtime invalidates relevance-thresholds.json runtimeFingerprint, a deliberate stop

**Invoked by**

- Pipelines verify.py
- Pipelines ui-design-catalog-refresh skill

**Invokes**

- core.search
- core.search_stack
- design_system.DesignSystemGenerator

**Notes**

No flag writes relevance-thresholds.json. After a data change its runtimeFingerprint and oracleFingerprint must be updated separately, which the refresh skill instructs; --write-baseline rewrites only the baseline. The thresholds file has status 'provisional-baseline-regression-gate', baselineRevision 97eb2a2, and an approvingMaintainer note. CHANGELOG records regenerating the fingerprint and baseline after the astro wording change.

### Pipelines smoke.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/maintenance/smoke.py`

New. Every registered domain or stack must answer a focused probe through the real search.py, and the registry size must equal spec.yaml.

**Entry points**

- `python maintenance/smoke.py domains [query]`
  - does: Probes the 12 domains.
  - changes: nothing
- `python maintenance/smoke.py stacks [query]`
  - does: Probes the 22 stacks.
  - changes: nothing

**Inputs**

- an optional override query

**Outputs**

- PASS and FAIL lines
- exit 0 all answered, 1 some returned none, 2 environment problem

**Reads**

- plugins/ui-design/spec.yaml
- core registries

**Depends on**

- pyyaml

**Environment and secret names (names only)**

- PYTHONIOENCODING, PYTHONDONTWRITEBYTECODE (set for its subprocesses)

**Gates and checkpoints**

- verify gates 9 and 10
- exit 2 on a registry/spec size mismatch, a missing search.py, or an unreadable spec or missing pyyaml

**Invoked by**

- Pipelines verify.py

**Invokes**

- search.py "<probe>" --domain|--stack <name> -n 1 --json

### Pipelines verify.py

`ci` · status `runs-today`

Paths: `plugins/ui-design/maintenance/verify.py`, `plugins/ui-design/maintenance/requirements.txt`

New. The single health command. It runs 10 gates in order from the plugin root, stops at the first failure and prints the exact command to re-run that gate.

**Entry points**

- `pip install -r maintenance/requirements.txt && python maintenance/verify.py`
  - does: Runs these gates in order: validate-csv; validate_data; validate-contract; generate-catalog-summary --check; generate-index --check; unittest discover -s catalog/scripts/tests -p "test_*.py"; unittest discover -s maintenance/tests -p "test_*.py"; evaluate-relevance; smoke domains; smoke stacks.
  - changes: nothing

**Outputs**

- '[n/10] <gate> ok' lines, or FAILED plus the re-run command on stderr
- exit 0 or 1

**Reads**

- the whole plugin

**Depends on**

- Python 3.10+ (for validate-contract)
- pyyaml (requirements.txt)

**Environment and secret names (names only)**

- PYTHONIOENCODING, PYTHONDONTWRITEBYTECODE (set for the gate subprocesses)

**Gates and checkpoints**

- Pipelines CLAUDE.md: the monorepo has no CI, so this is the gate

**Invoked by**

- maintainer
- Pipelines verify.yml workflow
- Pipelines ui-design-catalog-refresh skill

**Invokes**

- Pipelines validate-csv.py
- Pipelines validate_data.py
- Pipelines validate-contract.py
- Pipelines generate-catalog-summary.py
- Pipelines generate-index.py
- Pipelines test suites
- Pipelines evaluate-relevance.py
- Pipelines smoke.py

**Notes**

The docstring says it replaces the source project's 'npm run verify:data'. The requirements.txt comment names only validate-contract.py and smoke.py as needing pyyaml.

### Pipelines test suites

`ci` · status `runs-today`

Paths: `plugins/ui-design/catalog/scripts/tests/`, `plugins/ui-design/catalog/scripts/tests/fixtures/`, `plugins/ui-design/maintenance/tests/`

Unit tests.
- Engine: test_core, test_core_data_quality, test_data_contracts, test_style_taxonomy, test_text_layout_resilience, test_native_desktop_stack_freshness, test_web_stack_freshness, test_search_cli, test_route, test_merge_parts, test_tokens, test_contrast, test_shadcn_theme, test_design_system_mode, test_relevance_evaluator, test_catalog_refresh. Fixtures are the relevance JSONs and catalogs/*.
- Maintainer tools: test_generate_index, test_harvest_site_tokens (includes TestNotShipped), test_validate_contract_agents, test_validate_contract_portability.

**Entry points**

- `python -m unittest discover -s catalog/scripts/tests -p "test_*.py"`
  - does: Engine tests (verify gate 6).
  - changes: nothing claimed
- `python -m unittest discover -s maintenance/tests -p "test_*.py"`
  - does: Maintainer tests (verify gate 7).
  - changes: nothing claimed

**Inputs**

- fixtures under catalog/scripts/tests/fixtures

**Outputs**

- unittest results

**Depends on**

- Python 3 standard library unittest

**Invoked by**

- Pipelines verify.py

**Notes**

The test bodies were not read, apart from TestNotShipped. CHQ excluded upstream scripts/tests when vendoring.

### Pipelines refresh-google-fonts.py

`cli` · status `partial`

Paths: `plugins/ui-design/maintenance/refresh-google-fonts.py`, `plugins/ui-design/maintenance/.env.example`

New in the plugin. Rebuilds google-fonts.csv and google-font-licenses.json from the Google Fonts Developer API (or offline snapshots) plus google/fonts METADATA.pb, and prints a JSON change report.

**Entry points**

- `python maintenance/refresh-google-fonts.py (--live | --api-input PATH | --catalog-input PATH) (--metadata-root DIR | --metadata-input PATH) --metadata-revision <40-char sha|fixture-*> --existing-csv PATH --output-csv PATH --license-output PATH --verified-at YYYY-MM-DD [--overrides PATH] [--expected-count N] [--approve-changes]`
  - does: Validates and normalises, and prints the change report (addedFamilies, removedFamilies, metadataChangedFamilies, excludedFamilies). Refuses changes to the family set without --approve-changes. Exits 2 on any error.
  - changes: --output-csv and --license-output, written atomically with .google-font-refresh.lock and .google-font-refresh.incomplete.json in the output directory

**Inputs**

- API JSON or a live fetch
- a METADATA.pb tree

**Outputs**

- CSV
- licence JSON
- change report on stdout

**Reads**

- https://www.googleapis.com/webfonts/v1/webfonts (only with --live)
- the metadata root or metadata input
- --existing-csv

**Writes**

- the --output-csv and --license-output paths

**Depends on**

- Python 3 standard library (urllib)
- network for --live

**Environment and secret names (names only)**

- GOOGLE_FONTS_API_KEY (read from the process environment; .env.example documents it and is not loaded automatically)

**Gates and checkpoints**

- --live requires the key
- an existing incomplete marker or lock file aborts the run
- --approve-changes is needed for added or removed families

**Invoked by**

- Pipelines ui-design-catalog-refresh skill

**Notes**

The marker is created before publishing and removed if the run completes or nothing was published, so it survives only a partial publish. Offline fixture tests exist (test_catalog_refresh). The files do not show a live refresh ever being run.

### Pipelines refresh-icon-catalog.py

`cli` · status `partial`

Paths: `plugins/ui-design/maintenance/refresh-icon-catalog.py`

New in the plugin. Normalises the pinned Phosphor catalog (@phosphor-icons/core 2.1.1, react 2.1.10) into phosphor-icons-upstream.json and validates the curated icons.csv against it.

**Entry points**

- `python maintenance/refresh-icon-catalog.py --input PATH --package-json PATH --react-package-json PATH --react-exports-input PATH --curated-csv PATH --output PATH --verified-at YYYY-MM-DD [--expected-count N (default 1512)]`
  - does: Writes the manifest and prints a change report. Exits 2 on any error, including a version other than PACKAGE_VERSION or REACT_VERSION.
  - changes: the --output file (atomic os.replace)

**Inputs**

- JSON dumps derived from npm

**Outputs**

- a candidate phosphor-icons-upstream.json

**Reads**

- the --curated-csv path (normally plugins/ui-design/catalog/data/icons.csv)
- the input JSONs

**Writes**

- --output

**Depends on**

- Python 3 standard library
- node and npm upstream of it (driven by the skill)

**Gates and checkpoints**

- bumping PACKAGE_VERSION or REACT_VERSION is the maintainer's call

**Invoked by**

- Pipelines ui-design-catalog-refresh skill

**Notes**

The files do not show a live refresh ever being run.

### Pipelines harvest-site-tokens.py

`cli` · status `runs-today`

Paths: `plugins/ui-design/maintenance/harvest-site-tokens.py`

New. Maintainer-only tooling. It prints a browser extractor script that reads computed styles and canonicalises colours through a 1x1 canvas, then normalises the saved captures into a review report. It never writes the CSVs.

**Entry points**

- `python maintenance/harvest-site-tokens.py show-extractor`
  - does: Prints EXTRACTOR_JS.
  - changes: nothing (stdout; its own docs redirect it to extract.js)
- `python maintenance/harvest-site-tokens.py report <captures/*.json>`
  - does: Normalises captures into a proposal report and rejects shells (MIN_ELEMENTS 150, MIN_DISTINCT_BACKGROUNDS 3).
  - changes: nothing

**Inputs**

- capture JSON from a real browser

**Outputs**

- a review report on stdout

**Reads**

- capture files

**Depends on**

- Python 3 standard library (argparse, json, sys, collections, pathlib)
- a browser for the capture

**Gates and checkpoints**

- TestNotShipped asserts it is absent from catalog/scripts
- promotion to a CSV is an editorial and licensing decision

**Invoked by**

- maintainer

**Notes**

It does not import oklch.py. SOURCE-RESEARCH.md describes the failure modes found while building it. No run record for real captures was found.

### Pipelines ui-design-catalog skill

`skill` · status `runs-today`

Paths: `plugins/ui-design/skills/ui-design-catalog/SKILL.md`

The user-facing catalog skill. It covers the search modes, the query contract, design-system generation, persist, the dials, domains and stacks, zero-result handling, output formats and the contrast gate. Every path starts from ${CLAUDE_PLUGIN_ROOT}.

**Entry points**

- `/ui-design:ui-design-catalog (or selected automatically from its description)`
  - does: Drives search.py and route.py.
  - changes: nothing unless --persist is confirmed
- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<query>" --design-system --persist -p "Project Name" --output-dir "<project-root>"`
  - does: Persists after the user confirms.
  - changes: <project-root>/design-system/<slug>/

**Inputs**

- user UI task

**Outputs**

- recommendations sourced from the catalog

**Reads**

- plugins/ui-design/spec.yaml (read first; wins on conflict)
- plugins/ui-design/ROUTER.md
- plugins/ui-design/INDEX.md
- plugins/ui-design/references/quick-reference.md
- plugins/ui-design/references/pro-rules.md

**Writes**

- design-system/<slug>/, only through a confirmed --persist

**Depends on**

- Python 3 as python, python3 or py -3 (never installed)

**Environment and secret names (names only)**

- CLAUDE_PLUGIN_ROOT

**Gates and checkpoints**

- confirm the output directory with the user before --persist
- --force only with explicit user authorisation
- retry once, then label the fallback
- if ${CLAUDE_PLUGIN_ROOT} is unexpanded, do not run the command

**Invoked by**

- a Claude Code user or assistant

**Invokes**

- Pipelines search.py
- Pipelines route.py

**Notes**

This is the role counterpart of CHQ's ui_ux_intelligence, not a migration of that file. NOTICE lists the plugin's skills as additions. CHQ-specific content is absent: the Router attestation (P1), the studio-vs-product classification and token-authority split, ARTIFACT D, the context flushes and dashboard.json writeback, and the brand-gate mandatory context. The SKILL.md says each --motion preset carries a GSAP snippet, spring params, a CSS snippet and a reduced-motion fallback; only --json output (and partly dtcg) shows them. No run record appears in the files.

### Pipelines ui-design-multipart skill

`skill` · status `runs-today`

Paths: `plugins/ui-design/skills/ui-design-multipart/SKILL.md`

New. Orchestrates two workflows: (A) a search fan-out for wide briefs and (B) a four-area page review. A script splits the work, one agent handles each part, and merge_parts.py merges the results.

**Entry points**

- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/route.py" "<brief>" --stack <stack> --json`
  - does: Step A1: route, with the output saved to the scratchpad.
  - changes: a scratchpad file
- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/merge_parts.py" --mode search --manifest <route.json> --results <parts.txt>`
  - does: Step A7: merge.
  - changes: nothing
- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/merge_parts.py" --mode review --results <reviews.txt>`
  - does: Step B3: merge.
  - changes: nothing

**Inputs**

- a brief, or the path of a built page

**Outputs**

- a merged, checked report

**Reads**

- plugins/ui-design/ROUTER.md
- plugins/ui-design/INDEX.md
- plugins/ui-design/spec.yaml

**Writes**

- scratchpad files only

**Depends on**

- Agent tool

**Environment and secret names (names only)**

- CLAUDE_PLUGIN_ROOT

**Gates and checkpoints**

- fan out only when fan_out.recommended is true (4 or more parts)
- never dispatch not_covered parts
- re-dispatch failed parts once
- never persists

**Invoked by**

- Pipelines ui-design-catalog skill (for a wide brief or a page review)

**Invokes**

- Pipelines route.py
- Pipelines ui-design-search-part agent
- Pipelines ui-design-page-reviewer agent
- Pipelines merge_parts.py
- Pipelines search.py (the design-system command, run inline)

**Notes**

It borrows the split/one-agent-per-part/merge pattern from the Pipelines 'chunk-tag-backfill' skill. No run record appears in the files.

### Pipelines ui-design-catalog-refresh skill

`skill` · status `partial`

Paths: `plugins/ui-design/skills/ui-design-catalog-refresh/SKILL.md`

New. A human-run replacement for the upstream weekly refresh workflow: fetch upstream, generate candidates under maintenance/candidates/, diff them against live data, have an agent review them, report, then stop for the maintainer.

**Entry points**

- `/ui-design:ui-design-catalog-refresh [--fonts-only|--icons-only] [--dry-run]`
  - does: Preflight: the plugins/cache check, spec.yaml, validate_data, whether the key is set, and git, node and npm versions. Then fetch, generate, diff, review and report.
  - changes: maintenance/candidates/{raw,reports}/ and candidate files; after explicit approval, catalog/data/, catalog-summary.json, README count tokens and the relevance fixtures

**Inputs**

- args

**Outputs**

- per-file deltas
- BLOCK and FLAG rows
- [UNVERIFIED] items

**Reads**

- plugins/ui-design/spec.yaml
- plugins/ui-design/catalog/data/**
- the PACKAGE_VERSION and REACT_VERSION constants in refresh-icon-catalog.py

**Writes**

- plugins/ui-design/maintenance/candidates/** (gitignored)
- after approval: the live catalog/data file, catalog-summary.json, README.md count tokens, relevance-thresholds.json fingerprints and relevance-baseline.json

**Depends on**

- git
- node
- npm
- network
- Agent tool

**Environment and secret names (names only)**

- GOOGLE_FONTS_API_KEY
- CLAUDE_PLUGIN_ROOT

**Gates and checkpoints**

- refuses to run when the plugin path contains plugins/cache
- never writes catalog/data during a refresh
- never prints the key
- never deletes lock or marker files
- promotes only on the maintainer's explicit approval in chat
- verify.py must pass after promotion

**Invoked by**

- maintainer

**Invokes**

- Pipelines validate_data.py
- git clone --depth 1 --filter=blob:none --no-checkout, then sparse-checkout
- npm init --yes; npm install --ignore-scripts --no-audit --no-fund
- node --input-type=module
- Pipelines refresh-google-fonts.py
- Pipelines refresh-icon-catalog.py
- git diff --no-index
- Pipelines ui-design-catalog-reviewer agent
- Pipelines generate-catalog-summary.py
- Pipelines evaluate-relevance.py
- Pipelines verify.py

**Notes**

The files record no fonts or icons refresh run. The staged stack-accessibility candidates are a different, manual staging.

### Pipelines ui-design-search-part agent

`agent` · status `runs-today`

Paths: `plugins/ui-design/agents/ui-design-search-part.md`

New. Runs exactly one manifest search part and returns a PART/QUERY/RETRIED/VERDICT/ROWS block.

**Entry points**

- `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<query>" --domain|--stack <target> -n <n> --json --diagnostics`
  - does: Its one allowed command, with one retry allowed.
  - changes: nothing

**Inputs**

- part_id, kind, target, query, n

**Outputs**

- a fixed block with verdict match, low-confidence or empty

**Reads**

- plugins/ui-design/INDEX.md (retry words)

**Depends on**

- tools: Read, Grep, Glob, Bash

**Environment and secret names (names only)**

- CLAUDE_PLUGIN_ROOT

**Gates and checkpoints**

- never passes --persist, --output-dir, --design-system, --page or --force
- no redirects and no file writes
- Bash is granted only through spec.yaml agent_tool_exceptions

**Invoked by**

- Pipelines ui-design-multipart skill

**Invokes**

- Pipelines search.py

**Notes**

No run record appears in the files.

### Pipelines ui-design-page-reviewer agent

`agent` · status `runs-today`

Paths: `plugins/ui-design/agents/ui-design-page-reviewer.md`

New. A read-only review of one area of one built page (a11y+touch, layout, type-color-style or motion) against the quick-reference rule-ids.

**Entry points**

- `dispatched as agent type ui-design:ui-design-page-reviewer with the page path and AREA`
  - does: Returns AREA/FINDINGS/NOT-CHECKED.
  - changes: nothing

**Inputs**

- page path
- area

**Outputs**

- findings of the form 'rule-id | severity | line n: "quote" | fix'

**Reads**

- plugins/ui-design/references/quick-reference.md
- the page source

**Depends on**

- tools: Read, Grep, Glob

**Environment and secret names (names only)**

- CLAUDE_PLUGIN_ROOT

**Gates and checkpoints**

- never invents a rule-id; merge_parts rejects unknown ids

**Invoked by**

- Pipelines ui-design-multipart skill

**Notes**

No run record appears in the files.

### Pipelines ui-design-catalog-reviewer agent

`agent` · status `partial`

Paths: `plugins/ui-design/agents/ui-design-catalog-reviewer.md`

New. A read-only review of one refresh candidate (google-fonts.csv, google-font-licenses.json or phosphor-icons-upstream.json) against the live data.

**Entry points**

- `dispatched as ui-design:ui-design-catalog-reviewer with the candidate, diff and change-report paths`
  - does: Returns FILE/DELTA/OVERALL/ROW/[UNVERIFIED]/NOTES.
  - changes: nothing

**Inputs**

- candidate path
- diff path
- report path

**Outputs**

- a structured verdict: OK, FLAG or BLOCK

**Reads**

- plugins/ui-design/maintenance/candidates/*
- plugins/ui-design/catalog/data/* (including typography.csv and icons.csv cross-checks)

**Depends on**

- tools: Read, Grep, Glob

**Environment and secret names (names only)**

- CLAUDE_PLUGIN_ROOT

**Gates and checkpoints**

- cannot check licences upstream, so marks them [UNVERIFIED]

**Invoked by**

- Pipelines ui-design-catalog-refresh skill

**Notes**

No refresh run is recorded, so it has never been exercised on record.

### Pipelines ROUTER.md

`doc` · status `runs-today`

Paths: `plugins/ui-design/ROUTER.md`

New. A query-routing guide for the catalog: choosing the mode, the domain table, using the catalog's own words, what to do when a match looks wrong (route.py and the --diagnostics fields), the fan-out threshold and guardrails.

**Reads**

- plugins/ui-design/INDEX.md
- plugins/ui-design/spec.yaml

**Gates and checkpoints**

- --persist only with a confirmed --output-dir after approval
- fan-out agents never persist

**Invoked by**

- Pipelines ui-design-catalog skill
- Pipelines ui-design-multipart skill

**Invokes**

- Pipelines route.py

**Notes**

Not the equivalent of CHQ's Router.md. CHQ's is a studio-wide skill intercept; this is catalog query routing.

### Pipelines references

`doc` · status `runs-today`

Paths: `plugins/ui-design/references/quick-reference.md`, `plugins/ui-design/references/pro-rules.md`

New in the plugin. Prose rule sets. quick-reference.md has 10 numbered sections of rule-ids (Accessibility through Charts & Data), used by the page reviewers and merge_parts. pro-rules.md holds the native/mobile app rules and the canonical pre-delivery checklist.

**Gates and checkpoints**

- the skill falls back to these when Python is missing, and must say so
- validate-contract checks them for portability

**Invoked by**

- Pipelines ui-design-catalog skill
- Pipelines ui-design-page-reviewer agent
- Pipelines merge_parts.py

**Notes**

CHQ has no references/ directory.

### Pipelines plugin packaging

`launcher` · status `partial`

Paths: `plugins/ui-design/.claude-plugin/plugin.json`, `plugins/ui-design/.claude-plugin/marketplace.json`, `plugins/ui-design/.gitignore`, `plugins/ui-design/.gitattributes`, `CLAUDE.md`

New. The Claude Code plugin manifest (name ui-design, version 0.1.0, MIT, author groot99-droid, homepage and repository github.com/groot99-droid/ui-design-plugin) and a one-plugin marketplace (ui-design-plugin, source './'). It carries its own ignore and LF-pinning rules so it can be published on its own.

**Entry points**

- `/plugin marketplace add groot99-droid/ui-design-plugin ; /plugin install ui-design@ui-design-plugin`
  - does: Installs from the published repository (README).
  - changes: the Claude Code plugin cache
- `claude plugin marketplace add groot99-droid/ui-design-plugin ; claude plugin install ui-design@ui-design-plugin`
  - does: Shell form of the install (README).
  - changes: the Claude Code plugin cache
- `claude --plugin-dir ./plugins/ui-design (or claude plugin marketplace add ./plugins/ui-design, then claude plugin install ui-design@ui-design-plugin)`
  - does: Loads a local copy (Pipelines CLAUDE.md).
  - changes: nothing, or the plugin cache for the marketplace form
- `claude plugin validate ./plugins/ui-design`
  - does: Validates the manifest and marketplace. Not part of verify.py.
  - changes: nothing
- `git subtree split --prefix=plugins/ui-design -b release/ui-design-plugin`
  - does: The publishing step in Pipelines CLAUDE.md. Pushing and tagging are the author's call.
  - changes: a git branch

**Depends on**

- Claude Code CLI
- git

**Environment and secret names (names only)**

- CLAUDE_PLUGIN_ROOT (substituted in skill and agent bodies only)

**Gates and checkpoints**

- .gitignore entries: .env, .env.*, !.env.example, *.key, *.pem, __pycache__/, *.py[cod], .venv/, venv/, design-system/, candidates/, captures/
- .gitattributes: * text=auto eol=lf
- validate-contract checks: name 'ui-design', a semver version, the marketplace lists only 'ui-design' with source './', and the CHANGELOG heading matches the version

**Invoked by**

- user
- maintainer

**Notes**

CHANGELOG marks 0.1.0 as 'Unreleased'. It is the only plugin under Pipelines/plugins.

### Pipelines licence and attribution files

`doc` · status `runs-today`

Paths: `plugins/ui-design/LICENSE`, `plugins/ui-design/NOTICE`, `plugins/ui-design/CHANGELOG.md`, `plugins/ui-design/SOURCE-RESEARCH.md`, `plugins/ui-design/README.md`

New. These take over VENDOR.md's provenance role.
- LICENSE: MIT, with two copyright lines (Next Level Builder 2024 and groot99-droid 2026).
- NOTICE: the upstream sources (ui-ux-pro-max-skill, Phosphor core 2.1.1 and react 2.1.10, Google Fonts metadata, public design and accessibility docs, the DTCG spec, GSAP) and what was left behind (the installer, marketplace manifest, gallery and demo project).
- CHANGELOG: the 0.1.0 additions and changes.
- SOURCE-RESEARCH: the extension roadmap and its status.
- README: install, what the plugin writes, the contract and maintenance.

**Gates and checkpoints**

- validate-contract requires LICENSE, NOTICE, README.md and CHANGELOG.md to exist
- README.md is a counts_contract carrier
- generate-catalog-summary --check requires the README count tokens

**Invoked by**

- Pipelines validate-contract.py
- Pipelines generate-catalog-summary.py

**Notes**

SOURCE-RESEARCH.md cites scripts/add-motion-columns.py, which is in neither tree. It also uses stale paths: scripts/tokens.py, scripts/contrast.py, scripts/shadcn_theme.py, scripts/oklch.py (now under catalog/scripts/) and .claude/skills/ui-design-catalog/SKILL.md. It dates its baseline to catalog-summary 'as it stood on 2026-08-13', while the CHQ copy's verifiedAt is 2026-08-26. Done items: the DTCG exporter, the contrast gate, the shadcn exporter and the motion columns. Open items: tonal ramps and a platform rule layer.

### Pipelines verify.yml workflow

`ci` · status `never-exercised`

Paths: `plugins/ui-design/.github/workflows/verify.yml`

New. A GitHub Actions matrix (ubuntu, windows and macos, Python 3.10 and 3.13) that installs the maintenance requirements and runs maintenance/verify.py.

**Entry points**

- `on push to main or pull_request: python -m pip install -r maintenance/requirements.txt; python maintenance/verify.py`
  - does: Runs every gate.
  - changes: nothing

**Depends on**

- GitHub Actions (actions/checkout@v4, actions/setup-python@v5)

**Gates and checkpoints**

- permissions: contents: read

**Invoked by**

- GitHub (only once the plugin is published as its own repository)

**Invokes**

- Pipelines verify.py

**Notes**

Its own comment says it has no effect inside the Pipelines monorepo.

## Usage flows

### Shape of the CHQ -> Pipelines move (the precedent)

1. Source: CHQ tools/ui-ux-pro-max/{data,scripts}. It is a byte-identical LF copy of upstream v2.13.0 (44 files), with a sha256 in VENDOR.md that nothing verifies, a no-local-edits rule, and .gitattributes '-text'.
2. Relocate the payload to plugins/ui-design/catalog/{data,scripts} and keep the two folders as siblings, because core.py resolves DATA_DIR relative to itself. All 39 data files and all 5 scripts keep their names; nothing is dropped. The files do not show whether the copy came from CHQ or directly from upstream; NOTICE names upstream.
3. Extend the engine in place, which ends the no-local-edits rule: - add contrast.py, oklch.py, tokens.py and shadcn_theme.py; - change design_system.py (contrast key, dtcg and shadcn formats, tokens.json and theme.css on persist); - change search.py (--diagnostics, --strict-contrast, -f dtcg|shadcn); - change core.py (3 gsap output_cols, plus 'CSS Snippet' in UNTRUNCATED_COLS); - change the validate_data.py docstring name only.
4. Add orchestration scripts: route.py (brief router and manifest) and merge_parts.py (multipart checker).
5. Edit the data: - motion.csv gains 3 columns; - 15 stack accessibility rows are added, staged first under maintenance/candidates/stack-accessibility/; - the astro row is reworded; - catalog-summary.json is regenerated (2026-09-20, stackGuidelines 1275); - the relevance fingerprint and baseline are regenerated.
6. Declare a contract (spec.yaml) and add maintenance/, the only place for pyyaml, the network and GOOGLE_FONTS_API_KEY. It holds the validators, the summary and index generators, the relevance gate, smoke tests, refresh tools, the harvester, and the verify.py umbrella with requirements.txt and .env.example.
7. Replace the single CHQ skill with new plugin skills (ui-design-catalog, ui-design-multipart, ui-design-catalog-refresh), three agents (only ui-design-search-part holds Bash), ROUTER.md, references/ and the generated INDEX.md files. All paths use ${CLAUDE_PLUGIN_ROOT}, and persisting requires an --output-dir the user has confirmed.
8. Package the plugin: .claude-plugin/plugin.json and marketplace.json, a plugin-local .gitignore and .gitattributes, LICENSE with two copyright lines, NOTICE, CHANGELOG, README and .github/workflows/verify.yml. Publish through git subtree split (Pipelines CLAUDE.md).
9. Replace VENDOR.md's single unverified hash with hashes the gates enforce: the catalog-summary snapshot sha256 values and the relevance runtime and oracle fingerprints.
10. Leave behind the CHQ-only wiring: the Router intercept and attestation, the dashboard.json writeback, the brand-gate token-authority split and ARTIFACT D, and the Designer Pro tab.

### CHQ product-work design system (ui_ux_intelligence)

1. The Router intercept fires on a Trigger A phrase or a Trigger B asset (design-system/*/MASTER.md, tokens/design_tokens.json).
2. The Router runs MODE, RESOLVE (visual_identity, typography_system, color_science) and LADDER (L0), then RECALL, then VERIFY, which writes the attestation to .task_scratch/attestation.txt.
3. Run the prerequisites P1-P4: the attestation grep, the Python check, the 119-row payload check, and search.py "keyboard focus modal" --domain ux -n 1 --json.
4. Classify the work as product work (V1), detect the stack (V2), and read any existing MASTER.md (V3).
5. Run python3 tools/ui-ux-pro-max/scripts/search.py "<product> <industry> <keywords>" --design-system -p NAME [dials].
6. Context flush 1: record the resolved system in the Content MD ## Method.
7. Run python3 tools/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p NAME --output-dir <project-root> [--page P]. Use --force only with operator authorisation.
8. Audit with search.py "contrast ratio text legibility" --domain ux and search.py "<kw>" --stack <stack>.
9. Context flush 2: update Decisions in Force and Next Steps, then write one dashboard.json phase update and one event_log entry. DECISIONS.md D9 says this path has not been run end to end.

### CHQ studio-surface regeneration (ARTIFACT D)

1. GENERATE: run search.py --design-system against the studio brief with --json and no --persist.
2. DIFF: compare against context/brand/*.context.md and css_html_ui ARTIFACT A.
3. IMPACT: name every control_room.html value that would move, and confirm whether check_palette_parity would still pass.
4. PROPOSE to the operator and stop. Writing the gates, the css_html_ui skill or control_room.html without approval is an intercept violation. The D9 addendum records one operator-authorised run (TOKENS_COMMITTED on 2026-08-31).

### CHQ Designer Pro blend

1. Serve the repo over HTTP with python3 -m http.server 8347 (the .claude/launch.json entry hub-static-server), then open http://localhost:8347/hub/ and choose the Designer Pro tab.
2. The tab fetches 9 CSVs from ../tools/ui-ux-pro-max/data/ and ranks rows by token overlap.
3. Pick ingredient rows across domains. The deterministic conflict checks run from corpus fields.
4. Blend with local Ollama (default http://localhost:11434; the model tier can be overridden from dashboard.json hardware.local_llm). The conflict findings go into the prompt as facts.
5. The output is a proposal only and writes no tokens. The CLI's BM25 result wins when the two disagree.

### Pipelines single search or design system (ui-design-catalog)

1. Read ${CLAUDE_PLUGIN_ROOT}/spec.yaml first.
2. For a brief in free wording, run python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/route.py" "<brief>" [--stack s] and read the ambiguous, close-call and low-confidence warnings.
3. Run python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py" "<chosen product + terms>" --design-system -p NAME [-f ascii|markdown|dtcg|shadcn] [--variance/--motion/--density] [--strict-contrast].
4. Add supplements: search.py "<q>" --domain <d> [--diagnostics] and search.py "<q>" --stack <s>.
5. To persist: confirm <output-dir>/design-system/<slug>/ with the user, then run search.py ... --design-system --persist -p NAME --output-dir "<project-root>". This writes MASTER.md, tokens.json, theme.css and pages/. Use --force only with explicit authorisation.

### Pipelines multipart search fan-out

1. Run route.py "<brief>" [--stack s] --json and save the output to the scratchpad.
2. Address the warnings and name the chosen product row.
3. Run the design-system command from 'commands' inline. It is never fanned out and has no --persist.
4. Report the not_covered parts; never dispatch them.
5. If fan_out.recommended is true (4 or more parts), dispatch one ui-design:ui-design-search-part agent per manifest part in a single message. Otherwise run the parts inline with the printed commands.
6. Run merge_parts.py --mode search --manifest <route.json> --results <parts.txt>. On exit 1, re-dispatch the failed parts once.
7. Report the verdicts and rows, then stop for the user.

### Pipelines page review

1. Confirm the page is readable source.
2. Dispatch 4 ui-design:ui-design-page-reviewer agents, one each for a11y+touch, layout, type-color-style and motion.
3. Run merge_parts.py --mode review --results <reviews.txt>. Unknown rule-ids fail.
4. Report the findings by severity plus the NOT-CHECKED notes, and change nothing.

### Pipelines catalog refresh (maintainer)

1. Preflight: - refuse to run if the plugin path contains plugins/cache; - check that spec.yaml exists; - run validate_data.py; - check that GOOGLE_FONTS_API_KEY is set, without printing it; - check git, node and npm. With --dry-run, stop here.
2. Fetch: - sparse-clone the google/fonts METADATA.pb files into maintenance/candidates/raw/google-fonts and record rev-parse HEAD; - npm install the pinned @phosphor-icons packages (plus react@19) into raw/npm and dump the JSON with node.
3. Generate candidates: run refresh-google-fonts.py --live ... --approve-changes and refresh-icon-catalog.py ..., saving the change reports under candidates/reports/.
4. Diff each candidate against catalog/data with git diff --no-index.
5. Review: dispatch ui-design:ui-design-catalog-reviewer once per changed file.
6. Report and stop. Only on the maintainer's explicit approval: - copy the candidate over the live file; - run generate-catalog-summary.py --verified-at <date> and update the README count tokens; - run evaluate-relevance.py --no-thresholds and compare with the baseline; - if no metric moved, update the runtimeFingerprint and oracleFingerprint fields in relevance-thresholds.json by hand and rewrite the baseline with --write-baseline; - require verify.py to pass.

### Pipelines stack-accessibility row addition (as recorded)

1. Stage candidate rows for nextjs (4), astro (3) and angular (8) under maintenance/candidates/stack-accessibility/, with REVIEW.md (2026-09-20).
2. The rows appear in the live catalog/data/stacks CSVs, and catalog-summary.json is regenerated on 2026-09-20 with stackGuidelines 1275.
3. route.py gains STACK_QUERY_OVERRIDES for (nextjs, a11y) and (astro, a11y), so those parts are dispatched instead of landing in not_covered (CHANGELOG).
4. The astro 'Default to zero JS' row is reworded, and the relevance fingerprint and baseline are regenerated (CHANGELOG).
5. REVIEW.md was not updated and still says 'not promoted'.

### Pipelines verify gate

1. pip install -r maintenance/requirements.txt (pyyaml).
2. python maintenance/verify.py runs, in order: validate-csv, validate_data, validate-contract, generate-catalog-summary --check, generate-index --check, the engine unittests, the maintainer unittests, evaluate-relevance, smoke domains and smoke stacks.
3. It stops at the first failure and prints the single re-run command. verify.yml runs the same command on a 3-OS by 2-Python matrix once the plugin is published on its own.

## Relationships

| From | Relation | To |
|---|---|---|
| CHQ search.py | migrated-to | Pipelines search.py |
| CHQ core.py | migrated-to | Pipelines core.py |
| CHQ design_system.py | migrated-to | Pipelines design_system.py |
| CHQ reasoning_contract.py | migrated-to | Pipelines reasoning_contract.py |
| CHQ validate_data.py | migrated-to | Pipelines validate_data.py |
| CHQ vendored data corpus | migrated-to | Pipelines catalog data |
| CHQ ui_ux_intelligence skill | counterpart-in-target (not a file migration) | Pipelines ui-design-catalog skill |
| CHQ VENDOR.md vendoring protocol | replaced-by | Pipelines licence and attribution files |
| CHQ VENDOR.md vendoring protocol | integrity-role-replaced-by (gate-enforced fingerprints) | Pipelines evaluate-relevance.py |
| CHQ VENDOR.md vendoring protocol | integrity-role-replaced-by (snapshot sha256 checked by a gate) | Pipelines generate-catalog-summary.py |
| CHQ VENDOR.md vendoring protocol | absent-in-target (no whole-payload hash, local edits allowed) | Pipelines catalog data |
| CHQ Router intercept (Router.md / router.js / dashboard.json) | absent-in-target | Pipelines plugin packaging |
| CHQ brand gates + ARTIFACT D regeneration loop | absent-in-target | Pipelines ui-design-catalog skill |
| CHQ hub Designer Pro tab | absent-in-target | Pipelines plugin packaging |
| CHQ Router intercept (Router.md / router.js / dashboard.json) | name-collision-not-equivalent | Pipelines ROUTER.md |
| CHQ vendored data corpus | added-in-target | Pipelines contrast.py |
| CHQ vendored data corpus | added-in-target | Pipelines oklch.py |
| CHQ vendored data corpus | added-in-target | Pipelines tokens.py |
| CHQ vendored data corpus | added-in-target | Pipelines shadcn_theme.py |
| CHQ vendored data corpus | added-in-target | Pipelines route.py |
| CHQ vendored data corpus | added-in-target | Pipelines merge_parts.py |
| CHQ vendored data corpus | added-in-target | Pipelines staged stack-accessibility candidates |
| CHQ vendored data corpus | added-in-target | Pipelines spec.yaml contract |
| CHQ vendored data corpus | added-in-target | Pipelines validate-contract.py |
| CHQ vendored data corpus | added-in-target | Pipelines validate-csv.py |
| CHQ vendored data corpus | added-in-target | Pipelines generate-catalog-summary.py |
| CHQ vendored data corpus | added-in-target | Pipelines generate-index.py |
| CHQ vendored data corpus | added-in-target | Pipelines generated INDEX.md files |
| CHQ vendored data corpus | added-in-target | Pipelines evaluate-relevance.py |
| CHQ vendored data corpus | added-in-target | Pipelines smoke.py |
| CHQ vendored data corpus | added-in-target | Pipelines verify.py |
| CHQ vendored data corpus | added-in-target | Pipelines test suites |
| CHQ vendored data corpus | added-in-target | Pipelines refresh-google-fonts.py |
| CHQ vendored data corpus | added-in-target | Pipelines refresh-icon-catalog.py |
| CHQ vendored data corpus | added-in-target | Pipelines harvest-site-tokens.py |
| CHQ ui_ux_intelligence skill | added-in-target | Pipelines ui-design-multipart skill |
| CHQ ui_ux_intelligence skill | added-in-target | Pipelines ui-design-catalog-refresh skill |
| CHQ ui_ux_intelligence skill | added-in-target | Pipelines ui-design-search-part agent |
| CHQ ui_ux_intelligence skill | added-in-target | Pipelines ui-design-page-reviewer agent |
| CHQ ui_ux_intelligence skill | added-in-target | Pipelines ui-design-catalog-reviewer agent |
| CHQ ui_ux_intelligence skill | added-in-target | Pipelines ROUTER.md |
| CHQ ui_ux_intelligence skill | added-in-target | Pipelines references |
| CHQ VENDOR.md vendoring protocol | added-in-target | Pipelines plugin packaging |
| CHQ VENDOR.md vendoring protocol | added-in-target | Pipelines verify.yml workflow |
| CHQ Router intercept (Router.md / router.js / dashboard.json) | routes-to | CHQ ui_ux_intelligence skill |
| CHQ ui_ux_intelligence skill | invokes | CHQ search.py |
| CHQ ui_ux_intelligence skill | requires-context / proposes-regeneration | CHQ brand gates + ARTIFACT D regeneration loop |
| CHQ brand gates + ARTIFACT D regeneration loop | invokes | CHQ search.py |
| CHQ hub Designer Pro tab | reads | CHQ vendored data corpus |
| CHQ hub Designer Pro tab | defers-to | CHQ search.py |
| CHQ search.py | imports | CHQ core.py |
| CHQ search.py | imports | CHQ design_system.py |
| CHQ design_system.py | imports | CHQ core.py |
| CHQ design_system.py | imports | CHQ reasoning_contract.py |
| CHQ core.py | reads | CHQ vendored data corpus |
| CHQ validate_data.py | validates | CHQ vendored data corpus |
| CHQ validate_data.py | imports | CHQ core.py |
| Pipelines search.py | imports | Pipelines contrast.py |
| Pipelines search.py | imports | Pipelines design_system.py |
| Pipelines search.py | imports | Pipelines core.py |
| Pipelines design_system.py | imports | Pipelines core.py |
| Pipelines design_system.py | imports | Pipelines contrast.py |
| Pipelines design_system.py | lazy-imports | Pipelines tokens.py |
| Pipelines design_system.py | lazy-imports | Pipelines shadcn_theme.py |
| Pipelines design_system.py | imports | Pipelines reasoning_contract.py |
| Pipelines tokens.py | imports | Pipelines contrast.py |
| Pipelines tokens.py | imports (DIAL_TIERS, SEMANTIC_COLOR_ENTRIES) | Pipelines design_system.py |
| Pipelines shadcn_theme.py | imports | Pipelines oklch.py |
| Pipelines shadcn_theme.py | imports | Pipelines contrast.py |
| Pipelines core.py | reads | Pipelines catalog data |
| Pipelines route.py | imports | Pipelines core.py |
| Pipelines route.py | emits-commands-for | Pipelines search.py |
| Pipelines merge_parts.py | reads | Pipelines references |
| Pipelines merge_parts.py | consumes-manifest-of | Pipelines route.py |
| Pipelines ui-design-catalog skill | invokes | Pipelines search.py |
| Pipelines ui-design-catalog skill | invokes | Pipelines route.py |
| Pipelines ui-design-catalog skill | reads | Pipelines spec.yaml contract |
| Pipelines ui-design-catalog skill | reads | Pipelines ROUTER.md |
| Pipelines ui-design-catalog skill | reads | Pipelines generated INDEX.md files |
| Pipelines ui-design-catalog skill | reads | Pipelines references |
| Pipelines ui-design-catalog skill | hands-off-to | Pipelines ui-design-multipart skill |
| Pipelines ui-design-multipart skill | invokes | Pipelines route.py |
| Pipelines ui-design-multipart skill | dispatches | Pipelines ui-design-search-part agent |
| Pipelines ui-design-multipart skill | dispatches | Pipelines ui-design-page-reviewer agent |
| Pipelines ui-design-multipart skill | invokes | Pipelines merge_parts.py |
| Pipelines ui-design-search-part agent | invokes | Pipelines search.py |
| Pipelines ui-design-search-part agent | reads | Pipelines generated INDEX.md files |
| Pipelines ui-design-page-reviewer agent | reads | Pipelines references |
| Pipelines ui-design-catalog-refresh skill | invokes | Pipelines refresh-google-fonts.py |
| Pipelines ui-design-catalog-refresh skill | invokes | Pipelines refresh-icon-catalog.py |
| Pipelines ui-design-catalog-refresh skill | dispatches | Pipelines ui-design-catalog-reviewer agent |
| Pipelines ui-design-catalog-refresh skill | invokes | Pipelines validate_data.py |
| Pipelines ui-design-catalog-refresh skill | invokes | Pipelines generate-catalog-summary.py |
| Pipelines ui-design-catalog-refresh skill | invokes | Pipelines evaluate-relevance.py |
| Pipelines ui-design-catalog-refresh skill | invokes | Pipelines verify.py |
| Pipelines verify.py | invokes | Pipelines validate-csv.py |
| Pipelines verify.py | invokes | Pipelines validate_data.py |
| Pipelines verify.py | invokes | Pipelines validate-contract.py |
| Pipelines verify.py | invokes | Pipelines generate-catalog-summary.py |
| Pipelines verify.py | invokes | Pipelines generate-index.py |
| Pipelines verify.py | invokes | Pipelines test suites |
| Pipelines verify.py | invokes | Pipelines evaluate-relevance.py |
| Pipelines verify.py | invokes | Pipelines smoke.py |
| Pipelines verify.yml workflow | invokes | Pipelines verify.py |
| Pipelines validate-contract.py | enforces | Pipelines spec.yaml contract |
| Pipelines validate-contract.py | invokes | Pipelines search.py |
| Pipelines validate-contract.py | imports | Pipelines tokens.py |
| Pipelines validate-contract.py | validates | Pipelines plugin packaging |
| Pipelines validate-contract.py | validates | Pipelines licence and attribution files |
| Pipelines smoke.py | invokes | Pipelines search.py |
| Pipelines smoke.py | reads | Pipelines spec.yaml contract |
| Pipelines evaluate-relevance.py | fingerprints | Pipelines catalog data |
| Pipelines evaluate-relevance.py | imports | Pipelines design_system.py |
| Pipelines evaluate-relevance.py | imports | Pipelines core.py |
| Pipelines generate-index.py | reads | Pipelines catalog data |
| Pipelines generate-index.py | generates | Pipelines generated INDEX.md files |
| Pipelines generate-catalog-summary.py | writes catalog-summary.json | Pipelines catalog data |
| Pipelines validate_data.py | validates | Pipelines catalog data |
| Pipelines validate-csv.py | validates | Pipelines catalog data |
| Pipelines staged stack-accessibility candidates | promoted-into (15 rows live; REVIEW.md not updated) | Pipelines catalog data |

**Open questions the files could not settle**

- catalog-summary.json snapshot sha256 values differ between CHQ and Pipelines for all four files, but a directory listing shows those files at identical byte sizes on both sides, and both repos digest raw bytes. No hash was computed, so it is unknown which side's summary matches its own files, or whether the contents differ at equal length.
- Did Pipelines copy the payload from CHQ's vendored copy or directly from upstream? NOTICE names upstream. Pipelines carries upstream-derived items that CHQ excluded or never had: catalog/scripts/tests, validate-csv's mention of the removed design.csv and draft.csv, refresh scripts said to replace an upstream weekly workflow, and verify.py said to replace 'npm run verify:data'.
- Were the maintenance/ tools (validate-csv, refresh-google-fonts, refresh-icon-catalog, generate-catalog-summary, evaluate-relevance, relevance_metrics) ported from upstream repo-level tooling or authored new? CHANGELOG lists maintenance/ only as 'Added'.
- maintenance/candidates/stack-accessibility/ sits under a path the plugin .gitignore excludes ('candidates/'). Git tracking status was not checked, and REVIEW.md was never updated after the rows went live.
- relevance-thresholds.json baselineRevision '97eb2a2': the files do not say which repository or commit this refers to.
- Pipelines design_system.py is 72,490 bytes against CHQ's 70,937. The contrast, format and persist changes were located, but no line-by-line diff was run, so other changes cannot be ruled out. The same applies to reasoning_contract.py, which is only shown to have the same size.
- Has the plugin been published to github.com/groot99-droid/ui-design-plugin? CHANGELOG says 0.1.0 is Unreleased, and verify.yml has no effect until the plugin is published.
- Does CHQ's recorded payload sha256 still match the files on disk? No tool verifies it (DECISIONS.md D9). VENDOR.md says 3.11 MB and the vault note says 3.3 MB.
- No record shows CHQ validate_data.py ever being run, and tools/verify_system.py, which VENDOR.md names as the post-re-vendor check, does not reference tools/ui-ux-pro-max.
- For graphing into Pipelines, the files do not decide whether the CHQ-only pieces should be carried over or left out: the Router intercept and attestation, the dashboard writeback, the brand-gate token-authority split with ARTIFACT D, and the Designer Pro tab.
- No run record in the files shows the Pipelines skills or agents (ui-design-catalog, multipart, search-part, page-reviewer, catalog-refresh, catalog-reviewer) being invoked. Their 'runs-today' status means implemented and gate-checked, not observed running.
- Apart from TestNotShipped, the test files were not read, so test coverage and pass status are unknown. No script was executed.

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: Pipelines core.py: the only difference from CHQ is 3 added gsap output_cols
  - evidence: plugins/ui-design/catalog/scripts/core.py line 86: UNTRUNCATED_COLS also adds "CSS Snippet" (compare tools/ui-ux-pro-max/scripts/core.py line 86). The 65-byte size gap (41,299 vs 41,234) is exactly 50 bytes for the three output_cols entries plus 15 bytes for ', "CSS Snippet"'.
- **corrected**: The 4-byte difference between the validate_data.py copies (52,064 vs 52,060) was not located
  - evidence: Line 4 of the docstring reads 'Data integrity guardrail for ui-ux-pro-max' in CHQ and 'Data integrity guardrail for ui-design' in Pipelines. That is 4 bytes, which accounts for the whole size gap.
- **corrected**: tokens.py emits springs and reduced-motion under the extension
  - evidence: plugins/ui-design/catalog/scripts/tokens.py _motion_tokens: - motion.spring.default is a $type number token holding the stiffness, with the full model in $extensions['cc.uupm'].spring. - motion.reducedMotion.default is a plain $type string token, not placed in $extensions. - CSS Snippet is never emitted. SOURCE-RESEARCH.md item 5 says both go under $extensions, which the code contradicts.
- **corrected**: oklch.py is used for the shadcn oklch() output and for harvesting
  - evidence: Grep finds oklch imported only by catalog/scripts/shadcn_theme.py and tests/test_shadcn_theme.py. maintenance/harvest-site-tokens.py imports only argparse, json, sys, collections and pathlib; colours are canonicalised in the browser through a canvas. The inverse functions exist but only the tests call them.
- **corrected**: tokens.py is invoked only by design_system.py
  - evidence: maintenance/validate-contract.py load_catalog_modules() imports tokens so it can compare tokens.EXTENSION_KEY with spec.yaml dtcg_extension_key.
- **corrected**: generate-index.py depends on pyyaml
  - evidence: maintenance/generate-index.py calls load_yaml() only in collect_entries(), which runs only for the Pipelines root index when the plugin sits under plugins/ with CLAUDE.md at the root. The plugin INDEX.md build is standard library only. The requirements.txt comment names only validate-contract.py and smoke.py.
- **corrected**: generate-index.py reads catalog/data, references, skills and agents, and writes INDEX.md
  - evidence: In the monorepo it also reads Pipelines/.claude/skills/*/SKILL.md, .claude/agents/*.md, plugins/*/skills/*/SKILL.md, plugins/*/agents/*.md and the top-level folder names (TOOL_PURPOSE lists creative-writing and plugins). It writes both plugins/ui-design/INDEX.md and Pipelines/INDEX.md; both exist and carry the generated header.
- **corrected**: merge_parts.py exits 0 when all parts are well formed and 1 on errors
  - evidence: merge_parts.py main() also calls parser.error(), which exits 2, for --mode search without --manifest and for an unknown --areas value. argparse enforces --mode and --results as required.
- **corrected**: validate-contract.py runs "beauty spa wellness service" --design-system, "keyboard focus modal" --domain ux and "virtualized list" --stack react-native
  - evidence: run_json() appends --json to all three. check_release_files also requires plugin.json name == 'ui-design', a MAJOR.MINOR.PATCH version, a marketplace listing exactly ['ui-design'] with source './', and a newest CHANGELOG '## [x.y.z]' heading equal to the version. GUIDE_REQUIREMENTS phrases must appear in the ui-design-catalog SKILL.md. ROUTER.md and references/*.md are also checked for portability.
- **corrected**: evaluate-relevance.py: a data or runtime change forces regenerating the fingerprint, done through the script
  - evidence: No flag writes relevance-thresholds.json; --write-baseline writes only the baseline file. validate_manifest compares the thresholds file's runtimeFingerprint and oracleFingerprint with the live values. The ui-design-catalog-refresh SKILL.md tells the maintainer to regenerate those two fields separately. The runtime fingerprint covers core.py, design_system.py, reasoning_contract.py and every *.csv under catalog/data (no JSON). The oracle fingerprint covers evaluate-relevance.py, relevance_metrics.py and relevance-cases.json. The thresholds file's status is 'provisional-baseline-regression-gate' and its baselineRevision is 97eb2a2.
- **corrected**: The plugin .gitignore lists .env, design-system/, candidates/ and captures/
  - evidence: plugins/ui-design/.gitignore contains .env, .env.*, !.env.example, *.key, *.pem, __pycache__/, *.py[cod], .venv/, venv/, design-system/, candidates/ and captures/.
- **corrected**: CHQ ui_ux_intelligence skill -> Pipelines ui-design-catalog skill: migrated-to
  - evidence: NOTICE says the plugin's skills, agents, router, checks and packaging are additions. None of the CHQ skill's specific content (P1-P4, ARTIFACTs A-D, attestation, context flushes) appears in plugins/ui-design/skills/ui-design-catalog/SKILL.md. The relation is changed to 'counterpart-in-target (not a file migration)'.
- **unverifiable**: In Pipelines the same payload (the CHQ copy) became the plugin
  - evidence: NOTICE says the catalog 'began as a plain copy of' upstream ui-ux-pro-max-skill. Pipelines carries upstream-derived material that CHQ never vendored: catalog/scripts/tests, which VENDOR.md excluded; verify.py, 'replaces the source project's npm run verify:data'; and the refresh skill, 'replaces the weekly GitHub workflow the catalog came from'. No file shows the CHQ copy as the source.
- **corrected**: Pipelines dropped CHQ's vendoring model and has no payload hash
  - evidence: Pipelines has no whole-payload hash, but it has hashes the gates enforce: the catalog-summary.json snapshot sha256 values for 4 files (checked by validate_data.py and generate-catalog-summary.py --check) and the relevance runtime and oracle fingerprints (evaluate-relevance.py). CHQ carries the same catalog-summary snapshot mechanism, checked by its validate_data.py, which has no CHQ caller.
- **added**: Pipelines design_system.py surfaces the new motion columns
  - evidence: design_system.py format_ascii_box (lines 743-751), format_markdown (lines 868-881) and format_master_md (lines 1350-1372) render only Category, Intensity Tier, Trigger, Duration, Easing, GSAP Snippet, Framework Notes, Do, Don't and Performance Notes. Spring Params, CSS Snippet and Reduced Motion appear only through --json, -f dtcg (spring and reduced motion) and --domain gsap results.
- **added**: CHQ skill lists 22 stacks
  - evidence: The ARTIFACT A 'Stacks:' line in skills/ui_ux_intelligence.skill.md names 21 stacks and omits jetpack-compose, although the skill header says 22 technology stacks.
- **added**: CHQ payload excludes __pycache__ and *.pyc (VENDOR.md)
  - evidence: A Glob of tools/ui-ux-pro-max/** finds scripts/__pycache__/core.cpython-313.pyc, design_system.cpython-313.pyc and reasoning_contract.cpython-313.pyc. They are gitignored by CHQ .gitignore '__pycache__/', but the working tree is not the pure 44-file payload.
- **added**: The inventory covers everything on disk in plugins/ui-design
  - evidence: Missing from the inventory: - maintenance/candidates/stack-accessibility/{REVIEW.md,angular.csv,nextjs.csv,astro.csv}: staged 2026-09-20; REVIEW.md still says 'not promoted' although the rows are live. - maintenance/.env.example: GOOGLE_FONTS_API_KEY only, not loaded automatically. - maintenance/requirements.txt: pyyaml. - catalog/scripts/tests/fixtures/catalogs/*. - the generated plugins/ui-design/INDEX.md and Pipelines/INDEX.md.
- **added**: CHQ design_system.py exposes generate_design_system only; ARTIFACT B is the full payload shape
  - evidence: tools/ui-ux-pro-max/scripts/design_system.py also defines persist_design_system() (line 995) and safe_slug() (line 961). The payload has a 'reasoning_default' key (line 581) that ARTIFACT B does not list.
- **added**: validate_data.py prints an OK line on success
  - evidence: Both copies' docstrings say 'Exits 0 with no output on success', while main() prints 'OK: validated ...' (CHQ line 1086). The docstring is stale in both repos.
- **corrected**: SOURCE-RESEARCH.md stale references are scripts/add-motion-columns.py, scripts/tokens.py and .claude/skills/ui-design-catalog/SKILL.md
  - evidence: It also cites scripts/contrast.py, scripts/shadcn_theme.py and scripts/oklch.py (the files now live in catalog/scripts/). A Glob for add-motion-columns* finds nothing in either tree.
- **corrected**: Pipelines --diagnostics prints or includes top_score, margin, token_coverage and reason
  - evidence: The text line shows those 4 fields (DIAGNOSTIC_FIELDS in search.py). With --json the whole core diagnostics dict is included, with fields such as calibration_version and abstained (core.py lines 731 and 819). --diagnostics is ignored with --design-system.
- **added**: Plugin install and load commands
  - evidence: README.md also gives the shell forms 'claude plugin marketplace add groot99-droid/ui-design-plugin' and 'claude plugin install ui-design@ui-design-plugin'. Pipelines CLAUDE.md line 99 gives the local form 'claude plugin marketplace add ./plugins/ui-design'.
- **unverifiable**: The catalog-summary snapshot sha256 values differ between CHQ and Pipelines for an unshown reason
  - evidence: A directory listing shows the four snapshot files at identical byte sizes on both sides: google-fonts.csv 747241, google-font-licenses.json 433127, icons.csv 57945, phosphor-icons-upstream.json 823933. Both repos digest raw bytes (CHQ validate_data.py line 666; Pipelines generate-catalog-summary.py digest()). So either one side's recorded hashes do not match its own files, or the contents differ at equal length. No hashing was run.
- **corrected**: The Router intercept sequence is MODE -> RESOLVE -> LADDER -> RECALL -> VERIFY -> STATE -> EXECUTE -> WRITEBACK, and router.js dispatch is a stub
  - evidence: Router.md lines 131-141 confirm the 8 steps. router.js routeSkill() line 288 has 'TODO: POST to local agent runner', and the dashboard writeback at line 339 is also a TODO stub that only logs.
