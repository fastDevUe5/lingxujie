"""Add PostClose to EditorGuard's GuardWin class.

Closing a window with PostMessage(WM_CLOSE) reaches the dialog without moving the cursor or taking
focus. That replaces the coordinate click which used to be the fallback for dialogs that do not expose
UI Automation.

    python Tools/add_postclose.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/EditorGuard.ps1"

ANCHOR = (
    ' [DllImport("user32.dll")] public static extern bool SetWindowPos('
    'IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);'
)

ADDITION = (
    '\n [DllImport("user32.dll")] public static extern bool PostMessage('
    'IntPtr h, uint msg, IntPtr w, IntPtr l);\n'
    ' public static bool PostClose(IntPtr h) { return PostMessage(h, 0x0010, IntPtr.Zero, IntPtr.Zero); }'
)


def main():
    text = open(PATH, encoding="utf-8").read()
    if "PostMessage(IntPtr h" in text:
        print("already declared")
        return
    if ANCHOR not in text:
        print("anchor not found")
        for line in text.split("\n"):
            if "SetWindowPos" in line:
                print(repr(line))
        return
    text = text.replace(ANCHOR, ANCHOR + ADDITION, 1)
    open(PATH, "w", encoding="utf-8").write(text)
    print("PostClose added")


if __name__ == "__main__":
    main()
