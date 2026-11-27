"""Add the P/Invoke declarations the overlay check needs, keeping the file pure ASCII.

    python Tools/add_pinvoke.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/SetupLayout.ps1"

ANCHOR = " [DllImport(\"user32.dll\")] public static extern bool SetForegroundWindow(IntPtr h);"

ADDITIONS = (
    " [DllImport(\"user32.dll\")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);\n"
    " [DllImport(\"user32.dll\")] public static extern bool IsIconic(IntPtr h);"
)


def main():
    text = open(PATH, encoding="utf-8").read()
    if "GetWindowThreadProcessId" in text:
        print("already declared")
        return
    if ANCHOR not in text:
        print("anchor not found; declarations not added")
        return
    text = text.replace(ANCHOR, ANCHOR + "\n" + ADDITIONS, 1)
    open(PATH, "w", encoding="utf-8").write(text)

    raw = open(PATH, "rb").read()
    non_ascii = sum(1 for b in raw if b > 127)
    print("declarations added; non-ASCII bytes now %d" % non_ascii)


if __name__ == "__main__":
    main()
