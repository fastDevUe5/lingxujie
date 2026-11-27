"""Read the animation data model and its controller, which is where tracks actually live.

AnimSequence no longer stores raw tracks directly; it owns a data model, and the data model is
written through a controller interface. That layering is why the Python surface can read tracks
but not write them - the reader functions unwrap to the model, and the writer is a separate
interface that lives outside the reflected API.

This prints the model's structure and the controller's method list, which is the exact recipe an
importer would have to follow if it were written in C++.

    python Tools/read_animation_data_model.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

MODEL = "Runtime/Engine/Classes/Animation/AnimData/AnimDataModel.h"
CONTROLLER = "Runtime/Engine/Classes/Animation/AnimData/IAnimationDataController.h"
TRACK = "Runtime/Engine/Classes/Animation/AnimData/BoneAnimationTrack.h"


def show(path_relative, title, method_prefixes=None, limit=40):
    path = os.path.join(ENGINE, path_relative.replace("/", os.sep))
    if not os.path.exists(path):
        print("%s: missing at %s" % (title, path_relative))
        print("")
        return
    text = open(path, encoding="utf-8", errors="replace").read()
    print("=" * 78)
    print("%s" % title)
    print("  %s (%d bytes)" % (path_relative, len(text)))
    print("")

    if method_prefixes is None:
        # Print declared members and their types.
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith(("UPROPERTY", "//", "*", "/*")):
                continue
            match = re.match(r"([\w:<>,\s\*&]+?)\s+(\w+)\s*(?:=[^;]*)?;", stripped)
            if match and len(match.group(2)) > 2:
                kind, name = match.group(1).strip(), match.group(2)
                if kind and not kind.startswith(("return", "if", "for")):
                    print("  %-40s %s" % (name, kind[:28]))
    else:
        names = []
        for match in re.finditer(r"\b(\w+)\s*\(", text):
            name = match.group(1)
            if any(name.startswith(prefix) for prefix in method_prefixes):
                if name not in names:
                    names.append(name)
        for name in names[:limit]:
            print("  %s" % name)
        print("  ... %d total" % len(names))
    print("")


def main():
    show(MODEL, "UAnimationDataModel", method_prefixes=["Get", "Evaluate", "Is", "GetNum"])
    show(CONTROLLER, "IAnimationDataController",
         method_prefixes=["Set", "Add", "Remove", "Open", "Close", "Update", "Insert"])
    show(TRACK, "FBoneAnimationTrack (the per-bone record)")


if __name__ == "__main__":
    main()
