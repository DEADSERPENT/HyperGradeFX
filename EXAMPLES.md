# HyperGradeFX Usage Examples

## Example 1: Basic Color Grade

**Goal:** Apply a professional color grade to a rendered scene

```
1. Render your scene with default settings
2. Switch to Compositor workspace
3. Enable "Use Nodes" in compositor

Steps:
✓ HyperGradeFX → Enable All Render Passes
✓ HyperGradeFX → Auto-Connect Render Passes
✓ Color Grading → Create Color Grade Stack
✓ Adjust the color wheels for desired look
✓ Export → Quick Export
```

**Result:** Professional 7-stage color grading stack with full control

---

## Example 2: Cinematic Teal & Orange

**Goal:** Create the popular cinematic teal and orange look

```
Steps:
✓ HyperGradeFX → Auto-Connect Render Passes
✓ Node Blueprints → Load → stylized_looks.json
✓ Node Blueprints → Apply → "Stylized Teal & Orange"
✓ Color Grading → Create Split Tone Effect
   - Shadow Color: Teal (0.2, 0.4, 0.5)
   - Highlight Color: Orange (1.0, 0.6, 0.3)
   - Strength: 0.7
✓ Adjust to taste
```

**Result:** Classic Hollywood blockbuster color grade

---

## Example 3: Atmospheric Fog Scene

**Goal:** Add realistic fog to outdoor scene

```
Prerequisites:
- Scene with Z-depth pass enabled
- Outdoor environment

Steps:
✓ HyperGradeFX → Enable All Render Passes
✓ 3D Post-Fog → Apply Post-Fog
   - Density: 0.5
   - Start Distance: 10
   - End Distance: 50
   - Fog Color: Light blue (0.5, 0.5, 0.6)
✓ 3D Post-Fog → Create Volumetric Rays (optional)
   - For god rays effect
✓ Adjust fog color to match lighting
```

**Result:** Realistic atmospheric fog using depth information

---

## Example 4: Neon Cyberpunk Look

**Goal:** Create glowing neon edge effects

```
Steps:
✓ HyperGradeFX → Auto-Connect Render Passes
✓ Edge Effects → Detect Edges
   - Method: Sobel
   - Threshold: 0.1
✓ Edge Effects → Create Neon Glow
   - Glow Color: Cyan (0.0, 1.0, 1.0)
   - Intensity: 3.0
   - Blur Size: 25
✓ Color Grading → Apply Look Preset → Vibrant
✓ FX Layers → Chromatic Aberration
   - Strength: 0.02
```

**Result:** Cyberpunk-style neon glow effect

---

## Example 5: Batch Render Multiple Shots

**Goal:** Render multiple shots with different compositions

```
Preparation:
- Set up base compositor network
- Determine shot ranges

Steps:
✓ Sequences → Add Sequence
   - Name: "Shot_01_Intro"
   - Frame Start: 1
   - Frame End: 120

✓ Configure compositor for Shot 01
✓ Sequences → Add Sequence (capture current setup)

✓ Repeat for each shot:
   - Shot_02_Action (121-250)
   - Shot_03_Outro (251-350)

✓ Sequences → Batch Render Sequences
✓ All shots render with their respective compositions
```

**Result:** Automated rendering of multiple shots with different comps

---

## Example 6: Film Emulation

**Goal:** Emulate vintage film look

```
Steps:
✓ Node Blueprints → Load → film_emulation.json
✓ Node Blueprints → Apply → "Vintage Film"
✓ Color Grading → Create Split Tone Effect
   - Shadow: Slight blue (0.9, 0.95, 1.0)
   - Highlight: Warm (1.05, 1.0, 0.95)
   - Balance: 0.5
✓ Add grain (built-in Blender node):
   - Compositor → Add → Distort → Noise
   - Amount: 0.05
```

**Result:** Warm vintage film aesthetic with soft highlights

---

## Example 7: Motion-Based Effects

**Goal:** Add motion blur and glow to fast-moving objects

```
Prerequisites:
- Scene with moving objects
- Vector pass enabled

Steps:
✓ View Layer Properties → Passes → Vector (enable)
✓ HyperGradeFX → Auto-Connect Render Passes
✓ FX Layers → Create Motion Glow
   - Glow Intensity: 1.5
   - Motion Threshold: 0.1
   - Color: Orange (1.0, 0.8, 0.4)
✓ Adjust threshold to control which objects glow
```

**Result:** Objects in motion have speed-based glow trails

---

## Example 8: Heat Distortion Effect

**Goal:** Create heat haze above hot surface

```
Steps:
✓ HyperGradeFX → Auto-Connect Render Passes
✓ FX Layers → Create Heat Haze
   - Distortion: 0.05
   - Scale: 5.0
   - Speed: 1.5
✓ Create mask to limit effect to specific area:
   - Mask Drawing → Create Mask Layer
   - Paint mask over heat source
   - Connect mask to heat haze setup
```

**Result:** Shimmering heat distortion effect

---

## Example 9: Professional Export Pipeline

**Goal:** Export final render in multiple formats

```
Steps:
1. High-Quality Frames:
✓ Export & Automation → Batch Export Frames
   - Format: OpenEXR
   - Frame Range: Full
   - Output: //renders/frames/

2. Client Preview Video:
✓ Export & Automation → Export to Video
   - Codec: H.264
   - Quality: High
   - Output: //delivery/preview.mp4

3. Professional Delivery:
✓ Export & Automation → Export to Video
   - Codec: ProRes
   - Quality: High
   - Output: //delivery/final.mov
```

**Result:** Complete delivery package for client review

---

## Example 10: Custom Blueprint Creation

**Goal:** Save frequently used node setup as preset

```
Steps:
✓ Build your custom compositor network
   - Example: Specific color grade + fog + glow
✓ Select all nodes you want to include
✓ Node Blueprints → Save Selection
   - Name: "My Custom Look"
   - Category: Look Development
   - Description: "Describe your preset"
✓ Blueprint is saved to your library

Reuse later:
✓ Node Blueprints → Select "My Custom Look"
✓ Node Blueprints → Apply
```

**Result:** Reusable custom preset for future projects

---

## Advanced Techniques

### Technique 1: Layered Color Grading

```
Create separate color corrections for:
1. Primary correction (overall balance)
2. Secondary correction (specific hues)
3. Creative grade (look development)

Stack them in order for maximum control.
```

### Technique 2: Z-Depth Effects Combo

```
Combine multiple Z-depth effects:
1. Post-Fog for atmosphere
2. Depth of Field (Blender built-in)
3. Atmospheric perspective using depth masks
```

### Technique 3: Edge-Based Masking

```
Use edge detection to create luminance masks:
1. Detect Edges on render
2. Use edge mask to selectively apply effects
3. Great for sharpening or selective color
```

---

## Workflow Templates

### Template 1: Commercial Product Shot
```
1. Auto-Connect Render Passes
2. Enable clean background
3. Apply Look Preset: Vibrant
4. Add subtle Chromatic Aberration
5. Export in ProRes for editing
```

### Template 2: Moody Interior
```
1. Auto-Connect Render Passes
2. Apply fog for atmosphere
3. Split Tone: Cool shadows, warm highlights
4. Crush blacks slightly
5. Add film grain
```

### Template 3: Action Scene
```
1. Auto-Connect Render Passes
2. Motion Glow on fast objects
3. Shockwave effects for impacts
4. High contrast grading
5. Chromatic aberration for energy
```

---

## Tips for Best Results

### Color Grading
- Work in order: Exposure → White Balance → Contrast → Color
- Use scopes to ensure broadcast safe levels
- Reference real-world color grades from films
- Don't overdo saturation

### Effects
- Layer effects subtly
- Use masks for selective application
- Animate effect parameters for dynamic looks
- Preview at full resolution before final render

### Performance
- Use lower resolution for testing
- Disable live preview when not needed
- Organize nodes with frames
- Save incremental versions

### Export
- Test small ranges before full export
- Check codec compatibility with delivery platform
- Keep source frames separate from compressed video
- Document your settings for client revisions

---

## Common Recipes

### Recipe: "Blade Runner" Look
```
Teal shadows + Amber highlights + Haze + Chromatic aberration
```

### Recipe: "Mad Max" Look
```
Teal/orange + High contrast + Desaturation + Crush blacks
```

### Recipe: "Her" Look
```
Warm pastels + Soft highlights + Slight desaturation
```

### Recipe: "The Matrix" Look
```
Green tint + Crushed blacks + High contrast
```

---

**Experiment, iterate, and create your own signature looks!** 🎨
