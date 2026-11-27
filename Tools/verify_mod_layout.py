"""Verify the full mesh layout now that every structure in the chain has a measured size.

The client source gave the read order; the structures give the sizes:

    FILE_BASE_OBJECT_HEADER   324 bytes   (index 4, NODE_TM 184, children 4, parent 4, name 128)
    FILE_MESH_HEADER           48 bytes
    positions                  12 * vertex_count
    uvs                         8 * tex_vertex_count
    ext indices                 4 * ext_vertex_count
    face groups                per group
    FILE_PHYSIQUE_HEADER       12 bytes
    PHYSIQUE_VERTEX * n         5 bytes each
    BONE * bone_count          44 bytes each
    normals                    12 * vertex_count

The check that matters: if this is the real layout, the normals at the end must be unit length. That
single test validates every offset upstream of it at once, because a single mistake anywhere moves
the normals somewhere they are not.

    python Tools/verify_mod_layout.py
"""

import math
import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
HEADER = 8
MESH_MARKER = 0xF4000000

BASE_OBJECT = 324
MESH_HEADER = 48
PHYSIQUE_HEADER = 12
PHYSIQUE_VERTEX = 5
BONE = 44

SAMPLES = ["216.mod", "19240.mod", "choco.mod", "108_bird.mod",
           "jp03_dht00.mod", "w25260.mod", "20_eagle_01.mod", "11000.mod"]


def mesh_payload(data):
    offset = 28
    while offset + HEADER + 4 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + HEADER + size > len(data) + 4:
            return None
        if marker == MESH_MARKER:
            return offset + HEADER, size
        offset += HEADER + size
    return None


def describe(path):
    data = open(path, "rb").read()
    found = mesh_payload(data)
    if found is None:
        return {"file": os.path.basename(path), "error": "no mesh block"}
    payload, size = found
    out = {"file": os.path.basename(path), "payload": payload, "size": size}

    # Base object header: the name is the readable field.
    raw_name = data[payload + 200:payload + 200 + 128]
    end = raw_name.find(b"\x00")
    if end >= 0:
        raw_name = raw_name[:end]
    try:
        out["object_name"] = raw_name.decode("gbk")
    except UnicodeDecodeError:
        out["object_name"] = raw_name.decode("latin-1", errors="replace")

    cursor = payload + BASE_OBJECT
    (max_v, vertex_num, orig_v, ext_v, tex_v, mtl_index,
     face_group_num, mesh_flag, grid_index) = struct.unpack_from("<9I", data, cursor)
    out.update({
        "vertex_num": vertex_num,
        "tex_v": tex_v,
        "ext_v": ext_v,
        "face_group_num": face_group_num,
        "mtl_index": mtl_index,
        "max_v": max_v,
    })
    out["dir"] = struct.unpack_from("<3f", data, cursor + 36)
    cursor += MESH_HEADER

    if not (0 < vertex_num < 500000):
        out["error"] = "vertex count implausible: %d" % vertex_num
        return out

    out["positions_at"] = cursor - payload
    cursor += 12 * vertex_num
    out["uvs_at"] = cursor - payload
    cursor += 8 * tex_v
    out["ext_at"] = cursor - payload
    cursor += 4 * ext_v

    # Face groups: FILE_FACE_GROUP_HEADER is seven words, then that many faces as word triples,
    # then two optional light-UV arrays of eight bytes each.
    groups = []
    for _ in range(face_group_num):
        if cursor + 28 > len(data):
            break
        (mtl, index, faces_num, max_faces, vindex_num,
         light_uv1, light_uv2) = struct.unpack_from("<7I", data, cursor)
        groups.append((faces_num, light_uv1, light_uv2))
        cursor += 28
        cursor += 2 * faces_num * 3
        cursor += 8 * light_uv1
        cursor += 8 * light_uv2
    out["face_groups"] = groups[:8]

    if cursor + PHYSIQUE_HEADER > len(data):
        out["error"] = "ran out of data at the physique header"
        return out

    phy_verts, phy_bones, phy_alloc = struct.unpack_from("<3I", data, cursor)
    out.update({"phy_verts": phy_verts, "phy_bones": phy_bones, "phy_alloc": phy_alloc})
    out["physique_at"] = cursor - payload
    cursor += PHYSIQUE_HEADER

    if phy_verts > 500000:
        out["error"] = "physique vertex count implausible: %d" % phy_verts
        return out

    influences = []
    for _ in range(phy_verts):
        if cursor + PHYSIQUE_VERTEX > len(data):
            break
        influences.append((data[cursor], struct.unpack_from("<I", data, cursor + 1)[0]))
        cursor += PHYSIQUE_VERTEX
    out["vertices_at"] = cursor - payload - PHYSIQUE_VERTEX * len(influences)
    out["influence_sample"] = influences[:6]
    histogram = {}
    for bones_num, _ in influences:
        histogram[bones_num] = histogram.get(bones_num, 0) + 1
    out["influence_histogram"] = dict(sorted(histogram.items())[:8])

    weights = []
    indices = []
    for _ in range(min(phy_bones, 5000)):
        if cursor + BONE > len(data):
            break
        indices.append(struct.unpack_from("<I", data, cursor)[0])
        weights.append(struct.unpack_from("<f", data, cursor + 4)[0])
        cursor += BONE
    out["bones_at"] = cursor - payload - BONE * len(weights)
    out["bone_sample"] = list(zip(indices[:6], ["%.4f" % w for w in weights[:6]]))
    out["bone_count"] = len(weights)
    out["weights_ok"] = all(0.0 <= w <= 1.0001 for w in weights) if weights else False
    out["indices_ok"] = all(0 <= i < phy_bones for i in indices) if indices else False

    # The payoff test: are the trailing vectors unit length?
    out["normals_at"] = cursor - payload
    unit = 0
    total = 0
    for i in range(min(vertex_num, 4000)):
        if cursor + (i + 1) * 12 > len(data):
            break
        x, y, z = struct.unpack_from("<3f", data, cursor + i * 12)
        length = math.sqrt(x * x + y * y + z * z)
        total += 1
        if abs(length - 1.0) < 0.02:
            unit += 1
    out["normals_unit"] = "%d / %d" % (unit, total)
    out["normals_ok"] = total > 0 and unit >= total * 0.9
    out["consumed"] = cursor - payload + 12 * vertex_num
    out["tail"] = size - out["consumed"]
    return out


def main():
    for name in SAMPLES:
        path = os.path.join(FOLDER, name)
        if not os.path.exists(path):
            continue
        try:
            info = describe(path)
        except (OSError, struct.error) as error:
            print("%s: %s" % (name, error))
            continue

        print("=" * 80)
        print("%s   payload=%d" % (info["file"], info["size"]))
        if "error" in info:
            print("  FAILED: %s" % info["error"])
            continue
        print("  object name        %r" % info["object_name"])
        print("  vertex_num=%-6d tex_v=%-6d ext_v=%-6d groups=%s"
              % (info["vertex_num"], info["tex_v"], info["ext_v"], info["face_groups"]))
        print("  physique: verts=%-5d bones=%-4d alloc=%-4d at +%d"
              % (info["phy_verts"], info["phy_bones"], info["phy_alloc"], info["physique_at"]))
        print("  influences         %s" % info["influence_histogram"])
        print("  bone sample        %s" % info["bone_sample"])
        print("  weights 0..1: %-5s  indices in range: %s"
              % (info["weights_ok"], info["indices_ok"]))
        print("  normals at +%-6d unit %s   -> LAYOUT %s"
              % (info["normals_at"], info["normals_unit"],
                 "CONFIRMED" if info["normals_ok"] else "wrong"))
        print("  tail after normals %d bytes" % info["tail"])
        print("")


if __name__ == "__main__":
    main()
