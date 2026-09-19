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
.claude/skills/      creative-writing-pipeline, chunk-tag-backfill
.claude/agents/      creative-writing-{chunk-tagger,drafter,librarian-native}
creative-writing/    the creative-writing tool
  vault/             the Obsidian vault — 63 works, annotations, chunk tags,
                     idea library, and the vault's own search tooling
  pipeline/          the checkpointed pipeline that writes into that vault
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

## Adding a tool

1. Create `<tool-name>/` at the repo root, self-contained.
2. Put any skill under `.claude/skills/<skill-name>/` and any agent under
   `.claude/agents/`, with repo-root-relative paths.
3. Extend the root `.gitignore` if the tool produces state or caches.
4. Add a section to `README.md`.
