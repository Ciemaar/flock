from glom import glom, Path
import glom as g

class Dummy:
    pass

try:
    glom({'x': 42}, 'y')
except Exception as e:
    print(e.__class__.__name__)
    print(e.__class__.__module__)

try:
    glom({'x': 42}, Path('x', 'y'))
except Exception as e:
    print(e.__class__.__name__)
