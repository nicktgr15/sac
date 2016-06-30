from unittest import TestCase

import os
from mock import patch, call
from sac.model.audacity_label import AudacityLabel
from sac.cli.wav_editor import WavEditor


class TestWavEditor(TestCase):
    @patch('sac.cli.wav_editor.Util')
    @patch('sac.cli.wav_editor.WavEditor.get_rows')
    @patch('sac.cli.wav_editor.WavEditor.create_audio_segment')
    def test_create_audio_segments_f1(self, mocked_create_audio_segment, mocked_get_rows, mocked_util):
        mocked_get_rows.return_value = [
            ["1.00", "2.00", "m"],
            ["2.50", "3.00", "v"]
        ]

        WavEditor.create_audio_segments("labels_file", "input_wav", "output_dir", False, "\t", "f1")

        self.assertEquals(0, mocked_util.remove_dir.call_count)
        self.assertEquals(1, mocked_util.make_dir.call_count)
        self.assertEquals(1, mocked_get_rows.call_count)
        self.assertEquals(2, mocked_create_audio_segment.call_count)
        self.assertEquals('1.00', mocked_create_audio_segment.call_args_list[0][0][0])
        self.assertEquals('2.00', mocked_create_audio_segment.call_args_list[0][0][1])
        self.assertEquals('2.50', mocked_create_audio_segment.call_args_list[1][0][0])
        self.assertEquals('3.00', mocked_create_audio_segment.call_args_list[1][0][1])

    @patch('sac.cli.wav_editor.Util')
    @patch('sac.cli.wav_editor.WavEditor.get_rows')
    @patch('sac.cli.wav_editor.WavEditor.create_audio_segment')
    def test_create_audio_segments_f2(self, mocked_create_audio_segment, mocked_get_rows, mocked_util):
        mocked_get_rows.return_value = [
            ["1.00", "2.00", "m"],
            ["2.50", "3.00", "v"]
        ]

        WavEditor.create_audio_segments("labels_file", "input_wav", "output_dir", False, "\t", "f2")

        self.assertEquals(0, mocked_util.remove_dir.call_count)
        self.assertEquals(1, mocked_util.make_dir.call_count)
        self.assertEquals(1, mocked_get_rows.call_count)
        self.assertEquals(2, mocked_create_audio_segment.call_count)
        self.assertEquals('1.00', mocked_create_audio_segment.call_args_list[0][0][0])
        self.assertEquals('3.0', mocked_create_audio_segment.call_args_list[0][0][1])
        self.assertEquals('2.50', mocked_create_audio_segment.call_args_list[1][0][0])
        self.assertEquals('5.5', mocked_create_audio_segment.call_args_list[1][0][1])

    @patch('sac.cli.wav_editor.subprocess')
    def test_create_audio_segment(self, mocked_subprocess):
        # when
        WavEditor.create_audio_segment("0.50", "2.0", "input_wav", "output_wav")

        # then
        mocked_subprocess.check_call.called_once_with(
                ["sox", "input_wav", "output_wav", "trim", "0.50", "1.50"]
        )

    @patch('sac.cli.wav_editor.os.listdir')
    def test_get_files_grouped_by_class(self, mocked_os_listdir):
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

    def test_get_non_overlapping_items(self):
        rows = [['0.000000000', '22.530612244', 'm'], ['20.015600907', '2.461315192', 's'],
                ['22.530612244', '27.820408163', 'm'], ['49.959183673', '5.028571428', 's']]
        non_overlapping_rows = WavEditor.get_non_overlapping_items(rows)

        expected = [['0.0', '20.015600907', 'm'], ['22.476916099', '22.530612244', 'm'],
                    ['22.530612244', '49.959183673', 'm']]
        self.assertListEqual(expected, non_overlapping_rows)

    def test_get_non_overlapping_items_v2(self):

        rows = [['0.000000000', '22.530612244', 'm'], ['20.015600907', '2.461315192', 's'],
                ['22.530612244', '27.820408163', 'm'], ['49.959183673', '5.028571428', 's'],
                ['80.959183673', '5.028571428', 's']]
        non_overlapping_rows = WavEditor.get_non_overlapping_items_v2(rows)

        expected = [[80.959183673, 85.987755101, 's']]
        self.assertListEqual(expected, non_overlapping_rows)

    def test_are_labels_overlapping(self):

        """
        |---------| lbl1
                      |--------| lbl2
        """

        lbl1 = AudacityLabel(0.0, 10.0, '')
        lbl2 = AudacityLabel(11.0, 13.0, '')

        self.assertFalse(WavEditor.are_labels_overlapping(lbl1, lbl2))

        """
                        |---------| lbl1
        |--------| lbl2
        """

        lbl1 = AudacityLabel(10.0, 12.0, '')
        lbl2 = AudacityLabel(0.0, 8.0, '')

        self.assertFalse(WavEditor.are_labels_overlapping(lbl1, lbl2))

        """
                        |---------| lbl1
        |-------------------| lbl2
        """

        lbl1 = AudacityLabel(10.0, 12.0, '')
        lbl2 = AudacityLabel(0.0, 11.0, '')

        self.assertTrue(WavEditor.are_labels_overlapping(lbl1, lbl2))

        """
        |-----------------| lbl1
                      |--------| lbl2
        """

        lbl1 = AudacityLabel(0.0, 12.0, '')
        lbl2 = AudacityLabel(11.0, 13.0, '')

        self.assertTrue(WavEditor.are_labels_overlapping(lbl1, lbl2))

        """
                |-----------------| lbl1
                      |--------| lbl2
        """

        lbl1 = AudacityLabel(0.0, 12.0, '')
        lbl2 = AudacityLabel(5.0, 10.0, '')

        self.assertTrue(WavEditor.are_labels_overlapping(lbl1, lbl2))

        """
                            |------| lbl1
                      |-------------| lbl2
        """

        lbl1 = AudacityLabel(5.0, 10.0, '')
        lbl2 = AudacityLabel(3.0, 12.0, '')

        self.assertTrue(WavEditor.are_labels_overlapping(lbl1, lbl2))
