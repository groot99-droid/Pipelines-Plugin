# Right Door, Wrong Exit — teardown

The UDGT teardown of [Right Door, Wrong Exit](https://github.com/groot99-droid/Right-Door-Wrong-Exit),
made with the `udgt` plugin (`plugins/udgt/`). Its scope is the loop, the screens and the glitch, the
walk and the mini games, the seven rooms and their captions and logs, the video, procedural rooms and
sound, the engine on phones, and the history.

| File | What it is | Written by |
|---|---|---|
| `profile.json` | What to read in the game and how: the README (its only document) and its tables (the loop, inputs, mini games, what moves), the scene ids it cites, the code anchors (the chapters, captions, logs and clock stamps in `script.js`, the scene registry, the synthesized sounds, the pile generators), the seven stages and their prompts, the reference games, the explorer's views | by hand, with the owner |
| `teardown.json` | The extracted graph | `udgt.py scan` |
| `answers.json` | The owner's answers to the briefs, verbatim (none yet) | `udgt.py record` |
| `chapters/NN-<slug>.md` | One chapter per stage (none yet) | Claude, after each brief |
| `explorer/` | The page, in the game's amber on black (not versioned) | `udgt.py build` |

## Use it

The game is read from a sibling checkout (`../Right-Door-Wrong-Exit` beside this repo, or `--game <path>`,
or `UDGT_GAME`). Nothing is written into the game.

```
U="python plugins/udgt/engine/udgt.py"; P=teardowns/right-door-wrong-exit/profile.json
$U scan  --profile $P
$U check --profile $P
$U brief 0 --profile $P
$U build --profile $P && python -m http.server --directory teardowns/right-door-wrong-exit 8791
```

## What the first scan found

The game has no design documents, data files or CSS custom properties: its design lives in the README
and in `script.js`'s `CHAPTERS` array. So the teardown reads the README's tables and pulls the chapters,
captions, logs and stamps out of the code as anchors, and the explorer's theme is written from the
colours in `styles.css` rather than mapped onto tokens. Share Tech Mono, Oswald and American Typewriter
are named by the game but not shipped with it, so the page falls back as the game does.
