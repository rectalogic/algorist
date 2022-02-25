from __future__ import annotations

import bpy


class MeshFactory:
    def __init__(self):
        self._mesh_cache: dict[tuple[str, tuple], bpy.types.Mesh] = {}

    def shape(self, name: str, shapefunc, **kwargs) -> bpy.types.Object:
        meshkey = (name, tuple(sorted(kwargs.items())))
        mesh = self._mesh_cache.get(meshkey)
        if mesh:
            shape = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(shape)
        else:
            shapefunc(**kwargs)
            shape = bpy.context.object
            self._mesh_cache[meshkey] = shape.data
        return shape

    def torus(
        self,
        major_radius: float = 1.0,
        minor_radius: float = 0.25,
    ) -> bpy.types.Object:
        return self.shape(
            "Torus",
            bpy.ops.mesh.primitive_torus_add,
            major_radius=major_radius,
            minor_radius=minor_radius,
        )

    def plane(self, size: float = 2.0, create_material: bool = True):
        return self.shape(
            "Plane",
            bpy.ops.mesh.primitive_plane_add,
            size=size,
        )

    def icosphere(
        self, radius: float = 1.0, subdivisions: int = 2, create_material: bool = True
    ) -> bpy.types.Object:
        return self.shape(
            "IcoSphere",
            bpy.ops.mesh.primitive_ico_sphere_add,
            radius=radius,
            subdivisions=subdivisions,
        )

    def uvsphere(
        self,
        radius: float = 1.0,
        segments: int = 32,
        ring_count: int = 16,
    ) -> bpy.types.Object:
        return self.shape(
            "UVSphere",
            bpy.ops.mesh.primitive_uv_sphere_add,
            radius=radius,
            segments=segments,
            ring_count=ring_count,
        )

    def grid(self, size: float = 2.0, create_material: bool = True):
        return self.shape(
            "Grid",
            bpy.ops.mesh.primitive_grid_add,
            size=size,
        )

    def cylinder(
        self, radius: float = 1.0, depth: float = 2.0, create_material: bool = True
    ) -> bpy.types.Object:
        return self.shape(
            "Cylinder",
            bpy.ops.mesh.primitive_cylinder_add,
            radius=radius,
            depth=depth,
        )

    def cone(
        self,
        radius1: float = 1.0,
        radius2: float = 0.0,
        depth: float = 2.0,
    ) -> bpy.types.Object:
        return self.shape(
            "Cone",
            bpy.ops.mesh.primitive_cone_add,
            radius1=radius1,
            radius2=radius2,
            depth=depth,
        )

    def circle(
        self,
        radius: float = 1.0,
        fill_type: str = "NOTHING",
    ) -> bpy.types.Object:
        return self.shape(
            "Circle",
            bpy.ops.mesh.primitive_circle_add,
            radius=radius,
            fill_type=fill_type,
        )

    def cube(
        self,
        size: tuple[float, float, float] = (1, 1, 1),
    ) -> bpy.types.Object:
        # scale is baked into the vertices, (1,1,1) is a 2x2x2 cube
        return self.shape(
            "Cube",
            bpy.ops.mesh.primitive_cube_add,
            scale=tuple(s * 0.5 for s in size),
        )
