"""Classify every block by its marker, which is now known to be a type tag.

Two files settle the mapping:
    0x00F00000  material
    0xF5000000  bone
    0xF4000000  mesh

The bone blocks carry their index in the first payload word, and they are stored in descending
order - four, three, two, one in the prop. That is worth knowing because a mesh's bone indices count
from the other end.

This prints every block with its type and the first words of its payload, so the mesh can be found
wherever it sits rather than where it was assumed to be.

    python Tools/classify_mod_blocks.py
"""

import struct

SAMPLES = [
    ("w25260", "C:/Users/tk/Desktop/moxiang-study/resources/mod/w25260.mod"),
    ("jp03_dht00", "C:/Users/tk/Desktop/moxiang-study/resources/mod/jp03_dht00.mod"),
]

TYPES = {
    0x00F00000: "MATERIAL",
    0xF4000000: "MESH",
    0xF5000000: "BONE",
    0xF3000000: "?F3",
    0xF6000000: "?F6",
}


def main():
    for label, path in SAMPLES:
        data = open(path, "rb").read()
        print("=" * 78)
        print("%s  %d bytes" % (label, len(data)))
        print("")

        offset = 28
        index = 0
        counts = {}
        meshes = []
        while offset + 12 <= len(data):
            marker = struct.unpack_from("<I", data, offset)[0]
            size = struct.unpack_from("<I", data, offset + 4)[0]
            if size <= 0 or offset + 8 + size > len(data) + 4:
                print("  stop at %d: size %d implausible" % (offset, size))
                break
            payload = offset + 8
            kind = TYPES.get(marker, "0x%08X" % marker)
            counts[kind] = counts.get(kind, 0) + 1

            # First three words of the payload, which identify bones and mesh headers.
            words = struct.unpack_from("<3i", data, payload)
            print("  [%2d] @%-6d %-9s size=%-6d first=%s"
                  % (index, offset, kind, size, words))

            if kind == "MESH":
                meshes.append((index, offset, size, payload))
            offset = payload + size
            index += 1

        print("")
        print("  counts: %s" % counts)
        print("  tail: %d bytes" % (len(data) - offset))
        print("")

        for index, offset, size, payload in meshes:
            header = struct.unpack_from("<9i", data, payload)
            print("  MESH block [%d] @%d size=%d:" % (index, offset, size))
            labels = ["word0", "word1", "word2", "word3", "word4",
                      "word5", "word6", "word7", "word8"]
            for i, word_label in enumerate(labels):
                print("    +%-2d %-8s %d" % (i * 4, word_label, header[i]))
            print("    first 48 bytes: %s" % data[payload:payload + 48].hex())
            print("")


if __name__ == "__main__":
    main()
