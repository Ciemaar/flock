from typing import Any

try:
    from numbers import Number
except ImportError:
    Number = (int, float, complex)  # type: ignore[assignment,misc]

try:
    from types import FunctionType
except ImportError:
    FunctionType = type(lambda: None)  # type: ignore[assignment,misc]


class ClosureCollectorException(AttributeError):
    pass


def rebind(callable, from_obj, to_obj):
    if getattr(callable, "__closure__", False):
        for cell in callable.__closure__:
            if cell.cell_contents is from_obj:
                cell.cell_contents = to_obj


def is_rule(func):
    if not callable(func):
        return False

    if getattr(func, "__closure__", False):  ## TODO replace with inspect_getclosurevars, probably inspect only nonlocals
        for cell in func.__closure__:
            try:
                contents = cell.cell_contents
            except AttributeError:
                contents = cell
            if not isinstance(contents, (str, Number, bytes, tuple, frozenset)):
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
