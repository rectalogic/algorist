# flake8: noqa

import logging
import typing as ta

from .blender import MeshMaterialTransformer, ObjectFactory, background
from .decorator import limit, rule
from .random import coinflip, prnd, rnd
from .transform import ObjectTransformer, Transform, Transformer

if ta.TYPE_CHECKING:
    ColorComponent = ta.Annotated[float, ta.ValueRange(0.0, 1.0)]
    Color = tuple[ColorComponent, ColorComponent, ColorComponent, ColorComponent]

logging.basicConfig(level=logging.INFO)
