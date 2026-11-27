"""Map the engine-side animation architecture, which is the half not yet studied.

The animation document so far records the reachable surface - what Python can and cannot do - and
the plan for getting decoded tracks into the engine. What it does not cover is how the engine
actually stores and plays an animation, which is what decides whether an importer produces
something usable or just something that imports.

This reads the four classes that matter and reports what each owns.

    python Tools/map_animation_engine.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

TARGETS = [
    ("USkeleton", ["Skeleton.h", "Runtime/Engine/Classes/Engine/Skeleton.h"]),
    ("UAnimSequenceBase", ["AnimSequenceBase.h"]),
    ("UAnimSequence", ["AnimSequence.h"]),
    ("UAnimInstance", ["AnimInstance.h"]),
    ("UAnimMontage", ["AnimMontage.h"]),
    ("UBlendSpace", ["BlendSpace.h"]),
    ("UAnimBlueprintGeneratedClass", ["AnimBlueprintGeneratedClass.h"]),
    ("UAnimationDataModel", ["AnimDataModel.h"]),
    ("IAnimationDataController", ["IAnimationDataController.h"]),
]


def find(candidates):
    for name in candidates:
        path = os.path.join(ENGINE, name.replace("/", os.sep))
        if os.path.exists(path):
            return path
        for root, dirs, files in os.walk(ENGINE):
            if name in files:
                return os.path.join(root, name)
    return None


def class_body(text, name):
    pattern = re.compile(
        r"(?:class|struct)\s+(?:\w+_API\s+)?%s\b[^\{]*\{" % re.escape(name), re.S)
    match = pattern.search(text)
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


def public_functions(body, limit=14):
    names = []
    for match in re.finditer(r"\b(?:virtual\s+)?[\w:<>*&\s]+?\b([A-Z]\w{3,40})\s*\(", body):
        name = match.group(1)
        if name not in names and not name.startswith(("If", "For", "While", "Return")):
            names.append(name)
        if len(names) >= limit * 3:
            break
    return names[:limit]


def main():
    for class_name, candidates in TARGETS:
        path = find(candidates)
        if path is None:
            print("%-26s  header not found" % class_name)
            print("")
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        body = class_body(text, class_name)
        rel = os.path.relpath(path, ENGINE)
        print("=" * 78)
        print("%-26s %s" % (class_name, rel))
        print("  header %d bytes" % len(text))
        if body is None:
            print("  (declaration not matched - may be a template or forward declaration)")
            print("")
            continue
        print("  body %d bytes" % len(body))
        print("  functions: %s" % ", ".join(public_functions(body)))
        # What this class owns, which is the part that matters for an importer.
        owns = []
        for keyword in ("BoneTree", "RefSkeleton", "DataModel", "Notifies", "Curves",
                        "RateScale", "PlayLength", "Skeleton", "Montage", "BlendSpace"):
            if keyword in body:
                owns.append(keyword)
        if owns:
            print("  owns: %s" % ", ".join(owns))
        print("")


if __name__ == "__main__":
    main()
