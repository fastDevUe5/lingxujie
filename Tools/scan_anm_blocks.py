"""Find every 0xF000 block by scanning, since the header length is not constant.

The summary said the header is one hundred sixty bytes. For this file the first block begins at two
hundred six, and the bytes in between look like heap addresses, which means the writer dumped a
runtime structure rather than a clean header. So the header length has to be discovered per file
rather than assumed.

    python Tools/scan_anm_blocks.py [path]
"""

import os
import struct
import sys

DEFAULT = "C:/Users/tk/Desktop/moxiang-study/resources/anm/108_birda.anm"


def read_name(data, offset, length=40):
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
    print("%s  %d bytes" % (os.path.basename(path), len(data)))

    # A block is 0xF000 as a 32-bit word followed by a plausible size.
    candidates = []
    for offset in range(0, len(data) - 8):
        if data[offset] == 0x00 and data[offset + 1] == 0xF0 \
                and data[offset + 2] == 0x00 and data[offset + 3] == 0x00:
            size = struct.unpack_from("<I", data, offset + 4)[0]
            if 0 < size < len(data) - offset:
                candidates.append((offset, size))

    print("plausible 0xF000 blocks: %d" % len(candidates))
    print("")
    for index, (offset, size) in enumerate(candidates[:20]):
        # Name is somewhere in the first seventy payload bytes after the eight header bytes.
        name = ""
        for probe in range(offset + 8, min(offset + 8 + 72, offset + 8 + size) - 8):
            chunk = data[probe:probe + 8]
            if all(32 <= byte < 127 or byte >= 0x80 for byte in chunk):
                name = read_name(data, probe, 40)
                break
        print("  [%2d] @%-7d size=%-7d name=%r" % (index, offset, size, name[:30]))

    print("")
    # Walk from the first candidate and see whether the chain is contiguous.
    if candidates:
        offset, size = candidates[0]
        count = 0
        walked = []
        while True:
            found = None
            for block_offset, block_size in candidates:
                if block_offset == offset:
                    found = (block_offset, block_size)
                    break
            if found is None:
                break
            walked.append(found)
            offset = found[0] + 8 + found[1]
            count += 1
            if count > 200:
                break
        print("contiguous chain from %d: %d blocks" % (candidates[0][0], len(walked)))
        if walked:
            first, last = walked[0], walked[-1]
            print("  spans %d..%d" % (first[0], last[0] + 8 + last[1]))
            print("  file is %d bytes, so %d bytes follow the last block"
                  % (len(data), len(data) - (last[0] + 8 + last[1])))
    print("")


if __name__ == "__main__":
    main()
