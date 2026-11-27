"""Audit the tools for anything that can steal focus, move the cursor, or type.

The person runs other work while this agent works in the editor. Anything that calls
SetForegroundWindow, moves the mouse, or sends keystrokes breaks that independence, and it is easy to
add such a call without noticing. This reports every occurrence and says which are load-bearing.

    python Tools/audit_focus.py
"""

import glob
import os
import re

ROOT = "C:/Users/tk/Desktop/lingxujie"

# Calls that take focus or the cursor away from whatever the person is doing.
RISKY = {
    "SetForegroundWindow": "brings a window to the front, takes focus",
    "SetCursorPos": "moves the real mouse pointer",
    "mouse_event": "synthesises a real mouse click",
    "SendKeys": "types into whatever has focus",
    "AppActivate": "activates a window, takes focus",
}

# Harmless when used with these flags, so they are reported separately rather than as failures.
CONDITIONAL = {
    "ShowWindow": "harmless with SW_SHOWNOACTIVATE / SW_HIDE; steals focus with SW_RESTORE",
    "PostMessage": "harmless: posts to a window without activating it",
    "SendMessage": "blocks until handled but does not activate",
}


def scan(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    hits = []
    for lineno, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # A DllImport line declares the function; it does not call it. Matching the declaration was
        # the mistake that made this audit report SetupLayout as risky after the call was removed.
        if "DllImport" in stripped or "extern" in stripped:
            continue
        for name in RISKY:
            if name + "(" in stripped:
                hits.append((lineno, name, stripped[:90], "risky"))
        for name in CONDITIONAL:
            if name + "(" in stripped:
                hits.append((lineno, name, stripped[:90], "conditional"))
    return hits


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "Tools", "*.ps1")))
    files += sorted(glob.glob(os.path.join(ROOT, "Tools", "*.py")))

    total_risky = 0
    total_conditional = 0
    print("%-28s %-6s %-22s %s" % ("file", "line", "call", "verdict"))
    print("-" * 96)

    for path in files:
        hits = scan(path)
        if not hits:
            continue
        name = os.path.basename(path)
        for lineno, call, snippet, kind in hits:
            if kind == "risky":
                total_risky += 1
            else:
                total_conditional += 1
            print("%-28s %-6d %-22s %s" % (name[:28], lineno, call, kind))

    print("")
    print("risky calls: %d" % total_risky)
    print("conditional calls: %d (fine if used with the non-activating flags)" % total_conditional)
    print("")
    print("rules:")
    for call, why in RISKY.items():
        print("  %-22s %s" % (call, why))
    print("")
    print("preferred order for anything that manipulates a window:")
    print("  1. MCP tool call - runs inside the editor process, never touches focus")
    print("  2. UI Automation pattern - presses a named button without a cursor")
    print("  3. PostMessage(WM_CLOSE) - closes a dialog without a cursor")
    print("  4. SetWindowPos with SWP_NOACTIVATE - moves a window without focus")
    print("  5. coordinate click - only when 1-4 have all failed, and say so in the log")


if __name__ == "__main__":
    main()
