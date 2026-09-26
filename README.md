# Pipelines

One repo, multiple tools. Each tool gets a self-contained folder. The
creative-writing tool is used from this repo, so its skills and agents live once
at the repo root under `.claude/` and load whenever this repo is the working
directory. The ui-design tool is a Claude Code plugin published on its own, so
its skills and agents live inside it, under `plugins/ui-design/`.

```
INDEX.md               generated index of the tools, skills and agents
.claude/skills/        creative-writing-pipeline, chunk-tag-backfill
.claude/agents/        creative-writing-{chunk-tagger,drafter,librarian-native}
CLAUDE.md              repo conventions; points at the vault's own CLAUDE.md
creative-writing/
  vault/               the Obsidian vault: 63 works, _Annotations/,
                       _ChunkTags/, _Idea_Library/, tools/, CLAUDE.md
  pipeline/            the checkpointed pipeline that writes into that vault
plugins/ui-design/     the ui-design plugin: everything that is published
  .claude-plugin/      plugin.json and marketplace.json
  skills/, agents/     ui-design-{catalog,catalog-refresh,multipart},
                       ui-design-{catalog-reviewer,search-part,page-reviewer}
  spec.yaml            the declared contract; validate-contract.py enforces it
  INDEX.md, ROUTER.md  the catalog's vocabulary (generated) and how to route a brief
  catalog/             data/ and scripts/: the search catalog, stdlib only
  maintenance/         validators, relevance gate, refresh scripts, verify.py
  references/          prose the ui-design-catalog skill reads on demand
  README.md, LICENSE, NOTICE, CHANGELOG.md
```

Paths in the creative-writing skills and agents are relative to this repo
root. Vault-relative paths (as `vault_search.py` reports them, e.g.
`03_Stories/06_Melting_Away.md`) take a `creative-writing/vault/` prefix. Paths in
the ui-design skills and agents start from `${CLAUDE_PLUGIN_ROOT}`, the plugin's
install directory.

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

## UI design plugin

A local search catalog of UI design decisions, plus a generator that turns a
query into a contrast-checked design system, packaged as a Claude Code plugin in
[`plugins/ui-design`](plugins/ui-design). Its own
[README](plugins/ui-design/README.md) covers what it contains, how to install it,
what it will and will not write, how the catalog is verified and refreshed, and
where its data comes from; [`NOTICE`](plugins/ui-design/NOTICE) lists the upstream
sources, and the MIT licence is [`plugins/ui-design/LICENSE`](plugins/ui-design/LICENSE).

From this repo:

```powershell
python plugins/ui-design/maintenance/verify.py          # every gate, from any directory
python plugins/ui-design/catalog/scripts/search.py "keyboard focus modal" --domain ux
claude --plugin-dir ./plugins/ui-design                  # load its skills for a session
```

The plugin is published from its own repository, never from this one, because this
repo also holds the private vault. The steps are in [`CLAUDE.md`](CLAUDE.md), under
"Publishing the plugin".
