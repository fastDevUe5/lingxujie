"""Trace the block walk on one animation file, print every block, and say where it stops.

The density measurement says the average animation moves thirty-seven bones, and this file has
seventy block markers but yields six tracks. Both facts point at the walk stopping early rather
than at the file being sparse. Printing each block with its declared counts and the size the counts
require shows exactly which block ends the walk and why.

    python Tools/trace_anm_walk.py [path]
"""

import os
import struct
import sys

DEFAULT = "C:/Users/tk/Desktop/moxiang-study/resources/anm/Boss_cowf_01.anm"
MARKER = b"\x00\xF0\x00\x00"
HEADER = 152
POS = 20
ROT = 24
SCALE = 36


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    data = open(path, "rb").read()
    print("%s  %d bytes" % (path.rsplit("/", 1)[-1], len(data)))

    markers = [i for i in range(len(data) - 8) if data[i:i + 4] == MARKER]
    print("block markers found: %d, first ten at %s" % (len(markers), markers[:10]))
    print("")

    start = None
    for offset in markers:
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size >= HEADER and offset + 8 + size <= len(data):
            start = offset
            break
    if start is None:
        print("no usable first block")
        return

    print("%-4s %-8s %-8s %-6s %-5s %-5s %-6s %-9s %s"
          % ("#", "offset", "size", "pos", "rot", "scale", "mesh", "required", "name"))
    print("-" * 92)

    offset = start
    index = 0
    while offset + 8 <= len(data):
        if data[offset:offset + 4] != MARKER:
            print("stopped at %d: marker is %s" % (offset, data[offset:offset + 4].hex()))
            break
        size = struct.unpack_from("<I", data, offset + 4)[0]
        payload = offset + 8
        if size < HEADER or payload + size > len(data):
            print("stopped at %d: size %d implausible (payload %d, data %d)"
                  % (offset, size, payload, len(data)))
            break

        header = struct.unpack_from("<5I", data, payload)
        (_obj, rot_n, pos_n, scale_n, mesh_n) = header
        required = HEADER + pos_n * POS + rot_n * ROT + scale_n * SCALE
        name = read_name(data, payload + 20)

        flagged = ""
        if required > size:
            flagged = "  <-- counts do not fit"
        print("%-4d %-8d %-8d %-6d %-5d %-5d %-6d %-9d %s%s"
              % (index, offset, size, pos_n, rot_n, scale_n, mesh_n, required,
                 name[:26], flagged))

        if required > size:
            print("")
            print("the walk cannot continue: this block claims %d bytes of keys but is only %d."
                  % (required - HEADER, size - HEADER))
            print("payload hex: %s" % data[payload:payload + 64].hex())
            break

        offset = payload + size
        index += 1
        if index > 120:
            print("... stopped after 120 blocks")
            break

    print("")
    print("walked %d blocks, ended at %d of %d bytes (%d remaining)"
          % (index, offset, len(data), len(data) - offset))


if __name__ == "__main__":
    main()
