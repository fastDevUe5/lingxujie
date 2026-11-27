#requires -Version 5.1
# Waits for new .zip files in Downloads / Desktop and runs the Fab importer when they appear.
#
#   powershell -ExecutionPolicy Bypass -File Tools\WatchFabDownloads.ps1 -Minutes 30
#
# Prints a line when it imports, and exits once at least one import has run (or on timeout).
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [int]$Minutes = 30,
    [int]$SettleSeconds = 8
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$watchDirs = @("$env:USERPROFILE\Downloads", "$env:USERPROFILE\Desktop") |
    Where-Object { Test-Path $_ }
$deadline = (Get-Date).AddMinutes($Minutes)

# Baseline: everything that already exists is not "new".
$seen = @{}
foreach ($dir in $watchDirs) {
    Get-ChildItem $dir -Filter *.zip -File -ErrorAction SilentlyContinue | ForEach-Object {
        $seen[$_.FullName] = $_.LastWriteTime
    }
}
Write-Host ("watching {0} folder(s) for new zips, {1} existing ignored, until {2:HH:mm:ss}" -f `
    $watchDirs.Count, $seen.Count, $deadline)

$imported = 0
while ((Get-Date) -lt $deadline) {
    $fresh = @()
    foreach ($dir in $watchDirs) {
        Get-ChildItem $dir -Filter *.zip -File -ErrorAction SilentlyContinue | ForEach-Object {
            $known = $seen.ContainsKey($_.FullName)
            if (-not $known -or $seen[$_.FullName] -ne $_.LastWriteTime) {
                $fresh += $_
                $seen[$_.FullName] = $_.LastWriteTime
            }
        }
    }

    if ($fresh.Count -gt 0) {
        Write-Host ("new download(s): " + (($fresh | ForEach-Object { $_.Name }) -join ', '))
        # give the browser a moment to finish writing the archive
        Start-Sleep -Seconds $SettleSeconds
        Write-Host "running importer ..."
        $out = & powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'Tools\ImportFab.ps1') 2>&1
        $out | Select-Object -Last 12 | ForEach-Object { Write-Host $_ }
        $imported++
        Write-Host "import run finished"
    }

    Start-Sleep -Seconds 5
}

Write-Host ("watcher done; import runs: {0}" -f $imported)
