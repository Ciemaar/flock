import unittest
import uuid as uuid

from flock.closures import reference


class MyTestCase(unittest.TestCase):

    def test_reference(self):
        probe = uuid.uuid4()
        base_dict={'x':probe}
        assert probe is reference(base_dict,'x')()


if __name__ == '__main__':
    unittest.main()
