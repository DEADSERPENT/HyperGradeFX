# HyperGradeFX
**Professional-grade Post-Production Suite for Blender**

Transform your 3D renders into cinematic masterpieces with HyperGradeFX - a comprehensive compositing and color grading addon that brings Hollywood-level post-production tools directly into Blender.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/DEADSERPENT/hypergradefx)
[![Blender](https://img.shields.io/badge/Blender-3.6%2B-orange.svg)](https://www.blender.org)
[![License](https://img.shields.io/badge/license-GPL-green.svg)](LICENSE)

---

## Features

### Core Capabilities

#### Professional Color Grading
- **7-Stage Color Grade Stack** - Industry-standard lift, gamma, gain workflow
- **Split Toning** - Separate control over shadow and highlight colors
- **Color Harmony Tools** - Complementary, analogous, triadic, and split-complementary harmonies
- **Look Presets** - Netflix HDR, film emulation, vintage, grunge, and more
- **Broadcast-Safe Levels** - Automatic scoping and limiting

#### Advanced Compositing
- **Auto-Connect Render Passes** - Intelligent node graph generation
- **Node Blueprints System** - Save, load, and share complex node setups
- **Multi-Sequence Management** - Handle multiple shots in one project
- **Smart Pass Detection** - Automatically recognizes and uses render layers

#### 3D Post-Processing Effects
- **Depth-Based Fog** - Realistic atmospheric effects using Z-depth
- **Volumetric Rays** - God rays and volumetric lighting
- **Heat Haze/Distortion** - Animated heat shimmer effects
- **Depth of Field Enhancement** - Advanced DOF controls

#### Edge Detection & Masking
- **Multi-Algorithm Edge Detection** - Sobel, Prewitt, Roberts, Canny methods
- **Neon Glow Effects** - Cyberpunk-style edge illumination
- **Edge-Aware Masking** - Selective effect application
- **Luminance Isolation** - Precise color and tonal targeting

#### FX Layers
- **Chromatic Aberration** - Lens-style color fringing
- **Motion-Based Glow** - Speed-reactive particle trails
- **Film Grain** - Authentic film texture simulation
- **Vignetting** - Customizable lens darkening

#### Export & Automation
- **Batch Frame Export** - Multiple formats (EXR, PNG, JPEG, TIFF)
- **Video Export** - H.264, ProRes, DNxHD support via FFmpeg
- **Sequence Batch Rendering** - Render multiple shots automatically
- **Preset Management** - Save and recall complete grade setups

---

## Installation

### Quick Install

1. **Download** the HyperGradeFX folder
2. **Copy** to your Blender addons directory:
   - Windows: `C:\Users\[YourUsername]\AppData\Roaming\Blender Foundation\Blender\[Version]\scripts\addons\`
   - macOS: `~/Library/Application Support/Blender/[Version]/scripts/addons/`
   - Linux: `~/.config/blender/[Version]/scripts/addons/`
3. **Restart Blender**
4. **Enable** in Edit → Preferences → Add-ons → Search "HyperGradeFX"

For detailed installation instructions, see [INSTALL.md](INSTALL.md)

---

## Quick Start

### Your First Color Grade

1. **Render** your scene or open an existing render
2. **Switch** to the Compositor workspace
3. **Enable** "Use Nodes" in the compositor
4. **Open** the HyperGradeFX panel (press `N` in Node Editor)
5. Click **"Enable All Render Passes"**
6. Click **"Auto-Connect Render Passes"**
7. Navigate to **Color Grading** → **Create Color Grade Stack**
8. Adjust color wheels to taste
9. **Export** your final image or video

### Load a Preset

1. Go to **Node Blueprints** panel
2. Click **Load**
3. Navigate to `HyperGradeFX/presets/`
4. Select a preset JSON file (e.g., `netflix_hdr.json`)
5. Click **Apply** to instantly apply the look

---

## System Requirements

### Minimum
- Blender 3.6 or higher
- 4 GB RAM
- 2 GB free disk space
- GPU with OpenGL 4.3 support

### Recommended
- Blender 4.0 or higher
- 16 GB RAM
- 10 GB free disk space
- NVIDIA/AMD GPU with 4GB VRAM
- FFmpeg installed (for video export)

---

## Key Workflows

### Cinematic Teal & Orange Look
```
1. Auto-Connect Render Passes
2. Load stylized_looks.json preset
3. Apply "Stylized Teal & Orange"
4. Create Split Tone Effect:
   - Shadows: Teal (0.2, 0.4, 0.5)
   - Highlights: Orange (1.0, 0.6, 0.3)
5. Adjust strength to 0.7
```

### Atmospheric Fog Scene
```
1. Enable All Render Passes (ensure Z-depth is on)
2. 3D Post-Fog → Apply Post-Fog
3. Set Density: 0.5
4. Start Distance: 10, End Distance: 50
5. Choose fog color to match scene lighting
6. Optional: Create Volumetric Rays for god rays
```

### Cyberpunk Neon Glow
```
1. Auto-Connect Render Passes
2. Edge Effects → Detect Edges (Sobel method)
3. Edge Effects → Create Neon Glow
4. Glow Color: Cyan (0.0, 1.0, 1.0)
5. Intensity: 3.0, Blur Size: 25
6. Add Chromatic Aberration (strength 0.02)
```

For more examples and advanced techniques, see [EXAMPLES.md](EXAMPLES.md)

---

## Built-in Presets

HyperGradeFX includes professionally crafted presets:

- **netflix_hdr.json** - Netflix-style HDR grading with wide dynamic range
- **film_emulation.json** - Vintage film looks (Kodak, Fuji, etc.)
- **stylized_looks.json** - Teal & Orange, Blade Runner, Mad Max styles
- **grunge.json** - Gritty, desaturated, high-contrast aesthetics

Load them from the Node Blueprints panel to instantly apply professional grades.

---

## Documentation

- **[INSTALL.md](INSTALL.md)** - Detailed installation and configuration
- **[EXAMPLES.md](EXAMPLES.md)** - 10+ complete workflows and recipes
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Technical architecture
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates

---

## Tips for Best Results

### Color Grading
- Work in order: Exposure → White Balance → Contrast → Color
- Use scopes to ensure broadcast-safe levels
- Reference real films for inspiration
- Subtle adjustments often look better than extreme changes

### Performance
- Use lower resolution for testing complex node setups
- Disable live preview when working on heavy scenes
- Organize nodes with frames for better readability
- Save incremental versions of your .blend files

### Export
- Test small frame ranges before full batch export
- Keep uncompressed EXR frames separate from compressed video
- Verify codec compatibility with your delivery platform
- Document your settings for client revisions

---

## Troubleshooting

### Common Issues

**Panel not showing**
- Press `N` in the Node Editor to show sidebar
- Ensure you're in the Compositor workspace
- Check that "Use Nodes" is enabled

**FFmpeg not found**
- Install FFmpeg: https://ffmpeg.org/download.html
- Set path in HyperGradeFX preferences
- On Windows, include `.exe` in the path

**Nodes not connecting automatically**
- Enable "Auto-Connect Render Passes" in preferences
- Ensure render passes are enabled in View Layer Properties
- Try manual connection first, then report bug if persistent

**Performance issues**
- Reduce compositor resolution in scene properties
- Disable live preview in preferences
- Close unused Blender windows
- Upgrade GPU drivers

For more troubleshooting, see [INSTALL.md](INSTALL.md)

---

## Contributing

We welcome contributions! Whether it's:
- Bug reports and fixes
- New preset creation
- Feature suggestions
- Documentation improvements
- Tutorial creation

Please open an issue or pull request on GitHub.

---

## Credits

**Developer:** DEADSERPENT
**Version:** 1.0.0
**Category:** Compositing
**License:** GPL

---

## Support

- **Documentation:** This README and supporting .md files
- **Issues:** [GitHub Issues](https://github.com/DEADSERPENT/hypergradefx/issues)
- **Community:** Blender Artists Forum
- **Updates:** Follow project on GitHub

---

## License

HyperGradeFX is released under the GNU General Public License v3.0 or later.

See LICENSE file for full details.

---

## Changelog

### Version 1.0.0 (Current)
- Initial release
- 7-stage color grading system
- Auto-connect render passes
- Node blueprint system
- 3D post-fog and depth effects
- Edge detection and neon glow
- FX layers (chromatic aberration, motion glow)
- Multi-format export pipeline
- Built-in professional presets
- Color harmony tools
- Sequence management

For detailed changelog, see [CHANGELOG.md](CHANGELOG.md)

---

**Transform your renders. Elevate your art. Create cinematic magic with HyperGradeFX.**
