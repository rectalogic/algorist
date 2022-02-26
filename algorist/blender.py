from __future__ import annotations

import colorsys
import functools
import itertools
import typing as ta

import bpy

if ta.TYPE_CHECKING:
    ColorComponent = ta.Annotated[float, ta.ValueRange(0.0, 1.0)]
    Color = tuple[ColorComponent, ColorComponent, ColorComponent, ColorComponent]


def _primitive_wrapper(func: ta.Callable, *args, **kwargs) -> bpy.types.Object:
    func(*args, **kwargs)
    return bpy.context.object


class MeshFactory:
    def __init__(self):
        self._mesh_cache: dict[tuple[str, tuple], bpy.types.Mesh] = {}

    def create(
        self,
        name: str,
        creation_func: ta.Callable,
        *args,
        **kwargs,
    ) -> bpy.types.Object:
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
        return obj

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


def create_color_material(color: Color) -> bpy.types.Material:
    """Create a Principled BSDF Material with Base Color set to RGBA Color"""
    material = bpy.data.materials.new("Color")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[
        "Base Color"
    ].default_value = color
    material.diffuse_color = color
    if color[3] < 1:
        material.blend_method = "BLEND"
    return material


def hsva_to_rgba(color: Color) -> Color:
    """Convert color from HSVA to RGBA"""
    return (*colorsys.hsv_to_rgb(*color[:3]), color[3])


def background(color: Color):
    """Set Blender background color"""
    bpy.context.scene.world.node_tree.nodes["Background"].inputs[
        "Color"
    ].default_value = hsva_to_rgba(color)
