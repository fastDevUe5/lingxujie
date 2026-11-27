"""Add the glTF materials array that the per-group primitives now reference.

Primitives point at material indices, so the document needs a materials array or the file is invalid.
The materials are placeholders - a neutral grey - because the point of this step is slot count, and
turning indices into textures is the next step.

    python Tools/add_materials_array.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/export_mod_anim_gltf.py"

OLD = '        "meshes": [{"name": source_name, "primitives": primitives}],'
NEW = (
    '        "meshes": [{"name": source_name, "primitives": primitives}],\n'
    '        "materials": [\n'
    '            {"name": "moxiang_material_%d" % index,\n'
    '             "pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.8, 0.8, 1.0],\n'
    '                                      "metallicFactor": 0.0,\n'
    '                                      "roughnessFactor": 0.8}}\n'
    '            for index in range(max(1, len(used_materials)))\n'
    '        ],'
)


def main():
    text = open(PATH, encoding="utf-8").read()
    if '"materials": [' in text:
        print("already present")
        return
    if OLD not in text:
        print("insertion point not found")
        index = text.find('"meshes"')
        print(repr(text[index:index + 160]))
        return
    # The materials list depends on used_materials, so make sure it is defined before the dict.
    if "used_materials" not in text:
        print("used_materials is not in scope; cannot size the array")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("materials array added")


if __name__ == "__main__":
    main()
