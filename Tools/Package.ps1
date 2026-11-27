#requires -Version 5.1
# Packages LingXuJie into a runnable Windows build.
#
# Why two steps instead of one BuildCookRun:
#   The editor's Live Coding holds a mutex on UnrealEditor.exe, so UBT refuses to
#   build ("Unable to build while Live Coding is active"). BuildCookRun does not
#   accept -NoHotReloadFromIDE, so we build both targets ourselves first and let
#   BuildCookRun -skipbuild only cook/stage/pak/archive.
#
# Usage:  powershell -ExecutionPolicy Bypass -File Tools\Package.ps1 [-Config Development]
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Config = 'Development'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$Archive = Join-Path $Root ("Saved\Package\" + $Config)
$LogDir = Join-Path $Root 'Saved\Logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
if (Test-Path $Archive) { Remove-Item $Archive -Recurse -Force }

Write-Host "== 1/2  Building LingXuJieEditor (Development) and LingXuJie ($Config) =="
# The Editor target has no Shipping configuration; it is only needed so the
# cooker can run, so it always builds Development.
& (Join-Path $UE 'Engine\Build\BatchFiles\Build.bat') LingXuJieEditor Win64 Development "-Project=$Project" -WaitMutex -NoHotReloadFromIDE |
    Tee-Object -FilePath (Join-Path $LogDir 'package_build_editor.log') | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Editor target build failed ($LASTEXITCODE)" }

& (Join-Path $UE 'Engine\Build\BatchFiles\Build.bat') LingXuJie Win64 $Config "-Project=$Project" -WaitMutex -NoHotReloadFromIDE |
    Tee-Object -FilePath (Join-Path $LogDir 'package_build_game.log') | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Game target build failed ($LASTEXITCODE)" }

Write-Host "== 2/2  Cook / Stage / Pak / Archive =="
# -nodebuginfo: do not stage .pdb files (UAT ProjectParams "nodebuginfo").
# The symbols stay in the project's Binaries folder for crash analysis.
& (Join-Path $UE 'Engine\Build\BatchFiles\RunUAT.bat') BuildCookRun `
    "-project=$Project" -noP4 -platform=Win64 "-clientconfig=$Config" `
    -skipbuild -cook -stage -pak -archive -nodebuginfo "-archivedirectory=$Archive" -utf8output |
    Tee-Object -FilePath (Join-Path $LogDir 'package_cook.log') | Out-Null
if ($LASTEXITCODE -ne 0) { throw "BuildCookRun failed ($LASTEXITCODE)" }

$exe = Join-Path $Archive "Windows\LingXuJie\Binaries\Win64\LingXuJie.exe"
$realExe = Get-ChildItem (Split-Path $exe) -Filter 'LingXuJie*.exe' -ErrorAction SilentlyContinue |
    Sort-Object Length -Descending | Select-Object -First 1
if ($realExe) { $exe = $realExe.FullName }
Write-Host "Packaged: $exe"
if (Test-Path $exe) {
    Write-Host ("Executable size: {0:N1} MB" -f ((Get-Item $exe).Length / 1MB))
}

# --- Bundle the MSVC runtime ----------------------------------------------------
# Unreal Development builds link the dynamic CRT (/MD), so a machine without the
# VC++ Redistributable fails with "VCRUNTIME140.dll was not found". Copying the
# redist DLLs next to the exe makes the package self-contained (Windows resolves
# DLLs from the application directory first).
$exeDir = Split-Path -Parent $exe
$crtDirs = Get-ChildItem 'C:\Program Files\Microsoft Visual Studio' -Recurse -Directory -Filter 'Microsoft.VC*.CRT' -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '\\x64\\' -and $_.FullName -notmatch 'onecore' -and $_.FullName -notmatch 'debug_nonredist' }
if ($crtDirs) {
    $crt = $crtDirs | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Get-ChildItem $crt.FullName -Filter '*.dll' | ForEach-Object {
        Copy-Item $_.FullName -Destination $exeDir -Force
    }
    Write-Host ("Bundled MSVC runtime from: {0}" -f $crt.FullName)
}
else {
    Write-Host "WARNING: VC++ Redistributable not found; the package needs it installed on the target machine." -ForegroundColor Yellow
}
