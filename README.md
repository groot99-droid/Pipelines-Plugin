# Pipelines

One repo, multiple tools. Each tool gets a self-contained top-level folder;
skills and agents live once at the repo root under `.claude/`, so they load
whenever this repo is the working directory.

```
INDEX.md               generated index of the tools, skills and agents
.claude/skills/        creative-writing-pipeline, chunk-tag-backfill,
                       ui-design-catalog, ui-design-catalog-refresh,
                       ui-design-multipart
.claude/agents/        creative-writing-{chunk-tagger,drafter,librarian-native},
                       ui-design-{catalog-reviewer,search-part,page-reviewer}
CLAUDE.md              repo conventions; points at the vault's own CLAUDE.md
creative-writing/
  vault/               the Obsidian vault: 63 works, _Annotations/,
                       _ChunkTags/, _Idea_Library/, tools/, CLAUDE.md
  pipeline/            the checkpointed pipeline that writes into that vault
ui-design/
  spec.yaml            the declared contract; validate-contract.py enforces it
  INDEX.md, ROUTER.md  the catalog's vocabulary (generated) and how to route a brief
  catalog/             data/ and scripts/: the search catalog, stdlib only
  maintenance/         validators, relevance gate, refresh scripts, verify.py
  references/          prose the ui-design-catalog skill reads on demand
```

Paths throughout this file and in every skill/agent are relative to this repo
root. Vault-relative paths (as `vault_search.py` reports them, e.g.
`03_Stories/06_Melting_Away.md`) take a `creative-writing/vault/` prefix.

## Creative-writing pipeline

Turns an idea into a vault-integrated piece in the Obsidian vault at
[`creative-writing/vault`](creative-writing/vault), following that vault's own
rules in [`creative-writing/vault/CLAUDE.md`](creative-writing/vault/CLAUDE.md)
instead of re-deriving them each time. Open that folder directly in Obsidian —
its `.obsidian/` config travels with it.

Stages: **intake → reference pull → outline → draft → self-revision →
vault integration**. Every stage is a checkpoint — nothing moves to the
next stage until the author reviews the previous one's output. The final
stage (vault integration) additionally requires an explicit `--confirm`
before it writes anything to the real vault; without it, it only prints a
dry-run preview.

All four vault modes — `essay-self-help`, `horror-prose`, `epic-fantasy`,
and `confessional-poetry` — are implemented in `spec.yaml`. `unclassified`
is deliberately left a stub: per `CLAUDE.md`, a piece in that bucket
means asking the author which register they want rather than defaulting
to a fixed mode's rules.

### Three execution backends: local / native / mcp

The pipeline's generation work runs through one of three named backends:

- **local** (`ollama`) — the standalone script's default. **Done.** Runs
  fully offline via `llm.py`'s Ollama backend; see "The script's drafting
  backend" below.
- **native** (`claude`) — the live Claude Code skill session. **Done, via
  the skill, not `llm.py`.** The skill delegates its three heavy
  generation stages (outline, draft, self-revision) to a dedicated
  `creative-writing-drafter` subagent
  (`.claude/agents/creative-writing-drafter.md`), and
  its reference-condensation work (reference_pull, self_revision's
  connection checks) to `creative-writing-librarian-native`
  (`.claude/agents/creative-writing-librarian-native.md`)
  instead of Ollama — see "The librarian" below. Neither subagent has
  Write/Edit/Agent access; both return text only, and the top-level
  Claude still owns every checkpoint and all vault writes. There's no
  headless-CLI equivalent for this backend: a subagent is a feature of a
  live Claude Code session, not something `run_pipeline.py` can invoke
  over a wire.
- **mcp** (`gemini`) — Google Gemini as an alternative to `local`, via
  `llm.py`'s `backend="gemini_mcp"`. **Done.** It calls the Gemini API
  directly (same key and default model as the Gemini MCP plugin's
  `ask_gemini`), since a headless script can't speak MCP stdio. Needs
  `pip install google-genai` and a key: put `GEMINI_API_KEY=...` in
  `creative-writing/pipeline/.env` (gitignored, loaded by `llm.py`, overrides any shell
  value; see `.env.example`) or set `$env:GEMINI_API_KEY`; optional
  `$env:GEMINI_MODEL` (default `gemini-3.6-flash`). Select it for drafting
  with `$env:PIPELINE_LLM_BACKEND = "gemini_mcp"`, and/or for the librarian
  with `$env:LIBRARIAN_BACKEND = "gemini_mcp"` (or `librarian.py digest
  ... --backend gemini_mcp`). The two settings are independent. Note that
  this sends vault text to Google's API.

### Two entry points, one spec

[`creative-writing/pipeline/spec.yaml`](creative-writing/pipeline/spec.yaml) is the single
source of truth for the pipeline's stages, prompts, per-mode rules, and
the librarian's defaults. Neither of the two ways to run the pipeline
hardcodes its own copy of that logic:

1. **Claude Code skill** — inside a Claude Code session opened on this repo,
   invoke the
   [`creative-writing-pipeline`](.claude/skills/creative-writing-pipeline/SKILL.md)
   skill. Claude reads `spec.yaml` directly and walks the stages
   conversationally, using its own generation for outline/draft/revision.

2. **Standalone script** — `creative-writing/pipeline/run_pipeline.py`, a CLI
   that drafts each stage via `creative-writing/pipeline/llm.py`'s pluggable
   backend and persists state + artifacts under
   `creative-writing/pipeline/runs/<run-id>/`
   between invocations, so each `continue` call picks up where the last
   one stopped.

Both entry points draft with **Claude or Ollama, never a raw file dump**:
reference material (worked examples, `vault/tools/vault_search.py` hits, and
self-revision's connection checks) is read and condensed by
**`librarian.py`** first — see "Ollama as librarian" below — rather than
being read in full by whichever model is doing the actual writing.

### The librarian: two implementations, one digest format

The librarian's job is narrow and specific: read the *exact* vault files
a stage wants referenced and hand back a condensed Markdown digest
(bullet summary + a checked "Verbatim quotes" list) — never draft prose
itself. This keeps raw vault files out of whichever model is actually
writing. There are two implementations, both producing the same digest
format so downstream handling (treating an `[UNVERIFIED]`-flagged quote
as non-citable) doesn't care which one ran:

- **`librarian.py`** (Ollama by default, Gemini via `LIBRARIAN_BACKEND=gemini_mcp`) — used by the standalone script,
  which has no live subagent to call. See "Setup" below.
- **`creative-writing-librarian-native` subagent** (Claude-only, no
  Ollama) — used by the skill by default in a live Claude Code session.
  No server to start, no CPU-bound local-inference latency; Claude reads
  the file directly and condenses it under the same never-fabricate-a-
  quote discipline, enforced by instruction rather than a separate
  programmatic check. The skill falls back to `librarian.py` only if the
  author explicitly asks for the Ollama path.

Every quote either implementation returns is checked against the source
file before being handed to the drafter — `librarian.py` does this
programmatically (tolerant of curly-vs-straight quote/apostrophe
punctuation, which models routinely "clean up" without actually
fabricating content); the native subagent does it by only ever
copy-pasting from text it just read. An unverified quote is flagged
inline as `[UNVERIFIED]` either way, never silently trusted or dropped.

**Setup** (PowerShell):
```powershell
ollama serve             # start the local server, if not already running as a service
ollama pull llama3.1:8b  # one-time download of the default model (override via $env:OLLAMA_MODEL)
```
If `ollama serve` crashes immediately with `panic: bad origin: ...`, you
likely have an `OLLAMA_ORIGINS` environment variable set (e.g. from an
Obsidian Ollama plugin) whose entries don't satisfy Ollama's CORS
validation — it needs a `*` wildcard or an allowed URL scheme. Fix it with:
```powershell
[Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', 'app://obsidian.md/*', 'User')
```
(adjust the value to whatever origin you actually need; open a new
terminal afterward so the change takes effect).

`librarian.py` can also be run standalone, e.g. to sanity-check it:
```powershell
cd creative-writing\pipeline
python librarian.py digest 11_Essays/02_The_Architecture_of_Being.md --query "duality and presence"
```

Note: CPU-only local inference is slow — expect a `llama3.1:8b` condensation
call to take one to several minutes on modest hardware, not seconds.

### The script's drafting backend

`run_pipeline.py`'s own drafting (intake/outline/draft/self-revision/
vault-integration-metadata) uses `llm.py`'s pluggable backend, independent
of the librarian:

- **`ollama`** (default) — no API key needed. Uses `$env:OLLAMA_MODEL`
  (default `llama3.1:8b`) and `$env:OLLAMA_HOST` (default
  `http://localhost:11434`).
- **`anthropic`** — opt in with `$env:PIPELINE_LLM_BACKEND = "anthropic"`
  and `$env:ANTHROPIC_API_KEY = "sk-ant-..."`. Requires `pip install anthropic`
  (see `requirements.txt`).
- **`gemini_mcp`** — Gemini via google-genai; see "Three execution backends"
  above.

  ```powershell
  cd creative-writing\pipeline
  pip install -r requirements.txt
  # Ollama serving (see above) is enough to get started -- no key needed.

  python run_pipeline.py new --mode essay-self-help --idea "A short essay about persistence"
  ```

  Once a run is created (note the `run-id` it prints — the slugified idea
  plus a short random suffix, e.g. `a-short-essay-about-persistence-3f8a1c`):
  ```
  # review runs/<run-id>/idea.md, then:
  python run_pipeline.py continue <run-id>
  # review references.md, then outline.md, then draft.md, then...
  python run_pipeline.py continue <run-id>
  python run_pipeline.py continue <run-id>
  python run_pipeline.py continue <run-id>
  # review draft_revised.md and revision_notes.md, then preview the vault write:
  python run_pipeline.py continue <run-id>
  # once happy, actually write it into the vault:
  python run_pipeline.py continue <run-id> --confirm

  python run_pipeline.py status <run-id>   # check progress at any time
  ```
  If a stage fails (e.g. Ollama isn't serving, or the Anthropic key wasn't
  set), it prints a clean error and leaves the run's state untouched — fix
  the issue and run the same `continue <run-id>` command again to retry
  that stage; nothing is skipped or corrupted.

  Smaller local models are less reliable than Claude at the strict JSON
  formatting the vault-integration stage's metadata step asks for. That
  stage already fails loudly (no partial/garbage vault write) rather than
  guessing if parsing fails — if you hit that, retry, or temporarily switch
  to the `anthropic` backend for that one run.

The vault-integration stage automates the vault's existing 5-step
Maintenance procedure (see `creative-writing/vault/CLAUDE.md`) — it doesn't invent a new process,
just runs the existing one without you having to remember every step.

### Extending to another mode

Add a new entry under `modes:` in `spec.yaml` (worked examples, structure
rhythm, voice notes, target folder) with `status: implemented`. The six
stages and both entry points work unchanged — they read the mode's rules
out of the spec rather than having them hardcoded per mode.

## UI design catalog

A local search catalog of UI design decisions, plus a generator that
turns a query into a contrast-checked design system, in
[`ui-design`](ui-design). It exists so visual choices come from curated
data instead of being invented from memory. The catalog is a BM25 index
over curated files:

- 79 searchable styles (50 active)
- 192 product palettes, each with an exact reasoning profile
- 74 font pairings, and **1,934 approved Google Fonts** with
  **8 review exclusions** held out for licence review
- 119 UX guidelines
- 105 curated icons, as **105 curated rows** checked against the
  **1,512-icon upstream Phosphor manifest**
- 17 GSAP presets and 25 chart types
- 22 technology stacks

### Two halves, one rule

[`ui-design/catalog`](ui-design/catalog) is what the skill runs: the data
and the search scripts. It uses only the Python standard library and never
touches the network. [`ui-design/maintenance`](ui-design/maintenance) is
upkeep: the validators, the relevance gate, the refresh scripts and
`verify.py`. It alone holds the one dependency (`pyyaml`), the network
calls, and the one secret (`GOOGLE_FONTS_API_KEY`, see `.env.example`
there). The split is enforced: `validate-contract.py` fails if anything
under `catalog/` imports a third-party package.

### Searching

The [`ui-design-catalog`](.claude/skills/ui-design-catalog/SKILL.md) skill
drives it; the script is also usable directly, from the repo root:

```powershell
python ui-design/catalog/scripts/search.py "beauty spa wellness service" --design-system
python ui-design/catalog/scripts/search.py "keyboard focus modal" --domain ux
python ui-design/catalog/scripts/search.py "suspense streaming" --stack nextjs
```

`--design-system` also emits W3C design tokens (`-f dtcg`) or a shadcn/ui
`:root` block (`-f shadcn`). Add `--persist` only together with an
`--output-dir` that points **outside this repo**, at the project you are
designing for: without it the generated `design-system/` folder is written
into the current directory, which from here is this repo.

### Routing, indexes and multipart agents

Search only matches the catalog's own words, so a brief in free wording can
rank the wrong row first: `freelancer invoicing SaaS fintech trustworthy`
matches *Freelancer Platform* ahead of *Invoice & Billing Tool*, with no
warning. Three pieces address that.

- [`ui-design/INDEX.md`](ui-design/INDEX.md) lists the catalog's vocabulary
  (product types and keywords, style ids, font pairings, landing patterns,
  stacks), and [`INDEX.md`](INDEX.md) lists the tools, skills and agents. Both
  are generated by `ui-design/maintenance/generate-index.py`, and `verify.py`
  fails when either is stale or a skill or agent is missing from the root one.
- [`ui-design/ROUTER.md`](ui-design/ROUTER.md) says which mode, domain and query
  fits a request and what to do when a match looks wrong.
  `search.py --diagnostics` prints the confidence fields, and
  `route.py "<brief>"` cross-checks the product rows and warns when they
  disagree.
- The [`ui-design-multipart`](.claude/skills/ui-design-multipart/SKILL.md) skill
  fans a wide brief out to one `ui-design-search-part` agent per search, or a
  built page out to four `ui-design-page-reviewer` agents (one per area), then
  checks the answers with `merge_parts.py`: every part returned exactly once,
  and no review finding citing a rule that is not in the quick reference. One
  search takes milliseconds, so the router only recommends fan-out at four or
  more parts.

### The contract

[`ui-design/spec.yaml`](ui-design/spec.yaml) declares the search domains,
the stacks, the output formats, the design dials, the exit codes and the
persistence rule. The code implements them; the spec cannot be read by the
standard-library-only catalog, so
[`validate-contract.py`](ui-design/maintenance/validate-contract.py) is
what keeps the two from drifting apart. It also checks the skills, the
agents, the documented commands and the counts above against the data.

### Verifying

One command runs all ten gates and stops at the first failure, printing
the exact command to re-run it:

```powershell
pip install -r ui-design/maintenance/requirements.txt
python ui-design/maintenance/verify.py
```

There is no CI in this repo; `verify.py` is the gate.

### Refreshing the upstream catalogs

The Google Fonts and Phosphor catalogs are derived from upstream. The
[`ui-design-catalog-refresh`](.claude/skills/ui-design-catalog-refresh/SKILL.md)
skill fetches them, stages candidates under
`ui-design/maintenance/candidates/` (gitignored), diffs them against the
live rows and has the read-only `ui-design-catalog-reviewer` agent check
each one. It then stops. Promoting a candidate is an editorial decision
with a licensing dimension (see
[`ui-design/SOURCE-RESEARCH.md`](ui-design/SOURCE-RESEARCH.md)), so it
needs the author's explicit approval.

### Provenance and licence

The catalog is derived from
[ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
by Next Level Builder, released under the MIT licence, which is carried at
[`ui-design/LICENSE`](ui-design/LICENSE). It was imported as a plain copy
with no history. The installer, the marketplace manifest, the gallery and
the demo project were left behind. The origin of individual data rows is
recorded in `ui-design/catalog/data/data-provenance.json`.
