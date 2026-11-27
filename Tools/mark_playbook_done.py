"""Put the playbook at the top of both indexes.

It is the single document a person should open first when something looks wrong, so it belongs beside
the overview rather than buried in the list.

    python Tools/mark_playbook_done.py
"""

DEBUG_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"
LEARNING_INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

HEADER = """# UE5 调试与问题定位 · 系列索引

> **🔴 出问题时先看这份：`UE5-DEBUG-PLAYBOOK.md` —— 症状 → 该查什么。**
"""

SECTION = """
## 九、症状手册（七次实战提炼）

**`UE5-DEBUG-PLAYBOOK.md` 是**决策索引**，不是知识文档：左边是现象，右边是该查什么。**

| 类别 | 覆盖 |
| --- | --- |
| 模型看起来不对 | 散开 / 躺地 / 100 倍大小 / 黑块 / 灰格 |
| 动画不动 | 没赋值 / 模式错 / 改位置没反应 |
| 日志 Error/Warning | 6 种常见文本 → 该查什么 |
| 性能 | 30fps 显示绿 / 平均好看但有卡顿 / CVar 没效果 |
| 内存 | 环数 ≠ 泄漏 / 对象为何不销毁 |
| 渲染 | 缓冲可视化只有 UI / `vis` 拼错名字静默 |
| 脚本 | 没输出 / 异常定位 / 对话框卡死 |
| 崩溃 | `PCallStack` 不是 `CallStack` |

**第五节是七次实战里犯过的**五种推理错误**及各自的防法。**
"""


def main():
    text = open(DEBUG_INDEX, encoding="utf-8").read()

    if "PLAYBOOK" not in text:
        # Put the pointer at the very top, right after the title.
        first_newline = text.find("\n")
        if first_newline > 0 and text.startswith("# "):
            text = text[:first_newline + 1] + \
                "\n> **🔴 出问题时先看 `UE5-DEBUG-PLAYBOOK.md` —— 症状 → 该查什么。**\n" + \
                text[first_newline + 1:]
        with open(DEBUG_INDEX, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("debug index: added the playbook pointer")
    else:
        print("debug index: pointer already present")

    text = open(DEBUG_INDEX, encoding="utf-8").read()
    if "症状手册（七次实战提炼）" not in text:
        with open(DEBUG_INDEX, "a", encoding="utf-8") as handle:
            handle.write(SECTION)
        print("debug index: appended the playbook section")

    text = open(LEARNING_INDEX, encoding="utf-8").read()
    row = "| **🔍 实战案例** | **`Docs/UE5-DEBUG-CASE-ANIM.md`** | ✅ Boss 动画不播放已定位 |"
    new_row = ("| **🩺 症状手册** | **`Docs/UE5-DEBUG-PLAYBOOK.md`** | "
               "✅ 出问题先看这份：症状 → 该查什么 |")
    if row in text and "UE5-DEBUG-PLAYBOOK" not in text:
        text = text.replace(row, new_row + "\n" + row, 1)
        open(LEARNING_INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the playbook row")
    elif "UE5-DEBUG-PLAYBOOK" in text:
        print("learning index: already present")


if __name__ == "__main__":
    main()
