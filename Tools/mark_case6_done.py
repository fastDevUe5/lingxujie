"""Add case 006 to the indexes.

    python Tools/mark_case6_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = (
    "| **无害警告 + 被推翻的假设** | **`UE5-DEBUG-CASE-WARNING.md`** | "
    "**`Invalid animation skeleton` 是清空动画时的正常提示；「赋值顺序很重要」的假设经实测否决** |"
)

NEW_ROW = (
    "| **引擎测试噪音** | **`UE5-DEBUG-CASE-TESTNOISE.md`** | "
    "**13 条 `Condition failed` 来自引擎 `UnifiedErrorTests.cpp`；项目自己的 15 个测试全过** |"
)

LESSON = (
    "- **日志里的字符串在源码里一定存在** —— 拿日志行去源码搜，是区分引擎噪音和项目失败最快的办法\n"
    "- **`RunTests.ps1` 用独立无头进程**，不碰运行中的编辑器；`RunGame.ps1` 才会 `Stop-Process`\n"
)


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "CASE-TESTNOISE" not in text:
        if ANCHOR in text:
            text = text.replace(ANCHOR, ANCHOR + "\n" + NEW_ROW, 1)
            open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
            print("debug index: added the sixth case row")
        else:
            print("debug index: anchor not found")
    else:
        print("debug index: already present")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    if "引擎噪音" not in text:
        anchor = "- **清空 `anim_to_play` 会打 `Invalid animation skeleton`**"
        if anchor in text:
            text = text.replace(anchor, LESSON + anchor, 1)
            open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the two test-noise lessons")
        else:
            print("learning index: anchor not found")
    else:
        print("learning index: already present")


if __name__ == "__main__":
    main()
