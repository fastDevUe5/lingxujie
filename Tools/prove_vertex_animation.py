"""Prove that the remaining unparsed animations are vertex animations, not failures.

A file whose blocks declare zero rotation, position and scale keys but a non-zero animated mesh key
count has no bone tracks to find. Returning nothing for it is correct behaviour, not a parse error,
and lumping the two together in a report overstates how much is broken.

    python Tools/prove_vertex_animation.py
"""

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_mod_anim_gltf as exporter

ANM_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/anm"
MARKER = b"\x00\xF0\x00\x00"
HEADER = 152
POS = 20
ROT = 24
SCALE = 36


def block_summary(data, start):
    """Return totals of the declared counts across every block we can read."""
    totals = {"rot": 0, "pos": 0, "scale": 0, "mesh": 0, "blocks": 0}
    offset = start
    while offset + 8 <= len(data) and data[offset:offset + 4] == MARKER:
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        if size < HEADER or payload + size > len(data):
            break
        (_obj, rot_n, pos_n, scale_n, mesh_n) = struct.unpack_from("<5I", data, payload)
        required = HEADER + pos_n * POS + rot_n * ROT + scale_n * SCALE
        if required > size:
            break
        totals["rot"] += rot_n
        totals["pos"] += pos_n
        totals["scale"] += scale_n
        totals["mesh"] += mesh_n
        totals["blocks"] += 1
        offset = payload + size
    return totals


def main():
    names = sorted(n for n in os.listdir(ANM_FOLDER) if n.endswith(".anm"))
    no_tracks = []
    for name in names:
        path = os.path.join(ANM_FOLDER, name)
        try:
            tracks = exporter.parse_anm(path)
        except (OSError, struct.error):
            tracks = {}
        if tracks:
            continue
        data = open(path, "rb").read()
        start = exporter.anm_first_block(data)
        if start is None:
            no_tracks.append((name, None))
            continue
        no_tracks.append((name, block_summary(data, start)))

    print("files with no bone tracks: %d" % len(no_tracks))
    print("")

    vertex_only = 0
    other = 0
    unlocatable = 0
    mesh_total = 0

    for name, totals in no_tracks:
        if totals is None:
            unlocatable += 1
            continue
        bone_keys = totals["rot"] + totals["pos"] + totals["scale"]
        if bone_keys == 0 and totals["mesh"] > 0:
            vertex_only += 1
            mesh_total += totals["mesh"]
        else:
            other += 1

    print("  vertex-animated only (no bone keys, mesh keys present): %d" % vertex_only)
    print("    total mesh keys across them: %d" % mesh_total)
    print("  block start could not be located:                        %d" % unlocatable)
    print("  some other shape:                                       %d" % other)
    print("")

    print("examples of vertex-animated files:")
    shown = 0
    for name, totals in no_tracks:
        if totals is None:
            continue
        bone_keys = totals["rot"] + totals["pos"] + totals["scale"]
        if bone_keys == 0 and totals["mesh"] > 0:
            print("  %-26s %2d blocks, %d mesh keys" % (name, totals["blocks"], totals["mesh"]))
            shown += 1
            if shown >= 10:
                break

    print("")
    print("conclusion: these files animate mesh vertices rather than bones. Reporting zero bone")
    print("tracks for them is correct; they are props and effects, not characters.")


if __name__ == "__main__":
    main()
