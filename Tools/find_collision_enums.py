"""Locate the collision trace flag enumeration and the collision profile defaults.

The previous attempt looked in EngineTypes.h and BodySetup.h and found neither, so the enum lives
somewhere else. This searches every header for the identifiers themselves rather than guessing
the file, which is the faster route when a name is known but its home is not.

    python Tools/find_collision_enums.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

# Identifiers whose home file we want.
NEEDLES = {
    "CTF_UseDefault": "collision trace flag (default)",
    "CTF_UseSimpleAndComplex": "collision trace flag (both)",
    "CTF_UseSimpleAsComplex": "collision trace flag (simple as complex)",
    "CTF_UseComplexAsSimple": "collision trace flag (complex as simple)",
    "ECR_Ignore": "collision response (ignore)",
    "ECR_Overlap": "collision response (overlap)",
    "ECR_Block": "collision response (block)",
    "NoCollision": "collision enabled (none)",
    "QueryAndPhysics": "collision enabled (both)",
}


def main():
    found = {}
    for root, dirs, files in os.walk(ENGINE):
        for filename in files:
            if not filename.endswith(".h"):
                continue
            path = os.path.join(root, filename)
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for needle in NEEDLES:
                if needle in text and needle not in found:
                    found[needle] = path

    print("%-28s %s" % ("identifier", "home header"))
    print("-" * 100)
    for needle, description in NEEDLES.items():
        path = found.get(needle)
        name = os.path.relpath(path, ENGINE) if path else "NOT FOUND"
        print("%-28s %-58s %s" % (needle, name[:58], description))
    print("")

    # Print the enum body from whichever file holds the trace flags.
    holder = found.get("CTF_UseComplexAsSimple") or found.get("CTF_UseDefault")
    if holder:
        text = open(holder, encoding="utf-8", errors="replace").read()
        print("=== trace flags, from %s" % os.path.relpath(holder, ENGINE))
        for match in re.finditer(r"(CTF_\w+)\s*(?:UMETA\([^)]*\))?\s*,?", text):
            print("   ", match.group(1))
        print("")

    # Collision enabled values, in order.
    holder = found.get("QueryAndPhysics")
    if holder:
        text = open(holder, encoding="utf-8", errors="replace").read()
        print("=== collision enabled, from %s" % os.path.relpath(holder, ENGINE))
        match = re.search(r"namespace\s+ECollisionEnabled\s*\{(.*?)\}", text, re.S)
        if match:
            for line in match.group(1).split("\n"):
                stripped = line.strip()
                if stripped and not stripped.startswith("//"):
                    name = re.match(r"(\w+)", stripped)
                    if name:
                        print("   ", name.group(1))
        print("")


if __name__ == "__main__":
    main()
