import mythica.model


def die(num, sides, rnd=None):
    if not rnd:
        rnd = random
    return sum(rnd.randint(1, sides) for x in range(num))


def model():
    char = FlockDict(sheet)
    mythica.model.apply_rules(char)
    char["rand"] = lambda: random.Random(char["seed"])
    char["roll"] = lambda: partial(die, rnd=char["rand"])
    char["rolls"] = lambda: [
        char["roll"](1, 10) + char["roll"](1, 10) for _ in range(12)
    ]
    char["sorted_rolls"] = lambda: sorted(char["rolls"])
    return char
