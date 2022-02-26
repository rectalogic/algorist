from __future__ import annotations

import functools
import logging
import typing as ta

from .transform import Transform

log = logging.getLogger(__name__)


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
