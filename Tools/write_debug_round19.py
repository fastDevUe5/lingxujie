"""Append the closing round of the debugging series.

    python Tools/write_debug_round19.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 76. 调试系列第 19 轮：**收口 —— 一致性检查 + 总结**（2026-11-26 61:00）

### 一、三项验收

| # | 检查 | 结果 |
| --- | --- | --- |
| 1 | 体检工具 | `actors: 116` / `references checked: 103, missing: 0` / `collapsed skeletons: 4` |
| 2 | 项目测试 | **completed=15 failed=0 / ALL TESTS PASSED** |
| 3 | 文档与坑 | **调试文档 20 篇 / 全部文档 66 篇 / Gotchas 110 条** |

### 二、🔴 发现并修掉的结构问题

**磁盘有 19 篇调试文档，但 `LEARNING-INDEX.md` 只提到 11 篇。
→ 另外 7 个案例文档只能从调试索引找到，从主入口找不到。**

**修法：在学习索引的调试表下加了「七个实战案例」小表，逐条列出性质和状态。**

**修后核实：**
```
磁盘上的调试文档: 19 篇
学习索引里没提到的: （无，全覆盖）
```

### 三、新增 `Docs/UE5-DEBUG-SUMMARY.md`

**17 轮的收口文档，五节：**

| 节 | 内容 |
| --- | --- |
| 一 | 起点是什么、我自己定的四条标准 |
| 二 | 八个域 + 七个案例 + 两个工具 |
| 三 | **六类结论各自的验证方式** |
| 四 | **17 轮里更正自己的 9 次** |
| 五 | **还没做到的 7 件事（诚实清单）** |

**两个索引顶部都指向它。**

### 四、四之九次更正里最重要的三型

| 型 | 例子 | 出现次数 |
| --- | --- | --- |
| **把方法失败当事情做不到** | `set_position` 不求值 / `get_bone_pose` 挂死 | 2 |
| **数字真但含义错** | 101 个缺材质 / Textures 只有 1 个 | 2 |
| **把报错当结果** | `Get-Process` 报错 → 以为进程没了 | 1 |

**→ 第三型是这一轮又犯的（`Get-Content` 乱码）。**

**共同点：**推理真、前提错**。防法只有一条：**
**任何结论落地前，找一个能推翻它的独立观察。**

### 五、诚实清单（写在总结第五节）

| 事项 | 状态 |
| --- | --- |
| **三处导出器修复** | **已定位、已验证，未应用** |
| 一处材质赋值 | 已定位，未应用 |
| 网络调试 | 源码为主，**零实测** |
| minidump 分析 | 本机无 cdb/符号 |
| GPU 抓帧 | 本机无 RenderDoc/PIX |
| 蓝图断点 | Python 设不了 |
| 性能实测数字 | 面板抓不到，还没用 Insights 量 |

**⚠️ 最重要一条：所有修复停在「验证了机制」，没落到代码。**
**→ 「能定位」已证明；「能修好并确认」只证明了一半。**

### 六、调试系列最终结构

| 层 | 文档 |
| --- | --- |
| **入口** | `UE5-DEBUG-INDEX.md`（顶部指向手册和总结）|
| **总结** | `UE5-DEBUG-SUMMARY.md` |
| **决策** | `UE5-DEBUG-PLAYBOOK.md` |
| 机制（9 篇）| LOGGING / ASSERTS / CRASH / PERF / MEMORY / RENDER / SCRIPT / NET / ASSET |
| 实战（7 篇）| CASE-ANIM / NORMALS / IBM / MATERIAL / WARNING / TESTNOISE / MIP |
| 工具 | `UE5-DEBUG-TOOLKIT.md` + `diagnose.py` + `diff_captures.py` |

### 七、下一轮

**调试系列到此收口。**
**下一步最有价值的是**应用三处修复并跑体检验证** —— 把「能定位」补成「能修好」。**

**⚠️ 那会改代码，需要人点头。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 76." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 76; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
