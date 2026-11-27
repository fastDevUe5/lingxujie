# UE5 学习 · 补读（一）：Nanite 技术细节

> **这一篇开始补读剩下的 57 篇。先读最贴项目的 Nanite —— 项目里有 101 个 Nanite 网格。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档结构（17 节，26.5 KB）

```
Nanite Fallback Mesh and Precision Settings
Vertex Precision
Trimming Mesh Data
Fallback Mesh
Fallback Mesh Visualization
Using Custom Fallback Mesh LODs
Data Size
General Advice on Data Size
Visualization Modes
Nanite Culling
Nanite Ray Tracing Quality Scaling
Console Variables and Commands
Nanite Fallback Rendering Modes
Nanite Stats Command
Resizing the Nanite Streaming Pool Size
Setting Maximum Clusters in a Single Pass
```

**🔴 重心不是「Nanite 多快」，而是 **Fallback Mesh** —— 五节里有三节在讲它。**

---

## 二、🎯 Fallback Mesh 才是关键（文档反复强调）

**文档原话（意译）：**
> **「Many parts of Unreal Engine need access to the vertex buffer provided by traditional
> （LODs）...」**
> **Fallback mesh 被引擎的多个系统使用**（碰撞、光追、LOD、非 Nanite 平台）。

**→ 每个 Nanite 网格都**必须**有一个 fallback mesh。
→ Nanite 走 cluster 光栅化，但**其它系统仍然要传统顶点缓冲**。**

**→ 这解释了项目里那 101 个 Nanite 网格为什么「材质槽是 WorldGridMaterial」，**
**可能 Nanite 侧和 fallback 侧走的是不同的材质路径**（详见 MAT-03 的材质解析顺序）。

### 2.1 相关参数

| 参数 | 作用 |
| --- | --- |
| **Fallback Triangle Percent** | fallback 用多少比例的源三角形 |
| **Keep Triangle Percent** | Nanite 侧保留多少（默认 100%）|
| **Trim Relative Error** | 相对误差低于此值的三角形被删 |
| **Preserve Area** | 简化后**重新分配丢失面积** —— **对树叶特别有用** |
| **Source Import Filename** | 高模路径，替代 LOD0 |

**→ `Preserve Area` 是给**植被**准备的：叶子简化后会变成分离的三角形/四边形，面积会丢。**

---

## 三、🎯 Cluster 缓冲：文档给了精确数字

**文档原文：**
> **「The memory cost of a candidate cluster is currently 12 bytes and a visible cluster is 16 bytes.」**
> **「There is no mechanism for dynamically resizing either of these buffers, or automatically
> scaling down quality on overflow」**
> **「typically manifesting as missing or blinking geometry」**

| 事实 | 值 |
| --- | --- |
| 候选 cluster | **12 字节/个** |
| 可见 cluster | **16 字节/个** |
| 溢出后果 | **「missing or blinking geometry」** |
| 能否运行时改 | **❌ 只能写 .ini** |

---

## 四、✅ 源码核实（`NaniteShared.cpp:46-57`）

```cpp
int32 GNaniteMaxCandidateClusters = 16 * 1048576;   // 16,777,216
FAutoConsoleVariableRef CVarNaniteMaxCandidateClusters(TEXT("r.Nanite.MaxCandidateClusters"), ...);

int32 GNaniteMaxVisibleClusters   = 4 * 1048576;    // 4,194,304
FAutoConsoleVariableRef CVarNaniteMaxVisibleClusters(TEXT("r.Nanite.MaxVisibleClusters"), ...);
```

**→ 默认值确认：**候选 16M，可见 4M**。**

### 4.1 按文档的字节数算内存

```
候选: 16,777,216 × 12 B = 201,326,592 B = 192 MB
可见:  4,194,304 × 16 B =  67,108,864 B =  64 MB
合计: 256 MB
```

**→ 默认就占 **256 MB** 的 cluster 缓冲。**

---

## 五、✅ 实测（本项目的活值）

```
r.Nanite                          = "1"          LastSetBy: Constructor
r.Nanite.MaxCandidateClusters     = "16777216"   LastSetBy: Constructor
r.Nanite.MaxVisibleClusters       = "4194304"    LastSetBy: Constructor
r.Nanite.Streaming.StreamingPoolSize = "512"     LastSetBy: Constructor
r.Nanite.ProjectEnabled           = "1"          LastSetBy: ProjectSetting
```

**→ 全部是**默认值**，项目没改过。**
**→ 流式池 512（MB），比 cluster 缓冲小一半。（两个是**不同的**东西：一个是 cluster 中间缓冲，
一个是 Nanite 网格数据的流式池。）**

---

## 六、🎯 引擎会**自动告警** —— 而且项目日志里没有

**`NaniteFeedback.cpp:45-54`：**
```cpp
if (CandidateClusterState.Update(PeakCandidateClusters, MaxCandidateClusters))
    UE_LOG(..., "Increase r.Nanite.MaxCandidateClusters to prevent potential visual artifacts.",
           CandidateClusterState.HighWaterMark, MaxCandidateClusters);

if (VisibleClusterState.Update(PeakVisibleClusters, MaxVisibleClusters))
    UE_LOG(..., "Increase r.Nanite.MaxVisibleClusters to prevent potential visual artifacts.",
           VisibleClusterState.HighWaterMark, MaxVisibleClusters);
```

**→ 峰值超过上限时，引擎**自己打印**该调哪个 CVar。**

**✅ 搜索项目日志：**
```
Select-String -Pattern 'Increase r\.Nanite\.Max'
→ 没有找到溢出告警
```

**→ **这个项目从来没撞过 cluster 上限** —— 默认的 16M/4M 够用。**

**→ 意义：如果将来出现「几何闪烁/缺失」，先查这条告警；
没有告警就**不是** cluster 溢出问题，该去查流式或材质。**

---

## 七、其他可操作的命令

| 命令/CVar | 作用 |
| --- | --- |
| **`r.Nanite 0`** | 全局关掉 Nanite，**用来模拟不支持 Nanite 的平台** |
| **`NaniteStats`** | 视口右上角叠层，显示剔除统计 |
| `NaniteStats List` | 列出所有视图 |
| `NaniteStats VirtualShadowMaps` | 切到 VSM 视图（还有 `ShadowAtlas` / `CubemapShadows`）|
| **`r.Nanite.Streaming.StreamingPoolSize`** | 流式池大小，太小 → **cache thrashing，流式永不收敛** |
| `Show > Nanite > Streaming Geometry` | 可视化流式数据；关掉时只渲染常驻内存的部分 |

**⚠️ `NaniteStats` 和 `stat gpu` 一样是**屏幕叠层**，抓不到日志。**
**→ 但它能用 `CaptureViewport` + `bShowUI` 试一下，或者靠人眼看不。**
（之前测过 stat 面板抓不到，NaniteStats 大概率同样。）

---

## 八、这一篇学到什么

**1. 🔴 Nanite 的核心配套是 **Fallback Mesh**，不是「快」。**
引擎的碰撞/光追/LOD 用的都是 fallback 的传统顶点缓冲。

**2. 🎯 文档给了**精确的字节数**：候选 12 B、可见 16 B。**
→ 能算出默认值占 **256 MB**。

**3. 🔴 「几何闪烁/缺失」的直接原因是 cluster 缓冲太小，而引擎会**主动告警**。**
→ **排障第一步应该是搜这条告警，不是凭猜。**

**4. ✅ 本项目从没撞过上限** —— 默认值够用，这条可以排除。

**5. `r.Nanite 0` 是模拟「平台不支持 Nanite」的正规手段。**

**6. 两个容易混的东西：**
- **cluster 缓冲**（256 MB，固定尺寸，不能运行时改）
- **流式池**（512 MB，可调）

---

## 九、还没做到

| 项 | 说明 |
| --- | --- |
| 实际跑 `NaniteStats` 看数字 | 它是屏幕叠层，读不到日志 |
| 对比 `r.Nanite 0/1` 的画面 | 可以做，用像素对比（和 Lumen 那套一样）|
| Fallback mesh 的实际用途验证 | 例如碰撞是否走 fallback |

---

## 十、下一篇

**`nanite.md`（15 KB，入门篇）** —— 看它和 technical 的分工，以及有没有可验证的额外断言。

**⚠️ 编辑器状态：主关卡 116 actor、视口复位。**
