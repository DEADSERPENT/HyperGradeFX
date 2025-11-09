# HyperGradeFX Installation Guide

## Quick Installation

### Method 1: Direct Folder Install (Recommended)

1. **Copy the HyperGradeFX folder** to your Blender addons directory:

   **Windows:**
   ```
   C:\Users\[YourUsername]\AppData\Roaming\Blender Foundation\Blender\[Version]\scripts\addons\
   ```

   **macOS:**
   ```
   ~/Library/Application Support/Blender/[Version]/scripts/addons/
   ```

   **Linux:**
   ```
   ~/.config/blender/[Version]/scripts/addons/
   ```

2. **Restart Blender**

3. **Enable the addon:**
   - Edit → Preferences → Add-ons
   - Search for "HyperGradeFX"
   - Check the checkbox to enable

### Method 2: ZIP Install

1. **Compress the HyperGradeFX folder** to a ZIP file

2. **In Blender:**
   - Edit → Preferences → Add-ons
   - Click "Install..." button
   - Navigate to the ZIP file
   - Click "Install Add-on"

3. **Enable the addon:**
   - Search for "HyperGradeFX"
   - Check the checkbox

## Configuration

### Essential Settings

1. **Open Preferences:**
   ```
   Edit → Preferences → Add-ons → HyperGradeFX → Preferences
   ```

2. **Preset Directory** (Optional)
   ```
   Set custom location for storing your presets
   Default: Empty (uses addon's preset folder)

   Note: Leave empty to use the built-in presets folder,
   or set to a custom directory for your own presets
   ```

3. **FFmpeg Path** (Required for video export)
   ```
   Windows: C:\ffmpeg\bin\ffmpeg.exe
   macOS/Linux: /usr/local/bin/ffmpeg

   Download FFmpeg: https://ffmpeg.org/download.html
   ```

4. **Color Space** (Recommended: Linear)
   ```
   Linear - For physically accurate color
   sRGB - For standard displays
   ACES - For professional workflows
   ```

### Verifying Installation

1. **Switch to Compositor:**
   ```
   Top menu: Compositing workspace
   ```

2. **Check for HyperGradeFX panel:**
   ```
   Node Editor → Sidebar (press N) → HyperGradeFX tab
   ```

3. **Enable compositor:**
   ```
   Compositor → Use Nodes (checkbox in header)
   ```

4. **Test basic function:**
   ```
   HyperGradeFX → Enable All Render Passes
   HyperGradeFX → Auto-Connect Render Passes
   ```

## System Requirements

### Minimum
- Blender 3.6 or higher
- 4 GB RAM
- 2 GB free disk space
- GPU with OpenGL 4.3

### Recommended
- Blender 4.0 or higher
- 16 GB RAM
- 10 GB free disk space (for exports)
- NVIDIA/AMD GPU with 4GB VRAM
- FFmpeg installed for video export

## Optional Dependencies

### FFmpeg (Video Export)
**Windows:**
```
1. Download from https://www.gyan.dev/ffmpeg/builds/
2. Extract to C:\ffmpeg
3. Set path in HyperGradeFX preferences
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

### OpenImageIO (Advanced I/O)
Usually included with Blender, no additional install needed.

## Troubleshooting Installation

### "Add-on not showing in list"
- Ensure folder structure is correct (HyperGradeFX folder containing __init__.py)
- Check Python console for errors (Window → Toggle System Console)
- Verify Blender version compatibility (3.6+)

### "Add-on fails to enable"
- Check console for error messages
- Ensure all Python files are present
- Try reinstalling from scratch

### "FFmpeg not found"
- Verify FFmpeg is installed: `ffmpeg -version` in terminal
- Set correct path in preferences
- On Windows, ensure .exe is included in path

### "Preferences not saving"
- Blender Preferences → Save Preferences button
- Check file permissions on Blender config folder

## Post-Installation

### First Steps
1. Create a simple 3D scene
2. Switch to Compositor workspace
3. Enable "Use Nodes"
4. Open HyperGradeFX panel (N key)
5. Click "Enable All Render Passes"
6. Click "Auto-Connect Render Passes"
7. Explore the different panels!

### Loading Presets
Built-in presets are located in:
```
HyperGradeFX/presets/
- netflix_hdr.json
- grunge.json
- stylized_looks.json
- film_emulation.json
```

Load them via:
```
Node Blueprints → Load → Select JSON file
```

## Getting Help

- **Documentation:** README.md in the addon folder
- **Issues:** Report bugs on GitHub
- **Community:** Blender Artists Forum
- **Console:** Window → Toggle System Console (for errors)

## Updating HyperGradeFX

1. **Disable current version:**
   - Preferences → Add-ons → Uncheck HyperGradeFX

2. **Remove old version:**
   - Delete HyperGradeFX folder from addons directory

3. **Install new version:**
   - Follow installation steps above

4. **Restart Blender**

---

**You're all set! Start creating amazing post-production effects!** 🎨
