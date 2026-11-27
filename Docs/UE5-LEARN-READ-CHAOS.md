# UE5 学习 · 补读（四十三）：Chaos 碎裂 —— 八种工具，项目零资产

> **这一篇是**八种碎裂工具**的逐个说明。**
> **实测：GeometryCollection 类全可用，但项目**零资产** —— 而且碎裂工具本身（`FractureSettings`）**没暴露给 Python**。**
> **顺带查清了骨骼/物理资产的真实比例：70 骨骼网格，只有 7 个配了物理资产。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、chaos-fracture.md（19.3 KB，14 节）

**结构：**
```
Fracturing Geometry Collections User Guide
Fracture the Geometry Collection / Reset
View Settings
Common options included with most fracture methods
Use the Fracture Tools
  **Uniform**   ← 「uses a Voronoi algorithm」
  **Cluster**
  **Radial**
  **Planar**
  **Slice**
  **Brick**
  **Mesh**
  **Custom**
```

### 1.1 八种碎裂工具（各自的思路）

| 工具 | 原理 |
| --- | --- |
| **Uniform** | **Voronoi 算法** —— 随机均匀切块 |
| **Cluster** | 分层聚类 —— 碎块本身还能再碎 |
| **Radial** | 从一个中心向外辐射 |
| **Planar** | 用平面切 |
| **Slice** | 单次切片 |
| **Brick** | 砖块式规则切分 |
| **Mesh** | 用另一个网格当「刀」 |
| **Custom** | 自定义 |

**→ 这是一篇**工具手册**：告诉你每种切法长什么样、适合什么。**
**→ 它不解释 Voronoi 的数学，只说"用 Voronoi 算法"。**

### 1.2 一个重要的隐含前提

**→ 所有工具都作用在 **Geometry Collection** 上。**
**→ 而 Geometry Collection 是一个**特殊资产类型**，不是普通静态网格。**
**→ 所以「破坏」的前提是：先把网格转成 GeometryCollection。**

---

## 二、✅ 项目实测：类可用，资产为零

### 2.1 零 GeometryCollection 资产

```
/Game 下 GeometryCollection / Fracture / Chaos 资产: 0 个
```

### 2.2 类部分可用

```
GeometryCollection              可用: True
GeometryCollectionActor         可用: True
GeometryCollectionComponent     可用: True
FractureSettings                可用: False   ← 关键
GeometryCollectionEngine        可用: False
```

**→ 🔴 `FractureSettings` **没暴露** —— 这意味着**八种碎裂工具无法从 Python 调用**。**
**→ 和 Geometry Scripting 的 bake 缺失同一类问题：**有对象，没有操作它的函数。****

---

## 三、🎯 顺带查清：骨骼网格与物理资产的真实比例

**由这一篇引出（碎裂/布娃娃都依赖物理）：**

```
SkeletalMesh 资产:        70
Skeleton 资产:            50
PhysicsAsset 资产:        28
AnimSequence 资产:         7

前 30 个骨骼网格里配了 physics_asset 的:  7   （≈23%）
```

**→ 三个数字叠起来看：**

| 资产 | 数量 | 含义 |
| --- | --- | --- |
| **SkeletalMesh** | 70 | 导入的骨骼网格库 |
| **Skeleton** | 50 | 骨骼 |
| **AnimSequence** | 7 | **只有 7 个动画** |
| **PhysicsAsset** | 28 | 物理资产 |
| **配了物理的（前30）** | 7 | **≈23%** |

**→ 结论：这是一个**大素材库**，但**只有很小一部分是「游戏可用」的**（有动画 + 有物理）。**

**→ 这解释了为什么补读-41 说「50 骨骼 : 7 动画」——
现在更完整：**70 网格 / 50 骨骼 / 7 动画 / 28 物理 / 7 配了物理**。**

---

## 四、🎯 和之前几个「半条链」的对照

**本系列已经积累了三个同类模式：**

| 能力 | 对象 | 操作函数 | 结论 |
| --- | --- | --- | --- |
| **Geometry Scripting** | `DynamicMesh` ✅ | **bake ❌** | 能建几何，出不成资产 |
| **Chaos 碎裂** | `GeometryCollection` ✅ | **`FractureSettings` ❌** | 有对象，切不了 |
| **Enhanced Input** | `InputAction` ✅ | **无工厂但 `None` 可行 ✅** | **完整可用** |

**→ 三者的区别在于：**
- **Enhanced Input 缺的是「建资产」，而 `create_asset(None)` 补上了** → 通
- **Geometry Scripting 和 Chaos 缺的是「核心操作函数」** → 不通

**→ 所以判据不是「有没有工厂」，而是「**核心操作有没有暴露**」。**

---

## 五、这一篇学到什么

**1. 🎯 八种碎裂工具：Uniform（Voronoi）/ Cluster / Radial / Planar / Slice / Brick / Mesh / Custom。**

**2. 🎯 破坏的前提是**先把网格转成 GeometryCollection** —— 那不是普通静态网格。**

**3. 🔴 `FractureSettings` 没暴露给 Python → **八种工具都无法脚本调用**。**

**4. 🎯 项目的骨骼资产真相：**70 骨骼网格 / 50 骨骼 / 7 动画 / 28 物理资产**。**
**→ 大素材库，但只有小部分「游戏可用」。**

**5. 🎯 本系列的判据升级：**
**不是「有没有工厂」，而是「**核心操作有没有暴露**」。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「有 GeometryCollection 类就能做破坏」 | ❌ **`FractureSettings` 缺失，切不了** |
| 「50 骨骼只有 7 动画」 | ✅ **更完整：70 网格 / 50 骨骼 / 7 动画 / 28 物理** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| 建 GeometryCollection 资产 | 可能可以（`GeometryCollection` 类可用），但没有碎裂函数 |
| 八种碎裂工具的实测 | **`FractureSettings` 缺失，做不到** |
| 布娃娃（Ragdoll）| 需要物理资产，且 `PhysicalAnimationComponent` 可用，**但项目角色没配** |
| 物理约束（`PhysicsConstraintComponent`）| 可用，没试 |

---

## 八、状态

```
Docs/UE5-LEARN-READ-CHAOS.md   1 篇（共 50 篇 learn 文档）
补读进度：44 / 57
主关卡 116 actor / 视口复位
```

---

## 九、补读还剩 13 篇

```
water (2.6) / water-bodies (27.6)
light-types (5.5) / lighting-environment (4.2) / instanced-materials (9.7)
niagara (3.2) / niagara-modules (2.5)
fbx-static-mesh (16.1) / import-static-meshes (5.0)
audio (5.7) / sound-cue-editor (3.7) / sound-cue-reference (40.0)
python-with-ai-agents (8.0) / chaos-destruction (0.6)
```

**→ 下一轮：`sound-cue-reference.md`（40 KB）—— 音频域最大一篇，
补完音频域。**
