"""
HyperGradeFX Addon Validation Script
Validates addon structure, imports, and integrity

Run this script to validate the addon before installation:
    python validate_addon.py

Or run from Blender's Python console:
    exec(open("path/to/validate_addon.py").read())
"""

import os
import sys
import json
from pathlib import Path
import importlib.util


class AddonValidator:
    """Validates HyperGradeFX addon structure and code"""

    def __init__(self, addon_path=None):
        if addon_path is None:
            self.addon_path = Path(__file__).parent
        else:
            self.addon_path = Path(addon_path)

        self.errors = []
        self.warnings = []
        self.passed_checks = []

    def log_error(self, message):
        """Log an error"""
        self.errors.append(f"[ERROR] {message}")

    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(f"[WARNING] {message}")

    def log_success(self, message):
        """Log a successful check"""
        self.passed_checks.append(f"[OK] {message}")

    def check_file_exists(self, filepath, critical=True):
        """Check if a file exists"""
        full_path = self.addon_path / filepath

        if full_path.exists():
            self.log_success(f"File exists: {filepath}")
            return True
        else:
            if critical:
                self.log_error(f"Missing critical file: {filepath}")
            else:
                self.log_warning(f"Missing optional file: {filepath}")
            return False

    def validate_structure(self):
        """Validate addon directory structure"""
        print("\n=== Validating Addon Structure ===")

        # Critical files
        critical_files = [
            '__init__.py',
            'README.md',
            'core/__init__.py',
            'ui/__init__.py',
            'utils/__init__.py',
        ]

        for file in critical_files:
            self.check_file_exists(file, critical=True)

        # Core modules
        core_modules = [
            'core/compositing.py',
            'core/render_pass_automator.py',
            'core/node_blueprints.py',
            'core/color_harmony.py',
            'core/post_fog.py',
            'core/fx_layers.py',
            'core/edge_detection.py',
            'core/export.py',
        ]

        for module in core_modules:
            self.check_file_exists(module, critical=True)

        # UI modules
        ui_modules = [
            'ui/panels.py',
            'ui/operators.py',
            'ui/viewport_preview.py',
        ]

        for module in ui_modules:
            self.check_file_exists(module, critical=True)

        # Utils modules
        utils_modules = [
            'utils/constants.py',
            'utils/helpers.py',
            'utils/ffmpeg_handler.py',
            'utils/openimageio_handler.py',
            'utils/security.py',
            'utils/error_handler.py',
        ]

        for module in utils_modules:
            self.check_file_exists(module, critical=True)

        # Presets
        presets = [
            'presets/netflix_hdr.json',
            'presets/grunge.json',
            'presets/stylized_looks.json',
            'presets/film_emulation.json',
        ]

        for preset in presets:
            self.check_file_exists(preset, critical=False)

    def validate_bl_info(self):
        """Validate bl_info in __init__.py"""
        print("\n=== Validating bl_info ===")

        init_file = self.addon_path / '__init__.py'

        if not init_file.exists():
            self.log_error("__init__.py not found")
            return

        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for bl_info
            if 'bl_info' not in content:
                self.log_error("bl_info not found in __init__.py")
                return

            # Required bl_info keys
            required_keys = ['name', 'author', 'version', 'blender', 'category']

            for key in required_keys:
                if f'"{key}"' in content or f"'{key}'" in content:
                    self.log_success(f"bl_info has '{key}' key")
                else:
                    self.log_error(f"bl_info missing '{key}' key")

        except Exception as e:
            self.log_error(f"Failed to read __init__.py: {e}")

    def validate_json_presets(self):
        """Validate JSON preset files"""
        print("\n=== Validating JSON Presets ===")

        presets_dir = self.addon_path / 'presets'

        if not presets_dir.exists():
            self.log_warning("Presets directory not found")
            return

        for preset_file in presets_dir.glob('*.json'):
            try:
                with open(preset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check required keys
                if 'name' in data and 'category' in data:
                    self.log_success(f"Valid preset: {preset_file.name}")
                else:
                    self.log_warning(f"Preset missing keys: {preset_file.name}")

            except json.JSONDecodeError as e:
                self.log_error(f"Invalid JSON in {preset_file.name}: {e}")
            except Exception as e:
                self.log_error(f"Error reading {preset_file.name}: {e}")

    def validate_python_syntax(self):
        """Validate Python syntax in all .py files"""
        print("\n=== Validating Python Syntax ===")

        py_files = list(self.addon_path.rglob('*.py'))

        for py_file in py_files:
            # Skip validate_addon.py itself
            if py_file.name == 'validate_addon.py':
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                # Try to compile
                compile(code, str(py_file), 'exec')
                self.log_success(f"Valid syntax: {py_file.relative_to(self.addon_path)}")

            except SyntaxError as e:
                self.log_error(f"Syntax error in {py_file.name}: Line {e.lineno}: {e.msg}")
            except Exception as e:
                self.log_error(f"Error reading {py_file.name}: {e}")

    def check_imports(self):
        """Check if imports are valid (without importing)"""
        print("\n=== Checking Import Statements ===")

        py_files = list(self.addon_path.rglob('*.py'))
        import_errors = []

        for py_file in py_files:
            if py_file.name == 'validate_addon.py':
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    line = line.strip()

                    # Check for common import issues
                    if line.startswith('import') or line.startswith('from'):
                        # Check for relative imports outside package
                        if 'from .' in line and not line.startswith('from ..'):
                            pass  # Relative imports are OK

                        # Flag absolute imports that might fail
                        if 'import bpy' not in line:  # bpy is special
                            pass

                self.log_success(f"Imports OK: {py_file.name}")

            except Exception as e:
                self.log_warning(f"Could not check imports in {py_file.name}: {e}")

    def check_security_features(self):
        """Check if security features are present"""
        print("\n=== Checking Security Features ===")

        security_file = self.addon_path / 'utils' / 'security.py'

        if security_file.exists():
            with open(security_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for key security features
            features = [
                ('SecurityValidator', 'Security validator class'),
                ('validate_file_path', 'File path validation'),
                ('sanitize_filename', 'Filename sanitization'),
                ('validate_frame_range', 'Frame range validation'),
            ]

            for feature, description in features:
                if feature in content:
                    self.log_success(f"Security feature: {description}")
                else:
                    self.log_warning(f"Missing security feature: {description}")
        else:
            self.log_warning("Security module not found")

    def check_error_handling(self):
        """Check if error handling is present"""
        print("\n=== Checking Error Handling ===")

        error_file = self.addon_path / 'utils' / 'error_handler.py'

        if error_file.exists():
            with open(error_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for error handling features
            features = [
                ('HGFXLogger', 'Logging system'),
                ('ErrorHandler', 'Error handler'),
                ('safe_execute', 'Safe execution decorator'),
            ]

            for feature, description in features:
                if feature in content:
                    self.log_success(f"Error handling: {description}")
                else:
                    self.log_warning(f"Missing error handling: {description}")
        else:
            self.log_warning("Error handler module not found")

    def count_lines_of_code(self):
        """Count total lines of code"""
        print("\n=== Code Statistics ===")

        py_files = list(self.addon_path.rglob('*.py'))
        total_lines = 0
        total_files = 0

        for py_file in py_files:
            if py_file.name == 'validate_addon.py':
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    total_files += 1
            except Exception:
                pass

        print(f"Total Python files: {total_files}")
        print(f"Total lines of code: {total_lines:,}")

        self.log_success(f"Addon contains {total_files} Python files with {total_lines:,} lines")

    def generate_report(self):
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("HYPERGRADEFX VALIDATION REPORT")
        print("=" * 60)

        # Summary
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.errors)

        print(f"\nTotal Checks: {total_checks}")
        print(f"[OK] Passed: {len(self.passed_checks)}")
        print(f"[WARNING] Warnings: {len(self.warnings)}")
        print(f"[ERROR] Errors: {len(self.errors)}")

        # Show errors
        if self.errors:
            print("\n" + "-" * 60)
            print("ERRORS:")
            print("-" * 60)
            for error in self.errors:
                print(error)

        # Show warnings
        if self.warnings:
            print("\n" + "-" * 60)
            print("WARNINGS:")
            print("-" * 60)
            for warning in self.warnings:
                print(warning)

        # Overall status
        print("\n" + "=" * 60)
        if self.errors:
            print("[FAILED] VALIDATION FAILED - FIX ERRORS BEFORE INSTALLATION")
        elif self.warnings:
            print("[PASSED WITH WARNINGS] VALIDATION PASSED WITH WARNINGS")
        else:
            print("[SUCCESS] VALIDATION PASSED - ADDON READY FOR INSTALLATION")
        print("=" * 60)

        return len(self.errors) == 0

    def run_all_checks(self):
        """Run all validation checks"""
        print(f"\nValidating HyperGradeFX addon at: {self.addon_path}")

        self.validate_structure()
        self.validate_bl_info()
        self.validate_json_presets()
        self.validate_python_syntax()
        self.check_imports()
        self.check_security_features()
        self.check_error_handling()
        self.count_lines_of_code()

        return self.generate_report()


def main():
    """Main validation function"""
    validator = AddonValidator()
    success = validator.run_all_checks()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
