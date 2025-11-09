# HyperGradeFX Project Structure

## Directory Layout

```
HyperGradeFX/
├── __init__.py                 # Main addon entry point with bl_info
│
├── core/                       # Core compositing functionality
│   ├── __init__.py            # Core module registration
│   ├── compositing.py         # Sequence-Based Compositing System (SBCS)
│   ├── render_pass_automator.py  # Render Pass Automator (RPA)
│   ├── node_blueprints.py     # Node Group Blueprints (NGB)
│   ├── color_harmony.py       # Dynamic Color Harmony Engine
│   ├── post_fog.py            # 3D Post-Fog with Shadow Mapping
│   ├── fx_layers.py           # Post-Action FX Layer System
│   ├── edge_detection.py      # Edge-Aware Color Isolation
│   └── export.py              # Export and Automation Tools
│
├── ui/                         # User interface components
│   ├── __init__.py            # UI module registration
│   ├── panels.py              # Main UI panels
│   ├── operators.py           # UI-specific operators
│   └── viewport_preview.py    # Live Post Preview Viewport
│
├── utils/                      # Utility functions
│   ├── __init__.py            # Utils module registration
│   ├── constants.py           # Global constants
│   ├── helpers.py             # Helper functions
│   ├── ffmpeg_handler.py      # FFmpeg integration
│   └── openimageio_handler.py # OpenImageIO integration
│
├── presets/                    # Preset libraries
│   ├── netflix_hdr.json       # Netflix HDR preset
│   ├── grunge.json            # Grunge look preset
│   ├── stylized_looks.json    # Teal & Orange preset
│   └── film_emulation.json    # Vintage film preset
│
├── README.md                   # Main documentation
├── INSTALL.md                  # Installation guide
├── EXAMPLES.md                 # Usage examples
├── PROJECT_STRUCTURE.md        # This file
└── LICENSE                     # GPL v3 License (optional)
```

## Module Overview

### Core Modules

#### `__init__.py` (Main Entry)
- Blender addon registration
- bl_info metadata
- Addon preferences
- Scene properties
- Module initialization

#### `core/compositing.py`
**Classes:**
- `HGFXSequence` - Sequence data storage
- `HGFXSequenceManager` - Sequence management
- `HGFX_OT_AddSequence` - Add new sequence
- `HGFX_OT_RemoveSequence` - Remove sequence
- `HGFX_OT_ApplySequence` - Apply sequence setup
- `HGFX_OT_BatchApplySequences` - Batch render
- `HGFX_OT_SaveSequencePreset` - Save preset
- `HGFX_OT_LoadSequencePreset` - Load preset

**Features:**
- Shot-level compositing
- Node tree capture/restore
- Batch rendering
- Preset management

#### `core/render_pass_automator.py`
**Classes:**
- `HGFX_OT_AutoConnectRenderPasses` - Auto-connect passes
- `HGFX_OT_EnableRenderPasses` - Enable all passes
- `HGFX_OT_CreatePassMask` - Create pass masks

**Features:**
- Automatic pass detection
- Optimized network creation
- Pass-specific setups (Diffuse, AO, Shadow, etc.)
- Mask generation

#### `core/node_blueprints.py`
**Classes:**
- `HGFXNodeBlueprint` - Blueprint data
- `HGFX_UL_BlueprintList` - UI list
- `HGFX_OT_ApplyBlueprint` - Apply preset
- `HGFX_OT_SaveBlueprint` - Save selection
- `HGFX_OT_LoadBlueprintPreset` - Load from file
- `HGFX_OT_DeleteBlueprint` - Delete preset

**Features:**
- Node group creation
- Preset library
- Import/export
- Built-in presets

#### `core/color_harmony.py`
**Classes:**
- `HGFX_OT_ApplyColorHarmony` - Apply harmony
- `HGFX_OT_CreateSplitToneEffect` - Split toning
- `HGFX_OT_CreateColorGradeStack` - Full grade stack
- `HGFX_OT_ApplyLookPreset` - Look presets

**Features:**
- Color theory automation
- Complementary/Analogous/Triadic harmonies
- Split toning
- 7-stage grading stack
- Look presets (Cinematic, Vibrant, etc.)

#### `core/post_fog.py`
**Classes:**
- `HGFX_OT_ApplyPostFog` - Apply fog
- `HGFX_OT_ApplyFogPreset` - Fog presets
- `HGFX_OT_CreateVolumetricRays` - God rays
- `HGFX_OT_AnimateFog` - Animate fog

**Features:**
- Z-depth based fog
- Exponential/linear falloff
- Shadow scattering
- Volumetric effects
- Animation support

#### `core/fx_layers.py`
**Classes:**
- `HGFX_OT_CreateHeatHaze` - Heat distortion
- `HGFX_OT_CreateShockwave` - Shockwave effect
- `HGFX_OT_CreateMotionGlow` - Motion glow
- `HGFX_OT_CreateChromaticAberration` - Chromatic aberration
- `HGFX_OT_CreateLensDistortion` - Lens distortion

**Features:**
- Environmental effects
- Lens effects
- Vector pass integration
- Procedural FX

#### `core/edge_detection.py`
**Classes:**
- `HGFX_OT_DetectEdges` - Edge detection
- `HGFX_OT_CreateNeonGlow` - Neon glow
- `HGFX_OT_CreateOutlineEffect` - Cel-shading

**Features:**
- Sobel/Prewitt/Laplacian/Canny detection
- Normal pass integration
- Customizable effects

#### `core/export.py`
**Classes:**
- `HGFX_OT_BatchExportFrames` - Batch frames
- `HGFX_OT_ExportToVideo` - Video export
- `HGFX_OT_QuickExport` - Quick export
- `HGFX_OT_ExportCompStack` - Export comp setup
- `HGFX_OT_CreateContactSheet` - Contact sheet

**Features:**
- Multiple format support
- FFmpeg integration
- Quality presets
- Batch processing

### UI Modules

#### `ui/panels.py`
**Panels:**
- `HGFX_PT_MainPanel` - Main panel
- `HGFX_PT_SequencePanel` - Sequences
- `HGFX_PT_ColorGradingPanel` - Color grading
- `HGFX_PT_BlueprintsPanel` - Blueprints
- `HGFX_PT_FogPanel` - Fog effects
- `HGFX_PT_FXPanel` - FX layers
- `HGFX_PT_EdgePanel` - Edge effects
- `HGFX_PT_ExportPanel` - Export tools
- `HGFX_PT_SafeAreaPanel` - Safe areas
- `HGFX_PT_MaskPanel` - Mask drawing
- `HGFX_PT_RenderPassPanel` - Render passes

#### `ui/operators.py`
**Operators:**
- Safe area overlay
- Aspect ratio guides
- Mask layer creation
- Mask editing tools
- Preview controls

#### `ui/viewport_preview.py`
**Features:**
- Live preview toggle
- Safe area overlay rendering
- Side-by-side comparison
- Pixel inspector
- Scope displays

### Utility Modules

#### `utils/constants.py`
**Constants:**
- Version info
- Render pass names
- Color harmony angles
- Export formats
- Video codecs
- FX types
- Fog presets

#### `utils/helpers.py`
**Functions:**
- Node tree operations
- Color conversions
- Color harmony calculations
- Node creation helpers
- Connection utilities

#### `utils/ffmpeg_handler.py`
**Class:** `FFmpegHandler`
**Features:**
- Image sequence encoding
- Video creation
- Proxy generation
- Frame extraction
- Video info

#### `utils/openimageio_handler.py`
**Class:** `ImageIOHandler`
**Features:**
- Image loading/saving
- Pixel data manipulation
- Color space conversion
- Batch export
- Metadata handling

## File Counts

```
Total Python files: 17
Total JSON presets: 4
Total documentation files: 4

Lines of code (approximate):
- Core modules: ~3,500 lines
- UI modules: ~800 lines
- Utils modules: ~700 lines
- Total: ~5,000 lines
```

## Dependencies

**Python Standard Library:**
- json
- subprocess
- pathlib
- colorsys

**Blender API:**
- bpy (all modules)
- gpu (viewport rendering)
- gpu_extras (batch rendering)

**External (Optional):**
- FFmpeg (video export)
- OpenImageIO (via Blender)

## Features by File

| File | Primary Features |
|------|------------------|
| compositing.py | SBCS, Sequences, Batch rendering |
| render_pass_automator.py | RPA, Auto-connection, Pass masks |
| node_blueprints.py | NGB, Preset system, Templates |
| color_harmony.py | Color theory, Grading, Looks |
| post_fog.py | Fog, Volumetrics, God rays |
| fx_layers.py | Heat haze, Shockwave, Motion effects |
| edge_detection.py | Edge detection, Neon, Outlines |
| export.py | Batch export, Video encoding |
| panels.py | All UI panels (11 panels) |
| operators.py | UI operators (9 operators) |
| viewport_preview.py | Live preview, Overlays |

## Registration Flow

```
1. Blender loads __init__.py
2. bl_info is read for addon metadata
3. register() is called
4. Addon preferences registered
5. Scene properties registered
6. core.register() → All core classes
7. ui.register() → All UI classes
8. utils.register() → Utility classes
9. HyperGradeFX panel appears in Compositor
```

## Data Flow

```
User Action (UI Panel)
    ↓
Operator (HGFX_OT_*)
    ↓
Core Function (core/*.py)
    ↓
Helper Functions (utils/helpers.py)
    ↓
Blender API (bpy.*)
    ↓
Compositor Node Tree Modified
```

## Extension Points

### Adding New Presets
1. Create JSON file in `presets/`
2. Follow existing structure
3. Load via Node Blueprints panel

### Adding New FX
1. Add operator to `core/fx_layers.py`
2. Create node setup function
3. Register operator
4. Add to FX panel in `ui/panels.py`

### Adding New Color Modes
1. Add to color_harmony.py
2. Update COLOR_HARMONY_ANGLES in constants.py
3. Add calculation function
4. Update UI panel

---

**Complete Blender addon with professional post-production tools** ✅
