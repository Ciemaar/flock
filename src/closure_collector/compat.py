try:
    from typing import Any
except ImportError:  # MicroPython compatibility fallback for missing typing
    Any = object  # type: ignore[assignment,misc]

try:
    from collections.abc import Callable
except ImportError:  # MicroPython compatibility fallback for missing collections.abc
    Callable = object  # type: ignore[assignment,misc]

try:
    from typing import TypeVar
except ImportError:  # MicroPython compatibility fallback for missing typing

    def TypeVar(name: str, bound: Any = Any) -> Any:  # type: ignore[misc,no-redef]
        return object


try:
    _FuncT = TypeVar("_FuncT", bound=Callable[..., Any])
except TypeError:
    _FuncT = object  # type: ignore[assignment,misc]

try:
    from abc import ABCMeta, abstractmethod
except ImportError:  # MicroPython compatibility fallback for missing abc

    class ABCMeta(type):  # type: ignore[no-redef]
        pass

    def abstractmethod(funcobj: _FuncT) -> _FuncT:  # noqa: UP047
        return funcobj  # type: ignore[misc]


try:
    from collections.abc import Iterable, Mapping
except ImportError:  # MicroPython compatibility fallback for missing collections.abc
    Iterable = object  # type: ignore[assignment,misc]
    Mapping = object  # type: ignore[assignment,misc]

try:
    from itertools import chain
except ImportError:  # MicroPython compatibility fallback for missing itertools

    class chain:  # type: ignore[no-redef]
        def __init__(self, *iterables: Any):
            self.iterables = iterables

        def __iter__(self) -> Any:
            for it in self.iterables:
                yield from it

        @classmethod
        def from_iterable(cls, iterables: Any) -> Any:
            return cls(*iterables)


try:
    from pprint import pformat
except ImportError:  # MicroPython compatibility fallback for missing pprint
    pformat = repr  # type: ignore[assignment]

try:
    from numbers import Number
except ImportError:  # MicroPython compatibility fallback for missing numbers
    Number = (int, float, complex)  # type: ignore[assignment,misc]

try:
    from types import FunctionType
except ImportError:  # MicroPython compatibility fallback for missing types
    FunctionType = type(lambda: None)  # type: ignore[assignment,misc]

try:
    import inspect
except ImportError:  # MicroPython compatibility fallback for missing inspect
    inspect = None  # type: ignore[assignment]
