from __future__ import annotations

import colorsys
import typing as ta

import bpy

if ta.TYPE_CHECKING:
    ColorComponent = ta.Annotated[float, ta.ValueRange(0.0, 1.0)]
    Color = tuple[ColorComponent, ColorComponent, ColorComponent, ColorComponent]


def create_color_material(color: Color) -> bpy.types.Material:
    material = bpy.data.materials.new("Color")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[
        "Base Color"
    ].default_value = color
    material.diffuse_color = color
    if color[3] < 1:
        material.blend_method = "BLEND"
    return material


def hsva_to_rgba(color: Color) -> Color:
    return (*colorsys.hsv_to_rgb(*color[:3]), color[3])
