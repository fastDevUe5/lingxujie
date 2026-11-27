"""Mark the networking document done and add it to both indexes.

This one is different from the others: most of it is source reading rather than measurement, because
the project has no network. The index entry says so rather than implying equal confidence.

    python Tools/mark_net_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    (
        "| 8 | 网络调试 | `UE5-DEBUG-NET.md` | 待做 |",
        "| **8** | **网络调试**（**源码为主，本项目无网络未实测**）| **`UE5-DEBUG-NET.md`** | ⚠️ **已完成（未实测）** |",
    ),
    (
        "| 网络调试 | `UE5-DEBUG-NET.md` | 待做 |",
        "| **网络调试** ⚠️ | **`Docs/UE5-DEBUG-NET.md`** | ⚠️ 源码核实，**未实测** |",
    ),
]

LESSONS = """- **敲一个 CVar 名字：有 `= value` 才存在，只有 `Cmd:` 就是不存在** —— 通用判据
- **`net PktLag` / `PktDup` / `PktOrder` 有互斥** —— `PktOrder` 优先，`PktDup` 不能和 `PktLag` 同用，设了会静默失效
- **网络模拟设置存全局、跨 PIE 重启残留** —— 排查「PIE 有延迟」先检查这个（本项目无 NetDriver，未实测）
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
    anchor = "- **语法错误在日志里打两遍**（插件一次 + stderr 重定向一次）—— 重复不代表跑了两次"
    if anchor in text and "互斥" not in text.split(anchor)[0][-400:]:
        text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("added the three networking lessons")


if __name__ == "__main__":
    main()
