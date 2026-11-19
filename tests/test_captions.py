import json
import tempfile
import unittest
from pathlib import Path

from subtitle_pipeline.captions import Caption, export_subtitles, normalize_captions, render_srt, srt_timestamp


class CaptionTests(unittest.TestCase):
    def test_timestamp_rounding(self):
        self.assertEqual(srt_timestamp(3661.234), "01:01:01,234")
        self.assertEqual(srt_timestamp(0), "00:00:00,000")

    def test_clamps_overlap_and_empty_text(self):
        captions = [
            Caption(2, 4, " second "),
            Caption(1, 3, " first "),
            Caption(5, 6, "   "),
            Caption(6, 7, "beyond source"),
        ]
        result = normalize_captions(captions, duration=5)
        self.assertEqual(result, [Caption(1, 3, "first"), Caption(3, 4, "second")])

    def test_exports_srt_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [Caption(0.0, 1.5, "hello")]
            srt, json_file = export_subtitles(Path(tmp), rows, {"source_filename": "test.wav"})
            self.assertIn("00:00:01,500", srt.read_text())
            self.assertIn("hello", render_srt(rows))
            payload = json.loads(json_file.read_text())
            self.assertEqual(payload["captions"][0]["text"], "hello")


if __name__ == "__main__":
    unittest.main()
