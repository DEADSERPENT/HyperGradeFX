"""
Sequence-Based Compositing System (SBCS)
Enables shot-level post pipelines with batch operations
"""

import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, BoolProperty, CollectionProperty, IntProperty
import json
from pathlib import Path


class HGFXSequence(PropertyGroup):
    """Represents a compositing sequence"""

    name: StringProperty(
        name="Sequence Name",
        description="Name of this sequence",
        default="Sequence"
    )

    frame_start: IntProperty(
        name="Start Frame",
        description="Starting frame of this sequence",
        default=1
    )

    frame_end: IntProperty(
        name="End Frame",
        description="Ending frame of this sequence",
        default=250
    )

    comp_setup: StringProperty(
        name="Compositor Setup",
        description="JSON data of compositor node setup",
        default=""
    )

    enabled: BoolProperty(
        name="Enabled",
        description="Enable this sequence",
        default=True
    )


class HGFXSequenceManager(PropertyGroup):
    """Manages compositing sequences"""

    sequences: CollectionProperty(type=HGFXSequence)
    active_sequence_index: IntProperty(default=0)


class HGFX_OT_AddSequence(Operator):
    """Add a new compositing sequence"""
    bl_idname = "hgfx.add_sequence"
    bl_label = "Add Sequence"
    bl_options = {'REGISTER', 'UNDO'}

    sequence_name: StringProperty(
        name="Sequence Name",
        default="New Sequence"
    )

    def execute(self, context):
        manager = context.scene.hgfx_sequence_manager
        sequence = manager.sequences.add()
        sequence.name = self.sequence_name
        sequence.frame_start = context.scene.frame_start
        sequence.frame_end = context.scene.frame_end

        # Capture current compositor setup
        comp_setup = self.capture_compositor_setup(context.scene)
        sequence.comp_setup = json.dumps(comp_setup)

        manager.active_sequence_index = len(manager.sequences) - 1

        self.report({'INFO'}, f"Added sequence: {self.sequence_name}")
        return {'FINISHED'}

    def capture_compositor_setup(self, scene):
        """Capture the current compositor node tree setup"""
        if not scene.use_nodes:
            return {}

        node_tree = scene.node_tree
        setup_data = {
            'nodes': [],
            'links': []
        }

        # Capture nodes
        for node in node_tree.nodes:
            node_data = {
                'type': node.bl_rna.identifier,
                'name': node.name,
                'label': node.label,
                'location': list(node.location),
                'width': node.width,
                'height': node.height,
                'use_custom_color': node.use_custom_color,
                'color': list(node.color) if node.use_custom_color else None,
            }

            # Capture node-specific properties
            if hasattr(node, 'blend_type'):
                node_data['blend_type'] = node.blend_type
            if hasattr(node, 'filter_type'):
                node_data['filter_type'] = node.filter_type
            if hasattr(node, 'operation'):
                node_data['operation'] = node.operation

            setup_data['nodes'].append(node_data)

        # Capture links
        for link in node_tree.links:
            link_data = {
                'from_node': link.from_node.name,
                'from_socket': link.from_socket.identifier,
                'to_node': link.to_node.name,
                'to_socket': link.to_socket.identifier,
            }
            setup_data['links'].append(link_data)

        return setup_data


class HGFX_OT_RemoveSequence(Operator):
    """Remove a compositing sequence"""
    bl_idname = "hgfx.remove_sequence"
    bl_label = "Remove Sequence"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(default=-1)

    def execute(self, context):
        manager = context.scene.hgfx_sequence_manager

        if self.index >= 0:
            idx = self.index
        else:
            idx = manager.active_sequence_index

        if 0 <= idx < len(manager.sequences):
            name = manager.sequences[idx].name
            manager.sequences.remove(idx)
            manager.active_sequence_index = max(0, idx - 1)
            self.report({'INFO'}, f"Removed sequence: {name}")
        else:
            self.report({'WARNING'}, "No sequence to remove")

        return {'FINISHED'}


class HGFX_OT_ApplySequence(Operator):
    """Apply a sequence's compositor setup"""
    bl_idname = "hgfx.apply_sequence"
    bl_label = "Apply Sequence"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(default=-1)

    def execute(self, context):
        manager = context.scene.hgfx_sequence_manager

        if self.index >= 0:
            idx = self.index
        else:
            idx = manager.active_sequence_index

        if idx < 0 or idx >= len(manager.sequences):
            self.report({'WARNING'}, "Invalid sequence index")
            return {'CANCELLED'}

        sequence = manager.sequences[idx]

        if not sequence.enabled:
            self.report({'WARNING'}, f"Sequence '{sequence.name}' is disabled")
            return {'CANCELLED'}

        # Apply compositor setup
        if sequence.comp_setup:
            try:
                setup_data = json.loads(sequence.comp_setup)
                self.apply_compositor_setup(context.scene, setup_data)
                context.scene.frame_start = sequence.frame_start
                context.scene.frame_end = sequence.frame_end
                self.report({'INFO'}, f"Applied sequence: {sequence.name}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to apply sequence: {e}")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "No compositor setup stored in sequence")

        return {'FINISHED'}

    def apply_compositor_setup(self, scene, setup_data):
        """Apply compositor setup from data"""
        scene.use_nodes = True
        node_tree = scene.node_tree

        # Clear existing nodes
        node_tree.nodes.clear()

        # Create nodes
        node_map = {}
        for node_data in setup_data.get('nodes', []):
            try:
                node = node_tree.nodes.new(node_data['type'])
                node.name = node_data['name']
                node.label = node_data['label']
                node.location = node_data['location']
                node.width = node_data['width']
                node.height = node_data['height']

                if node_data.get('use_custom_color'):
                    node.use_custom_color = True
                    node.color = node_data['color']

                # Apply node-specific properties
                if 'blend_type' in node_data and hasattr(node, 'blend_type'):
                    node.blend_type = node_data['blend_type']
                if 'filter_type' in node_data and hasattr(node, 'filter_type'):
                    node.filter_type = node_data['filter_type']
                if 'operation' in node_data and hasattr(node, 'operation'):
                    node.operation = node_data['operation']

                node_map[node_data['name']] = node

            except Exception as e:
                print(f"Error creating node {node_data['name']}: {e}")

        # Create links
        for link_data in setup_data.get('links', []):
            try:
                from_node = node_map.get(link_data['from_node'])
                to_node = node_map.get(link_data['to_node'])

                if from_node and to_node:
                    from_socket = None
                    to_socket = None

                    # Find sockets by identifier
                    for socket in from_node.outputs:
                        if socket.identifier == link_data['from_socket']:
                            from_socket = socket
                            break

                    for socket in to_node.inputs:
                        if socket.identifier == link_data['to_socket']:
                            to_socket = socket
                            break

                    if from_socket and to_socket:
                        node_tree.links.new(from_socket, to_socket)

            except Exception as e:
                print(f"Error creating link: {e}")


class HGFX_OT_BatchApplySequences(Operator):
    """Batch apply all sequences and render"""
    bl_idname = "hgfx.batch_apply_sequences"
    bl_label = "Batch Render Sequences"
    bl_options = {'REGISTER'}

    def execute(self, context):
        manager = context.scene.hgfx_sequence_manager

        if len(manager.sequences) == 0:
            self.report({'WARNING'}, "No sequences to process")
            return {'CANCELLED'}

        # Store original filepath
        original_filepath = context.scene.render.filepath

        sequences_processed = 0

        for idx, sequence in enumerate(manager.sequences):
            if not sequence.enabled:
                continue

            # Apply sequence
            bpy.ops.hgfx.apply_sequence(index=idx)

            # Set output path
            output_path = f"{original_filepath}{sequence.name}_"
            context.scene.render.filepath = output_path

            # Render animation
            try:
                bpy.ops.render.render(animation=True)
                sequences_processed += 1
                self.report({'INFO'}, f"Rendered sequence: {sequence.name}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to render {sequence.name}: {e}")

        # Restore original filepath
        context.scene.render.filepath = original_filepath

        self.report({'INFO'}, f"Batch processed {sequences_processed} sequences")
        return {'FINISHED'}


class HGFX_OT_SaveSequencePreset(Operator):
    """Save sequence as a preset"""
    bl_idname = "hgfx.save_sequence_preset"
    bl_label = "Save Sequence Preset"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')
    index: IntProperty(default=-1)

    def execute(self, context):
        manager = context.scene.hgfx_sequence_manager

        if self.index >= 0:
            idx = self.index
        else:
            idx = manager.active_sequence_index

        if idx < 0 or idx >= len(manager.sequences):
            self.report({'WARNING'}, "Invalid sequence index")
            return {'CANCELLED'}

        sequence = manager.sequences[idx]

        # Save to file
        preset_data = {
            'name': sequence.name,
            'frame_start': sequence.frame_start,
            'frame_end': sequence.frame_end,
            'comp_setup': sequence.comp_setup,
        }

        try:
            with open(self.filepath, 'w') as f:
                json.dump(preset_data, f, indent=2)
            self.report({'INFO'}, f"Saved preset: {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save preset: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class HGFX_OT_LoadSequencePreset(Operator):
    """Load sequence from a preset"""
    bl_idname = "hgfx.load_sequence_preset"
    bl_label = "Load Sequence Preset"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        manager = context.scene.hgfx_sequence_manager

        try:
            with open(self.filepath, 'r') as f:
                preset_data = json.load(f)

            sequence = manager.sequences.add()
            sequence.name = preset_data['name']
            sequence.frame_start = preset_data['frame_start']
            sequence.frame_end = preset_data['frame_end']
            sequence.comp_setup = preset_data['comp_setup']

            manager.active_sequence_index = len(manager.sequences) - 1

            self.report({'INFO'}, f"Loaded preset: {preset_data['name']}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load preset: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Registration
classes = (
    HGFXSequence,
    HGFXSequenceManager,
    HGFX_OT_AddSequence,
    HGFX_OT_RemoveSequence,
    HGFX_OT_ApplySequence,
    HGFX_OT_BatchApplySequences,
    HGFX_OT_SaveSequencePreset,
    HGFX_OT_LoadSequencePreset,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.hgfx_sequence_manager = bpy.props.PointerProperty(
        type=HGFXSequenceManager
    )


def unregister():
    del bpy.types.Scene.hgfx_sequence_manager

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
