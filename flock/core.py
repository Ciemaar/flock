from collections import MutableMapping, Mapping
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

    def __getitem__(self, key):
        """
        Access values by key

        :type key: any hashable type
        :return: the value of the lamba when executed
        """
        return self.promises[key]()

    def __delitem__(self, key):
        del self.promises[key]

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
                ret[key] = value.check(path + [key])
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
        for key, value in self.promises.items():
            if hasattr(value, 'shear'):
                ret[key] = value.shear()
            elif callable(value):
                ret[key] = value()
            else:
                ret[key] = copy(value)
        return ret


class Aggregator(object):
    """
    Aggregate across parallel maps.
    """
    def __init__(self, sources, fn):
        """
        Aggregate across parallel maps.

        :type sources: list of sources to aggregate across, each source should be a map, generally a list, dict, or FlockDict, not all keys need to be present in all sources.
        :type fn: function must take a generator, there is no constraint on the return value
        """
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
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.sources)):
            for sourceNo, source in enumerate(self.sources):
                if key in source:
                    value = source[key]
                    try:
                        self.function([value])
                    except:
                        print("{path}: Source: {sourceNo} is not compatible with function (value={value})".format(
                            value=value, path=path + [key], sourceNo=sourceNo))
                        raise
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


class MetaAggregator(object):
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