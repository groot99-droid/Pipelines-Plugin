# Ninety-Nine — teardown

The UDGT teardown of [NINETY-NINE](https://github.com/groot99-droid/The-Intern) (the repo is The-Intern),
made with the `udgt` plugin (`plugins/udgt/`). Its scope is the interface, the sets and scenes as data,
the spine and the walked choice, the engine and audio, the building and its canon, the art and audio
pipelines, the history (the video era, the retired mini-games) and what is stale or next.

| File | What it is | Written by |
|---|---|---|
| `profile.json` | What to read in the game and how: the four specs and the vault notes beside the code, the `Doc N §x` citations, canon `C1`–`C8`, scene and room keys, the spine and mini-game tables, the data files, the code anchors (the beat vocabulary, the set builders, the synthesized cues), the nine stages and their prompts, the reference games, the explorer's views | by hand, with the owner |
| `teardown.json` | The extracted graph | `udgt.py scan` |
| `answers.json` | The owner's answers to the briefs, verbatim (none yet) | `udgt.py record` |
| `chapters/NN-<slug>.md` | One chapter per stage (none yet) | Claude, after each brief |
| `explorer/` | The page, in the company's Courier and the building's black (not versioned) | `udgt.py build` |

## Use it

The game is read from a sibling checkout (`../The-Intern` beside this repo, or `--game <path>`, or
`UDGT_GAME`). Nothing is written into the game.

```
U="python plugins/udgt/engine/udgt.py"; P=teardowns/ninety-nine/profile.json
$U scan  --profile $P            # after the game changes; `diff` first shows what moved
$U check --profile $P            # broken citations, stale scan, chapter links
$U brief 0 --profile $P          # the first stage's questions for the owner
$U build --profile $P && python -m http.server --directory teardowns/ninety-nine 8791
# then open http://127.0.0.1:8791/explorer/index.html
```

## What the first scan found

`check` reports four citations that point nowhere. Three cite Doc 1 §9.1 and §9.2, which are bold
paragraphs inside §9, not headings, so the engine cannot split them out. One is a real slip in the game:
Doc 1 §6 cites Doc 4 §4.3, and Doc 4 §4 has only 4.1 and 4.2.

The game uses system fonts (Courier New, Times New Roman), so no font files are copied.
