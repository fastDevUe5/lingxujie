"""Append the thirty-sixth round.

    python Tools/write_round_thirtysix.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 53. 第三十六轮：**写最终总览 —— `UE5-KNOWLEDGE-SUMMARY.md`**（2026-11-26 37:00）

### 一、为什么需要这一份

**36 轮产出 31 篇专题文档。**
**但「一堆文档」不是「知识体系」—— 除非有一份东西说清：**

- 哪一篇回答哪个问题
- 哪些结论是**实测**的，可以直接用
- 哪些是**未验证**的，不能当真

### 二、`UE5-KNOWLEDGE-SUMMARY.md` 的结构

| 章 | 内容 |
| --- | --- |
| 一 | **文档地图**（18 篇引擎 + 5 篇格式 + 2 篇工程状态，每篇一句话）|
| 二 | **已掌握结论速查**（架构 / 配置 / API 体量 / 格式 / 数据总量 / 管道产出）|
| 三 | **✅ 已验证 vs ❌ 未验证**（两张表，明确分开）|
| 四 | **104 条坑的分类**（5 类）|
| 五 | **诚实的掌握度评估**（17 个域，平均 61%）|
| 六 | **下一阶段按价值排序**（5 项）|
| 七 | **工具清单**（12 个可复用脚本）|

### 三、「未验证」那张表最重要

| 未验证 | 卡在哪 |
| --- | --- |
| 编辑器里动画**看得见在动** | `set_position` 不触发求值；PIE 里编辑器状态不继承 |
| 96 骨骼人形的**蒙皮姿态正确** | 只验证了 38/67 骨骼的 Boss |
| 材质**多槽**（Boss 有 40 个 MATERIAL 块，只用了 1 槽）| 未按槽分配 |
| 批量导入 UE | 只导入了 4 个角色 |

> **一份省略了这些的总览，比没有总览更糟。**

### 四、掌握度评估（诚实）

| 域 | 掌握 |
| --- | --- |
| 编辑器脚本 / MCP | **90%** |
| 墨香格式逆向 | **90%** |
| 核心架构 | 80% |
| 子系统 | 75% |
| 碰撞 / 网格合并 | 70% |
| 材质 | 68% |
| 音频 / Gameplay 流程 | 65% |
| 渲染 / 动画引擎侧 | 55% |
| 动画运行时 / 物理 | 50% |
| 输入 / 资产管线 | 45% |
| UI | 30% |
| 网络 | 25% |

**平均约 61%。「精通」还差得远 —— 但没有一块是空白。**

### 五、`LEARNING-INDEX.md` 已更新

**新增「〇、先读总览」一章，指向 `UE5-KNOWLEDGE-SUMMARY.md`。**

**新会话开场路径变成：**
```
AGENTS.md → LEARNING-INDEX.md（第〇章）→ UE5-KNOWLEDGE-SUMMARY.md → 再选专题
```

### 六、剩余 4 轮的计划

| 轮 | 任务 |
| --- | --- |
| 37 | 批量材质实例（2,407 PNG → 材质）|
| 38 | 按槽分配材质（Boss 40 个 MATERIAL 块）|
| 39 | 收口：更新所有交叉引用、检查文档一致性 |
| 40 | 最终验收：跑一遍回归 + 报告 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 53." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 53; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
