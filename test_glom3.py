from glom import glom, Path

class Dummy:
    pass

try:
    glom({'x': 42}, 'y')
except Exception as e:
    print(type(e))

try:
    glom({'x': 42}, 'y', default=0)
    print("Default worked")
except Exception as e:
    print(type(e))
