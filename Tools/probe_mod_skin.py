"""Look for skin weights in a .mod file, which glTF needs to build a skin.

The animation import plan landed on a blocker: the engine's glTF animation translator binds its
skeletal tracks to a skeleton node, and a skeleton node exists only because a mesh declared one.
So an animation-only file will not produce AnimSequence, and the mesh has to come along - which
means vertices need bone indices and weights.

The format notes mention a "skinned/dense mesh" section but never describe how weights are
stored. This opens a real character model and looks for the pattern weights would leave:
small repeated integers for bone indices paired with floats summing to one.

    python Tools/probe_mod_skin.py
"""

import glob
import os
import struct

MOD_DIR = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
OBJECT_MESH = 0xF4000000
OBJECT_BONE = 0xF5000000


def header(data):
    return struct.unpack_from("<7I", data, 0)  # version, objects, materials, meshes, lights, cameras, bones


def find_sample():
    """The smallest model that actually carries bones."""
    best = None
    for path in sorted(glob.glob(os.path.join(MOD_DIR, "*.mod")), key=os.path.getsize):
        try:
            data = open(path, "rb").read(28)
        except OSError:
            continue
        fields = header(data)
        bones = fields[6]
        if 3 <= bones <= 40:
            size = os.path.getsize(path)
            if best is None or size < best[1]:
                best = (path, size, fields)
    return best


def scan_objects(data):
    """Count the object markers, and record where each mesh object starts."""
    markers = {}
    mesh_offsets = []
    for offset in range(0, len(data) - 8, 4):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in (OBJECT_MESH, OBJECT_BONE):
            markers[value] = markers.get(value, 0) + 1
            if value == OBJECT_MESH:
                mesh_offsets.append(offset)
    return markers, mesh_offsets


def count_small_byte_runs(data, start, length):
    """Weights typically appear as runs of small integers (bone index) plus floats.

    Counting one-byte values under 64 in a window gives a rough signal of whether such a run is
    there; the header and indices are dominated by larger or zero bytes.
    """
    window = data[start:start + length]
    small = sum(1 for byte in window if 0 < byte < 64)
    return small, len(window)


def main():
    sample = find_sample()
    if sample is None:
        print("no model with a sensible bone count found")
        return
    path, size, fields = sample
    version, objects, materials, meshes, lights, cameras, bones = fields
    print("sample: %s  (%d bytes)" % (os.path.basename(path), size))
    print("  header: objects=%d materials=%d meshes=%d lights=%d cameras=%d bones=%d"
          % (objects, materials, meshes, lights, cameras, bones))
    print("")

    data = open(path, "rb").read()
    markers, mesh_offsets = scan_objects(data)
    print("object markers found: %s"
          % {hex(key): value for key, value in markers.items()})
    print("tree objects (0xF7000000) present: %s" % (0xF7000000 in markers))
    print("")

    if not mesh_offsets:
        print("no mesh object markers located; the scan may need the block chain rather than a raw sweep")
        return

    print("first mesh objects and their byte neighbourhoods:")
    for offset in mesh_offsets[:5]:
        small, total = count_small_byte_runs(data, offset, 2048)
        print("  @%-8d small-byte density %.1f%% (%d/%d)"
              % (offset, 100.0 * small / total, small, total))
    print("")
    print("A skinned mesh section should show a dense run of small integers next to float data;")
    print("a static mesh would show indices and positions only, with far fewer small values.")


if __name__ == "__main__":
    main()
