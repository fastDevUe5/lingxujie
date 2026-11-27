"""Measure how many bones a typical animation actually moves.

The boss whose thirty-eight bones produced eight channels prompted a question that one file cannot
answer: is a sparse animation unusual, or normal? If most files move only a few bones, then eight is
unremarkable and the pipeline is fine. If most move nearly all of them, something specific is going
on with that boss.

    python Tools/measure_animation_density.py
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_mod_anim_gltf as exporter

ANM_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/anm"


def normalise(value):
    """Sort into a bucket for reporting."""
    for bound, label in ((2, "1"), (5, "2-5"), (11, "6-11"), (21, "12-21"),
                         (41, "22-41"), (81, "42-81")):
        if value < bound:
            return label
    return "82+"


def main():
    names = sorted(n for n in os.listdir(ANM_FOLDER) if n.endswith(".anm"))
    print("anm files: %d" % len(names))
    print("")

    buckets = {}
    total_tracks = 0
    parsed = 0
    empty = 0
    failed = 0

    for name in names:
        path = os.path.join(ANM_FOLDER, name)
        try:
            tracks = exporter.parse_anm(path)
        except (OSError, struct.error):
            failed += 1
            continue
        if not tracks:
            failed += 1
            continue
        parsed += 1
        counted = sum(1 for value in tracks.values()
                      if value["rotations"] or value["positions"] or value["scales"])
        total_tracks += counted
        if counted == 0:
            empty += 1
            continue
        label = normalise(counted)
        buckets[label] = buckets.get(label, 0) + 1

    print("parsed: %d, failed: %d, with zero animated tracks: %d"
          % (parsed, failed, empty))
    print("total animated tracks: %d" % total_tracks)
    if parsed:
        print("average tracks per file: %.1f" % (total_tracks / float(parsed)))
    print("")
    print("distribution of animated track counts:")
    order = ["1", "2-5", "6-11", "12-21", "22-41", "42-81", "82+"]
    for label in order:
        count = buckets.get(label, 0)
        if count:
            print("  %-8s %5d files" % (label, count))

    print("")
    print("interpretation: if most files sit in the low buckets, a sparse animation is normal")
    print("and a character moving six bones is not a pipeline problem.")


if __name__ == "__main__":
    main()
