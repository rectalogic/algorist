from math import sqrt

import bpy
from mathutils import Matrix

from algorist import Context

ctx = Context(background_color=(0.025, 0.862, 0.193, 1))
xfm = ctx.transform

side = 2
height = side * (sqrt(3) / 2)


@ctx.limit(max_depth=7)
def sierpinksi(depth=0):
    with xfm.color(hue=0.008, saturation=1.3, value=1.2), xfm.scale(xyz=0.5):
        with xfm.translate(x=0, y=-(height - (side / 2)) / 2, z=height):
            sierpinksi(depth + 1)
        with xfm.translate(x=0, y=height - (side / 2), z=0):
            sierpinksi(depth + 1)
        with xfm.translate(x=-side / 2, y=-side / 2, z=-0):
            sierpinksi(depth + 1)
        with xfm.translate(x=side / 2, y=-side / 2, z=0):
            sierpinksi(depth + 1)

    if depth > 4:
        xfm.apply(
            ctx.mesh.ops_primitive(
                bpy.ops.mesh.primitive_cone_add, radius1=side / 2, depth=height
            )
        )


with xfm.color(color=(0.048, 0.5, 0.3, 1)), xfm.scale(xyz=2):
    sierpinksi()

with xfm.color(color=(0.114, 0.77, 0.8, 1)), xfm.translate(z=-1):
    xfm.apply(
        ctx.mesh.ops_primitive(
            bpy.ops.mesh.primitive_circle_add, radius=100, fill_type="NGON"
        )
    )

bpy.context.scene.camera.matrix_world = Matrix(
    (
        (
            0.343774676322937,
            -0.36449429392814636,
            0.8654264211654663,
            10.366129875183105,
        ),
        (
            0.939052164554596,
            0.13343019783496857,
            -0.31682395935058594,
            -7.059553623199463,
        ),
        (
            6.496500645880587e-06,
            0.9215965867042542,
            0.38814908266067505,
            5.887676239013672,
        ),
        (0.0, 0.0, 0.0, 1.0),
    )
)
