"""Convert the source DDS files to PNG so Unreal will import them.

The engine refuses this set outright:

    Error: DDS DXGIFormat not supported : 71 : BC1_UNORM
    Error: Texture import failed

Its DDS reader will not take a DXGI-format surface, and the whole texture collection is written that
way. Pillow reads DDS without complaint, so converting first sidesteps the reader entirely - and PNG
is a format the importer is happy with.

    python Tools/convert_dds.py [name ...]
"""

import os
import sys

from PIL import Image

DDS = "C:/Users/tk/Desktop/moxiang-study/resources/dds"
OUT = "C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/textures_png"


def convert(stem):
    source = os.path.join(DDS, stem + ".dds")
    if not os.path.exists(source):
        return None, "missing"
    target = os.path.join(OUT, stem + ".png")
    if os.path.exists(target) and os.path.getsize(target) > 0:
        return target, "exists"
    try:
        image = Image.open(source)
        image.load()
    except Exception as error:  # noqa: BLE001
        return None, "Pillow could not read it: %s" % error
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "A" in image.mode else "RGB")
    image.save(target, "PNG")
    return target, "%dx%d %s" % (image.width, image.height, image.mode)


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    stems = sys.argv[1:]
    if not stems:
        stems = ["boss_mob01", "N012", "N012-1", "107_crow", "M_santa",
                 "20_eagle01", "EFF_07_01", "ice_fire_01"]

    ok = 0
    for stem in stems:
        target, detail = convert(stem)
        if target:
            ok += 1
            print("%-20s -> %s  (%s, %d bytes)"
                  % (stem, os.path.basename(target), detail, os.path.getsize(target)))
        else:
            print("%-20s failed: %s" % (stem, detail))

    print("")
    print("converted %d of %d" % (ok, len(stems)))


if __name__ == "__main__":
    main()
