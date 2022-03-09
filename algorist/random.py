import random


def rnd(r: float) -> float:
    """returns random number from -r  to r"""
    return (random.random() - 0.5) * 2 * r


def prnd(r: float) -> float:
    """returns random numbere from 0 to r"""
    return random.random() * r


def coinflip(sides: int = 2) -> bool:
    """returns true as if coin with `sides` sides is flipped"""
    coin = random.randint(0, sides - 1)
    return coin == 1
