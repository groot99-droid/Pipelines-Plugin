"""Optional whisperX backend: forced word alignment (wav2vec2) and speaker diarization (pyannote).

Why: Whisper's own word times drift by 50-100 ms, which is why cut edges are padded; whisperX aligns words
against the audio and can label who is speaking. Output is flattened into the same word list the faster-whisper
backend produces, so `pack` and `render` need no changes (speaker labels land in `speaker_id`).

Install: pip install 'videoeditor[speech-plus]'   (pulls torch ~2.8, pyannote-audio; several GB)
Diarization additionally needs a Hugging Face token (HF_TOKEN or --hf-token) with the pyannote terms accepted.
whisperX words with no alignable characters (e.g. "2014.", "$13.60") come back untimed; transcribe.py
interpolates them.
"""
from __future__ import annotations

import os
from pathlib import Path


def flatten_result(result: dict) -> list[dict]:
    """whisperX aligned result -> [{text, start, end, speaker}] (speaker falls back to the segment's)."""
    words: list[dict] = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []) or []:
            words.append({
                "text": w.get("word", ""),
                "start": w.get("start"),
                "end": w.get("end"),
                "speaker": w.get("speaker") or seg.get("speaker"),
            })
    return words


def run_whisperx(wav: Path, *, model: str, language: str | None, device: str = "cpu",
                 compute_type: str = "int8", batch_size: int = 8, diarize: bool = False,
                 hf_token: str | None = None, min_speakers: int | None = None,
                 max_speakers: int | None = None) -> tuple[list[dict], str, float]:
    """Returns (words, language, duration_seconds)."""
    try:
        import whisperx
    except ImportError:
        raise SystemExit("the whisperx backend needs: pip install 'videoeditor[speech-plus]'") from None

    token = hf_token or os.environ.get("HF_TOKEN")
    if diarize and not token:
        raise SystemExit("diarization needs a Hugging Face token: set HF_TOKEN or pass --hf-token, and accept the "
                         "pyannote model terms on huggingface.co")

    audio = whisperx.load_audio(str(wav))
    duration = len(audio) / 16000
    asr = whisperx.load_model(model, device, compute_type=compute_type, language=language, use_auth_token=token)
    result = asr.transcribe(audio, batch_size=batch_size)
    lang = result.get("language") or language or "en"
    align_model, metadata = whisperx.load_align_model(language_code=lang, device=device)
    try:
        result = whisperx.align(result["segments"], align_model, metadata, audio, device, return_char_alignments=False)
    except LookupError as exc:  # whisperX downloads NLTK's sentence tokenizer on first use
        if "punkt" not in str(exc):
            raise
        raise SystemExit("whisperX needs NLTK's punkt_tab data once: python -m nltk.downloader punkt_tab "
                         "(on a restricted network, download it elsewhere and set NLTK_DATA)") from None
    if diarize:
        from whisperx.diarize import DiarizationPipeline

        pipe = DiarizationPipeline(token=token, device=device)
        turns = pipe(audio, min_speakers=min_speakers, max_speakers=max_speakers)
        result = whisperx.assign_word_speakers(turns, result)
    return flatten_result(result), lang, duration
