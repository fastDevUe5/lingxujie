"""Teach the exporter to carry every mesh block, not just the first.

The bird had one mesh, so taking the first was invisible. Characters have several - this one has a
body of six hundred thirty-two vertices and two smaller pieces - and exporting only the first
produced an object a third of a metre across instead of a person. The bounds were the clue: no
humanoid is thirty-nine centimetres tall.

Each mesh block carries its own positions, indices and physique, so the fix is to emit one glTF mesh
with one primitive per block, all sharing a single skin whose joints come from the bone blocks.

    python Tools/fix_multi_mesh.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/export_mod_anim_gltf.py"

HELPERS = '''
def emit_primitive(mesh, views, accessors, binary):
    """Write one mesh block as a glTF primitive and return its attribute indices."""
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

    def cp(p):
        return (p[0] * 0.01, p[2] * 0.01, -p[1] * 0.01)

    def cn(n):
        return (n[0], n[2], -n[1])

    vertex_num = mesh["vertex_num"]
    positions = [cp(p) for p in mesh["positions"]]
    pos_acc = add_accessor(
        add_view(b"".join(struct.pack("<3f", *p) for p in positions), 34962),
        5126, vertex_num, "VEC3",
        {"min": [min(p[i] for p in positions) for i in range(3)],
         "max": [max(p[i] for p in positions) for i in range(3)]})
    norm_acc = add_accessor(
        add_view(b"".join(struct.pack("<3f", *cn(n)) for n in mesh["normals"]), 34962),
        5126, vertex_num, "VEC3")

    uv_raw = b"".join(struct.pack("<2f", u, 1.0 - v) for u, v in mesh["uvs"][:vertex_num])
    if len(mesh["uvs"]) < vertex_num:
        uv_raw += struct.pack("<2f", 0.0, 0.0) * (vertex_num - len(mesh["uvs"]))
    uv_acc = add_accessor(add_view(uv_raw, 34962), 5126, vertex_num, "VEC2")

    flat = [i for tri in mesh["triangles"] for i in tri]
    index_acc = add_accessor(
        add_view(b"".join(struct.pack("<H", i) for i in flat), 34963),
        5123, len(flat), "SCALAR")

    joints = []
    weights = []
    starts = mesh["influence_starts"]
    records = mesh["bone_records"]
    for v in range(vertex_num):
        bones_num, bone_start = starts[v] if v < len(starts) else (0, 0)
        js = []
        ws = []
        for k in range(bones_num):
            idx = bone_start + k
            if 0 <= idx < len(records):
                js.append(records[idx][0])
                ws.append(records[idx][1])
        while len(js) < 4:
            js.append(0)
            ws.append(0.0)
        total = sum(ws)
        if total > 1e-6:
            ws = [w / total for w in ws]
        joints.append(js[:4])
        weights.append(ws[:4])

    joint_acc = add_accessor(
        add_view(b"".join(struct.pack("<4H", *j) for j in joints), 34962),
        5123, vertex_num, "VEC4")
    weight_acc = add_accessor(
        add_view(b"".join(struct.pack("<4f", *w) for w in weights), 34962),
        5126, vertex_num, "VEC4")

    return {"POSITION": pos_acc, "NORMAL": norm_acc, "TEXCOORD_0": uv_acc,
            "JOINTS_0": joint_acc, "WEIGHTS_0": weight_acc}, index_acc
'''


def main():
    text = open(PATH, encoding="utf-8").read()
    if "def emit_primitive" in text:
        print("helper already present")
        return

    # Insert the helper before build().
    marker = "def build(objects, tracks, source_name):"
    if marker not in text:
        print("build() not found")
        return
    text = text.replace(marker, HELPERS.strip() + "\n\n\n" + marker, 1)

    # Replace the single-mesh emission with a loop over all meshes.
    old_start = '    vertex_num = mesh["vertex_num"]'
    old_end = '    # Nodes.'
    start = text.find(old_start)
    end = text.find(old_end)
    if start < 0 or end < 0:
        print("single-mesh block boundaries not found")
        return

    replacement = '''    primitives = []
    for each_mesh in meshes:
        attributes, indices = emit_primitive(each_mesh, views, accessors, binary)
        primitives.append({"attributes": attributes, "indices": indices})

'''
    text = text[:start] + replacement + text[end:]

    # The mesh entry now carries every primitive.
    text = text.replace(
        '"meshes": [{"name": source_name, "primitives": [{\n'
        '            "attributes": {"POSITION": pos_acc, "NORMAL": norm_acc, "TEXCOORD_0": uv_acc,\n'
        '                           "JOINTS_0": joint_acc, "WEIGHTS_0": weight_acc},\n'
        '            "indices": index_acc}]}],',
        '"meshes": [{"name": source_name, "primitives": primitives}],')

    open(PATH, "w", encoding="utf-8").write(text)
    print("exporter now emits one primitive per mesh block")


if __name__ == "__main__":
    main()
