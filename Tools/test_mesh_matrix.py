"""Test whether applying a mesh block's matrix is what scatters the parts.

Every fix so far preserved the same odd arrangement, and the skinless copy has the same bounds as
the skinned one, which says the arrangement comes from the vertex data rather than from skinning.
The remaining assumption is that each mesh block's mat4 should be applied at all.

Two readings are possible and they disagree: either the matrix places each part in world space, or
the vertices already are in world space and the matrix is a bind-pose artifact. Comparing the bounds
with and without it decides between them, because a model whose parts are already positioned will
come together when the matrix stops being applied.

    python Tools/test_mesh_matrix.py
"""

import struct
import sys

sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")
import export_mod_anim_gltf as exporter

PATH = "C:/Users/tk/Desktop/moxiang-study/resources/mod/boss001.mod"


def main():
    data = open(PATH, "rb").read()
    objects = exporter.parse_mod(PATH)
    meshes = [o for o in objects if o["marker"] == exporter.MOD_MESH_MARKER]
    print("boss001: %d mesh blocks" % len(meshes))

    with_matrix = []
    without_matrix = []
    for mesh in meshes:
        block = mesh
        matrix = mesh.get("node_matrix")
        for p in block["positions"]:
            without_matrix.append(p)
            if matrix:
                with_matrix.append((
                    p[0] * matrix[0] + p[1] * matrix[4] + p[2] * matrix[8] + matrix[12],
                    p[0] * matrix[1] + p[1] * matrix[5] + p[2] * matrix[9] + matrix[13],
                    p[0] * matrix[2] + p[1] * matrix[6] + p[2] * matrix[10] + matrix[14],
                ))
            else:
                with_matrix.append(p)

    def extent(points):
        if not points:
            return (0.0, 0.0, 0.0)
        return tuple(max(p[i] for p in points) - min(p[i] for p in points) for i in range(3))

    a = extent(with_matrix)
    b = extent(without_matrix)

    print("")
    print("applying each mesh's mat4:")
    print("  total extent %.1f x %.1f x %.1f cm   (%d vertices)" % (a[0], a[1], a[2], len(with_matrix)))
    print("ignoring each mesh's mat4:")
    print("  total extent %.1f x %.1f x %.1f cm   (%d vertices)" % (b[0], b[1], b[2], len(without_matrix)))
    print("")

    # Per-block spread: how far apart are the blocks' own centres in each reading?
    def centres(points_list):
        return [tuple(sum(p[i] for p in pts) / len(pts) for i in range(3)) for pts in points_list if pts]

    raw_centres = []
    placed_centres = []
    for mesh in meshes:
        block = mesh
        if not block["positions"]:
            continue
        raw_centres.append(block["positions"])
        matrix = mesh.get("node_matrix")
        if matrix:
            placed_centres.append([
                (p[0] * matrix[0] + p[1] * matrix[4] + p[2] * matrix[8] + matrix[12],
                 p[0] * matrix[1] + p[1] * matrix[5] + p[2] * matrix[9] + matrix[13],
                 p[0] * matrix[2] + p[1] * matrix[6] + p[2] * matrix[10] + matrix[14])
                for p in block["positions"]])
        else:
            placed_centres.append(block["positions"])

    raw_c = centres(raw_centres)
    placed_c = centres(placed_centres)

    def spread(cs):
        return tuple(max(c[i] for c in cs) - min(c[i] for c in cs) for i in range(3)) if cs else (0, 0, 0)

    print("spread between block centres, raw:   %.1f x %.1f x %.1f cm" % spread(raw_c))
    print("spread between block centres, placed: %.1f x %.1f x %.1f cm" % spread(placed_c))
    print("")
    print("if the raw spread is already sensible for a body and the placed spread is larger,")
    print("the matrix is inflating the arrangement and should not be applied.")


if __name__ == "__main__":
    main()
