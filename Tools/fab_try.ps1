#requires -Version 5.1
# Try several Fab search terms in a row: search -> first result -> add to library -> add to
# project -> wait -> report log lines and whether Content actually changed.
#
#   powershell -ExecutionPolicy Bypass -File Tools\fab_try.ps1 -Terms "wood planks","dirt ground"
#
# Prints one block per term so it is obvious which asset installed content and which did not.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string[]]$Terms = @('wood planks'),
    [int]$WaitSeconds = 45
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

foreach ($term in $Terms) {
    Write-Host ""
    Write-Host ("=== " + $term + " ===")
    $before = (Get-ChildItem (Join-Path $Root 'Content') -Recurse -File | Measure-Object).Count
    $logBefore = (Select-String -Path $Log -Pattern 'LogFab').Count

    DoUi -Action 'activate' -Title 'Fab'
    Start-Sleep -Milliseconds 700
    DoUi -Action 'click' -X 1180 -Y 449
    Start-Sleep -Milliseconds 500
    DoUi -Action 'key' -Keys '^a'
    Set-Clipboard -Value $term
    DoUi -Action 'key' -Keys '^v'
    Start-Sleep -Milliseconds 400
    DoUi -Action 'key' -Keys '{ENTER}'
    Start-Sleep -Seconds 8

    DoUi -Action 'click' -X 1114 -Y 671
    Start-Sleep -Seconds 8
    DoUi -Action 'click' -X 1574 -Y 827
    Start-Sleep -Seconds 7
    DoUi -Action 'click' -X 1574 -Y 789
    Write-Host "submitted, waiting $WaitSeconds s"
    Start-Sleep -Seconds $WaitSeconds

    $after = (Get-ChildItem (Join-Path $Root 'Content') -Recurse -File | Measure-Object).Count
    Write-Host ("content files: {0} -> {1}" -f $before, $after)
    Select-String -Path $Log -Pattern 'LogFab' | Select-Object -Skip $logBefore | Select-Object -Last 5 |
        ForEach-Object { Write-Host ("  " + $_.Line.Substring(0, [Math]::Min(140, $_.Line.Length))) }
}
