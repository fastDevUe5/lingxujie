"""Export a mod file to glTF, including skinning, so the engine can import it.

Every structure is now known from the client source and verified byte-exactly on four files, so this
is engineering rather than reverse engineering. The pieces:

    - node tree from dwParentObjectIndex, with 0xFFFFFFFF meaning root
    - transforms from NODE_TM, which is one hundred eighty-four bytes inside the base header
    - positions, normals, uvs and triangle indices
    - skin weights, where each vertex has a variable number of influences that must be padded to four

The padding is the only part that is not a straight copy: glTF requires exactly four joint and
weight entries per vertex, while the source allows one to three.

    python Tools/export_mod_gltf.py <mod path> [output path]
"""

import json
import math
import os
import struct
import sys

HEADER = 8
MESH_MARKER = 0xF4000000
BONE_MARKER = 0xF5000000

BASE_OBJECT = 324
MESH_HEADER = 48
FACE_GROUP_HEADER = 28
PHYSIQUE_HEADER = 12
PHYSIQUE_VERTEX = 5
BONE_SIZE = 44
ROOT_PARENT = 0xFFFFFFFF


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end >= 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def parse(path):
    """Return the object list with mesh and skin data, using the verified layout."""
    data = open(path, "rb").read()
    objects = []

    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + HEADER + size > len(data) + 4:
            break
        payload = offset + HEADER

        if marker in (BONE_MARKER, MESH_MARKER):
            entry = {
                "marker": marker,
                "index": struct.unpack_from("<I", data, payload)[0],
                "parent": struct.unpack_from("<I", data, payload + 192)[0],
                "children": struct.unpack_from("<I", data, payload + 188)[0],
                "name": read_name(data, payload + 196),
                "node_tm": struct.unpack_from("<13f", data, payload + 4),
            }
            if marker == MESH_MARKER:
                entry.update(read_mesh(data, payload))
            objects.append(entry)
        offset = payload + size

    return objects


def read_mesh(data, payload):
    cursor = payload + BASE_OBJECT
    (max_v, vertex_num, orig_v, ext_v, tex_v, mtl,
     face_group_num, flag, grid) = struct.unpack_from("<9I", data, cursor)
    cursor += MESH_HEADER

    positions = []
    for i in range(vertex_num):
        positions.append(struct.unpack_from("<3f", data, cursor + i * 12))
    cursor += 12 * vertex_num

    uvs = []
    for i in range(tex_v):
        uvs.append(struct.unpack_from("<2f", data, cursor + i * 8))
    cursor += 8 * tex_v

    cursor += 4 * ext_v

    triangles = []
    for _ in range(face_group_num):
        (g_mtl, g_index, faces_num, max_faces, vindex, light1, light2) = \
            struct.unpack_from("<7I", data, cursor)
        cursor += FACE_GROUP_HEADER
        for i in range(faces_num):
            triangles.append(struct.unpack_from("<3H", data, cursor + i * 6))
        cursor += 2 * faces_num * 3
        cursor += 8 * light1
        cursor += 8 * light2

    phy_verts, phy_bones, phy_alloc = struct.unpack_from("<3I", data, cursor)
    cursor += PHYSIQUE_HEADER

    influence_starts = []
    for i in range(phy_verts):
        bones_num = data[cursor]
        start = struct.unpack_from("<I", data, cursor + 1)[0]
        influence_starts.append((bones_num, start))
        cursor += PHYSIQUE_VERTEX

    bone_records = []
    for i in range(phy_bones):
        bone_index = struct.unpack_from("<I", data, cursor)[0]
        weight = struct.unpack_from("<f", data, cursor + 4)[0]
        bone_records.append((bone_index, weight))
        cursor += BONE_SIZE

    normals = []
    for i in range(vertex_num):
        normals.append(struct.unpack_from("<3f", data, cursor + i * 12))

    return {
        "vertex_num": vertex_num,
        "positions": positions,
        "uvs": uvs,
        "triangles": triangles,
        "influence_starts": influence_starts,
        "bone_records": bone_records,
        "normals": normals,
    }


def quaternion_from_axis_angle(axis, angle):
    length = math.sqrt(axis[0] ** 2 + axis[1] ** 2 + axis[2] ** 2)
    if length < 1e-8:
        return (0.0, 0.0, 0.0, 1.0)
    half = angle * 0.5
    s = math.sin(half) / length
    return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(half))


def build_gltf(objects, source_name):
    bones = [o for o in objects if o["marker"] == BONE_MARKER]
    meshes = [o for o in objects if o["marker"] == MESH_MARKER]
    if not meshes:
        raise ValueError("no mesh in this file")

    mesh = meshes[0]
    vertex_num = mesh["vertex_num"]

    # glTF coordinates: Y up, right handed, metres. The source is Z up, centimetres.
    def convert_position(p):
        return (p[0] * 0.01, p[2] * 0.01, -p[1] * 0.01)

    def convert_normal(n):
        return (n[0], n[2], -n[1])

    binary = bytearray()
    buffer_views = []
    accessors = []

    def add_view(raw, target=None):
        while len(binary) % 4:
            binary.append(0)
        view = {"buffer": 0, "byteOffset": len(binary), "byteLength": len(raw)}
        if target:
            view["target"] = target
        binary.extend(raw)
        buffer_views.append(view)
        return len(buffer_views) - 1

    def add_accessor(view, component_type, count, kind, extra=None):
        accessor = {
            "bufferView": view,
            "componentType": component_type,
            "count": count,
            "type": kind,
        }
        if extra:
            accessor.update(extra)
        accessors.append(accessor)
        return len(accessors) - 1

    # Positions.
    raw_positions = b"".join(struct.pack("<3f", *convert_position(p)) for p in mesh["positions"])
    pos_view = add_view(raw_positions, 34962)
    pos_min = [min(p[i] for p in [convert_position(q) for q in mesh["positions"]]) for i in range(3)]
    pos_max = [max(p[i] for p in [convert_position(q) for q in mesh["positions"]]) for i in range(3)]
    pos_acc = add_accessor(pos_view, 5126, vertex_num, "VEC3",
                           {"min": pos_min, "max": pos_max})

    # Normals.
    raw_normals = b"".join(struct.pack("<3f", *convert_normal(n)) for n in mesh["normals"])
    norm_view = add_view(raw_normals, 34962)
    norm_acc = add_accessor(norm_view, 5126, vertex_num, "VEC3")

    # UVs. glTF expects the origin at the top left, so V is flipped.
    raw_uvs = b"".join(struct.pack("<2f", u, 1.0 - v) for u, v in mesh["uvs"][:vertex_num])
    while len(raw_uvs) < vertex_num * 8:
        raw_uvs += struct.pack("<2f", 0.0, 0.0)
    uv_view = add_view(raw_uvs, 34962)
    uv_acc = add_accessor(uv_view, 5126, vertex_num, "VEC2")

    # Indices.
    flat = [index for tri in mesh["triangles"] for index in tri]
    raw_indices = b"".join(struct.pack("<H", i) for i in flat)
    index_view = add_view(raw_indices, 34963)
    index_acc = add_accessor(index_view, 5123, len(flat), "SCALAR")

    # Joints and weights, padded to four per vertex as glTF requires.
    joints = []
    weights = []
    starts = mesh["influence_starts"]
    records = mesh["bone_records"]
    for v in range(vertex_num):
        if v < len(starts):
            bones_num, bone_start = starts[v]
        else:
            bones_num, bone_start = 0, 0
        entry_joints = []
        entry_weights = []
        for k in range(bones_num):
            record_index = bone_start + k
            if 0 <= record_index < len(records):
                bone_index, weight = records[record_index]
                entry_joints.append(bone_index)
                entry_weights.append(weight)
        while len(entry_joints) < 4:
            entry_joints.append(0)
            entry_weights.append(0.0)
        total = sum(entry_weights)
        if total > 1e-6:
            entry_weights = [w / total for w in entry_weights]
        joints.append(entry_joints[:4])
        weights.append(entry_weights[:4])

    raw_joints = b"".join(struct.pack("<4H", *j) for j in joints)
    joint_view = add_view(raw_joints, 34962)
    joint_acc = add_accessor(joint_view, 5123, vertex_num, "VEC4")

    raw_weights = b"".join(struct.pack("<4f", *w) for w in weights)
    weight_view = add_view(raw_weights, 34962)
    weight_acc = add_accessor(weight_view, 5126, vertex_num, "VEC4")

    # Nodes: one per bone plus the mesh.
    nodes = []
    bone_order = sorted(bones, key=lambda b: b["index"])

    # Map source object index to glTF node index.
    node_of = {}
    for i, bone in enumerate(bone_order):
        node_of[bone["index"]] = i

    for i, bone in enumerate(bone_order):
        ang = bone["node_tm"][0]
        axis = bone["node_tm"][4:7]
        pos = bone["node_tm"][1:4]
        scale = bone["node_tm"][7:10]
        quat = quaternion_from_axis_angle(axis, ang)
        node = {
            "name": bone["name"] or ("bone_%d" % bone["index"]),
            "translation": [pos[0] * 0.01, pos[2] * 0.01, -pos[1] * 0.01],
            "rotation": [quat[0], quat[2], -quat[1], quat[3]],
            "scale": [scale[0], scale[2], scale[1]],
        }
        children = [node_of[b["index"]] for b in bone_order
                    if b["parent"] == bone["index"] and b["index"] in node_of]
        if children:
            node["children"] = children
        nodes.append(node)

    mesh_node = len(nodes)
    nodes.append({
        "name": mesh["name"] or "mesh",
        "mesh": 0,
        "skin": 0,
    })

    roots = [node_of[b["index"]] for b in bone_order
             if b["parent"] == ROOT_PARENT or b["parent"] not in node_of]

    joint_node_indices = [node_of[b["index"]] for b in bone_order]

    gltf = {
        "asset": {"version": "2.0", "generator": "LingXuJie mod exporter"},
        "scene": 0,
        "scenes": [{"nodes": roots + [mesh_node]}],
        "nodes": nodes,
        "meshes": [{
            "name": source_name,
            "primitives": [{
                "attributes": {
                    "POSITION": pos_acc,
                    "NORMAL": norm_acc,
                    "TEXCOORD_0": uv_acc,
                    "JOINTS_0": joint_acc,
                    "WEIGHTS_0": weight_acc,
                },
                "indices": index_acc,
            }],
        }],
        "skins": [{
            "joints": joint_node_indices,
            "inverseBindMatrices": add_inverse_bind(binary, buffer_views, accessors,
                                                    nodes, joint_node_indices),
        }],
        "bufferViews": buffer_views,
        "accessors": accessors,
        "buffers": [{"byteLength": len(binary)}],
    }
    return gltf, bytes(binary)


def add_inverse_bind(binary, buffer_views, accessors, nodes, joint_indices):
    """Identity inverse bind matrices: the bind pose is the node transforms themselves."""
    while len(binary) % 4:
        binary.append(0)
    view = {"buffer": 0, "byteOffset": len(binary), "byteLength": 64 * len(joint_indices)}
    binary.extend(b"\x00" * (64 * len(joint_indices)))
    # Column-major identity.
    identity = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    offset = view["byteOffset"]
    for i in range(len(joint_indices)):
        binary[offset + i * 64:offset + (i + 1) * 64] = struct.pack("<16f", *identity)
    buffer_views.append(view)
    accessors.append({
        "bufferView": len(buffer_views) - 1,
        "componentType": 5126,
        "count": len(joint_indices),
        "type": "MAT4",
    })
    return len(accessors) - 1


def main():
    if len(sys.argv) < 2:
        print("usage: python export_mod_gltf.py <mod path> [out .gltf]")
        return
    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(source)[0] + ".gltf"

    objects = parse(source)
    bones = [o for o in objects if o["marker"] == BONE_MARKER]
    meshes = [o for o in objects if o["marker"] == MESH_MARKER]
    print("%s: %d objects (%d bones, %d meshes)"
          % (os.path.basename(source), len(objects), len(bones), len(meshes)))
    if not meshes:
        print("  no mesh; skipping")
        return

    mesh = meshes[0]
    print("  vertex_num=%d triangles=%d influence_records=%d"
          % (mesh["vertex_num"], len(mesh["triangles"]), len(mesh["bone_records"])))

    gltf, blob = build_gltf(objects, os.path.splitext(os.path.basename(source))[0])

    folder = os.path.dirname(output)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    bin_path = os.path.splitext(output)[0] + ".bin"
    with open(bin_path, "wb") as handle:
        handle.write(blob)
    gltf["buffers"][0]["uri"] = os.path.basename(bin_path)

    with open(output, "w", encoding="utf-8") as handle:
        json.dump(gltf, handle, indent=1)

    print("  wrote %s (%d bytes) and %s (%d bytes)"
          % (output, os.path.getsize(output), bin_path, len(blob)))
    print("  nodes=%d skin joints=%d accessors=%d"
          % (len(gltf["nodes"]), len(gltf["skins"][0]["joints"]), len(gltf["accessors"])))


if __name__ == "__main__":
    main()
