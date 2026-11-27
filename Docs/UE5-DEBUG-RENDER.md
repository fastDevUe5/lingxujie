# UE5 调试 · 六：渲染调试（缓冲可视化 / vis / CVar）

> **本篇全部结论来自本机源码 + 在灵虚界项目上的实测（含像素级 A/B 对比）。**
>
> **最关键的一条对比：**
> **`stat` 面板抓不到（0% 像素差），但 `vis` 能抓到（16.7% 像素差）。
> 因为前者画在 Canvas 覆盖层，后者改的是场景渲染。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、缓冲可视化：24 种，配置驱动

**源码：`Runtime/Engine/Private/BufferVisualizationData.cpp` 第 29-79 行**
```cpp
const FConfigSection* MaterialSection =
    GConfig->GetSection(TEXT("Engine.BufferVisualizationMaterials"), false, GEngineIni);
// 每条读 Material=（后处理材质）、Display=（CVar 开关）、Name=（显示名）
// Material->AddToRoot();   ← 防止被 GC
```

**→ 可选哪些可视化，完全由 ini 决定，不是硬编码。**

### 1.1 全部 24 种（`BaseEngine.ini` 的 `[Engine.BufferVisualizationMaterials]`）

| 键 | 含义 | ApplyAutoExposure |
| --- | --- | --- |
| `BaseColor` | 基础色 | |
| `FinalImage` | 最终图像 | ✅ |
| `ShadingModel` | 着色模型 | |
| `MaterialAO` | 材质 AO | |
| `AmbientOcclusion` | 屏幕空间 AO | |
| `Metallic` / `Roughness` / `Specular` | 金属度 / 粗糙度 / 高光 | |
| `Anisotropy` | 各向异性 | |
| `Opacity` | 不透明度 | |
| `SubsurfaceColor` | 次表面色 | |
| `WorldNormal` / `WorldTangent` | 世界法线 / 切线 | |
| `SceneColor` | 场景色 | ✅ |
| `SceneDepth` / `SceneDepthWorldUnits` | 深度 / 世界单位深度 | |
| `CustomDepth` / `CustomDepthWorldUnits` | 自定义深度 | |
| `CustomStencil` | 自定义模板 | |
| `SeparateTranslucencyRGB` / `A` | 分离半透明 RGB / Alpha | ✅（RGB）|
| `Velocity` | 速度缓冲（运动模糊/TSR 用）| |
| `PreTonemapHDRColor` / `PostTonemapHDRColor` | 色调映射前/后 | ✅ |

**`ApplyAutoExposure=✅` 很重要：这几项应用自动曝光，所以亮度是"归一化"过的，
不能直接当 HDR 值读。**

### 1.2 🔴 切换到哪一个是**UI 专属的，没有控制台命令**

**源码：`EditorViewportClient.cpp` 第 3280 行**
```cpp
void FEditorViewportClient::ChangeBufferVisualizationMode(FName InName) {
    SetViewMode(VMI_VisualizeBuffer);
    CurrentBufferVisualizationMode = InName;
}
```

**→ 状态是 `FEditorViewportClient::CurrentBufferVisualizationMode`（一个 `FName`），
只在编辑器视口客户端上，**不暴露给 Python，也没有控制台命令**。**

**实测搜遍 `Editor/` 也没有 `viewmode` 命令注册。**

**→ **只能通过视口菜单切换**（视口左上角 View Mode → Buffer Visualization）。

**⚠️ 这是本轮最重要的可自动化性结论之一。**

---

## 二、`vis`（VisualizeTexture）：**这个是控制台命令**

**源码：`Runtime/Renderer/Private/Renderer.cpp` 第 823-828 行**
```cpp
if (FParse::Command(&Cmd, TEXT("VisualizeTexture")) || FParse::Command(&Cmd, TEXT("Vis"))) {
    VisualizeTextureExec(Cmd, Ar);
    return true;
}
```
**`VisualizeTextureExec` 先 `FlushRenderingCommands()` 再 `GVisualizeTexture.ParseCommands(Cmd, Ar)`。**

### 2.1 权威语法：直接问它

**实测 `vis help` 的输出：**
```
VisualizeTexture/Vis <RDGResourceNameWildcard>:
VisualizeTexture/Vis <RDGResourceName>[@<Version>] [<Mode>] [PIP/UV0/UV1/UV2] [BMP] [FRAC/SAT] [FULL]:
VisualizeTexture/Vis 0
VisualizeTexture/Vis pool [BYNAME/BYSIZE]:
VisualizeTexture/Vis view=[ID/NAME]
```

| 命令 | 作用 |
| --- | --- |
| `vis <名字通配符>` | 全屏显示匹配的 RDG 资源 |
| `vis <名字>@<版本>` | 显示特定版本 |
| **`vis 0`** | **关闭** |
| **`vis pool`** | **列出渲染目标池里的所有资源（含尺寸/格式/占用）** |
| `vis pool BYSIZE` / `BYNAME` | 排序 |
| `vis view=?` | 列出可用的 view |
| `vis help` | 打印用法 |

**源码 `VisualizeTexture.cpp` 第 17 行起的分支：**
```cpp
if (FirstParameter.IsEmpty())                  → NOP
else if (FChar::IsDigit(**FirstParameter))     → DisableVisualization
else if (FirstParameter == "help")             → DisplayHelp
else if (FirstParameter == "pool")             → DisplayPoolResourceList
else if (FirstParameter.StartsWith("view="))   → SetViewId / DisplayViewList
```

### 2.2 `vis pool` 是本项目最有用的渲染诊断命令

**实测输出（本项目，编辑器空闲时）：**
```
16 = (2D 592x344 PF_FloatRGBA RT)         VolumetricRenderTarget.ReconstructDepth  1792 KB
22 = (Cube 128 PF_FloatR11G11B10 RT UAV)  SkyLight.ConvolvedSkyRenderTarget0       576 KB
23 = (Cube 128 PF_FloatR11G11B10 RT UAV)  SkyRenderTarget                          576 KB
24 = (Cube 128 PF_FloatR11G11B10 RT UAV)  SkyLight.ConvolvedSkyRenderTarget1       576 KB
64 = (2D 592x344 PF_FloatRGBA RT)         VolumetricRenderTarget.Reconstruct        1792 KB
73 = (2D 296x172 PF_FloatRGBA RT UAV)     VolumetricRenderTarget.SecondaryTracing    448 KB
...
```

**能看出：**
- **有体积渲染目标** → 体积雾/体积云在跑
- **SkyLight 卷积立方图 3 个，各 576 KB** → 天光在跑
- **分辨率是 592×344** —— 比视口窗口小，说明**有屏幕百分比缩放**（Lumen/TSR 的典型配置）

### 2.3 🔴 `vis pool` 和 `obj list` 量的**不是同一样东西**

| 命令 | 量的是什么 | 生命周期 |
| --- | --- | --- |
| `obj list` | **UObject 资产**（Texture2D / StaticMesh …）| 持久，磁盘来的 |
| **`vis pool`** | **运行时渲染目标（RDG 池）** | **每帧可能复用，不是资产** |

**上一轮 `memreport` 说 `TextureCube` 3 个占 16.5 MB —— 那是**资产**。
`vis pool` 里的 `SkyRenderTarget 576 KB` 是**运行时立方图**。
**两者不能相加，也不是同一个东西。**

**⚠️ 这个区分很容易搞混，但搞混就会得出错误的内存结论。**

---

## 三、🔴 决定性实验：渲染改动**能**被截图抓到

**上一轮证明 `stat` 面板抓不到（两张截图完全一致）。这一轮做同样的 A/B 测试 `vis`。**

### 3.1 实验步骤

1. `vis SkyRenderTarget` → 截图 `shot_vis.png`
2. `vis 0`（关闭）→ 截图 `shot_vis_off.png`
3. 用 `Tools/diff_captures.py` 做像素级对比

### 3.2 结果

```
size: 1180x688 (811840 pixels)
pixels differing by more than 8: 135611 (16.70%)
mean absolute channel delta:   3.386
bounding box of any change:    (0, 0, 1180, 688)
VERDICT: the two captures differ in a region, not everywhere
```

### 3.3 结论对比表

| 调试方式 | 改的是什么 | `CaptureViewport` 能抓到吗 | 实测证据 |
| --- | --- | --- | --- |
| `stat unit` 面板 | Canvas 覆盖层 | ❌ **不能** | 0% 像素差（两张图完全一致）|
| **`vis <资源>`** | **场景渲染** | ✅ **能** | **16.7% 像素差，均值 3.386** |

**→ 规则：**
> **改**渲染状态**的调试手段能被截图，画**覆盖层**的不能。**
>
> **所以：`vis`、缓冲可视化、ShowFlag 可以自动化验证；
> `stat`、`stat unit`、调试文字不能。**

**这条规则直接决定了以后验证渲染改动的做法。**

---

## 四、渲染排查清单

### 4.1 「画面不对，是哪个环节」

| 现象 | 先看什么 |
| --- | --- |
| 颜色全错 | `BaseColor` 可视化 → 贴图/材质输入 |
| 光照不自然 | `SceneColor` + `WorldNormal` |
| 表面发黑 | `WorldNormal`（法线翻转）+ `AmbientOcclusion` |
| 发光过强/过弱 | `PreTonemapHDRColor` / `PostTonemapHDRColor` |
| 有闪烁/拖影 | `Velocity`（TSR 用了错误的运动矢量）|
| 遮挡不对 | `SceneDepth` / `CustomDepth` |

**⚠️ `ApplyAutoExposure` 的几项（`SceneColor` / `FinalImage` / `PreTonemapHDRColor` /
`PostTonemapHDRColor` / `SeparateTranslucencyRGB`）亮度是归一化过的，
不能拿来判断绝对亮度。**

### 4.2 「渲染目标池爆了」

```
vis pool BYSIZE
```
**→ 按大小排序看池里谁最大。**
**→ `r.RenderTargetPoolMin` 是池的最小值（本项目实测 **400**，`LastSetBy: Scalability`）。**

### 4.3 「某个 pass 的输出长什么样」

```
vis <RDG 资源名的一部分>
```
**→ 通配符匹配，全屏显示。`vis 0` 关闭。**

**⚠️ 名字来自 `vis pool` 的输出，或者 RDG 的 pass 名。
拼错了不会报错，只会什么都不显示 —— 所以**先 `vis pool` 确认名字存在**。**

---

## 五、待做

| 事项 | 为什么 |
| --- | --- |
| 用 `vis` 逐个看 24 种缓冲，记录每种能看出什么 | 还没系统做过 |
| 验证 `r.BufferVisualizationDumpFrames=1` 是否能自动导出 | 源码里有这个 CVar（`BufferVisualizationData.cpp` 21-27 行）|
| 确认屏幕百分比（592×344 说明有缩放）| 影响性能判断 |
| GPU 抓帧（RenderDoc/PIX）| 本机未装，是硬限制 |

**⚠️ 按用户要求本轮**只读不改**。**

---

## 六、本篇依据的源码位置

| 事实 | 文件 | 行 |
| --- | --- | --- |
| 缓冲可视化读 ini 的 `[Engine.BufferVisualizationMaterials]` | `BufferVisualizationData.cpp` | 38 |
| `Material->AddToRoot()` 防 GC | 同上 | 70 |
| `r.BufferVisualizationDumpFrames` CVar | 同上 | 21-27 |
| 切换靠 `CurrentBufferVisualizationMode`（FName）| `EditorViewportClient.cpp` | 3280 |
| `vis` / `VisualizeTexture` 命令入口 | `Renderer.cpp` | 823-828 |
| `vis` 的参数分支（help/pool/view=/数字）| `VisualizeTexture.cpp` | 17-60 |
| `VMI_VisualizeBuffer` 的名字 | `ShowFlags.cpp` | 1007 |
