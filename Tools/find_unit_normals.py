"""Find the geometry inside a mesh payload by its arithmetic signature.

Normals are unit length, which no other float triple in a mesh should be. Scanning for the longest
run of triples whose length is 1.0 locates the normal array without knowing any offset, and from
there the vertex positions follow, because they have the same count.

That is more reliable than reading a header whose position keeps turning out to be wrong.

    python Tools/find_unit_normals.py
"""

import math
import struct

SAMPLES = [
    ("w25260", "C:/Users/tk/Desktop/moxiang-study/resources/mod/w25260.mod", 15872, 1620),
    ("jp03_dht00", "C:/Users/tk/Desktop/moxiang-study/resources/mod/jp03_dht00.mod", 3884, 1272),
]


def is_unit(data, offset, tolerance=0.001):
    try:
        x, y, z = struct.unpack_from("<3f", data, offset)
    except struct.error:
        return False
    if any(math.isnan(value) or math.isinf(value) for value in (x, y, z)):
        return False
    return abs(math.sqrt(x * x + y * y + z * z) - 1.0) <= tolerance


def longest_run(data, start, end):
    """Longest consecutive run of unit triples, in floats."""
    best_start = -1
    best_count = 0
    offset = start
    while offset + 12 <= end:
        if is_unit(data, offset):
            run_start = offset
            count = 0
            while offset + 12 <= end and is_unit(data, offset):
                count += 1
                offset += 12
            if count > best_count:
                best_count = count
                best_start = run_start
        else:
            offset += 4
    return best_start, best_count


def main():
    for label, path, payload, size in SAMPLES:
        data = open(path, "rb").read()
        end = min(payload + size, len(data))
        print("=" * 78)
        print("%s  mesh payload %d..%d (%d bytes)" % (label, payload, end, end - payload))

        start, count = longest_run(data, payload, end)
        if start < 0:
            print("  no unit-length triples found")
            print("")
            continue

        print("  longest unit-normal run: %d triples at +%d (absolute %d)"
              % (count, start - payload, start))
        print("  that run occupies %d bytes" % (count * 12))

        # Positions follow the normals: same count, immediately after.
        positions_at = start + count * 12
        if positions_at + count * 12 <= end:
            print("  positions would follow at +%d, covering %d bytes"
                  % (positions_at - payload, count * 12))
            remaining = end - (positions_at + count * 12)
            print("  bytes left after normals+positions: %d" % remaining)
            if count:
                print("  that is %.2f bytes per vertex" % (remaining / float(count)))
            # Show the first three normals and positions for a sanity read.
            print("  first normals:")
            for i in range(min(3, count)):
                values = struct.unpack_from("<3f", data, start + i * 12)
                print("    %s" % ["%.4f" % v for v in values])
            print("  first positions:")
            for i in range(min(3, count)):
                values = struct.unpack_from("<3f", data, positions_at + i * 12)
                print("    %s" % ["%.2f" % v for v in values])
        else:
            print("  not enough bytes after the normals for positions")

        # Whatever precedes the normals is the header.
        header_bytes = start - payload
        print("  header length before normals: %d bytes" % header_bytes)
        if header_bytes >= 4:
            words = struct.unpack_from("<%di" % (header_bytes // 4), data, payload)
            print("    as ints:  %s" % list(words[:12]))
            floats = struct.unpack_from("<%df" % (header_bytes // 4), data, payload)
            print("    as floats: %s" % ["%.3f" % v for v in floats[:12]])
        print("")


if __name__ == "__main__":
    main()
