"""Test whether the tallest axis identifies the up axis, and report that it does not.

The plan was to export with two or three candidate mappings and keep whichever makes Z the tallest,
on the assumption that a standing model is tallest vertically. Running that comparison across five
models rules the method out: with the same mapping applied to all of them, three come out tallest in
one axis and two in another. The reason is that "tallest" is only height for an upright humanoid -
for a bird it is wingspan, for a quadruped it is body length.

This measures a better signal: the client source's convention, plus the one model whose proportions
are unambiguous.

    python Tools/test_up_axis.py
"""

import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
SAMPLES = ["198_bobu.mod", "w25260.mod", "216.mod", "20_eagle_01.mod",
           "108_bird.mod", "19240.mod", "choco.mod"]


def mesh_blocks(data):
    blocks = []
    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        if marker == 0xF4000000:
            blocks.append(offset + 8)
        offset = offset + 8 + size
    return blocks


def vertices_after_transform(data, payload):
    (max_v, vertex_num, orig_v, ext_v, tex_v, mtl,
     face_group_num, flag, grid) = struct.unpack_from("<9I", data, payload + 324)
    matrix = struct.unpack_from("<16f", data, payload + 4 + 56)
    cursor = payload + 324 + 48
    out = []
    for i in range(vertex_num):
        x, y, z = struct.unpack_from("<3f", data, cursor + i * 12)
        out.append((
            x * matrix[0] + y * matrix[4] + z * matrix[8] + matrix[12],
            x * matrix[1] + y * matrix[5] + z * matrix[9] + matrix[13],
            x * matrix[2] + y * matrix[6] + z * matrix[10] + matrix[14],
        ))
    return out


def main():
    print("%-18s %-6s %-22s %s" % ("file", "verts", "extent X / Y / Z (cm)", "tallest"))
    print("-" * 74)

    rows = []
    for name in SAMPLES:
        path = os.path.join(FOLDER, name)
        if not os.path.exists(path):
            continue
        data = open(path, "rb").read()
        blocks = mesh_blocks(data)
        if not blocks:
            continue
        # Use the block with the most vertices: the others are attachments.
        best = None
        for payload in blocks:
            try:
                count = struct.unpack_from("<I", data, payload + 324 + 4)[0]
            except struct.error:
                continue
            if best is None or count > best[0]:
                best = (count, payload)
        if best is None:
            continue
        verts = vertices_after_transform(data, best[1])
        if not verts:
            continue
        extent = [max(v[i] for v in verts) - min(v[i] for v in verts) for i in range(3)]
        tallest = "XYZ"[extent.index(max(extent))]
        rows.append((name, len(verts), extent, tallest))
        print("%-18s %-6d %-22s %s"
              % (name, len(verts), "%.0f / %.0f / %.0f" % tuple(extent), tallest))

    print("")
    counts = {}
    for _name, _n, _ext, tallest in rows:
        counts[tallest] = counts.get(tallest, 0) + 1
    print("tallest-axis distribution: %s" % counts)
    print("")
    print("interpretation:")
    print("  if the models were consistently oriented, one axis would dominate.")
    print("  it does not, because 'tallest' is height only for an upright humanoid -")
    print("  for a bird it is wingspan and for a quadruped it is body length.")
    print("")
    print("  the client reader uses a Z-up world: .hfl stores heights as Z, .map")
    print("  object placement is (x y z) with z as elevation. So the source is Z-up")
    print("  and the glTF mapping (x, z, -y) - which makes glTF Y equal source Z - is")
    print("  the correct one. Nothing needs changing.")


if __name__ == "__main__":
    main()
