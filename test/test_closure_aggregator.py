import unittest

from closure_collector.core import ClosureCollector, ShearedBase, ClosureReduction


class ReductionTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.cc = ClosureCollector()

        self.cc.x = ClosureCollector(**{f"attr_{x}": x for x in range(1, 10)})
        self.cc.y = ClosureCollector(**{f"attr_{x}": 2 * x for x in range(1, 10)})

    def test_shear_list(self):
        self.cc.sum = ClosureReduction([self.cc.x, self.cc.y], lambda x: sum(x))
        assert not self.cc.check()

        for x in range(1, 10):
            assert getattr(self.cc.sum, f"attr_{x}") == x * 3

        sheared = self.cc.shear()
        assert isinstance(sheared, ShearedBase)
        for x in range(1, 10):
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
