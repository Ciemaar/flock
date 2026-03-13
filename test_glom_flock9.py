from flock import FlockDict
from glom import glom, Path

f = FlockDict()
f['source'] = 'Original Value'

try:
    print(glom(f, lambda x: x['source']))
except Exception as e:
    print("lambda failed", e)
