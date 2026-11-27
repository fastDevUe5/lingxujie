"""Find the rotation track inside an .anm bone payload.

Translation is solved: a section of twenty byte records, each an index followed by three floats
in centimetres. Scale is solved: thirty-six byte records of three floats. What is not solved is
rotation, and a skeleton cannot be animated without it - a character whose bones only translate
and scale has no pose.

The earlier notes mention a section beginning with the marker 0x0C and one with five floats whose
meaning was never settled. A rotation track would look different from both: either four floats
that hold together as a unit quaternion, or three small floats in radians. This decodes a real
bone payload section by section and reports which arithmetic the numbers actually satisfy,
rather than which one the notes hoped they would.

    python Tools/find_rotation_track.py <anm path> [bone name]
"""

import math
import os
import struct
import sys

DEFAULT = "C:/Users/tk/Desktop/moxiang-study/animations/198_bobu.anm"
BLOCK_MAGIC = 0xF000


def read_u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def find_bone_payloads(data):
    """Walk the block chain: each block is a marker, a size, then the payload."""
    blocks = []
    offset = 0
    end = len(data) - 8
    while offset < end:
        marker = read_u32(data, offset)
        if marker == BLOCK_MAGIC:
            size = read_u32(data, offset + 4)
            if 8 < size < len(data) - offset:
                blocks.append((offset + 8, size - 8))
                offset += size
                continue
        offset += 4
    return blocks


def describe_section(payload, start, count, stride):
    """Report whether the floats at this stride look like a quaternion or a rotation."""
    values = []
    for i in range(min(count, 8)):
        base = start + i * stride
        if base + stride > len(payload):
            break
        index = read_u32(payload, base)
        floats = struct.unpack_from("<%df" % ((stride - 4) // 4), payload, base + 4)
        values.append((index, floats))

    if not values:
        return None

    floats_per = (stride - 4) // 4
    # A unit quaternion has length 1 within rounding. Test the first few records.
    if floats_per == 4:
        lengths = [math.sqrt(sum(v * v for v in floats)) for _, floats in values[:5]]
        if all(0.9 < length < 1.1 for length in lengths):
            return ("QUATERNION", lengths[0], values[:3])
        return ("4 floats, not unit", lengths[0], values[:3])

    # Three small values in radians would be a Euler rotation.
    if floats_per == 3:
        spans = [max(abs(v) for v in floats) for _, floats in values[:5]]
        if all(span <= 6.3 for span in spans):
            return ("EULER radians (possible)", spans[0], values[:3])
        return ("3 floats, large (likely position)", spans[0], values[:3])

    return ("%d floats" % floats_per, None, values[:3])


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    want = sys.argv[2] if len(sys.argv) > 2 else "Bip01 R Thigh"

    if not os.path.exists(path):
        print("missing %s" % path)
        return 1

    data = open(path, "rb").read()
    print("%s  %d bytes" % (os.path.basename(path), len(data)))

    blocks = find_bone_payloads(data)
    print("bone payloads found: %d" % len(blocks))
    print("")

    for start, size in blocks:
        payload = data[start:start + size]
        name_end = payload.find(b"\x00", 0)
        # The name sits after a short fixed prefix; find the printable run instead.
        text = payload[:400]
        best = b""
        for chunk in text.split(b"\x00"):
            if 3 < len(chunk) < 40 and chunk[:1].isalpha():
                if len(chunk) > len(best):
                    best = chunk
        try:
            name = best.decode("latin-1")
        except UnicodeDecodeError:
            name = "?"
        if want.lower() not in name.lower():
            continue

        print("=== %s  (payload %d bytes)" % (name, size))
        # Try each candidate stride from the notes and see which self-validates: an index that
        # counts 0, 1, 2 ... is the marker that a stride is correct.
        for stride in (20, 24, 36, 56, 16, 28, 32, 40, 44, 48, 52):
            floats_per = (stride - 4) // 4
            if stride % 4 or floats_per < 1:
                continue
            for offset in range(0, min(len(payload) - stride * 4, 4000), 4):
                indices = []
                ok = True
                for i in range(4):
                    base = offset + i * stride
                    if base + stride > len(payload):
                        ok = False
                        break
                    indices.append(read_u32(payload, base))
                if ok and indices == [0, 1, 2, 3]:
                    result = describe_section(payload, offset, 64, stride)
                    if result:
                        verdict, measure, sample = result
                        print("  stride %-3d floats %-2d at offset %-5d -> %s"
                              % (stride, floats_per, offset, verdict))
                        if measure is not None:
                            print("        measure %.4f" % measure)
                        for index, floats in sample:
                            print("        [%d] %s"
                                  % (index, ", ".join("%.4f" % f for f in floats)))
                        break
        print("")


if __name__ == "__main__":
    main()
