from closure_collector.compat import Any, TypeVar  # type: ignore[import-untyped]

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
except ImportError:
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

    def copy(x: Any) -> Any:  # noqa: UP047  # type: ignore[misc,no-redef]
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
except ImportError:
    try:
        from collections.abc import Hashable
    except ImportError:  # MicroPython compatibility fallback for missing collections.abc
        Hashable = object  # type: ignore[assignment,misc]
