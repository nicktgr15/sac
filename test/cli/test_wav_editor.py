import os
from unittest import TestCase
from mock import patch, call

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

        WavEditor.create_audio_segments("labels_file", "input_wav", "output_dir", False, "\t")

        self.assertEquals(0, mocked_util.remove_dir.call_count)
        self.assertEquals(1, mocked_util.make_dir.call_count)
        self.assertEquals(1, mocked_get_rows.call_count)
        self.assertEquals(2, mocked_create_audio_segment.call_count)

    @patch('sac.cli.wav_editor.subprocess')
    def test_create_audio_segment(self, mocked_subprocess):
        # when
        WavEditor.create_audio_segment("0.50", "2.0", "input_wav", "output_wav")

        # then
        mocked_subprocess.check_call.called_once_with(
            ["sox", "input_wav", "output_wav", "trim", "0.50", "1.50"]
        )

    @patch('sac.cli.wav_editor.os.listdir')
    def test_get_files_grouped_by_class(self,  mocked_os_listdir):
        mocked_os_listdir.return_value = [
            "first_file_class1.wav",
            "second_file_class2.wav"
        ]

        files_grouped_by_class = WavEditor.get_files_grouped_by_class("input_dir")

        self.assertTrue(files_grouped_by_class.has_key("class1"))
        self.assertTrue(files_grouped_by_class.has_key("class2"))
        self.assertEqual(2, len(files_grouped_by_class))


    @patch('sac.cli.wav_editor.Util')
    @patch('sac.cli.wav_editor.logging')
    @patch('sac.cli.wav_editor.subprocess')
    @patch('sac.cli.wav_editor.WavEditor.get_files_grouped_by_class')
    def test_combine_audio_segments(self, mocked_get_files, mocked_subprocess, mocked_logging, mocked_util):

        mocked_get_files.return_value = {
            "class1": [
                "file1",
                "file3"
            ],
            "class2": [
                "file2"
            ]
        }

        WavEditor.combine_audio_segments("input_dir", "output_name", "output_dir", False)

        mocked_subprocess.check_call.assert_has_calls([
            call(['sox', 'file2', 'output_dir/output_name_class2.wav']),
            call(['sox', 'file1', "file3", 'output_dir/output_name_class1.wav'])
        ])

    def test_get_rows(self):
        comma_separated = os.path.join(os.path.dirname(__file__), 'fixtures/comma-separated.csv')
        rows = WavEditor.get_rows(comma_separated, ",")
        self.assertEquals(3, len(rows))
        self.assertEquals(3, len(rows[0]))

        tab_separated = os.path.join(os.path.dirname(__file__), 'fixtures/tab-separated.csv')
        rows = WavEditor.get_rows(tab_separated, '\t')
        self.assertEquals(3, len(rows))
        self.assertEquals(3, len(rows[0]))
