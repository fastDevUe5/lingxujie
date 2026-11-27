#requires -Version 5.1
# Imports whatever Fab dropped on this machine (Downloads by default) into the project.
#
#   powershell -ExecutionPolicy Bypass -File Tools\ImportFab.ps1
#   powershell -ExecutionPolicy Bypass -File Tools\ImportFab.ps1 -Source D:\Fab
#
# Handles UE-format payloads (Content/... or loose .uasset), and raw FBX + textures.
# Extraction happens in Saved\FabStaging, so a bad zip never touches Content.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Source = ''
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$Cmd = Join-Path $UE 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$LogDir = Join-Path $Root 'Saved\Logs'
$Staging = Join-Path $Root 'Saved\FabStaging'
$Log = Join-Path $LogDir 'fab_import.log'
New-Item -ItemType Directory -Force -Path $LogDir, $Staging | Out-Null

if (-not [string]::IsNullOrWhiteSpace($Source)) {
    if (-not (Test-Path $Source)) { throw "source folder not found: $Source" }
    $zips = Get-ChildItem $Source -Filter *.zip -ErrorAction SilentlyContinue
    foreach ($zip in $zips) {
        Copy-Item $zip.FullName -Destination $Staging -Force
        Write-Host "staged: $($zip.Name)"
    }
    if (-not $zips) { Write-Host "no .zip in $Source - the script also picks up Saved\FabStaging" }
}

$editor = Get-Process UnrealEditor -ErrorAction SilentlyContinue
if ($editor) {
    Write-Host "WARNING: UnrealEditor is running; close it first (asset copies and shader work both want it closed)." -ForegroundColor Yellow
}

& $Cmd "$Project" -run=pythonscript -script="$(Join-Path $Root 'Tools\import_fab.py')" `
    -unattended -nosplash -nop4 -stdout -FullStdOutLogOutput *> $Log
$exit = $LASTEXITCODE
Select-String -Path $Log -Pattern '\[LingXuJie\]|Traceback|Error:' | Select-Object -Last 25 | ForEach-Object { $_.Line }
Write-Host "import exit code: $exit (log: $Log)"
if ($exit -ne 0) { exit $exit }
