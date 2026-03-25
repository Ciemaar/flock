import inspect
import warnings
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from collections.abc import Iterable, Mapping, MutableMapping, MutableSequence, Sequence
from copy import copy
from itertools import chain
from pprint import pformat

from closure_collector.util import (
    ClosureCollectorException,
    is_rule,
    rebind,
)

CLOSURE_ATTRS = {"root", "cache", "peers", "promises"}


class ShearedBase:
    """A basic, dynamic object used as a return type from shear() functions."""

    def __bool__(self):
        return bool(self.__dict__)

    def __str__(self):
        return pformat(self.__dict__)


class CCBase(metaclass=ABCMeta):
    """Base class for Closure Collector Objects of all sorts."""

    @abstractmethod
    def check(self, path):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.
        """

    @abstractmethod
    def shear(self, record_errors=False):
        """
        Convert this closure collection into a simple object

        :param record_errors: if True any exception raised will be stored in place of the result that caused it rather
        than continuing up the call stack

        :return: a simple object representing these closures
        """

    @abstractmethod
    def __dir__(self):
        """Closure collector objects all support the dir() method returning the added attributes"""
        pass

    def __call__(self):
        """
        Call must be specified so that Closure Collections can be nested within eachother

        :return: self
        """
        return self

    def clear_cache(self):
        """Empty any cache kept on this object"""

    def get_relatives(self) -> Iterable:
        return ()


class DynamicClosureCollector(CCBase):
    """Base class for closure collector objects that change over time."""

    def __init__(self, root=None):
        """ """
        super().__init__()
        self.cache = {}
        self.root = root
        self.peers = set()

    def clear_cache(self):
        """
        Recursively clear the cache for this object and all related closure collectors.

        If this object is not the root, it delegates to the root. Otherwise, it performs
        a graph traversal using object identities (to support unhashable sequence types
        like ClosureList) and clears the `.cache` attribute of every related object.
        """
        if self.root is not None:
            self.root.clear_cache()
            return

        stack = [self]
        visited_ids = set()

        while stack:
            curr = stack.pop()
            curr_id = id(curr)
            if curr_id not in visited_ids:
                visited_ids.add(curr_id)
                if hasattr(curr, "cache"):
                    curr.cache.clear()
                stack.extend(curr.get_relatives())

    def get_relatives(self) -> Iterable:
        return self.peers


class ClosurePromiseMapping(DynamicClosureCollector):
    """
    A convenience class for mapping collections of closures.

    This base class implements dictionary-like attribute access (`__getitem__`, `__setitem__`)
    but delays type specialization to its subclasses (`ClosureMapping` and `ClosureList`).
    """

    def __dir__(self):
        return object.__dir__(self)

    _exception_class: type[Exception] = ClosureCollectorException
    # We delay setting _mapping_class until ClosureMapping is defined
    _mapping_class: type  # type: ignore

    def __init__(self, root=None):
        self.promises = {}
        super().__init__(root=root)

    def __setitem__(self, key, val):
        value = self.make_callable(val)
        self.promises[key] = value
        self.clear_cache()

    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            # For sequences, we need to handle out of bounds or missing differently.
            # We try indexing into self.promises directly.
            try:
                promise = self.promises[key]
            except IndexError:
                raise IndexError(key)
            except KeyError:
                # We need to raise the expected exception type, since flock expects a FlockException (KeyError subclass)
                # But when standard missing key occurs, FlockDict raises `KeyError` natively before `try` block,
                # actually wait: original `FlockDict` raised `KeyError` naturally from `self.promises[key]` before.
                # However `FlockException` inherits `KeyError`.
                raise KeyError(key)

            try:
                ret = promise()
            except Exception as e:
                raise self._exception_class(f"Error calculating key:{key}") from e
            self.cache[key] = ret
            return ret

    def __contains__(self, key):
        return key in self.promises

    def __delitem__(self, key):
        del self.promises[key]
        self.clear_cache()

    def __len__(self):
        return len(self.promises)

    def make_callable(self, value):
        if callable(value) and len(inspect.signature(value).parameters) == 0:
            ret = value
            # if it's a closure and there is something in there
            if hasattr(value, "__closure__") and value.__closure__:
                for closure in value.__closure__:
                    if isinstance(closure.cell_contents, DynamicClosureCollector):
                        try:
                            closure.cell_contents.peers.add(self)
                        except TypeError:
                            pass
        elif isinstance(value, Mapping):
            child_root = self.root if self.root is not None else self
            ret = self._mapping_class(value, root=child_root)
            try:
                ret.peers.add(self)
            except TypeError:
                pass
        elif getattr(self, "_list_class", None) is not None and isinstance(value, Sequence) and not isinstance(value, str):
            # In the old Flock implementation, sequences were NOT wrapped.
            # But the new code wraps them. If we want them not wrapped, maybe we should just allow `_list_class` to be `None` to bypass this,
            # or perhaps `FlockList` wrappers should support `==` with `list`.
            child_root = self.root if self.root is not None else self
            ret = self._list_class(value, root=child_root)
            try:
                ret.peers.add(self)
            except TypeError:
                pass
        else:
            ret = lambda: value
        return ret


class ClosurePromiseCollector(DynamicClosureCollector):
    """
    A convenience class for default implementations of methods from Dynamic Closure Collector.

    This class enables dot-notation (attribute access) for working with closures rather than dictionary-like indexing.
    """

    def __init__(self, root=None):
        """Initialize the ClosurePromiseCollector with an optional root."""
        self.promises = {}
        super().__init__(root=root)

    def __setattr__(self, item, val):
        """
        Add an attribute to this closure collection

        default implementation:

        if value is callable it will be added directly to promises, if not it will be converted to a simple lambda.
        Any other handling should be dealt with via direct access to the promises dict.
        """
        if item in CLOSURE_ATTRS:
            return super().__setattr__(item, val)
        value = self.make_callable(val)
        self.promises[item] = value
        self.clear_cache()

    def __getattr__(self, item):
        """
        Access values by key

        :type item: any hashable type
        :return: the value of the lamba when executed
        """
        if item.startswith("_") or item in {"root", "cache", "peers", "promises"}:
            return super().__getattribute__(item)
        if item in self.cache:
            return self.cache[item]
        else:
            if item in self.promises:
                promise = self.promises[item]
            else:  # If the promise is not there, fallback ultimately to an error.
                return super().__getattribute__(item)

            try:
                ret = promise()
            except Exception as e:
                raise ClosureCollectorException(f"Error calculating attribute:{item}") from e
            self.cache[item] = ret
            return ret

    def __delattr__(self, item):
        del self.promises[item]
        self.clear_cache()

    def __bool__(self):
        return bool(self.promises)

    def make_callable(self, value):
        if callable(value) and len(inspect.signature(value).parameters) == 0:
            ret = value
            if isinstance(value, DynamicClosureCollector):
                value.peers.add(self)
                if value.root is None:
                    value.root = self
            # if it's a closure and there is something in there
            if hasattr(value, "__closure__") and value.__closure__:
                for closure in value.__closure__:
                    if isinstance(closure.cell_contents, DynamicClosureCollector):
                        closure.cell_contents.peers.add(self)
        else:
            ret = lambda: value
        return ret


class ClosureCollector(ClosurePromiseCollector):
    """
    A Closure Collector intended for general use.

    This acts as a namespace where attributes mapped to functions are automatically invoked
    as closures upon retrieval, caching their results.
    """

    def __init__(self, *, root=None, **indict):
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type indict: Keyword arguments to add as attributes

        Values from indict are assigned to self one at a time.

        """
        super().__init__()
        for key, value in indict.items():
            setattr(self, key, value)

    def __dir__(self):
        return set(self.promises.keys()).union(self.cache.keys())

    def get_relatives(self):
        rels = {promise for promise in self.promises.values() if hasattr(promise, "clear_cache")}
        rels.update(peer for peer in getattr(self, "peers", ()) if hasattr(peer, "clear_cache"))
        return rels

    def __repr__(self):
        return f"{self.__class__.__name__}({self.shear()})"

    #
    # def __hash__(self):
    #     return id(self)

    def check(self, path=[]):
        """
        check for any contents that would prevent this ClosureCollector from being used normally, esp sheared.

        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this ClosureCollector from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        ret = {}
        for key, value in self.promises.items():
            if hasattr(value, "check"):
                value_check = value.check(path + [key])
                if value_check:  # if anything showed up wrong in the check
                    ret[key] = value_check
            assert callable(value)
        return ret

    def shear(self, record_errors=False):
        """
        Recursively convert this ClosureCollector into a normal python dict.

        Removes all the lambda 'woolieness' from this flock by calling every item and recursively calling anything
         with a shear() function.

        :param record_errors:
        :return: a dict()
        """
        ret = ShearedBase()
        for key in sorted(dir(self), key=lambda x: (str(x), repr(x))):
            promise = self.promises[key]
            if hasattr(promise, "shear"):
                setattr(ret, key, promise.shear(record_errors=record_errors))
            elif key in self.cache:
                setattr(ret, key, self.cache[key])
            else:
                try:
                    setattr(ret, key, getattr(self, key))
                except ClosureCollectorException as e:
                    if record_errors:
                        setattr(ret, key, e)
                    else:
                        raise
        return ret

    def dataset(self):
        ret = ShearedBase()
        for k, v in self.promises.items():
            if not is_rule(v):
                setattr(ret, k, v())
        return ret

    def ruleset(self):
        ret = ClosureCollector()
        for k, v in self.promises.items():
            if is_rule(v):
                rebind(v, self, ret)
                setattr(ret, k, v)
        return ret


class ClosureMapping(ClosurePromiseMapping, MutableMapping):
    """
    A mutable mapping that contains lambdas which will be evaluated when indexed
    """

    def __init__(self, indict: list[tuple] | Mapping | None = None, root=None):
        if indict is None:
            indict = {}
        super().__init__(root=root)
        if not hasattr(indict, "items"):
            indict = dict(indict)
        for key, value in indict.items():  # type: ignore
            self[key] = value

    def get_relatives(self):
        rels = set()
        for promise in self.promises.values():
            if hasattr(promise, "clear_cache"):
                try:
                    rels.add(promise)
                except TypeError:
                    # In case the promise (e.g. nested ClosureMapping) is unhashable
                    pass
        for peer in self.peers:
            if hasattr(peer, "clear_cache"):
                try:
                    rels.add(peer)
                except TypeError:
                    pass
        return rels

    def __iter__(self):
        return iter(self.promises)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.shear()},{self.root})"

    def check(self, path=[]):
        """
        check for any contents that would prevent this ClosureMapping from being used normally.
        """
        ret = {}
        for key, value in self.promises.items():
            if hasattr(value, "check"):
                value_check = value.check(path + [key])
                if value_check:
                    ret[key] = value_check
            assert callable(value)
        return ret

    def shear(self, record_errors=False):
        """
        Recursively convert this ClosureMapping into a normal python dict.
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
                except self._exception_class as e:
                    if record_errors:
                        ret[key] = e
                    else:
                        raise
            if not isinstance(ret, MutableMapping):
                self.cache[key] = ret[key]
        return ret

    def dataset(self):
        return {k: v() for k, v in self.promises.items() if not is_rule(v)}

    def ruleset(self):
        return {k: v for k, v in self.promises.items() if is_rule(v)}


ClosurePromiseMapping._mapping_class = ClosureMapping


class ClosureList(ClosurePromiseMapping, MutableSequence):
    """
    A mutable sequence that contains lambdas which will be evaluated when indexed
    """

    _list_class: type | None = None  # Assigned below

    def __eq__(self, other):
        if isinstance(other, list):
            return list(self) == other
        elif isinstance(other, tuple):
            return tuple(self) == other
        return super().__eq__(other)

    def __init__(self, inlist: Sequence | None = None, root=None):
        if inlist is None:
            inlist = ()
        super().__init__(root=root)
        self.promises = []
        for key in inlist:
            self.append(key)

    def __iter__(self):
        return (self[x] for x in range(len(self)))

    def insert(self, index, value):
        value = self.make_callable(value)
        self.promises.insert(index, value)
        self.clear_cache()

    def get_relatives(self):
        rels = set()
        for promise in self.promises:
            if hasattr(promise, "clear_cache"):
                try:
                    rels.add(promise)
                except TypeError:
                    pass
        for peer in self.peers:
            if hasattr(peer, "clear_cache"):
                try:
                    rels.add(peer)
                except TypeError:
                    pass
        return rels

    def check(self, path=[]):
        ret = {}
        for key, value in enumerate(self.promises):
            if hasattr(value, "check"):
                value_check = value.check(path + [key])
                if value_check:
                    ret[key] = value_check
            assert callable(value)
        return ret

    def shear(self, record_errors=False):
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

    def make_callable(self, value):
        if callable(value) and len(inspect.signature(value).parameters) == 0:
            ret = value
            if hasattr(value, "__closure__") and value.__closure__:
                for closure in value.__closure__:
                    if isinstance(closure.cell_contents, DynamicClosureCollector):
                        closure.cell_contents.peers.add(self)
        elif isinstance(value, Mapping):
            child_root = self.root if self.root is not None else self
            ret = self._mapping_class(value, root=child_root)
            try:
                ret.peers.add(self)
            except TypeError:
                pass
        elif isinstance(value, Sequence) and not isinstance(value, str):
            child_root = self.root if self.root is not None else self
            ret = self._list_class(value, root=child_root)
            try:
                ret.peers.add(self)
            except TypeError:
                pass
        else:
            ret = lambda: value
        return ret


ClosureList._list_class = ClosureList


class ClosureReductionMapping(CCBase, Mapping):
    """
    A mapping-based implementation of a closure reduction across multiple maps or parallel data structures.
    """

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
        self.source_keys = keys

    def __getitem__(self, key):
        """
        Perform the aggregation for the given key across all the sources.
        """
        try:
            cross_items = [source[key] for source in self.get_sources() if key in source]
            if not cross_items:
                raise KeyError(f"Key {key} not found")
            return self.function(cross_items)
        except KeyError:
            raise
        except Exception as e:
            raise ClosureCollectorException(
                f"Error Calculating {key}:  " + str(e) + "\n" + ",".join(f"{source}:{source[key]}" for source in self.get_sources() if key in source)
            ) from e

    def __len__(self):
        return sum(1 for x in self.__iter__())

    def __iter__(self):
        if self.source_keys is not None:
            if callable(self.source_keys):
                return iter(set(self.source_keys()))
            else:
                return iter(self.source_keys)
        return iter(set(chain.from_iterable(source.keys() for source in self.get_sources())))

    def __dir__(self):
        return set(self.__iter__())

    def get_sources(self):
        if isinstance(self.sources, Mapping):
            return self.sources.values()
        elif callable(self.sources):
            return self.sources()
        else:
            return self.sources

    def check(self, path=[]):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        """
        ret = {}
        for key in self.__iter__():
            for sourceNo, source in enumerate(self.get_sources()):
                if key in source:
                    value = source[key]
                    try:
                        self.function([value])
                    except Exception as e:
                        msg = f"function {self.function.__name__} incompatible with value {value} exception: {str(e)}"
                        if key not in ret:
                            ret[key] = {}
                        ret[key][f"Source: {sourceNo}"] = msg
                        # raise
        return ret

    def shear(self, record_errors=False):
        """
        Convert this Aggregator into a simple dict
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


class ClosureReduction:
    """
    Aggregate across parallel maps.

    :type sources: one of:
        - a Mapping the values in sources are used as the list above, keys are ignored
        - a callable that returns the list of sources
        - a list of sources to aggregate across, each source should be a map, generally a dict, or FlockDict, not all keys need to be present in all sources.

        Precedence is Mapping, callable, then list

    :type fn: function must take a generator, there is no constraint on the return value
    """

    def __dir__(self):
        return set(chain.from_iterable(dir(source) for source in self.get_sources()))

    def __init__(self, sources, fn, keys=None):
        self.sources = sources
        self.function = fn

    def __getattr__(self, item):
        """
        Perform the reduction for the given key across all the sources.

        :type key: str key to aggregate
        :return: value as returned by the function for that key.
        """
        try:
            cross_items = [getattr(source, item) for source in self.get_sources() if hasattr(source, item)]
            if not cross_items:
                raise AttributeError(f"Attribute {item} not found")
            return self.function(cross_items)
        except AttributeError:
            raise
        except Exception as e:
            raise ClosureCollectorException(
                f"Error Calculating {item}:  "
                + str(e)
                + "\n"
                + ",".join(
                    "{}:{}".format(
                        source,
                        getattr(source, item, "NO VALUE"),
                    )
                    for source in self.get_sources()
                )
            ) from e

    def get_sources(self):
        if isinstance(self.sources, Mapping):
            return self.sources.values()
        elif callable(self.sources):
            return self.sources()
        else:
            return self.sources

    def shear(self):
        return NotImplemented

    def check(self, path=[]):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        return {}
        # ret = defaultdict(dict)
        # for key in set(chain.from_iterable(source.keys() for source in self.sources)):
        #     for sourceNo, source in enumerate(self.sources):
        #         if key in source:
        #             value = source[key]
        #             try:
        #                 self.function([value])
        #             except Exception as e:
        #                 msg = "function {function} incompatible with value {value} exception: {e}".format(
        #                     e=str(e),
        #                     value=value,
        #                     path=path + [key],
        #                     sourceNo=sourceNo,
        #                     function=self.function.__name__,
        #                 )
        #                 ret[key]["Source: {sourceNo}".format(sourceNo=sourceNo)] = msg
        #                 # raise
        # return ret
