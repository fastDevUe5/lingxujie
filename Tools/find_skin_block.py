"""Search the character .mod payload for the skin weight block by its arithmetic signature.

The partial conclusion is that characters declare four influences per vertex while props declare
zero. If that is right, somewhere in the file is a run of vertexcount times four weights, and
weights for one vertex must sum to a constant - 255 if stored as bytes, or 1.0 if stored as floats,
or 65535 if stored as words.

Rather than guessing offsets, this scans every offset and every plausible layout, and reports where
the sum-to-constant property holds. A real weight block is not just arithmetic that works once; it
works for every vertex group in the run.

    python Tools/find_skin_block.py
"""

import struct
import sys


def load(path):
    return open(path, "rb").read()


def try_layout(data, start, count, per_vertex, value_size, fmt, target, tolerance):
    """Check whether count/per_vertex groups of per_vertex values each sum to target."""
    group_bytes = per_vertex * value_size
    need = (count // per_vertex) * group_bytes
    if start + need > len(data):
        return 0.0

    groups = count // per_vertex
    good = 0
    for g in range(groups):
        offset = start + g * group_bytes
        values = struct.unpack_from("<" + fmt * per_vertex, data, offset)
        if abs(sum(values) - target) <= tolerance:
            good += 1
    return good / float(groups) if groups else 0.0


def scan(path, vertex_count, influences, bone_count):
    data = load(path)
    print("%s: %d bytes, %d vertices, %d influences, %d bones"
          % (path.rsplit("/", 1)[-1], len(data), vertex_count, influences, bone_count))
    print("")

    if influences == 0:
        print("this file declares zero influences - it is a prop, not a character")
        return

    layouts = [
        ("u8 weights, 255", 1, "B", 255, 0),
        ("u16 weights, 65535", 2, "H", 65535, 0),
        ("f32 weights, 1.0", 4, "f", 1.0, 0.01),
    ]

    print("looking for a run where every %d-value group sums to a constant:" % influences)
    print("%-22s %-8s %-8s %s" % ("layout", "at", "fraction", "note"))
    print("-" * 78)

    best = []
    for label, value_size, fmt, target, tolerance in layouts:
        group_bytes = influences * value_size
        run_bytes = vertex_count * group_bytes
        if run_bytes > len(data):
            continue
        # Step by one byte: a wrong alignment would otherwise be invisible.
        for start in range(0, len(data) - run_bytes + 1):
            fraction = try_layout(data, start, vertex_count, influences,
                                  value_size, fmt, target, tolerance)
            if fraction >= 0.999:
                best.append((fraction, label, start, run_bytes))
                print("%-22s %-8d %-8.3f run of %d bytes"
                      % (label, start, fraction, run_bytes))

    print("")
    if not best:
        print("no exact run found.")
        print("")
        print("That is informative: it means the weights are not stored as a plain")
        print("sum-to-constant run at this vertex count, so one of these is wrong -")
        print("  the influence count, the vertex count, or the assumption that weights")
        print("  are normalised in this file.")
        return

    for fraction, label, start, run_bytes in best[:6]:
        print("candidate: %s at offset %d, %d bytes" % (label, start, run_bytes))
        # Show the first few groups so the structure is visible.
        print("  first groups:")
        for g in range(min(4, vertex_count // influences)):
            offset = start + g * influences * (1 if "u8" in label else
                                              2 if "u16" in label else 4)
            if "u8" in label:
                values = list(data[offset:offset + influences])
            elif "u16" in label:
                values = list(struct.unpack_from("<" + "H" * influences, data, offset))
            else:
                values = list(struct.unpack_from("<" + "f" * influences, data, offset))
            print("    %s" % values)
        print("")


def mod_header(path):
    """Read the object header fields this script needs, using the verified walk."""
    data = load(path)
    if len(data) < 32:
        return None
    # FILE_SCENE_HEADER: 4 bytes magic, then counts.
    materials, bones, meshes = struct.unpack_from("<III", data, 8) if len(data) >= 20 else (0, 0, 0)
    offset = 28
    # Material blocks, then object blocks; size excludes the 8-byte header.
    for _ in range(materials):
        if offset + 8 > len(data):
            return None
        size = struct.unpack_from("<I", data, offset)[0]
        offset += size + 8
    for _ in range(bones + meshes):
        if offset + 8 > len(data):
            return None
        kind = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if kind == 4:  # mesh
            payload = offset + 8
            if payload + 36 <= len(data):
                header = struct.unpack_from("<9i", data, payload)
                return {
                    "vertex_count": header[0],
                    "influences": header[3],
                    "bone_count": bones,
                }
        offset += size + 8
    return None


def main():
    candidates = sys.argv[1:] or [
        "C:/Users/tk/Desktop/moxiang-study/resources/mod/w25260.mod",
        "C:/Users/tk/Desktop/moxiang-study/resources/mod/jp03_dht00.mod",
    ]
    for path in candidates:
        try:
            info = mod_header(path)
        except OSError:
            print("%s: cannot read" % path)
            continue
        if info is None:
            print("%s: header walk failed" % path)
            continue
        scan(path, info["vertex_count"], info["influences"], info["bone_count"])
        print("=" * 78)


if __name__ == "__main__":
    main()
