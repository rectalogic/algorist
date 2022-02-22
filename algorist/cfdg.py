from __future__ import annotations

import colorsys
import functools
import logging
import math
import random
import typing as ta
from contextlib import contextmanager

import bpy
from bl_math import clamp
from mathutils import Matrix, Vector

if ta.TYPE_CHECKING:
    import bpy.types

log = logging.getLogger(__name__)


class Context:
    def __init__(
        self,
        matrix: ta.Optional[Matrix] = None,
        color: ta.Optional[tuple[float, float, float, float]] = None,
    ):
        self._matrix = matrix or Matrix()
        self._color = color
        self._mesh_cache: dict[
            tuple[str, ta.Any], tuple[bpy.types.Mesh, tuple[bpy.types.Collection, ...]]
        ] = {}
        self._rules: dict[str, list[tuple[float, ta.Callable]]] = {}

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
                            (s <= min_scale for s in self._matrix.to_scale())
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

    @property
    def color_rgba(self) -> tuple[float, float, float, float]:
        return (*colorsys.hsv_to_rgb(*self._color[:3]), self._color[3])

    @contextmanager
    def color(
        self,
        hue: ta.Optional[float] = None,
        saturation: ta.Optional[float] = None,
        value: ta.Optional[float] = None,
        alpha: ta.Optional[float] = None,
        color: ta.Optional[tuple[float, float, float, float]] = None,
    ):
        if color:
            self._color = color
        elif self._color is None:
            yield
            return
        new_color = (
            self._color[0] if hue is None else math.modf(self._color[0] + hue)[0],
            self._color[1]
            if saturation is None
            else clamp(self._color[1] * saturation),
            self._color[2] if value is None else clamp(self._color[2] * value),
            self._color[3] if alpha is None else clamp(self._color[3] * alpha),
        )
        current_color = self._color
        self._color = new_color
        yield
        self._color = current_color

    def _assign_color(self, obj: bpy.types.Object):
        if not self._color:
            return

        color = self.color_rgba
        material = bpy.data.materials.new("Color")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = color
        material.diffuse_color = color
        if self._color[3] < 1:
            material.blend_method = "BLEND"
        obj.data.materials.append(material)

    def shape(self, name: str, shapefunc, **kwargs) -> bpy.types.Object:
        meshkey = (name, tuple(sorted(kwargs.items())))
        mesh, collections = self._mesh_cache.get(meshkey, (None, None))
        if mesh and collections is not None:
            shape = bpy.data.objects.new(name, mesh.copy())
            for c in collections:
                c.objects.link(shape)
        else:
            shapefunc(**kwargs)
            shape = bpy.context.object
            self._mesh_cache[meshkey] = (shape.data.copy(), shape.users_collection)
        shape.matrix_world = self._matrix
        self._assign_color(shape)
        return shape

    def torus(
        self, major_radius: float = 1.0, minor_radius: float = 0.25
    ) -> bpy.types.Object:
        return self.shape(
            "Torus",
            bpy.ops.mesh.primitive_torus_add,
            major_radius=major_radius,
            minor_radius=minor_radius,
        )

    def plane(self, size: float = 2.0):
        return self.shape(
            "Plane",
            bpy.ops.mesh.primitive_plane_add,
            size=size,
        )

    def icosphere(self, radius: float = 1.0, subdivisions: int = 2) -> bpy.types.Object:
        return self.shape(
            "IcoSphere",
            bpy.ops.mesh.primitive_ico_sphere_add,
            radius=radius,
            subdivisions=subdivisions,
        )

    def uvsphere(
        self, radius: float = 1.0, segments: int = 32, ring_count: int = 16
    ) -> bpy.types.Object:
        return self.shape(
            "UVSphere",
            bpy.ops.mesh.primitive_uv_sphere_add,
            radius=radius,
            segments=segments,
            ring_count=ring_count,
        )

    def grid(self, size: float = 2.0):
        return self.shape(
            "Grid",
            bpy.ops.mesh.primitive_grid_add,
            size=size,
        )

    def cylinder(self, radius: float = 1.0, depth: float = 2.0) -> bpy.types.Object:
        return self.shape(
            "Cylinder",
            bpy.ops.mesh.primitive_cylinder_add,
            radius=radius,
            depth=depth,
        )

    def cone(
        self, radius1: float = 1.0, radius2: float = 0.0, depth: float = 2.0
    ) -> bpy.types.Object:
        return self.shape(
            "Cone",
            bpy.ops.mesh.primitive_cone_add,
            radius1=radius1,
            radius2=radius2,
            depth=depth,
        )

    def circle(
        self, radius: float = 1.0, fill_type: str = "NOTHING"
    ) -> bpy.types.Object:
        return self.shape(
            "Circle",
            bpy.ops.mesh.primitive_circle_add,
            radius=radius,
            fill_type=fill_type,
        )

    # XXX make this generic, support user defined construction too
    def cube(self, size: tuple[float, float, float] = (1, 1, 1)) -> bpy.types.Object:
        # scale is baked into the vertices, (1,1,1) is a 2x2x2 cube
        return self.shape(
            "Cube", bpy.ops.mesh.primitive_cube_add, scale=tuple(s * 0.5 for s in size)
        )
