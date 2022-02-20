from __future__ import annotations

import functools
import logging
import typing as ta
from contextlib import contextmanager

import bpy
from mathutils import Color, Matrix, Vector

if ta.TYPE_CHECKING:
    import bpy.types

log = logging.getLogger(__name__)


class Context:
    def __init__(
        self,
        matrix: ta.Optional[Matrix] = None,
        color: ta.Optional[Color] = None,
        alpha: float = 1.0,
    ):
        self._matrix = matrix or Matrix()
        self._color = color or Color((1, 1, 1))
        self._alpha = alpha

    def limit(self, max_depth=12, max_objects=10000):
        def decorator(func):
            depth = 0
            objects = 0  # XXX need a better way to track objects than just calls to the function?

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
                        result = func(*args, **kwargs)
                depth -= 1
                return result

            return wrapper

        return decorator

    @contextmanager
    def scale(
        self,
        x: ta.Optional[float] = None,
        y: ta.Optional[float] = None,
        z: ta.Optional[float] = None,
        xyz: float = 1.0,
    ):
        matrix = self._matrix
        self._matrix = self._matrix @ Matrix.Diagonal(
            (x or xyz, y or xyz, z or xyz, 1.0)
        )
        yield
        self._matrix = matrix

    @contextmanager
    def translate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        matrix = self._matrix
        self._matrix = self._matrix @ Matrix.Translation((x, y, z))
        yield
        self._matrix = matrix

    @contextmanager
    def rotate(self, angle: float, axis: ta.Union[str, Vector]):
        matrix = self._matrix
        self._matrix = self._matrix @ Matrix.Rotation(angle, 4, axis)
        yield
        self._matrix = matrix

    @contextmanager
    def color(self, color: ta.Optional[Color] = None, alpha: float = 1.0):
        # XXX deal with hsv better
        # XXX this is wrong, need to adjust colors vs current, and clamp
        if color:
            current_color = self._color
            self._color = color
        current_alpha = self._alpha
        self._alpha = alpha
        yield
        if color:
            self._color = current_color
        self._alpha = current_alpha

    def _assign_color(self, obj: bpy.types.Object):
        color = (self._color.r, self._color.g, self._color.b, self._alpha)
        material = bpy.data.materials.new("Color")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = color
        material.diffuse_color = color
        obj.data.materials.append(material)

    def cube(self):
        # XXX make this generic, support user defined construction too
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.object
        cube.matrix_world = self._matrix
        self._assign_color(cube)
