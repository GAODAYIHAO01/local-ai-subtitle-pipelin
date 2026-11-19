import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from subtitle_pipeline.audio import extract_wav_clip, wav_duration
from subtitle_pipeline.vad import SpeechInterval, validate_intervals


class AudioVADTests(unittest.TestCase):
    def test_validate_intervals(self):
        spans = [SpeechInterval(2.0, 3.0), SpeechInterval(-1.0, 1.0), SpeechInterval(0.8, 2.2)]
        self.assertEqual(validate_intervals(spans, 2.5), [
            SpeechInterval(0.0, 1.0), SpeechInterval(1.0, 2.2), SpeechInterval(2.2, 2.5),
        ])

    def test_clip_preserves_duration_and_sample_rate(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.wav"
            target = Path(tmp) / "clip.wav"
            with wave.open(str(source), "wb") as writer:
                writer.setnchannels(1)
                writer.setsampwidth(2)
                writer.setframerate(16000)
                writer.writeframes(b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * n / 16000))) for n in range(32000)))
            extract_wav_clip(source, target, 0.5, 1.25)
            self.assertAlmostEqual(wav_duration(target), 0.75, places=4)
            with wave.open(str(target), "rb") as reader:
                self.assertEqual(reader.getframerate(), 16000)


if __name__ == "__main__":
    unittest.main()
