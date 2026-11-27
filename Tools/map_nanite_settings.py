"""Read the two Nanite settings structs, which are the ones that change how a mesh renders.

Two different structs share the name: FMeshNaniteSettings on a static mesh, and FNaniteSettings on
the world. Confusing them is easy and the effects differ - one decides whether a mesh is
virtualised at all, the other decides whether the scene supports it.

    python Tools/map_nanite_settings.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

TARGETS = [
    ("FMeshNaniteSettings", "Runtime/Engine/Classes/Engine/EngineTypes.h"),
    ("FNaniteSettings", "Runtime/Engine/Classes/GameFramework/WorldSettings.h"),
]


def body_of(text, struct_name):
    match = re.search(r"struct\s+(?:\w+_API\s+)?%s\s*[^\{]*\{" % struct_name, text)
    if not match:
        return None
    start = match.end()
    depth = 1
    index = start
    while index < len(text) and depth:
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    return text[start:index - 1]


def fields_of(body):
    out = []
    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("UPROPERTY"):
            continue
        match = re.match(r"([\w:<>,\s\*&]+?)\s+(\w+)\s*(?:=\s*([^;]+))?;", stripped)
        if match:
            out.append((match.group(1).strip(), match.group(2), (match.group(3) or "").strip()))
    return out


def main():
    for struct_name, relative in TARGETS:
        path = os.path.join(ENGINE, relative.replace("/", os.sep))
        if not os.path.exists(path):
            print("%s: header missing at %s" % (struct_name, relative))
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        body = body_of(text, struct_name)
        print("=" * 78)
        print("%s   in %s" % (struct_name, os.path.basename(relative)))
        print("  header %d bytes" % len(text))
        if body is None:
            print("  body not matched")
            print("")
            continue
        fields = fields_of(body)
        print("  %d fields" % len(fields))
        print("")
        for kind, name, default in fields:
            print("    %-38s %-18s %s" % (name, kind[:18], default[:26]))
        print("")


if __name__ == "__main__":
    main()
