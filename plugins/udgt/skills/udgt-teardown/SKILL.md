---
name: udgt-teardown
description: Tear a game's repository apart stage by stage (UI and frontend, datasets, gameplay and mechanics, backend, world bible, art pipeline, history, future plans) into a dataset, written chapters and an explorer page that wears the game's own look, asking the owner a short creative brief before each chapter. Use when the owner asks for a teardown, a design review of the whole game, a chapter of it, or to refresh it after the game changed. Not for looking one thing up in an existing teardown (that is udgt-consult), and never writes into the game's repository.
---
# UDGT teardown

UDGT is UI, Dataset & Gameplay Teardown. A teardown lives in a **teardown folder** that the owner keeps
somewhere permanent, never inside this plugin (the plugin's install folder is replaced on update). The
folder holds:

| File | What it is | Who writes it |
|---|---|---|
| `profile.json` | what to read in the game and how (schema: `${CLAUDE_PLUGIN_ROOT}/profiles/schema.json`) | you, with the owner |
| `teardown.json` | the extracted graph: sections, decisions, data, code, UI, history, plans | `udgt.py scan` only |
| `answers.json` | the owner's answers to the briefs, verbatim | `udgt.py record` only |
| `chapters/NN-<slug>.md` | the written teardown, one chapter per stage | you |
| `explorer/` | the page | `udgt.py build` only |

The engine is `${CLAUDE_PLUGIN_ROOT}/engine/udgt.py` (Python 3.10+, stdlib only). Below, `udgt` means
`python ${CLAUDE_PLUGIN_ROOT}/engine/udgt.py` and `P` the teardown's `profile.json`. Every command reads
the game checkout and never writes it.

## Start or refresh

1. Find the teardown folder. Ask the owner if you do not know it. If the game has none yet, write a
   `profile.json` from the schema and the game's own docs (its document list, its citation patterns,
   its data folders, its design-token files, its stages and their prompts), and show it to the owner
   before the first scan.
2. `udgt scan --profile P [--game <checkout>]`. Read the counts and the notes. A shallow clone has
   partial history: say so, and suggest `git fetch --unshallow` in the game checkout.
3. `udgt check --profile P` and `udgt stages --profile P` tell you what is broken, stale and unwritten.
   After a game change, `udgt diff --profile P` lists what moved.

## One stage at a time, brief first

For each stage, in order, unless the owner picks one:

1. `udgt brief <stage> --profile P` prints the stage's prompts, the gaps the scan found in its areas
   (open items, unresolved questions, plans a later document withdrew) and what was already answered.
2. **Ask the owner before writing.** Turn the brief into 2 to 4 questions with AskUserQuestion. Give
   concrete options grounded in what the scan found (name the decision, the section, the number), put
   your recommendation first, and keep "Other" open for their own words. Do not ask what the documents
   already answer; ask what only the owner knows: intent, feeling, regret, priority, taste.
3. Record every answer verbatim, the option label or their typed words, nothing paraphrased:
   `udgt record <stage> --profile P --question "<question as asked>" --answer "<their words>"`.
4. Write `chapters/NN-<slug>.md` (NN is the stage id, two digits). Shape:
   - `# <Stage title>` then a one-paragraph summary.
   - One `##` per design choice that matters, each with three parts:
     **Describe** (what it is, how it was made, how it changed, with citations),
     **Compare** (genre references from the profile's `compare` list, and only claims you are sure of),
     **Critique** (tensions, risks, docs that disagree with code, choices that cost more than they buy).
   - A `## Owner's word` section quoting this stage's answers.
   - A `## Open threads` section: what the owner should decide next.
   - Cite teardown nodes as `[[dec:A115]]`, `[[sec:GDD:3.11]]`, `[[rec:roles/roles/killer]]`, and
     game files as `path:line`. Compare and Critique are your analysis. Label them so, and never put
     words in the owner's mouth.
   - For a wide stage, you may hand the drafting to the `udgt-chapter-analyst` agent. Give it the
     node ids, files and answers it needs. Read its draft against the sources before saving it.
5. `udgt check --profile P` must report no `chapter-link` findings. Then `udgt build --profile P`.
6. Tell the owner, in a line or two, what the chapter found that surprised you, and move on to the
   next stage's brief.

## Viewing

`udgt build --profile P [--game <checkout>]` copies the page, writes `theme.css` from the game's
tokens (and the fonts the profile names), and writes `chapters.json`. Serve the teardown folder
(`python -m http.server --directory <teardown> 8791`) and open `explorer/index.html`. The page reads only
`../teardown.json`, `../answers.json` and `chapters.json`.

## Refusals

- Never edit `teardown.json`, `answers.json` or `explorer/` by hand, and never edit an answer.
- Never write into the game's repository from this skill.
- Never present Compare or Critique as the owner's view, or a guess as a fact.
- Copy nothing from the game but token values and the font files the profile names; respect the
  font licences in the teardown's README.
