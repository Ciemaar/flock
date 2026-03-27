import inspect
import warnings
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from collections.abc import (
    Iterable,
    Mapping,
    Sequence,
)
from itertools import chain

from closure_collector.core import (
    CCBase,
    ClosureList,
    ClosureMapping,
    ClosureMappingReduction,
    ClosurePromiseMapping,
    DynamicClosureCollector,
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


class MutableFlock(FlockBase, DynamicClosureCollector):
    """
    The abstract base class for flocks with items that can be set.

    Provides standard mapping-based mutation endpoints (`__setitem__`, etc.) over `closure_collector`'s underlying attribute-based storage logic.
    """

    def __init__(self, root=None):
        """Initialize the object."""
        super().__init__()

    @abstractmethod
    def __setitem__(self, key, val):
        """Set a value in a MutableFlock

        some amount of processing may need to be done."""

    @abstractmethod
    def __getitem__(self, key):
        "Reminder to implement Mapping"

    @abstractmethod
    def __contains__(self, key):
        "Reminder to implement Mapping"

    @abstractmethod
    def __delitem__(self, key):
        "Reminder to implement Mapping"

    @abstractmethod
    def __len__(self):
        "Reminder to implement Mapping"

    def make_callable(self, value):
        if callable(value) and len(inspect.signature(value).parameters) == 0:
            ret = value
            # if it's a closure and there is something in there
            if hasattr(value, "__closure__") and value.__closure__:
                for closure in value.__closure__:
                    if isinstance(closure.cell_contents, DynamicClosureCollector):
                        closure.cell_contents.peers.add(self)
        elif isinstance(value, Mapping):
            ret = FlockDict(value, root=self.root if self.root is not None else self)
        else:
            ret = lambda: value
        return ret


class PromiseFlock(ClosurePromiseMapping):
    """
    A convenience class for default implementations of methods from `MutableFlock`.

    This acts as a shim over `closure_collector`'s `ClosurePromiseMapping`, providing
    dictionary-style access (`__getitem__`, `__setitem__`) mapping to closures.
    """

    _list_class: type | None

    def clear_cache(self):
        # Keeps original behavior in case something specifically depends on it, but uses super() logic.
        super().clear_cache()


class FlockList(ClosureList, FlockBase):
    """
    A sequence implementation equivalent to Python's `list`, natively integrated with closure collection.

    This class leverages `ClosureList` from `closure_collector` to proxy sequence mutations
    and item accesses through the standard flock promise-evaluation pattern.
    """

    def __init__(self, inlist: Sequence | None = None, root: FlockBase | None = None):
        if inlist is None:
            inlist = ()
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type inlist: List to be used to create the new FlockList

        Values from indict are assigned to self one at a time.

        """
        super().__init__(inlist=inlist, root=root)


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

    def __init__(self, indict: list[tuple] | Mapping | None = None, root=None):
        if indict is None:
            indict = {}
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type indict: Mapping to be used to create the new FlockDict

        Values from indict are assigned to self one at a time.

        """
        super().__init__(indict=indict, root=root)


FlockDict._mapping_class = FlockDict
FlockDict._list_class = None

PromiseFlock._mapping_class = FlockDict
PromiseFlock._list_class = None


class Aggregator:
    """
    Aggregate across parallel maps.

    Deprecated - use FlockAggregator
    """

    def __init__(self, sources, fn):
        """
        Aggregate across parallel maps.

        :type sources: list of sources to aggregate across, each source should be a map, generally a dict, or
        FlockDict, not all keys need to be present in all sources.
        :type fn: function must take a generator, there is no constraint on the return value
        """
        warnings.warn(
            "Aggregator is generally replaced with FlockAggregator and will be removed.",
            DeprecationWarning,
        )
        ##TODO:  Allow lists as arguments
        self.sources = sources
        self.function = fn

    def __getitem__(self, key):
        """
        Perform the aggregation for the given key across all the sources.

        :type key: str key to aggregate
        :return: value as returned by the function for that key.
        """
        return self.function(source[key] for source in self.sources if key in source)

    # def __getattr__(self, key):
    #     return self[key]()

    def __call__(self):
        """
        When an Aggregator is returned from a FlockDict or otherwise called, shear it.
        :return:  a sheared version of this Aggrgator
        """
        return self.shear()

    def check(self, path=[]):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        ret = defaultdict(dict)
        for key in set(chain.from_iterable(source.keys() for source in self.sources)):
            for sourceNo, source in enumerate(self.sources):
                if key in source:
                    value = source[key]
                    try:
                        self.function([value])
                    except Exception as e:
                        msg = f"function {self.function.__name__} incompatible with value {value} exception: {str(e)}"
                        ret[key][f"Source: {sourceNo}"] = msg
                        # raise
        return ret

    def shear(self, record_errors=False):
        """
        Convert this Aggregator into a simple dict

        :return: a dict() representation of this Aggregator
        """
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.sources)):
            try:
                ret[key] = self[key]
            except Exception as e:
                if record_errors:
                    ret[key] = e
                else:
                    raise
        return ret


class MetaAggregator:
    """
    Misnamed class that should be merged with the normal aggregator

    Deprecated -  use FlockAggregator
    """

    def __init__(self, source_function, fn):
        warnings.warn(
            "MetaAggregator is generally replaced with FlockAggregator and will be removed.",
            DeprecationWarning,
        )
        self.source_function = source_function
        self.function = fn

    def __getitem__(self, key):
        return lambda: self.function(source[key] for source in self.source_function() if key in source)

    # def __getattr__(self, key):
    #     return self[key]()

    def __call__(self):
        return self.shear()

    def shear(self, record_errors=False):
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.source_function())):
            try:
                ret[key] = self[key]()
            except Exception as e:
                if record_errors:
                    ret[key] = e
                else:
                    raise
        return ret


class FlockAggregator(ClosureMappingReduction, FlockBase):
    """
    An object representing a mathematical or logical aggregation spanning multiple Flock mapping sources.

    This implements `flock`'s legacy `Aggregator` mapping logic using `ClosureMappingReduction` natively
    over `closure_collector` objects.
    """

    def __repr__(self):
        return f"flock.core.FlockAggregator({str(self.shear())})"
