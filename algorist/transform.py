from __future__ import annotations

import math
import typing as ta
from contextlib import contextmanager

import bpy
from bl_math import clamp
from mathutils import Matrix, Vector

from .blender import create_color_material, hsva_to_rgba

if ta.TYPE_CHECKING:
    from .blender import Color, ColorComponent


class Transform:
    def __init__(
        self,
        matrix: ta.Optional[Matrix] = None,
        color: Color = (0.0, 0.0, 1.0, 1.0),
    ):
        self._matrix = matrix or Matrix()
        self._color = color

    @contextmanager
    def scale(
        self,
        x: ta.Optional[float] = None,
        y: ta.Optional[float] = None,
        z: ta.Optional[float] = None,
        xyz: float = 1.0,
    ):
        """Scale specified dimension. xyz is a shortcut for scaling all
        dimensions equally
        """
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
    def rotate(self, angle: float, axis: ta.Union[ta.Literal["X", "Y", "Z"], Vector]):
        """Rotate angle radians around axis"""
        matrix = self._matrix
        self._matrix = self._matrix @ Matrix.Rotation(angle, 4, axis)
        yield
        self._matrix = matrix

    @property
    def matrix(self) -> Matrix:
        return self._matrix

    @property
    def color_rgba(self) -> Color:
        return hsva_to_rgba(self._color)

    @contextmanager
    def color(
        self,
        hue: ta.Optional[ColorComponent] = None,
        saturation: ta.Optional[ColorComponent] = None,
        value: ta.Optional[ColorComponent] = None,
        alpha: ta.Optional[ColorComponent] = None,
        color: ta.Optional[Color] = None,
    ):
        """Transform color

        If color is specified, it is used as the new base color
        hue increments the hue value, and wraps around.
        saturation, value and alpha are multipliers and clamp to 0..1
        """
        current_color = self._color
        base_color = color or self._color
        self._color = (
            base_color[0] if hue is None else math.modf(base_color[0] + hue)[0],
            base_color[1] if saturation is None else clamp(base_color[1] * saturation),
            base_color[2] if value is None else clamp(base_color[2] * value),
            base_color[3] if alpha is None else clamp(base_color[3] * alpha),
        )
        yield
        self._color = current_color

    def apply(self, obj: bpy.types.Object, create_material: bool = True):
        obj.matrix_world = self._matrix

        if create_material:
            if not obj.material_slots:
                obj.data.materials.append(None)
            material = create_color_material(self.color_rgba)
            # Link the material to the new object, not the shared mesh data
            obj.material_slots[0].link = "OBJECT"
            obj.material_slots[0].material = material
