"""Find the supported way to write animation bone tracks.

Reading raw tracks is exposed to Python through AnimationBlueprintLibrary, but writing them is
not - there is no SetRawTrackPositionData alongside the Get versions. That means an importer
built from decoded game data either has to reach the animation data model through C++, or use a
different route entirely.

This searches the engine for whichever interface actually owns the write side, so the conclusion
rests on the source rather than on the absence of a name in one header.

    python Tools/find_animation_write_path.py
"""

import os
import re

ENGINE = r"C:\Program Files\Epic Games\UE_5.8\Engine\Source"

# Names that would indicate the write side of animation data.
KEYWORDS = [
    "SetBoneTrackKeys",
    "AddBoneTrack",
    "SetRawTrack",
    "OpenBracket",
    "AddBoneCurve",
    "AnimationDataController",
    "IAnimationDataController",
    "SetPlayLength",
    "AddNewRawTrack",
]

# Files whose names suggest they hold the controller.
FILE_HINTS = ["DataController", "AnimDataModel", "AnimSequence", "AnimationData"]


def main():
    interesting_files = []
    for root, dirs, files in os.walk(ENGINE):
        for name in files:
            if not name.endswith((".h", ".cpp")):
                continue
            if any(hint in name for hint in FILE_HINTS):
                interesting_files.append(os.path.join(root, name))

    print("candidate files: %d" % len(interesting_files))
    print("")

    hits = {}
    for path in interesting_files:
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for keyword in KEYWORDS:
            if keyword in text:
                hits.setdefault(keyword, []).append(
                    (os.path.relpath(path, ENGINE), text.count(keyword)))

    for keyword in KEYWORDS:
        entries = hits.get(keyword, [])
        if not entries:
            continue
        print("=== %s  (%d files)" % (keyword, len(entries)))
        for relative, count in sorted(entries, key=lambda item: -item[1])[:4]:
            print("    %-72s x%d" % (relative, count))
        print("")

    # Where is the controller declared, and is any of it reachable from Python?
    for path in interesting_files:
        if "DataController" not in os.path.basename(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        callable_count = len(re.findall(r"UFUNCTION\s*\([^)]*BlueprintCallable", text))
        print("=== %s" % os.path.relpath(path, ENGINE))
        print("    size %d bytes, BlueprintCallable UFUNCTIONs: %d" % (len(text), callable_count))
        for match in re.finditer(r"^\s*(?:virtual\s+)?[\w:<>*&\s]+?\b(Set\w+|Add\w+|Open\w+)\s*\(",
                                 text, re.M):
            print("      %s" % match.group(1))
        print("")


if __name__ == "__main__":
    main()
