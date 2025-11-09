"""
HyperGradeFX Helper Functions
Common utility functions used across the addon
"""

import bpy
import mathutils
import colorsys
from .constants import COLOR_HARMONY_ANGLES


def get_compositor_node_tree(scene):
    """Get or create compositor node tree for scene"""
    scene.use_nodes = True
    return scene.node_tree


def create_node_group(name, node_tree_type='CompositorNodeTree'):
    """Create a new node group"""
    node_group = bpy.data.node_groups.new(name, node_tree_type)
    return node_group


def find_node_by_label(node_tree, label):
    """Find a node by its label"""
    for node in node_tree.nodes:
        if node.label == label:
            return node
    return None


def find_nodes_by_type(node_tree, node_type):
    """Find all nodes of a specific type"""
    return [node for node in node_tree.nodes if node.type == node_type]


def get_render_layer_node(node_tree):
    """Get the render layer node from compositor"""
    for node in node_tree.nodes:
        if node.type == 'R_LAYERS':
            return node
    return None


def create_node(node_tree, node_type, location=(0, 0), label=""):
    """Create a node in the node tree"""
    node = node_tree.nodes.new(node_type)
    node.location = location
    if label:
        node.label = label
    return node


def connect_nodes(node_tree, from_node, from_socket, to_node, to_socket):
    """Connect two nodes"""
    try:
        node_tree.links.new(from_node.outputs[from_socket], to_node.inputs[to_socket])
        return True
    except Exception as e:
        print(f"Error connecting nodes: {e}")
        return False


def rgb_to_hsv(rgb):
    """Convert RGB to HSV"""
    return colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])


def hsv_to_rgb(hsv):
    """Convert HSV to RGB"""
    return colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])


def adjust_hue(rgb, angle_degrees):
    """Adjust the hue of an RGB color by a given angle in degrees"""
    h, s, v = rgb_to_hsv(rgb)
    h = (h + angle_degrees / 360.0) % 1.0
    return hsv_to_rgb((h, s, v))


def get_complementary_color(rgb):
    """Get complementary color"""
    return adjust_hue(rgb, COLOR_HARMONY_ANGLES['COMPLEMENTARY'])


def get_analogous_colors(rgb):
    """Get analogous colors (base + two neighbors)"""
    angle = COLOR_HARMONY_ANGLES['ANALOGOUS']
    color1 = adjust_hue(rgb, angle)
    color2 = adjust_hue(rgb, -angle)
    return [color1, color2]


def get_split_complementary_colors(rgb):
    """Get split-complementary colors"""
    angle = COLOR_HARMONY_ANGLES['SPLIT_COMPLEMENTARY']
    color1 = adjust_hue(rgb, angle)
    color2 = adjust_hue(rgb, -angle)
    return [color1, color2]


def get_triadic_colors(rgb):
    """Get triadic colors"""
    angle = COLOR_HARMONY_ANGLES['TRIADIC']
    color1 = adjust_hue(rgb, angle)
    color2 = adjust_hue(rgb, -angle)
    return [color1, color2]


def calculate_color_harmony(base_color, mode='COMPLEMENTARY'):
    """Calculate color harmony based on mode"""
    if mode == 'COMPLEMENTARY':
        return [get_complementary_color(base_color)]
    elif mode == 'ANALOGOUS':
        return get_analogous_colors(base_color)
    elif mode == 'SPLIT_COMPLEMENTARY':
        return get_split_complementary_colors(base_color)
    elif mode == 'TRIADIC':
        return get_triadic_colors(base_color)
    return []


def mix_colors(color1, color2, factor):
    """Mix two RGB colors with a factor (0-1)"""
    return tuple(color1[i] * (1 - factor) + color2[i] * factor for i in range(3))


def get_active_render_layer():
    """Get the active render layer"""
    scene = bpy.context.scene
    return scene.view_layers[scene.view_layers.active_index]


def ensure_render_passes(view_layer, passes):
    """Ensure specific render passes are enabled"""
    for pass_name in passes:
        if hasattr(view_layer, f'use_pass_{pass_name.lower()}'):
            setattr(view_layer, f'use_pass_{pass_name.lower()}', True)


def get_scene_frame_range(scene):
    """Get frame range of the scene"""
    return scene.frame_start, scene.frame_end


def normalize_vector(vector):
    """Normalize a vector"""
    length = sum(x**2 for x in vector) ** 0.5
    if length > 0:
        return tuple(x / length for x in vector)
    return vector


def interpolate_value(start, end, factor):
    """Linear interpolation between two values"""
    return start + (end - start) * factor


def clamp(value, min_value=0.0, max_value=1.0):
    """Clamp a value between min and max"""
    return max(min_value, min(max_value, value))


def get_image_dimensions(image):
    """Get dimensions of a Blender image"""
    if image:
        return image.size[0], image.size[1]
    return 0, 0


def create_color_ramp(node_tree, location, stops):
    """
    Create a color ramp node with custom stops
    stops: list of tuples [(position, color), ...]
    """
    ramp_node = create_node(node_tree, 'CompositorNodeValToRGB', location)

    # Remove default stops
    while len(ramp_node.color_ramp.elements) > 2:
        ramp_node.color_ramp.elements.remove(ramp_node.color_ramp.elements[0])

    # Add custom stops
    for i, (pos, color) in enumerate(stops):
        if i < 2:
            element = ramp_node.color_ramp.elements[i]
        else:
            element = ramp_node.color_ramp.elements.new(pos)
        element.position = pos
        element.color = color

    return ramp_node


def get_node_tree_output_node(node_tree):
    """Get the output node of a node tree"""
    for node in node_tree.nodes:
        if node.type == 'COMPOSITE':
            return node
    return None


def organize_node_tree(node_tree, start_x=0, start_y=0, spacing_x=300, spacing_y=200):
    """Organize nodes in a tree layout"""
    layers = {}

    # Group nodes by their depth in the tree
    for node in node_tree.nodes:
        depth = calculate_node_depth(node, node_tree)
        if depth not in layers:
            layers[depth] = []
        layers[depth].append(node)

    # Position nodes
    for depth, nodes in sorted(layers.items()):
        for i, node in enumerate(nodes):
            node.location.x = start_x + depth * spacing_x
            node.location.y = start_y - i * spacing_y


def calculate_node_depth(node, node_tree, visited=None):
    """Calculate the depth of a node in the tree"""
    if visited is None:
        visited = set()

    if node in visited:
        return 0

    visited.add(node)
    max_depth = 0

    for input_socket in node.inputs:
        for link in input_socket.links:
            depth = calculate_node_depth(link.from_node, node_tree, visited)
            max_depth = max(max_depth, depth + 1)

    return max_depth


def get_preferences():
    """Get HyperGradeFX preferences"""
    # Get base package name (remove subdirectory from package path)
    base_package = __package__.rsplit('.', 1)[0] if '.' in __package__ else __package__
    return bpy.context.preferences.addons[base_package].preferences


def get_preset_directory():
    """
    Get preset directory with fallback to addon directory

    Returns:
        Path: Preset directory path
    """
    from pathlib import Path

    prefs = get_preferences()

    # If user has set a custom directory, use that
    if prefs.preset_directory and prefs.preset_directory.strip():
        return Path(prefs.preset_directory)

    # Otherwise, use the addon's preset directory
    addon_dir = Path(__file__).parent.parent
    return addon_dir / "presets"


def create_frame_node(node_tree, label, color=(0.4, 0.4, 0.4)):
    """Create a frame node for organizing"""
    frame = node_tree.nodes.new('NodeFrame')
    frame.label = label
    frame.use_custom_color = True
    frame.color = color
    return frame


def enable_compositor_preview(context):
    """
    Enable compositor preview features for real-time feedback
    - Enables compositor backdrop
    - Sets up viewer node
    - Forces UI update
    """
    import bpy

    # Enable compositor use_nodes if not already
    if not context.scene.use_nodes:
        context.scene.use_nodes = True

    # Enable backdrop in all node editor areas
    for area in context.screen.areas:
        if area.type == 'NODE_EDITOR':
            for space in area.spaces:
                if space.type == 'NODE_EDITOR':
                    space.backdrop_channels = 'COLOR'  # Show color channels
                    space.show_backdrop = True  # Enable backdrop
                    area.tag_redraw()

    # Force redraw
    for area in context.screen.areas:
        area.tag_redraw()


def activate_viewer_node(node_tree, viewer_node):
    """
    Activate a viewer node to show its output in the backdrop

    Args:
        node_tree: The compositor node tree
        viewer_node: The viewer node to activate
    """
    if viewer_node and viewer_node.type == 'VIEWER':
        node_tree.nodes.active = viewer_node

        # Force update
        viewer_node.update()


def connect_to_composite_output(node_tree, output_node, output_socket='Image'):
    """
    Connect a node to the Composite output for final rendering

    Args:
        node_tree: The compositor node tree
        output_node: The node whose output should go to Composite
        output_socket: The socket name on the output node (default: 'Image')

    Returns:
        The Composite node
    """
    # Find or create Composite output node
    composite = None
    for node in node_tree.nodes:
        if node.type == 'COMPOSITE':
            composite = node
            break

    if not composite:
        # Create composite node if it doesn't exist
        composite = create_node(
            node_tree,
            'CompositorNodeComposite',
            location=(output_node.location.x + 300, output_node.location.y),
            label="Composite Output"
        )

    # Connect the output node to composite
    try:
        node_tree.links.new(
            output_node.outputs[output_socket],
            composite.inputs['Image']
        )
    except Exception as e:
        print(f"Error connecting to composite: {e}")

    return composite


def setup_realtime_preview(context, node_tree, final_node, final_socket='Image'):
    """
    Complete setup for real-time preview
    Combines all preview features: backdrop, viewer, and composite output

    Args:
        context: Blender context
        node_tree: The compositor node tree
        final_node: The final node in your effect chain
        final_socket: The output socket name (default: 'Image')

    Returns:
        tuple: (viewer_node, composite_node)
    """
    # Enable backdrop
    enable_compositor_preview(context)

    # Find or create viewer node
    viewer = None
    for node in node_tree.nodes:
        if node.type == 'VIEWER' and 'Preview' in node.label:
            viewer = node
            break

    if not viewer:
        viewer = create_node(
            node_tree,
            'CompositorNodeViewer',
            location=(final_node.location.x + 250, final_node.location.y),
            label="HGFX Preview"
        )

    # Connect final node to viewer
    try:
        node_tree.links.new(
            final_node.outputs[final_socket],
            viewer.inputs['Image']
        )
    except Exception as e:
        print(f"Error connecting to viewer: {e}")

    # Activate the viewer
    activate_viewer_node(node_tree, viewer)

    # Connect to composite output for final rendering
    composite = connect_to_composite_output(node_tree, final_node, final_socket)

    # Force redraw
    for area in context.screen.areas:
        area.tag_redraw()

    return viewer, composite
