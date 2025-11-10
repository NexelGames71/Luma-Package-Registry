# Luma Package Registry - Pack Script
# Creates a package zip archive, computes SHA256, and updates manifests

param(
    [Parameter(Mandatory=$true)]
    [string]$PackagePath,
    
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [string]$RegistryPath = ".",
    [string]$PackageName = ""
)

# Error handling
$ErrorActionPreference = "Stop"

# Determine package name from path if not provided
if ([string]::IsNullOrEmpty($PackageName)) {
    $PackageName = Split-Path -Leaf $PackagePath
}

# Validate package structure
if (-not (Test-Path "$PackagePath\package.json")) {
    Write-Error "package.json not found in $PackagePath"
    exit 1
}

# Read package.json to get package ID
$packageJson = Get-Content "$PackagePath\package.json" | ConvertFrom-Json
$packageId = $packageJson.name

if ([string]::IsNullOrEmpty($packageId)) {
    Write-Error "package.json must contain a 'name' field"
    exit 1
}

Write-Host "Packing $packageId version $Version..."

# Create version directory
$versionDir = "$RegistryPath\packages\$packageId\$Version"
if (-not (Test-Path $versionDir)) {
    New-Item -ItemType Directory -Path $versionDir -Force | Out-Null
}

# Create zip archive
$zipName = "$packageId-$Version.zip"
$zipPath = "$versionDir\$zipName"

# Remove existing zip if it exists
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Write-Host "Creating zip archive..."
Compress-Archive -Path "$PackagePath\*" -DestinationPath $zipPath -Force

# Compute SHA256 checksum
Write-Host "Computing SHA256 checksum..."
$sha256 = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash.ToLower()
Write-Host "SHA256: $sha256"

# Update or create manifest
$manifestDir = "$RegistryPath\manifests\$packageId"
if (-not (Test-Path $manifestDir)) {
    New-Item -ItemType Directory -Path $manifestDir -Force | Out-Null
}

$manifestPath = "$manifestDir\index.json"

# Load existing manifest or create new
if (Test-Path $manifestPath) {
    $manifest = Get-Content $manifestPath | ConvertFrom-Json
} else {
    $manifest = @{
        name = $packageId
        versions = @()
    } | ConvertTo-Json -Depth 10 | ConvertFrom-Json
}

# Determine category (default to assets-store if not specified)
# Map old category names to new ones
$rawCategory = if ($packageJson.category) { $packageJson.category } else { "assets-store" }
if ($rawCategory -eq "core") { $category = "registry" }
elseif ($rawCategory -eq "third-party") { $category = "assets-store" }
else { $category = $rawCategory }

# Create version entry
$versionEntry = @{
    version = $Version
    shasum = $sha256
    size = (Get-Item $zipPath).Length
    url = "https://raw.githubusercontent.com/nexelgames/Luma-Package-Registry/main/packages/$packageId/$Version/$zipName"
    dependencies = if ($packageJson.dependencies) { $packageJson.dependencies } else { @{} }
    engine = $packageJson.engine
    description = $packageJson.description
    category = $category
    published = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
}

# Remove existing version entry if it exists
$manifest.versions = $manifest.versions | Where-Object { $_.version -ne $Version }

# Add new version entry
$manifest.versions += $versionEntry

# Sort versions (newest first)
$manifest.versions = $manifest.versions | Sort-Object { [version]$_.version } -Descending

# Save manifest
$manifest | ConvertTo-Json -Depth 10 | Set-Content $manifestPath -Encoding UTF8

Write-Host "Manifest updated: $manifestPath"
Write-Host "Package created successfully: $zipPath"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Run update_index.py to update the global index"
Write-Host "2. Submit a Pull Request with your changes"

