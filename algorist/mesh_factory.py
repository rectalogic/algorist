from __future__ import annotations

import itertools
import typing as ta

import bpy


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

    def ops_primitive(self, primitive_func, *args, **kwargs) -> bpy.types.Object:
        """Create a blender ops primitive

        primitive_func should be one of:
          bpy.ops.mesh.primitive_torus_add
          bpy.ops.mesh.primitive_plane_add
          bpy.ops.mesh.primitive_ico_sphere_add
          bpy.ops.mesh.primitive_uv_sphere_add
          bpy.ops.mesh.primitive_grid_add
          bpy.ops.mesh.primitive_cylinder_add
          bpy.ops.mesh.primitive_cone_add
          bpy.ops.mesh.primitive_circle_add
          bpy.ops.mesh.primitive_cube_add
        """
        return self.create(primitive_func.idname(), primitive_func, *args, **kwargs)
