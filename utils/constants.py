"""
HyperGradeFX Constants
Global constants and configuration values
"""

# Version
VERSION = (1, 0, 0)
VERSION_STRING = f"{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"

# Render Pass Names
RENDER_PASSES = {
    'COMBINED': 'Combined',
    'DIFFUSE': 'DiffCol',
    'SPECULAR': 'SpecCol',
    'EMISSION': 'Emit',
    'ENVIRONMENT': 'Env',
    'AO': 'AO',
    'SHADOW': 'Shadow',
    'NORMAL': 'Normal',
    'UV': 'UV',
    'VECTOR': 'Vector',
    'Z': 'Depth',
    'OBJECT_INDEX': 'IndexOB',
    'MATERIAL_INDEX': 'IndexMA',
    'MIST': 'Mist',
    'GLOSSY': 'GlossCol',
    'TRANSMISSION': 'TransCol',
}

# Color Harmony Angles (in degrees)
COLOR_HARMONY_ANGLES = {
    'COMPLEMENTARY': 180,
    'ANALOGOUS': 30,
    'SPLIT_COMPLEMENTARY': 150,
    'TRIADIC': 120,
}

# Safe Area Percentages
SAFE_AREAS = {
    'ACTION': 0.90,  # 90% of frame
    'TITLE': 0.80,   # 80% of frame
}

# Aspect Ratios
ASPECT_RATIOS = {
    '16:9': 16/9,
    '4:3': 4/3,
    '21:9': 21/9,
    '1:1': 1.0,
    '9:16': 9/16,  # Vertical video
    '2.39:1': 2.39,  # Cinemascope
}

# Export Formats
EXPORT_FORMATS = {
    'PNG': {'ext': '.png', 'color_depth': '8', 'compression': 15},
    'JPEG': {'ext': '.jpg', 'quality': 90},
    'EXR': {'ext': '.exr', 'color_depth': '32', 'codec': 'ZIP'},
    'TIFF': {'ext': '.tif', 'color_depth': '16'},
}

# Video Codecs
VIDEO_CODECS = {
    'PRORES': {'codec': 'prores_ks', 'profile': 'hq'},
    'H264': {'codec': 'libx264', 'crf': 18},
    'H265': {'codec': 'libx265', 'crf': 22},
    'DNXHD': {'codec': 'dnxhd', 'bitrate': '185M'},
}

# Node Group Preset Categories
PRESET_CATEGORIES = [
    'COLOR_GRADING',
    'LOOK_DEVELOPMENT',
    'FILM_EMULATION',
    'STYLIZED',
    'HDR',
    'TECHNICAL',
    'FX',
]

# FX Types
FX_TYPES = {
    'HEAT_HAZE': 'Heat Distortion',
    'SHOCKWAVE': 'Shockwave',
    'MOTION_GLOW': 'Motion Glow',
    'METALLIC_SHEEN': 'Metallic Sheen',
    'CHROMATIC_ABERRATION': 'Chromatic Aberration',
    'LENS_DISTORTION': 'Lens Distortion',
}

# Edge Detection Methods
EDGE_DETECTION_METHODS = [
    ('SOBEL', 'Sobel', 'Sobel edge detection operator'),
    ('PREWITT', 'Prewitt', 'Prewitt edge detection operator'),
    ('LAPLACIAN', 'Laplacian', 'Laplacian edge detection'),
    ('CANNY', 'Canny', 'Canny edge detection (advanced)'),
]

# Default Node Colors (for visual organization)
NODE_COLORS = {
    'INPUT': (0.4, 0.6, 1.0),      # Blue
    'COLOR': (1.0, 0.6, 0.4),      # Orange
    'FILTER': (0.4, 1.0, 0.6),     # Green
    'VECTOR': (1.0, 0.4, 0.6),     # Pink
    'MATTE': (0.8, 0.8, 0.4),      # Yellow
    'OUTPUT': (0.6, 0.4, 1.0),     # Purple
}

# Fog Preset Values
FOG_PRESETS = {
    'LIGHT_MIST': {'density': 0.2, 'start': 10, 'end': 50},
    'MEDIUM_FOG': {'density': 0.5, 'start': 5, 'end': 25},
    'HEAVY_FOG': {'density': 0.8, 'start': 2, 'end': 15},
    'VOLUMETRIC_HAZE': {'density': 0.3, 'start': 0, 'end': 100},
}
