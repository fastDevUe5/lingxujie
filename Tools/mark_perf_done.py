"""Mark the performance document done and add its findings to the indexes.

    python Tools/mark_perf_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    (
        "| 4 | 性能剖析（stat / Insights）| `UE5-DEBUG-PERF.md` | 待做 |",
        "| **4** | **性能剖析（stat / 帧预算）** | **`UE5-DEBUG-PERF.md`** | ✅ **已完成** |",
    ),
    (
        "| 性能剖析 | `UE5-DEBUG-PERF.md` | 待做 |",
        "| **性能剖析** | **`Docs/UE5-DEBUG-PERF.md`** | ✅ 已完成 |",
    ),
    (
        "| 5 | 内存与泄漏（memreport）| `UE5-DEBUG-MEMORY.md` | 待做 |",
        "| 5 | 内存与泄漏（memreport）| `UE5-DEBUG-MEMORY.md` | 待做 |",
    ),
]

# The three facts worth having in the quick-reference block.
LESSONS = """- **`stat unit` 是 0.9/0.1 的 EMA 平滑值** —— 单帧卡顿会被稀释，要用 `stat unitmax`
- **`CaptureViewport` 抓不到 `stat` 面板** —— 它不含 Canvas/HUD 层，`bShowUI` 两种都试过
- **引擎默认 `t.TargetFrameTimeThreshold = 33.9 ms`（30 fps）** —— 不是 16.6，项目目标 60 fps 时要改
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
    anchor = "- **`ensure` 同一行只报一次** —— 第一次没看到就永远消失"
    if anchor in text and "EMА" not in text and "EMA 平滑值" not in text:
        text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("added the three performance lessons")


if __name__ == "__main__":
    main()
