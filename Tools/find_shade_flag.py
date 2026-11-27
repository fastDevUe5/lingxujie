"""Find the shade-type flag values, which decide whether a mesh carries normals at all.

The client reads normals only when the mesh is not light-mapped:

    if (m_meshFlag.GetShadeType() == SHADE_TYPE_LIGHT_MAP)
        m_pLightTexture->ReadFile(pFP);
    else
        FSRead(normals, 12 * dwVertexNum);

The batch failure pattern - running ten to twenty bytes past the end - is exactly what reading a
normal array that is not there would produce. So the flag in FILE_MESH_HEADER decides both whether
normals exist and whether a light texture follows.

    python Tools/find_shade_flag.py
"""

import os
import struct

FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
GOOD = ["108_bird.mod", "198_bobu.mod", "216.mod"]
BAD = ["101_1ava00.mod", "102_light.mod", "104_elf_eff.mod", "106_fire.mod"]


def mesh_flags(path):
    data = open(path, "rb").read()
    out = []
    offset = 28
    while offset + 12 <= len(data):
        marker = struct.unpack_from("<I", data, offset)[0]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size <= 0 or offset + 8 + size > len(data) + 4:
            break
        if marker == 0xF4000000:
            payload = offset + 8
            (max_v, vertex_num, orig_v, ext_v, tex_v, mtl,
             group_num, mesh_flag, grid) = struct.unpack_from("<9I", data, payload + 324)
            out.append({
                "name": "",
                "vertex_num": vertex_num,
                "tex_v": tex_v,
                "group_num": group_num,
                "mesh_flag": mesh_flag,
                "flag_hex": "0x%08X" % mesh_flag,
                "shade": mesh_flag & 0x0F,
            })
        offset = offset + 8 + size
    return out


def main():
    print("%-20s %-8s %-8s %-12s %s"
          % ("file", "verts", "groups", "mesh_flag", "shade&0xF"))
    print("-" * 70)

    for label, group in (("parsed", GOOD), ("failing", BAD)):
        print("--- %s" % label)
        for name in group:
            path = os.path.join(FOLDER, name)
            if not os.path.exists(path):
                continue
            try:
                blocks = mesh_flags(path)
            except (OSError, struct.error) as error:
                print("%-20s %s" % (name, error))
                continue
            for block in blocks[:2]:
                print("%-20s %-8d %-8d %-12s %d"
                      % (name[:20], block["vertex_num"], block["group_num"],
                         block["flag_hex"], block["shade"]))
        print("")

    print("the client compares GetShadeType() against SHADE_TYPE_LIGHT_MAP.")
    print("whichever low bits distinguish the failing files are the light-mapped ones,")
    print("and those meshes carry a light texture where the others carry normals.")


if __name__ == "__main__":
    main()
