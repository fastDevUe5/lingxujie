"""Patch the inverse bind matrices properly: correct slot order and correct units.

The first patch moved the translation into the slots glTF reads and restored bone offsets, but the
skeleton came out four hundred metres tall. Mesh positions are scaled from centimetres to metres while
the bind matrices are built from centimetre-space node matrices, so the rotation is right and the
translation is a hundred times too large.

This second patch fixes both and can also be run with scaling disabled, so the two effects stay
separated.

    python Tools/patch_ibm2.py            # slots plus scale
    python Tools/patch_ibm2.py --noscalc  # slots only
"""

import json
import os
import shutil
import struct
import sys

SOURCE_GLTF = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001.gltf"
TARGET_GLTF = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_ibmfix2.gltf"

# The mesh positions are written as cm * 0.01, so the bind translation needs the same factor.
POSITION_SCALE = 0.01


def main():
    apply_scale = "--noscalc" not in sys.argv
    gltf = json.loads(open(SOURCE_GLTF, encoding="utf-8").read())

    buffers = gltf.get("buffers", [])
    if not buffers:
        print("no buffer")
        return
    uri = buffers[0].get("uri", "")
    if uri.startswith("data:"):
        print("embedded buffer; this script expects an external .bin")
        return

    source_bin = os.path.join(os.path.dirname(SOURCE_GLTF), uri)
    target_bin_name = os.path.splitext(os.path.basename(TARGET_GLTF))[0] + ".bin"
    target_bin = os.path.join(os.path.dirname(SOURCE_GLTF), target_bin_name)
    shutil.copyfile(source_bin, target_bin)

    data = bytearray(open(target_bin, "rb").read())

    skin = gltf["skins"][0]
    accessor = gltf["accessors"][skin["inverseBindMatrices"]]
    view = gltf["bufferViews"][accessor["bufferView"]]
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    count = accessor["count"]

    moved = 0
    for index in range(count):
        base = offset + index * 64
        values = list(struct.unpack_from("<16f", data, base))
        slots_3 = (values[3], values[7], values[11])
        if not any(abs(v) > 1e-6 for v in slots_3):
            continue
        tx, ty, tz = slots_3
        if apply_scale:
            tx *= POSITION_SCALE
            ty *= POSITION_SCALE
            tz *= POSITION_SCALE
        values[12], values[13], values[14] = tx, ty, tz
        values[3] = values[7] = values[11] = 0.0
        struct.pack_into("<16f", data, base, *values)
        moved += 1

    open(target_bin, "wb").write(bytes(data))
    gltf["buffers"][0]["uri"] = target_bin_name
    open(TARGET_GLTF, "w", encoding="utf-8").write(json.dumps(gltf, indent=1))

    print("scale applied: %s" % apply_scale)
    print("patched %d of %d matrices" % (moved, count))
    print("wrote %s and %s"
          % (os.path.basename(TARGET_GLTF), os.path.basename(target_bin)))

    # Show the first few translations so the magnitude is visible before importing anything.
    for index in range(min(4, count)):
        values = struct.unpack_from("<16f", data, offset + index * 64)
        print("  matrix %d translation = (%.4f, %.4f, %.4f)"
              % (index, values[12], values[13], values[14]))


if __name__ == "__main__":
    main()
