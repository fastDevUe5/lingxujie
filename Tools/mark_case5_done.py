"""Add case 005 to the indexes and record the falsified hypothesis.

    python Tools/mark_case5_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = (
    "| **材质缺失（真假各一）** | **`UE5-DEBUG-CASE-MATERIAL.md`** | "
    "**「101 个 Nanite 网格缺材质」是误报（98 个有组件 override）；真缺陷是 `MX_BOSS001_STATIC` 一个** |"
)

NEW_ROW = (
    "| **无害警告 + 被推翻的假设** | **`UE5-DEBUG-CASE-WARNING.md`** | "
    "**`Invalid animation skeleton` 是清空动画时的正常提示；「赋值顺序很重要」的假设经实测否决** |"
)

LESSON = (
    "- **清空 `anim_to_play` 会打 `Invalid animation skeleton`** —— 合法操作，引擎只是提示，不必追\n"
    "- **读一段源码得出「必须这样」，可能忽略了同文件的另一条路径** —— 顺序假设就是这样被推翻的\n"
)


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "CASE-WARNING" not in text:
        if ANCHOR in text:
            text = text.replace(ANCHOR, ANCHOR + "\n" + NEW_ROW, 1)
            open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
            print("debug index: added the fifth case row")
        else:
            print("debug index: anchor not found")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "Invalid animation skeleton" not in text:
        anchor = "- **结论与观察矛盾时，先信观察**"
        if anchor in text:
            text = text.replace(anchor, LESSON + anchor, 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the two warning lessons")
        else:
            print("learning index: anchor not found")
    else:
        print("learning index: already present")


if __name__ == "__main__":
    main()
