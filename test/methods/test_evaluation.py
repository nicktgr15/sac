from unittest import TestCase

from sac.model.audacity_label import AudacityLabel
from sac.methods import evaluation


class TestEvaluation(TestCase):

    def test_transition_points_f1_score_perfect(self):

        ground_truth_segments = [
            AudacityLabel(0, 10, "-"),
            AudacityLabel(10, 15, "-"),
            AudacityLabel(15, 20, "-"),
            AudacityLabel(20, 25, "-")
        ]

        detected_segments = [
            AudacityLabel(0, 10, "-"),
            AudacityLabel(10, 15, "-"),
            AudacityLabel(15, 20, "-"),
            AudacityLabel(20, 25, "-")
        ]

        precision, recall, fs = evaluation.transition_points_precision_recall_fs(ground_truth_segments, detected_segments, 1)
        self.assertEqual(1.0, precision)

    def test_transition_points_f1_score_low_precision_high_recall(self):
        ground_truth_segments = [
            AudacityLabel(0, 10, "-"),
            AudacityLabel(10, 15, "-"),
            AudacityLabel(15, 20, "-"),
            AudacityLabel(20, 25, "-")
        ]

        detected_segments = [
            AudacityLabel(0, 5, "-"),
            AudacityLabel(5, 8, "-"),
            AudacityLabel(8, 10, "-"),
            AudacityLabel(10, 15, "-"),
            AudacityLabel(15, 20, "-"),
            AudacityLabel(20, 25, "-")
        ]

        precision, recall, fs = evaluation.transition_points_precision_recall_fs(ground_truth_segments, detected_segments, 1)
        self.assertEqual(0.6, precision)
        self.assertEqual(1.0, recall)

    def test_transition_points_f1_score_high_precision_low_recall(self):
        ground_truth_segments = [
            AudacityLabel(0, 10, "-"),
            AudacityLabel(10, 15, "-"),
            AudacityLabel(15, 20, "-"),
            AudacityLabel(20, 25, "-")
        ]

        detected_segments = [
            AudacityLabel(0, 10, "-"),
            AudacityLabel(10, 15, "-"),
        ]

        precision, recall, fs = evaluation.transition_points_precision_recall_fs(ground_truth_segments, detected_segments, 1)
        self.assertEqual(1.0, precision)
        self.assertAlmostEqual(0.33333333333, recall)
