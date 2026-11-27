"""Find out what the models with no material block actually are.

Sixteen percent of models name no texture. That could mean anything - props coloured by vertex colour,
effect quads with procedural materials, skeletal attachments - and the answer decides whether the
sixteen percent is a gap or simply a category that does not need textures.

Classifying by their mesh block names, which have already proven a reliable guide to what a file is,
and by how many blocks they have, gives the shape of the group.

    python Tools/classify_no_material.py
"""

import os
import re
import struct

MOD = "C:/Users/tk/Desktop/moxiang-study/resources/mod"

EFFECT_WORDS = ("fire", "eff", "smoke", "spray", "boom", "glow", "light", "flare",
                "dust", "spark", "trail", "particle", "water", "fog", "sand", "ice")
BODY_WORDS = ("body", "head", "arm", "leg", "hand", "foot", "torso", "cloth",
              "hair", "face", "eye", "tail", "wing", "horn", "weapon", "shoulder")


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def scan(path):
    """Return (has_material_texture, mesh_names, bone_count)."""
    try:
        data = open(path, "rb").read()
    except OSError:
        return None
    has_texture = False
    meshes = []
    bones = 0
    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        if marker == 0x00F00000:
            block = data[offset + 8:offset + 8 + size]
            if re.search(rb"[A-Za-z0-9_\-\.]+\.(tga|dds|bmp|png|jpg)", block, re.I):
                has_texture = True
        elif marker == 0xF4000000:
            meshes.append(read_name(data, offset + 8 + 196))
        elif marker == 0xF5000000:
            bones += 1
        offset = offset + 8 + size
    return has_texture, meshes, bones


def main():
    names = sorted(n for n in os.listdir(MOD) if n.endswith(".mod"))
    print("scanning %d models" % len(names))

    no_material = []
    for name in names:
        result = scan(os.path.join(MOD, name))
        if result is None:
            continue
        has_texture, meshes, bones = result
        if not has_texture:
            no_material.append((name, meshes, bones))

    print("models with no named texture: %d of %d (%.1f%%)"
          % (len(no_material), len(names), 100.0 * len(no_material) / len(names)))
    print("")

    # Classify by mesh names.
    effect = 0
    body = 0
    unknown = 0
    for _name, meshes, _bones in no_material:
        lowered = [m.lower() for m in meshes]
        if any(any(word in m for word in EFFECT_WORDS) for m in lowered):
            effect += 1
        elif any(any(word in m for word in BODY_WORDS) for m in lowered):
            body += 1
        else:
            unknown += 1

    print("by the names of their mesh blocks:")
    print("  effect-like (fire/smoke/water/fog/...): %d" % effect)
    print("  body-like (head/arm/torso/...):         %d" % body)
    print("  neither:                                %d" % unknown)
    print("")

    # Bones: a model with bones probably wants a texture, so those are the interesting ones.
    boneless = sum(1 for _n, _m, b in no_material if b == 0)
    with_bones = len(no_material) - boneless
    print("by skeleton:")
    print("  no bones (static props):                %d" % boneless)
    print("  has bones (characters or attachments):  %d" % with_bones)
    print("")

    print("sample of the boneless ones:")
    shown = 0
    for name, meshes, bones in no_material:
        if bones == 0:
            print("  %-28s %d blocks: %s"
                  % (name[:28], len(meshes), ", ".join(m[:14] for m in meshes[:3])))
            shown += 1
            if shown >= 8:
                break

    print("")
    print("sample of the ones with bones (these are the ones worth a look):")
    shown = 0
    for name, meshes, bones in no_material:
        if bones > 0:
            print("  %-28s %d bones, %d blocks: %s"
                  % (name[:28], bones, len(meshes), ", ".join(m[:14] for m in meshes[:3])))
            shown += 1
            if shown >= 8:
                break


if __name__ == "__main__":
    main()
