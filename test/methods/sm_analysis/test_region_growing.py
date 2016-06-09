import pickle
from unittest import TestCase

import os
from sac.methods.sm_analysis import region_growing
from sac.methods.sm_analysis.region_growing import REGION_MAX_SIZE
from sac.util import Util


class TestRegionGrowing(TestCase):

    def setUp(self):

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures/sm.pickle'))) as f:
            self.sm = pickle.load(f)

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fixtures/timestamps.pickle'))) as f:
            self.timestamps = pickle.load(f)

    def test_calculate_region_sums_and_boundaries(self):
        region_sums, region_stds, region_means, region_boundaries = \
            region_growing.calculate_region_sums_and_boundaries(0, self.sm)
        self.assertEquals(REGION_MAX_SIZE-1, len(region_sums))
        self.assertEquals(REGION_MAX_SIZE-1, len(region_boundaries))

    def test_identify_homogeneous_region(self):
        region_sums, region_stds, region_means, region_boundaries = \
            region_growing.calculate_region_sums_and_boundaries(0, self.sm)
        detected_boundaries, segment = region_growing.identify_homogeneous_region(
                region_sums, region_stds, region_means, region_boundaries, debug=False)

        self.assertListEqual([0, 23, 0, 23], detected_boundaries)
        self.assertListEqual([0, 23], segment)

    def test_get_segments(self):
        self.sm = Util.kmeans_image_quantisation(self.sm)
        segments = region_growing.get_segments(self.timestamps, self.sm, thresh=0.1, draw=False, debug=False)
        # self.assertEqual(18, len(segments))
        # Util.write_audacity_labels(segments, "labels.txt")
