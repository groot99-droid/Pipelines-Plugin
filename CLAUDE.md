# CLAUDE.md — Pipelines

## What this repo is

A single repo holding multiple tools, each in its own folder. A tool folder is
self-contained: its code, its data, and its docs live together, so a tool can be
read, run, or removed without untangling it from the others.

Where a tool's skills and agents live depends on how the tool is used:

- **creative-writing** is used from this repo, so its skills and agents live once,
  at the repo root under `.claude/`. They load whenever this repo is your working
  directory.
- **ui-design** is a Claude Code plugin, published on its own. A plugin is copied
  into a cache when it is installed and cannot reach outside its own folder, so its
  skills and agents live inside it, in `plugins/ui-design/`, not under `.claude/`.

## Layout

```
INDEX.md             generated index of the tools, skills and agents
.claude/skills/      creative-writing-pipeline, chunk-tag-backfill
.claude/agents/      creative-writing-{chunk-tagger,drafter,librarian-native}
creative-writing/    the creative-writing tool
  vault/             the Obsidian vault — 63 works, annotations, chunk tags,
                     idea library, and the vault's own search tooling
  pipeline/          the checkpointed pipeline that writes into that vault
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
  README.md, LICENSE, NOTICE, CHANGELOG.md, .gitignore, .gitattributes, .github/
```

**Paths in the creative-writing skills and agents are relative to this repo
root**, which is the working directory. Vault-relative paths (as `vault_search.py`
reports and accepts them, e.g. `03_Stories/06_Melting_Away.md`) need a
`creative-writing/vault/` prefix before you Read or Write them.

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
- `creative-writing/pipeline/.env` holds a live `GEMINI_API_KEY` and is
  gitignored. Never commit it, never echo its value.

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
  fails. In this repo there is no CI; this is the gate. The plugin carries its own
  workflow, `plugins/ui-design/.github/workflows/verify.yml`, which runs it on Linux,
  Windows and macOS once the plugin is published as its own repository.
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

### Publishing the plugin

The plugin is published from its own repository, never from this one: this repo also
holds the private creative-writing vault, and a live `.env`. Only the contents of
`plugins/ui-design/` leave it.

1. `python plugins/ui-design/maintenance/verify.py` passes, and
   `claude plugin validate ./plugins/ui-design` passes.
2. Bump `version` in `.claude-plugin/plugin.json` and add the matching entry at the top
   of `CHANGELOG.md`; `validate-contract.py` checks that they agree.
3. Commit, then `git subtree split --prefix=plugins/ui-design -b release/ui-design-plugin`
   produces a branch whose root is the plugin root. Check
   `git ls-tree -r --name-only release/ui-design-plugin` contains no `creative-writing/`,
   no `.env` and no `.obsidian/`.
4. Pushing that branch to the plugin's repository, and tagging it, is the author's call.
   Do not push, tag or publish without being asked.

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
