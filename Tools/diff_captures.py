"""Decide whether vis visualisations reach a viewport capture, by diffing two captures.

Comparing images by eye is unreliable: anti-aliasing alone shifts pixels between frames, so a subtle
difference proves nothing. Two captures with a known state change between them, diffed numerically,
does prove something.

    python Tools/diff_captures.py a.png b.png
"""

import sys

from PIL import Image, ImageChops


def stats(path):
    image = Image.open(path).convert("RGB")
    return image


def main():
    if len(sys.argv) < 3:
        print("usage: diff_captures.py <a.png> <b.png>")
        return 1

    a = stats(sys.argv[1])
    b = stats(sys.argv[2])
    if a.size != b.size:
        print("sizes differ: %r vs %r" % (a.size, b.size))
        return 1

    diff = ImageChops.difference(a, b)
    histogram = diff.histogram()
    total_pixels = a.size[0] * a.size[1]

    # Count pixels where any channel moved by more than a threshold that anti-aliasing would not
    # explain, and report the mean absolute change.
    changed = 0
    total_delta = 0
    pixels = diff.load()
    width, height = a.size
    for y in range(height):
        for x in range(width):
            r, g, bl = pixels[x, y]
            peak = max(r, g, bl)
            total_delta += r + g + bl
            if peak > 8:
                changed += 1

    print("size: %dx%d (%d pixels)" % (width, height, total_pixels))
    print("pixels differing by more than 8: %d (%.2f%%)"
          % (changed, 100.0 * changed / total_pixels))
    print("mean absolute channel delta: %.3f" % (total_delta / (3.0 * total_pixels)))

    boxes = diff.getbbox()
    print("bounding box of any change: %r" % (boxes,))

    # A crude verdict, stated as what the numbers support rather than what I expected.
    fraction = changed / total_pixels
    if fraction > 0.5:
        print("VERDICT: the two captures differ over most of the frame")
    elif fraction > 0.02:
        print("VERDICT: the two captures differ in a region, not everywhere")
    else:
        print("VERDICT: the two captures are effectively identical at this threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
