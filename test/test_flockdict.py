from flock.closures import toggle, reference
from flock.core import FlockDict, Aggregator, MetaAggregator, FlockAggregator, FlockList

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
        self.flock["Shepherd"] = "John"
        self.assertEqual(self.flock["Shepherd"], "John")

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

    def test_consistent_shear(self):
        t = toggle()
        self.flock['toggle'] = t
        self.flock['toggle2'] = t
        self.flock.update({x: lambda: self.flock['toggle'] for x in range(5)})
        sheared = self.flock.shear()
        self.assertEqual(sheared['toggle'], not sheared['toggle2'])
        self.assertEqual([sheared['toggle']] * 5, [sheared[x] for x in range(5)])


class FlockListTestCase(unittest.TestCase):
    """
    Tests of the basic operations of a flock
    """

    def setUp(self):
        super().setUp()
        self.flock = FlockList()

    def test_simple_values(self):
        """
        Test that simple(non-dict, non-callable) values are stored and retrieved transparently.

        """
        assert len(self.flock) == 0
        self.flock.append(3)
        assert self.flock[0] == 3
        assert len(self.flock) == 1
        self.flock.append("Mary")
        assert len(self.flock) == 2
        self.assertEqual(self.flock[1], "Mary")
        self.flock.append(["Mary", "Joshua", "Isaac"])
        assert len(self.flock) == 3
        self.assertEqual(self.flock[2], ["Mary", "Joshua", "Isaac"])
        self.flock[1] = "John"
        self.assertEqual(self.flock[1], "John")

    def test_simple_list(self):
        """
        Test that nested dicts still look like dicts.

        """
        self.flock.append({"Mary": {"lambs": 1, "size": 'little'}})
        assert self.flock[0]["Mary"]['lambs'] == 1
        assert self.flock[0]["Mary"]['size'] == 'little'

    def test_simple_closure(self):
        """
        Test that simple closures are stored without mangling and evaluated on retrieval

        """
        self.flock.append(lambda: "little")
        self.assertEqual(self.flock[0], "little")

    def test_shear(self):
        """
        Test trivial shear opperation
        """
        self.flock.append(15)
        assert not self.flock.check()
        sheared = self.flock.shear()
        assert len(sheared) == 1
        assert isinstance(sheared, list)
        assert sheared[0] == 15

        self.flock.append(lambda: 'Abbey')
        assert not self.flock.check()
        sheared = self.flock.shear()
        assert len(sheared) == 2
        assert isinstance(sheared, list)
        assert sheared[1] == 'Abbey'

    def test_consistent_shear(self):
        t = toggle()
        self.flock.append(t)
        self.flock.append(t)
        self.flock.extend([lambda: self.flock[0] for x in range(5)])
        sheared = self.flock.shear()
        self.assertEqual(sheared[0], not sheared[1])
        self.assertEqual([sheared[0]] * 5, [sheared[x] for x in range(2, 7)])


class FlockCacheTestCase(unittest.TestCase):
    """
    Tests of the basic operations of a flock
    """

    def setUp(self):
        super().setUp()
        self.flock = FlockDict()
        self.flock['source'] = 'Original Value'
        self.flock['nested_source'] = {'source': 'Original Value'}

    def test_nested_cache(self):
        self.flock['dest'] = reference(self.flock, 'source')
        self.flock['nested_dest'] = {'dest': reference(self.flock, 'nested_source', 'source')}
        self.flock['jump_dest'] = {'dest': reference(self.flock['nested_source'], 'source')}
        assert self.flock['dest'] == self.flock['nested_dest']['dest'] == 'Original Value'
        self.flock['source'] = '1st New Value'
        assert self.flock['dest'] == '1st New Value'
        assert self.flock['nested_dest']['dest'] == self.flock['jump_dest']['dest'] == 'Original Value'
        self.flock['nested_source']['source'] = '2nd New Value'
        assert self.flock['dest'] == '1st New Value'
        assert self.flock['nested_dest']['dest'] == '2nd New Value'
        assert self.flock['jump_dest']['dest'] == '2nd New Value'

    def test_split_cache(self):
        self.flock2 = FlockDict()
        self.flock2['dest'] = reference(self.flock, 'source')
        self.flock2['nested_dest'] = {'dest': reference(self.flock, 'nested_source', 'source')}
        self.flock2['jump_dest'] = {'dest': reference(self.flock['nested_source'], 'source')}
        assert self.flock2['dest'] == self.flock2['nested_dest']['dest'] == 'Original Value'
        self.flock['source'] = '1st New Value'
        assert self.flock2['dest'] == '1st New Value'
        assert self.flock2['nested_dest']['dest'] == self.flock2['jump_dest']['dest'] == 'Original Value'
        self.flock['nested_source']['source'] = '2nd New Value'
        assert self.flock2['dest'] == '1st New Value'
        assert self.flock2['nested_dest']['dest'] == '2nd New Value'
        assert self.flock2['jump_dest']['dest'] == '2nd New Value'

class AggregatorTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.flock = FlockDict()
        self.flock['x'] = {x: x for x in range(1, 10)}
        self.flock['y'] = {x: 2 * x for x in range(1, 10)}

    def test_shear(self):
        self.flock['sum'] = Aggregator([self.flock['x'], self.flock['y']], lambda x: sum(x))
        assert not self.flock.check()
        sheared = self.flock.shear()
        assert len(sheared) == 3
        assert isinstance(sheared, dict)
        assert sheared['sum'] == {x: x * 3 for x in range(1, 10)}
        assert dict(self.flock()) == sheared

    def test_check(self):
        self.flock['sum'] = Aggregator([self.flock['x'], self.flock['y']], lambda x: int(x))
        check = self.flock.check()
        assert check
        assert len(check['sum']) == 9
        for value in check['sum'].values():
            assert len(value) == 2


class MetaAggregatorTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.flock = FlockDict()
        self.flock['x'] = {x: x for x in range(1, 10)}
        self.flock['y'] = {x: 2 * x for x in range(1, 10)}

    def test_shear(self):
        self.flock['sum'] = MetaAggregator(lambda: [self.flock[ls] for ls in ['x', 'y']], sum)
        assert not self.flock.check()
        sheared = self.flock.shear()
        assert len(sheared) == 3
        assert isinstance(sheared, dict)
        assert sheared['sum'] == {x: x * 3 for x in range(1, 10)}
        assert dict(self.flock()) == sheared


class FlockAggregatorTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.flock = FlockDict()
        self.flock['x'] = {x: x for x in range(1, 10)}
        self.flock['y'] = {x: 2 * x for x in range(1, 10)}

    def test_shear_list(self):
        self.flock['sum'] = FlockAggregator([self.flock['x'], self.flock['y']], lambda x: sum(x))
        assert not self.flock.check()

        assert len(self.flock['sum']) == 9
        assert self.flock['sum'] == {x: x * 3 for x in range(1, 10)}
        assert self.flock['sum'].shear() == {x: x * 3 for x in range(1, 10)}
        assert self.flock['sum']() == {x: x * 3 for x in range(1, 10)}
        assert self.flock.promises['sum'].shear() == {x: x * 3 for x in range(1, 10)}
        assert self.flock.promises['sum']() == {x: x * 3 for x in range(1, 10)}

        sheared = self.flock.shear()
        assert len(sheared) == 3
        assert isinstance(sheared, dict)
        assert sheared['sum'] == {x: x * 3 for x in range(1, 10)}
        assert dict(self.flock()) == sheared

    def test_shear_func(self):
        self.flock['sum'] = FlockAggregator(lambda: [self.flock[ls] for ls in ['x', 'y']], sum)
        assert not self.flock.check()

        assert len(self.flock['sum']) == 9
        assert self.flock['sum'] == self.flock.promises['sum'].shear() == self.flock.promises['sum']() == {x: x * 3 for
                                                                                                           x in
                                                                                                           range(1, 10)}

        sheared = self.flock.shear()
        assert len(sheared) == 3
        assert isinstance(sheared, dict)
        assert sheared['sum'] == {x: x * 3 for x in range(1, 10)}
        assert dict(self.flock()) == sheared

    def test_check(self):
        self.flock['sum'] = FlockAggregator([self.flock['x'], self.flock['y']], lambda x: int(x))
        check = self.flock.check()
        assert check
        assert len(check['sum']) == 9
        for value in check['sum'].values():
            assert len(value) == 2


if __name__ == '__main__':
    unittest.main()
