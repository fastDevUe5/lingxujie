"""Produce a skinless copy of the export so the appearance can be attributed.

The per-bone pose read blocks the Python thread, so the question "is skinning working or is this the
bind pose" needs a different probe. A static mesh has no skinning at all: it renders exactly the
vertices in the buffer, transformed only by the actor.

So: strip the skin from the glTF and import that. If the static mesh looks the same as the skeletal
one, the skeletal one is showing its bind pose and nothing is broken. If they differ, skinning is
changing the shape and whatever it produces is what the inverse bind matrices are doing.

    python Tools/make_skinless.py
"""

import json
import os

SOURCE = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001.gltf"
TARGET = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001_static.gltf"


def main():
    gltf = json.load(open(SOURCE, encoding="utf-8"))

    # Drop everything that makes it a skinned mesh.
    gltf.pop("skins", None)
    gltf.pop("animations", None)

    kept = 0
    for mesh in gltf.get("meshes", []):
        primitives = []
        for primitive in mesh.get("primitives", []):
            attributes = primitive.get("attributes", {})
            attributes.pop("JOINTS_0", None)
            attributes.pop("WEIGHTS_0", None)
            primitives.append(primitive)
            kept += 1
        mesh["primitives"] = primitives

    # The mesh node no longer references a skin.
    for node in gltf.get("nodes", []):
        node.pop("skin", None)

    # The skin's joint nodes are harmless but noise; leave the hierarchy in place since the meshes
    # no longer depend on it.

    output = json.loads(json.dumps(gltf))
    text = json.dumps(output, indent=1)
    open(TARGET, "w", encoding="utf-8").write(text)

    print("wrote %s" % TARGET)
    print("  primitives kept: %d" % kept)
    print("  skins: %d" % len(output.get("skins", [])))
    print("  animations: %d" % len(output.get("animations", [])))
    print("  bytes: %d" % os.path.getsize(TARGET))
    print("")
    print("the .bin is shared with the original export, so the geometry is identical.")


if __name__ == "__main__":
    main()
