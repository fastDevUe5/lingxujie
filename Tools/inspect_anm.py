"""Inspect one anm file's actual byte layout, rather than trusting the summary.

The research notes describe the container as a hundred and sixty byte header followed by tagged
blocks, with each block payload holding a name, some zeros, a type word, a count and then keyframes.
That description is not precise enough to parse from, so this dumps the first block in detail and
finds where the sections and their records actually begin.

    python Tools/inspect_anm.py [path]
"""

import os
import struct
import sys

DEFAULT = "C:/Users/tk/Desktop/moxiang-study/resources/anm/108_birda.anm"
MARKER = 0xF000


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    data = open(path, "rb").read()
    print("%s  %d bytes" % (os.path.basename(path), len(data)))
    print("")

    # Header words.
    print("header (first 160 bytes, as 32-bit words):")
    for offset in range(0, 160, 4):
        value = struct.unpack_from("<I", data, offset)[0]
        print("  +%-4d %-12d 0x%08X" % (offset, value, value))
    print("")

    # First block at 160.
    print("block at 160:")
    tag = struct.unpack_from("<H", data, 160)[0]
    length = struct.unpack_from("<I", data, 162)[0]
    print("  tag=0x%04X length=%d" % (tag, length))
    payload = 166
    print("  payload starts at %d" % payload)
    print("  first 96 payload bytes:")
    for row in range(0, 96, 16):
        chunk = data[payload + row:payload + row + 16]
        hexed = " ".join("%02X" % byte for byte in chunk)
        text = "".join(chr(byte) if 32 <= byte < 127 else "." for byte in chunk)
        print("    +%-3d %-48s %s" % (row, hexed, text))
    print("")

    # Walk all blocks and report their sizes.
    print("all blocks:")
    offset = 160
    index = 0
    while offset + 6 <= len(data):
        tag = struct.unpack_from("<H", data, offset)[0]
        length = struct.unpack_from("<I", data, offset + 2)[0]
        if tag != MARKER:
            print("  stop at %d: tag 0x%04X" % (offset, tag))
            break
        if length <= 0 or offset + 6 + length > len(data):
            print("  stop at %d: length %d implausible" % (offset, length))
            break
        # Name is somewhere in the payload; show the first printable run.
        payload = offset + 6
        name = ""
        for probe in range(payload, min(payload + 64, payload + length) - 4):
            chunk = data[probe:probe + 12]
            if all(32 <= byte < 127 or byte >= 0x80 for byte in chunk):
                raw = data[probe:probe + 40]
                end = raw.find(b"\x00")
                if end > 0:
                    raw = raw[:end]
                try:
                    name = raw.decode("gbk")
                except UnicodeDecodeError:
                    name = raw.decode("latin-1", errors="replace")
                break
        print("  [%2d] @%-7d length=%-7d name~%r" % (index, offset, length, name[:28]))
        offset = payload + length
        index += 1
    print("")
    print("ended at %d of %d bytes, %d bytes after the blocks" % (offset, len(data), len(data) - offset))


if __name__ == "__main__":
    main()
