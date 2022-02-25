from __future__ import annotations

import functools
import logging
import typing as ta

import bpy

from .blender import hsva_to_rgba
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

    @property
    def transform(self) -> Transform:
        return self._transform

    @property
    def mesh(self) -> MeshFactory:
        return self._mesh_factory
