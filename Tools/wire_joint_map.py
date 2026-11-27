"""Pass the bone-to-joint mapping into the mesh emitter.

Bone indices are sparse, so a vertex's joint attribute must be the position of its bone in the
sorted joint list rather than the bone index itself.

    python Tools/wire_joint_map.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/export_mod_anim_gltf.py"

OLD = (
    '    primitives = []\n'
    '    for each in meshes:\n'
    '        attributes, indices = emit_mesh(each, shared_centre)'
)

NEW = (
    '    # The joint list is the bones sorted by their own index, and a vertex\'s joint attribute\n'
    '    # is its position here rather than the bone index, because those indices are sparse.\n'
    '    ordered_bones = sorted(bones, key=lambda b: b["index"])\n'
    '    joint_of_bone = {b["index"]: i for i, b in enumerate(ordered_bones)}\n'
    '\n'
    '    primitives = []\n'
    '    for each in meshes:\n'
    '        attributes, indices = emit_mesh(each, shared_centre, joint_of_bone)'
)


def main():
    text = open(PATH, encoding="utf-8").read()
    if "joint_of_bone" in text:
        print("already wired")
        return
    if OLD not in text:
        print("target loop not found")
        index = text.find("primitives = []")
        print(text[max(0, index - 200):index + 300])
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("joint mapping wired in")


if __name__ == "__main__":
    main()
