"""
FFmpeg Handler for HyperGradeFX
Handles video encoding and export operations
"""

import subprocess
import os
import bpy
from pathlib import Path
from .constants import VIDEO_CODECS


class FFmpegHandler:
    """Handle FFmpeg operations for video export"""

    def __init__(self, ffmpeg_path="ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def check_ffmpeg_available(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"FFmpeg not found: {e}")
            return False

    def encode_image_sequence(self, input_pattern, output_path, codec='H264',
                             framerate=24, start_number=1, quality='high'):
        """
        Encode an image sequence to video

        Args:
            input_pattern: Input file pattern (e.g., "frame_%04d.png")
            output_path: Output video file path
            codec: Video codec (H264, H265, PRORES, DNXHD)
            framerate: Frame rate of the video
            start_number: Starting frame number
            quality: Quality preset (high, medium, low)
        """
        if not self.check_ffmpeg_available():
            raise RuntimeError("FFmpeg is not available")

        codec_settings = VIDEO_CODECS.get(codec, VIDEO_CODECS['H264'])

        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            '-framerate', str(framerate),
            '-start_number', str(start_number),
            '-i', input_pattern,
            '-c:v', codec_settings['codec'],
        ]

        # Add codec-specific settings
        if codec == 'PRORES':
            cmd.extend(['-profile:v', codec_settings['profile']])
        elif codec in ['H264', 'H265']:
            crf = codec_settings['crf']
            if quality == 'high':
                crf -= 2
            elif quality == 'low':
                crf += 2
            cmd.extend(['-crf', str(crf)])
        elif codec == 'DNXHD':
            cmd.extend(['-b:v', codec_settings['bitrate']])

        # Add output settings
        cmd.extend([
            '-pix_fmt', 'yuv420p',
            '-y',  # Overwrite output file
            output_path
        ])

        try:
            print(f"Running FFmpeg: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                print(f"Video encoded successfully: {output_path}")
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("FFmpeg encoding timed out")
            return False
        except Exception as e:
            print(f"Error running FFmpeg: {e}")
            return False

    def create_proxy(self, input_path, output_path, resolution='720p'):
        """Create a proxy video for preview"""
        if not self.check_ffmpeg_available():
            raise RuntimeError("FFmpeg is not available")

        resolution_map = {
            '360p': '640:360',
            '480p': '854:480',
            '720p': '1280:720',
            '1080p': '1920:1080',
        }

        scale = resolution_map.get(resolution, '1280:720')

        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-vf', f'scale={scale}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'fast',
            '-y',
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error creating proxy: {e}")
            return False

    def extract_frames(self, video_path, output_pattern, start_frame=None,
                      end_frame=None, format='png'):
        """Extract frames from a video"""
        if not self.check_ffmpeg_available():
            raise RuntimeError("FFmpeg is not available")

        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
        ]

        if start_frame is not None:
            cmd.extend(['-start_number', str(start_frame)])

        if end_frame is not None:
            duration = end_frame - (start_frame or 0)
            cmd.extend(['-frames:v', str(duration)])

        cmd.extend([
            '-f', 'image2',
            output_pattern
        ])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return False

    def get_video_info(self, video_path):
        """Get video information using ffprobe"""
        ffprobe_path = self.ffmpeg_path.replace('ffmpeg', 'ffprobe')

        cmd = [
            ffprobe_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None


def get_ffmpeg_handler():
    """Get FFmpeg handler with preferences"""
    # Get base package name (remove subdirectory from package path)
    base_package = __package__.rsplit('.', 1)[0] if '.' in __package__ else __package__
    prefs = bpy.context.preferences.addons[base_package].preferences
    return FFmpegHandler(prefs.ffmpeg_path)
