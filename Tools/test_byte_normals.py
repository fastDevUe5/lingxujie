"""Test the byte-quantisation hypothesis for normals, with vertex count as the free variable.

The argument: no float layout found unit-length vectors in most character models, and engines of
this era commonly stored normals as three unsigned bytes scaled from minus one to one. If that is
right, wherever normals live there is a run of vertexcount triples of bytes whose scaled values have
length one.

The unknown is the vertex count, so this does not guess it. For each candidate count it checks every
offset for a run of that many consecutive normalised-triple bytes, and reports how many candidates
survive. A layout that is right should produce long exact runs at a specific vertex count;
a layout that is wrong produces scattered coincidence.

    python Tools/test_byte_normals.py
"""

import math
import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
HEADER = 8

SAMPLES = ["216.mod", "219.mod", "19240.mod", "choco.mod", "108_bird.mod",
           "costume_wing_10.mod", "20_eagle_01.mod"]


def mesh_payload(data):
    offset = 28
    while offset + HEADER + 4 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + HEADER + size > len(data) + 4:
            return None
        if marker == 0xF4000000:
            return offset + HEADER, size
        offset += HEADER + size
    return None


def normalised(values):
    """Scale three bytes as if they were the range -1..1."""
    return [value / 127.5 - 1.0 for value in values]


def unit_like(values, tolerance=0.06):
    x, y, z = normalised(values)
    return abs(math.sqrt(x * x + y * y + z * z) - 1.0) <= tolerance


def best_run(data, start, end, count):
    """Longest run of `count` consecutive unit-like byte triples, returning its offset."""
    best_offset = -1
    best_length = 0
    offset = start
    while offset + 3 <= end:
        if unit_like(data[offset:offset + 3]):
            run_start = offset
            length = 0
            while offset + 3 <= end and unit_like(data[offset:offset + 3]):
                length += 1
                offset += 3
            if length > best_length:
                best_length = length
                best_offset = run_start
        else:
            offset += 1
    return best_offset, best_length


def main():
    for name in SAMPLES:
        path = os.path.join(FOLDER, name)
        if not os.path.exists(path):
            print("%s: missing" % name)
            continue
        data = open(path, "rb").read()
        result = mesh_payload(data)
        if result is None:
            print("%s: no mesh block" % name)
            continue
        payload, size = result

        print("=" * 78)
        print("%s  payload=%d bytes" % (name, size))

        # Try the byte-normal hypothesis at several plausible vertex counts.
        # The payload must hold positions as floats too, so the count is bounded.
        candidates = [64, 96, 128, 192, 256, 384, 512, 768, 1024]
        printed = 0
        for count in candidates:
            if size < count * 15:
                continue
            offset, length = best_run(data, payload, payload + size, count)
            if length >= count * 0.9:
                print("  vertex count %-5d -> run of %d unit-like triples at +%d"
                      % (count, length, offset - payload))
                printed += 1
        if printed == 0:
            # Report the single longest run regardless of count, for reference.
            offset, length = best_run(data, payload, payload + size, 0)
            print("  no candidate count produced a run of 90%% or more")
            print("  longest unit-like byte run overall: %d triples at +%d"
                  % (length, offset - payload if offset >= 0 else -1))
        print("")


if __name__ == "__main__":
    main()
