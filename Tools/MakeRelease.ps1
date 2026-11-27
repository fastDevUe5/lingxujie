#requires -Version 5.1
# Builds a distributable zip from the Shipping archive.
#   Output: Saved\Release\LingXuJie-<Version>-win64.zip
# Usage:  powershell -ExecutionPolicy Bypass -File Tools\MakeRelease.ps1 [-Version v0.0.1]
#
# IMPORTANT: the archive root is Saved\Package\Shipping\Windows, which contains the
# BootstrapPackagedGame launcher (LingXuJie.exe), the shared Engine\ folder and the
# LingXuJie\ content folder. Shipping only the inner LingXuJie\ folder produces a build
# that exits immediately with code 1 (it resolves engine modules through ../../../Engine).
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Version = 'v0.0.1'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$ArchiveRoot = Join-Path $Root 'Saved\Package\Shipping\Windows'
$ReleaseRoot = Join-Path $Root 'Saved\Release'
$Stage = Join-Path $ReleaseRoot ("LingXuJie-" + $Version)
$Zip = Join-Path $ReleaseRoot ("LingXuJie-" + $Version + "-win64.zip")

if (-not (Test-Path (Join-Path $ArchiveRoot 'LingXuJie.exe'))) {
    throw "Shipping archive not found or incomplete: $ArchiveRoot  (run Tools\Package.ps1 -Config Shipping first)"
}

if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

Write-Host "== Staging $Version =="
Copy-Item (Join-Path $ArchiveRoot '*') -Destination $Stage -Recurse -Force

# Drop runtime logs/config, debug symbols and the D3D12 debug layer if present.
foreach ($junk in @('LingXuJie\Saved', 'd3d12SDKLayers.dll')) {
    $path = Join-Path $Stage $junk
    if (Test-Path $path) { Remove-Item $path -Recurse -Force }
}
Get-ChildItem $Stage -Recurse -File -Filter '*.pdb' -ErrorAction SilentlyContinue | Remove-Item -Force

$readme = @"
LingXuJie $Version (Windows x64)

HOW TO PLAY
  Double-click LingXuJie.exe (the launcher in this folder).
  Do not run Binaries\...\LingXuJie-Win64-Shipping.exe directly: that binary needs
  the Engine\ folder next to it and will exit without a message otherwise.

  WASD / arrow keys   move
  Mouse, Q / E        turn camera
  R / F               camera pitch
  Space               jump
  Shift (hold)        sprint
  Enter               restart
  Esc                 quit

GOAL
  Collect all 8 coins before the clock runs out.
  Pick up coins within 4 seconds of each other to build a streak:
  every chained coin adds 1.5 seconds.

REQUIREMENTS
  Windows 10/11 x64, a GPU with a recent driver (D3D12).
  No Unreal Engine or Visual Studio installation is required; the MSVC runtime
  ships next to the executables.

NOTE
  The build is unsigned, so Windows SmartScreen may ask for confirmation on first
  run: click "More info" -> "Run anyway".

BUILD INFO
  Unreal Engine 5.8.4, Shipping configuration.
"@
Set-Content -Path (Join-Path $Stage 'README.txt') -Value $readme -Encoding ASCII

Write-Host "== Zipping =="
if (Test-Path $Zip) { Remove-Item $Zip -Force }
Compress-Archive -Path (Join-Path $Stage '*') -DestinationPath $Zip -CompressionLevel Optimal

$zipMb = (Get-Item $Zip).Length / 1MB
$stageMb = (Get-ChildItem $Stage -Recurse -File | Measure-Object Length -Sum).Sum / 1MB
Write-Host ("Release: {0}" -f $Zip)
Write-Host ("  uncompressed {0:N0} MB -> zip {1:N0} MB" -f $stageMb, $zipMb)
