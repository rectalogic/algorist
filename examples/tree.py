import logging
from math import pi, radians

import bpy
from mathutils import Matrix

from algorist import MeshFactory, Transform, limit, prnd, rnd, rule

log = logging.getLogger(__name__)

xfm = Transform()
mf = MeshFactory()


@rule()
def grow():
    with xfm.rotate(axis="X", angle=radians(5 + prnd(30))):
        branch()


@rule()  # type: ignore[no-redef]
def grow():  # noqa: F811
    with xfm.rotate(axis="X", angle=radians(-5 + -prnd(30))):
        branch()


@rule()  # type: ignore[no-redef]
def grow():  # noqa: F811
    with xfm.rotate(axis="Y", angle=radians(5 + prnd(30))):
        branch()


@rule()  # type: ignore[no-redef]
def grow():  # noqa: F811
    with xfm.rotate(axis="Y", angle=radians(-5 + -prnd(30))):
        branch()


@limit()
def branch():
    xfm.apply(mf.cylinder(radius=0.1, depth=1))
    with xfm.translate(z=0.7), xfm.scale(xyz=0.7 + rnd(0.15)), xfm.color(
        value=0.8
    ), xfm.rotate(axis="Z", angle=2 * pi):
        grow()
        grow()


with xfm.scale(x=3, y=3, z=3), xfm.color(color=(0, 1, 1, 1)):
    branch()


with xfm.color(color=(0, 0, 1, 1)):
    xfm.apply(mf.plane(size=100))

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
