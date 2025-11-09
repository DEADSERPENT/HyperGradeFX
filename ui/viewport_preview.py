"""
Live Post Preview Viewport
Live compositor preview with side-by-side comparison
"""

import bpy
from bpy.types import Operator, Panel
import gpu
from gpu_extras.batch import batch_for_shader


# Global preview state
_preview_enabled = False
_draw_handler = None


def draw_safe_area_overlay(self, context):
    """Draw safe area overlay on viewport"""
    scene = context.scene
    hgfx = scene.hypergradefx

    if not hgfx.safe_area_enabled:
        return

    # Get render resolution
    render = scene.render
    width = render.resolution_x
    height = render.resolution_y

    # Calculate safe area dimensions
    if hgfx.safe_area_type == 'ACTION':
        safe_percentage = 0.90
    elif hgfx.safe_area_type == 'TITLE':
        safe_percentage = 0.80
    else:
        safe_percentage = 0.90

    safe_width = width * safe_percentage
    safe_height = height * safe_percentage

    # Calculate positions (centered)
    left = (width - safe_width) / 2
    right = left + safe_width
    bottom = (height - safe_height) / 2
    top = bottom + safe_height

    # Normalize to viewport coordinates (0-1)
    # This is simplified - actual implementation would need proper viewport transformation
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    # Draw rectangle outline
    vertices = (
        (left, bottom),
        (right, bottom),
        (right, top),
        (left, top)
    )

    indices = ((0, 1), (1, 2), (2, 3), (3, 0))

    batch = batch_for_shader(shader, 'LINES', {"pos": vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", (1.0, 1.0, 0.0, 0.5))  # Yellow overlay

    gpu.state.line_width_set(2.0)
    batch.draw(shader)
    gpu.state.line_width_set(1.0)


class HGFX_OT_EnableLivePreview(Operator):
    """Enable live compositor preview"""
    bl_idname = "hgfx.enable_live_preview"
    bl_label = "Enable Live Preview"

    def execute(self, context):
        global _preview_enabled, _draw_handler

        _preview_enabled = True

        # Add draw handler
        if _draw_handler is None:
            _draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(
                draw_safe_area_overlay,
                (self, context),
                'WINDOW',
                'POST_PIXEL'
            )

        # Enable viewer node auto-update
        if context.scene.use_nodes:
            for node in context.scene.node_tree.nodes:
                if node.type == 'VIEWER':
                    context.scene.node_tree.nodes.active = node

        self.report({'INFO'}, "Live preview enabled")

        # Force redraw
        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}


class HGFX_OT_DisableLivePreview(Operator):
    """Disable live compositor preview"""
    bl_idname = "hgfx.disable_live_preview"
    bl_label = "Disable Live Preview"

    def execute(self, context):
        global _preview_enabled, _draw_handler

        _preview_enabled = False

        # Remove draw handler
        if _draw_handler is not None:
            bpy.types.SpaceNodeEditor.draw_handler_remove(_draw_handler, 'WINDOW')
            _draw_handler = None

        self.report({'INFO'}, "Live preview disabled")

        # Force redraw
        for area in context.screen.areas:
            area.tag_redraw()

        return {'FINISHED'}


class HGFX_PT_LivePreviewPanel(Panel):
    """Live preview control panel"""
    bl_label = "Live Preview"
    bl_idname = "HGFX_PT_live_preview_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        prefs = context.preferences.addons[__package__.split('.')[0]].preferences

        box = layout.box()
        box.prop(prefs, "enable_live_preview", text="Auto-Update Preview")

        row = layout.row(align=True)
        if _preview_enabled:
            row.operator("hgfx.disable_live_preview", icon='PAUSE', text="Disable")
        else:
            row.operator("hgfx.enable_live_preview", icon='PLAY', text="Enable")

        row.operator("hgfx.refresh_preview", icon='FILE_REFRESH')

        layout.separator()
        box = layout.box()
        box.label(text="Preview Tools", icon='VIEW_CAMERA')
        col = box.column(align=True)
        col.operator("hgfx.toggle_preview_mode", icon='ARROW_LEFTRIGHT')
        col.operator("hgfx.create_preview_split", icon='UV_SYNC_SELECT')

        # Pixel inspector (simplified)
        layout.separator()
        box = layout.box()
        box.label(text="Pixel Inspector", icon='EYEDROPPER')
        box.label(text="Move mouse over viewer to inspect")


class HGFX_OT_PixelInspector(Operator):
    """Inspect pixel values in compositor"""
    bl_idname = "hgfx.pixel_inspector"
    bl_label = "Pixel Inspector"

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            # Get pixel under mouse
            # This is a simplified version
            context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class HGFX_OT_CreateScopeDisplay(Operator):
    """Create scope display (waveform, histogram, vectorscope)"""
    bl_idname = "hgfx.create_scope_display"
    bl_label = "Create Scope Display"
    bl_options = {'REGISTER', 'UNDO'}

    scope_type: bpy.props.EnumProperty(
        name="Scope Type",
        items=[
            ('HISTOGRAM', 'Histogram', 'RGB Histogram'),
            ('WAVEFORM', 'Waveform', 'Waveform monitor'),
            ('VECTORSCOPE', 'Vectorscope', 'Color vectorscope'),
            ('PARADE', 'Parade', 'RGB Parade'),
        ],
        default='HISTOGRAM'
    )

    def execute(self, context):
        # This would create actual scope displays in production
        # For now, we'll create placeholder nodes

        from ..utils.helpers import get_compositor_node_tree, create_node

        node_tree = get_compositor_node_tree(context.scene)

        # Find render layer
        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return {'CANCELLED'}

        # Create viewer for scope
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(800, -400),
            label=f"{self.scope_type} Scope"
        )

        self.report({'INFO'}, f"Created {self.scope_type} scope display")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Registration
classes = (
    HGFX_OT_EnableLivePreview,
    HGFX_OT_DisableLivePreview,
    HGFX_PT_LivePreviewPanel,
    HGFX_OT_PixelInspector,
    HGFX_OT_CreateScopeDisplay,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    global _draw_handler

    # Remove draw handler if it exists
    if _draw_handler is not None:
        try:
            bpy.types.SpaceNodeEditor.draw_handler_remove(_draw_handler, 'WINDOW')
        except:
            pass
        _draw_handler = None

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
