# ROSW Complete Record (public copy)

**6 ROSW documents in one file.** Compiled 17 November 2026 for NotebookLM. This is the copy kept in the public repository.

## What was left out
The owner's full record has a seventh document (a personal record reconciliation) and personal sections in Part 3 and in the Capacity Addendum. They cover residence, family, health, study, relationships, private research topics and personal routines. They are **not** in this copy. Where a document here points to a personal section, that section is not included. The owner holds the full version. Nothing else was changed.

## How this file is organised
Each document below is reproduced in full, in the order listed, with its own headings, labels and section numbers (minus the omissions above). Documents refer to each other by name (for example "Part 3 section 1B").

## Contents
1. **Part 1 (updated edition): the Studio Headless OS, its review, and its status**: What the Studio Headless OS is, the v1 audit, the v2 design, the independent review, and where each idea stands.
2. **Part 2 (updated edition): March to 18 October**: Every project and every cloud session to 18 October, with corrections.
3. **Part 3: 18 October to 17 November**: The last 30 days, the owner's purpose, bottlenecks, portfolio, and corrections to earlier parts.
4. **Phase 4 Planning**: All fixes, suggestions and proposals, with questions and defaults for the owner.
5. **Skillification Plan**: How to turn everything into repeatable skills, skeletons and one world.
6. **Owner Profile and Capacity Addendum**: The owner's capacity, pace and constraints. Controls where it conflicts with the others.

## Which document controls
- **The Owner Profile and Capacity Addendum controls** wherever any other document conflicts with it about the owner's pace, attention, capacity or constraints.
- **Part 3 section 12** lists corrections to Part 2.
- **The Phase 4 Planning document and the Skillification Plan hold proposals only.** Everything else records what happened.

## Labels used across the documents
[Evidence] a file or record shows it; [Owner] the owner said it and it was not verified; [Memory Log] the owner's Memory Log says it; [Inference] Claude's interpretation; [Corrected] changes an earlier statement; [Resolved] the owner settled a conflict; [Proposal] a suggestion not yet decided; [Unknown] the record cannot say. In Part 1, SOURCE, ANALYSIS and PROPOSAL keep their original meanings and STATUS was added.



---

# DOCUMENT 1 OF 6

# ROSW Progress Report, Part 1 (updated edition)

**Studio Headless OS: the v1 post-mortem, the v2 architecture, the independent review, and where each idea stands on 17 November 2026.**
Original written for NotebookLM before 18 October 2026. Updated 17 November 2026.

---

## 0. How to read this document

- **This is a condensed, updated edition.** The original Part 1 ("Studio Headless OS: Complete Source Document and Critical Analysis", about 28 pages) remains the full source for line counts, defect lists, the drive layout, the learning curriculum and the verbatim reasoning. This edition keeps every idea and finding, shortens the prose, and adds a status for each one.
- **Provenance labels are kept.** SOURCE is a statement by the project's author. ANALYSIS is explanation added by the reviewer. PROPOSAL is a reviewer recommendation that the author has not adopted. STATUS (new) is what the repositories and the owner say about it on 17 November.
- **STATUS evidence.** Marked [Evidence] when a file, test or commit shows it, [Owner] when the owner said it on 17 November and it was not checked, and [Not checked] when I could not tell. The repositories read are Pipelines-Plugin (ROSW), where the studio lives, and the others in Part 3.
- **The owner's purpose changes how this document should be read.** The owner builds to learn, builds to prove, and measures work done, not whether it is good (Part 3 section 1B). Part 1's own risk framing (scope, "specified, not built") is kept as the original author wrote it; it is not a pass or fail test.

---

## 1. What the system is for

**SOURCE.** A creative engine that remembers your work, so that output is grounded in your own accumulated precedent, not a generic model's guess.
**ANALYSIS.** The valuable asset is not the model, which is replaceable, but the accumulated record of decisions, which is not.
**The loop (SOURCE).** (1) an input arrives; (2) it is routed to a skill; (3) the skill's required context is resolved; (4) the Content MD note for the thing is read; (5) the skill executes; (6) the artifact is written; (7) the note is updated; (8) the note is indexed so it becomes precedent; (9) that precedent feeds the next task's context resolution.
**ANALYSIS.** The loop is closed and self-feeding, which makes the system accumulate. It is also the source of its subtlest risk (section 6, G.3).
**STATUS [Evidence].** The studio in ROSW runs a version of this loop with six stages and checkpoints (`studio/vault/CLAUDE.md`): intake, context, recipe, execute, review and record. Each stage writes a file (`brief.md`, `attestation.md`, `recipe.md`, `execute_log.md`, `review.md`, then a note) that the author reads before the next stage.

### Three foundational ideas (SOURCE)
1. **The Prime Rule.** No skill executes without its context resolved, attested and sourced. Context carries the reason; skill files carry the method. Output is a function of the input and the matched context, and nothing else.
2. **Memory is a note on disk, not session state.** Every made thing gets one Content MD note in an Obsidian vault: the exact steps, the decisions now binding, and what happens next. No conversation state survives; if the note does not say it, it is lost.
3. **The system never guesses and never launders provenance.** A constraint it cannot source it does not have. Derived constraints are labelled derived, with confidence and sources, permanently. A task that cannot be grounded is parked with a written reason; the work stops, the system does not.

**STATUS [Evidence].** All three are written into the studio vault's own CLAUDE.md as "the prime rule", the ladder and parking, and into `studio/pipeline/spec.yaml` ("nothing is made before its context is resolved, attested and sourced"; "a derived constraint is always marked provisional, with its sources"; "a run with an unresolved constraint does not advance; it is answered or parked").

---

## 2. The seven mechanisms (SOURCE, with ANALYSIS and STATUS)

| # | Mechanism | What it is | STATUS on 17 Nov |
|---|---|---|---|
| 1 | **Dual-trigger intercept** | Two independent detectors decide whether a request is a routed task: intent verbs in what the user said, and file types and pipeline state in what the task touches. Either firing is enough. Accepts false positives to avoid silently skipping the protocol. | [Evidence, partial] The studio is entered by choice. Its CLAUDE.md says "a pipeline is entered by choice. Nothing here can stop a tool being called outside one." Skill trigger descriptions were tightened on 31 October (Wave 1 lane D). No automatic interception. |
| 2 | **Routing table** | Each of nine skills declares two or three mandatory brand gates. The exact place of v1's four-copy drift. | [Evidence] `spec.yaml` is the single source for pipelines, stages, gates and refusals; `studio_run.py` reads it and nothing about a stage is in the code. Tests check that the spec, gate folder, documents and skill agree. |
| 3 | **Resolution ladder** | L0 authored file, L1 recalled decision, L2 derived from at least three notes, L3 nothing. Confidence at every rung. Three notes is a hedge against inventing a pattern from coincidence. | [Evidence] Implemented as written in `spec.yaml` and the vault CLAUDE.md, including the three-note rule for L2. At L3 the author is asked; if they do not answer, the run is parked. |
| 4 | **Mode gate** | Three modes (manual, supervised, autonomous) differ in one respect only: what happens on an unresolved constraint. L3 parks in every mode. | [Evidence, differs] The studio has **one mode**: "every stage is a checkpoint... there is no autonomous mode here" (`spec.yaml`). The three-mode matrix was not built. The orchestrated session fleets (Part 3) are where autonomy lives, outside the studio. |
| 5 | **Attestation block** | Printed before the first tool call: every required context, its level, confidence and source. A missing row is itself a violation. | [Evidence] The context stage writes `attestation.md` and shows it; `studio_run.py advance` will not mark context done without a whole attestation; each row is checked to be backed the way its level requires (an L1 row cites a note that exists, an L2 row cites three notes of the kind being made). The CLAUDE.md states what is not enforced: it cannot check that a citation says what the row says. [Not checked] whether source content hashes are stored. |
| 6 | **Hardware gate** | A bouncer, not a launcher. Compute work needs a fresh PASS token with a 30-minute time-to-live; one token, one job. Power, thermal and single-flight are first-class gates. | [Evidence] `compute_gate.py` and `machine.yaml`: tokens with `ttl_seconds: 1800`, per-class TTL and renew, single live token at a time, thermal and memory thresholds, AMD and Arc GPU detection added 31 October. |
| 7 | **Content MD writeback** | Every routed task reads one note and rewrites it at the end. Timeline append-only; steps never fabricated. | [Evidence] Every write into `studio/vault/` goes through `content_md.py` (plan, then apply, which is a dry run without `--confirm`, then a recorded author go-ahead). Notes are previewed before they are written. |

---

## 3. The v1 audit (SOURCE), with what has changed

### 3.1 Scale
About 78,000 lines, of which about 58,000 were a vendored third-party corpus (so about 20,000 first-party). 27 commits. About 2,000 lines uncommitted at the time.

### 3.2 What genuinely worked in v1 (SOURCE)
The brush designer UI and its 51-parameter model (5,700 lines, 34 typed ranges, 10 panels); the live stroke preview (three-layer canvas, speed-based pressure substitute labelled honestly as speed); the GIMP `.gbr` encoder (65 lines, correct); the Universal Kit export (which explicitly refuses to guess at Photoshop's `.abr`); AI brush assist with real Ollama calls and a patch validator that surfaces rejected keys; `vault_rag.py` (588 lines, standard library, content-hash reuse, model eviction as protocol law); the hardware gate (the only tested code, ten test cases); `verify_system.py` (13 integrity checks); CI that treats `EncodingWarning` as fatal; Hub Designer Pro (deterministic conflict checks injected into the prompt); a loopback-only launcher; and about 1,800 lines of protocol documents judged "genuinely excellent".

### 3.3 What was built but broken or unproven in v1 (SOURCE)
- **The Procreate `.brush` export was structurally broken**: the plist encoder had no UID branch, so object references were encoded as dictionaries, and string de-duplication shifted the `$objects` indices. The output was a valid property list that NSKeyedUnarchiver could not decode. No file had ever been opened in Procreate. **STATUS [Evidence + Owner]:** ROSW's `brushes/` has a codec rebuilt as "byte-exact Procreate archives" (30 October) with keyed-archive tests and fixtures, and a frozen contract document. The owner reports on 17 November that the brush tool works in both Procreate and Photoshop (owner's own testing). The brush app's README says `.abr` is deliberately "not offered", so the Photoshop route uses another export; which one is not recorded.
- **Preview fidelity:** only 13 of 51 parameters affected the preview. **STATUS [Not checked]** for the rebuilt designer app; the capability coverage manifest (G.5) was not found.
- **Pressure curves** (editor worked, renderer ignored it, undo corrupted it, tabs reset it), brush import (a toast saying "not yet implemented"), the download-source feature (a hardcoded list of 22 paths, one non-existent), `router.js` dispatch (logic ending in a console log; never called), `dashboard.json` (a hand-authored fixture with null sensors), and an archived seven-service cloud stack (FastAPI, PostgreSQL, Neo4j, Pinecone, Redis, Celery, Groq) that had never been installed. **STATUS:** the archive was left behind when the work moved to ROSW; Creative-Headquarters was deleted on 1 October 2026 after migration. [Not checked] each item in the rebuilt brush tool.
- **Any routed task: specified end to end; nothing executed it.** **STATUS [Evidence]:** the studio's stages now run through `studio_run.py` and are exercised by tests; 68 of 78 new tests failed against pre-fix code in the 28 to 29 September review (Part 2), which is the proof the tests catch what they should.

### 3.4 The structural failure (SOURCE)
**The duplication disease.** The routing table lived in four hand-maintained copies; the palette in four places; model tags in four; the same port in four (8765, 8347, 8000 and 8787 for a runner that did not exist); an HTML-escaping helper three times; a UUID generator three times. **Root cause (SOURCE):** the protocol is prose that code is trusted to obey, not a definition that code is compelled to derive from. **ANALYSIS:** the verifier passing 17 checks was not health; it was a machine managing a problem that should not exist.
**Two further limits:** no client and server boundary (the browser talked to Ollama directly, so `OLLAMA_ORIGINS` was a manual step; `localStorage` became the database and would exceed its quota); and no tests where they mattered (the encoders).
**What v1 got right and must survive (SOURCE):** every fake thing is labelled as fake. "A system that is half-built and says so is more useful than one that is three-quarters built and does not."
**STATUS [Evidence].** The honesty discipline survives: the studio CLAUDE.md has a "What is not enforced" section; repository docs carry "unverified" notes; Wave 1 (31 October) was a "truth pass" that corrected claims against code; every Blender add-on tool ships off.

---

## 4. The v2 design (SOURCE), with status

**Target.** A self-contained creative operating system on a 2 TB external drive: plug into any Windows machine, run one executable, and the kernel, database, local models, vault and interface come up with nothing installed on the host.

### The six laws
| Law | Rule | STATUS on 17 Nov |
|---|---|---|
| **L1** | One machine-readable protocol definition from which everything derives. | [Evidence, adopted in a different form] `studio/pipeline/spec.yaml` is the single source; code and tests derive from or check against it. It is YAML read by Python, not TypeScript types. |
| **L2** | The kernel is the only thing that touches the outside world. | [Evidence, partial] The hub binds 127.0.0.1 and serves its own folder only; Wave 1 added a Host and Origin check. There is no single privileged kernel; `studio_run.py` is a bookkeeper that "never calls a model or a tool". |
| **L3** | The vault is the source of truth; the database is a rebuildable index. | [Evidence, adopted] The studio vault is Markdown; `vault_index.py` builds an index that "carries no note bodies and is not versioned". |
| **L4** | Zero network at runtime. | [Evidence, not adopted as written] Studio pipelines call connectors (Higgsfield, Meshy, others) and say so: each pipeline lists the tools it may call, and the vault CLAUDE.md has a "What leaves the machine" section. The law was replaced by an explicit, per-pipeline list. The F.1 contradiction with a git remote was resolved by making egress declared, not absent. |
| **L5** | A skill is an executable module with a typed manifest. | [Evidence, partial] Skills are Markdown files governed by `spec.yaml` and a contract validator; agents carry an explicit model (31 October). Not TypeScript modules. |
| **L6** | Nothing merges without a test that would fail if it broke. | [Evidence, partial] Each tool has tests; CI runs on Linux, Windows and macOS; the brush codec has keyed-archive tests and fixtures. Not enforced as a merge rule. |

### Stack, drive layout and phase plan (SOURCE)
TypeScript, portable Node 22, Fastify, SQLite in WAL mode, brute-force cosine search, React with Vite, portable ollama.exe, Vitest with golden files, a thin `studio.exe`; drive layout with `kernel/protocol/`, `data/` for all mutable state and a read-only `reference/` of v1. Eight phases, each ending in a visible result or a failing test, starting with scaffolding and CI, then a portable kernel, the vault layer, a minimal protocol core, the first skill (the brush designer, rewritten, golden-file harness first), retrieval, the hardware gate, the remaining skills and the surfaces.
**STATUS [Evidence].** No `Studio-OS` repository exists among the repositories read. The studio lives inside ROSW and is built in Python, driven by Claude Code sessions, not by a local Ollama stack on a portable drive. [Not checked] whether the portable-drive version was started elsewhere. The brush tool did become the first end-to-end tool, as the plan specified, with its golden-style tests first.

### The three open decisions (SOURCE)
Model storage location (hard disk versus SSD), whether the 3.11 MB vendored design corpus carries over, and new repository versus a v2 branch (recommended: a new repository, Studio-OS). **STATUS [Evidence].** The studio went into the ROSW repository. [Inference] The ui-design plugin (`plugins/ui-design/`), with its search catalog and declared contract, is where design reference data lives; whether it is the same corpus as v1's vendored data was not checked. The model location question is moot unless the local-model design is revived.

---

## 5. Independent review: tensions (ANALYSIS and PROPOSAL, not project decisions)

| Tension | Reviewer's proposal (not adopted unless STATUS says so) | STATUS |
|---|---|---|
| **F.1** Zero network versus a mandatory git remote | Scope L4 to the execution data path; enumerate exemptions. | [Evidence] Resolved differently (declared egress per pipeline). |
| **F.2** Phase order contradicts "protocol follows the first skill" | Invert the phases, or declare Phase 3 a spike. | [Not applicable] The studio was built with the pipelines and spec growing together. |
| **F.3** L1 and L5 both own the routing table | Skills own manifests; the central definition is composed from them. | [Evidence] `spec.yaml` owns it and tests check the skills against it. |
| **F.4** TypeScript types erase at run time; the vault is untyped | A run-time schema that also validates notes, with types generated from it. | [Evidence, partial] `spec.yaml` plus content-lint checks on notes (for example flags CloudFront, Canva, Figma and Gamma links on 31 October); no generated types. |
| **F.5** Eviction law plus a spinning disk equals 60 seconds per call | A host cache tier with a strict portable mode. | [Not applicable] Models are cloud models, not local. |
| **F.6** Portable code, non-portable hardware policy | Separate workload taxonomy from host thresholds; probe a host profile. | [Evidence, partial] `machine.yaml` describes classes; the probe now reads discrete AMD, Arc and all adapters (31 October). It still describes one machine. |

## 6. Proposed improvements beyond the design (PROPOSAL), with status

| Proposal | What it said | STATUS |
|---|---|---|
| **G.1** Persist and hash the attestation | Record a content hash of every source at attestation time; produce a stale-artifact report when a gate changes. | [Not found] The attestation is persisted as a run file; hashing was not found. |
| **G.2** Version the brand gates | A superseded-by pointer; attestations cite a version. | [Not found] |
| **G.3** Provenance tiers | A, authored; B, confirmed; C, generated; only A and B vote toward L2. | [Evidence, partial] The `origin` field on vault works (`original`, `derived`, `auto-authored`; 1 November) separates what the owner wrote from generated work and limits the verbatim rule to originals. It is not wired into L2 voting. |
| **G.4** A parked queue with a lifecycle | Parked tasks as notes, retried when the named gate resolves, with a visible count. | [Evidence, partial] Parking exists and writes the blocker into the note; the hub shows runs. [Not found] automatic retry. |
| **G.5** Capability coverage manifest | Each capability declares previewed, export-only, unimplemented or unverified. | [Not found] |
| **G.6** Referential integrity | Immutable IDs for notes; a link check. | [Not checked] |
| **G.7** Conformance corpus | Snapshot the router's decisions on fixtures. | [Not found] |
| **G.8** Kernel security | A per-session token, path confinement, a privileged proxy. | [Evidence, partial] Host and Origin check on the hub, loopback binding, masked links in the Meshy ledger (31 October). |
| **G.9** Minimum honest system and a 30-day self-use gate | Use it for real work for 30 days before building more. | [Evidence, different shape] The owner's use of tools is documented in Part 3 (154 sessions in 30 days). The owner's measure is work done, not a gate. |
| **G.10** Do not rebuild the dashboard as a fixture | | [Evidence] The hub reads the vault and runs and "writes nothing but a new run". |

The risk register (Part H of the original) ranked scope exceeding capacity first. The owner's purpose (learn, prove, work done) reframes that risk: breadth is a fact about the work, not a failure.

---

## 7. Knowledge carried over from v1 (SOURCE)
The Content MD schema (never fabricate a timeline entry; rewrite next-steps in full); the ladder and mode gate; the gate laws (null-law, thermal-law, host-law, single-flight, and "an unverifiable gate is a closed gate"); the four workload classes sized for 16 GB; the Windows and WSL traps (the Linux memory-info file describes the VM, not the laptop; WSL gateway rewrite; Photoshop cannot open a WSL path; COM integrity levels); the plist UID defect ("do not reproduce it"); Procreate brush key names; the correct GIMP `.gbr` header; and DECISIONS.md entries 1 to 10.
The learning curriculum (16 topics in four tiers, from single source of truth to observability) and the five questions to ask of every piece of work (What test fails if this breaks? Where else does this value live? Show me it running. What does this not do? Is it reachable from a keyboard at 375 pixels?) are in the original.

---

## 8. What the original did not contain (limits)
The nine skills and the brand gates were never enumerated; the four workload classes were named only as a concept; the full Content MD schema and DECISIONS 1 to 10 were not reproduced; no dates were given; no code was reproduced. **STATUS [Evidence].** The studio's brand gates now live in `studio/vault/_Context/brand/` and are the author's; the spec lists the pipelines and stages; the studio vault has SCHEMA.md.

## 9. Where this fits
Part 2 covers every project and session to 18 October (updated edition). Part 3 covers 18 October to 17 November (the owner's personal details are omitted in this copy). The Phase 4 Planning document holds all proposals.



---

# DOCUMENT 2 OF 6

# ROSW Progress Report, Part 2 (updated edition)

**Where the work progressed from March to 18 October 2026, every project, and every recoverable Claude session in that period, with the corrections known on 17 November 2026.**
Original prepared 18 October 2026 for NotebookLM. Updated 17 November 2026 with the owner's Memory Log and the owner's statements of that day. Part 3 covers 18 October to 17 November; the Phase 4 Planning document holds all suggestions.

---

## 0. How to read this document

Statements are labelled [Evidence] when a record shows them, [Inference] when they are my interpretation, [Owner] when the owner said it on 17 November and it was not checked, and [Corrected] where this edition changes the 18 October text.

### Limits of the record
- **Sessions.** Drawn from the metadata of 89 Claude Code cloud sessions (title, date, model, origin, final status). Transcripts were not read. The earliest recoverable cloud session is 6 March 2026.
- **Repositories.** Six were read: Pipelines-Plugin (ROSW), Who-Did-It, The-Intern, Earth_Worldbuild, Strategy-Planner and Right-Door-Wrong-Exit. Others named in sessions (Claude-Code, Creative-Writing, Creative-Headquarters, Strategic_Planning, Art-Talk) were not readable. Creative-Headquarters was deleted on 1 October 2026 after migration; Art-Talk survives as a folder in Earth_Worldbuild.
- **[Corrected] The gap.** The 18 October text said no cloud sessions exist from 22 March to 21 August and inferred the work was "probably local or Claude was not used". The owner's Memory Log shows steady chat work in that window (a Procreate brush engine, the Creative OS charter, graduate and relocation dossiers, a Right Door prompt pack, NotebookLM corpora, research compendia). Cloud sessions simply do not show chat work. See Part 3 sections 3A and 3B.
- **Dates in git** can differ from session dates (merged PRs, rebased work). Counts are commits on default-branch history as cloned on 18 October.

---

## 1. Executive summary

Between March and October 2026 the work moved from small, single-purpose builds (a Procreate brush tool, a company website) to a connected system of tools that feed each other, then, in the last three weeks, to a fleet of parallel AI sessions building a multiplayer game against a written contract. What changed most is the unit of work: from one conversation producing one artifact, to a documented process (gates, contracts, decision logs) that many sessions can follow without the author in the loop.

- **Volume.** 89 recoverable cloud sessions: 4 in March, 8 in August, 23 in September, 54 in October (42 of them in the nine days from 10 to 18 October). Six repositories hold 469 commits (381 non-merge) across about 9,800 tracked files.
- **Progress is clearest in:** process design (pipelines, gates, contracts, decision logs); content at scale (a 63-work vault, about 2,200 world-building notes, 54 leader plans fact-checked); 3D and web delivery (a walkable museum, a continuous-walk game); and multi-session orchestration (up to 13 parallel build sessions per round, each ending in a merged PR).
- **Open items (stated as facts, not tests):** playtests were not yet written up in the repository (the owner has since reported 8+ playtests; see Part 3); finishing items on the laptop side; the same GitHub Pages 404 problem consumed five sessions; a large unverified-fact backlog (551 plan-review notes); and breadth (six active repositories plus earlier ones).
- **Three pivots:** (a) March to August, work in chat, then a restart on 22 August around a creative-writing vault; (b) late September, from one-off apps to shared tooling (pipelines, a plugin marketplace, a studio vault); (c) 10 October, from "Claude helps me build" to "Claude sessions are the team and I am the owner-orchestrator", with models assigned by task type.
- **[Corrected] Measure.** The 18 October text called real playtesting "the single most important open item" and framed the M3 "fun-or-stop decision" as a gate. The owner builds to learn, to prove and to get work done, and does not hold a fun-or-stop test (Part 3 section 1B). The facts about the playtest folder remain in section 4.2; they are not a pass-or-fail condition.

---

## 2. Recap of Part 1

Part 1 described the Studio Headless OS as a post-mortem and architecture: a creative engine that keeps workflow memory so that output is grounded in accumulated precedent. Key ideas: the Prime Rule (every skill gets resolved context), the resolution ladder (authored file, recalled decision, derived precedent, nothing), Content MD notes as the single source of truth, parking instead of waiting, v1's "duplication disease" (protocol kept in prose), and a clean-room rewrite under six laws. See the updated Part 1 for status.
[Evidence] The studio tool lives in Pipelines-Plugin (named ROSW on 29 September 2026). Its review document, `studio/docs/REVIEW.md` (28 September), records five reviewing lenses producing 59 findings, fixed the next day with a test file pinning each fix (68 of 78 new tests failed against pre-fix code, the proof that the tests catch what they should). Its `BASELINE.md` records measuring existing checks before adding anything: the ui-design plugin gate at 10 of 10 and 63 creative-writing tests passing before the studio was added.

---

## 3. Timeline: six phases

| Phase | Dates | What happened | Cloud sessions |
|---|---|---|---|
| **0. Early builds** | 6 to 21 Mar | Local Claude Code agent setup; a Procreate brush creation and editing tool (7 March, and a web-app version 21 March); the SSCC.inc fiber-optics company website. All on claude-sonnet-4-6, all started from the phone, all in one repo called Claude-Code. | 4 |
| **Chat period [Corrected]** | 22 Mar to 21 Aug | No cloud sessions, **but** chat work per the owner's Memory Log: Phase 1 foundations to 20 June (identity, Living Archive, concept projects, coursework, skill suite, Sinyal Terakhir); July reorientation (a Procreate brush engine with an NSKeyedArchiver builder, mentor cards); August academic dossiers, the Creative OS charter, the Right Door prompt pack. | 0 |
| **1. Restart: writing vault and a first game** | 22 Aug to 3 Sep | Right-Door-Wrong-Exit (a liminal "backrooms" click-through game) reviewed and rebuilt around a loading-screen loop. The Creative-Writing vault unzipped into a repo (63 works), then Obsidian and Ollama retrieval analysed (3 weaknesses, 4 ranked fixes). Strategy-Planner begins (54 Civilization VI leader guides). Creative-Headquarters app work, a skill-file assessment, an application remake review. | 11 |
| **2. Breadth and 3D curiosity** | 14 to 29 Sep | Mini-games planning; a first Blender render; Art-Talk (artist timeline, scope broadened to four domains, 53 profiles, 299 works, responsive redesign); Earth_Worldbuild (Earth Chronicle vault) gets a Pages site and a walkable 3D museum, then Xbox-controller support. First spend-limit hit recorded on 28 Sep. | 12 |
| **3. Convergence burst** | 30 Sep to 3 Oct | The densest four days. The-Intern (ninety-nine) goes through four PRs of game fixes in one day, then rebuilds as live 3D sets and one continuous walk. The Writing Museum built from the creative-writing vault with the studio's scene-3d pipeline. A Library explore page, GitHub Pages publishing, Strategy-Planner's cinematic redesign and 54 leader plans, Creative-Headquarters migrated and deleted. Five sessions fight the Pages 404. | 18 |
| **4. Tools consolidate** | 9 Oct | The Higgsfield generations library imported (every generation catalogued); the Who Did It multiplayer game plan session begins. | 2 |
| **5. Orchestrated fleet** | 10 to 18 Oct | Gemini-to-Blender integration and a Blender skills plugin (10 Oct), then Who Did It built by parallel sessions named A to Y, then 5A to 5M, one session per file-ownership slice, models assigned per task type. Five rounds in nine days, 144 commits. | 42 |

---

## 4. Project by project (state on 18 October, with later facts marked)

### 4.1 Pipelines-Plugin / ROSW (the hub)
One repository holding several self-contained tools: a creative-writing pipeline with its Obsidian vault (63 works, annotations, chunk tags, idea library), a studio tool with its own vault and checkpointed pipelines, a ui-design Claude Code plugin (search catalog, router, multipart sub-agents), a Blender plugin, a blender-gemini installer, a generations library and the Writing Museum. 1,536 tracked files (947 are WebP thumbnails), 64 commits from 27 August to 16 October.
**Progress [Evidence].** 19 Sep: vault tooling lands (frontmatter, annotations, chunk tags, idea library, pipeline skill) and a pipelines index eliminates all 33 orphan notes. 20 Sep: the ui-design catalog with a declared contract and a single verify gate; 26 Sep it is packaged as an installable plugin. 29 Sep: plot logic and registers added; the studio tool added; the repo named ROSW. 30 Sep (the biggest day): API keys moved out of the repo into `~/.rosw/keys.env`; the brand-gate pipeline; the studio hub; a Procreate brush packer; five connector pipelines; a compute gate; the Writing Museum and the scene-3d pipeline; ten museum scenes. CI on Linux, Windows and macOS with Python 3.10 and 3.13. 1 Oct: a library explore page and GitHub Pages publishing. 9 to 10 Oct: the Higgsfield library, blender-gemini, a Blender plugin installable through the marketplace, a render-pipeline skill and villager concept sync for Who Did It.
**Facts as of 18 Oct.** Documentation and tool count were growing faster than evidence of day-to-day use of each tool; the CLAUDE.md touched many subsystems. The Pages deployment source had to be changed by hand in GitHub settings, which an AI session cannot do. Two CLAUDE.md items remain "the author's call": pushing and tagging, and any use of the full Blender-code profile.
**Since [Owner, 17 Nov].** Railway and Pages are live; PRs #25 to #28 are merged; Meshy, ComfyUI (limited by the owner's computer lacking the GPU) and the Blender tools work; the video editor has been used and its publisher has not.

### 4.2 Who-Did-It (the then-current centre of gravity)
A browser multiplayer hidden-role game for 4 to 10 players: a static Phaser client on GitHub Pages, an authoritative Colyseus server, a pnpm monorepo. A short quick mode, "One Night Ultimate Baguette" (ONUB), shared the server. 144 commits in nine days (10 to 18 Oct), 288 TypeScript files, 65 numbered decisions, 50 Markdown documents.
**How it was built [Evidence].** A frozen master plan and GDD (10 Oct), then a coordination contract (`docs/SESSIONS.md`) assigning each parallel session the paths it may touch. Round 1 (A to D, plus E, a plan-mode session that decided 15 open questions): server, client, content, art pipeline. Round 2 (F to J): lobby and roles, movement, villager art, UI design system, studio project. Round 3 (K to Q): the kill-body-vote loop, audio, playtest kit. Round 4 (R to Y): quick mode, NPC fill, bots, CI soak. Round 5 (5A to 5M): ONUB v2 rules, isometric client, maps, avatars and covers, character and world art. Each round ends with an orchestrator integration pass recorded in DECISIONS.md.
**Progress.** M0 (scaffold), M1 (lobby and role cards), M2 (movement and the first house; a 30-minute soak with 229 portal crossings and no leaks), M3 (match flow, kill, bodies, clues, notebook, meeting, votes, win) and M3b and M3c (quick mode, NPC fill) merged. A real-server match test passed on the first merged tree. The server was configured for Railway and the published client pointed at it.
**Facts as of 18 Oct.** The `docs/PLAYTESTS` folder held a run sheet, a feedback form, a scorecard and a template; the M2 entry was a stub. The repository's M3 exit called for a recorded "fun-or-stop decision"; the owner does not hold that test [Corrected]. Several round-5 PRs were Review Ready or Blocked (5A, 5C, 5F, 5H, 5I, 5L; 5M waited on three answers; 5K was working). Open owner questions remained in DECISIONS (12 to 14), including saving Higgsfield's terms of service as a dated copy before concept images could return. Art masters (.blend, .glb) had to be copied by hand to the laptop's ROSW studio path. M5b (resources, mobs, quests) was already planned for round 6; the plan's own risk register (#4) names scope creep, which the owner's measure (work done) treats as a fact about growth, not a fault.
**Since.** 915 commits by 16 November; rounds 6 to 10, Story mode and a numbered "Session N" series (Part 3). [Owner] 8+ playtests with 2 to 5 people each.

### 4.3 The-Intern ("ninety-nine")
A static-web narrative game where an intern at a fake (low-poly) company works inside a real (photoreal) building; now one continuous first-person walk through live three.js rooms. 109 commits from 13 Sep (initial), 99 in October; 306 files (106 PNG, 42 MP4, 41 WAV).
**Progress [Evidence].** 30 Sep: four PRs in one day fixed video races, hold-to-run and spine logic, and added generative music and walkable rooms. 1 Oct: the AI-video and still pipeline was replaced with live 3D sets, and every set rebuilt in Higgsfield's 3D scene builder. 3 Oct: one continuous walk (rooms joined by doorways; choices made by walking into zones; no cuts). Then a polish-and-review cycle per scene (S0 street to S8 and the endings) with a "critic" step, and engine work (driven actors, out-of-view changes, light sync, ambient hum). A headless test suite and an A* autopilot play whole games.
**Facts.** Its docs say the Blender copies are stale until the Higgsfield rebuild tool learns doorways, floor heights and the polish builders. The CLAUDE.md lists protected files (reference stills, saved Blender output paths, the audio source of truth). Last commit 16 Oct. **Since:** it is now a door inside Look Over There (1 November), and a teardown was written for it (26 to 29 October).

### 4.4 Earth_Worldbuild (the Earth Chronicle)
An Obsidian world-building vault (eras, regions, entities, themes, timelines, sources, maps), a static site, a RAG index and a 3D walkable museum. 6,854 tracked files including 4,265 JPGs; 2,214+ Markdown notes. All 69 commits fall on 28 to 29 Sep.
**Progress [Evidence].** Briefs for Cultures (13 batches), Species and Technologies; a "site rewrite" executed as eight numbered waves of agents (batches 039 to 090, about 1,600 notes plus a cleanup pass, each wave committed as a checkpoint); the museum viewer (vendored Three.js r160), a Grand Hall hub with era doors, scene-per-room, real-size paintings and Xbox-controller support. Art-Talk (53 profiles, 299 works) lives here as Art-Talk-main. This is where the batch-and-checkpoint fan-out method was proven before it was used for games.
**Facts.** The repo went quiet after 29 Sep. [Inference] It became source material (the museum viewer was copied into the Writing Museum). No commits since.

### 4.5 Strategy-Planner (Leadership Focus)
A cinematic static codex of the 54 Civilization VI leaders: focus, power curve, history, kit, terrain, wonders, barbarians, an interactive plan tab per leader and a leader-match quiz. 43 commits, 31 Aug to 2 Oct; 482 files.
**Progress [Evidence].** 1 Oct: rebuilt as a cinematic codex; every leader plus all 37 natural wonders got a Wikimedia Commons image with licence credits. 2 Oct: all 54 plans written (in tranches of 13, 20, 9 and 11) and fact-checked against Gathering Storm; a validator script exists.
**Facts.** `PLAN-REVIEW-NOTES.md` holds a long list of unverified rules per leader (551 notes per the session summary), which need someone with the game open. One site-wide convention (governments as "wildcard" policy slots, 62 entries) was knowingly left. No commits since 2 Oct.

### 4.6 Right-Door-Wrong-Exit
A click-through liminal-space game: title card, loading clip, room video with typed caption, then (since 30 Sep) a first-person 3D walk to the room's exit. 40 commits, 28 of them on 22 to 25 Aug. Smallest repo (51 files).
**Progress.** Aug: asset-path fixes, a loading-screen loop, per-section audio, a skip tab. 30 Sep to 3 Oct: first-person 3D rooms and stairwell, animated rooms, mini-games and room-only item piles in three rooms (PR #11, merged 9 Oct).
**Facts.** The PR #11 summary said four rooms and old seams remained open; the 30 Sep room-refinement session ended Failed. It is a testbed that fed techniques (walk scenes, mini-games) into The-Intern. **Since:** a door inside Look Over There (1 November).

---

## 5. Claude usage: what the 89 sessions show

### 5.1 Counts
| Month | Sessions | Notes |
|---|---|---|
| March 2026 | 4 | All claude-sonnet-4-6; all from iOS; one repo (Claude-Code) |
| April to mid-August | 0 | Cloud sessions only; chat work not visible here [Corrected] |
| August 2026 | 8 | From 22 Aug. Sonnet-5 and Opus-5 (4 each) |
| September 2026 | 23 | First Fable-5-1 sessions (10 of them), the 3D museum, the Intern game |
| October 2026 (to 18th) | 54 | 40 of them on 10 to 18 Oct, mostly parallel fleet sessions |

| Model (configured) | Sessions | Typical use [Inference from titles] |
|---|---|---|
| claude-sonnet-4-6 | 4 | March small builds |
| claude-sonnet-5 | 12 | Docs, HTML, design redesigns, debugging |
| claude-opus-5 | 7 | Repo analysis, migration plans, application review |
| claude-fable-5-1 | 21 | Large reasoning-heavy tasks: 3D museum, game architecture, UI design system, planning |
| claude-opus-5-5 | 16 | Art direction, asset pipelines, content data, decisions, the Opus slice of each fleet round |
| claude-sonnet-5-5 | 29 | Bulk implementation (server, client, tests, CI) |

| Where the session started | Sessions |
|---|---|
| Spawned by another session | 38 |
| Desktop app | 28 |
| iOS (phone) | 15 |
| Claude Code CLI | 8 |

| Final status (at 18 Oct) | Sessions |
|---|---|
| Completed | 75 |
| Review ready | 6 |
| Failed | 4 |
| Working | 2 (including the Part 2 session) |
| Blocked | 2 |

**Failures and limits [Evidence].** The four Failed sessions: "Museum walkthrough refinement" (28 Sep; ended with a monthly spend limit message), "Room refinement and video animations" (30 Sep), "GitHub Pages file not found" (1 Oct) and "Game scene polish and mechanics" (3 Oct; ended with a session limit message). Two of four were usage-limit stops.
**Context size.** Where recorded, finishing context of non-fleet sessions ranged from about 100,000 to 600,000 tokens (artist timeline 603k; 3D museum 558k; dining-room 3D 571k; world art 5K 576k). Fleet sessions mostly ended between 100k and 470k. [Inference] The largest sessions are the most exposed to limits.

### 5.2 Eight recurring paths [Inference from titles]
- **A. Knowledge vaults:** unzip and add files; MD migration gap analysis; Obsidian and Ollama; leader Markdown; artist timeline; broadening artist scope. Turn source material into linked, searchable, fact-checked notes, then add retrieval.
- **B. Pipelines and gates:** Creative-Headquarters migration; skill file assessment; application remake review; Library explore; Creative HQ deletion. Move from ad hoc prompting to checkpointed pipelines with approvals, specs and tests.
- **C. Web delivery:** HTML and navigation JS; HTML redesign; taskbar shortcut; 404 error x5; GitHub Pages build error. Static sites, responsive design, repeated fights with the Pages source setting.
- **D. 3D and walkable worlds:** Blender render; 3D museum; Xbox controller; 3D dining room; 3D scenes from the vault; 3D game environment with Higgsfield.
- **E. Games:** interactive loading screens; mini-games plans; game bugs; choice logic; hold to run; scene polish; the Who Did It plan.
- **F. Strategy and reference data:** leader strategy guides; Civilization profiles redesign.
- **G. AI media tooling:** import Higgsfield assets; Gemini-Blender integration; Blender skills plugin; re-render calibration.
- **H. Orchestrated fleets:** WDI A to Y and 5A to 5M. One orchestrator, many scoped sessions, a coordination contract, per-round integration and a decision log.

---

## 6. How the paths converge [Inference]
- **One method:** resolve context, then act, then record. The vault CLAUDE.md, the studio's Prime Rule and ladder, Who Did It's GDD-is-source-of-truth rule and The-Intern's Canon (C1 to C8) are the same move: write the rules down once, make every later action cite them, let tests check that documents agree.
- **One content spine:** the 63-work vault becomes the source of the Writing Museum (ten rooms built through the scene-3d pipeline). The Earth Chronicle's museum viewer seeded the Writing Museum's viewer, which Who-Did-It's CLAUDE.md names as the candidate seed for its V2 first-person renderer.
- **One art pipeline:** Higgsfield (generation) plus Blender plus a library that catalogues every generation (cited by id in Who Did It's CREDITS). Masters stay on the laptop under `studio/assets`; repos keep manifests and hashes.
- **One delivery path:** static sites on GitHub Pages with a small hosted server only where multiplayer needs one.
- **One operating model:** Earth_Worldbuild proved batch fan-out (eight waves, checkpoint commits); The-Intern used per-scene polish branches with a critic review; Who Did It generalised it into a numbered-session fleet with file ownership, a coordination contract and an orchestrator integration step.
- **One tooling layer:** ui-design, the Blender and blender-gemini plugins, the studio skill and the marketplace file turn each hard-won workflow into something a later session can install.
**The greater picture [Inference].** A personal creative studio in which writing, worldbuilding, 3D scenes, art and games are produced through documented, repeatable pipelines, with Claude doing the volume work and the author owning the decisions, the taste gates and the go-ahead. The repositories are the products; the pipelines are the product that makes the products. [Corrected] The Memory Log adds the owner's own statement of purpose: build to learn, build to prove, and measure work done.

---

## 7. Trajectory
| Dimension | March to early Sept | Late September | October |
|---|---|---|---|
| Unit of work | One conversation, one artifact | One session, one repo feature, merged PR | One scoped session in a numbered fleet, inside a contract |
| Who coordinates | The author, in the chat | The author, across a few repos | An orchestrator session plus the author's decision log; sessions spawn sessions (38 of 89) |
| Quality control | Manual checks | Reviewer lenses, fact-check passes, verify gates | CI on three OSes, soak tests, bot swarms, critic reviews, adversarial plan reviews |
| Model use | One model (Sonnet 4.6) | Sonnet-5 and Opus-5 for routine work, Fable-5-1 for heavy ones | Sonnet-5-5 for implementation, Opus-5-5 for art and decisions, Fable for UI design |
| Scope | Single tool or site | Several parallel projects | One flagship (Who Did It) plus the shared tooling it draws on |
| Where it starts | Phone (iOS) | Desktop app and CLI | Mostly spawned sessions; phone sessions for review and fixes |
| Risk handled | Does it run? | Is it true? Is it licensed? Is the key outside the repo? | Does it leak a secret role? Is the tick budget safe? Is the privacy invariant tested? |

**The three pivots.** (1) 22 Aug: restart on a creative base, two fronts at once (a creative-writing vault and a playable media game); the vault imports 63 works and immediately questions its own retrieval. (2) 19 to 30 Sep: from projects to a platform; the Pipelines repo is initialised, the vault merged in, ui-design becomes a plugin, the studio and its gates arrive, keys leave the repo, and a Creative-Headquarters migration and deletion closes the older structure. (3) 10 Oct: from builder to orchestrator; the 9 Oct plan produces a master plan, GDD and the SESSIONS.md contract; the author's role shifts to deciding open questions.
**What did not change.** Games remain the target form; static, no-build web delivery remains the default; decisions are recorded with dates; generated work is labelled as such.

---

## 8. Where progress is strongest
- **Process engineering.** Specs read by code, gates that refuse, tests that check documents agree with code, decision logs with IDs. The studio review (59 findings, all fixed with pinned tests) is the clearest example.
- **Throughput with control.** 144 Who-Did-It commits in nine days, four fleet rounds, each with an integration log; merges done "with only doc unions" and green lint, typecheck and unit suites on the merged tree.
- **Privacy and fairness by construction.** No field a client receives may reveal a role, cover or NPC seat; tests prove it; secret and public random streams are separated.
- **Content at scale with provenance.** Image credits with licences for 54 leaders and 37 wonders; CC0-by-default asset policy with a CREDITS row for any exception; Higgsfield generation ids cited.
- **3D delivery.** A walkable museum with controller support, ten literary rooms, and a continuous-walk game with an autopilot that plays whole games in headless tests.
- **Security hygiene.** API keys moved out of the repo; tests compare key names, not values; connectors listed per pipeline; telemetry disabled in the Blender plugin.

---

## 9. Open items as of 18 October (evidence only; actions are in the Phase 4 Planning document)
| # | Area | Evidence | Status on 17 Nov |
|---|---|---|---|
| 1 | Playtests | PLAYTESTS held templates and an M2 stub; owner prerequisites (Railway, VITE_SERVER_URL, form, scorecard) outstanding. | [Owner] 8+ playtests run; unrecorded in the repo. Railway and Pages live. |
| 2 | Integrating round 5 | Six round-5 sessions Review Ready, two Blocked or Working; 5M waited on three answers. | Superseded by rounds 6 to 10 (Part 3). |
| 3 | Breadth | Six active repos plus earlier ones; Right Door and Earth_Worldbuild idle; the Intern's Blender copies stale. | More repos added in November. |
| 4 | Deployment repeatability | Five sessions (28 Sep to 2 Oct) on the Pages 404 and source setting. | [Owner] Pages live. The workflow warns and skips when the source is wrong (23 Oct). |
| 5 | Usage limits | Two of four failed sessions ended on a spend or session limit; several sessions exceeded 450k tokens. | Seven later failures were re-run on Opus (Part 3). |
| 6 | Laptop-side hand-offs | Repeated "copy these .blend/.glb masters" and "move the brush designer" notes at session ends. | Still applies. |
| 7 | Unverified facts | 551 plan-review notes in Strategy-Planner; vault fact-check batches. | Unchanged. |
| 8 | Licensing and terms | Open question 13 (Higgsfield terms as a dated copy) and two concept images held back. | Not checked. |
| 9 | Scope | M5b planned; the plan's own risks #4 and #15. | M5b shipped; see Part 3. |
| 10 | Documentation load | Long CLAUDE.md files; stale areas flagged in The-Intern. | Still applies. |

---

## 10. Questions to ask NotebookLM
- Which projects share assets, code or methods, and what is the single most reused idea?
- Build a timeline of the decisions that changed direction (the three pivots) and what triggered each.
- Where did usage limits or repeated errors (the Pages 404) appear, and what do those episodes have in common?
- Compare the March builds with the October fleet: what skills were gained between them?
- Which of the six repositories were active on 18 October, and which were not?

---

## Appendix A. Full session ledger (89 cloud sessions, to 18 Oct)

**March (4, sonnet-4-6, phone, all Completed):** 6 Mar Set up Claude code agents locally; 7 Mar Build Procreate brush creation and editing tools; 7 Mar Build SSCC.inc fiber optics company website; 21 Mar Procreate Brush Designer Web Application.

**August (8):** 22 Aug Repo strengths and improvements (sonnet-5, phone); 24 Aug Interactive loading screen sequence (opus-5, phone); 27 Aug Unzip and add files (opus-5, phone); 27 Aug Creative-Writing MD migration gap analysis (opus-5, desktop); 27 Aug Obsidian and Ollama integration (opus-5, desktop); 31 Aug Leader Markdown documentation (sonnet-5, desktop); 31 Aug HTML and navigation JavaScript (sonnet-5, CLI); 31 Aug Ollama library HTML pages (sonnet-5, CLI). All Completed.

**September (23):** 1 Sep Taskbar shortcut for application (opus-5, CLI); 1 Sep Skill file assessment (opus-5, CLI); 3 Sep Application remake technical review (opus-5, CLI); 14 Sep Folder checkout, a PC-named session, Mini games plans (sonnet-5, CLI); 16 Sep Blender render (sonnet-5, desktop); 25 Sep Artist timeline design (opus-5-5, desktop); 26 Sep Broadening artist scope, HTML redesign with responsive design (sonnet-5, desktop); 28 Sep Handoff checklist review, 404 error investigation (sonnet-5, desktop); 28 Sep 3D museum walkthrough (fable-5-1, Completed); 28 Sep Museum walkthrough refinement (fable-5-1, **Failed**); 29 Sep Bluetooth Xbox controller museum navigation (fable-5-1); 30 Sep 404 error on site run (sonnet-5-5); 30 Sep Game bugs and scene revisions, 3D dining room scene with mobile optimization, Games choice logic and video playback, Creative-Headquarters migration plan, Hold to run video loop bug (all fable-5-1, desktop, Completed); 30 Sep 3D scenes from creative writing vault (fable-5-1, phone); 30 Sep Room refinement and video animations (fable-5-1, **Failed**).

**October 1 to 9 (12):** 1 Oct Civilization profiles interface redesign, 3D game environment with Higgsfield scenes (fable-5-1, desktop); 1 Oct Library explore page, Leader-specific strategy guides, Creative headquarters deletion (fable-5-1, phone); 1 Oct GitHub Pages file not found (fable-5-1, phone, **Failed**); 2 Oct GitHub Pages build error, 404 error fix options (fable-5-1, phone); 3 Oct Game scene polish and mechanics (fable-5-1, desktop, **Failed**); 3 Oct Interactive 3D scenes and room-specific items (opus-5-5, desktop); 9 Oct Import Higgsfield assets to AI library (opus-5-5, desktop); 9 Oct Who Did It multiplayer game plan (fable-5-1, desktop, **Blocked**).

**October 10 to 18 (42):**
- 10 Oct Gemini-Blender API integration, Blender skills plugin (sonnet-5-5, desktop); Re-render calibration sheet with ramp fix (opus-5-5, desktop).
- 10 Oct Who Did It round 1 and 2, spawned: A server and shared (Sonnet); B client and Pages (Sonnet); C content data and rules JSON (Opus); D art direction and asset pipeline (Opus); E decide the 15 open questions (Opus, plan mode); F M1 finish, shared protocol and Start deals roles (Sonnet); G M2 movement, scene sync and the first house (Sonnet); H villager character art through the render rig (Opus); I UI design system, role cards, lobby and HUD (Fable); J who-did-it studio project in the ROSW repo (Sonnet). All Completed.
- 16 Oct round 3 and 4, spawned, all Completed: K match flow, meetings, votes, win; L kill, bodies, clues, Notebook; M meeting, game over, chat, theme screens; N world actions, clues, HUD theme; O bots, match e2e, soak (all Sonnet); P art, props, clues, VFX, body sprite; Q playtest kit, audio, copy deck (Opus); R quick mode server; S NPC fill server; T quick mode client world; U quick mode meeting and end; V lobby, settings, network edge; W bots, e2e, soak, CI (Sonnet); X art, bakery, loft, placeholders; Y content, copy, audio, playtest kit (Opus).
- 18 Oct round 5, spawned: 5A ONUB v2 rules, server deal and prep (Review Ready); 5B server night and morning (Completed); 5C client prep, mini-games, deck editor (Review Ready); 5D client night, morning and results (Completed); 5E bots, NPC brains, e2e and soak (Completed); 5F avatars, public looks, covers, Impersonate (Review Ready); 5G main deck and Werewolf roles (Completed); 5H NPC routines and fixes (Review Ready); 5I isometric client and lighting (Review Ready); 5J maps, Opus (Completed); 5K world art, Opus (Working); 5L character art, Opus (Review Ready); 5M ONUB art, Opus (Blocked). Sonnet slices: 5A to 5I; Opus slices: 5J to 5M.
- 18 Oct Progress report part 2 and Claude usage patterns (sonnet-5-5, phone, Working).

## Appendix B. Sources and method
Git history, README, CLAUDE.md and docs of the six repositories read; metadata for all 89 Claude Code cloud sessions (title, creation date, model, origin, final status, final summary line); on 17 November, the owner's Memory Log and statements. Transcripts and chats were not read. Counts are from the cloned default branches on 18 October. Model names are the configured model at session creation.



---

# DOCUMENT 3 OF 6

# ROSW Studio Progress Report, Part 3

**Where the studio stands, 18 October to 17 November 2026.**
Prepared 17 November 2026 for NotebookLM. Part 1 covered the Studio Headless OS post-mortem and architecture. Part 2 covered every project and every recoverable session from March to 18 October. Part 3 treats ROSW as one studio: a hub repository (Pipelines-Plugin, named ROSW) that holds the tools, plus the product repositories that the tools feed. It covers the 30 days since Part 2.

---

## 0. How to read this document

**This is one of five documents.** Part 1 (updated edition) covers the Studio Headless OS design and its status. Part 2 (updated edition) covers March to 18 October, every project and session. This Part 3 covers 18 October to 17 November and holds the owner's full portfolio (section 3B; personal details omitted in this copy). The Phase 4 Planning document holds all proposals, and the Skillification Plan sets out how to turn everything into repeatable skills. Part 3 does not repeat the full detail of Parts 1 and 2; it recaps them in section 2 and corrects them in section 12.

Statements are labelled **[Evidence]** when a record shows them (a commit, a file, a session title or status) and **[Inference]** when they are my interpretation. Please keep that distinction when asking NotebookLM questions.

### Limits of the record
- **Session transcripts were not read.** For sessions I have only the title, date, origin, final status and sometimes a one-line summary. What was built comes from the repositories, which is more reliable.
- **Commit dates are not a clean activity log.** Who-Did-It has 915 commits in total, but the commits dated 18 to 28 October are almost absent, even though about 90 sessions ran then. [Inference] Work was probably merged and re-dated at integration passes (many commits fall on 29 to 30 October). Use session dates for "when was work done" and commit dates only for "when did it land".
- **Counts come from the clones in this session.** Sessions: the account list returned 154 sessions created from 18 October to 17 November. Older sessions exist beyond the page I read, so the all-time total is roughly 240 (89 from Part 2 plus these), not an exact figure.
- **Chat history is now partly covered.** The owner supplied a "Memory Log: Phases 1 and 2, March to November 2026" (dated 17 November) that summarises claude.ai chat work, which cloud sessions never show. It is a summary written from chat history, not the chats themselves, and it says that chats inside Projects (Songs, CIV VI, Creative Headquarters and others) were not searchable. Section 3A uses it. Personal information and the full project list from it are in section 3B.
- **Owner-supplied facts (17 November).** After the first draft the owner confirmed: humans have played Who Did It at least 8 times, at almost every update; PRs #25 to #28 are merged; Railway and GitHub Pages are live; Meshy, ComfyUI and the Blender tools work (ComfyUI only through a connection, because the owner's computer lacks the GPU); the video editor has been used but its publisher has not. These are the owner's word and are marked as such. I could not check any of them from this session.
- **Not readable here:** the author's laptop (art masters, Blender), the playtests themselves and the live Railway service, and the Creative-Headquarters, Claude-Code and Strategic_Planning repositories.
- **I did not verify that anything runs live.** Where a repository's CLAUDE.md still says an integration has "never run", the owner has since reported otherwise (see the owner-supplied facts above); those repository statements are out of date, not wrong at the time.

---

## 1. Executive summary

*This report records what happened and what the evidence shows. All fixes, suggestions and proposals have been moved to a separate document, "Phase 4 Planning".*

In one sentence: **in the last 30 days ROSW stopped being a place where tools were built and became a shelf of tools that the games draw on, while almost all of the actual work volume moved into game repositories run by large numbered fleets of sessions.**

- **Volume [Evidence].** 154 sessions in 30 days, against 89 in the whole of March to 18 October. 144 completed, 7 failed, 1 blocked, 1 ready for review, 1 working (this one). 120 were spawned by another session. The busiest days were 22 October (19 sessions) and 23 October (30 sessions).
- **ROSW itself [Evidence].** 133 non-merge commits between 21 October and 3 November, then nothing for two weeks. In that burst: a 3,577-item sound library, a 990-brush Procreate catalog with a new byte-exact codec, a teardown plugin (udgt) used on three games, an imported internet-reading base (agent-reach), a video-editor plugin, a graphic-design plugin, a full audit and roadmap, and a four-lane hardening pass.
- **Products [Evidence].** Who Did It grew from 144 to 915 commits through rounds 6 to 10, a Story mode and a numbered "Session N" series. Three new repositories appeared: **Look Over There** (a multilevel Backrooms game, 227 commits in 16 days), **esc-ZINE99** (designs, data, art and web modules for ten games adapted from the creative-writing vault, 50 commits in two days) and **gamechat** (a private voice and video app, v2.2.0). A fourth, **Juniper-Collective**, is a static advisory-firm site.
- **Playtests have happened and are not a pass/fail test.** The owner reports that humans have played Who Did It at least 8 times, with 2 to 5 people each time, at almost every update. The owner's observation: the game is fun, it makes people laugh and it has come a long way, but the gameplay still lacks a repeating enjoyment, and it is hard to tell novelty from a good game. **The owner does not hold a "fun or stop" test.** The repository's own planning documents do (the M3 exit in `ROADMAP.md`, `MASTER_PLAN.md` and `docs/PLAYTESTS/`), and that conflicts with the owner's stated purpose in section 1B. The repository still holds only a playtest stub (`2026-xx-xx-m2.md`), a run sheet, a form and a scorecard, so the playtests themselves are not recorded.
- **The chat record changes the picture of the "gap".** Part 2 inferred the March to August silence meant no Claude use; the owner's Memory Log shows steady chat work in that window (a Procreate brush engine, the Creative OS charter, dossiers, a Right Door prompt pack). See section 3A. Chat is where designs start; cloud sessions and repos are where they are built.
- **The owner and the whole portfolio are part of the record.** Section 3B holds the owner's domains, protocols and the projects named in their Memory Log, studio and non-studio alike (personal details are omitted in this copy). The owner never withholds that work was made with AI, and treats dislike and envy as fuel.
- **The clearest new signal about method.** All 7 failed sessions came in the 23 and 24 October round, and all 7 were re-run the next day on Opus with the same task name. That is the first documented use of "retry on a stronger model" as a routine.

---

## 1B. Why the owner builds (owner's words, 17 November)

The owner asked that the reports not measure the work by a "fun or stop" test. These are their stated purposes, in their own terms, condensed:

- **Build to learn.** Who Did It "will always be a win" in the owner's mind. This is not about what other people understand or enjoy about the creations. The same mechanics behind a game are used differently in finance, education and other applications, so building a game teaches transferable systems.
- **Build to prove.** The first proof was a pitch document that a human could read and judge a good idea. That showed the AI was not approving the owner's ideas whatever their quality, but helping to create ideas other people liked.
- **Measure work done, not whether it is good.** The owner cares about what work is actually getting done. "Good" describes only a finished thing.

**The owner's account of playtests.** Everyone loves a good idea, the owner says, and most people are jealous of a good build. They have run 8 games with 2 to 5 people each. Every time, they report unfair criticism and a real lack of honesty about the enjoyment of the game, and most people cannot get past "you just used AI", as if the owner had done nothing to create the games. **The owner says this applies to the gameplay itself, not only to opinions about it:** some friends refuse to allow themselves to have fun because it is AI, and treat anything as "slop" no matter the level of detail or the hard work behind it.

**What this changes in this report.**
- The report treats the volume and kinds of work done (sessions, commits, tools, systems, projects) as the primary evidence of progress, since that is the owner's measure.
- The owner's playtest observations (fun, laughter, missing repeat enjoyment) are recorded as observations, not as a verdict or a gate.
- Where earlier parts and the repositories describe a "fun-or-stop" decision, this report notes it as a conflict with the owner's purpose, not as an open item to satisfy.
- Playtest feedback is a weak signal about the game, because a player's attitude to AI can decide whether they let themselves enjoy it at all (the owner's account above). [Inference] The AI attitude is a confound on the enjoyment signal, which fits the owner not using playtests as a score. It also means the "fun, laughs, missing repeat enjoyment" observation comes from a mixed group, some open to the game and some not, and cannot be read as one measurement.

---

## 1A. The owner's three bottlenecks (added after listening to the report)

After hearing this report read aloud, the owner named the three problems they have faced head on. The framing below is the owner's; the evidence mapping is mine and is labelled. Proposals for each bottleneck are kept out of this report and live in the separate Phase 4 planning document.

| # | Bottleneck (owner's words, condensed) | What solved or is solving it |
|---|---|---|
| 1 | **Human speed limit.** The first bottleneck was how fast the owner's typing speed could increase. | The swarm: many parallel sessions instead of one fast typist. |
| 2 | **Swarm organization and user dependencies.** Once the swarm existed, the problem became organization, tool access, context configuration and management, and overlapping work when two or more agents get the same task. | Contracts, file ownership, orchestrators, hooks and scoped tools. Partly solved. |
| 3 | **Human context limit.** How can one human manage the current output while staying on top of everything, and respond as a real pivot point instead of an observer? | Not solved. This is the current problem. |

### How the record fits each one [Evidence for the facts; Inference for the reading]
**1. Human speed limit.** The March to August record is chat and phone work (every March session started on the phone; the Memory Log shows one-conversation, one-artifact work). The jump to 89 sessions by 18 October, then 154 in the next 30 days, with 78% started by another session, is the swarm replacing the typist. The owner's essay "Stop Asking For It, Ask For What It Takes" names "just me and AI" as the unacknowledged prerequisite; the swarm is that prerequisite at scale.

**2. Swarm organization.** Every item the owner lists has a visible artefact:
- **Organization and overlap:** `docs/SESSIONS.md` gives each session the paths it may touch; numbered rounds and slices (6A to 10Y); an orchestrator session (6Z); a merge queue (7 November) and "five skipped PRs" cleanup (7 November). The 7 failed round-8 sessions were re-run on Opus the next day, which is the same task assigned twice on purpose. Whether unplanned double assignment happened is not visible in the titles, but the owner says it did, and the contract and merge queue exist to prevent it.
- **Tool access:** scoped `allowed-tools`, hooks that ask before editing an original or publishing, pinned tool versions, tools shipped off by default, MCP install and Blender tool setup sessions.
- **Context configuration:** per-repo compaction windows (400k in ROSW; 300k, 500k and 800k tiers in Who Did It, chosen by kind of work), a "Session autocompact strategy" session (29 October), a model assigned per agent and per task type.
This is the most engineered of the three layers.

**3. Human context limit.** This is the bottleneck the record shows most clearly and least solved:
- **Output outruns review.** 154 sessions in 30 days against one human; peak of 30 sessions in a day (23 October); at one point four hardening PRs sat unreviewed for days; one session is "review ready" and one "blocked" right now.
- **What the owner has learned lives in their head, not the repo.** The 8+ playtests and what they showed were never written down. While that stayed unrecorded, the swarm kept adding scope (Story mode, vendettas, economy, overworld, city, three new repos). That is the observer failure mode in practice: output keeps flowing while what the human has seen and decided is not captured anywhere the swarm can read.
- **Stale statements.** READMEs and CLAUDE.md lines that no longer match reality (for example "nothing is built yet", "never run") show documentation also falling behind the human's own awareness.

### The owner's partial fix: the questionnaire docs [Evidence from Who-Did-It; owner named it as their most recent partial fix for bottleneck 3]
**What they are.** Planning sessions end by writing a questionnaire for the owner instead of deciding. Two are in the Who-Did-It repo: `docs/round11/questions.md` (22 questions from sessions 11A and 11B, about the art makeover) and `docs/story/questions.md` (17 questions, written 6 November after four Story chapters shipped).
**How they are built.**
- Every question has a **proposed default** and says where the answer lands. The owner answers **default** or **different**, with a note in their own words.
- A question left unanswered takes its default and is marked *proposed*, so the swarm is never blocked waiting.
- Questions that two planning documents both asked are asked once and name both sources; where the documents disagreed, the question says so.
- Nothing outside the planning folder changes until the owner approves the plan.
- Answers were collected in a form (a saved page) and written back to the repo as `docs/round11/owner-answers.md`, which "wins over" the planning documents wherever they disagree.
**What the record shows.** The owner answered all 22 round-11 questions in the form between about 01:28 and 03:37 UTC on 30 October (roughly two hours), **21 by default and 1 different** (a taste call about building shadows, quoted verbatim). The plan was approved the same day.
**Reading [Inference].**
- This is a working decision inbox: a bounded list, options with a default, a recorded answer, and no blocking. It converts "observer" into "pivot" by making the human's role a short list of choices.
- It fits the Part 1 principle that the work stops but the system does not.
- 21 defaults out of 22 can mean the proposals were good, or that defaults are easy to accept. The record cannot tell which. The single different answer was a taste question, which suggests where the human's judgement actually changes the outcome.
- **Gaps.** The questions are ordered by topic, not by consequence, so a choice that shapes scope (for example the Meshy licensing question, SC2) sits beside minor ones. The format covers design decisions; it is not yet used to capture what the owner learned from observing play (the playtests), or the owner's own scope calls. Those need a different kind of question: ones the owner answers from what they saw, not from reading a proposal.

[Inference] The three problems are the same problem at different scales: each fix moved the constraint to a smaller, harder place (fingers, then coordination, then attention).

---

## 2. Recap of Parts 1 and 2 (so this document stands alone)

- **Part 1:** the Studio Headless OS idea. Output should be grounded in accumulated precedent, not model guesswork. Core laws: the Prime Rule (no skill runs without resolved, attested context), the resolution ladder (authored file, recalled decision, derived precedent, nothing), parking instead of waiting, Content MD notes as the only memory, and the diagnosis that version one failed because its protocol lived in prose that code was trusted to obey ("duplication disease").
- **Part 2:** six repositories, 89 sessions, three pivots (restart on a creative base in August; from projects to a platform in late September; from builder to orchestrator on 10 October). Open items: real playtesting, integrating round 5, finishing before starting, repeatable deployment, usage limits, laptop-side hand-offs, unverified facts, licensing, scope discipline, documentation load.

---

## 3. What ROSW is now: the studio map

ROSW is a single repository (`Pipelines-Plugin`, 319 commits, 5,267 tracked files as cloned) that holds self-contained tools. Its CLAUDE.md lists them. For this report I group them by job.

| Job | Tool | State on 17 Nov [Evidence unless marked] |
|---|---|---|
| **Make writing** | creative-writing pipeline + vault | 64 works recorded. 59 are marked `origin: original`; 4 are derived (archetype profiles); the rest are `auto-authored`. The "verbatim, never edit" rule now covers only originals. The Who Did It lore (about 75 later works) was written in eight waves on 23 and 24 October. |
| **Make things** | studio (vault, pipelines, hub, brand gates) | Checkpointed pipelines with go-ahead, parking and `keep`. Added `asset-3d` (Meshy) and `assemble-3d` (Blender) on 29 October. Hardened by "Wave 1 lane A" on 31 October. |
| **Catalogue what was generated** | studio/library | 1,272 Higgsfield generations catalogued; 215 added on 23 October. |
| **Catalogue sounds** | sound-library | 3,577 items by 17 November, ingested in about 20 commits on 21 and 22 October (categories such as impacts, braams, risers, sci-fi ambience, cars, weapons). Originals live in GitHub Releases, not in git. |
| **Make brushes** | brushes/ | Catalog of 990 brush records, a byte-exact Procreate codec, search engine, vault, MCP server, tagger and librarian agents, designer app (30 October). Replaces the studio's old brush packer. **Owner reports it works in Procreate and Photoshop** (17 Nov; the owner's own testing, not checked here). |
| **Understand a game** | udgt plugin + `teardowns/` | A teardown engine that maps every design choice to its decision, section, data, code and history, and records the owner's answers verbatim. Run on Who Did It (stages 0 to 8, 23 October), Right Door, Wrong Exit (0 to 6, 25 October) and Ninety-Nine (0 to 8, 26 to 29 October). |
| **Read the internet** | agent-reach base + reach plugin | Imported on 29 October with `reach-setup`, `reach-connect` and two toolsets (`reach-research`, `reach-references`). Read-only by rule. |
| **Make video** | video-editor plugin | Moved in from its standalone repo on 29 October. **Owner reports the editor has been used; `ve publish` has not** (dry-run and private by default; never run against a live account). |
| **Make 3D** | blender plugin, blender-addons, blender-gemini, ComfyUI client | 81 add-on tools shipped disabled. Versions of `mcp-for-blender` (2.2.6) and `gemini-mcp-tool` (1.1.4) pinned. ComfyUI (Trellis 2 / Pixal3D) client: the repo's own tests use only a fake server. **Owner (17 Nov): Meshy, ComfyUI and the Blender tools work, and the Blender tools made a large difference to Claude's capability; ComfyUI is limited by this computer's lack of a GPU and the cloud version is unused.** |
| **Make graphic design** | graphic-design plugin | Added 1 November: catalog, SVG lint, print preflight, render helper and tool router. |
| **Make UI** | ui-design plugin | Unchanged in role. Skills were split into `references/` and the trigger narrowed on 31 October. |
| **Show it** | Writing Museum, docs pages | Pages workflow now skips the deploy with a warning when the Pages source cannot be switched (23 October). |

[Inference] The tool list has grown past what one person can use day to day. The roadmap itself says so, and the section 8 table treats this as a risk.

---

## 3A. What the chat record adds (work that cloud sessions do not show)

Part 2 listed a five-month gap (22 March to 21 August) and said work in it was "probably local or Claude was not used". **The Memory Log shows the work was happening in claude.ai chat.** This corrects that inference. All items below are [Evidence] from the owner's own log unless marked.

### What ROSW means
ROSW is **Resonant Origins Studio Works LLC** (Wyoming, pronounced "Rose"), the transactional entity. **Resonant Origins** is the body of work. The repository named ROSW on 29 September takes its name from the company. The log names five domains: **The Hand** (making), **The World** (research), **The Machine** (infrastructure), **The Standard** (frameworks and writing) and **The School** (teaching). [Inference] The "studio" in this report maps mainly to The Machine, and the repositories are its output; The Hand and The World explain why creative-writing, brushes and worldbuilding sit beside the engineering tools.

### Timeline additions (chat, not cloud)
| When | Work in chat |
|---|---|
| March (first session about 7 March) | A meta-critique of the collaboration. Two rules came out of it: concepts are the deliverables, and Claude is an equal thinking partner who pushes back. The name Resonant Origins was revealed on 7 March. |
| March to June 20 (Phase 1) | Identity and manifesto, a Living Archive of 40+ works, concept projects (Stillpoint, TrailPod, Desert Antipode and others), coursework, a skill suite (/paper-pusher, /paper-planner, /peer-pressure, /critical-thinking, /background-checker, /assignment-brief, /placement-test-UNI), and the Sinyal Terakhir short film (30-shot Higgsfield queue, rough cut 15 of 30 shots). |
| June 21 to July | Reorientation; a **Procreate brush engine** with procedural textures, Bezier pressure curves and "a real NSKeyedArchiver builder", producing a working Procedural Watercolor brush; mentor cards and decks. |
| August | NotebookLM corpora; the **Creative OS "Master Charter"** (Phase III: Grid, Space, Code); a Higgsfield prompt PDF for **Right Door, Wrong Exit** (seven PS1-style loading screens); a rebuild proposal and client pitch for The Reserve at Hot Springs. |
| September | The **Studio Headless OS** document (28 pages), with Claude's five main arguments recorded (schema-first over TypeScript types, provenance tiering, the zero-network vs git-remote contradiction, phase ordering, hashed attestations; the capability coverage manifest flagged as best value). Agent-Reach reviewed. NINETY-NINE's four production documents. The first Blender MCP attempt and the procedural liminal hallway. A propositional-logic idea (the "premise ledger"). |
| October to November | Juniper Collective (28 October: a law-firm-model advisory firm; Claude pushed back on a two-day build and proposed a thin vertical slice, which matches the repo's commits on 28 to 29 October). Essays: "Stop Asking For It, Ask For What It Takes" (3 November, which became the 64th original work in the vault) and "What It Bends" (4 November, 25 pages). The Legacy Cafe brand board (14 November). |

### Findings from combining chat and cloud records
1. **The brush tool has a longer history than the repos show.** The chat log has a working NSKeyedArchiver builder in July, the Part 1 document records v1's `.brush` export as structurally broken, and ROSW's `brushes/` codec was rebuilt "byte-exact" on 30 October. [Inference] These are three attempts at one problem. **Owner statement, 17 November: the brush tool works in both Procreate and Photoshop.** That is the owner's own testing, not something I could verify, and it closes the Part 1 acceptance test (a produced file opens in Procreate) on the owner's word. One thing to reconcile: the brush app's README says `.abr` (Photoshop's native format) is deliberately "not offered", so the Photoshop route must use another export (the v1 Universal Kit used ink-alpha PNGs, masks and `.gbr` plus an import recipe). The documents should say which export works in Photoshop and how it was tested. Part 1 also noted the v1 design refused to guess at `.abr`; that discipline appears to have been kept.
2. **Work enters the studio as chat, then becomes a repo.** NINETY-NINE (documents in September chat, The-Intern repo from 13 September, teardown in October), Right Door (chat prompt PDF in August, repo from 22 August), Juniper (chat 28 October, repo 28 October) and the "Stop Asking" essay (chat 3 November, vault commit 3 November) all follow it. [Inference] Chat is the design room; cloud sessions and repositories are the build room. This pattern was invisible in Parts 1 and 2.
3. **Some recorded projects have no repository or cloud session at all.** Sinyal Terakhir (15 of 30 shots), the Legacy Cafe brand board, The Reserve at Hot Springs, "What It Bends", the Creative OS charter and the mentor-card system appear only in the log. [Inference] They are real work that the studio's repositories do not track, which matters for any "ship list" decision.
4. **Part 1's critique was acted on in part, not wholly.** The `origin` field and the "ship every tool off" rule echo the provenance-tier and honesty arguments. No evidence found of schema-first definitions, hashed attestations or a coverage manifest in the studio.
5. **The owner's own open questions overlap this report's gaps.** The log lists unresolved items that match section 9: NINETY-NINE ("is the spine becoming visible on replay a flaw or the thesis?"), Juniper ("the one-sentence method statement"), Legacy Cafe ("which identity leads, and what is the legacy?") and Sinyal Terakhir ("still in motion").


---

## 3B. The owner and the full portfolio (from the owner's Memory Log, 17 November)

The owner said personal information is as important as the project information. This section records both, as the Memory Log states them. It is a chronicle written from chat history; chats inside Projects (Songs, CIV VI, Creative Headquarters and others) were not searchable, so those appear only where they surfaced elsewhere. Nothing here was checked against other sources. This public copy omits the owner's personal details (residence, family, health, study, relationships and private research topics); the owner holds the full version.

### How the owner works with Claude [Evidence]
- **First session (about 7 March)** was a meta-critique of the collaboration. Two corrections reset everything: concepts are the deliverables ("next steps" means conceptual, never build-or-ship), and Claude is an equal thinking partner who pushes back, not an assistant.
- **The Resonant Origins reveal (7 March).** Claude proposed patterns; the owner refined each (constraint became compositional discipline, dual-use became "density of purpose", invisible systems became the earthworm metaphor); Claude proposed *augmented naturalism* and the owner confirmed it with the mountain metaphor. Only then was the name revealed. The method: existence precedes naming, substance before structure.
- **Insight-formation method (documented 1 July):** sober observation, an integration session, plain-language naming, then cross-domain pressure-testing with Claude.
- **Protocols in force.** No em dashes in any writing. Songwriting: lyrics in a code block and the style prompt in a separate block under 1,000 characters. Textbook PDFs: ReportLab, Times-Roman, letter, 1.2 inch margins, INK #1a1a1a, GRAY #555555, RULE #aaaaaa. UI work: run UI/UX Pro Max first, no generic choices. Concepts are the deliverables.

### How the owner meets reactions to AI [Owner's words, 17 November]
The owner never withholds that a project was made with AI. They see dislike and discrimination as fuel, and love it when people feel jealous, because it tells them they are doing something right. [Inference] The owner treats hostile and envious reactions as a signal about the work's reach and about the audience, not as a verdict on the work, which fits the owner's stated measure (work done, not whether it is good).

### Ideas and foundations [Evidence]
- **The Pendulum Principle.** Born from two field observations (a forest glade built from accumulated failure; a fern field whose gas exchange felt perceptible). Systems receive because they expend; sealed systems dampen and die. Locked as a foundation of the owner's research, with Alaska Native vernacular architecture (barabara, igloo, qasgi) as survival evidence.
- **ROSW identity.** A manifesto ("I am building an argument..."), six precedents (Beuys, Abloh, Gates, Eliasson, Westwood, Hadid).
- **The Living Archive.** 40+ works organized by generative potential across six modalities (Seed, Root, Branch, Fruit, Compost, Mycelium); a four-act collapse structure (False Haven, Erosion, Revelation, Living Death); a nine-principle lunar voice document.
- **Alaska and the Amazon (May).** Reading about Percy Fawcett triggered a civilizational vision for the Amazon. Claude misread it as savior framing and the owner corrected it. Resolution: Alaska as proving ground, Amazon as the civilizational project.
- **"What It Bends" (4 November).** A 25-page, 8,300-word theory of secondary systems (the creeper parable, a seven-part topology, a ten-style taxonomy, the main game as a battery). Noted that the liminal game may invert it, with dread as the energy source.
- **"Stop Asking For It, Ask For What It Takes" (3 November).** An essay naming "just me and AI" as an unacknowledged prerequisite; later became the 64th original work in the vault.
- **Propositional logic for coding.** The premise ledger idea (most failures are unsound premises, not invalid inference) and a sourcing prompt for a Z3-backed plugin or MCP.

### Every project the log names, by group [Evidence]
**Studio and tooling (the repos in this report).** ROSW (Pipelines-Plugin) with the creative-writing vault, studio, brushes, sound library, udgt, reach, video-editor, graphic-design, ui-design and blender plugins; the Studio Headless OS design (Part 1); Creative OS "Master Charter" (August); the Procreate brush engine (July) and brush designer (March and 21 March web app); Agent-Reach and agent-skill-simplified-technical-english (reviewed in September); the skill suite (/paper-pusher, /paper-planner, /peer-pressure, /critical-thinking, /background-checker, /assignment-brief, /placement-test-UNI, a GSD workflow).

**Games.** Who Did It; The Intern / NINETY-NINE / Following The Sheep (four production documents: master game logic with endings ASSIMILATION, EXPULSION and PENDING REVIEW at 27, 27 and 202 across 256 paths; a Higgsfield and Kling pipeline of 80 stills and 40 videos; a mini-game UX spec of seven unfailable games feeding a hidden friction score; a technical build spec with the 48 Hz drone rule and a 256-path CI sweep); Right Door, Wrong Exit (8-page Higgsfield prompt PDF for seven PS1-style loading screens and a start screen); Look Over There; esc-ZINE99 (ten games); the liminal hallway built procedurally in Blender (hotel version, then the mustard institutional version with the vending machine and "THE END").

**Film and media.** Sinyal Terakhir: a 5-minute AI conservation thriller about the Sumatran rhino, a 30-shot Higgsfield queue (6-concurrent-job cap, two-pass FFmpeg DTS fix), rough cut v1 at 1:47 with 15 of 30 shots, still in motion. A 10-second pine tree clip extracted to 240 frames. Songwriting for Suno ("To Be Known", a Morgan Wallen-style folk hymn, the Ye *Bully* resonance analysis). Spotify playlists ("Golden Hour Dreams").

**Business and client work.** Juniper Collective (28 October; an advisory firm for experience-based businesses on a law-firm model; Claude pushed for a thin vertical slice; the open item is a one-sentence method statement). The Reserve at Hot Springs (rebuild proposal and client pitch PDF in the property's palette, after an earlier congressional dinner menu). The Legacy Cafe brand board (14 November; Serra layout, seal and monogram, Cinzel / Playfair / Inter, six colors; problems: the dark seal and bright yellow garden read as two brands, the monogram fails small; open question: what does "Legacy" refer to). SSCC.inc fiber optics company website; fiber optic route map viewer (Dogwood Valley); Vermeer HDD fault diagnostics.

**Concept projects.** Stillpoint (live-work institution, two iterations, research brochure), TrailPod (zero-waste trail nutrition, field-tested on a 22-mile Appalachian Trail hike), FIRMAMENT (interactive art history brief), Folio, Dial, N.I.R.F., Oculus Dome, Desert Antipode (Zeedyk earthworks, biocrust, dikengyuan courtyard, olla irrigation), Stone and Seed (Tassili n'Ajjer and Sacred Valley), Avrame Trio 150B dual-unit build, "Extra Credit, No Debit" archive document, "The Complete Learning System" binder, an Age of Synthesis essay, a Discipline Architecture textbook, mentor cards (ten historical figures: da Vinci, Fuller, Jung, Humboldt, Alexander, Gaudi, Kahn, Tesla, Noguchi, C.S. Lewis) and a three-deck museum placard system (Character Study, Fields of Inquiry, Portfolio Idea) with a two-sided PPTX mentor card skill.

### The owner's own open questions [Evidence]
- Where does the Church-Turing thesis sit relative to the Pendulum Principle?
- When does augmentation become the erasure it was meant to prevent?
- How does the ROSW portfolio replicate the Resonant Origins reveal for a stranger?
- Does the logo's W-to-E rotation land yet?
- Creative OS: the Code layer's movement scheme and Ctrl+up/down.
- NINETY-NINE: is the spine becoming visible on replay a flaw or the thesis?
- Juniper: the one-sentence method statement.
- Legacy Cafe: which identity leads, and what is the legacy?
- Sinyal Terakhir: 15 of 30 shots, still in motion.

---

## 4. Timeline since Part 2: five phases

| Phase | Dates | What happened | Sessions |
|---|---|---|---|
| **A. Asset burst** | 21 to 22 Oct | Sound library built and filled; Higgsfield library synced; Who Did It round 6 runs 17 sessions in one day (time scale, event bus, GitHub auth and admin room, gathering and crafting, mobs, quests, cutscenes, music, integration). | 21 |
| **B. Lore and teardowns** | 23 to 25 Oct | The peak. 30 sessions on 23 October: Who Did It round 7 (menus, re-skin, parties, vendettas, the Daily Train, quick mode removed) and round 8 (bodies, scrip, rent, faith, moods, creatures, anti-cheat, rules). Eight waves of lore written into the vault. udgt built and run on three games. Round 9: design sessions and the admin Studio. | about 55 |
| **C. Consolidate and audit** | 28 Oct to 3 Nov | Round 10 (contracts, "the law", logic table, refusal sweep, wave 2 roles, kit, town, ghosts). ROSW imports agent-reach and video-editor, builds the brushes tool, then audits itself (ROADMAP.md, 30 Oct) and runs four hardening lanes (31 Oct). Housekeeping sessions: OneDrive to Google Drive migration, duplicate folders, deleting remote branches, MCP install issue. | about 35 |
| **D. Story and a new family of games** | 4 to 10 Nov | Who Did It Story mode (S1 to S4, P0 to P4), a merge queue for round 10 PRs, the verbs (hide, dust, autopsy, cover-up). Look Over There begins (first commit 1 November). Numbered Sessions 2 to 12 on modes, parties, results, overworld, city, physics. | about 30 |
| **E. Rooms, determinism and spread** | 11 to 17 Nov | Look Over There peaks (46 commits on 12 November). Sessions 13 to 18: deterministic tests, rooms, "go to a friend", rules for arsenal and food. esc-ZINE99 created 15 November; gamechat created and released 15 November. | about 13 |

Note the gap: **no sessions on 26 and 27 October, none on 4 to 5 November except one blocked session, and the last two days are quiet.** [Inference] Sessions run in bursts after the owner sets a plan, then stop while the owner reviews.

---

## 5. Project by project

### 5.1 Who Did It (the flagship)
**What it is.** Browser multiplayer hidden-role game, Phaser client, Colyseus server, pnpm monorepo. 915 commits (144 at Part 2).

**Progress [Evidence from session titles and commit subjects].**
- **Round 6 (22 Oct, 17 sessions):** simulation harness and time scale, event bus and invariants, GitHub auth and an admin room, gathering and crafting, mobs and dark visibility, quests and mini-games, cutscenes, music, opening cinematic, ROSW media, integration pass (6P).
- **Round 7 (23 Oct):** theme pieces, menus and profiles, a three-column lobby, match screens re-skin, parties (open and private), vendettas, the Daily Train and the Ascended Vicar, Crumb's Ovens rooms drawn from the owner's station pictures, and **the quick mode's removal (7J)**. The 2D quick mode that Part 2 described is gone; the Who-Did-It CLAUDE.md now says so.
- **Round 8 (23 to 24 Oct):** bodies, inspect and the relations table, scrip and wages, rent and faith, moods and mugging, characters, creatures, interface motion, HD art, HollowMere and BlackPine rooms, anti-cheat, rules, icons, canon, the NPC hive, meeting notes and NPC talk. An orchestrator session (6Z) runs it.
- **Round 9 (25 Oct):** design sessions (world mode, logic table, living world), a fold of the owner's answers into a round-10 plan, and the admin Studio (server, client, live redraw, NPC editor).
- **Round 10 (29 to 30 Oct, then 7 Nov):** contracts, "the law", death's cost, the logic table, a refusal sweep, role cards, new roles, kit, the town, ghosts, the missing verbs, a scope census, and two **Fable** fix sessions (10X server and rules, 10Y client and screens).
- **Story mode (6 to 10 Nov):** content and schema, engine with seat handover, protocol and client cards, tests, replay and bot, a HollowMere arc, achievements on the device, a sections engine, saves and end screen, a Medium's rite.
- **"Session N" series (8 to 15 Nov):** Original tuning, modes and parties, results v2 with deaths and revives, Overworld v0, physics decision, Going-back-in prototype, City v0 on Hallam Row, rooms, "go to a friend", arsenal rules.

**Needs work.**
1. **Playtest observations are unrecorded, and the repo's gate does not match the owner's purpose.** The owner reports at least 8 sessions with 2 to 5 players each: fun and laughter, but no loop that makes people want to return, and no way yet to tell novelty from a good game. They also report unfair criticism and a lack of honesty about enjoyment, with some players refusing to let themselves have fun because AI was used and calling the result "slop" regardless of the work behind it. The scorecard and form in `docs/PLAYTESTS/` are unfilled, so none of this is in the repository, and the folder still frames the M3 exit as a "fun-or-stop decision".
2. **Test flakiness is recurring.** About nine sessions are named for timing races or intermittent tests (22 Oct three times, 24 Oct, 11 Nov, 12 Nov twice, 14 Nov, 16 Nov, the last still "review ready"). [Inference] The cost of running many parallel sessions against real-time servers shows up as timing-dependent tests; each fix is local and the class keeps returning.
3. **Scope.** M5b (resources, mobs, quests) was planned in Part 2 and shipped in round 6. Rounds 7 to 10 added an economy, a town, vendettas and a story mode. The project's own risk register names scope creep as a risk. [Inference] The owner's stated measure is work done, not whether the result is good (section 1B), so this is recorded as a fact about growth, not as a fault.
4. **One session blocked:** "Game scenes and level connections" (4 Nov).

### 5.1A 3D and art production for Who Did It (reported by a Who Did It session, partial)
Source: a report pasted by the owner from a Who Did It session (Story-mode work). That session says it can speak only for what passed through it. [Evidence from that report; not checked against the repos.]

**Built with Meshy (the owner's uploads, merged by that session)**
- **Props:** four zips with 23 GLBs. The session split the fused models and named them, giving **118 interior props**, plus 6 duplicates of set 14 and 8 extras not on the interior list (food, bottles).
- **Characters:** 27 rigged models in `characters/meshy_rigged`. The session is not certain all were made in Meshy (it inferred this from merge folder names).
- **Items:** 32 item models in the merge; origin not known to the session.
- **Known gaps:** `woven_rug` is a flat green patch; seven prop kinds have no model (bar_counter, bar_counter_taps, barrel, bottle_crate, keg_rack, tavern_table, tin_crate).

**Built with Higgsfield (not Meshy)**
- The `mallory` and `villagerlass` 3D models, which brings the total to **40 characters with 3D models**.
- 22 low-poly prop sheets, cut into 43 sets of three props or fewer.
- The 2.5D prototype and decision A615, in draft PR #549.

**Built in the local Blender session**
- The reporting session saw only that session's messages. They mention the **Blender map from PR #539** and the **walk-viewer contract in PR #547, which has one GLB per area**. What else that session built is not known here.

**Terrain and map generation.** The owner says the 81 Blender add-on tools are the ones used for terrain and maps (trees, rocks, hills, clouds, water), from a Story-mode session. In the repo, `ENABLED` in `blender-addons/build_manifests.py` was still empty on 3 November, so the on/off choices appear to live only on the owner's machine. [Inference]

**Reading (inference).** Meshy is no longer only a studio pipeline: it is a main prop and character source for the game, fed by the owner's uploads and merged by hand rather than through the studio's `asset-3d` run with go-ahead and `keep`. This supports the section 7 observation that game work uses ROSW as a tool shelf rather than a governed pipeline. The Blender add-on tools cover the map side; Higgsfield and Meshy cover the object and character side.

### 5.2 Look Over There (new)
**What it is.** A walkable multilevel Backrooms building built in Blender and served as a static three.js page: poolrooms, an office maze, a plaster room, a showroom, a parking lot and a city, with monsters, doors, items, co-op revive and controller support. First commit 1 November; 227 commits since, 46 on 12 November alone; the last was 16 November.
**Convergence [Evidence].** Commits on 1 November put **Right Door, Wrong Exit** and **The Intern** inside it: a stairwell gate on the lawn opens the dining-room walker; the apartment door on the sidewalk opens the original Intern game and returns on its ending. This is the first time the earlier games are literally doors in a newer one.
**Needs work.** Hosting the large world file as a release asset fetched at deploy time (15 November) is a workaround, not a decision. [Inference] No playtest of Look Over There is recorded; whether it has been played by others is unknown.

### 5.3 esc-ZINE99 (new)
**What it is.** Ten games adapted from the creative-writing vault. Rules live in `docs/PILLARS.md` and `docs/COLLECTION.md`. Each game has a design, data, pictographs, art made by code, 3D asset lists, Blender build files and a web module, with validators that must pass before a commit. 50 commits on 15 and 16 November.
**Needs work.** The README still says "Nothing is built yet", while the CLAUDE.md describes a web build and art pipeline. [Inference] The README is stale. Ten games in two days is a design layer, not shipped games. The vault's own rule that source works are never edited is kept; each design lists what was added so the author can approve or strike it.

### 5.4 gamechat (new)
A serverless Electron app for voice, video and screen share with friends, with a phone web client (v2.2.0). It is a tool the owner uses to play together, not part of the studio pipelines. Phone mic and audio were still untested at the last session summary. Small and separate; mentioned for completeness.

### 5.5 Juniper-Collective, The-Intern, Right Door, Strategy-Planner, Earth_Worldbuild
- **Juniper-Collective:** 8 commits on 28 to 29 October; a static site for an advisory firm, rewritten "around the founders, the Reserve and Arkansas". It is a client-style project outside the studio pipelines.
- **The-Intern / Right Door, Wrong Exit:** a few commits each since Part 2 (the last on 30 October and 3 November), mostly because their teardowns were written and because Look Over There now hosts them.
- **Strategy-Planner and Earth_Worldbuild:** no commits since Part 2. Strategy-Planner's 551 unverified plan notes from Part 2 are unchanged as far as the repository shows. Earth_Worldbuild stays a source of material.

---

## 6. Claude usage in the last 30 days

| Measure | Value |
|---|---|
| Sessions created 18 Oct to 17 Nov | 154 (this one included) |
| By month | 18 to 31 Oct: 111; 1 to 17 Nov: 43 |
| Peak days | 23 Oct: 30; 22 Oct: 19; 24 Oct: 15; 29 Oct: 13; 25 Oct: 10; 30 Oct: 11 |
| Started by | spawned by another session 120; desktop app 21; Claude Code CLI 8; iOS 5 |
| Final status | completed 144; failed 7; blocked 1; review ready 1; working 1 |
| Models named in titles | Opus and Sonnet named in session titles by round (for example "(Opus)", "(Sonnet)"); Fable on two round-10 fix sessions |

**The spawned share rose from 38 of 89 (43%) to 120 of 154 (78%).** [Evidence] This confirms Part 2's third pivot: sessions are now mostly created by other sessions.

**The 7 failures [Evidence].** 7M, 8A, 8E, 8F, 8I, 8N and 8V, all on 23 and 24 October, all in round 8. Each has a matching "(Opus)" session on 24 October. Round 8 ran many large tasks in parallel on Sonnet. [Inference] The common factor was size or context pressure, as in Part 2's two limit-related failures, but I did not read the transcripts and cannot say the cause. What matters is the response: retry the task on Opus, which worked in all 7.

**Naming schemes show method [Evidence].** Part 2's "WDI 5A" became "6A" through "10Y" (round and slice), then "Story S1/P0", then "Round 10 V3" and finally "Session 2" to "Session 18". Titles now carry the model, the round, the slice and sometimes the PR or issue number (for example "8Y: #243", "8Z: #253"). [Inference] Sessions have become units of a work queue, each with a number the owner can refer to.

---

## 7. How the trajectory changed (Part 2's table, extended)

| Dimension | Part 2 (to 18 Oct) | Part 3 (to 17 Nov) |
|---|---|---|
| Where work happens | Mostly one game repo | One hub plus four or five game repos |
| Role of ROSW | Tool-maker | Tool shelf and audit target |
| Session size | Rounds of about 13 | Rounds of about 17 to 20, plus design-only rounds |
| Quality control | CI, soak, critic, adversarial reviews | Added: invariant checks (6B), refusal sweep, scope census, a determinism hunt, an audit roadmap, a review checklist per PR |
| Safety posture | Keys out of the repo | Added: hooks that ask before editing an original or sending a publish; `allowed-tools` scopes; pinned tool versions; every add-on tool disabled by default; an Origin/Host check on the hub |
| Model use | Sonnet for implementation, Opus for art and decisions, Fable for UI | Same, plus Opus as the retry path, plus Fable for fixes |
| Product shape | Browser hidden-role game | A world: overworld, city, rooms, Story mode, other games as doors inside it |

### Pivots since Part 2
- **Pivot 4 (29 October to 1 November): from building tools to auditing them.** On 30 October a session reviewed the whole repo and stored the result as `ROADMAP.md` (Parts A to F: fixes, generalising, optimising, new pipelines, a graphic-design toolkit, a local/cloud split). Four hardening lanes followed on 31 October (studio safety, plugins and tooling, truth pass, skills and agents). [Evidence] This is the first time the studio's own claims were checked against its code at scale. It echoes Part 1's honesty discipline.
- **Pivot 5 (1 November): the owner restates the goal.** The roadmap records the owner's decision that the studio should be a set of plugins and skills for specific outcomes (games, films, pitch decks, automated video), with an **orchestrator agent in a separate session managing the "employees"**, the Who Did It agent-swarm model. [Evidence] The studio "does not produce"; it manages the tool list and how to harness it. The graphic-design plugin comes first. [Inference] This formalises what the fleets were already doing.
- **Pivot 6 (November): the games leave the studio's pipeline.** The Who Did It "Session N" series, Look Over There and esc-ZINE99 run mostly on their own repositories' contracts rather than through the studio's `studio-pipeline` gates. [Inference] I found no evidence in these repositories that the studio's checkpointed pipelines with go-ahead and `keep` are used for them. They use ROSW as a library of tools, sounds and generations. This is the largest gap between the studio's stated design and how work actually flows.

### What did not change
Games remain the target. Static, no-build web delivery remains the default. Decisions are still dated and numbered. The label "generated, not the author's" is still carried everywhere (the origin field on every vault work is the newest form).

---

## 8. Where progress is strongest

1. **Reuse across projects [Evidence].** Brushes, sounds and Higgsfield generations are catalogued once and cited by id. The brush codec was rebuilt byte-exact, which addresses the v1 defect from Part 1 (a `.brush` file that no one had opened in Procreate). The owner reports it now works in both Procreate and Photoshop (their own testing; I could not verify it from this session). This is the one Part 1 "never ran" defect with a reported fix.
2. **Self-audit.** ROADMAP.md, the 59-finding style review recorded earlier, the Wave 1 checklist and the truth pass show a habit of testing claims against code.
3. **Safe defaults by design.** Add-on tools off, publishing dry-run, keys outside the repo, hooks that ask before touching originals.
4. **Throughput.** Up to 30 sessions in a day, 144 completed in 30 days, with orchestrator logs.
5. **Convergence.** Earlier games became doors inside Look Over There; the vault feeds a museum, a lore set and ten game designs; the teardown tool reads three games and records the owner's answers.
6. **Provenance.** The `origin` field splits original, derived and auto-authored work so the verbatim rule applies only where it should.

---

## 9. Open items (evidence only; actions are in the Phase 4 planning document)

| # | Area | Evidence |
|---|---|---|
| 1 | **Playtest record vs repo gate** | Owner: 8+ playtests, 2 to 5 people each; fun and funny; repeat enjoyment missing and novelty cannot be separated from fun; unfair criticism and AI-origin objections. The owner does not hold a fun-or-stop test, but `ROADMAP.md`, `MASTER_PLAN.md` and `docs/PLAYTESTS/` still do. The playtest folder is a stub. |
| 2 | **Studio vs how work really flows** | The "Session N" and Look Over There work do not obviously use studio pipelines. |
| 3 | **Scope** | Three new repositories in November; ten game designs in two days; Who Did It adds modes weekly. |
| 4 | **Flaky tests** | About nine determinism sessions. |
| 5 | **Wave 1 merge state** | **Resolved.** The owner confirms PRs #25 to #28 are merged. The roadmap still lists them as open. |
| 6 | **Integrations: mostly exercised; two loose ends** | Owner: Meshy, ComfyUI and the Blender tools work, and the Blender tools made a large difference to Claude's capability (see section 5.1A). The 81 add-on tools are the ones used for **terrain and map generation** (trees, rocks, hills, clouds, water) in a Story-mode session. ComfyUI: the owner's computer lacks the GPU and the cloud version is unused, so it is unclear how far a full run got. The video editor has been used; **`ve publish` has not**. In the repo, `ENABLED` in `blender-addons/build_manifests.py` was still empty on 3 Nov, so the on/off choices live only on the owner's machine. Some repository CLAUDE.md lines still say "never run". |
| 7 | **Laptop-side hand-offs** | Masters (.blend, .glb) and Blender add-on discovery need the owner's machine. (The Procreate and Photoshop brush test is reported done.) |
| 8 | **Documentation load** | The ROSW CLAUDE.md now covers about 15 subsystems; esc-ZINE99's README is stale. |
| 9 | **Stale content** | Strategy-Planner (551 unverified notes) and Earth_Worldbuild untouched since September or early October. |
| 10 | **Deployment** | Pages deploy still depends on the owner setting the source by hand; the workflow only warns. |
| 11 | **Access and hosting** | Railway and Pages are live (owner). User, Client and Viewer access tiers were deferred to the Railway launch, which has now happened. |
| 12 | **ROSW silence** | No commits to the hub since 3 November. |

---

## 10. Reading Part 1's ideas against what happened

[Inference for the reading; evidence for the facts it cites.]
- **Part 1 proposed a persisted, hashed attestation and provenance tiers so that generated work could not vote as precedent.** The `origin` field (original, derived, auto-authored) is a real, partial version of the provenance tier idea. It stops the verbatim rule from covering generated work and keeps derived work labelled. It does not (as far as the repository shows) restrict what counts as precedent for a pipeline's context resolution.
- **Part 1 proposed a minimum honest system and a thirty-day self-use gate.** The owner's own use is visible in the record: 154 sessions in 30 days, with tools (Meshy, Blender, the video editor, ComfyUI) and libraries used for real work. Playtests have happened but are not written up. Self-use of the studio's own pipelines for game work is not visible.
- **Part 1 proposed making the honesty discipline structural.** Wave 1's truth pass, "ship every tool off", and pinned versions with tests are examples of turning a habit into a check.

---

## 11. Questions to ask NotebookLM about this report

- Which of the owner's three bottlenecks (typing speed, swarm organization, human context limit) does each project hit hardest, and what evidence is there?
- Which pivot changed the shape of the work most, and what triggered it?
- Compare the 7 failed sessions and their Opus re-runs. What does the pattern say about how to size a task?
- Which studio tools are used by more than one project, and which are used by none?
- Which open items in section 9 depend on other items?
- Which projects show the most evidence of shipped, used work, and which show the least?
- What would a minimum studio look like if the owner's 1 November goal (an orchestrator plus specific-outcome plugins) were the only requirement?

---

## 12. Corrections to earlier parts

These statements in Part 2 (18 October) no longer hold, or never fully did. They are corrected here, not rewritten there.
- **"No cloud sessions exist in the 21 March to 22 August window, so work was probably local or Claude was not used."** The Memory Log shows steady chat work in that window (section 3A and 3B).
- **"Getting real humans to play" as the most important item, and the "M3 fun-or-stop decision."** The owner has run playtests (8+ games, 2 to 5 people each), and does not hold a fun-or-stop test. The measure is learning, proving and work done (section 1B).
- **"No playtest has been recorded."** Playtests happened; they are unrecorded in the repository.
- **"Hold M5b until M3 is decided by playtest."** M5b shipped in round 6; not a fault by the owner's measure.
- **Part 2 said Meshy, Blender tools and the video editor were unverified or unused in practice.** The owner reports Meshy, ComfyUI (limited by this computer's GPU) and the Blender tools work, and the video editor has been used. The publisher has not.
- **Part 2 listed PRs #25 to #28 as open.** The owner confirms they are merged.
- **Part 2 named the repositories as the whole portfolio.** The Memory Log lists many more projects that have no repository or cloud session (section 3B).

---

## Appendix A. Session ledger summary, 18 Oct to 17 Nov

| Date | Count | Main work |
|---|---|---|
| 18 Oct | 1 | 5N: art-style switch (8-bit / low poly) |
| 21 Oct | 2 | Planning; plugin sound upload |
| 22 Oct | 19 | Round 6 (6A to 6Q), test robustness fixes |
| 23 Oct | 30 | Round 7 (7A to 7M), round 8 first pass (8A to 8N), Railway, ROSW cleanup, lore, teardown |
| 24 Oct | 15 | Round 8 Opus re-runs, hive, canon, orchestrator 6Z |
| 25 Oct | 10 | Round 9 designs, admin Studio, teardown config |
| 28 to 29 Oct | 14 | Tailwind, agent-reach, session autocompact, round 10 slices, render pipeline, 3D asset pipeline |
| 30 Oct | 11 | Round 10 fixes and wave 2, Blender blockout, repository review |
| 31 Oct | 9 | Wave 1 lanes A to D, PR review, folder and MCP housekeeping |
| 1 to 5 Nov | 4 | Controller fix, branch cleanup, "Stop asking for it" chapter, one blocked scene session |
| 6 to 7 Nov | 17 | Story mode, merge queue, round 10 verbs, player accounts plan, local gaming chat |
| 8 to 12 Nov | 14 | Sessions 2 to 14, Blender tools, creative-writing-to-game adaptation |
| 13 to 17 Nov | 8 | First-person HollowMere walk, Sessions 15 to 18, gamechat, server-test timing, this report |

## Appendix B. Repository activity since Part 2

| Repo | Commits since 18 Oct (non-merge) | Last commit | Note |
|---|---|---|---|
| Pipelines-Plugin (ROSW) | 133 | 3 Nov | 319 commits in total |
| Who-Did-It | 427 | 16 Nov | 915 in total; dates cluster on integration days |
| Look-Over-There | 227 | 16 Nov | new |
| esc-ZINE99 | 50 | 16 Nov | new |
| Juniper-Collective | 7 | 29 Oct | new |
| gamechat | 3 | 15 Nov | new |
| Right-Door-Wrong-Exit | 4 | 30 Oct | |
| The-Intern | 3 | 3 Nov | |
| Video-Editor | 3 | 29 Oct | merged into ROSW as a plugin |
| Strategy-Planner | 0 | 2 Oct | |
| Earth_Worldbuild | 0 | 29 Sep | |

## Appendix C. Sources and method
Git history, README, CLAUDE.md, ROADMAP.md and docs of the eleven repositories cloned in this session; metadata for 154 Claude Code cloud sessions (title, date, origin, status bucket, and sometimes a summary line) from the account's session list; and the owner's "Memory Log: Phases 1 and 2, March to November 2026" (chat-history summary, 17 November). Transcripts and the underlying chats were not read. Anything outside those sources is labelled as inference.



---

# DOCUMENT 4 OF 6

# ROSW Phase 4 Planning

**Fixes, suggestions and proposals, kept separate from the progress reports.**
Started 17 November 2026 for NotebookLM. This is the companion to *ROSW Progress Report, Part 3*, which records what has happened. This document holds only what could be done next.

---

## 0. How to read this document

- **Everything here is a proposal.** None of it has been decided or adopted. The owner may reject, change or reorder any of it. Please do not report a proposal as a project decision when asking NotebookLM questions.
- **Evidence lives in Part 3.** Each item names the Part 3 section it rests on. Facts marked "owner" were supplied by the owner on 17 November and were not verified from the repositories.
- **Authorship.** The proposals are Claude's. The owner's framing (the three bottlenecks below) is quoted from the owner.
- **Style.** To match the owner's own questionnaire docs, section 5 is written as questions with a proposed default. Answer *default* or *different*.
- **How to add to this document.** All future fixes and suggestions go here, under the matching section, with a date and a status (*proposed*, *accepted*, *rejected*, *done*). Part 3 and later progress reports should not carry proposals.

### Status key
`proposed` (new, not yet looked at) · `accepted` · `rejected` · `done`. Everything below is currently `proposed` unless stated.

---

## 1. The owner's purpose (the lens for every proposal)

Stated by the owner on 17 November. Proposals here are meant to serve these, and any proposal that does not should be rejected:
- **Build to learn.** Who Did It is a win whatever others think of it. The mechanics are used differently in finance, education and other applications, so the learning transfers.
- **Build to prove.** The first proof was a pitch document that a human judged a good idea, showing the AI was not simply approving whatever the owner said.
- **Never withhold that it is AI; treat dislike as fuel.** The owner always says the work was made with AI. They see dislike or discrimination as fuel and love it when people are jealous, because it means they are doing something right.
- **Measure work done, not whether it is good.** "Good" can only describe a finished thing. There is **no "fun or stop" test.**

Earlier planning documents in the Who-Did-It repo (`ROADMAP.md`, `MASTER_PLAN.md`, `docs/PLAYTESTS/`) do contain a "fun-or-stop decision" as the M3 exit. See 3, item 1.

---

## 1A. The three bottlenecks (owner's framing)

1. **Human speed limit.** How fast the owner's typing speed could increase. *Answer so far: the swarm.*
2. **Swarm organization and user dependencies.** Organization, tool access, context configuration and management, and overlap when two or more agents get the same task. *Answer so far: contracts, file ownership, orchestrators, hooks, scoped tools.*
3. **Human context limit.** How one human can manage the current output while staying on top of everything, and act as a real pivot point instead of an observer. *Answer so far: the questionnaire docs (a partial fix, per the owner). Still open.*

Phase 4 is assumed here to be the work on bottleneck 3 and the open items from Part 3 section 9. If the owner defines Phase 4 differently, section 6 below is the place to say so.

---

## 2. Proposals for bottleneck 3: the human context limit

### 2.1 Define what a pivot point is `proposed`
The swarm cannot decide taste, scope cuts or what the owner wants to learn. List the decision types that only the owner makes (brand gates, scope cuts, release and publish, spend, what to learn next) and route only those to the owner; everything else gets a default and proceeds. This echoes Part 1: the work stops, the system does not.

### 2.2 A decision inbox, not a status feed `proposed`
Build on the existing questionnaire docs. Each round's orchestrator ends with **at most five** items that need a human, each with options, evidence and a recommended default. The session list already carries a `needs_action` flag in each session's post-turn summary; an orchestrator can use it to assemble the inbox so the owner does not read session titles.

### 2.3 Order questions by consequence `proposed`
The questionnaires are ordered by topic. Add a top line marking which items change scope, cost, licensing or release, and put those first. Example from round 11: the Meshy licensing question (SC2) sat beside minor questions.

### 2.4 A playtest log, not a scorecard `proposed`
Replace the pass/fail scorecard with a short log saved in the game's `docs/PLAYTESTS/` folder, in the same question format as the other questionnaires. Suggested fields: date and build, who played (count, new or returning), what happened, what the owner saw and learned, what the group said about the game, **each player's stance toward AI before playing (open, skeptical, or refuses to enjoy it; by category, not by name)**, how their reaction related to that stance, and what the owner wants to test or build next. The AI attitude is treated as a factor that shapes the experience, not as a separate matter, because the owner reports it changes whether some players let themselves have fun at all. There is no verdict field. The aim is to make what the owner learns readable to the swarm, not to score the game.

### 2.5 One generated state-of-the-studio page per round `proposed`
Part 3 is a manual version of this. At each integration pass, generate a page from the repositories and the session list, plus a short checklist the owner fills in for owner-only facts (playtests, hosting, what works on their machine). Make it audio-friendly, since listening on NotebookLM already works as a context-limit tool for the owner.

### 2.6 Pause scope on a decision the owner flags `proposed`
When the owner flags a decision as open, the orchestrator proposes no new work on that decision until it is answered; everything else continues. This keeps the swarm from deciding by building. It is the owner's call which decisions get flagged.

### 2.7 Close the stale-statement loop `proposed`
Out-of-date lines (a README that says "nothing is built yet", CLAUDE.md lines that say "never run") add to the owner's load because they cannot be trusted. Have the end-of-round integration pass list statements that conflict with the owner's reported facts and fix them.

### 2.8 A work ledger `proposed`
Since the owner's measure is work done, generate a ledger from the repositories and the session list, per project and per week: sessions completed, PRs merged, features and tools shipped, systems built. Part 3 is a manual version. It records progress in the owner's terms, without judging quality. **Also record the owner's own contributions** (decisions logged, questionnaires answered, the one answer that overrode a default, designs and direction supplied), since some players dismiss the games as "slop" and say the owner did nothing. The ledger is the factual answer to that, drawn from the record rather than argued.

### 2.9 A learning and transfer map `proposed`
For each mechanic or system built (a hidden-role deal, an economy, a vendetta, a decision inbox, a render pipeline), record in one line where else it applies (finance, education, other products). This captures the "build to learn" purpose, which is currently only in the owner's head.

### 2.10 A proof ledger `proposed`
Record each claim the owner wants to prove, what was shown, to whom, and what happened (the pitch document is the first entry: a human judged the idea good, evidence that the AI was not just approving). Include the playtest groups as an audience, with their reactions logged as reactions, including players who refuse to enjoy the game because of AI use. A player who has decided in advance is a result about the player's stance, not about the game.

---

### 2.11 One portfolio register for the owner's whole body of work `proposed`
Part 3 section 3B lists about 60 projects, studio and non-studio, in one place. Most have no repository or cloud session. Keep that list as a living register (name, group, status *active / parked / done*, last touched, where its files are) so that the studio's view and the owner's view of the portfolio agree. The register also supports the work ledger (2.8) and the learning map (2.9) for projects outside the repos.

### 2.12 Keep the personal record current `proposed`
The owner treats their personal record (protocols and open questions, among other things) as equal in importance to the projects. Refresh section 3B of the progress report from each new Memory Log, and carry the owner's protocols (for example, no em dashes in any writing) into the instructions every session starts from, so that sessions follow them without being reminded.

---

## 3. Proposals from the open items (Part 3 section 9)

| # | Item | Proposed action | Status |
|---|---|---|---|
| 1 | Playtest record vs repo gate | Replace the "fun-or-stop" M3 exit in the Who-Did-It docs (`ROADMAP.md`, `MASTER_PLAN.md`, `docs/PLAYTESTS/README.md` and `SCORECARD.md`) with the playtest log in 2.4, since the owner does not hold that test. Record the 8+ sessions already run, from the owner's memory, as a first entry. | proposed |
| 2 | Studio vs how work really flows | Decide whether the studio governs game work or only supplies tools; say so in the ROSW CLAUDE.md. | proposed |
| 3 | Scope | Mark each project *active* or *parked* with a one-line reason, so it is clear where work is going. Parked is not failed. | proposed |
| 4 | Flaky tests | One shared test-clock and wait helper, enforced in CI, instead of per-test fixes. | proposed |
| 5 | Wave 1 roadmap | Strike the Wave 1 checklist and items from `ROADMAP.md`, since PRs #25 to #28 are merged (owner). | proposed |
| 6 | Integrations | Record which of the 81 Blender add-on tools are enabled (put them in `ENABLED` in `blender-addons/build_manifests.py`); decide whether `ve publish` is wanted, park it if not; record the cloud ComfyUI plan; update the CLAUDE.md lines that still say "never run". | proposed |
| 7 | Laptop-side hand-offs | A short end-of-round laptop checklist for masters (.blend, .glb) and add-on discovery. | proposed |
| 8 | Documentation load | Prune CLAUDE.md files to rules a test enforces; regenerate stale READMEs (esc-ZINE99). | proposed |
| 9 | Stale content | Park Strategy-Planner (551 unverified notes) and Earth_Worldbuild explicitly, or finish them. | proposed |
| 10 | Deployment | A one-page checklist and a CI check for the Pages source. (Railway and Pages are live per the owner.) | proposed |
| 11 | Access tiers | Decide whether to add the User, Client and Viewer tiers now that the Railway launch has happened; check the CDN-link lint noted in the roadmap. | proposed |
| 12 | ROSW silence | Either resume the roadmap on purpose or mark the hub stable. | proposed |
| 13 | Meshy workflow | Props and characters are merged by hand rather than through `asset-3d`. Decide whether the studio pipeline is the intended route, and if so, record merged props there so each has a run id and a credits row. | proposed |
| 14 | Known art gaps | `woven_rug` is a flat green patch; seven prop kinds have no model (bar_counter, bar_counter_taps, barrel, bottle_crate, keg_rack, tavern_table, tin_crate). | proposed |
| 15 | Brush export for Photoshop | Name the export that works in Photoshop and how it was tested (the brush app does not offer `.abr`). | proposed |
| 16 | Usage limits and big sessions | Part 2: two failed sessions ended on spend or session limits and several exceeded 450k tokens; Part 3: seven later failures were re-run on Opus. Split heavy tasks earlier, and keep "retry on a stronger model" as a routine, not an accident. | proposed |
| 17 | Licensing and terms | Part 2 open question 13: save Higgsfield's terms of service as a dated copy; confirm that Meshy output on the owner's plan is theirs to ship (round-11 question SC2). | proposed |
| 18 | Unverified facts | Strategy-Planner's 551 plan-review notes and the vault fact-check batches: clear them with someone with the game open, or mark the codex as unverified where shown. | proposed |

---

## 4. Carried over from Part 1 (the Studio Headless OS review)

These were proposed in Part 1 and are not adopted. They are listed so that Phase 4 can pick them up or drop them deliberately. Part 3 section 10 notes how far the studio has gone toward each.

- **Provenance tiers** so generated notes cannot vote as precedent (the `origin` field is a partial version).
- **Persisted, hashed attestation** so an artifact can be traced to the constraints it was made under.
- **Gate versioning** with a superseded-by pointer.
- **A parked-task queue with a lifecycle** (this overlaps with the decision inbox in 2.2).
- **A capability coverage manifest** (flagged in Part 1 as the best value for effort).
- **Schema-first protocol definition** so notes are validated at run time, not only code.
- **A minimum honest system and a thirty-day self-use gate.** The owner's own use is already visible in the work ledger (2.8).

---

## 5. Questions for the owner (with proposed defaults)

*Answer **default** or **different** (with a note). A question left unanswered takes its default and is marked proposed. The first four change scope or the owner's purpose, so they come first.*

**P1. Replace the "fun-or-stop" gate in the Who-Did-It docs?** The owner does not hold that test, but the M3 exit still says it.
- Default: yes. Replace it with the playtest log (2.4) and record the 8+ sessions already run.

**P2. Which projects are active this phase, and which are parked?** Candidates from Part 3: Who Did It, Look Over There, esc-ZINE99 (designs), Juniper-Collective, gamechat, and the chat-only projects.
- Default: the owner's choice. Parked is not failed.

**P3. Does the studio govern game work, or supply tools to it?**
- Default: supply tools. Studio pipelines stay for the things they are good at (brand gates, `keep`, spend), and game repos keep their own contracts.

**P4. Should `ve publish` stay?**
- Default: keep it, parked. No work on it until there is something to publish.

**P5. Decision inbox limit.** Five items per round?
- Default: five, ordered by consequence.

**P6. Playtest log.** Add one to each game's `docs/PLAYTESTS/`, recording each player's stance toward AI alongside their reaction?
- Default: yes, in the same format as the round questionnaires, with no verdict field.

**P7. Generated state page per round.**
- Default: yes, one page per round, generated by the orchestrator, with an owner checklist.

**P8. Which Blender add-on tools are enabled?**
- Default: list the ones you actually use (terrain, trees, rocks, hills, clouds, water) in `ENABLED` and leave the rest off.

**P9. Meshy through `asset-3d`?**
- Default: yes for new props (run id and credits row); leave the existing 118 merged props as they are.

**P11. Work ledger.** Generate it per project and per week?
- Default: yes, one page, generated each round.

**P12. Learning and transfer map.** One line per mechanic on where else it applies?
- Default: yes, kept in the studio vault, owner confirms each line.

**P13. Proof ledger.** Start with the pitch document and the playtest groups?
- Default: yes.

**P10. Access tiers (User, Client, Viewer).**
- Default: not yet; revisit when there is a client or a second audience.

---

## 6. Phase 4 scope and sequencing (proposed)

The owner has not yet defined Phase 4 beyond "all future fixes and suggestions go into planning for phase 4". A proposed order, smallest and most decision-bearing first:

1. **Week 1: purpose and scope.** Answer P1 to P4. Write the first playtest log entry from the 8+ sessions already run.
2. **Week 2: decisions and housekeeping.** Strike roadmap items, record add-on tool state, update stale CLAUDE.md and README lines (items 5, 6, 8).
3. **Week 3: inbox, state page and ledgers.** Build the decision inbox, the generated state page and the work ledger (2.2, 2.5, 2.8).
4. **Later: carried-over ideas.** Pick from section 4, and the learning and proof ledgers (2.9, 2.10), when the owner wants them.

*Owner: change this section freely; it is the placeholder for the Phase 4 definition.*

---

## 7. Questions to ask NotebookLM about this plan

- Which proposals serve the owner's three purposes (learn, prove, work done), and which do not?
- Which proposals depend on the answers to P1 to P4?
- Which proposals reduce the owner's load most, and which add to it?
- What would a decision inbox contain today, using Part 3?
- Which items in section 3 can be done by sessions without the owner, and which need the owner?

---

## 7A. The owner's own open questions (from the Memory Log; not proposals)

These are the owner's questions, listed so Phase 4 can pick them up. They are not Claude's proposals.
- Where does the Church-Turing thesis sit relative to the Pendulum Principle?
- When does augmentation become the erasure it was meant to prevent?
- How does the ROSW portfolio replicate the Resonant Origins reveal for a stranger?
- Does the logo's W-to-E rotation land yet?
- Creative OS: the Code layer's movement scheme and Ctrl+up/down.
- NINETY-NINE: is the spine becoming visible on replay a flaw or the thesis?
- Juniper: the one-sentence method statement.
- Legacy Cafe: which identity leads, and what is the legacy?
- Sinyal Terakhir: 15 of 30 shots, still in motion.

---

## 7B. Related plan

The separate **ROSW Skillification Plan** sets out how to turn the owner's work (questionnaires, sub-sessions and orchestrators, templates, pipelines, game skeletons) into repeatable skills so the projects become one world. It is Phase 4's main construction plan; this document keeps the decisions and open items.

---

## 8. Change log

| Date | Change |
|---|---|
| 17 Nov 2026 | Created. All proposals moved out of Part 3 into this document. |
| 17 Nov 2026 | Added a pointer to the Skillification Plan (7B). |
| 17 Nov 2026 | Added the owner's stance on AI (never withheld; dislike is fuel), the portfolio register (2.11), the personal record (2.12) and the owner's open questions (7A). Part 3 now carries the owner's full personal and project information. |
| 17 Nov 2026 | Corrected: the owner says AI attitudes affect the gameplay experience itself (some friends refuse to let themselves have fun), so AI comments are no longer kept separate from comments on play; stance is recorded as a factor. The work ledger now also records the owner's own contributions. |
| 17 Nov 2026 | Owner stated their purpose (build to learn, build to prove, measure work done, no fun-or-stop test). Removed the repeat-play gate and ship-list framing; replaced the post-playtest scorecard with a playtest log; added work, learning and proof ledgers (2.8 to 2.10, P11 to P13). |



---

# DOCUMENT 5 OF 6

# ROSW Skillification Plan

**How to turn everything the owner has built into repeatable skills, so that every project becomes one district of one world.**
Written 17 November 2026 for NotebookLM. A companion to the Phase 4 Planning document. Everything here is a **proposal** unless marked [Evidence]; none of it is decided.

---

## 0. How to read this document

- **Goal, in the owner's words.** Not to slow down. To turn every separate project into one giant one, because a world cannot be built without building scale. Every game, tool, session, decision, change and detail is connected in ways that can only be found by trying, failing, and rebranding the failure as a success in another light.
- **The owner's frame.** The old principles (seeds, compost, mycelium and the rest of the six modalities from the Living Archive: Seed, Root, Branch, Fruit, Compost, Mycelium) are still followed, now internally. This document uses them as its structure, so each skill has a home in the cycle.
- **Rule for the whole plan: skills are harvested, not designed first.** Part 1's own lesson was that protocol shape follows the first working skill. Every skill below is extracted from something that already ran, at the moment it repeats a second time, as a by-product of work already under way. No skill needs a pause in building.
- **Labels.** [Evidence] means a file or record shows it exists (paths are given). [Owner] means the owner said it. [Proposal] means Claude suggests it.
- **Style.** The owner approves design through questionnaires (a standing rule in the Who-Did-It orchestrator handoff), so section 11 is written as questions with proposed defaults.

---

## 1. The thesis: one world, many districts

[Evidence] The connections are already forming without a plan:
- **Look Over There** (a multilevel Backrooms game) contains **Right Door, Wrong Exit** and **The Intern** as doors in its world (commits of 1 November; `games/intern` and `games/rdwe` inside the repo).
- The **creative-writing vault** feeds the Writing Museum, the Who Did It lore (about 75 works), and the ten esc-ZINE99 game designs.
- **Libraries** are shared: 3,577 sounds, 1,272 Higgsfield generations, 990 brush records, one vault of 64 works.
- The **teardown tool** (udgt) reads three different games with one engine.
- The same **session contract** and **questionnaire** format run Who Did It, its Story mode, and the round-11 art makeover.

[Proposal] Treat this as the design: **the world is the product, and each game is a district with a door.** A door is a small, fixed agreement (enter, exit, return what happened). The skills below make the shared parts (registries, skeletons, mechanics, orchestration, libraries, memory) reusable, so a new district costs a content pack, not a new engine.

---

## 2. What already repeats (the raw material)

These patterns appear in more than one place. Each is a candidate skill. [Evidence] unless marked.

| Pattern | Where it exists today | What repeats | Candidate skill |
|---|---|---|---|
| **Questionnaire with defaults** | `Who-Did-It/docs/round11/questions.md` (22 questions), `docs/story/questions.md` (17); answers in `round11/owner-answers.md` | Each question has a proposed default and says where the answer lands; answer "default" or "different"; unanswered takes the default; nothing changes until the plan is approved; answers written back to the repo | Questionnaire builder (S2) |
| **Session contract** | `Who-Did-It/docs/SESSIONS.md` | A table of sessions with model, track, branch and owned paths; interfaces between sessions; merge order; draft PRs under 400 lines; shared root files owned by one session | Session contract (B1) |
| **Round packet** | `docs/round10/` (README, seams, scope, briefs, handoffs), `docs/round11/`, `docs/story/` (README, status, test-plan) | Each round has a README, a seams document, per-session briefs and a status file | Round packet (B2) |
| **Orchestrator** | Session 6Z; `docs/story/orchestrator-handoff.md` ("so any later session can resume without the chat") | Standing rules from the owner, merge authority, resume notes, an integration pass | Orchestrator (B3) |
| **Retry on a stronger model** | Seven round-8 sessions failed and were re-run on Opus the next day | Same task, different model | Retry rule (B4) |
| **Design template** | `esc-ZINE99/docs/DESIGN_TEMPLATE.md` (every `DESIGN.md` has the same ordered sections), `PILLARS.md`, `COLLECTION.md` | One design shape for ten games | Design-from-template (S3) |
| **Game skeleton on disk** | `esc-ZINE99/games/<slug>/` with `art/`, `assets/`, `blender/`, `data/`, `pictographs/`, `tools/`, plus `schemas/` (game, scenes, endings, flags) and validators (`tools/validate.py`, `check_assets.py`, `check_blender.py`, `check_storyboards.py`) | Ten games with one structure and checks that refuse drift | Game skeleton (R2) |
| **Mechanics as modules with tests** | `Look_Over_There/shared/` has 34 mechanic modules (cloak, crossbow, baton, beacon, fuses, keypad, loot, power, save, spawn and more) and 33 test files | One mechanic, one module, one test | Mechanic cards (R3) |
| **Rules as data** | `studio/pipeline/spec.yaml`, `packages/content/data/balance.json`, GDD as the only source of numbers | One source of truth, with tests that check documents agree | Rules-as-data (R4) |
| **Studio pipelines** | `studio/pipeline/spec.yaml`: six stages (intake, context, recipe, execute, review, record), the ladder, attestation, parking | A checkpointed run with a record | Pipeline runner (exists) |
| **Asset intake** | `games/<slug>/assets/assets.json`, `CREDITS.md`, `studio/library/catalog.json`, Meshy merges, build files per location | Prompt, model and job id kept with each image; a credits row for each exception | Asset intake (F1) |
| **Tagging with a closed vocabulary** | `chunk-tag-backfill` (vault), `brush-tag-backfill`, sound-library categories | Tag everything from a fixed list so it can be searched | Universal tagger (M1) |
| **Teardown** | `plugins/udgt` and `teardowns/` (stages 0 to 8, owner's brief, answers verbatim) | An engine that reads a project and maps every choice to its reason | Teardown (M2) |
| **Doors** | `Look_Over_There` hosting `games/intern` and `games/rdwe` | A game entered from another and returning on its ending | Door protocol (M3) |
| **Memory log** | The owner's Memory Log; the Phase 1 log became an installable skill on 21 June | A chronicle that restores context for a new session | Memory skill (M4) |
| **Protocols in force** | No em dashes; songwriting format; PDF format; UI work runs UI/UX Pro Max first; concepts are deliverables | Standing rules for every session | Protocol pack (R1) |

---

## 3. The cycle (the owner's six modalities as the structure)

Each skill lives in one stage. A piece of work moves around the cycle, and the cycle feeds itself: compost becomes soil for the next seed, and mycelium carries it across districts.

| Stage | Meaning in this plan | Skills in it |
|---|---|---|
| **Seed** | An idea becomes a pitch, a question and a design | S1 to S4 |
| **Root** | The shared foundations every district uses | R1 to R5 |
| **Branch** | Parallel work: sessions, orchestrators, contracts | B1 to B5 |
| **Fruit** | Finished things: assets, builds, playtests, proofs | F1 to F5 |
| **Compost** | Failure and leftovers turned into learning | C1 to C4 |
| **Mycelium** | Hidden connections across everything | M1 to M5 |

---

## 4. The skill catalog

Each entry: what it does, built from (Evidence), and its gate. [Proposal] throughout. "Gate" means the owner's go-ahead is required where noted; the studio's own rule is that every write into the vault goes through a plan, a dry run and a recorded go-ahead.

### SEED: from idea to design

**S1. Pitch seed.** Turns a rough idea into a one-page pitch a human can judge. *Built from:* the pitch document the owner used as the first proof that people liked the ideas the AI helped create. *Output:* a pitch page plus a line in the proof ledger (Phase 4 item 2.10). *Gate:* none (a pitch is a draft).

**S2. Questionnaire builder.** Given a planning document, writes the owner's questionnaire: one question per decision, a proposed default, where the answer lands, the source it came from, dedup where two documents asked the same thing. Writes the answers back as `owner-answers.md`. *Built from:* `round11/questions.md`, `story/questions.md`, `owner-answers.md`. *Add:* a top line marking questions that change scope, cost, licensing or release, ordered first (Phase 4 item 2.3). *Gate:* none to ask; the owner's answers are the gate for what follows.

**S3. Design from template.** Produces a `DESIGN.md` in the fixed section order for any game, checking it against the pillars and the collection map (no game takes a verb that belongs to another). *Built from:* `esc-ZINE99/docs/DESIGN_TEMPLATE.md`, `PILLARS.md`, `COLLECTION.md`, `tools/validate.py`. *Gate:* the design is shown to the owner; the source works are never edited.

**S4. Source adaptation.** Takes a work from the vault and lists what is verbatim, what is added for the game, and what the author must approve or strike. *Built from:* the esc-ZINE99 rule that every design's last section lists what was added; the vault's verbatim rule for originals. *Gate:* the owner approves or strikes each addition.

### ROOT: foundations every district shares

**R1. Protocol pack.** The owner's standing rules as one loadable skill every session reads first: no em dashes, formats for songs and PDFs, UI/UX Pro Max first, concepts are the deliverables, work is always labelled as made with AI. *Built from:* the Memory Log's "protocols in force" and the studio vault's CLAUDE.md. *Why it matters:* sessions currently follow them only when reminded.

**R2. Game skeleton.** See section 5. A prebuilt, genre-aware starting structure so a new game begins as a content pack, not an engine.

**R3. Mechanic cards.** A card per mechanic: what it does, its data, its tests, which games use it, which rules (GDD numbers) it reads. *Built from:* the 34 modules in `Look_Over_There/shared/` and the verbs implemented in Who Did It (hide, dust, compare, autopsy, cover-up, vendettas, scrip, rent). A new game picks cards instead of reinventing them.

**R4. Rules as data.** One file of numbers and one file of rules per district, with a test that fails when a document and the data disagree. *Built from:* `spec.yaml`, `balance.json`, the GDD-as-source rule.

**R5. World registry.** One shared set of ids (places, characters, items, sounds, brushes, generations) so that two districts can refer to the same thing. *Built from:* `studio/library/catalog.json`, `sound-library/catalog.json`, `brushes/catalog`, the vault, the CREDITS ids. *Rule from Who Did It:* ids, once published, are frozen and append-only.

### BRANCH: parallel work

**B1. Session contract.** Generates a `SESSIONS.md` for a round: sessions with model, track, branch and owned paths; the interfaces between them; the merge order; a shared-root rule. *Built from:* `Who-Did-It/docs/SESSIONS.md`. *Addition, from the Part 3 findings:* a line saying which sessions may touch which files prevents the double-assignment the owner named as bottleneck 2.

**B2. Round packet.** A fixed set of files for each round: README, seams, scope, per-session briefs, a status file, handoffs. *Built from:* `docs/round10/`, `docs/round11/`, `docs/story/`.

**B3. Orchestrator.** A session that holds the standing rules, authorises merges only on the owner's say-so and green CI, writes resume notes "so any later session can resume without the chat", and runs the integration pass. *Built from:* session 6Z, `story/orchestrator-handoff.md`. *New duty:* end every round with the owner's decision inbox (Phase 4 item 2.2) and the skillify step (section 7).

**B4. Brief and retry rules.** A brief template for a sub-session (goal, owned paths, interfaces, definition of done, what it must not touch) and the retry rule: if a session fails or hits a limit, re-run the same brief on a stronger model. *Built from:* the seven round-8 failures re-run on Opus.

**B5. Merge queue.** The ordered merge of a round's PRs with a record of skipped ones. *Built from:* the 7 November merge queue and "five skipped PRs" cleanup.

### FRUIT: finished things

**F1. Asset intake.** Any generated or modelled asset (Meshy, Higgsfield, Blender) enters through one path: prompt, model and job id recorded, a credits row, a library entry, a master location. *Built from:* `assets.json`, the Meshy ledger, `studio/library`, the 118 merged interior props. *Known gaps recorded:* `woven_rug` is a flat patch; seven prop kinds have no model.

**F2. Build and publish.** One checklist for Pages and Railway: source setting, build, base path, relative paths. *Built from:* the Pages 404 episodes and `pages.yml`. [Owner] Pages and Railway are live.

**F3. Playtest log.** The log proposed in Phase 4 item 2.4: who played, stance toward AI, what happened, what the owner learned. No verdict field.

**F4. Proof ledger entry.** Each thing shown to someone, and their reaction, recorded as a reaction (Phase 4 item 2.10).

**F5. Release pack.** Trailer, screenshots, a one-page description and the credits, generated from the district's data. *Built from:* 6K (loading, transitions, trailer, budgets) and the Look Over There and Who Did It pages.

### COMPOST: failure becomes soil

The owner's practice: try, fail, and rebrand the failure as a success in another light. [Proposal] Make that practice a skill with one honest rule from Part 1: the failure stays labelled as a failure, and the "other light" is added beside it, never in place of it. That keeps the record true and keeps the compost useful.

**C1. Failure ledger.** For every failed session, test, abandoned mode or discarded design, write three lines: what failed, what it revealed, where the revelation applies next. *Evidence already in the record:*
- Seven failed round-8 sessions, retried on Opus (revealed: task size and model fit).
- The **quick mode** was removed in round 7 (7J); NPC fill and bots built for it were reused.
- **Right Door, Wrong Exit** was a testbed that fed walk scenes and mini-games into The Intern, and is now a door in Look Over There.
- The v1 `.brush` export that never opened in Procreate led to the byte-exact codec and a tool that works in Procreate and Photoshop [Owner].
- Chat-only projects that never got a repo (Sinyal Terakhir at 15 of 30 shots, Legacy Cafe) are compost waiting to be used.

**C2. Flake hunter.** About nine sessions were named for timing races or intermittent tests. One shared test-clock and wait helper, applied to every district's tests. *Built from:* Sessions 13 to 15 and the 22 October fixes.

**C3. Stale-statement sweep.** At each integration pass, list lines in READMEs and CLAUDE.md files that conflict with what the owner has said is true (for example "never run", "nothing is built yet"). Part 3 found several.

**C4. Leftover harvest.** Anything finished but unused (parked projects, unused props, spare lore works, an unused sound category) gets a line in the world registry marked *available*, so another district can take it.

### MYCELIUM: the hidden connections

**M1. Universal tagger.** One closed-vocabulary tagging skill generalized from the three that exist (vault chunks, brushes, sounds), applied to every made thing: sessions, decisions, mechanics, assets, failures. Tags are how connections get found. *Built from:* `chunk-tag-backfill`, `brush-tag-backfill`, the sound categories.

**M2. Teardown as connection engine.** The teardown tool already maps every design choice to its decision, data, code and history. Run it on every district and keep its output in one place. *Built from:* `plugins/udgt`, `teardowns/`. *Added question per choice:* where else does this appear?

**M3. Door protocol.** A fixed agreement for entering one district from another: spawn point, what is carried in, what is returned on exit, how the door looks. *Built from:* the way `games/intern` and `games/rdwe` plug into Look Over There.

**M4. Memory skill.** The owner's Memory Log, kept current and loadable at the start of any session. *Built from:* the Phase 1 log, converted to a skill on 21 June.

**M5. World map and ledgers.** One page generated each round: the portfolio register (Phase 4 2.11), the work ledger (2.8), the learning and transfer map (2.9: where each mechanic applies in finance, education and elsewhere), the proof ledger (2.10), the failure ledger (C1) and the decision inbox. This is the single view of the whole world.

---

## 5. Prebuilt game skeletons

**What a skeleton is.** Everything a game needs except its individual design. A new game supplies a **content pack** (its story, scenes, characters, rules numbers, art); the skeleton supplies the rest.

### 5.1 Layers [Proposal, built from Evidence]
| Layer | Holds | Evidence it exists |
|---|---|---|
| **0. Shell** | Hosting, build, Pages and Railway setup, CI on three operating systems, a hub entry, credits and manifest | `pages.yml`, `verify.yml`, `docs/MANIFEST.md`, `CREDITS.md` |
| **1. Walk and render** | First-person walk viewer with controller and touch, doors, lights, per-location Blender build files | Writing Museum viewer; `Look_Over_There` three.js game; `docs/BLENDER.md` |
| **2. Data schemas** | `game`, `scenes`, `endings`, `flags` schemas and validators that refuse drift | `esc-ZINE99/schemas/`, `tools/validate.py` |
| **3. Mechanic cards** | The picked modules (cloak, crossbow, keypad, loot, power, save, spawn...) with tests | `Look_Over_There/shared/`, Who Did It server rules |
| **4. Multiplayer core** | Lobby, parties by mode, accounts, host and admin guides, bots, soak, determinism checks | Who Did It (rounds 7 to 9, `docs/guides`, `tools/bots`, `tools/auto`) |
| **5. Local layer** | Results, saves and achievements on the device, story sections, an admin Studio for editing content | Who Did It Story P2 to P4; 9S to 9W admin Studio |
| **6. Content pack** | The one thing that is individual: design, lore, characters, numbers, art, audio | A `DESIGN.md` from the template; assets from the intake skill |

### 5.2 Skeleton types [Proposal]
- **Walk-in-3D** (layers 0 to 3, 5): a first-person world, solo or co-op, from the Look Over There line.
- **Multiplayer deduction** (layers 0, 2 to 5): the Who Did It line, with isometric or first-person client.
- **Narrative and 1D** (layers 0, 2, 5): static, no-build pages with choice logic, from The Intern's data-driven rooms and the 1D games of esc-ZINE99.
- **2D mode modules** (layer 2 plus a style): one module per 2D mode and 1D game, each in its own graphic style, from esc-ZINE99's `web/`.

### 5.3 The honest limit
A skeleton is extracted from games that already work, and each of those games is tangled with its own rules. [Proposal] Start with the structure that is **already uniform: esc-ZINE99**, where ten games share one folder layout, one design template, four schemas and four validators. Extract that skeleton first (cheapest, least coupled). Then pull mechanic cards out of Look Over There's `shared/`, since each is already its own module. Treat Who Did It's server and lobby (layers 4 and 5) last and carefully, because they are the most coupled and the most valuable.

---

## 6. The world model: districts and doors

[Proposal]
- **One shell, many districts.** Look Over There is the nearest thing to a world shell today (it already hosts two older games). Decide whether it becomes the shell, or whether the world shell is a separate, thinner hub. Either way, each game is a district with a door.
- **Shared identity.** One player profile (the accounts plan of 7 November), one save format (`shared/save.js` exists), one achievements store, across districts.
- **Shared libraries.** Sounds, generations, brushes, props and the vault are the same for every district through the registry (R5).
- **Shared lore.** The vault is the lore source; Who Did It's eight lore waves and the ten esc-ZINE99 adaptations already draw on it. The "origin" field (original, derived, auto-authored) keeps the author's own works separate from generated ones.
- **Scale comes from reuse, not from size.** A district that costs a content pack is a district that can be added without slowing the others.

---

## 7. How to do it without slowing down

1. **Rule of two.** Extract a skill only when something repeats a second time. Do not design a skill before a first working example exists (Part 1, F.2).
2. **Skillify step in every round.** Each orchestrator ends a round with one question: what did we do twice this round? Write each answer as a draft skill (a template, a checklist, a contract) in a `skills/` folder. Do not stop the round to do it.
3. **Draft first, harden later.** A draft skill is a markdown file with an example. It becomes a tested skill only after it has been used a third time.
4. **Harvest from existing sessions.** Several skills already exist as documents (questionnaires, SESSIONS.md, the design template). The first pass only moves them into a shared place and adds a header saying what they are.
5. **Keep the studio's gates where they matter.** Anything that writes into a vault, spends money, publishes or changes a brand gate keeps the checkpoint and go-ahead. Everything else runs without waiting.
6. **Ledgers are generated, not typed.** M5 pulls from repos and the session list.

### Order of extraction [Proposal, by payoff and least coupling]
1. S2 questionnaire builder, B1 session contract, B3 orchestrator (they exist as documents; mostly moving and labelling).
2. R1 protocol pack and M4 memory skill (cheap; every session benefits immediately).
3. R2 game skeleton from esc-ZINE99, and R3 mechanic cards from `Look_Over_There/shared/`.
4. C1 failure ledger and M5 world map (the compost and mycelium layers; they turn the history already recorded into connections).
5. F1 asset intake, F3 playtest log, F4 proof entry.
6. M1 universal tagger, M2 teardown across districts, M3 door protocol.
7. Multiplayer core (layers 4 and 5) as a skeleton, last.

---

## 8. Risks and honest limits

- **Skills freeze decisions.** A skill that encodes a design choice can keep a wrong choice alive. Each skill carries its date and its source, and the questionnaire builder asks the owner when a default is older than a set time.
- **Over-generalising.** Not every game needs every layer. A skeleton that tries to serve all games becomes the v1 "specified, not built" protocol again. Keep skeleton types small.
- **The owner's attention is the limit** (bottleneck 3). More skills mean more things to approve. Skills should reduce decisions: a skill that asks more questions than it saves should be cut.
- **Cross-project links cost upkeep.** The registry, tags and ledgers need a generator, or they become stale statements (Part 3 found several).
- **Rebranding failure as success needs a rule.** Keep the failure record true; add the lens beside it. This is the Part 1 honesty discipline, and it is also what makes compost usable.
- **The unverified.** Whether the Photoshop brush export, ComfyUI on a GPU, `ve publish` and the add-on tool choices work as described is the owner's report, not checked here. Skills built on them inherit that status.

---

## 9. The first week (a sketch, not a gate)

- **Day 1:** Create `skills/` with the questionnaire format, the SESSIONS.md contract and the design template copied in as drafts, each with a header (what it is, where it came from, an example).
- **Day 2:** Write the protocol pack and refresh the memory skill from the latest Memory Log.
- **Day 3:** List esc-ZINE99's skeleton (folder layout, schemas, validators) as a template; scaffold one empty game from it to see what breaks.
- **Day 4:** Make cards for five of `shared/`'s mechanics (what, data, tests, where used).
- **Day 5:** Run the first failure ledger over the recorded failures (section 4, C1) and the first generated world map.
Work on the games continues in parallel throughout.

---

## 10. What this is for

The owner builds to learn, to prove and to get work done. [Proposal] Skills serve all three: each repeatable skill is learning kept, a proof that can be shown (a pitch, a ledger entry, a door), and work done once and reused. A world is built from many small repeatable things that connect, and the skills are how the connections get made on purpose.

---

## 11. Questions for the owner (with proposed defaults)

*Answer **default** or **different**. The first four set direction.*

**K1. One world with districts and doors?** Treat every game as a district with a door in a shared world.
- Default: yes.

**K2. Which is the world shell?** Look Over There, or a separate thin hub?
- Default: Look Over There for now, since it already hosts two games; revisit when a third door is added.

**K3. Rule of two and draft-first?** Extract a skill only on its second repeat; harden it on its third.
- Default: yes.

**K4. Skillify step at the end of every round?**
- Default: yes, run by the orchestrator, no pause to the build.

**K5. First skeleton from esc-ZINE99?**
- Default: yes, then mechanic cards from `Look_Over_There/shared/`, with multiplayer last.

**K6. A `skills/` folder in each repo, or one shared repo?**
- Default: one shared folder in ROSW, linked from each repo, so every district reads the same copy.

**K7. Failure ledger in the compost rule: keep the failure labelled, add the new light beside it?**
- Default: yes.

**K8. Protocol pack: include "always say it is AI" and the no-em-dash rule?**
- Default: yes, both, plus the other protocols in force.

**K9. Which games get doors first?** Who Did It, the esc-ZINE99 games, or Sinyal Terakhir and the chat-only projects?
- Default: Who Did It first (largest, most reusable), esc-ZINE99 next.

---

## 12. Questions to ask NotebookLM

- Which patterns in section 2 already repeat three or more times?
- Which skills depend on others in the catalog, and in what order do they need to exist?
- What would a new game need from each skeleton layer?
- Which failures in the record could go into the failure ledger today?
- Where do the owner's old principles (seed, root, branch, fruit, compost, mycelium) show up in the work that has already been done?



---

# DOCUMENT 6 OF 6

# ROSW Owner Profile and Capacity Addendum

**Correcting how the other ROSW documents describe the owner's pace, attention and limits.**
Written 17 November 2026 for NotebookLM. This document does not change Parts 1, 2, 3, the Phase 4 Planning document or the Skillification Plan. Where any of them conflicts with this one about the owner's capacity, pace or constraints, **this document controls**.

---

## 0. Why this exists

The owner read the other documents and pointed out that they misconstrue the facts in three ways:
1. They treat the owner's attention as a bottleneck (a "human context limit", an "observer" risk) when the owner has kept up with the AI, with few interruptions, across eight months.
2. They read quiet days in the record as pauses or review lags, when the owner says those days were hand work done away from the machine.
3. They leave out the real constraints: usage-limit hits and problem-solving blocks.

This addendum records the owner as they describe themselves, what the record supports, which statements to read differently, and the constraints that actually limit output.

**Labels.** [Owner] is the owner's statement, which I could not verify. [Evidence] is something a file or record shows. [Inference] is my reading. [Unknown] marks what the record cannot say.

---

## 1. The owner, in their own account [Owner, 17 November]

The owner reports a full life alongside the work: a job, study, physical art and training. Personal details are not reproduced in this copy.

**Usage.** The owner has never missed a 5-hour usage limit or a weekly usage limit, and believes they are getting all of their credits. [Owner] I read this to mean that they use each window's allowance in full, every time, so the plan's allowance is the ceiling on machine output and is reached routinely. (If "never missed" means something else, tell me and I will correct it.)

**What quiet days mean.** On days with no machine output, the owner did things themself: typed notes, dreamed up ideas, played them through in their head. The amount of work the hand does never changes. The machine lengthens the output; it does not set it.

**How they meet doubt.** They never withhold that work was made with AI. They treat dislike, discrimination and envy as fuel, and take jealousy as a sign they are doing something right (Part 3, section 1B).

---

## 2. What the record supports [Evidence unless marked]

All figures are from the Claude Code cloud session list and the repositories. They cover cloud sessions only; chat work and hand work are not counted.

| Measure | Record |
|---|---|
| **Continuity** | From 18 October to 17 November (31 days), 25 days had at least one cloud session. The six quiet days were 19 and 20 October, 26 and 27 October, 5 November and 9 November. |
| **Volume** | 154 sessions in those 31 days, after 89 from March to 18 October. About 243 in total. |
| **Completion** | 144 of 154 (93.5%) completed in the latest 31 days. 75 of 89 (84%) completed in the earlier period. Eleven sessions failed across both periods, under 5% of the total. |
| **Recovery** | All 7 failures of 23 and 24 October were re-run on a stronger model the next day. The Pages 404 problem took five sessions over about five days and was worked through to a deploy. |
| **Decision turnaround** | The round-11 questionnaire file was created at 00:08 UTC on 30 October. The owner's 22 answers were submitted at 03:37 UTC the same night (about 3.5 hours later): 21 by default, 1 different. The plan was approved the same day. |
| **Decision volume** | Who Did It's decision log reached A614 by mid-November, from A1 on 10 October (about five weeks). |
| **Consistency of rules** | Standing rules from the owner (design approved through questionnaires; merge only on green CI and the owner's say-so; no em dashes; the protocols in the Memory Log) recur across chat, handoff documents and sessions without being restated by hand. |
| **Usage pattern** | Consistent with full use of the allowance: 154 sessions in 31 days; two sessions ended on recorded limit messages (28 September monthly spend, 3 October session); fleet rounds of 13 to 30 sessions in a day. The record cannot show per-window use. [Owner] says every window is used. |
| **Spread** | In the same 31 days the owner worked in at least eleven repositories, wrote essays and brand material in chat, and kept Railway and Pages live (owner). |

[Inference] Taken together, the record shows sustained high throughput over about eight months, alongside a job, school and the other commitments the owner lists, with decisions made quickly and few lost threads. It does not measure attention or retention directly, and I cannot verify the hours or the routine. But on the evidence it is not consistent with a person who is falling behind their own output.

### A labelling point, not a correction of the owner
The vault marks many of its later works `origin: auto-authored`. That field records who produced the final text (a pipeline), not whose idea it was. The owner says they originate the lore, models and ideas. Both can be true. The record has no field for who conceived a thing, so it cannot show the owner's authorship of ideas, only that of text. [Inference]

---

## 3. What the record cannot see

- **Hand work.** Typing notes, planning in their head, playing games through mentally, physical art, hiking and reading leave no trace in a session list. The earlier documents read some quiet days as review pauses; per the owner those are production days. [Owner]
- **Chat work.** Visible only through the Memory Log (Part 3, sections 3A and 3B).
- **The job and school.** A 20 to 30 hour working week and coursework sit outside every repository.
- **What the owner carries in mind.** The owner says they can keep up and can create all the lore, models and detail themself. [Owner] The record shows that what the owner has learned from playtests, for example, was not written into the repository. [Evidence] That is a gap in what sessions can read, not a limit of the owner's memory.

---

## 4. Statements in the other documents to read differently

| Where | What it says | Read it as |
|---|---|---|
| Part 3, section 1A; Phase 4, sections 1A and 2 | The "human context limit" is the current and unsolved bottleneck; the owner risks being an "observer". | The owner reports keeping up, and the record supports continuity. The binding constraints are on the machine side (section 5). Any "inbox" or "state page" is a convenience for sessions, not a repair to the owner. |
| Part 3, section 1A | "Output outruns review." | Not shown. A few pull requests waiting for review is a fact about those PRs, not evidence of overload. |
| Part 3, section 1A | "What the owner has learned lives in their head, not the repo." | True as a fact about what sessions can read. It is not a limit of the owner. |
| Part 3, sections 3A and 4 | Sessions arrive in bursts, followed by review pauses; the studio is one of several demands on the owner's attention. | Quiet days were often the owner's hand work. The owner's load is broader than the document shows (section 1) and the record still shows continuity. |
| Phase 4, section 2.6 | Pause new scope when a decision is open. | Optional, and only for a decision the owner flags. The owner does not want to slow down. |
| Phase 4, section 2.2 | A decision inbox limited to five items. | A convenience only. The owner can take more. |
| Phase 4 and Skillification Plan | Wording about attention as the limit, and about not slowing the work. | The goal is more, bigger and deeper work. Skills exist to multiply output, not to ration it. |
| Part 2 and Part 3 | Usage limits and problem-solving blocks appear only as footnotes, and Part 2 says to split heavy tasks and "check headroom". | The owner uses every window in full, so the allowance is always the ceiling. The question is output per unit of allowance, not headroom (section 5). |

---

## 5. The constraints that actually limit output

The earlier documents left these out or underplayed them. They are on the machine and tool side, not on the owner's side.

### 5.1 Usage limits are the binding constraint, and the owner uses all of the allowance
[Owner] The owner has never missed a 5-hour limit or a weekly limit and believes they use all their credits. [Inference] This makes the plan's allowance the permanent ceiling on machine output, not an occasional interruption. Each window is spent in full, so what the owner can build in a week is set by how much work each token of allowance produces.

What the record shows [Evidence]:
- **Monthly spend limit**, 28 September: "Museum walkthrough refinement" ended with a spend-limit message.
- **Session limit**, 3 October: "Game scene polish and mechanics" ended with a session-limit message.
- **Seven failures on 23 and 24 October** (7M, 8A, 8E, 8F, 8I, 8N, 8V). The causes were not read. [Unknown] whether they were limits. Each was re-run on Opus the next day, which means the work was paid for twice.
- **Context size.** Finished sessions ranged from about 100,000 to over 600,000 tokens (artist timeline 603k; dining-room 3D 571k; world art 5K 576k). Large sessions spend allowance quickly.
- **Sessions that spend allowance without adding output** [Inference from titles]: about nine flaky-test and timing sessions, five Pages 404 sessions, and the retried failures. These are the clearest places where allowance turns into rework.
- **Vendor caps.** Higgsfield's 6-concurrent-job limit (Memory Log).
- **The owner's routine fits the window structure.** The owner often wakes, starts Claude coding, and goes back to bed. [Owner] [Inference] That uses a window while asleep, so the allowance is working while the owner rests. Whether it is deliberate timing is the owner's to say.

### 5.2 Problem-solving blocks [Evidence]
| Block | Record |
|---|---|
| Pages 404 and source setting | Five sessions, 28 September to 2 October |
| Flaky and timing-dependent tests | About nine sessions (22 October, 24 October, 11 to 16 November) |
| Blocked sessions | "Who Did It multiplayer game plan" (9 October), "Game scenes and level connections" (4 November), 5M (18 October, waiting on three answers) |
| Tool installs and setup | "MCP server installation issue" (31 October), "Blender tools setup" (10 November), "Railway connection setup" (23 October) |
| Hardware | The owner's computer has no GPU, so ComfyUI's models cannot run locally; the cloud version is unused. [Owner] |
| File and folder chaos | "OneDrive to Google Drive migration" and "Duplicate folders investigation" (31 October) |
| Asset gaps | `woven_rug` is a flat patch; seven prop kinds have no model. Meshy output merged by hand. |
| Terms | Higgsfield's terms of service, held as an open question (DECISIONS 12 to 14) |

### 5.3 What the pattern shows [Inference]
Every block has a visible follow-up (a fix session, a re-run, a workaround) usually within a day to a few days, which fits the owner's account: they look for solutions and do not dwell on problems. The usage ceiling and the tool and hardware blocks, not the owner's attention, are what stand between the owner and more output. A more accurate framing of the earlier "three bottlenecks" is:
1. The owner's typing speed (solved by the swarm).
2. Swarm organisation and overlapping work (largely solved by contracts and orchestrators).
3. **The usage allowance and machine-side ceilings:** the 5-hour and weekly limits, which the owner fully uses; context size; blocked tasks; missing hardware; tool friction. This is the live constraint on output.

### 5.4 What this means for how sessions should work [Inference; proposals are listed for the Phase 4 document when the owner next updates it]
- **Allowance is the budget.** Each round could carry a rough spend plan by session and model, so the owner's full use goes to new work, not rework.
- **Rework is the leak.** Retries after failure, flaky tests and long-context sessions spend allowance without producing output; the failure ledger and flake hunter in the Skillification Plan target exactly these.
- **Match model to task.** The existing split (Sonnet for implementation, Opus for art and decisions, Fable for fixes and UI) is a spend decision as well as a quality one.
- **Keep contexts small.** Per-tier compaction windows (300k, 400k, 500k, 800k) are already a spend control; the largest sessions are the most expensive.
- **Use windows on purpose.** Because windows reset on a clock, work queued for when a window opens would let the allowance run during sleep or the owner's job hours. The owner already does a version of this by hand.
- **Repeatable skills save allowance.** A skill replaces long re-derivation with a known recipe, so the same allowance produces more. This is the strongest argument for the Skillification Plan.

---

## 6. How to categorise the owner [Inference]

The owner asks to be categorised as an anomaly and not a typical user. The record supports this description of the profile, without claiming more than it shows:
- **A sustained high-output single operator.** About 243 cloud sessions in eight months, 154 of them in the last month, across more than ten repositories, alongside a 20 to 30 hour job, school and physical art.
- **A hybrid worker.** Hand work (notes, ideas, mental play-through, physical art) and machine work run in parallel, and the machine extends the hand's output without replacing it.
- **An orchestrator who is also the decider.** Decisions return within hours, with standing rules that carry across sessions.
- **A builder who treats failure as material.** Failed sessions are re-run, retired modes are reused, and blocked work is routed around (see the Skillification Plan's compost stage).
- **An outlier on the usual assumptions.** Ordinary guidance about pacing, workload, review limits and "slowing down" does not describe this profile and should not be applied to it by default.

[Unknown] Any claim about the owner's cognition (for example, a measured context limit) cannot be made from this record. The documents should describe throughput and continuity, which the record shows, and leave the rest to the owner.

---

## 7. Working agreement for any session reading this [Owner's stated preferences]

- Do not suggest slowing down. Suggest how to do more, to greater depth.
- Frame problems as problems with solutions, and bring solutions.
- The owner is the pivot. The machine's limits (usage, context, hardware, tools) are the constraint to design around.
- Always label work as made with AI. Never withhold it.
- No em dashes. Follow the protocols in the Memory Log.
- Do not describe the owner as a typical user. Describe them as an outlier, with evidence.

---

## 8. Open facts only the owner can supply

So the record can describe the real constraints:
- Whether any limit has ended a task partway through (as opposed to a window being fully used), and how often.
- The plan tier and any caps that apply (spend, sessions, concurrent jobs).
- Which blocks cost the most time (hardware, tools, vendor limits, test flakiness).
- Roughly how many hours a week go to hand work versus machine work.

---

## 9. Questions to ask NotebookLM

- What does the record show about the owner's continuity over eight months?
- Which constraints on output are on the machine side, and what has the owner done about each?
- If the owner uses every usage window in full, where does the allowance go, and where is it lost to rework?
- How should earlier statements about attention and observer risk be read?
- Compare the owner's reported load (job, school, art, hiking) with the volume of recorded work.
- Which quiet days in the record are explained by hand work, according to the owner?

---

## 10. Change log

| Date | Change |
|---|---|
| 17 Nov 2026 | Created. |
| 17 Nov 2026 | Added the owner's statement that they have never missed a 5-hour or weekly usage limit and use all their credits. Usage is now described as the permanent ceiling on machine output; section 5.1 rewritten, section 5.4 added, open facts updated. |
