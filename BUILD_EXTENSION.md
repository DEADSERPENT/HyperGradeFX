# Building HyperGradeFX for Blender Extension Platform

This guide explains how to package HyperGradeFX for the Blender 4.2+ Extension Platform.

## Prerequisites

- Blender 4.2 or later installed
- The `blender_manifest.toml` file is now in the root directory

## Method 1: Using Blender's Command-Line Tool (Recommended)

Blender provides a built-in command to build extensions. This is the official and recommended method.

### Windows:

```bash
# Navigate to your Blender installation directory
cd "C:\Program Files\Blender Foundation\Blender 4.2"

# Build the extension
blender.exe --command extension build "C:\Users\AKSHAY\Music\HyperGradeFX"
```

### Linux/Mac:

```bash
blender --command extension build "/path/to/HyperGradeFX"
```

This will create a `.zip` file in the same directory with the naming format: `hypergradefx-1.0.0.zip`

## Method 2: Manual Packaging

If you prefer to package manually or the command-line tool isn't working:

### Windows (PowerShell):

```powershell
# Navigate to the parent directory
cd C:\Users\AKSHAY\Music

# Create the zip file
Compress-Archive -Path "HyperGradeFX\*" -DestinationPath "hypergradefx-1.0.0.zip" -Force -CompressionLevel Optimal
```

### Linux/Mac:

```bash
# Navigate to the parent directory
cd ~/Music

# Create the zip file
zip -r hypergradefx-1.0.0.zip HyperGradeFX/ -x "*.pyc" -x "__pycache__/*" -x ".git/*" -x "*.md" -x "validate_addon.py"
```

## What Gets Included

The `blender_manifest.toml` file automatically excludes:
- `__pycache__/` directories
- `.pyc` and `.pyo` files
- `.git/` directory
- Documentation files (`.md`)
- `validate_addon.py`
- Development files

## Files That MUST Be Included

Ensure these are in the .zip:
- `blender_manifest.toml` (required!)
- `__init__.py`
- `LICENSE`
- All `core/`, `ui/`, and `utils/` directories
- All `presets/` directory (if present)

## Validating Your Extension

Before uploading, validate your extension:

```bash
blender --command extension validate "C:\Users\AKSHAY\Music\HyperGradeFX"
```

## Uploading to Blender Extension Platform

1. Go to: https://extensions.blender.org/
2. Log in with your account
3. Click "Submit Extension"
4. Upload the `.zip` file generated above
5. Fill in any additional metadata
6. Submit for review

## Troubleshooting

### "Manifest file is missing"
- Ensure `blender_manifest.toml` is in the root of the addon directory
- Ensure it's included in the .zip file at the root level

### "Only .zip files are accepted"
- The file must have a `.zip` extension
- Don't use `.tar.gz`, `.rar`, or other formats

### "Invalid manifest"
- Run validation: `blender --command extension validate "path/to/addon"`
- Check that `schema_version`, `id`, `name`, and `version` are present

### "Build command not found"
- Update to Blender 4.2 or later
- Ensure you're using the correct Blender executable path

## Testing the Extension

After building, test installation:

1. Open Blender 4.2+
2. Go to Edit > Preferences > Get Extensions
3. Click the dropdown (top-right) > Install from Disk
4. Select your `.zip` file
5. Enable "HyperGradeFX" in the extensions list

## Additional Resources

- Blender Extension Platform: https://extensions.blender.org/
- Extension Documentation: https://docs.blender.org/manual/en/latest/extensions/index.html
- Manifest Schema: https://docs.blender.org/manual/en/latest/extensions/manifest.html
