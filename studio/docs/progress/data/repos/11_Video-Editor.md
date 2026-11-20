# Video-Editor

**Questionnaire-driven video editor (now a plugin inside ROSW).** Source: https://github.com/groot99-droid/Video-Editor

Generated 20 November 2026 from the repository clone (`git log`, `git ls-files`, and the files at HEAD). Counts are as cloned. Commit dates are git author dates in UTC and can differ from when the work was done (merged PRs, integration passes).

## 1. Numbers

| Measure | Value |
|---|---|
| Commits (all branches) | 12 (9 non-merge, 3 merge) |
| First commit | 2026-09-23 |
| Last commit | 2026-11-19 |
| Days with commits | 3 |
| Tracked files | 89 |
| Checked-out branch | HEAD |
| Commit authors (non-merge, by name) | Claude: 5; groot99-droid: 4 |

Author names are git author names: "Claude" marks commits made by a Claude session, and the owner's GitHub handle marks commits made by the owner. Email addresses are left out.

**Tracked files by type (top 15):** .py 53; .md 24; (none) 2; .license 2; .json 2; .tsx 2; .ts 2; .toml 1; .sh 1

**Tracked files by top-level folder:** src 54; skills 18; tests 11; (root) 4; LICENSES 2

## 2. Activity by month and by day

| Month | Non-merge commits |
|---|---|
| 2026-09 | 1 |
| 2026-10 | 7 |
| 2026-11 | 1 |

**Per day (non-merge commits):** 2026-09-23 1; 2026-10-29 7; 2026-11-19 1

## 3. Layout (folders and file counts)

- **src/** 54 files
  - src/videoeditor/ 54
- **skills/** 18 files
  - skills/manim-video/ 17
  - skills/video-editor/ 1
- **tests/** 11 files
- **(repository root)** 4 files
- **LICENSES/** 2 files

## 6. Documents inventory (24 Markdown files)

Markdown files by folder (top 25): skills/manim-video/references 14; src/videoeditor/recipes/playbooks 5; skills/manim-video 2; (root) 1; skills/video-editor 1; src/videoeditor/templates/remotion_overlay 1

- `README.md` (967 words): Video-Editor. Sections: Use cases (recipes); Install (Linux); Use; Publishing (`ve publish`); Known limits
- `skills/manim-video/README.md` (111 words): Manim Video Skill. Sections: What it does; Use cases; Prerequisites
- `skills/manim-video/SKILL.md` (1593 words): Manim Video Production Pipeline. Sections: Creative Standard; Prerequisites; Modes; Stack; Pipeline; Project Structure; Creative Direction; Workflow; Critical Implementation Notes; Performance Targets
- `skills/manim-video/references/animation-design-thinking.md` (1117 words): Animation Design Thinking. Sections: Should I animate this?; Decomposing a concept into animation; Pacing: the universal mistake is too fast; Narration synchronization; Equation decomposition strategy; Architecture and pipeline diagrams; Common design mistakes
- `skills/manim-video/references/animations.md` (959 words): Animations Reference. Sections: Core Concept; Creation Animations; Removal Animations; Transform Animations; The .animate Syntax; Additional Creation Animations; Movement Animations; Emphasis Animations; Rate Functions; Composition
- `skills/manim-video/references/camera-and-3d.md` (377 words): Camera and 3D Reference. Sections: MovingCameraScene (2D Camera Control); ThreeDScene; When to Use 3D; When NOT to Use 3D; ZoomedScene — Inset Zoom; LinearTransformationScene — Linear Algebra
- `skills/manim-video/references/decorations.md` (574 words): Decorations and Visual Polish. Sections: SurroundingRectangle; BackgroundRectangle; Brace and BraceLabel; Arrows for Annotation; DashedLine and DashedVMobject; Angle and RightAngle Markers; Cross (strikethrough); Underline; Color Highlighting Workflow; Combining Annotations
- `skills/manim-video/references/equations.md` (705 words): Equations and LaTeX Reference. Sections: Basic LaTeX; Step-by-Step Derivations; Selective Color; Building Incrementally; Highlighting; Annotation; Common LaTeX; Matrices; Cases and Piecewise Functions; Aligned Environments
- `skills/manim-video/references/graphs-and-data.md` (482 words): Graphs, Plots, and Data Visualization. Sections: Axes; Plotting; Animated Plotting; Bar Charts; Number Lines; Animated Counters; Algorithm Visualization Pattern; Data Story Pattern; Graph / DiGraph — Graph Theory Visualization; ArrowVectorField / StreamLines — Vector Fields
- `skills/manim-video/references/mobjects.md` (1140 words): Mobjects Reference. Sections: Text; Shapes; Polygons and Arcs; Sectors and Annuli; Positioning; VGroup vs Group; Styling; Specialized Mobjects; Custom Mobjects; Matrix Mobjects
- `skills/manim-video/references/paper-explainer.md` (1297 words): Paper Explainer Workflow. Sections: Why animate a paper?; Who is watching?; The 5-minute template; Pre-code workflow; Hook (30s); Problem (60s); First-principles equation explanation; Building architecture diagrams; Animating results; Domain-specific patterns
- `skills/manim-video/references/production-quality.md` (927 words): Production Quality Checklist. Sections: Pre-Code Checklist; Text Quality; Spatial Layout; Animation Quality; Color Quality; Data Visualization Quality; Pre-Render Checklist; Post-Render Checklist
- `skills/manim-video/references/rendering.md` (651 words): Rendering Reference. Sections: Prerequisites; CLI Reference; Quality Presets; Output Structure; Stitching with ffmpeg; Add Voiceover; Add Background Music; GIF Export; Aspect Ratios; Render Workflow
- `skills/manim-video/references/scene-planning.md` (455 words): Scene Planning Reference. Sections: Narrative Arc Structures; Scene Transitions; Cross-Scene Consistency; Scene Checklist; Duration Estimation; Planning Template; Overview; Color Palette; Arc: [Discovery / Problem-Solution / Comparison / Build-Up]; Scene 1: [Name] (~Ns)
- `skills/manim-video/references/troubleshooting.md` (516 words): Troubleshooting. Sections: LaTeX Errors; VGroup TypeError; Group save_state() / restore() Not Supported; letter_spacing Is Not a Valid Parameter; Animation Errors; Rendering Issues; Common Mistakes; Debugging Strategy
- `skills/manim-video/references/updaters-and-trackers.md` (993 words): Updaters and Value Trackers. Sections: The problem updaters solve; ValueTracker: an invisible steering wheel; Types of updaters; DecimalNumber: showing live values; Removing updaters; Animation-based updaters; Practical patterns; Common mistakes
- `skills/manim-video/references/visual-design.md` (651 words): Visual Design Principles. Sections: 12 Core Principles; Layout Templates; Color Palettes; Font Selection; Visual Hierarchy Checklist
- `skills/video-editor/SKILL.md` (718 words): video-editor. Sections: 1. Ask first (this is what keeps competing tools out); 2. Rules that apply in every recipe; 3. Optional upgrades (only if the user has installed the extra; never install them silently, they are large); 4. Publishing (only when the user asks; read `src/videoeditor/recipes/playbooks/publish.md` first); 5. Command reference
- `src/videoeditor/recipes/playbooks/action_montage.md` (184 words): Playbook: action_montage
- `src/videoeditor/recipes/playbooks/explainer.md` (225 words): Playbook: explainer (overlay add-on)
- `src/videoeditor/recipes/playbooks/highlight_clips.md` (243 words): Playbook: highlight_clips
- `src/videoeditor/recipes/playbooks/long_form.md` (217 words): Playbook: long_form
- `src/videoeditor/recipes/playbooks/publish.md` (376 words): Playbook: publish (optional closing step). Sections: What you may do without asking; What needs the user's explicit instruction, every time; Declarations that belong to the user; Writing the post; Platform behaviour to tell the user about; When something fails
- `src/videoeditor/templates/remotion_overlay/README.md` (82 words): remotion_overlay (slot template)

## 9. Skills, agents and plugins

- `skills/manim-video/SKILL.md`: "Production pipeline for mathematical and technical animations using Manim Community Edition. Creates 3Blue1Brown-style explainer videos, algorithm visualizations, equation derivations, architecture diagrams, and data stories. Use when users request: animated 
- `skills/video-editor/SKILL.md`: Edit video by conversation. Use when the user wants to cut clips from long video, make vertical/9:16 shorts, edit a talking-head or interview into one polished video, cut an action/rhythm montage on impacts, or add animated overlays and captions. Starts with a

## 10. Pull requests merged (1)

- 2026-11-19 #5 from `groot99-droid/claude/inspiring-cori-juqfrm`

## 11. Source documents (verbatim)

Each file below is quoted from the repository at HEAD. Lines start with ">" so its headings do not mix with this document's.

### Source file: README.md

> # Video-Editor
>
> > **Status, 2026-11-19: this repository is the original, kept as of its PR #3 (2026-10-29).** The maintained version is the `video-editor` plugin in groot99-droid/Pipelines-Plugin (`plugins/video-editor/`), which moved this code in and has gone on since: `ve doctor`, the `bin/ve.py` launcher (runs from a plugin install with no `pip install`), the publish guard hook, the `/ve-doctor` command, the `video-editor-render-qa` agent, the `manim-video` creative-direction reference and `UNVERIFIED.md`, the checklist of what has not been run against a live account. Make changes there; this copy is not kept in step.
>
> One questionnaire-driven video editor, merged from [video-use](https://github.com/browser-use/video-use) and
> [clipify](https://github.com/louisedesadeleer/clipify). You answer a few questions first; the answers select a single
> use-case recipe, so vertical-vs-landscape, dialogue-vs-action and similar choices never compete.
>
> ## Use cases (recipes)
>
> | Recipe | For |
> |---|---|
> | `highlight_clips` | pull the best moments from long dialogue; optional 9:16 reframe (center / speaker-pan / split-screen) and captions |
> | `long_form` | one polished edit: cut retakes, grade, caption, QA |
> | `action_montage` | cut on every strike/beat via audio transients; no speech needed |
> | `explainer` (add-on) | animated overlays: PIL cards built in, Manim/HyperFrames/Remotion on demand |
>
> More recipes can be added: a module in `src/videoeditor/recipes/`, a playbook, and one branch in the questionnaire.
>
> ## Install (Linux)
>
> ```bash
> sudo apt-get install ffmpeg          # ffmpeg + ffprobe
> pip install -e '.[speech,dev]'       # faster-whisper (local transcription) and pytest
> ```
>
> Optional extras (each is lazy-loaded; the base install stays light):
>
> | Extra | Adds | Improves |
> |---|---|---|
> | `speech-plus` | [whisperX](https://github.com/m-bain/whisperX): forced word alignment, optional speaker labels (`ve transcribe --backend whisperx [--diarize]`) | tighter cut edges and captions; `ve reframe --turns` follows real speaker turns. Several GB (torch). Diarization needs a Hugging Face token and the pyannote terms; NLTK `punkt_tab` is downloaded once |
> | `stems` | [Demucs](https://github.com/adefossez/demucs) (maintained fork, v4.1): `ve separate`, `ve transcribe --clean-speech`, `ve find --stem drums` | music under speech; action montages with a soundtrack. About 1.5x track length on CPU |
> | (Node) | Remotion overlay template: `ve overlay --engine remotion` | titles and caption pages as overlays, opaque MP4 or transparent WebM. Needs Node 20.19+/22.13+; Remotion has its own [licence](https://www.remotion.pro/license) (free for individuals, for-profit orgs up to 3 people, non-profits) |
>
> ## Use
>
> ```bash
> ve ask my_video.mp4                  # interactive questionnaire -> edit/brief.json -> recipe
> ve plan --edit-dir edit              # the recipe's concrete steps + playbook path
> ```
>
> Agents: copy or symlink `skills/video-editor` into your skills directory; it drives the same CLI.
> Run `ve --help` for every command. Tests: `pytest`.
>
> ## Publishing (`ve publish`)
>
> A safer rebuild of the idea behind browser-automation posters. It uses **official platform APIs only**: OAuth or app
> tokens, no passwords, no cookies, no headless browser, no user-agent spoofing. Install: `pip install -e '.[publish]'`.
>
> ```bash
> ve publish prepare --video final.mp4 --caption "..." --platforms youtube,mastodon --not-made-for-kids   # checks only
> ve publish plan                                  # dry run: what each platform would get, in which mode
> ve publish init youtube                          # one-time login (tokens go to the OS keyring or env vars, never a file)
> ve publish send --platform youtube --yes         # sends as PRIVATE; add --public to post publicly
> ve publish handoff                               # no API at all: where to upload + the caption to paste
> ```
>
> Rules enforced in code (and tested): nothing is sent without `--yes`, one platform per command; **private/draft is the
> default** wherever a platform has one; platforms with no private mode (Bluesky, X) refuse unless you pass `--public`; X
> also needs `--accept-cost` (pay-per-post); validation errors block sending; the same video + platform + mode + text is
> sent once (an idempotency ledger in `<edit>/publish_ledger.jsonl`, `--force` to repeat); secrets are never written to a
> file (without a keyring, use `VE_<PLATFORM>_<NAME>` environment variables); the "made for kids" declaration for YouTube is
> never defaulted; `--ai-generated` / `--branded` are passed to platforms that have a field for them.
>
> | Platform | Default (no `--public`) | `--public` | Notes |
> |---|---|---|---|
> | YouTube | private upload | public | official docs say unverified API projects are not forced private; 1 quota unit per upload, 100/day |
> | Mastodon | followers-only | public | token from your instance; limits read from the instance |
> | LinkedIn | connections-only | public | no draft state exists for API posts; 60-day tokens, no refresh for self-serve apps (`init --manual` if localhost redirects are refused) |
> | TikTok | inbox upload (finish in the app; caption not sent) | Direct Post | non-private posting needs an audited app |
> | Instagram Reels | container prepared, **not published** (expires in 24 h) | publish | professional account + Meta app; token and user id supplied by you |
> | Bluesky | refused | public | no private posts exist |
> | X | refused | public + `--accept-cost` | pay-per-use pricing |
>
> **Verified against official docs, but never run against a live account** (no accounts or app approvals exist in the
> build environment): request shapes are unit-tested against a fake network and, for the trickiest transports
> (multipart, streamed files, Content-Range, basic auth), against a local HTTP server. Details that the docs left open
> and that may need adjusting on first real use: Bluesky's service-auth audience/method for video upload (taken from
> Bluesky's own client), whether LinkedIn's userinfo `sub` equals the id in `urn:li:person` (override with
> `VE_LINKEDIN_PERSON_ID`), whether Instagram resumable upload is available to your login type (or host the file and set
> `VE_INSTAGRAM_VIDEO_URL`), TikTok's scope separator, X's billing of media-upload calls, and what YouTube counts as a Short.
>
> ## Known limits
>
> - Local Whisper normalizes fillers ("um", "uh"), so filler removal is best-effort.
> - Speaker-follow reframing uses motion inside two hand-placed face regions by default and needs a static camera; real speaker turns need the optional whisperX diarization (not testable without a Hugging Face token).
> - Manim needs LaTeX; HyperFrames needs Node 22.
>
> See `NOTICE` for attribution.
>

## 12. Full commit log (date, hash, subject)

Every commit, oldest first. Merge commits are shown with their subjects.


### 2026-09

- 2026-09-23 dc5e9004 Initial commit

### 2026-10

- 2026-10-29 46b46aba Merge video-use and clipify into a questionnaire-driven editor
- 2026-10-29 ff9701ff Tidy: remove dead code and duplicate CLIs, friendlier missing-extra error
- 2026-10-29 d1d4cb10 Merge video-use and clipify into a questionnaire-driven editor (#1)
- 2026-10-29 fa5bfac7 Add optional backends: whisperX, Demucs stems, Remotion overlay template
- 2026-10-29 e10b3d0d Merge remote-tracking branch 'origin/claude/happy-davinci-2jcki7' into claude/happy-davinci-2jcki7 [merge]
- 2026-10-29 06931946 Add optional backends: whisperX, Demucs stems, Remotion overlay template (#2)
- 2026-10-29 8838527b Add ve publish: official-API publishing with dry-run, private/draft-by-default and an idempotency ledger
- 2026-10-29 14501ea4 Merge remote-tracking branch 'origin/claude/happy-davinci-2jcki7' into claude/happy-davinci-2jcki7 [merge]
- 2026-10-29 7b0de770 Add ve publish: official-API publishing, dry-run and private/draft by default (#3)

### 2026-11

- 2026-11-19 abddf706 docs: README says the maintained version is the Pipelines-Plugin video-editor plugin, and what it has that this copy lacks
- 2026-11-19 3dbf531a Merge pull request #5 from groot99-droid/claude/inspiring-cori-juqfrm [merge]
