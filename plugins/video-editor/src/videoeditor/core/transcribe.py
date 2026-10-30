"""Local Whisper transcription that emits ElevenLabs-Scribe-shaped JSON.

pack.py and render.py read `{"words": [{"type": "word"|"spacing", "text", "start", "end"}]}`.
Producing that shape here means they work unchanged on Whisper output.

Whisper tends to drop fillers ("um", "uh"); the initial prompt below nudges it to keep them,
but it is not a guarantee. Cuts around fillers are therefore less reliable than with Scribe.

Backends: `faster-whisper` (default) and `whisperx` (optional: tighter word timing and speaker labels,
see transcribe_whisperx.py). Both produce the same JSON, so everything downstream is backend-agnostic.

CLI: `ve transcribe <video> [--edit-dir DIR] [--model base.en] [--language en] [--backend ...]`.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

FILLER_PROMPT = "Um, uh, so, like, you know, I mean, hmm. Uh, well, okay."


def extract_audio(video: Path, wav: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
        check=True,
    )


def load_wav(path: Path) -> np.ndarray:
    """Read our own 16 kHz mono PCM16 WAV as float32. Handing Whisper an array also avoids PyAV decoding."""
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


BACKENDS = ("faster-whisper", "whisperx")


def _fill_missing_times(words: list[dict], duration: float) -> list[dict]:
    """Give words without timestamps (e.g. "90%" which an aligner cannot place) an even share of the gap
    between their timed neighbours, so captions and cuts never silently lose them."""
    out = [dict(w) for w in words]
    i = 0
    while i < len(out):
        if out[i].get("start") is not None and out[i].get("end") is not None:
            i += 1
            continue
        j = i
        while j < len(out) and (out[j].get("start") is None or out[j].get("end") is None):
            j += 1
        lo = out[i - 1]["end"] if i > 0 else 0.0
        hi = out[j]["start"] if j < len(out) else max(duration, lo)
        step = max(hi - lo, 0.0) / (j - i)
        for k in range(i, j):
            out[k]["start"] = lo + (k - i) * step
            out[k]["end"] = lo + (k - i + 1) * step
        i = j
    return out


def words_to_scribe(words: list[dict], language: str, duration: float, **meta) -> dict:
    """Shared by every backend. `words`: dicts with text, start, end and optional speaker."""
    words = _fill_missing_times([w for w in words if (w.get("text") or "").strip()], duration)
    out: list[dict] = []
    prev_end: float | None = None
    for w in words:
        if prev_end is not None and w["start"] > prev_end:
            out.append({"type": "spacing", "text": " ", "start": round(prev_end, 3), "end": round(w["start"], 3)})
        entry = {"type": "word", "text": w["text"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}
        if w.get("speaker"):
            entry["speaker_id"] = w["speaker"]
        out.append(entry)
        prev_end = w["end"]
    return {
        "language_code": language,
        "duration": duration,
        "text": " ".join(w["text"] for w in out if w["type"] == "word"),
        "words": out,
        **meta,
    }


def to_scribe_shape(segments, language: str, duration: float) -> dict:
    """Convert faster-whisper segments (with word timestamps) to the Scribe-like schema."""
    words = [{"text": w.word, "start": w.start, "end": w.end} for seg in segments for w in (seg.words or [])]
    return words_to_scribe(words, language, duration, backend="faster-whisper")


def _preflight(backend: str, clean_speech: bool) -> None:
    """Fail fast, before any audio work, if an optional dependency is missing."""
    import importlib.util

    need = {"faster-whisper": ("faster_whisper", "speech"), "whisperx": ("whisperx", "speech-plus")}[backend]
    if importlib.util.find_spec(need[0]) is None:
        raise SystemExit(f"the {backend} backend needs: pip install 'videoeditor[{need[1]}]'")
    if clean_speech and importlib.util.find_spec("demucs") is None:
        raise SystemExit("--clean-speech needs demucs: pip install 'videoeditor[stems]'")


def _is_cached(out: Path, video: Path, backend: str, diarize: bool) -> bool:
    if not out.exists() or out.stat().st_mtime < video.stat().st_mtime:
        return False
    try:
        data = json.loads(out.read_text())
    except ValueError:
        return False
    return data.get("backend", "faster-whisper") == backend and (data.get("diarized", False) or not diarize)


def transcribe(
    video: Path,
    edit_dir: Path,
    model: str = "base.en",
    language: str | None = "en",
    vad_filter: bool = False,
    force: bool = False,
    *,
    backend: str = "faster-whisper",
    diarize: bool = False,
    hf_token: str | None = None,
    min_speakers: int | None = None,
    max_speakers: int | None = None,
    clean_speech: bool = False,
) -> Path:
    """Transcribe `video` into <edit_dir>/transcripts/<stem>.json. Cached per source file and backend."""
    if backend not in BACKENDS:
        raise SystemExit(f"unknown backend '{backend}' (choose from {', '.join(BACKENDS)})")
    if diarize and backend != "whisperx":
        raise SystemExit("--diarize needs --backend whisperx (pip install 'videoeditor[speech-plus]')")
    out = edit_dir / "transcripts" / f"{video.stem}.json"
    if not force and _is_cached(out, video, backend, diarize):
        print(f"cached: {out}")
        return out

    _preflight(backend, clean_speech)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "audio.wav"
        if clean_speech:
            from videoeditor.core import stems

            wav = stems.separate(video, edit_dir / "stems", ["vocals"], mono_16k=True)["vocals"]
        else:
            extract_audio(video, wav)
        if backend == "whisperx":
            from videoeditor.core.transcribe_whisperx import run_whisperx

            words, lang, duration = run_whisperx(
                wav, model=model, language=language, diarize=diarize, hf_token=hf_token,
                min_speakers=min_speakers, max_speakers=max_speakers)
            data = words_to_scribe(words, lang, duration, backend="whisperx", diarized=diarize)
        else:
            from faster_whisper import WhisperModel  # lazy: heavy, and not needed by the action recipe

            wm = WhisperModel(model, device="cpu", compute_type="int8")
            segments, info = wm.transcribe(
                load_wav(wav),
                language=language,
                word_timestamps=True,
                initial_prompt=FILLER_PROMPT,
                vad_filter=vad_filter,
                condition_on_previous_text=False,
            )
            data = to_scribe_shape(list(segments), info.language, info.duration)  # list(): decoding is lazy
    out.write_text(json.dumps(data, indent=2))
    print(f"transcript -> {out} ({sum(1 for w in data['words'] if w['type'] == 'word')} words, backend {backend})")
    return out
