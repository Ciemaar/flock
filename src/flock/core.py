from abc import ABCMeta, abstractmethod
from collections.abc import (
    Iterable,
    Mapping,
)

from closure_collector.core import (
    CCBase,
    ClosureList,
    ClosureMapping,
    ClosureMappingReduction,
    ClosurePromiseMapping,
)

__author__ = "Andy Fundinger"

"""
>>> myList = []
>>> myList.append(lambda:5)
>>> myList.append(lambda:3)
>>> myList.append(lambda:myList[0]()+myList[1]())
>>> [x() for x in myList]
[5, 3, 8]

"""


class FlockBase(CCBase, Mapping, metaclass=ABCMeta):
    """
    Abstract base class establishing the contract for all legacy `flock` objects.

    This essentially mirrors the core base `closure_collector.CCBase` but integrates with standard Python `Mapping`
    interfaces expected by legacy code.
    """

    @abstractmethod
    def check(self, path):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.
        """

    @abstractmethod
    def shear(self, record_errors=False) -> Iterable:
        """
        Convert this Mapping into a simple dict

        :param record_errors: if True any exception raised will be stored in place of the result that caused it rather
        than continuing up the call stack

        :return: a dict() representation of this Aggregator
        """
        pass

    def __call__(self):
        """
        Call must be specified so that FlockMappings can be nested within eachother

        :return: self
        """
        return self

    def __hash__(self, *args, **kwargs):
        return id(self)

    def __dir__(self):
        return object.__dir__(self)


class PromiseFlock(ClosurePromiseMapping):
    """
    A convenience class for mapping collections of closures (legacy).

    This acts as a shim over `closure_collector`'s `ClosurePromiseMapping`, providing
    dictionary-style access (`__getitem__`, `__setitem__`) mapping to closures.
    """

    _list_class: type | None


class FlockList(ClosureList, FlockBase):
    """
    A sequence implementation equivalent to Python's `list`, natively integrated with closure collection.

    This class leverages `ClosureList` from `closure_collector` to proxy sequence mutations
    and item accesses through the standard flock promise-evaluation pattern.
    """


FlockList._list_class = FlockList


class FlockDict(ClosureMapping, FlockBase):
    """
    A mutable mapping (dictionary-like object) that contains closures to be evaluated upon retrieval.

    This implements legacy `flock.FlockDict` behaviour utilizing `closure_collector`'s `ClosureMapping` namespace logic natively.
    By doing so, we ensure `FlockDict` maintains Python `MutableMapping` properties while completely relying on the modern
    `closure_collector` backend execution and dependency graph evaluation flow.
    """

    _list_class: type | None
    _mapping_class: type


FlockDict._mapping_class = FlockDict
FlockDict._list_class = FlockList

PromiseFlock._mapping_class = FlockDict
PromiseFlock._list_class = FlockList


class FlockAggregator(ClosureMappingReduction, FlockBase):
    """
    An object representing a mathematical or logical aggregation spanning multiple Flock mapping sources.

    This implements `flock`'s legacy `Aggregator` mapping logic using `ClosureMappingReduction` natively
    over `closure_collector` objects.
    """

    def __repr__(self):
        return f"flock.core.FlockAggregator({str(self.shear())})"
