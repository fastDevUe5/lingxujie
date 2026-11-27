#requires -Version 5.1
# Arrange the windows for a 2560x1440 display (the human's preferred layout, kept tidy).
#
#   powershell -ExecutionPolicy Bypass -File Tools\SetupLayout.ps1
#   powershell -ExecutionPolicy Bypass -File Tools\SetupLayout.ps1 -DryRun
#
# Layout: editor column on the left (viewport on top, content browser underneath), browser/Fab
# on the top right, chat at the bottom right. 6 px gutters everywhere, nothing under the taskbar.
#
#   editor          0,0      1494x864     (the viewport screenshots are taken from)
#   content browser 0,870    1494x516     (floats under the editor; skipped if docked/hidden)
#   Fab / browser   1500,0   1040x640
#   chat            1500,646 1040x740
#
# Any window that is not found is skipped, so this is safe to run at any time.
# NOTE: keep this file ASCII-only (PowerShell 5.1 reads BOM-less files as ANSI).

param([switch]$DryRun)

$ErrorActionPreference = 'Stop'

Add-Type @"
using System;using System.Text;using System.Runtime.InteropServices;
public static class Lay {
 [DllImport("user32.dll")] public static extern bool EnumWindows(E cb, IntPtr p);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int c);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RC r);
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
 public delegate bool E(IntPtr h, IntPtr p);
 [StructLayout(LayoutKind.Sequential)] public struct RC { public int L,T,Rt,B; }

 public static IntPtr Find(string needle) {
   IntPtr best = IntPtr.Zero; int area = 0;
   EnumWindows((h,p) => {
     if (!IsWindowVisible(h)) return true;
     var sb = new StringBuilder(512); GetWindowText(h, sb, 512);
     if (!sb.ToString().Contains(needle)) return true;
     RC r; if (!GetWindowRect(h, out r)) return true;
     int a = (r.Rt-r.L) * (r.B-r.T);
     if (a > area) { area = a; best = h; }
     return true;
   }, IntPtr.Zero);
   return best;
 }
 public static string Rect(IntPtr h) { RC r; GetWindowRect(h, out r); return r.L + "," + r.T + " " + (r.Rt-r.L) + "x" + (r.B-r.T); }
 public static void Place(IntPtr h, int x, int y, int cx, int cy) {
   // SWP_NOACTIVATE keeps the window from taking focus. Placement must never interrupt whatever the
   // person is doing in another window.
   ShowWindow(h, 4);                                     // SW_SHOWNOACTIVATE
   SetWindowPos(h, IntPtr.Zero, x, y, cx, cy, 0x0040 | 0x0010 | 0x0004);  // SWP_SHOWWINDOW|NOACTIVATE|NOZORDER
 }

 // Hide (not minimise) any visible window of the given processes that overlaps the keeper. SW_HIDE
 // activates nothing; SW_MINIMIZE would hand focus to the next window, which is exactly the
 // interference this is meant to avoid. Matching by rectangle rather than by title keeps this file
 // ASCII-only, which PowerShell 5.1 requires.
 public static void MinimiseOverlapping(IntPtr keeper, int[] pids) {
   RC keep; if (!GetWindowRect(keeper, out keep)) return;
   int hidden = 0;
   EnumWindows((h,p) => {
     if (h == keeper) return true;
     if (!IsWindowVisible(h)) return true;
     if (IsIconic(h)) return true;
     uint pid; GetWindowThreadProcessId(h, out pid);
     bool ours = false;
     foreach (int want in pids) if ((uint)want == pid) { ours = true; break; }
     if (!ours) return true;
     RC r; if (!GetWindowRect(h, out r)) return true;
     int w = r.Rt - r.L, ht = r.B - r.T;
     if (w <= 0 || ht <= 0) return true;
     // The content browser is placed below the editor on purpose, so anything starting lower down
     // is left alone.
     if (r.T >= keep.B) return true;
     bool overlaps = r.L < keep.Rt && r.Rt > keep.L && r.T < keep.B && r.B > keep.T;
     if (overlaps) {
       ShowWindow(h, 0);                    // SW_HIDE - activates nothing
       hidden++;
     }
     return true;
   }, IntPtr.Zero);
   if (hidden > 0) {
     Console.WriteLine("{0,-12} -> {1} overlapping window(s) hidden", "overlay", hidden);
   }
 }
}
"@

# Work area of the 2560x1440 display: the taskbar eats the bottom ~48 px.
$W = 2560
$H = 1392
$G = 6
$LeftW = $W - 1066           # 1494: editor column, 6 px gutter + 1040 right column + 20 px margin
$RightX = 1500
$RightW = 1040
$EditorH = 864
$ContentY = $EditorH + $G
$ContentH = $H - $ContentY - $G
$BrowserH = 640
$HarnessY = $BrowserH + $G
$HarnessH = $H - $HarnessY - $G

# Title of the floating content browser, spelled with char codes to keep this file ASCII.
$contentBrowser = [string][char]0x5185 + [char]0x5BB9 + [char]0x6D4F + [char]0x89C8 + [char]0x5668

$targets = @(
    @{ Match = 'LingXuJie - ';     Label = 'editor';       X = 0;        Y = 0;            W = $LeftW;  H = $EditorH },
    @{ Match = $contentBrowser;    Label = 'content';      X = 0;        Y = $ContentY;    W = $LeftW;  H = $ContentH },
    @{ Match = 'Fab';              Label = 'fab/browser';  X = $RightX;  Y = 0;            W = $RightW; H = $BrowserH },
    @{ Match = 'DeepSeek Harness'; Label = 'chat';         X = $RightX;  Y = $HarnessY;    W = $RightW; H = $HarnessH }
)

foreach ($target in $targets) {
    $handle = [Lay]::Find($target.Match)
    if ($handle -eq [IntPtr]::Zero) {
        Write-Host ("{0,-12} not found, skipped" -f $target.Label)
        continue
    }
    if ($DryRun) {
        Write-Host ("{0,-12} now {1} -> would be {2},{3} {4}x{5}" -f $target.Label, [Lay]::Rect($handle),
            $target.X, $target.Y, $target.W, $target.H)
        continue
    }
    [Lay]::Place($handle, $target.X, $target.Y, $target.W, $target.H)
    Write-Host ("{0,-12} -> {1}" -f $target.Label, [Lay]::Rect($handle))
}

# The editor used to be forced to the front here. It no longer is: bringing a window forward takes
# focus from whatever the person is doing, and nothing needs it. Viewport screenshots come from MCP
# CaptureViewport, which renders inside the editor process and does not care about Z order.
$editor = [Lay]::Find('LingXuJie - ')

# Windows that sit over the viewport eat clicks and hide the scene, and the Message Log is the usual
# culprit. Its title is localised, so it cannot be matched by name in an ASCII-only file; instead any
# visible window of this editor process that overlaps the editor rectangle, and is not the editor or
# the content browser we just placed, is minimised. Engine logs are read through MCP, never by
# looking at that window (Docs/UE5-Gotchas.md rule 6).
if (-not $DryRun -and $editor -ne [IntPtr]::Zero) {
    $ue = (Get-Process -Name 'UnrealEditor*' -ErrorAction SilentlyContinue).Id
    [Lay]::MinimiseOverlapping($editor, $ue)
}

Write-Host 'layout applied'
