from unittest import TestCase

import pickle

import os
from sac.methods.sm_analysis import kernel
from sac.util import Util


class TestKernel(TestCase):

    def setUp(self):

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures/sm.pickle'))) as f:
            self.sm = pickle.load(f)

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures/timestamps.pickle'))) as f:
            self.timestamps = pickle.load(f)

    def test_get_segments(self):
        self.sm = Util.kmeans_image_quantisation(self.sm)
        segments = kernel.get_segments(self.timestamps, self.sm, 0, 3, thresh=0.25, draw=False)
        # self.assertEqual(24, len(segments))
        # Util.write_audacity_labels(segments, "labels.txt")