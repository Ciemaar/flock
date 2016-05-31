from flock.core import FlockDict, Aggregator

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
        assert len(self.flock) == 0
        self.flock[3] = 3
        assert self.flock[3] == 3
        assert len(self.flock) == 1
        self.flock["Shepherd"] = "Mary"
        assert len(self.flock) == 2
        self.assertEqual(self.flock["Shepherd"], "Mary")
        self.flock["Management"] = ["Mary", "Joshua", "Isaac"]
        assert len(self.flock) == 3
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

    def test_shear(self):
        """
        Test trivial shear opperation
        """
        self.flock[3] = 15
        assert not self.flock.check()
        sheared = self.flock.shear()
        assert len(sheared) == 1
        assert isinstance(sheared, dict)
        assert sheared[3] == 15

        self.flock['cat'] = lambda: 'Abbey'
        assert not self.flock.check()
        sheared = self.flock.shear()
        assert len(sheared) == 2
        assert isinstance(sheared, dict)
        assert sheared['cat'] == 'Abbey'


class AggregatorTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.flock = FlockDict()
        self.flock['x'] = {x: x for x in range(1, 10)}
        self.flock['y'] = {x: 2 * x for x in range(1, 10)}

    def test_total(self):
        self.flock['sum'] = Aggregator([self.flock['x'], self.flock['y']], lambda x: sum(x))
        assert not self.flock.check()
        sheared = self.flock.shear()
        assert len(sheared) == 3
        assert isinstance(sheared, dict)
        assert sheared['sum'] == {x: x * 3 for x in range(1, 10)}


if __name__ == '__main__':
    unittest.main()
