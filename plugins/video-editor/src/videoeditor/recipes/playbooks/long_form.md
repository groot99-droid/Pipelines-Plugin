# Playbook: long_form

Principles: audio first, visuals follow. Reason from `takes_packed.md`; drill into `ve timeline` only at
decision points. Ask -> confirm -> execute -> iterate -> persist (`project.md`).

Hard rules: captions LAST; per-segment extract then lossless concat; 30ms audio fades at every boundary;
overlay PTS shifted to its window; caption times on the OUTPUT timeline; never cut inside a word; pad
every cut edge 30-200ms; cache transcripts; confirm the plain-English strategy before cutting; all outputs
under `<videos_dir>/edit/`.

Better timing: with the `speech-plus` extra, `ve transcribe --backend whisperx` aligns words against the audio
(on a synthetic test its word starts were about 3x closer to true onsets than faster-whisper's; confirm on real
footage). Music under the speech: `ve transcribe --clean-speech` (needs `stems`).

Whisper caveat: fillers ("um", "uh") may be absent from the transcript. Listen-free detection of them is
limited to silence gaps >= 400ms. Tell the user filler removal is best-effort with local Whisper.

Self-eval before showing the user: `ve timeline` on the RENDERED output at each cut boundary (+-1.5s),
first/last 2s, a few midpoints; check loudness with `ffmpeg -af ebur128=peak=true`. Cap at 3 passes.
Publishable work: have a critic sub-agent review the render.

Cut craft: candidate cuts from word boundaries and silences >= 400ms; keep laughs/reactions; 400-600ms air
between speakers; never reason audio and video independently.
