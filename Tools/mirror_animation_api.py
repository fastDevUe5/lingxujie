"""Animation-related Python API classes, for the one part of the project that needs them.

LingXuJie has 4,056 animations extracted from the client in the game's own format and no path
into the engine yet. That work sits entirely in the animation system - skeletons, bones, pose
tracks, animation sequences - which is the area this project knows least about. These are the
classes that work touches.

Fetched separately from the main list so re-running after an engine upgrade does not have to
pull the whole editor surface again.

    python Tools/mirror_animation_api.py
"""

import html as html_module
import os
import re
import time
import urllib.error
import urllib.request

OUT_DIR = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"
BASE = "https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

CLASSES = [
    # Skeleton and bones
    "Skeleton",
    "SkeletalMesh",
    "SkeletalMeshComponent",
    "SkeletalMeshSocket",
    "SkeletalMeshLODInfo",
    "BoneNode",
    "BoneReference",
    "BoneID",
    "ReferenceSkeleton",
    "FReferenceSkeleton",
    # Animation assets
    "AnimSequence",
    "AnimSequenceBase",
    "AnimMontage",
    "AnimComposite",
    "BlendSpace",
    "BlendSpace1D",
    "AnimationAsset",
    "AnimationDataModel",
    "AnimationLibrary",
    # Raw animation data - the layer an importer writes into
    "AnimDataModel",
    "AnimationAttributeIdentifier",
    "AnimationCurveIdentifier",
    "BoneAnimationTrack",
    "AnimTrack",
    "RawAnimSequenceTrack",
    "FRawAnimSequenceTrack",
    "RawAnimationData",
    # Playing animations
    "AnimInstance",
    "AnimSingleNodeInstance",
    "AnimationBlueprintLibrary",
    "AnimationBlueprintSystem",
    "AnimBlueprint",
    # Editors
    "SkeletalMeshEditorSubsystem",
    "AnimationEditorSubsystem",
    # Import
    "SkeletalMeshImportData",
    "AnimSequenceImportData",
    "FbxImportUI",
    "FbxSkeletalMeshImportData",
    "FbxAnimImportData",
    "AssetImportTask",
]


def fetch(url, timeout=50):
    last = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last = error
            time.sleep(1.2 * (attempt + 1))
    raise last if last else RuntimeError("unknown failure")


def strip_html(raw):
    start = raw.find("<h1")
    if start < 0:
        start = raw.find("<body")
    if start < 0:
        start = 0
    end = raw.find("Table of Contents")
    body = raw[start:end] if end > start else raw[start:]
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body)
    body = html_module.unescape(body).replace("\u00b6", "")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n\s*\n+", "\n\n", body)
    return body.strip()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    saved = skipped = failed = 0
    failures = []
    started = time.time()

    for name in CLASSES:
        target = os.path.join(OUT_DIR, name + ".txt")
        if os.path.exists(target) and os.path.getsize(target) > 200:
            skipped += 1
            continue
        try:
            raw = fetch(BASE + name + ".html")
        except Exception as error:  # noqa: BLE001
            failed += 1
            failures.append("%s: %s" % (name, str(error)[:70]))
            print("  FAIL %s" % name, flush=True)
            continue
        text = strip_html(raw)
        if len(text) < 120:
            failed += 1
            failures.append("%s: empty page" % name)
            print("  EMPTY %s" % name, flush=True)
            continue
        with open(target, "w", encoding="utf-8") as handle:
            handle.write("# unreal.%s  (UE 5.8 Python API)\n\nSource: %s%s.html\n\n"
                         % (name, BASE, name))
            handle.write(text)
        saved += 1
        print("  [ok] %-32s %6d chars" % (name, len(text)), flush=True)

    print("DONE saved %d skipped %d failed %d in %.0fs"
          % (saved, skipped, failed, time.time() - started), flush=True)
    if failures:
        print("failures: %s" % "; ".join(failures))


if __name__ == "__main__":
    main()
