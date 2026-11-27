"""Check whether a bone's readable transform fields agree with its prepared matrix.

Skinning only reproduces the bind pose if the joint node transform equals the bone's bind world
transform. The node transform is built from fRotAng, fPos, fRotAxis and fScale; if those disagree
with the mat4 that ships alongside them, the two halves of the calculation use different skeletons
and the mesh distorts no matter how correct the inverse bind matrices are.

    python Tools/compare_bone_transform.py
"""

import math
import struct

PATH = "C:/Users/tk/Desktop/moxiang-study/resources/mod/boss001.mod"


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def compose(angle, axis, position, scale):
    """Build a row-vector matrix from axis-angle, position and scale, as the client would."""
    length = math.sqrt(axis[0] ** 2 + axis[1] ** 2 + axis[2] ** 2)
    if length < 1e-9 or abs(angle) < 1e-9:
        rot = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    else:
        x, y, z = axis[0] / length, axis[1] / length, axis[2] / length
        c, s = math.cos(angle), math.sin(angle)
        t = 1.0 - c
        rot = [
            t * x * x + c, t * x * y - s * z, t * x * z + s * y,
            t * x * y + s * z, t * y * y + c, t * y * z - s * x,
            t * x * z - s * y, t * y * z + s * x, t * z * z + c,
        ]
    sx, sy, sz = scale
    return [
        rot[0] * sx, rot[1] * sx, rot[2] * sx, 0.0,
        rot[3] * sy, rot[4] * sy, rot[5] * sy, 0.0,
        rot[6] * sz, rot[7] * sz, rot[8] * sz, 0.0,
        position[0], position[1], position[2], 1.0,
    ]


def main():
    data = open(PATH, "rb").read()
    offset = 28
    shown = 0
    worst = 0.0
    checked = 0
    while offset + 12 <= len(data) and shown < 6:
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        payload = offset + 8
        if marker == 0xF5000000:
            name = read_name(data, payload + 196)
            tm = struct.unpack_from("<13f", data, payload + 4)
            matrix = struct.unpack_from("<16f", data, payload + 4 + 56)

            angle = tm[0]
            position = (tm[1], tm[2], tm[3])
            axis = (tm[4], tm[5], tm[6])
            scale = (tm[7], tm[8], tm[9])
            rebuilt = compose(angle, axis, position, scale)

            difference = max(abs(rebuilt[i] - matrix[i]) for i in range(16))
            checked += 1
            worst = max(worst, difference)
            print("%-18s rotAng=%.4f  diff=%.4f %s"
                  % (name[:18], angle, difference,
                     "MATCH" if difference < 1e-3 else "DIFFERENT"))
            if difference >= 1e-3:
                print("    from mat4 position (%.2f, %.2f, %.2f)"
                      % (matrix[12], matrix[13], matrix[14]))
                print("    from fields position (%.2f, %.2f, %.2f)" % position)
                print("    mat4 row0  [%s]" % ", ".join("%8.3f" % matrix[c] for c in range(4)))
                print("    rebuilt r0 [%s]" % ", ".join("%8.3f" % rebuilt[c] for c in range(4)))
            shown += 1
        offset = payload + size

    print("")
    print("worst difference across the first %d bones: %.4f" % (checked, worst))
    if worst > 1e-3:
        print("conclusion: the readable fields do NOT reproduce mat4, so the glTF node transform")
        print("and the inverse bind matrix describe different poses. Node transforms must be")
        print("derived from mat4 - decomposing it into translation, rotation and scale.")
    else:
        print("conclusion: the fields reproduce mat4, so the node transforms agree with the")
        print("inverse bind matrices and the distortion has another cause.")


if __name__ == "__main__":
    main()
