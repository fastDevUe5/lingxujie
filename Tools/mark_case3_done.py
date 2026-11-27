"""Add the third case study to the indexes, with the methodological lesson.

    python Tools/mark_case3_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR_ROW = (
    "| **SM_Boss001 退化法线** | **`UE5-DEBUG-CASE-NORMALS.md`** | "
    "**`TRANSFORM_TYPE_NOT_SOLID (0x10)` 的几何本来就没有可用法线；导出器当正常数据导出了** |"
)

NEW_ROW = (
    "| **Boss 模型散开** | **`UE5-DEBUG-CASE-IBM.md`** | "
    "**逆绑定矩阵转置了两次：平移从 12/13/14 槽跑到 3/7/11，glTF 读到全零 → 骨骼塌缩到原点** |"
)

LESSONS = """- **验证必须用独立读取者** —— 「自己算 IBM 再逆回去」误差 2e-16 也证明不了字节顺序对；要用 glTF 规范位置读回来
- **包围盒正常 ≠ 模型正确** —— 它只量顶点，不量矩阵和绑定姿态
- **退化数据（全零/全同）比错误数据更危险** —— 它「看起来没坏」；67 根骨骼全在同一位置就是这样
"""


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "CASE-IBM" not in text:
        if ANCHOR_ROW in text:
            text = text.replace(ANCHOR_ROW, ANCHOR_ROW + "\n" + NEW_ROW, 1)
            open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
            print("debug index: added the third case row")
        else:
            print("debug index: anchor row not found")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "独立读取者" not in text:
        anchor = "- **「有没有法线」和「法线能不能用」是两件事** —— 客户端读了 NOT_SOLID 的法线但不用"
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the three methodology lessons")
        else:
            print("learning index: anchor not found")
    else:
        print("learning index: already present")


if __name__ == "__main__":
    main()
