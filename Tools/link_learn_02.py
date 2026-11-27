"""Append the second Lumen block to the practice table.

    python Tools/link_learn_02.py
"""

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

FIRST_ROW = ("| **Lumen 第一块** | **`Docs/UE5-LEARN-LUMEN-01.md`** | "
             "✅ 配置实测 + 图集数据 + 关 GI 量出 37.84% 像素变化 |")

SECOND_ROW = ("| **Lumen 第二块** | **`Docs/UE5-LEARN-LUMEN-02.md`** | "
              "✅ 源码判定骨骼网格有 Card；发现官方文档限制清单不完整 |")


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-LUMEN-02" in text:
        print("already present")
        return
    if FIRST_ROW not in text:
        print("anchor not found")
        return
    text = text.replace(FIRST_ROW, FIRST_ROW + "\n" + SECOND_ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(text)
    print("learning index: added the second block")


if __name__ == "__main__":
    main()
