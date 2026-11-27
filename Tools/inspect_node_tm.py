"""Dump the object transform that ships inside every base object header.

NODE_TM holds a rotation angle and axis, a position, a scale, and two prepared matrices. If the mesh
lies flat, either the vertices are authored lying down and this transform raises them, or the
transform is identity and something else is wrong. Printing it decides which.

    python Tools/inspect_node_tm.py
"""

import struct
import sys

DEFAULT = "C:/Users/tk/Desktop/moxiang-study/resources/mod/198_bobu.mod"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    data = open(path, "rb").read()
    print("%s  %d bytes" % (path.rsplit("/", 1)[-1], len(data)))
    print("")

    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        payload = offset + 8

        if marker == 0xF4000000:
            tm = struct.unpack_from("<13f", data, payload + 4)
            print("MESH @%d  size=%d" % (offset, size))
            print("  fRotAng      %.4f" % tm[0])
            print("  fPos         (%.3f, %.3f, %.3f)" % (tm[1], tm[2], tm[3]))
            print("  fRotAxis     (%.4f, %.4f, %.4f)" % (tm[4], tm[5], tm[6]))
            print("  fScale       (%.4f, %.4f, %.4f)" % (tm[7], tm[8], tm[9]))
            print("  fScaleAxis   (%.4f, %.4f, %.4f)" % (tm[10], tm[11], tm[12]))

            mat4 = struct.unpack_from("<16f", data, payload + 4 + 56)
            identity = (
                abs(mat4[0] - 1) < 1e-5 and abs(mat4[5] - 1) < 1e-5
                and abs(mat4[10] - 1) < 1e-5 and abs(mat4[15] - 1) < 1e-5
                and all(abs(mat4[i]) < 1e-5
                        for i in (1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14)))
            print("  mat4  %s" % ("IDENTITY" if identity else "non-identity"))
            for row in range(4):
                print("      [%s]" % ", ".join("%9.4f" % mat4[row * 4 + c] for c in range(4)))

            inverse = struct.unpack_from("<16f", data, payload + 4 + 56 + 64)
            inverse_identity = (
                abs(inverse[0] - 1) < 1e-5 and abs(inverse[5] - 1) < 1e-5
                and abs(inverse[10] - 1) < 1e-5 and abs(inverse[15] - 1) < 1e-5)
            print("  mat4Inverse  %s" % ("IDENTITY" if inverse_identity else "non-identity"))
            for row in range(4):
                print("      [%s]" % ", ".join("%9.4f" % inverse[row * 4 + c] for c in range(4)))
            print("")
        offset = payload + size


if __name__ == "__main__":
    main()
