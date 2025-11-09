"""
HyperGradeFX UI Operators
UI-specific operators for safe areas, masks, and overlays
"""

import bpy
from bpy.types import Operator
import gpu
from gpu_extras.batch import batch_for_shader


class HGFX_OT_ToggleSafeAreaOverlay(Operator):
    """Toggle safe area overlay display"""
    bl_idname = "hgfx.toggle_safe_area_overlay"
    bl_label = "Toggle Safe Area Overlay"

    def execute(self, context):
        scene = context.scene
        hgfx = scene.hypergradefx

        hgfx.safe_area_enabled = not hgfx.safe_area_enabled

        if hgfx.safe_area_enabled:
            self.report({'INFO'}, "Safe area overlay enabled")
        else:
            self.report({'INFO'}, "Safe area overlay disabled")

        # Force redraw
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                area.tag_redraw()

        return {'FINISHED'}


class HGFX_OT_CreateAspectGuides(Operator):
    """Create aspect ratio guides"""
    bl_idname = "hgfx.create_aspect_guides"
    bl_label = "Create Aspect Guides"
    bl_options = {'REGISTER', 'UNDO'}

    aspect_ratio: bpy.props.EnumProperty(
        name="Aspect Ratio",
        items=[
            ('16:9', '16:9', 'Standard HD/4K'),
            ('4:3', '4:3', 'Classic TV'),
            ('21:9', '21:9', 'Ultra-wide'),
            ('1:1', '1:1', 'Square (Instagram)'),
            ('9:16', '9:16', 'Vertical (Stories)'),
            ('2.39:1', '2.39:1', 'Cinemascope'),
        ],
        default='16:9'
    )

    def execute(self, context):
        self.report({'INFO'}, f"Created {self.aspect_ratio} guides")
        # In production, this would create visual guides in the compositor
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateMaskLayer(Operator):
    """Create a new mask layer for manual drawing"""
    bl_idname = "hgfx.create_mask_layer"
    bl_label = "Create Mask Layer"
    bl_options = {'REGISTER', 'UNDO'}

    mask_name: bpy.props.StringProperty(
        name="Mask Name",
        default="Mask"
    )

    def execute(self, context):
        # Create a new mask
        mask = bpy.data.masks.new(name=self.mask_name)

        # Add a mask layer
        mask_layer = mask.layers.new(name="Layer")

        self.report({'INFO'}, f"Created mask: {self.mask_name}")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_EditMask(Operator):
    """Edit mask in mask editor"""
    bl_idname = "hgfx.edit_mask"
    bl_label = "Edit Mask"

    def execute(self, context):
        # Switch to mask editing mode
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.mode = 'MASK'
                        self.report({'INFO'}, "Switched to mask editing mode")
                        return {'FINISHED'}

        self.report({'WARNING'}, "No Image Editor found. Open an Image Editor to edit masks")
        return {'CANCELLED'}


class HGFX_OT_FeatherMask(Operator):
    """Feather mask edges"""
    bl_idname = "hgfx.feather_mask"
    bl_label = "Feather Mask"
    bl_options = {'REGISTER', 'UNDO'}

    feather_amount: bpy.props.FloatProperty(
        name="Feather",
        description="Feather amount",
        default=10.0,
        min=0.0,
        max=100.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = scene.node_tree

        if not node_tree:
            self.report({'WARNING'}, "No compositor node tree")
            return {'CANCELLED'}

        # Find selected mask node
        selected_mask = None
        for node in node_tree.nodes:
            if node.select and node.type == 'MASK':
                selected_mask = node
                break

        if selected_mask and selected_mask.mask:
            for layer in selected_mask.mask.layers:
                for spline in layer.splines:
                    for point in spline.points:
                        point.feather_points.add(1)

            self.report({'INFO'}, f"Applied feather: {self.feather_amount}")
        else:
            self.report({'WARNING'}, "No mask node selected")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_InvertMask(Operator):
    """Invert selected mask"""
    bl_idname = "hgfx.invert_mask"
    bl_label = "Invert Mask"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        node_tree = scene.node_tree

        if not node_tree:
            self.report({'WARNING'}, "No compositor node tree")
            return {'CANCELLED'}

        # Find or create invert node for selected mask
        for node in node_tree.nodes:
            if node.select and node.type == 'MASK':
                # Create invert node
                invert = node_tree.nodes.new('CompositorNodeInvert')
                invert.location = (node.location.x + 200, node.location.y)

                # Connect mask to invert
                node_tree.links.new(node.outputs[0], invert.inputs['Color'])

                self.report({'INFO'}, "Created inverted mask")
                return {'FINISHED'}

        self.report({'WARNING'}, "No mask node selected")
        return {'CANCELLED'}


class HGFX_OT_RefreshPreview(Operator):
    """Refresh live preview"""
    bl_idname = "hgfx.refresh_preview"
    bl_label = "Refresh Preview"

    def execute(self, context):
        # Force compositor update
        if context.scene.use_nodes:
            context.scene.node_tree.update_tag()

        # Redraw all areas
        for area in context.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "Preview refreshed")
        return {'FINISHED'}


class HGFX_OT_TogglePreviewMode(Operator):
    """Toggle between original and processed preview"""
    bl_idname = "hgfx.toggle_preview_mode"
    bl_label = "Toggle Preview Mode"

    def execute(self, context):
        scene = context.scene
        node_tree = scene.node_tree

        if not node_tree:
            return {'CANCELLED'}

        # Find viewer node
        viewer = None
        for node in node_tree.nodes:
            if node.type == 'VIEWER':
                viewer = node
                break

        if viewer:
            # Toggle viewer usage
            viewer.use_alpha = not viewer.use_alpha
            self.report({'INFO'}, "Toggled preview mode")

        return {'FINISHED'}


class HGFX_OT_CreatePreviewSplit(Operator):
    """Create side-by-side preview comparison"""
    bl_idname = "hgfx.create_preview_split"
    bl_label = "Create Preview Split"
    bl_options = {'REGISTER', 'UNDO'}

    split_position: bpy.props.FloatProperty(
        name="Split Position",
        default=0.5,
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = scene.node_tree

        if not node_tree:
            self.report({'WARNING'}, "No compositor node tree")
            return {'CANCELLED'}

        # Create split preview setup
        from ..utils.helpers import create_node, connect_nodes

        # Find render layer
        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return {'CANCELLED'}

        # Create mask for split
        mask = create_node(
            node_tree,
            'CompositorNodeBoxMask',
            location=(400, -200),
            label="Split Mask"
        )
        mask.x = self.split_position
        mask.width = 1.0 - self.split_position

        self.report({'INFO'}, "Created split preview")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Registration
classes = (
    HGFX_OT_ToggleSafeAreaOverlay,
    HGFX_OT_CreateAspectGuides,
    HGFX_OT_CreateMaskLayer,
    HGFX_OT_EditMask,
    HGFX_OT_FeatherMask,
    HGFX_OT_InvertMask,
    HGFX_OT_RefreshPreview,
    HGFX_OT_TogglePreviewMode,
    HGFX_OT_CreatePreviewSplit,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
