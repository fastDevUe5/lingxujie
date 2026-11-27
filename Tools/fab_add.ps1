#requires -Version 5.1
# Add one Fab listing to the project through the in-editor Fab panel.
#
#   powershell -ExecutionPolicy Bypass -File Tools\fab_add.ps1 -Term "fern"
#
# Assumes the editor runs with the Fab panel docked at (777,393) 1006x606 at 100% DPI (the
# layout this project has used). Clicks: Window menu -> Fab, search box, first result,
# "Add to project", then waits for the download+import.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [Parameter(Mandatory = $true)][string]$Term,
    [int]$DownloadWaitSeconds = 45
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$UI = Join-Path $Root 'Tools\ui.ps1'
$Shot = Join-Path $Root 'Saved\Screenshots\fab_add.png'

function DoUi([string]$Action, [int]$X = 0, [int]$Y = 0, [string]$Title = '', [string]$Keys = '') {
    & powershell -ExecutionPolicy Bypass -File $UI -Action $Action -X $X -Y $Y -Title $Title -Keys $Keys | Out-Null
}

DoUi -Action 'activate' -Title 'LingXuJie'
Start-Sleep -Milliseconds 800
DoUi -Action 'click' -X 636 -Y 257
Start-Sleep -Milliseconds 1200
DoUi -Action 'click' -X 675 -Y 312
Start-Sleep -Seconds 6

DoUi -Action 'click' -X 1180 -Y 449
Start-Sleep -Milliseconds 600
DoUi -Action 'key' -Keys '^a'
Set-Clipboard -Value $Term
DoUi -Action 'key' -Keys '^v'
Start-Sleep -Milliseconds 400
DoUi -Action 'key' -Keys '{ENTER}'
Start-Sleep -Seconds 8

DoUi -Action 'click' -X 1114 -Y 671
Start-Sleep -Seconds 9

DoUi -Action 'click' -X 1574 -Y 789
Write-Host "clicked add-to-project for '$Term', waiting $DownloadWaitSeconds s"
Start-Sleep -Seconds $DownloadWaitSeconds

& powershell -ExecutionPolicy Bypass -File $UI -Action shot -Out $Shot | Out-Null
Write-Host "panel screenshot: $Shot"

$known = @('Collections', 'Developers', 'Maps', 'Materials', 'Megaplant_Library', 'Polyfork', 'Props', 'Textures', 'Fab')
Get-ChildItem (Join-Path $Root 'Content') -Directory |
    Where-Object { $known -notcontains $_.Name } |
    ForEach-Object { Write-Host ("new content dir: " + $_.Name) }