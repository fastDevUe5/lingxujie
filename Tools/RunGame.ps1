#requires -Version 5.1
# Launches the game windowed, optionally holds a key, grabs a screenshot of the
# game's client area and prints the interesting parts of the log.

param(
    [int]$Seconds = 40,
    [string]$OutFile = '',
    [string]$HoldKeys = '',
    [int]$HoldSeconds = 0,
    [string]$Sequence = '',
    [int]$SettleMs = 1200,
    [string]$ExecCmds = '',
    [string]$ExtraArgs = '',
    [string]$ExePath = '',
    [switch]$Editor,
    [switch]$KeepRunning,
    [switch]$KillExisting
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public static class GameWin
{
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr extra);

    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT point);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr extra);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint flags);

    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }

    public static string Title(IntPtr h)
    {
        var sb = new StringBuilder(512);
        GetWindowText(h, sb, sb.Capacity);
        return sb.ToString();
    }

    public static List<IntPtr> WindowsOfProcess(int pid)
    {
        var result = new List<IntPtr>();
        EnumWindows((h, e) =>
        {
            uint wpid;
            GetWindowThreadProcessId(h, out wpid);
            if (wpid == pid && IsWindowVisible(h)) result.Add(h);
            return true;
        }, IntPtr.Zero);
        return result;
    }

    /** Answer Windows Firewall prompts (Allow) so the game window is not blocked. */
    public static int DismissSecurityDialogs()
    {
        int handled = 0;
        var targets = new List<IntPtr>();
        EnumWindows((h, e) =>
        {
            if (!IsWindowVisible(h)) return true;
            string title = Title(h);
            if (title.Contains("\u5B89\u5168\u4E2D\u5FC3") || title.Contains("\u5B89\u5168\u8B66\u62A5") ||
                title.Contains("Security Alert") || title.Contains("Windows \u5B89\u5168") ||
                title.Contains("\u9632\u706B\u5899"))
            {
                targets.Add(h);
            }
            return true;
        }, IntPtr.Zero);

        foreach (IntPtr dialog in targets)
        {
            bool clicked = false;
            EnumChildWindows(dialog, (child, e) =>
            {
                string text = Title(child);
                if (text.Contains("\u5141\u8BB8") || text.Contains("Allow"))
                {
                    SendMessage(child, 0x00F5, IntPtr.Zero, IntPtr.Zero); // BM_CLICK
                    clicked = true;
                    return false;
                }
                return true;
            }, IntPtr.Zero);

            if (!clicked)
            {
                PostMessage(dialog, 0x0010, IntPtr.Zero, IntPtr.Zero); // WM_CLOSE
            }
            handled++;
        }
        return handled;
    }

    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumWindowsProc cb, IntPtr extra);

    public static void KeyDown(IntPtr hwnd, int vk)
    {
        PostMessage(hwnd, 0x0100, (IntPtr)vk, (IntPtr)0x00000001); // WM_KEYDOWN
    }

    public static void KeyUp(IntPtr hwnd, int vk)
    {
        PostMessage(hwnd, 0x0101, (IntPtr)vk, unchecked((IntPtr)(int)0xC0000001)); // WM_KEYUP
    }

    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
"@

$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$Exe = Join-Path $UE 'Engine\Binaries\Win64\UnrealEditor.exe'
$LogDir = Join-Path $Root 'Saved\Logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if ([string]::IsNullOrWhiteSpace($OutFile)) {
    $OutFile = Join-Path $Root 'Saved\Screenshots\LingXuJie.png'
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutFile) | Out-Null

[void][GameWin]::SetProcessDPIAware()

if ($KillExisting) {
    Get-Process UnrealEditor -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*LingXuJie*' } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 400
}
else {
    # Never kill a session we did not start: an open editor may hold unsaved work.
    # The screenshot is taken from this run's own pid, so leftovers only add noise.
    $running = Get-Process UnrealEditor -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host ("note: UnrealEditor already running (pid {0}); leaving it alone (use -KillExisting to force)" -f (($running | ForEach-Object { $_.Id }) -join ',')) -ForegroundColor Yellow
    }
}

$gameLog = Join-Path $LogDir 'game.log'
if (-not [string]::IsNullOrWhiteSpace($ExePath)) {
    # Packaged build: the exe embeds its project, so no .uproject argument and no -game flag.
    $Exe = $ExePath
    $gameArgs = @('-windowed', '-resx=1280', '-resy=720', '-vsync=0', '-NoSplash')
}
else {
    $gameArgs = @("`"$Project`"")
    if ($Editor) {
        $gameArgs += @('-NoSplash', '-log')
    }
    else {
        $gameArgs += @('-game', '-windowed', '-resx=1280', '-resy=720', '-vsync=0', '-NoSplash', '-NoTrace', '-log', '-FullStdOutLogOutput')
    }
}
if (-not [string]::IsNullOrWhiteSpace($ExecCmds)) {
    $gameArgs += "`"-ExecCmds=$ExecCmds`""
}
if (-not [string]::IsNullOrWhiteSpace($ExtraArgs)) {
    $gameArgs += $ExtraArgs.Split(' ')
}
# The editor's realtime Lumen/Nanite viewport competes with the game for the GPU: measured
# 64 ms frame time with the editor visible versus 7.4 ms with it minimised. Minimise it for the
# run and restore afterwards so measurements mean something.
$editorWasMinimised = $false
$editorHandle = [IntPtr]::Zero
Add-Type -TypeDefinition @"
using System;using System.Text;using System.Runtime.InteropServices;
public static class EdWin {
    [DllImport("user32.dll")] public static extern bool EnumWindows(E cb, IntPtr p);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int c);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
    public delegate bool E(IntPtr h, IntPtr p);
    public static IntPtr Find(string needle) {
        IntPtr best = IntPtr.Zero;
        EnumWindows((h,p) => {
            if (!IsWindowVisible(h)) return true;
            var sb = new StringBuilder(512); GetWindowText(h, sb, 512);
            if (sb.ToString().Contains(needle)) best = h;
            return true;
        }, IntPtr.Zero);
        return best;
    }
}
"@ -ErrorAction SilentlyContinue
if (-not ("EdWin" -as [type])) { }
$editorHandle = [EdWin]::Find('LingXuJie - ')
if ($editorHandle -ne [IntPtr]::Zero) {
    if (-not [EdWin]::IsIconic($editorHandle)) {
        [EdWin]::ShowWindow($editorHandle, 6) | Out-Null   # SW_MINIMIZE
        $editorWasMinimised = $true
        Write-Host 'editor minimised for the measurement'
        Start-Sleep -Seconds 3
    }
}
try {

if ([string]::IsNullOrWhiteSpace($ExePath)) {
    $proc = Start-Process -FilePath $Exe -ArgumentList $gameArgs -PassThru -WindowStyle Normal -RedirectStandardOutput $gameLog -RedirectStandardError "$gameLog.err"
}
else {
    # Packaged builds are unsigned: starting them through the shell pops the
    # "Open File - Security Warning" dialog and blocks automation. Use CreateProcess
    # directly instead of ShellExecute.
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Exe
    $psi.Arguments = ($gameArgs -join ' ')
    $psi.WorkingDirectory = Split-Path -Parent $Exe
    $psi.UseShellExecute = $false
    $proc = [System.Diagnostics.Process]::Start($psi)
}

Write-Host "game process started: $($proc.Id), waiting $Seconds s ..."
Start-Sleep -Seconds $Seconds

# Windows may throw a firewall prompt on top of the game. Poll for a while and
# answer it, otherwise the screenshot ends up with a system dialog in front.
for ($i = 0; $i -lt 40; $i++) {
    $dismissed = [GameWin]::DismissSecurityDialogs()
    if ($dismissed -gt 0) {
        Write-Host "handled $dismissed security dialog(s)"
        Start-Sleep -Milliseconds 900
        break
    }
    Start-Sleep -Milliseconds 250
}

if ($proc.HasExited) {
    Write-Host "GAME EXITED EARLY with code $($proc.ExitCode)"
}
else {
    $best = [IntPtr]::Zero
    $bestArea = 0
    foreach ($h in [GameWin]::WindowsOfProcess($proc.Id)) {
        $r = New-Object GameWin+RECT
        if ([GameWin]::GetWindowRect($h, [ref]$r)) {
            $area = ($r.Right - $r.Left) * ($r.Bottom - $r.Top)
            if ($area -gt $bestArea -and ($r.Right - $r.Left) -gt 200) {
                $bestArea = $area
                $best = $h
            }
        }
    }

    if ($best -eq [IntPtr]::Zero) {
        Write-Host "no visible game window found"
    }
    else {
        [void][GameWin]::ShowWindow($best, 9)   # SW_RESTORE
        [void][GameWin]::SetForegroundWindow($best)
        Start-Sleep -Milliseconds 800

        if (-not [string]::IsNullOrWhiteSpace($HoldKeys) -and $HoldSeconds -gt 0) {
            Write-Host "holding keys: $HoldKeys for $HoldSeconds s"
            $vks = @()
            foreach ($k in $HoldKeys.ToUpper().ToCharArray()) {
                if ($k -eq ' ') { $vks += 0x20 } else { $vks += [int][char]$k }
            }
            foreach ($vk in $vks) { [GameWin]::KeyDown($best, $vk) }
            Start-Sleep -Seconds $HoldSeconds
            foreach ($vk in $vks) { [GameWin]::KeyUp($best, $vk) }
            Start-Sleep -Milliseconds 400
        }

        # A scripted input sequence such as "E:0.4|W:3" (turn a little, then walk).
        if (-not [string]::IsNullOrWhiteSpace($Sequence)) {
            foreach ($step in $Sequence.Split('|')) {
                $parts = $step.Split(':')
                if ($parts.Length -ne 2) { continue }
                $keys = $parts[0].ToUpper()
                $duration = [double]::Parse($parts[1], [Globalization.CultureInfo]::InvariantCulture)
                $vks = @()
                foreach ($token in $keys.Split('+')) {
                    switch ($token) {
                        'SPACE' { $vks += 0x20 }
                        'SHIFT' { $vks += 0x10 }
                        'ENTER' { $vks += 0x0D }
                        default { if ($token.Length -eq 1) { $vks += [int][char]$token } }
                    }
                }
                Write-Host "  key '$keys' for $duration s"
                foreach ($vk in $vks) { [GameWin]::KeyDown($best, $vk) }
                Start-Sleep -Milliseconds ([int]($duration * 1000))
                foreach ($vk in $vks) { [GameWin]::KeyUp($best, $vk) }
                Start-Sleep -Milliseconds 250
            }
        }

        # Give the camera lag and physics a moment to settle before the screenshot.
        Start-Sleep -Milliseconds $SettleMs

        $client = New-Object GameWin+RECT
        [void][GameWin]::GetClientRect($best, [ref]$client)
        $origin = New-Object GameWin+POINT
        [void][GameWin]::ClientToScreen($best, [ref]$origin)
        $w = $client.Right - $client.Left
        $h = $client.Bottom - $client.Top
        Write-Host "capturing '$([GameWin]::Title($best))' client ${w}x${h} at $($origin.X),$($origin.Y)"

        # PrintWindow renders the window itself, so stray dialogs do not end up in
        # the image. Fall back to a screen grab if Direct3D refuses to cooperate.
        $windowRect = New-Object GameWin+RECT
        [void][GameWin]::GetWindowRect($best, [ref]$windowRect)
        $ww = $windowRect.Right - $windowRect.Left
        $wh = $windowRect.Bottom - $windowRect.Top
        $offsetX = [Math]::Max(0, $origin.X - $windowRect.Left)
        $offsetY = [Math]::Max(0, $origin.Y - $windowRect.Top)

        $full = New-Object System.Drawing.Bitmap($ww, $wh)
        $fg = [System.Drawing.Graphics]::FromImage($full)
        $hdc = $fg.GetHdc()
        $printed = [GameWin]::PrintWindow($best, $hdc, 2)
        $fg.ReleaseHdc($hdc)
        $fg.Dispose()

        $sampleDark = $true
        for ($x = 10; $x -lt $ww; $x += 97) {
            for ($y = 10; $y -lt $wh; $y += 89) {
                $c = $full.GetPixel($x, $y)
                if (($c.R + $c.G + $c.B) -gt 24) { $sampleDark = $false; break }
            }
            if (-not $sampleDark) { break }
        }

        if ($printed -and -not $sampleDark) {
            $crop = New-Object System.Drawing.Rectangle($offsetX, $offsetY, $w, $h)
            $bmp = $full.Clone($crop, $full.PixelFormat)
            Write-Host "captured via PrintWindow"
        }
        else {
            $bmp = New-Object System.Drawing.Bitmap($w, $h)
            $g = [System.Drawing.Graphics]::FromImage($bmp)
            $g.CopyFromScreen($origin.X, $origin.Y, 0, 0, $bmp.Size)
            $g.Dispose()
            Write-Host "captured via screen grab"
        }

        $bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
        $bmp.Dispose()
        $full.Dispose()
        Write-Host "screenshot saved: $OutFile"
    }

    if (-not $KeepRunning) {
        # Ask the window to close so the engine shuts down normally and flushes its log;
        # a hard kill loses the last seconds of output (learned the hard way).
        if ($best -ne [IntPtr]::Zero) {
            [void][GameWin]::PostMessage($best, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) # WM_CLOSE
            if (-not $proc.WaitForExit(6000)) {
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        }
        else {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
        Write-Host "game closed"
    }
}
}
finally {
    if ($editorWasMinimised -and $editorHandle -ne [IntPtr]::Zero) {
        [EdWin]::ShowWindow($editorHandle, 9) | Out-Null   # SW_RESTORE
        Write-Host 'editor restored'
    }
}

Write-Host '== log (LingXuJie / errors) =='
# KeepRunning leaves the log file open by the child process; reading it then blocks.
if (-not $KeepRunning -and (Test-Path $gameLog)) {
    Select-String -Path $gameLog -Pattern '\[LingXuJie\]|Error:|Fatal|Warning: Failed' | Select-Object -Last 30 | ForEach-Object { $_.Line }
}
