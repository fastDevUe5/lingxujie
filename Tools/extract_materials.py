"""Extract the texture each material block names, and check the file can be found.

A material block is mostly binary, but it carries the texture filename as plain text - a boss names
boss_mob01.tga - and the same name exists on disk as a .dds. Finding that correspondence is the whole
prerequisite for giving the imported meshes a surface instead of default grey.

This reports the mapping across a set of models and how many of the named textures actually exist,
because a mapping that fails half the time is not worth building on.

    python Tools/extract_materials.py
"""

import os
import re
import struct
import sys

sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")
import export_mod_anim_gltf as exporter

MOD = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
DDS = "C:/Users/tk/Desktop/moxiang-study/resources/dds"
TGA = "C:/Users/tk/Desktop/moxiang-study/resources/tga"

SAMPLE = ["boss001", "198_bobu", "108_bird", "107_crow", "216", "w25260",
          "boss_cowf_01", "20_eagle_01"]

# A filename with an image extension, or a plausible bare texture name.
IMAGE_SUFFIX = re.compile(r"[A-Za-z0-9_\-\.\\/]+\.(tga|dds|bmp|png|jpg)", re.I)
PRINTABLE = re.compile(rb"[\x20-\x7e]{4,}")


def material_textures(path):
    """Return the image filenames referenced by a model's material blocks."""
    data = open(path, "rb").read()
    found = []
    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        if marker == 0x00F00000:
            block = data[offset + 8:offset + 8 + size]
            for match in PRINTABLE.finditer(block):
                text = match.group(0).decode("latin-1")
                for image in IMAGE_SUFFIX.finditer(text):
                    found.append(image.group(0))
        offset = offset + 8 + size
    return found


def locate(name):
    """Find the file for a texture name, trying the extensions on disk."""
    stem = os.path.splitext(os.path.basename(name))[0]
    for folder, extension in ((DDS, ".dds"), (TGA, ".tga")):
        candidate = os.path.join(folder, stem + extension)
        if os.path.exists(candidate):
            return candidate
    return None


def main():
    total = 0
    resolved = 0
    print("%-16s %s" % ("model", "textures"))
    print("-" * 76)
    for name in SAMPLE:
        path = os.path.join(MOD, name + ".mod")
        if not os.path.exists(path):
            continue
        textures = material_textures(path)
        unique = sorted(set(textures))
        marks = []
        for texture in unique:
            total += 1
            located = locate(texture)
            if located:
                resolved += 1
                marks.append(texture)
            else:
                marks.append(texture + " (missing)")
        print("%-16s %s" % (name, ", ".join(marks[:5]) if marks else "none"))

    print("")
    print("references: %d, resolved: %d (%.0f%%)"
          % (total, resolved, 100.0 * resolved / total if total else 0))
    print("")
    print("the material block stores a .tga name while the file on disk is a .dds,")
    print("so the lookup swaps the extension rather than trusting the stored one.")


if __name__ == "__main__":
    main()
