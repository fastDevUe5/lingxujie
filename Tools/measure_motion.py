"""Measure how much motion the source animation actually contains.

The engine-side playback probe has cost several attempts on API names. The question underneath it -
does this clip move anything - can be answered from the file, with no engine involved: for each track,
how far do the rotation keys travel from the first one, and how much does position vary.

A clip whose every key is identical is a still pose. One whose keys diverge by tens of degrees is an
animation, and if that is what the exporter wrote then any playback problem is in the engine setup
rather than in the data.

    python Tools/measure_motion.py
"""

import math
import sys

sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")
import export_mod_anim_gltf as exporter

CASES = [
    ("boss001_01.anm", "C:/Users/tk/Desktop/moxiang-study/resources/anm/boss001_01.anm"),
    ("Boss_cowf_01.anm", "C:/Users/tk/Desktop/moxiang-study/resources/anm/Boss_cowf_01.anm"),
    ("108_birda.anm", "C:/Users/tk/Desktop/moxiang-study/resources/anm/108_birda.anm"),
    ("198_bobu.anm", "C:/Users/tk/Desktop/moxiang-study/resources/anm/198_bobu.anm"),
]


def quat_angle(a, b):
    """Angle in degrees between two quaternions, robust to sign."""
    dot = abs(a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3])
    dot = min(1.0, max(-1.0, dot))
    return 2.0 * math.degrees(math.acos(dot))


def main():
    for name, path in CASES:
        try:
            tracks = exporter.parse_anm(path)
        except Exception as error:  # noqa: BLE001
            print("%-20s parse failed: %s" % (name, error))
            continue
        if not tracks:
            print("%-20s no tracks" % name)
            continue

        rotation_ranges = []
        position_ranges = []
        for track_name, data in tracks.items():
            rotations = data.get("rotations", [])
            positions = data.get("positions", [])
            if len(rotations) >= 2:
                first = rotations[0][1]
                worst = max(quat_angle(first, r[1]) for r in rotations[1:])
                rotation_ranges.append((worst, track_name, len(rotations)))
            if len(positions) >= 2:
                first = positions[0][1]
                worst = max(max(abs(p[1][i] - first[i]) for i in range(3))
                            for p in positions[1:])
                position_ranges.append((worst, track_name, len(positions)))

        rotation_ranges.sort(reverse=True)
        position_ranges.sort(reverse=True)

        print("=== %s: %d tracks" % (name, len(tracks)))
        if rotation_ranges:
            biggest = rotation_ranges[0]
            print("    rotation: %d tracks with 2+ keys, largest swing %.1f deg on %r (%d keys)"
                  % (len(rotation_ranges), biggest[0], biggest[1], biggest[2]))
            moving = sum(1 for r in rotation_ranges if r[0] > 1.0)
            print("    tracks whose rotation changes by more than 1 degree: %d" % moving)
        if position_ranges:
            biggest = position_ranges[0]
            print("    position: %d tracks with 2+ keys, largest travel %.2f cm on %r"
                  % (len(position_ranges), biggest[0], biggest[1]))
        if not rotation_ranges and not position_ranges:
            print("    every track has a single key: a still pose, not a motion")
        print("")


if __name__ == "__main__":
    main()
