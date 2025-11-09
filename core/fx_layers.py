"""
Post-Action FX Layer System
Procedural environmental effects using velocity vectors and material metadata
"""

import bpy
from bpy.types import Operator
from ..utils.helpers import get_compositor_node_tree, create_node, connect_nodes
from ..utils.constants import FX_TYPES


class HGFX_OT_CreateHeatHaze(Operator):
    """Create heat distortion/haze effect"""
    bl_idname = "hgfx.create_heat_haze"
    bl_label = "Create Heat Haze"
    bl_options = {'REGISTER', 'UNDO'}

    distortion_strength: bpy.props.FloatProperty(
        name="Distortion",
        description="Strength of heat distortion",
        default=0.05,
        min=0.0,
        max=1.0
    )

    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale of distortion pattern",
        default=5.0,
        min=0.1,
        max=20.0
    )

    speed: bpy.props.FloatProperty(
        name="Speed",
        description="Animation speed",
        default=1.0,
        min=0.0,
        max=10.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.create_heat_haze_setup(
            node_tree,
            self.distortion_strength,
            self.scale,
            self.speed
        )

        self.report({'INFO'}, "Created heat haze effect")
        return {'FINISHED'}

    def create_heat_haze_setup(self, node_tree, strength, scale, speed):
        """Create heat haze distortion"""

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

        # Create texture for distortion pattern
        texture = create_node(
            node_tree,
            'CompositorNodeTexture',
            location=(x, y - 200),
            label="Heat Pattern"
        )

        # Create distort node
        distort = create_node(
            node_tree,
            'CompositorNodeDisplace',
            location=(x + 250, y),
            label="Heat Distortion"
        )

        # Connect texture to displacement
        connect_nodes(node_tree, render_layer, 'Image', distort, 'Image')
        connect_nodes(node_tree, texture, 'Value', distort, 'X')
        connect_nodes(node_tree, texture, 'Value', distort, 'Y')

        # Scale the displacement
        distort.inputs['Scale X'].default_value = strength
        distort.inputs['Scale Y'].default_value = strength

        # Create viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 500, y),
            label="Haze Preview"
        )
        connect_nodes(node_tree, distort, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateShockwave(Operator):
    """Create shockwave/impact effect"""
    bl_idname = "hgfx.create_shockwave"
    bl_label = "Create Shockwave"
    bl_options = {'REGISTER', 'UNDO'}

    center_x: bpy.props.FloatProperty(
        name="Center X",
        default=0.5,
        min=0.0,
        max=1.0
    )

    center_y: bpy.props.FloatProperty(
        name="Center Y",
        default=0.5,
        min=0.0,
        max=1.0
    )

    radius: bpy.props.FloatProperty(
        name="Radius",
        default=0.3,
        min=0.0,
        max=1.0
    )

    strength: bpy.props.FloatProperty(
        name="Strength",
        default=0.5,
        min=0.0,
        max=2.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.create_shockwave_setup(
            node_tree,
            self.center_x,
            self.center_y,
            self.radius,
            self.strength
        )

        self.report({'INFO'}, "Created shockwave effect")
        return {'FINISHED'}

    def create_shockwave_setup(self, node_tree, cx, cy, radius, strength):
        """Create radial shockwave effect"""

        x = 400
        y = 0

        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return

        # Create ellipse mask for shockwave
        ellipse = create_node(
            node_tree,
            'CompositorNodeEllipseMask',
            location=(x, y - 200),
            label="Shockwave Mask"
        )
        ellipse.x = cx
        ellipse.y = cy
        ellipse.width = radius
        ellipse.height = radius

        # Create blur for wave propagation
        blur = create_node(
            node_tree,
            'CompositorNodeBlur',
            location=(x + 200, y - 200),
            label="Wave Blur"
        )
        blur.size_x = int(radius * 100)
        blur.size_y = int(radius * 100)
        connect_nodes(node_tree, ellipse, 'Mask', blur, 'Image')

        # Use as displacement
        displace = create_node(
            node_tree,
            'CompositorNodeDisplace',
            location=(x + 400, y),
            label="Shockwave Displace"
        )
        displace.inputs['Scale X'].default_value = strength
        displace.inputs['Scale Y'].default_value = strength

        connect_nodes(node_tree, render_layer, 'Image', displace, 'Image')
        connect_nodes(node_tree, blur, 'Image', displace, 'X')
        connect_nodes(node_tree, blur, 'Image', displace, 'Y')

        # Create viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 600, y),
            label="Shockwave Preview"
        )
        connect_nodes(node_tree, displace, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateMotionGlow(Operator):
    """Create motion-based glow effect using velocity pass"""
    bl_idname = "hgfx.create_motion_glow"
    bl_label = "Create Motion Glow"
    bl_options = {'REGISTER', 'UNDO'}

    glow_intensity: bpy.props.FloatProperty(
        name="Glow Intensity",
        default=1.0,
        min=0.0,
        max=5.0
    )

    threshold: bpy.props.FloatProperty(
        name="Motion Threshold",
        description="Minimum motion to trigger glow",
        default=0.1,
        min=0.0,
        max=1.0
    )

    color: bpy.props.FloatVectorProperty(
        name="Glow Color",
        subtype='COLOR',
        default=(1.0, 0.8, 0.4),
        size=3
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        # Enable vector pass
        context.view_layer.use_pass_vector = True

        self.create_motion_glow_setup(
            node_tree,
            self.glow_intensity,
            self.threshold,
            self.color
        )

        self.report({'INFO'}, "Created motion glow effect")
        return {'FINISHED'}

    def create_motion_glow_setup(self, node_tree, intensity, threshold, color):
        """Create motion-based glow"""

        x = 400
        y = 0

        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer or 'Vector' not in render_layer.outputs:
            return

        # Calculate motion magnitude from vector pass
        vector_blur = create_node(
            node_tree,
            'CompositorNodeVecBlur',
            location=(x, y),
            label="Motion Blur"
        )
        vector_blur.factor = intensity
        vector_blur.samples = 32

        connect_nodes(node_tree, render_layer, 'Image', vector_blur, 'Image')
        connect_nodes(node_tree, render_layer, 'Vector', vector_blur, 'Speed')
        connect_nodes(node_tree, render_layer, 'Depth', vector_blur, 'Z')

        # Create glow from motion
        glare = create_node(
            node_tree,
            'CompositorNodeGlare',
            location=(x + 250, y),
            label="Motion Glow"
        )
        glare.glare_type = 'FOG_GLOW'
        glare.threshold = threshold

        connect_nodes(node_tree, vector_blur, 'Image', glare, 'Image')

        # Colorize glow
        color_mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 500, y),
            label="Color Glow"
        )
        color_mix.blend_type = 'MULTIPLY'
        color_mix.inputs[2].default_value = (*color, 1.0)

        connect_nodes(node_tree, glare, 'Image', color_mix, 1)

        # Mix with original
        final_mix = create_node(
            node_tree,
            'CompositorNodeMixRGB',
            location=(x + 700, y),
            label="Apply Glow"
        )
        final_mix.blend_type = 'ADD'

        connect_nodes(node_tree, render_layer, 'Image', final_mix, 1)
        connect_nodes(node_tree, color_mix, 'Image', final_mix, 2)

        # Viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 900, y),
            label="Glow Preview"
        )
        connect_nodes(node_tree, final_mix, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateChromaticAberration(Operator):
    """Create chromatic aberration effect"""
    bl_idname = "hgfx.create_chromatic_aberration"
    bl_label = "Create Chromatic Aberration"
    bl_options = {'REGISTER', 'UNDO'}

    strength: bpy.props.FloatProperty(
        name="Strength",
        default=0.01,
        min=0.0,
        max=0.1
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.create_chromatic_aberration(node_tree, self.strength)

        self.report({'INFO'}, "Created chromatic aberration")
        return {'FINISHED'}

    def create_chromatic_aberration(self, node_tree, strength):
        """Create chromatic aberration effect"""

        x = 400
        y = 0

        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return

        # Separate RGB channels
        separate = create_node(
            node_tree,
            'CompositorNodeSeparateColor',
            location=(x, y),
            label="Separate RGB"
        )
        connect_nodes(node_tree, render_layer, 'Image', separate, 'Image')

        # Transform each channel slightly differently
        transform_r = create_node(
            node_tree,
            'CompositorNodeTransform',
            location=(x + 200, y + 200),
            label="Red Shift"
        )
        transform_r.inputs['X'].default_value = -strength * 10

        transform_b = create_node(
            node_tree,
            'CompositorNodeTransform',
            location=(x + 200, y - 200),
            label="Blue Shift"
        )
        transform_b.inputs['X'].default_value = strength * 10

        # Connect channels to transform
        connect_nodes(node_tree, separate, 'Red', transform_r, 'Image')
        connect_nodes(node_tree, separate, 'Blue', transform_b, 'Image')

        # Recombine channels
        combine = create_node(
            node_tree,
            'CompositorNodeCombineColor',
            location=(x + 400, y),
            label="Combine RGB"
        )
        connect_nodes(node_tree, transform_r, 'Image', combine, 'Red')
        connect_nodes(node_tree, separate, 'Green', combine, 'Green')
        connect_nodes(node_tree, transform_b, 'Image', combine, 'Blue')

        # Viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 600, y),
            label="Aberration Preview"
        )
        connect_nodes(node_tree, combine, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_CreateLensDistortion(Operator):
    """Create lens distortion effect"""
    bl_idname = "hgfx.create_lens_distortion"
    bl_label = "Create Lens Distortion"
    bl_options = {'REGISTER', 'UNDO'}

    distortion: bpy.props.FloatProperty(
        name="Distortion",
        default=0.0,
        min=-1.0,
        max=1.0
    )

    dispersion: bpy.props.FloatProperty(
        name="Dispersion",
        default=0.0,
        min=0.0,
        max=1.0
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        self.create_lens_distortion_setup(
            node_tree,
            self.distortion,
            self.dispersion
        )

        self.report({'INFO'}, "Created lens distortion")
        return {'FINISHED'}

    def create_lens_distortion_setup(self, node_tree, distortion, dispersion):
        """Create lens distortion"""

        x = 400
        y = 0

        render_layer = None
        for node in node_tree.nodes:
            if node.type == 'R_LAYERS':
                render_layer = node
                break

        if not render_layer:
            return

        # Use lens distortion node
        lens = create_node(
            node_tree,
            'CompositorNodeLensdist',
            location=(x, y),
            label="Lens Distortion"
        )
        lens.inputs['Distort'].default_value = distortion
        lens.inputs['Dispersion'].default_value = dispersion

        connect_nodes(node_tree, render_layer, 'Image', lens, 'Image')

        # Viewer
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(x + 250, y),
            label="Distortion Preview"
        )
        connect_nodes(node_tree, lens, 'Image', viewer, 'Image')

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Registration
classes = (
    HGFX_OT_CreateHeatHaze,
    HGFX_OT_CreateShockwave,
    HGFX_OT_CreateMotionGlow,
    HGFX_OT_CreateChromaticAberration,
    HGFX_OT_CreateLensDistortion,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
