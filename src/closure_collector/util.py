try:
    from numbers import Number
except ImportError:  # MicroPython compatibility fallback for missing numbers
    Number = (int, float, complex)  # type: ignore[assignment,misc]

try:
    import inspect
except ImportError:  # MicroPython compatibility fallback for missing inspect
    inspect = None  # type: ignore[assignment]

try:
    from typing import Any
except ImportError:  # MicroPython compatibility fallback for missing typing
    Any = object  # type: ignore[assignment,misc]

try:
    from types import FunctionType
except ImportError:  # MicroPython compatibility fallback for missing types
    FunctionType = type(lambda: None)  # type: ignore[assignment,misc]


if inspect is not None:

    def is_zero_arg(value: Any) -> bool:
        if not callable(value):
            return False
        return len(inspect.signature(value).parameters) == 0
else:

    def is_zero_arg(value: Any) -> bool:
        if not callable(value):
            return False
        try:
            return value.__code__.co_argcount == 0
        except AttributeError:
            return True


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
