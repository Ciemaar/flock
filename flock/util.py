"""Module docstring."""

import logging
from collections.abc import MutableMapping, MutableSequence
from typing import Any, Hashable, Sequence

log = logging.getLogger(__name__)
__author__ = "Andy Fundinger"


class FlockException(KeyError):
    """Docstring for FlockException."""

    pass


def patch(collection: (MutableMapping | MutableSequence), key_list: Sequence[Hashable], val: Any):
    """Docstring for patch."""
    if not key_list:
        raise TypeError("Empty key_lists are invalid for patch.")
    for key in key_list[0:-1]:
        try:
            collection = collection[key]  # type: ignore
        except FlockException:
            raise
        except TypeError as e:
            raise KeyError from e
        except KeyError:
            collection[key] = {}  # type: ignore
            collection = collection[key]  # type: ignore
    if key_list[-1] == "append":
        collection.append(val)  # type: ignore
    else:
        try:
            collection[key_list[-1]] = val  # type: ignore
        except TypeError as e:
            raise KeyError from e
