from flock import FlockDict
from glom import glom, Path

f = FlockDict()
f['source'] = 'Original Value'

try:
    print(glom(f, Path('source')))
except Exception as e:
    print("Failed")
