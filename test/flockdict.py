from flock.core import FlockDict

__author__ = 'andriod'

import unittest


class BasicFlockTestCase(unittest.TestCase):
    """
    Tests of the basic operations of a flock
    """

    def setUp(self):
        super().setUp()
        self.flock = FlockDict()

    def test_simple_values(self):
        """
        Test that simple(non-dict, non-callable) values are stored and retrieved transparently.

        """
        self.flock[3] = 3
        assert self.flock[3] == 3
        self.flock["Shepherd"] = "Mary"
        self.assertEqual(self.flock["Shepherd"], "Mary")
        self.flock["Management"] = ["Mary", "Joshua", "Isaac"]
        self.assertEqual(self.flock["Management"], ["Mary", "Joshua", "Isaac"])

    def test_simple_dict(self):
        """
        Test that nested dicts still look like dicts.

        """
        self.flock["Management"] = {"Mary": {"lambs": 1, "size": 'little'}}
        assert self.flock["Management"]["Mary"]['lambs'] == 1
        assert self.flock["Management"]["Mary"]['size'] == 'little'

    def test_simple_closure(self):
        """
        Test that simple closures are stored without mangling and evaluated on retrieval

        """
        self.flock["lamb"] = lambda: "little"
        self.assertEqual(self.flock["lamb"], "little")


if __name__ == '__main__':
    unittest.main()
