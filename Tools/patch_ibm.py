"""Patch the inverse bind matrices in a copy of the glTF and leave the original alone.

The diagnosis says the translation sits in slots 3, 7 and 11 because invert's already-column-major
result was transposed again. Undoing that transposition means moving the values back to 12, 13, 14 -
which is exactly what swapping the matrix between row-major and column-major interpretation does.

This writes a new .gltf and .bin next to the original, never over them, so the fix can be measured
before anything is decided.

    python Tools/patch_ibm.py
"""

import json
import os
import shutil
import struct

SOURCE_GLTF = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001.gltf"
TARGET_GLTF = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_ibmfix.gltf"


def main():
    if not os.path.exists(SOURCE_GLTF):
        print("missing %s" % SOURCE_GLTF)
        return

    gltf = json.loads(open(SOURCE_GLTF, encoding="utf-8").read())

    # The buffer is a sibling .bin; copy it under the new name so the patched glTF is self-consistent.
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
    print("copied buffer -> %s" % os.path.basename(target_bin))

    data = bytearray(open(target_bin, "rb").read())

    skin = gltf["skins"][0]
    accessor_index = skin["inverseBindMatrices"]
    accessor = gltf["accessors"][accessor_index]
    view = gltf["bufferViews"][accessor["bufferView"]]
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    count = accessor["count"]

    moved = 0
    for index in range(count):
        base = offset + index * 64
        values = list(struct.unpack_from("<16f", data, base))
        slots_3 = (values[3], values[7], values[11])
        slots_12 = (values[12], values[13], values[14])
        if any(abs(v) > 1e-6 for v in slots_3) and all(abs(v) < 1e-6 for v in slots_12):
            # Put the translation where a conformant reader looks, and zero the old slots.
            values[12], values[13], values[14] = slots_3
            values[3] = values[7] = values[11] = 0.0
            struct.pack_into("<16f", data, base, *values)
            moved += 1

    print("moved the translation on %d of %d matrices" % (moved, count))

    open(target_bin, "wb").write(bytes(data))

    gltf["buffers"][0]["uri"] = target_bin_name
    open(TARGET_GLTF, "w", encoding="utf-8").write(json.dumps(gltf, indent=1))
    print("wrote %s" % os.path.basename(TARGET_GLTF))

    # Read the result back the same way the diagnosis did, to confirm the patch landed.
    check = json.loads(open(TARGET_GLTF, encoding="utf-8").read())
    check_accessor = check["accessors"][check["skins"][0]["inverseBindMatrices"]]
    check_view = check["bufferViews"][check_accessor["bufferView"]]
    check_offset = check_view.get("byteOffset", 0) + check_accessor.get("byteOffset", 0)
    in_12 = sum(
        1 for i in range(check_accessor["count"])
        if any(abs(v) > 1e-6
               for v in struct.unpack_from("<3f", data, check_offset + i * 64 + 48))
    )
    print("verification: matrices with translation in slots 12/13/14: %d" % in_12)


if __name__ == "__main__":
    main()
