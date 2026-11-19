"""Timestamp alignment and SRT/JSON subtitle serialization."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Caption:
    start: float
    end: float
    text: str


def normalize_captions(captions: list[Caption], duration: float) -> list[Caption]:
    """Clamp, sort, and enforce non-overlapping, positive subtitle intervals."""
    result: list[Caption] = []
    last_end = 0.0
    for item in sorted(captions, key=lambda c: (c.start, c.end)):
        if not all(math.isfinite(v) for v in (item.start, item.end)):
            continue
        begin = max(0.0, last_end, item.start)
        end = min(duration, item.end)
        text = " ".join(item.text.split())
        if text and end > begin:
            result.append(Caption(start=begin, end=end, text=text))
            last_end = end
    return result


def srt_timestamp(seconds: float) -> str:
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("SRT timestamps must be non-negative finite values")
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def render_srt(captions: list[Caption]) -> str:
    return "\n".join(
        f"{number}\n{srt_timestamp(item.start)} --> {srt_timestamp(item.end)}\n{item.text}\n"
        for number, item in enumerate(captions, 1)
    )


def export_subtitles(directory: Path, captions: list[Caption], metadata: dict[str, Any]) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    srt_file = directory / "subtitles.srt"
    json_file = directory / "subtitles.json"
    srt_file.write_text(render_srt(captions), encoding="utf-8")
    json_file.write_text(
        json.dumps({**metadata, "captions": [asdict(c) for c in captions]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return srt_file, json_file
