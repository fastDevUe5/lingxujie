"""Keep each face group's material index so the export can produce multiple slots.

A mesh block's face groups each name a material: one block of a boss has six groups pointing at
materials thirty-four through thirty-nine. Combining them into a single primitive loses that, and the
engine then gives the mesh one slot for everything.

This records the grouping so the emitter can write one primitive per group.

    python Tools/add_group_materials.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/export_mod_anim_gltf.py"

OLD = """    triangles = []
    truncated = False
    for _ in range(face_group_num):
        group = safe_unpack("<7I", cursor, None)
        if group is None:
            truncated = True
            break
        (g_mtl, g_index, faces_num, max_faces, vindex, light1, light2) = group
        cursor += 28
        for i in range(faces_num):
            tri = safe_unpack("<3H", cursor + i * 6, None)
            if tri is None:
                truncated = True
                break
            triangles.append(tri)
        cursor += 2 * faces_num * 3
        cursor += 8 * light1 + 8 * light2"""

NEW = """    # Each face group names its own material. Keeping the groups separate is what allows one
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
            groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if '"groups": groups' in text:
        print("already recorded")
        return
    if OLD not in text:
        print("triangle loop not found in the expected form")
        return
    text = text.replace(OLD, NEW)

    # Return the groups alongside the flat list.
    old_return = ('    return {"vertex_num": vertex_num, "positions": positions, "uvs": uvs,\n'
                  '            "triangles": triangles, "influence_starts": starts,')
    new_return = ('    return {"vertex_num": vertex_num, "positions": positions, "uvs": uvs,\n'
                  '            "triangles": triangles, "groups": groups,\n'
                  '            "influence_starts": starts,')
    if old_return in text:
        text = text.replace(old_return, new_return)
        print("return updated")
    else:
        print("return statement not found; groups will be unused")

    open(PATH, "w", encoding="utf-8").write(text)
    print("face-group materials recorded")


if __name__ == "__main__":
    main()
