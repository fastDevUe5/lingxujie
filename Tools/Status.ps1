#requires -Version 5.1
#
# One screen that answers "can I work right now?": editor, MCP, level, camera, git, disk.
#
#   powershell -ExecutionPolicy Bypass -File Tools\Status.ps1
#   powershell -ExecutionPolicy Bypass -File Tools\Status.ps1 -NoMcp      (skip the editor query, faster)
#
# Read-only. It prints, it does not fix anything: EditorGuard has the fixing verbs.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [switch]$NoMcp
)

$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
$Scratch = Join-Path $Root 'Saved\scratch'
New-Item -ItemType Directory -Force -Path $Scratch | Out-Null

function Test-Port([string]$HostName = '127.0.0.1', [int]$Port = 8000, [int]$TimeoutMs = 600) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $task = $client.ConnectAsync($HostName, $Port)
        if (-not $task.Wait($TimeoutMs)) { return $false }
        return $client.Connected
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

# ---------------------------------------------------------------- process --

$editor = Get-Process UnrealEditor -ErrorAction SilentlyContinue
$editorText = if ($editor) { ('running (pid {0})' -f $editor.Id) } else { 'NOT RUNNING' }

# ------------------------------------------------------------------- mcp --

$mcpUp = Test-Port
$guardText = ''
if (Test-Path (Join-Path $PSScriptRoot 'EditorGuard.ps1')) {
    $guard = & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'EditorGuard.ps1') -Action check 2>&1
    $guardText = (@($guard) | Select-Object -Last 1) -replace '^\[[^\]]+\]\s*', ''
}

# ------------------------------------------------------- level / camera --

$levelText = 'unknown (mcp down)'
$actorText = '-'
$cameraText = '-'
$cameraDefault = '-'
if ($mcpUp -and -not $NoMcp) {
    $script = @'
import json

def T(n, a):
    return execute_tool(n, json.dumps(a))["returnValue"]

def run():
    out = {}
    out["level"] = T("editor_toolset.toolsets.scene.SceneTools.get_current_level", {})
    listing = T("lingxujie_tools.level_ops.LingXuJieTools.list_actors", {"prefix": ""})
    out["actors"] = len(listing)
    out["camera"] = T("EditorToolset.EditorAppToolset.GetCameraTransform", {})
    return out
'@
    # mcp.ps1 resolves these against the repo root, so keep them relative (it does Join-Path).
    $relArgs = 'Saved\scratch\status_args.json'
    $relOut = 'Saved\scratch\status_out.json'
    $argsPath = Join-Path $Root $relArgs
    $outPath = Join-Path $Root $relOut
    @{ script = [string]$script } | ConvertTo-Json -Compress | Set-Content $argsPath -Encoding ASCII
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'mcp.ps1') `
        -Toolset 'editor_toolset.toolsets.programmatic.ProgrammaticToolset' -Tool 'execute_tool_script' `
        -ArgsFile $relArgs -OutFile $relOut 2>&1 | Out-Null
    if (Test-Path $outPath) {
        try {
            $raw = Get-Content $outPath -Raw
            $outer = $raw | ConvertFrom-Json
            $inner = $outer.returnValue | ConvertFrom-Json
            if ($inner.level) { $levelText = $inner.level }
            if ($null -ne $inner.actors) { $actorText = [string]$inner.actors }
            if ($inner.camera) {
                $loc = $inner.camera.location; $rot = $inner.camera.rotation
                $cameraText = ('{0:F0}, {1:F0}, {2:F0}  yaw {3:F0}  pitch {4:F1}' -f $loc.x, $loc.y, $loc.z, $rot.yaw, $rot.pitch)
                $atDefault = ([math]::Abs($loc.x - 8950) -lt 1) -and ([math]::Abs($loc.y + 6200) -lt 1) -and
                             ([math]::Abs($loc.z - 3900) -lt 1) -and ([math]::Abs($rot.yaw) -lt 1) -and
                             ([math]::Abs($rot.pitch + 2) -lt 1)
                $cameraDefault = if ($atDefault) { 'yes' } else { 'NO - run Tools\reset_view.py' }
            }
        } catch {
            $levelText = 'unreadable result'
        }
    }
}

# ------------------------------------------------------------------- git --

$branch = (git -C $Root rev-parse --abbrev-ref HEAD 2>$null)
$dirty = @(git -C $Root status --porcelain 2>$null).Count
$ahead = 0; $behind = 0
$upstream = git -C $Root rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null
if ($LASTEXITCODE -eq 0 -and $upstream) {
    $counts = (git -C $Root rev-list --left-right --count "$upstream...HEAD" 2>$null) -split '\s+'
    $behind = [int]$counts[0]; $ahead = [int]$counts[1]
}

# ------------------------------------------------------------------ disk --

$saved = Get-ChildItem (Join-Path $Root 'Saved') -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum
$shots = @(Get-ChildItem (Join-Path $Root 'Saved\Screenshots') -File -ErrorAction SilentlyContinue).Count

# ------------------------------------------------------- stray windows --
# The editor restores whatever windows were open when it last exited, and a hard
# kill means "closed" was never recorded - that is how the Message Log keeps coming
# back and covering the viewport (AGENTS rule 6). Check for it instead of trusting
# memory. The titles are Chinese, so they are built from code points to keep this
# file ASCII.
Add-Type @"
using System;using System.Text;using System.Runtime.InteropServices;
public static class EWinStatus {
 [DllImport("user32.dll")] public static extern bool EnumWindows(E cb, IntPtr p);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int c);
 public delegate bool E(IntPtr h, IntPtr p);
 public static bool Has(string needle){ bool found=false; EnumWindows((h,p)=>{ if(!IsWindowVisible(h)) return true;
   var t=new StringBuilder(512); GetWindowText(h,t,512); if(t.ToString().Contains(needle)) found=true; return true; }, IntPtr.Zero); return found; }
}
"@
$strays = New-Object System.Collections.ArrayList
foreach ($probe in @(
    @{ Name = 'message log';    Text = (-join ([char]0x6D88, [char]0x606F, [char]0x65E5, [char]0x5FD7)) },
    @{ Name = 'save content';   Text = (-join ([char]0x4FDD, [char]0x5B58, [char]0x5185, [char]0x5BB9)) },
    @{ Name = 'restore pkgs';   Text = (-join ([char]0x6062, [char]0x590D, [char]0x5305)) }
)) {
    if ([EWinStatus]::Has($probe.Text)) { [void]$strays.Add($probe.Name) }
}
$strayText = if ($strays.Count -eq 0) { 'none' } else { ($strays -join ', ') + '  <- close: PostMessage WM_CLOSE' }

# ----------------------------------------------------------------- print --

Write-Host ''
Write-Host '== LingXuJie status =='
Write-Host ('editor     : {0}' -f $editorText)
Write-Host ('mcp  :8000 : {0}' -f $(if ($mcpUp) { 'listening' } else { 'DOWN' }))
if ($guardText) { Write-Host ('guard      : {0}' -f $guardText) }
Write-Host ('level      : {0}  |  actors {1}' -f $levelText, $actorText)
Write-Host ('camera     : {0}' -f $cameraText)
if ($cameraDefault -ne '-') { Write-Host ('             default view: {0}' -f $cameraDefault) }
Write-Host ('git        : {0}{1}  ahead {2}  behind {3}  dirty {4}' -f $branch,
            $(if ($upstream) { ' -> ' + $upstream } else { ' (no upstream)' }), $ahead, $behind, $dirty)
Write-Host ('disk       : Saved {0:N1} MB  |  screenshots {1}  (cleanup trigger 1200 MB / 600)' -f
            (($saved.Sum) / 1MB), $shots)
Write-Host ('windows    : {0}' -f $strayText)
Write-Host ''
