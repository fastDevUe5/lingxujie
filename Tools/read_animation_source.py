"""Read the engine headers that decide how an animation can be built from raw data.

The question this answers: given bone tracks decoded from the game's own format, what is the
supported way to turn them into an AnimSequence? That is not a question the Python API reference
answers, because it only lists what is exposed - this reads what exists and what is marked
BlueprintCallable, which is what Python can reach.

    python Tools/read_animation_source.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

# Headers that decide whether a raw-data animation importer is possible.
WANTED = [
    "AnimSequence.h",
    "AnimationDataModel.h",
    "AnimationDataController.h",
    "AnimDataModel.h",
    "BoneAnimationTrack.h",
    "AnimationBlueprintLibrary.h",
    "SkeletalMesh.h",
    "ReferenceSkeleton.h",
    "Skeleton.h",
]


def find(name):
    for root, dirs, files in os.walk(ENGINE):
        if name in files:
            return os.path.join(root, name)
    return None


def show_declared(path, title):
    text = open(path, encoding="utf-8", errors="replace").read()
    print("=" * 78)
    print("%s" % title)
    print("  %s" % path)
    print("  %d bytes" % len(text))
    print("")

    # Functions exposed to Python/Blueprint are what matters: those are the reachable surface.
    exposed = []
    for match in re.finditer(
            r"UFUNCTION\s*\(([^)]*)\)\s*\n\s*(?:virtual\s+)?[\w:<>*&\s]+?\b(\w+)\s*\(([^;{]*)\)",
            text):
        spec, name, args = match.group(1), match.group(2), match.group(3)
        if "BlueprintCallable" in spec or "BlueprintPure" in spec or "ScriptCallable" in spec:
            exposed.append((name, " ".join(args.split())[:90]))

    if exposed:
        print("  BlueprintCallable / Python-reachable (%d):" % len(exposed))
        for name, args in exposed[:40]:
            print("    %-42s (%s)" % (name, args))
    else:
        print("  no BlueprintCallable functions found in this header")
    print("")


def main():
    for name in WANTED:
        path = find(name)
        if path is None:
            print("= = = %s -- NOT FOUND\n" % name)
            continue
        show_declared(path, name)


if __name__ == "__main__":
    main()
