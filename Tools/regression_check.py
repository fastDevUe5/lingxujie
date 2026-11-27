"""Check that removing the mesh matrix did not break the models that worked before.

The bird and the other character exported correctly when mesh matrices were applied, so the change
that fixed the boss could have broken them. This exports a set of models and reports each one's
bounds so a regression shows up as a number rather than as a picture nobody compares.

A model is suspect if its bounds are enormous (metres where centimetres belong), degenerate (all
three extents near zero), or wildly different in one axis from the others.

    python Tools/regression_check.py
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")

import export_mod_anim_gltf as exporter

MOD = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
ANM = "C:/Users/tk/Desktop/moxiang-study/resources/anm"
OUT = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/regression"

# name, animation if any
CASES = [
    ("108_bird", "108_birda.anm"),
    ("198_bobu", "198_bobu.anm"),
    ("boss001", "boss001_01.anm"),
    ("boss_cowf_01", "Boss_cowf_01.anm"),
    ("216", None),
    ("w25260", None),
    ("107_crow", "107_crow.anm"),
    ("20_eagle_01", None),
]


def bounds(gltf_path):
    data = json.load(open(gltf_path, encoding="utf-8"))
    low = [1e18] * 3
    high = [-1e18] * 3
    primitives = 0
    for mesh in data.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            accessor = data["accessors"][primitive["attributes"]["POSITION"]]
            primitives += 1
            for axis in range(3):
                low[axis] = min(low[axis], accessor["min"][axis])
                high[axis] = max(high[axis], accessor["max"][axis])
    return tuple(high[i] - low[i] for i in range(3)), primitives


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    print("%-16s %-8s %-9s %-26s %s"
          % ("model", "blocks", "channels", "bounds (m)", "verdict"))
    print("-" * 84)

    problems = 0
    for name, animation in CASES:
        mod_path = os.path.join(MOD, name + ".mod")
        if not os.path.exists(mod_path):
            print("%-16s missing" % name)
            continue
        anm_path = os.path.join(ANM, animation) if animation else None
        if anm_path and not os.path.exists(anm_path):
            anm_path = None

        out_path = os.path.join(OUT, name + ".gltf")
        try:
            objects = exporter.parse_mod(mod_path)
            tracks = exporter.parse_anm(anm_path) if anm_path else {}
            gltf, blob = exporter.build(objects, tracks, name)

            binary_path = os.path.splitext(out_path)[0] + ".bin"
            open(binary_path, "wb").write(blob)
            gltf["buffers"][0]["uri"] = os.path.basename(binary_path)
            # byteLength must be recomputed after animation accessors were appended.
            gltf["buffers"][0]["byteLength"] = len(blob)
            json.dump(gltf, open(out_path, "w", encoding="utf-8"), indent=1)
        except Exception as error:  # noqa: BLE001
            print("%-16s FAILED: %s: %s" % (name, type(error).__name__, error))
            problems += 1
            continue

        extent, primitives = bounds(out_path)
        channels = 0
        if gltf.get("animations"):
            channels = len(gltf["animations"][0].get("channels", []))

        verdict = "ok"
        if max(extent) > 100.0:
            verdict = "TOO BIG"
        elif max(extent) < 0.01:
            verdict = "DEGENERATE"
        elif max(extent) > 10.0 * max(min(extent), 1e-6) and min(extent) > 0:
            verdict = "very lopsided"
        if verdict not in ("ok", "very lopsided"):
            problems += 1

        print("%-16s %-8d %-9d %-26s %s"
              % (name, primitives, channels,
                 "%.2f x %.2f x %.2f" % extent, verdict))

    print("")
    print("problems: %d" % problems)
    if problems == 0:
        print("every model still produces plausible bounds, so the mesh-matrix change is safe.")
    else:
        print("at least one model regressed; compare against the numbers recorded earlier.")


if __name__ == "__main__":
    main()
