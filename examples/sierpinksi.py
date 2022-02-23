from math import radians, sqrt

import bpy
from mathutils import Matrix

from algorist import Context

ctx = Context(background_color=(0.025, 0.862, 0.193, 1))

side = 2
height = side * (sqrt(3) / 2)


@ctx.limit(max_depth=7)
def sierpinksi(depth=0):
    with ctx.color(hue=0.008, saturation=1.3, value=1.2), ctx.scale(xyz=0.5):
        with ctx.translate(x=0, y=-(height - (side / 2)) / 2, z=height):
            sierpinksi(depth + 1)
        with ctx.translate(x=0, y=height - (side / 2), z=0):
            sierpinksi(depth + 1)
        with ctx.translate(x=-side / 2, y=-side / 2, z=-0):
            sierpinksi(depth + 1)
        with ctx.translate(x=side / 2, y=-side / 2, z=0):
            sierpinksi(depth + 1)

    if depth > 4:
        ctx.cone(radius1=side / 2, depth=height)


with ctx.color(color=(0.048, 0.5, 0.3, 1)), ctx.scale(xyz=2):
    sierpinksi()

with ctx.color(color=(0.114, 0.77, 0.8, 1)), ctx.translate(z=-1):
    ctx.circle(radius=100, fill_type="NGON")

bpy.context.scene.camera.matrix_world = Matrix(
    (
        (
            0.6859206557273865,
            -0.32401347160339355,
            0.6515582203865051,
            16.23420524597168,
        ),
        (
            0.7276763319969177,
            0.305420845746994,
            -0.6141703724861145,
            -21.557098388671875,
        ),
        (0.0, 0.8953956365585327, 0.44527140259742737, 12.594623565673828),
        (0.0, 0.0, 0.0, 1.0),
    )
)
