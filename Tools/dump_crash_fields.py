"""Dump every field of the crash context, with length and a preview, sorted by usefulness.

The point is to find where the diagnostic detail actually lives. XML field names suggest content but
do not prove it: ErrorMessage turned out to hold one line while the stack went elsewhere, and knowing
which field carries the module list is what makes a crash readable in seconds.

    python Tools/dump_crash_fields.py
"""

import glob
import os
import xml.etree.ElementTree as ET

ROOT = "C:/Users/tk/Desktop/lingxujie/Saved/Crashes"


def main():
    folders = sorted(glob.glob(os.path.join(ROOT, "UECC-*")))
    if not folders:
        print("no crash folders")
        return
    folder = folders[-1]

    root = ET.parse(os.path.join(folder, "CrashContext.runtime-xml")).getroot()
    leaves = {}

    def collect(element):
        for child in element:
            if len(child):
                collect(child)
            else:
                leaves.setdefault(child.tag, (child.text or "").strip())

    collect(root)

    print("fields: %d" % len(leaves))
    print("")
    print("%-30s %8s  %s" % ("field", "chars", "first line"))
    print("-" * 96)

    # Longest first: the big ones are where the detail hides.
    for name, value in sorted(leaves.items(), key=lambda kv: -len(kv[1])):
        first = value.split("\n")[0][:60].replace("\r", "")
        print("%-30s %8d  %s" % (name, len(value), first))

    print("")
    print("=== fields mentioning a module name ===")
    for name, value in leaves.items():
        if "UnrealEditor_" in value or value.count("\n") > 20:
            lines = [l for l in value.split("\n") if l.strip()]
            print("%-30s %d line(s)" % (name, len(lines)))
            for line in lines[:6]:
                print("    %s" % line.strip()[:80])


if __name__ == "__main__":
    main()
