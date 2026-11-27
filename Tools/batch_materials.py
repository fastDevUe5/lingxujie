"""Build the material map for many models and convert only the textures they reference.

Converting all five thousand textures would take a long time and most may be unused by the models we
care about. Reading the material blocks first says which textures the models actually name, and only
those get converted - which also produces a number worth reporting: how many distinct textures the
whole model set depends on.

    python Tools/batch_materials.py [--limit N]
"""

import os
import re
import struct
import sys

from PIL import Image

sys.path.insert(0, "C:/Users/tk/Desktop/lingxujie/Tools")

MOD = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
DDS = "C:/Users/tk/Desktop/moxiang-study/resources/dds"
TGA = "C:/Users/tk/Desktop/moxiang-study/resources/tga"
TIF = "C:/Users/tk/Desktop/moxiang-study/resources/tif"
OUT = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/textures_png"

IMAGE_SUFFIX = re.compile(
    r"[A-Za-z0-9_\-\.\\/]+\.(tga|dds|bmp|png|jpg|tif|tiff)", re.I)
PRINTABLE = re.compile(rb"[\x20-\x7e]{4,}")


def material_textures(path):
    """Image filenames named by a model's material blocks."""
    try:
        data = open(path, "rb").read()
    except OSError:
        return []
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
    stem = os.path.splitext(os.path.basename(name))[0]
    for folder, extension in ((DDS, ".dds"), (TGA, ".tga"), (TIF, ".tif")):
        candidate = os.path.join(folder, stem + extension)
        if os.path.exists(candidate):
            return candidate
    return None


def convert(source, stem):
    target = os.path.join(OUT, stem + ".png")
    if os.path.exists(target) and os.path.getsize(target) > 0:
        return "cached"
    try:
        image = Image.open(source)
        image.load()
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.mode else "RGB")
        image.save(target, "PNG")
        return "converted"
    except Exception as error:  # noqa: BLE001
        return "failed: %s" % error


def main():
    limit = 600
    args = sys.argv[1:]
    if "--limit" in args:
        index = args.index("--limit")
        if index + 1 < len(args):
            limit = int(args[index + 1])

    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    names = sorted(n for n in os.listdir(MOD) if n.endswith(".mod"))[:limit]
    print("scanning %d models for material textures" % len(names))

    references = {}
    models_with_material = 0
    models_without = 0
    for name in names:
        textures = material_textures(os.path.join(MOD, name))
        if not textures:
            models_without += 1
            continue
        models_with_material += 1
        for texture in set(textures):
            references.setdefault(os.path.splitext(os.path.basename(texture))[0], 0)
            references[os.path.splitext(os.path.basename(texture))[0]] += 1

    print("")
    print("models with a named texture:     %d" % models_with_material)
    print("models with no material entry:   %d" % models_without)
    print("distinct texture names:          %d" % len(references))
    print("")

    resolved = 0
    missing = 0
    converted = 0
    cached = 0
    failed = []
    for stem in sorted(references):
        source = locate(stem)
        if source is None:
            missing += 1
            continue
        resolved += 1
        outcome = convert(source, stem)
        if outcome == "converted":
            converted += 1
        elif outcome == "cached":
            cached += 1
        else:
            failed.append((stem, outcome))

    print("textures found on disk:  %d" % resolved)
    print("textures missing:        %d" % missing)
    print("converted this run:      %d" % converted)
    print("already converted:       %d" % cached)
    print("conversion failures:     %d" % len(failed))
    for stem, reason in failed[:6]:
        print("    %-28s %s" % (stem, reason[:60]))

    print("")
    print("most referenced textures:")
    for stem, count in sorted(references.items(), key=lambda kv: -kv[1])[:10]:
        print("    %-32s %d models" % (stem, count))

    total = sum(os.path.getsize(os.path.join(OUT, f))
                for f in os.listdir(OUT) if f.endswith(".png"))
    print("")
    print("PNG folder now holds %d files, %.1f MB"
          % (len([f for f in os.listdir(OUT) if f.endswith('.png')]), total / (1024.0 * 1024.0)))


if __name__ == "__main__":
    main()
