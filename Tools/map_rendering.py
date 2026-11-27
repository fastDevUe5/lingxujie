"""Map the rendering system from the engine's own headers.

Rendering is the area where folklore outruns fact - which settings matter, what Nanite does to
collision, what Lumen costs. The headers give the real parameter sets and their defaults, which
is a better starting point than any tutorial.

This reads the key settings structs and prints their fields with declared defaults.

    python Tools/map_rendering.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

TARGETS = [
    ("FMeshNaniteSettings", ["MeshNaniteSettings.h", "NaniteSettings.h"]),
    ("FStaticMeshLODGroup", ["StaticMesh.h"]),
    ("FEngineShowFlags", ["ShowFlags.h"]),
    ("FPostProcessSettings", ["Scene.h"]),
    ("FLightmassWorldInfoSettings", ["Scene.h"]),
]

# Settings that decide how a mesh renders, worth knowing by name.
INTERESTING = ("Nanite", "Lumen", "VirtualShadow", "LOD", "Distance", "Shadow", "RayTracing",
               "Ambient", "Bloom", "Exposure", "AutoExposure")


def find(names):
    for name in names:
        for root, dirs, files in os.walk(ENGINE):
            if name in files:
                return os.path.join(root, name)
    return None


def struct_fields(path, struct_name):
    """Pull the member declarations out of a settings struct."""
    text = open(path, encoding="utf-8", errors="replace").read()
    match = re.search(r"struct\s+(?:\w+_API\s+)?%s\s*(?:final\s*)?\{" % struct_name, text)
    if not match:
        return None, len(text)
    start = match.end()
    # Walk braces to find the end of the body.
    depth = 1
    index = start
    while index < len(text) and depth:
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    body = text[start:index]

    fields = []
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        decl = re.match(r"(?:UPROPERTY\([^)]*\)\s*)?([\w:<>\s\*&]+?)\s+(\w+)\s*(?:=\s*([^;]+))?;", stripped)
        if decl:
            fields.append((decl.group(1).strip(), decl.group(2), (decl.group(3) or "").strip()))
    return fields, len(text)


def main():
    for struct_name, filenames in TARGETS:
        path = find(filenames)
        if path is None:
            print("= %s -- header not found" % struct_name)
            print("")
            continue
        fields, size = struct_fields(path, struct_name)
        print("=" * 78)
        print("%s   in %s (%d bytes)" % (struct_name, os.path.basename(path), size))
        if not fields:
            print("  (struct body not matched; may be declared differently)")
            print("")
            continue
        print("  %d fields" % len(fields))
        shown = 0
        for kind, name, default in fields:
            if any(word.lower() in name.lower() for word in INTERESTING):
                print("    %-40s %-20s %s" % (name, kind[:20], default[:28]))
                shown += 1
            if shown >= 18:
                break
        if shown == 0:
            for kind, name, default in fields[:12]:
                print("    %-40s %-20s %s" % (name, kind[:20], default[:28]))
        print("")


if __name__ == "__main__":
    main()
