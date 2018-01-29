import pickle
from unittest import TestCase

import numpy as np
import os
from sac.model.audacity_label import AudacityLabel
from sac.util import Util


class UtilTests(TestCase):
    def setUp(self):
        self.stats_csv = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_stats.csv')
        self.no_stats_csv = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_no_stats.csv')
        self.double_stats_csv = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_double_stats.csv')
        self.no_stats_derivate = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_no_stats_derivate.csv')
        self.stats_derivate = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_stats_derivate.csv')

        # with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures/sm.pickle')), 'rb') as f:
        #     self.sm = pickle.load(f)

        # with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures/timestamps.pickle')), 'rb') as f:
        #     self.timestamps = pickle.load(f)

    # # yaafe header parser
    def test_parse_yaafe_header_stats(self):
        header = Util.parse_yaafe_header(self.stats_csv)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(15360, header['effective_step_size'])

    def test_parse_yaafe_header_no_stats(self):
        header = Util.parse_yaafe_header(self.no_stats_csv)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(512, header['effective_step_size'])

    def test_parse_yaafe_header_double_stats(self):
        header = Util.parse_yaafe_header(self.double_stats_csv)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(460800, header['effective_step_size'])

    def test_parse_yaafe_header_no_stats_derivate(self):
        header = Util.parse_yaafe_header(self.no_stats_derivate)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(512, header['effective_step_size'])

    def test_parse_yaafe_header_stats_derivate(self):
        header = Util.parse_yaafe_header(self.stats_derivate)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(15360, header['effective_step_size'])

    # # yaafe csv parser
    def test_load_yaafe_csv_no_stats(self):
        timestamps, features = Util.load_yaafe_csv(self.no_stats_csv)
        self.assertEqual((17, 2), features.shape)
        self.assertEqual(0.37151927437641724, timestamps[-1])

    def test_load_yaafe_csv_stats(self):
        timestamps, features = Util.load_yaafe_csv(self.stats_csv)
        self.assertEqual((17, 2), features.shape)
        self.assertEqual(11.145578231292516, timestamps[-1])

    def test_load_yaafe_csv_double_stats(self):
        timestamps, features = Util.load_yaafe_csv(self.double_stats_csv)
        self.assertEqual((17, 2), features.shape)
        self.assertEqual(334.3673469387755, timestamps[-1])

    # # merge classifications
    def test_generate_labels_from_classifications(self):
        classifications = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1]
        timestamps = [0.0, 0.6965986394557823, 1.3931972789115645, 2.089795918367347, 2.786394557823129,
                      3.4829931972789114, 4.179591836734694, 4.876190476190477, 5.572789115646258, 6.2693877551020405,
                      6.965986394557823, 7.662585034013605, 8.359183673469389, 9.05578231292517, 9.752380952380953,
                      10.448979591836734, 11.145578231292516, 11.842176870748299, 12.538775510204081,
                      13.235374149659863, 13.931972789115646, 14.628571428571428, 15.32517006802721, 16.021768707482995]

        labels = Util.generate_labels_from_classifications(classifications, timestamps)

        expected_labels = [AudacityLabel(0.0, 1.3931972789115645, 1),
                           AudacityLabel(1.3931972789115645, 9.752380952380953, 0),
                           AudacityLabel(9.752380952380953, 10.448979591836736, 1),
                           AudacityLabel(10.448979591836734, 11.145578231292516, 0),
                           AudacityLabel(11.145578231292516, 12.538775510204081, 1),
                           AudacityLabel(12.538775510204081, 13.235374149659863, 0),
                           AudacityLabel(13.235374149659863, 16.718367346938777, 1)]

        self.assertListEqual(expected_labels, labels)

    def test_combine_adjacent_labels_of_the_same_class(self):
        input_labels = [
            AudacityLabel(0, 10, "m"),
            AudacityLabel(10, 20, "m"),
            AudacityLabel(20, 21, "s"),
            AudacityLabel(21, 22, "s"),
            AudacityLabel(22, 23, "s"),
            AudacityLabel(23, 30, "m")
        ]
        expected_labels = [
            AudacityLabel(0, 20, "m"),
            AudacityLabel(20, 23, "s"),
            AudacityLabel(23, 30, "m"),
        ]

        actual_labels = Util.combine_adjacent_labels_of_the_same_class(input_labels)

        self.assertListEqual(expected_labels, actual_labels)

    def test_calculate_classes_percentages(self):
        classifications = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1]
        percentages = Util.calculate_classes_percentages(classifications)

        self.assertAlmostEqual(0.5833333333333334, percentages[0])
        self.assertAlmostEqual(0.4166666666666667, percentages[1])

    def test_get_annotated_data(self):
        timestamps = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        data = np.random.rand(7, 10)
        labels = [
            AudacityLabel(1.2, 2.5, "m"),
            AudacityLabel(4.5, 6.0, "s")
        ]

        annotated_data = Util.get_annotated_data(timestamps, data, labels)
        self.assertTrue("m" in annotated_data)
        self.assertTrue("s" in annotated_data)
        self.assertTrue(data[2, :] in annotated_data["m"])
        self.assertTrue(data[5, :] in annotated_data["s"])
        self.assertTrue(data[6, :] in annotated_data["s"])

    def test_get_annotated_data_x_y(self):
        timestamps = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        data = np.random.rand(7, 10)
        labels = [
            AudacityLabel(1.2, 2.5, "m"),
            AudacityLabel(4.5, 6.0, "s")
        ]

        x, y, classes, timestamps = Util.get_annotated_data_x_y(timestamps, data, labels)

        self.assertEqual(3, x.shape[0])
        self.assertListEqual(["m", "s", "s"], y)
        self.assertListEqual(["m", "s"], classes)
        self.assertListEqual([0.0, 1.0, 2.0], timestamps)

    def test_split_data_based_on_annotation(self):
        X = np.array([
            [1, 2, 3, 4],
            [2, 3, 4, 5],
            [4, 5, 6, 7]
        ])
        Y = [0, 0, 1]
        classes = ["music", "speech"]

        data = Util.split_data_based_on_annotation(X, Y, classes)

        self.assertEqual(data["music"].shape[0], 2)
        self.assertEqual(data["speech"].shape[0], 1)

    # def test_kmeans_image_quantisation(self):
    #     quantised_image = Util.kmeans_image_quantisation(self.sm, 5)
    #     self.assertEquals(5, len(np.unique(quantised_image)))

    def test_combine_peaks(self):

        a_peaks = [3, 8]
        a_peak_values = [2, 2, 2, 3, 2, 2, 2, 4, 5, 4, 2, 2, 2]

        b_peaks = [6]
        b_peak_values = [2, 2, 2, 2, 2, 2, 7, 2, 2, 2, 2, 2, 2]

        p, v = Util.combine_peaks(a_peaks, a_peak_values, b_peaks, b_peak_values)

        self.assertListEqual([3, 6, 8], p)

    def test_non_maximum_suppression(self):
        peaks = [2, 3, 4, 7, 8, 9]
        values = [2, 2, 2, 3, 2, 2, 2, 4, 5, 4, 2, 2, 2]
        p, v = Util.non_maximum_suppression(peaks, values)

        self.assertListEqual([3, 8], p)
        self.assertListEqual(values, v)

    def test_get_annotated_labels_from_predictions_and_sm_segments(self):

        timestamps = [0, 1, 2, 3, 4, 5, 6]
        segments = [
            AudacityLabel(0, 2.5, '-'),
            AudacityLabel(2.5, 5.5, '-')
        ]
        frame_level_predictions = np.array(['v', 'v', 'v', 's', 's', 'v', 'v'])

        labels = Util.get_annotated_labels_from_predictions_and_sm_segments(frame_level_predictions, segments, timestamps)

        self.assertListEqual(['v', 's'], [l.label for l in labels])


    def test_get_shifted_data(self):

        labels = [
            AudacityLabel(1.0, 5.0, 'A'),
            AudacityLabel(8.0, 10.0, 'B'),
            AudacityLabel(15.0, 20.0, 'C')
        ]

        X, y, classes, new_timestamps = Util.get_annotated_data_x_y([float(i) for i in range(0,25)], np.ones((25, 10)),
                                                                    labels)

        self.assertListEqual(['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'C', 'C'], y)
        self.assertListEqual([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0], new_timestamps)

        shifted_labels = Util.get_annotation_time_shift(labels)

        shifted_predictions, shifted_timestamps = Util.get_shifted_data(y, new_timestamps, shifted_labels)

        self.assertListEqual(['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C', 'C', 'C', 'C'],
                             shifted_predictions)
        self.assertListEqual([1.0, 2.0, 3.0, 4.0, 5.0, 8.0, 9.0, 10.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0],
                             shifted_timestamps)

    def test_get_annotation_time_shift(self):

        labelsA = [
            AudacityLabel(1.0, 5.0, 'A'),
            AudacityLabel(8.0, 10.0, 'B'),
            AudacityLabel(15.0, 20.0, 'B')
        ]

        new_labels = Util.get_annotation_time_shift(labelsA)

        expected = [
                {
                    'old_label': AudacityLabel(1.0, 5.0, 'A'),
                    'new_label': AudacityLabel(0.0, 4.0, 'A'),
                    'shift': 1.0
                },
                {
                    'old_label': AudacityLabel(8.0, 10.0, 'B'),
                    'new_label': AudacityLabel(4.0, 6.0, 'B'),
                    'shift': 4.0
                },
                {
                    'old_label': AudacityLabel(15.0, 20.0, 'B'),
                    'new_label': AudacityLabel(6.0, 11.0, 'B'),
                    'shift': 9.0
                }
            ]

        self.assertListEqual(expected, new_labels)
