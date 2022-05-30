import warnings
from collections import defaultdict, OrderedDict
from copy import copy

import inspect
from abc import abstractmethod, ABCMeta
from collections.abc import MutableMapping, Mapping, MutableSequence, Iterable
from itertools import chain

from flock.util import FlockException
from .util import is_rule

__author__ = 'Andy Fundinger'

"""
>>> myList = []
>>> myList.append(lambda:5)
>>> myList.append(lambda:3)
>>> myList.append(lambda:myList[0]()+myList[1]())
>>> [x() for x in myList]
[5, 3, 8]

"""


class FlockBase(Iterable, metaclass=ABCMeta):
    @abstractmethod
    def check(self, path):
        """
        check for any contents that would prevent this Aggregator from being used normally, esp sheared.
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
        return id(self)


class MutableFlock(FlockBase):
    '''The abstract base class for flocks with items that can be set
    '''

    def __init__(self, root=None):
        """
        """
        super(MutableFlock, self).__init__()
        self.root = root

    @abstractmethod
    def __setitem__(self, key, val):
        """Set a value in a MutableFlock
        
        some amount of processing may need to be done."""
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass

    @abstractmethod
    def __contains__(self, key):
        pass

    @abstractmethod
    def __delitem__(self, key):
        pass

    @abstractmethod
    def __len__(self):
        pass

    def make_callable(self, value):
        if callable(value) and len(inspect.signature(value).parameters) == 0:
            ret = value
            # if it's a closure and there is something in there
            if hasattr(value, '__closure__') and value.__closure__:
                for closure in value.__closure__:
                    if isinstance(closure.cell_contents, MutableFlock):
                        closure.cell_contents.peers.add(self)
        elif isinstance(value, Mapping):
            ret = FlockDict(value, root=self.root if self.root is not None else self)
        else:
            ret = lambda: value
        return ret

    def clear_cache(self):
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
            peer.cache = {}

    @abstractmethod
    def get_relatives(self):
        pass


class PromiseFlock(MutableFlock):
    '''A convenience class for default implementations of methods from MutableFlock'''

    def __init__(self, root=None):
        """
        """
        super(PromiseFlock, self).__init__(root=root)
        self.promises = {}

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
                raise FlockException('Error calculating key:%s' % key) from e
            self.cache[key] = ret
            return ret

    def __contains__(self, key):
        return key in self.promises

    def __delitem__(self, key):
        del self.promises[key]
        self.clear_cache()

    def __len__(self):
        return len(self.promises)


class FlockList(PromiseFlock, MutableSequence):
    def __init__(self, inlist=(), root=None):
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type inlist: MutableMapping to be used to create the new FlockList

        Values from indict are assigned to self one at a time.

        """
        super(FlockList, self).__init__()
        self.promises = []
        self.cache = {}
        self.root = root
        self.peers = set()
        for key in inlist:
            self.append(key)

    def __iter__(self):
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
        rels = {promise for promise in self.promises if hasattr(promise, 'clear_cache')}
        rels.update(peer for peer in self.peers if hasattr(peer, 'clear_cache'))
        return rels

    def check(self, path=[]):
        """
        check for any contents that would prevent this FlockList from being used normally, esp sheared.

        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this FlockList from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        ret = {}
        for key, value in enumerate(self.promises):
            if hasattr(value, 'check'):
                value_check = value.check(path + [key])
                if value_check:  # if anything showed up wrong in the check
                    ret[key] = value_check
            assert callable(value)
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
            if hasattr(promise, 'shear'):
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

    def __init__(self, indict={}, root=None):
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type indict: MutableMapping to be used to create the new FlockDict

        Values from indict are assigned to self one at a time.

        """
        super(FlockDict, self).__init__()
        self.promises = {}
        self.cache = {}
        self.root = root
        self.peers = set()
        for key in indict:
            self[key] = indict[key]

    def get_relatives(self):
        rels = {promise for promise in self.promises.values() if hasattr(promise, 'clear_cache')}
        rels.update(peer for peer in self.peers if hasattr(peer, 'clear_cache'))
        return rels

    def __iter__(self):
        return iter(self.promises)

    def __len__(self):
        return len(self.promises)

    #
    # def __hash__(self):
    #     return id(self)

    def check(self, path=[]):
        """
        check for any contents that would prevent this FlockDict from being used normally, esp sheared.

        :type path: list the path to this object, will be prepended to any errors generated
        :return: list of errors that prevent items in this FlockDict from being sheared.

        NOT YET PROPERLY IMPLEMENTED
        """
        ret = {}
        for key, value in self.promises.items():
            if hasattr(value, 'check'):
                value_check = value.check(path + [key])
                if value_check:  # if anything showed up wrong in the check
                    ret[key] = value_check
            assert callable(value)
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
            if hasattr(promise, 'shear'):
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
        return {k: v() for k, v in self.promises.items() if not is_rule(v)}

    def ruleset(self):
        return {k: v for k, v in self.promises.items() if is_rule(v)}


class Aggregator():
    """
    Aggregate across parallel maps.

    Deprecated - use FlockAggregator
    """

    def __init__(self, sources, fn):
        """
        Aggregate across parallel maps.

        :type sources: list of sources to aggregate across, each source should be a map, generally a dict, or FlockDict, not all keys need to be present in all sources.
        :type fn: function must take a generator, there is no constraint on the return value
        """
        warnings.warn('Aggregator is generally replaced with FlockAggregator and will be removed.', DeprecationWarning)
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
                        msg = "function {function} incompatible with value {value} exception: {e}".format(e=str(e),
                                                                                                          value=value,
                                                                                                          path=path + [
                                                                                                              key],
                                                                                                          sourceNo=sourceNo,
                                                                                                          function=self.function.__name__)
                        ret[key]["Source: {sourceNo}".format(sourceNo=sourceNo)] = msg
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


class MetaAggregator():
    """
    Misnamed class that should be merged with the normal aggregator

    Deprecated -  use FlockAggregator
    """

    def __init__(self, source_function, fn):
        warnings.warn('MetaAggregator is generally replaced with FlockAggregator and will be removed.',
                      DeprecationWarning)
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


class FlockAggregator(FlockBase, Mapping):
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
        ##TODO:  Allow lists as arguments
        self.sources = sources
        self.function = fn
        if keys is not None and not callable(keys):
            keys = set(keys)
        self.source_keys = keys

    def __getitem__(self, key):
        """
        Perform the aggregation for the given key across all the sources.

        :type key: str key to aggregate
        :return: value as returned by the function for that key.
        """
        try:
            cross_items = [source[key] for source in self.get_sources() if key in source]
            if not cross_items:
                raise KeyError('Key %s not found' % key)
            return self.function(cross_items)
        except KeyError:
            raise
        except Exception as e:
            raise FlockException('Error Calculating %s:  ' % key + str(e) + '\n' + ','.join(
                '%s:%s' % (source, source[key]) for source in self.get_sources() if key in source)) from e

    def __len__(self):
        return sum(1 for x in self.__iter__())

    def __iter__(self):
        if self.source_keys is not None:
            if callable(self.source_keys):
                return iter(set(self.source_keys()))
            else:
                return iter(self.source_keys)
        return iter(set(chain.from_iterable(source.keys() for source in self.get_sources())))

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
                        msg = "function {function} incompatible with value {value} exception: {e}".format(e=str(e),
                                                                                                          value=value,
                                                                                                          path=path + [
                                                                                                              key],
                                                                                                          sourceNo=sourceNo,
                                                                                                          function=self.function.__name__)
                        ret[key]["Source: {sourceNo}".format(sourceNo=sourceNo)] = msg
                        # raise
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
        return "flock.core.FlockAggregator(%s)" % str(self.shear())
