"""Audit the Python API mirror correctly, by header rather than by size.

The first audit used a 1500 byte floor and reported fifty-five files as suspicious. Sampling them showed
they are correct: a struct with no methods is only three hundred bytes and that is the whole page. Size
was the wrong signal, exactly as it was when counting bullet lines to find index pages.

A real page begins with "# unreal.<Name>  (UE 5.8 Python API)". A miss begins with a 404 notice. Anything
else is genuinely unknown and worth listing.

    python Tools/audit_api_mirror.py [--clean]
"""

import glob
import os
import re
import sys

DIR = "C:/Users/tk/Desktop/lingxujie/Docs/PythonAPI"

HEADER = re.compile(r"^# unreal\.([A-Za-z_][A-Za-z0-9_]*)\s+\(UE")
NOT_PAGES = {"MANIFEST.txt", "README.txt"}


def classify(path):
    """Return (name, size, verdict) where verdict is 'ok', '404', or 'unknown'."""
    size = os.path.getsize(path)
    with open(path, encoding="utf-8", errors="replace") as handle:
        head = handle.read(400)

    if any(marker in head for marker in ("404Page not found", "404 Not Found", "Page not found")):
        return os.path.basename(path)[:-4], size, "404"
    match = HEADER.match(head)
    if match:
        return match.group(1), size, "ok"
    return os.path.basename(path)[:-4], size, "unknown"


def main():
    clean = "--clean" in sys.argv
    files = sorted(glob.glob(os.path.join(DIR, "*.txt")))

    ok, bad, unknown = [], [], []
    for path in files:
        if os.path.basename(path) in NOT_PAGES:
            continue
        name, size, verdict = classify(path)
        entry = (name, size, path)
        {"ok": ok, "404": bad, "unknown": unknown}[verdict].append(entry)

    total = len(ok) + len(bad) + len(unknown)
    print("api pages: %d" % total)
    print("  ok      : %d" % len(ok))
    print("  404     : %d" % len(bad))
    print("  unknown : %d" % len(unknown))
    print("")
    print("usable: %.0f%%" % (100.0 * len(ok) / max(total, 1)))

    if unknown:
        print("")
        print("--- unknown, neither a page nor a 404 ---")
        for name, size, _path in sorted(unknown):
            print("  %-44s %6d bytes" % (name, size))

    if bad:
        print("")
        print("--- 404 pages ---")
        for name, size, _path in sorted(bad):
            print("  %-44s %6d bytes" % (name, size))

    if clean and bad:
        print("")
        removed = 0
        for _name, _size, path in bad:
            os.remove(path)
            removed += 1
        print("removed %d 404 file(s)" % removed)
        print("these are worse than missing: they look covered but hold nothing")

    # A short page is not a defect; report the distribution so that is visible.
    if ok:
        sizes = sorted(size for _n, size, _p in ok)
        print("")
        print("size distribution of usable pages: min %d, median %d, max %d bytes"
              % (sizes[0], sizes[len(sizes) // 2], sizes[-1]))
        small = [n for n, s, _p in ok if s < 600]
        print("usable pages under 600 bytes: %d (these are valid, just memberless types)"
              % len(small))


if __name__ == "__main__":
    main()
