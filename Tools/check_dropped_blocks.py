"""Check whether the blocks I dropped for being huge are huge because of their transform.

Keeping the small pieces and discarding the large ones is only right if the large ones are
backgrounds. If the transform is what inflates them - a scale baked into mat4 that the object never
really used for rendering - then the body is among the discarded and the import keeps only props.

    python Tools/check_dropped_blocks.py
"""

import struct

PATH = "C:/Users/tk/Desktop/moxiang-study/resources/mod/boss_cowf_01.mod"


def read_name(data, offset, length=128):
    raw = data[offset:offset + length]
    end = raw.find(b"\x00")
    if end > 0:
        raw = raw[:end]
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def main():
    data = open(PATH, "rb").read()
    print("%s  %d bytes" % (PATH.rsplit("/", 1)[-1], len(data)))
    print("")
    print("%-3s %-16s %-8s %-24s %-12s %s"
          % ("#", "name", "verts", "mat4 scale (col len)", "axis extent", "verdict"))
    print("-" * 100)

    offset = 28
    index = 0
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        payload = offset + 8
        if marker == 0xF4000000:
            name = read_name(data, payload + 196)
            (max_v, vertex_num, orig_v, ext_v, tex_v, mtl,
             group_num, mesh_flag, grid) = struct.unpack_from("<9I", data, payload + 324)
            matrix = struct.unpack_from("<16f", data, payload + 4 + 56)

            # Column lengths give the scale the matrix applies.
            sx = (matrix[0] ** 2 + matrix[1] ** 2 + matrix[2] ** 2) ** 0.5
            sy = (matrix[4] ** 2 + matrix[5] ** 2 + matrix[6] ** 2) ** 0.5
            sz = (matrix[8] ** 2 + matrix[9] ** 2 + matrix[10] ** 2) ** 0.5
            translation = (matrix[12], matrix[13], matrix[14])

            cursor = payload + 324 + 48
            points = []
            for i in range(min(vertex_num, 4000)):
                x, y, z = struct.unpack_from("<3f", data, cursor + i * 12)
                points.append((x, y, z))
            if points:
                raw_extent = max(max(p[i] for p in points) - min(p[i] for p in points)
                                 for i in range(3))
            else:
                raw_extent = 0.0

            verdict = ""
            if raw_extent > 10000:
                verdict = "raw verts already huge"
            elif raw_extent * max(sx, sy, sz) > 10000:
                verdict = "transform inflates it"

            print("%-3d %-16s %-8d (%7.2f,%7.2f,%7.2f) %-12.1f %s"
                  % (index, (name or "?")[:16], vertex_num, sx, sy, sz, raw_extent, verdict))
            if verdict == "transform inflates it":
                print("        translation (%.1f, %.1f, %.1f), raw extent %.1f cm"
                      % (translation[0], translation[1], translation[2], raw_extent))
            index += 1
        offset = payload + size


if __name__ == "__main__":
    main()
