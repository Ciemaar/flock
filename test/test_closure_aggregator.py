import unittest

from closure_collector.core import ClosureCollector, ShearedBase, ClosureReduction
from closure_collector.util import ClosureCollectorException


class ReductionTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.cc = ClosureCollector()

        self.cc.x = ClosureCollector(**{f"attr_{x}": x for x in range(1, 10)})
        self.cc.y = ClosureCollector(**{f"attr_{x}": 2 * x for x in range(1, 10)})
        self.cc.z = ClosureCollector(**{f"attr_{x}": 3 * x for x in range(2, 20, 2)})

    def test_attr_error(self):
        self.cc.sum = ClosureReduction([self.cc.x, self.cc.y], sum)

        with self.assertRaises(AttributeError):
            assert 33 != self.cc.sum.attr_11

    def test_error_func(self):
        self.cc.sum = ClosureReduction([self.cc.x, self.cc.y], sum)
        self.cc.x.attr_1 = "some string"
        with self.assertRaises(ClosureCollectorException):
            assert 3 != self.cc.sum.attr_1

    def test_shear_list(self):
        self.cc.sum = ClosureReduction([self.cc.x, self.cc.y], lambda x: sum(x))
        assert not self.cc.check()
        assert len(dir(self.cc.sum)) == 9
        assert dir(self.cc.sum) == dir(self.cc.y) == dir(self.cc.x)
        assert "attr_1" in dir(self.cc.sum)
        assert "attr_18" not in dir(self.cc.sum)

        for x in range(1, 10):
            assert getattr(self.cc.sum, f"attr_{x}") == x * 3

        sheared = self.cc.shear()
        assert isinstance(sheared, ShearedBase)
        for x in range(1, 10):
            assert getattr(sheared.sum, f"attr_{x}") == x * 3

    def test_shear_list2(self):
        self.cc.sum = ClosureReduction([self.cc.x, self.cc.z], lambda x: sum(x))
        assert not self.cc.check()
        assert set(dir(self.cc.sum)) == set(dir(self.cc.z)).union(dir(self.cc.x))
        assert len(dir(self.cc.sum)) == 14
        assert "attr_1" in dir(self.cc.sum)
        assert "attr_18" in dir(self.cc.sum)

        for x in range(1, 10, 2):
            assert getattr(self.cc.sum, f"attr_{x}") == x
        for x in range(2, 10, 2):
            assert getattr(self.cc.sum, f"attr_{x}") == x * 4
        for x in range(10, 20, 2):
            assert getattr(self.cc.sum, f"attr_{x}") == x * 3

        sheared = self.cc.shear()
        assert isinstance(sheared, ShearedBase)
        # assert len(dir(sheared.sum)) == 14  #TODO define desired behavior for shearedBase objects

        for x in range(1, 10, 2):
            assert getattr(sheared.sum, f"attr_{x}") == x
        for x in range(2, 10, 2):
            assert getattr(sheared.sum, f"attr_{x}") == x * 4
        for x in range(10, 20, 2):
            assert getattr(sheared.sum, f"attr_{x}") == x * 3

    def test_shear_func(self):
        self.cc.sum = ClosureReduction(
            lambda: [getattr(self.cc, ls) for ls in ["x", "y"]], sum
        )
        assert not self.cc.check()

        for x in range(1, 10):
            assert getattr(self.cc.sum, f"attr_{x}") == x * 3

        sheared = self.cc.shear()
        for x in range(1, 10):
            assert getattr(sheared.sum, f"attr_{x}") == x * 3
        assert isinstance(sheared, ShearedBase)

    def test_check(self):
        self.cc.sum = ClosureReduction([self.cc.x, self.cc.y], lambda x: int(x))
        check = self.cc.check()
        assert not check

    def assertContentsEqual(self, param, param1, *args, **kwargs):
        return self.assertSetEqual(set(param), set(param1), *args, **kwargs)
