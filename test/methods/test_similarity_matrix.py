from unittest import TestCase
from sac.methods import self_similarity
import numpy as np


class TestSimilarityMatrix(TestCase):
    def test_calculate_similarity_matrix(self):
        example_feature_vectors = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
            [1, 1, 1],
            [1, 1, 1],
            [2, 2, 2],
            [2, 2, 2],
            [0, 0, 0],
            [0, 0, 0],
            [2, 2, 2],
            [2, 2, 2]
        ])
        sm = self_similarity.calculate_similarity_matrix(example_feature_vectors)

        self.assertTrue(sm[6, 0] == 0)
        self.assertTrue(sm[7, 1] == 0)

        self.assertTrue(sm[4, 0] != 0)
        self.assertTrue(sm[5, 0] != 0)

        self.assertEqual(example_feature_vectors.shape[0], sm.shape[0])
        self.assertEqual(sm.shape[0], sm.shape[1])

    def test_get_checkerboard_matrix(self):

        checkerboard_matrix = self_similarity.get_checkerboard_matrix(2)
        self.assertEqual((4, 4), checkerboard_matrix.shape)

    def test_calculate_segment_start_end_times_from_peak_positions(self):
        # when
        peaks = [0, 10, 30, 44, 50]
        samping_rate = 22050

        # then
        expected_segments = [
            [0.0, 0.00045351473922902497],
            [0.00045351473922902497, 0.001360544217687075],
            [0.001360544217687075, 0.00199546485260771],
            [0.00199546485260771, 0.0022675736961451248]
        ]

        segments = self_similarity.calculate_segment_start_end_times_from_peak_positions(peaks, samping_rate)
        self.assertListEqual(expected_segments, segments)

    def test_get_window_in_seconds(self):
        self.assertAlmostEqual(0.00004535147392, self_similarity.get_window_in_seconds(22050))

    def test_checkerboard_matrix_filtering(self):

        # This generate a simple similarity matrix with 4 equally sized rectangles on the main diagonal
        example_feature_vectors = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ])

        sm = self_similarity.calculate_similarity_matrix(example_feature_vectors)
        peaks, convolution_values = self_similarity.checkerboard_matrix_filtering(sm, kernel_width=2, peak_range=2)

        self.assertListEqual([0, 4, 9, 13, 15], peaks)
        self.assertEqual(5, len(peaks))
        self.assertTrue(0 in peaks)  # check that 0 is always added in the peaks
        self.assertTrue((len(peaks)-1) in peaks)  # check that the last samples is always added to the peaks
