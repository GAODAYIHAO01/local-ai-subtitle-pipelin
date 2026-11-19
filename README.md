# Local-first AI Subtitle Pipeline

[![Unit tests](https://img.shields.io/badge/status-early%20PoC-orange)](#project-status)

A reproducible **proof of concept** for speech activity detection, local transcription, and timestamped subtitle generation. This repository documents the first engineering task intended for evaluation with **Devin**: implement and validate a small, independently testable ASR module before adding a distributed backend.

## Project status

**Early PoC / unverified end-to-end.** This repository contains a Python package, CLI, FFmpeg audio normalization, Silero VAD and faster-whisper integration, SRT/JSON export, deterministic unit tests, and a GitHub Actions workflow. The model-dependent pipeline still requires validation on an actual media sample and suitable local compute. No claimed performance metrics, production deployment, or completed Devin session are implied.

## Milestone 1: First concrete Devin task

> Deliver a standalone **Silero VAD + faster-whisper** subtitle-transcription module that processes a 5-10 minute, rights-cleared video, maps timestamps to the original timeline, and produces independently verifiable `subtitles.srt` and `subtitles.json` artifacts.

### Scope and acceptance criteria

| Area | Implementation approach | Acceptance evidence |
| --- | --- | --- |
| Media ingestion | FFmpeg extracts 16 kHz, mono, 16-bit PCM WAV | A user-provided MP3/WAV/MP4 can be decoded |
| Speech detection | Silero VAD returns intervals with absolute offsets | Silence filtered; interval validity confirmed |
| Transcription | faster-whisper/CTranslate2, CPU INT8 or optional CUDA | Real, reproducible model run on authorized test media |
| Alignment | Restore ASR clip offsets to the source clock | Ordered, finite, positive and non-overlapping subtitle spans |
| Artifacts | Standard SRT plus structured JSON | Both files generated and parseable |
| Engineering quality | CLI, error reporting, unit tests, CI and README | Unit test suite passes and one full demo is documented |

**Definition of Done:** A real 5-10 minute sample can be processed end to end without manual editing; the resulting SRT and JSON files are available for review; processing duration and runtime environment are recorded. Unit tests alone do **not** meet this definition.

## Architecture

```text
Authorized local media (MP3 / WAV / MP4)
                 |
                 v
       FFmpeg audio normalization
         (16 kHz mono PCM WAV)
                 |
                 v
        Silero VAD speech spans
                 |
                 v
     Clip extraction with source offsets
                 |
                 v
       faster-whisper transcription
         (CPU INT8 / CUDA FP16)
                 |
                 v
      Time normalization + validation
                 |
                 v
       subtitles.srt + subtitles.json
```

Milestone 1 is a **single-process CLI**. FastAPI, Celery, Redis, PostgreSQL and optional object storage are **planned for Milestone 2**, not claimed as present.

## Requirements

- Python 3.11+
- FFmpeg executable available on `PATH`
- For ASR: `faster-whisper`, `silero-vad` and PyTorch (see optional dependencies)
- CPU works with the INT8 configuration; a CUDA-compatible GPU can accelerate inference with appropriate driver/runtime support
- Internet may be required **on the first run** to download model weights; subsequent runs can use cached models

Model sizes, available memory and exact CUDA dependencies depend on the actual system. Start with `tiny` or `base` for low-resource smoke tests, then increase to `small` if practical.

## Quick start

```bash
# Clone the repository after publishing it on GitHub
# git clone https://github.com/GAODAYIHAO01/local-ai-subtitle-pipelin.git
# cd local-ai-subtitle-pipelin

python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate        # Windows PowerShell
python -m pip install -e ".[asr]"

subtitle-pipeline path/to/your-video.mp4 \
  --output-dir outputs \
  --model base \
  --device cpu \
  --compute-type int8
```

For a supported CUDA setup, try `--device cuda --compute-type float16` after installing the necessary NVIDIA runtime dependencies. FFmpeg must be installed separately. `outputs/` is intentionally ignored by Git.

## Outputs

`subtitles.srt` is standard SRT, with source-relative timestamps. `subtitles.json` contains a list of `{start, end, text}` caption objects and execution metadata: model, device, compute type, source filename, duration, speech interval count, subtitle count and wall-clock processing time.

## Testing

The deterministic tests do not download model weights:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m compileall -q src
```

End-to-end ASR performance and transcript correctness require a separate manual run using a media sample that can legally be processed. Refer to [ROADMAP](docs/ROADMAP.md) for the exact outstanding verification tasks.

## Intended use of Devin

1. Review current design and identify timestamp, codec and language-handling edge cases.
2. Add repeatable integration tests, a rights-cleared sample fixture and reproducible execution logs.
3. Improve model loading, graceful fallbacks, long-form audio chunking and resource monitoring.
4. After Milestone 1 is verified, implement Milestone 2: FastAPI + Celery + Redis queue, task tracking and deployment topology.

The purpose of the requested development credit is to evaluate whether an AI coding agent can deliver these scoped, reviewable tasks. It is not a claim that the whole platform already exists.

## Privacy and content rights

Media stays local in the current pipeline, except for optional initial model-weight downloads. Do not process material without appropriate rights. No torrent ingestion, remote upload, account authentication or cloud storage is implemented.