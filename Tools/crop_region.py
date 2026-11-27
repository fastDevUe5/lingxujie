"""Crop the same region from two captures and save them side by side for inspection.

Numbers said eight point eight percent of the region changed with a small colour shift, while my eye
said the creature turned from grey to red. One of those is wrong, and cropping both to the same region
and enlarging makes it checkable without guessing.

    python Tools/crop_region.py
"""

from PIL import Image

BEFORE = "C:/Users/tk/Desktop/lingxujie/Saved/shot_mat_before.png"
AFTER = "C:/Users/tk/Desktop/lingxujie/Saved/shot_mat_after.png"
OUT = "C:/Users/tk/Desktop/lingxujie/Saved/shot_mat_compare.png"

# The creature sits around here; the crop is generous so the surroundings give scale.
BOX = (440, 340, 700, 500)
SCALE = 3


def main():
    a = Image.open(BEFORE).convert("RGB").crop(BOX)
    b = Image.open(AFTER).convert("RGB").crop(BOX)

    a = a.resize((a.width * SCALE, a.height * SCALE), Image.NEAREST)
    b = b.resize((b.width * SCALE, b.height * SCALE), Image.NEAREST)

    combined = Image.new("RGB", (a.width + b.width + 8, max(a.height, b.height)), (20, 20, 20))
    combined.paste(a, (0, 0))
    combined.paste(b, (a.width + 8, 0))
    combined.save(OUT)
    print("wrote %s (%dx%d) - left is before, right is after" % (OUT, combined.width, combined.height))


if __name__ == "__main__":
    main()
