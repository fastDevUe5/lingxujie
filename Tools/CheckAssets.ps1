#requires -Version 5.1
# LingXuJie asset check: naming convention, LFS coverage, file size, and build artifacts leaking into git.
# Usage:  powershell -ExecutionPolicy Bypass -File Tools\CheckAssets.ps1
# Exit code: 0 = all good, 1 = errors found (printed one per line).
# NOTE: keep this file ASCII-only. PowerShell 5.1 reads BOM-less files as ANSI and mangles non-ASCII literals.

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

# ---- 1. every binary extension must be stored in LFS --------------------------
$binaryExt = @('.uasset', '.umap', '.ubulk', '.uexp', '.upk', '.pak', '.png', '.jpg', '.jpeg', '.tga', '.wav', '.fbx', '.blend')
$tracked = @(git ls-files)
foreach ($file in $tracked) {
    $ext = [System.IO.Path]::GetExtension($file).ToLowerInvariant()
    if ($binaryExt -notcontains $ext) { continue }
    $attr = git check-attr filter -- $file
    if ($attr -notmatch 'filter:\s*lfs') {
        $errors.Add("not in LFS: $file")
    }
}

# ---- 2. build artifacts must never be tracked ---------------------------------
$forbidden = @('Intermediate/', 'Binaries/', 'Saved/', 'DerivedDataCache/', '.vs/')
foreach ($file in $tracked) {
    foreach ($prefix in $forbidden) {
        if ($file -like "*${prefix}*") { $errors.Add("build artifact tracked: $file") }
    }
}

# ---- 3. naming convention under Content ---------------------------------------
$contentDir = Join-Path $Root 'LingXuJie\Content'
$allowedPrefix = @('SM_', 'M_', 'MI_', 'MPC_', 'T_', 'BP_', 'WBP_', 'NS_', 'S_', 'A_', 'SK_', 'AM_', 'E_', 'P_')
if (Test-Path $contentDir) {
    Get-ChildItem $contentDir -Recurse -File -Include '*.uasset', '*.umap' | ForEach-Object {
        $name = $_.BaseName
        $rel = $_.FullName.Substring($Root.Length + 1)
        if ($_.Extension -eq '.umap') { return }   # level names are free-form
        if ($name -match '\s') { $errors.Add("space in file name: $rel") }
        $ok = $false
        foreach ($p in $allowedPrefix) { if ($name.StartsWith($p)) { $ok = $true; break } }
        if (-not $ok) { $warnings.Add("name prefix not in convention: $rel") }
    }
}

# ---- 4. single file size ------------------------------------------------------
foreach ($file in $tracked) {
    $full = Join-Path $Root $file
    if (-not (Test-Path $full)) { continue }
    $mb = (Get-Item $full).Length / 1MB
    if ($mb -gt 100) { $errors.Add(("file too large ({0:N1} MB): {1}" -f $mb, $file)) }
    elseif ($mb -gt 20) { $warnings.Add(("large file ({0:N1} MB): {1}" -f $mb, $file)) }
}

# ---- summary ------------------------------------------------------------------
$warnings | ForEach-Object { Write-Host "WARN  $_" -ForegroundColor Yellow }
$errors   | ForEach-Object { Write-Host "ERROR $_" -ForegroundColor Red }
Write-Host ("Checked {0} tracked files: {1} error(s), {2} warning(s)" -f $tracked.Count, $errors.Count, $warnings.Count)

Pop-Location
if ($errors.Count -gt 0) { exit 1 }
exit 0
