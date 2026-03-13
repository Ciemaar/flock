"""Module docstring."""

import random
from functools import partial

from flock.core import FlockDict
from model import apply_rules

sheet = {"seed": 42}


def die(num, sides, rnd=None):
    """Docstring for die."""
    if not rnd:
        rnd = random
    return sum(rnd.randint(1, sides) for x in range(num))


def model():
    """Docstring for model."""
    char = FlockDict(sheet)
    apply_rules(char)
    char["rand"] = lambda: random.Random(char["seed"])  # noqa: S311
    char["roll"] = lambda: partial(die, rnd=char["rand"])
    char["rolls"] = lambda: [(char["roll"](1, 10) + char["roll"](1, 10)) for _ in range(12)]
    char["sorted_rolls"] = lambda: sorted(char["rolls"])
    return char
