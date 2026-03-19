from typing import Any

try:
    import inspect
except ImportError:
    inspect = None  # type: ignore[assignment]

from collections.abc import Callable
from typing import TypeVar

_FuncT = TypeVar("_FuncT", bound=Callable[..., Any])

try:
    from abc import ABCMeta, abstractmethod
except ImportError:

    class ABCMeta(type):  # type: ignore[no-redef]
        pass

    def abstractmethod(funcobj: _FuncT) -> _FuncT:  # noqa: UP047
        return funcobj  # type: ignore[misc]


try:
    from collections.abc import Iterable, Mapping
except ImportError:
    try:
        from collections.abc import Iterable, Mapping
    except ImportError:
        Iterable = object  # type: ignore[assignment,misc]
        Mapping = object  # type: ignore[assignment,misc]

try:
    from itertools import chain
except ImportError:

    class chain:  # type: ignore[no-redef]
        def __init__(self, *iterables: Any):
            self.iterables = iterables

        def __iter__(self) -> Any:
            for it in self.iterables:
                yield from it

        @classmethod
        def from_iterable(cls, iterables: Any) -> Any:
            return cls(*iterables)


try:
    from pprint import pformat
except ImportError:
    pformat = repr  # type: ignore[assignment]

from closure_collector.util import ClosureCollectorException, is_rule, rebind  # noqa: E402

CLOSURE_ATTRS = {"root", "cache", "peers", "promises"}


class ShearedBase:
    """A basic, dynamic object used as a return type from shear() functions"""

    def __bool__(self):
        return bool(self.__dict__)

    def __str__(self):
        return pformat(self.__dict__)


class CCBase(metaclass=ABCMeta):
    """Base class for Closure Collector Objects of all sorts"""

    @abstractmethod
    def check(self, path):
        pass

    @abstractmethod
    def shear(self, record_errors=False):
        pass

    @abstractmethod
    def __dir__(self):
        pass

    def __call__(self):
        return self

    def clear_cache(self):
        pass

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
        if callable(value):
            if inspect is not None:
                is_zero_arg = len(inspect.signature(value).parameters) == 0
            else:
                try:
                    is_zero_arg = value.__code__.co_argcount == 0
                except AttributeError:
                    is_zero_arg = True
        else:
            is_zero_arg = False

        if is_zero_arg:
            ret = value
            if isinstance(value, DynamicClosureCollector):
                value.peers.add(self)
                if getattr(value, "root", None) is None:
                    value.root = self
            # if it's a closure and there is something in there
            if hasattr(value, "__closure__") and value.__closure__:
                for closure in value.__closure__:
                    try:
                        contents = closure.cell_contents
                    except AttributeError:
                        contents = closure
                    if isinstance(contents, DynamicClosureCollector):
                        contents.peers.add(self)
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
