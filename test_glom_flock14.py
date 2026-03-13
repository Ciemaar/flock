from collections.abc import MutableMapping
from glom import glom, Path

class MyMapping(MutableMapping):
    def __init__(self, d):
        self.d = d
    def __getitem__(self, key):
        return self.d[key]
    def __setitem__(self, key, value):
        self.d[key] = value
    def __delitem__(self, key):
        del self.d[key]
    def __iter__(self):
        return iter(self.d)
    def __len__(self):
        return len(self.d)

m = MyMapping({'source': 'val'})

try:
    print(glom(m, 'source'))
except Exception as e:
    print("FAILED", type(e))
    import traceback
    traceback.print_exc()
