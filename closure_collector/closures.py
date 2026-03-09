from closure_collector.util import ClosureCollectorException
from flock import FlockException


def collection_reduce(int_collection, func):
    """Create a closure that consists of lazily executing a function on an iterable"""
    return lambda: func(int_collection)


def index_reference(flock, *indexes, **kwargs):
    """
    return closure that references values stored elsewhere in a mapping
    :type flock: flock.core.FlockDict
    :param indexes: lambdas to be resolved in order (tree walking)
    :return: 0 parameter function with all parameters included as a closure, returns referenced value
    """

    def de_ref():
        currObj = flock

        try:
            # recursively resolve indexes
            for index in indexes:
                currObj = currObj[index]
            return currObj
        except (ClosureCollectorException, FlockException):
            raise
        except KeyError as e:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise

    return de_ref


def attr_reference(flock, *indexes, **kwargs):
    """
    return closure that references values stored elsewhere in a mapping
    :type flock: flock.core.FlockDict
    :param indexes: lambdas to be resolved in order (tree walking)
    :return: 0 parameter function with all parameters included as a closure, returns referenced value
    """

    def de_ref():
        currObj = flock

        try:
            # recursively resolve indexes
            for index in indexes:
                currObj = getattr(currObj, index)
            return currObj
        except (ClosureCollectorException, FlockException):
            raise
        except AttributeError as e:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise

    return de_ref


def toggle():
    store = [False]

    def inner_toggle():
        store[0] = not store[0]
        return store[0]

    return inner_toggle
