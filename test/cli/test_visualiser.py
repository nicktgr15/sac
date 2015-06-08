import sys
import os
from unittest import TestCase
from sac.cli import visualiser
import tempfile


TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'testdata.html')



class MyTestCase(TestCase):

    def setUp(self):
        self.stats_csv = os.path.join(os.path.dirname(__file__), '../fixtures/example_yaafe_stats.csv')
        self.no_stats_csv = os.path.join(os.path.dirname(__file__), '../fixtures/example_yaafe_no_stats.csv')

    def test_parse_yaafe_header(self):
        header = visualiser.parse_yaafe_header(self.stats_csv)
        self.assertEqual(22050, header['samplerate'])
        self.assertEqual(15360, header['effective_step_size'])


# if __name__ == '__main__':
#     unittest.main()
