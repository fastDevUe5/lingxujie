"""Link the learning summary into both indexes.

    python Tools/link_learn_summary.py
"""

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = ("| **🎯 完整场景第四块** | **`Docs/UE5-LEARN-SCENE-04.md`** | "
          "✅ **begin_play 游戏态验证**（PlayerController/Pawn/HUD/GameMode 全在）；"
          "量出 14 actor 场景：FrameTime 10.73ms / 工作 0.469ms |")

SUMMARY_ROW = ("| **📋 阶段总结** | **`Docs/UE5-LEARN-SUMMARY.md`** | "
               "22 篇 / 28 条更正；**目标终点已达成**，但 69 篇只覆盖约 17% |")


def main():
    text = open(INDEX, encoding="utf-8").read()

    if "UE5-LEARN-SUMMARY" not in text:
        if ANCHOR in text:
            text = text.replace(ANCHOR, ANCHOR + "\n" + SUMMARY_ROW, 1)
            open(INDEX, "w", encoding="utf-8").write(text)
            print("learning index: added the summary row")
        else:
            print("anchor not found; appending at the end of the section")
            text = text.rstrip("\n") + "\n" + SUMMARY_ROW + "\n"
            open(INDEX, "w", encoding="utf-8").write(text)
            print("learning index: appended")
    else:
        print("already present")


if __name__ == "__main__":
    main()
