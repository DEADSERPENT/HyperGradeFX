"""
HyperGradeFX Error Handling and Logging
Centralized error handling and logging system
"""

import bpy
import traceback
from datetime import datetime
from pathlib import Path


class HGFXLogger:
    """Centralized logging system for HyperGradeFX"""

    LOG_LEVELS = {
        'DEBUG': 0,
        'INFO': 1,
        'WARNING': 2,
        'ERROR': 3,
        'CRITICAL': 4
    }

    def __init__(self, name="HyperGradeFX", log_to_file=False):
        self.name = name
        self.log_to_file = log_to_file
        self.log_file = None
        self.min_level = self.LOG_LEVELS['INFO']

        if log_to_file:
            self._setup_log_file()

    def _setup_log_file(self):
        """Setup log file in Blender's temporary directory"""
        try:
            import tempfile
            log_dir = Path(tempfile.gettempdir()) / "HyperGradeFX"
            log_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d")
            self.log_file = log_dir / f"hypergradefx_{timestamp}.log"

        except Exception as e:
            print(f"HyperGradeFX: Could not setup log file: {e}")
            self.log_to_file = False

    def _format_message(self, level, message):
        """Format log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.name}] [{level}] {message}"

    def _write_to_file(self, formatted_message):
        """Write message to log file"""
        if self.log_to_file and self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(formatted_message + '\n')
            except Exception:
                pass  # Silently fail file logging

    def log(self, level, message):
        """Log a message"""
        if self.LOG_LEVELS.get(level, 0) >= self.min_level:
            formatted = self._format_message(level, message)

            # Print to console
            print(formatted)

            # Write to file
            self._write_to_file(formatted)

    def debug(self, message):
        """Log debug message"""
        self.log('DEBUG', message)

    def info(self, message):
        """Log info message"""
        self.log('INFO', message)

    def warning(self, message):
        """Log warning message"""
        self.log('WARNING', message)

    def error(self, message):
        """Log error message"""
        self.log('ERROR', message)

    def critical(self, message):
        """Log critical message"""
        self.log('CRITICAL', message)

    def exception(self, message):
        """Log exception with traceback"""
        exc_info = traceback.format_exc()
        full_message = f"{message}\n{exc_info}"
        self.log('ERROR', full_message)


# Global logger instance
logger = HGFXLogger(log_to_file=True)


class ErrorHandler:
    """Centralized error handling with user-friendly messages"""

    @staticmethod
    def handle_error(operator, error, context="Operation"):
        """
        Handle error with logging and user notification

        Args:
            operator: Blender operator instance
            error: Exception or error message
            context: Context description

        Returns:
            set: {'CANCELLED'}
        """
        error_msg = str(error)

        # Log the error
        logger.error(f"{context} failed: {error_msg}")

        # Show user-friendly message
        if hasattr(operator, 'report'):
            operator.report({'ERROR'}, f"{context} failed: {error_msg}")

        return {'CANCELLED'}

    @staticmethod
    def safe_execute(func):
        """
        Decorator for safe operator execution with error handling

        Usage:
            @ErrorHandler.safe_execute
            def execute(self, context):
                # operator code
        """
        def wrapper(self, context):
            try:
                return func(self, context)
            except Exception as e:
                logger.exception(f"Error in {self.__class__.__name__}")
                self.report({'ERROR'}, f"Operation failed: {str(e)}")
                return {'CANCELLED'}

        return wrapper

    @staticmethod
    def validate_scene(context):
        """
        Validate scene setup for compositing

        Args:
            context: Blender context

        Returns:
            tuple: (is_valid, error_message)
        """
        scene = context.scene

        # Check if compositor is enabled
        if not scene.use_nodes:
            return False, "Compositor not enabled. Enable 'Use Nodes' in compositor"

        # Check if node tree exists
        if not scene.node_tree:
            return False, "No compositor node tree found"

        return True, ""

    @staticmethod
    def validate_context(context, required_areas=None):
        """
        Validate Blender context

        Args:
            context: Blender context
            required_areas: List of required area types

        Returns:
            tuple: (is_valid, error_message)
        """
        if not context:
            return False, "No context available"

        if not context.scene:
            return False, "No active scene"

        if required_areas:
            available_areas = [area.type for area in context.screen.areas]
            for req_area in required_areas:
                if req_area not in available_areas:
                    return False, f"Required area '{req_area}' not found"

        return True, ""


class OperationValidator:
    """Validates operations before execution"""

    @staticmethod
    def can_render(context):
        """Check if rendering is possible"""
        scene = context.scene

        if not scene.camera:
            return False, "No camera in scene"

        if scene.frame_start > scene.frame_end:
            return False, "Invalid frame range"

        return True, ""

    @staticmethod
    def can_export(context, output_path):
        """Check if export is possible"""
        from ..utils.security import SecurityValidator

        # Validate output path
        is_valid, error = SecurityValidator.validate_file_path(output_path)
        if not is_valid:
            return False, error

        # Check write permissions
        try:
            output_dir = Path(output_path).parent
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)

            # Test write access
            test_file = output_dir / ".write_test"
            test_file.touch()
            test_file.unlink()

        except Exception as e:
            return False, f"Cannot write to output directory: {e}"

        return True, ""

    @staticmethod
    def has_render_passes(context):
        """Check if required render passes are enabled"""
        view_layer = context.view_layer

        required_passes = []

        # Check if any passes are enabled
        passes_enabled = False
        for attr in dir(view_layer):
            if attr.startswith('use_pass_'):
                if getattr(view_layer, attr, False):
                    passes_enabled = True
                    break

        if not passes_enabled:
            return False, "No render passes enabled"

        return True, ""


class SafeOperator:
    """
    Mixin class for operators with built-in safety checks

    Usage:
        class MyOperator(SafeOperator, bpy.types.Operator):
            ...
    """

    def safe_report(self, level, message):
        """Safely report to user"""
        try:
            self.report({level}, message)
            logger.log(level, message)
        except Exception:
            print(f"{level}: {message}")

    def validate_and_execute(self, context, validation_func, execute_func):
        """
        Validate before executing

        Args:
            context: Blender context
            validation_func: Function to validate (returns tuple)
            execute_func: Function to execute if valid

        Returns:
            set: Operation result
        """
        # Validate
        is_valid, error = validation_func(context)

        if not is_valid:
            self.safe_report('ERROR', error)
            return {'CANCELLED'}

        # Execute with error handling
        try:
            return execute_func(context)
        except Exception as e:
            logger.exception(f"Error in {self.__class__.__name__}")
            self.safe_report('ERROR', f"Operation failed: {str(e)}")
            return {'CANCELLED'}


# Decorator for safe property updates
def safe_update(func):
    """
    Decorator for safe property update callbacks

    Usage:
        @safe_update
        def update_fog_density(self, context):
            # update code
    """
    def wrapper(self, context):
        try:
            return func(self, context)
        except Exception as e:
            logger.exception(f"Error in property update: {func.__name__}")
            print(f"Property update failed: {e}")

    return wrapper


# Context manager for safe operations
class SafeOperation:
    """
    Context manager for safe operations with cleanup

    Usage:
        with SafeOperation("Creating fog effect") as op:
            # operation code
    """

    def __init__(self, operation_name, cleanup_func=None):
        self.operation_name = operation_name
        self.cleanup_func = cleanup_func

    def __enter__(self):
        logger.info(f"Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.exception(f"Failed: {self.operation_name}")

            # Run cleanup if provided
            if self.cleanup_func:
                try:
                    self.cleanup_func()
                except Exception as e:
                    logger.error(f"Cleanup failed: {e}")

            return False  # Re-raise exception

        logger.info(f"Completed: {self.operation_name}")
        return True
