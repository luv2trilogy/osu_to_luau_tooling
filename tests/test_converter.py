import io
import tempfile
import unittest
from pathlib import Path

from converter import ConversionPipeline, parse_osu
from main import resolve_input_text


class ConverterTests(unittest.TestCase):
    def test_resolve_input_text_from_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".osu", delete=False) as handle:
            handle.write("[General]\nAudioFilename: demo.mp3\n")
            path = Path(handle.name)

        try:
            self.assertIn("demo.mp3", resolve_input_text(str(path)))
        finally:
            path.unlink(missing_ok=True)

    def test_resolve_input_text_from_stdin(self) -> None:
        stream = io.StringIO("[General]\nAudioFilename: from_stdin.mp3\n")
        self.assertIn("from_stdin.mp3", resolve_input_text(use_stdin=True, stdin_stream=stream))

    def test_parse_and_serialize_sample_beatmap(self) -> None:
        sample = """
[General]
AudioFilename: song.mp3
Mode: 0

[Metadata]
Title: Demo Map
Artist: Demo Artist
Version: Normal

[TimingPoints]
0,500,4,1,0,100,1,0

[HitObjects]
256,192,1000,1,0,0:0:0:0:0
"""

        beatmap = parse_osu(sample)
        self.assertEqual(beatmap.metadata.title, "Demo Map")
        self.assertEqual(len(beatmap.timing_points), 1)

        pipeline = ConversionPipeline()
        output = pipeline.convert(sample, output_format="json")
        self.assertIn("Demo Map", output)
        self.assertIn("song.mp3", output)


if __name__ == "__main__":
    unittest.main()
