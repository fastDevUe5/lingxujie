"""Classify the animations that still fail to parse.

Ninety-three percent parse; the rest are not noise, they are a category. Sorting them by what goes
wrong - no block marker at all, a first block that does not fit, a walk that stops partway - says
which of those categories is worth handling and which is a genuinely broken file.

    python Tools/classify_anm_failures.py
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


def classify(path):
    """Return (category, detail) for a file the exporter could not use."""
    try:
        data = open(path, "rb").read()
    except OSError as error:
        return "unreadable", str(error)

    if len(data) < 16:
        return "too small", "%d bytes" % len(data)

    markers = [i for i in range(len(data) - 8) if data[i:i + 4] == MARKER]
    if not markers:
        return "no marker", "no 00 F0 00 00 anywhere; first bytes %s" % data[:8].hex()

    # Find the first marker whose block is plausible.
    start = None
    for offset in markers:
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size >= HEADER and offset + 8 + size <= len(data):
            start = offset
            break
    if start is None:
        size = struct.unpack_from("<I", data, markers[0] + 4)[0]
        return "first block implausible", "size %d at offset %d" % (size, markers[0])

    offset = start
    blocks = 0
    while offset + 8 <= len(data) and data[offset:offset + 4] == MARKER:
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        if size < HEADER or payload + size > len(data):
            break
        (_obj, rot_n, pos_n, scale_n, _mesh) = struct.unpack_from("<5I", data, payload)
        required = HEADER + pos_n * POS + rot_n * ROT + scale_n * SCALE
        if required > size:
            return "counts overflow", ("block %d needs %d of %d"
                                       % (blocks, required, size))
        offset = payload + size
        blocks += 1

    if blocks == 0:
        return "no blocks read", "first marker at %d" % start
    return "partial", "%d blocks, %d bytes left" % (blocks, len(data) - offset)


def main():
    names = sorted(n for n in os.listdir(ANM_FOLDER) if n.endswith(".anm"))
    print("anm files: %d" % len(names))
    print("")

    failures = {}
    for name in names:
        path = os.path.join(ANM_FOLDER, name)
        try:
            tracks = exporter.parse_anm(path)
        except (OSError, struct.error):
            category, detail = classify(path)
            failures.setdefault(category, []).append((name, detail))
            continue
        if not tracks:
            category, detail = classify(path)
            failures.setdefault(category, []).append((name, detail))

    total = sum(len(v) for v in failures.values())
    print("failures: %d" % total)
    print("")
    for category in sorted(failures, key=lambda key: -len(failures[key])):
        group = failures[category]
        print("%-26s %4d files" % (category, len(group)))
        for name, detail in group[:3]:
            print("    %-30s %s" % (name, detail[:70]))
        print("")

    print("if 'partial' dominates, the walk stops before the end of the file and the remainder")
    print("is a tail - which is fine and only worth reporting, not fixing.")


if __name__ == "__main__":
    main()
