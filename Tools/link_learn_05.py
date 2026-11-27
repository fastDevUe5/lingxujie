"""Link the fifth block and tidy the one-off scripts from this round.

    python Tools/link_learn_05.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

FOURTH_ROW = ("| **Lumen 第四块** | **`Docs/UE5-LEARN-LUMEN-04.md`** | "
              "✅ **搭出可控练习关卡**；10 cm 天花板漏光、60 cm 不漏，实验成功 |")

FIFTH_ROW = ("| **Lumen 第五块** | **`Docs/UE5-LEARN-LUMEN-05.md`** | "
             "🔴 **更正**：练习关卡零距离场，测的是阴影穿透不是 GI 漏光 |")

SCRATCH = [
    "Tools/learn_df_cost_test.py",
    "Tools/learn_light_control.py",
    "Tools/learn_light_restore.py",
    "Tools/learn_back_main.py",
]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-LUMEN-05" not in text and FOURTH_ROW in text:
        text = text.replace(FOURTH_ROW, FOURTH_ROW + "\n" + FIFTH_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the fifth block")
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
