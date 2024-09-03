import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, Iterable

from closure_collector.util import ClosureCollectorException, is_rule, rebind


class ShearedBase:
    """A basic, dynamic object used as a return type from shear() functions"""

    def __bool__(self):
        return bool(self.__dict__)


class CCBase(metaclass=ABCMeta):
    """Base class for Closure Collector Objects of all sorts"""

    @abstractmethod
    def check(self, path):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this Aggregator from being sheared.
        """

    @abstractmethod
    def shear(self, record_errors=False) -> Any:
        """
        Convert this Mapping into a simple dict

        :param record_errors: if True any exception raised will be stored in place of the result that caused it rather
        than continuing up the call stack

        :return: a simple object representing these closures
        """

    def __call__(self):
        """
        Call must be specified so that FlockMappings can be nested within eachother

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
        super(DynamicClosureCollector, self).__init__()
        self.cache = {}
        self.root = root
        self.peers = set()

    def clear_cache(self):
        if self.root is not None:
            self.root.clear_cache()
            return

        to_collect = {self}
        to_clear = set()
        while to_collect:
            curr = to_collect.pop()
            if curr not in to_clear:
                to_clear.add(curr)
                to_collect.update(curr.get_relatives())

        for peer in to_clear:
            if hasattr(peer, "cache"):
                peer.cache = {}

    def get_relatives(self) -> Iterable:
        return self.peers


class ClosurePromiseCollector(DynamicClosureCollector):
    """A convenience class for default implementations of methods from Dynamic Closure Collector"""

    def __init__(self, root=None):
        """ """
        self.promises = {}
        super(ClosurePromiseCollector, self).__init__(root=root)

    def __setattr__(self, item, val):
        """
        Set a value in a MutableFlock

        default implementation:

        if value is callable it will be added directly to promises, if not it will be converted to a simple lambda.
        Mappings are converted into MutableFlocks, any other handling should be dealt with via direct access to the promises dict.
        """
        if item in {"root", "cache", "peers", "promises"}:
            return super(ClosurePromiseCollector, self).__setattr__(item, val)
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
            return super(ClosurePromiseCollector, self).__getattribute__(item)
        if item in self.cache:
            return self.cache[item]
        else:
            if item in self.promises:
                promise = self.promises[item]
            else:  # If the promise is not there, fallback ultimately to an error.
                return super(ClosurePromiseCollector, self).__getattribute__(item)

            try:
                ret = promise()
            except Exception as e:
                raise ClosureCollectorException(
                    "Error calculating attribute:%s" % item
                ) from e
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
    A Closure Collector  intended for use.
    """

    def __init__(self, *, root=None, **indict):
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type indict: Mapping to be used to create the new FlockDict

        Values from indict are assigned to self one at a time.

        """
        super(ClosureCollector, self).__init__()
        for key, value in indict.items():
            setattr(self, key, value)

    def get_relatives(self):
        rels = {
            promise
            for promise in self.promises.values()
            if hasattr(promise, "clear_cache")
        }
        rels.update(
            peer for peer in getattr(self, "peers", ()) if hasattr(peer, "clear_cache")
        )
        return rels

    def __repr__(self):
        return f"{self.__class__.__name__}({self.shear()},{self.root})"

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
        for key in sorted(self.promises, key=lambda x: (str(x), repr(x))):
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
