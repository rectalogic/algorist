from __future__ import annotations

import functools
import logging
import math
import random
import typing as ta
from contextlib import contextmanager

import bpy
from mathutils import Matrix, Vector

from .blender import create_color_material, hsva_to_rgba
from .mesh_factory import MeshFactory
from .transform import Transform

if ta.TYPE_CHECKING:
    import bpy.types

    from .blender import Color

log = logging.getLogger(__name__)


class Context:
    def __init__(
        self,
        transform: ta.Optional[Transform] = None,
        background_color: ta.Optional[Color] = None,
    ):
        self._transform = transform or Transform()
        self._mesh_factory = MeshFactory()
        self._rules: dict[str, list[tuple[float, ta.Callable]]] = {}
        if background_color:
            bpy.context.scene.world.node_tree.nodes["Background"].inputs[
                "Color"
            ].default_value = hsva_to_rgba(background_color)

    def limit(
        self,
        max_depth: int = 12,
        max_objects: int = 10000,
        min_scale: ta.Optional[float] = None,
    ):
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
                            (s <= min_scale for s in self._transform.matrix.to_scale())
                        ):
                            log.warning("Min scale exceeded")
                            result = None
                        else:
                            result = func(*args, **kwargs)
                depth -= 1
                return result

            return wrapper

        return decorator

    def rule(self, weight=1.0):
        def decorator(func):
            name = func.__name__

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._invoke_rule(name, *args, **kwargs)

            if name not in self._rules:
                self._rules[name] = []
                last_weight = 0
            else:
                last_weight = self._rules[name][-1][0]
            self._rules[name].append((last_weight + weight, func))

            return wrapper

        return decorator

    def _invoke_rule(self, name: str, *args, **kwargs):
        rules = self._rules[name]
        return random.choices(
            [rule[1] for rule in rules], cum_weights=[rule[0] for rule in rules]
        )[0](*args, **kwargs)

    @property
    def transform(self) -> Transform:
        return self._transform

    @property
    def mesh(self) -> MeshFactory:
        return self._mesh_factory
