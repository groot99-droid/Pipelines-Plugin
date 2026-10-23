# Who Did It — teardown

The UDGT teardown of [Who Did It](https://github.com/groot99-droid/Who-Did-It), made with the `udgt`
plugin (`plugins/udgt/`). It covers every design choice in the game: what it is, how it was made, how it
changed and where it is going. Its scope is the UI and frontend, datasets, gameplay and mechanics, backend,
the world bible, the art and audio pipeline, the history, and the future plans.

| File | What it is | Written by |
|---|---|---|
| `profile.json` | What to read in the game and how: documents, citation patterns, the decision log's layout, data, code anchors, design tokens, fonts, the nine stages and their prompts, the reference games, the explorer's views | by hand, with the owner |
| `teardown.json` | The extracted graph | `udgt.py scan` |
| `answers.json` | The owner's answers to the briefs, verbatim | `udgt.py record` |
| `chapters/NN-<slug>.md` | One chapter per stage: Describe, Compare, Critique (the last two are Claude's analysis) | Claude, after each brief |
| `explorer/` | The page, dressed in the game's night glass, pixel type and role cards (not versioned) | `udgt.py build` |

## Use it

The game is read from a sibling checkout (`../Who-Did-It` beside this repo, or `--game <path>`, or
`UDGT_GAME`). Nothing is written into the game.

```
U="python plugins/udgt/engine/udgt.py"; P=teardowns/who-did-it/profile.json
$U scan  --profile $P            # after the game changes; `diff` first shows what moved
$U check --profile $P            # broken citations, stale scan, chapter links
$U brief 3 --profile $P          # the next stage's questions for the owner
$U build --profile $P && python -m http.server --directory teardowns/who-did-it 8791
# then open http://127.0.0.1:8791/explorer/index.html
$U query "quick mode" --profile $P; $U show dec:A115 --profile $P
```

From a session working on Who Did It, use the `udgt-consult` skill: it answers "why is it like this"
from this folder before you change the game.

## Fonts

`build` copies the game's font files into `explorer/fonts/`: Press Start 2P, Pixelify Sans, Inter
and Oswald, all under the SIL Open Font License 1.1, as the game's `CREDITS.md` records. They are used
only to dress the explorer and are not versioned here.
