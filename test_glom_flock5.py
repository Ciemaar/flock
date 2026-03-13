from flock import FlockDict
from glom import glom, Path, T

f = FlockDict()
f['source'] = 'Original Value'
try:
    print(glom(f, T['source']))
except Exception as e:
    print("T failed", e)

try:
    print(glom(f, Path('source')))
except Exception as e:
    print("Path failed", e)
