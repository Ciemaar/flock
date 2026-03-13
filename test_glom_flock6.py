import sys
from collections import UserDict
from glom import glom, Path

class FlockDict(UserDict):
    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        raise AttributeError(f"no attribute {key}")

f = FlockDict()
f['source'] = 'Original Value'

try:
    print(glom(f, Path('source')))
except Exception as e:
    import traceback
    traceback.print_exc()
