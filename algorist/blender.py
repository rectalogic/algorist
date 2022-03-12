from __future__ import annotations

import functools
import itertools
import typing as ta

import bpy
from mathutils import Matrix

from .transform import ObjectTransformer, Transformer, hsva_to_rgba

if ta.TYPE_CHECKING:
    from . import Color


def _primitive_wrapper(func: ta.Callable, *args, **kwargs) -> bpy.types.Object:
    func(*args, **kwargs)
    return bpy.context.object


class MeshMaterialTransformer(ObjectTransformer):
    def apply_color(self, color: Color):
        """Create a Principled BSDF Material with Base Color set to RGBA Color"""
        if not self.obj.material_slots:
            self.obj.data.materials.append(None)

        material = bpy.data.materials.new("Color")
        material.use_nodes = True
        material.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = color
        material.diffuse_color = color
        if color[3] < 1:
            material.blend_method = "BLEND"

        # Link the material to the new object, not the shared mesh data
        self.obj.material_slots[0].link = "OBJECT"
        self.obj.material_slots[0].material = material


class GreasePencilMaterialTransformer(Transformer):
    def __init__(
        self, grease_pencil: bpy.types.GreasePencil, stroke: bpy.types.GPencilStroke
    ):
        self.grease_pencil = grease_pencil
        self.stroke = stroke

    def apply_matrix(self, matrix: Matrix):
        for p in self.stroke.points:
            p.co = matrix @ p.co
        self.stroke.line_width = int(self.stroke.line_width * matrix.median_scale)

    def apply_color(self, color: Color):
        material = bpy.data.materials.new("GPColor")
        self.grease_pencil.materials.append(material)
        bpy.data.materials.create_gpencil_data(material)
        material.grease_pencil.color = color
        self.stroke.material_index = len(self.grease_pencil.materials)


class ObjectFactory:
    def __init__(self):
        self._data_cache: dict[tuple[str, tuple], bpy.types.ID] = {}

    def create_mesh(
        self,
        name: str,
        creation_func: ta.Callable,
        transformer_cls: ta.Type[ObjectTransformer] = ObjectTransformer,
        *args,
        **kwargs,
    ) -> ObjectTransformer:
        """Create blender object

        name should be a unique name to use as a cache key for the data object
        creation_func should return a bpy.types.Object or else set
         bpy.context.object to one
        """
        datakey = (
            name,
            tuple(sorted(itertools.chain(args, kwargs.items()))),
        )
        mesh = self._data_cache.get(datakey)
        if mesh:
            obj = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(obj)
        else:
            result = creation_func(*args, **kwargs)
            # Handle bpy.ops.mesh.primitive_* functions
            if isinstance(result, bpy.types.Object):
                obj = result
            else:
                obj = bpy.context.object
            self._data_cache[datakey] = obj.data
        return transformer_cls(obj)

    def line(
        self,
        points: tuple[tuple[float, float, float], ...] = ((0, 0, 0), (0, 0, 1)),
        thickness: ta.Annotated[int, ta.ValueRange(0, 1000)] = 1,
        transformer_cls=GreasePencilMaterialTransformer,
    ) -> bpy.types.GPencilStroke:
        datakey: tuple[str, tuple] = (
            "Line",
            tuple(),
        )
        data = self._data_cache.get(datakey)
        if not data:
            data = bpy.data.grease_pencils.new("Line")
            data.layers.new("Layer").frames.new(0)
            obj = bpy.data.objects.new("Line", data)
            bpy.context.collection.objects.link(obj)
            self._data_cache[datakey] = data
        stroke = data.layers[0].frames[0].strokes.new()
        stroke.line_width = thickness
        stroke.points.add(count=len(points))
        for sp, p in zip(stroke.points, points):
            sp.co = p
        return transformer_cls(data, stroke)

    torus = functools.partialmethod(
        create_mesh,
        "Torus",
        bpy.ops.mesh.primitive_torus_add,
        transformer_cls=MeshMaterialTransformer,
    )
    plane = functools.partialmethod(
        create_mesh,
        "Plane",
        bpy.ops.mesh.primitive_plane_add,
        transformer_cls=MeshMaterialTransformer,
    )
    ico_sphere = functools.partialmethod(
        create_mesh,
        "IcoSphere",
        bpy.ops.mesh.primitive_ico_sphere_add,
        transformer_cls=MeshMaterialTransformer,
    )
    uv_sphere = functools.partialmethod(
        create_mesh,
        "UVSphere",
        bpy.ops.mesh.primitive_uv_sphere_add,
        transformer_cls=MeshMaterialTransformer,
    )
    grid = functools.partialmethod(
        create_mesh,
        "Grid",
        bpy.ops.mesh.primitive_grid_add,
        transformer_cls=MeshMaterialTransformer,
    )
    cylinder = functools.partialmethod(
        create_mesh,
        "Cylinder",
        bpy.ops.mesh.primitive_cylinder_add,
        transformer_cls=MeshMaterialTransformer,
    )
    cone = functools.partialmethod(
        create_mesh,
        "Cone",
        bpy.ops.mesh.primitive_cone_add,
        transformer_cls=MeshMaterialTransformer,
    )
    circle = functools.partialmethod(
        create_mesh,
        "Circle",
        bpy.ops.mesh.primitive_circle_add,
        transformer_cls=MeshMaterialTransformer,
    )
    cube = functools.partialmethod(
        create_mesh,
        "Cube",
        bpy.ops.mesh.primitive_cube_add,
        transformer_cls=MeshMaterialTransformer,
    )


def background(color: Color):
    """Set Blender background color"""
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[
        "Color"
    ].default_value = hsva_to_rgba(color)
