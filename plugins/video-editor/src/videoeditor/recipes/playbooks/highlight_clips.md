# Playbook: highlight_clips

Goal: 3-5 standalone clips of 10-25s from long dialogue.

Picking moments (read `takes_packed.md`, not raw JSON):
- Punchlines and reactions; setup question -> unexpected answer; awkward pauses; quotable one-liners;
  rapid back-and-forth (alternating short phrases).
- Propose each as `[start, end, why, title]`. Snap start/end to word boundaries; pad 30-200ms.
- Whisper-only caveat: fillers may be missing from the transcript, so do not promise filler removal here.

Reframing 16:9 -> 9:16 (only when the user chose vertical):
- `center`: single subject.
- `turns` (needs the `speech-plus` extra): `ve transcribe --backend whisperx --diarize --max-speakers 2`, read who is
  SPEAKER_00/01 in `takes_packed.md`, then `ve reframe --mode pan --turns ... --speaker-map ... --clip-start S`.
  Real speaker turns beat motion when hands or camera shake move the face boxes. Still place both ROIs.
- `pan`/`split`: two people. Sample one frame, eyeball each face's mouth+chin as `x,y,w,h`, draw boxes to
  check, at most two tuning passes. Motion-diff is forgiving. Camera must be static in the clip.
- Source 4K: scale ROI coordinates accordingly. Many scene cuts inside a clip break fixed ROIs; warn the user.

Captions: run `ve finish` on the reframed clip so timestamps are relative to the clip start.
Captions go LAST in the filter chain; keep the bottom ~30% clear of platform UI.

Hard rules that still apply (from video-use): never cut inside a word, 30ms audio fades at every cut,
strategy confirmed before execution, cache transcripts, outputs only under the edit dir.
