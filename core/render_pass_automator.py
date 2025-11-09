"""
Render Pass Automator (RPA)
Automatically connects render passes into optimized compositing networks
"""

import bpy
from bpy.types import Operator
from ..utils.helpers import get_compositor_node_tree, create_node, connect_nodes, create_frame_node
from ..utils.constants import RENDER_PASSES, NODE_COLORS


class HGFX_OT_AutoConnectRenderPasses(Operator):
    """Automatically connect render passes to optimized compositor network"""
    bl_idname = "hgfx.auto_connect_render_passes"
    bl_label = "Auto-Connect Render Passes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        # Get render layer node
        render_layer = self.get_or_create_render_layer(node_tree)

        if not render_layer:
            self.report({'ERROR'}, "Could not find or create Render Layer node")
            return {'CANCELLED'}

        # Detect available passes
        available_passes = self.detect_available_passes(render_layer)

        if not available_passes:
            self.report({'WARNING'}, "No render passes detected")
            return {'CANCELLED'}

        # Build compositor network
        self.build_compositor_network(node_tree, render_layer, available_passes)

        self.report({'INFO'}, f"Auto-connected {len(available_passes)} render passes")
        return {'FINISHED'}

    def get_or_create_render_layer(self, node_tree):
        """Get existing or create new render layer node"""
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                return node

        # Create new render layer node
        render_layer = create_node(node_tree, 'CompositorNodeRLayers', location=(0, 0))
        return render_layer

    def detect_available_passes(self, render_layer):
        """Detect which render passes are available"""
        available = []

        for pass_key, pass_name in RENDER_PASSES.items():
            # Check if output socket exists
            if pass_name in render_layer.outputs:
                output = render_layer.outputs[pass_name]
                if output.enabled:
                    available.append(pass_key)

        return available

    def build_compositor_network(self, node_tree, render_layer, passes):
        """Build optimized compositor network"""

        # Create output node if it doesn't exist
        output_node = None
        for node in node_tree.nodes:
            if node.type == 'COMPOSITE':
                output_node = node
                break

        if not output_node:
            output_node = create_node(
                node_tree,
                'CompositorNodeComposite',
                location=(1000, 0)
            )

        x_offset = 300
        y_start = 400
        y_spacing = 250

        current_y = y_start
        current_x = x_offset

        # Create frame for organization
        main_frame = create_frame_node(node_tree, "HyperGradeFX Auto Network", NODE_COLORS['OUTPUT'])

        # Combined pass is the base
        if 'COMBINED' in passes:
            combined_socket = render_layer.outputs['Combined']
            current_comp = combined_socket
            current_y -= y_spacing
        else:
            # Create a mix node as starting point
            mix_node = create_node(
                node_tree,
                'CompositorNodeMixRGB',
                location=(current_x, current_y),
                label="Base Mix"
            )
            mix_node.blend_type = 'ADD'
            current_comp = mix_node.outputs[0]
            current_y -= y_spacing

        # Process Diffuse pass
        if 'DIFFUSE' in passes:
            diffuse_setup = self.create_diffuse_setup(
                node_tree, render_layer, (current_x, current_y)
            )
            mix_node = create_node(
                node_tree,
                'CompositorNodeMixRGB',
                location=(current_x + 300, current_y),
                label="Add Diffuse"
            )
            mix_node.blend_type = 'ADD'
            connect_nodes(node_tree, diffuse_setup, 0, mix_node, 1)

            if 'COMBINED' in passes:
                # Mix with combined
                pass
            current_y -= y_spacing

        # Process Emission pass
        if 'EMISSION' in passes:
            emission_mix = create_node(
                node_tree,
                'CompositorNodeMixRGB',
                location=(current_x + 600, current_y),
                label="Add Emission"
            )
            emission_mix.blend_type = 'ADD'
            emission_mix.inputs[0].default_value = 1.0
            connect_nodes(node_tree, render_layer, 'Emit', emission_mix, 2)
            current_y -= y_spacing

        # Process AO (Ambient Occlusion) pass
        if 'AO' in passes:
            ao_setup = self.create_ao_setup(
                node_tree, render_layer, (current_x, current_y)
            )
            current_y -= y_spacing

        # Process Shadow pass
        if 'SHADOW' in passes:
            shadow_setup = self.create_shadow_setup(
                node_tree, render_layer, (current_x, current_y)
            )
            current_y -= y_spacing

        # Process Specular/Glossy passes
        if 'SPECULAR' in passes or 'GLOSSY' in passes:
            specular_setup = self.create_specular_setup(
                node_tree, render_layer, (current_x, current_y)
            )
            current_y -= y_spacing

        # Process Z-Depth for effects
        if 'Z' in passes:
            zdepth_setup = self.create_zdepth_setup(
                node_tree, render_layer, (current_x, current_y)
            )
            current_y -= y_spacing

        # Process Normal pass for effects
        if 'NORMAL' in passes:
            normal_setup = self.create_normal_setup(
                node_tree, render_layer, (current_x, current_y)
            )
            current_y -= y_spacing

        # Create final composite chain
        final_x = current_x + 900

        # Color correction
        color_correct = create_node(
            node_tree,
            'CompositorNodeColorCorrection',
            location=(final_x, 0),
            label="Color Grading"
        )

        # Exposure/Gamma
        exposure_node = create_node(
            node_tree,
            'CompositorNodeExposure',
            location=(final_x + 200, 0),
            label="Exposure"
        )

        # Final viewer
        viewer_node = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(final_x + 400, 200),
            label="Preview"
        )

        # Connect to output
        if 'COMBINED' in passes:
            connect_nodes(node_tree, render_layer, 'Combined', color_correct, 'Image')
        connect_nodes(node_tree, color_correct, 'Image', exposure_node, 'Image')
        connect_nodes(node_tree, exposure_node, 'Image', output_node, 'Image')
        connect_nodes(node_tree, exposure_node, 'Image', viewer_node, 'Image')

        # Alpha passthrough
        if 'COMBINED' in passes:
            connect_nodes(node_tree, render_layer, 'Alpha', output_node, 'Alpha')

    def create_diffuse_setup(self, node_tree, render_layer, location):
        """Create diffuse pass processing setup"""
        color_correct = create_node(
            node_tree,
            'CompositorNodeHueSat',
            location=location,
            label="Diffuse Adjust"
        )
        connect_nodes(node_tree, render_layer, 'DiffCol', color_correct, 'Image')
        return color_correct

    def create_ao_setup(self, node_tree, render_layer, location):
        """Create AO pass processing setup"""
        ao_multiply = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=location,
            label="AO Multiply"
        )
        ao_multiply.blend_type = 'MULTIPLY'
        ao_multiply.inputs[0].default_value = 1.0
        connect_nodes(node_tree, render_layer, 'AO', ao_multiply, 2)
        return ao_multiply

    def create_shadow_setup(self, node_tree, render_layer, location):
        """Create shadow pass processing setup"""
        shadow_multiply = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=location,
            label="Shadow Multiply"
        )
        shadow_multiply.blend_type = 'MULTIPLY'
        shadow_multiply.inputs[0].default_value = 0.7
        connect_nodes(node_tree, render_layer, 'Shadow', shadow_multiply, 2)
        return shadow_multiply

    def create_specular_setup(self, node_tree, render_layer, location):
        """Create specular/glossy pass processing setup"""
        spec_add = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=location,
            label="Specular Add"
        )
        spec_add.blend_type = 'ADD'
        spec_add.inputs[0].default_value = 1.0

        if 'SpecCol' in render_layer.outputs:
            connect_nodes(node_tree, render_layer, 'SpecCol', spec_add, 2)
        elif 'GlossCol' in render_layer.outputs:
            connect_nodes(node_tree, render_layer, 'GlossCol', spec_add, 2)

        return spec_add

    def create_zdepth_setup(self, node_tree, render_layer, location):
        """Create Z-depth processing setup"""
        # Normalize depth
        normalize = create_node(
            node_tree,
            'CompositorNodeNormalize',
            location=location,
            label="Normalize Depth"
        )
        connect_nodes(node_tree, render_layer, 'Depth', normalize, 'Value')

        # Map to viewer for preview
        map_value = create_node(
            node_tree,
            'CompositorNodeMapValue',
            location=(location[0] + 200, location[1]),
            label="Depth Range"
        )
        connect_nodes(node_tree, normalize, 'Value', map_value, 'Value')

        return map_value

    def create_normal_setup(self, node_tree, render_layer, location):
        """Create normal pass processing setup"""
        # Normal passes can be used for relighting or edge detection
        separate_rgb = create_node(
            node_tree,
            'CompositorNodeSeparateColor',
            location=location,
            label="Split Normals"
        )
        connect_nodes(node_tree, render_layer, 'Normal', separate_rgb, 'Image')

        return separate_rgb


class HGFX_OT_EnableRenderPasses(Operator):
    """Enable all render passes for compositing"""
    bl_idname = "hgfx.enable_render_passes"
    bl_label = "Enable All Render Passes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        view_layer = context.view_layer

        # Enable various passes
        passes_to_enable = [
            'use_pass_z',
            'use_pass_mist',
            'use_pass_normal',
            'use_pass_diffuse_color',
            'use_pass_glossy_color',
            'use_pass_transmission_color',
            'use_pass_emit',
            'use_pass_environment',
            'use_pass_ambient_occlusion',
            'use_pass_shadow',
        ]

        enabled_count = 0
        for pass_attr in passes_to_enable:
            if hasattr(view_layer, pass_attr):
                setattr(view_layer, pass_attr, True)
                enabled_count += 1

        self.report({'INFO'}, f"Enabled {enabled_count} render passes")
        return {'FINISHED'}


class HGFX_OT_CreatePassMask(Operator):
    """Create a mask from a render pass"""
    bl_idname = "hgfx.create_pass_mask"
    bl_label = "Create Pass Mask"
    bl_options = {'REGISTER', 'UNDO'}

    pass_name: bpy.props.EnumProperty(
        name="Pass",
        description="Render pass to create mask from",
        items=[
            ('Z', 'Z-Depth', 'Depth pass'),
            ('AO', 'Ambient Occlusion', 'AO pass'),
            ('Shadow', 'Shadow', 'Shadow pass'),
            ('Normal', 'Normal', 'Normal pass'),
            ('IndexOB', 'Object Index', 'Object index pass'),
            ('IndexMA', 'Material Index', 'Material index pass'),
        ]
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        # Get render layer node
        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            self.report({'ERROR'}, "No Render Layer node found")
            return {'CANCELLED'}

        # Check if pass is available
        pass_output = RENDER_PASSES.get(self.pass_name, self.pass_name)
        if pass_output not in render_layer.outputs:
            self.report({'ERROR'}, f"Pass '{pass_output}' not available")
            return {'CANCELLED'}

        # Create mask setup
        x = 600
        y = 0

        # Create color ramp for mask control
        ramp_node = create_node(
            node_tree,
            'CompositorNodeValToRGB',
            location=(x, y),
            label=f"{self.pass_name} Mask"
        )

        # Connect pass to ramp
        connect_nodes(node_tree, render_layer, pass_output, ramp_node, 0)

        # Create viewer for preview
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 200, y),
            label=f"{self.pass_name} Mask Preview"
        )
        connect_nodes(node_tree, ramp_node, 'Image', viewer, 'Image')

        self.report({'INFO'}, f"Created mask from {self.pass_name} pass")
        return {'FINISHED'}


# Registration
classes = (
    HGFX_OT_AutoConnectRenderPasses,
    HGFX_OT_EnableRenderPasses,
    HGFX_OT_CreatePassMask,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
