from math import radians, sqrt

import bpy
from mathutils import Matrix

from algorist import Context

ctx = Context(background_color=(0.025, 0.862, 0.193, 1))

side = 2


def shape():
    # Cone pivot/center point is wrong, so transform the mesh
    obj = ctx.cone(radius1=side / 2, depth=side * (sqrt(3) / 2))
    matrix_world = obj.matrix_world.copy()
    obj.matrix_world = Matrix.Identity(4)
    obj.data.transform(Matrix.Translation((0, 0, 0.29)))
    obj.matrix_world = matrix_world


def cone():
    with ctx.translate(y=-side), ctx.scale(xyz=0.5):
        sierpinksi()


@ctx.limit(min_scale=0.009)
def sierpinksi():
    shape()

    with ctx.color(hue=0.008, saturation=1.3, value=1.2):
        with ctx.rotate(angle=radians(120), axis="X"):
            cone()
            with ctx.rotate(angle=radians(120), axis="X"):
                cone()
                with ctx.rotate(angle=radians(120), axis="X"):
                    cone()


with ctx.color(color=(0.048, 0.5, 0.3, 1)), ctx.scale(xyz=2), ctx.rotate(
    radians(60), axis="X"
):
    sierpinksi()

with ctx.color(color=(0.114, 0.77, 0.8, 1)), ctx.translate(z=-7):
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
