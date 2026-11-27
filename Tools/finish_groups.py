"""Finish the per-group primitives: change what emit_mesh returns and how it is consumed.

Two edits: the return statement now carries the per-group index accessors, and the caller turns each
group into its own primitive with a material index.

    python Tools/finish_groups.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/export_mod_anim_gltf.py"

OLD_RETURN = (
    '        return {"POSITION": block_pos, "NORMAL": block_norm, "TEXCOORD_0": block_uv,\n'
    '                "JOINTS_0": block_joint, "WEIGHTS_0": block_weight}, block_indices'
)
NEW_RETURN = (
    '        attributes = {"POSITION": block_pos, "NORMAL": block_norm, "TEXCOORD_0": block_uv,\n'
    '                      "JOINTS_0": block_joint, "WEIGHTS_0": block_weight}\n'
    '        return attributes, block_indices, group_indices'
)

OLD_CALL = (
    '    primitives = []\n'
    '    for each in meshes:\n'
    '        attributes, indices = emit_mesh(each, shared_centre, joint_of_bone)\n'
    '        primitives.append({"attributes": attributes, "indices": indices})'
)
NEW_CALL = (
    '    primitives = []\n'
    '    used_materials = []\n'
    '    for each in meshes:\n'
    '        attributes, indices, groups = emit_mesh(each, shared_centre, joint_of_bone)\n'
    '        if groups:\n'
    '            # One primitive per face group, each naming its material.\n'
    '            for material_index, accessor in groups:\n'
    '                primitive = {"attributes": attributes, "indices": accessor}\n'
    '                if material_index not in used_materials:\n'
    '                    used_materials.append(material_index)\n'
    '                primitive["material"] = used_materials.index(material_index)\n'
    '                primitives.append(primitive)\n'
    '        else:\n'
    '            primitives.append({"attributes": attributes, "indices": indices})'
)


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    if OLD_RETURN in text:
        text = text.replace(OLD_RETURN, NEW_RETURN)
        changed += 1
    if OLD_CALL in text:
        text = text.replace(OLD_CALL, NEW_CALL)
        changed += 1
    if changed == 0:
        print("nothing matched; printing the current forms")
        index = text.find("return {\"POSITION\"")
        print(repr(text[index:index + 200]))
        index = text.find("primitives = []")
        print(repr(text[index:index + 300]))
        return
    open(PATH, "w", encoding="utf-8").write(text)
    print("applied %d change(s)" % changed)


if __name__ == "__main__":
    main()
