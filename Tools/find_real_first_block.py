"""Find the real first block by validating more than the size.

The scan accepts the first place where a block marker is followed by a plausible size. Some files
have that pattern inside their header by coincidence, and the result is a block whose counts demand
thirteen billion bytes. A real block also carries a printable object name, so requiring that throws
out the coincidences.

    python Tools/find_real_first_block.py
"""

import os
import struct
import sys

ANM_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/anm"
MARKER = b"\x00\xF0\x00\x00"
HEADER = 152
POS = 20
ROT = 24
SCALE = 36


def name_is_plausible(data, offset, length=128):
    """A block name is a short printable string, usually starting with a letter."""
    raw = data[offset:offset + length]
    if not raw:
        return False
    end = raw.find(b"\x00")
    if end < 0:
        end = len(raw)
    text = raw[:end]
    if len(text) < 2:
        return False
    for byte in text:
        if byte < 0x20 or byte > 0x7E:
            # GBK continuation bytes are above 0x7E, so allow those but not control codes.
            if byte < 0x80:
                return False
    return True


def real_first_block(data):
    """Return (offset, blocks_walked) for the longest valid walk, or (None, 0)."""
    markers = [i for i in range(len(data) - 8) if data[i:i + 4] == MARKER]
    best = (None, 0)
    for candidate in markers[:40]:
        size = struct.unpack_from("<I", data, candidate + 4)[0]
        if size < HEADER or candidate + 8 + size > len(data):
            continue
        payload = candidate + 8
        if not name_is_plausible(data, payload + 20):
            continue

        offset = candidate
        blocks = 0
        while offset + 8 <= len(data) and data[offset:offset + 4] == MARKER:
            block_size = struct.unpack_from("<I", data, offset + 4)[0]
            block_payload = offset + 8
            if block_size < HEADER or block_payload + block_size > len(data):
                break
            (_obj, rot_n, pos_n, scale_n, _mesh) = struct.unpack_from(
                "<5I", data, block_payload)
            required = HEADER + pos_n * POS + rot_n * ROT + scale_n * SCALE
            if required > block_size:
                break
            offset = block_payload + block_size
            blocks += 1
            if blocks > 5000:
                break

        if blocks > best[1]:
            best = (candidate, blocks)
    return best


def main():
    samples = ["102_lake.anm", "102_shine.anm", "102_side.anm", "101_1ava00.anm",
               "102_flame.anm", "105_staywater.anm", "108_birda.anm"]
    for name in samples:
        path = os.path.join(ANM_FOLDER, name)
        if not os.path.exists(path):
            continue
        data = open(path, "rb").read()
        offset, blocks = real_first_block(data)
        print("%-22s %8d bytes  real first block @%s, %d blocks"
              % (name, len(data), offset, blocks))

    print("")
    print("now across every file that failed before:")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import export_mod_anim_gltf as exporter

    fixed = 0
    still = 0
    for name in sorted(n for n in os.listdir(ANM_FOLDER) if n.endswith(".anm")):
        path = os.path.join(ANM_FOLDER, name)
        try:
            tracks = exporter.parse_anm(path)
        except (OSError, struct.error):
            tracks = {}
        if tracks:
            continue
        data = open(path, "rb").read()
        offset, blocks = real_first_block(data)
        if offset is not None and blocks > 0:
            fixed += 1
        else:
            still += 1
    print("  recoverable with the stricter scan: %d" % fixed)
    print("  still unrecoverable:                 %d" % still)


if __name__ == "__main__":
    main()
