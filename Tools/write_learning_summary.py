"""Append the learning summary to the handoff document.

Writing through a file because the text carries pipes, backticks and quotes that PowerShell
mangles when a heredoc is passed to python -c.

    python Tools/write_learning_summary.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 17. UE5 系统学习：六块完成 + 掌握度自评（2026-11-26 18:50）

### 一、本轮完成的六块（全部引擎源码核实）

| 块 | 文档 | 核心结论 |
| --- | --- | --- |
| **1. 核心架构** | `UE5-CORE-ARCHITECTURE.md` (8.5 KB) | 继承链、生命周期、Gameplay 五类职责 |
| **2. 子系统** | `UE5-SUBSYSTEMS.md` (6.9 KB) | 四层按寿命选；`GameInstanceSubsystem` 直接继承 `USubsystem`，所以跨关卡存活 |
| **3. 渲染** | `UE5-RENDERING.md` (6.9 KB) | 两套 Nanite 结构；**Fallback 网格就是碰撞来源** |
| **4. 碰撞** | `UE5-COLLISION.md` (5.9 KB) | Enabled / 通道 / Response 三组正交 + CTF 怎么选 |
| **5. 四域调查** | `UE5-OTHER-DOMAINS.md` (7.8 KB) | 音频 186 KB / UI 294 KB / 网络 350 KB / 资产 196 KB |
| **6. 资产管线** | `UE5-ASSET-PIPELINE.md` (9.6 KB) | **引用链实测** + 软引用三态 + **Python 无异步加载** |

### 二、实测验证过的硬数据

```
SM_Lanzhou_Terrain:
  Nanite        = false
  三角形        = 524,288    (= 512×512×2)
  顶点          = 263,174
  依赖          = [NavigationSystem, InterchangeEngine, WorldGridMaterial]

Content/Moxiang 资产 298 个:
  SM_LZ_*  = 96   ← 与清单完全一致
  M_LZ_*   = 95
  jp_*     = 49   ← 旧构建遗留
  17_*     = 12   ← 旧构建遗留
```

### 三、新增的两条能力

| 能力 | 怎么做 |
| --- | --- |
| **查任意资产的引用链** | `AssetTools.get_dependencies` / `get_referencers` |
| **找出遗留资产** | 清单 vs 磁盘比对（不能凭名字对不上就删）|

### 四、发现的边界

**Python 侧没有异步加载** —— `AssetTools` 只有 `load_asset`（同步）。
**运行时资产管理必须 C++。** 编辑器自动化能用 Python，运行时不行。

### 五、掌握度自评（六块 + 已有）

| 域 | 掌握 | 证据 |
| --- | --- | --- |
| **编辑器脚本 / MCP / 工具集** | 🟢 **90%** | 自建工具集跑通，217 个工具逐条读过 |
| **核心架构** | 🟢 **80%** | 继承链、生命周期、复制标志都查过 |
| **子系统** | 🟢 **75%** | 四层结构 + 三个判断问题 |
| **碰撞** | 🟢 **70%** | 三组正交概念 + CTF 选择 |
| **资产管线** | 🟡 **45%** | 引用链实测过，异步加载确认做不到 |
| **渲染** | 🟡 **35%** | Nanite/后处理结构清楚，Lumen 零 |
| **动画** | 🟡 **30%** | 墨香侧格式 85%，引擎侧只到边界 |
| **音频** | 🟡 **25%** | 知道类，没播过声音 |
| **UI** | 🟡 **20%** | 知道三层，没做过控件 |
| **网络** | 🔴 **10%** | 知道 GameMode/GameState 复制差异 |

### 六、下一轮该学什么

**按"本项目最需要"排序：**

| 顺位 | 域 | 理由 |
| --- | --- | --- |
| 1 | **动画引擎侧** | 墨香 4,056 个动画要导入，这是唯一硬阻塞 |
| 2 | 音频 | 481 个音频已提取，迟早要播 |
| 3 | 材质图 | 观感最关键，且有 22 个现成工具 |
| 4 | UI（UMG） | 古风样式 Canvas 做不出来 |
| — | 网络 | **P0 单机不需要** |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 17." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 17; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
