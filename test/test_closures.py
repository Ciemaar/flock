import unittest
import uuid as uuid

from flock.closures import reference, lookup, toggle


class ClosureTestCase(unittest.TestCase):

    def test_reference(self):
        probe = uuid.uuid4()
        base_dict={'x':probe}
        assert probe is reference(base_dict,'x')()

    def test_lookup(self):
        probe = uuid.uuid4()
        table_row = 5
        base_dict = {'x': table_row}
        table = {table_row: probe}
        assert probe is lookup(base_dict, 'x', table)()

    def test_toggle(self):
        tt = toggle()
        self.assertEqual([tt() for x in range(4)], [True, False, True, False])


if __name__ == '__main__':
    unittest.main()
