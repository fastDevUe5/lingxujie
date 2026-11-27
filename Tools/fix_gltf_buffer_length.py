"""Fix the buffer length, which was computed before the animation data was appended.

The glTF dictionary is assembled with byteLength taken at that moment, and every animation accessor
is added to the binary after that point. The declared length therefore undercounts, and Interchange
rejects the file with a buffer size mismatch - which reads like a corruption rather than an ordering
mistake.

    python Tools/fix_gltf_buffer_length.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/export_mod_anim_gltf.py"

OLD = """    if channels:
        gltf["animations"] = [{"name": source_name, "channels": channels, "samplers": samplers}]

    return gltf, bytes(binary)"""

NEW = """    if channels:
        gltf["animations"] = [{"name": source_name, "channels": channels, "samplers": samplers}]

    # The byte length has to be taken after every accessor has appended to the binary. Reading it
    # at dictionary construction time undercounts by exactly the animation data, and the importer
    # reports that as a buffer size mismatch.
    gltf["buffers"][0]["byteLength"] = len(binary)

    return gltf, bytes(binary)"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if OLD not in text:
        print("target block not found; already fixed?")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("buffer length is now taken after all accessors are written")


if __name__ == "__main__":
    main()
