from glom import Path, glom  # type: ignore

from closure_collector.util import ClosureCollectorException
from flock import FlockException


def collection_reduce(int_collection, func):
    """Create a closure that consists of lazily executing a function on an iterable"""
    return lambda: func(int_collection)


def index_reference(flock, *indexes, **kwargs):
    """
    return closure that references values stored elsewhere using glom.
    :type flock: flock.core.FlockDict
    :param indexes: keys or attributes to be resolved in order (tree walking)
    :return: 0 parameter function with all parameters included as a closure, returns referenced value
    """

    def de_ref():
        try:
            # We specifically want item access since this is index_reference

            # Helper to access by items for index_reference
            def item_access(target):
                curr = target
                for key in indexes:
                    curr = curr[key]
                return curr

            if "default" in kwargs:
                return glom(flock, item_access, default=kwargs["default"], skip_exc=KeyError)
            return glom(flock, item_access)
        except (ClosureCollectorException, FlockException):
            raise

    return de_ref


def attr_reference(flock, *indexes, **kwargs):
    """
    return closure that references values stored elsewhere using glom.
    :type flock: flock.core.FlockDict
    :param indexes: attributes or keys to be resolved in order (tree walking)
    :return: 0 parameter function with all parameters included as a closure, returns referenced value
    """

    def de_ref():
        try:
            if "default" in kwargs:
                return glom(flock, Path(*indexes), default=kwargs["default"], skip_exc=AttributeError)
            return glom(flock, Path(*indexes))
        except (ClosureCollectorException, FlockException):
            raise

    return de_ref


def toggle():
    store = [False]

    def inner_toggle():
        store[0] = not store[0]
        return store[0]

    return inner_toggle
