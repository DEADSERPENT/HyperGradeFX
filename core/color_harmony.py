"""
Dynamic Color Harmony Engine
Real-time color harmony adjustments for artistic color grading
"""

import bpy
from bpy.types import Operator
import colorsys
from ..utils.helpers import (get_compositor_node_tree, create_node, connect_nodes,
                             calculate_color_harmony, mix_colors, create_color_ramp,
                             setup_realtime_preview)
from ..utils.constants import COLOR_HARMONY_ANGLES


class HGFX_OT_ApplyColorHarmony(Operator):
    """Apply color harmony adjustments to the compositor"""
    bl_idname = "hgfx.apply_color_harmony"
    bl_label = "Apply Color Harmony"
    bl_options = {'REGISTER', 'UNDO'}

    mode: bpy.props.EnumProperty(
        name="Harmony Mode",
        items=[
            ('COMPLEMENTARY', 'Complementary', 'Opposite colors on color wheel'),
            ('ANALOGOUS', 'Analogous', 'Adjacent colors on color wheel'),
            ('SPLIT_COMPLEMENTARY', 'Split-Complementary', 'Base + two colors adjacent to complement'),
            ('TRIADIC', 'Triadic', 'Three colors equally spaced on color wheel'),
        ],
        default='COMPLEMENTARY'
    )

    base_color: bpy.props.FloatVectorProperty(
        name="Base Color",
        subtype='COLOR',
        default=(0.8, 0.4, 0.2),
        min=0.0,
        max=1.0,
        size=3
    )

    strength: bpy.props.FloatProperty(
        name="Strength",
        description="Strength of color harmony effect",
        default=0.5,
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        # Calculate harmony colors
        harmony_colors = calculate_color_harmony(self.base_color, self.mode)

        # Create color harmony node setup
        final_node = self.create_harmony_setup(node_tree, self.base_color, harmony_colors, self.strength)

        # Setup real-time preview
        if final_node:
            setup_realtime_preview(context, node_tree, final_node)

        self.report({'INFO'}, f"Applied {self.mode} color harmony - Check backdrop for preview!")
        return {'FINISHED'}

    def create_harmony_setup(self, node_tree, base_color, harmony_colors, strength):
        """Create node setup for color harmony"""

        x_start = 400
        y_start = 0
        x_spacing = 250

        # Find the render layers or viewer input
        input_node = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                input_node = node
                break

        if not input_node:
            self.report({'WARNING'}, "No input node found")
            return

        # Create color balance nodes for each harmony color
        color_nodes = []

        for i, harmony_color in enumerate(harmony_colors):
            x = x_start + (i * x_spacing)
            y = y_start - (i * 200)

            # Create RGB curves for selective color adjustment
            rgb_curves = create_node(
                node_tree,
                'CompositorNodeCurveRGB',
                location=(x, y),
                label=f"Harmony Color {i+1}"
            )

            # Adjust the curve based on harmony color
            # This is a simplified version - in production you'd want more sophisticated curve adjustment
            color_nodes.append(rgb_curves)

        # Create color balance node
        color_balance = create_node(
            node_tree,
            'CompositorNodeColorBalance',
            location=(x_start, y_start),
            label="Color Harmony Balance"
        )

        # Apply base color to color balance
        color_balance.lift = base_color
        color_balance.gamma = harmony_colors[0] if harmony_colors else (0.5, 0.5, 0.5)

        # Create mix node to blend harmony effect
        mix_node = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x_start + x_spacing * 2, y_start),
            label="Harmony Mix"
        )
        mix_node.blend_type = 'MIX'
        mix_node.inputs[0].default_value = strength

        # Connect nodes
        if input_node:
            connect_nodes(node_tree, input_node, 'Image', color_balance, 'Image')
            connect_nodes(node_tree, input_node, 'Image', mix_node, 1)
            connect_nodes(node_tree, color_balance, 'Image', mix_node, 2)

        # Return the final mix node for preview setup
        return mix_node

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateSplitToneEffect(Operator):
    """Create split toning effect (different colors for shadows and highlights)"""
    bl_idname = "hgfx.create_split_tone"
    bl_label = "Create Split Tone Effect"
    bl_options = {'REGISTER', 'UNDO'}

    shadow_color: bpy.props.FloatVectorProperty(
        name="Shadow Color",
        subtype='COLOR',
        default=(0.2, 0.3, 0.5),
        min=0.0,
        max=1.0,
        size=3
    )

    highlight_color: bpy.props.FloatVectorProperty(
        name="Highlight Color",
        subtype='COLOR',
        default=(0.9, 0.7, 0.4),
        min=0.0,
        max=1.0,
        size=3
    )

    balance: bpy.props.FloatProperty(
        name="Balance",
        description="Balance between shadows and highlights",
        default=0.5,
        min=0.0,
        max=1.0
    )

    strength: bpy.props.FloatProperty(
        name="Strength",
        description="Overall effect strength",
        default=0.5,
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        final_node = self.create_split_tone_setup(
            node_tree,
            self.shadow_color,
            self.highlight_color,
            self.balance,
            self.strength
        )

        # Setup real-time preview
        if final_node:
            setup_realtime_preview(context, node_tree, final_node)

        self.report({'INFO'}, "Created split tone effect - Check backdrop for preview!")
        return {'FINISHED'}

    def create_split_tone_setup(self, node_tree, shadow_color, highlight_color,
                                balance, strength):
        """Create split toning node setup"""

        x = 400
        y = 0

        # Find input
        input_node = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                input_node = node
                break

        if not input_node:
            return

        # Create RGB to BW node to get luminance mask
        rgb_to_bw = create_node(
            node_tree,
            'CompositorNodeRGBToBW',
            location=(x, y + 200),
            label="Luminance"
        )
        connect_nodes(node_tree, input_node, 'Image', rgb_to_bw, 'Image')

        # Create color ramp to control shadow/highlight split
        color_ramp = create_node(
            node_tree,
            'CompositorNodeValToRGB',
            location=(x + 200, y + 200),
            label="Split Control"
        )

        # Adjust color ramp position based on balance
        color_ramp.color_ramp.elements[0].position = balance - 0.2
        color_ramp.color_ramp.elements[1].position = balance + 0.2

        connect_nodes(node_tree, rgb_to_bw, 'Val', color_ramp, 'Fac')

        # Create shadow color node
        shadow_rgb = create_node(
            node_tree,
            'CompositorNodeRGB',
            location=(x, y - 100),
            label="Shadow Tone"
        )
        shadow_rgb.outputs[0].default_value = (*shadow_color, 1.0)

        # Create highlight color node
        highlight_rgb = create_node(
            node_tree,
            'CompositorNodeRGB',
            location=(x, y - 300),
            label="Highlight Tone"
        )
        highlight_rgb.outputs[0].default_value = (*highlight_color, 1.0)

        # Mix shadow and highlight based on mask
        tone_mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 400, y),
            label="Tone Mix"
        )
        tone_mix.blend_type = 'MIX'

        connect_nodes(node_tree, color_ramp, 'Image', tone_mix, 'Fac')
        connect_nodes(node_tree, shadow_rgb, 'RGBA', tone_mix, 1)
        connect_nodes(node_tree, highlight_rgb, 'RGBA', tone_mix, 2)

        # Blend with original using Overlay or Soft Light
        final_mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 600, y),
            label="Apply Split Tone"
        )
        final_mix.blend_type = 'OVERLAY'
        final_mix.inputs[0].default_value = strength

        connect_nodes(node_tree, input_node, 'Image', final_mix, 1)
        connect_nodes(node_tree, tone_mix, 'Image', final_mix, 2)

        # Return final node for preview setup
        return final_mix

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateColorGradeStack(Operator):
    """Create a complete color grading stack"""
    bl_idname = "hgfx.create_color_grade_stack"
    bl_label = "Create Color Grade Stack"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        final_node = self.create_grade_stack(node_tree, context)

        # Setup real-time preview
        if final_node:
            setup_realtime_preview(context, node_tree, final_node)

        self.report({'INFO'}, "Created color grading stack - Check backdrop for preview!")
        return {'FINISHED'}

    def create_grade_stack(self, node_tree, context):
        """Create a professional color grading stack"""

        x_start = 400
        y = 0
        x_spacing = 250

        # Find input
        input_node = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                input_node = node
                break

        if not input_node:
            return None

        current_x = x_start
        current_input = input_node
        current_socket = 'Image'

        # 1. Exposure
        exposure = create_node(
            node_tree,
            'CompositorNodeExposure',
            location=(current_x, y),
            label="1. Exposure"
        )
        connect_nodes(node_tree, current_input, current_socket, exposure, 'Image')
        current_input = exposure
        current_socket = 'Image'
        current_x += x_spacing

        # 2. White Balance
        white_balance = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(current_x, y),
            label="2. White Balance"
        )
        white_balance.blend_type = 'ADD'
        white_balance.inputs[0].default_value = 0.0
        connect_nodes(node_tree, current_input, current_socket, white_balance, 1)
        current_input = white_balance
        current_socket = 'Image'
        current_x += x_spacing

        # 3. Contrast
        contrast = create_node(
            node_tree,
            'CompositorNodeBrightContrast',
            location=(current_x, y),
            label="3. Contrast"
        )
        connect_nodes(node_tree, current_input, current_socket, contrast, 'Image')
        current_input = contrast
        current_socket = 'Image'
        current_x += x_spacing

        # 4. Saturation
        saturation = create_node(
            node_tree,
            'CompositorNodeHueSat',
            location=(current_x, y),
            label="4. Saturation"
        )
        connect_nodes(node_tree, current_input, current_socket, saturation, 'Image')
        current_input = saturation
        current_socket = 'Image'
        current_x += x_spacing

        # 5. Color Correction (Lift/Gamma/Gain)
        color_correction = create_node(
            node_tree,
            'CompositorNodeColorCorrection',
            location=(current_x, y),
            label="5. Color Wheels"
        )
        connect_nodes(node_tree, current_input, current_socket, color_correction, 'Image')
        current_input = color_correction
        current_socket = 'Image'
        current_x += x_spacing

        # 6. RGB Curves
        curves = create_node(
            node_tree,
            'CompositorNodeCurveRGB',
            location=(current_x, y),
            label="6. Curves"
        )
        connect_nodes(node_tree, current_input, current_socket, curves, 'Image')
        current_input = curves
        current_socket = 'Image'
        current_x += x_spacing

        # 7. Final Adjustment
        final_hue_sat = create_node(
            node_tree,
            'CompositorNodeHueSat',
            location=(current_x, y),
            label="7. Final Adjust"
        )
        connect_nodes(node_tree, current_input, current_socket, final_hue_sat, 'Image')

        # Return final node for preview setup
        return final_hue_sat


class HGFX_OT_ApplyLookPreset(Operator):
    """Apply a color grading look preset"""
    bl_idname = "hgfx.apply_look_preset"
    bl_label = "Apply Look Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset: bpy.props.EnumProperty(
        name="Preset",
        items=[
            ('CINEMATIC_WARM', 'Cinematic Warm', 'Warm cinematic look'),
            ('CINEMATIC_COOL', 'Cinematic Cool', 'Cool cinematic look'),
            ('VIBRANT', 'Vibrant', 'Saturated vibrant colors'),
            ('DESATURATED', 'Desaturated', 'Muted desaturated look'),
            ('VINTAGE', 'Vintage', 'Vintage film look'),
            ('NOIR', 'Film Noir', 'High contrast black and white'),
        ],
        default='CINEMATIC_WARM'
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.apply_preset(node_tree, self.preset)

        self.report({'INFO'}, f"Applied {self.preset} look")
        return {'FINISHED'}

    def apply_preset(self, node_tree, preset):
        """Apply preset values to color grading nodes"""

        # Find or create color correction node
        color_correction = None
        for node in node_tree.nodes:
            if node.type == 'COLORCORRECTION' and node.label == "Look Preset":
                color_correction = node
                break

        if not color_correction:
            color_correction = create_node(
                node_tree,
                'CompositorNodeColorCorrection',
                location=(600, 0),
                label="Look Preset"
            )

        # Apply preset values
        if preset == 'CINEMATIC_WARM':
            color_correction.lift = (1.0, 0.95, 0.9)
            color_correction.gamma = (1.0, 0.98, 0.95)
            color_correction.gain = (1.05, 1.0, 0.95)

        elif preset == 'CINEMATIC_COOL':
            color_correction.lift = (0.9, 0.95, 1.0)
            color_correction.gamma = (0.95, 0.98, 1.0)
            color_correction.gain = (0.95, 1.0, 1.05)

        elif preset == 'VIBRANT':
            # Create or find saturation node
            saturation = create_node(
                node_tree,
                'CompositorNodeHueSat',
                location=(400, 0),
                label="Vibrant Sat"
            )
            saturation.inputs['Saturation'].default_value = 1.3

        elif preset == 'DESATURATED':
            saturation = create_node(
                node_tree,
                'CompositorNodeHueSat',
                location=(400, 0),
                label="Desat"
            )
            saturation.inputs['Saturation'].default_value = 0.6

        elif preset == 'VINTAGE':
            color_correction.lift = (1.05, 1.0, 0.95)
            color_correction.gamma = (1.0, 0.98, 0.95)
            # Add some warmth and reduce contrast

        elif preset == 'NOIR':
            # Create desaturation
            desat = create_node(
                node_tree,
                'CompositorNodeHueSat',
                location=(400, -200),
                label="B&W"
            )
            desat.inputs['Saturation'].default_value = 0.0

            # High contrast
            contrast = create_node(
                node_tree,
                'CompositorNodeBrightContrast',
                location=(600, -200),
                label="High Contrast"
            )
            contrast.inputs['Contrast'].default_value = 50

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Registration
classes = (
    HGFX_OT_ApplyColorHarmony,
    HGFX_OT_CreateSplitToneEffect,
    HGFX_OT_CreateColorGradeStack,
    HGFX_OT_ApplyLookPreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
