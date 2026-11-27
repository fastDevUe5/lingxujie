"""Map the subsystem hierarchy, which decides where code belongs.

A subsystem is the engine's answer to "where does this belong": engine-wide, editor-wide,
per-world, or per-game-session. Getting the level wrong produces bugs that look unrelated - state
that resets unexpectedly, editors that keep stale data, tools that work once.

Each level is a class in the engine's source with a documented purpose, so this reads the headers
and reports lifetime, count and the accessor that fetches one.

    python Tools/map_subsystems.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

LEVELS = [
    ("UEngineSubsystem", "Runtime/Engine/Public/Subsystems/EngineSubsystem.h"),
    ("UEditorSubsystem", "Editor/UnrealEd/Public/Subsystems/EditorSubsystem.h"),
    ("UWorldSubsystem", "Runtime/Engine/Public/Subsystems/WorldSubsystem.h"),
    ("UTickableWorldSubsystem", "Runtime/Engine/Public/Subsystems/WorldSubsystem.h"),
    ("UGameInstanceSubsystem", "Runtime/Engine/Public/Subsystems/GameInstanceSubsystem.h"),
    ("ULocalPlayerSubsystem", "Runtime/Engine/Public/Subsystems/LocalPlayerSubsystem.h"),
]


def find(name, hint):
    candidate = os.path.join(ENGINE, hint.replace("/", os.sep))
    if os.path.exists(candidate):
        return candidate
    stem = name[1:] + ".h"
    for root, dirs, files in os.walk(ENGINE):
        if stem in files:
            return os.path.join(root, stem)
    return None


def bases_of(path, name):
    text = open(path, encoding="utf-8", errors="replace").read()
    pattern = re.compile(
        r"class\s+(?:\w+_API\s+)?%s\s*(?:final\s*)?:\s*public\s+([^{]+)\{"
        % re.escape(name), re.S)
    match = pattern.search(text)
    return (" ".join(match.group(1).split()) if match else "?"), len(text)


def lifecycle_hooks(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    hooks = []
    for hook in ("Initialize", "Deinitialize", "OnWorldBeginPlay", "ShouldCreateSubsystem",
                 "DoesSupportWorldType", "Tick"):
        if re.search(r"virtual\s+[\w:*&\s]+%s\s*\(" % hook, text):
            hooks.append(hook)
    return hooks


def main():
    print("%-26s %-30s %8s %s" % ("class", "inherits", "header", "lifecycle hooks"))
    print("-" * 100)
    resolved = {}
    for name, hint in LEVELS:
        path = find(name, hint)
        if path is None:
            print("%-26s %-30s  NOT FOUND" % (name, "-"))
            continue
        resolved[name] = path
        bases, size = bases_of(path, name)
        hooks = lifecycle_hooks(path)
        print("%-26s %-30s %7dB  %s" % (name, bases[:30], size, ", ".join(hooks)))
    print("")

    print("accompanying collection types (one per level):")
    for name, hint in (("FSubsystemCollection", "Runtime/Engine/Public/Subsystems/SubsystemCollection.h"),
                       ("USubsystem", "Runtime/Engine/Public/Subsystems/Subsystem.h")):
        path = find(name, hint)
        if path:
            text = open(path, encoding="utf-8", errors="replace").read()
            print("  %-24s %7dB  exists" % (name, len(text)))
    print("")

    # Where the engine itself uses each level tells you what each is for.
    print("engine usage: how many classes derive from each level")
    counts = {name: 0 for name, _ in LEVELS}
    for root, dirs, files in os.walk(ENGINE):
        for filename in files:
            if not filename.endswith(".h"):
                continue
            try:
                text = open(os.path.join(root, filename), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for name in counts:
                short = name[1:]
                if re.search(r":\s*public\s+%s\b" % short, text):
                    counts[name] += 1
    for name, count in counts.items():
        print("  %-26s %4d subclasses" % (name, count))


if __name__ == "__main__":
    main()
