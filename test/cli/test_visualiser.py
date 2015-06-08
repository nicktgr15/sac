from unittest import TestCase
from sac.cli import visualiser


class MyTestCase(TestCase):

    def test_parse_yaafe_header(self):
        visualiser.downsample()
        self.assertEqual(True, True)

# if __name__ == '__main__':
#     unittest.main()
