import logging
from math import pi, radians

import bpy
from mathutils import Matrix

from algorist import ObjectFactory, Transform, limit, prnd, rnd, rule

log = logging.getLogger(__name__)

xfm = Transform()
of = ObjectFactory()


@rule(2)
def grow():
    with xfm.rotate(axis="X", angle=radians(5 + prnd(30))):
        branch()


@rule(2)  # type: ignore[no-redef]
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
    xfm.apply(of.line(thickness=50))
    with xfm.translate(z=1), xfm.scale(xyz=0.7 + rnd(0.15)), xfm.color(
        value=0.8
    ), xfm.rotate(axis="Z", angle=2 * pi):
        grow()
        grow()


with xfm.scale(x=3, y=3, z=3), xfm.color(color=(0, 1, 1, 1)):
    branch()


with xfm.color(color=(0, 0, 1, 1)):
    xfm.apply(of.plane(size=100))

bpy.context.scene.camera.matrix_world = Matrix(
    (
        (
            0.4211483597755432,
            -0.502444326877594,
            0.7551051378250122,
            12.773435592651367,
        ),
        (
            0.9069917798042297,
            0.23329788446426392,
            -0.3506251871585846,
            -5.096395492553711,
        ),
        (
            5.18989054398844e-06,
            0.8325393795967102,
            0.5539658665657043,
            14.000414848327637,
        ),
        (0.0, 0.0, 0.0, 1.0),
    )
)
