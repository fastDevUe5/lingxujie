# UE5 学习 · Lumen（第一块）

> **本块学的是 `Docs/UEManual/lumen-technical.md` 和 `lumen-performance.md` 两篇本地官方文档。**
>
> **每一节都标了：官方怎么说 → 引擎源码/本项目怎么验 → 结论。**
>
> **日期：2026-11-27 · UE 5.8.4 · 项目：灵虚界**

---

## 一、官方文档说了什么（原文要点）

`lumen-technical.md` 里可操作、可验证的结论：

| # | 官方结论 |
| --- | --- |
| 1 | Lumen 用**屏幕追踪（Screen Traces）先打**，打不到再回退到更可靠的方法 |
| 2 | 两种光追：**软件光追**（距离场）和**硬件光追**（三角形）；硬件质量高但贵 |
| 3 | **Surface Cache** 用 Cards 近似；默认每网格 12 张；`r.Lumen.Visualize.CardPlacement 1` |
| 4 | 软件光追**只支持静态网格 / ISM / HISM / 地形** |
| 5 | **植被**必须勾选 `Affect Distance Field Lighting` 才进 Lumen Scene |
| 6 | 墙**不能薄于 10 cm**，否则漏光 |
| 7 | **距离场分辨率按导入尺度分配**；导入很小再靠缩放放大的网格分辨率不够 |
| 8 | 提高分辨率两个旋钮：项目级 `Distance Field Voxel Density`、单网格 `Distance Field Resolution Scale` |
| 9 | `r.DistanceFields.LogAtlasStats 1` 输出距离场图集统计 |
| 10 | 软件光追的 Lumen Scene **默认覆盖 200 m**，可调到 800 m（后处理体积里设）|
| 11 | Far Field 默认 **10 km**，需要 World Partition 的 **HLOD1** |
| 12 | Lumen **不兼容前向着色**、**不支持 VR**、**不能和光照贴图静态光同时用** |

---

## 二、本项目实测：配置层

**跑 `r.<名字>` 读回，`Cmd:` 后面那行就是值和设置来源（✅ 实测）：**

```
r.DynamicGlobalIlluminationMethod   = "1"    LastSetBy: Console        → 1 = Lumen，开着
r.ReflectionMethod                  = "1"    LastSetBy: Console        → 1 = Lumen 反射
r.Lumen.HardwareRayTracing          = "0"    LastSetBy: ProjectSetting → 软件光追
r.GenerateMeshDistanceFields        = "1"    LastSetBy: ProjectSetting → 距离场已启用
r.DistanceFields.DefaultVoxelDensity = "0.2" LastSetBy: Constructor    → 默认值
r.LumenScene.SurfaceCache.MeshCardsMergeComponents = "1"  Constructor
```

**关键读数：**

| 项 | 值 | 含义 |
| --- | --- | --- |
| **GI 方式** | `1` = Lumen | 动态全局光照在用 Lumen |
| **反射方式** | `1` = Lumen | 反射也在用 Lumen |
| **硬件光追** | **`0`** | **本项目走软件光追（距离场）** |
| **体素密度** | **0.2** | 范围 0.05–0.4 的**中位**，是构造函数默认值 |

**⚠️ `r.LumenScene.ViewDistance` 命令**没有输出** —— 它**不是 CVar**，
是**后处理体积**里的 `Lumen Scene View Distance` 字段。想读它要读 PostProcessVolume。**

---

## 三、本项目实测：距离场图集

**`r.DistanceFields.LogAtlasStats 1` 的输出（✅ 实测，完整原文）：**

```
LogDistanceField: Mesh Distance Field Atlas 1024x1024x64 = 64.0Mb (256.0Mb target max),
                  with 25.0Mb free, 0.8Mb block allocator waste,
                  Indirection Table 2.0Mb, Indirection Texture 0.0Mb
LogDistanceField:    Bricks at Mip0: 3.1Mb,  8.0%
LogDistanceField:    Bricks at Mip1: 7.5Mb, 19.2%
LogDistanceField:    Bricks at Mip2: 27.6Mb, 70.7%
```

**怎么读这张表：**

| 字段 | 值 | 含义 |
| --- | --- | --- |
| 图集尺寸 | 1024×1024×64 | 立体的体素网格 |
| 占用 | **64 MB** | 实际用了多少 |
| 上限 | 256 MB | 引擎允许的上限 |
| 剩余 | **25 MB（39%）** | **还有余量，没爆** |
| 块分配器浪费 | 0.8 MB | 碎片，很小 |
| **Mip2 占 70.7%** | **七成体素在最低精度层** | **说明大部分是远处/大物体的粗表示** |

**→ 结论：距离场没爆图集，还有 39% 余量。Mip2 占七成是**正常现象** ——
远处物体的距离场用低精度是设计如此，不是问题。**

---

## 四、🔴 我原来的假设被推翻了

**学这篇文档之前我以为：**

> 「本项目 101 个 Nanite 网格很可能就是『导入时很小、靠缩放放大』，
> 所以距离场分辨率不够。」

**实测（`Tools/lumen_df_audit.py`）：**

```
actors with scale != 1: 0
largest uniform scale: 1.00 on 'MX_TERRAIN'
meshes under 100 cm natively that are enlarged on screen: 0
flagged: 0
```

**→ 本项目 **零个** actor 有非 1 缩放。最大缩放就是 1.00。
→ 官方文档第 7 条那个坑，**在本项目不存在**。**

**这是本轮最重要的一条更正：**
**我拿「文档里有个坑」直接推「本项目一定踩了」，没先量。**

**教训：文档说的坑是**可能发生**，不是**已经发生**。
先量，再判断。**

---

## 五、🎯 实操：关掉 Lumen GI，量出它贡献多少

### 5.1 方法

```
1. 相机固定在默认位 (8950, -6200, 3900) yaw 0 pitch -2
2. 截图 shot_gi_on.png
3. r.Lumen.DiffuseIndirect.Allow 0
4. 截图 shot_gi_off.png
5. 恢复 r.Lumen.DiffuseIndirect.Allow 1
6. 像素对比
```

**⚠️ `CaptureViewport` 的 `captureTransform` 是**必填参数**，不传会报
`input param "captureTransform" needs a default value`。**

### 5.2 结果（✅ 实测）

```
size: 1180x688 (811840 pixels)
pixels differing by more than 8: 307214 (37.84%)
mean absolute channel delta: 6.930
VERDICT: the two captures differ in a region, not everywhere
```

**→ 关掉 Lumen GI，**37.84% 的像素变了**。**

### 5.3 变化在哪（看图）

| 位置 | GI 开 | GI 关 |
| --- | --- | --- |
| **左侧建筑的侧墙** | **暖色、被照亮** | **暗灰、死黑** |
| 地面 | 更亮 | 更暗 |
| 阴影区 | 有补光 | 纯黑 |

**→ 左侧墙面从亮到暗，就是**反弹光**。这是 Lumen GI 最直观的证据。**

---

## 六、官方文档里本项目要留意的三条

| 官方结论 | 本项目情况 | 要不要处理 |
| --- | --- | --- |
| **软件光追只支持静态网格 / ISM / HISM / 地形** | 项目用**软件光追**（`HardwareRayTracing=0`）；**4 个骨骼网格（Boss）不在 Lumen Scene 里** | ⚠️ **Boss 不参与反弹光**，室内场景会显得贴合不好 |
| **墙不能薄于 10 cm** | 兰州建筑墙厚**未测** | 待量 |
| **植被要勾 `Affect Distance Field Lighting`** | 项目**没有植被**（`foliage` 未用） | 不适用 |

**→ 第一条是**真问题**：Boss 是骨骼网格，软件光追下它们**不会被间接光照到**，
所以站在阴影里的 Boss 会比周围环境暗。**

**要解决只有两条路：**
1. 开硬件光追（`HardwareRayTracing=1`，需要 RTX 2000+ 显卡，且要重启引擎）
2. 给 Boss 补一点自发光/环境光，骗过眼睛

**→ 这条要实测确认：把 Boss 放进阴影里，看它是不是比地面暗。**

---

## 七、还没验证的

| 项 | 为什么没验 |
| --- | --- |
| 硬件光追的效果 | 需要改项目设置 + **重启引擎** |
| Lumen Scene View Distance 200m 的效果 | 是后处理体积设置，得建一个 PPV |
| Surface Cache 可视化（粉色=没覆盖）| 是**视口 View Mode**，只能 UI 切 |
| Voxel Density 从 0.2 调到 0.4 的效果 | 工具提示说**改这个要重启编辑器** |
| 帧时间 | 需要 Insights，还没跑 |

---

## 八、这一块学到什么

**1. Lumen 的两种光追是**互斥选择**，不是叠加。本项目选了软件光追，代价是不支持骨骼网格。**

**2. 距离场图集有**上限**（256 MB），超了会出问题。本项目用 64 MB，还有 39% 余量。**

**3. Mip2 占七成是正常的。** 我一开始以为那是「精度不够」的信号，其实是远处物体的粗表示。

**4. 最重要的：文档里的坑不等于本项目踩了。** 我差点去修一个不存在的问题（缩放）。

**5. `CaptureViewport` 的 `captureTransform` 必填。** 不传会静默失败，只报一行错。

---

## 九、下一块

**按计划：继续 Lumen，验证「Boss 在软件光追下不参与间接光」这一条。**
**方法：把 Boss 移进阴影，对比它和地面的亮度。**
