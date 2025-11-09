# ##### BEGIN GPL LICENSE BLOCK #####
#
#  HyperGradeFX - Multi-Dimensional Post-Production Suite for Blender
#  Copyright (C) 2025  DEADSERPENT
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

"""
HyperGradeFX - Multi-Dimensional Post-Production Suite for Blender
Professional-grade compositing and post-production tools

This is a Blender Extension (4.2+). All metadata is in blender_manifest.toml
For legacy add-ons, this bl_info has been removed.
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty

# Import modules
from . import core
from . import ui
from . import utils

# Module list for registration
modules = [
    core,
    ui,
    utils,
]


class HyperGradeFXPreferences(AddonPreferences):
    bl_idname = __package__

    preset_directory: StringProperty(
        name="Preset Directory",
        description="Directory for storing HyperGradeFX presets (leave empty to use addon directory)",
        default="",
        subtype='DIR_PATH'
    )

    ffmpeg_path: StringProperty(
        name="FFmpeg Path",
        description="Path to FFmpeg executable",
        default="ffmpeg",
        subtype='FILE_PATH'
    )

    enable_live_preview: BoolProperty(
        name="Enable Live Preview",
        description="Enable live compositor preview (may impact performance)",
        default=True
    )

    auto_connect_passes: BoolProperty(
        name="Auto-Connect Render Passes",
        description="Automatically connect render passes when detected",
        default=True
    )

    color_space: EnumProperty(
        name="Color Space",
        description="Default color space for operations",
        items=[
            ('SRGB', 'sRGB', 'Standard RGB color space'),
            ('LINEAR', 'Linear', 'Linear color space'),
            ('ACES', 'ACES', 'ACES color space'),
            ('FILMIC', 'Filmic', 'Filmic color space'),
        ],
        default='LINEAR'
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Paths", icon='FILE_FOLDER')
        box.prop(self, "preset_directory")
        box.prop(self, "ffmpeg_path")

        box = layout.box()
        box.label(text="Performance", icon='SETTINGS')
        box.prop(self, "enable_live_preview")

        box = layout.box()
        box.label(text="Automation", icon='AUTO')
        box.prop(self, "auto_connect_passes")

        box = layout.box()
        box.label(text="Color Management", icon='COLOR')
        box.prop(self, "color_space")


# Scene properties
class HyperGradeFXSceneProperties(bpy.types.PropertyGroup):
    sequence_mode: BoolProperty(
        name="Sequence Mode",
        description="Enable sequence-based compositing",
        default=False
    )

    current_sequence: StringProperty(
        name="Current Sequence",
        description="Name of the current sequence",
        default=""
    )

    fog_enabled: BoolProperty(
        name="Enable Post-Fog",
        description="Enable 3D post-fog effects",
        default=False
    )

    fog_density: bpy.props.FloatProperty(
        name="Fog Density",
        description="Density of the post-fog effect",
        default=0.5,
        min=0.0,
        max=1.0
    )

    fog_start: bpy.props.FloatProperty(
        name="Fog Start",
        description="Distance where fog starts",
        default=5.0,
        min=0.0
    )

    fog_end: bpy.props.FloatProperty(
        name="Fog End",
        description="Distance where fog reaches maximum density",
        default=25.0,
        min=0.0
    )

    fog_color: bpy.props.FloatVectorProperty(
        name="Fog Color",
        description="Color of the fog",
        subtype='COLOR',
        default=(0.5, 0.5, 0.6, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )

    edge_detection_enabled: BoolProperty(
        name="Edge Detection",
        description="Enable edge-aware color isolation",
        default=False
    )

    edge_threshold: bpy.props.FloatProperty(
        name="Edge Threshold",
        description="Threshold for edge detection",
        default=0.1,
        min=0.0,
        max=1.0
    )

    color_harmony_mode: EnumProperty(
        name="Color Harmony Mode",
        description="Color harmony adjustment mode",
        items=[
            ('NONE', 'None', 'No harmony adjustment'),
            ('COMPLEMENTARY', 'Complementary', 'Complementary color harmony'),
            ('ANALOGOUS', 'Analogous', 'Analogous color harmony'),
            ('SPLIT_COMPLEMENTARY', 'Split-Complementary', 'Split-complementary harmony'),
            ('TRIADIC', 'Triadic', 'Triadic color harmony'),
        ],
        default='NONE'
    )

    harmony_strength: bpy.props.FloatProperty(
        name="Harmony Strength",
        description="Strength of color harmony effect",
        default=0.5,
        min=0.0,
        max=1.0
    )

    safe_area_enabled: BoolProperty(
        name="Show Safe Areas",
        description="Display safe area guides",
        default=False
    )

    safe_area_type: EnumProperty(
        name="Safe Area Type",
        description="Type of safe area to display",
        items=[
            ('ACTION', 'Action Safe', 'Action safe area (90%)'),
            ('TITLE', 'Title Safe', 'Title safe area (80%)'),
            ('CUSTOM', 'Custom', 'Custom safe area'),
        ],
        default='ACTION'
    )


# Registration
classes = (
    HyperGradeFXPreferences,
    HyperGradeFXSceneProperties,
)


def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register modules
    for module in modules:
        if hasattr(module, 'register'):
            module.register()

    # Add scene properties
    bpy.types.Scene.hypergradefx = bpy.props.PointerProperty(type=HyperGradeFXSceneProperties)

    print("HyperGradeFX v1.0.0 loaded successfully")


def unregister():
    # Remove scene properties
    del bpy.types.Scene.hypergradefx

    # Unregister modules
    for module in reversed(modules):
        if hasattr(module, 'unregister'):
            module.unregister()

    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    print("HyperGradeFX unloaded")


if __name__ == "__main__":
    register()
