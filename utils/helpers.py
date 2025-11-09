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
    return bpy.context.preferences.addons[__package__.split('.')[0]].preferences


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
