from __future__ import annotations

import functools
import random
import typing as ta

_RULES: dict[str, list[tuple[float, ta.Callable]]] = {}


def rule(weight=1.0):
    """Create a function decorator to weight a rule

    Multipke functions of the same name should be decorated -
    they will be randomly called based on their relative weights.
    """

    def decorator(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return _invoke_rule(name, *args, **kwargs)

        if name not in _RULES:
            _RULES[name] = []
            last_weight = 0
        else:
            last_weight = _RULES[name][-1][0]
        _RULES[name].append((last_weight + weight, func))

        return wrapper

    return decorator


def _invoke_rule(name: str, *args, **kwargs):
    rules = _RULES[name]
    return random.choices(
        [rule[1] for rule in rules], cum_weights=[rule[0] for rule in rules]
    )[0](*args, **kwargs)
