from glom import glom, Path

class MyDict(dict):
    def __init__(self, d):
        super().__init__(d)
    def __getattr__(self, item):
        raise AttributeError(f"no attribute {item}")

m = MyDict({'source': 'val'})
print(glom(m, 'source'))
