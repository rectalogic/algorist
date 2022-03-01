from __future__ import annotations

import typing as ta
from math import radians

import bpy
from mathutils import Matrix

from algorist import ObjectFactory, ObjectTransformer, Transform, limit

if ta.TYPE_CHECKING:
    from algorist import Color

with bpy.data.libraries.load("examples/glassball.blend", relative=True) as (
    data_from,
    data_to,
):
    data_to.objects = data_from.objects
    data_to.materials = data_from.materials
    data_to.meshes = data_from.meshes

sphere_prototype = bpy.data.objects["Sphere"]


class GlassTransformer(ObjectTransformer):
    def apply_color(self, color: Color):
        material = self.obj.material_slots[0].material.copy()
        self.obj.material_slots[0].material = material
        material.node_tree.nodes["Glass BSDF"].inputs["Color"].default_value = color


def sphere():
    obj = sphere_prototype.copy()
    bpy.context.collection.objects.link(obj)
    return GlassTransformer(obj)


xfm = Transform()
of = ObjectFactory()


@limit()
def pit(level=1):
    with xfm.color(hue=0.1):
        for angle in range(0, 360, int(360 / (level * 3.8))):
            with xfm.rotate(angle=radians(angle), axis="Z"), xfm.translate(x=level):
                xfm.apply(sphere())
        with xfm.translate(z=1.5):
            pit(level + 1)


with xfm.color(color=(0, 0.9, 1, 1)):
    pit()


with xfm.translate(z=-1):
    circle = of.circle(
        radius=100,
        fill_type="NGON",
    )
    xfm.apply(circle)
    node_tree = circle.obj.material_slots[0].material.node_tree
    checker = node_tree.nodes.new("ShaderNodeTexChecker")
    checker.inputs["Scale"].default_value = 25
    checker.inputs["Color1"].default_value = [0.800000, 0.226496, 0.029006, 1.000000]
    node_tree.links.new(
        checker.outputs["Color"],
        node_tree.nodes["Principled BSDF"].inputs["Base Color"],
    )


light = bpy.context.scene.objects["Light"]
light.location = (0, 0, 11)
light.data.energy = 3000
bpy.ops.object.light_add(type="SUN")
bpy.context.object.data.energy = 0.4

bpy.context.scene.camera.matrix_world = Matrix(
    (
        (
            0.6756927967071533,
            -0.4583091735839844,
            0.5774010419845581,
            31.51889991760254,
        ),
        (
            0.7371833324432373,
            0.4200795888900757,
            -0.5292389988899231,
            -28.093042373657227,
        ),
        (
            7.073239203236881e-07,
            0.7832533717155457,
            0.6217026114463806,
            44.53771209716797,
        ),
        (0.0, 0.0, 0.0, 1.0),
    )
)
