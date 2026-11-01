# Changelog

## Unreleased

- Command `/ve-doctor`; agent `video-editor-render-qa` (read-only render check); `manim-video` creative direction moved to `references/creative-direction.md`, non-standard `version:` dropped.

## 0.1.0

- Moved in from the standalone Video-Editor repository (its PRs #1 to #3), plus `ve doctor`
  and the `bin/ve.py` launcher so the plugin runs from an install cache with no `pip install`.
- Questionnaire (`ve ask`) selects one recipe: highlight clips, long-form edit, action montage, with an
  animated-overlay add-on. Local faster-whisper transcription; word-level JSON shared by every recipe.
- Reframe 16:9 to 9:16 (centre, speaker pan, split screen), one caption engine, grade, loudness, timeline QA.
- Optional extras: whisperX (word alignment, speaker turns), Demucs stems, a Remotion overlay template.
- `ve publish`: official APIs only, dry run by default, private/draft by default, idempotency ledger,
  credentials in the OS keyring or environment variables. YouTube, Mastodon, Bluesky, LinkedIn, TikTok,
  Instagram Reels, X. Never run against a live account; see README "What is not verified".
