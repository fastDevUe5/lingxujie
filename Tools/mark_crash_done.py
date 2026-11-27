"""Mark the crash document as done in both indexes.

The inline attempt failed because a path in the replacement text started with a backslash, which
Python read as a unicode escape. Writing from a file avoids the quoting entirely.

    python Tools/mark_crash_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    (
        "| 3 | 崩溃 / 调用栈 / .dmp | `UE5-DEBUG-CRASH.md` | 待做 |",
        "| **3** | **崩溃 / 调用栈 / 崩溃上下文** | **`UE5-DEBUG-CRASH.md`** | ✅ **已完成** |",
    ),
    (
        "| 崩溃与调用栈 | `UE5-DEBUG-CRASH.md` | 待做 |",
        "| **崩溃与调用栈** | **`Docs/UE5-DEBUG-CRASH.md`** | ✅ 已完成 |",
    ),
]

# The lesson from the crash round, added to the index as a permanent quick note.
LESSON = """| **`UserActivityHint` 告诉你崩溃时在干什么** | 本系列第 3 篇实测 |
| **故障地址按字节解成 ASCII，能判断"数据被当指针"** | 本系列第 3 篇实测 |
"""


def main():
    for path in (DEBUG_INDEX, LEARNING_INDEX):
        text = open(path, encoding="utf-8").read()
        changed = 0
        for old, new in PAIRS:
            if old in text:
                text = text.replace(old, new)
                changed += 1
        if changed:
            open(path, "w", encoding="utf-8").write(text)
            print("%s: %d row(s) marked done" % (path.rsplit("/", 1)[-1], changed))
        else:
            print("%s: nothing to change" % path.rsplit("/", 1)[-1])

    # Add the two new lessons next to the other quick-reference lines.
    text = open(DEBUG_INDEX, encoding="utf-8").read()
    anchor = "| **引擎只在级别**调高**时告发，调低**无记录** | `LogSuppressionInterface.cpp` 345-349 |"
    if anchor in text and "UserActivityHint" not in text:
        text = text.replace(
            anchor,
            anchor + "\n| **崩溃上下文的 `PCallStack` 才带偏移，`CallStack` 只有模块名** | `GenericPlatformCrashContext.cpp` 1208 |",
            1)
        open(DEBUG_INDEX, "w", encoding="utf-8").write(text)
        print("added the PCallStack note")


if __name__ == "__main__":
    main()
