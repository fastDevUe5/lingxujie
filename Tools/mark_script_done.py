"""Mark the script document done and put its findings into the indexes.

    python Tools/mark_script_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    (
        "| 7 | 蓝图与脚本调试 | `UE5-DEBUG-SCRIPT.md` | 待做 |",
        "| **7** | **蓝图与脚本调试** | **`UE5-DEBUG-SCRIPT.md`** | ✅ **已完成** |",
    ),
    (
        "| 蓝图与脚本调试 | `UE5-DEBUG-SCRIPT.md` | 待做 |",
        "| **蓝图与脚本调试** | **`Docs/UE5-DEBUG-SCRIPT.md`** | ✅ 已完成 |",
    ),
]

LESSONS = """- **Python 异常永远打不垮编辑器**（实测连炸 4 次全程 healthy）—— 「脚本报错」和「编辑器崩了」是两件事
- **蓝图 runaway 循环抛异常时会弹模态对话框** —— 自动化环境里会卡死（`bp.ScriptRecurseLimit=120`、循环上限 100 万）
- **语法错误在日志里打两遍**（插件一次 + stderr 重定向一次）—— 重复不代表跑了两次
"""


def main():
    for path in (DEBUG_INDEX, LEARNING_INDEX):
        text = open(path, encoding="utf-8").read()
        changed = 0
        for old, new in PAIRS:
            if old in text and old != new:
                text = text.replace(old, new)
                changed += 1
        if changed:
            open(path, "w", encoding="utf-8").write(text)
            print("%s: %d row(s) updated" % (path.rsplit("/", 1)[-1], changed))
        else:
            print("%s: nothing to change" % path.rsplit("/", 1)[-1])

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    anchor = "- **改渲染能被截图抓到（16.7% 像素差），改 Canvas 覆盖层抓不到（0%）** —— 决定验证方式"
    if anchor in text and "runaway" not in text:
        text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("added the three script lessons")


if __name__ == "__main__":
    main()
