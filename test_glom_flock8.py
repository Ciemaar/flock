from flock import FlockDict
from glom import glom, Path

f = FlockDict()
f['source'] = 'Original Value'

print(glom(f, 'source'))
