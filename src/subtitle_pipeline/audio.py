"""Audio extraction and lossless PCM slicing, using FFmpeg and the stdlib."""

from __future__ import annotations

import shutil
import subprocess
import wave
from pathlib import Path

SAMPLE_RATE = 16000


def normalize_audio(source: Path, output: Path) -> Path:
    """Decode an audio/video file to 16-kHz mono, signed 16-bit PCM WAV."""
    if not source.is_file():
        raise FileNotFoundError(f"Input media does not exist: {source}")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("FFmpeg is not installed or not available on PATH")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-i", str(source), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
        "-c:a", "pcm_s16le", str(output),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"FFmpeg failed: {exc.stderr.strip()}") from exc
    if not output.is_file() or output.stat().st_size < 44:
        raise RuntimeError("FFmpeg produced an empty or invalid WAV file")
    return output


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as reader:
        return reader.getnframes() / reader.getframerate()


def extract_wav_clip(source: Path, target: Path, start: float, end: float) -> Path:
    """Cut a PCM WAV clip without re-encoding or introducing time drift."""
    if start < 0 or end <= start:
        raise ValueError(f"Invalid audio interval: {start}..{end}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(source), "rb") as reader:
        frame_rate = reader.getframerate()
        total_frames = reader.getnframes()
        first_frame = min(total_frames, max(0, round(start * frame_rate)))
        last_frame = min(total_frames, max(first_frame, round(end * frame_rate)))
        if last_frame <= first_frame:
            raise ValueError("Audio interval is outside the source duration")
        reader.setpos(first_frame)
        raw_audio = reader.readframes(last_frame - first_frame)
        parameters = reader.getparams()
    with wave.open(str(target), "wb") as writer:
        writer.setparams(parameters)
        writer.writeframes(raw_audio)
    return target
