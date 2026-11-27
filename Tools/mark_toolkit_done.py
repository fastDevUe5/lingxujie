"""Add the toolkit document to the indexes and correct the texture count.

    python Tools/mark_toolkit_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

TOOLKIT_SECTION = """
## 八、可复用的体检工具

| 工具 | 覆盖 | 用法 |
| --- | --- | --- |
| **`Tools/diagnose.py`** | 资产/引用/骨骼/动画/内存/配置 | **`py Tools/diagnose.py`** |

**第一次跑就抓到全部已知缺陷：4 个骨骼角色**同时**中了「骨骼塌缩」和「没有动画」两个 bug。**

**文档：`UE5-DEBUG-TOOLKIT.md`（含它能查什么、查不出什么）。**
"""

CORRECTION = """- **`/Game/Moxiang` 有 99 个 Texture2D，不是 1 个** —— 之前只查了 `Textures` 子目录就下结论，分母搞错
"""


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "TOOLKIT" not in text:
        with open(DEBUG_INDEX, "a", encoding="utf-8") as handle:
            handle.write(TOOLKIT_SECTION)
        print("debug index: appended the toolkit section")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "99 个 Texture2D" not in text:
        anchor = "- **`/Game` 2194 个资产但 `/Game/Moxiang` 只有 370** —— 「项目有 N 个资产」的分母容易搞错"
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + CORRECTION.rstrip(), 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the texture count correction")
        else:
            print("learning index: anchor not found")
    else:
        print("learning index: already present")

    # Register the toolkit in the debug table.
    text = open(LEARNING_INDEX, encoding="utf-8").read()
    row = "| **资产与加载** | **`Docs/UE5-DEBUG-ASSET.md`** | ✅ 已完成 |"
    new_row = "| **🔧 体检工具** | **`Docs/UE5-DEBUG-TOOLKIT.md`** | ✅ 已完成 |"
    if row in text and "UE5-DEBUG-TOOLKIT" not in text:
        text = text.replace(row, row + "\n" + new_row, 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the toolkit row")


if __name__ == "__main__":
    main()
