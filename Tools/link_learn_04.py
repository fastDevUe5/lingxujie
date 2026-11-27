"""Link the fourth block and tidy the one-off scripts from this round.

    python Tools/link_learn_04.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

THIRD_ROW = ("| **Lumen 第三块** | **`Docs/UE5-LEARN-LUMEN-03.md`** | "
             "✅ 量出 4 个网格薄于 10 cm（1 个 0.0）；漏光实验**失败**并写明原因 |")

FOURTH_ROW = ("| **Lumen 第四块** | **`Docs/UE5-LEARN-LUMEN-04.md`** | "
              "✅ **搭出可控练习关卡**；10 cm 天花板漏光、60 cm 不漏，实验成功 |")

SCRATCH = [
    "Tools/learn_inventory_engine_assets.py",
    "Tools/learn_ceiling_thickness.py",
    "Tools/learn_verify_ceiling.py",
    "Tools/learn_restore_main.py",
]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-LUMEN-04" not in text and THIRD_ROW in text:
        text = text.replace(THIRD_ROW, THIRD_ROW + "\n" + FOURTH_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the fourth block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
            print("removed %s" % os.path.basename(path))


if __name__ == "__main__":
    main()
