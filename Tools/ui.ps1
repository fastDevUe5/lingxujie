#requires -Version 5.1
# Tiny UI automation helper: screenshot, click, wheel, type, focus a window by title.
# Used when a task genuinely needs a human-like interaction (e.g. a web view inside a panel).
#
#   powershell -ExecutionPolicy Bypass -File Tools\ui.ps1 -Action shot -Out Saved\Screenshots\ui.png
#   powershell -ExecutionPolicy Bypass -File Tools\ui.ps1 -Action click -X 100 -Y 200
#   powershell -ExecutionPolicy Bypass -File Tools\ui.ps1 -Action wheel -X 100 -Y 200 -Keys 600
#   powershell -ExecutionPolicy Bypass -File Tools\ui.ps1 -Action activate -Title "Fab"
#
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [Parameter(Mandatory = $true)][ValidateSet('shot', 'click', 'dclick', 'focus', 'maximize', 'key', 'activate', 'wheel')]
    [string]$Action,
    [int]$X = 0,
    [int]$Y = 0,
    [string]$Out = '',
    [string]$Title = '',
    [string]$Keys = ''
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;
public static class Ui {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr SetActiveWindow(IntPtr h);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int c);
    public delegate bool EnumProc(IntPtr h, IntPtr p);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }

    public static IntPtr FindByTitle(string needle) {
        IntPtr best = IntPtr.Zero; int area = 0;
        EnumWindows((h, p) => {
            if (!IsWindowVisible(h)) return true;
            var sb = new StringBuilder(512); GetWindowText(h, sb, 512);
            if (!sb.ToString().Contains(needle)) return true;
            RECT r; if (!GetWindowRect(h, out r)) return true;
            int a = (r.Right - r.Left) * (r.Bottom - r.Top);
            if (a > area) { area = a; best = h; }
            return true;
        }, IntPtr.Zero);
        return best;
    }

    public static void Click(int x, int y, bool dbl) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(120);
        mouse_event(0x0002, 0, 0, 0, IntPtr.Zero);
        System.Threading.Thread.Sleep(60);
        mouse_event(0x0004, 0, 0, 0, IntPtr.Zero);
        if (dbl) {
            System.Threading.Thread.Sleep(90);
            mouse_event(0x0002, 0, 0, 0, IntPtr.Zero);
            System.Threading.Thread.Sleep(60);
            mouse_event(0x0004, 0, 0, 0, IntPtr.Zero);
        }
    }

    public static void Wheel(int x, int y, int delta) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(120);
        mouse_event(0x0800, 0, 0, (uint)delta, IntPtr.Zero);
    }
}
"@
[Ui]::SetProcessDPIAware() | Out-Null

switch ($Action) {
    'focus' {
        $h = [Ui]::FindByTitle($Title)
        if ($h -eq [IntPtr]::Zero) { Write-Host "window not found: $Title"; exit 1 }
        [void][Ui]::ShowWindow($h, 9)
        [void][Ui]::SetForegroundWindow($h)
        Write-Host "focused: $h"
    }
    'activate' {
        $h = [Ui]::FindByTitle($Title)
        if ($h -eq [IntPtr]::Zero) { Write-Host "window not found: $Title"; exit 1 }
        [void][Ui]::ShowWindow($h, 9)
        $fg = [Ui]::GetForegroundWindow()
        $fgThread = [Ui]::GetWindowThreadProcessId($fg, [ref]([uint32]0))
        $myThread = [Ui]::GetCurrentThreadId()
        [void][Ui]::AttachThreadInput($myThread, $fgThread, $true)
        [void][Ui]::BringWindowToTop($h)
        [void][Ui]::SetForegroundWindow($h)
        [void][Ui]::SetActiveWindow($h)
        [void][Ui]::AttachThreadInput($myThread, $fgThread, $false)
        Write-Host "activated: $h"
    }
    'maximize' {
        $h = [Ui]::FindByTitle($Title)
        if ($h -eq [IntPtr]::Zero) { Write-Host "window not found: $Title"; exit 1 }
        [void][Ui]::ShowWindow($h, 3)
        [void][Ui]::SetForegroundWindow($h)
        Write-Host "maximized: $h"
    }
    'click' { [Ui]::Click($X, $Y, $false); Write-Host "clicked $X,$Y" }
    'dclick' { [Ui]::Click($X, $Y, $true); Write-Host "double-clicked $X,$Y" }
    'wheel' {
        $delta = 0
        if (-not [int]::TryParse($Keys, [ref]$delta)) { $delta = 600 }
        [Ui]::Wheel($X, $Y, $delta)
        Write-Host "wheel $delta at $X,$Y"
    }
    'key' {
        [System.Windows.Forms.SendKeys]::SendWait($Keys)
        Write-Host "sent keys: $Keys"
    }
    'shot' {
        if ([string]::IsNullOrWhiteSpace($Out)) { throw 'need -Out for a screenshot' }
        $vs = [System.Windows.Forms.SystemInformation]::VirtualScreen
        $bmp = New-Object System.Drawing.Bitmap $vs.Width, $vs.Height
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($vs.X, $vs.Y, 0, 0, $bmp.Size)
        $bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose(); $bmp.Dispose()
        Write-Host "shot: $Out ($($vs.Width)x$($vs.Height))"
    }
}
