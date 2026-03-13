from glom import glom, Path
from flock import FlockDict

f = FlockDict()
f['x'] = 42

print(glom(f, 'x'))
