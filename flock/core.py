from collections import MutableMapping, Mapping
from copy import copy
from itertools import chain

__author__ = 'andriod'


class LiveDict(MutableMapping):
    def __init__(self, indict={}):
        super(LiveDict, self).__init__()
        self.promises = {}
        for key in indict:
            self[key] = indict[key]

    def __setitem__(self, key, val):
        if isinstance(val, Mapping):
            value = LiveDict(val)
        elif not callable(val):
            value = lambda: val
        else:
            value = val
        self.promises[key] = value

    def __getitem__(self, key):
        return self.promises[key]()

    def __delitem__(self, key):
        del self.promises[key]

    def __iter__(self):
        return iter(self.promises)

    def __len__(self):
        return len(self.promises)

    def __hash__(self):
        return id(self)

    def __call__(self):
        return self

    def check(self,path=[]):
        ret = {}
        for key, value in self.promises.items():
            if hasattr(value, 'check'):
                ret[key] = value.check(path+[key])
            assert callable(value)
        return ret

    def resolve(self):
        ret = {}
        for key, value in self.promises.items():
            if hasattr(value, 'resolve'):
                ret[key] = value.resolve()
            elif callable(value):
                ret[key] = value()
            else:
                ret[key] = copy(value)
        return ret


class Aggregator(object):
    def __init__(self, sources, fn):
        self.sources = sources
        self.function = fn

    def __getitem__(self, key):
        return self.function(source[key] for source in self.sources if key in source)
    #
    # def __getattr__(self, key):
    #     return self[key]()

    def __call__(self):
        return self.resolve()

    def check(self,path=[]):
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.sources)):
            for sourceNo,source in enumerate(self.sources):
                if key in source:
                    value = source[key]
                    try:
                        self.function([value])
                    except:
                        print("{path}: Source: {sourceNo} is not compatible with function (value={value})".format(value=value,path=path+[key],sourceNo=sourceNo))
                        raise
        return ret

    def resolve(self):
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.sources)):
            ret[key] = self[key]
        return ret


class MetaAggregator(object):
    def __init__(self, source_function, fn):
        self.source_function = source_function
        self.function = fn

    def __getitem__(self, key):
        return lambda: self.function(source[key] for source in self.source_function() if key in source)
    #
    # def __getattr__(self, key):
    #     return self[key]()

    def __call__(self):
        return self.resolve()

    def resolve(self):
        ret = {}
        for key in set(chain.from_iterable(source.keys() for source in self.source_function())):
            ret[key] = self[key]()
        return ret