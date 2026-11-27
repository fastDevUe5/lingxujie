"""Diff every A/B shot against the baseline, with the control shot as the noise floor.

A difference only means something relative to how much the same scene differs from itself. The
control shot (same settings, taken twice) is the denominator: if a CVar moves fewer pixels than the
control does, the honest conclusion is "no measurable effect at this threshold", not "subtle effect".

    python Tools/learn_diff_all.py [shot-dir]
"""

import glob
import os
import sys

from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "Saved", "learn_ab")
THRESHOLD = 8


def find(name):
    matches = glob.glob(os.path.join(SHOTS, "**", name + ".png"), recursive=True)
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)


def measure(path_a, path_b):
    a = Image.open(path_a).convert("RGB")
    b = Image.open(path_b).convert("RGB")
    if a.size != b.size:
        return {"error": "size %r vs %r" % (a.size, b.size)}
    diff = ImageChops.difference(a, b)
    total = a.size[0] * a.size[1]
    changed = 0
    total_delta = 0
    for r, g, bl in diff.getdata():
        peak = max(r, g, bl)
        total_delta += r + g + bl
        if peak > THRESHOLD:
            changed += 1
    return {
        "changed": changed,
        "fraction": 100.0 * changed / total,
        "mean": total_delta / (3.0 * total),
        "size": a.size,
    }


def main():
    if len(sys.argv) > 1:
        global SHOTS
        SHOTS = sys.argv[1] if os.path.isabs(sys.argv[1]) else os.path.join(ROOT, sys.argv[1])
    base = find("ab_base")
    if not base:
        print("no ab_base.png found under %s" % SHOTS)
        return 1
    print("baseline: %s" % os.path.relpath(base, ROOT))

    names = sorted({os.path.splitext(os.path.basename(p))[0]
                    for p in glob.glob(os.path.join(SHOTS, "**", "ab_*.png"), recursive=True)})
    rows = []
    for name in names:
        if name == "ab_base":
            continue
        path = find(name)
        if not path:
            continue
        result = measure(base, path)
        rows.append((name, result))
        if "error" in result:
            print("%-18s %s" % (name, result["error"]))
        else:
            print("%-18s changed %6d px (%5.2f%%)  mean delta %6.3f"
                  % (name, result["changed"], result["fraction"], result["mean"]))

    control = [r for r in rows if r[0] == "ab_control"]
    if control and "fraction" in control[0][1]:
        floor = control[0][1]["fraction"]
        print("\nnoise floor (control shot vs baseline): %.2f%% of pixels" % floor)
        for name, result in rows:
            if "fraction" not in result:
                continue
            verdict = "above floor" if result["fraction"] > max(floor * 2.0, 0.5) else "at or below floor"
            print("  %-18s %6.2f%%  %s" % (name, result["fraction"], verdict))
    return 0


if __name__ == "__main__":
    sys.exit(main())
