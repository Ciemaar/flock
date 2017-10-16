import logging
import unittest

import pytest

from flock.util import patch, is_rule

log = logging.getLogger(__name__)

__author__ = 'andriod'
logging.basicConfig()


class ProbeObject:
    def __call__(self): pass


class ProbeClassRule(ProbeObject):
    kr = log


class ProbeInstanceRule(ProbeObject):
    def __init__(self, inst_var):
        self.inst_var = inst_var


tir = ProbeInstanceRule(log)


def mk_closure(kr):
    return lambda: kr


@pytest.mark.parametrize(('func', 'is_it'),
                         [(3, False), (lambda: 3, False), (lambda: log, True), (mk_closure(5), False),
                          (mk_closure({}), True), (ProbeObject, False), (ProbeObject(), False),
                          (ProbeClassRule(), True), (ProbeClassRule, True), (tir, True)])
def test_is_rule(func, is_it):
    assert is_rule(func) == is_it


class PatchTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.d = {'outer': 1, 'mid': {'sub': 2, 'inner': {'most_inner': 3}}}

    def test_patch(self):
        assert self.d == {'outer': 1, 'mid': {'sub': 2, 'inner': {'most_inner': 3}}}
        patch(self.d, ('outer',), 4)
        assert self.d == {'outer': 4, 'mid': {'sub': 2, 'inner': {'most_inner': 3}}}
        patch(self.d, ['mid', 'sub'], 5)
        assert self.d == {'outer': 4, 'mid': {'sub': 5, 'inner': {'most_inner': 3}}}
        patch(self.d, ['mid', 'inner', 'most_inner'], 6)
        assert self.d == {'outer': 4, 'mid': {'sub': 5, 'inner': {'most_inner': 6}}}
        patch(self.d, ['mid', 'inner', ], 7)
        assert self.d == {'outer': 4, 'mid': {'sub': 5, 'inner': 7}}
        patch(self.d, ['mid', ], 8)
        assert self.d == {'outer': 4, 'mid': 8}

    def test_patch_missingkeys(self):
        assert self.d == {'outer': 1, 'mid': {'sub': 2, 'inner': {'most_inner': 3}}}
        patch(self.d, ('outer',), 4)
        assert self.d == {'outer': 4, 'mid': {'sub': 2, 'inner': {'most_inner': 3}}}
        patch(self.d, ['newmid', 'sub'], 5)
        assert self.d == {'outer': 4, 'newmid': {'sub': 5}, 'mid': {'sub': 2, 'inner': {'most_inner': 3}}}
        patch(self.d, ['strata', 'inner', 'most_inner'], 6)
        assert self.d == {'strata': {'inner': {'most_inner': 6}}, 'outer': 4, 'newmid': {'sub': 5},
                          'mid': {'sub': 2, 'inner': {'most_inner': 3}}}


if __name__ == '__main__':
    unittest.main()
