"""Classify mirrored pages by size alone, because the link-ratio metric does not work here.

The first attempt counted lines that start with "-" or "|" and treated a high ratio as evidence of an
index page. That is wrong for this data: the HTML stripper converts every list item into a bullet, so a
page containing any list or table scores as link-heavy. lumen-technical at twenty-five kilobytes of
prose scored seventy-eight percent and was called navigation.

Size is the honest signal. A landing page is short because it only lists children; a real article is
long because it explains something.

    python Tools/audit_manual_quality.py
"""

import glob
import os

DIR = "C:/Users/tk/Desktop/lingxujie/Docs/UEManual"

# A real article here is comfortably over this; landing pages land well under it.
THIN = 3000


def main():
    files = sorted(f for f in glob.glob(os.path.join(DIR, "*.md"))
                   if not f.endswith("README.md"))

    rows = []
    for path in files:
        name = os.path.basename(path)[:-3]
        text = open(path, encoding="utf-8").read()
        lines = len([ln for ln in text.split("\n") if ln.strip()])
        rows.append((name, len(text), lines))

    substantive = [r for r in rows if r[1] >= THIN]
    thin = [r for r in rows if r[1] < THIN]
    total_kb = sum(os.path.getsize(os.path.join(DIR, r[0] + ".md")) for r in rows) / 1024.0

    print("pages: %d, total %.1f KB" % (len(rows), total_kb))
    print("substantive (>= %d chars): %d" % (THIN, len(substantive)))
    print("landing pages (< %d chars): %d" % (THIN, len(thin)))
    print("")
    print("--- landing pages, they only list child topics ---")
    for name, chars, lines in sorted(thin, key=lambda r: r[1]):
        print("  %-30s %6d chars %4d lines" % (name, chars, lines))
    print("")
    print("--- substantive ---")
    for name, chars, lines in sorted(substantive, key=lambda r: -r[1]):
        print("  %-30s %6d chars %4d lines" % (name, chars, lines))


if __name__ == "__main__":
    main()
