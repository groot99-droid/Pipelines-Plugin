"""Find candidate moments: audio impact transients (action mode) and in-frame verification.

Ported from clipify's detect_transients.py with the same defaults. Dialogue-mode moment
picking stays LLM-driven from the packed transcript (see recipes/playbooks/highlight_clips.md).
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

import numpy as np


def extract_wav(video: Path, wav: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
        check=True,
    )


def detect_transients(path: Path | str, band_lo: int = 1000, band_hi: int = 6000,
                      min_flux: float = 30.0, min_gap: float = 0.6) -> list[dict]:
    """Spectral-flux onset detection on a band. Returns [{time, flux, db}] sorted by time."""
    with wave.open(str(path), "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            raise SystemExit(
                f"expected 16-bit mono WAV, got {w.getnchannels()}ch {w.getsampwidth()*8}-bit; "
                "convert with: ffmpeg -i INPUT -vn -ac 1 -ar 16000 audio.wav")
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0

    win_size = int(sr * 0.025)
    hop = int(sr * 0.01)
    n_frames = (len(data) - win_size) // hop
    if n_frames < 4:
        return []
    frames = np.lib.stride_tricks.as_strided(
        data, shape=(n_frames, win_size), strides=(data.strides[0] * hop, data.strides[0]))
    spec = np.abs(np.fft.rfft(frames * np.hanning(win_size), axis=1))

    bin_lo = max(1, int(band_lo * win_size / sr))
    bin_hi = min(spec.shape[1], int(band_hi * win_size / sr))
    diff = np.diff(spec[:, bin_lo:bin_hi], axis=0)
    flux = np.sum(np.maximum(diff, 0), axis=1)
    times = (np.arange(len(flux)) + 1) * hop / sr
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-10)
    db = 20 * np.log10(rms + 1e-10)

    min_gap_frames = max(1, int(min_gap * sr / hop))
    peaks: list[dict] = []
    last = -min_gap_frames
    for i in range(2, len(flux) - 2):
        if flux[i] < min_flux:
            continue
        if flux[i] != np.max(flux[max(0, i - 3):i + 4]):
            continue
        rec = {"time": round(float(times[i]), 3), "flux": float(flux[i]),
               "db": round(float(db[i]), 1) if i < len(db) else 0.0}
        if i - last < min_gap_frames:
            if peaks and rec["flux"] > peaks[-1]["flux"]:
                peaks[-1] = rec
                last = i
            continue
        peaks.append(rec)
        last = i
    return peaks


def verify_frames(video: Path, times: list[float], out_dir: Path, width: int = 320) -> list[Path]:
    """Grab one small frame per candidate time so a human/LLM can drop off-screen events.

    Audio finds the sound of an event, not whether the camera saw it. Always run this
    before rendering an action montage.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for t in times:
        p = out_dir / f"verify_{t:08.3f}.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video),
             "-frames:v", "1", "-vf", f"scale={width}:-1", str(p)],
            check=True)
        paths.append(p)
    return paths


def shots_around(strikes: list[dict], pre: float = 0.4, post: float = 0.5, duration: float | None = None) -> list[dict]:
    """Turn strike times into cut ranges: wind-up before, follow-through after (~0.9s/beat)."""
    shots = []
    for s in strikes:
        a = max(0.0, s["time"] - pre)
        b = s["time"] + post
        if duration is not None:
            b = min(b, duration)
        if b > a:
            shots.append({"start": round(a, 3), "end": round(b, 3), "strike": s["time"]})
    return shots
