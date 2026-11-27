"""Walk the mod container without requiring a fixed marker value.

The layout has been right since the eight-byte header was measured; the check that broke it was
requiring every block to begin with 0x00F00000. Block types carry different marker values, so the
marker is a type tag, not a constant. Walking on size alone reproduces the offsets recorded in an
earlier session exactly:

    28 + 8 + 1444 = 1480   a material block, then the first bone
    1480 + 8 + 588 = 2076
    2076 + 8 + 592 = 2676
    2676 + 8 + 592 = 3276
    3276 + 8 + 592 = 3876  the mesh

    python Tools/parse_mod.py [path ...]
"""

import struct
import sys

DEFAULT = [
    "C:/Users/tk/Desktop/moxiang-study/resources/mod/w25260.mod",
    "C:/Users/tk/Desktop/moxiang-study/resources/mod/jp03_dht00.mod",
]

HEADER = 8


def read_name(data, offset, length=32):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end >= 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def find_name(data, payload, size):
    """A printable run inside the payload, taken as the block's name."""
    best = ""
    end = min(payload + min(size, 128), len(data) - 4)
    for probe in range(payload, end):
        run = data[probe:probe + 16]
        if len(run) < 4:
            break
        printable = sum(1 for byte in run if 32 <= byte < 127 or byte >= 0x80)
        if printable >= len(run) - 1:
            candidate = read_name(data, probe, 24)
            if len(candidate) > len(best) and candidate.strip():
                best = candidate
    return best


def parse(path):
    data = open(path, "rb").read()
    if len(data) < 40:
        print("%s: too short" % path)
        return

    version, total, materials, meshes, _a, _b, bones = struct.unpack_from("<7I", data, 0)

    print("=" * 78)
    print("%s" % path.rsplit("/", 1)[-1])
    print("  %d bytes  version=%d  objects=%d  materials=%d  meshes=%d  bones=%d"
          % (len(data), version, total, materials, meshes, bones))
    print("  check: materials + bones = %d, objects = %d" % (materials + bones, total))
    print("")

    offset = 28
    index = 0
    blocks = []
    while offset + HEADER + 4 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + HEADER + size > len(data) + 4:
            print("  implausible size %d at %d; stopping" % (size, offset))
            break
        payload = offset + HEADER
        kind = "MESH" if meshes and index == materials + bones else "BONE"
        if index < materials:
            kind = "MATERIAL"
        name = find_name(data, payload, size)
        blocks.append((offset, marker, size, payload, kind, name))
        print("  [%2d] @%-6d %-8s marker=0x%08X size=%-6d name=%r"
              % (index, offset, kind, marker, size, name))
        offset = payload + size
        index += 1

    print("")
    print("  %d blocks, ended at %d of %d bytes, tail %d bytes"
          % (len(blocks), offset, len(data), len(data) - offset))
    print("")

    for start, marker, size, payload, kind, name in blocks:
        if kind != "MESH" or payload + 36 > len(data):
            continue
        header = struct.unpack_from("<9i", data, payload)
        print("  MESH '%s' payload header (+0 .. +32):" % name)
        labels = ["vertex_count", "vertex_count_b", "index_count", "influences",
                  "vertex_count_c", "flag_e", "flag_f", "value_g", "value_h"]
        for i, label in enumerate(labels):
            print("    +%-2d %-16s %d" % (i * 4, label, header[i]))
        print("")


def main():
    for path in sys.argv[1:] or DEFAULT:
        try:
            parse(path)
        except OSError as error:
            print("%s: %s" % (path, error))


if __name__ == "__main__":
    main()
