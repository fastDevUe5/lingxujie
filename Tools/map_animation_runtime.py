"""Read the runtime half of the animation system: instance, montage, blend space, notifies.

Everything studied so far concerns the asset - how tracks are stored and written. None of it
explains how an animation plays, or how one animation replaces another when the character starts
running, or how a hit is triggered at frame fifteen. Those are the runtime classes, and they are
the difference between an animation that imports and an animation that is used.

    python Tools/map_animation_runtime.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

TARGETS = [
    ("UAnimInstance", "AnimInstance.h"),
    ("UAnimMontage", "AnimMontage.h"),
    ("UBlendSpace", "BlendSpace.h"),
    ("UAnimNotify", "AnimNotify.h"),
    ("UAnimNotifyState", "AnimNotifyState.h"),
    ("UAnimationStateMachineLibrary", "AnimationStateMachineLibrary.h"),
    ("FAnimNode_StateMachine", "AnimNode_StateMachine.h"),
]

PREFIXES = ("Play", "Montage", "Get", "Set", "Stop", "Is", "Jump", "Blend", "Update",
            "Trigger", "Add", "Remove")


def size_and_path(name):
    for root, dirs, files in os.walk(ENGINE):
        if name in files:
            full = os.path.join(root, name)
            return os.path.getsize(full), full
    return None, None


def functions(path, limit=20):
    text = open(path, encoding="utf-8", errors="replace").read()
    names = []
    for match in re.finditer(r"\b(?:virtual\s+)?[\w:<>*&\s]+?\b(\w{4,40})\s*\(", text):
        name = match.group(1)
        if name in names:
            continue
        if not any(name.startswith(prefix) for prefix in PREFIXES):
            continue
        names.append(name)
        if len(names) >= limit:
            break
    return names, len(text)


def main():
    for class_name, filename in TARGETS:
        size, path = size_and_path(filename)
        if path is None:
            print("%-32s  missing" % class_name)
            print("")
            continue
        names, header_size = functions(path)
        rel = os.path.relpath(path, ENGINE)
        print("=" * 78)
        print("%-32s %s" % (class_name, rel))
        print("  %d bytes" % header_size)
        print("  %s" % ", ".join(names))
        print("")


if __name__ == "__main__":
    main()
