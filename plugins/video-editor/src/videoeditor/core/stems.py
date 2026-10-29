"""Optional stem separation with Demucs (maintained fork, PyPI `demucs>=4.1`).

Two uses inside the recipes:
  * `ve transcribe --clean-speech`: transcribe the vocals stem when music sits under speech.
  * `ve find --stem drums`: detect impacts on an isolated drum stem instead of the full mix.

Stems are cached under <edit>/stems/ per source and model. CPU time is roughly 1.5x the track length
(Demucs README), so this is always opt-in. Install: pip install 'videoeditor[stems]'.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

DEFAULT_MODEL = "htdemucs"


def _cache_key(media: Path, model: str) -> str:
    st = media.stat()
    return hashlib.sha1(f"{media.resolve()}|{st.st_size}|{int(st.st_mtime)}|{model}".encode()).hexdigest()[:12]


def _extract_stereo_44k(media: Path, wav: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(media), "-vn", "-ac", "2", "-ar", "44100", str(wav)],
                   check=True)


def _to_mono_16k(src: Path, dst: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-ac", "1", "-ar", "16000", str(dst)], check=True)


def separate(media: Path, out_dir: Path, stems: list[str], *, model: str = DEFAULT_MODEL,
             device: str = "cpu", mono_16k: bool = False) -> dict[str, Path]:
    """Return {stem: wav_path} for the requested stems. "no_<stem>" asks for the sum of all the others
    (e.g. no_vocals = the music bed). `mono_16k` converts results for transcription / transient detection."""
    try:
        import demucs.api
    except ImportError:
        raise SystemExit("stem separation needs demucs: pip install 'videoeditor[stems]'") from None

    out_dir.mkdir(parents=True, exist_ok=True)
    key = _cache_key(media, model)
    suffix = "_16k" if mono_16k else ""
    wanted = {s: out_dir / f"{media.stem}.{key}.{s}{suffix}.wav" for s in stems}
    if all(p.exists() for p in wanted.values()):
        return wanted

    import tempfile

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.wav"
        _extract_stereo_44k(media, src)
        sep = demucs.api.Separator(model=model, device=device, progress=False)
        _, separated = sep.separate_audio_file(src)
        for stem, path in wanted.items():
            if stem.startswith("no_"):
                skip = stem[3:]
                if skip not in separated:
                    raise SystemExit(f"model '{model}' has no stem '{skip}' (has: {', '.join(separated)})")
                audio = sum(t for name, t in separated.items() if name != skip)
            elif stem in separated:
                audio = separated[stem]
            else:
                raise SystemExit(f"model '{model}' has no stem '{stem}' (has: {', '.join(separated)})")
            full = path.with_name(path.name.replace("_16k.wav", ".wav")) if mono_16k else path
            demucs.api.save_audio(audio, str(full), samplerate=sep.samplerate)
            if mono_16k:
                _to_mono_16k(full, path)
    return wanted
