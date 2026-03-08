"""Module docstring."""

import logging
from collections.abc import MutableMapping, MutableSequence
from numbers import Number
from types import FunctionType
from typing import Any, Hashable, Sequence

log = logging.getLogger(__name__)
__author__ = "Andy Fundinger"


class FlockException(KeyError):
    """Docstring for FlockException."""

    pass


def patch(collection: (MutableMapping | MutableSequence), key_list: Sequence[Hashable], val: Any):
    """Docstring for patch."""
    if not key_list:
        raise TypeError("Empty key_lists are invalid for patch.")
    for key in key_list[0:-1]:
        try:
            collection = collection[key]
        except FlockException:
            raise
        except TypeError as e:
            raise KeyError from e
        except KeyError:
            collection[key] = {}
            collection = collection[key]
    if key_list[-1] == "append":
        collection.append(val)
    else:
        try:
            collection[key_list[-1]] = val
        except TypeError as e:
            raise KeyError from e


def is_rule(func):
    """Docstring for is_rule."""
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
        pass
    if isinstance(func, FunctionType):
        return False
    if len(dir(func)) > 26:
        return True
    return False
