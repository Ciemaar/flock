"""Module docstring."""

from glom import T, glom  # type: ignore

from closure_collector.util import ClosureCollectorException
from flock import FlockException


def collection_reduce(int_collection, func):
    """Create a closure that consists of lazily executing a function on an iterable"""
    return lambda: func(int_collection)


def index_reference(flock, *indexes, **kwargs):
    """
    Return closure that references values stored elsewhere in a mapping
    :type flock: flock.core.FlockDict
    :param indexes: lambdas to be resolved in order (tree walking)
    :return: 0 parameter function with all parameters included as a closure, returns referenced value
    """

    def de_ref():
        """Docstring for de_ref."""
        spec = T
        for index in indexes:
            spec = spec[index]

        try:
            if "default" in kwargs:
                return glom(flock, spec, default=kwargs["default"])
            else:
                return glom(flock, spec)
        except (ClosureCollectorException, FlockException):
            raise

    return de_ref


def attr_reference(flock, *indexes, **kwargs):
    """
    Return closure that references values stored elsewhere in a mapping
    :type flock: flock.core.FlockDict
    :param indexes: lambdas to be resolved in order (tree walking)
    :return: 0 parameter function with all parameters included as a closure, returns referenced value
    """

    def de_ref():
        """Docstring for de_ref."""
        spec = T
        for index in indexes:
            spec = getattr(spec, index)

        try:
            if "default" in kwargs:
                return glom(flock, spec, default=kwargs["default"])
            else:
                return glom(flock, spec)
        except (ClosureCollectorException, FlockException):
            raise

    return de_ref


def toggle():
    """Docstring for toggle."""
    store = [False]

    def inner_toggle():
        """Docstring for inner_toggle."""
        store[0] = not store[0]
        return store[0]

    return inner_toggle
