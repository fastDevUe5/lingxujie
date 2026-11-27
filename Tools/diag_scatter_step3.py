"""Case 003: measure the boss geometry in source space, before any axis conversion.

The exporter maps (x, y, z) to (x, z, -y), which turns a Y-up model into Z-up - correct if the source
is Y-up, and a rotation onto its back if the source is already Z-up. Which it is can only be settled by
measuring the raw vertices, so this reports the extent along each source axis.

    python Tools/diag_scatter_step3.py
"""

import sys

MODS = [
    ("boss001", "C:/Users/tk/Desktop/moxiang-study/resources/mod/boss001.mod"),
    ("boss_cowf", "C:/Users/tk/Desktop/moxiang-study/resources/mod/boss_cowf_01.mod"),
    ("bird 108", "C:/Users/tk/Desktop/moxiang-study/resources/mod/108_bird.mod"),
]

sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")


def main():
    import export_mod_anim_gltf as ex

    for name, path in MODS:
        try:
            objects = ex.parse_mod(path)
        except Exception as error:  # noqa: BLE001
            print("%-12s parse failed: %r" % (name, error))
            continue

        meshes = [o for o in objects if o["marker"] == ex.MOD_MESH_MARKER]
        if not meshes:
            print("%-12s no mesh blocks" % name)
            continue

        xs = []
        ys = []
        zs = []
        for block in meshes:
            for p in block["positions"]:
                xs.append(p[0])
                ys.append(p[1])
                zs.append(p[2])

        ex_x = max(xs) - min(xs)
        ex_y = max(ys) - min(ys)
        ex_z = max(zs) - min(zs)

        print("")
        print("%s (%d mesh blocks, %d verts)" % (name, len(meshes), len(xs)))
        print("  source extent X = %.1f cm" % ex_x)
        print("  source extent Y = %.1f cm" % ex_y)
        print("  source extent Z = %.1f cm" % ex_z)
        longest = max(("X", ex_x), ("Y", ex_y), ("Z", ex_z), key=lambda kv: kv[1])
        print("  longest source axis: %s" % longest[0])

        # What the current export transform produces.
        print("  after (x, z, -y):  X=%.1f  Y=%.1f  Z=%.1f"
              % (ex_x, ex_z, ex_y))
        print("  after (x, -z, y):  X=%.1f  Y=%.1f  Z=%.1f"
              % (ex_x, ex_z, ex_y))

        if ex_z > ex_y:
            print("  -> source is Z-tall; (x, z, -y) lays it down. Keeping Z as Z would stand it up.")
        else:
            print("  -> source is Y-tall; (x, z, -y) is the standard Y-up to Z-up conversion.")


if __name__ == "__main__":
    main()
