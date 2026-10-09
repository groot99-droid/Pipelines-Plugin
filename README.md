# ROSW

**New here?** Open [`docs/index.html`](docs/index.html) for a page per tool, and run
`python docs/setup_keys.py` to add any API keys (most of ROSW needs none).

One repo, multiple tools. Each tool gets a self-contained folder. The
creative-writing tool is used from this repo, so its skills and agents live once
at the repo root under `.claude/` and load whenever this repo is the working
directory. The studio tool is used from this repo too, and keeps its skill
there. The ui-design tool is a Claude Code plugin published on its own, so
its skills and agents live inside it, under `plugins/ui-design/`.

```
INDEX.md               generated index of the tools, skills and agents
.claude/skills/        creative-writing-pipeline, chunk-tag-backfill,
                       studio-pipeline
.claude/agents/        creative-writing-{chunk-tagger,drafter,librarian-native}
CLAUDE.md              repo conventions; points at each vault's own CLAUDE.md
creative-writing/
  vault/               the Obsidian vault: 63 works, _Annotations/,
                       _ChunkTags/, _Idea_Library/, tools/, CLAUDE.md
  pipeline/            the checkpointed pipeline that writes into that vault
studio/
  vault/               a second Obsidian vault: one note per made thing, the
                       brand gates, SCHEMA.md, CLAUDE.md
  pipeline/            spec.yaml, the bookkeeper and the note writer
  docs/                what was carried from Creative-Headquarters, and how
docs/                  HTML pages for new users, and setup_keys.py for API keys
.claude-plugin/        marketplace.json: installs plugins/ui-design from this repo
plugins/ui-design/     the ui-design plugin: self-contained
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

Paths in the creative-writing and studio skills and agents are relative to this
repo root. Vault-relative paths (as `vault_search.py` reports them, e.g.
`03_Stories/06_Melting_Away.md`) take a `creative-writing/vault/` prefix; a
studio note's path takes `studio/vault/`. Paths in
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

### Plot logic and registers

A story is a chain of *but* and *therefore*, never *and then*. The outline stage
now requires a **causal ledger**: one table, a row per beat, each row naming the
earlier beat it depends on and a phrase copied from that beat's `Changes`. A
checker (`creative-writing/pipeline/plot_logic.py`) verifies the phrase is really
there, the chain's shape, and that the ending is legal for the mode; a failing
ledger gets one automatic repair pass, and the report is written beside the
outline (`plot_logic_report.md`). It cannot judge whether a link is true; that
stays with the author at the checkpoint.

A **register** (`liminal`, `psychedelic`, `cosmic`) is an overlay on a mode: the
mode says how the piece sounds, the register says what kind of world it runs in.
It adds one state column to the ledger and a few shape rules.

```
python creative-writing/pipeline/run_pipeline.py new --mode horror-prose --register cosmic --idea "..."
python creative-writing/pipeline/plot_logic.py check outline.md --mode horror-prose --register cosmic
python -m unittest discover -s creative-writing/pipeline/tests
```

The rules are in `creative-writing/vault/CLAUDE.md` ("Plot logic"); the reasoning
and worked examples, including ledgers of the vault's own pieces, are in
`creative-writing/vault/_Craft/`.

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
  `pip install google-genai` and a key: run `python docs/setup_keys.py` and paste it
  into the page that opens. It is saved to `~/.rosw/keys.env`, outside the repo, which
  `llm.py` loads and which overrides any shell value. Or set `$env:GEMINI_API_KEY`; optional
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

## Studio pipelines

Makes one thing at a time through six checkpointed stages, and leaves a note in
the vault at [`studio/vault`](studio/vault) that says how it was made, what is
decided about it, and what happens next. Its own [README](studio/README.md)
covers what it contains, what it writes and when, and what it does not do. Its
rules are in [`studio/vault/CLAUDE.md`](studio/vault/CLAUDE.md).

Stages: **intake → context → recipe → execute → review → record**. Every stage is
a checkpoint. Execute and record each need an explicit go-ahead as well. Nothing
is made before every constraint it needs has been resolved and its source shown;
a constraint that cannot be sourced is asked for, never guessed.

Nine pipelines are declared in
[`studio/pipeline/spec.yaml`](studio/pipeline/spec.yaml) and eight are
implemented: `ui-direction`, which runs the ui-design catalog under the studio's
brand gates; `brand-gate`, which writes a brand gate from an interview with the
author; `still-image`, `video-shot` and `music-cue`, through the Higgsfield
connector; `edit-2d`, through the Adobe connector; `scene-3d`, which builds one room of the
Writing Museum for a work the author names; and `scene-blender`, through the
Blender scene connector. Each names the connector tools it may call, spends
nothing before the execute go-ahead, and keeps what the author keeps under
`studio/assets/`. `ui-build` and `brush` are entries that say what each needs;
`brush` has its packer (`studio/pipeline/brush_pack.py`) and waits for the
designer app.

The generations library, [`studio/library`](studio/library), catalogues every
image, video, audio clip and 3D model the author has made on Higgsfield, with
thumbnails and a page to look through them. The `higgsfield-library-sync` skill
brings it up to date; originals are downloaded on request and are not versioned.

The hub, [`studio/hub`](studio/hub), is a local page over the vault's notes, the
runs and the gates: `python studio/hub/serve.py`, then open
`http://127.0.0.1:8765/`. Its Writing tab links to the Writing Museum's library
and viewer on their own server (`--museum-port`, default 8768) and says whether
that server is up; the hub serves none of the museum itself. On Windows,
`studio/hub/launcher/Install-Shortcut.ps1` puts a shortcut on the Desktop and in
the Start Menu, and `Start-Hub.ps1 -Museum` starts both servers.

It carries the ideas of Creative-Headquarters into this repo.
[`studio/docs/INVENTORY.md`](studio/docs/INVENTORY.md) is what that repo
contained; [`studio/docs/IDEAS.md`](studio/docs/IDEAS.md) is what became of each
idea.

From this repo, in a Claude Code session, use the `studio-pipeline` skill. There
is no standalone script: the tools a stage calls exist only inside a live
session.

```powershell
python -m unittest discover -s studio/pipeline/tests     # the studio's own check
python studio/pipeline/studio_run.py status              # every run
python studio/pipeline/content_md.py lint --all          # every note in the vault
```

## Writing Museum

A walkable 3D museum of the creative-writing vault, fashioned after the Chronicle
Museum of `Earth_Worldbuild`: a hall with a door to every scene, and one room per
work whose passages hang on the walls as verbatim text panels, cited to their vault
path and lines. The room's door, walls, floor, frames and light follow the work's
own mode, moods and motifs through one reference table. The engine and the data
live in [`writing-museum/`](writing-museum) (its [README](writing-museum/README.md)
says how to view and build it); every scene is made through the studio's
`scene-3d` pipeline and has a note in `studio/vault/writing-museum/3d/`. Beside the
3D viewer is **the library** (`web/explore.html`): a flat page to read every work of
the vault, passage by passage, and look through the rooms, each with its colours,
its door and where every value came from.

Both are published on GitHub Pages, with the docs pages, on every push to `main`
(`.github/workflows/pages.yml`): the library at
<https://groot99-droid.github.io/Pipelines-Plugin/museum/web/explore.html> and the
museum at <https://groot99-droid.github.io/Pipelines-Plugin/museum/web/index.html>.
The deploy rebuilds the museum from the vault, so a merged `scene-3d` run's room is
on the site a few minutes later. The workflow is the site's only publisher: its first
step sets the repository's Pages source to GitHub Actions, because a "deploy from a
branch" source publishes `docs/` alone on the same push, after it, and drops `museum/`.

```powershell
python -m http.server 8768 --directory writing-museum          # then open /web/index.html, or /web/explore.html to read
python writing-museum/build/build_museum.py build --lint        # the layout lint
python -m unittest discover -s writing-museum/build/tests       # the builder's tests
node writing-museum/tools/walk_test.mjs                         # the browser walk-through
```

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

Install it from this repo in Claude Code with
`/plugin marketplace add groot99-droid/Pipelines-Plugin`, then
`/plugin install ui-design@rosw`. Release steps are in [`CLAUDE.md`](CLAUDE.md), under
"Publishing".
