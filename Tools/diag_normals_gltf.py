"""Case 002, step two: check the normals in the exported glTF rather than in the imported mesh.

Python cannot read normals off a StaticMesh here, but the glTF is plain JSON plus buffers and holds
exactly what the importer was given. If the normals are already degenerate in the file, the import
warning is reporting a fact about our own export rather than an engine quirk.

    python Tools/diag_normals_gltf.py
"""

import json
import math
import struct

SOURCE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_static.gltf"

COMPONENT_FLOAT = 5126
TYPE_CHANNELS = {"VEC3": 3, "VEC2": 2, "VEC4": 4, "SCALAR": 1}


def read_accessor(gltf, base, index):
    """Decode one accessor into a list of tuples."""
    accessor = gltf["accessors"][index]
    count = accessor["count"]
    kind = accessor["type"]
    channels = TYPE_CHANNELS[kind]
    component_type = accessor["componentType"]
    if component_type != COMPONENT_FLOAT:
        raise ValueError("only float accessors supported, got %r" % component_type)

    view = gltf["bufferViews"][accessor["bufferView"]]
    offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    stride = view.get("byteStride") or (4 * channels)
    raw = base[offset:offset + stride * count]

    out = []
    for i in range(count):
        start = i * stride
        values = struct.unpack_from("<" + "f" * channels, raw, start)
        out.append(values if channels > 1 else values[0])
    return out


def main():
    with open(SOURCE, "rb") as handle:
        raw = handle.read()

    # A .gltf embeds its buffer as base64 or points at a .bin; check which this is.
    gltf = json.loads(raw.decode("utf-8"))
    buffers = gltf.get("buffers", [])
    print("buffers: %d" % len(buffers))
    if not buffers:
        print("no buffer declared")
        return

    uri = buffers[0].get("uri", "")
    if uri.startswith("data:"):
        import base64
        header, _, payload = uri.partition(",")
        base = base64.b64decode(payload)
        print("buffer is embedded base64 (%d bytes)" % len(base))
    else:
        import os
        path = os.path.join(os.path.dirname(SOURCE), uri)
        base = open(path, "rb").read()
        print("buffer is external %r (%d bytes)" % (uri, len(base)))

    meshes = gltf.get("meshes", [])
    print("meshes: %d, primitives: %d"
          % (len(meshes), sum(len(m.get("primitives", [])) for m in meshes)))

    total = 0
    zero = 0
    near = 0
    nonfinite = 0
    no_normal = 0

    for mesh_index, mesh in enumerate(meshes):
        for prim_index, primitive in enumerate(mesh.get("primitives", [])):
            attributes = primitive.get("attributes", {})
            if "NORMAL" not in attributes:
                no_normal += 1
                other = sorted(attributes.keys())
                print("  mesh %d prim %d has NO normals; attributes: %r"
                      % (mesh_index, prim_index, other))
                continue
            normals = read_accessor(gltf, base, attributes["NORMAL"])
            local_zero = 0
            local_near = 0
            local_bad = 0
            for n in normals:
                length_sq = n[0] * n[0] + n[1] * n[1] + n[2] * n[2]
                if not math.isfinite(length_sq):
                    local_bad += 1
                    continue
                length = math.sqrt(length_sq)
                if length == 0.0:
                    local_zero += 1
                elif abs(length - 1.0) > 1e-3:
                    local_near += 1
            total += len(normals)
            zero += local_zero
            near += local_near
            nonfinite += local_bad
            if local_zero or local_near or local_bad:
                print("  mesh %d prim %d: %d normals, %d zero, %d non-unit, %d non-finite"
                      % (mesh_index, prim_index, len(normals), local_zero, local_near, local_bad))

    print("")
    print("TOTAL normals: %d" % total)
    print("  exactly zero:      %d" % zero)
    print("  not unit length:   %d" % near)
    print("  non-finite (NaN):  %d" % nonfinite)
    print("  primitives with no normals at all: %d" % no_normal)
    if total:
        bad = zero + near + nonfinite
        print("  degenerate fraction: %.2f%%" % (100.0 * bad / total))
    print("")
    print("note: tangents are not stored in glTF; the importer derives them, which is why the")
    print("engine reports NaNs in tangent space rather than missing tangent data")


if __name__ == "__main__":
    main()
