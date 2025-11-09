# GitHub Actions Workflows for HyperGradeFX

## 🚀 What These Workflows Do

### 1. **lint.yml** - Code Quality Check
- **Runs on**: Every push to main, every pull request
- **What it does**: Checks your Python code for errors and style issues
- **Time**: ~30 seconds
- **Status**: You'll see ✅ or ❌ on GitHub

### 2. **test.yml** - Addon Import Test
- **Runs on**: Every push to main, every pull request
- **What it does**:
  - Tests if addon can be imported on Python 3.10 & 3.11
  - Verifies all modules load correctly
  - Checks required files exist
- **Time**: ~1 minute
- **Status**: You'll see ✅ or ❌ on GitHub

### 3. **release.yml** - 🎉 Auto-Build & Release
- **Runs on**: When you create a GitHub Release (or manually)
- **What it does**:
  - Builds the `.zip` file automatically
  - Updates version number
  - Attaches ZIP to the release
  - Creates SHA256 hash for verification
- **Time**: ~2 minutes
- **Result**: Auto-generated ZIP file ready to download!

---

## 📖 How to Use

### Initial Setup (One Time)

1. **Push these workflow files to GitHub**:
   ```bash
   cd C:\Users\AKSHAY\Music\HyperGradeFX
   git add .github/workflows/
   git commit -m "Add GitHub Actions workflows"
   git push origin main
   ```

2. **Check Actions tab on GitHub**:
   - Go to your repository on GitHub
   - Click "Actions" tab
   - You should see the workflows running!

---

## 🎯 Creating a Release (Auto-Builds ZIP!)

### Step 1: Prepare for Release
```bash
# Make sure all changes are committed
git add .
git commit -m "Ready for release v1.0.1"
git push origin main
```

### Step 2: Create a Tag
```bash
# Create version tag
git tag v1.0.1

# Push the tag to GitHub
git push origin v1.0.1
```

### Step 3: Create GitHub Release

**Option A: GitHub Web UI** (Recommended)
1. Go to your repository on GitHub
2. Click "Releases" (right sidebar)
3. Click "Create a new release"
4. Click "Choose a tag" → select `v1.0.1`
5. Title: `HyperGradeFX v1.0.1`
6. Description: Write release notes (what's new, what's fixed)
7. Click "Publish release"

**🎉 GitHub Actions will automatically:**
- Build `hypergradefx-1.0.1.zip`
- Attach it to the release
- Generate SHA256 hash
- Make it available for download!

**Option B: Command Line** (gh CLI)
```bash
# Install GitHub CLI first: https://cli.github.com/
gh release create v1.0.1 --title "HyperGradeFX v1.0.1" --notes "Bug fixes and improvements"
```

### Step 4: Download Your ZIP
- Go to Releases tab
- Click on `v1.0.1`
- Download `hypergradefx-1.0.1.zip` ✅
- **No more manual building!**

---

## 🔧 Manual Build (Without Release)

Want to build a ZIP without creating a release?

### Option 1: GitHub Web UI
1. Go to Actions tab
2. Click "Build and Release Addon"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"
6. Wait ~2 minutes
7. Download from "Artifacts" section

### Option 2: Command Line
```bash
gh workflow run release.yml
```

---

## 📊 Workflow Status Badges

Add these to your README.md to show workflow status:

```markdown
![Lint](https://github.com/DEADSERPENT/hypergradefx/actions/workflows/lint.yml/badge.svg)
![Test](https://github.com/DEADSERPENT/hypergradefx/actions/workflows/test.yml/badge.svg)
![Release](https://github.com/DEADSERPENT/hypergradefx/actions/workflows/release.yml/badge.svg)
```

(Replace `DEADSERPENT/hypergradefx` with your actual username/repo)

---

## 🐛 Troubleshooting

### "Workflow not running"
- Check Actions tab → Workflows (make sure they're enabled)
- Verify `.github/workflows/` files are in the main branch
- Check if repository has Actions enabled (Settings → Actions)

### "Build failed"
- Click on the failed workflow
- Read the error logs
- Usually it's a Python import error or missing file
- Fix the issue and push again

### "ZIP not attached to release"
- Make sure you created a GitHub Release (not just a tag)
- Check Actions tab to see if workflow ran
- Workflow must finish successfully (green ✅)

---

## 🎓 Understanding the Workflow Files

### lint.yml
```yaml
on:
  push:
    branches: [ main ]  # Runs when you push to main
  pull_request:        # Runs on pull requests
```

### test.yml
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']  # Tests on both versions
```

### release.yml
```yaml
on:
  release:
    types: [created]    # Runs when you create a release
  workflow_dispatch:    # Allows manual triggering
```

---

## 💡 Pro Tips

1. **Version Numbering**:
   - Use semantic versioning: `v1.0.0`, `v1.0.1`, `v1.1.0`, `v2.0.0`
   - Patch (bug fixes): v1.0.**1**
   - Minor (new features): v1.**1**.0
   - Major (breaking changes): v**2**.0.0

2. **Release Notes Template**:
   ```markdown
   ## What's New
   - Added real-time preview system
   - Fixed preference access bug

   ## Bug Fixes
   - Fixed KeyError in viewport_preview.py
   - Fixed backdrop not auto-enabling

   ## Installation
   1. Download `hypergradefx-1.0.1.zip`
   2. Install in Blender: Edit → Preferences → Get Extensions → Install from Disk
   ```

3. **Pre-release Testing**:
   - Use manual workflow trigger to build test ZIPs
   - Download from Artifacts
   - Test in Blender
   - Then create official release

4. **Automatic Versioning**:
   - The workflow auto-updates `blender_manifest.toml` version
   - No need to manually edit version numbers!

---

## 🔄 Complete Release Workflow Example

```bash
# 1. Make changes
nano core/color_harmony.py

# 2. Test locally
python validate_addon.py

# 3. Commit changes
git add .
git commit -m "Fix: Color harmony real-time preview"
git push origin main

# 4. Wait for CI to pass (check Actions tab)

# 5. Create tag
git tag v1.0.2
git push origin v1.0.2

# 6. Create release on GitHub
gh release create v1.0.2 \
  --title "HyperGradeFX v1.0.2" \
  --notes "Fixed color harmony preview bug"

# 7. Wait ~2 minutes

# 8. Download hypergradefx-1.0.2.zip from Releases tab! ✅
```

---

## 📦 What Gets Built

The release ZIP includes:
- ✅ All Python files
- ✅ blender_manifest.toml (with updated version)
- ✅ LICENSE
- ✅ Presets folder
- ❌ Excluded: .git, .github, .md files, build scripts

Exactly like your manual build, but automatic!

---

## 🎉 Benefits

**Before:**
1. Edit code
2. Run PowerShell script manually
3. Find the ZIP file
4. Upload somewhere
5. Tell users where to get it

**After:**
1. Edit code
2. Create GitHub release
3. **GitHub builds and publishes automatically!**
4. Users download from Releases tab ✅

**Time saved:** 5-10 minutes per release!

---

## 🔐 Security

- Workflows run in isolated containers
- No access to your local machine
- Only has access to your repository files
- Uses GitHub's secure token system

---

**Ready to try it?** Push these workflows and create your first auto-release! 🚀
