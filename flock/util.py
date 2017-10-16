import logging
from numbers import Number

from types import FunctionType

from flock.core import FlockException

log = logging.getLogger(__name__)

__author__ = 'andriod'


def patch(map, key_list, val):
    for key in key_list[0:-1]:
        try:
            map = map[key]
        except (KeyError, FlockException) as e:
            if isinstance(e, FlockException) and not isinstance(e.__cause__, KeyError):
                raise
            map[key] = {}
            map = map[key]
    if key_list[-1] == 'append':
        map.append(val)
    else:
        map[key_list[-1]] = val

def is_rule(func):
    if not callable(func):
        return False

    if getattr(func, '__closure__', False):
        for cell in func.__closure__:
            if not isinstance(cell.cell_contents,(str, Number, bytes, tuple, frozenset)):
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