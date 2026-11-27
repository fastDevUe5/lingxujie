"""Read the real crash context from this project and report what is diagnostic in it.

A crash folder holds four artefacts: the runtime XML, a copy of the log, a minidump, and the client
ini. Knowing which field holds the actual assertion text - and which fields are noise - is the
difference between reading a crash in a minute and an hour.

    python Tools/read_crash_context.py
"""

import glob
import os
import xml.etree.ElementTree as ET

ROOT = "C:/Users/tk/Desktop/lingxujie/Saved/Crashes"

# Fields worth reading first, in the order a diagnosis needs them.
PRIORITY = [
    "ErrorMessage",
    "CrashType",
    "CrashReporterMessage",
    "IsAssert",
    "IsEnsure",
    "AssertionType",
    "ProcessId",
    "SecondsSinceStart",
    "GameName",
    "EngineVersion",
    "PlatformFullName",
    "CommandLine",
]


def main():
    folders = sorted(glob.glob(os.path.join(ROOT, "UECC-*")))
    if not folders:
        print("no crash folders")
        return
    folder = folders[-1]
    print("crash folder: %s" % os.path.basename(folder))
    print("")

    print("=== files ===")
    for path in sorted(glob.glob(os.path.join(folder, "*"))):
        print("  %-28s %8.1f KB" % (os.path.basename(path),
                                    os.path.getsize(path) / 1024.0))
    print("")

    xml_path = os.path.join(folder, "CrashContext.runtime-xml")
    if not os.path.exists(xml_path):
        print("no runtime xml")
        return

    root = ET.parse(xml_path).getroot()
    print("=== top-level sections ===")
    for section in root:
        print("  %-24s %d child element(s)" % (section.tag, len(section)))
    print("")

    # Flatten every leaf so a field can be found regardless of nesting.
    leaves = {}

    def collect(element):
        for child in element:
            if len(child):
                collect(child)
            else:
                leaves.setdefault(child.tag, (child.text or "").strip())

    collect(root)

    print("=== priority fields ===")
    for name in PRIORITY:
        if name in leaves:
            value = leaves[name].replace("\n", " ")
            print("  %-24s %s" % (name, value[:140]))
        else:
            print("  %-24s (absent)" % name)
    print("")

    # The fields that usually explain an editor crash but are easy to overlook.
    for name in ("ErrorMessage", "CrashType", "Threads"):
        if name in leaves and len(leaves[name]) > 20:
            print("=== %s, first 400 chars ===" % name)
            print(leaves[name][:400])
            print("")

    print("=== all leaf names (%d) ===" % len(leaves))
    for name in sorted(leaves):
        print("  %s" % name)


if __name__ == "__main__":
    main()
