# UE5 学习 · 补读（十五）：LOD —— 一次差点误报的审计

> **审计先给出「143 个网格缺 LOD」这个吓人的数字。**
> **再查一步，发现它们**一个都没放进关卡**。**
> **→ 这是我第 N 次踩「资产数 ≠ 屏幕上有什么」。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、static-mesh-lod.md（8.7 KB，6 节）

```
Setup
Creating LODs
Using LOD Groups
Manually Creating LODs
End Result
```

**关键机制：**
- **`Auto Compute LOD Distances`** —— 自动算每个 LOD 的屏幕尺寸阈值
- **顶点合并 / 三角形塌陷** —— 简化时选「最佳位置放置合并后的顶点」，并移除随之塌陷的三角形
- **`LOD Group`** —— 预设（如 `SmallProp`），决定默认的屏幕尺寸阈值
- **`Percent Triangles`** —— 每个 LOD 保留的三角形比例

**文档的例子：** `LOD2 = 25%`，`LOD3 = 12%`

---

## 二、hlod.md（13.6 KB，10 节）

```
Property and Interface Reference
HLOD Actions / HLOD Scene Actors
LOD Actor Context Menu / Actor Context Menu
Properties
**Cluster Generation Settings**
**Mesh Generation Settings**
**Material Settings**
```

**关键机制（文档原话）：**
> **「It calculates the distance at which the cluster would occupy the user defined screen size,
> according to a fixed Field of View (FOV) / 16:9 ratio」**

**→ HLOD 把一组 actor **合并成一个代理网格**，按「集群占屏幕多大」决定何时切换。
→ 三个设置组：**集群生成**（怎么分组）/ **网格生成**（怎么合并）/ **材质**（合并后的材质怎么办）。**

**→ 这是**流式 + 远处几何**的核心手段。**

---

## 三、🔴 审计第一步：吓人的数字

```
StaticMesh assets in /Game:      610
  多 LOD:                        240
  单 LOD:                        370
  Nanite 启用:                   227

单 LOD 且无 Nanite:              143
```

**→ 非 Nanite 的 383 个里，**143 个（37%）没有 LOD**。**

**为什么这看起来严重 —— VSM 文档原话：**
> **「It is important that non-Nanite meshes have LODs setup
> or else they become **extremely expensive to render into small pages**.」**

**→ 这 143 个正好是 VSM 文档警告的那一类。**

**→ 我第一反应是「发现了大问题」。**

---

## 四、🎯 审计第二步：它们根本不在关卡里

**改成问「**屏幕上实际有什么**」，不是「**库里有什么**」：**

```
关卡里实际放置的网格:              99 种 / 99 个组件
其中「单 LOD 且无 Nanite」的:      0
实例数:                            0
```

**→ **零个。****

**→ 那 143 个资产是**素材库里的备用件**，当前关卡一个都没用。**

**→ **不是问题。是我的审计口径错了。****

---

## 五、🔴 这是同一个错误第 N 次出现

**回顾本系列里同类错误：**

| 轮次 | 我量了什么 | 我该量什么 |
| --- | --- | --- |
| 早期 | **文件个数**判 API 是否有效 | 内容是不是 404 页 |
| 早期 | **链接行数**判是不是索引页 | 正文长度 |
| 早期 | **字节数**判抓取成功 | `<title>` |
| **本轮** | **资产数**判性能问题 | **放置实例数** |

**→ 四次都是同一个形状：**
**用一个「便宜但间接」的指标代替「贵但直接」的指标。**

**→ 而且每次都**偏悲观**（把没问题判成有问题）。**

---

## 六、这一篇学到什么

**1. 🎯 性能问题的正确口径是「屏幕上有什么」，不是「库房里有什么」。**
610 个资产里 143 个缺 LOD 听起来严重，实际放置数是 0。

**2. 🔴 我差点基于错误的审计结果去「修」143 个资产。**
**那会浪费大量时间，且可能改坏素材。**
**→ 审计的第一条纪律：先确认问题会不会真的发生。**

**3. 🎯 `Auto Compute LOD Distances` + `LOD Group` + `Percent Triangles` 是 LOD 的三件套。**
文档例子里 LOD2=25%、LOD3=12%。

**4. 🎯 HLOD 的判据是「集群占屏幕多大」，按固定 FOV/16:9 算。**
→ 它解决的是「远处一堆小物件太多 draw call」的问题。

**5. 🔴 「便宜指标代替直接指标」是本系列最顽固的错误形状。**
四次了，每次都需要被数据打回来一次。

---

## 七、更正

| 之前（本轮的第一次审计）| 现在 |
| --- | --- |
| 「143 个网格缺 LOD 是问题」 | ❌ **它们一个都没放进关卡** |
| 「审计资产库能发现性能问题」 | ❌ **必须审**放置情况**才算数** |

---

## 八、还没做到

| 项 | 说明 |
| --- | --- |
| 那 99 个放置网格的 **LOD 质量** | 只知道「有多 LOD 或 Nanite」，没看 LOD 级别是否合理 |
| **HLOD 的实际配置** | 项目有没有 HLOD layer，没查 |
| 视距剔除 / streaming | 没查 |
| 屏幕尺寸阈值的合理性 | 没看具体数值 |

**→ 下一步值得查：**那 99 个放置网格分别有几个 LOD、屏幕阈值是多少。**

---

## 九、状态

```
Docs/UE5-LEARN-READ-LOD.md   1 篇（共 36 篇 learn 文档）
补读进度：16 / 57
主关卡 116 actor / 视口复位
```

---

## 十、下一篇

**继续补读（还剩 41 篇）。下一批：**
- `world-partition.md`（19.5 KB）—— 和 HLOD 直接相关
- `asset-management.md`（14.3 KB）
- `geometry-scripting.md`（10.4 KB）
