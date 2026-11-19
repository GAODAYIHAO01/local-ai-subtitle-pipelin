"""Command-line interface for the local ASR proof of concept."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import transcribe_media


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe authorized media to local SRT and JSON subtitles")
    parser.add_argument("input", type=Path, help="Input audio or video file")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--model", default="small", help="faster-whisper model, e.g. tiny/base/small")
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--compute-type", default="int8", help="e.g. int8 for CPU, float16 for CUDA")
    parser.add_argument("--language", default=None, help="Optional ISO language code, e.g. en or zh")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        srt_path, json_path = transcribe_media(
            args.input, args.output_dir, args.model,
            args.device, args.compute_type, args.language,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote: {srt_path}")
    print(f"Wrote: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
