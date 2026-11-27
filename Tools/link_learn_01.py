"""Link the first learning block into the index.

    python Tools/link_learn_01.py
"""

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = "## 一、"
ROW = ("| **Lumen 第一块** | **`Docs/UE5-LEARN-LUMEN-01.md`** | "
       "✅ 配置实测 + 图集数据 + 关 GI 量出 37.84% 像素变化 |")


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-LUMEN-01" in text:
        print("already present")
        return

    section = """
## 〇之三、实操学习系列（进行中）

**按本地官方文档逐块学，每块都必须在项目上实测。**

| 主题 | 文档 | 状态 |
| --- | --- | --- |
""" + ROW + "\n"

    marker = "## 一、"
    position = text.find(marker)
    if position < 0:
        print("section marker not found; appending at the end")
        text = text.rstrip("\n") + "\n" + section
    else:
        text = text[:position] + section + "\n" + text[position:]

    open(INDEX, "w", encoding="utf-8").write(text)
    print("learning index: added the practice section")


if __name__ == "__main__":
    main()
