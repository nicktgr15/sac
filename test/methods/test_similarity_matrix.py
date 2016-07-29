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
            [0, 0, 1],
            [0, 0, 1],
            [1, 1, 1],
            [1, 1, 1],
            [2, 2, 2],
            [2, 2, 2],
            [0, 0, 1],
            [0, 0, 1],
            [2, 2, 2],
            [2, 2, 2]
        ])
        sm = self_similarity.calculate_similarity_matrix(example_feature_vectors)

        # plt.figure()
        # plt.imshow(sm, cmap=plt.cm.gray)
        # plt.show()

        self.assertAlmostEqual(sm[6, 0], 0)
        self.assertAlmostEqual(sm[7, 1], 0)

        self.assertNotAlmostEqual(sm[4, 0], 0)
        self.assertNotAlmostEqual(sm[5, 0], 0)

        self.assertEqual(example_feature_vectors.shape[0], sm.shape[0])
        self.assertEqual(sm.shape[0], sm.shape[1])

    def test_get_checkerboard_matrix(self):

        checkerboard_matrix = self_similarity.get_checkerboard_matrix(2)
        self.assertEqual((4, 4), checkerboard_matrix.shape)

    def test_calculate_segment_start_end_times_from_peak_positions(self):
        # when
        peaks = [0, 10, 30, 44, 50]
        timestamps = [0, 1, 2]

        # then
        expected_segments = [
            [0.0, 10.0],
            [10.0, 30.0],
            [30.0, 44.0],
            [44.0, 50.0]
        ]

        segments = self_similarity.calculate_segment_start_end_times_from_peak_positions(peaks, timestamps)
        self.assertListEqual(expected_segments, segments)

    def test_get_window_in_seconds(self):
        self.assertAlmostEqual(1, self_similarity.get_window_in_seconds([0,1,2,3]))

    def test_end_to_end(self):
        X = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [0, 1, 0],
            [0, 1, 0],
            [1, 1, 1],
            [1, 1, 1],
            [2, 2, 2],
            [2, 2, 2],
            [0, 1, 0],
            [0, 1, 0],
            [2, 2, 2],
            [2, 2, 2]
        ])

        timestamps = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

        expected_segments = [[0, 4], [4, 5], [5, 6], [6, 7], [7, 7], [7, 10], [10, 13]]
        segments = self_similarity.get_segments(X, timestamps, 2, 5, 1, False)

        self.assertListEqual(expected_segments, segments)

    def test_checkerboard_matrix_filtering(self):

        # This generate a simple similarity matrix with 4 equally sized rectangles on the main diagonal
        example_feature_vectors = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [0, 0.1, 0],
            [0, 0.1, 0],
            [0, 0.1, 0],
            [0, 0.1, 0],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [0, 0.1, 0],
            [0, 0.1, 0],
            [0, 0.1, 0],
            [0, 0.1, 0]
        ])

        sm = self_similarity.calculate_similarity_matrix(example_feature_vectors)

        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # ax.imshow(sm, cmap=plt.cm.gray)
        # plt.show()

        peaks, convolution_values = self_similarity.checkerboard_matrix_filtering(sm, kernel_width=2, peak_range=2)
        self.assertListEqual([0, 4, 13, 15], peaks)
        self.assertTrue(0 in peaks)  # check that 0 is always added in the peaks
        self.assertTrue((len(sm)-1) in peaks)  # check that the last samples is always added to the peaks
