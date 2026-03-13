from flock import FlockDict
from glom import glom, Path

f = FlockDict()
f['source'] = 'Original Value'

class C:
    pass
c = C()
c.x = 42

print(glom(c, Path('x')))
print(glom({'y': 42}, Path('y')))
