"""Mark the memory document done and put its findings into the indexes.

    python Tools/mark_memory_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    (
        "| 5 | 内存与泄漏（memreport）| `UE5-DEBUG-MEMORY.md` | 待做 |",
        "| **5** | **内存与泄漏（memreport / obj cycles）** | **`UE5-DEBUG-MEMORY.md`** | ✅ **已完成** |",
    ),
    (
        "| 内存与泄漏 | `UE5-DEBUG-MEMORY.md` | 待做 |",
        "| **内存与泄漏** | **`Docs/UE5-DEBUG-MEMORY.md`** | ✅ 已完成 |",
    ),
]

LESSONS = """- **`memreport` 延迟到帧末执行（先强制 GC）** —— 输出在 `Saved/Profiling/MemReports/`，不在控制台
- **`obj cycles` 报环数 ≠ 泄漏数** —— 必须看环里是谁；本项目 29 个环内对象全是引擎 World/Level
- **`obj refs name=<对象>` 是回答「为什么没被销毁」的唯一可靠办法**
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
    anchor = "- **引擎默认 `t.TargetFrameTimeThreshold = 33.9 ms`（30 fps）** —— 不是 16.6，项目目标 60 fps 时要改"
    if anchor in text and "obj cycles" not in text:
        text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("added the three memory lessons")


if __name__ == "__main__":
    main()
