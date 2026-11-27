"""Compare mesh payload structure across models, controlled for bone count.

The first batch was dominated by props with zero bones, so the structure it showed was the structure
of scenery, not of a skinned character. 1,893 of the 5,305 models declare bones, and 1,385 of those
declare more than sixty - the player character rigs.

This groups by bone count and prints, for each model, the vertex count implied by the payload and
the lengths of every unit-vector run. The point is to see whether any run length is consistently
a small multiple of the vertex count, which would identify the influence count.

    python Tools/compare_mesh_layouts.py
"""

import collections
import math
import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
HEADER = 8


def read_counts(data):
    version, total, materials, meshes, _a, _b, bones = struct.unpack_from("<7I", data, 0)
    return {"version": version, "objects": total, "materials": materials,
            "meshes": meshes, "bones": bones}


def mesh_payloads(data):
    offset = 28
    while offset + HEADER + 4 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + HEADER + size > len(data) + 4:
            return
        if marker == 0xF4000000:
            yield size, offset + HEADER
        offset += HEADER + size


def unit_runs(data, start, end, tolerance=0.001):
    runs = []
    offset = start
    while offset + 12 <= end:
        try:
            x, y, z = struct.unpack_from("<3f", data, offset)
        except struct.error:
            break
        if any(math.isnan(v) or math.isinf(v) for v in (x, y, z)) or \
                abs(math.sqrt(x * x + y * y + z * z) - 1.0) > tolerance:
            offset += 4
            continue
        run_start = offset
        count = 0
        while offset + 12 <= end:
            try:
                x, y, z = struct.unpack_from("<3f", data, offset)
            except struct.error:
                break
            if any(math.isnan(v) or math.isinf(v) for v in (x, y, z)):
                break
            if abs(math.sqrt(x * x + y * y + z * z) - 1.0) > tolerance:
                break
            count += 1
            offset += 12
        if count >= 2:
            runs.append((run_start - start, count))
    return runs


def main():
    names = sorted(n for n in os.listdir(FOLDER) if n.endswith(".mod"))
    buckets = collections.defaultdict(list)

    for name in names:
        path = os.path.join(FOLDER, name)
        try:
            data = open(path, "rb").read()
        except OSError:
            continue
        if len(data) < 40:
            continue
        try:
            counts = read_counts(data)
        except struct.error:
            continue
        if counts["bones"] == 0:
            continue
        payloads = list(mesh_payloads(data))
        if len(payloads) != 1:
            continue
        size, payload = payloads[0]
        runs = unit_runs(data, payload, payload + size)
        if not runs:
            continue

        bucket = "<16" if counts["bones"] < 16 else "16-59" if counts["bones"] < 60 else "60+"
        buckets[bucket].append((name, counts["bones"], size, runs, data, payload))

    for bucket in ("<16", "16-59", "60+"):
        rows = buckets.get(bucket, [])
        print("=" * 96)
        print("bone count %s : %d models with exactly one mesh block" % (bucket, len(rows)))
        if not rows:
            print("")
            continue

        print("%-22s %-5s %-8s %s" % ("file", "bones", "meshsize", "runs offset:length"))
        print("-" * 96)
        for name, bones, size, runs, data, payload in rows[:8]:
            shown = ", ".join("%d:%d" % r for r in runs[:8])
            print("%-22s %-5d %-8d %s" % (name[:22], bones, size, shown))
        print("")

        # Is any run length a small multiple of some common vertex count?
        ratios = collections.Counter()
        for name, bones, size, runs, data, payload in rows:
            largest = max(runs, key=lambda r: r[1])[1]
            for divisor in range(1, 9):
                if largest % divisor == 0:
                    ratios[divisor] += 1
        print("  how often the largest run divides by k: %s"
              % dict(sorted(ratios.items())))
        print("")


if __name__ == "__main__":
    main()
