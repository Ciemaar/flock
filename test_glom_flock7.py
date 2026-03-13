import sys
from collections import UserDict
from glom import glom, Path

class FlockDict(dict):
    pass

f = FlockDict()
f['source'] = 'Original Value'

try:
    print(glom(f, Path('source')))
except Exception as e:
    import traceback
    traceback.print_exc()
