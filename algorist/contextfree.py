from __future__ import annotations

import functools
import logging
import math
import random
import typing as ta
from contextlib import contextmanager

import bpy
from bl_math import clamp
from mathutils import Matrix, Vector

from .blender import create_color_material, hsva_to_rgba

if ta.TYPE_CHECKING:
    import bpy.types

log = logging.getLogger(__name__)


class Context:
    def __init__(
        self,
        matrix: ta.Optional[Matrix] = None,
        background_color: ta.Optional[tuple[float, float, float, float]] = None,
    ):
        self._matrix = matrix or Matrix()
        self._color = (0.0, 0.0, 1.0, 1.0)
        self._mesh_cache: dict[tuple[str, tuple], bpy.types.Mesh] = {}
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
        return hsva_to_rgba(self._color)

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

    def shape(
        self, name: str, shapefunc, create_material: bool = True, **kwargs
    ) -> bpy.types.Object:
        meshkey = (name, tuple(sorted(kwargs.items())))
        mesh = self._mesh_cache.get(meshkey)
        if mesh:
            shape = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(shape)
        else:
            shapefunc(**kwargs)
            shape = bpy.context.object
            # Create an empty material slot
            if create_material:
                shape.data.materials.append(None)
            self._mesh_cache[meshkey] = shape.data
        shape.matrix_world = self._matrix
        if create_material:
            material = create_color_material(self.color_rgba)
            # Link the material to the new object, not the shared mesh data
            shape.material_slots[0].link = "OBJECT"
            shape.material_slots[0].material = material
        return shape

    def torus(
        self,
        major_radius: float = 1.0,
        minor_radius: float = 0.25,
        create_material: bool = True,
    ) -> bpy.types.Object:
        return self.shape(
            "Torus",
            bpy.ops.mesh.primitive_torus_add,
            major_radius=major_radius,
            minor_radius=minor_radius,
            create_material=create_material,
        )

    def plane(self, size: float = 2.0, create_material: bool = True):
        return self.shape(
            "Plane",
            bpy.ops.mesh.primitive_plane_add,
            size=size,
            create_material=create_material,
        )

    def icosphere(
        self, radius: float = 1.0, subdivisions: int = 2, create_material: bool = True
    ) -> bpy.types.Object:
        return self.shape(
            "IcoSphere",
            bpy.ops.mesh.primitive_ico_sphere_add,
            radius=radius,
            subdivisions=subdivisions,
            create_material=create_material,
        )

    def uvsphere(
        self,
        radius: float = 1.0,
        segments: int = 32,
        ring_count: int = 16,
        create_material: bool = True,
    ) -> bpy.types.Object:
        return self.shape(
            "UVSphere",
            bpy.ops.mesh.primitive_uv_sphere_add,
            radius=radius,
            segments=segments,
            ring_count=ring_count,
            create_material=create_material,
        )

    def grid(self, size: float = 2.0, create_material: bool = True):
        return self.shape(
            "Grid",
            bpy.ops.mesh.primitive_grid_add,
            size=size,
            create_material=create_material,
        )

    def cylinder(
        self, radius: float = 1.0, depth: float = 2.0, create_material: bool = True
    ) -> bpy.types.Object:
        return self.shape(
            "Cylinder",
            bpy.ops.mesh.primitive_cylinder_add,
            radius=radius,
            depth=depth,
            create_material=create_material,
        )

    def cone(
        self,
        radius1: float = 1.0,
        radius2: float = 0.0,
        depth: float = 2.0,
        create_material: bool = True,
    ) -> bpy.types.Object:
        return self.shape(
            "Cone",
            bpy.ops.mesh.primitive_cone_add,
            radius1=radius1,
            radius2=radius2,
            depth=depth,
            create_material=create_material,
        )

    def circle(
        self,
        radius: float = 1.0,
        fill_type: str = "NOTHING",
        create_material: bool = True,
    ) -> bpy.types.Object:
        return self.shape(
            "Circle",
            bpy.ops.mesh.primitive_circle_add,
            radius=radius,
            fill_type=fill_type,
            create_material=create_material,
        )

    def cube(
        self, size: tuple[float, float, float] = (1, 1, 1), create_material: bool = True
    ) -> bpy.types.Object:
        # scale is baked into the vertices, (1,1,1) is a 2x2x2 cube
        return self.shape(
            "Cube",
            bpy.ops.mesh.primitive_cube_add,
            scale=tuple(s * 0.5 for s in size),
            create_material=create_material,
        )
