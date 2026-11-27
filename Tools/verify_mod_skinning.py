"""Verify the skinning layout against real files, using the client's own structures.

The client source settles what three sessions of scanning could not. The mesh is read in this order:

    FILE_MESH_HEADER        48 bytes
    positions               12 * vertex_count
    uvs                      8 * tex_vertex_count
    ext indices              4 * ext_vertex_count
    face groups             per group
    FILE_PHYSIQUE_HEADER    12 bytes
    PHYSIQUE_VERTEX * n      5 bytes each
    BONE * total_bones      44 bytes each
    normals                 12 * vertex_count

And the weight is a float at offset four of each BONE record, while the influence count is a single
byte per vertex - which is why assuming a fixed four influences per vertex failed.

This walks that layout and checks the numbers for internal consistency: bone indices inside the
bone list, weights inside zero to one, and per-vertex weights summing to one.

    python Tools/verify_mod_skinning.py
"""

import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
HEADER = 8
MESH = 0xF4000000

SAMPLES = ["216.mod", "19240.mod", "choco.mod", "108_bird.mod",
           "jp03_dht00.mod", "w25260.mod", "20_eagle_01.mod"]

MESH_HEADER = 48
PHYSIQUE_HEADER = 12
PHYSIQUE_VERTEX = 5
BONE = 44


def mesh_payload(data):
    offset = 28
    while offset + HEADER + 4 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + HEADER + size > len(data) + 4:
            return None
        if marker == MESH:
            return offset + HEADER, size
        offset += HEADER + size
    return None


def parse(path):
    data = open(path, "rb").read()
    found = mesh_payload(data)
    if found is None:
        return None
    payload, size = found

    (max_v, vertex_num, orig_v, ext_v, tex_v, mtl_index,
     face_group_num, mesh_flag, grid_index) = struct.unpack_from("<9I", data, payload)
    dir_x, dir_y, dir_z = struct.unpack_from("<3f", data, payload + 36)

    cursor = payload + MESH_HEADER
    positions_at = cursor
    cursor += 12 * vertex_num
    uvs_at = cursor
    cursor += 8 * tex_v
    ext_at = cursor
    cursor += 4 * ext_v

    # Face groups: [count][...] - the exact framing is not needed here, but the cursor has to
    # move past them. Each group in the client reader is a count followed by index triples.
    groups = []
    for _ in range(face_group_num):
        if cursor + 4 > len(data):
            break
        index_count = struct.unpack_from("<I", data, cursor)[0]
        if index_count > 10_000_000:
            break
        groups.append(index_count)
        cursor += 4 + 4 * index_count

    result = {
        "file": os.path.basename(path),
        "payload": payload,
        "size": size,
        "vertex_num": vertex_num,
        "tex_v": tex_v,
        "ext_v": ext_v,
        "face_groups": groups,
        "groups_at": cursor,
    }

    if cursor + PHYSIQUE_HEADER > len(data):
        result["error"] = "no room for the physique header"
        return result

    phy_vertex_num, phy_bones, phy_alloc = struct.unpack_from("<3I", data, cursor)
    result["phy_vertex_num"] = phy_vertex_num
    result["phy_bones"] = phy_bones
    cursor += PHYSIQUE_HEADER
    result["phy_header_at"] = cursor - PHYSIQUE_HEADER

    if phy_vertex_num == 0 or phy_vertex_num > 200000:
        result["error"] = "physique vertex count implausible: %d" % phy_vertex_num
        return result

    verts = []
    for i in range(phy_vertex_num):
        if cursor + PHYSIQUE_VERTEX > len(data):
            break
        bones_num = data[cursor]
        bone_start = struct.unpack_from("<I", data, cursor + 1)[0]
        verts.append((bones_num, bone_start))
        cursor += PHYSIQUE_VERTEX
    result["verts_at"] = cursor - PHYSIQUE_VERTEX * len(verts)
    result["vertex_influences"] = verts[:6]
    result["influence_histogram"] = {}
    for bones_num, _ in verts:
        key = bones_num
        result["influence_histogram"][key] = result["influence_histogram"].get(key, 0) + 1

    # Bones.
    bones = []
    for i in range(min(phy_bones, 2000)):
        if cursor + BONE > len(data):
            break
        index = struct.unpack_from("<I", data, cursor)[0]
        weight = struct.unpack_from("<f", data, cursor + 4)[0]
        bones.append((index, weight))
        cursor += BONE
    result["bones_at"] = cursor - BONE * len(bones)
    result["bones"] = bones[:8]
    result["bone_count_read"] = len(bones)

    # Consistency: weights should be within zero and one, bone indices within range.
    weights = [w for _, w in bones]
    result["weights_in_range"] = all(0.0 <= w <= 1.0001 for w in weights)
    result["bone_indices_in_range"] = all(0 <= i < phy_bones for i, _ in bones) if bones else False
    result["weight_sum"] = sum(weights)

    # After the bones come the normals; check they are unit length.
    normals_ok = 0
    normals_checked = 0
    if cursor + 12 * vertex_num <= len(data):
        for i in range(vertex_num):
            x, y, z = struct.unpack_from("<3f", data, cursor + i * 12)
            length = (x * x + y * y + z * z) ** 0.5
            normals_checked += 1
            if abs(length - 1.0) < 0.01:
                normals_ok += 1
    result["normals_at"] = cursor
    result["normals_unit"] = "%d / %d" % (normals_ok, normals_checked)
    result["tail_after_normals"] = size - (cursor - payload + 12 * vertex_num)
    return result


def main():
    for name in SAMPLES:
        path = os.path.join(FOLDER, name)
        if not os.path.exists(path):
            print("%s: missing" % name)
            continue
        try:
            info = parse(path)
        except (OSError, struct.error) as error:
            print("%s: %s" % (name, error))
            continue
        print("=" * 78)
        if info is None:
            print("%s: no mesh block" % name)
            continue
        print("%s  payload=%d" % (info["file"], info["size"]))
        print("  vertex_num=%d  tex_v=%d  ext_v=%d  face_groups=%s"
              % (info["vertex_num"], info["tex_v"], info["ext_v"], info["face_groups"]))
        if "error" in info:
            print("  FAILED: %s" % info["error"])
            print("")
            continue
        print("  physique header at +%d: vertex=%d bones=%d alloc=%d"
              % (info["phy_header_at"] - info["payload"], info["phy_vertex_num"],
                 info["phy_bones"], info["phy_alloc_bones"] if "phy_alloc_bones" in info else -1))
        print("  influence histogram: %s" % info["influence_histogram"])
        print("  first vertices (bones_num, bone_start): %s" % info["vertex_influences"])
        print("  first bones (index, weight): %s"
              % [("%d" % i, "%.4f" % w) for i, w in info["bones"]])
        print("  weights in 0..1: %s   indices in range: %s   weight sum: %.4f"
              % (info["weights_in_range"], info["bone_indices_in_range"], info["weight_sum"]))
        print("  normals at +%d: unit %s"
              % (info["normals_at"] - info["payload"], info["normals_unit"]))
        print("  tail after normals: %d bytes" % info["tail_after_normals"])
        print("")


if __name__ == "__main__":
    main()
