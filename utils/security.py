"""
HyperGradeFX Security Module
Input validation, sanitization, and security utilities
"""

import os
import re
from pathlib import Path


class SecurityValidator:
    """Validates and sanitizes user inputs for security"""

    # Allowed file extensions for various operations
    ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.exr', '.tif', '.tiff', '.bmp', '.hdr'}
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
    ALLOWED_PRESET_EXTENSIONS = {'.json', '.blend'}

    # Maximum safe values
    MAX_FRAME_COUNT = 100000
    MAX_FILE_SIZE_MB = 1000
    MAX_PATH_LENGTH = 260  # Windows MAX_PATH
    MAX_BLUR_SIZE = 500
    MAX_SAMPLES = 1000

    @staticmethod
    def validate_file_path(filepath, must_exist=False, allowed_extensions=None):
        """
        Validate file path for security issues

        Args:
            filepath: Path to validate
            must_exist: Whether file must exist
            allowed_extensions: Set of allowed extensions

        Returns:
            tuple: (is_valid, error_message)
        """
        if not filepath:
            return False, "Empty file path"

        try:
            # Convert to Path object
            path = Path(filepath)

            # Check for path traversal attempts
            if '..' in str(path):
                return False, "Path traversal detected - '..' not allowed"

            # Check path length
            if len(str(path)) > SecurityValidator.MAX_PATH_LENGTH:
                return False, f"Path too long (max {SecurityValidator.MAX_PATH_LENGTH})"

            # Check for dangerous characters
            dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
            for char in dangerous_chars:
                if char in str(path.name):
                    return False, f"Dangerous character '{char}' in filename"

            # Check extension if specified
            if allowed_extensions:
                ext = path.suffix.lower()
                if ext not in allowed_extensions:
                    return False, f"Extension '{ext}' not allowed"

            # Check existence if required
            if must_exist and not path.exists():
                return False, "File does not exist"

            return True, ""

        except Exception as e:
            return False, f"Invalid path: {str(e)}"

    @staticmethod
    def validate_directory_path(dirpath, create_if_missing=False):
        """
        Validate directory path

        Args:
            dirpath: Directory path to validate
            create_if_missing: Create directory if it doesn't exist

        Returns:
            tuple: (is_valid, error_message)
        """
        if not dirpath:
            return False, "Empty directory path"

        try:
            path = Path(dirpath)

            # Check for path traversal
            if '..' in str(path):
                return False, "Path traversal detected"

            # Check path length
            if len(str(path)) > SecurityValidator.MAX_PATH_LENGTH:
                return False, "Path too long"

            # Create if needed
            if create_if_missing:
                path.mkdir(parents=True, exist_ok=True)

            return True, ""

        except Exception as e:
            return False, f"Invalid directory: {str(e)}"

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize filename by removing dangerous characters

        Args:
            filename: Filename to sanitize

        Returns:
            str: Sanitized filename
        """
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext

        return filename or "unnamed"

    @staticmethod
    def validate_frame_range(start, end):
        """
        Validate frame range

        Args:
            start: Start frame
            end: End frame

        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(start, int) or not isinstance(end, int):
            return False, "Frame numbers must be integers"

        if start < 0 or end < 0:
            return False, "Frame numbers must be positive"

        if start > end:
            return False, "Start frame must be <= end frame"

        if (end - start) > SecurityValidator.MAX_FRAME_COUNT:
            return False, f"Too many frames (max {SecurityValidator.MAX_FRAME_COUNT})"

        return True, ""

    @staticmethod
    def validate_numeric_input(value, min_val=None, max_val=None, value_type=float):
        """
        Validate numeric input

        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            value_type: Expected type (int or float)

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Convert to expected type
            if value_type == int:
                value = int(value)
            else:
                value = float(value)

            # Check range
            if min_val is not None and value < min_val:
                return False, f"Value must be >= {min_val}"

            if max_val is not None and value > max_val:
                return False, f"Value must be <= {max_val}"

            return True, ""

        except (ValueError, TypeError):
            return False, f"Invalid {value_type.__name__} value"

    @staticmethod
    def validate_color(color):
        """
        Validate color tuple

        Args:
            color: Color tuple (R, G, B) or (R, G, B, A)

        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(color, (tuple, list)):
            return False, "Color must be tuple or list"

        if len(color) not in (3, 4):
            return False, "Color must have 3 or 4 components"

        for component in color:
            if not isinstance(component, (int, float)):
                return False, "Color components must be numeric"

            if component < 0 or component > 1:
                return False, "Color components must be 0-1"

        return True, ""

    @staticmethod
    def validate_string_input(text, max_length=1000, allow_empty=False):
        """
        Validate string input

        Args:
            text: String to validate
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed

        Returns:
            tuple: (is_valid, error_message)
        """
        if not allow_empty and not text:
            return False, "Empty string not allowed"

        if not isinstance(text, str):
            return False, "Input must be a string"

        if len(text) > max_length:
            return False, f"String too long (max {max_length})"

        # Check for null bytes
        if '\x00' in text:
            return False, "Null bytes not allowed"

        return True, ""

    @staticmethod
    def validate_json_data(data, max_size_kb=1024):
        """
        Validate JSON data size

        Args:
            data: JSON data (dict or list)
            max_size_kb: Maximum size in KB

        Returns:
            tuple: (is_valid, error_message)
        """
        import json

        try:
            # Serialize to check size
            json_str = json.dumps(data)
            size_kb = len(json_str.encode('utf-8')) / 1024

            if size_kb > max_size_kb:
                return False, f"JSON data too large ({size_kb:.1f}KB > {max_size_kb}KB)"

            return True, ""

        except Exception as e:
            return False, f"Invalid JSON data: {str(e)}"

    @staticmethod
    def is_safe_command(command):
        """
        Check if shell command is safe (basic check)

        Args:
            command: Command string

        Returns:
            bool: True if safe, False otherwise
        """
        # Dangerous patterns
        dangerous_patterns = [
            r';\s*rm\s',  # Remove commands
            r';\s*del\s',  # Delete commands
            r'\|\s*rm\s',  # Piped remove
            r'&&\s*rm\s',  # Chained remove
            r'`.*`',  # Command substitution
            r'\$\(',  # Command substitution
            r'>\s*/dev/',  # Writing to system devices
            r'>\s*/proc/',  # Writing to proc
            r';\s*shutdown',  # Shutdown commands
            r';\s*reboot',  # Reboot commands
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False

        return True


class PathSanitizer:
    """Sanitizes file paths for safe operations"""

    @staticmethod
    def normalize_path(path, base_dir=None):
        """
        Normalize and validate path against base directory

        Args:
            path: Path to normalize
            base_dir: Base directory to validate against

        Returns:
            Path: Normalized path or None if invalid
        """
        try:
            path = Path(path).resolve()

            if base_dir:
                base_dir = Path(base_dir).resolve()

                # Ensure path is within base directory
                if not str(path).startswith(str(base_dir)):
                    return None

            return path

        except Exception:
            return None

    @staticmethod
    def safe_join(*parts):
        """
        Safely join path parts

        Args:
            *parts: Path components to join

        Returns:
            str: Joined path or None if invalid
        """
        try:
            path = Path(*parts).resolve()

            # Check for traversal
            for part in parts:
                if '..' in str(part):
                    return None

            return str(path)

        except Exception:
            return None


# Convenience functions
def validate_and_sanitize_filepath(filepath, allowed_extensions=None):
    """Validate and sanitize file path"""
    is_valid, error = SecurityValidator.validate_file_path(
        filepath,
        allowed_extensions=allowed_extensions
    )
    if not is_valid:
        raise ValueError(error)

    return SecurityValidator.sanitize_filename(Path(filepath).name)


def safe_float_input(value, min_val=0.0, max_val=1.0):
    """Safely convert and validate float input"""
    is_valid, error = SecurityValidator.validate_numeric_input(
        value,
        min_val=min_val,
        max_val=max_val,
        value_type=float
    )
    if not is_valid:
        raise ValueError(error)

    return float(value)


def safe_int_input(value, min_val=0, max_val=1000):
    """Safely convert and validate integer input"""
    is_valid, error = SecurityValidator.validate_numeric_input(
        value,
        min_val=min_val,
        max_val=max_val,
        value_type=int
    )
    if not is_valid:
        raise ValueError(error)

    return int(value)
