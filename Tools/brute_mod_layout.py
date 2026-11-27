"""Brute-force the container layout by requiring the walk to consume the whole file.

Every hand-computed offset has been wrong so far - twenty-eight, then thirty, then a four-byte
marker at a fixed position. Rather than reason about it further, this tries every combination of
start offset, header length and size-field position, and keeps only the walks that land exactly on
the end of the file with a plausible number of blocks.

A layout that reaches the end of a five kilobyte file and a twenty-six kilobyte file with sane
block sizes is almost certainly the real one.

    python Tools/brute_mod_layout.py
"""

import struct

SAMPLES = [
    ("w25260", "C:/Users/tk/Desktop/moxiang-study/resources/mod/w25260.mod"),
    ("jp03_dht00", "C:/Users/tk/Desktop/moxiang-study/resources/mod/jp03_dht00.mod"),
]


def walk(data, start, header, size_at, sanity=1_000_000):
    """Follow blocks from start; return (count, end offset) or None if a size is implausible."""
    offset = start
    count = 0
    while offset + header <= len(data):
        if size_at + 4 > header:
            return None
        size = struct.unpack_from("<I", data, offset + size_at)[0]
        if size <= 0 or size > sanity:
            return None
        offset += header + size
        count += 1
        if count > 500:
            return None
    return count, offset


def main():
    for label, path in SAMPLES:
        data = open(path, "rb").read()
        print("=" * 78)
        print("%s  %d bytes" % (label, len(data)))

        winners = []
        for start in range(0, 256):
            for header in (4, 8, 12, 16, 20, 24, 28, 30, 32):
                for size_at in range(0, header - 3):
                    result = walk(data, start, header, size_at)
                    if result is None:
                        continue
                    count, end = result
                    if abs(end - len(data)) <= 4 and 2 <= count <= 200:
                        winners.append((start, header, size_at, count, end))

        if not winners:
            print("  no layout consumes the file exactly")
            continue

        # Prefer the layout that finds the most blocks for the same start.
        winners.sort(key=lambda w: (-w[3], w[0]))
        print("  layouts that land on the end of file: %d" % len(winners))
        for start, header, size_at, count, end in winners[:8]:
            print("    start=%-4d header=%-3d size_at=+%-2d blocks=%-4d end=%d"
                  % (start, header, size_at, count, end))
        print("")

        # Print the block table for the best candidate.
        start, header, size_at, count, end = winners[0]
        print("  best: start=%d header=%d size_at=+%d" % (start, header, size_at))
        offset = start
        for index in range(min(count, 12)):
            size = struct.unpack_from("<I", data, offset + size_at)[0]
            head = data[offset:offset + min(header, 8)].hex()
            print("    [%2d] @%-6d size=%-6d head=%s" % (index, offset, size, head))
            offset += header + size
        print("")


if __name__ == "__main__":
    main()
