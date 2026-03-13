"""Module docstring."""

import logging
import unittest

import pytest

from closure_collector.util import is_rule
from flock import FlockDict
from flock.util import patch

log = logging.getLogger(__name__)
__author__ = "Andy Fundinger"
logging.basicConfig()


class ProbeObject:
    """Docstring for ProbeObject."""

    def __call__(self):
        """Docstring for __call__."""
        pass


class ProbeClassRule(ProbeObject):
    """Docstring for ProbeClassRule."""

    kr = log


class ProbeInstanceRule(ProbeObject):
    """Docstring for ProbeInstanceRule."""

    def __init__(self, inst_var):
        """Docstring for __init__."""
        self.inst_var = inst_var


tir = ProbeInstanceRule(log)


def mk_closure(kr):
    """Docstring for mk_closure."""
    return lambda: kr


@pytest.mark.parametrize(
    ("func", "is_it"),
    [
        (3, False),
        (lambda: 3, False),
        (lambda: log, True),
        (mk_closure(5), False),
        (mk_closure({}), True),
        (ProbeObject, True),
        (ProbeObject(), True),
        (ProbeClassRule(), True),
        (ProbeClassRule, True),
        (tir, True),
    ],
)
def test_is_rule(func, is_it):
    """Docstring for test_is_rule."""
    assert is_rule(func) == is_it


class PatchTestCase(unittest.TestCase):
    """Docstring for PatchTestCase."""

    def setUp(self):
        """Docstring for setUp."""
        super().setUp()
        self.d = {"outer": 1, "mid": {"sub": 2, "inner": {"most_inner": 3}}}

    def test_patch(self):
        """Docstring for test_patch."""
        assert self.d == {"outer": 1, "mid": {"sub": 2, "inner": {"most_inner": 3}}}
        patch(self.d, ("outer",), 4)  # type: ignore
        assert self.d == {"outer": 4, "mid": {"sub": 2, "inner": {"most_inner": 3}}}
        patch(self.d, ["mid", "sub"], 5)
        assert self.d == {"outer": 4, "mid": {"sub": 5, "inner": {"most_inner": 3}}}
        patch(self.d, ["mid", "inner", "most_inner"], 6)
        assert self.d == {"outer": 4, "mid": {"sub": 5, "inner": {"most_inner": 6}}}
        patch(self.d, ["mid", "inner"], 7)
        assert self.d == {"outer": 4, "mid": {"sub": 5, "inner": 7}}
        patch(self.d, ["mid"], 8)
        assert self.d == {"outer": 4, "mid": 8}

    def test_patch_missingkeys(self):
        """Docstring for test_patch_missingkeys."""
        assert self.d == {"outer": 1, "mid": {"sub": 2, "inner": {"most_inner": 3}}}
        patch(self.d, ("outer",), 4)  # type: ignore
        assert self.d == {"outer": 4, "mid": {"sub": 2, "inner": {"most_inner": 3}}}
        patch(self.d, ["newmid", "sub"], 5)
        assert self.d == {"outer": 4, "newmid": {"sub": 5}, "mid": {"sub": 2, "inner": {"most_inner": 3}}}
        patch(self.d, ["strata", "inner", "most_inner"], 6)
        assert self.d == {"strata": {"inner": {"most_inner": 6}}, "outer": 4, "newmid": {"sub": 5}, "mid": {"sub": 2, "inner": {"most_inner": 3}}}


class PatchFlockTestCase(PatchTestCase):
    """Docstring for PatchFlockTestCase."""

    def setUp(self):
        """Docstring for setUp."""
        super().setUp()
        self.d = FlockDict({"outer": 1, "mid": {"sub": 2, "inner": {"most_inner": 3}}})


if __name__ == "__main__":
    unittest.main()
