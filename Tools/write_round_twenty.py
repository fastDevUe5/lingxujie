"""Append the twentieth round and take stock at the halfway point.

    python Tools/write_round_twenty.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 37. 第二十轮：朝向问题关闭 + 40 轮中点盘点（2026-11-26 25:30）

### 一、朝向问题关闭

**原计划：用两种映射各导一次，保留让 Z 最高的那个。**

**实测七个模型（同一套映射）：**

| 文件 | X / Y / Z (cm) | 最高轴 |
| --- | --- | --- |
| `198_bobu` | 126 / 156 / 110 | Y |
| `w25260` | 10 / 20 / 23 | Z |
| `216` | 59 / 134 / 71 | Y |
| `20_eagle_01` | 84 / 177 / 139 | Y |
| `108_bird` | 143 / 111 / 144 | Z |
| `19240` | 174 / 98 / 133 | X |
| `choco` | 186 / 149 / 40 | X |

**分布 `{Y:3, Z:2, X:2}` —— 没有主导轴，**判据本身无效**。**

**真正的原因：**
> **「最高」只对直立人形等于「高度」。
> 鸟的 Y 是**翼展**，四足兽的 Y 是**体长**，扁平道具的 X 是**宽度**。**

**正确判据是源格式的约定：**
- `.hfl` 高度场把高程存为 **Z**
- `.map` 摆放 `(x y z)`，**z 是高程**
- → 源是 **Z-up**，映射 `(x, z, -y)` 让 glTF Y = 源 Z，**正确**

**`198_bobu` 的 126 × 156 × 110 就是**一只体长大于身高的矮胖生物**，不是 bug。**

**→ gotcha #87：选判据前先验证判据本身。**

### 二、40 轮中点：目标进度盘点

**已完成（20/40 轮）：**

| 领域 | 文档 | 状态 |
| --- | --- | --- |
| 核心架构 | `UE5-CORE-ARCHITECTURE.md` | ✅ |
| 子系统四层 | `UE5-SUBSYSTEMS.md` | ✅ |
| 碰撞 | `UE5-COLLISION.md` | ✅ |
| 物理仿真 | `UE5-PHYSICS.md` | ✅ |
| 渲染 | `UE5-RENDERING.md` | ✅ |
| Lumen | `UE5-LUMEN.md` | ✅ |
| 材质 | `UE5-MATERIALS.md` | ✅ 含实操 |
| 动画（引擎）| `UE5-ANIMATION-ENGINE.md` | ✅ |
| 动画（运行时）| `UE5-ANIMATION-RUNTIME.md` | ✅ |
| 音频 | `UE5-AUDIO.md` | ✅ 含实装 |
| UI | `UE5-UI.md` | ✅ 边界实测 |
| 网络 | `UE5-NETWORKING.md` | ✅ |
| 输入 | `UE5-INPUT.md` | ✅ |
| 资产管线 | `UE5-ASSET-PIPELINE.md` | ✅ |
| API 体量 | `UE5-API-INVENTORY.md` | ✅ 实测 |
| 项目配置 | `UE5-PROJECT-CONFIG.md` | ✅ |
| 网格合并 | `UE5-MESH-MERGE.md` | ✅ |
| Gameplay 流程 | `UE5-GAMEPLAY-FLOW.md` | ✅ |
| **墨香格式** | `MOD-FORMAT-SOLVED` / `ANM-FORMAT-SOLVED` / `MOXIANG-TO-UE-PIPELINE` | ✅ |
| 角色导入 | `CHARACTER-IMPORT-STATUS.md` | ✅ 管道通 |

**共 30+ 篇文档、87 条坑、102 次提交。**

### 三、诚实的掌握度（中点评估）

| 域 | 掌握 | 依据 |
| --- | --- | --- |
| 编辑器脚本 / MCP | **90%** | 自建工具集 + 200+ 工具用过 |
| 核心架构 | **80%** | 继承链 + 生命周期 + 复制标志 |
| 子系统 | **75%** | 四层 + 取用 |
| 碰撞 | **70%** | 三组正交 + CTF |
| 物理仿真 | **50%** | 开关 + 材质 + 约束（零实操）|
| 材质 | **65%** | 三平面实操 |
| 渲染 / Lumen | **55%** | 配置 + 原理（没调过参数）|
| 动画（引擎+运行时）| **55%** | 数据结构 + 状态机（实操靠自建管道）|
| 音频 | **65%** | 实装背景音乐 + 压缩实测 |
| UI | **30%** | 边界实测（做不了）|
| 网络 | **25%** | 机制清楚（零需求）|
| 输入 | **45%** | 三代方案 + 本项目选择 |
| 资产管线 | **45%** | 引用链实测 |
| **墨香格式逆向** | **90%** | 两格式全解 + 端到端验证 |

**`★` 附注：动画和墨香格式这两块已经**超出"学习"进入"工程"** —— 自建了可用管道。**

### 四、剩下的 20 轮

| 优先级 | 任务 | 为什么 |
| --- | --- | --- |
| **1** | **批量导出** | 5,305 模型 + 4,014 动画，现在一次一个 |
| **2** | **材质接入** | 导入警告「未指定材质的图元」|
| 3 | 逆绑定矩阵 | 动画姿态对不上时 |
| 4 | Lumen 参数实操 | 需重启编辑器，先问人 |
| 5 | 后处理实操 | 350 字段已读未调 |

**目标**仍然未完成**，但**主要知识骨架已建立**。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 37." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 37; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
