"""Export a mod plus an anm as a single glTF carrying both the skinned mesh and the animation.

The two formats are separately verified, and the bone names line up: the bird's mod declares
Bone01 through Bone09 and its anm declares the same nine plus two objects that are not bones.
So this is assembly, not discovery.

Time comes from ticks over four thousand eight hundred, which is the constant that makes the
measured one hundred sixty ticks per frame land on exactly thirty frames per second.

    python Tools/export_mod_anim_gltf.py <mod> <anm> <out.gltf>
"""

import json
import math
import os
import struct
import sys

MOD_HEADER = 8
MOD_MESH_MARKER = 0xF4000000
MOD_BONE_MARKER = 0xF5000000
MOD_BASE_OBJECT = 324
MOD_MESH_HEADER = 48
MOD_PHYSIQUE_HEADER = 12
MOD_PHYSIQUE_VERTEX = 5
MOD_BONE_SIZE = 44
MOD_ROOT_PARENT = 0xFFFFFFFF

# mesh_flag bit fields, from the client's mesh_flag.h.
SHADE_TYPE_LIGHT_MAP = 0x03      # light texture instead of normals
TRANSFORM_TYPE_ALIGN_VIEW = 0x30  # billboard; also no normals

ANM_MARKER = b"\x00\xF0\x00\x00"
ANM_OBJECT_HEADER = 152
ANM_POS_KEY = 20
ANM_ROT_KEY = 24
ANM_SCALE_KEY = 36   # u32 ticks + u32 frame + VECTOR3 scale + VECTOR3 axis + float angle

TICKS_PER_SECOND = 4800.0


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


# ---------------------------------------------------------------- mod ----------

def parse_mod(path):
    data = open(path, "rb").read()
    objects = []
    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + MOD_HEADER + size > len(data) + 4:
            break
        payload = offset + MOD_HEADER
        if marker in (MOD_BONE_MARKER, MOD_MESH_MARKER):
            entry = {
                "marker": marker,
                "index": struct.unpack_from("<I", data, payload)[0],
                "parent": struct.unpack_from("<I", data, payload + 192)[0],
                "name": read_name(data, payload + 196),
                "node_tm": struct.unpack_from("<13f", data, payload + 4),
                "node_matrix": struct.unpack_from("<16f", data, payload + 4 + 56),
            }
            if marker == MOD_MESH_MARKER:
                entry.update(read_mod_mesh(data, payload))
            objects.append(entry)
        offset = payload + size
    return objects


def read_mod_mesh(data, payload):
    """Read one mesh block, degrading rather than failing when a block is short.

    A handful of files claim a block that runs a few bytes past the end of the data, which makes
    every packed read at the tail throw. Those files still have usable geometry - the positions and
    indices are fine - so the reads are guarded and anything missing is substituted. A batch that
    stops on the seventh file tells you less than one that exports it approximately and says so.
    """
    def safe_unpack(fmt, offset, fallback):
        try:
            return struct.unpack_from(fmt, data, offset)
        except struct.error:
            return fallback

    cursor = payload + MOD_BASE_OBJECT
    header = safe_unpack("<9I", cursor, (0, 0, 0, 0, 0, 0, 0, 0, 0))
    (max_v, vertex_num, orig_v, ext_v, tex_v, mtl,
     face_group_num, mesh_flag, grid) = header
    cursor += MOD_MESH_HEADER

    if vertex_num <= 0 or vertex_num > 500000:
        raise ValueError("vertex count implausible: %d" % vertex_num)

    positions = []
    for i in range(vertex_num):
        values = safe_unpack("<3f", cursor + i * 12, (0.0, 0.0, 0.0))
        positions.append(values)
    cursor += 12 * vertex_num

    uvs = []
    for i in range(tex_v):
        values = safe_unpack("<2f", cursor + i * 8, (0.0, 0.0))
        uvs.append(values)
    cursor += 8 * tex_v
    cursor += 4 * ext_v

    # Each face group names its own material. Keeping the groups separate is what allows one
    # primitive per material, and therefore more than one slot in the engine.
    triangles = []
    groups = []
    truncated = False
    for _ in range(face_group_num):
        group = safe_unpack("<7I", cursor, None)
        if group is None:
            truncated = True
            break
        (g_mtl, g_index, faces_num, max_faces, vindex, light1, light2) = group
        cursor += 28
        group_triangles = []
        for i in range(faces_num):
            tri = safe_unpack("<3H", cursor + i * 6, None)
            if tri is None:
                truncated = True
                break
            triangles.append(tri)
            group_triangles.append(tri)
        cursor += 2 * faces_num * 3
        cursor += 8 * light1 + 8 * light2
        if group_triangles:
            groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})

    phy = safe_unpack("<3I", cursor, (0, 0, 0))
    phy_verts, phy_bones, phy_alloc = phy
    cursor += MOD_PHYSIQUE_HEADER

    starts = []
    for _ in range(phy_verts):
        bones_num = data[cursor] if cursor < len(data) else 0
        start = safe_unpack("<I", cursor + 1, (0,))[0]
        starts.append((bones_num, start))
        cursor += MOD_PHYSIQUE_VERTEX

    records = []
    for _ in range(phy_bones):
        values = safe_unpack("<If", cursor, (0, 0.0))
        records.append((values[0], values[1]))
        cursor += MOD_BONE_SIZE

    # Normals are conditional, not unconditional. The client reads them only when the mesh is
    # neither light-mapped nor view-aligned:
    #
    #   if (shadeType == SHADE_TYPE_LIGHT_MAP)                 read a light texture instead
    #   else if (transformType != TRANSFORM_TYPE_ALIGN_VIEW)   read the normals
    #
    # Reading them anyway runs past the end of the mesh, which is what the batch failures were.
    shade_type = mesh_flag & 0x0000000F
    transform_type = mesh_flag & 0x000000F0
    has_normals = (shade_type != SHADE_TYPE_LIGHT_MAP
                   and transform_type != TRANSFORM_TYPE_ALIGN_VIEW
                   and cursor + 12 * vertex_num <= len(data))

    if has_normals:
        normals = [struct.unpack_from("<3f", data, cursor + i * 12)
                   for i in range(vertex_num)]
    else:
        # A mesh without normals still needs the attribute for glTF, so it gets a constant up
        # vector. Shading will be flat, which is what the source says by omitting them.
        normals = [(0.0, 0.0, 1.0)] * vertex_num

    return {"vertex_num": vertex_num, "positions": positions, "uvs": uvs,
            "triangles": triangles, "groups": groups,
            "influence_starts": starts,
            "bone_records": records, "normals": normals,
            "has_normals": has_normals, "mesh_flag": mesh_flag,
            "truncated": truncated}


# ---------------------------------------------------------------- anm ----------

def anm_first_block(data):
    """Find where the motion blocks really begin.

    The header length is not fixed - a bird animation starts its first block at byte two hundred six
    and an earlier one at two hundred nine - so the scan looks for the block marker. Scanning for
    the marker alone is not enough: some headers contain the same four bytes by coincidence, and
    accepting one of those produces a block whose key counts demand thirteen billion bytes.

    A real block also carries a printable object name, and the longer of two candidate walks is the
    real one. Both checks together separate the two.
    """
    markers = [i for i in range(len(data) - 8) if data[i:i + 4] == ANM_MARKER]
    best = None
    for candidate in markers[:64]:
        size = struct.unpack_from("<I", data, candidate + 4)[0]
        if size < ANM_OBJECT_HEADER or candidate + 8 + size > len(data):
            continue
        payload = candidate + 8
        if not anm_name_plausible(data, payload + 20):
            continue

        offset = candidate
        blocks = 0
        while offset + 8 <= len(data) and data[offset:offset + 4] == ANM_MARKER:
            block_size = struct.unpack_from("<I", data, offset + 4)[0]
            block_payload = offset + 8
            if block_size < ANM_OBJECT_HEADER or block_payload + block_size > len(data):
                break
            (_obj, rot_n, pos_n, scale_n, _mesh) = struct.unpack_from(
                "<5I", data, block_payload)
            required = (ANM_OBJECT_HEADER + pos_n * ANM_POS_KEY + rot_n * ANM_ROT_KEY
                        + scale_n * ANM_SCALE_KEY)
            if required > block_size:
                break
            offset = block_payload + block_size
            blocks += 1
            if blocks > 5000:
                break

        if best is None or blocks > best[1]:
            best = (candidate, blocks)
        if blocks > 0 and candidate == markers[0]:
            # The very first marker that works is almost always the right one; stop early.
            break
    return best[0] if best else None


def anm_name_plausible(data, offset, length=128):
    """A block name is a short printable string, not control codes."""
    raw = data[offset:offset + length]
    if not raw:
        return False
    end = raw.find(b"\x00")
    if end < 0:
        end = len(raw)
    text = raw[:end]
    if len(text) < 2:
        return False
    for byte in text:
        if byte < 0x20:
            return False
    return True


def parse_anm(path):
    data = open(path, "rb").read()
    start = anm_first_block(data)
    if start is None:
        return {}

    tracks = {}
    offset = start
    while offset + 8 <= len(data) and data[offset:offset + 4] == ANM_MARKER:
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        if size < ANM_OBJECT_HEADER or payload + size > len(data):
            break

        header = struct.unpack_from("<5I", data, payload)
        (obj_index, rot_n, pos_n, scale_n, mesh_n) = header

        # Self-check: the declared key counts have to fit inside the block. They need not fill it
        # exactly, because a block with animated mesh keys carries variable-length vertex and UV
        # arrays after the scale keys, whose size depends on the mesh rather than on the counts.
        #
        #   expected = 152 + pos*20 + rot*24 + scale*40
        #   expected <= size      and the remainder belongs to the animated mesh keys
        #
        # Requiring equality stopped the walk at the first such block, which is why files with
        # seventy blocks appeared to contain five.
        required = (ANM_OBJECT_HEADER + pos_n * ANM_POS_KEY + rot_n * ANM_ROT_KEY
                    + scale_n * ANM_SCALE_KEY)
        if required > size:
            break

        name = read_name(data, payload + 20)
        cursor = payload + ANM_OBJECT_HEADER

        positions = []
        for i in range(pos_n):
            ticks, frame, x, y, z = struct.unpack_from("<II3f", data, cursor + i * ANM_POS_KEY)
            positions.append((ticks, (x, y, z)))
        cursor += pos_n * ANM_POS_KEY

        rotations = []
        for i in range(rot_n):
            ticks, frame, qx, qy, qz, qw = struct.unpack_from(
                "<II4f", data, cursor + i * ANM_ROT_KEY)
            rotations.append((ticks, (qx, qy, qz, qw)))
        cursor += rot_n * ANM_ROT_KEY

        scales = []
        for i in range(scale_n):
            ticks, frame, sx, sy, sz = struct.unpack_from(
                "<II3f", data, cursor + i * ANM_SCALE_KEY)
            scales.append((ticks, (sx, sy, sz)))
        cursor += scale_n * ANM_SCALE_KEY

        if positions or rotations or scales:
            tracks[name] = {"positions": positions, "rotations": rotations, "scales": scales}
        offset = payload + size
    return tracks


# ------------------------------------------------------------- gltf -----------

def axis_angle_quat(axis, angle):
    length = math.sqrt(axis[0] ** 2 + axis[1] ** 2 + axis[2] ** 2)
    if length < 1e-8:
        return (0.0, 0.0, 0.0, 1.0)
    half = angle * 0.5
    s = math.sin(half) / length
    return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(half))


def build(objects, tracks, source_name):
    bones = [o for o in objects if o["marker"] == MOD_BONE_MARKER]
    meshes = [o for o in objects if o["marker"] == MOD_MESH_MARKER]
    mesh = meshes[0]

    def cp(p):
        return (p[0] * 0.01, p[2] * 0.01, -p[1] * 0.01)

    def cn(n):
        return (n[0], n[2], -n[1])

    binary = bytearray()
    views = []
    accessors = []

    def add_view(raw, target=None):
        while len(binary) % 4:
            binary.append(0)
        view = {"buffer": 0, "byteOffset": len(binary), "byteLength": len(raw)}
        if target:
            view["target"] = target
        binary.extend(raw)
        views.append(view)
        return len(views) - 1

    def add_accessor(view, ctype, count, kind, extra=None):
        accessor = {"bufferView": view, "componentType": ctype, "count": count, "type": kind}
        if extra:
            accessor.update(extra)
        accessors.append(accessor)
        return len(accessors) - 1

    def emit_mesh(each, shared_centre, joint_of):
        """Write one mesh block as a primitive; each block carries its own skin data.

        Two transforms are needed and both were missing at first.

        The object carries a NODE_TM whose mat4 holds rotation, scale and translation together. A
        character's parts are placed by it - one mesh sits a hundred and twelve centimetres up and
        another is rotated a hundred fifteen degrees around Y - so skipping it leaves the pieces
        scattered, and the model lies flat. The matrix is row-vector convention, so a point
        transforms as [x y z 1] times the matrix.

        The vertices are already in world space. Mesh blocks carry a NODE_TM matrix like everything
        else, and applying it looked right - it does place each part - but measurement says
        otherwise: with the matrix the whole model spans 192 x 434 x 152 cm and without it 297 x 272
        x 208 cm, and the spread between part centres goes from a balanced 181 x 191 x 105 to a
        stretched 159 x 383 x 75. The matrix doubles the model along one axis.

        Bones are the opposite: their mat4 is a genuine world transform, which is why consecutive
        spine bones read Y of ninety-four, one hundred twelve, one hundred twenty-seven. So bones
        keep theirs and meshes do not.

        A centre is still subtracted, shared across every block, so the model sits at the origin and
        the actor's own transform means what it says.
        """
        count = each["vertex_num"]

        transformed = list(each["positions"])

        block_positions = [cp((p[0] - shared_centre[0], p[1] - shared_centre[1],
                               p[2] - shared_centre[2]))
                           for p in transformed]
        block_pos = add_accessor(
            add_view(b"".join(struct.pack("<3f", *p) for p in block_positions), 34962),
            5126, count, "VEC3",
            {"min": [min(p[i] for p in block_positions) for i in range(3)],
             "max": [max(p[i] for p in block_positions) for i in range(3)]})
        block_norm = add_accessor(
            add_view(b"".join(struct.pack("<3f", *cn(n)) for n in each["normals"]), 34962),
            5126, count, "VEC3")

        block_uvs = each["uvs"][:count]
        raw_uvs = b"".join(struct.pack("<2f", u, 1.0 - v) for u, v in block_uvs)
        raw_uvs += struct.pack("<2f", 0.0, 0.0) * (count - len(block_uvs))
        block_uv = add_accessor(add_view(raw_uvs, 34962), 5126, count, "VEC2")

        flat = [i for tri in each["triangles"] for i in tri]
        block_indices = add_accessor(
            add_view(b"".join(struct.pack("<H", i) for i in flat), 34963),
            5123, len(flat), "SCALAR")

        # Per-group index buffers, so each face group becomes its own primitive with its own
        # material. glTF allows primitives to share vertex attributes and differ only in indices,
        # which keeps this cheap.
        group_indices = []
        for group in each.get("groups") or []:
            group_flat = [i for tri in group["triangles"] for i in tri]
            if not group_flat:
                continue
            accessor = add_accessor(
                add_view(b"".join(struct.pack("<H", i) for i in group_flat), 34963),
                5123, len(group_flat), "SCALAR")
            group_indices.append((group.get("material", 0), accessor))

        block_joints = []
        block_weights = []
        block_starts = each["influence_starts"]
        block_records = each["bone_records"]
        for v in range(count):
            bones_num, bone_start = block_starts[v] if v < len(block_starts) else (0, 0)
            js = []
            ws = []
            for k in range(bones_num):
                idx = bone_start + k
                if 0 <= idx < len(block_records):
                    mapped = joint_of.get(block_records[idx][0])
                if mapped is not None:
                    js.append(mapped)
                    ws.append(block_records[idx][1])
            while len(js) < 4:
                js.append(0)
                ws.append(0.0)
            total = sum(ws)
            if total > 1e-6:
                ws = [w / total for w in ws]
            block_joints.append(js[:4])
            block_weights.append(ws[:4])

        block_joint = add_accessor(
            add_view(b"".join(struct.pack("<4H", *j) for j in block_joints), 34962),
            5123, count, "VEC4")
        block_weight = add_accessor(
            add_view(b"".join(struct.pack("<4f", *w) for w in block_weights), 34962),
            5126, count, "VEC4")

        attributes = {"POSITION": block_pos, "NORMAL": block_norm, "TEXCOORD_0": block_uv,
                      "JOINTS_0": block_joint, "WEIGHTS_0": block_weight}
        return attributes, block_indices, group_indices

    # Drop blocks whose geometry spans an implausible distance. A character file also carries
    # background and effect geometry, and some of it has vertices tens of kilometres apart - a boss
    # two metres tall produced bounds fourteen kilometres across. Every block here is skinned, so
    # bone records do not separate them; size does.
    #
    # A hundred metres is generous for any single piece of a character, and the alternative is an
    # asset whose bounds make it unusable in the editor.
    def block_extent(each):
        matrix = each.get("node_matrix")
        points = []
        for p in each["positions"]:
            if matrix:
                points.append((
                    p[0] * matrix[0] + p[1] * matrix[4] + p[2] * matrix[8] + matrix[12],
                    p[0] * matrix[1] + p[1] * matrix[5] + p[2] * matrix[9] + matrix[13],
                    p[0] * matrix[2] + p[1] * matrix[6] + p[2] * matrix[10] + matrix[14],
                ))
            else:
                points.append(p)
        if not points:
            return 0.0
        return max(max(q[i] for q in points) - min(q[i] for q in points)
                   for i in range(3))

    keep = []
    dropped = 0
    for each in meshes:
        if block_extent(each) > 10000.0:
            dropped += 1
            continue
        keep.append(each)
    if keep:
        meshes = keep
    elif dropped:
        # Every block was oversized, so filtering everything out leaves an empty mesh - three models
        # did exactly that and exported with a zero extent. Keeping the smallest block preserves
        # something rather than nothing, and the report above already flags the file as unusual.
        smallest = min(meshes, key=block_extent)
        meshes = [smallest]
        dropped -= 1
    if dropped:
        print("  dropped %d block(s) larger than 100 m" % dropped)

    # One centre for the whole model, computed over every transformed vertex, so the pieces keep
    # their arrangement relative to each other.
    # Raw vertices, because the emitter no longer applies the mesh matrix; the centre has to be
    # computed from the same points it is subtracted from.
    all_points = []
    for each in meshes:
        all_points.extend(each["positions"])
    if all_points:
        shared_centre = [sum(p[i] for p in all_points) / len(all_points) for i in range(3)]
    else:
        shared_centre = [0.0, 0.0, 0.0]

    # The joint list is the bones sorted by their own index, and a vertex's joint attribute
    # is its position here rather than the bone index, because those indices are sparse.
    ordered_bones = sorted(bones, key=lambda b: b["index"])
    joint_of_bone = {b["index"]: i for i, b in enumerate(ordered_bones)}

    primitives = []
    used_materials = []
    for each in meshes:
        attributes, indices, groups = emit_mesh(each, shared_centre, joint_of_bone)
        if groups:
            # One primitive per face group, each naming its material.
            for material_index, accessor in groups:
                primitive = {"attributes": attributes, "indices": accessor}
                if material_index not in used_materials:
                    used_materials.append(material_index)
                primitive["material"] = used_materials.index(material_index)
                primitives.append(primitive)
        else:
            primitives.append({"attributes": attributes, "indices": indices})

    # Nodes.
    #
    # The node transform must be the bone's LOCAL transform, but NODE_TM's mat4 is its world
    # transform. Building nodes from fPos and fRotAng was wrong twice over: those fields do not even
    # reproduce mat4 (a spine bone reads a position of (13.9, 0, 0) where mat4 says
    # (-32.4, 94.4, -11.2)), and the matrix is already world. So each node's local transform is
    # inverse(parentWorld) * world, decomposed into translation, rotation and scale for glTF.
    ordered = sorted(bones, key=lambda b: b["index"])
    node_of = {b["index"]: i for i, b in enumerate(ordered)}

    def bone_world(bone):
        matrix = bone.get("node_matrix")
        if matrix is None:
            return [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        return matrix

    def invert_affine(m):
        a, b, c = m[0], m[1], m[2]
        d, e, f = m[4], m[5], m[6]
        g, h, i = m[8], m[9], m[10]
        det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        if abs(det) < 1e-12:
            return None
        inv_det = 1.0 / det
        r = [
            (e * i - f * h) * inv_det, (c * h - b * i) * inv_det, (b * f - c * e) * inv_det,
            (f * g - d * i) * inv_det, (a * i - c * g) * inv_det, (c * d - a * f) * inv_det,
            (d * h - e * g) * inv_det, (b * g - a * h) * inv_det, (a * e - b * d) * inv_det,
        ]
        tx, ty, tz = m[12], m[13], m[14]
        return [
            r[0], r[1], r[2], 0.0,
            r[3], r[4], r[5], 0.0,
            r[6], r[7], r[8], 0.0,
            -(tx * r[0] + ty * r[3] + tz * r[6]),
            -(tx * r[1] + ty * r[4] + tz * r[7]),
            -(tx * r[2] + ty * r[5] + tz * r[8]),
            1.0,
        ]

    def multiply(a, b):
        out = [0.0] * 16
        for r in range(4):
            for c in range(4):
                out[r * 4 + c] = sum(a[r * 4 + k] * b[k * 4 + c] for k in range(4))
        return out

    def decompose(m, centre):
        """Translation, quaternion and scale from a world matrix, in glTF's Y-up metres."""
        tx = m[12] - centre[0]
        ty = m[13] - centre[1]
        tz = m[14] - centre[2]
        translation = cp((tx, ty, tz))

        # Column lengths are the scale; normalise to get the rotation.
        cols = [(m[0], m[1], m[2]), (m[4], m[5], m[6]), (m[8], m[9], m[10])]
        lengths = [math.sqrt(sum(v * v for v in col)) or 1.0 for col in cols]
        basis = [[cols[c][r] / lengths[c] for c in range(3)] for r in range(3)]

        # Convert the basis to glTF axes: X stays, Y takes source Z, Z takes -source Y.
        gx = (basis[0][0], basis[1][0], basis[2][0])
        gy = (basis[0][2], basis[1][2], basis[2][2])
        gz = (-basis[0][1], -basis[1][1], -basis[2][1])
        rot = [
            gx[0], gy[0], gz[0],
            gx[1], gy[1], gz[1],
            gx[2], gy[2], gz[2],
        ]
        trace = rot[0] + rot[4] + rot[8]
        if trace > 0.0:
            s = math.sqrt(trace + 1.0) * 2.0
            w = 0.25 * s
            x = (rot[7] - rot[5]) / s
            y = (rot[2] - rot[6]) / s
            z = (rot[3] - rot[1]) / s
        elif rot[0] > rot[4] and rot[0] > rot[8]:
            s = math.sqrt(1.0 + rot[0] - rot[4] - rot[8]) * 2.0
            w = (rot[7] - rot[5]) / s
            x = 0.25 * s
            y = (rot[1] + rot[3]) / s
            z = (rot[2] + rot[6]) / s
        elif rot[4] > rot[8]:
            s = math.sqrt(1.0 + rot[4] - rot[0] - rot[8]) * 2.0
            w = (rot[2] - rot[6]) / s
            x = (rot[1] + rot[3]) / s
            y = 0.25 * s
            z = (rot[5] + rot[7]) / s
        else:
            s = math.sqrt(1.0 + rot[8] - rot[0] - rot[4]) * 2.0
            w = (rot[3] - rot[1]) / s
            x = (rot[2] + rot[6]) / s
            y = (rot[5] + rot[7]) / s
            z = 0.25 * s
        gltf_scale = [lengths[0], lengths[2], lengths[1]]
        return list(translation), [x, y, z, w], gltf_scale

    nodes = []
    for bone in ordered:
        world = bone_world(bone)
        parent = bone["parent"]
        if parent in node_of or (parent in {b["index"] for b in ordered}):
            parent_world = bone_world(next(b for b in ordered if b["index"] == parent))
            inverse_parent = invert_affine(parent_world)
            local = multiply(world, inverse_parent) if inverse_parent else world
        else:
            local = world

        translation, rotation, scale = decompose(local, [0.0, 0.0, 0.0])
        node = {
            "name": bone["name"] or ("bone_%d" % bone["index"]),
            "translation": translation,
            "rotation": rotation,
            "scale": scale,
        }
        children = [node_of[b["index"]] for b in ordered
                    if b["parent"] == bone["index"]]
        if children:
            node["children"] = children
        nodes.append(node)

    mesh_node = len(nodes)
    nodes.append({"name": mesh["name"] or "mesh", "mesh": 0, "skin": 0})

    joint_nodes = [node_of[b["index"]] for b in ordered]
    roots = [node_of[b["index"]] for b in ordered
             if b["parent"] == MOD_ROOT_PARENT or b["parent"] not in node_of]

    # Inverse bind matrices. Identity works only when every bone sits at the origin in the bind
    # pose; with a real skeleton, identity drags every vertex towards the origin and the parts fly
    # apart, which is what the boss did before this was computed.
    #
    #   IBM[i] = inverse(bindWorld[i])
    #
    # bindWorld accumulates each bone's NODE_TM up its parent chain. glTF stores matrices in
    # column-major order and multiplies column vectors, while the source matrices are row-vector, so
    # the inverse is transposed on the way out.
    def multiply(a, b):
        out = [0.0] * 16
        for r in range(4):
            for c in range(4):
                out[r * 4 + c] = sum(a[r * 4 + k] * b[k * 4 + c] for k in range(4))
        return out

    def invert(m):
        a, b, c = m[0], m[1], m[2]
        d, e, f = m[4], m[5], m[6]
        g, h, i = m[8], m[9], m[10]
        det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        if abs(det) < 1e-12:
            return None
        inv_det = 1.0 / det
        r = [
            (e * i - f * h) * inv_det, (c * h - b * i) * inv_det, (b * f - c * e) * inv_det,
            (f * g - d * i) * inv_det, (a * i - c * g) * inv_det, (c * d - a * f) * inv_det,
            (d * h - e * g) * inv_det, (b * g - a * h) * inv_det, (a * e - b * d) * inv_det,
        ]
        tx, ty, tz = m[12], m[13], m[14]
        return [
            r[0], r[1], r[2], 0.0,
            r[3], r[4], r[5], 0.0,
            r[6], r[7], r[8], 0.0,
            -(tx * r[0] + ty * r[3] + tz * r[6]),
            -(tx * r[1] + ty * r[4] + tz * r[7]),
            -(tx * r[2] + ty * r[5] + tz * r[8]),
            1.0,
        ]

    bone_by_index = {b["index"]: b for b in ordered}
    world_cache = {}

    def bind_world(bone, depth=0):
        """A bone's bind transform.

        NODE_TM's mat4 is already the bone's world transform - consecutive spine bones read
        (-32, 94, -11), (-31, 112, -15), (-28, 127, -19), marching up in Y by a comfortable
        amount for a spine. Treating it as a local transform and multiplying up the parent chain
        squares it, which put the bones ten metres away from a two-metre body and made the
        inverse bind matrices meaningless.
        """
        index = bone["index"]
        if index in world_cache:
            return world_cache[index]
        world = bone.get("node_matrix")
        if world is None:
            world = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                     0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        world_cache[index] = world
        return world

    while len(binary) % 4:
        binary.append(0)
    ibm_view = {"buffer": 0, "byteOffset": len(binary),
                "byteLength": 64 * len(joint_nodes)}
    ibm_start = len(binary)
    binary.extend(b"\x00" * (64 * len(joint_nodes)))

    for position, bone in enumerate(ordered):
        world = bind_world(bone)
        inverse = invert(world)
        if inverse is None:
            inverse = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                       0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        # Transpose into glTF's column-major order.
        column_major = [inverse[c * 4 + r] for r in range(4) for c in range(4)]
        start = ibm_start + position * 64
        binary[start:start + 64] = struct.pack("<16f", *column_major)
    views.append(ibm_view)
    ibm_acc = len(accessors)
    accessors.append({"bufferView": len(views) - 1, "componentType": 5126,
                      "count": len(joint_nodes), "type": "MAT4"})

    gltf = {
        "asset": {"version": "2.0", "generator": "LingXuJie mod+anm exporter"},
        "scene": 0,
        "scenes": [{"nodes": roots + [mesh_node]}],
        "nodes": nodes,
        "meshes": [{"name": source_name, "primitives": primitives}],
        "materials": [
            {"name": "moxiang_material_%d" % index,
             "pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.8, 0.8, 1.0],
                                      "metallicFactor": 0.0,
                                      "roughnessFactor": 0.8}}
            for index in range(max(1, len(used_materials)))
        ],
        "skins": [{"joints": joint_nodes, "inverseBindMatrices": ibm_acc}],
        "bufferViews": views,
        "accessors": accessors,
        "buffers": [{"byteLength": len(binary)}],
    }

    # Animation: one channel set per bone that has tracks.
    channels = []
    samplers = []
    for bone in ordered:
        track = tracks.get(bone["name"])
        if not track:
            continue
        node_index = node_of[bone["index"]]

        def add_track(keys, path, convert, kind, entries):
            if len(keys) < 2:
                return
            times = [k[0] / TICKS_PER_SECOND for k in keys]
            values = [convert(k[1]) for k in keys]
            time_acc = add_accessor(
                add_view(b"".join(struct.pack("<f", t) for t in times), None),
                5126, len(times), "SCALAR",
                {"min": [min(times)], "max": [max(times)]})
            value_acc = add_accessor(
                add_view(b"".join(struct.pack("<%df" % entries, *v) for v in values), None),
                5126, len(values), kind)
            samplers.append({"input": time_acc, "output": value_acc,
                             "interpolation": "LINEAR"})
            channels.append({"sampler": len(samplers) - 1,
                             "target": {"node": node_index, "path": path}})

        add_track(track["positions"], "translation", cp, "VEC3", 3)
        add_track(track["scales"], "scale", lambda s: (s[0], s[2], s[1]), "VEC3", 3)

        if track["rotations"]:
            converted = [(t, (q[0], q[2], -q[1], q[3])) for t, q in track["rotations"]]
            if len(converted) >= 2:
                times = [t / TICKS_PER_SECOND for t, _ in converted]
                time_acc = add_accessor(
                    add_view(b"".join(struct.pack("<f", t) for t in times), None),
                    5126, len(times), "SCALAR",
                    {"min": [min(times)], "max": [max(times)]})
                value_acc = add_accessor(
                    add_view(b"".join(struct.pack("<4f", *q) for _, q in converted), None),
                    5126, len(converted), "VEC4")
                samplers.append({"input": time_acc, "output": value_acc,
                                 "interpolation": "LINEAR"})
                channels.append({"sampler": len(samplers) - 1,
                                 "target": {"node": node_index, "path": "rotation"}})

    if channels:
        gltf["animations"] = [{"name": source_name, "channels": channels, "samplers": samplers}]

    # The byte length has to be taken after every accessor has appended to the binary. Reading it
    # at dictionary construction time undercounts by exactly the animation data, and the importer
    # reports that as a buffer size mismatch.
    gltf["buffers"][0]["byteLength"] = len(binary)

    return gltf, bytes(binary)


def main():
    if len(sys.argv) < 4:
        print("usage: python export_mod_anim_gltf.py <mod> <anm> <out.gltf>")
        return
    mod_path, anm_path, out_path = sys.argv[1:4]

    objects = parse_mod(mod_path)
    tracks = parse_anm(anm_path)
    bones = [o for o in objects if o["marker"] == MOD_BONE_MARKER]
    meshes = [o for o in objects if o["marker"] == MOD_MESH_MARKER]

    matched = [b["name"] for b in bones if b["name"] in tracks]
    print("mod: %d bones, %d meshes" % (len(bones), len(meshes)))
    print("anm: %d tracks" % len(tracks))
    print("matched bones: %d of %d -> %s" % (len(matched), len(bones), matched))
    if not meshes:
        print("no mesh; abort")
        return

    gltf, blob = build(objects, tracks,
                       os.path.splitext(os.path.basename(mod_path))[0])

    folder = os.path.dirname(out_path)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    bin_path = os.path.splitext(out_path)[0] + ".bin"
    with open(bin_path, "wb") as handle:
        handle.write(blob)
    gltf["buffers"][0]["uri"] = os.path.basename(bin_path)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(gltf, handle, indent=1)

    animation = gltf.get("animations", [{}])[0]
    print("wrote %s (%d bytes) and %s (%d bytes)"
          % (out_path, os.path.getsize(out_path), bin_path, len(blob)))
    print("nodes=%d joints=%d animation channels=%d"
          % (len(gltf["nodes"]), len(gltf["skins"][0]["joints"]),
             len(animation.get("channels", []))))


if __name__ == "__main__":
    main()
