#requires -Version 5.1
# End-to-end check of a packaged LingXuJie build:
#   launch -> drive a short input sequence (walk + attack) -> screenshot -> read the log.
# Usage: powershell -ExecutionPolicy Bypass -File Tools\VerifyPackage.ps1
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [string]$Config = 'Shipping',
    [string]$PackageRoot = '',
    [string]$Seq = 'W:3|J:0.4|J:0.4',
    [int]$StartDelaySeconds = 12,
    [int]$RunSeconds = 14
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($PackageRoot)) {
    $PackageRoot = "Saved\Package\$Config\Windows"
}
$Pkg = Join-Path $Root $PackageRoot
$Shots = Join-Path $Root 'Saved\Screenshots'
New-Item -ItemType Directory -Force -Path $Shots | Out-Null

# Prefer the real shipping binary: the root LingXuJie.exe is a bootstrap that hands off to
# a *different* process, so its PID has no window and the screenshot logic cannot follow it.
# Running the shipping exe from its archive location still resolves ..\..\..\Engine fine.
$Exe = Join-Path $Pkg 'LingXuJie\Binaries\Win64\LingXuJie-Win64-Shipping.exe'
if (-not (Test-Path $Exe)) {
    $candidate = Get-ChildItem (Join-Path $Pkg 'LingXuJie\Binaries\Win64') -Filter 'LingXuJie*.exe' -ErrorAction SilentlyContinue |
        Sort-Object Length -Descending | Select-Object -First 1
    if ($candidate) { $Exe = $candidate.FullName }
}
if (-not (Test-Path $Exe)) { throw "packaged exe not found under $Pkg" }
Write-Host "exe: $Exe"

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class PkgWin {
    public delegate bool EnumProc(IntPtr h, IntPtr p);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);

    public static List<IntPtr> ForPid(uint target) {
        var list = new List<IntPtr>();
        EnumWindows((h, p) => {
            uint pid; GetWindowThreadProcessId(h, out pid);
            if (pid == target && IsWindowVisible(h)) list.Add(h);
            return true;
        }, IntPtr.Zero);
        return list;
    }

    public static IntPtr Largest(uint pid) {
        IntPtr best = IntPtr.Zero; int area = 0;
        foreach (IntPtr h in ForPid(pid)) {
            RECT r; if (!GetWindowRect(h, out r)) continue;
            int a = (r.Right - r.Left) * (r.Bottom - r.Top);
            if (a > area) { area = a; best = h; }
        }
        return best;
    }

    public static void Key(IntPtr h, int vk, bool down) {
        uint msg = down ? 0x0100u : 0x0101u;
        PostMessage(h, msg, (IntPtr)vk, (IntPtr)0);
    }

    public static bool Close(IntPtr h) {
        return PostMessage(h, 0x0010u, IntPtr.Zero, IntPtr.Zero); // WM_CLOSE
    }

    public static bool Capture(IntPtr h, string path) {
        RECT r; if (!GetWindowRect(h, out r)) return false;
        int w = r.Right - r.Left, ht = r.Bottom - r.Top;
        if (w <= 0 || ht <= 0) return false;
        using (var bmp = new System.Drawing.Bitmap(w, ht)) {
            using (var g = System.Drawing.Graphics.FromImage(bmp)) {
                g.CopyFromScreen(r.Left, r.Top, 0, 0, bmp.Size);
            }
            bmp.Save(path, System.Drawing.Imaging.ImageFormat.Png);
        }
        return true;
    }
}
"@ -ReferencedAssemblies System.Drawing

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $Exe
$psi.Arguments = '-windowed -resx=1280 -resy=720 -log -NoSplash'
$psi.WorkingDirectory = Split-Path -Parent $Exe
$psi.UseShellExecute = $false
$proc = [System.Diagnostics.Process]::Start($psi)
Write-Host "launched pid=$($proc.Id)"
Start-Sleep -Seconds $StartDelaySeconds

if ($proc.HasExited) {
    throw "game exited during startup (code $($proc.ExitCode)) - see the log below"
}

$hwnd = [PkgWin]::Largest([uint32]$proc.Id)
Write-Host "window=$hwnd"
[void][PkgWin]::ShowWindow($hwnd, 9)
[void][PkgWin]::SetForegroundWindow($hwnd)
Start-Sleep -Milliseconds 800

foreach ($step in $Seq.Split('|')) {
    $parts = $step.Split(':')
    if ($parts.Length -ne 2) { continue }
    $keys = $parts[0].ToUpper()
    $duration = [double]::Parse($parts[1], [Globalization.CultureInfo]::InvariantCulture)
    $vks = @()
    foreach ($token in $keys.Split('+')) {
        switch ($token) {
            'SPACE' { $vks += 0x20 }
            'SHIFT' { $vks += 0x10 }
            default { if ($token.Length -eq 1) { $vks += [int][char]$token } }
        }
    }
    Write-Host "  hold $keys for $duration s"
    foreach ($vk in $vks) { [PkgWin]::Key($hwnd, $vk, $true) }
    Start-Sleep -Milliseconds ([int]($duration * 1000))
    foreach ($vk in $vks) { [PkgWin]::Key($hwnd, $vk, $false) }
    Start-Sleep -Milliseconds 250
}

Start-Sleep -Seconds $RunSeconds
$shot = Join-Path $Shots 'Pkg_Run.png'
Write-Host ("screenshot: " + [PkgWin]::Capture([PkgWin]::Largest([uint32]$proc.Id), $shot))

$alive = -not $proc.HasExited
Write-Host "alive_after_sequence=$alive"

# Close through the window so the engine shuts down and flushes its log.
$proc.Refresh()
[void][PkgWin]::Close([PkgWin]::Largest([uint32]$proc.Id))
if (-not $proc.WaitForExit(8000)) { $proc.Kill(); Write-Host 'killed (no graceful exit)' } else { Write-Host "exit code: $($proc.ExitCode)" }

# Packaged builds write their log under %LOCALAPPDATA% (gotcha #27), Development also
# keeps one inside the package. Look in both.
$logs = @(
    (Join-Path $Pkg 'LingXuJie\Saved\Logs\LingXuJie.log'),
    (Join-Path $env:LOCALAPPDATA 'LingXuJie\Saved\Logs\LingXuJie.log')
) | Where-Object { Test-Path $_ }
$log = $logs | Select-Object -First 1
if ($log) {
    Write-Host "log: $log"
    $ready = Select-String -Path $log -Pattern '\[LingXuJie\] Player ready' | Select-Object -First 1
    $errors = Select-String -Path $log -Pattern 'Error: |Fatal error'
    Write-Host ("marker_player_ready=" + [bool]$ready)
    Write-Host ("error_lines=" + $errors.Count)
    if ($errors.Count -gt 0) { $errors | Select-Object -First 5 | ForEach-Object { Write-Host $_.Line } }
}
else {
    Write-Host "WARNING: no packaged log found (checked the package and %LOCALAPPDATA%)" -ForegroundColor Yellow
}

if (-not $alive) { throw 'game died during the run' }
if (-not (Test-Path $shot)) { throw 'screenshot was not written' }
Write-Host 'DONE'
