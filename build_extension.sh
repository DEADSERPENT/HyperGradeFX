#!/bin/bash
# Build script for HyperGradeFX extension
# Usage: ./build_extension.sh

set -e

echo -e "\033[0;36mBuilding HyperGradeFX Extension...\033[0m"

# Configuration
EXTENSION_NAME="hypergradefx"
VERSION="1.0.0"
OUTPUT_NAME="${EXTENSION_NAME}-${VERSION}.zip"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SOURCE_DIR")"

# Check if blender_manifest.toml exists
if [ ! -f "$SOURCE_DIR/blender_manifest.toml" ]; then
    echo -e "\033[0;31mERROR: blender_manifest.toml not found!\033[0m"
    echo -e "\033[0;33mPlease ensure the manifest file exists in the root directory.\033[0m"
    exit 1
fi

echo -e "\033[0;90mSource directory: $SOURCE_DIR\033[0m"
echo -e "\033[0;90mOutput file: $OUTPUT_NAME\033[0m"

# Method 1: Try using Blender's CLI (if available)
BLENDER_PATHS=(
    "/usr/bin/blender"
    "/usr/local/bin/blender"
    "/Applications/Blender.app/Contents/MacOS/Blender"
    "$HOME/Applications/Blender.app/Contents/MacOS/Blender"
)

BLENDER_EXE=""
for path in "${BLENDER_PATHS[@]}"; do
    if [ -x "$path" ]; then
        BLENDER_EXE="$path"
        break
    fi
done

if [ -n "$BLENDER_EXE" ]; then
    echo -e "\n\033[0;36mAttempting to build with Blender CLI...\033[0m"
    echo -e "\033[0;90mBlender found at: $BLENDER_EXE\033[0m"

    if "$BLENDER_EXE" --command extension build "$SOURCE_DIR" --output-dir "$PARENT_DIR" 2>/dev/null; then
        if [ -f "$PARENT_DIR/$OUTPUT_NAME" ]; then
            echo -e "\n\033[0;32m[SUCCESS] Extension built successfully!\033[0m"
            echo -e "\033[0;32mOutput: $PARENT_DIR/$OUTPUT_NAME\033[0m"
            echo -e "\n\033[0;36mYou can now upload this file to Blender Extension Platform:\033[0m"
            echo -e "\033[0;34mhttps://extensions.blender.org/\033[0m"
            exit 0
        fi
    else
        echo -e "\033[0;33mBlender CLI method failed, falling back to manual packaging...\033[0m"
    fi
else
    echo -e "\033[0;33mBlender 4.2+ not found, using manual packaging...\033[0m"
fi

# Method 2: Manual packaging
echo -e "\n\033[0;36mCreating zip file manually...\033[0m"

OUTPUT_PATH="$PARENT_DIR/$OUTPUT_NAME"

# Remove old zip if exists
if [ -f "$OUTPUT_PATH" ]; then
    rm -f "$OUTPUT_PATH"
    echo -e "\033[0;90mRemoved existing $OUTPUT_NAME\033[0m"
fi

# Create the zip
echo -e "\033[0;90mCreating archive...\033[0m"
cd "$PARENT_DIR"

zip -r "$OUTPUT_NAME" "$(basename "$SOURCE_DIR")" \
    -x "**/__pycache__/*" \
    -x "**/*.pyc" \
    -x "**/*.pyo" \
    -x "**/.git/*" \
    -x "**/.gitignore" \
    -x "**/*.md" \
    -x "**/validate_addon.py" \
    -x "**/requirements.txt" \
    -x "**/.vscode/*" \
    -x "**/.idea/*" \
    -x "**/*.zip" \
    -x "**/build_extension.ps1" \
    -x "**/build_extension.sh" \
    > /dev/null

if [ -f "$OUTPUT_PATH" ]; then
    echo -e "\n\033[0;32m[SUCCESS] Extension packaged successfully!\033[0m"
    echo -e "\033[0;32mOutput: $OUTPUT_PATH\033[0m"

    # Show file size
    FILE_SIZE=$(du -h "$OUTPUT_PATH" | cut -f1)
    echo -e "\033[0;90mSize: $FILE_SIZE\033[0m"

    echo -e "\n\033[0;36mNext steps:\033[0m"
    echo -e "\033[0;37m1. Validate: blender --command extension validate \"$SOURCE_DIR\"\033[0m"
    echo -e "\033[0;34m2. Upload to: https://extensions.blender.org/\033[0m"
else
    echo -e "\n\033[0;31m[ERROR] Failed to create extension package!\033[0m"
    exit 1
fi
