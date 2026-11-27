"""Case 002, step three: classify the normals the .mod actually supplies.

The exporter substitutes (0,0,1) when a block declares no normals, so a zero in the glTF can only come
from the file. This reuses the exporter's own parser - a second implementation could disagree for
reasons that have nothing to do with the question - and reports each block's flag alongside a count of
zero, filler and unnormalised normals.

    python Tools/diag_normals_mod.py
"""

import math
import sys

MOD = "C:/Users/tk/Desktop/moxiang-study/resources/mod/boss001.mod"
sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")


def classify(normals):
    zero = flat_up = non_unit = nonfinite = 0
    for n in normals:
        length_sq = n[0] * n[0] + n[1] * n[1] + n[2] * n[2]
        if not math.isfinite(length_sq):
            nonfinite += 1
        elif length_sq == 0.0:
            zero += 1
        elif n[0] == 0.0 and n[1] == 0.0 and n[2] == 1.0:
            flat_up += 1
        elif abs(math.sqrt(length_sq) - 1.0) > 1e-3:
            non_unit += 1
    return zero, flat_up, non_unit, nonfinite


def main():
    import export_mod_anim_gltf as ex

    objects = ex.parse_mod(MOD)
    print("mod: %s" % MOD)
    print("objects parsed: %d" % len(objects))

    meshes = [o for o in objects if o["marker"] == ex.MOD_MESH_MARKER]
    print("mesh blocks: %d" % len(meshes))

    total = zero = flat_up = non_unit = nonfinite = 0
    without = 0

    for index, block in enumerate(meshes):
        normals = block["normals"]
        has = block["has_normals"]
        flag = block["mesh_flag"]
        z, f, u, nf = classify(normals)
        if not has:
            without += 1
        total += len(normals)
        zero += z
        flat_up += f
        non_unit += u
        nonfinite += nf
        print("  mesh %2d: flag=0x%08X has=%-5s verts=%-4d zero=%-4d filler=%-4d non_unit=%-4d nan=%d"
              % (index, flag, has, len(normals), z, f, u, nf))

    print("")
    print("TOTAL normals: %d" % total)
    print("  exactly zero:        %d" % zero)
    print("  the (0,0,1) filler:  %d" % flat_up)
    print("  not unit length:     %d" % non_unit)
    print("  non-finite:          %d" % nonfinite)
    print("  blocks without normals: %d of %d" % (without, len(meshes)))
    if total:
        bad = zero + non_unit + nonfinite
        print("  degenerate: %d (%.2f%%)" % (bad, 100.0 * bad / total))

    print("")
    print("interpretation:")
    print("  zero > 0 and has_normals=True  -> the .mod stores zero normals itself")
    print("  filler > 0 and has_normals=False -> exporter substitution, expected")
    print("  non_unit > 0 and has_normals=True -> the .mod stores unnormalised normals")


if __name__ == "__main__":
    main()
