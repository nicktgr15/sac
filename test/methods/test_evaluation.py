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

    def test_get_classification_based_on_time_range(self):

        labels = [
            AudacityLabel(0, 10, "m"),
            AudacityLabel(10, 20, "s"),
            AudacityLabel(22, 24, "m")
        ]

        self.assertEqual("m", evaluation.get_classification_based_on_time_range(5, 5.01, labels))
        self.assertEqual("s", evaluation.get_classification_based_on_time_range(10, 10.01, labels))
        self.assertRaises(Exception, evaluation.get_classification_based_on_time_range, 20, 20.01, labels)
        self.assertEqual("m", evaluation.get_classification_based_on_time_range(22, 22.01, labels))

    def test_frame_level_evaluation(self):

        ground_labels = [
            AudacityLabel(0, 5, "m"),
            AudacityLabel(5, 6, "s"),
            AudacityLabel(6, 10, "m")
        ]

        # 100% f1-score
        detected_labels = [
            AudacityLabel(0, 5, "m"),
            AudacityLabel(5, 6, "s"),
            AudacityLabel(6, 10, "m")
        ]

        p, r, f1 = evaluation.frame_level_evaluation(ground_labels, detected_labels)

        self.assertEqual(1.0, f1)

        # 90% f1-score
        detected_labels = [
            AudacityLabel(0, 5, "m"),
            AudacityLabel(5, 6, "m"),
            AudacityLabel(6, 10, "m")
        ]

        p, r, f1 = evaluation.frame_level_evaluation(ground_labels, detected_labels)
        self.assertEqual(0.9, f1)

        # not existing classifications
        ground_labels = [
            AudacityLabel(0, 5, "m"),
            AudacityLabel(5, 6, "s"),
            AudacityLabel(6, 10, "m")
        ]

        detected_labels = [
            AudacityLabel(0, 5, "m"),
            AudacityLabel(6, 10, "m")
        ]

        p, r, f1 = evaluation.frame_level_evaluation(ground_labels, detected_labels)
        self.assertAlmostEqual(0.94736842, f1)
