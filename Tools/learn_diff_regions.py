"""Localise a pixel difference: which part of the frame is moving when nothing was changed?

Whole-frame percentages hid the answer in the first rendering run: the control shot differed from the
baseline by 23% of the frame. A 3x3 grid says whether that is the animated sky, the temporal
accumulation on the architecture, or noise everywhere.

    python Tools/learn_diff_regions.py a.png b.png
"""

import sys

from PIL import Image, ImageChops

THRESHOLD = 8


def region_stats(diff, box, size):
    width = box[2] - box[0]
    height = box[3] - box[1]
    total = width * height
    changed = 0
    total_delta = 0
    crop = diff.crop(box)
    for r, g, b in crop.getdata():
        total_delta += r + g + b
        if max(r, g, b) > THRESHOLD:
            changed += 1
    return changed, 100.0 * changed / total, total_delta / (3.0 * total)


def main():
    if len(sys.argv) < 3:
        print("usage: learn_diff_regions.py <a.png> <b.png>")
        return 1

    a = Image.open(sys.argv[1]).convert("RGB")
    b = Image.open(sys.argv[2]).convert("RGB")
    if a.size != b.size:
        print("sizes differ: %r vs %r" % (a.size, b.size))
        return 1
    diff = ImageChops.difference(a, b)
    width, height = a.size

    print("%-18s %6s %6s %6s" % ("region", "changed", "%", "mean"))
    for row in range(3):
        for column in range(3):
            box = (column * width // 3, row * height // 3,
                   (column + 1) * width // 3, (row + 1) * height // 3)
            changed, fraction, mean = region_stats(diff, box, a.size)
            print("row%d col%d        %6d %5.1f%% %6.2f" % (row, column, changed, fraction, mean))

    # The two bands that matter for this scene: sky on top, architecture and ground below.
    sky = (0, 0, width, height // 3)
    lower = (0, height // 3, width, height)
    for label, box in (("sky band", sky), ("lower band", lower)):
        changed, fraction, mean = region_stats(diff, box, a.size)
        print("%-18s %6d %5.1f%% %6.2f" % (label, changed, fraction, mean))
    return 0


if __name__ == "__main__":
    sys.exit(main())
