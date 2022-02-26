from __future__ import annotations

import functools
import logging
import random
import typing as ta

from .transform import Transform

log = logging.getLogger(__name__)


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


def limit(
    max_depth: int = 12,
    max_objects: int = 10000,
    min_scale: ta.Optional[float] = None,
    transform: ta.Optional[Transform] = None,
):
    if transform is None and min_scale is not None:
        raise ValueError("Cannot set min_scale without transform")

    def decorator(func):
        depth = 0
        objects = 0

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal depth, objects
            depth += 1
            objects += 1
            if depth >= max_depth:
                log.warning("Max recursion depth exceeded")
                result = None
            else:
                if objects >= max_objects:
                    log.warning("Max objects exceeded")
                    result = None
                else:
                    if min_scale is not None and any(
                        (s <= min_scale for s in transform.matrix.to_scale())
                    ):
                        log.warning("Min scale exceeded")
                        result = None
                    else:
                        result = func(*args, **kwargs)
            depth -= 1
            return result

        return wrapper

    return decorator
