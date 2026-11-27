"""Point the import script at the real boss body.

    python Tools/switch_to_boss001.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/import_and_place.py"

PAIRS = [
    ("boss_cowf.gltf", "boss001.gltf"),
    ('NAME = "SK_BossCowf"', 'NAME = "SK_Boss001"'),
    ('LABEL = "MX_BOSSCOWF"', 'LABEL = "MX_BOSS001"'),
    ("LOCATION = unreal.Vector(9400.0, -6200.0, 3720.0)",
     "LOCATION = unreal.Vector(9350.0, -6200.0, 3740.0)"),
    ("SCALE = 3.0", "SCALE = 1.0"),
]


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    for old, new in PAIRS:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    if changed == 0:
        print("nothing to change")
        return
    open(PATH, "w", encoding="utf-8").write(text)
    print("applied %d change(s)" % changed)


if __name__ == "__main__":
    main()
