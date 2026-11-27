"""Add case 007 to the indexes, plus the listtextures NumMips technique.

    python Tools/mark_case7_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = (
    "| **引擎测试噪音** | **`UE5-DEBUG-CASE-TESTNOISE.md`** | "
    "**13 条 `Condition failed` 来自引擎 `UnifiedErrorTests.cpp`；项目自己的 15 个测试全过** |"
)

NEW_ROW = (
    "| **历史警告 vs 当前状态** | **`UE5-DEBUG-CASE-MIP.md`** | "
    "**「贴图无 mip」是 DDS 导入失败的残留；实测 `NumMips=10` 完整，资产健康** |"
)

LESSON = (
    "- **`listtextures <名字>` 有 `NumMips` 列** —— Python 读不到贴图 mip，只能靠这条控制台命令\n"
    "- **日志告诉你发生过什么，不告诉你现在是什么** —— 旧警告必须用当前实测去否定\n"
)


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "CASE-MIP" not in text:
        if ANCHOR in text:
            text = text.replace(ANCHOR, ANCHOR + "\n" + NEW_ROW, 1)
            open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
            print("debug index: added the seventh case row")
        else:
            print("debug index: anchor not found")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "listtextures" not in text:
        anchor = "- **日志里的字符串在源码里一定存在**"
        if anchor in text:
            text = text.replace(anchor, LESSON + anchor, 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the two mip lessons")


if __name__ == "__main__":
    main()
