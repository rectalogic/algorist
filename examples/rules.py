"""
Based on http://structuresynth.sourceforge.net/learn.php
"""

import logging

import bpy
from mathutils import Matrix

from algorist import ObjectFactory, Transform, limit, rule

log = logging.getLogger(__name__)

limitdepth = limit(max_depth=50)
xfm = Transform()
of = ObjectFactory()


@rule()
@limitdepth
def rule1():
    # { x 0.9 rz 6 ry 6 s 0.99  sat 0.99  } R1
    with xfm.color(saturation=0.99), xfm.scale(xyz=0.99), xfm.rotate(
        6, "Y"
    ), xfm.rotate(6, "Z"), xfm.translate(x=0.9):
        rule1()
    with xfm.scale(xyz=2):
        xfm.apply(of.ico_sphere(radius=0.25))


@rule()  # type: ignore[no-redef]
@limitdepth
def rule1():  # noqa: F811
    # { x 0.9 rz -6 ry 6 s 0.99  sat 0.99  } R1
    with xfm.color(saturation=0.99), xfm.scale(xyz=0.99), xfm.rotate(
        6, "Y"
    ), xfm.rotate(-6, "Z"), xfm.translate(x=0.9):
        rule1()
    with xfm.scale(xyz=2):
        xfm.apply(of.ico_sphere(radius=0.25))


with xfm.color(color=(0, 1, 1, 1)):
    rule1()


bpy.context.scene.camera.matrix_world = Matrix(
    (
        (0.5779627561569214, -0.5464786887168884, 0.6060693860054016, 11.4134521484375),
        (
            0.8160631656646729,
            0.3870314955711365,
            -0.4292406737804413,
            -7.15428352355957,
        ),
        (
            2.9313766845007194e-06,
            0.7426760196685791,
            0.6696509122848511,
            15.054122924804688,
        ),
        (0.0, 0.0, 0.0, 1.0),
    )
)
