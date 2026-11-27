#requires -Version 5.1
# Regenerate the level *inside* the running editor - no closing, no separate commandlet.
#
#   powershell -ExecutionPolicy Bypass -File Tools\RebuildInEditor.ps1
#   powershell -ExecutionPolicy Bypass -File Tools\RebuildInEditor.ps1 -Script Tools\build_level.py
#
# Types `py "<script>"` into the editor's console box (bottom status bar) and waits for the
# builder's "Done. N actors" line in the log. The editor window must be visible (not minimised);
# any modal dialog will block it, so close dialogs first.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Script = 'Tools\build_level.py',
    [int]$TimeoutSeconds = 240,
    [string]$WaitPattern = 'Done\. \d+ actors'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$UI = Join-Path $Root 'Tools\ui.ps1'
$Log = Join-Path $Root 'Saved\Logs\LingXuJie.log'
$FullScript = (Join-Path $Root $Script) -replace '\\', '/'

Add-Type @"
using System;using System.Text;using System.Runtime.InteropServices;
public static class EWin {
 [DllImport("user32.dll")] public static extern bool EnumWindows(E cb, IntPtr p);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int c);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RC r);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 public delegate bool E(IntPtr h, IntPtr p);
 [StructLayout(LayoutKind.Sequential)] public struct RC { public int L,T,Rt,B; }
 public static IntPtr Find(string needle){ IntPtr best=IntPtr.Zero; EnumWindows((h,p)=>{ if(!IsWindowVisible(h)) return true;
   var sb=new StringBuilder(512); GetWindowText(h,sb,512); if(sb.ToString().Contains(needle)) best=h; return true; }, IntPtr.Zero); return best; }
 public static int[] Rect(IntPtr h){ RC r; GetWindowRect(h, out r); return new int[] { r.L, r.T, r.Rt - r.L, r.B - r.T }; }
}
"@

$editor = [EWin]::Find('LingXuJie - ')
if ($editor -eq [IntPtr]::Zero) { throw 'the Unreal editor window was not found - is it running?' }
$rect = [EWin]::Rect($editor)
$left = $rect[0]; $top = $rect[1]; $width = $rect[2]
Write-Host ("editor window: {0},{1} {2}x{3}" -f $left, $top, $width, $rect[3])

# A crash reporter or a "restore packages" box swallows the keystrokes we are about to send and
# then the script just looks like it timed out. Clear those first, and say so.
$guard = Join-Path $PSScriptRoot 'EditorGuard.ps1'
& powershell -ExecutionPolicy Bypass -File $guard -Action check | Out-Null
if ($LASTEXITCODE -eq 1) {
    Write-Host 'modal window is blocking automation - clearing it first'
    & powershell -ExecutionPolicy Bypass -File $guard -Action dismiss | Out-Null
}

# console box sits on the bottom status bar: "Cmd" dropdown then the "输入控制台命令" field.
# Measured against the current layout (editor 1494 wide): the field spans x 265..530, so its
# centre is ~26.6% of the width, and it is centred ~10 px above the bottom edge. The old
# 0.334/-13 guess landed on the status bar's blank area and the click never focused the field.
Add-Type -AssemblyName System.Windows.Forms
$work = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$consoleX = $left + [int]($width * 0.266)
$consoleY = $top + $rect[3] - 10
if ($consoleY -gt ($work.Bottom - 8)) { $consoleY = $work.Bottom - 8 }
Write-Host ("console click at {0},{1} (work area bottom {2})" -f $consoleX, $consoleY, $work.Bottom)

& powershell -ExecutionPolicy Bypass -File $UI -Action activate -Title 'LingXuJie - ' | Out-Null
Start-Sleep -Milliseconds 800
& powershell -ExecutionPolicy Bypass -File $UI -Action click -X $consoleX -Y $consoleY | Out-Null
Start-Sleep -Milliseconds 600

Set-Clipboard -Value ('py "' + $FullScript + '"')
& powershell -ExecutionPolicy Bypass -File $UI -Action key -Keys '^v' | Out-Null
Start-Sleep -Milliseconds 400
& powershell -ExecutionPolicy Bypass -File $UI -Action key -Keys '{ENTER}' | Out-Null
Write-Host ("sent py command for {0}, waiting for the builder ..." -f $Script)

$before = (Select-String -Path $Log -Pattern $WaitPattern).Count
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 5
    # A dead editor never writes the line we are waiting for: detect the crash instead of
    # sitting out the whole timeout, clear the reporter and bring the editor back.
    if (-not (Get-Process UnrealEditor -ErrorAction SilentlyContinue)) {
        Write-Host 'the editor process is gone - it crashed while running the script'
        & powershell -ExecutionPolicy Bypass -File $guard -Action restart
        Write-Host 'editor restarted; if the window moved, run Tools\SetupLayout.ps1'
        exit 1
    }
    $now = (Select-String -Path $Log -Pattern $WaitPattern).Count
    if ($now -gt $before) {
        Select-String -Path $Log -Pattern '\[LingXuJie\]' | Select-Object -Last 12 |
            ForEach-Object { Write-Host ('  ' + $_.Line.Substring(0, [Math]::Min(150, $_.Line.Length))) }
        Write-Host 'level regenerated inside the editor'
        exit 0
    }
}
Write-Host 'timed out waiting for the builder; last log lines:'
Get-Content $Log -Tail 10 | ForEach-Object { Write-Host ('  ' + $_.Substring(0, [Math]::Min(150, $_.Length))) }
$crash = Get-ChildItem (Join-Path $Root 'Saved\Crashes') -Directory -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($crash -and $crash.LastWriteTime -gt (Get-Date).AddMinutes(-10)) {
    Write-Host ('a crash dump was written {0}: {1}' -f $crash.LastWriteTime, $crash.FullName)
    Write-Host 'run Tools\EditorGuard.ps1 -Action dismiss - then rebuild'
}
exit 1
