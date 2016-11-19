from collections import MutableMapping, Mapping, defaultdict
from copy import copy
from itertools import chain


__author__ = 'andriod'

"""
>>> myList = []
>>> myList.append(lambda:5)
>>> myList.append(lambda:3)
>>> myList.append(lambda:myList[0]()+myList[1]())
>>> [x() for x in myList]
[5, 3, 8]

"""


class FlockDict(MutableMapping):
    """
    A mutable mapping that contains lambdas which will be evaluated when indexed

    The actual lambdas must take 0 params and are accessible in the .promises attribute
    """
    def __init__(self, indict={}):
        """
        A mutable mapping that contains lambdas which will be evaluated when indexed

        :type indict: MutableMapping to be used to create the new FlockDict

        Values from indict are assigned to self one at a time.

        """
        super(FlockDict, self).__init__()
        self.promises = {}
        self.cache = {}
        for key in indict:
            self[key] = indict[key]

    def __setitem__(self, key, val):
        """
        Add value to FlockDict

        if value is callable it will be added directly to promises, if not it will be converted to  a simple lambda.
        Mappings are converted into FlockDicts, any other handling should be dealt with via direct access to the promises dict.
        """
        if callable(val):
            value = val
        elif isinstance(val, Mapping):
            value = FlockDict(val)
        else:
            value = lambda: val
        self.promises[key] = value
        self.cache = {}

    def __getitem__(self, key):
        """
        Access values by key

        :type key: any hashable type
        :return: the value of the lamba when executed
        """
        if key in self.cache:
            return self.cache[key]
        else:
            ret = self.promises[key]()
            self.cache[key] = ret
            return ret

    def __delitem__(self, key):
        del self.promises[key]
        del self.cache[key]

    def __iter__(self):
        return iter(self.promises)

    def __len__(self):
        return len(self.promises)
    #
    # def __hash__(self):
    #     return id(self)

    def __call__(self):
        """
        Call must be specified so that FlockDicts can be nested within eachother

        :return: self
        """
        return self

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

    def shear(self):
        """
        Recursively convert this FlockDict into a normal python dict.

        Removes all the lambda 'woolieness' from this flock by calling every item and recursively calling anything
         with a shear() function.

        :return: a dict()
        """
        ret = {}
        for key in sorted(self.promises):
            promise = self.promises[key]
            if hasattr(promise, 'shear'):
                ret[key] = promise.shear()
            elif key in self.cache:
                ret[key] = self.cache[key]
            elif callable(promise):
                ret[key] = promise()
            else:
                ret[key] = copy(promise)
            self.cache[key] = ret[key]
        return ret


class Aggregator():
    """
    Aggregate across parallel maps.
    """
    def __init__(self, sources, fn):
        """
        Aggregate across parallel maps.

        :type sources: list of sources to aggregate across, each source should be a map, generally a dict, or FlockDict, not all keys need to be present in all sources.
        :type fn: function must take a generator, there is no constraint on the return value
        """
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

    def shear(self):
        """
        Convert this Aggregator into a simple dict

        :return: a dict() representation of this Aggregator
        """
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.sources)):
            ret[key] = self[key]
        return ret


class MetaAggregator():
    """
    Misnamed class that should be merged with the normal aggregator
    """
    def __init__(self, source_function, fn):
        self.source_function = source_function
        self.function = fn

    def __getitem__(self, key):
        return lambda: self.function(source[key] for source in self.source_function() if key in source)

    # def __getattr__(self, key):
    #     return self[key]()

    def __call__(self):
        return self.shear()

    def shear(self):
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.source_function())):
            ret[key] = self[key]()
        return ret


class FlockAggregator(Mapping):
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
        if keys is not None:
            keys = set(keys)
        self.keys = keys

    def __getitem__(self, key):
        """
        Perform the aggregation for the given key across all the sources.

        :type key: str key to aggregate
        :return: value as returned by the function for that key.
        """
        return self.function(source[key] for source in self.get_sources() if key in source)

    def __len__(self):
        return len(self.__iter__())

    def __iter__(self):
        if self.keys is not None:
            return iter(self.keys)
        return iter(set(chain.from_iterable(source.keys() for source in self.get_sources())))

    def get_sources(self):
        if isinstance(self.sources, Mapping):
            return self.sources.values()
        elif callable(self.sources):
            return self.sources()
        else:
            return self.sources

    def __call__(self):
        """
        When an Aggregator is returned from a FlockDict or otherwise called, shear it.
        :return:  a sheared version of this Aggregator
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

    def shear(self):
        """
        Convert this Aggregator into a simple dict

        :return: a dict() representation of this Aggregator
        """
        ret = {}
        for key in self.__iter__():
            ret[key] = self[key]
        return ret
