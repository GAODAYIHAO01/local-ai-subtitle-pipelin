"""VAD integration and interval validation."""

from __future__ import annotations

import wave
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


def read_pcm_wav(audio: Path):
    """Read the FFmpeg-normalized 16kHz mono PCM16 WAV directly.

    This avoids torchaudio's optional torchcodec dependency in current releases.
    The pipeline always normalizes its audio to this exact format first.
    """
    try:
        import numpy as np
        import torch
    except ImportError as exc:
        raise RuntimeError('ASR dependencies missing; run: pip install -e ".[asr]"') from exc
    with wave.open(str(audio), "rb") as wav:
        if wav.getnchannels() != 1 or wav.getframerate() != 16000 or wav.getsampwidth() != 2:
            raise ValueError("VAD requires 16-kHz mono signed 16-bit PCM WAV")
        raw = wav.readframes(wav.getnframes())
    pcm = np.frombuffer(raw, dtype="<i2").copy()
    return torch.from_numpy(pcm).float() / 32768.0


def detect_speech(audio: Path, duration: float) -> list[SpeechInterval]:
    """Return speech spans in absolute source seconds, using Silero VAD."""
    try:
        from silero_vad import get_speech_timestamps, load_silero_vad
    except ImportError as exc:
        raise RuntimeError('ASR dependencies missing; run: pip install -e ".[asr]"') from exc

    waveform = read_pcm_wav(audio)
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
