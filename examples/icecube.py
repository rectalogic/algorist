from __future__ import annotations

import typing as ta

import bpy
from mathutils import Matrix

from algorist import (
    MeshMaterialTransformer,
    ObjectFactory,
    Transform,
    coinflip,
    limit,
    prnd,
)

if ta.TYPE_CHECKING:
    from algorist import Color

# background((0.025, 0.862, 0.193, 1))

xfm = Transform()
of = ObjectFactory()


class IceTransformer(MeshMaterialTransformer):
    def apply_color(self, color: Color):
        super().apply_color(color)
        node_tree = self.obj.material_slots[0].material.node_tree
        glass_node = node_tree.nodes.new("ShaderNodeBsdfGlass")
        output = node_tree.nodes.get("Material Output")
        node_tree.links.new(output.inputs["Surface"], glass_node.outputs["BSDF"])


def glasscube():
    if coinflip(4):
        with xfm.scale(xyz=prnd(0.7) + 0.3):
            xfm.apply(of.cube(size=1, transformer_cls=IceTransformer))


@limit(max_depth=14)
def column():
    with xfm.translate(y=1):
        column()
        glasscube()


@limit(max_depth=14)
def row():
    with xfm.translate(x=1):
        column()
        row()


@limit(max_depth=14)
def cube():
    with xfm.translate(z=1):
        row()
        cube()


cube()

bpy.data.objects.remove(bpy.data.objects["Light"])
bpy.ops.object.light_add(type="SUN")
sun = bpy.context.object
sun.data.energy = 0.4
sun.data.angle = 0.003491
sun.matrix_world = Matrix(
    (
        (0.7651504874229431, -0.4111352562904358, -0.49549219012260437, 0.0),
        (0.19498077034950256, 0.8814009428024292, -0.43024975061416626, 0.0),
        (0.6136181354522705, 0.2325943559408188, 0.7545678615570068, 15.0),
        (0.0, 0.0, 0.0, 1.0),
    )
)

with xfm.color(
    color=(0.5924139022827148, 0.9358978867530823, 0.2919842302799225, 1)
), xfm.translate(z=-1):
    xfm.apply(of.circle(radius=100, fill_type="NGON"))

bpy.context.scene.camera.matrix_world = Matrix(
    (
        (
            0.6334812045097351,
            -0.24474962055683136,
            0.7340294122695923,
            39.14384460449219,
        ),
        (
            0.773758053779602,
            0.20037397742271423,
            -0.6009564995765686,
            -23.72161293029785,
        ),
        (
            3.478045528026996e-06,
            0.9486558437347412,
            0.3163101375102997,
            20.467344284057617,
        ),
        (0.0, 0.0, 0.0, 1.0),
    )
)
