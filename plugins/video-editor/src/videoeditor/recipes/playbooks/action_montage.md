# Playbook: action_montage

No Whisper, no captions. The impact sounds are the rhythm.

Detection: spectral flux in a band. Defaults `--band 1000:6000 --min-flux 30 --min-gap 0.6`.
- Too many false hits: raise `--min-flux` to 40-50. Too few: drop to 20 (then 15) before changing the band.
- Heavy thuds (kick, body shot): `--band 200:2000`. Clinks, snare cracks, whistles: `--band 4000:10000`.
- Drumming needs `--min-gap` ~0.2; chopping 0.6-1.0.

Music playing over the action? Add `--stem drums` (or `other` for clinks) to `ve find` so detection runs on the
separated stem (needs the `stems` extra; about 1.5x clip length on CPU). Cached under `<edit>/stems/`.

ALWAYS run `ve verify` before rendering. Audio finds the sound, not whether the camera saw it. Drop shots
where the subject is bent over or off-frame, a thumb covers the lens, or another sound (door, dropped tool)
triggered the detector.

Shot shape: start ~0.4s before the strike (wind-up), end ~0.5s after (~0.9s/beat). For a 45-60s montage use
50-65 beats, varied across angles.

Speed ramps (optional): 1.5x brisk, 2x punchy, 3-4x time-lapse; chain `atempo=2.0,atempo=2.0` for 4x;
mute ambient audio instead of chipmunking it.
