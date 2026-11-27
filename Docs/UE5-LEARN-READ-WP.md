# UE5 学习 · 补读（十七）：World Partition 与资产管理 —— 两条都没走的路

> **这两篇描述的是**大世界**和**按需加载**的基础设施。**
> **实测结论：项目两条都没用。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、world-partition.md（19.5 KB，24 节）

### 1.1 核心机制

> **「The World Partition system works by storing your world in a single persistent level
> separated into **grid cells**, and provides you with an **automatic streaming system**
> to load and unload those cells based on distance from a streaming source.」**

**关键数字（文档例子）：**
```
Cell Size      = 256m × 256m × 256m
Loading Range  = 768 米半径（围绕 streaming source）
```

### 1.2 两个决定「单元格加载与否」的因素

| 因素 | 说明 |
| --- | --- |
| **1. Streaming Sources** | **每个 Player Controller 就是一个流源**；另有 `World Partition Streaming Source Component` |
| **2. Runtime Grid Settings** | 网格本身的设置 |

### 1.3 其它重要章节

```
Enabling World Partition（三种方式）
Using the Open World Default Map
**Converting Existing Levels to use World Partition**   ← 可以转换
Actors in World Partition（编辑时自动分配到单元格）
Loading and Unloading Regions in the Editor / World Partition Window / Location Volumes
**Dynamic Loading Range Scaling**（改善 PIE 性能）
Generating a Minimap
**Generating Hierarchical Levels of Detail (HLODs)**（Build HLODs 操作）
**Cooking a World Partition world**（必须用 Cook commandlet）
Using World Partition with Blueprint
Debugging and Runtime Overrides（控制台命令）
**World Partition Builder Commandlets**
```

**→ HLOD 在 WP 里是**构建时生成**的（Build HLODs），不是手工摆的。
→ 打包 WP 关卡**必须走 cook commandlet**，这对 `Package.ps1` 有意义。**

---

## 二、asset-management.md（14.3 KB，9 节）

### 2.1 核心概念

> **「The Asset management system in Unreal breaks all Assets into two types,
> **Primary Assets** and **Secondary Assets**.」**

| 概念 | 说明 |
| --- | --- |
| **Primary Asset** | 可以被**显式加载/卸载**的顶层资产（蓝图类、数据资产等）|
| **Secondary Asset** | 被 Primary 引用的资产，跟着一起加载 |
| **Asset Manager** | **单例**，管理所有 Primary Asset 的注册与加载 |
| **Asset Bundles** | **命名的资产列表**，挂在某个 Primary Asset 上 |

**→ Asset Bundles 的用途：把一个 Primary Asset 关联的一组资产打标签，
让「只加载菜单需要的那部分」成为可能。**

### 2.2 为什么重要

**→ 没有 Primary Asset 注册，就没有**异步按需加载策略**。
→ 所有引用关系在关卡加载时一次性解析完。**

---

## 三、✅ 本项目实测：两条都没走

### 3.1 没有 World Partition

```
LingXuJie   116 actors   wp actors []
L_Scene01    14 actors   wp actors []
probe: get_world_partition / is_partitioned_world 都不存在
```

**配置文件：**
```
Config/*.ini 里：完全没有 WorldPartition 配置
DefaultEngine.ini：没有 WorldPartition 段
```

**→ **项目用的是传统单文件关卡。****

### 3.2 没有任何 Primary Asset 注册

```
Config/*.ini 里：完全没有 AssetManager / PrimaryAssetTypes 配置
AssetManagerSettings：不在 Python 里（读不到）
```

**→ 但**配置文件里零条目**已经足够说明问题：**
**→ 项目没有自定义任何 Primary Asset Type。**
**→ 用的是引擎默认的资产加载策略（关卡加载时解析全部引用）。**

### 3.3 uproject 插件清单（✅ 8 个）

```
PythonScriptPlugin               ← Python 脚本
EditorScriptingUtilities         ← 编辑器脚本工具
ModelContextProtocol             ← MCP
ToolsetRegistry                  ← MCP 工具集
EditorToolset                    ← MCP 编辑器工具
AutomationTestToolset            ← MCP 自动化测试
SlateInspectorToolset            ← MCP UI 检查
**ProceduralVegetationEditor**   ← 程序化植被编辑器
```

**→ **没有显式启用 World Partition 插件**（UE5 里它内建，按关卡开关）。
→ **`ProceduralVegetationEditor` 开着** —— 但关卡里没有 Foliage actor（见补读-13）。**

---

## 四、🎯 这意味着什么

### 4.1 拿不到的能力

| 能力 | 现状 |
| --- | --- |
| **单元格流式加载** | ❌ 关卡整体加载 |
| **运行时网格** | ❌ |
| **WP 生成的 HLOD** | ❌ |
| **Primary Asset 按需加载** | ❌ |
| **Asset Bundles 分包** | ❌ |
| **Dynamic Loading Range Scaling** | ❌ |

### 4.2 这个选择对不对

**对**P0 单机垂直切片**来说，是对的：
- 116 个 actor 一次性加载完全没问题
- 没有流式就没有流式的 bug
- 关卡只有一个文件，容易版本控制**

**但这是一个**明确的天花板**：
- 地图规模一大（比如要做到整个兰州城），
  116 → 几万个 actor 时，**必须**上 World Partition
- 那时要做的不是「加配置」，而是**转换关卡格式 + 重新组织资产 + 改 cook 流程**

---

## 五、这一篇学到什么

**1. 🎯 World Partition 的本质是「单关卡文件 + 网格单元格 + 距离流式」。**
不是「多个子关卡」，而是**一个**持久关卡内部切网格。**

**2. 🎯 Cell Size 和 Loading Range 是两个可调数字**（例 256m / 768m 半径）。

**3. 🎯 Player Controller 本身就是流源** —— 不需要额外配置。

**4. 🔴 WP 关卡**必须**用 cook commandlet 打包** —— 这对 `Package.ps1` 是个前提条件。

**5. 🔴 Asset Manager 的 Primary/Secondary 划分是**选择加入**的。**
不注册就一切照旧（同步解析），注册了才有异步按需加载。

**6. ✅ 本项目两条都没走，且对当前规模是合理的。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「大世界靠多个子关卡」 | ❌ **WP 是单关卡内切网格** |
| 「资产加载引擎自动管，没什么可配」 | ❌ **Primary/Secondary 划分要主动注册才有** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| 实测 WP 单元格流式 | 项目没 WP，**做不了** |
| 转换一个练习关卡试 WP | **可以做**（`new_level` 支持 WP 模板？）|
| Asset Bundles 的实际配置 | 没试 |
| WP 的调试控制台命令 | 没查 |

---

## 八、状态

```
Docs/UE5-LEARN-READ-WP.md   1 篇（共 37 篇 learn 文档）
补读进度：18 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 39 篇）。下一批：**
- `collision.md`（7.1 KB）—— 物理域，之前只做落体
- `physics.md`（15.9 KB）—— 物理主篇
- `navigation-basic.md` / `navigation-mesh.md` —— AI 寻路

**→ 选 `collision.md` + `physics.md`，把物理域补扎实。**
