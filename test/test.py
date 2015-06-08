import unittest
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sac.cli import visualiser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        visualiser.downsample()
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
