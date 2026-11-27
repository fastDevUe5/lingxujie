"""Map the collision system: channels, the two body setups, and the four collision profiles.

Collision is where "it did not work" almost always means "the wrong channel answered". The engine
defines a fixed set of object and trace channels, and every query names one. Knowing the default
responses is what turns trial and error into a decision.

This reads EngineTypes.h for the channel enumerations and CollisionProfile for the defaults.

    python Tools/map_collision.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"


def find(name):
    for root, dirs, files in os.walk(ENGINE):
        if name in files:
            return os.path.join(root, name)
    return None


def enum_values(text, enum_name):
    match = re.search(r"enum\s+%s\s*:?\s*\w*\s*\{(.*?)\}" % enum_name, text, re.S)
    if not match:
        return []
    body = match.group(1)
    values = []
    for line in body.split("\n"):
        stripped = line.strip()
        item = re.match(r"(ECC_\w+|ECollisionChannel\w*)\s*(?:UMETA[^,]*)?[=,]?", stripped)
        if item:
            values.append(item.group(1))
    return values


def main():
    types = find("EngineTypes.h")
    if types is None:
        print("EngineTypes.h not found")
        return
    text = open(types, encoding="utf-8", errors="replace").read()
    print("EngineTypes.h  %d bytes" % len(text))
    print("")

    # The object channel enum and the trace channel enum.
    for enum_name in ("ECollisionChannel", "ECollisionResponse", "ECollisionEnabled"):
        values = enum_values(text, enum_name)
        print("=== %s  (%d values)" % (enum_name, len(values)))
        for value in values:
            print("   ", value)
        print("")

    # The body setup class holds the actual geometry settings.
    setup = find("BodySetup.h")
    if setup:
        body = open(setup, encoding="utf-8", errors="replace").read()
        print("=== BodySetup.h  %d bytes" % len(body))
        for field in ("CollisionTraceFlag", "bDoubleSidedGeometry", "bConsiderForBounds",
                      "CollisionRepMode", "AggGeom"):
            if field in body:
                print("   has", field)
        print("   trace flag enum:")
        match = re.search(r"enum\s+ECollisionTraceFlag\s*:?[^{]*\{(.*?)\}", body, re.S)
        if match:
            for line in match.group(1).split("\n"):
                stripped = line.strip()
                if stripped.startswith("CTF_"):
                    print("     ", stripped.split(",")[0].split("UMETA")[0].strip())
        print("")

    profiles = find("CollisionProfile.h")
    if profiles:
        text2 = open(profiles, encoding="utf-8", errors="replace").read()
        print("=== CollisionProfile.h  %d bytes" % len(text2))
        names = re.findall(r"TEXT\(\"(\w+)\"\)", text2)
        preset = [n for n in names if n[0].isupper() and len(n) > 4][:20]
        print("   preset names seen:", ", ".join(preset[:15]))
        print("")


if __name__ == "__main__":
    main()
