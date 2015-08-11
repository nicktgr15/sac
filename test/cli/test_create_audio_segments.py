from unittest import TestCase
from mock import patch

from sac.cli.wav_editor import WavEditor


class TestWavEditor(TestCase):

    @patch('sac.cli.wav_editor.Util')
    @patch('sac.cli.wav_editor.WavEditor.get_rows')
    @patch('sac.cli.wav_editor.WavEditor.create_audio_segment')
    def test_create_audio_segments(self, mocked_create_audio_segment, mocked_get_rows, mocked_util):

        mocked_get_rows.return_value = [
            ["0.01", "2.10", "m"],
            ["2.20", "3.14", "v"]
        ]

        WavEditor.create_audio_segments("labels_file", "input_wav", "output_dir", False)

        self.assertEquals(0, mocked_util.remove_dir.call_count)
        self.assertEquals(1, mocked_util.make_dir.call_count)
        self.assertEquals(1, mocked_get_rows.call_count)
        self.assertEquals(2, mocked_create_audio_segment.call_count)
