import colorsys

import bpy


def create_color_material(
    color: tuple[float, float, float, float]
) -> bpy.types.Material:
    material = bpy.data.materials.new("Color")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[
        "Base Color"
    ].default_value = color
    material.diffuse_color = color
    if color[3] < 1:
        material.blend_method = "BLEND"
    return material


def hsva_to_rgba(
    color: tuple[float, float, float, float]
) -> tuple[float, float, float, float]:
    return (*colorsys.hsv_to_rgb(*color[:3]), color[3])
