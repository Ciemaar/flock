__all__ = [
    "Any",
    "Callable",
    "TypeVar",
    "_FuncT",
    "ABCMeta",
    "abstractmethod",
    "Iterable",
    "Mapping",
    "chain",
    "pformat",
    "Number",
    "FunctionType",
    "inspect",
    "warnings",
    "OrderedDict",
    "defaultdict",
    "MutableMapping",
    "MutableSequence",
    "Sequence",
    "_T",
    "copy",
    "logging",
    "Hashable",
]

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

try:
    import warnings
except ImportError:  # MicroPython compatibility fallback for missing warnings

    class warnings:  # type: ignore[no-redef]
        @staticmethod
        def warn(*args: Any, **kwargs: Any) -> None:
            pass


try:
    from collections import OrderedDict, defaultdict
except ImportError:  # MicroPython compatibility fallback for missing collections

    class OrderedDict(dict):  # type: ignore[no-redef]
        pass

    class defaultdict(dict):  # type: ignore[no-redef]
        def __init__(self, default_factory: Any = None, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)
            self.default_factory = default_factory

        def __missing__(self, key: Any) -> Any:
            if self.default_factory is None:
                raise KeyError(key)
            ret = self[key] = self.default_factory()
            return ret


try:
    from collections.abc import MutableMapping, MutableSequence, Sequence
except ImportError:  # MicroPython compatibility fallback for missing collections.abc
    MutableMapping = object  # type: ignore[assignment,misc]
    MutableSequence = object  # type: ignore[assignment,misc]
    Sequence = object  # type: ignore[assignment,misc]

try:
    _T = TypeVar("_T")
except TypeError:
    _T = object  # type: ignore[assignment,misc]

try:
    from copy import copy
except ImportError:  # MicroPython compatibility fallback for missing copy

    def copy(x: _T) -> _T:  # noqa: UP047  # type: ignore[misc,no-redef]
        return x


try:
    import logging
except ImportError:  # MicroPython compatibility fallback for missing logging

    class logging:  # type: ignore[no-redef]
        @staticmethod
        def getLogger(name: str) -> Any:
            class Logger:
                def warning(self, msg: str, *args: Any) -> None:
                    print(msg % args if args else msg)

                def info(self, msg: str, *args: Any) -> None:
                    print(msg % args if args else msg)

                def debug(self, msg: str, *args: Any) -> None:
                    pass

                def error(self, msg: str, *args: Any) -> None:
                    print(msg % args if args else msg)

            return Logger()


try:
    from collections.abc import Hashable
except ImportError:  # MicroPython compatibility fallback for missing collections.abc
    Hashable = object  # type: ignore[assignment,misc]
