"""VAD integration and interval validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpeechInterval:
    start: float
    end: float


def validate_intervals(items: list[SpeechInterval], duration: float) -> list[SpeechInterval]:
    """Clamp intervals to the source and remove overlaps and zero-length spans."""
    cleaned: list[SpeechInterval] = []
    last_end = 0.0
    for item in sorted(items, key=lambda row: (row.start, row.end)):
        begin = max(0.0, last_end, item.start)
        finish = min(duration, item.end)
        if finish > begin:
            cleaned.append(SpeechInterval(start=begin, end=finish))
            last_end = finish
    return cleaned


def detect_speech(audio: Path, duration: float) -> list[SpeechInterval]:
    """Return speech spans in absolute source seconds, using Silero VAD."""
    try:
        from silero_vad import get_speech_timestamps, load_silero_vad, read_audio
    except ImportError as exc:
        raise RuntimeError('ASR dependencies missing; run: pip install -e ".[asr]"') from exc

    waveform = read_audio(str(audio), sampling_rate=16000)
    model = load_silero_vad()
    spans = get_speech_timestamps(
        waveform,
        model,
        sampling_rate=16000,
        return_seconds=True,
        min_speech_duration_ms=250,
        min_silence_duration_ms=400,
        speech_pad_ms=200,
    )
    return validate_intervals(
        [SpeechInterval(float(span["start"]), float(span["end"])) for span in spans],
        duration,
    )
