# She Does Not Run

A 2:20 short film made from Higgsfield generations with the `video-editor` plugin. A conservation scientist
tracks a collared Sumatran rhino and finds poachers' snares. She cuts the rhino free, and is knocked down and
spared. She stops the poachers by firing at their truck's fuel tank from a ridge, and at dawn the rhino walks
into the river. The scientist narrates.

**Watch it:** the finished film, a 720p share copy, the subtitles and the narration lines are attached to the
GitHub release [`film-she-does-not-run-v5`](https://github.com/groot99-droid/Pipelines-Plugin/releases/tag/film-she-does-not-run-v5).

## What is here

This folder is the edit, not the media. The video and audio are large and are not versioned (see `.gitignore`).

| File | What it is |
|---|---|
| `ranges.json` | the cut list: 24 shots, each a source and an in/out point, in story order |
| `edl.json` | that cut list with its sources, as `ve edl` writes it; paths are relative to this folder |
| `finish.py` | the finishing pass `ve render` does not do: transitions (xfade), the sound mix (ducked clip audio, beds, music, SFX, narration with sidechain ducking) and two-pass loudness to −14 LUFS |
| `finish.json` | its cue sheet: which transition after which shot, and every sound cue placed by shot and offset |
| `narration/script.json` | the 12 narration lines: text, delivery note, window, placement, and the fitted length |
| `narration/fit.py` | fits each generated line to its window (shortens long pauses, at most 8% faster, −16 LUFS) and writes the cues and the `.srt` |
| `narration/NARRATION_PLAN.md` | the narration plan as approved |
| `She_Does_Not_Run.srt` | subtitles for the narration |
| `cards/` | the title and end cards (rendered with the plugin's PIL text card) |
| `refs/` | the two reference stills that keep the scientist and the rhino consistent across generated shots |

## Where the media comes from

- **Shots:** Higgsfield video generations: Seedance 2.0 and Kling 3.0 for the original 15, Seedance 2.0 for 7
  regenerated shots, Wan 3.0 for the 8 storyline shots (`N1` to `N7`, with `N5a`/`N5b`). The cut list expects
  them under `media/clips/` (originals) and `media/regen/` (regenerated and storyline shots). They are in the
  author's Higgsfield history, which the studio's generations library (`studio/library/`) catalogues.
- **Narration:** Seed Audio 1.0, preset voice Vera; the 12 fitted lines are attached to the release.
- **Music and SFX:** the author's sound library. `finish.json` points into `sound-library/files/`; fetch the files with
  `python sound-library/library.py fetch --id <id>` (the ids are the paths under `files/`).

## Rebuild

From this folder, with ffmpeg on `PATH` and the media in place:

```
python ../../plugins/video-editor/bin/ve.py render edl.json -o base.mp4 --no-loudnorm
python narration/fit.py
python finish.py finish.json -o She_Does_Not_Run.mp4
```

`ve render` writes the graded segments to `clips_graded/`, which `finish.py` joins. Every range edge is on a
whole frame, so picture and sound stay in sync.

## Not verified

- The music tracks were chosen by name, not by ear.
- `finish.py` lives here rather than in the plugin: transitions and a multi-track mix are not part of
  `ve render` yet.
