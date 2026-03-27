try:
    from numbers import Number
except ImportError:  # MicroPython compatibility fallback for missing numbers
    Number = (int, float, complex)  # type: ignore[assignment,misc]

try:
    from typing import Any
except ImportError:  # MicroPython compatibility fallback for missing typing
    Any = object  # type: ignore[assignment,misc]

try:
    from types import FunctionType
except ImportError:  # MicroPython compatibility fallback for missing types
    FunctionType = type(lambda: None)  # type: ignore[assignment,misc]

try:
    import inspect

    def is_zero_arg(value: Any) -> bool:
        if not callable(value):
            return False
        return len(inspect.signature(value).parameters) == 0

    def get_cell_contents(cell: Any) -> Any:
        return cell.cell_contents

    def set_cell_contents(cell: Any, value: Any) -> None:
        cell.cell_contents = value

except ImportError:  # MicroPython compatibility fallback for missing inspect

    def is_zero_arg(value: Any) -> bool:
        if not callable(value):
            return False
        try:
            return value.__code__.co_argcount == 0
        except AttributeError:
            return True

    def get_cell_contents(cell: Any) -> Any:
        try:
            return cell.cell_contents
        except AttributeError:
            return cell

    def set_cell_contents(cell: Any, value: Any) -> None:
        try:
            cell.cell_contents = value
        except AttributeError:
            pass  # Read-only fallback in MicroPython


class ClosureCollectorException(AttributeError):
    pass


def rebind(callable, from_obj, to_obj):
    if getattr(callable, "__closure__", False):
        for cell in callable.__closure__:
            if get_cell_contents(cell) is from_obj:
                set_cell_contents(cell, to_obj)


def is_rule(func):
    if not callable(func):
        return False

    if getattr(func, "__closure__", False):  ## TODO replace with inspect_getclosurevars, probably inspect only nonlocals
        for cell in func.__closure__:
            contents = get_cell_contents(cell)
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
