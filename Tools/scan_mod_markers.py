"""Locate the block markers exactly, rather than trusting an offset computed by hand.

Two attempts have now assumed where the first block starts and both were off. Scanning for the
0xF000 marker and printing what follows it is faster and does not depend on getting the header
length right.

    python Tools/scan_mod_markers.py
"""

import struct

SAMPLES = ["w25260", "jp03_dht00"]
BASE = "C:/Users/tk/Desktop/moxiang-study/resources/mod/%s.mod"


def read_name(data, offset, length=32):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end >= 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def main():
    for name in SAMPLES:
        data = open(BASE % name, "rb").read()
        print("=" * 76)
        print("%s.mod  %d bytes" % (name, len(data)))

        positions = [i for i in range(len(data) - 1)
                     if data[i] == 0x00 and data[i + 1] == 0xF0]
        print("  0xF000 found at %d places; first ten: %s"
              % (len(positions), positions[:10]))
        print("")

        for start in positions[:6]:
            if start + 58 > len(data):
                continue
            size = struct.unpack_from("<I", data, start + 2)[0]
            label = read_name(data, start + 26, 32)
            print("  marker @%-6d size=%-6d name=%r" % (start, size, label))

        # Try walking from the first marker that yields a sane size.
        print("")
        for candidate in positions[:3]:
            offset = candidate
            count = 0
            ok = True
            while offset + 30 <= len(data):
                if data[offset] != 0x00 or data[offset + 1] != 0xF0:
                    ok = False
                    break
                size = struct.unpack_from("<I", data, offset + 2)[0]
                if size == 0 or offset + size + 30 > len(data):
                    break
                offset += size + 30 if start_is_marker(offset) else size + 8
                count += 1
                if count > 60:
                    break
            print("  walk from %d: %d blocks, ended at %d (complete=%s)"
                  % (candidate, count, offset, offset >= len(data) - 4))
        print("")


def start_is_marker(offset):
    """Whether the 30-byte header assumption holds at this offset."""
    return True


if __name__ == "__main__":
    main()
