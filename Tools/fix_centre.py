"""Make the shared centre use raw vertices too, matching the emit path.

The emitter stopped applying the mesh matrix, so the centre must be computed from the same raw
vertices - otherwise it is subtracted from differently-placed points and the model shifts.

    python Tools/fix_centre.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/export_mod_anim_gltf.py"


def main():
    text = open(PATH, encoding="utf-8").read()

    old = """    all_points = []
    for each in meshes:
        matrix = each.get("node_matrix")
        for p in each["positions"]:
            if matrix:
                all_points.append((
                    p[0] * matrix[0] + p[1] * matrix[4] + p[2] * matrix[8] + matrix[12],
                    p[0] * matrix[1] + p[1] * matrix[5] + p[2] * matrix[9] + matrix[13],
                    p[0] * matrix[2] + p[1] * matrix[6] + p[2] * matrix[10] + matrix[14],
                ))
            else:
                all_points.append(p)"""

    new = """    # Raw vertices, because the emitter no longer applies the mesh matrix; the centre has to be
    # computed from the same points it is subtracted from.
    all_points = []
    for each in meshes:
        all_points.extend(each["positions"])"""

    if old not in text:
        print("centre block not found in the expected form")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(old, new))
    print("centre now uses raw vertices")


if __name__ == "__main__":
    main()
