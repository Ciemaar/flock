import unittest
import uuid as uuid

import pytest

from closure_collector.closures import (
    index_reference,
    attr_reference,
    toggle,
    collection_reduce,
)
from closure_collector.core import ShearedBase, ClosureCollector
from flock import FlockDict
from flock.closures import lookup


def test_list_reduce():
    test_list = [1, 2, 3]
    test = collection_reduce(test_list, sum)
    assert test() == 6
    test_list[0] = 3
    assert test() == 8


class ClosureAttrTestCase(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.base_obj = ShearedBase()

    def test_attr_reference(self):
        probe = uuid.uuid4()
        self.base_obj.x = probe
        assert probe is attr_reference(self.base_obj, "x")()

    def test_attr_reference_default(self):
        probe = uuid.uuid4()
        assert probe is attr_reference(self.base_obj, "x", default=probe)()

    def test_attr_reference_no_default(self):
        probe = uuid.uuid4()
        with pytest.raises(AttributeError):
            assert probe is attr_reference(self.base_obj, "x")()


class ClosureIndexTestCase(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.base_dict = {}

    def test_index_reference(self):
        probe = uuid.uuid4()
        self.base_dict["x"] = probe
        assert probe is index_reference(self.base_dict, "x")()

    def test_index_reference_default(self):
        probe = uuid.uuid4()
        assert probe is index_reference(self.base_dict, "x", default=probe)()

    def test_attr_reference_no_default(self):
        probe = uuid.uuid4()
        with pytest.raises(KeyError):
            assert probe is index_reference(self.base_dict, "x")()

    def test_lookup(self):
        probe = uuid.uuid4()
        table_row = 5
        base_dict = {"x": table_row}
        table = {table_row: probe}
        assert probe is lookup(base_dict, "x", table)()

    def test_toggle(self):
        tt = toggle()
        self.assertEqual([tt() for x in range(4)], [True, False, True, False])


class FlockClosureTestCase(ClosureIndexTestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.base_dict = FlockDict()


class ClosureCollectorTestCase(ClosureAttrTestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.base_obj = ClosureCollector()


if __name__ == "__main__":
    unittest.main()
