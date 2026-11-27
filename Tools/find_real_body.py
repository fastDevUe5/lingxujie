"""Find models that actually contain a body rather than an effect.

The file named after the boss turned out to hold fire planes: twenty-four blocks named fire03,
BU_fire_boom_02 and so on, with a degenerate transform and garbage vertices on half of them. That
means the name tells you what the file belongs to, not what it is.

Sorting candidate models by how many of their mesh block names look like body parts rather than
effect parts finds the one worth importing.

    python Tools/find_real_body.py
"""

import os
import re
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"

# Names that mark a block as an effect rather than a piece of a body.
EFFECT_WORDS = ("fire", "eff", "smoke", "spray", "boom", "glow", "light", "flare",
                "dust", "spark", "trail", "particle", "water", "fog", "fsand")
# Names that suggest geometry: a body part, or the model's own name without a suffix.
BODY_WORDS = ("body", "head", "arm", "leg", "hand", "foot", "torso", "cloth",
              "hair", "face", "eye", "tail", "wing", "horn", "weapon")


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def mesh_names(path):
    try:
        data = open(path, "rb").read()
    except OSError:
        return []
    names = []
    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        if marker == 0xF4000000:
            names.append(read_name(data, offset + 8 + 196))
        offset = offset + 8 + size
    return names


def score(names, stem):
    if not names:
        return 0, 0, 0
    effect = 0
    body = 0
    for name in names:
        lowered = name.lower()
        if any(word in lowered for word in EFFECT_WORDS):
            effect += 1
        elif any(word in lowered for word in BODY_WORDS):
            body += 1
        elif lowered.startswith(stem.lower()[:4]):
            # Named after the model itself: almost certainly a real piece.
            body += 1
    return body - effect, effect, body


def main():
    candidates = []
    for name in sorted(os.listdir(FOLDER)):
        if not name.endswith(".mod"):
            continue
        if not (name.lower().startswith("boss") or "cow" in name.lower()):
            continue
        path = os.path.join(FOLDER, name)
        names = mesh_names(path)
        net, effect, body = score(names, os.path.splitext(name)[0])
        candidates.append((net, effect, body, name, names))

    candidates.sort(reverse=True)
    print("candidates sorted by how body-like their mesh names are:")
    print("")
    for net, effect, body in [(c[0], c[1], c[2]) for c in candidates[:1]]:
        pass
    for net, effect, body, name, names in candidates[:14]:
        label = "BODY" if net > 0 else ("effect" if effect else "?")
        print("%-22s net=%-4d effect=%-3d body=%-3d %-7s %s"
              % (name[:22], net, effect, body, label, ", ".join(n[:12] for n in names[:4])))

    print("")
    best = candidates[0]
    print("best candidate: %s" % best[3])
    print("  blocks: %s" % ", ".join(best[4][:12]))


if __name__ == "__main__":
    main()
