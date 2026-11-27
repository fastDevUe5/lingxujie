#requires -Version 5.1
# Open (or focus) the Fab panel in the running editor through the UE MCP Slate inspector.
#
#   powershell -ExecutionPolicy Bypass -File Tools\fab_open.ps1
#
# Uses control refs instead of screen coordinates: the menu bar's third button (Window) ->
# popup window -> the "Fab" entry. Requires -ModelContextProtocolStartServer on the editor.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Mcp = Join-Path $Root 'Tools\mcp.ps1'
$ArgsFile = Join-Path $Root 'Saved\mcp_args.json'

function Mcp([string]$Tool, [string]$Json) {
    Set-Content -Path $ArgsFile -Value $Json -Encoding UTF8 -NoNewline
    & powershell -ExecutionPolicy Bypass -File $Mcp -Toolset 'SlateInspectorToolset.SlateInspectorToolset' `
        -Tool $Tool -ArgsFile $ArgsFile | Out-Null
}

function McpText([string]$Tool, [string]$Json, [string]$Out) {
    Set-Content -Path $ArgsFile -Value $Json -Encoding UTF8 -NoNewline
    & powershell -ExecutionPolicy Bypass -File $Mcp -Toolset 'SlateInspectorToolset.SlateInspectorToolset' `
        -Tool $Tool -ArgsFile $ArgsFile -OutFile $Out | Out-Null
    $path = Join-Path $Root $Out
    if (Test-Path $path) { Get-Content $path -Raw } else { '' }
}

function Unescape([string]$text) { $text -replace '\\n', "`n" -replace '\\"', '"' }

$snapshot = Unescape (McpText 'Snapshot' '{"ref":"","maxDepth":3}' 'Saved\fabopen_snap.txt')
$windowRef = ''
foreach ($line in ($snapshot -split "`n")) {
    if ($line -match 'window ".*\[ref=(w\d+)\]') { $windowRef = $matches[1]; break }
}
if (-not $windowRef) { throw 'could not find the editor window ref' }

Mcp 'Observe' ('{"ref":"' + $windowRef + '","maxDepth":30}')
Start-Sleep -Seconds 2
$tree = Unescape (McpText 'Snapshot' ('{"ref":"' + $windowRef + '","maxDepth":30}') 'Saved\fabopen_tree.txt')

# menu bar buttons sit on one row near the top; the third one is Window
$menuButtons = @()
foreach ($line in ($tree -split "`n")) {
    if ($line -match 'button .*\[pos=(\d+),(\d+) size=(\d+),(\d+)\] \[ref=(b\d+)\]') {
        $y = [int]$matches[2]
        $x = [int]$matches[1]
        if ($y -ge 330 -and $y -le 350 -and $x -lt 900) {
            $menuButtons += [pscustomobject]@{ x = $x; ref = $matches[5] }
        }
    }
}
$menuButtons = $menuButtons | Sort-Object x
if ($menuButtons.Count -lt 3) { throw ('expected at least 3 menu buttons, found ' + $menuButtons.Count) }
$menuRef = $menuButtons[2].ref
Write-Host "window menu ref: $menuRef (buttons: $(($menuButtons | ForEach-Object { $_.ref }) -join ', '))"

Mcp 'Click' ('{"ref":"' + $menuRef + '"}')
Start-Sleep -Seconds 2

$after = Unescape (McpText 'Snapshot' '{"ref":"","maxDepth":3}' 'Saved\fabopen_after.txt')
$popupRef = ''
foreach ($line in ($after -split "`n")) {
    if ($line -match 'window \[pos=.*\[ref=(w\d+)\]') { $popupRef = $matches[1] }
}
if (-not $popupRef) { throw 'window menu did not open a popup' }

Mcp 'Observe' ('{"ref":"' + $popupRef + '","maxDepth":30}')
Start-Sleep -Seconds 2
$popup = Unescape (McpText 'Snapshot' ('{"ref":"' + $popupRef + '","maxDepth":30}') 'Saved\fabopen_popup.txt')

$fabRef = ''
foreach ($line in ($popup -split "`n")) {
    if ($line -match 'generic "Fab" .*\[ref=(g\d+)\]') { $fabRef = $matches[1]; break }
}
if (-not $fabRef) { throw 'could not find the Fab entry in the Window menu' }

Mcp 'Click' ('{"ref":"' + $fabRef + '"}')
Start-Sleep -Seconds 8
Write-Host "opened Fab (entry ref $fabRef)"
