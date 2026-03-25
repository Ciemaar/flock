from flock.core import FlockDict
d = FlockDict({'a': lambda: 1, 'b': lambda: 2})
print(list(d))
