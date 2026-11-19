# Engineering roadmap

## Milestone 1: Local ASR PoC (current)

- [x] Package layout and CLI entry point
- [x] FFmpeg-based 16 kHz mono WAV conversion
- [x] Silero VAD integration code
- [x] faster-whisper integration code
- [x] Time-offset mapping to the original media and SRT/JSON serializers
- [x] Dependency-free unit tests for interval handling and subtitles
- [ ] Run the complete pipeline on a real, rights-cleared 5-10 minute video
- [ ] Capture CPU/GPU memory use, wall-clock processing time and transcription accuracy
- [ ] Validate Chinese and English subtitle quality

## Milestone 2: Task orchestration (planned)

- FastAPI job submission/status/result endpoints
- Celery and Redis worker queue with retry/backoff and concurrency limits
- PostgreSQL task metadata and a stable schema
- Artifact retention rules and optional S3-compatible object storage
- Docker Compose service topology and integration tests

## Milestone 3: Translation and refinement (planned)

- Local LLM translation service and terminology consistency checks
- Subtitle reflow, time-alignment quality metrics and ASS export
- End-to-end load tests and documented runtime budgets

All checkboxes reflect repository implementation state, not external validation.