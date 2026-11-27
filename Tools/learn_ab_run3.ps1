#requires -Version 5.1
# Final rendering A/B pass with a complete reset list, and the destructive knob run last.
#
# The previous pass leaked state: each variant toggled a CVar that the reset list did not name, so
# "GI off" stayed off for every later variant and the last three shots were the same picture. A reset
# list has to name every knob any variant touches, in both directions.
#
#   powershell -ExecutionPolicy Bypass -File Tools\learn_ab_run3.ps1
#
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$OutDir = 'Saved\learn_ab4'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Python = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python.exe'

# Every CVar any variant below touches, at its project default. Missing one line here is what made
# pass two unreadable.
$Reset = @(
    'r.DynamicGlobalIlluminationMethod 1',
    'r.ReflectionMethod 1',
    'r.Shadow.Virtual.Enable 1',
    'r.AntiAliasingMethod 4',
    'r.Lumen.DiffuseIndirect.Allow 1',
    'r.Lumen.Reflections.Allow 1',
    'r.LumenScene.Radiosity 1',
    'r.Lumen.ScreenProbeGather.DownsampleFactor 1',
    'r.Lumen.Visualize 0',
    'r.VolumetricCloud 0'
)
$Variants = @(
    @{ name = 'ab_base';            probe = 'r.Lumen.DiffuseIndirect.Allow';              commands = @() },
    @{ name = 'ab_control';         probe = 'r.Lumen.DiffuseIndirect.Allow';              commands = @() },
    @{ name = 'ab_aa_none';         probe = 'r.AntiAliasingMethod';                       commands = @('r.AntiAliasingMethod 0') },
    @{ name = 'ab_vsm_off';         probe = 'r.Shadow.Virtual.Enable';                    commands = @('r.Shadow.Virtual.Enable 0') },
    @{ name = 'ab_radiosity_off';   probe = 'r.LumenScene.Radiosity';                     commands = @('r.LumenScene.Radiosity 0') },
    @{ name = 'ab_spg_ds4';         probe = 'r.Lumen.ScreenProbeGather.DownsampleFactor'; commands = @('r.Lumen.ScreenProbeGather.DownsampleFactor 4') },
    @{ name = 'ab_reflections_off'; probe = 'r.Lumen.Reflections.Allow';                  commands = @('r.Lumen.Reflections.Allow 0') },
    @{ name = 'ab_gi_off';          probe = 'r.Lumen.DiffuseIndirect.Allow';              commands = @('r.Lumen.DiffuseIndirect.Allow 0') }
)

New-Item -ItemType Directory -Force -Path (Join-Path $Root $OutDir) | Out-Null
$Readback = Join-Path $Root ($OutDir + '\cvar_readback.txt')
if (Test-Path $Readback) { Remove-Item $Readback -Force }

foreach ($variant in $Variants) {
    $payload = [ordered]@{
        name     = $variant.name
        camera   = @(5830.0, -1382.0, 570.0, 169.5, 4.4)
        reset    = $Reset
        commands = $variant.commands
    }
    $payload | ConvertTo-Json -Depth 4 -Compress |
        Set-Content -Path (Join-Path $Root 'Saved\learn_one.json') -Encoding ASCII
    Write-Host ('--- {0} : {1}' -f $variant.name, ($variant.commands -join '; '))

    & powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'Tools\RebuildInEditor.ps1') `
        -Script 'Tools/learn_render_one.py' -TimeoutSeconds 120 -WaitPattern 'LEARN: done' | Out-Null

    ('{"name":"' + $variant.probe + '"}') |
        Set-Content -Path (Join-Path $Root 'Saved\mcp_args.json') -Encoding ASCII
    & powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'Tools\mcp.ps1') `
        -Toolset 'EditorToolset.EditorAppToolset' -Tool 'SearchCVars' `
        -ArgsFile 'Saved\mcp_args.json' -OutFile 'Saved\cvar_tmp.json' | Out-Null
    $cvarJson = (Get-Content (Join-Path $Root 'Saved\cvar_tmp.json') -Raw -Encoding UTF8)
    [System.IO.File]::AppendAllText($Readback,
        ($variant.name + ' ' + $variant.probe + ' => ' + $cvarJson + [Environment]::NewLine),
        (New-Object System.Text.UTF8Encoding($false)))

    '{"captureTransform":null,"annotations":null,"bShowUI":false}' |
        Set-Content -Path (Join-Path $Root 'Saved\mcp_args.json') -Encoding ASCII
    & powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'Tools\mcp.ps1') `
        -Toolset 'EditorToolset.EditorAppToolset' -Tool 'CaptureViewport' `
        -ArgsFile 'Saved\mcp_args.json' -OutFile 'Saved\learn_ab_raw.json' | Out-Null
    & $Python (Join-Path $Root 'Tools\mcp_capture.py') (Join-Path $Root 'Saved\learn_ab_raw.json') `
        (Join-Path $Root ($OutDir + '\' + $variant.name + '.png')) | Out-Null
    Write-Host ('    shot -> {0}\{1}.png' -f $OutDir, $variant.name)
}

$restore = [ordered]@{ name = 'restore'; camera = @(5830.0, -1382.0, 570.0, 169.5, 4.4); reset = @(); commands = $Reset }
$restore | ConvertTo-Json -Depth 4 -Compress |
    Set-Content -Path (Join-Path $Root 'Saved\learn_one.json') -Encoding ASCII
& powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'Tools\RebuildInEditor.ps1') `
    -Script 'Tools/learn_render_one.py' -TimeoutSeconds 120 -WaitPattern 'LEARN: done' | Out-Null

# Prove the reset actually happened instead of assuming it: a shot after the restore must match the
# baseline. This is the check whose absence made pass two misread.
'{"captureTransform":null,"annotations":null,"bShowUI":false}' |
    Set-Content -Path (Join-Path $Root 'Saved\mcp_args.json') -Encoding ASCII
& powershell -ExecutionPolicy Bypass -File (Join-Path $Root 'Tools\mcp.ps1') `
    -Toolset 'EditorToolset.EditorAppToolset' -Tool 'CaptureViewport' `
    -ArgsFile 'Saved\mcp_args.json' -OutFile 'Saved\learn_ab_raw.json' | Out-Null
& $Python (Join-Path $Root 'Tools\mcp_capture.py') (Join-Path $Root 'Saved\learn_ab_raw.json') `
    (Join-Path $Root ($OutDir + '\ab_after_restore.png')) | Out-Null
Write-Host 'renderer settings restored, verification shot taken'
