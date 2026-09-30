# Ideas carried from Creative-Headquarters

Creative-Headquarters was mostly a specification. This file records every idea
in it and what became of that idea here, so that nothing was dropped without a
reason being written down.

What Creative-Headquarters contains, tool by tool, is in
[INVENTORY.md](INVENTORY.md).

Paths on the left of each table are in Creative-Headquarters. Paths on the right
are in this repo.

## The decisions that shaped this

Made by the author on 2026-09-28.

1. Migrate only what works. The ideas matter more than the code; the rest is rebuilt.
2. Everything is in scope, redone for its new usage rather than copied.
3. New usage: staged, checkpointed pipelines whose stages call the connectors
   available in Claude Code.
4. Memory: a new studio vault of Content MDs. The creative-writing vault is not touched.
5. Every stage is a checkpoint.
6. The UI pipeline is built first.
7. Three stage agents replace the nine generic personas.

## What each status means

| Status | Meaning |
|---|---|
| carried | the idea holds here as it did there, and what the row names exists |
| changed | the idea holds, in a different form; the difference is stated. What the row names exists |
| rebuilt | the idea is kept and its code has been written again. It exists |
| planned | the idea is kept. Nothing is built yet; the row says what will be |
| deferred | kept, with no work scheduled until something needs it |
| dropped | not carried; the reason is stated |

A test reads this file. A row marked carried, changed or rebuilt that names a
path in this repo fails the test if the path is not there.

## What a check here can and cannot do

Every check reads what the skill wrote down. None can tell whether what was
written is true. Where a row below says something is checked, it means the
record is checked: that a row exists, that it cites a section the gate has, that
a note it names is in the vault and says the line quoted. Whether the section
really states the constraint is for the author, at the checkpoint.

## The protocol

Source: `Router.md`.

| Idea | Source | Here | Status |
|---|---|---|---|
| No skill executes without its context resolved, attested and sourced | §0 | `context` comes before `execute` in `studio/pipeline/spec.yaml`. `advance` will not mark context done without an attestation that has a row for every needed constraint, each backed the way its level requires | carried |
| Output is a function of the input and the matched context, nothing else | §0 | the recipe stage asks for the source of every value. Nothing checks a recipe | carried |
| Derived is allowed and labelled; invented is not allowed | §0, §10 | a row whose level is derived must be marked provisional and cite three notes; the note must then record it as provisional. A derivation written down as authored is not seen | carried |
| Dual-trigger intercept: intent words, or the asset and state a task touches | §2 | Claude Code's own skill matching on the skill's description. **This is opt-in.** There is no intercept, so the second trigger (asset and state) has no counterpart | changed |
| The eight-step sequence | §2 | six stages: `intake`, `context`, `recipe`, `execute`, `review`, `record` | changed |
| Routing table: skill to mandatory context | §3 | `requires_context` on each pipeline entry, stated as gate and what is needed from it | carried |
| Routing table: context loaded only when flagged in the dashboard | §3 | there is no dashboard. A pipeline lists what it always needs; anything else is asked for at the context stage | dropped |
| A multi-skill task takes the union of its context sets | §3 | UI work is two pipelines, not one: `ui-direction` needs three gates, `ui-build` needs those and `brand_voice` | carried |
| A domain library never satisfies a mandatory slot | §1, §3 | a row's gate must be one of the ten in the spec | carried |
| L0 means authored, not complete | §3 | a gate's declared gaps are its own `## N. Unresolved` section, read from the file. An L0 row that cites one is refused | carried |
| A brand gate encodes taste and is never generated | `context/brand/README.md` | the `brand-gate` pipeline: an interview whose transcript is the only source, the whole gate shown before `studio/pipeline/gate_md.py` writes it, and a Provenance section naming the author, the date and the run | rebuilt |
| Three execution modes | §4 | one mode. The skill stops at every stage and waits (decision 5) | changed |
| Resolution ladder: L0 authored, L1 recalled, L2 derived, L3 unresolved | §5 | the `context` stage, with a fifth level, `STATED`, for what the author says at the checkpoint | changed |
| L1 cites the note and states the constraint directly | §5 | the row names the note and quotes the line. The note must exist, must list the gate under `context_brand`, and must have that line under Decisions in Force | carried |
| L2 needs at least three notes; fewer is a coincidence | §5 | three notes that exist in the vault and are of the kind the pipeline makes | carried |
| L2 weighs a complete note over one in progress, and a recent one over an old one | §5 | stated in the ladder. Nothing checks the weighing | carried |
| L2 confidence between 0.3 and 0.8 | §5 | no formula was ever defined. The row lists its sources and is marked provisional; it carries no number | changed |
| Park: write the gap into Next Steps, set `status: blocked`, move on | §5 | `studio_run.py park`, after the author has been asked and has not answered. The note must then name the constraint in its first Next Step | changed |
| Attestation block, printed before the first tool call | §6 | `attestation.md`, written in `context` and shown at its checkpoint | carried |
| Create the Content MD at task start, as a seed | §7 | the note is not created at intake. Every write to the vault needs a preview and a yes, so the first write is at record, at a flush, or at a park. A session that ends without a flush leaves only the run folder | changed |
| Every routed task reads and writes exactly one Content MD | §7 | a run that has written a note cannot be pointed at another | carried |
| Decisions in Force bind a task exactly as a brand constant does | §7 | the context stage is told to list them. Nothing checks that it did | carried |
| Context flush: state lives in the Content MD, not in the conversation | §8 | the session flush. `runs/<run-id>/state.json` is bookkeeping and may be deleted | carried |
| Confirm no phase conflict before executing | §2 | the writer refuses when the note in the vault changed after the plan was made, and `note` warns when another live run names the same note | changed |
| One dashboard write and one event per phase change | §9 | each run keeps its own list of events in `state.json`. There is no dashboard | changed |
| `PARKED`, `PROVISIONAL` and `INTERCEPT_VIOLATION` are logged with the context name and the note path | §9 | parked and provisional are written into the note itself. There is no intercept violation, because there is no intercept | changed |
| A skill whose `host_kinds` excludes the current host is not routable | §1 | there is one host, and it is Windows | dropped |
| Hard refusals hold in every mode | §10 | `refusals:` in the spec. Each names what enforces it and what that cannot see | carried |

## The memory

Source: `vault/SCHEMA.md`, `DECISIONS.md` D6.

| Idea | Here | Status |
|---|---|---|
| One Content MD per made thing, not per session | `studio/vault/SCHEMA.md` | carried |
| The first screenful answers: what is this, and what do I do next | `studio/pipeline/content_md.py` refuses a note whose first section is not Overview, whose second is not Next Steps, or that has text before them | carried |
| The note is read cold and must be enough to resume | a flush must name the run and the stage in its first Next Step | carried |
| Timeline is append-only; a wrong entry is corrected by a new one | the writer refuses a proposal that changes, removes or reorders an entry of the note in the vault, and refuses to write over a note it cannot read | carried |
| Never record a step that was not taken | the skill is told to build the entry from `execute_log.md` and `review.md`. Nothing checks it | carried |
| Next Steps is rewritten in full each session | the skill is told to. Nothing checks it | carried |
| Method must be enough to reproduce | the skill is told to. Nothing checks it | carried |
| The vault is the source of truth; an index never owns it | carried as written | carried |
| Self-learning is corpus growth | the ladder's L1 and L2 read past notes | carried |
| The `kind` vocabulary does not fit writing | moot: the writing vault keeps its own schema and is not migrated | dropped |

## The decisions, one by one

Source: `DECISIONS.md`.

| Decision | What it said | Here | Status |
|---|---|---|---|
| D1 | The memory layer is local-first: no seven-service cloud stack | the vault is plain files; `studio/vault/tools/vault_index.py` indexes it without note bodies | carried |
| D2 | The brush designer becomes a capability the system can call, not a panel it links to | a `brush` pipeline: the designer exports a bundle, `studio/pipeline/brush_pack.py` packs it. It starts once the app is under `studio/hub/brush/` | planned |
| D3 | The archive's canonical source is crispy-engine | the archive is not carried | dropped |
| D4 | The archive's directory structure was derived from its imports | the archive is not carried | dropped |
| D5 | A third-party key was scrubbed from the archive's docs | nothing from `archive/` is copied, its documents included | carried |
| D6 | The unit of memory is the Content MD, not a ledger of live variables | `studio/vault/` | carried |
| D6 addendum | Five skills gate on stale state; rewrite them after `brush_designer`, which goes first | the five are declared as pipelines. **The order changed**: the UI pipeline goes first (decision 6) | changed |
| D7 | The router is mode-aware; autonomous never waits on a human | **Changed by decision 5.** The skill waits at every stage. What D7 protected is kept: nothing is guessed, and a blocker is written into the note | changed |
| D8 | One Windows laptop, not a Mac and a CUDA node. Thresholds re-cut, single flight, models evicted, tiers instead of a model name | kept for anything that runs locally, when something does. The WSL branches are not carried: they never ran on this machine | planned |
| D9 | ui-ux-pro-max is vendored as a skill and authors three brand gates; two token authorities, split by consumer | the corpus is `plugins/ui-design`. The split is the `consumers:` block of `ui-direction` | carried |
| D9 addendum | The generator misrouted twice; the old palette failed WCAG; four bugs appeared only on rendering | `ui-direction` checks the matched category before using a result and retries once. Rendering is `ui-build`'s, which is not built | carried |
| D10 | HARD MONO: one family, no glow, inversion as elevation, three measured contrast floors | the three gate files, carried unchanged, and `studio/vault/_Context/brand/tokens.json` as a real file | carried |

## The skills

Source: the nine files in `skills/`. Each was a set of instructions for an agent
to follow. No code executed any of them.

Each is now an entry under `pipelines:` in `studio/pipeline/spec.yaml`. One is
implemented. The rest say what they need and what they carry, and do not start.

| Skill | Becomes | What is kept | What is dropped | Status |
|---|---|---|---|---|
| `ui_ux_intelligence` | `ui-direction` | the anti-fabrication law, the query contract, the scope boundary between studio surfaces and product work, the propose-only loop | the vendored copy; `plugins/ui-design` replaces it. "Never install Python" is that plugin's own rule and stays there | rebuilt |
| `css_html_ui` | `ui-build` | tokens are law; render and measure at each breakpoint; script toggles a token-backed class and never sets a literal colour; a status maps to a class as the token dictionary says; a new region is a grid area; HTML written from data is escaped | the token dictionary embedded in a skill file, which is now `tokens.json`. Its copy rules wait on `brand_voice`, which is the author's to write | planned |
| `adobe_firefly` | `still-image` | a style reference is recorded, and a change supersedes it without erasing the old one; no speculative submission | the credential step, the payload templates, the regex set. The connector is Higgsfield, not Firefly: the installed image tools are edits, not generation | rebuilt |
| `higgsfield_api` | `video-shot` | continuity is carried in the note; a continuation starts from the last frame; a drift check every third shot; the seed is never randomised | the API payloads, the continuity state machine file, the UUID protocol | rebuilt |
| `suno_audio` | `music-cue` | tempo and key are decisions in force; one direction per generation | the endpoints, which were never called; the bracket-tag fixtures | rebuilt |
| `adobe_suite_uxp` | `edit-2d` | never change a file that was not read in this task; work on a copy; the output spec comes from the gate | the COM bridge and the ExtendScript wrappers; Premiere | rebuilt |
| `blender_python` | `scene-3d` | fixed scripts with their parameters as the Method; a local render needs a compute token | the headless templates; the Blender scene connector does the cloud branch, a local Blender the other, when installed | rebuilt |
| `local_rag_orchestration` | an index of the vault | answer only from what was retrieved, and cite it; evict a model after use | local generation as the executor. Claude is the executor here | planned |
| `hardware_compute` | a compute gate | one token authorizes one job; an unreadable reading closes the gate; one heavy job at a time; AC power and thermal headroom | thresholds embedded in markdown and extracted by a regular expression | planned |

The Four-Part Artifact Architecture (header, prerequisites, process, embedded
artifacts) maps to: a pipeline entry, the `context` and `recipe` stages, the
stage list, and real files.

## The tools

| Tool | Here | Status |
|---|---|---|
| `tools/ui-ux-pro-max/` | already `plugins/ui-design/`, with more than was vendored | carried |
| `tools/brush-designer/` | the Procreate export written again in Python: `studio/pipeline/brush_pack.py`. The app itself is copied in from the laptop when the author has it; its bplist encoder and its Ollama tab are left behind | changed |
| `hub/`, `tools/launcher/` | `studio/hub/`: a page over the vault's notes, the runs and the gates, served by `studio/hub/serve.py` from its own folder only; the launcher and shortcut scripts under `studio/hub/launcher/`. No browser-side Ask, no Ollama | rebuilt |
| `tools/vault_manifest.py` | `studio/vault/tools/vault_index.py`: one row per note without its body, and a search by section | rebuilt |
| `tools/vault_rag.py` | not carried. Its index was built from a folder that no longer exists, and its generation step duplicates the executor | dropped |
| `tools/hw/` | a compute gate with three defects fixed: a denial that overwrites a live token, a re-issue that clears who holds it, a test that writes to the real token | planned |
| `tools/bootstrap.sh`, the embedded probe | a probe written for this laptop, as a real file | planned |
| `tools/reconcile_models.py` | report only, against a settings file | planned |
| `tools/verify_system.py` | `studio/pipeline/tests/test_spec.py`. The idea is kept: a contract stated in several places is checked to agree | rebuilt |
| `control_room.html`, `router.js` | the Runs tab of `studio/hub/`. The routing stubs are not carried | rebuilt |
| `dashboard.json` | split: `studio/pipeline/spec.yaml` holds the registry, `runs/` holds run state. Model settings get a file of their own when something local needs them | changed |
| `context/brand/` (three authored) | `studio/vault/_Context/brand/`, byte for byte | carried |
| `context/brand/` (seven unauthored) | names in the spec. No file exists until the author writes one | carried |
| `context/domain/` (ten libraries) | none carried yet. No skill ever named one. One is carried when a recipe first cites it | deferred |
| `agents/` (nine personas) | three read-only stage agents (decision 7): one to condense precedent, one to draft a recipe, one to review | planned |
| `archive/` | never installed, built or started; its stack was rejected by D1. Its classification contract and its graph view are recorded below | dropped |
| `vault/_migration/GAP-ANALYSIS.md` | the writing vault is not migrated | dropped |
| `vault/studio-os/ui/ui-ux-intelligence-integration.md` | to be carried as the vault's first precedent, through the writer, so that it is previewed | planned |

## Kept as ideas, with no work scheduled

| Idea | Source | Note |
|---|---|---|
| A classifier that returns a taxonomy path, a confidence, links, entities, a summary and key phrases | `archive/backend/app/services/ai_engine.py` | If it is ever built, it runs on the local model. It sends note text to a model, so it is never a cloud call |
| The cosmos view: the vault drawn as a graph | D6 | Wikilinks under `## Links` and Obsidian's own graph come first. A generated canvas follows, from `docs/inventory/graph.json` and the vault |
| Blending catalog rows into one direction with a local model | the hub's Designer Pro tab | The conflict checks need no model and are the more useful half |
| Renaming the accent tokens from colours to meanings | D10, recorded there as debt | Still debt |

## Where the source contradicted itself

| Question | One source | Another | Settled as |
|---|---|---|---|
| What happens at L3 | D7: "L3 parks in every mode" | `Router.md` §5 table: ask, ask, park | Ask at the checkpoint. If the author does not answer, park. Nothing is guessed either way |
| Which tool issues the compute token | `Router.md` §10: `verify_compute.sh` | `BOOT.md`, D8: `evaluate_gate.py` | The evaluator issues it. The probe only measures |
| Whether a token is consumed at issue | `BOOT.md`: `--consume` at issue | two skills: `consumed_by` must be null on arrival | The consumer stamps it. Issue leaves it null |
| How many font weights | the policy, `typography_system` §2 and `visual_identity` §6: two, and no third | the same §2 allows 500 for a status word; the token dictionary declares `weight.mid` 500 | 500 is for a status word only, as §2 says. The files are carried unchanged and the spec lists the conflict |
| What enforces the gate files | two gate files: "machine-enforced" | the check read seven colour values and never opened a gate file | Nothing enforced them. Here `test_context.py` checks that the ten colours in `tokens.json` are the ten in `color_science` §2. There is no surface to check yet |

## What is not enforced, stated plainly

- A pipeline is entered by choice. A connector can be called without one.
- The bookkeeper refuses to advance a run. It cannot refuse a tool call.
- A checkpoint stage advances when `advance` is run. The bookkeeper cannot tell
  whether the author reviewed it.
- A go-ahead is recorded because the skill says one was given.
- An attestation is checked for its form and for what it cites. Whether the gate
  says what the row claims is not.
- A note edited by hand in Obsidian passes through none of this. `content_md.py
  lint --all` reads it afterwards.
