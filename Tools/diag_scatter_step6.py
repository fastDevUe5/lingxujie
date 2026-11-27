"""Case 003: test whether the inverse bind matrices are transposed twice.

invert() returns a list with the translation already in slots 12,13,14, and build() then transposes it
again. If that is the bug, the translation will be sitting in slots 3, 7 and 11 instead. Reading both
sets of slots settles it without changing anything.

    python Tools/diag_scatter_step6.py
"""

import base64
import json
import os
import struct

SOURCE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001.gltf"


def main():
    gltf = json.loads(open(SOURCE, encoding="utf-8").read())
    skin = gltf["skins"][0]
    accessor = gltf["accessors"][skin["inverseBindMatrices"]]
    buffers = gltf["buffers"]

    uri = buffers[0].get("uri", "")
    if uri.startswith("data:"):
        base = base64.b64decode(uri.partition(",")[2])
    else:
        base = open(os.path.join(os.path.dirname(SOURCE), uri), "rb").read()

    view = gltf["bufferViews"][accessor["bufferView"]]
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)

    print("accessor count: %d, type: %s" % (accessor["count"], accessor["type"]))
    print("")
    print("%-4s %-10s %-10s %-10s | %-10s %-10s %-10s"
          % ("idx", "slot3", "slot7", "slot11", "slot12", "slot13", "slot14"))
    print("-" * 78)

    nonzero_3 = nonzero_12 = 0
    for index in range(min(accessor["count"], 10)):
        matrix = struct.unpack_from("<16f", base, offset + index * 64)
        print("%-4d %-10.4f %-10.4f %-10.4f | %-10.4f %-10.4f %-10.4f"
              % (index, matrix[3], matrix[7], matrix[11],
                 matrix[12], matrix[13], matrix[14]))

    for index in range(accessor["count"]):
        matrix = struct.unpack_from("<16f", base, offset + index * 64)
        if abs(matrix[3]) + abs(matrix[7]) + abs(matrix[11]) > 1e-6:
            nonzero_3 += 1
        if abs(matrix[12]) + abs(matrix[13]) + abs(matrix[14]) > 1e-6:
            nonzero_12 += 1

    print("")
    print("matrices with translation in slots 3/7/11:  %d" % nonzero_3)
    print("matrices with translation in slots 12/13/14: %d" % nonzero_12)
    print("")
    if nonzero_3 > 0 and nonzero_12 == 0:
        print("VERDICT: the translation is in the wrong slots - the matrix was transposed twice")
    elif nonzero_12 > 0:
        print("VERDICT: translation is where glTF expects it; the collapse has another cause")
    else:
        print("VERDICT: no translation anywhere - the matrices are pure rotation or identity")


if __name__ == "__main__":
    main()
