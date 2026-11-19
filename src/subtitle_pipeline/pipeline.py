"""Single-machine, synchronous proof-of-concept processing pipeline."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from .audio import extract_wav_clip, normalize_audio, wav_duration
from .captions import Caption, export_subtitles, normalize_captions
from .vad import detect_speech


def transcribe_media(
    source: Path,
    output_dir: Path,
    model_name: str = "small",
    device: str = "cpu",
    compute_type: str = "int8",
    language: str | None = None,
) -> tuple[Path, Path]:
    """Extract, detect speech, transcribe, and export timestamped captions."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError('ASR dependencies missing; run: pip install -e ".[asr]"') from exc

    started = time.perf_counter()
    source = source.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Input media does not exist: {source}")

    # Both model downloads happen on first use; do not claim the process is offline on a fresh install.
    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    captions: list[Caption] = []

    with TemporaryDirectory(prefix="subtitle-pipeline-") as workspace:
        temp = Path(workspace)
        normalized = normalize_audio(source, temp / "normalized.wav")
        duration = wav_duration(normalized)
        spans = detect_speech(normalized, duration)
        for number, span in enumerate(spans, 1):
            clip = extract_wav_clip(normalized, temp / f"speech-{number:04d}.wav", span.start, span.end)
            transcript, _info = model.transcribe(
                str(clip), language=language, beam_size=5, vad_filter=False,
                condition_on_previous_text=False,
            )
            for part in transcript:
                begin = span.start + max(0.0, float(part.start))
                end = min(span.end, span.start + float(part.end))
                captions.append(Caption(start=begin, end=end, text=str(part.text)))

    aligned = normalize_captions(captions, duration)
    metadata = {
        "status": "completed",
        "source_filename": source.name,
        "model": model_name,
        "device": device,
        "compute_type": compute_type,
        "language_hint": language,
        "audio_duration_seconds": round(duration, 3),
        "speech_intervals": len(spans),
        "subtitle_count": len(aligned),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    return export_subtitles(output_dir, aligned, metadata)
