"""Case 003: check whether the exported skeleton carries bone offsets at all.

Every bone in the imported component reports the actor's position, a span of zero on all three axes.
That either means the skeleton has no offsets or that the accessor is not reporting the bind pose.
The glTF holds the joint nodes and their translations outright, so it can settle which.

    python Tools/diag_scatter_step5.py
"""

import json
import os

SOURCES = [
    ("boss001", "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/boss001.gltf"),
    ("bird108", "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/ue_import/108_bird.gltf"),
]


def report(name, path):
    if not os.path.exists(path):
        print("%s: missing %s" % (name, path))
        return

    gltf = json.loads(open(path, encoding="utf-8").read())
    nodes = gltf.get("nodes", [])
    skins = gltf.get("skins", [])

    print("")
    print("=== %s ===" % name)
    print("nodes: %d, skins: %d" % (len(nodes), len(skins)))

    if skins:
        joints = skins[0].get("joints", [])
        print("skin 0 joints: %d" % len(joints))

        zero = 0
        nonzero = 0
        largest = 0.0
        samples = []
        for joint in joints[:200]:
            if joint >= len(nodes):
                continue
            node = nodes[joint]
            translation = node.get("translation")
            if translation is None:
                zero += 1
                continue
            magnitude = max(abs(v) for v in translation)
            if magnitude == 0.0:
                zero += 1
            else:
                nonzero += 1
                largest = max(largest, magnitude)
                if len(samples) < 8:
                    samples.append((node.get("name", "?"), translation))

        print("  joints with zero translation: %d" % zero)
        print("  joints with non-zero translation: %d" % nonzero)
        print("  largest translation component: %.3f" % largest)
        for sample_name, sample in samples:
            print("    %-22s translation = %r" % (sample_name, sample))

        # The inverse bind matrices are the other half of the evidence.
        if "inverseBindMatrices" in skins[0]:
            accessor_index = skins[0]["inverseBindMatrices"]
            accessor = gltf["accessors"][accessor_index]
            print("  inverseBindMatrices accessor: count=%d, type=%s"
                  % (accessor["count"], accessor["type"]))
            identity_count = 0
            offset_count = 0
            for entry in gltf.get("bufferViews", []):
                pass
            # Decode enough of them to see whether any carries a translation.
            import base64
            import struct
            buffers = gltf.get("buffers", [])
            if buffers:
                uri = buffers[0].get("uri", "")
                if uri.startswith("data:"):
                    base = base64.b64decode(uri.partition(",")[2])
                else:
                    base = open(os.path.join(os.path.dirname(path), uri), "rb").read()
                view = gltf["bufferViews"][accessor["bufferView"]]
                offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
                for index in range(min(accessor["count"], 200)):
                    matrix = struct.unpack_from("<16f", base, offset + index * 64)
                    # Column-major: translation lives in elements 12, 13, 14.
                    tx, ty, tz = matrix[12], matrix[13], matrix[14]
                    if abs(tx) + abs(ty) + abs(tz) < 1e-6:
                        identity_count += 1
                    else:
                        offset_count += 1
                print("  IBM with zero translation: %d" % identity_count)
                print("  IBM with non-zero translation: %d" % offset_count)


def main():
    for name, path in SOURCES:
        report(name, path)


if __name__ == "__main__":
    main()
