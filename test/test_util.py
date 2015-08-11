import os
from unittest import TestCase
from sac.util import Util


class UtilTests(TestCase):
    def setUp(self):
        self.stats_csv = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_stats.csv')
        self.no_stats_csv = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_no_stats.csv')
        self.double_stats_csv = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_double_stats.csv')
        self.no_stats_derivate = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_no_stats_derivate.csv')
        self.stats_derivate = os.path.join(os.path.dirname(__file__), 'fixtures/example_yaafe_stats_derivate.csv')

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
        expected_labels = [[0.0, 1.3931972789115645, 1], [1.3931972789115645, 9.752380952380953, 0],
                           [9.752380952380953, 10.448979591836736, 1], [10.448979591836734, 11.145578231292516, 0],
                           [11.145578231292516, 12.538775510204081, 1], [12.538775510204081, 13.235374149659863, 0],
                           [13.235374149659863, 16.718367346938777, 1]]

        self.assertListEqual(expected_labels, labels)

    def test_calculate_classes_percentages(self):
        classifications = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1]
        percentages = Util.calculate_classes_percentages(classifications)

        self.assertAlmostEqual(0.5833333333333334, percentages[0])
        self.assertAlmostEqual(0.4166666666666667, percentages[1])
