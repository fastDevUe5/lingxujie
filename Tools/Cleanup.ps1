#requires -Version 5.1
#
# Reclaim what accumulation actually costs, and nothing else.
#
# Dry run by default: it prints, per category, how many files there are, how much
# they take, and how many it WOULD delete. Nothing is removed without -Apply.
#
#   powershell -ExecutionPolicy Bypass -File Tools\Cleanup.ps1
#   powershell -ExecutionPolicy Bypass -File Tools\Cleanup.ps1 -Apply
#   powershell -ExecutionPolicy Bypass -File Tools\Cleanup.ps1 -KeepDays 3 -KeepShots 40 -Apply
#   powershell -ExecutionPolicy Bypass -File Tools\Cleanup.ps1 -IncludeIntermediate   (editor must be closed)
#
# Whitelist only. These are never touched: Content, Assets, Binaries, Config,
# Source, Docs, Tools, .git, Saved\Config, Saved\SaveGames, Saved\Collections.
# A file younger than -KeepDays days is always protected; among screenshots and
# logs the newest -KeepShots / -KeepLogs are protected as well, because they are
# the evidence the docs point at.
#
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [switch]$Apply,
    [int]$KeepDays = 14,
    [int]$KeepShots = 120,
    [int]$KeepLogs = 15,
    [switch]$IncludeIntermediate,

    # Trigger thresholds: below these, cleaning is not worth doing at all.
    [double]$SavedTriggerMB = 1200,
    [int]$ScreenshotTrigger = 600
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Now = Get-Date
$Cutoff = $Now.AddDays(-$KeepDays)

$Targets = New-Object System.Collections.ArrayList
$Rows = New-Object System.Collections.ArrayList

function Get-SizeMB($items) {
    if ($null -eq $items) { return 0.0 }
    $sum = ($items | Measure-Object Length -Sum).Sum
    if ($null -eq $sum) { return 0.0 }
    return [math]::Round($sum / 1MB, 1)
}

function Add-Category {
    param($Name, $All, $Delete)

    $allItems = @($All)
    $delItems = @($Delete)
    $row = [pscustomobject]@{
        Category = $Name
        Files    = $allItems.Count
        TotalMB  = (Get-SizeMB $allItems)
        DropFiles = $delItems.Count
        DropMB   = (Get-SizeMB $delItems)
    }
    [void]$Rows.Add($row)
    foreach ($item in $delItems) { [void]$Targets.Add($item) }
}

function Get-Files($Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return @() }
    return @(Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue)
}

# ---------------------------------------------------------------- whitelist --

# 1. Screenshots: keep everything recent, and the newest N whatever their age.
$shots = Get-Files (Join-Path $Root 'Saved\Screenshots')
$keepShotSet = @($shots | Sort-Object LastWriteTime -Descending | Select-Object -First $KeepShots)
$delShots = @($shots | Where-Object { $_.LastWriteTime -lt $Cutoff -and $keepShotSet -notcontains $_ })
Add-Category 'Saved\Screenshots' $shots $delShots

# 2. Logs: same rule, smaller number kept.
$logs = Get-Files (Join-Path $Root 'Saved\Logs')
$keepLogSet = @($logs | Sort-Object LastWriteTime -Descending | Select-Object -First $KeepLogs)
$delLogs = @($logs | Where-Object { $_.LastWriteTime -lt $Cutoff -and $keepLogSet -notcontains $_ })
Add-Category 'Saved\Logs' $logs $delLogs

# 3. Autosaves, crash dumps, editor shader dumps: pure age.
foreach ($pair in @(
    @('Saved\Autosaves', 'Saved\Autosaves'),
    @('Saved\Crashes', 'Saved\Crashes'),
    @('Saved\ShaderDebugInfo', 'Saved\ShaderDebugInfo'),
    @('Saved\Shaders', 'Saved\Shaders')
)) {
    $items = Get-Files (Join-Path $Root $pair[0])
    Add-Category $pair[1] $items @($items | Where-Object { $_.LastWriteTime -lt $Cutoff })
}

# 4. The learn-ab folders from the render experiments (whole folder, by its own age).
$abAll = New-Object System.Collections.ArrayList
$abOld = New-Object System.Collections.ArrayList
foreach ($dir in @(Get-ChildItem -LiteralPath (Join-Path $Root 'Saved') -Directory -ErrorAction SilentlyContinue |
                   Where-Object { $_.Name -like 'learn_ab*' })) {
    $abFiles = @(Get-Files $dir.FullName)
    foreach ($file in $abFiles) { [void]$abAll.Add($file) }
    if ($dir.LastWriteTime -lt $Cutoff) {
        foreach ($file in $abFiles) { [void]$abOld.Add($file) }
    }
}
Add-Category 'Saved\learn_ab*' $abAll $abOld

# 5. Loose files in Saved root: captures and tool argument files from past runs.
$loose = @(Get-ChildItem -LiteralPath (Join-Path $Root 'Saved') -File -ErrorAction SilentlyContinue |
           Where-Object { $_.Extension -in @('.txt', '.json', '.png', '.jpg', '.bmp', '.log') })
Add-Category 'Saved\* (loose)' $loose @($loose | Where-Object { $_.LastWriteTime -lt $Cutoff })

# 6. Opt-in: the build intermediate. Regenerable, but it costs a full rebuild.
if ($IncludeIntermediate) {
    $build = Get-Files (Join-Path $Root 'Intermediate\Build')
    Add-Category 'Intermediate\Build' $build $build
}

# ------------------------------------------------------------------ report --

$savedAll = @(Get-ChildItem -LiteralPath (Join-Path $Root 'Saved') -Recurse -File -ErrorAction SilentlyContinue)
$savedMB = Get-SizeMB $savedAll
$triggered = ($savedMB -ge $SavedTriggerMB) -or ($shots.Count -ge $ScreenshotTrigger)

Write-Host ''
Write-Host ('Cleanup plan  root={0}' -f $Root)
Write-Host ('keep: {0} days, newest {1} screenshots, newest {2} logs' -f $KeepDays, $KeepShots, $KeepLogs)
Write-Host ('mode: {0}' -f $(if ($Apply) { 'APPLY' } else { 'dry run (add -Apply to delete)' }))
Write-Host ''
$Rows | Format-Table -AutoSize | Out-String -Width 200 | Write-Host

$dropFiles = $Targets.Count
$dropMB = Get-SizeMB $Targets
Write-Host ('would delete: {0} files, {1:N1} MB' -f $dropFiles, $dropMB)
Write-Host ('Saved now: {0:N1} MB (trigger {1:N0} MB), screenshots {2} (trigger {3}) -> {4}' -f
            $savedMB, $SavedTriggerMB, $shots.Count, $ScreenshotTrigger,
            $(if ($triggered) { 'ABOVE threshold' } else { 'below threshold, nothing urgent' }))

if (-not $Apply) {
    Write-Host ''
    Write-Host 'dry run only; nothing was deleted.'
    exit 0
}

if ($IncludeIntermediate) {
    $editor = Get-Process -Name UnrealEditor -ErrorAction SilentlyContinue
    if ($editor) {
        Write-Host 'REFUSED: Intermediate\Build needs the editor closed (Live Coding holds the files).'
        exit 1
    }
}

# ------------------------------------------------------------------- apply --

$deleted = 0
$failed = 0
foreach ($item in $Targets) {
    $full = $item.FullName
    if (-not $full.StartsWith($Root, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Host ('SKIP (outside root): {0}' -f $full)
        $failed++
        continue
    }
    try {
        Remove-Item -LiteralPath $full -Force -ErrorAction Stop
        $deleted++
    } catch {
        Write-Host ('FAILED: {0}  {1}' -f $full, $_.Exception.Message)
        $failed++
    }
}

# Remove folders that the learn-ab step emptied out.
foreach ($dir in @(Get-ChildItem -LiteralPath (Join-Path $Root 'Saved') -Directory -ErrorAction SilentlyContinue |
                   Where-Object { $_.Name -like 'learn_ab*' })) {
    if (-not (Get-ChildItem -LiteralPath $dir.FullName -Recurse -File -ErrorAction SilentlyContinue)) {
        Remove-Item -LiteralPath $dir.FullName -Force -ErrorAction SilentlyContinue
    }
}

$savedAfter = @(Get-ChildItem -LiteralPath (Join-Path $Root 'Saved') -Recurse -File -ErrorAction SilentlyContinue)
$savedAfterMB = Get-SizeMB $savedAfter

$line = '{0}  APPLY keep-{1}d/{2}shots  deleted {3} files {4:N1} MB  failed {5}  Saved {6:N1} -> {7:N1} MB' -f
        $Now.ToString('yyyy-MM-dd HH:mm'), $KeepDays, $KeepShots, $deleted, $dropMB, $failed, $savedMB, $savedAfterMB
Write-Host ''
Write-Host $line
$logPath = Join-Path $Root 'Saved\cleanup.log'
Add-Content -LiteralPath $logPath -Value $line -Encoding ASCII
Write-Host ('logged -> {0}' -f $logPath)
if ($failed -gt 0) { exit 1 }
exit 0
