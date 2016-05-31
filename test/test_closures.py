import unittest
import uuid as uuid

from flock.closures import reference, lookup


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



if __name__ == '__main__':
    unittest.main()
