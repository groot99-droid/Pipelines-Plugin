# CLAUDE.md — ROSW

## What this repo is

A single repo holding multiple tools, each in its own folder. A tool folder is
self-contained: its code, its data, and its docs live together, so a tool can be
read, run, or removed without untangling it from the others.

Where a tool's skills and agents live depends on how the tool is used:

- **creative-writing** is used from this repo, so its skills and agents live once,
  at the repo root under `.claude/`. They load whenever this repo is your working
  directory.
- **studio** is used from this repo too, for the same reason: it writes into a
  vault that lives here. Its skill is under `.claude/`.
- **ui-design** is a Claude Code plugin, published on its own. A plugin is copied
  into a cache when it is installed and cannot reach outside its own folder, so its
  skills and agents live inside it, in `plugins/ui-design/`, not under `.claude/`.

## Layout

```
INDEX.md             generated index of the tools, skills and agents
.claude/skills/      creative-writing-pipeline, chunk-tag-backfill, studio-pipeline
.claude/agents/      creative-writing-{chunk-tagger,drafter,librarian-native}
creative-writing/    the creative-writing tool
  vault/             the Obsidian vault — 63 works, annotations, chunk tags,
                     idea library, and the vault's own search tooling
  pipeline/          the checkpointed pipeline that writes into that vault
studio/              the studio tool
  vault/             a second Obsidian vault — one note per made thing, the brand
                     gates, and the vault's own CLAUDE.md and SCHEMA.md
  pipeline/          spec.yaml, the bookkeeper, the note and gate writers, the brush
                     packer, the compute gate, and their tests
  hub/               the desk: a loopback server and page over the vault and the runs,
                     the Windows launcher, and (once copied in) the brush designer
  assets/            what runs keep, by project, kind and slug. Not versioned
  docs/              what was carried from Creative-Headquarters, and how
writing-museum/      the Writing Museum: a walkable 3D museum of the creative-writing vault,
  build/             works.py (a work as passage panels), mapping.json, layout.py, library.py,
                     build_museum.py, and their tests
  data/              scenes/<id>.json (one per scene-3d run), the built manifest + layout,
                     and library.json (every work and scene, for the explore page)
  web/, assets/      the viewer (copied from Earth_Worldbuild/_Museum), the library page
                     (explore.html, this museum's own) and the CC0 textures
  tools/             walk_test.mjs: the browser walk-through
docs/                HTML pages describing each tool, and setup_keys.py (a localhost-only
                     helper that saves API keys to ~/.rosw/keys.env)
.claude-plugin/      marketplace.json: installs plugins/ui-design from this repo
plugins/ui-design/   the ui-design plugin: the plugin root, and the whole of what is published
  .claude-plugin/    plugin.json and marketplace.json
  skills/            ui-design-catalog, ui-design-catalog-refresh, ui-design-multipart
  agents/            ui-design-{catalog-reviewer,search-part,page-reviewer}
  spec.yaml          the declared contract; validate-contract.py enforces it
  INDEX.md           generated: the catalog's own vocabulary, data files, references
  ROUTER.md          which mode, domain and query; what to do when a match looks wrong
  catalog/           data/ and scripts/ — the search catalog, stdlib only
  maintenance/       validators, relevance gate, refresh scripts, verify.py
  references/        prose the ui-design-catalog skill reads on demand
  README.md, LICENSE, NOTICE, CHANGELOG.md, .gitignore, .gitattributes
.github/workflows/   verify.yml: CI for the whole repo (see "Working on the ui-design plugin")
```

**Paths in the creative-writing and studio skills and agents are relative to this
repo root**, which is the working directory. Vault-relative paths (as
`vault_search.py` reports and accepts them, e.g. `03_Stories/06_Melting_Away.md`)
need a `creative-writing/vault/` prefix before you Read or Write them. A studio
note's path (e.g. `aurora/ui/console.md`) is relative to `studio/vault/`.

**Paths in the ui-design skills and agents start from `${CLAUDE_PLUGIN_ROOT}`**, the
plugin's install directory, never from the working directory: once installed, the
working directory is someone else's project. Claude Code substitutes the variable in
the Markdown body of a skill or agent, but not in frontmatter, so no `description`
may contain it. `validate-contract.py` enforces both, and fails on any hard-coded
`ui-design/` path, `.claude/` path or mention of this repo in a skill, agent or doc.

## Creative writing is governed by the vault's own CLAUDE.md

**`creative-writing/vault/CLAUDE.md` is authoritative** for anything that writes
creative prose: the four style modes and their sentence- and structure-level
rules, the anti-style do-not list, the frontmatter schema, the ethical-restraint
precedent, and the rule that the 63 existing works are certified verbatim
transcriptions that are **not** to be edited. Read it in full before writing or
revising any creative material — this file does not summarize or replace it, and
`creative-writing/pipeline/spec.yaml` points back to it too.

Do not duplicate its rules here. If the writing rules change, they change there.

## Working on the creative-writing tool

- Search the vault: `python creative-writing/vault/tools/vault_search.py search "<query>"`.
  It resolves the vault and its index from its own location, so it runs from
  anywhere. Re-index after any content or frontmatter change:
  `python creative-writing/vault/tools/vault_search.py index`.
- Develop a new work: use the `creative-writing-pipeline` skill, or the
  standalone `python creative-writing/pipeline/run_pipeline.py`. Both read
  `creative-writing/pipeline/spec.yaml` as their single source of truth.
- The pipeline's `vault_integration` stage only writes to the vault with an
  explicit `--confirm`; without it, it prints a dry-run preview. Keep it that way.
- **Plot logic.** Story outlines carry a causal ledger (but / therefore, never
  and-then) that `creative-writing/pipeline/plot_logic.py` checks; a **register**
  (`liminal`, `psychedelic`, `cosmic`) overlays a mode. The rules live in
  `creative-writing/vault/CLAUDE.md` ("Plot logic"), their machine-readable form in
  `spec.yaml` (`plot_logic:`, `registers:`), and the reasoning and worked examples in
  `creative-writing/vault/_Craft/`. Run the tests after touching any of them:
  `python -m unittest discover -s creative-writing/pipeline/tests`. They check every
  ledger in `_Craft/` against its declared verdict and every quotation in it against
  the vault, so editing a craft note can fail them; that is the point.
- `_Craft/` notes are analysis written with Claude, not the author's prose. Do not
  present them as the author's voice, and do not edit the 63 originals to fit them.
- **Keys live outside the repo**, in `~/.rosw/keys.env` (or `ROSW_KEYS_FILE`).
  `python docs/setup_keys.py` writes it from a local page; `llm.py` reads it, and still
  reads a legacy `creative-writing/pipeline/.env` if one exists (`--migrate` moves it).
  Never commit a key, never echo its value, and never let a test print os.environ: the
  tests in `creative-writing/pipeline/tests/test_llm_keys.py` and `docs/tests/` point both
  locations at temp files and compare names, not values.

## The studio is governed by its vault's own CLAUDE.md

**`studio/vault/CLAUDE.md` is authoritative** for anything that makes a thing
through the studio or writes a note into that vault: the six stages, the ladder
that resolves a constraint, the attestation, parking, the refusals, and the rule
that a brand gate is the author's and is never generated. Read it in full before
running or changing a pipeline. `studio/pipeline/spec.yaml` is its
machine-readable form and points back to it.

Do not duplicate its rules here. The two vaults are separate: nothing in the
studio writes `creative-writing/vault/`, and nothing reads it except the one work
the author names at a `scene-3d` intake, through `writing-museum/build/`.

## Working on the studio tool

- Make something: use the `studio-pipeline` skill. There is no standalone script;
  the tools a stage calls exist only inside a live session.
- `studio/pipeline/spec.yaml` is the single source of truth for the pipelines, the
  stages, the gates and the refusals. `studio_run.py` reads stage order, outputs,
  checks and confirmation rules from it; nothing about a particular stage or
  pipeline is written into the code. Read it before changing either.
- `studio_run.py` is a bookkeeper. It never calls a model or a tool. When it
  refuses, fix what it names. Never edit a run's `state.json` by hand.
- **Every write into `studio/vault/` goes through `content_md.py`**: `plan`
  previews and writes nothing to the vault, `apply` without `--confirm` is a dry
  run, and `apply --confirm` still refuses unless the author's go-ahead was
  recorded after the plan was made. Keep it that way. Never write a note there
  with Write or Edit.
- `studio/vault/_Context/brand/` holds the brand gates and `tokens.json`. They
  are the author's. A gate is written only by a `brand-gate` run, through
  `studio/pipeline/gate_md.py`, after the author has seen the whole file.
  Anything else there is proposed as a diff, never written.
- `plugins/ui-design/` is read-only from the studio. The `ui-direction` pipeline
  runs its scripts and changes nothing in it.
- **A run keeps a file only through `studio_run.py keep`**, after the execute
  go-ahead, into `studio/assets/<project>/<kind>/<slug>/` (not versioned). A note
  lists what was kept under `artifacts`, by that path, and never a link. A
  connector's result is downloaded into the run folder during execute.
- A pipeline that runs through a connector lists every tool it may call under
  `connector: tools` in the spec, and calls no other; `connectors: never` still
  holds. A `local-compute` pipeline names a `workload:` class from
  `studio/pipeline/machine.yaml`, and execute is not marked done without a live
  token from `compute_gate.py` consumed by the run. `mint` writes nothing on a
  DENY; the token lives under `runs/`.
- **The hub** (`studio/hub/serve.py`) binds 127.0.0.1, serves only its own folder
  and a few JSON routes over the vault and the runs, and writes nothing but a new
  run through the bookkeeper. It links to the Writing Museum's library and viewer
  on the museum's own server (`/api/museum`, `--museum-port`) and never serves or
  reads the museum's files beyond whether `library.json` exists. Its stylesheet holds no literal value: every colour,
  size and font is a custom property set from `tokens.json` at load, and
  `tests/test_hub.py` refuses a literal. `studio/vault/tools/vault_index.py` is
  the index it searches; it carries no note bodies and is not versioned.
- `studio/pipeline/brush_pack.py` packs a designer bundle into a Procreate file
  with `plistlib`. A Procreate-written `.brush` under
  `studio/pipeline/tests/fixtures/procreate/` turns its format test on.
- Run the tests after touching the spec, a gate, `tokens.json`, `SCHEMA.md`, the
  vault's `CLAUDE.md`, the skill or either script:
  `python -m unittest discover -s studio/pipeline/tests`. They run against
  temporary folders, and they check that the spec, the gate folder, the documents
  and the skill agree with one another, so editing a document can fail them; that
  is the point.
- A pipeline is entered by choice. Nothing here can stop a tool being called
  outside one, and the documents say so. Do not describe the studio as enforcing
  more than it does.

## Working on the Writing Museum

`writing-museum/` is the engine and the data of a walkable 3D museum of the
creative-writing vault, fashioned after the Chronicle Museum in the author's
`Earth_Worldbuild` repo (its viewer and layout builder were copied; `writing-museum/README.md`
lists what changed). One room per work; the work's passages hang as verbatim text
panels cited by vault path and lines.

- A scene is made only through the studio's `scene-3d` pipeline
  (`studio/pipeline/spec.yaml`), which writes `writing-museum/data/scenes/<id>.json`
  at execute and leaves a note at `studio/vault/<project>/3d/<id>.md`. Do not write
  a scene spec by hand.
- `build/mapping.json` is a reference table, never binding: a run records which of
  its rows it took and why. `build_museum.py propose <vault-path>` prints that.
- Build: `python writing-museum/build/build_museum.py build` (`--lint` writes
  nothing). Walk it: `node writing-museum/tools/walk_test.mjs` (Playwright and
  Chromium; output under `writing-museum/tools/out/`, git-ignored). View it:
  `python -m http.server 8768 --directory writing-museum`, then `/web/index.html`.
- **The library** (`web/explore.html`) is the flat page beside the viewer: every work
  of the vault read passage by passage, and every scene with its colours and sources.
  It reads only `data/library.json`, which `build` writes from the whole vault through
  `build/library.py`. After a vault or scene change, rebuild; the walk test's
  `library_page` case checks the page against that file.
- Tests: `python -m unittest discover -s writing-museum/build/tests`. They run on a
  temporary vault, and read the real one only to check the ten-work path.
- It reads `creative-writing/vault/` and never writes it. The 63 works stay verbatim;
  the transcription header above a work's text is left off its panels.
- `web/` stays the Chronicle Museum's viewer with the edits the README lists. Bring a
  fix from that repo over as a copy, and note it there.

## Working on the ui-design plugin

`plugins/ui-design/spec.yaml` is the declared contract — search domains, stacks,
output formats, design dials, exit codes, the persistence rule. Read it before
changing any of them; this file does not repeat it. Every path in it is relative to
the plugin root.

- **Loading the skills in this repo.** They are no longer under `.claude/`. Start
  Claude Code with `claude --plugin-dir ./plugins/ui-design`, or register the local
  marketplace once (`claude plugin marketplace add ./plugins/ui-design`, then
  `claude plugin install ui-design@ui-design-plugin`). Skills and agents are then
  namespaced: `/ui-design:ui-design-catalog`, agent type
  `ui-design:ui-design-search-part`.
- Search the catalog:
  `python plugins/ui-design/catalog/scripts/search.py "<query>" --domain <domain>`,
  or `--design-system` for a whole-product recommendation. The `ui-design-catalog`
  skill drives it. The scripts find their data relative to themselves, so they run
  from any directory.
- **Two halves, one rule.** `catalog/` is stdlib-only and never touches the network;
  anything needing a dependency, the network or a secret belongs in `maintenance/`.
  `catalog/data` and `catalog/scripts` must stay siblings: `core.py` finds its data
  at `Path(__file__).parent.parent / "data"`.
- Verify with one command: `python plugins/ui-design/maintenance/verify.py`, from any
  directory. It runs every gate and prints the exact command to re-run whichever one
  fails. On GitHub, `.github/workflows/verify.yml` runs it, and the creative-writing,
  studio and docs test suites, on Linux, Windows and macOS with Python 3.10 and 3.13,
  on every push to `main` and every pull request.
- `claude plugin validate ./plugins/ui-design` checks the manifest and marketplace
  file. It is not part of `verify.py`, because it needs the Claude Code CLI.
- `--persist` writes `design-system/<project-slug>/` under `--output-dir`, or under
  the current directory if it is omitted. Installed as a plugin the current directory
  is the user's own project, so every documented `--persist` command passes
  `--output-dir`, and the skill has the assistant confirm that directory with the
  user first. When you test it yourself, point `--output-dir` **outside** this repo.
- Files under `plugins/ui-design/` are pinned to LF (`plugins/ui-design/.gitattributes`,
  and `.gitattributes` here): the relevance gate fingerprints their raw bytes. The
  fingerprints hash files by their path relative to the plugin root, so moving the
  folder does not change them. After a deliberate change to a runtime or data file,
  regenerate them rather than working around the gate.
- Refresh the upstream Google Fonts and Phosphor data with the
  `ui-design-catalog-refresh` skill. Promoting a candidate is an editorial
  decision with a licensing dimension; it stops for the author's approval. The
  skill writes into the plugin folder, so it refuses to run from an installed copy
  (the cache is discarded on update): run it from this checkout.
- Three agents, all one-part-per-invocation. `ui-design-catalog-reviewer` exists for
  the refresh review only. `ui-design-search-part` and `ui-design-page-reviewer`
  are the parts of the `ui-design-multipart` skill. All are read-only, and none
  persists anything.
- Search is a fast local lookup and is not delegated by default. Multipart
  fan-out happens only from a `route.py` manifest, and only when the router says
  the brief is wide (4 or more parts); otherwise run the parts inline. Stack parts
  the stack's data cannot answer come back in `not_covered`; they are reported and
  never dispatched. Only `ui-design-search-part` holds `Bash` (to run `search.py`
  once), declared in `spec.yaml` `agent_tool_exceptions` and enforced by
  `validate-contract.py`.
- Route a free-wording brief with
  `python plugins/ui-design/catalog/scripts/route.py "<brief>"` before searching: a
  literal query can rank the wrong product row first with no warning.
  `search.py --diagnostics` shows the confidence fields for one search.
- `INDEX.md` and `plugins/ui-design/INDEX.md` are generated, never hand-edited. After
  adding or renaming a skill, an agent, a data file or a product row, run
  `python plugins/ui-design/maintenance/generate-index.py`; `verify.py` fails on a
  stale index or a skill or agent missing from the root one. Outside this repo the
  script handles the plugin's own index only.
- `GOOGLE_FONTS_API_KEY` is needed only for a live font refresh, comes from the
  environment (see `plugins/ui-design/maintenance/.env.example`), and is never echoed.

### Publishing

The whole repo, both vaults included, is public at
`https://github.com/groot99-droid/Pipelines-Plugin` (the author's decision, 2026-09-30).
The plugin installs from it through the root `.claude-plugin/marketplace.json`
(`/plugin marketplace add groot99-droid/Pipelines-Plugin`, then
`/plugin install ui-design@rosw`).

1. `python plugins/ui-design/maintenance/verify.py` passes, and
   `claude plugin validate ./plugins/ui-design` and `claude plugin validate .` pass.
2. For a plugin release, bump `version` in `plugins/ui-design/.claude-plugin/plugin.json`
   and add the matching entry at the top of its `CHANGELOG.md`; `validate-contract.py`
   checks that they agree.
3. Before any push, check that `git ls-files` holds no `.env` and no key file, and that
   no key value appears in any commit.
4. Pushing and tagging are the author's call. Do not push, tag or publish without being
   asked.

## Adding a tool

1. Create `<tool-name>/` at the repo root, self-contained. If it is to be shipped as a
   Claude Code plugin, create `plugins/<tool-name>/` instead, with its own
   `.claude-plugin/`, `skills/`, `agents/`, `.gitignore` and `.gitattributes`, so it can
   be published on its own.
2. For a tool used from this repo, put any skill under `.claude/skills/<skill-name>/`
   and any agent under `.claude/agents/`, with repo-root-relative paths. For a plugin,
   keep them inside the plugin and start every path from `${CLAUDE_PLUGIN_ROOT}`.
3. Extend the root `.gitignore` if the tool produces state or caches.
4. Add a section to `README.md`.
5. For a new top-level folder, add it to `TOOL_PURPOSE` in
   `plugins/ui-design/maintenance/generate-index.py`; the index generator exits 2
   on a folder it has no purpose for. That file ships in the published plugin, so
   keep the wording neutral. Then regenerate the index and run the gate:
   `python plugins/ui-design/maintenance/generate-index.py` and
   `python plugins/ui-design/maintenance/verify.py`. The same two commands follow
   any new skill or agent.
