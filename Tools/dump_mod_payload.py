"""Dump the whole mesh payload and identify where positions, normals and skin weights sit.

The walk now reads correctly once the block size is understood to exclude its own eight-byte
header: four bones of 588-592 bytes, then one mesh of 1272. Inside the mesh, the first floats
after the base header form a unit vector, so normals start there.

What remains is finding the skin weights, if they exist. With four bones in this model, weights
would appear either as runs of small integers (bone index) paired with small floats, or as an
array of (index, weight) pairs per vertex. This prints the payload in labelled blocks so the
transition from normals to positions to any weight array can be seen directly.

    python Tools/dump_mod_payload.py
"""

import glob
import os
import struct

MOD_DIR = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
BASE_OBJECT_SIZE = 324


def pick_sample():
    best = None
    for path in sorted(glob.glob(os.path.join(MOD_DIR, "*.mod")), key=os.path.getsize):
        try:
            data = open(path, "rb").read()
        except OSError:
            continue
        if len(data) < 40:
            continue
        fields = struct.unpack_from("<7I", data, 0)
        if fields[6] >= 2 and fields[3] >= 1:
            if best is None or len(data) < best[1]:
                best = (path, len(data), fields)
    return best


def objects(data):
    version, object_count, material_count = struct.unpack_from("<3I", data, 0)
    offset = 28
    for _ in range(material_count):
        msize = struct.unpack_from("<I", data, offset + 4)[0]
        offset += msize + 8
    out = []
    for _ in range(object_count):
        otype, osize = struct.unpack_from("<2I", data, offset)
        out.append((otype, osize, offset))
        offset += osize + 8
    return out


def main():
    sample = pick_sample()
    if sample is None:
        print("no suitable model")
        return
    path, size, fields = sample
    print("%s  %d bytes  objects=%d materials=%d meshes=%d bones=%d"
          % (os.path.basename(path), size, fields[1], fields[2], fields[3], fields[6]))
    data = open(path, "rb").read()

    for otype, osize, offset in objects(data):
        if (otype >> 24) != 0xF4:
            continue
        after = data[offset + 8 + BASE_OBJECT_SIZE:offset + 8 + osize]
        print("mesh payload after base: %d bytes" % len(after))
        print("")

        # Header words
        print("leading words:")
        for i in range(0, 36, 4):
            value = struct.unpack_from("<I", after, i)[0]
            as_float = struct.unpack_from("<f", after, i)[0]
            print("  +%-3d %10d   (as float %.4f)" % (i, value, as_float))
        print("")

        # Floats from +36, in groups of three, checking whether each triple is unit length.
        print("triples from +36 (|v| near 1.0 suggests normals, larger values suggest positions):")
        for group in range(0, 12):
            base = 36 + group * 12
            if base + 12 > len(after):
                break
            x, y, z = struct.unpack_from("<3f", after, base)
            length = (x * x + y * y + z * z) ** 0.5
            kind = "normal" if 0.9 < length < 1.1 else ("position" if length > 3 else "?")
            print("  #%-2d +%-4d  %9.4f %9.4f %9.4f   |v|=%-7.4f %s"
                  % (group, base, x, y, z, length, kind))
        print("")

        # Looking for weight-like data: bytes with small values in a dense run.
        print("byte histogram by 64-byte window (small bytes 1..19 could be bone indices):")
        for window_start in range(0, len(after), 64):
            chunk = after[window_start:window_start + 64]
            small = sum(1 for b in chunk if 0 < b < 20)
            zero = sum(1 for b in chunk if b == 0)
            if small > 8:
                print("  +%-4d small=%-3d zero=%-3d  %s"
                      % (window_start, small, zero,
                         " ".join("%02x" % b for b in chunk[:16])))
        print("")


if __name__ == "__main__":
    main()
