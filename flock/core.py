"""Module docstring."""

import inspect
import warnings
from abc import ABCMeta, abstractmethod
from collections import OrderedDict, defaultdict
from collections.abc import Callable, Iterable, Mapping, MutableMapping, MutableSequence
from copy import copy
from itertools import chain
from typing import Any, Sequence, cast

from flock.util import FlockException

from .util import is_rule

__author__ = "Andy Fundinger"
"""
>>> myList = []
>>> myList.append(lambda:5)
>>> myList.append(lambda:3)
>>> myList.append(lambda:myList[0]()+myList[1]())
>>> [x() for x in myList]
[5, 3, 8]

"""


class FlockBase(Iterable, metaclass=ABCMeta):
    """Docstring for FlockBase."""

    @abstractmethod
    def check(self, path):
        """
        Check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.
        """
        pass

    @abstractmethod
    def shear(self, record_errors=False):
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
        """Docstring for __hash__."""
        return id(self)


class MutableFlock(FlockBase):
    """The abstract base class for flocks with items that can be set"""

    def __init__(self, root=None):
        """Docstring for __init__."""
        """ """
        super(MutableFlock, self).__init__()
        self.root = root
        self.peers: set = set()

    @abstractmethod
    def __setitem__(self, key, val):
        """Set a value in a MutableFlock

        some amount of processing may need to be done.
        """
        pass

    @abstractmethod
    def __getitem__(self, key):
        """Docstring for __getitem__."""
        pass

    @abstractmethod
    def __contains__(self, key):
        """Docstring for __contains__."""
        pass

    @abstractmethod
    def __delitem__(self, key):
        """Docstring for __delitem__."""
        pass

    @abstractmethod
    def __len__(self):
        """Docstring for __len__."""
        pass

    def make_callable(self, value):
        """Docstring for make_callable."""
        if callable(value) and len(inspect.signature(value).parameters) == 0:
            ret = value
            if hasattr(value, "__closure__") and value.__closure__:
                for closure in value.__closure__:
                    if isinstance(closure.cell_contents, MutableFlock):
                        closure.cell_contents.peers.add(self)
        elif isinstance(value, Mapping):
            ret = FlockDict(value, root=self.root if self.root is not None else self)
        else:

            def ret():
                """Docstring for ret."""
                return value

        return ret

    def clear_cache(self):
        """Docstring for clear_cache."""
        if self.root is not None:
            self.root.clear_cache()
            return
        to_collect = set([self])
        to_clear = set()
        while to_collect:
            curr = to_collect.pop()
            if curr not in to_clear:
                to_clear.add(curr)
                to_collect.update(curr.get_relatives())
        for peer in to_clear:
            if hasattr(peer, "cache"):
                peer.cache = {}

    @abstractmethod
    def get_relatives(self):
        """Docstring for get_relatives."""
        pass


class PromiseFlock(MutableFlock):
    """A convenience class for default implementations of methods from MutableFlock"""

    def __init__(self, root=None):
        """Docstring for __init__."""
        """ """
        super(PromiseFlock, self).__init__(root=root)
        self.promises: Any = {}
        self.cache: dict = {}

    def __setitem__(self, key, val):
        """
        Set a value in a MutableFlock

        default implementation:

        if value is callable it will be added directly to promises, if not it will be converted to a simple lambda.
        Mappings are converted into MutableFlocks, any other handling should be dealt with via direct access to the promises dict.
        """
        value = self.make_callable(val)
        self.promises[key] = value
        self.clear_cache()

    def __getitem__(self, key):
        """
        Access values by key

        :type key: any hashable type
        :return: the value of the lamba when executed
        """
        if key in self.cache:
            return self.cache[key]
        else:
            promise = self.promises[key]
            try:
                ret = promise()
            except Exception as e:
                raise FlockException("Error calculating key:%s" % key) from e
            self.cache[key] = ret
            return ret

    def __contains__(self, key):
        """Docstring for __contains__."""
        return key in self.promises

    def __delitem__(self, key):
        """Docstring for __delitem__."""
        del self.promises[key]
        self.clear_cache()

    def __len__(self):
        """Docstring for __len__."""
        return len(self.promises)


class FlockList(PromiseFlock, MutableSequence):
    """Docstring for FlockList."""

    def __init__(self, inlist: Sequence = (), root: (FlockBase | None) = None):
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type inlist: List to be used to create the new FlockList

        Values from indict are assigned to self one at a time.

        """
        super(FlockList, self).__init__()
        self.promises: list = []
        self.cache: dict = {}
        self.root = root
        self.peers = set()
        for key in inlist:
            self.append(key)

    def __iter__(self):
        """Docstring for __iter__."""
        return (self[x] for x in range(len(self)))

    def insert(self, index, value):
        """
        Add value to FlockList

        if value is callable it will be added directly to promises, if not it will be converted to  a simple lambda.
        Mappings are converted into FlockLists, any other handling should be dealt with via direct access to the promises dict.
        """
        value = self.make_callable(value)
        self.promises.insert(index, value)
        self.clear_cache()

    def get_relatives(self):
        """Docstring for get_relatives."""
        rels = {promise for promise in self.promises if hasattr(promise, "clear_cache")}
        rels.update(peer for peer in self.peers if hasattr(peer, "clear_cache"))
        return rels

    def check(self, path=[]):
        """
        Check for any contents that would prevent this FlockList from being used normally, esp sheared.

        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this FlockList from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        ret = {}
        for key, value in enumerate(self.promises):
            if hasattr(value, "check"):
                value_check = value.check(path + [key])
                if value_check:
                    ret[key] = value_check
            if not callable(value):
                raise FlockException(f"Value at {key} is not callable")
        return ret

    def shear(self, record_errors=False):
        """
        Recursively convert this FlockList into a normal python dict.

        Removes all the lambda 'woolieness' from this flock by calling every item and recursively calling anything
         with a shear() function.

        :param record_errors:
        :return: a dict()
        """
        ret = []
        for key, promise in enumerate(self.promises):
            if hasattr(promise, "shear"):
                ret.append(promise.shear(record_errors=record_errors))
            elif key in self.cache:
                ret.append(self.cache[key])
            elif callable(promise):
                try:
                    ret.append(promise())
                except Exception as e:
                    if record_errors:
                        ret.append(e)
                    else:
                        raise
            else:
                warnings.warn(DeprecationWarning("Non callable in promises"))
                ret.append(copy(promise))
            self.cache[key] = ret[key]
        return ret


class FlockDict(PromiseFlock, MutableMapping):
    """
    A mutable mapping that contains lambdas which will be evaluated when indexed

    The actual lambdas must take 0 params and are accessible in the .promises attribute
    """

    def __init__(self, indict: (Mapping | list[tuple]) = {}, root=None):
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type indict: Mapping to be used to create the new FlockDict

        Values from indict are assigned to self one at a time.

        """
        super(FlockDict, self).__init__()
        self.promises = {}
        self.cache = {}
        self.root = root
        self.peers = set()
        if not hasattr(indict, "items"):
            indict = dict(indict)
        if not isinstance(indict, Mapping):
            raise TypeError("indict must be a Mapping")
        for key, value in indict.items():
            self[key] = value

    def get_relatives(self):
        """Docstring for get_relatives."""
        rels = {promise for promise in self.promises.values() if hasattr(promise, "clear_cache")}
        rels.update(peer for peer in self.peers if hasattr(peer, "clear_cache"))
        return rels

    def __iter__(self):
        """Docstring for __iter__."""
        return iter(self.promises)

    def __len__(self):
        """Docstring for __len__."""
        return len(self.promises)

    def __repr__(self):
        """Docstring for __repr__."""
        return f"{self.__class__.__name__}({self.shear()},{self.root})"

    def check(self, path=[]):
        """
        Check for any contents that would prevent this FlockDict from being used normally, esp sheared.

        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this FlockDict from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        ret = {}
        for key, value in self.promises.items():
            if hasattr(value, "check"):
                value_check = value.check(path + [key])
                if value_check:
                    ret[key] = value_check
            if not callable(value):
                raise FlockException(f"Value at {key} is not callable")
        return ret

    def shear(self, record_errors=False):
        """
        Recursively convert this FlockDict into a normal python dict.

        Removes all the lambda 'woolieness' from this flock by calling every item and recursively calling anything
         with a shear() function.

        :param record_errors:
        :return: a dict()
        """
        ret = OrderedDict()
        for key in sorted(self.promises, key=lambda x: (str(x), repr(x))):
            promise = self.promises[key]
            if hasattr(promise, "shear"):
                ret[key] = promise.shear(record_errors=record_errors)
            elif key in self.cache:
                ret[key] = self.cache[key]
            else:
                try:
                    ret[key] = self[key]
                except FlockException as e:
                    if record_errors:
                        ret[key] = e
                    else:
                        raise
            if not isinstance(ret, MutableMapping):
                self.cache[key] = ret[key]
        return ret

    def dataset(self):
        """Docstring for dataset."""
        return {k: v() for k, v in self.promises.items() if not is_rule(v)}

    def ruleset(self):
        """Docstring for ruleset."""
        return {k: v for k, v in self.promises.items() if is_rule(v)}


class Aggregator:
    """
    Aggregate across parallel maps.

    Deprecated - use FlockAggregator
    """

    def __init__(self, sources, fn):
        """
        Aggregate across parallel maps.

        :type sources: list of sources to aggregate across, each source should be a map,
            generally a dict, or FlockDict, not all keys need to be present in all sources.
        :type fn: function must take a generator, there is no constraint on the return value
        """
        warnings.warn("Aggregator is generally replaced with FlockAggregator and will be removed.", DeprecationWarning)
        self.sources = sources
        self.function = fn

    def __getitem__(self, key):
        """
        Perform the aggregation for the given key across all the sources.

        :type key: str key to aggregate
        :return: value as returned by the function for that key.
        """
        return self.function(source[key] for source in self.sources if key in source)

    def __call__(self):
        """
        When an Aggregator is returned from a FlockDict or otherwise called, shear it.
        :return:  a sheared version of this Aggrgator
        """
        return self.shear()

    def check(self, path=[]):
        """
        Check for any contents that would prevent this Aggregator from being used normally, esp sheared.
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
                        msg = "function {function} incompatible with value {value} exception: {e} at path {path} source {sourceNo}".format(
                            e=str(e), value=value, path=path + [key], sourceNo=sourceNo, function=self.function.__name__
                        )
                        ret[key]["Source: {sourceNo}".format(sourceNo=sourceNo)] = msg
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
        """Docstring for __init__."""
        warnings.warn("MetaAggregator is generally replaced with FlockAggregator and will be removed.", DeprecationWarning)
        self.source_function = source_function
        self.function = fn

    def __getitem__(self, key):
        """Docstring for __getitem__."""
        return lambda: self.function(source[key] for source in self.source_function() if key in source)

    def __call__(self):
        """Docstring for __call__."""
        return self.shear()

    def shear(self, record_errors=False):
        """Docstring for shear."""
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


class FlockAggregator(FlockBase, Mapping):
    """Docstring for FlockAggregator."""

    def __init__(self, sources, fn, keys=None):
        """
        Aggregate across parallel maps.

        :type sources: one of:
            - list of sources to aggregate across, each source should be a map, generally a dict, or FlockDict, not all keys need to be present in all sources.
            - Mapping the values in sources are used as the list above, keys are ignored
            - a callable that returns the list of sources

            Precedence is Mapping, callable, then list

        :type fn: function must take a generator, there is no constraint on the return value
        """
        self.sources = sources
        self.function = fn
        if keys is not None and not callable(keys):
            keys = set(keys)
        self.source_keys: set | Callable[[], Iterable] | None = keys

    def __getitem__(self, key):
        """
        Perform the aggregation for the given key across all the sources.

        :type key: str key to aggregate
        :return: value as returned by the function for that key.
        """
        try:
            cross_items = [source[key] for source in self.get_sources() if key in source]
            if not cross_items:
                raise KeyError("Key %s not found" % key)
            return self.function(cross_items)
        except KeyError:
            raise
        except Exception as e:
            raise FlockException(
                "Error Calculating %s:  " % key + str(e) + "\n" + ",".join("%s:%s" % (source, source[key]) for source in self.get_sources() if key in source)
            ) from e

    def __len__(self):
        """Docstring for __len__."""
        return sum(1 for x in self.__iter__())

    def __iter__(self):
        """Docstring for __iter__."""
        if self.source_keys is not None:
            if callable(self.source_keys):
                return iter(set(cast(Callable[[], Iterable], self.source_keys)()))
            else:
                return iter(self.source_keys)
        return iter(set(chain.from_iterable(source.keys() for source in self.get_sources())))

    def get_sources(self) -> Iterable[Mapping]:
        """Docstring for get_sources."""
        if isinstance(self.sources, Mapping):
            return self.sources.values()
        elif callable(self.sources):
            return cast(Iterable[Mapping], self.sources())
        else:
            return cast(Iterable[Mapping], self.sources)

    def check(self, path=[]):
        """
        Check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        ret = defaultdict(dict)
        for key in self.__iter__():
            for sourceNo, source in enumerate(self.get_sources()):
                if key in source:
                    value = source[key]
                    try:
                        self.function([value])
                    except Exception as e:
                        msg = "function {function} incompatible with value {value} exception: {e} at path {path} source {sourceNo}".format(
                            e=str(e), value=value, path=path + [key], sourceNo=sourceNo, function=self.function.__name__
                        )
                        ret[key]["Source: {sourceNo}".format(sourceNo=sourceNo)] = msg
        return ret

    def shear(self, record_errors=False):
        """
        Convert this Aggregator into a simple dict

        :param record_errors:
        :return: a dict() wmrepresentation of this Aggregator
        """
        ret = {}
        for key in self.__iter__():
            try:
                ret[key] = self[key]
            except Exception as e:
                if record_errors:
                    ret[key] = e
                else:
                    raise
        return ret

    def __repr__(self):
        """Docstring for __repr__."""
        return "flock.core.FlockAggregator(%s)" % str(self.shear())
