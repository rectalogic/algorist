"""
Based on http://structuresynth.sourceforge.net/learn.php
"""

import logging

import bpy
from mathutils import Matrix

from algorist import Context

log = logging.getLogger(__name__)

ctx = Context()
limit = ctx.limit(max_depth=50)


@ctx.rule()
@limit
def rule1():
    # { x 0.9 rz 6 ry 6 s 0.99  sat 0.99  } R1
    with ctx.color(saturation=0.99), ctx.scale(xyz=0.99), ctx.rotate(
        6, "Y"
    ), ctx.rotate(6, "Z"), ctx.translate(x=0.9):
        rule1()
    with ctx.scale(xyz=2):
        ctx.icosphere(radius=0.25)


@ctx.rule()  # type: ignore[no-redef]
@limit
def rule1():
    # { x 0.9 rz -6 ry 6 s 0.99  sat 0.99  } R1
    with ctx.color(saturation=0.99), ctx.scale(xyz=0.99), ctx.rotate(
        6, "Y"
    ), ctx.rotate(-6, "Z"), ctx.translate(x=0.9):
        rule1()
    with ctx.scale(xyz=2):
        ctx.icosphere(radius=0.25)


with ctx.color(color=(0, 1, 1, 1)):
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
