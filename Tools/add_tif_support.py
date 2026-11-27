"""Add .tif to the material scan and conversion.

The first full pass reported eight hundred forty-one models with no texture. They do have textures -
the material blocks name .tif files, and nine hundred twenty-nine such files sit in resources/tif.
The extension list simply did not include tif, so those references were never counted and the
sixteen percent looked like a gap in the data rather than a gap in the pattern.

    python Tools/add_tif_support.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/batch_materials.py"

REPLACEMENTS = [
    ('TGA = "C:/Users/tk/Desktop/moxiang-study/resources/tga"',
     'TGA = "C:/Users/tk/Desktop/moxiang-study/resources/tga"\n'
     'TIF = "C:/Users/tk/Desktop/moxiang-study/resources/tif"'),
    ('IMAGE_SUFFIX = re.compile(r"[A-Za-z0-9_\\-\\.\\\\/]+\\.(tga|dds|bmp|png|jpg)", re.I)',
     'IMAGE_SUFFIX = re.compile(\n'
     '    r"[A-Za-z0-9_\\-\\.\\\\/]+\\.(tga|dds|bmp|png|jpg|tif|tiff)", re.I)'),
    ('    for folder, extension in ((DDS, ".dds"), (TGA, ".tga")):',
     '    for folder, extension in ((DDS, ".dds"), (TGA, ".tga"), (TIF, ".tif")):'),
]


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
            changed += 1
        else:
            print("not found: %s" % old[:60])
    if changed == 0:
        print("nothing changed")
        return
    open(PATH, "w", encoding="utf-8").write(text)
    print("applied %d of %d replacements" % (changed, len(REPLACEMENTS)))


if __name__ == "__main__":
    main()
