"""Look for skin weights in a real character model, where they must exist.

The four-bone prop had eight vertices and index values from zero to seven, which is a static mesh
indexing its own vertices - not a skinned one. Skinning only becomes necessary when a mesh follows
tens of bones, so this reads a model with thirty-eight of them.

The test is arithmetic rather than pattern matching. Per-vertex skin data has a signature that
nothing else produces: bone indices that stay below the bone count, and weights that sum to one
for each vertex. If a run of numbers satisfies both, it is skinning.

    python Tools/find_mod_skin_weights.py
"""

import glob
import os
import struct

MOD_DIR = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
BASE_OBJECT_SIZE = 324


def pick_sample():
    """A small character model - many bones, few objects, so the mesh data is easy to isolate."""
    best = None
    for path in sorted(glob.glob(os.path.join(MOD_DIR, "*.mod")), key=os.path.getsize):
        try:
            data = open(path, "rb").read()
        except OSError:
            continue
        if len(data) < 64:
            continue
        fields = struct.unpack_from("<7I", data, 0)
        bones, meshes, objects = fields[6], fields[3], fields[1]
        if 30 <= bones <= 60 and meshes >= 1:
            if best is None or len(data) < best[1]:
                best = (path, len(data), fields)
            # smallest is enough; the list is sorted by size already
            break
    return best


def objects(data):
    version, object_count, material_count = struct.unpack_from("<3I", data, 0)
    offset = 28
    for _ in range(material_count):
        size = struct.unpack_from("<I", data, offset + 4)[0]
        offset += size + 8
    out = []
    for _ in range(object_count):
        otype, osize = struct.unpack_from("<2I", data, offset)
        out.append((otype, osize, offset))
        offset += osize + 8
    return out


def scan_for_weights(after, bone_count):
    """Find a run where u16 indices stay under bone_count and float weights sum to one.

    Tries the two plausible layouts: (index u16, weight f32) contiguous, and two parallel arrays
    of indices then weights.
    """
    findings = []

    # Layout A: interleaved pairs of (u16 index, padding u16, f32 weight) = 8 bytes.
    for stride in (8, 6, 4):
        for start in range(0, max(0, len(after) - stride * 4), 2):
            values = []
            valid = True
            for i in range(4):
                base = start + i * stride
                if base + stride > len(after):
                    valid = False
                    break
                index = struct.unpack_from("<H", after, base)[0]
                if index >= bone_count:
                    valid = False
                    break
                if stride == 8:
                    weight = struct.unpack_from("<f", after, base + 4)[0]
                elif stride == 6:
                    weight = struct.unpack_from("<f", after, base + 2)[0]
                else:
                    weight = 1.0
                if not (0.0 <= weight <= 1.001 or stride == 4):
                    valid = False
                    break
                values.append((index, weight))
            if not valid or not values:
                continue
            if stride in (8, 6):
                total = sum(w for _, w in values)
                if 0.9 <= total <= 1.1:
                    findings.append((stride, start, values, total))
                    break

    return findings[:5]


def main():
    sample = pick_sample()
    if sample is None:
        print("no character model found")
        return
    path, size, fields = sample
    version, object_count, material_count, mesh_count, lights, cameras, bones = fields
    print("%s  %d bytes  bones=%d meshes=%d objects=%d"
          % (os.path.basename(path), size, bones, mesh_count, object_count))
    data = open(path, "rb").read()

    for otype, osize, offset in objects(data):
        if (otype >> 24) != 0xF4:
            continue
        after = data[offset + 8 + BASE_OBJECT_SIZE:offset + 8 + osize]
        print("mesh payload after base: %d bytes" % len(after))
        print("")

        print("leading words:")
        for i in range(0, 36, 4):
            print("  +%-3d %d" % (i, struct.unpack_from("<I", after, i)[0]))
        print("")

        found = scan_for_weights(after, bones)
        if found:
            print("SKIN WEIGHT CANDIDATES:")
            for stride, start, values, total in found:
                print("  stride %d at +%d, weight sum %.4f" % (stride, start, total))
                for index, weight in values:
                    print("      bone %-3d weight %.4f" % (index, weight))
        else:
            print("no interleaved (index, weight) run found with the layouts tried")

        print("")
        print("byte windows with many small values (possible index arrays):")
        for start in range(0, len(after), 128):
            chunk = after[start:start + 128]
            small = sum(1 for b in chunk if 0 < b < 20)
            if small > 20:
                print("  +%-5d small=%-3d  %s"
                      % (start, small, " ".join("%02x" % b for b in chunk[:20])))


if __name__ == "__main__":
    main()
