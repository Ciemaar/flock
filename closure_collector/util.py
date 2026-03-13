"""Module docstring."""

from numbers import Number
from types import FunctionType


class ClosureCollectorException(AttributeError):
    """Docstring for ClosureCollectorException."""

    pass


def rebind(callable, from_obj, to_obj):
    """Docstring for rebind."""
    if getattr(callable, "__closure__", False):
        for cell in callable.__closure__:  # type: ignore
            if cell.cell_contents is from_obj:
                cell.cell_contents = to_obj


def is_rule(func):
    """Docstring for is_rule."""
    if not callable(func):
        return False
    if getattr(func, "__closure__", False):
        for cell in func.__closure__:  # type: ignore
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
