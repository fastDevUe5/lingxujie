#requires -Version 5.1
# Add one Fab listing, coping with the two button layouts seen on listing pages.
#
#   powershell -ExecutionPolicy Bypass -File Tools\fab_add2.ps1 -Term "megaplants grass"
#
# Listing pages either have a quality dropdown (Add-to-project sits lower, screen y ~789) or
# not (y ~747). The script clicks the upper spot first, checks the Fab log for a new
# "Add listing to project" line, and falls back to the lower spot when nothing happened.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [Parameter(Mandatory = $true)][string]$Term,
    [int]$WaitSeconds = 55
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$UI = Join-Path $Root 'Tools\ui.ps1'
$Log = Join-Path $Root 'Saved\Logs\LingXuJie.log'

function DoUi([string]$Action, [int]$X = 0, [int]$Y = 0, [string]$Title = '', [string]$Keys = '') {
    $argumentList = @('-ExecutionPolicy', 'Bypass', '-File', $UI, '-Action', $Action)
    if ($X -ne 0 -or $Y -ne 0) { $argumentList += @('-X', "$X", '-Y', "$Y") }
    if (-not [string]::IsNullOrWhiteSpace($Title)) { $argumentList += @('-Title', $Title) }
    if (-not [string]::IsNullOrWhiteSpace($Keys)) { $argumentList += @('-Keys', $Keys) }
    & powershell @argumentList | Out-Null
}

function AddListingCount { (Select-String -Path $Log -Pattern 'Add listing to project').Count }

$before = (Get-ChildItem (Join-Path $Root 'Content') -Recurse -File | Measure-Object).Count

& powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'Tools\fab_open.ps1') | Out-Null
Start-Sleep -Seconds 3
DoUi -Action 'activate' -Title 'Fab'
Start-Sleep -Milliseconds 700
DoUi -Action 'click' -X 1180 -Y 449
Start-Sleep -Milliseconds 500
DoUi -Action 'key' -Keys '^a'
Set-Clipboard -Value $Term
DoUi -Action 'key' -Keys '^v'
Start-Sleep -Milliseconds 400
DoUi -Action 'key' -Keys '{ENTER}'
Start-Sleep -Seconds 8

DoUi -Action 'click' -X 1114 -Y 671
Start-Sleep -Seconds 8

$countBefore = AddListingCount
DoUi -Action 'click' -X 1574 -Y 827      # add to library (same spot in both layouts)
Start-Sleep -Seconds 6
DoUi -Action 'click' -X 1575 -Y 747      # add to project, no-dropdown layout
Start-Sleep -Seconds 8
if ((AddListingCount) -eq $countBefore) {
    Write-Host 'upper button did nothing, trying the dropdown layout'
    DoUi -Action 'click' -X 1575 -Y 789
    Start-Sleep -Seconds 8
}
if ((AddListingCount) -eq $countBefore) { Write-Host 'WARNING: no Add listing line appeared at all' }

Write-Host "submitted '$Term', waiting $WaitSeconds s"
Start-Sleep -Seconds $WaitSeconds
$after = (Get-ChildItem (Join-Path $Root 'Content') -Recurse -File | Measure-Object).Count
Write-Host ("content files: {0} -> {1}" -f $before, $after)
Select-String -Path $Log -Pattern 'LogFab' | Select-Object -Last 3 |
    ForEach-Object { Write-Host ('  ' + $_.Line.Substring(0, [Math]::Min(140, $_.Line.Length))) }
