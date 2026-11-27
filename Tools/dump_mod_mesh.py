"""Dump a mesh object's sub-structure, trying both size conventions.

The first attempt walked the object list and landed on type zero repeatedly, which means the
advance is wrong - either the material block's size field excludes its own eight-byte header, or
it includes it. Rather than assume, this checks both readings against a fact that cannot be
guessed: the object types must come out as the known markers (0xF4 mesh, 0xF5 bone). Whichever
convention produces those is the right one.

    python Tools/dump_mod_mesh.py
"""

import glob
import os
import struct

MOD_DIR = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
BASE_OBJECT_SIZE = 324
KNOWN = {0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7}
OBJ_NAMES = {
    0xF1: "LIGHT", 0xF2: "CAMERA", 0xF3: "CAMERA_TARGET", 0xF4: "MESH",
    0xF5: "BONE", 0xF6: "ILLUSION_MESH", 0xF7: "COLLISION",
}


def pick_sample():
    best = None
    for path in sorted(glob.glob(os.path.join(MOD_DIR, "*.mod")), key=os.path.getsize):
        try:
            data = open(path, "rb").read()
        except OSError:
            continue
        if len(data) < 40:
            continue
        fields = struct.unpack_from("<7I", data, 0)
        objects, bones, meshes = fields[1], fields[6], fields[3]
        if bones >= 2 and meshes >= 1:
            if best is None or len(data) < best[1]:
                best = (path, len(data), fields)
    return best


def walk(data, header_in_size):
    """Return (materials, objects) using the chosen size convention."""
    version, object_count, material_count = struct.unpack_from("<3I", data, 0)
    extra = 0 if header_in_size else 8
    offset = 28

    materials = []
    for _ in range(material_count):
        if offset + 8 > len(data):
            return materials, []
        mtype, msize = struct.unpack_from("<2I", data, offset)
        materials.append((mtype, msize, offset))
        offset += msize + extra

    objects = []
    for _ in range(object_count):
        if offset + 8 > len(data):
            break
        otype, osize = struct.unpack_from("<2I", data, offset)
        objects.append((otype, osize, offset))
        offset += osize + extra
    return materials, objects


def score(objects):
    """How many object types look like real markers."""
    good = 0
    for otype, osize, offset in objects:
        if (otype >> 24) in KNOWN:
            good += 1
    return good


def main():
    sample = pick_sample()
    if sample is None:
        print("no suitable model found")
        return
    path, size, fields = sample
    print("sample: %s (%d bytes)" % (os.path.basename(path), size))
    print("  header: objects=%d materials=%d meshes=%d bones=%d"
          % (fields[1], fields[2], fields[3], fields[6]))
    print("")

    data = open(path, "rb").read()

    for header_in_size in (True, False):
        mats, objs = walk(data, header_in_size)
        good = score(objs)
        label = "size includes header" if header_in_size else "size excludes header"
        print("convention %-22s -> %d/%d objects recognise, %d/%d materials"
              % (label, good, len(objs), len(mats), fields[2]))
        if good >= max(1, len(objs) - 1):
            print("   ^^ this one reads correctly")
        print("")

    mats, objs = walk(data, True) if score(walk(data, True)[1]) >= score(walk(data, False)[1]) else walk(data, False)

    print("chosen walk:")
    for otype, osize, offset in objs:
        kind = OBJ_NAMES.get(otype >> 24, hex(otype >> 24))
        name_raw = data[offset + 8 + 196:offset + 8 + 196 + 128].split(b"\x00")[0]
        name = name_raw.decode("latin-1", errors="replace")
        print("  %-14s size %-7d @%-7d name=%s" % (kind, osize, offset, name or "?"))
    print("")

    for otype, osize, offset in objs:
        if (otype >> 24) != 0xF4:
            continue
        payload = data[offset + 8:offset + osize]
        after = payload[BASE_OBJECT_SIZE:]
        print("MESH payload %d bytes; %d after the base object header"
              % (len(payload), len(after)))
        for row in range(0, min(128, len(after)), 16):
            chunk = after[row:row + 16]
            hexed = " ".join("%02x" % byte for byte in chunk)
            words = struct.unpack_from("<%dI" % (len(chunk) // 4), after, row)
            print("  +%-3d %-49s %s" % (row, hexed, " ".join(str(w) for w in words)))
        print("")


if __name__ == "__main__":
    main()
