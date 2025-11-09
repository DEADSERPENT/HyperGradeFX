"""
Edge-Aware Color Isolation
Gradient-based edge detection for outline FX and neon glow
"""

import bpy
from bpy.types import Operator
from ..utils.helpers import get_compositor_node_tree, create_node, connect_nodes
from ..utils.constants import EDGE_DETECTION_METHODS


class HGFX_OT_DetectEdges(Operator):
    """Detect edges using gradient-based detection"""
    bl_idname = "hgfx.detect_edges"
    bl_label = "Detect Edges"
    bl_options = {'REGISTER', 'UNDO'}

    method: bpy.props.EnumProperty(
        name="Method",
        items=EDGE_DETECTION_METHODS,
        default='SOBEL'
    )

    threshold: bpy.props.FloatProperty(
        name="Threshold",
        description="Edge detection threshold",
        default=0.1,
        min=0.0,
        max=1.0
    )

    use_normal_pass: bpy.props.BoolProperty(
        name="Use Normal Pass",
        description="Use normal pass for better edge detection",
        default=False
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        if self.use_normal_pass:
            context.view_layer.use_pass_normal = True

        self.create_edge_detection_setup(
            node_tree,
            self.method,
            self.threshold,
            self.use_normal_pass
        )

        scene.hypergradefx.edge_detection_enabled = True
        scene.hypergradefx.edge_threshold = self.threshold

        self.report({'INFO'}, f"Applied {self.method} edge detection")
        return {'FINISHED'}

    def create_edge_detection_setup(self, node_tree, method, threshold, use_normals):
        """Create edge detection node setup"""

        x = 400
        y = 0

        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return

        if method in ['SOBEL', 'PREWITT', 'LAPLACIAN']:
            edge_mask = self.sobel_edge_detection(
                node_tree, render_layer, (x, y), threshold, use_normals
            )
        elif method == 'CANNY':
            edge_mask = self.canny_edge_detection(
                node_tree, render_layer, (x, y), threshold
            )

        # Create viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 600, y),
            label="Edge Preview"
        )
        connect_nodes(node_tree, edge_mask, 'Image', viewer, 'Image')

        return edge_mask

    def sobel_edge_detection(self, node_tree, render_layer, location, threshold, use_normals):
        """Sobel edge detection using filters"""

        x, y = location

        # Choose input
        if use_normals and 'Normal' in render_layer.outputs:
            input_socket = 'Normal'
        else:
            input_socket = 'Image'

        # Convert to grayscale
        rgb_to_bw = create_node(
            node_tree,
            'CompositorNodeRGBToBW',
            location=(x, y),
            label="To Grayscale"
        )
        connect_nodes(node_tree, render_layer, input_socket, rgb_to_bw, 'Image')

        # Use filter node for edge detection
        filter_x = create_node(
            node_tree,
            'CompositorNodeFilter',
            location=(x + 200, y + 100),
            label="Sobel X"
        )
        filter_x.filter_type = 'SOBEL'

        filter_y = create_node(
            node_tree,
            'CompositorNodeFilter',
            location=(x + 200, y - 100),
            label="Sobel Y"
        )
        filter_y.filter_type = 'SOBEL'

        connect_nodes(node_tree, rgb_to_bw, 'Val', filter_x, 'Image')
        connect_nodes(node_tree, rgb_to_bw, 'Val', filter_y, 'Image')

        # Combine gradients
        math_add = create_node(
            node_tree,
            'CompositorNodeMath',
            location=(x + 400, y),
            label="Combine Gradients"
        )
        math_add.operation = 'ADD'

        connect_nodes(node_tree, filter_x, 'Image', math_add, 0)
        connect_nodes(node_tree, filter_y, 'Image', math_add, 1)

        # Threshold
        color_ramp = create_node(
            node_tree,
            'CompositorNodeValToRGB',
            location=(x + 550, y),
            label="Edge Threshold"
        )
        color_ramp.color_ramp.elements[0].position = threshold
        color_ramp.color_ramp.elements[1].position = threshold + 0.1

        connect_nodes(node_tree, math_add, 'Value', color_ramp, 'Fac')

        return color_ramp

    def canny_edge_detection(self, node_tree, render_layer, location, threshold):
        """Canny-like edge detection (simplified)"""

        x, y = location

        # Blur first to reduce noise
        blur = create_node(
            node_tree,
            'CompositorNodeBlur',
            location=(x, y),
            label="Gaussian Blur"
        )
        blur.size_x = 3
        blur.size_y = 3

        connect_nodes(node_tree, render_layer, 'Image', blur, 'Image')

        # Then apply Sobel
        return self.sobel_edge_detection(
            node_tree, {'outputs': {'Image': blur.outputs[0]}},
            (x + 200, y), threshold, False
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateNeonGlow(Operator):
    """Create neon glow effect from edges"""
    bl_idname = "hgfx.create_neon_glow"
    bl_label = "Create Neon Glow"
    bl_options = {'REGISTER', 'UNDO'}

    glow_color: bpy.props.FloatVectorProperty(
        name="Glow Color",
        subtype='COLOR',
        default=(0.0, 1.0, 1.0),
        size=3
    )

    intensity: bpy.props.FloatProperty(
        name="Intensity",
        default=2.0,
        min=0.0,
        max=10.0
    )

    blur_size: bpy.props.IntProperty(
        name="Blur Size",
        default=20,
        min=1,
        max=100
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.create_neon_glow_setup(
            node_tree,
            self.glow_color,
            self.intensity,
            self.blur_size
        )

        self.report({'INFO'}, "Created neon glow effect")
        return {'FINISHED'}

    def create_neon_glow_setup(self, node_tree, color, intensity, blur_size):
        """Create neon glow from edges"""

        x = 400
        y = 0

        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return

        # Detect edges first
        filter_node = create_node(
            node_tree,
            'CompositorNodeFilter',
            location=(x, y),
            label="Edge Detect"
        )
        filter_node.filter_type = 'SOBEL'

        connect_nodes(node_tree, render_layer, 'Image', filter_node, 'Image')

        # Blur edges for glow
        blur = create_node(
            node_tree,
            'CompositorNodeBlur',
            location=(x + 200, y),
            label="Glow Blur"
        )
        blur.size_x = blur_size
        blur.size_y = blur_size

        connect_nodes(node_tree, filter_node, 'Image', blur, 'Image')

        # Colorize
        color_node = create_node(
            node_tree,
            'CompositorNodeRGB',
            location=(x + 200, y - 200),
            label="Neon Color"
        )
        color_node.outputs[0].default_value = (*color, 1.0)

        mix_color = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 400, y),
            label="Colorize Glow"
        )
        mix_color.blend_type = 'MULTIPLY'

        connect_nodes(node_tree, blur, 'Image', mix_color, 'Fac')
        connect_nodes(node_tree, color_node, 'RGBA', mix_color, 2)

        # Intensify
        multiply = create_node(
            node_tree,
            'CompositorNodeMath',
            location=(x + 600, y),
            label="Intensity"
        )
        multiply.operation = 'MULTIPLY'
        multiply.inputs[1].default_value = intensity

        connect_nodes(node_tree, mix_color, 'Image', multiply, 0)

        # Add to original
        final_mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 800, y),
            label="Apply Glow"
        )
        final_mix.blend_type = 'ADD'

        connect_nodes(node_tree, render_layer, 'Image', final_mix, 1)
        connect_nodes(node_tree, multiply, 'Value', final_mix, 2)

        # Viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 1000, y),
            label="Neon Preview"
        )
        connect_nodes(node_tree, final_mix, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateOutlineEffect(Operator):
    """Create cel-shaded outline effect"""
    bl_idname = "hgfx.create_outline"
    bl_label = "Create Outline Effect"
    bl_options = {'REGISTER', 'UNDO'}

    outline_color: bpy.props.FloatVectorProperty(
        name="Outline Color",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        size=3
    )

    thickness: bpy.props.FloatProperty(
        name="Thickness",
        default=2.0,
        min=0.1,
        max=10.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.create_outline_setup(
            node_tree,
            self.outline_color,
            self.thickness
        )

        self.report({'INFO'}, "Created outline effect")
        return {'FINISHED'}

    def create_outline_setup(self, node_tree, color, thickness):
        """Create cel-shaded outline"""

        x = 400
        y = 0

        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return

        # Detect edges
        filter_node = create_node(
            node_tree,
            'CompositorNodeFilter',
            location=(x, y),
            label="Edge Detect"
        )
        filter_node.filter_type = 'SOBEL'

        connect_nodes(node_tree, render_layer, 'Image', filter_node, 'Image')

        # Dilate edges for thickness
        dilate = create_node(
            node_tree,
            'CompositorNodeDilateErode',
            location=(x + 200, y),
            label="Thicken"
        )
        dilate.distance = int(thickness)

        connect_nodes(node_tree, filter_node, 'Image', dilate, 'Mask')

        # Colorize outline
        color_node = create_node(
            node_tree,
            'CompositorNodeRGB',
            location=(x + 200, y - 200),
            label="Outline Color"
        )
        color_node.outputs[0].default_value = (*color, 1.0)

        # Composite over original
        alpha_over = create_node(
            node_tree,
            'CompositorNodeAlphaOver',
            location=(x + 400, y),
            label="Composite Outline"
        )

        connect_nodes(node_tree, render_layer, 'Image', alpha_over, 1)
        connect_nodes(node_tree, color_node, 'RGBA', alpha_over, 2)
        connect_nodes(node_tree, dilate, 'Mask', alpha_over, 'Fac')

        # Viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 600, y),
            label="Outline Preview"
        )
        connect_nodes(node_tree, alpha_over, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Registration
classes = (
    HGFX_OT_DetectEdges,
    HGFX_OT_CreateNeonGlow,
    HGFX_OT_CreateOutlineEffect,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
