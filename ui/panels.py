"""
HyperGradeFX UI Panels
Main UI panels for the compositor
"""

import bpy
from bpy.types import Panel


class HGFX_PT_MainPanel(Panel):
    """Main HyperGradeFX panel"""
    bl_label = "HyperGradeFX"
    bl_idname = "HGFX_PT_main_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_context = "compositor"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Header
        box = layout.box()
        box.label(text="Multi-Dimensional Post-Production", icon='CAMERA_DATA')

        # Quick actions
        col = layout.column(align=True)
        col.operator("hgfx.auto_connect_render_passes", icon='AUTO')
        col.operator("hgfx.enable_render_passes", icon='RENDERLAYERS')


class HGFX_PT_SequencePanel(Panel):
    """Sequence-Based Compositing panel"""
    bl_label = "Sequences"
    bl_idname = "HGFX_PT_sequence_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        manager = scene.hgfx_sequence_manager

        row = layout.row()
        row.operator("hgfx.add_sequence", icon='ADD')

        if len(manager.sequences) > 0:
            layout.template_list(
                "UI_UL_list", "hgfx_sequences",
                manager, "sequences",
                manager, "active_sequence_index",
                rows=3
            )

            if manager.active_sequence_index >= 0 and manager.active_sequence_index < len(manager.sequences):
                seq = manager.sequences[manager.active_sequence_index]

                box = layout.box()
                box.prop(seq, "name")
                box.prop(seq, "frame_start")
                box.prop(seq, "frame_end")
                box.prop(seq, "enabled")

                row = layout.row(align=True)
                row.operator("hgfx.apply_sequence", icon='PLAY')
                row.operator("hgfx.remove_sequence", icon='REMOVE')

            layout.separator()
            layout.operator("hgfx.batch_apply_sequences", icon='RENDERLAYERS')


class HGFX_PT_ColorGradingPanel(Panel):
    """Color Grading panel"""
    bl_label = "Color Grading"
    bl_idname = "HGFX_PT_color_grading_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Color Harmony
        box = layout.box()
        box.label(text="Color Harmony", icon='COLOR')
        box.operator("hgfx.apply_color_harmony")

        hgfx = scene.hypergradefx
        box.prop(hgfx, "color_harmony_mode")
        box.prop(hgfx, "harmony_strength")

        # Split Toning
        layout.separator()
        box = layout.box()
        box.label(text="Split Toning", icon='IMAGE_RGB_ALPHA')
        box.operator("hgfx.create_split_tone")

        # Look Presets
        layout.separator()
        box = layout.box()
        box.label(text="Look Presets", icon='PRESET')
        box.operator("hgfx.apply_look_preset")

        # Full Grade Stack
        layout.separator()
        layout.operator("hgfx.create_color_grade_stack", icon='NODE_COMPOSITING')


class HGFX_PT_BlueprintsPanel(Panel):
    """Node Blueprints panel"""
    bl_label = "Node Blueprints"
    bl_idname = "HGFX_PT_blueprints_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator("hgfx.save_blueprint", icon='ADD', text="Save Selection")
        row.operator("hgfx.load_blueprint_preset", icon='IMPORT', text="Load")

        if len(scene.hgfx_blueprints) > 0:
            layout.template_list(
                "HGFX_UL_BlueprintList", "",
                scene, "hgfx_blueprints",
                scene, "hgfx_blueprint_index",
                rows=4
            )

            if scene.hgfx_blueprint_index >= 0 and scene.hgfx_blueprint_index < len(scene.hgfx_blueprints):
                bp = scene.hgfx_blueprints[scene.hgfx_blueprint_index]

                box = layout.box()
                box.label(text=bp.name, icon='NODE')
                box.label(text=f"Category: {bp.category}")
                if bp.description:
                    box.label(text=bp.description)

                row = layout.row(align=True)
                row.operator("hgfx.apply_blueprint", icon='PLAY', text="Apply")
                row.operator("hgfx.delete_blueprint", icon='REMOVE', text="Delete")


class HGFX_PT_FogPanel(Panel):
    """Post-Fog panel"""
    bl_label = "3D Post-Fog"
    bl_idname = "HGFX_PT_fog_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hgfx = scene.hypergradefx

        box = layout.box()
        box.prop(hgfx, "fog_enabled")

        if hgfx.fog_enabled:
            box.prop(hgfx, "fog_density")
            box.prop(hgfx, "fog_start")
            box.prop(hgfx, "fog_end")
            box.prop(hgfx, "fog_color")

        layout.separator()
        layout.operator("hgfx.apply_post_fog", icon='PROP_ON')
        layout.operator("hgfx.apply_fog_preset", icon='PRESET')

        layout.separator()
        box = layout.box()
        box.label(text="Volumetric Effects", icon='LIGHT_SUN')
        box.operator("hgfx.create_volumetric_rays", text="God Rays")
        box.operator("hgfx.animate_fog", text="Animate Fog")


class HGFX_PT_FXPanel(Panel):
    """FX Layer panel"""
    bl_label = "FX Layers"
    bl_idname = "HGFX_PT_fx_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Environmental FX
        box = layout.box()
        box.label(text="Environmental FX", icon='WORLD')
        col = box.column(align=True)
        col.operator("hgfx.create_heat_haze", icon='FORCE_TURBULENCE')
        col.operator("hgfx.create_shockwave", icon='FORCE_FORCE')
        col.operator("hgfx.create_motion_glow", icon='LIGHT')

        # Lens FX
        layout.separator()
        box = layout.box()
        box.label(text="Lens FX", icon='OUTLINER_OB_CAMERA')
        col = box.column(align=True)
        col.operator("hgfx.create_chromatic_aberration", icon='IMAGE_RGB')
        col.operator("hgfx.create_lens_distortion", icon='MESH_CIRCLE')


class HGFX_PT_EdgePanel(Panel):
    """Edge Detection panel"""
    bl_label = "Edge Effects"
    bl_idname = "HGFX_PT_edge_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hgfx = scene.hypergradefx

        box = layout.box()
        box.prop(hgfx, "edge_detection_enabled")
        if hgfx.edge_detection_enabled:
            box.prop(hgfx, "edge_threshold")

        layout.operator("hgfx.detect_edges", icon='MESH_GRID')

        layout.separator()
        box = layout.box()
        box.label(text="Edge FX", icon='LIGHT_SUN')
        col = box.column(align=True)
        col.operator("hgfx.create_neon_glow", icon='LIGHT_AREA')
        col.operator("hgfx.create_outline", icon='MESH_PLANE')


class HGFX_PT_ExportPanel(Panel):
    """Export panel"""
    bl_label = "Export & Automation"
    bl_idname = "HGFX_PT_export_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Quick export
        box = layout.box()
        box.label(text="Quick Export", icon='EXPORT')
        box.operator("hgfx.quick_export", icon='RENDER_STILL')

        # Batch export
        layout.separator()
        box = layout.box()
        box.label(text="Batch Export", icon='RENDERLAYERS')
        col = box.column(align=True)
        col.operator("hgfx.batch_export_frames", icon='IMAGE_DATA')
        col.operator("hgfx.export_to_video", icon='FILE_MOVIE')

        # Utilities
        layout.separator()
        box = layout.box()
        box.label(text="Utilities", icon='SETTINGS')
        col = box.column(align=True)
        col.operator("hgfx.export_comp_stack", icon='NODE_COMPOSITING')
        col.operator("hgfx.create_contact_sheet", icon='IMGDISPLAY')


class HGFX_PT_SafeAreaPanel(Panel):
    """Safe Area panel"""
    bl_label = "Safe Areas & Guides"
    bl_idname = "HGFX_PT_safe_area_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        hgfx = scene.hypergradefx

        box = layout.box()
        box.prop(hgfx, "safe_area_enabled")

        if hgfx.safe_area_enabled:
            box.prop(hgfx, "safe_area_type")

        layout.separator()
        layout.operator("hgfx.toggle_safe_area_overlay", icon='VIEW_CAMERA')
        layout.operator("hgfx.create_aspect_guides", icon='CAMERA_DATA')


class HGFX_PT_MaskPanel(Panel):
    """Manual Mask Drawing panel"""
    bl_label = "Mask Drawing"
    bl_idname = "HGFX_PT_mask_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.operator("hgfx.create_mask_layer", icon='ADD')
        layout.operator("hgfx.edit_mask", icon='GREASEPENCIL')

        layout.separator()
        box = layout.box()
        box.label(text="Mask Tools", icon='MOD_MASK')
        col = box.column(align=True)
        col.operator("hgfx.feather_mask", icon='SMOOTHCURVE')
        col.operator("hgfx.invert_mask", icon='ARROW_LEFTRIGHT')


class HGFX_PT_RenderPassPanel(Panel):
    """Render Pass panel"""
    bl_label = "Render Passes"
    bl_idname = "HGFX_PT_render_pass_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HyperGradeFX"
    bl_parent_id = "HGFX_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        layout.operator("hgfx.create_pass_mask", icon='MOD_MASK')

        layout.separator()
        box = layout.box()
        box.label(text="Pass Utilities", icon='RENDERLAYERS')
        col = box.column(align=True)

        # Add individual pass operators
        col.label(text="Create masks from:")
        col.operator("hgfx.create_pass_mask", text="Z-Depth").pass_name = 'Z'
        col.operator("hgfx.create_pass_mask", text="AO").pass_name = 'AO'
        col.operator("hgfx.create_pass_mask", text="Shadow").pass_name = 'Shadow'


# Registration
classes = (
    HGFX_PT_MainPanel,
    HGFX_PT_SequencePanel,
    HGFX_PT_ColorGradingPanel,
    HGFX_PT_BlueprintsPanel,
    HGFX_PT_FogPanel,
    HGFX_PT_FXPanel,
    HGFX_PT_EdgePanel,
    HGFX_PT_ExportPanel,
    HGFX_PT_SafeAreaPanel,
    HGFX_PT_MaskPanel,
    HGFX_PT_RenderPassPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
