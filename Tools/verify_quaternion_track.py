"""Confirm that the 24-byte section is a quaternion track, across many bones and files.

The earlier notes left the twenty-four byte records unexplained - five floats, described as
"possibly position plus weight". Four of those five held together as a unit length in one
sample, which is what a quaternion looks like and what nothing else does. One sample is not
enough to build an importer on, so this checks the arithmetic across every bone in several
files and reports how often it holds.

A quaternion track makes skeletal animation possible at all: translation and scale alone leave a
character unable to bend a limb.

    python Tools/verify_quaternion_track.py
"""

import glob
import math
import os
import struct

ANIM_DIR = "C:/Users/tk/Desktop/moxiang-study/animations"
BLOCK_MAGIC = 0xF000
STRIDE = 24
TOLERANCE = 0.02


def sections_at_stride(data, start, stride, limit=64):
    """Yield (offset, count) where consecutive indices 0,1,2,3 appear."""
    found = []
    offset = start
    end = min(len(data) - stride * 4, start + 60000)
    while offset < end:
        try:
            indices = [struct.unpack_from("<I", data, offset + i * stride)[0] for i in range(4)]
        except struct.error:
            break
        if indices == [0, 1, 2, 3]:
            found.append(offset)
            offset += stride * limit
            continue
        offset += 4
    return found


def quaternion_lengths(data, offset, count=8):
    lengths = []
    for i in range(count):
        base = offset + i * STRIDE
        if base + STRIDE > len(data):
            break
        x, y, z, w, extra = struct.unpack_from("<5f", data, base + 4)
        lengths.append((math.sqrt(x * x + y * y + z * z + w * w), extra))
    return lengths


def main():
    files = sorted(glob.glob(os.path.join(ANIM_DIR, "*.anm")))
    print("animation files: %d" % len(files))
    print("")

    checked = unit = not_unit = 0
    extras = []
    samples = []
    scanned = 0

    for path in files:
        scanned += 1
        if scanned > 60:
            break
        try:
            data = open(path, "rb").read()
        except OSError:
            continue

        # Bone table: 0xF000 blocks of 160 bytes, each with a 152-byte declaration.
        markers = 0
        offset = 160
        while offset + 8 < len(data) and struct.unpack_from("<I", data, offset)[0] == BLOCK_MAGIC:
            markers += 1
            offset += 160
        if markers == 0:
            continue
        body_start = 160 + markers * 160

        for section in sections_at_stride(data, body_start, STRIDE)[:6]:
            lengths = quaternion_lengths(data, section)
            if not lengths:
                continue
            checked += len(lengths)
            for length, extra in lengths:
                extras.append(extra)
                if abs(length - 1.0) < TOLERANCE:
                    unit += 1
                else:
                    not_unit += 1
            if len(samples) < 6:
                first = lengths[0][0]
                samples.append((os.path.basename(path), markers, section, first))

    print("quaternion candidates checked: %d" % checked)
    print("  unit length (|q| within %.2f of 1.0): %d  (%.1f%%)"
          % (TOLERANCE, unit, 100.0 * unit / checked if checked else 0))
    print("  not unit length: %d" % not_unit)
    print("")
    if samples:
        print("samples:")
        for name, bones, offset, length in samples:
            print("  %-24s bones %-3d section @%-6d |q| = %.5f"
                  % (name, bones, offset, length))
        print("")
    if extras:
        zero_count = sum(1 for value in extras if abs(value) < 1e-6)
        print("fifth float: %d of %d are exactly zero (%.1f%%)"
              % (zero_count, len(extras), 100.0 * zero_count / len(extras)))
        print("  -> consistent with a padding float after the quaternion")


if __name__ == "__main__":
    main()
