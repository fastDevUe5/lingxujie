"""Fix the face group framing in the layout verifier.

The group is not a count followed by indices. It is a twenty-eight byte header of seven words, then
faces as words, then two optional light-UV arrays. Reading it as a count consumed the wrong number
of bytes and threw every offset after it out of place.

    python Tools/fix_face_groups.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/verify_mod_layout.py"

OLD = '''    # Face groups: each is a count then that many index triples, per the client reader.
    groups = []
    for _ in range(face_group_num):
        if cursor + 4 > len(data):
            break
        count = struct.unpack_from("<I", data, cursor)[0]
        if count > 5_000_000:
            groups.append(("bad", count))
            break
        groups.append(count)
        cursor += 4 + 4 * count
    out["face_groups"] = groups[:8]'''

NEW = '''    # Face groups: FILE_FACE_GROUP_HEADER is seven words, then that many faces as word triples,
    # then two optional light-UV arrays of eight bytes each.
    groups = []
    for _ in range(face_group_num):
        if cursor + 28 > len(data):
            break
        (mtl, index, faces_num, max_faces, vindex_num,
         light_uv1, light_uv2) = struct.unpack_from("<7I", data, cursor)
        groups.append((faces_num, light_uv1, light_uv2))
        cursor += 28
        cursor += 2 * faces_num * 3
        cursor += 8 * light_uv1
        cursor += 8 * light_uv2
    out["face_groups"] = groups[:8]'''


def main():
    text = open(PATH, encoding="utf-8").read()
    if OLD not in text:
        print("block not found; already fixed?")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("face group framing replaced with the seven-word header")


if __name__ == "__main__":
    main()
