"""Mark the asset document done, which completes the eight-domain plan.

    python Tools/mark_asset_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    (
        "| 9 | 资产与加载问题 | `UE5-DEBUG-ASSET.md` | 待做 |",
        "| **9** | **资产与加载问题** | **`UE5-DEBUG-ASSET.md`** | ✅ **已完成** |",
    ),
]

LESSONS = """- **`could not be found in the Asset Registry` 几乎总是路径猜错了** —— 用 `get_assets_by_path` 按名字搜，不要手写 `/Game/...`
- **`/Game` 2194 个资产但 `/Game/Moxiang` 只有 370** —— 「项目有 N 个资产」的分母容易搞错
- **Cooker 靠引用图找资产，硬编码路径它看不见** —— 编辑器能跑、打包后静默失败的头号原因
"""

COMPLETION = """
## 六、八个域全部完成（第 6 轮收口）

| # | 域 | 文档 | 实测程度 |
| --- | --- | --- | --- |
| 1 | 日志与断言 | `UE5-DEBUG-LOGGING.md` + `UE5-DEBUG-ASSERTS.md` | ✅ 全部实测 |
| 2 | 崩溃与调用栈 | `UE5-DEBUG-CRASH.md` | ✅ 用本项目真实崩溃 |
| 3 | 性能剖析 | `UE5-DEBUG-PERF.md` | ✅ 部分（stat 面板抓不到）|
| 4 | 内存与泄漏 | `UE5-DEBUG-MEMORY.md` | ✅ 全部实测 |
| 5 | 渲染调试 | `UE5-DEBUG-RENDER.md` | ✅ 含像素级 A/B |
| 6 | 蓝图与脚本 | `UE5-DEBUG-SCRIPT.md` | ✅ 故意失败实测 |
| 7 | 网络调试 | `UE5-DEBUG-NET.md` | ⚠️ **源码为主，未实测** |
| 8 | 资产与加载 | `UE5-DEBUG-ASSET.md` | ✅ 用本项目真实日志 |

**八个域覆盖完毕。下一步该做的是**实战演练** ——
找一个项目里的真实问题，用这九篇的方法从头定位，而不是继续写文档。**
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
    if anchor in text and "Asset Registry" not in text:
        text = text.replace(anchor, anchor + "\n" + LESSONS.rstrip(), 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("added the three asset lessons")

    index = open(DEBUG_INDEX, encoding="utf-8").read()
    if "八个域全部完成" not in index:
        open(DEBUG_INDEX, "a", encoding="utf-8").write(COMPLETION)
        print("appended the completion summary")


if __name__ == "__main__":
    main()
