"""
Export and Automation Tools
Handles batch export and FFmpeg integration
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty, BoolProperty, IntProperty
from pathlib import Path
from ..utils.ffmpeg_handler import get_ffmpeg_handler
from ..utils.openimageio_handler import get_image_handler
from ..utils.constants import EXPORT_FORMATS, VIDEO_CODECS


class HGFX_OT_BatchExportFrames(Operator):
    """Batch export frames with post-processing"""
    bl_idname = "hgfx.batch_export_frames"
    bl_label = "Batch Export Frames"
    bl_options = {'REGISTER'}

    output_directory: StringProperty(
        name="Output Directory",
        subtype='DIR_PATH',
        default="//render_output/"
    )

    file_format: EnumProperty(
        name="Format",
        items=[
            ('PNG', 'PNG', 'PNG format'),
            ('JPEG', 'JPEG', 'JPEG format'),
            ('OPEN_EXR', 'OpenEXR', 'OpenEXR format'),
            ('TIFF', 'TIFF', 'TIFF format'),
        ],
        default='PNG'
    )

    frame_start: IntProperty(
        name="Start Frame",
        default=1
    )

    frame_end: IntProperty(
        name="End Frame",
        default=250
    )

    def execute(self, context):
        scene = context.scene

        if self.frame_start == 1 and self.frame_end == 250:
            self.frame_start = scene.frame_start
            self.frame_end = scene.frame_end

        output_dir = Path(bpy.path.abspath(self.output_directory))
        output_dir.mkdir(parents=True, exist_ok=True)

        # Store original settings
        original_filepath = scene.render.filepath
        original_format = scene.render.image_settings.file_format

        try:
            scene.render.image_settings.file_format = self.file_format

            for frame in range(self.frame_start, self.frame_end + 1):
                scene.frame_set(frame)

                # Generate filename
                filename = f"frame_{frame:04d}"
                if self.file_format == 'PNG':
                    filename += '.png'
                elif self.file_format == 'JPEG':
                    filename += '.jpg'
                elif self.file_format == 'OPEN_EXR':
                    filename += '.exr'
                elif self.file_format == 'TIFF':
                    filename += '.tif'

                filepath = output_dir / filename
                scene.render.filepath = str(filepath)

                # Render frame
                bpy.ops.render.render(write_still=True)

                self.report({'INFO'}, f"Exported frame {frame}")

            self.report({'INFO'}, f"Batch export complete: {self.frame_end - self.frame_start + 1} frames")

        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {e}")
            return {'CANCELLED'}

        finally:
            # Restore settings
            scene.render.filepath = original_filepath
            scene.render.image_settings.file_format = original_format

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_ExportToVideo(Operator):
    """Export compositor output to video using FFmpeg"""
    bl_idname = "hgfx.export_to_video"
    bl_label = "Export to Video"
    bl_options = {'REGISTER'}

    output_path: StringProperty(
        name="Output Video",
        subtype='FILE_PATH',
        default="//output.mp4"
    )

    codec: EnumProperty(
        name="Codec",
        items=[
            ('H264', 'H.264', 'H.264 codec (most compatible)'),
            ('H265', 'H.265/HEVC', 'H.265 codec (better compression)'),
            ('PRORES', 'ProRes', 'Apple ProRes (high quality)'),
            ('DNXHD', 'DNxHD', 'Avid DNxHD (professional)'),
        ],
        default='H264'
    )

    quality: EnumProperty(
        name="Quality",
        items=[
            ('high', 'High', 'High quality'),
            ('medium', 'Medium', 'Medium quality'),
            ('low', 'Low', 'Low quality (smaller file)'),
        ],
        default='high'
    )

    render_first: BoolProperty(
        name="Render Frames First",
        description="Render all frames before encoding",
        default=True
    )

    def execute(self, context):
        scene = context.scene

        ffmpeg = get_ffmpeg_handler()

        if not ffmpeg.check_ffmpeg_available():
            self.report({'ERROR'}, "FFmpeg not found. Please set FFmpeg path in preferences")
            return {'CANCELLED'}

        output_path = bpy.path.abspath(self.output_path)

        # Render frames first if needed
        if self.render_first:
            temp_dir = Path(bpy.path.abspath("//temp_frames/"))
            temp_dir.mkdir(parents=True, exist_ok=True)

            self.report({'INFO'}, "Rendering frames...")

            for frame in range(scene.frame_start, scene.frame_end + 1):
                scene.frame_set(frame)
                filepath = temp_dir / f"frame_{frame:04d}.png"
                scene.render.filepath = str(filepath)
                bpy.ops.render.render(write_still=True)

            # Encode to video
            self.report({'INFO'}, "Encoding video...")

            input_pattern = str(temp_dir / "frame_%04d.png")
            framerate = scene.render.fps

            success = ffmpeg.encode_image_sequence(
                input_pattern,
                output_path,
                codec=self.codec,
                framerate=framerate,
                start_number=scene.frame_start,
                quality=self.quality
            )

            if success:
                self.report({'INFO'}, f"Video exported: {output_path}")

                # Clean up temp frames
                import shutil
                shutil.rmtree(temp_dir)

                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "FFmpeg encoding failed")
                return {'CANCELLED'}

        else:
            self.report({'ERROR'}, "Frame sequence export not yet implemented")
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class HGFX_OT_QuickExport(Operator):
    """Quick export current frame"""
    bl_idname = "hgfx.quick_export"
    bl_label = "Quick Export Frame"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        # Export to temp directory
        output_dir = Path(bpy.path.abspath("//quick_export/"))
        output_dir.mkdir(parents=True, exist_ok=True)

        frame = scene.frame_current
        filepath = output_dir / f"frame_{frame:04d}.png"

        scene.render.filepath = str(filepath)
        bpy.ops.render.render(write_still=True)

        self.report({'INFO'}, f"Exported: {filepath}")

        return {'FINISHED'}


class HGFX_OT_ExportCompStack(Operator):
    """Export compositor node tree as preset"""
    bl_idname = "hgfx.export_comp_stack"
    bl_label = "Export Comp Stack"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        scene = context.scene

        if not scene.use_nodes:
            self.report({'WARNING'}, "No compositor nodes active")
            return {'CANCELLED'}

        import json

        node_tree = scene.node_tree
        data = {
            'nodes': [],
            'links': []
        }

        # Export node data
        for node in node_tree.nodes:
            node_data = {
                'type': node.bl_rna.identifier,
                'name': node.name,
                'label': node.label,
                'location': list(node.location),
            }
            data['nodes'].append(node_data)

        # Export links
        for link in node_tree.links:
            link_data = {
                'from_node': link.from_node.name,
                'to_node': link.to_node.name,
                'from_socket': link.from_socket.identifier,
                'to_socket': link.to_socket.identifier,
            }
            data['links'].append(link_data)

        # Save to file
        try:
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)

            self.report({'INFO'}, f"Exported comp stack: {self.filepath}")
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class HGFX_OT_CreateContactSheet(Operator):
    """Create contact sheet of rendered frames"""
    bl_idname = "hgfx.create_contact_sheet"
    bl_label = "Create Contact Sheet"
    bl_options = {'REGISTER'}

    columns: IntProperty(
        name="Columns",
        default=4,
        min=1,
        max=10
    )

    rows: IntProperty(
        name="Rows",
        default=3,
        min=1,
        max=10
    )

    def execute(self, context):
        self.report({'INFO'}, "Contact sheet feature coming soon")
        # This would require PIL/Pillow or similar
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Registration
classes = (
    HGFX_OT_BatchExportFrames,
    HGFX_OT_ExportToVideo,
    HGFX_OT_QuickExport,
    HGFX_OT_ExportCompStack,
    HGFX_OT_CreateContactSheet,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
