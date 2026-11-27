#requires -Version 5.1
# Regenerates the LingXuJie level from Tools/build_level.py (editor must be closed).
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$LogDir = Join-Path $Root 'Saved\Logs'
$Cmd = Join-Path $UE 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$levelLog = Join-Path $LogDir 'levelgen.log'
Write-Host "== Generating /Game/Maps/LingXuJie =="
& $Cmd "$Project" -run=pythonscript -script="$(Join-Path $Root 'Tools\build_level.py')" -unattended -nosplash -nop4 -stdout -FullStdOutLogOutput *>&1 | Out-File -FilePath $levelLog -Encoding utf8
$levelExit = $LASTEXITCODE
Select-String -Path $levelLog -Pattern 'LogPython: \[LingXuJie\]|Exception|Error:' | Select-Object -Last 25 | ForEach-Object { $_.Line }
Write-Host "levelgen exit code: $levelExit"
if ($levelExit -ne 0) { exit $levelExit }
