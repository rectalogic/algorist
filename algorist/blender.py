from __future__ import annotations

import functools
import itertools
import typing as ta

import bpy

from .transform import Transformer, hsva_to_rgba

if ta.TYPE_CHECKING:
    from . import Color


def _primitive_wrapper(func: ta.Callable, *args, **kwargs) -> bpy.types.Object:
    func(*args, **kwargs)
    return bpy.context.object


class ColorMaterialTransformer(Transformer):
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


class MeshFactory:
    def __init__(
        self, transformer_cls: ta.Type[Transformer] = ColorMaterialTransformer
    ):
        self._mesh_cache: dict[tuple[str, tuple], bpy.types.Mesh] = {}
        self.transformer_cls = transformer_cls

    def create(
        self,
        name: str,
        creation_func: ta.Callable,
        *args,
        **kwargs,
    ) -> Transformer:
        """Create blender mesh object

        name should be a unique name to use as a cache key for this mesh
        creation_func should return a bpy.types.Object or else set
         bpy.context.object to one
        """
        meshkey = (
            name,
            tuple(sorted(itertools.chain(args, kwargs.items()))),
        )
        mesh = self._mesh_cache.get(meshkey)
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
            self._mesh_cache[meshkey] = obj.data
        return self.transformer_cls(obj)

    torus = functools.partialmethod(create, "Torus", bpy.ops.mesh.primitive_torus_add)
    plane = functools.partialmethod(create, "Plane", bpy.ops.mesh.primitive_plane_add)
    ico_sphere = functools.partialmethod(
        create, "IcoSphere", bpy.ops.mesh.primitive_ico_sphere_add
    )
    uv_sphere = functools.partialmethod(
        create, "UVSphere", bpy.ops.mesh.primitive_uv_sphere_add
    )
    grid = functools.partialmethod(create, "Grid", bpy.ops.mesh.primitive_grid_add)
    cylinder = functools.partialmethod(
        create, "Cylinder", bpy.ops.mesh.primitive_cylinder_add
    )
    cone = functools.partialmethod(create, "Cone", bpy.ops.mesh.primitive_cone_add)
    circle = functools.partialmethod(
        create, "Circle", bpy.ops.mesh.primitive_circle_add
    )
    cube = functools.partialmethod(create, "Cube", bpy.ops.mesh.primitive_cube_add)


def background(color: Color):
    """Set Blender background color"""
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[
        "Color"
    ].default_value = hsva_to_rgba(color)
