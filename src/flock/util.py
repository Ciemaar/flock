import logging
from collections.abc import Hashable, MutableMapping

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
