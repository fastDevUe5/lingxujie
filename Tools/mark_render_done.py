"""Mark the render document done and record the capturability rule in both indexes.

    python Tools/mark_render_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    (
        "| 6 | 渲染调试（CVar / Visualize）| `UE5-DEBUG-RENDER.md` | 待做 |",
        "| **6** | **渲染调试（缓冲可视化 / vis）** | **`UE5-DEBUG-RENDER.md`** | ✅ **已完成** |",
    ),
    (
        "| 渲染调试 | `UE5-DEBUG-RENDER.md` | 待做 |",
        "| **渲染调试** | **`Docs/UE5-DEBUG-RENDER.md`** | ✅ 已完成 |",
    ),
]

LESSONS = """- **`vis <RDG资源名>` 是控制台命令，能改场景渲染；缓冲可视化切换只有菜单** —— `vis help` 是权威语法
- **`vis pool` 列的是运行时渲染目标，不是资产** —— 和 `obj list`/`memreport` 量的不是同一样东西
- **改渲染能被截图抓到（16.7% 像素差），改 Canvas 覆盖层抓不到（0%）** —— 决定验证方式
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
    anchor = "- **`obj refs name=<对象>` 是回答「为什么没被销毁」的唯一可靠办法**"
    if anchor in text and "vis pool" not in text:
        text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("added the three render lessons")


if __name__ == "__main__":
    main()
