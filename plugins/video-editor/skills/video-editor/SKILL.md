---
name: video-editor
description: Edit video by conversation, with local tools. Use when the user wants to cut highlight clips from long video, make vertical 9:16 shorts, edit a talking head or interview into one polished video, cut an action or rhythm montage on impacts, add captions, a colour grade or animated overlays, or prepare and (only when they say so) publish the result. Starts with a short questionnaire so only one recipe's tools are used.
---

# video-editor

All paths here start from `${CLAUDE_PLUGIN_ROOT}`. If a path shows a literal `$` followed by
`{CLAUDE_PLUGIN_ROOT}`, the variable was not expanded; ask the user for the plugin folder.

Everything goes through one command-line tool. **Wherever a plan, a playbook or this file writes `ve <command>`,
run `python "${CLAUDE_PLUGIN_ROOT}/bin/ve.py" <command>`.** It needs no install: the launcher puts the plugin's
`src/` on the path. Session output goes to `<videos_dir>/edit/` next to the source footage, never into the
plugin folder.

## 0. Check the machine first

```bash
python "${CLAUDE_PLUGIN_ROOT}/bin/ve.py" doctor
```

It reports, by name only, what is installed (ffmpeg, ffprobe, numpy, Pillow are required) and which optional
extras are missing, each with the `pip install` that adds it. Install nothing large without asking: the extras
`speech-plus` (whisperX) and `stems` (Demucs) pull in torch, several GB. For transcription the user needs
`pip install faster-whisper` (the `speech` extra); the model downloads once on first use and no key is needed.

## 1. Ask first (this is what keeps competing tools out)

Run `ve ask --schema` to get the questions as JSON, then ask the USER those questions (batch them in one
AskUserQuestion call where possible; skip the ones that clearly do not apply). Then:

```bash
ve ask <source.mp4> [more sources] --answers '{"deliverable":"vertical","content":"dialogue","goal":"highlights","captions":"opus"}' --edit-dir <videos_dir>/edit
ve plan --edit-dir <videos_dir>/edit
```

`ve ask` probes the source, prunes questions that do not apply (no reframe question when the source is already
vertical, no captions or goal questions for action footage), saves `brief.json`, and selects ONE recipe. `ve plan`
prints that recipe's concrete steps and the path to its playbook. Read the playbook, then follow the steps. Do not
use tools from other recipes.

| Recipe | Chosen when | Core tools |
|---|---|---|
| `highlight_clips` | dialogue + goal=highlights | transcribe, pack, cut, reframe, finish |
| `long_form` | dialogue + goal=single_edit | transcribe, pack, edl, captions, render, timeline |
| `action_montage` | content=action (no Whisper, no captions) | find, verify, edl, render |
| `explainer` (add-on) | overlays != none | overlay (PIL or Remotion), or Manim slots |

## 2. Rules that apply in every recipe

1. Confirm the plan with the user in plain English before cutting.
2. Never cut inside a word; pad every cut edge 30-200 ms; 30 ms audio fades at every cut (`render` does the fades).
3. Captions are applied LAST in the filter chain; caption times are on the output timeline.
4. Cache transcripts; never re-transcribe an unchanged source.
5. Verify your own output before showing it: `ve timeline` on the RENDERED file at each cut boundary; measure
   loudness rather than guessing; cap self-evaluation at 3 passes.
6. Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort. Say so.
7. Action footage: always `ve verify` strikes visually before rendering; audio finds the sound, not the picture.
8. Never skip a recipe step silently; if something cannot be tested or done, tell the user.

## 3. Optional upgrades (only if the user has installed the extra; never install them silently)

| Situation | Use | Extra |
|---|---|---|
| Cut edges or captions drift; need speaker labels | `ve transcribe --backend whisperx [--diarize --max-speakers 2]` (diarize needs `HF_TOKEN`) | `speech-plus` |
| Two people, vertical output, diarized transcript exists | `ve reframe --mode pan --turns <transcript.json> --speaker-map SPEAKER_00=left,SPEAKER_01=right --clip-start S` | `speech-plus` |
| Music under speech | `ve transcribe --clean-speech` (or `ve separate --stems vocals no_vocals`) | `stems` |
| Action footage with a soundtrack | `ve find --stem drums` | `stems` |
| Titles or caption pages as an overlay | `ve overlay "Title" --engine remotion [--captions-from edl.json] [--transparent]` | Node, and a Remotion licence check |

whisperX still gives untimed words for tokens like "$13.60"; they are interpolated, so treat their timing as
approximate. Manim overlays: read `${CLAUDE_PLUGIN_ROOT}/skills/manim-video/SKILL.md` (needs LaTeX and `pip install manim`).

## 4. Publishing (only when the user asks; read `${CLAUDE_PLUGIN_ROOT}/src/videoeditor/recipes/playbooks/publish.md` first)

`ve publish prepare | plan | init | send | handoff | status | revoke`. It is a dry run until the USER says to send.
It uses official platform APIs only, and nothing in it has been run against a live account (see the plugin README).

- **Never** pass `--yes`, `--public`, `--accept-cost` or `--force`, and never run `ve publish init` or `revoke`,
  on your own judgement: each needs the user's explicit instruction in this conversation, per platform.
- **Never read, print, echo or ask for a credential value.** The user pastes tokens into `ve publish init` at their
  own terminal, or sets the `VE_<PLATFORM>_*` environment variables. `ve doctor` and `ve publish status` report
  presence by name only. Never open the OS keyring or an `.env` file.
- Never choose the YouTube "made for kids" declaration for them, and never decide `--ai-generated` or `--branded` for them.
- A platform that refuses `--yes` without `--public` (Bluesky, X) is working as intended; do not work around it.

## 5. Command reference

`ve ask | plan | doctor | transcribe | pack | find | separate | verify | cut | reframe | edl | captions | render |
grade | timeline | overlay | finish | publish` (`ve <cmd> --help` for flags; `render`, `grade`, `timeline` pass extra
flags through, for example `ve render edl.json -o out.mp4 --preview`).

Adding a use case: a recipe module in `${CLAUDE_PLUGIN_ROOT}/src/videoeditor/recipes/`, a playbook, and a branch in
`questionnaire.select_recipes`.
