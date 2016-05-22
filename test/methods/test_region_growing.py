import pickle
from unittest import TestCase

from sac.methods.region_growing import REGION_MAX_SIZE
from sac.methods import region_growing
from sac.util import Util
import os


class TestRegionGrowing(TestCase):

    def setUp(self):
        print

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fixtures/sm.pickle'))) as f:
            self.sm = pickle.load(f)

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fixtures/timestamps.pickle'))) as f:
            self.timestamps = pickle.load(f)

    def test_calculate_region_sums_and_boundaries(self):
        region_sums, region_boundaries = region_growing.calculate_region_sums_and_boundaries(0, self.sm)
        self.assertEquals(REGION_MAX_SIZE-1, len(region_sums))
        self.assertEquals(REGION_MAX_SIZE-1, len(region_boundaries))

    def test_identify_homogeneous_region(self):
        region_sums, region_boundaries = region_growing.calculate_region_sums_and_boundaries(0, self.sm)
        detected_boundaries, segment = region_growing.identify_homogeneous_region(region_sums, region_boundaries)

        self.assertListEqual([0, 8, 0, 8], detected_boundaries)
        self.assertListEqual([0, 8], segment)

    def test_region_growing(self):
        segments = region_growing.get_regions(self.timestamps, self.sm, draw=False, debug=False)
        self.assertEqual(23, len(segments))
        # Util.write_audacity_labels(segments, "labels.txt")

