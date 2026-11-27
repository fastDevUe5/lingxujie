"""Parse an anm block using the client's own structure, now that the sizes agree.

The block payload is exactly one hundred fifty-two bytes of FILE_MOTION_OBJECT_HEADER, which is the
size the header struct computes to - five words, a hundred twenty-eight byte name, and a four byte
flags word. Blocks of size 152 have no keys; blocks of size 3416 and 6116 do.

Key order follows the client reader: positions, then rotations, then scales. Their record sizes are
twenty, twenty-four and forty bytes.

    python Tools/parse_anm_motion.py [path]
"""

import os
import struct
import sys

DEFAULT = "C:/Users/tk/Desktop/moxiang-study/resources/anm/108_birda.anm"

MOTION_OBJECT_HEADER = 152
POS_KEY = 20
ROT_KEY = 24
SCALE_KEY = 40


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def parse(path):
    data = open(path, "rb").read()

    # The first block is found by scanning, not by a fixed offset.
    start = None
    for offset in range(0, len(data) - 8):
        if data[offset:offset + 4] == b"\x00\xF0\x00\x00":
            size = struct.unpack_from("<I", data, offset + 4)[0]
            if size >= MOTION_OBJECT_HEADER and offset + 8 + size <= len(data):
                start = offset
                break
    if start is None:
        print("%s: no block found" % path)
        return

    print("%s  %d bytes  first block at %d" % (os.path.basename(path), len(data), start))
    print("")

    offset = start
    index = 0
    total_frames = 0
    while offset + 8 <= len(data):
        if data[offset:offset + 4] != b"\x00\xF0\x00\x00":
            print("stop at %d: not a block marker" % offset)
            break
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        if size < MOTION_OBJECT_HEADER or payload + size > len(data):
            print("stop at %d: size %d implausible" % (offset, size))
            break

        (obj_index, rot_keys, pos_keys, scale_keys,
         mesh_keys) = struct.unpack_from("<5I", data, payload)
        name = read_name(data, payload + 20)
        flags = struct.unpack_from("<I", data, payload + 148)[0]

        keys_bytes = pos_keys * POS_KEY + rot_keys * ROT_KEY + scale_keys * SCALE_KEY
        expected = MOTION_OBJECT_HEADER + keys_bytes
        match = "OK" if expected == size else "MISMATCH (%d vs %d)" % (expected, size)

        print("  [%2d] @%-7d size=%-6d name=%-22r rot=%-4d pos=%-4d scale=%-4d mesh=%-3d flags=0x%X  %s"
              % (index, offset, size, name[:22], rot_keys, pos_keys, scale_keys,
                 mesh_keys, flags, match))

        if rot_keys:
            total_frames = max(total_frames, rot_keys)
        offset = payload + size
        index += 1

    print("")
    print("  blocks=%d, longest rotation track=%d frames" % (index, total_frames))
    print("  ended at %d, tail %d bytes" % (offset, len(data) - offset))

    # Show the first few keyframes of the first block that has them.
    offset = start
    for _ in range(index):
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        (obj_index, rot_keys, pos_keys, scale_keys,
         mesh_keys) = struct.unpack_from("<5I", data, payload)
        if rot_keys and pos_keys:
            cursor = payload + MOTION_OBJECT_HEADER
            print("")
            print("  first block with keys: %r" % read_name(data, payload + 20))
            print("    positions:")
            for i in range(min(3, pos_keys)):
                ticks, frame, x, y, z = struct.unpack_from("<II3f", data, cursor + i * POS_KEY)
                print("      [%d] ticks=%-6d frame=%-5d pos=(%.3f, %.3f, %.3f)"
                      % (i, ticks, frame, x, y, z))
            cursor += pos_keys * POS_KEY
            print("    rotations:")
            for i in range(min(3, rot_keys)):
                ticks, frame, qx, qy, qz, qw = struct.unpack_from("<II4f", data, cursor + i * ROT_KEY)
                length = (qx * qx + qy * qy + qz * qz + qw * qw) ** 0.5
                print("      [%d] ticks=%-6d frame=%-5d quat=(%.4f, %.4f, %.4f, %.4f) len=%.4f"
                      % (i, ticks, frame, qx, qy, qz, qw, length))
            break
        offset = payload + size


def main():
    for path in (sys.argv[1:] or [DEFAULT]):
        try:
            parse(path)
        except OSError as error:
            print("%s: %s" % (path, error))
        print("=" * 90)


if __name__ == "__main__":
    main()
