# udgt — UI, Dataset & Gameplay Teardown

A Claude Code plugin that pulls a game's repository apart. For each design choice it records what
the choice is, how it was made, how it changed and what is planned next, across the frontend, the
backend, the datasets, the gameplay, the world bible and the art pipeline. The result has three parts:

- **a dataset** (`teardown.json`): a graph of the game's documents and numbered sections, decisions and
  open questions, data records, code areas and ordered anchors (a phase machine, a tick order),
  protocol messages, design tokens, UI copy, screens, pull requests, commits and stated plans, linked
  by the citations between them;
- **written chapters**, one per stage, each choice in three parts: *Describe*, *Compare* (with genre
  references) and *Critique*. The last two are labelled as Claude's analysis;
- **an explorer page** dressed in the game's own look. It is themed from the game's design tokens
  and fonts, its title view is laid out like the game's menu, and records are dealt as the game's cards.

The owner takes part through **briefs**: before each chapter, Claude asks 2 to 4 questions about intent,
feeling and priority. `udgt.py record` stores the answers verbatim, and the chapter quotes them.

## Install

```
/plugin marketplace add groot99-droid/Pipelines-Plugin
/plugin install udgt@rosw
```

The skills are `/udgt:udgt-teardown` (write or refresh a teardown) and `/udgt:udgt-consult` (look
something up while working on the game). The agent is `udgt:udgt-chapter-analyst`.

## How it fits together

A game gets a **teardown folder**, kept wherever the owner wants it, never inside the plugin. It holds:

- a `profile.json` (see `profiles/schema.json`) naming the documents, the citation patterns, the decision
  log's layout, the data folders, the code areas and anchors, the token and font files, any lore kept
  outside the game (a folder of Markdown works, taken by their frontmatter), the stages and their
  prompts, the reference games and the explorer's views;
- the files the engine and Claude write there.

```
python engine/udgt.py scan   --profile <folder>/profile.json [--game <checkout>]
python engine/udgt.py check  --profile <folder>/profile.json        # writes nothing
python engine/udgt.py brief  3 --profile <folder>/profile.json      # the stage's questions and gaps
python engine/udgt.py record 3 --profile <folder>/profile.json --question "..." --answer "..."
python engine/udgt.py build  --profile <folder>/profile.json
python engine/udgt.py query  "quick mode" --profile <folder>/profile.json
```

Serve the folder (`python -m http.server --directory <folder> 8791`) and open `explorer/index.html`.

The engine is Python 3.10+ standard library only. It reads the game checkout and its git history and
never writes to them. It runs nothing from the game: it reads text, JSON and `git log`.

## Tests

```
python -m unittest discover -s plugins/udgt/tests
```

The tests build a small fake game in a temporary folder. They cover the decision layouts, nested
numbering, list-item sections, citations and ranges, datasets, anchors, the append-only answers,
the build, and the page reading nothing but local JSON.
