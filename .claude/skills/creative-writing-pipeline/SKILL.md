---
name: creative-writing-pipeline
description: Walk a new idea for this vault through the checkpointed multi-stage pipeline (intake, reference pull, outline, draft, self-revision, vault integration) instead of writing a finished piece in one shot. Use when the author wants to develop a new work for the vault from an idea, not when editing one of the 63 existing verbatim originals.
---

# Creative-writing pipeline

All paths in this file are relative to the **Pipelines repo root**, which is
your working directory. The layout:

- `creative-writing/vault/` — the Obsidian vault: the 63 works, `_Annotations/`,
  `_ChunkTags/`, `_Idea_Library/`, `tools/`, and the vault's own `CLAUDE.md`.
- `creative-writing/pipeline/` — this pipeline's scripts and `spec.yaml`.

Where a path below is given vault-relative (e.g. `03_Stories/06_Melting_Away.md`)
— as `vault_search.py` and `librarian.py` both report and accept them — it means
relative to `creative-writing/vault/`.

This skill is the interactive counterpart to
`creative-writing/pipeline/run_pipeline.py` (the standalone
script). Both read the same spec file —
`creative-writing/pipeline/spec.yaml` — so read that file now,
in full, before doing anything else. It is the source of truth for stage
order, stage prompts, per-mode rules, and the frontmatter schema. Do not
re-derive or improvise stage logic that contradicts it; if it and this
file ever disagree, spec.yaml wins.

Also load `creative-writing/vault/CLAUDE.md` for full context — spec.yaml summarizes and
references it, it doesn't replace it.

## How to run this

1. **Determine the mode.** If the author didn't already say which vault
   mode this belongs to, ask — check spec.yaml's `modes:` block for which
   are `status: implemented` (`essay-self-help`, `horror-prose`,
   `epic-fantasy`, and `confessional-poetry` all have real rules;
   `unclassified` is deliberately left a stub per CLAUDE.md — for that
   one, ask the author which register they actually want rather than
   defaulting to one of the four modes).

   **Then determine the register(s), if any:** `liminal`, `psychedelic`
   and/or `cosmic` (spec.yaml `registers:`). A register is what kind of
   world the piece runs in; the mode is how it sounds, and they cut across
   each other. **Never infer a register** — if the idea seems to want one,
   say so and ask. A register switches plot logic on even for a mode that
   would not ask for it (an essay or a poem). Keep the chosen registers for
   every stage below.

2. **Walk the stages in spec.yaml's `stages:` list, in order, one at a
   time:** intake → reference_pull → outline → draft → self_revision →
   vault_integration. For each stage:
   - Fill that stage's `prompt` text using the current mode's block
     under `modes:` (the `{mode.field}` placeholders map directly to keys
     there — e.g. `{mode.voice_notes}`, `{mode.structure_rhythm}`).
   - **intake, reference_pull, vault_integration**: do the actual work
     yourself (write the idea capture, run
     `creative-writing/vault/tools/vault_search.py`,
     read/write vault files) using your own judgment — these are
     data-gathering or file-writing steps, not heavy generation, and
     vault_integration in particular must stay under your direct control
     for its approval gate (see step 5).
   - **outline, draft, self_revision**: these are the pipeline's heavy
     generation stages — full artifacts from substantial context, not
     quick data lookups. Delegate them to the `creative-writing-drafter`
     subagent via the Agent tool instead of generating inline yourself.
     Give it, in its prompt: the filled stage prompt text, the mode's
     rule block from spec.yaml, and the relevant prior artifacts
     (idea.md/references.md for outline; outline.md+references.md for
     draft; draft.md for self_revision). The subagent has no Write/Edit/
     Agent access — it only returns text. You still own the checkpoint:
     take its returned artifact, save it to the stage's output file
     yourself, and show it to the author for approval before continuing.
   - **outline, specifically — plot logic.** The outline stage prompt
     contains a `{plot_logic}` placeholder. Fill it by running
     `python creative-writing/pipeline/plot_logic.py rules --mode <mode> [--register <r> ...]`
     and pasting its output into the drafter's prompt (empty output means the
     mode and registers have no plot logic; then there is nothing to add).
     The drafter must return an outline that ends with a `## Causal ledger`.
     After you save it to `outline.md`, **check it**:
     `python creative-writing/pipeline/plot_logic.py check <outline.md> --mode <mode> [--register <r> ...]`.
     If it reports errors, re-invoke the drafter **once** with the checker's
     report and the outline, and ask for the corrected outline. Show the author
     the outline **and the report** either way; never hide a failing ledger.
     Warnings (`no-but`, `smooth-run`, `pile-on`, `no-investigates`) are for the
     author to weigh, not to silently fix. The checker cannot judge whether a
     link is true, so you review that too: read each `Because` phrase against
     the beat it cites, and say plainly where a link looks cosmetic.
   - **reference_pull with a register:** add the register's `worked_examples`
     (spec.yaml) to the file list you hand the librarian, and give the drafter
     the register's craft note (`creative-writing/vault/_Craft/<note>.md`,
     named in spec.yaml as `note`) as guidance. The notes are analysis written
     with Claude, not the author's prose: never present a line from them as
     the author's voice.
   - Save the stage's output to a scratch file for the session (a
     reasonable temp/session location is fine — the point is the author
     can review it, not where exactly it lives) using the filename in
     that stage's `output_file`/`output_files`.
   - **Stop and show the author the result.** Every stage in spec.yaml
     has `checkpoint: true` — do not proceed to the next stage until the
     author has reviewed this one's output and says to continue. If they
     want changes, redo the current stage, don't silently patch forward.

3. **Reference pull stage specifically:** actually run
   `python creative-writing/vault/tools/vault_search.py search "<query>" --top 5 --json`
   — that's a cheap index lookup, do it directly. It resolves the vault and its
   index from its own location, so it works from any working directory. Cite its
   results exactly as it reports them (file + heading/line range) — never
   fabricate a citation, per CLAUDE.md. Also run the `--tag` search
   spec.yaml's `reference_pull` prompt describes (derived from this idea's
   candidate themes/archetypes) — this is what actually widens the
   candidate pool beyond the mode's fixed worked_examples list; follow
   spec.yaml's own instructions for it rather than re-deriving them here.

   For the mode's worked-example files (and any strong search hits) —
   **do not Read their full text yourself.** Compile the exact file list
   and delegate the condensation instead — you have two equivalent paths
   that produce the same digest format:

   - **Native (default in a live skill session):** invoke the
     `creative-writing-librarian-native` subagent via the Agent tool,
     giving it the file list and a focus/query string (the idea summary).
     It has Read/Grep/Glob only — no Bash, no Ollama dependency, no
     CPU-bound local-inference latency — and returns the same
     `### <path>` + bullets + "Verbatim quotes" digest format
     `librarian.py` produces.
   - **Script path (`librarian.py`, Ollama-backed):**
     ```
     python creative-writing/pipeline/librarian.py digest <path1> [<path2> ...] --query "<idea summary>"
     ```
     (run via Bash from the repo root; `<path1>` etc. are vault-relative).
     Only fall back to this if the
     author explicitly asks for the Ollama-backed path, or the native
     subagent is unavailable — it needs `ollama serve` running first, and
     CPU-only condensation is slow (minutes per file).

   - **Gemini option (`librarian.py --backend gemini_mcp`):** same script
     and same digest format, condensed by Google Gemini instead of
     Ollama — fast, no local server. Add `--backend gemini_mcp` to the
     command above (or set `LIBRARIAN_BACKEND=gemini_mcp`). Needs
     `GEMINI_API_KEY` set and `pip install google-genai`; uses the same
     key and default model (`GEMINI_MODEL`) as the Gemini MCP plugin.
     Use it only if the author asks for Gemini; note it sends vault file
     text to Google's API.

   Whichever path you use, build `references.md` from the resulting digest. Treat
   lines under a "Verbatim quotes" heading as exact ONLY if not marked
   `[UNVERIFIED]` — treat everything else in the digest as paraphrase,
   not a citable quote. Never Read the raw worked-example files yourself
   as a substitute for either path.

3b. **Draft stage with a ledger:** tell the drafter to write to the ledger.
   Each beat's `Because` phrase must be visible on the page, and no beat may
   be added that is not in the ledger (if the draft needs one, it is added with
   its Link and Because and flagged). For a `psychedelic` register, the draft
   contains no substances, doses, sourcing or how-to; see CLAUDE.md's
   anti-style list.

4. **Self-revision stage specifically:** this is where CLAUDE.md's
   anti-style rule "don't silently invent mode/project/archetype ties"
   gets enforced. Delegate this stage to `creative-writing-drafter` per
   step 2 above, telling it explicitly: if the draft claims or implies a
   connection to an existing vault work, verify it — run
   `vault_search.py` for it, and if there's a hit, condense that hit's
   file focused on the claim (via `creative-writing-librarian-native`, or
   `librarian.py --query "<the claim>"` if using the script path, with `--backend gemini_mcp` for Gemini) and
   judge the tie against the condensed digest rather than trusting the
   similarity score alone. `creative-writing-drafter` has its own Bash
   access for `vault_search.py`, but it cannot call `creative-writing-
   librarian-native` itself (no Agent tool) — if it needs a file
   condensed, have it say so in its output and you run that condensation
   step yourself before re-invoking it, or condense proactively when you
   hand it the stage. Cut or flag the claim if it doesn't hold up, per
   spec.yaml's `vault_wide_rules`, and include the condensation-backed
   detail in `revision_notes.md`, not just a pass/fail. Read the
   subagent's returned revision_notes.md yourself before showing it to
   the author — if a claimed tie looks asserted rather than verified,
   push back and re-run the stage rather than passing it through.

4b. **Self-revision also walks the ledger.** Have the drafter re-walk
   `outline.md`'s ledger against the draft beat by beat: a beat whose
   `Because` phrase is not visible on the page has become an and-then in
   execution, so it is fixed or flagged, and the draft's ending must be the
   ledger's declared `Ending:`. Put the result in `revision_notes.md`.

5. **Vault-integration stage specifically — the highest-stakes step.**
   This automates CLAUDE.md's existing 5-step Maintenance procedure
   (create file → frontmatter → folder `_index.md` entry → companion
   annotation → reindex). It must **never run without the author's
   explicit go-ahead on the final draft** — asking "should I integrate
   this into the vault now?" and getting a clear yes is that go-ahead.
   Before writing anything:
   - Confirm the target filename (matching the folder's `NN_Title.md`
     numbering convention).
   - If registers were used, the frontmatter gets `register: [<names>]` and a
     `register/<name>` tag each (never for a piece that used none), and the
     annotation should say where the piece's buts and therefores fall and how
     the protagonist's agency moves, drawing on the checker's report.
   - Show the author the exact frontmatter you're about to write (see
     `frontmatter_schema` in spec.yaml), the `_index.md` line, and a
     draft of the companion annotation — genuine craft analysis of this
     specific piece, not a template, matching the style of existing
     `_Annotations/` files.
   - Only after that preview is approved: create the file, add the
     frontmatter, append the `_index.md` entry, write the annotation
     file, then run
     `python creative-writing/vault/tools/vault_search.py index` (and
     `python creative-writing/vault/tools/build_canvas.py` if this piece's
     `mode`/`project` changes the style/project map).

## What this skill does not do

It does not touch any of the 63 original works — those are verbatim and
out of scope for this pipeline entirely (per CLAUDE.md's Purpose &
scope). It only creates new pieces from a new idea.
