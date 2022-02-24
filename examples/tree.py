import logging
from math import radians

import bpy
from mathutils import Matrix

from algorist import Context, prnd, rnd

log = logging.getLogger(__name__)

ctx = Context()


@ctx.limit()
def branch():
    ctx.cylinder(radius=0.1, depth=1)
    with ctx.translate(z=0.7), ctx.scale(xyz=0.7 + rnd(0.15)), ctx.color(value=0.8):
        with ctx.rotate(axis="X", angle=radians(5 + prnd(30))):
            branch()
        with ctx.rotate(axis="X", angle=radians(-5 - prnd(30))):
            branch()


with ctx.scale(x=3, y=3, z=3), ctx.color(color=(0, 1, 1, 1)):
    branch()
    with ctx.rotate(axis="Z", angle=radians(90)):
        branch()

with ctx.color(color=(0, 0, 1, 1)):
    ctx.plane(size=100)

bpy.context.scene.camera.matrix_world = Matrix(
    (
        (
            0.6859205961227417,
            -0.32401344180107117,
            0.6515582799911499,
            9.91963005065918,
        ),
        (
            0.7276763916015625,
            0.30542072653770447,
            -0.6141703724861145,
            -9.201038360595703,
        ),
        (
            4.6507988571420356e-08,
            0.8953956961631775,
            0.4452713131904602,
            10.667835235595703,
        ),
        (0.0, 0.0, 0.0, 1.0),
    )
)