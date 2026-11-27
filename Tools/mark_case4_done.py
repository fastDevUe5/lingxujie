"""Add case 004 to the indexes and note the fourth same-shaped near-miss.

    python Tools/mark_case4_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = (
    "| **Boss 模型散开** | **`UE5-DEBUG-CASE-IBM.md`** | "
    "**逆绑定矩阵转置了两次：平移从 12/13/14 槽跑到 3/7/11，glTF 读到全零 → 骨骼塌缩到原点** |"
)

NEW_ROW = (
    "| **材质缺失（真假各一）** | **`UE5-DEBUG-CASE-MATERIAL.md`** | "
    "**「101 个 Nanite 网格缺材质」是误报（98 个有组件 override）；真缺陷是 `MX_BOSS001_STATIC` 一个** |"
)

LESSON = (
    "- **结论与观察矛盾时，先信观察** —— 「101 个网格都用默认材质」但画面有贴图，"
    "一查发现 98 个靠组件 override；这是第四次同型误报被直觉拦住\n"
)


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "CASE-MATERIAL" not in text:
        if ANCHOR in text:
            text = text.replace(ANCHOR, ANCHOR + "\n" + NEW_ROW, 1)
            open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
            print("debug index: added the fourth case row")
        else:
            print("debug index: anchor not found")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "先信观察" not in text:
        anchor = "- **验证必须用独立读取者**"
        if anchor in text:
            text = text.replace(anchor, LESSON + anchor, 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the observation lesson")
        else:
            print("learning index: anchor not found")
    else:
        print("learning index: already present")


if __name__ == "__main__":
    main()
