"""
3D Post-Fog with Shadow Mapping
Realistic fog and volumetric atmosphere using Z-depth
"""

import bpy
from bpy.types import Operator
from ..utils.helpers import get_compositor_node_tree, create_node, connect_nodes, create_color_ramp
from ..utils.constants import FOG_PRESETS


class HGFX_OT_ApplyPostFog(Operator):
    """Apply post-process fog effect using Z-depth"""
    bl_idname = "hgfx.apply_post_fog"
    bl_label = "Apply Post-Fog"
    bl_options = {'REGISTER', 'UNDO'}

    density: bpy.props.FloatProperty(
        name="Density",
        description="Fog density",
        default=0.5,
        min=0.0,
        max=1.0
    )

    start_distance: bpy.props.FloatProperty(
        name="Start Distance",
        description="Distance where fog starts",
        default=5.0,
        min=0.0,
        max=1000.0
    )

    end_distance: bpy.props.FloatProperty(
        name="End Distance",
        description="Distance where fog reaches maximum density",
        default=25.0,
        min=0.0,
        max=1000.0
    )

    fog_color: bpy.props.FloatVectorProperty(
        name="Fog Color",
        subtype='COLOR',
        default=(0.5, 0.5, 0.6),
        min=0.0,
        max=1.0,
        size=3
    )

    use_exponential: bpy.props.BoolProperty(
        name="Exponential Falloff",
        description="Use exponential fog falloff instead of linear",
        default=False
    )

    affect_shadows: bpy.props.BoolProperty(
        name="Affect Shadows",
        description="Make fog scatter into shadow areas",
        default=True
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        # Ensure Z-depth pass is enabled
        view_layer = context.view_layer
        view_layer.use_pass_z = True

        # Create fog setup
        self.create_fog_setup(
            node_tree,
            self.density,
            self.start_distance,
            self.end_distance,
            self.fog_color,
            self.use_exponential,
            self.affect_shadows
        )

        # Update scene properties
        scene.hypergradefx.fog_enabled = True
        scene.hypergradefx.fog_density = self.density
        scene.hypergradefx.fog_start = self.start_distance
        scene.hypergradefx.fog_end = self.end_distance
        scene.hypergradefx.fog_color = (*self.fog_color, 1.0)

        self.report({'INFO'}, "Applied post-fog effect")
        return {'FINISHED'}

    def create_fog_setup(self, node_tree, density, start, end, fog_color,
                        exponential, affect_shadows):
        """Create fog effect node setup"""

        x_start = 400
        y = 0

        # Find render layer
        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            self.report({'ERROR'}, "No Render Layer node found")
            return

        # Check if Z pass is available
        if 'Depth' not in render_layer.outputs:
            self.report({'ERROR'}, "Z-Depth pass not available")
            return

        # 1. Normalize depth
        normalize = create_node(
            node_tree,
            'CompositorNodeNormalize',
            location=(x_start, y),
            label="Normalize Depth"
        )
        connect_nodes(node_tree, render_layer, 'Depth', normalize, 'Value')

        # 2. Map depth to fog range
        map_range = create_node(
            node_tree,
            'CompositorNodeMapRange',
            location=(x_start + 200, y),
            label="Fog Range"
        )

        # Calculate normalized range values
        # Note: This is simplified - actual depth values depend on camera settings
        map_range.inputs['From Min'].default_value = 0.0
        map_range.inputs['From Max'].default_value = 1.0
        map_range.inputs['To Min'].default_value = start / 100.0  # Normalized
        map_range.inputs['To Max'].default_value = end / 100.0

        connect_nodes(node_tree, normalize, 'Value', map_range, 'Value')

        # 3. Apply fog density with color ramp
        fog_ramp = create_node(
            node_tree,
            'CompositorNodeValToRGB',
            location=(x_start + 400, y),
            label="Fog Density"
        )

        # Configure color ramp for fog falloff
        if exponential:
            # Exponential falloff - adjust color ramp curve
            fog_ramp.color_ramp.elements[0].position = 0.0
            fog_ramp.color_ramp.elements[1].position = density
        else:
            # Linear falloff
            fog_ramp.color_ramp.elements[0].position = 0.0
            fog_ramp.color_ramp.elements[1].position = 1.0

        connect_nodes(node_tree, map_range, 'Value', fog_ramp, 'Fac')

        # 4. Create fog color
        fog_rgb = create_node(
            node_tree,
            'CompositorNodeRGB',
            location=(x_start + 400, y - 200),
            label="Fog Color"
        )
        fog_rgb.outputs[0].default_value = (*fog_color, 1.0)

        # 5. Mix fog with image
        fog_mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x_start + 600, y),
            label="Apply Fog"
        )
        fog_mix.blend_type = 'MIX'
        fog_mix.inputs[0].default_value = density

        connect_nodes(node_tree, render_layer, 'Image', fog_mix, 1)
        connect_nodes(node_tree, fog_rgb, 'RGBA', fog_mix, 2)
        connect_nodes(node_tree, fog_ramp, 'Alpha', fog_mix, 'Fac')

        # 6. Optional: Shadow scattering
        if affect_shadows:
            self.add_shadow_scattering(
                node_tree,
                render_layer,
                fog_mix,
                (x_start + 600, y - 300)
            )

        # 7. Create viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x_start + 800, y),
            label="Fog Preview"
        )
        connect_nodes(node_tree, fog_mix, 'Image', viewer, 'Image')

    def add_shadow_scattering(self, node_tree, render_layer, fog_node, location):
        """Add fog scattering in shadow areas"""

        # Check if shadow pass is available
        if 'Shadow' not in render_layer.outputs:
            return

        x, y = location

        # Invert shadow pass (so shadows are white)
        invert = create_node(
            node_tree,
            'CompositorNodeInvert',
            location=(x, y),
            label="Invert Shadows"
        )
        connect_nodes(node_tree, render_layer, 'Shadow', invert, 'Color')

        # Multiply fog by inverted shadows for scattering effect
        scatter_mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 200, y),
            label="Shadow Scatter"
        )
        scatter_mix.blend_type = 'MULTIPLY'
        scatter_mix.inputs[0].default_value = 0.3  # Scatter strength

        connect_nodes(node_tree, fog_node, 'Image', scatter_mix, 1)
        connect_nodes(node_tree, invert, 'Color', scatter_mix, 2)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_ApplyFogPreset(Operator):
    """Apply a fog preset"""
    bl_idname = "hgfx.apply_fog_preset"
    bl_label = "Apply Fog Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset: bpy.props.EnumProperty(
        name="Preset",
        items=[
            ('LIGHT_MIST', 'Light Mist', 'Subtle atmospheric mist'),
            ('MEDIUM_FOG', 'Medium Fog', 'Moderate fog density'),
            ('HEAVY_FOG', 'Heavy Fog', 'Dense fog'),
            ('VOLUMETRIC_HAZE', 'Volumetric Haze', 'Long-distance atmospheric haze'),
        ],
        default='MEDIUM_FOG'
    )

    def execute(self, context):
        preset_values = FOG_PRESETS.get(self.preset)

        if not preset_values:
            self.report({'ERROR'}, "Invalid preset")
            return {'CANCELLED'}

        # Apply preset using the main fog operator
        bpy.ops.hgfx.apply_post_fog(
            density=preset_values['density'],
            start_distance=preset_values['start'],
            end_distance=preset_values['end']
        )

        self.report({'INFO'}, f"Applied {self.preset} preset")
        return {'FINISHED'}


class HGFX_OT_CreateVolumetricRays(Operator):
    """Create volumetric god rays effect"""
    bl_idname = "hgfx.create_volumetric_rays"
    bl_label = "Create Volumetric Rays"
    bl_options = {'REGISTER', 'UNDO'}

    ray_length: bpy.props.FloatProperty(
        name="Ray Length",
        description="Length of volumetric rays",
        default=0.5,
        min=0.0,
        max=1.0
    )

    intensity: bpy.props.FloatProperty(
        name="Intensity",
        description="Ray intensity",
        default=0.3,
        min=0.0,
        max=1.0
    )

    samples: bpy.props.IntProperty(
        name="Samples",
        description="Number of samples for ray quality",
        default=100,
        min=10,
        max=200
    )

    center_x: bpy.props.FloatProperty(
        name="Center X",
        description="X position of light source",
        default=0.5,
        min=0.0,
        max=1.0
    )

    center_y: bpy.props.FloatProperty(
        name="Center Y",
        description="Y position of light source",
        default=0.5,
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.create_god_rays(
            node_tree,
            self.ray_length,
            self.intensity,
            self.center_x,
            self.center_y
        )

        self.report({'INFO'}, "Created volumetric rays")
        return {'FINISHED'}

    def create_god_rays(self, node_tree, ray_length, intensity, center_x, center_y):
        """Create god rays effect"""

        x = 400
        y = 0

        # Find render layer
        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return

        # Use glare node for god rays
        glare = create_node(
            node_tree,
            'CompositorNodeGlare',
            location=(x, y),
            label="God Rays"
        )
        glare.glare_type = 'STREAKS'
        glare.quality = 'HIGH'
        glare.streaks = 12
        glare.threshold = 0.8

        connect_nodes(node_tree, render_layer, 'Image', glare, 'Image')

        # Mix with original
        mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 250, y),
            label="Mix Rays"
        )
        mix.blend_type = 'ADD'
        mix.inputs[0].default_value = intensity

        connect_nodes(node_tree, render_layer, 'Image', mix, 1)
        connect_nodes(node_tree, glare, 'Image', mix, 2)

        # Create viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 450, y),
            label="Rays Preview"
        )
        connect_nodes(node_tree, mix, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_AnimateFog(Operator):
    """Animate fog parameters over time"""
    bl_idname = "hgfx.animate_fog"
    bl_label = "Animate Fog"
    bl_options = {'REGISTER', 'UNDO'}

    keyframe_density: bpy.props.BoolProperty(
        name="Keyframe Density",
        default=True
    )

    keyframe_color: bpy.props.BoolProperty(
        name="Keyframe Color",
        default=False
    )

    def execute(self, context):
        scene = context.scene
        hgfx = scene.hypergradefx

        current_frame = scene.frame_current

        # Keyframe fog properties
        if self.keyframe_density:
            hgfx.fog_density = hgfx.fog_density
            hgfx.keyframe_insert(data_path="fog_density", frame=current_frame)

        if self.keyframe_color:
            hgfx.fog_color = hgfx.fog_color
            hgfx.keyframe_insert(data_path="fog_color", frame=current_frame)

        self.report({'INFO'}, f"Keyframed fog at frame {current_frame}")
        return {'FINISHED'}


# Registration
classes = (
    HGFX_OT_ApplyPostFog,
    HGFX_OT_ApplyFogPreset,
    HGFX_OT_CreateVolumetricRays,
    HGFX_OT_AnimateFog,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
