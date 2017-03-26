import logging

from flock.util import patch

log = logging.getLogger(__name__)

__author__ = 'andriod'
logging.basicConfig()

import unittest


class PatchTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.d={'outer':1,'mid':{'sub':2,'inner':{'most_inner':3}}}

    def test_patch(self):
        assert self.d=={'outer':1,'mid':{'sub':2,'inner':{'most_inner':3}}}
        patch(self.d, ('outer',), 4)
        assert self.d == {'outer': 4, 'mid': {'sub': 2, 'inner': {'most_inner': 3}}}
        patch(self.d, ['mid','sub'], 5)
        assert self.d == {'outer': 4, 'mid': {'sub': 5, 'inner': {'most_inner': 3}}}
        patch(self.d, ['mid','inner','most_inner'], 6)
        assert self.d == {'outer': 4, 'mid': {'sub': 5, 'inner': {'most_inner': 6}}}
        patch(self.d, ['mid','inner',], 7)
        assert self.d == {'outer': 4, 'mid': {'sub': 5, 'inner': 7}}
        patch(self.d, ['mid',], 8)
        assert self.d == {'outer': 4, 'mid': 8}


if __name__ == '__main__':
    unittest.main()
