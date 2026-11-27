#requires -Version 5.1
# Watches the editor for the states that quietly break automation, and clears them.
#
#   Unreal crash reporter  -> "Close Without Sending" (the crash is already logged, no upload)
#   "restore packages" box -> "Skip restore" (the level is regenerated from Tools\build_level.py)
#   editor process gone    -> optional restart with the MCP server, then wait for the port
#
#   powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action check
#   powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action dismiss
#   powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action restart [-ApplyLayout]
#   powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action watch [-IntervalSeconds 20]
#   powershell -ExecutionPolicy Bypass -File Tools\EditorGuard.ps1 -Action stop
#
# watch stays resident: it dismisses modal windows as soon as they appear and restarts the editor
# only after a *new* crash dump shows up (closing the editor by hand is respected). It writes its
# pid to Saved\editor_guard.pid so `-Action stop` (or a later session) can shut it down.
#
# NOTE: the .ps1 has to be started through `powershell -ExecutionPolicy Bypass -File ...`;
# dot-sourcing it from a restricted session fails with "running scripts is disabled".
#
# Exit codes: 0 = healthy / handled, 1 = something still needs a human, 2 = nothing to do but
# the editor is not running (check only).
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param(
    [ValidateSet('check', 'dismiss', 'restart', 'watch', 'stop')]
    [string]$Action = 'check',
    [switch]$ApplyLayout,
    [int]$TimeoutSeconds = 300,
    [int]$IntervalSeconds = 20,
    [switch]$NoRestart
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$UE = 'C:\Program Files\Epic Games\UE_5.8'
$Project = Join-Path $Root 'LingXuJie.uproject'
$LogFile = Join-Path $Root 'Saved\Logs\editor_guard.log'
$PidFile = Join-Path $Root 'Saved\editor_guard.pid'

Add-Type @"
using System;using System.Text;using System.Runtime.InteropServices;using System.Collections.Generic;
public static class GuardWin {
 [DllImport("user32.dll")] public static extern bool EnumWindows(E cb, IntPtr p);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int c);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RC r);
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
 public static bool PostClose(IntPtr h) { return PostMessage(h, 0x0010, IntPtr.Zero, IntPtr.Zero); }
 public delegate bool E(IntPtr h, IntPtr p);
 [StructLayout(LayoutKind.Sequential)] public struct RC { public int L,T,R,B; }

 public static List<IntPtr> Find(string needle) {
  var found = new List<IntPtr>();
  EnumWindows((h,p) => {
   if (!IsWindowVisible(h)) return true;
   var sb = new StringBuilder(512); GetWindowText(h, sb, 512);
   var title = sb.ToString();
   if (title.Length > 0 && title.IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0) found.Add(h);
   return true;
  }, IntPtr.Zero);
  return found;
 }

 public static string Title(IntPtr h) { var sb = new StringBuilder(512); GetWindowText(h, sb, 512); return sb.ToString(); }

 public static int[] Rect(IntPtr h) { RC r; GetWindowRect(h, out r); return new int[] { r.L, r.T, r.R - r.L, r.B - r.T }; }
}
"@

function Write-GuardLog([string]$Message) {
    $line = ('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message)
    Write-Host $line
    try {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LogFile) | Out-Null
        Add-Content -Path $LogFile -Value $line -Encoding UTF8
    } catch { }
}

function Invoke-Click([int]$X, [int]$Y) {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'ui.ps1') -Action click -X $X -Y $Y | Out-Null
}

# Closing a dialog does not require clicking it. PostMessage(WM_CLOSE) reaches the window without
# moving the cursor and without taking focus, so the person can be typing in another application while
# this runs. The coordinate click above is kept only for a window that ignores WM_CLOSE.
function Close-WindowByMessage([IntPtr]$Handle) {
    try {
        return [GuardWin]::PostClose($Handle)
    } catch {
        return $false
    }
}

# UIAutomation can press a button by name, which survives layout/DPI changes; the coordinate
# fallback is there because the crash reporter is a Qt window and does not always expose UIA.
function Invoke-ButtonByName([IntPtr]$Handle, [string]$Name) {
    try {
        Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes -ErrorAction Stop
        $window = [System.Windows.Automation.AutomationElement]::FromHandle($Handle)
        if ($window -eq $null) { return $false }
        $condition = New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::NameProperty, $Name)
        $button = $window.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)
        if ($button -eq $null) { return $false }
        $pattern = $button.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
        $pattern.Invoke()
        return $true
    } catch {
        return $false
    }
}

function Close-CrashReporters {
    $closed = 0
    foreach ($handle in [GuardWin]::Find('Crash Reporter')) {
        $title = [GuardWin]::Title($handle)
        $rect = [GuardWin]::Rect($handle)
        Write-GuardLog ("crash reporter found: '{0}' at {1},{2} {3}x{4}" -f $title, $rect[0], $rect[1], $rect[2], $rect[3])

        $ok = Invoke-ButtonByName $handle 'Close Without Sending'
        if ($ok) {
            Write-GuardLog 'crash reporter: pressed Close Without Sending via UIAutomation'
        } else {
            # Message-based close first: no cursor movement, no focus change, so this can run while
            # the person is typing somewhere else.
            [void](Close-WindowByMessage $handle)
            Start-Sleep -Milliseconds 800
            if ([GuardWin]::Find('Crash Reporter').Count -gt 0) {
                # Last resort only: the dialog ignored WM_CLOSE.
                Invoke-Click ($rect[0] + 100) ($rect[1] + $rect[3] - 26)
                Write-GuardLog 'crash reporter: clicked Close Without Sending (coordinate fallback)'
            } else {
                Write-GuardLog 'crash reporter: closed via WM_CLOSE'
            }
        }

        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Milliseconds 300
            if ([GuardWin]::Find('Crash Reporter').Count -eq 0) { $closed++; break }
        }
        if ([GuardWin]::Find('Crash Reporter').Count -gt 0) {
            Write-GuardLog 'crash reporter did NOT close - needs a human'
        }
    }
    return $closed
}

function Close-RestoreDialogs {
    $closed = 0
    foreach ($handle in [GuardWin]::Find(([char]0x6062 + [char]0x590D + [char]0x5305))) {
        $rect = [GuardWin]::Rect($handle)
        # The dialog opens too short for its own buttons; give it room, then click Skip restore
        # (bottom-right) - the same fix gotcha #43 documents.
        [void][GuardWin]::SetWindowPos($handle, [IntPtr]::Zero, 660, 180, 1180, 1010, 0x0040)
        Start-Sleep -Milliseconds 700
        $rect = [GuardWin]::Rect($handle)
        $ok = Invoke-ButtonByName $handle ([string]([char]0x8DF3 + [char]0x8FC7 + [char]0x6062 + [char]0x590D))
        if (-not $ok) {
            # Message-based close before clicking: skipping the restore is what WM_CLOSE means here,
            # and it does not move the cursor or take focus.
            [void](Close-WindowByMessage $handle)
            Start-Sleep -Milliseconds 800
            if ([GuardWin]::Find(([char]0x6062 + [char]0x590D + [char]0x5305)).Count -gt 0) {
                Invoke-Click ($rect[0] + $rect[2] - 72) ($rect[1] + $rect[3] - 33)
                Write-GuardLog 'restore dialog: clicked Skip restore (coordinate fallback)'
            } else {
                Write-GuardLog 'restore dialog: closed via WM_CLOSE'
            }
        } else {
            Write-GuardLog 'restore dialog: pressed Skip restore via UIAutomation'
        }
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Milliseconds 300
            if ([GuardWin]::Find(([char]0x6062 + [char]0x590D + [char]0x5305)).Count -eq 0) { $closed++; break }
        }
    }
    return $closed
}

function Get-EditorProcess {
    return Get-Process UnrealEditor -ErrorAction SilentlyContinue | Select-Object -First 1
}

function Test-McpPort {
    return [bool](Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)
}

function Get-LastCrashFolder {
    $dir = Join-Path $Root 'Saved\Crashes'
    if (-not (Test-Path $dir)) { return $null }
    return Get-ChildItem $dir -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

function Start-Editor {
    $editor = Join-Path $UE 'Engine\Binaries\Win64\UnrealEditor.exe'
    if (-not (Test-Path $editor)) { throw "editor not found: $editor" }
    Start-Process -FilePath $editor -ArgumentList @(('"' + $Project + '"'), '-ModelContextProtocolStartServer') | Out-Null
    Write-GuardLog 'editor process started, waiting for the MCP port ...'
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 5
        if (Test-McpPort) {
            Write-GuardLog 'MCP server is listening on 127.0.0.1:8000'
            return $true
        }
        if (-not (Get-EditorProcess)) {
            Write-GuardLog 'editor exited while starting - see Saved\Logs\LingXuJie.log'
            return $false
        }
    }
    Write-GuardLog ("MCP port did not come up within {0}s" -f $TimeoutSeconds)
    return $false
}

# --- run ---------------------------------------------------------------------------------------

$editor = Get-EditorProcess
$mcp = Test-McpPort
$reporters = [GuardWin]::Find('Crash Reporter')
$restores = [GuardWin]::Find(([char]0x6062 + [char]0x590D + [char]0x5305))
$crash = Get-LastCrashFolder
$needsAttention = ($reporters.Count -gt 0) -or ($restores.Count -gt 0)

Write-GuardLog ("state: editor={0} mcp={1} crash_reporters={2} restore_dialogs={3}" -f `
    $(if ($editor) { 'running (pid ' + $editor.Id + ')' } else { 'not running' }), $mcp, $reporters.Count, $restores.Count)

$watcherState = 'not running'
if (Test-Path $PidFile) {
    $watcherPid = 0
    if ([int]::TryParse((Get-Content $PidFile -Raw).Trim(), [ref]$watcherPid) -and
        (Get-Process -Id $watcherPid -ErrorAction SilentlyContinue)) {
        $watcherState = 'running (pid ' + $watcherPid + ')'
    } else {
        $watcherState = 'stale pid file'
    }
}
Write-GuardLog ('watcher: ' + $watcherState)
if ($crash) {
    Write-GuardLog ("last crash folder: {0} ({1})" -f $crash.FullName, $crash.LastWriteTime)
}

switch ($Action) {
    'check' {
        if ($needsAttention) {
            Write-GuardLog 'CHECK: modal windows are blocking automation - run -Action dismiss'
            exit 1
        }
        if (-not $editor) {
            Write-GuardLog 'CHECK: editor is not running'
            exit 2
        }
        if (-not $mcp) {
            Write-GuardLog 'CHECK: editor is up but the MCP server is not listening (restart without -ModelContextProtocolStartServer?)'
            exit 1
        }
        Write-GuardLog 'CHECK: healthy'
        exit 0
    }
    'dismiss' {
        $closedReporters = Close-CrashReporters
        $closedRestores = Close-RestoreDialogs
        Write-GuardLog ("dismiss: crash reporters closed={0} restore dialogs closed={1}" -f $closedReporters, $closedRestores)
        $still = ([GuardWin]::Find('Crash Reporter').Count -gt 0) -or `
                 ([GuardWin]::Find(([char]0x6062 + [char]0x590D + [char]0x5305)).Count -gt 0)
        if ($still) { exit 1 }
        exit 0
    }
    'restart' {
        [void](Close-CrashReporters)
        [void](Close-RestoreDialogs)
        $editor = Get-EditorProcess
        if ($editor) {
            Write-GuardLog 'restart: an editor is already running - leaving it alone (dismiss only)'
        } else {
            if (-not (Start-Editor)) { exit 1 }
        }
        if ($ApplyLayout) {
            & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'SetupLayout.ps1') | Out-Null
            Write-GuardLog 'restart: window layout re-applied'
        }
        if (Test-McpPort) { exit 0 } else { exit 1 }
    }
    'watch' {
        $started = Get-Date
        $seenRunning = $false
        $lastEditorPid = 0
        $knownCrash = $null
        $lastHeartbeat = Get-Date
        $restarts = 0
        $goneLogged = $false
        Write-GuardLog ("watch: checking every {0}s, auto-restart={1} (an editor closed by hand stays closed)" -f `
            $IntervalSeconds, (-not $NoRestart))
        Set-Content -Path $PidFile -Value $PID -Encoding ASCII
        Write-GuardLog ("watch: pid {0} written to Saved\editor_guard.pid (stop with -Action stop)" -f $PID)
        try {
        while ($true) {
            Start-Sleep -Seconds ([Math]::Max(5, $IntervalSeconds))
            try {
                $reporters = [GuardWin]::Find('Crash Reporter')
                $restores = [GuardWin]::Find(([char]0x6062 + [char]0x590D + [char]0x5305))
                if ($reporters.Count -gt 0 -or $restores.Count -gt 0) {
                    Write-GuardLog ("watch: {0} crash reporter(s) / {1} restore dialog(s) on screen - dismissing" -f `
                        $reporters.Count, $restores.Count)
                    [void](Close-CrashReporters)
                    [void](Close-RestoreDialogs)
                }

                $editor = Get-EditorProcess
                if ($editor) {
                    if (-not $seenRunning -or $lastEditorPid -ne $editor.Id) {
                        Write-GuardLog ("watch: editor running (pid {0}), mcp={1}" -f $editor.Id, (Test-McpPort))
                        $lastEditorPid = $editor.Id
                    }
                    $seenRunning = $true
                    $goneLogged = $false
                } else {
                    $crash = Get-LastCrashFolder
                    $isNewCrash = $crash -and $crash.LastWriteTime -gt $started -and $crash.FullName -ne $knownCrash
                    if ($isNewCrash) { $knownCrash = $crash.FullName }

                    if ($isNewCrash -and $seenRunning -and -not $NoRestart -and $restarts -lt 3) {
                        $restarts++
                        Write-GuardLog ("watch: editor died ({0}) - restarting, attempt {1} of 3" -f $crash.Name, $restarts)
                        if (Start-Editor) {
                            $seenRunning = $true
                            $goneLogged = $false
                        } else {
                            Write-GuardLog 'watch: restart failed - see Saved\Logs\LingXuJie.log'
                        }
                    } elseif (-not $goneLogged) {
                        if ($isNewCrash -and $restarts -ge 3) {
                            Write-GuardLog 'watch: crash loop (3 restarts) - leaving it for a human'
                        } elseif ($seenRunning) {
                            Write-GuardLog 'watch: editor gone with no new crash dump - treating it as closed by hand'
                        } else {
                            Write-GuardLog 'watch: editor is not running yet'
                        }
                        $seenRunning = $false
                        $goneLogged = $true
                    }
                }

                if (((Get-Date) - $lastHeartbeat).TotalMinutes -ge 15) {
                    Write-GuardLog ("watch: alive, editor={0} mcp={1} restarts={2}" -f `
                        $(if (Get-EditorProcess) { 'up' } else { 'down' }), (Test-McpPort), $restarts)
                    $lastHeartbeat = Get-Date
                }
            } catch {
                Write-GuardLog ("watch: iteration failed: {0}" -f $_.Exception.Message)
            }
        }
        } finally {
            Remove-Item $PidFile -ErrorAction SilentlyContinue
            Write-GuardLog 'watch: stopped'
        }
    }
    'stop' {
        if (-not (Test-Path $PidFile)) {
            Write-GuardLog 'stop: no watcher pid file - nothing to stop'
            exit 0
        }
        $watcherPid = 0
        if (-not [int]::TryParse((Get-Content $PidFile -Raw).Trim(), [ref]$watcherPid)) {
            Write-GuardLog 'stop: pid file is unreadable - removing it'
            Remove-Item $PidFile -ErrorAction SilentlyContinue
            exit 0
        }
        $proc = Get-Process -Id $watcherPid -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $watcherPid -Force
            Write-GuardLog ("stop: watcher {0} stopped" -f $watcherPid)
        } else {
            Write-GuardLog ("stop: watcher {0} was already gone" -f $watcherPid)
        }
        # A forced stop skips the watcher's finally block, so clean the pid file up here.
        Remove-Item $PidFile -ErrorAction SilentlyContinue
        exit 0
    }
}
