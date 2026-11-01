# video-editor

Claude Code plugin for editing video by conversation. A short questionnaire picks **one** use-case recipe, so
vertical vs landscape and dialogue vs action choices never compete. The editing runs locally on ffmpeg and
local Whisper; no API keys are needed for any of it.

| Piece | What it is |
|---|---|
| `video-editor` skill | Runs the questionnaire, follows the chosen recipe's playbook, and enforces the editing and publishing rules |
| `manim-video` skill | Production pipeline for Manim explainer overlays (vendored from video-use, see NOTICE) |
| `bin/ve.py` | Launcher: runs the CLI from the plugin folder or the install cache, no `pip install` |
| `src/videoeditor/` | The CLI (`ve`): questionnaire, recipes and playbooks, ffmpeg render, captions, reframe, publish |

## Install

```
/plugin marketplace add groot99-droid/Pipelines-Plugin
/plugin install video-editor@rosw
```

Then, in a folder of footage, ask for what you want ("cut the best clips from this interview into vertical
shorts with captions"). The skill starts by running `ve doctor` and asking the questionnaire.

## Setup

Required: Python 3.10+, `ffmpeg` and `ffprobe` on `PATH` (with the `subtitles` filter, i.e. libass), and
`pip install numpy pillow`. For transcription: `pip install faster-whisper` (free, local; the model downloads once).

Run `python plugins/video-editor/bin/ve.py doctor` (or `ve doctor`) to see what is missing. It prints names only,
never a credential value.

| Extra (pip, from this folder) | Adds | Improves |
|---|---|---|
| `.[speech]` | faster-whisper | local transcription (all dialogue recipes) |
| `.[speech-plus]` | whisperX | tighter word timing; optional speaker labels (needs a Hugging Face token for diarization; NLTK `punkt_tab` is fetched once). Several GB (torch) |
| `.[stems]` | Demucs | music under speech (`--clean-speech`), drums for action montages (`--stem drums`). About 1.5x track length on CPU |
| `.[publish]` | requests, keyring | `ve publish` |
| (Node 20.19+/22.13+) | Remotion template | `ve overlay --engine remotion`. Remotion is not open source: free for individuals, for-profit organisations of up to 3 people and non-profits, otherwise a company licence |

## Recipes

| Recipe | For |
|---|---|
| `highlight_clips` | pull the best moments from long dialogue; optional 9:16 reframe (centre, speaker pan, split screen) and captions |
| `long_form` | one polished edit: cut retakes, grade, caption, QA |
| `action_montage` | cut on every strike or beat via audio transients; no speech needed |
| `explainer` (add-on) | animated overlays: PIL cards built in, Remotion template, Manim on demand |

A new use case is a recipe module, a playbook and one branch in the questionnaire.

## Publishing (`ve publish`)

Official platform APIs only: no passwords, cookies, headless login or user-agent spoofing. **Dry run by default;
private or draft by default** wherever a platform has one; nothing sends without `--yes` (one platform per
command); Bluesky and X have no private mode and refuse without `--public` (X also needs `--accept-cost`); an
idempotency ledger stops an identical re-send. Credentials live in the OS keyring or `VE_<PLATFORM>_*`
environment variables, never in a file, and never in this plugin.

| Platform | Default (no `--public`) | `--public` |
|---|---|---|
| YouTube | private upload | public |
| Mastodon | followers-only | public |
| LinkedIn | connections-only (no draft exists for API posts) | public |
| TikTok | inbox upload, finish in the app (caption not sent) | Direct Post |
| Instagram Reels | container prepared, not published | publish |
| Bluesky | refused | public |
| X | refused | public + `--accept-cost` |

`ve publish handoff` needs no API at all: it prints where to upload and the caption to paste.

## What is not verified

- **`ve publish` has never been run against a live account.** Request shapes follow the platforms' official
  docs and are tested against a fake network and a local HTTP server. Open points to check on first real use
  (Bluesky's video service-auth audience, LinkedIn's person id, localhost redirects for LinkedIn/TikTok,
  Instagram resumable upload, X media billing) are listed in `UNVERIFIED.md`, with the rest of what is deferred.
- whisperX **speaker diarization** was not run (needs a Hugging Face token); real footage and real human speech
  were not used (all runs were on synthetic fixtures); GPU paths and Remotion-beyond-our-template
  engines were not run.
- Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort.

## Tests

```
python -m unittest discover -s plugins/video-editor/tests     # from the repo root; needs ffmpeg, numpy, pillow, requests
```

The tests run without installing the package and need none of the optional extras (their backends are faked).
