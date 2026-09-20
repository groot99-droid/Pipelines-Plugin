# CLAUDE.md — Pipelines

## What this repo is

A single repo holding multiple tools, each in its own top-level folder. A tool
folder is self-contained: its code, its data, and its docs live together, so a
tool can be read, run, or removed without untangling it from the others.

Skills and agents live once, at the repo root under `.claude/`, not inside the
tool folders. That way they load whenever this repo is your working directory,
whichever tool you are working on, and the repo is already in the shape a Claude
Code plugin wants when one is added later.

## Layout

```
INDEX.md             generated index of the tools, skills and agents
.claude/skills/      creative-writing-pipeline, chunk-tag-backfill,
                     ui-design-catalog, ui-design-catalog-refresh,
                     ui-design-multipart
.claude/agents/      creative-writing-{chunk-tagger,drafter,librarian-native},
                     ui-design-{catalog-reviewer,search-part,page-reviewer}
creative-writing/    the creative-writing tool
  vault/             the Obsidian vault — 63 works, annotations, chunk tags,
                     idea library, and the vault's own search tooling
  pipeline/          the checkpointed pipeline that writes into that vault
ui-design/           the UI design catalog tool
  spec.yaml          the declared contract; validate-contract.py enforces it
  INDEX.md           generated: the catalog's own vocabulary, data files, references
  ROUTER.md          which mode, domain and query; what to do when a match looks wrong
  catalog/           data/ and scripts/ — the search catalog, stdlib only
  maintenance/       validators, relevance gate, refresh scripts, verify.py
  references/        prose the ui-design-catalog skill reads on demand
```

**Paths in skills and agents are relative to this repo root**, which is the
working directory. Vault-relative paths (as `vault_search.py` reports and
accepts them, e.g. `03_Stories/06_Melting_Away.md`) need a
`creative-writing/vault/` prefix before you Read or Write them.

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

## Working on the ui-design tool

`ui-design/spec.yaml` is the declared contract — search domains, stacks, output
formats, design dials, exit codes, the persistence rule. Read it before changing
any of them; this file does not repeat it.

- Search the catalog:
  `python ui-design/catalog/scripts/search.py "<query>" --domain <domain>`, or
  `--design-system` for a whole-product recommendation. The `ui-design-catalog`
  skill drives it.
- **Two halves, one rule.** `ui-design/catalog/` is stdlib-only and never touches
  the network; anything needing a dependency, the network or a secret belongs in
  `ui-design/maintenance/`. `catalog/data` and `catalog/scripts` must stay
  siblings: `core.py` finds its data at `Path(__file__).parent.parent / "data"`.
- Verify with one command: `python ui-design/maintenance/verify.py`. It runs every
  gate and prints the exact command to re-run whichever one fails. There is no CI;
  this is the gate.
- `--persist` writes `design-system/<project-slug>/` under `--output-dir`, or
  under the current directory if it is omitted — and from this repo that is this
  repo. Always pass `--output-dir` pointing **outside** it.
- Files under `ui-design/` are pinned to LF (`.gitattributes`): the relevance
  gate fingerprints their raw bytes. After a deliberate change to a runtime or
  data file, regenerate the fingerprints rather than working around the gate.
- Refresh the upstream Google Fonts and Phosphor data with the
  `ui-design-catalog-refresh` skill. Promoting a candidate is an editorial
  decision with a licensing dimension; it stops for the author's approval.
- Three agents, all one-part-per-invocation. `ui-design-catalog-reviewer` exists for
  the refresh review only. `ui-design-search-part` and `ui-design-page-reviewer`
  are the parts of the `ui-design-multipart` skill. All are read-only, and none
  persists anything.
- Search is a fast local lookup and is not delegated by default. Multipart
  fan-out happens only from a `route.py` manifest, and only when the router says
  the brief is wide (4 or more parts); otherwise run the parts inline. Only
  `ui-design-search-part` holds `Bash` (to run `search.py` once), declared in
  `spec.yaml` `agent_tool_exceptions` and enforced by `validate-contract.py`.
- Route a free-wording brief with `python ui-design/catalog/scripts/route.py "<brief>"`
  before searching: a literal query can rank the wrong product row first with no
  warning. `search.py --diagnostics` shows the confidence fields for one search.
- `INDEX.md` and `ui-design/INDEX.md` are generated, never hand-edited. After
  adding or renaming a skill, an agent, a data file or a product row, run
  `python ui-design/maintenance/generate-index.py`; `verify.py` fails on a stale
  index or a skill or agent missing from the root one.
- `GOOGLE_FONTS_API_KEY` is needed only for a live font refresh, comes from the
  environment (see `ui-design/maintenance/.env.example`), and is never echoed.

## Adding a tool

1. Create `<tool-name>/` at the repo root, self-contained.
2. Put any skill under `.claude/skills/<skill-name>/` and any agent under
   `.claude/agents/`, with repo-root-relative paths.
3. Extend the root `.gitignore` if the tool produces state or caches.
4. Add a section to `README.md`.
