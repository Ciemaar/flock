import unittest

import pytest

from closure_collector.core import ClosureCollector
from closure_collector.tagadile import Tagadile
from closure_collector.tags import AttributeTagset


class TagadileTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.cc = ClosureCollector()

        self.cc.x = ClosureCollector(**{f"attr_{x}": x for x in range(1, 10)})
        self.cc.y = ClosureCollector(**{f"attr_{x}": 2 * x for x in range(1, 10)})
        self.tagset = AttributeTagset(self.cc)

    @pytest.mark.xfail
    def test_shear_list(self):
        self.cc.sum = Tagadile([self.cc.x, self.cc.y], lambda x: sum(x))
        assert not self.cc.check()

        for x in range(1, 10):
            assert getattr(self.cc.sum, f"attr_{x}") == x * 3

        sheared = self.cc.shear()
        for x in range(1, 10):
            assert getattr(sheared.sum, f"attr_{x}") == x * 3

    @pytest.mark.xfail
    def test_shear_func(self):
        self.cc.sum = Tagadile(lambda: [self.cc[ls] for ls in ["x", "y"]], sum)
        assert not self.cc.check()

        for x in range(1, 10):
            assert getattr(self.cc.sum, f"attr_{x}") == x * 3

        sheared = self.cc.shear()
        for x in range(1, 10):
            assert getattr(sheared.sum, f"attr_{x}") == x * 3

    def test_check(self):
        self.cc.sum = Tagadile([self.cc.x, self.cc.y], lambda x: int(x))
        check = self.cc.check()
        assert not check

    def assertContentsEqual(self, param, param1, *args, **kwargs):
        return self.assertSetEqual(set(param), set(param1), *args, **kwargs)
