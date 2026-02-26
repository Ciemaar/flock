import logging
from collections.abc import MutableMapping, MutableSequence
from numbers import Number
from types import FunctionType
from typing import Any, Hashable, Sequence

log = logging.getLogger(__name__)

__author__ = "Andy Fundinger"


class FlockException(KeyError):
    pass


def patch(map: MutableMapping | MutableSequence, key_list: Sequence[Hashable], val: Any):
    if not key_list:
        raise TypeError("Empty key_lists are invalid for patch.")

    for key in key_list[0:-1]:
        try:
            map = map[key]  # type: ignore
        except FlockException:
            raise
        except TypeError as e:
            raise KeyError from e

        except KeyError:
            map[key] = {}  # type: ignore
            map = map[key]  # type: ignore
    if key_list[-1] == "append":
        map.append(val)  # type: ignore
    else:
        try:
            map[key_list[-1]] = val  # type: ignore
        except TypeError as e:
            raise KeyError from e


def is_rule(func):
    if not callable(func):
        return False

    closure = getattr(func, "__closure__", None)
    if closure:
        for cell in closure:
            if not isinstance(cell.cell_contents, (str, Number, bytes, tuple, frozenset)):
                return True
    try:
        if set(func.__globals__).intersection(func.__code__.co_names):
            return True
    except AttributeError:
        pass  # not a function object
    if isinstance(func, FunctionType):
        return False

    # Classes with extra properties are considered rules
    if len(dir(func)) > 26:
        return True
    return False
