"""Diff only the region that changed, so a small-object change is not averaged away.

The whole-frame verdict said effectively identical while the creature plainly changed colour, because
eight thousand pixels out of eight hundred thousand is one percent and the threshold was set for scene
wide changes. Cropping to the region before comparing removes the averaging.

    python Tools/diff_region.py a.png b.png x0 y0 x1 y1
"""

import sys

from PIL import Image, ImageChops


def main():
    if len(sys.argv) < 7:
        print("usage: diff_region.py <a.png> <b.png> <x0> <y0> <x1> <y1>")
        return 1

    a_path, b_path = sys.argv[1], sys.argv[2]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])

    a = Image.open(a_path).convert("RGB").crop((x0, y0, x1, y1))
    b = Image.open(b_path).convert("RGB").crop((x0, y0, x1, y1))

    diff = ImageChops.difference(a, b)
    pixels = diff.load()
    width, height = a.size
    total = width * height

    changed = 0
    total_delta = 0
    for y in range(height):
        for x in range(width):
            r, g, bl = pixels[x, y]
            total_delta += r + g + bl
            if max(r, g, bl) > 8:
                changed += 1

    print("region: (%d,%d) to (%d,%d), %d pixels" % (x0, y0, x1, y1, total))
    print("changed: %d (%.1f%%)" % (changed, 100.0 * changed / total))
    print("mean delta: %.2f" % (total_delta / (3.0 * total)))

    # Mean absolute colour in each version, which says whether the hue moved.
    def mean_colour(image):
        data = image.load()
        w, h = image.size
        tr = tg = tb = 0
        n = 0
        for yy in range(h):
            for xx in range(w):
                r, g, bl = data[xx, yy]
                tr += r
                tg += g
                tb += bl
                n += 1
        return (tr / n, tg / n, tb / n)

    ma = mean_colour(a)
    mb = mean_colour(b)
    print("mean colour before: (%.1f, %.1f, %.1f)" % ma)
    print("mean colour after:  (%.1f, %.1f, %.1f)" % mb)
    print("channel shift:      (%+.1f, %+.1f, %+.1f)"
          % (mb[0] - ma[0], mb[1] - ma[1], mb[2] - ma[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
