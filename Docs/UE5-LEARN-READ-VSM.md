# UE5 学习 · 补读（四）：虚拟阴影贴图 —— 五种溢出，各有各的解法

> **上一篇的实验撞上了 VSM 溢出警告。这一篇把它查清楚了：**
> **VSM 有**五种**溢出，我遇到的是最轻的一种（只影响性能，不出画面瑕疵）。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档结构（43.9 KB，33 节）

**核心章节：**
```
Goals of Virtual Shadow Maps
Enabling Virtual Shadow Maps
Soft Shadows with Shadow Map Ray Tracing（SMRT）
Controlling Penumbra Shadow Quality
Clipmaps for Directional Light
Local Lights（Spot 用单个 16k VSM + mip 链）
Caching / Managing Cache Invalidations
Deformation and Foliage / Disabling Mesh Deformation at a Distance
Separate Static Caching
Coarse Pages
Visualization / GPU Profiling and Optimization
Shadow Depths / Shadow Projection
**Improving Non-Nanite Performance**
Issues and Limitations：Object Bounds / Multiple Lights / Low Poly Geometry
**Overflow of Physical Page Pool**
Unsupported Geometry / Map Check Warnings
```

---

## 二、🎯 引擎里其实有**五种**溢出（源码核实）

**`VirtualShadowMapCacheManager.cpp:1076-1088`：**
```cpp
case VSM_STAT_OVERFLOW_FLAG_MARKING_JOB_QUEUE:
    "[VSM] Non-Nanite Marking Job Queue overflow. Performance may be affected.
     This occurs when many non-nanite meshes cover a large area of the shadow map."

case VSM_STAT_OVERFLOW_FLAG_OPP_MAX_LIGHTS:
    "[VSM] One Pass Projection max lights overflow. If you see shadow artifacts,
     decrease the amount of local lights per pixel,
     or increase r.Shadow.Virtual.OnePassProjection.MaxLightsPerPixel."

case VSM_STAT_OVERFLOW_FLAG_PAGE_POOL:
    "[VSM] Page Pool overflow detected, this will produce visual artifacts (missing shadow).
     Increase the page pool limit or reduce resolution bias to avoid."

case VSM_STAT_OVERFLOW_FLAG_VISIBLE_INSTANCES:
    "[VSM] Non-Nanite visible instances buffer overflow detected,
     this will produce visual artifacts (missing shadow)."

default: "[VSM] Unknown overflow"
```

### 2.1 🎯 排障速查表

| 溢出类型 | 后果 | 解法 |
| --- | --- | --- |
| **MARKING_JOB_QUEUE** | ⚠️ **只有性能，无画面瑕疵** | 减少非 Nanite 网格覆盖面积 |
| OPP_MAX_LIGHTS | 阴影瑕疵 | `r.Shadow.Virtual.OnePassProjection.MaxLightsPerPixel` |
| **PAGE_POOL** | ❌ **阴影缺失** | **增大页池 / 降低分辨率偏差** |
| **VISIBLE_INSTANCES** | ❌ **阴影缺失** | 减少非 Nanite 可见实例 |
| Unknown | — | — |

**🔴 关键区分：名字里带「**Performance may be affected**」的只有 MARKING_JOB_QUEUE。**
**其它三种都会真的**缺阴影**。**

**→ 我上一篇撞到的正是 MARKING_JOB_QUEUE —— 最轻的一种。**

---

## 三、🎯 文档的「Improving Non-Nanite Performance」是全篇最实用的一节

**原文要点（逐条）：**

| # | 建议 |
| --- | --- |
| 1 | **「Enable Nanite on as much geometry as possible」** |
| 2 | **「Nanite geometry renders far more efficiently into Virtual Shadow Maps and should be preferred in every applicable case, regardless of polygon counts」** |
| 3 | **「Nanite geometry can occlude non-Nanite geometry and avoid spurious cache invalidations. Thus, the only non-Nanite objects should be those that are not supported by Nanite itself.」** |
| 4 | **「Non-Nanite objects should have full Mesh LOD hierarchies setup」** |
| 5 | **「It is important that non-Nanite meshes have LODs setup or else they become extremely expensive to render into small pages」** |
| 6 | 远处关掉网格变形（WPO/PDO/tessellation） |
| 7 | **`r.Shadow.RadiusThreshold`** —— 非 Nanite 物体的 CPU 剔除 |
| 8 | 远处用 **Distance Field Shadows** 接管非 Nanite |
| 9 | **禁用 Coarse Pages 里的非 Nanite 几何**（常有大收益） |

**→ 第 3 条是核心思想：**Nanite 能**遮挡**非 Nanite 并避免无谓的缓存失效。
→ **非 Nanite 应该只留给「Nanite 本身不支持的物体」。**

**→ 这正好解释了关掉 Nanite 后为什么爆队列：
101 个网格全变成非 Nanite，覆盖大片阴影贴图。**

---

## 四、页池溢出（另一件独立的事）

**文档原文：**
> **「With Virtual Shadow Maps, all of the shadow data in the scene for all lights is
> stored in a single large texture pool.」**
> **「The page pool size can be adjusted using **`r.Shadow.Virtual.MaxPhysicalPages`**」**
> **「Enabling stats with **`r.Shadow.Virtual.Stats 1`** will display statistics about the current page pool use」**
> **「If this occurs, increase the size of the page pool or decrease the shadow resolution
> or number of virtual shadow map casting lights」**

**⚠️ 注意：`r.Shadow.Virtual.Stats 1` 是**屏幕统计**，和 `stat gpu` 一样读不到日志。**

---

## 五、✅ 本项目的活值

```
r.Shadow.Virtual.Enable                            = 1        Console
r.Shadow.Virtual.MaxPhysicalPages                  = 4096     Scalability
r.Shadow.Virtual.AllowScreenOverflowMessages       = 1        Constructor
r.Shadow.Virtual.AccumulateStats                   = 0        Constructor
r.Shadow.Virtual.Cache                             = 1        Constructor
r.Shadow.Virtual.Cache.InvalidateUseHZB            = 1        Constructor
r.Shadow.Virtual.Cache.MaxPageAgeSinceLastRequest  = 1000     Constructor
r.Shadow.Virtual.Cache.FramesStaticThreshold       = 100      Constructor
r.Shadow.Virtual.DynamicRes.MaxPagePoolLoadFactor  = 0.85     Constructor
r.Shadow.Virtual.DynamicRes.MaxResolutionLodBias   = 2        Constructor
r.Shadow.RadiusThreshold                           = 0.01     Scalability
```

**→ VSM 开着，页池 4096 页，动态分辨率负载因子 0.85，最大 LOD 偏差 2。**
**→ 项目**从没调过**这些（全是 Constructor / Scalability 默认）。**

---

## 六、`r.Shadow.Virtual.AllowScreenOverflowMessages`

**源码（`CacheManager.cpp:205-209`）：**
```cpp
int32 GVSMAllowScreenOverflowMessages = 1;
FAutoConsoleVariableRef CVarVSMAllowScreenOverflowMessages(
    TEXT("r.Shadow.Virtual.AllowScreenOverflowMessages"),
    GVSMAllowScreenOverflowMessages,
    TEXT("Can be used to disable on-screen VSM-related overflow messages.
          Even with the messages disabled, overflows will still be logged..."));
```

**→ **关掉屏幕提示，日志里仍然会记**。**
**→ 所以「日志里有这条警告」是可靠信号，不会被这个 CVar 掩盖。**

---

## 七、这一篇学到什么

**1. 🎯 VSM 有**五种**溢出，症状和处理都不同。**
**→ 排障第一步是**看清是哪一种**，不是笼统地「增大页池」。**

**2. 🔴 「Performance may be affected」是**唯一**只影响性能的那种。**
其它三种会真的缺阴影。**看到这句可以放心，看到「missing shadow」要立刻处理。**

**3. 🎯 VSM 的核心优化思想：**尽量让几何是 Nanite**。**
文档说得非常直接：「regardless of polygon counts」。
**→ 因为 Nanite 走高效的 VSM 路径，还能**遮挡**非 Nanite 避免缓存失效。**

**4. 🔴 非 Nanite 网格**必须有完整 LOD**，否则渲染到小页里代价极高。**

**5. 项目所有 VSM 参数都是默认值，没调过。**

---

## 八、更正

| 之前 | 现在 |
| --- | --- |
| 「VSM 溢出了，可能要调页池」（上一篇）| ⚠️ **我遇到的是标记队列溢出，调页池没用** |
| 「VSM 溢出 = 阴影缺失」 | ❌ **只有 PAGE_POOL / VISIBLE_INSTANCES 会缺阴影** |

---

## 九、还没做到

| 项 | 说明 |
| --- | --- |
| 实际触发一次 PAGE_POOL 溢出 | 需要极端场景 |
| `r.Shadow.Virtual.Stats 1` 看页池用量 | 屏幕统计，读不到 |
| 用 `r.Shadow.RadiusThreshold` 调优 | 未测 |

---

## 十、状态

```
Docs/UE5-LEARN-READ-VSM.md   1 篇（共 27 篇 learn 文档）
补读进度：4 / 57
编辑器：主关卡 116 actor / 视口复位
```

---

## 十一、下一篇

**继续补读。`temporal-super-resolution.md`（85 KB，最大的文档）或
`post-process-materials.md`（18.6 KB）或 `sky-atmosphere.md`（27.6 KB）。**

**→ 选 `sky-atmosphere.md` —— 我的练习场景里就有一个 SkyAtmosphere，可以边读边调。**
