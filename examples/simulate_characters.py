"""EXPERIMENTAL simulate characters"""

import random
from functools import partial

import mythica.model

from flock.core import FlockDict

sheet = {"seed": 42}


def die(num, sides, rnd=None):
    """Local die function"""
    if not rnd:
        rnd = random
    return sum(rnd.randint(1, sides) for x in range(num))


def model():
    """create and return a character"""
    char = FlockDict(sheet)
    mythica.model.apply_rules(char)
    char["rand"] = lambda: random.Random(char["seed"])
    char["roll"] = lambda: partial(die, rnd=char["rand"])
    char["rolls"] = lambda: [char["roll"](1, 10) + char["roll"](1, 10) for _ in range(12)]
    char["sorted_rolls"] = lambda: sorted(char["rolls"])
    return char
