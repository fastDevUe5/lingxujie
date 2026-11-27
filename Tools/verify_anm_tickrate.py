"""Confirm the tick rate across many files, which settles the frame rate question.

One file gave one hundred sixty ticks per frame. That only becomes a frame rate once the ticks per
second is known, and the value that makes the arithmetic land on a round number is four thousand
eight hundred - the 3ds Max constant, which is what a Biped rig would be exported from.

This measures ticks-per-frame and implied frames-per-second across a range of files, so the claim
rests on a distribution rather than on one sample.

    python Tools/verify_anm_tickrate.py
"""

import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/anm"
MOTION_OBJECT_HEADER = 152
ROT_KEY = 24

TICK_CANDIDATES = [4800, 160000, 1000, 90000, 3200, 2400]


def first_block(data):
    for offset in range(0, len(data) - 8):
        if data[offset:offset + 4] == b"\x00\xF0\x00\x00":
            size = struct.unpack_from("<I", data, offset + 4)[0]
            if MOTION_OBJECT_HEADER <= size and offset + 8 + size <= len(data):
                return offset, size
    return None, None


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def analyse(path):
    """Return (ticks_per_frame, frame_count) from the first block that has rotation keys."""
    data = open(path, "rb").read()
    offset, size = first_block(data)
    if offset is None:
        return None

    while offset + 8 <= len(data) and data[offset:offset + 4] == b"\x00\xF0\x00\x00":
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        if size < MOTION_OBJECT_HEADER or payload + size > len(data):
            break
        (obj_index, rot_keys, pos_keys, scale_keys,
         mesh_keys) = struct.unpack_from("<5I", data, payload)
        if rot_keys >= 2:
            cursor = payload + MOTION_OBJECT_HEADER + pos_keys * 20
            if cursor + ROT_KEY * 2 <= payload + size:
                t0, f0 = struct.unpack_from("<II", data, cursor)
                t1, f1 = struct.unpack_from("<II", data, cursor + ROT_KEY)
                if f1 > f0 and t1 > t0:
                    return ((t1 - t0) / float(f1 - f0), rot_keys)
        offset = payload + size
    return None


def main():
    names = sorted(n for n in os.listdir(FOLDER) if n.endswith(".anm"))
    print("anm files: %d" % len(names))
    print("")

    results = []
    examined = 0
    for name in names:
        if examined >= 60:
            break
        try:
            outcome = analyse(os.path.join(FOLDER, name))
        except (OSError, struct.error):
            continue
        if outcome is None:
            continue
        ticks_per_frame, frames = outcome
        if 0 < ticks_per_frame < 100000:
            results.append((name, ticks_per_frame, frames))
            examined += 1

    print("%-34s %-14s %s" % ("file", "ticks/frame", "frames"))
    print("-" * 66)
    for name, ticks, frames in results[:24]:
        print("%-34s %-14.2f %d" % (name[:34], ticks, frames))

    print("")
    if results:
        ticks_values = sorted(set(round(r[1], 0) for r in results))
        print("distinct ticks-per-frame values: %s" % ticks_values[:12])
        print("")
        print("implied frames per second for each candidate tick rate:")
        for per_second in TICK_CANDIDATES:
            rates = sorted(set(round(per_second / r[1], 2) for r in results
                               if r[1] > 0))
            print("  %-8d -> fps %s" % (per_second, rates[:8]))
    print("")


if __name__ == "__main__":
    main()
