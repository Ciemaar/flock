"""Module docstring."""

import math
from collections.abc import MutableMapping

from hypothesis import given, settings
from hypothesis import strategies as st
from pytest import raises  # type: ignore

import closure_collector.util
import flock
import flock.closures
import flock.core
import flock.util
from flock import FlockDict

MAX_TEST_LENGTH = 100


@given(
    inlist=st.one_of(
        st.binary().map(memoryview),  # type: ignore
        st.builds(range, st.integers(min_value=0, max_value=MAX_TEST_LENGTH)),
        st.builds(lambda start, size: range(start, start + size), st.integers(), st.integers(min_value=0, max_value=MAX_TEST_LENGTH)),
        st.builds(
            lambda start, size, step: range(start, start + size * step, step),
            st.integers(),
            st.integers(min_value=0, max_value=MAX_TEST_LENGTH),
            st.integers(min_value=1, max_value=MAX_TEST_LENGTH),
        ),
        st.text(),
        st.builds(tuple),
    ),
    root=st.none(),
)
def test_fuzz_FlockList(inlist, root):
    """Docstring for test_fuzz_FlockList."""
    flock.core.FlockList(inlist=inlist, root=root)


@given(
    indict=st.one_of(
        st.dictionaries(st.text(), st.one_of(st.integers(), st.floats(), st.characters(), st.text())),
        st.lists(st.tuples(st.text(), st.one_of(st.integers(), st.floats(), st.characters(), st.text()))),
    ),
    root=st.none(),
)
def test_fuzz_FlockDict(indict, root):
    """Docstring for test_fuzz_FlockDict."""
    flock.FlockDict(indict=indict, root=root)


@given(func=st.functions())
def test_fuzz_is_rule(func):
    """Docstring for test_fuzz_is_rule."""
    assert closure_collector.util.is_rule(func=func)


@given(var=st.one_of(st.integers(), st.floats(), st.characters(), st.text()))
def test_fuzz_is_not_rule(var):
    """Docstring for test_fuzz_is_not_rule."""
    assert not closure_collector.util.is_rule(func=var)


@given(
    map_obj=st.one_of(
        st.dictionaries(st.text(), st.one_of(st.integers(), st.floats(), st.characters(), st.text())),
        st.dictionaries(st.text(), st.one_of(st.integers(), st.floats(), st.characters(), st.text()), dict_class=flock.FlockDict),
    ),
    key_list=st.lists(st.text()),
    val=st.one_of(st.functions(pure=True), st.integers(), st.floats(), st.characters(), st.text()),
)
@settings(report_multiple_bugs=False)
def test_fuzz_patch(map_obj, key_list, val):
    """Docstring for test_fuzz_patch."""
    expect_key_error = False
    ok_to_test = False
    if not len(key_list):
        with raises(TypeError):
            flock.util.patch(collection=map_obj, key_list=key_list, val=val)
    else:
        map_iter = map_obj
        for key in key_list[0:-1]:
            if isinstance(map_iter, list) and not isinstance(key, int):
                expect_key_error = True
                break
            if key in map_iter:
                if not isinstance(map_iter[key], MutableMapping):
                    expect_key_error = True
                    break
                map_iter = map_iter[key]
            else:
                ok_to_test = True
                break
        else:
            if isinstance(map_iter, list) and key_list[-1] != "append" and not isinstance(key_list[-1], int):
                expect_key_error = True

            if not expect_key_error:
                ok_to_test = True
        if expect_key_error:
            with raises(KeyError):
                flock.util.patch(collection=map_obj, key_list=key_list, val=val)
        if ok_to_test:
            flock.util.patch(collection=map_obj, key_list=key_list, val=val)

            map_iter = map_obj
            for key in key_list[0:-1]:
                map_iter = map_iter[key]
            stored_value = map_iter[key_list[-1]]
            if callable(val) and isinstance(map_iter, FlockDict):
                val = val()
            assert stored_value == val or math.isnan(stored_value) and math.isnan(val)  # type: ignore
