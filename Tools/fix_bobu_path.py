"""Point the placement script at the real asset path.

Interchange nests imports under a folder named after the source file, so the mesh is not at the
destination path given to the import task - it is one level deeper, inside a folder named
char_bobu/SkeletalMeshes.

    python Tools/fix_bobu_path.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/place_bobu.py"
OLD = 'MESH = "/Game/Moxiang/Skeletal/Characters/SK_Bobu.SK_Bobu"'
NEW = ('MESH = "/Game/Moxiang/Skeletal/Characters/char_bobu/'
       'SkeletalMeshes/SK_Bobu.SK_Bobu"')


def main():
    text = open(PATH, encoding="utf-8").read()
    if OLD not in text:
        print("line not found; already fixed?")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("path corrected to the nested Interchange location")


if __name__ == "__main__":
    main()
