"""
Node Group Blueprints (NGB)
Drag-and-drop compositing preset system
"""

import bpy
from bpy.types import Operator, PropertyGroup, UIList
from bpy.props import StringProperty, EnumProperty, CollectionProperty, IntProperty
import json
from pathlib import Path
from ..utils.helpers import get_compositor_node_tree, create_node, connect_nodes
from ..utils.constants import PRESET_CATEGORIES


class HGFXNodeBlueprint(PropertyGroup):
    """Represents a node group blueprint/preset"""

    name: StringProperty(
        name="Blueprint Name",
        description="Name of this blueprint",
        default="Blueprint"
    )

    category: EnumProperty(
        name="Category",
        description="Blueprint category",
        items=[
            ('COLOR_GRADING', 'Color Grading', 'Color grading presets'),
            ('LOOK_DEVELOPMENT', 'Look Development', 'Look development presets'),
            ('FILM_EMULATION', 'Film Emulation', 'Film emulation presets'),
            ('STYLIZED', 'Stylized', 'Stylized looks'),
            ('HDR', 'HDR', 'HDR processing'),
            ('TECHNICAL', 'Technical', 'Technical operations'),
            ('FX', 'FX', 'Special effects'),
        ],
        default='COLOR_GRADING'
    )

    description: StringProperty(
        name="Description",
        description="Blueprint description",
        default=""
    )

    node_data: StringProperty(
        name="Node Data",
        description="JSON data of the node group",
        default=""
    )

    thumbnail_path: StringProperty(
        name="Thumbnail",
        description="Path to thumbnail image",
        default="",
        subtype='FILE_PATH'
    )


class HGFX_UL_BlueprintList(UIList):
    """UI List for blueprints"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=item.name, icon='NODE')
            row.label(text=item.category.replace('_', ' ').title())
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='NODE')


class HGFX_OT_ApplyBlueprint(Operator):
    """Apply a node blueprint to the compositor"""
    bl_idname = "hgfx.apply_blueprint"
    bl_label = "Apply Blueprint"
    bl_options = {'REGISTER', 'UNDO'}

    blueprint_name: StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        # Find blueprint
        blueprint = None
        for bp in context.scene.hgfx_blueprints:
            if bp.name == self.blueprint_name or bp.name == context.scene.hgfx_active_blueprint:
                blueprint = bp
                break

        if not blueprint:
            self.report({'ERROR'}, "Blueprint not found")
            return {'CANCELLED'}

        # Apply blueprint
        try:
            node_data = json.loads(blueprint.node_data)
            group_node = self.create_node_group_from_data(node_tree, node_data, blueprint.name)

            if group_node:
                self.report({'INFO'}, f"Applied blueprint: {blueprint.name}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to create node group")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error applying blueprint: {e}")
            return {'CANCELLED'}

    def create_node_group_from_data(self, node_tree, data, name):
        """Create a node group from blueprint data"""

        # Create node group
        node_group = bpy.data.node_groups.new(name, 'CompositorNodeTree')

        # Create group input/output
        group_input = node_group.nodes.new('NodeGroupInput')
        group_output = node_group.nodes.new('NodeGroupOutput')

        group_input.location = (0, 0)
        group_output.location = (600, 0)

        # Create sockets
        for input_data in data.get('inputs', []):
            socket_type = input_data.get('type', 'NodeSocketColor')
            socket_name = input_data.get('name', 'Input')
            node_group.inputs.new(socket_type, socket_name)

        for output_data in data.get('outputs', []):
            socket_type = output_data.get('type', 'NodeSocketColor')
            socket_name = output_data.get('name', 'Output')
            node_group.outputs.new(socket_type, socket_name)

        # Create nodes inside group
        node_map = {}
        for node_data in data.get('nodes', []):
            try:
                node = node_group.nodes.new(node_data['type'])
                node.location = node_data.get('location', [0, 0])
                node.label = node_data.get('label', '')

                # Set properties
                for prop, value in node_data.get('properties', {}).items():
                    if hasattr(node, prop):
                        setattr(node, prop, value)

                node_map[node_data['name']] = node

            except Exception as e:
                print(f"Error creating node: {e}")

        # Create links inside group
        for link_data in data.get('links', []):
            try:
                from_node_name = link_data['from_node']
                to_node_name = link_data['to_node']

                # Handle group input/output
                if from_node_name == 'GROUP_INPUT':
                    from_node = group_input
                else:
                    from_node = node_map.get(from_node_name)

                if to_node_name == 'GROUP_OUTPUT':
                    to_node = group_output
                else:
                    to_node = node_map.get(to_node_name)

                if from_node and to_node:
                    from_socket_idx = link_data.get('from_socket', 0)
                    to_socket_idx = link_data.get('to_socket', 0)

                    node_group.links.new(
                        from_node.outputs[from_socket_idx],
                        to_node.inputs[to_socket_idx]
                    )

            except Exception as e:
                print(f"Error creating link: {e}")

        # Add group node to main compositor
        group_node = node_tree.nodes.new('CompositorNodeGroup')
        group_node.node_tree = node_group
        group_node.label = name
        group_node.location = (400, 0)

        return group_node


class HGFX_OT_SaveBlueprint(Operator):
    """Save current node selection as a blueprint"""
    bl_idname = "hgfx.save_blueprint"
    bl_label = "Save Blueprint"
    bl_options = {'REGISTER', 'UNDO'}

    blueprint_name: StringProperty(
        name="Name",
        description="Blueprint name",
        default="New Blueprint"
    )

    category: EnumProperty(
        name="Category",
        items=[
            ('COLOR_GRADING', 'Color Grading', ''),
            ('LOOK_DEVELOPMENT', 'Look Development', ''),
            ('FILM_EMULATION', 'Film Emulation', ''),
            ('STYLIZED', 'Stylized', ''),
            ('HDR', 'HDR', ''),
            ('TECHNICAL', 'Technical', ''),
            ('FX', 'FX', ''),
        ],
        default='COLOR_GRADING'
    )

    description: StringProperty(
        name="Description",
        default=""
    )

    def execute(self, context):
        scene = context.scene
        node_tree = get_compositor_node_tree(scene)

        # Get selected nodes
        selected_nodes = [node for node in node_tree.nodes if node.select]

        if not selected_nodes:
            self.report({'WARNING'}, "No nodes selected")
            return {'CANCELLED'}

        # Create blueprint data
        blueprint_data = self.capture_node_selection(selected_nodes, node_tree)

        # Create blueprint
        blueprint = scene.hgfx_blueprints.add()
        blueprint.name = self.blueprint_name
        blueprint.category = self.category
        blueprint.description = self.description
        blueprint.node_data = json.dumps(blueprint_data, indent=2)

        self.report({'INFO'}, f"Saved blueprint: {self.blueprint_name}")
        return {'FINISHED'}

    def capture_node_selection(self, nodes, node_tree):
        """Capture selected nodes as blueprint data"""
        data = {
            'inputs': [],
            'outputs': [],
            'nodes': [],
            'links': []
        }

        # Node map for link creation
        node_map = {node: f"node_{i}" for i, node in enumerate(nodes)}

        # Capture nodes
        for node in nodes:
            node_data = {
                'name': node_map[node],
                'type': node.bl_rna.identifier,
                'label': node.label,
                'location': list(node.location),
                'properties': {}
            }

            # Capture common properties
            if hasattr(node, 'blend_type'):
                node_data['properties']['blend_type'] = node.blend_type
            if hasattr(node, 'operation'):
                node_data['properties']['operation'] = node.operation
            if hasattr(node, 'filter_type'):
                node_data['properties']['filter_type'] = node.filter_type

            data['nodes'].append(node_data)

        # Capture links between selected nodes
        for link in node_tree.links:
            if link.from_node in nodes and link.to_node in nodes:
                link_data = {
                    'from_node': node_map[link.from_node],
                    'to_node': node_map[link.to_node],
                    'from_socket': list(link.from_node.outputs).index(link.from_socket),
                    'to_socket': list(link.to_node.inputs).index(link.to_socket),
                }
                data['links'].append(link_data)

        # Detect external inputs/outputs
        for link in node_tree.links:
            if link.from_node not in nodes and link.to_node in nodes:
                # External input
                input_socket = link.to_socket
                data['inputs'].append({
                    'name': input_socket.name,
                    'type': input_socket.bl_idname
                })

            if link.from_node in nodes and link.to_node not in nodes:
                # External output
                output_socket = link.from_socket
                data['outputs'].append({
                    'name': output_socket.name,
                    'type': output_socket.bl_idname
                })

        return data

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_LoadBlueprintPreset(Operator):
    """Load blueprint from file"""
    bl_idname = "hgfx.load_blueprint_preset"
    bl_label = "Load Blueprint Preset"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        try:
            with open(self.filepath, 'r') as f:
                preset_data = json.load(f)

            blueprint = context.scene.hgfx_blueprints.add()
            blueprint.name = preset_data.get('name', Path(self.filepath).stem)
            blueprint.category = preset_data.get('category', 'COLOR_GRADING')
            blueprint.description = preset_data.get('description', '')
            blueprint.node_data = json.dumps(preset_data.get('node_data', {}))

            self.report({'INFO'}, f"Loaded blueprint: {blueprint.name}")

        except Exception as e:
            self.report({'ERROR'}, f"Error loading blueprint: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class HGFX_OT_DeleteBlueprint(Operator):
    """Delete a blueprint"""
    bl_idname = "hgfx.delete_blueprint"
    bl_label = "Delete Blueprint"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(default=-1)

    def execute(self, context):
        scene = context.scene
        blueprints = scene.hgfx_blueprints

        if self.index >= 0:
            idx = self.index
        else:
            idx = scene.hgfx_blueprint_index

        if 0 <= idx < len(blueprints):
            name = blueprints[idx].name
            blueprints.remove(idx)
            scene.hgfx_blueprint_index = max(0, idx - 1)
            self.report({'INFO'}, f"Deleted blueprint: {name}")
        else:
            self.report({'WARNING'}, "No blueprint to delete")

        return {'FINISHED'}


def create_builtin_blueprints():
    """Create built-in blueprint presets"""

    blueprints = []

    # Netflix HDR Blueprint
    netflix_hdr = {
        'name': 'Netflix HDR',
        'category': 'HDR',
        'description': 'Netflix-style HDR color grading',
        'node_data': {
            'inputs': [{'name': 'Image', 'type': 'NodeSocketColor'}],
            'outputs': [{'name': 'Image', 'type': 'NodeSocketColor'}],
            'nodes': [
                {
                    'name': 'node_0',
                    'type': 'CompositorNodeColorCorrection',
                    'label': 'Shadows',
                    'location': [0, 0],
                    'properties': {}
                },
                {
                    'name': 'node_1',
                    'type': 'CompositorNodeColorCorrection',
                    'label': 'Midtones',
                    'location': [200, 0],
                    'properties': {}
                },
                {
                    'name': 'node_2',
                    'type': 'CompositorNodeColorCorrection',
                    'label': 'Highlights',
                    'location': [400, 0],
                    'properties': {}
                },
            ],
            'links': [
                {'from_node': 'GROUP_INPUT', 'to_node': 'node_0', 'from_socket': 0, 'to_socket': 0},
                {'from_node': 'node_0', 'to_node': 'node_1', 'from_socket': 0, 'to_socket': 0},
                {'from_node': 'node_1', 'to_node': 'node_2', 'from_socket': 0, 'to_socket': 0},
                {'from_node': 'node_2', 'to_node': 'GROUP_OUTPUT', 'from_socket': 0, 'to_socket': 0},
            ]
        }
    }
    blueprints.append(netflix_hdr)

    # Grunge Look
    grunge_look = {
        'name': 'Grunge Look',
        'category': 'STYLIZED',
        'description': 'Gritty, desaturated grunge aesthetic',
        'node_data': {
            'inputs': [{'name': 'Image', 'type': 'NodeSocketColor'}],
            'outputs': [{'name': 'Image', 'type': 'NodeSocketColor'}],
            'nodes': [
                {
                    'name': 'node_0',
                    'type': 'CompositorNodeHueSat',
                    'label': 'Desaturate',
                    'location': [0, 0],
                    'properties': {}
                },
                {
                    'name': 'node_1',
                    'type': 'CompositorNodeBrightContrast',
                    'label': 'Contrast',
                    'location': [200, 0],
                    'properties': {}
                },
            ],
            'links': [
                {'from_node': 'GROUP_INPUT', 'to_node': 'node_0', 'from_socket': 0, 'to_socket': 1},
                {'from_node': 'node_0', 'to_node': 'node_1', 'from_socket': 0, 'to_socket': 0},
                {'from_node': 'node_1', 'to_node': 'GROUP_OUTPUT', 'from_socket': 0, 'to_socket': 0},
            ]
        }
    }
    blueprints.append(grunge_look)

    # Cinematic Teal & Orange
    teal_orange = {
        'name': 'Teal & Orange',
        'category': 'LOOK_DEVELOPMENT',
        'description': 'Classic cinematic teal and orange look',
        'node_data': {
            'inputs': [{'name': 'Image', 'type': 'NodeSocketColor'}],
            'outputs': [{'name': 'Image', 'type': 'NodeSocketColor'}],
            'nodes': [
                {
                    'name': 'node_0',
                    'type': 'CompositorNodeColorBalance',
                    'label': 'Color Balance',
                    'location': [0, 0],
                    'properties': {}
                },
            ],
            'links': [
                {'from_node': 'GROUP_INPUT', 'to_node': 'node_0', 'from_socket': 0, 'to_socket': 1},
                {'from_node': 'node_0', 'to_node': 'GROUP_OUTPUT', 'from_socket': 0, 'to_socket': 0},
            ]
        }
    }
    blueprints.append(teal_orange)

    return blueprints


# Registration
classes = (
    HGFXNodeBlueprint,
    HGFX_UL_BlueprintList,
    HGFX_OT_ApplyBlueprint,
    HGFX_OT_SaveBlueprint,
    HGFX_OT_LoadBlueprintPreset,
    HGFX_OT_DeleteBlueprint,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.hgfx_blueprints = CollectionProperty(type=HGFXNodeBlueprint)
    bpy.types.Scene.hgfx_blueprint_index = IntProperty(default=0)
    bpy.types.Scene.hgfx_active_blueprint = StringProperty(default="")

    # Load built-in blueprints on first load
    # (This would be done in a more sophisticated way in production)


def unregister():
    del bpy.types.Scene.hgfx_active_blueprint
    del bpy.types.Scene.hgfx_blueprint_index
    del bpy.types.Scene.hgfx_blueprints

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
