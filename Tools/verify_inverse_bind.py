"""Compute real inverse bind matrices from the bone hierarchy.

Identity matrices work only when the bind pose is the rest pose with every bone at the origin. Real
skeletons place bones throughout the body, so skinning with identity pulls every vertex towards the
origin and the parts fly apart - which is exactly what the boss does.

The matrix for a joint is the inverse of that bone's world transform in the bind pose:

    IBM[i] = inverse(bindWorld[i])

In glTF a vertex goes through inverseBindMatrices into bone space and then through the joint's own
world transform back out, so with these the bind pose reproduces the input vertices exactly.

Two space changes have to be folded in. Vertices are shifted by the shared centroid so the model
sits at the origin; the bind matrices must carry the same shift. And the source is Z-up scaled to
centimetres while glTF is Y-up in metres, so each bind matrix has to be expressed the way the vertex
positions are.

    python Tools/verify_inverse_bind.py
"""

import math
import struct
import sys

sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")
import export_mod_anim_gltf as exporter


def mat_mul(a, b):
    """4x4 multiply in row-vector convention, matching the source's matrix layout."""
    out = [0.0] * 16
    for r in range(4):
        for c in range(4):
            total = 0.0
            for k in range(4):
                total += a[r * 4 + k] * b[k * 4 + c]
            out[r * 4 + c] = total
    return out


def mat_inverse(m):
    """Invert a 4x4 given as sixteen floats, row-major, treating it as an affine transform."""
    # Upper-left 3x3 is the rotation-scale part; the fourth row is the translation.
    a, b, c = m[0], m[1], m[2]
    d, e, f = m[4], m[5], m[6]
    g, h, i = m[8], m[9], m[10]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        return None
    inv_det = 1.0 / det
    r = [
        (e * i - f * h) * inv_det, (c * h - b * i) * inv_det, (b * f - c * e) * inv_det,
        (f * g - d * i) * inv_det, (a * i - c * g) * inv_det, (c * d - a * f) * inv_det,
        (d * h - e * g) * inv_det, (b * g - a * h) * inv_det, (a * e - b * d) * inv_det,
    ]
    tx, ty, tz = m[12], m[13], m[14]
    out = [
        r[0], r[1], r[2], 0.0,
        r[3], r[4], r[5], 0.0,
        r[6], r[7], r[8], 0.0,
        -(tx * r[0] + ty * r[3] + tz * r[6]),
        -(tx * r[1] + ty * r[4] + tz * r[7]),
        -(tx * r[2] + ty * r[5] + tz * r[8]),
        1.0,
    ]
    return out


def bind_world(bones):
    """Accumulate each bone's world transform up its parent chain."""
    by_index = {b["index"]: b for b in bones}
    cache = {}

    def resolve(bone, depth=0):
        index = bone["index"]
        if index in cache:
            return cache[index]
        if depth > 128:
            return bone["node_matrix"]

        local = bone.get("node_matrix")
        if local is None:
            local = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                     0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

        parent_index = bone["parent"]
        if parent_index in by_index:
            parent_world = resolve(by_index[parent_index], depth + 1)
            world = mat_mul(local, parent_world)
        else:
            world = local

        cache[index] = world
        return world

    for bone in bones:
        resolve(bone)
    return cache


def main():
    path = "C:/Users/tk/Desktop/moxiang-study/resources/mod/boss001.mod"
    objects = exporter.parse_mod(path)
    bones = [o for o in objects if o["marker"] == exporter.MOD_BONE_MARKER]
    meshes = [o for o in objects if o["marker"] == exporter.MOD_MESH_MARKER]
    print("boss001: %d bones, %d meshes" % (len(bones), len(meshes)))

    worlds = bind_world(bones)
    print("computed %d bind world matrices" % len(worlds))

    ok = 0
    singular = 0
    for bone in bones:
        world = worlds.get(bone["index"])
        inverse = mat_inverse(world) if world else None
        if inverse is None:
            singular += 1
        else:
            ok += 1
    print("invertible: %d, singular: %d" % (ok, singular))

    # Show a sample so the numbers can be sanity checked: a bone's world position and its inverse.
    sample = bones[0]
    world = worlds[sample["index"]]
    inverse = mat_inverse(world)
    print("")
    print("bone %r at world (%.2f, %.2f, %.2f)"
          % (sample["name"], world[12], world[13], world[14]))
    print("  world rows:")
    for row in range(4):
        print("    [%s]" % ", ".join("%9.3f" % world[row * 4 + c] for c in range(4)))
    print("  inverse rows:")
    for row in range(4):
        print("    [%s]" % ", ".join("%9.3f" % inverse[row * 4 + c] for c in range(4)))

    # Verify the round trip: world * inverse should be identity.
    product = mat_mul(world, inverse)
    error = max(abs(product[r * 4 + c] - (1.0 if r == c else 0.0))
                for r in range(4) for c in range(4))
    print("")
    print("round-trip error (should be ~0): %.2e" % error)

    # The tell for a bind pose that will not explode: bone world positions should be spread over the
    # body, not clustered at the origin.
    positions = [(worlds[b["index"]][12], worlds[b["index"]][13], worlds[b["index"]][14])
                 for b in bones if b["index"] in worlds]
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    zs = [p[2] for p in positions]
    print("bone world position span: X %.1f cm, Y %.1f cm, Z %.1f cm"
          % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))


if __name__ == "__main__":
    main()
