import os
from unittest import TestCase
from sac.cli import visualiser


class MyTestCase(TestCase):

    def setUp(self):
        self.stats_csv = os.path.join(os.path.dirname(__file__), '../fixtures/example_yaafe_stats.csv')
        self.no_stats_csv = os.path.join(os.path.dirname(__file__), '../fixtures/example_yaafe_no_stats.csv')
        self.double_stats_csv = os.path.join(os.path.dirname(__file__), '../fixtures/example_yaafe_double_stats.csv')

    def test_parse_yaafe_header_stats(self):
        header = visualiser.parse_yaafe_header(self.stats_csv)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(15360, header['effective_step_size'])

    def test_parse_yaafe_header_no_stats(self):
        header = visualiser.parse_yaafe_header(self.no_stats_csv)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(512, header['effective_step_size'])

    def test_parse_yaafe_header_double_stats(self):
        header = visualiser.parse_yaafe_header(self.double_stats_csv)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(460800, header['effective_step_size'])