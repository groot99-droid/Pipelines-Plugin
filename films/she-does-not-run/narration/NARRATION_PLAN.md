# She Does Not Run: narration plan

Status: **draft for approval**. Nothing has been generated.

## Voice

The narrator is the scientist herself, speaking in the first person, quietly, after the fact.

- **How it matches her:** her clips carry almost no dialogue (voice-band level about −34 LUFS), so there is no
  on-screen voice to copy. Instead the voice is generated from her look. **Seed Audio 1.0** accepts an image
  reference, and it gets the same scientist still that keeps her face consistent in the video
  (`edit/refs/scientist_crop.jpg`, Higgsfield media 3d76dc6c…).
- **Voice prompt:** "A woman in her late thirties, Indonesian, speaking English with a light Indonesian accent.
  Low, warm, slightly husky; tired but steady; close to the microphone, unhurried, no performance."
- **Keeping it the same across lines:** line 1 is generated as **3 takes**, and you pick one. Every other line
  then uses that take as its audio reference, so all 11 lines share one voice.
- **Pace:** about 2.2 words per second, slower than normal speech. Every line fits its window with room left over.

## Narration windows

The times are on the v4 timeline (2:18). Narration stays clear of the loud moments: the snare hit, the knife,
the knockdown, the rifle shot, the explosion and the flight. In those stretches the picture and the sound
effects carry the story.

| # | Window (s) | Over | Room | Line | Words |
|---|---|---|---|---|---|
| L1 | 3.6 – 13.2 | dusk ranger post → antenna | 9.6 s | For six years, her collar has told me where she sleeps, where she feeds, where she bathes. Tonight, it stopped moving. | 21 |
| L2 | 14.2 – 20.0 | she moves through the jungle | 5.8 s | A rhino that stops moving at night is either asleep… or caught. | 12 |
| L3 | 21.0 – 26.0 | hands tying the snare | 5.0 s | Wire is cheap. A horn is worth a fortune. | 9 |
| L4 | 32.2 – 37.4 | she lowers the binoculars | 5.2 s | Three men. Three torches. And somewhere out there… her. | 9 |
| — | 37.7 – 44.0 | the snare hits | | *(no narration)* | |
| L5 | 44.5 – 55.2 | trapped → she reads the wire | 10.7 s | Snares don't kill quickly. They hold. The harder she fights the wire, the deeper it cuts. | 16 |
| L6 | 56.3 – 61.6 | the eye | 5.3 s | She doesn't run. She watches me decide. | 7 |
| — | 61.9 – 76.0 | knife, release, knockdown | | *(no narration)* | |
| L7 | 76.4 – 81.2 | the boot touch | 4.8 s | She could have crushed me. She didn't. | 7 |
| L8 | 82.0 – 87.2 | poachers load the truck | 5.2 s | The men who set the wire were coming back for her. | 11 |
| — | 87.4 – 109.5 | headlights, shot, explosion, flight | | *(no narration)* | |
| L9 | 110.0 – 113.2 | watching the fire | 3.2 s | They won't come back tonight. | 5 |
| L10 | 116.0 – 121.3 | dawn, she walks into the river | 5.3 s | At first light, she does what her kind has always done. | 11 |
| L11 | 127.5 – 132.8 | drone rises over the plantation | 5.3 s | Her forest is an island now. And the sea keeps rising. | 11 |
| L12 *(optional)* | 133.6 – 137.6 | end card | 4.0 s | There may be fewer than fifty of them left. | 9 |

L12 repeats the end card's own text. Leave it out to let the card speak in silence, which is my recommendation;
keep it if the film may be watched without the sound on screen being read.

## Delivery notes (go into each prompt)

- L1–L4: hushed, almost a whisper by L4 (she is hiding).
- L5: matter-of-fact, clinical: the scientist talking.
- L6, L7: slower, with a pause at the full stop; L7 a little shaken.
- L8: flat, hard.
- L9: an exhale, quietly relieved.
- L10, L11: the warmest lines, unhurried; L11 lets "rising" fall away.

## The mix (in `finish.py`)

- The narration WAVs go in as cues placed by their window start, at about −16 LUFS each, so speech sits on top.
- **Ducking:** music, beds and the clips' own sound pass through a sidechain compressor keyed by the narration.
  They drop about 8 dB under each line, with a 20 ms attack and a 400 ms release, then come back up. The
  explosion and rifle shot are never under narration, so they stay at full level.
- Loudness is still normalised to −14 LUFS with peaks at or below −1.5 dB.

## And more

- **Subtitles:** an `.srt` sidecar written from the script and the measured line lengths, so a player can show
  them. It is not burned into the picture unless you want that.
- **Script file:** `narration/script.json` holds each line's text, window and delivery note. `finish.json`
  reads the timings from it, so re-recording one line means changing one file.
- **Title:** the title card stays silent, and the narration starts on the first image.

## Cost

| Item | Credits |
|---|---|
| 3 voice takes of L1 | 5.4 |
| L2–L11 (10 lines), plus L12 if kept | 18 – 19.8 |
| Allowance for about 5 retakes of single lines | 9 |
| **Total** | **about 32 – 34** (balance 3,974) |

Seed Audio 1.0 costs 1.8 credits per line (quoted). A preset voice through Text to Speech V2 would be 0.45 per
line, but none of the presets is built from her picture.

## Order after approval

1. Generate 3 takes of L1 with the image reference, and send them to you to pick one.
2. Generate L2–L11 (and L12 if wanted) with the chosen take as the audio reference.
3. Measure each line's length, check it fits its window, and retake any that run over.
4. Add the narration and ducking to `finish.py` and `finish.json`, write the `.srt`, re-render, and check
   loudness and that no line overlaps a hit.
5. Send v5.
