# HyperGradeFX Complete Usage Guide

## 🎬 IMPORTANT: How to See Real-Time Results

### Prerequisites
1. **Switch to Compositor Workspace**: Top menu → Compositor (or press Shift+F3)
2. **Enable Compositor**: Top menu → Use Nodes checkbox
3. **Have a Render or Image**: You need either:
   - A rendered image in your scene (press F12 to render)
   - OR a Render Layers node in the compositor

### Seeing Your Effects in Real-Time

After clicking ANY effect button:
1. **Backdrop is AUTO-ENABLED**: You'll see the image preview in the background
2. **Viewer Node is AUTO-CREATED**: Shows the effect output
3. **Composite Output is AUTO-CONNECTED**: For final rendering

**If you don't see anything:**
- Check the top menu: "View" → "Backdrop" should be checked ✓
- Make sure you have rendered an image first (F12)
- Look for the "HGFX Preview" viewer node (it's auto-activated)

---

## 📊 Main Panel Features

### Quick Actions

#### 1. **Auto-Connect Render Passes**
- **What it does**: Automatically detects and connects render passes (AO, Shadow, Mist, etc.)
- **When to use**: After you render, to quickly set up pass-based compositing
- **Result**: Creates organized node setup with all available passes connected
- **See it**: Backdrop shows your render with passes ready to use

#### 2. **Enable Render Passes**
- **What it does**: Turns on common render passes in View Layer settings
- **When to use**: Before rendering, to enable depth, normal, AO, etc.
- **Result**: Render will include additional data channels for compositing
- **See it**: Check View Layer Properties → Passes (checkboxes enabled)

---

## 🎨 Color Grading Panel

### Color Harmony

#### **Apply Color Harmony** Button
- **What it does**: Applies artistic color schemes based on color theory
- **Options**:
  - **Complementary**: Opposite colors (e.g., blue & orange)
  - **Analogous**: Adjacent colors (e.g., blue, blue-green, green)
  - **Split-Complementary**: Base + two neighbors of complement
  - **Triadic**: Three equally-spaced colors
- **How to use**:
  1. Click button
  2. Choose color harmony mode
  3. Pick base color
  4. Adjust strength (0.0 = none, 1.0 = full effect)
- **See it**: Backdrop shows color-shifted image IMMEDIATELY
- **Final output**: Auto-connected to Composite for rendering

#### **Create Split Tone** Button
- **What it does**: Different colors for shadows vs highlights (film look)
- **How to use**:
  1. Click button
  2. Choose Shadow Color (e.g., blue/teal)
  3. Choose Highlight Color (e.g., warm orange)
  4. Balance: where shadow/highlight split happens (0.5 = middle)
  5. Strength: how strong the effect is
- **Example**: Teal shadows + orange highlights = blockbuster movie look
- **See it**: Backdrop updates with split-tone effect
- **Nodes created**: RGB to BW, Color Ramp, Mix nodes

#### **Apply Look Preset** Button
- **What it does**: One-click cinematic looks
- **Presets available**:
  - **Cinematic Warm**: Orange/warm tones, Hollywood style
  - **Cinematic Cool**: Blue/teal tones, thriller/sci-fi style
  - **Vibrant**: Boosted saturation, music video style
  - **Desaturated**: Muted colors, documentary style
  - **Vintage**: Old film look, slightly warm
  - **Film Noir**: Black & white, high contrast
- **How to use**: Click → Choose preset → Apply
- **See it**: Instant preview in backdrop
- **Tip**: Stack multiple presets for custom looks!

#### **Create Color Grade Stack** Button
- **What it does**: Professional 7-stage color grading workflow
- **Stages created**:
  1. **Exposure**: Overall brightness
  2. **White Balance**: Temperature (warm/cool)
  3. **Contrast**: Darks vs lights separation
  4. **Saturation**: Color intensity
  5. **Color Wheels** (Lift/Gamma/Gain): Precise color control
  6. **Curves**: Fine-tune tones
  7. **Final Adjust**: Last tweaks
- **How to use**:
  1. Click button
  2. Nodes are created in order (left to right)
  3. Adjust each node's properties to grade
  4. Work from left (Exposure) to right (Final)
- **See it**: Backdrop shows result as you adjust any node
- **Pro tip**: This is how Hollywood colorists work!

---

## 🌫️ 3D Post-Fog Panel

### **Apply Post-Fog** Button
- **What it does**: Depth-based atmospheric fog (needs Z-depth pass)
- **Requirements**: Enable Z-Depth pass before rendering
- **Settings**:
  - **Fog Density**: How thick the fog is (0-1)
  - **Fog Start**: Distance where fog begins
  - **Fog End**: Distance where fog is thickest
  - **Fog Color**: Color of the fog
- **How to use**:
  1. Enable fog in panel checkbox
  2. Adjust settings
  3. Click "Apply Post-Fog"
- **See it**: Backdrop shows depth-based fog overlay
- **Use case**: Atmospheric renders, depth enhancement

### **God Rays** Button
- **What it does**: Volumetric light rays (like sunlight through fog)
- **How to use**: Click → Adjust intensity
- **See it**: Dramatic light beams in backdrop
- **Tip**: Works best with bright light sources

---

## 🎭 FX Layers Panel

### Environmental FX

#### **Heat Haze** Button
- **What it does**: Animated heat distortion effect
- **Use for**: Desert scenes, fire effects, hot surfaces
- **See it**: Wavy distortion in backdrop
- **Animates**: Can be animated over time

#### **Shockwave** Button
- **What it does**: Radial explosion/impact wave
- **Use for**: Explosions, impacts, magic effects
- **See it**: Circular wave distortion

#### **Motion Glow** Button
- **What it does**: Glow that follows movement
- **Use for**: Fast-moving objects, energy effects
- **See it**: Trailing glow on moving elements

### Lens FX

#### **Chromatic Aberration** Button
- **What it does**: Color fringing like real camera lenses
- **Use for**: Realistic camera imperfections
- **See it**: Red/blue color splits at edges

#### **Lens Distortion** Button
- **What it does**: Barrel/pincushion distortion
- **Use for**: Wide-angle camera simulation
- **See it**: Curved/warped image edges

---

## ✨ Edge Effects Panel

### **Detect Edges** Button
- **What it does**: Finds edges in your image
- **Methods**: Sobel, Prewitt, Roberts, Canny algorithms
- **How to use**:
  1. Enable Edge Detection checkbox
  2. Adjust threshold
  3. Click button
- **See it**: White edges on black background in backdrop
- **Use for**: Masks, outlines, stylized effects

### **Neon Glow** Button
- **What it does**: Glowing edges (cyberpunk style)
- **How to use**: Click → Choose glow color
- **See it**: Colored glow along edges
- **Popular for**: Cyberpunk, sci-fi, music videos

### **Create Outline** Button
- **What it does**: Solid outline around objects
- **How to use**: Click → Choose color and thickness
- **See it**: Cartoon/cel-shaded outline effect

---

## 📤 Export & Automation Panel

### **Quick Export** Button
- **What it does**: One-click export of current compositor view
- **Format**: PNG with alpha
- **Location**: Same as blend file
- **Use for**: Quick tests, client previews

### **Batch Export Frames** Button
- **What it does**: Exports frame range as image sequence
- **How to use**:
  1. Set frame range in timeline
  2. Click button
  3. Choose output folder
- **Result**: Numbered image sequence
- **Use for**: Video editing, VFX workflows

### **Export to Video** Button
- **What it does**: Exports directly to video file (MP4/MOV)
- **Requires**: FFmpeg installed
- **Codecs**: H.264, H.265, ProRes, DNxHD
- **Use for**: Final delivery, social media

---

## 🎯 Live Preview Panel

### **Enable Live Preview** Button
- **What it does**:
  - Enables compositor backdrop
  - Creates viewer node
  - Auto-activates viewer for real-time feedback
- **When to use**: At the START of compositing
- **Result**: See ALL changes instantly in backdrop

### **Refresh Preview** Button
- **What it does**: Forces compositor to update
- **When to use**: If preview seems frozen
- **Shortcut**: Just reactivate viewer node

### **Toggle Preview Mode** Button
- **What it does**: Switches between multiple viewer nodes (before/after)
- **How to use**: Create 2+ viewer nodes, this switches between them
- **Use for**: A/B comparisons

### **Create Split Preview** Button
- **What it does**: Side-by-side before/after comparison
- **How to use**:
  1. Click button
  2. Set split position (0.5 = center)
  3. Connect "before" to input 1, "after" to input 2
- **See it**: Vertical split showing both versions
- **Use for**: Client presentations, final checks

---

## 🔧 Safe Areas & Guides Panel

### **Show Safe Areas** Button
- **What it does**: Displays TV-safe guides
- **Types**:
  - **Action Safe** (90%): Keep important action here
  - **Title Safe** (80%): Keep text here
- **See it**: Yellow overlay lines in backdrop
- **Use for**: Broadcast, TV, streaming delivery

### **Create Aspect Guides** Button
- **What it does**: Shows framing for different aspect ratios
- **Ratios**: 16:9, 4:3, 21:9, 1:1 (Instagram), 9:16 (Stories)
- **Use for**: Multi-format delivery

---

## 📋 Node Blueprints Panel

### **Save Selection** Button
- **What it does**: Saves selected nodes as reusable preset
- **How to use**:
  1. Create cool node setup
  2. Select all nodes (B-key drag)
  3. Click "Save Selection"
  4. Name your blueprint
- **Result**: Saved for reuse in any project

### **Load** Button
- **What it does**: Recreates saved blueprint
- **How to use**: Click → Choose from list → Apply
- **Result**: Entire node setup appears ready to use

---

## 🎬 Complete Workflow Example

### Basic Color Grading Workflow:

1. **Setup** (Do this FIRST):
   ```
   - Switch to Compositor workspace
   - Press F12 to render your scene
   - Click "Enable Live Preview" in HyperGradeFX panel
   - Backdrop should now show your render
   ```

2. **Create Grade Stack**:
   ```
   - Go to Color Grading panel
   - Click "Create Color Grade Stack"
   - You'll see 7 nodes appear
   - Backdrop shows the preview IMMEDIATELY
   ```

3. **Adjust the Grade**:
   ```
   - Click each node (1. Exposure, 2. White Balance, etc.)
   - Adjust sliders in properties
   - Backdrop updates IN REAL-TIME as you adjust!
   ```

4. **Add Creative Look**:
   ```
   - Click "Create Split Tone"
   - Choose teal shadows, orange highlights
   - Adjust strength
   - Backdrop updates instantly
   ```

5. **Final Render**:
   ```
   - Press F12 to render (output is auto-connected to Composite)
   - Or click "Export to Video" for final delivery
   ```

---

## ❓ Troubleshooting

### "I don't see anything in the backdrop"
✅ Solutions:
- Did you render first? Press F12
- Is backdrop enabled? View menu → Backdrop (check it)
- Is the viewer node active? Look for green outline on "HGFX Preview" node
- Is compositor enabled? Top menu "Use Nodes" checkbox

### "Effects create nodes but nothing changes"
✅ Solutions:
- The backdrop should auto-enable now
- Check the Composite output node - it should have green connection
- Look for "HGFX Preview" viewer node - should be active (green outline)
- Force refresh: Click "Refresh Preview" button

### "How do I get the final rendered image?"
✅ Solutions:
- Press F12 to render - the Composite node has your final graded output
- Or use "Quick Export" button to save current view
- Or use "Export to Video" for animation

### "Too many nodes, can't see anything"
✅ Solutions:
- Press Home key in compositor to frame all
- Use Save Blueprint to save your work
- Delete old nodes you don't need
- Use Frame nodes to organize (Shift+A → Layout → Frame)

---

## 🚀 Pro Tips

1. **Always Enable Live Preview FIRST**: Click it before doing anything else
2. **Work Non-Destructively**: All effects use nodes, you can always delete/adjust
3. **Use Blueprints**: Save your best color grades for reuse
4. **Layer Effects**: Stack multiple effects (Harmony + Split Tone + Fog = amazing!)
5. **Check Backdrop**: If you can see it in backdrop, it will render
6. **Composite Node = Final Output**: Whatever connects there is what renders

---

## 📊 What Happens When You Click a Button?

**Every button does these 3 things:**

1. **Creates Nodes**: Adds compositing nodes to node tree
2. **Connects Them**: Links nodes together automatically
3. **Shows Preview**:
   - Enables backdrop (if not enabled)
   - Creates and activates viewer node
   - Connects to Composite output
   - **YOU SEE RESULTS IMMEDIATELY!**

**The NEW system ensures:**
- ✅ Backdrop is ALWAYS enabled
- ✅ Viewer node is ALWAYS created and activated
- ✅ Composite output is ALWAYS connected
- ✅ You ALWAYS see real-time results!

---

## 🎓 Learning Path

### Beginner:
1. Enable Live Preview
2. Try "Apply Look Preset" → Choose "Cinematic Warm"
3. See instant result!

### Intermediate:
1. Create Color Grade Stack
2. Adjust each of the 7 stages
3. Watch backdrop update in real-time

### Advanced:
1. Create custom node setups
2. Save as Blueprints
3. Combine multiple effects
4. Export to high-quality video

---

**Remember**: With the new real-time preview system, you should see EVERY change IMMEDIATELY in the backdrop. If you don't, click "Refresh Preview" or reactivate the "HGFX Preview" viewer node.

Happy Grading! 🎨🎬
