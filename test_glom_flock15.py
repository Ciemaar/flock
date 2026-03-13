from glom import glom, Path, Check, Match, T

m = {'a': 1}

print(glom(m, T['a']))
