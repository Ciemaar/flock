import unittest
import uuid as uuid

from flock import FlockDict
from flock.closures import reference, lookup, toggle


class ClosureTestCase(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.base_dict = {}

    def test_reference(self):
        probe = uuid.uuid4()
        self.base_dict["x"] = probe
        assert probe is reference(self.base_dict, "x")()

    def test_lookup(self):
        probe = uuid.uuid4()
        table_row = 5
        base_dict = {"x": table_row}
        table = {table_row: probe}
        assert probe is lookup(base_dict, "x", table)()

    def test_toggle(self):
        tt = toggle()
        self.assertEqual([tt() for x in range(4)], [True, False, True, False])


class FlockClosureTestCase(ClosureTestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.base_dict = FlockDict()


if __name__ == "__main__":
    unittest.main()
