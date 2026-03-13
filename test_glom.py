from glom import glom, Path

class Dummy:
    pass

d = Dummy()
d.x = {'y': 42}

print(glom(d, 'x.y'))
print(glom({'x': Dummy()}, 'x'))
