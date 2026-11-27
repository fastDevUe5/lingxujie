# UE5 学习 · 补读（三十五）：蓝图 —— 项目里 5 个蓝图，一个都没用

> **文档讲蓝图的五种类型和玩法。**
> **实测：项目有 5 个 Blueprint 资产，但**关卡里零个实例**。**
> **→ 这不是「蓝图用得少」，是「蓝图没参与这个关卡」。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、blueprints.md（21.4 KB，19 节）

### 1.1 🎯 蓝图的五种类型（文档分类）

| 类型 | 用途 |
| --- | --- |
| **Blueprint Class** | 最常见的「蓝图」，一个可实例化的类资产 |
| **Level Blueprint** | **每个关卡都有**，关卡级的全局脚本 |
| **Blueprint Interface** | 一组函数签名（像 C++ 的纯虚接口）|
| **Blueprint Function Library** | 存**静态函数**的库 |
| **Blueprint Macro Library** | 存**宏**的容器 |
| **Blueprint Utilities**（Editor Utility）| **只在编辑器里跑**的蓝图 |

**→ 关键点：Level Blueprint 是**每个关卡都有**的，不需要手动创建。**

### 1.2 蓝图的三个组成部分

| 部分 | 作用 |
| --- | --- |
| **Construction Script** | **蓝图 actor 生成时**执行（编辑器里放置时也跑）|
| **Event Graph** | 事件驱动的逻辑图 |
| **Variables / Functions** | 属性与函数 |

**→ `Construction Script` 在**编辑器里放置时也会执行** —— 这是个双刃剑：
→ 好处：可以程序化摆组件
→ 陷阱：放 100 个实例就执行 100 次，编辑器会卡**

---

## 二、✅ 项目实测：5 个蓝图，0 个使用

### 2.1 全部蓝图资产（只有 7 个）

```
Blueprint         BP_GlobalFoliageActor    /Game/Fab/Megascans/Plants/
Blueprint         BP_CurvedRoof            /Game/Props/
Blueprint         BP_GrassField            /Game/Props/
Blueprint         BP_StoneField            /Game/Props/
Blueprint         BP_Terrain               /Game/Props/

WidgetBlueprint   WBP_LabLabel             /Game/Learning/      ← 我自己建的
WidgetBlueprint   WBP_Test                 /Game/Moxiang/UI/
```

**→ 总共 7 个，其中 1 个是我建的（`WBP_LabLabel`）。**

### 2.2 🔴 关卡里**零个**蓝图实例

```
/Game/Maps/LingXuJie  关卡里放置的 BP_ 实例: {}
```

**→ 116 个 actor 里，**没有一个**来自蓝图。**
**→ 全是 C++ 类（`LXJGameMode` / `LXJCharacter` / `LXJMonster` / `LXJHUD`）
或普通 `StaticMeshActor`。**

### 2.3 那 5 个蓝图是什么

**→ 名字看，都是**道具/环境容器**：地形、草地、石头场、曲屋顶、植被。**
**→ 它们**没被放进关卡** —— 可能是导入素材时带的、或早期试验留下的。**

**→ 但它们的父类读不到（`parent_class` 返回 None），
所以无法确认它们是简单容器还是有逻辑。**

---

## 三、🎯 这和项目设计前提一致

**AGENTS.md 原文：**
> **「不把玩法逻辑写进蓝图（设计前提是 C++ + Python；蓝图只做胶水）」**

**→ 实测证明了这条被执行得更彻底：**
**→ 不只是「玩法不在蓝图里」，而是「关卡里根本没有蓝图」。**

### 3.1 这个选择的理由（从项目结构反推）

| 理由 | 证据 |
| --- | --- |
| **可单元测试** | 项目有 15 条 C++ 自动化测试（`Private/Tests/`）；蓝图无法这样测 |
| **可脚本生成** | `Tools/build_level.py` 用 Python 生成关卡；蓝图节点图**无法用 Python 编辑** |
| **可版本控制 diff** | C++ 代码 diff 可读；蓝图是二进制 `.uasset`，diff 不可读 |
| **性能** | C++ 比蓝图快（但这不是主要理由）|

**→ 最关键的是第二条：**蓝图逻辑无法用 Python 生成。**
**→ 如果玩法在蓝图里，`build_level.py` 就没法生成完整关卡。**

---

## 四、🎯 蓝图的真实定位（从文档读出的定价）

| 蓝图擅长 | 蓝图不擅长 |
| --- | --- |
| **快速原型**（不用编译）| 大规模重构（节点图连线会失控）|
| **美术/策划自助** | 单元测试 |
| **编辑器工具**（Editor Utility）| 版本控制 diff |
| **简单胶水逻辑** | 脚本化生成 |
| **Construction Script 程序化摆件** | 性能敏感路径 |

**→ 这个项目把蓝图**完全排除在关卡之外**，代价是：**
- 美术/策划不能自助加道具（要改 Python 或 C++）
- 快速试验慢一点（要重编译）

**→ 收益是：关卡完全可脚本重建、可测试、可读 diff。**

**→ 对一个**程序生成关卡 + 大量自动化**的项目，这个取舍成立。**

---

## 五、这一篇学到什么

**1. 🎯 蓝图有**五种**类型，其中 **Level Blueprint 每个关卡都有**（不需要建）。**

**2. 🎯 `Construction Script` 在**编辑器里放置时也会执行** —— 大量实例会卡编辑器。**

**3. 🔴 项目只有 7 个蓝图资产，且**关卡里零个实例**。**
**→ 蓝图完全没参与这个关卡。**

**4. 🎯 这个选择的核心理由是：**蓝图逻辑无法用 Python 生成**。**
**→ 项目靠 `build_level.py` 生成关卡，所以玩法必须在 C++ 里。**
**→ 「可测试 / 可 diff / 可脚本生成」三条都指向 C++。**

**5. ✅ 项目和 AGENTS.md 的声明一致，且比声明更彻底。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「项目用蓝图做胶水」 | ❌ **关卡里一个蓝图实例都没有** |
| 「蓝图用得少是技术债」 | ⚠️ **是**刻意的**架构选择，理由是脚本化生成** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **建一个带 Construction Script 的蓝图实操** | **可以做**，但项目不用蓝图 |
| 蓝图节点图的 Python 编辑 | **做不到**（本系列 MAT 块已确认材质图可编辑，但蓝图节点图没有对应 API）|
| Level Blueprint 的内容 | 没查（项目可能用它做初始化）|
| Blueprint Function Library | 没建过 |

**→ ⚠️ 值得注意：Level Blueprint 是「每个关卡都有」的，
我**没有查过项目关卡的 Level Blueprint 里有什么**。那可能是隐藏逻辑的位置。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-BP.md   1 篇（共 46 篇 learn 文档）
补读进度：36 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 21 篇）。下一批：**
- `sequencer-editor.md`（14.4 KB）
- `geometry-scripting.md`（10.4 KB）
- `fbx-static-mesh.md`（16.1 KB）
- `asset-management.md` — 已合并到补读-17

**→ 选 `geometry-scripting.md`（10.4 KB）—— 程序化几何，和项目的程序化地面直接相关。**
