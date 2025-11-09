"""
OpenImageIO Handler for HyperGradeFX
Handles advanced image I/O operations
"""

import bpy
import numpy as np
from pathlib import Path


class ImageIOHandler:
    """Handle image I/O operations using Blender's native capabilities"""

    @staticmethod
    def load_image(filepath, check_existing=True):
        """
        Load an image file

        Args:
            filepath: Path to the image file
            check_existing: Check if image already loaded

        Returns:
            bpy.types.Image object
        """
        filepath = str(filepath)

        if check_existing:
            for img in bpy.data.images:
                if img.filepath == filepath:
                    return img

        try:
            image = bpy.data.images.load(filepath, check_existing=check_existing)
            return image
        except Exception as e:
            print(f"Error loading image {filepath}: {e}")
            return None

    @staticmethod
    def save_image(image, filepath, file_format='PNG', color_depth='8',
                   compression=15, quality=90):
        """
        Save an image to a file

        Args:
            image: bpy.types.Image object
            filepath: Output file path
            file_format: Image format (PNG, JPEG, OPEN_EXR, TIFF)
            color_depth: Color depth ('8', '16', '32')
            compression: Compression level for PNG (0-100)
            quality: Quality for JPEG (0-100)
        """
        if not image:
            return False

        # Store original settings
        original_format = bpy.context.scene.render.image_settings.file_format
        original_depth = bpy.context.scene.render.image_settings.color_depth
        original_compression = bpy.context.scene.render.image_settings.compression
        original_quality = bpy.context.scene.render.image_settings.quality

        try:
            # Set render settings
            settings = bpy.context.scene.render.image_settings
            settings.file_format = file_format
            settings.color_depth = color_depth

            if file_format == 'PNG':
                settings.compression = compression
            elif file_format == 'JPEG':
                settings.quality = quality
            elif file_format == 'OPEN_EXR':
                settings.exr_codec = 'ZIP'

            # Save image
            image.save_render(filepath)
            print(f"Image saved: {filepath}")
            return True

        except Exception as e:
            print(f"Error saving image: {e}")
            return False

        finally:
            # Restore original settings
            settings = bpy.context.scene.render.image_settings
            settings.file_format = original_format
            settings.color_depth = original_depth
            settings.compression = original_compression
            settings.quality = original_quality

    @staticmethod
    def create_image(name, width, height, alpha=True, float_buffer=False):
        """Create a new image"""
        image = bpy.data.images.new(
            name=name,
            width=width,
            height=height,
            alpha=alpha,
            float_buffer=float_buffer
        )
        return image

    @staticmethod
    def get_pixel_data(image):
        """Get pixel data from an image as numpy array"""
        if not image:
            return None

        width, height = image.size
        channels = image.channels

        # Get pixels as list
        pixels = list(image.pixels)

        # Convert to numpy array and reshape
        pixel_array = np.array(pixels).reshape((height, width, channels))

        return pixel_array

    @staticmethod
    def set_pixel_data(image, pixel_data):
        """Set pixel data from numpy array"""
        if not image or pixel_data is None:
            return False

        try:
            # Flatten array
            pixels = pixel_data.flatten().tolist()

            # Set pixels
            image.pixels = pixels
            image.update()

            return True
        except Exception as e:
            print(f"Error setting pixel data: {e}")
            return False

    @staticmethod
    def convert_color_space(image, from_space='sRGB', to_space='Linear'):
        """Convert image color space"""
        if not image:
            return False

        try:
            image.colorspace_settings.name = to_space
            return True
        except Exception as e:
            print(f"Error converting color space: {e}")
            return False

    @staticmethod
    def batch_export_frames(scene, output_dir, file_pattern='frame_####',
                           file_format='PNG', frame_start=None, frame_end=None):
        """
        Batch export rendered frames

        Args:
            scene: Blender scene
            output_dir: Output directory
            file_pattern: File naming pattern (use #### for frame number)
            file_format: Output format
            frame_start: Start frame (None = scene start)
            frame_end: End frame (None = scene end)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if frame_start is None:
            frame_start = scene.frame_start
        if frame_end is None:
            frame_end = scene.frame_end

        # Store original settings
        original_filepath = scene.render.filepath
        original_format = scene.render.image_settings.file_format

        try:
            scene.render.image_settings.file_format = file_format

            exported_frames = []

            for frame in range(frame_start, frame_end + 1):
                scene.frame_set(frame)

                # Generate filename
                frame_str = str(frame).zfill(4)
                filename = file_pattern.replace('####', frame_str)

                if file_format == 'PNG':
                    filename += '.png'
                elif file_format == 'JPEG':
                    filename += '.jpg'
                elif file_format == 'OPEN_EXR':
                    filename += '.exr'

                filepath = output_dir / filename
                scene.render.filepath = str(filepath)

                # Render frame
                bpy.ops.render.render(write_still=True)
                exported_frames.append(str(filepath))

                print(f"Exported frame {frame}: {filepath}")

            return exported_frames

        except Exception as e:
            print(f"Error during batch export: {e}")
            return []

        finally:
            # Restore original settings
            scene.render.filepath = original_filepath
            scene.render.image_settings.file_format = original_format

    @staticmethod
    def get_image_metadata(image):
        """Get image metadata"""
        if not image:
            return None

        metadata = {
            'name': image.name,
            'filepath': image.filepath,
            'size': image.size[:],
            'channels': image.channels,
            'depth': image.depth,
            'is_float': image.is_float,
            'colorspace': image.colorspace_settings.name,
        }

        return metadata


def get_image_handler():
    """Get image handler instance"""
    return ImageIOHandler()
