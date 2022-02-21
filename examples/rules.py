"""
Based on http://structuresynth.sourceforge.net/learn.php
"""

import logging

from algorist import Context

log = logging.getLogger(__name__)

ctx = Context()
limit = ctx.limit(max_depth=50)


@ctx.rule()
@limit
def rule1():
    # { x 0.9 rz 6 ry 6 s 0.99  sat 0.99  } R1
    with ctx.translate(x=0.9), ctx.rotate(6, "Z"), ctx.rotate(6, "Y"), ctx.scale(
        xyz=0.99
    ), ctx.color(saturation=0.99):
        rule1()
    with ctx.scale(xyz=2):
        ctx.icosphere(radius=0.25)


@ctx.rule()  # type: ignore[no-redef]
@limit
def rule1():
    # { x 0.9 rz -6 ry 6 s 0.99  sat 0.99  } R1
    with ctx.translate(x=0.9), ctx.rotate(-6, "Z"), ctx.rotate(6, "Y"), ctx.scale(
        xyz=0.99
    ), ctx.color(saturation=0.99):
        rule1()
    with ctx.scale(xyz=2):
        ctx.icosphere(radius=0.25)


with ctx.color(color=(0, 1, 1, 1)):
    rule1()
