#requires -Version 5.1
# Builds the LingXuJie C++ module and regenerates the sandbox level.
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$LogDir = Join-Path $Root 'Saved\Logs'
$Cmd = Join-Path $UE 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Host "== 1/2  Building LingXuJieEditor =="
# A running editor holds the Live Coding mutex and makes UBT fail in a confusing way.
# Say so up front instead of letting the user decode "Unable to build while Live Coding is active".
$editor = Get-Process UnrealEditor -ErrorAction SilentlyContinue
if ($editor) {
    Write-Host ("WARNING: UnrealEditor is running (pid {0}). Close it if the build fails with a Live Coding mutex error." -f (($editor | ForEach-Object { $_.Id }) -join ',')) -ForegroundColor Yellow
}
$buildLog = Join-Path $LogDir 'build.log'
$buildScript = Join-Path $UE 'Engine\Build\BatchFiles\Build.bat'
& $buildScript LingXuJieEditor Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE *>&1 | Out-File -FilePath $buildLog -Encoding utf8
$buildExit = $LASTEXITCODE
Select-String -Path $buildLog -Pattern 'error|Result:|Output binary' | Select-Object -Last 20 | ForEach-Object { $_.Line }
Write-Host "build exit code: $buildExit"
if ($buildExit -ne 0) {
    Write-Host "BUILD FAILED - see $buildLog"
    if ($editor) {
        Write-Host "HINT: UnrealEditor is open - its Live Coding mutex blocks UBT. Close the editor and rerun." -ForegroundColor Yellow
    }
    exit $buildExit
}

Write-Host "== 2/2  Generating /Game/Maps/LingXuJie with Python =="
$levelLog = Join-Path $LogDir 'levelgen.log'
& $Cmd "$Project" -run=pythonscript -script="$(Join-Path $Root 'Tools\build_level.py')" -unattended -nosplash -nop4 -stdout -FullStdOutLogOutput *>&1 | Out-File -FilePath $levelLog -Encoding utf8
$levelExit = $LASTEXITCODE
Select-String -Path $levelLog -Pattern 'LogPython: \[LingXuJie\]|Exception|Error:' | Select-Object -Last 25 | ForEach-Object { $_.Line }
Write-Host "levelgen exit code: $levelExit"
if ($levelExit -ne 0) { exit $levelExit }

Write-Host "== Done =="
