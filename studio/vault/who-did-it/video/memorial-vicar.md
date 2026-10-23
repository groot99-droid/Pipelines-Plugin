---
id: cmd_20261023_memorial-vicar
type: content-md
kind: video
title: Who Did It — the Vicar's memorial video
status: in-progress
created: 2026-10-23
updated: 2026-10-23
pipelines: [video-shot]
context_brand: [motion_language, narrative_continuity, visual_identity]
context_domain: []
artifacts:
  - path: who-did-it/video/memorial-vicar/shot1.mp4
    role: variant
  - path: who-did-it/video/memorial-vicar/shot2.mp4
    role: variant
  - path: who-did-it/video/memorial-vicar/shot3.mp4
    role: variant
  - path: who-did-it/video/memorial-vicar/memorial_master.mp4
    role: final
  - path: who-did-it/video/memorial-vicar/shot3_last.png
    role: reference
tags: [video, who-did-it, memorial, pixel-art]
---

## Overview

The memorial video for the Vicar in Who Did It: 21 seconds of 8-bit pixel art. The camera pans across a swaying lavender field to a lone orange tree under a bright sky with thick clouds, then slowly pushes in on the tree. It has no voice; the Vicar's words are captions in the round-7 cutscene. It was made through `video-shot` as three chained 7-second Higgsfield shots, each starting on the previous shot's last frame. The author kept all three, and the joined master is final. What remains is the game's file.

## Next Steps

- [ ] Make `apps/client/public/assets/video/memorial_vicar.webm` in Who-Did-It from `memorial_master.mp4`: VP9, 960x540, 24 fps, Vorbis audio, at most 2 MB. Mix a sound-library tension builder or riser under it. Add CREDITS and MANIFEST rows citing the three Higgsfield job ids and the sound's catalog id.
- [ ] A longer cut (up to 30 s) would need a fourth shot, starting from `shot3_last.png`. That is a new execute with its own go-ahead.

## Timeline

### 2026-10-23 · video-shot · who-did-it-vicar-memorial-f17a90
Execute, with the go-ahead given 2026-10-23 ("go ahead with all", then "yes"). Three shots of `flux_3_video` at 16:9, 720p, 7 s, without audio, each at 42 credits (126 in all), with no retries and no failures. Shot 1 is text-to-video (job 27560588-5c0b-49ca-b1d0-66d8ba89e39f). Shot 2 starts from shot 1's last frame (media d8aba9fe-8f01-4c4a-89a0-924617104a81, job b4434ac9-680a-4a74-bbfd-62881c3ea4a3). Shot 3 starts from shot 2's last frame (media 9a208384-b377-4774-9be4-f5a1acabcc99, job 83796721-9583-4b13-913d-4aff65917bdb). Each came back as h264, 1280x704, 24 fps, 7.04 s. The optional fourth shot was not run, since 21.1 s already meets the length. The shots were joined by hard cuts on matching frames (ffmpeg concat, stream copy). Review: every shot holds to the five attested constraints. Drift check: shot 3's frames were set beside shot 1's opening frame, and pixel scale, palette, sky, hills and tree are unchanged. Author's verdict: "make the memorial video", all three kept.
→ `shot1.mp4`, `shot2.mp4`, `shot3.mp4` (variant), `memorial_master.mp4` (final), `shot3_last.png` (reference)

## Method

```
model:         flux_3_video (the connector's recommendation, 2026-10-23; not binding)
aspect_ratio:  16:9          (attestation: generated imagery)
resolution:    720p          (the smallest above the game's 960x540)
duration:      7 s per shot  (attestation: shot lengths)
generate_audio:false         (intake: audio is mixed in after)
seed:          none: the model exposes no seed; continuity rides on the start frame
start image:   shot 1 none; shot N+1 = last frame of shot N, pulled with
               ffmpeg -sseof -0.1 -i shotN.mp4 -update 1 -frames:v 1 shotN_last.png,
               uploaded with media_upload and passed as medias[role=start_image]
shot index:    3 shots made; the next would be shot 4, from shot3_last.png
joined:        ffmpeg -f concat -i concat.txt -c copy memorial_master.mp4
```

Environment anchor, the opening of every prompt (the author's words from the brief):

> 8-bit pixel art, chunky pixels, limited palette. A swaying lavender field over wind-swept rolling hills, a lone orange tree in the near distance looming over the field, a bright blue sky filled with thick white puffy clouds. No text, no logos, no people, no faces.

Shot actions, appended to the anchor as sent:

1. Slow lateral pan from left to right across the lavender field, horizon locked, the lavender swaying in the wind, the orange tree entering frame on the right.
2. The camera continues its slow pan and settles with the orange tree at the centre, horizon locked, the clouds drifting slowly, the lavender swaying.
3. Slow push-in toward the orange tree, horizon locked, no zoom, the wind moving through the lavender and the leaves.

## Decisions in Force

- STATED 2026-10-22, camera grammar: a slow lateral pan or a slow push-in, horizon locked; no handheld motion and no zoom.
- STATED 2026-10-22, shot lengths: about 7 s per shot, three or four shots, 20 to 30 s in all.
- STATED 2026-10-22, transitions to avoid: no whip pans, flashes or spinning; hard cuts or a short dissolve only.
- STATED 2026-10-22, what persists between shots: the 8-bit pixel look, the game's world palette, and the same lavender field, orange tree, hills and sky.
- STATED 2026-10-22, generated imagery: motifs, framing, texture: 16:9, chunky pixel art, a limited palette, no text or logos in frame, no faces.
- The environment anchor above is used verbatim in every shot's prompt. The model has no seed, so a later shot starts from `shot3_last.png`.

## Links

- [[visual_identity]]
