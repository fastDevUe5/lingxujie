"""Point the material script at the converted PNG.

    python Tools/switch_to_png.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/apply_boss_material2.py"

OLD = 'TEXTURE = "C:/Users/tk/Desktop/moxiang-study/resources/dds/boss_mob01.dds"'
NEW = ('TEXTURE = '
       '"C:/Users/tk/Desktop/lingxujie/Assets/Moxiang/textures_png/boss_mob01.png"')


def main():
    text = open(PATH, encoding="utf-8").read()
    if NEW.strip() in text:
        print("already pointing at the PNG")
        return
    if OLD not in text:
        print("source line not found")
        return
    open(PATH, "w", encoding="utf-8").write(text.replace(OLD, NEW))
    print("now importing the PNG")


if __name__ == "__main__":
    main()
