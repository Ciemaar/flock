from glom import glom, Path

class Dummy:
    pass

d = Dummy()
d.x = 42

print(glom(d, Path('x')))

print(glom({'x': 42}, Path('x')))

print(glom({'x': 42}, 'x'))

print(glom({'x': {'y': 42}}, Path('x', 'y')))
