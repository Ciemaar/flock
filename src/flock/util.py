from typing import Any

try:
    import logging
except ImportError:

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
    from collections.abc import Hashable, MutableMapping
except ImportError:
    try:
        from collections.abc import Hashable, MutableMapping
    except ImportError:
        Hashable = object  # type: ignore[assignment,misc]
        MutableMapping = object  # type: ignore[assignment,misc]

log = logging.getLogger(__name__)

__author__ = "Andy Fundinger"


class FlockException(KeyError):
    pass


def patch(map: MutableMapping, key_list: list[Hashable], val):
    if not key_list:
        raise TypeError("Empty key_lists are invalid for patch.")

    for key in key_list[0:-1]:
        try:
            map = map[key]
        except FlockException:
            raise
        except TypeError as e:
            raise KeyError from e

        except KeyError:
            map[key] = {}
            map = map[key]
    if key_list[-1] == "append":
        if isinstance(map, list):
            map.append(val)
        else:
            raise KeyError("Cannot append to non-list mapping.")
    else:
        try:
            map[key_list[-1]] = val
        except TypeError as e:
            raise KeyError(str(e)) from e
