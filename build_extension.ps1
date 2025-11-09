# PowerShell script to build HyperGradeFX extension
# Usage: .\build_extension.ps1

Write-Host "Building HyperGradeFX Extension..." -ForegroundColor Cyan

# Configuration
$extensionName = "hypergradefx"
$version = "1.0.0"
$outputName = "$extensionName-$version.zip"
$sourceDir = $PSScriptRoot
$parentDir = Split-Path -Parent $sourceDir

# Check if blender_manifest.toml exists
if (-not (Test-Path "$sourceDir\blender_manifest.toml")) {
    Write-Host "ERROR: blender_manifest.toml not found!" -ForegroundColor Red
    Write-Host "Please ensure the manifest file exists in the root directory." -ForegroundColor Yellow
    exit 1
}

# Files and directories to exclude
$exclude = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    ".gitignore",
    "*.md",
    "validate_addon.py",
    "requirements.txt",
    ".vscode",
    ".idea",
    "*.zip",
    "build_extension.ps1",
    "build_extension.sh"
)

Write-Host "Source directory: $sourceDir" -ForegroundColor Gray
Write-Host "Output file: $outputName" -ForegroundColor Gray

# Method 1: Try using Blender's CLI (if available)
$blenderPaths = @(
    "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
    "C:\Program Files\Blender Foundation\Blender\blender.exe"
)

$blenderExe = $null
foreach ($path in $blenderPaths) {
    if (Test-Path $path) {
        $blenderExe = $path
        break
    }
}

if ($blenderExe) {
    Write-Host "`nAttempting to build with Blender CLI..." -ForegroundColor Cyan
    Write-Host "Blender found at: $blenderExe" -ForegroundColor Gray

    try {
        & $blenderExe --command extension build $sourceDir --output-dir $parentDir 2>&1 | Out-Null

        if (Test-Path "$parentDir\$outputName") {
            Write-Host "`n[SUCCESS] Extension built successfully!" -ForegroundColor Green
            Write-Host "Output: $parentDir\$outputName" -ForegroundColor Green
            Write-Host "`nYou can now upload this file to Blender Extension Platform:" -ForegroundColor Cyan
            Write-Host "https://extensions.blender.org/" -ForegroundColor Blue
            exit 0
        }
    }
    catch {
        Write-Host "Blender CLI method failed, falling back to manual packaging..." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Blender 4.2+ not found, using manual packaging..." -ForegroundColor Yellow
}

# Method 2: Manual packaging
Write-Host "`nCreating zip file manually..." -ForegroundColor Cyan

# Remove old zip if exists
$outputPath = Join-Path $parentDir $outputName
if (Test-Path $outputPath) {
    Remove-Item $outputPath -Force
    Write-Host "Removed existing $outputName" -ForegroundColor Gray
}

# Create temporary directory structure
$tempDir = Join-Path $env:TEMP "hypergradefx_build"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy files
Write-Host "Copying files..." -ForegroundColor Gray
Copy-Item -Path "$sourceDir\*" -Destination $tempDir -Recurse -Force

# Remove excluded files
Write-Host "Removing excluded files..." -ForegroundColor Gray
foreach ($pattern in $exclude) {
    Get-ChildItem -Path $tempDir -Recurse -Force -Filter $pattern -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
}

# Create the zip
Write-Host "Creating archive..." -ForegroundColor Gray
Compress-Archive -Path "$tempDir\*" -DestinationPath $outputPath -CompressionLevel Optimal -Force

# Cleanup
Remove-Item $tempDir -Recurse -Force

if (Test-Path $outputPath) {
    Write-Host "`n[SUCCESS] Extension packaged successfully!" -ForegroundColor Green
    Write-Host "Output: $outputPath" -ForegroundColor Green

    # Show file size
    $fileSize = (Get-Item $outputPath).Length / 1MB
    Write-Host "Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray

    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Validate: blender --command extension validate `"$sourceDir`"" -ForegroundColor White
    Write-Host "2. Upload to: https://extensions.blender.org/" -ForegroundColor Blue
}
else {
    Write-Host "`n[ERROR] Failed to create extension package!" -ForegroundColor Red
    exit 1
}
