import math
from collections.abc import MutableMapping

from _pytest.python_api import raises
from hypothesis import given, strategies as st, settings

import flock
import flock.closures
import flock.core
import flock.util
# TODO: replace st.nothing() with appropriate strategies
from flock import FlockDict


@given(
    indict=st.one_of(
        st.dictionaries(
            st.text(), st.one_of(st.integers(), st.floats(), st.characters(), st.text())
        ),
        st.lists(
            st.tuples(
                st.text(),
                st.one_of(st.integers(), st.floats(), st.characters(), st.text()),
            )
        ),
    ),
    root=st.none(),
)
def test_fuzz_FlockDict(indict, root):
    flock.FlockDict(indict=indict, root=root)


@given(func=st.functions())
def test_fuzz_is_rule(func):
    assert flock.core.is_rule(func=func)


@given(var=st.one_of(st.integers(), st.floats(), st.characters(), st.text()))
def test_fuzz_is_not_rule(var):
    assert not flock.core.is_rule(func=var)


@given(
    map_obj=st.one_of(
        st.dictionaries(
            st.text(), st.one_of(st.integers(), st.floats(), st.characters(), st.text())
        ),
        st.dictionaries(
            st.text(),
            st.one_of(st.integers(), st.floats(), st.characters(), st.text()),
            dict_class=flock.FlockDict,
        ),
    ),
    key_list=st.lists(st.text()),
    val=st.one_of(
        st.functions(pure=True), st.integers(), st.floats(), st.characters(), st.text()
    ),
)
@settings(report_multiple_bugs=False)
def test_fuzz_patch(map_obj, key_list, val):
    expect_key_error = False
    ok_to_test = False
    if not len(key_list):
        with raises(TypeError):
            flock.util.patch(map=map_obj, key_list=key_list, val=val)
    else:
        map_iter = map_obj
        for key in key_list[0:-1]:
            if key in map_iter:
                if not isinstance(map_iter[key], MutableMapping):
                    expect_key_error = True
                    break
                map_iter = map_iter[key]
            else:
                ok_to_test = True
                break
        else:
            ok_to_test = True
        if expect_key_error:
            with raises(KeyError):
                flock.util.patch(map=map_obj, key_list=key_list, val=val)
        if ok_to_test:
            flock.util.patch(map=map_obj, key_list=key_list, val=val)

            map_iter = map_obj
            for key in key_list[0:-1]:
                map_iter = map_iter[key]

            stored_value = map_iter[key_list[-1]]
            if callable(val) and isinstance(map_iter, FlockDict):
                val = val()
            assert stored_value == val or (math.isnan(stored_value) and math.isnan(val))

# TODO: replace st.nothing() with appropriate strategies
