from flock import FlockDict
from glom import glom, Path

f = FlockDict()
f['source'] = 'Original Value'

print("Using item:", glom(f, ['source']))

try:
    print("Using attr:", glom(f, Path('source')))
except Exception as e:
    print(type(e), e)
