"""Extract the mesh payload from many mod files and look for a repeated structural pattern.

One file is not evidence. With a container walk that now lands on every block, the payloads can be
compared across dozens of models, and the question stops being "where are the weights in this file"
and becomes "what changes with vertex count and what does not".

The specific measurement: inside each mesh payload, list every run of unit-length float triples with
its length. If a run's length equals the vertex count, it is the normals. If a run's length equals
vertex count times some small integer, that integer is the influence count and the run is either
indices or weights.

    python Tools/batch_mod_meshes.py
"""

import math
import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
HEADER = 8

TYPES = {
    0x00F00000: "MATERIAL",
    0xF4000000: "MESH",
    0xF5000000: "BONE",
}


def read_counts(data):
    if len(data) < 28:
        return None
    version, total, materials, meshes, _a, _b, bones = struct.unpack_from("<7I", data, 0)
    return {"version": version, "objects": total, "materials": materials,
            "meshes": meshes, "bones": bones}


def mesh_payloads(data):
    """Yield (offset, size, payload_offset) for every mesh block."""
    offset = 28
    while offset + HEADER + 4 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + HEADER + size > len(data) + 4:
            return
        if marker == 0xF4000000:
            yield offset, size, offset + HEADER
        offset += HEADER + size


def unit_runs(data, start, end, tolerance=0.001):
    """Every maximal run of consecutive unit-length float triples."""
    runs = []
    offset = start
    while offset + 12 <= end:
        try:
            x, y, z = struct.unpack_from("<3f", data, offset)
        except struct.error:
            break
        bad = any(math.isnan(v) or math.isinf(v) for v in (x, y, z))
        if not bad and abs(math.sqrt(x * x + y * y + z * z) - 1.0) <= tolerance:
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
        else:
            offset += 4
    return runs


def main():
    names = sorted(os.listdir(FOLDER))
    names = [n for n in names if n.endswith(".mod")]
    print("mod files: %d" % len(names))
    print("")

    examined = 0
    rows = []
    for name in names:
        if examined >= 40:
            break
        path = os.path.join(FOLDER, name)
        try:
            data = open(path, "rb").read()
        except OSError:
            continue
        counts = read_counts(data)
        if counts is None:
            continue
        payloads = list(mesh_payloads(data))
        if not payloads:
            continue
        for offset, size, payload in payloads:
            runs = unit_runs(data, payload, payload + size)
            if not runs:
                continue
            rows.append({
                "name": name,
                "bones": counts["bones"],
                "size": size,
                "counts": counts,
                "runs": runs[:6],
                "payload": payload,
                "data": data,
            })
            examined += 1
            break

    print("%-22s %-6s %-7s %s" % ("file", "bones", "meshsiz", "unit-runs (offset,length)"))
    print("-" * 96)
    for row in rows:
        shown = ", ".join("%d:%d" % (r[0], r[1]) for r in row["runs"])
        print("%-22s %-6d %-7d %s" % (row["name"][:22], row["bones"], row["size"], shown))

    print("")
    print("interpretation:")
    print("  a run of length equal to the vertex count is the normal array")
    print("  a run of length vertex_count * k suggests k is the influence count")
    print("")

    # Where does the largest run sit relative to the end of the payload?
    print("%-22s %-8s %-8s %-8s %s"
          % ("file", "largest", "payload", "gap-to-end", "gap / count"))
    print("-" * 84)
    for row in rows:
        largest = max(row["runs"], key=lambda r: r[1])
        payload_size = row["size"]
        run_end = largest[0] + largest[1] * 12
        gap = payload_size - run_end
        print("%-22s %-8d %-8d %-8d %.2f"
              % (row["name"][:22], largest[1], payload_size, gap,
                 gap / float(largest[1]) if largest[1] else 0.0))


if __name__ == "__main__":
    main()
