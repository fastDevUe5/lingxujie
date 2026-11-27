# UE5 学习 · 补读（十三）：植被与地形 —— 精确公式，以及项目走的是另一条路

> **这两篇给了很硬的数字（地形尺寸公式、Z 轴换算、推荐尺寸表）。**
> **但它们也暴露一件事：**这个项目根本没用 Landscape 和 Foliage**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、foliage.md（13 KB，15 节）

**结构：**
```
Foliage Edit Mode / Panel / Types / Tools
Brush Options / Filter Settings
**Culling Settings**      ← 实例作为 cluster 单次 draw call 渲染
**LOD Settings**          ← Static Mesh LOD 支持，有 caveat
Lighting                  ← Lightmass 逐实例生成阴影/光照图
**Foliage Scalability**   ← 可接入 Scalability 系统
**Using Foliage with World Partition**  ← 默认网格尺寸
Adding Foliage to a Landscape
Reattaching Foliage Instances
```

**关键机制：**
- **实例按 cluster 合批，单次 draw call** —— 这是植被能铺满的关键
- **逐实例生成光照图**（代价高，所以大面积植被通常用可移动光）
- **World Partition 下有默认网格尺寸**

---

## 二、landscape-technical.md（10.5 KB，12 节）—— 这篇有精确数学

### 2.1 高度图尺寸公式

```
(AQuads + 1, BQuads + 1)

A, B   = 每个方向上 Landscape Component 的数量
Quads  = 每个 Component 的四边形数
```

### 2.2 官方推荐尺寸表（完整）

| 总顶点数 | Quads/节 | 节/组件 | 组件尺寸 | 组件总数 |
| --- | --- | --- | --- | --- |
| **8129 × 8129** | 127 | 4 (2×2) | 254×254 | **1024 (32×32)** |
| 4033 × 4033 | 63 | 4 | 126×126 | 1024 (32×32) |
| 2017 × 2017 | 63 | 4 | 126×126 | 256 (16×16) |
| 1009 × 1009 | 63 | 4 | 126×126 | 64 (8×8) |
| 1009 × 1009 | 63 | 1 | 63×63 | 256 (16×16) |
| 505 × 505 | 63 | 4 | 126×126 | 16 (4×4) |
| 505 × 505 | 63 | 1 | 63×63 | 64 (8×8) |
| 253 × 253 | 63 | 4 | 126×126 | 4 (2×2) |
| 253 × 253 | 63 | 1 | 63×63 | 16 (4×4) |
| **127 × 127** | 63 | 4 | 126×126 | **1** |
| 127 × 127 | 63 | 1 | 63×63 | 4 (2×2) |

**→ 注意规律：顶点数总是 **2^n + 1**（127、253、505、1009、2017、4033、8129）。
→ 因为公式是 `A × Quads + 1`。取 63 的倍数再加 1 就是这个序列。**

**✅ 验算：** `32 × 254 + 1 = 8129` ✓，`16 × 126 + 1 = 2017` ✓，`4 × 126 + 1 = 505` ✓

### 2.3 🎯 Z 轴换算（精确到小数）

**文档原文：**
> **「Unreal Engine calculates your heightmap's height by using values between
> **-256 and 255.992**, stored with **16-bit precision**.
> The calculated height is then multiplied by the **Z scale** value that you input...
> a Z scale value of **1** results in a maximum height of roughly **256 cm** and a maximum depth of **-256 cm**.
> Therefore, at the **default Z scale value of 100**, your height values will be between **256 m and -256 m**.」**

**自定义高度的换算比例：**
> **「the height range is a total of **512 units** (-256 to 0 is 256 units and 0 to 256 is another 256 units),
> the ratio is **1/512 or 0.001953125**」**

**公式：**
```
Z_scale = 目标高度(cm) × 0.001953125
```

**文档例子（Mauna Kea 4207 m）—— ✅ 我验算过：**
```
4207 × 100        = 420,700 cm
420,700 × 0.001953125 = 821.6796875    ← Z scale
256 × 821.6796875 = 210,350 cm         ← 实际高度范围 ±210,350 cm ✓
```

**→ 三个数字自洽。文档这条是**可验证的硬事实**。**

---

## 三、🎯 但项目走的是另一条路（✅ 实测）

```
/Game/Maps/LingXuJie   116 actors
has Landscape actor: False
has Foliage: False
```

**→ 项目**没有 Landscape，没有 Foliage。****

**地面是 `LXJGround` 自建的**（AGENTS.md 记载：「程序化地面（高度场参数存关卡，几何在加载时自建）」）。**

### 3.1 这个选择的代价

| 拿不到的 | 说明 |
| --- | --- |
| **分块 LOD** | Landscape 的组件级 LOD，远处组件降精度 |
| **分块流式** | 组件级 streaming，大地形只加载视野内 |
| **推荐尺寸的优化** | 上面那张表的全部收益 |
| **Foliage 模式** | 无法在它上面刷植被 |
| **Landscape 材质分层** | Layer blend 那套 |

### 3.2 这个选择的收益

| 得到的 | 说明 |
| --- | --- |
| **完全控制高度场** | 参数存关卡，几何在加载时按参数生成 |
| **不依赖 Landscape 资产** | 关卡里没有 Landscape actor，数据更轻 |
| **可以程序化生成任意形状** | 不受 Landscape 的 2^n+1 尺寸约束 |

**→ 这是一个**明确的架构权衡**，不是疏忽。**

---

## 四、这一篇学到什么

**1. 🎯 Landscape 的尺寸不是随便取的：顶点数 = `A × Quads + 1`，所以总是 `2^n + 1` 形态。**

**2. 🎯 Z 轴换算有一个精确常数：`0.001953125`（= 1/512）。**
**这个数字可以从「-256 到 255.992，共 512 个单位」推出来，且文档的例子能验算。**

**3. 🔴 Foliage 的性能关键在「实例合批成单次 draw call」。**
不是「减少数量」，而是「合并绘制」。

**4. 🔴 本项目的程序化地面放弃了 Landscape 的 LOD 和流式。**
**→ 如果将来地图变大，这会成为瓶颈。**

**5. 「没用什么」和「用了什么」一样重要。**
这一篇没有产出任何资产，但明确了**地形这条路项目是绕开走的**。

---

## 五、更正

| 之前 | 现在 |
| --- | --- |
| 「项目有地形，应该和 Landscape 一样」 | ❌ **是自建 mesh，没有 Landscape 的任何优化** |
| 「Z scale 是随便填的倍数」 | ❌ **是 `目标cm × 0.001953125`，有精确换算** |

---

## 六、还没做到

| 项 | 说明 |
| --- | --- |
| 实测 Landscape 的组件 LOD | 项目没 Landscape，**做不了** |
| 实测 Foliage 的合批效果 | 项目没 Foliage，**做不了** |
| 给项目地面加 LOD | 属于开发，不做 |
| 验证 Z scale 换算 | 可以从代码里找常量核对，没做 |

---

## 七、状态

```
Docs/UE5-LEARN-READ-WORLD.md   1 篇（共 35 篇 learn 文档）
补读进度：14 / 57
主关卡 116 actor / 视口复位
```

---

## 八、下一篇

**继续补读（还剩 43 篇）。下一批优先：**
- `hlod.md`（13.6 KB）—— 和地形/流式直接相关
- `world-partition.md`（19.5 KB）—— 同上
- `static-mesh-lod.md`（8.7 KB）

**→ 这三篇是一条线：**LOD → HLOD → World Partition**，正好接上「本项目没有 Landscape LOD」这个缺口。**
