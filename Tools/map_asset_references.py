"""Read the reference types that decide when an asset loads.

The distinction that matters for any real project is between a hard reference, which forces the
asset to load with its owner, and a soft reference, which is a path that can be resolved later or
not at all. Getting this wrong is why projects that run fine in the editor ship with a hundred
second load times, or why content fails to appear in a packaged build.

This reads the soft-reference headers and reports the API each one offers.

    python Tools/map_asset_references.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

TARGETS = [
    ("SoftObjectPtr", "Runtime/CoreUObject/Public/UObject/SoftObjectPtr.h"),
    ("SoftObjectPath", "Runtime/CoreUObject/Public/UObject/SoftObjectPath.h"),
    ("SoftClassPath", "Runtime/CoreUObject/Public/UObject/SoftObjectPath.h"),
    ("TSoftObjectPtr", "Runtime/CoreUObject/Public/UObject/SoftObjectPtr.h"),
    ("FStreamableManager", "Runtime/Engine/Public/Engine/StreamableManager.h"),
    ("FStreamableHandle", "Runtime/Engine/Public/Engine/StreamableManager.h"),
    ("UAssetManager", "Runtime/Engine/Classes/Engine/AssetManager.h"),
]


def find(relative):
    path = os.path.join(ENGINE, relative.replace("/", os.sep))
    return path if os.path.exists(path) else None


def methods(text, class_name):
    """Collect the member function names declared in a class body."""
    match = re.search(r"(?:class|struct)\s+(?:\w+_API\s+)?%s\b[^\{]*\{" % class_name, text)
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
    body = text[start:index]

    names = []
    for match in re.finditer(r"\b([A-Z]\w{3,40})\s*\(", body):
        name = match.group(1)
        if name not in names and not name.startswith(("if", "for", "while", "return")):
            names.append(name)
    return names[:24]


def main():
    seen_paths = {}
    for class_name, relative in TARGETS:
        path = find(relative)
        if path is None:
            print("%-22s  header missing" % class_name)
            continue
        if path not in seen_paths:
            seen_paths[path] = os.path.getsize(path)
        text = open(path, encoding="utf-8", errors="replace").read()
        names = methods(text, class_name)
        print("=" * 78)
        print("%s   in %s" % (class_name, os.path.basename(path)))
        if names is None:
            print("  (declaration not matched)")
        else:
            print("  %s" % ", ".join(names))
        print("")

    print("header sizes:")
    for path, size in seen_paths.items():
        print("  %-44s %8d B" % (os.path.basename(path), size))
    print("")
    print("What the distinction buys:")
    print("  hard reference (UObject*)    owner and target load together; simple, and heavy")
    print("  soft reference (TSoftObjectPtr)  a path only; load on demand, or never")
    print("  StreamableManager            resolves soft paths asynchronously, with a handle")
    print("  AssetManager                 groups assets into primary bundles with rules")


if __name__ == "__main__":
    main()
