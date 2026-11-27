#requires -Version 5.1
# Call a UE MCP toolset tool: toolset + short tool name + JSON args file.
#
#   powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 `
#       -Toolset "SlateInspectorToolset.SlateInspectorToolset" -Tool "Snapshot" `
#       -ArgsFile Saved\mcp_args.json -OutFile Saved\snapshot.txt
#   powershell -ExecutionPolicy Bypass -File Tools\mcp.ps1 -Top "list_toolsets"
#
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Toolset = '',
    [string]$Tool = '',
    [string]$Top = '',
    [string]$ArgsFile = '',
    [string]$OutFile = ''
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Url = 'http://127.0.0.1:8000/mcp'
$SessionFile = Join-Path $Root 'Saved\ue_mcp_session.txt'

$argsJson = '{}'
if (-not [string]::IsNullOrWhiteSpace($ArgsFile) -and (Test-Path $ArgsFile)) {
    $raw = (Get-Content $ArgsFile -Raw).Trim()
    if (-not [string]::IsNullOrWhiteSpace($raw)) { $argsJson = $raw }
}

if (-not [string]::IsNullOrWhiteSpace($Top)) {
    $callArgs = '{"tool_name":"' + $Top + '","arguments":' + $argsJson + '}'
} else {
    $callArgs = '{"toolset_name":"' + $Toolset + '","tool_name":"' + $Tool + '","arguments":' + $argsJson + '}'
}
$body = '{"jsonrpc":"2.0","id":42,"method":"tools/call","params":{"name":"call_tool","arguments":' + $callArgs + '}}'

function Read-Session { if (Test-Path $SessionFile) { (Get-Content $SessionFile -Raw).Trim() } else { '' } }

function New-Session {
    $init = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"dsh-tools","version":"1.0"}}}'
    $resp = Invoke-WebRequest -Uri $Url -Method Post -Body $init -ContentType 'application/json' `
        -Headers @{ Accept = 'application/json, text/event-stream' } -UseBasicParsing -TimeoutSec 60
    $sid = $resp.Headers['Mcp-Session-Id']
    if (-not $sid) { throw 'no Mcp-Session-Id from initialize' }
    Set-Content -Path $SessionFile -Value $sid -NoNewline
    try {
        Invoke-WebRequest -Uri $Url -Method Post -Body '{"jsonrpc":"2.0","method":"notifications/initialized"}' `
            -ContentType 'application/json' -Headers @{ Accept = 'application/json, text/event-stream'; 'Mcp-Session-Id' = $sid } `
            -UseBasicParsing -TimeoutSec 30 | Out-Null
    } catch { }
    return $sid
}

function Post-Body($sid) {
    Invoke-WebRequest -Uri $Url -Method Post -Body $body -ContentType 'application/json' `
        -Headers @{ Accept = 'application/json, text/event-stream'; 'Mcp-Session-Id' = $sid } -UseBasicParsing -TimeoutSec 300
}

$sid = Read-Session
if (-not $sid) { $sid = New-Session }
try { $resp = Post-Body $sid } catch { $sid = New-Session; $resp = Post-Body $sid }

$raw = [string]$resp.Content
if ($raw.TrimStart().StartsWith('event:') -or $raw.TrimStart().StartsWith('data:')) {
    $raw = ((($raw -split "`n") | Where-Object { $_ -match '^data:\s*' } | ForEach-Object { $_ -replace '^data:\s*', '' }) -join '').Trim()
}

$obj = $raw | ConvertFrom-Json
if ($obj.error) { Write-Host ('MCP error: ' + ($obj.error | ConvertTo-Json -Compress)); exit 1 }

$text = ''
$imagePath = ''
if ($obj.result -and $obj.result.content) {
    $text = (($obj.result.content | Where-Object { $_.type -eq 'text' } | ForEach-Object { $_.text }) -join "`n")
    $image = $obj.result.content | Where-Object { $_.type -eq 'image' } | Select-Object -First 1
    if ($image) {
        # save binary so read_image can inspect it
        $imagePath = if ($OutFile) { [System.IO.Path]::ChangeExtension($OutFile, '.png') } else { '' }
        if ($imagePath) {
            [System.IO.File]::WriteAllBytes((Join-Path $Root $imagePath), [Convert]::FromBase64String($image.data))
            Write-Host ("image saved: $imagePath")
        }
    }
} else { $text = $raw }

if ([string]::IsNullOrWhiteSpace($text)) { $text = '(empty result)' }
if (-not [string]::IsNullOrWhiteSpace($OutFile)) {
    Set-Content -Path (Join-Path $Root $OutFile) -Value $text -Encoding UTF8
    Write-Host ("wrote {0} chars -> {1}" -f $text.Length, $OutFile)
} else {
    Write-Host $text
}
