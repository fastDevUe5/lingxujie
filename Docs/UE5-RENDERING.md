# UE5 渲染体系（引擎源码核实）

> **本文只写**验证过的**内容。渲染领域传闻最多，所以每个数字都标了出处。**

---

## 一、两套 Nanite 设置，别搞混

**引擎里有两个不同的结构，名字都叫 Nanite 设置：**

| 结构 | 位置 | 字段数 | 管什么 |
| --- | --- | --- | --- |
| **`FMeshNaniteSettings`** | `Engine/Classes/Engine/EngineTypes.h` | **28** | **这一个网格**要不要虚拟化 |
| **`FNaniteSettings`** | `Engine/Classes/GameFramework/WorldSettings.h` | **1** | 整个世界允不允许变异材质 |

**`FNaniteSettings` 只有一个字段：`bAllowMaskedMaterials`。**

**我们之前调的是第一个（`StaticMeshEditorSubsystem.set_nanite_settings`）。**

---

## 二、`FMeshNaniteSettings` 的 28 个字段（重点）

### 2.1 开关与质量

| 字段 | 默认 | 含义 |
| --- | --- | --- |
| **`bEnabled`** | — | **总开关** |
| `KeepPercentTriangles` | **1.0** | 保留多少比例的三角形 |
| `TrimRelativeError` | 0.0 | 裁剪相对误差 |
| `PositionPrecision` | **-1** | 位置精度，-1 = 自动 |
| `NormalPrecision` | -1 | 法线精度 |
| `TangentPrecision` | -1 | 切线精度 |
| `BoneWeightPrecision` | -1 | **骨骼权重精度**（做动画时相关） |
| `ShapePreservation` | 枚举 | 形状保留策略 |
| `MaxEdgeLengthFactor` | 0.0 | 最大边长因子 |

**精度字段默认都是 `-1`（自动）—— 说明引擎会按三角形密度自己决定。**

### 2.2 🔴 Fallback：这就是碰撞的来源

| 字段 | 默认 | 含义 |
| --- | --- | --- |
| **`GenerateFallback`** | 枚举 | **是否生成回退网格** |
| **`FallbackTarget`** | `Auto` | 回退网格的目标 |
| **`FallbackPercentTriangles`** | **1.0** | **回退网格保留多少三角形** |
| `FallbackRelativeError` | 1.0 | 回退相对误差 |

**这就是我们踩过的坑的机制解释：**

> **Nanite 网格本身不提供复杂碰撞，碰撞来自**Fallback 网格**（回退网格）。**
>
> **`FallbackPercentTriangles = 1.0` 意味着回退网格是**全精度**的 —— 所以默认配置下碰撞是好的。**
>
> **但如果 `GenerateFallback` 被关掉、或者回退网格没生成，就没有碰撞。**

**我们当初的修法是"关掉 Nanite"，其实更精确的做法是**检查回退网格是否生成**。**

**重查命令：**
```python
mesh = unreal.EditorAssetLibrary.load_asset("/Game/.../SM_XXX")
settings = mesh.get_editor_property("nanite_settings")
print(settings.get_editor_property("generate_fallback"))
print(settings.get_editor_property("fallback_percent_triangles"))
```

### 2.3 其他字段

`bExplicitTangents` / `bLerpUVs` / `bSeparable` / `bVoxelNDF` / `bVoxelOpacity` /
`NumRays`(64) / `VoxelLevel` / `RayBackUp` / `DisplacementUVChannel` / `DisplacementMaps` /
`NaniteAssemblyData`

**`NumRays = 64` —— 这是光追模式下每个像素的采样数。**

---

## 三、后处理：351 个字段

**`FPostProcessSettings` 在 `Engine/Classes/Engine/Scene.h`（161,309 字节），有 **351 个字段**。**

**挑常用的几组：**

| 组 | 字段例 |
| --- | --- |
| **曝光** | `AutoExposureMethod`、`AutoExposureBias`… |
| **Bloom** | `BloomMethod`、`BloomIntensity`、`BloomThreshold`、`BloomSizeScale`、`Bloom1Size`…`Bloom6Size` |
| **颜色分级（按阴影/中间调/高光分开）** | `ColorSaturationShadows`、`ColorContrastShadows`、`ColorGammaShadows`、`ColorGainShadows`、`ColorOffsetShadows`、`ColorCorrectionShadowsMax` |

**注意颜色分级是**六维**的（Saturation / Contrast / Gamma / Gain / Offset + 一个 Max），
而且**分阴影/中间调/高光三段**。所以调色是 3 段 × 5 参数。**

**这就是为什么"画面看起来不对"很难调 —— 参数空间是 351 维的。**

---

## 四、本项目当前的渲染配置（实测）

**用 `StaticMeshTools` 查的真实数据：**

```
SM_Lanzhou_Terrain:
  is_nanite_enabled   → false        ← 我们当初为了碰撞关掉的
  get_triangle_count  → 524,288      ← = 512 × 512 × 2，正好是地形格数
  get_vertex_count    → 263,174      ≈ 513 × 513
```

**`524,288 = 2^19` —— 512 格 × 512 格 × 每格 2 个三角形。这是地形网格的精确构造。**

### 4.1 🔴 更正确的碰撞做法（之前做错了）

**当初的修法是**关掉 Nanite**。现在知道有更精确的工具：**

| 工具 | 作用 |
| --- | --- |
| `StaticMeshTools.is_nanite_enabled(mesh)` | 查 Nanite 开关 |
| `StaticMeshTools.set_nanite_enabled(mesh, enabled)` | 开关 Nanite |
| **`StaticMeshTools.generate_convex_collisions(mesh)`** | **生成凸包碰撞** |
| `StaticMeshTools.remove_collisions(mesh)` | 清除碰撞 |

**`generate_convex_collisions` 的官方 docstring：**
> Generates convex hull collision shapes for a static mesh. Convex hulls provide accurate
> collision for physics

**所以正确做法应该是：保留 Nanite（享受虚拟几何），**另外生成碰撞**。
而不是为了碰撞把 Nanite 关掉。**

**⚠️ 但凸包对地形不合适** —— 凸包是"包住整个物体"，地形会变成一块大平板。
**地形应该用 `CTF_USE_COMPLEX_AS_SIMPLE`（我们已经在用），或者专门的 Landscape。**

### 4.2 资产路径格式（踩过）

**`StaticMeshTools` 的 `mesh` 参数要**完整对象路径**，不是资产路径：**

```
❌ /Game/Moxiang/SM_Lanzhou_Terrain
✅ /Game/Moxiang/SM_Lanzhou_Terrain.SM_Lanzhou_Terrain
```

**报错原文：**
```
Parameter error: /Game/Moxiang/SM_Lanzhou_Terrain is not a valid object path for property 'mesh'.
```

**规则：`/Game/<文件夹>/<资产名>.<对象名>`，两者通常相同。**

### 4.3 本项目渲染现状

| 项 | 现状 |
| --- | --- |
| 地表材质 | `M_Moxiang_Ground`，贴图 96 次平铺，无 UV 变化 |
| 建筑材质 | 96 个材质实例，每张贴图一个 |
| 光照 | 默认天光 |
| Nanite | **地形已关闭** |
| 后处理 | **未配置** |

**最明显的观感问题（已知）：**

| 问题 | 原因 | 该动哪个 |
| --- | --- | --- |
| 地面平铺网格太明显 | `tiles=96` 固定重复 | 材质 UV，加随机偏移 |
| 陡坡贴图拉伸 | 平面投影 | 用三平面（triplanar）映射 |
| 材质全是平涂 | 没有法线/AO | 加法线贴图 + 环境光遮蔽 |

**这三条都不是"引擎问题"，是我们自己的材质没做。**

---

## 五、还没学的

| 主题 | 状态 |
| --- | --- |
| Lumen（全局光照） | 完全没碰 |
| 虚拟阴影贴图（Virtual Shadow Maps） | 没碰 |
| 材质表达式全集 | 只知道 4 种节点（现在知道 `MaterialTools` 能查引脚了） |
| 后处理卷（Post Process Volume）怎么用 | 没碰 |
| 世界分区（World Partition） | 没碰 |

**下一轮渲染相关应该从**材质**入手 —— 因为那是当前观感最关键的一块，且已有 22 个现成工具。**

---

## 六、重查命令

```powershell
python Tools\map_nanite_settings.py    # 两套 Nanite 设置的全部字段
python Tools\map_rendering.py           # 后处理 / ShowFlags
```

---

## 十、更正：Lumen 一直在运行（2026-11-26）

**本文原先写「Lumen 零」。这是错的。**

**`Config/DefaultEngine.ini` 实测：**
```ini
r.DynamicGlobalIlluminationMethod=1     ; = Lumen GI
r.ReflectionMethod=1                    ; = Lumen 反射
r.Shadow.Virtual.Enable=1               ; 虚拟阴影贴图
r.GenerateMeshDistanceFields=True       ; Lumen 软件光追的前提
r.AllowStaticLighting=False             ; 全动态光照
r.AntiAliasingMethod=4                  ; = TSR
```

**`EDynamicGlobalIlluminationMethod` 的枚举（`EngineTypes.h` 源码）：**
```
0 = None
1 = Lumen        <- 本项目
2 = ScreenSpace（已废弃）
3 = Plugin
```

**所以场景光照看起来不错，不是"默认天光凑合"，而是 Lumen 在算间接光。**

**详细原理见 `Docs/UE5-LUMEN.md`。**
