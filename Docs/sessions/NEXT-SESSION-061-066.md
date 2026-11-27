# NEXT-SESSION 归档 · 第 61–66 节

> 从 `Docs/NEXT-SESSION.md` 分出来的历史（2026-11-27）。**当前状态看主文件。**

## 61. 调试系列第 4 轮：**内存 — 环数不等于泄漏**（2026-11-26 46:00）

### 一、`memreport` 的机制：延迟到帧末，先强制 GC

**源码 `UnrealEngine.cpp` 8120-8126：**
```cpp
// This will defer the report to the end of the frame so we can force a GC and get a real report
// with no gcable objects
GEngine->DeferredCommands.Add(FString::Printf(TEXT("MemReportDeferred %s"), Cmd ));
```

**→ 敲 `memreport` 不会立刻输出，它在帧末跑，**报告写进文件**。**

**落盘路径（实测）：**
```
Saved/Profiling/MemReports/LingXuJie-WindowsEditor-11.26-20.54.27/
    Pid4544_LingXuJie-WindowsEditor-26-20.54.27.memreport   ← 468.5 KB
```

**默认跑 **34 条命令**（`BaseEngine.ini` 2371 起），可用 `[MemReport<Profile>Commands]` 自定义。**

### 二、🔴 `obj cycles` 找到 29 个环内对象 —— 但**一个都不是项目的**

**实测输出：**
```
66998 total objects, 126353 total edges.
Non-permanent: 12333 objects, 8616 edges, 14 strongly connected components,
               29 objects are included in cycles.
```

**逐个看环的成员，只有 4 种类型：**
```
Level / ParticleEventManager / World / WorldSettings
```
**全是 `/Engine/Transient.World_N`，`/Game/` 出现 **0 次**。**

**环结构（引擎固有）：**
```
ParticleEventManager → WorldSettings      [Actor:Owner]
WorldSettings → ParticleEventManager      [Actor:Children]

Level → World                             [Level:OwningWorld]
World → Level                             [World:PersistentLevel / LevelCollection:*]
```

**→ World 不是靠 GC 回收的，是靠 `UWorld::Destroy()` 显式销毁。
这些环**设计如此**，不是泄漏。**

### 三、本条是本轮最重要的教训

> **`obj cycles` 报「29 个对象在环里」不等于「29 个泄漏」。必须看**环里是谁**。**
>
> **判断方法：搜输出里的 `/Game/`。没有 = 项目零泄漏。**

**这和本系列反复出现的「数字是真的但量错了东西」是同一类。**

### 四、本项目实测内存

```
Time Since Boot: 3733.60 Seconds          （62 分钟）
Process Physical Memory: 4554.05 MB used, 4648.82 MB peak
Process Virtual Memory:  8406.94 MB used
AssetRegistry memory usage = 140.97 MB
Nametable memory usage = 17.76 MB
```

**按类的资源占用：**

| 类 | 数量 | 资源内存 |
| --- | --- | --- |
| Texture2D | 251 | 43.1 MB |
| **TextureCube** | **3** | **16.5 MB** |
| Material | 152 | 15.0 MB |
| StaticMesh | 136 | 10.6 MB |
| **VolumeTexture** | **7** | **10.5 MB** |
| FontFace | 7 | 4.8 MB |

### 五、🔴 反直觉：10 张贴图占 63%

**3 张 cubemap (16.5MB) + 7 张 volume (10.5MB) = 27 MB，
而 251 张 Texture2D 才 43 MB。**

**但逐个列过：这 10 个**全是 `/Engine/`** —— 没有任何一张是 `/Game/`。**
```
/Engine/EngineResources/DefaultTextureCube
/Engine/MapTemplates/Sky/DaylightAmbientCubemap
/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128
/Engine/EngineMaterials/Hair/Hair_DualScattering
...
```

**→ 本项目内存大头是**引擎编辑器开销**，不是项目内容。**
**→ 要评估项目真实占用，必须量**打包版**。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-MEMORY.md`** | memreport 机制 + obj cycles + obj refs + 实测数据 |
| `Tools/practice_memory_commands.py` | 跑 obj cycles / memreport |
| `Tools/list_expensive_textures.py` | 列贵的 cube/volume 贴图 |

**证据：`Saved/Profiling/MemReports/` 里那份 468.5 KB 报告。**

### 七、这轮学到的排查套路

**「内存一直在涨」的六步：**
1. `memreport -full` 记基线
2. 做可疑操作 N 次
3. 再 `memreport -full`
4. 对比两份，看哪一类 **Count 涨了** → 对象泄漏
5. 看哪一类 **Count 不变但 NumKB 涨** → 同一对象在累积
6. `obj cycles` + `obj refs name=<对象>` 定位持有者

**⚠️ 第 4 和第 5 必须分开 —— 它们的病因完全不同。**

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **渲染调试** —— `r.*` CVar、VisualizeBuffer、`r.ShaderPrint`、GPU 抓帧 |
| 2 | 蓝图与脚本调试 |
| 3 | 网络调试 |


## 62. 调试系列第 5 轮：**渲染 — 改渲染能抓到，改覆盖层抓不到**（2026-11-26 47:00）

### 一、缓冲可视化：24 种，配置驱动

**源码 `BufferVisualizationData.cpp` 38 行：**
```cpp
const FConfigSection* MaterialSection =
    GConfig->GetSection(TEXT("Engine.BufferVisualizationMaterials"), false, GEngineIni);
```
**→ 可选哪些可视化由 ini 决定，不是硬编码。**

**24 种：BaseColor / SceneColor / SceneDepth / WorldNormal / WorldTangent /
Metallic / Roughness / Specular / AmbientOcclusion / MaterialAO / Anisotropy /
Opacity / SubsurfaceColor / ShadingModel / Velocity / CustomDepth / CustomStencil /
CustomDepthWorldUnits / SceneDepthWorldUnits / SeparateTranslucencyRGB /
SeparateTranslucencyA / PreTonemapHDRColor / PostTonemapHDRColor / FinalImage**

**⚠️ 5 种带 `ApplyAutoExposure=true`（SceneColor / FinalImage / PreTonemapHDRColor /
PostTonemapHDRColor / SeparateTranslucencyRGB）—— 亮度被归一化过，不能判绝对亮度。**

### 二、🔴 缓冲可视化的切换**只有菜单，没有控制台命令**

**源码 `EditorViewportClient.cpp` 3280：**
```cpp
void FEditorViewportClient::ChangeBufferVisualizationMode(FName InName) {
    SetViewMode(VMI_VisualizeBuffer);
    CurrentBufferVisualizationMode = InName;
}
```
**→ 状态在视口客户端上，`FName` 类型，不暴露给 Python，也没有命令。
搜遍 `Editor/` 没有 `viewmode` 注册。**

### 三、`vis`（VisualizeTexture）**是**控制台命令

**实测 `vis help` 的输出（权威语法）：**
```
VisualizeTexture/Vis <RDGResourceNameWildcard>:
VisualizeTexture/Vis <RDGResourceName>[@<Version>] [<Mode>] [PIP/UV0/UV1/UV2] [BMP] [FRAC/SAT] [FULL]:
VisualizeTexture/Vis 0                                   ← 关闭
VisualizeTexture/Vis pool [BYNAME/BYSIZE]:               ← 列池
VisualizeTexture/Vis view=[ID/NAME]
```

**`vis pool` 实测输出（本项目）：**
```
16 = (2D 592x344 PF_FloatRGBA RT)        VolumetricRenderTarget.ReconstructDepth  1792 KB
22 = (Cube 128 PF_FloatR11G11B10 RT UAV) SkyLight.ConvolvedSkyRenderTarget0       576 KB
23 = (Cube 128 PF_FloatR11G11B10 RT UAV) SkyRenderTarget                          576 KB
73 = (2D 296x172 PF_FloatRGBA RT UAV)    VolumetricRenderTarget.SecondaryTracing   448 KB
```

**能看出：体积渲染在跑 / 天光在跑 / **分辨率 592×344** 说明有屏幕百分比缩放。**
**`r.RenderTargetPoolMin = "400"` LastSetBy: Scalability。**

### 四、🔴 关键区分：`vis pool` ≠ `obj list`

| 命令 | 量什么 | 生命周期 |
| --- | --- | --- |
| `obj list` / `memreport` | **UObject 资产** | 持久，磁盘来的 |
| **`vis pool`** | **运行时渲染目标（RDG 池）** | **每帧可能复用** |

**上一轮 `TextureCube 3 个 16.5 MB` 是**资产**；
`vis pool` 里的 `SkyRenderTarget 576 KB` 是**运行时立方图**。
**两者不能相加，也不是同一个东西。****

### 五、🎯 决定性实验：渲染改动**能**被抓到

**A/B 测试（`vis SkyRenderTarget` vs `vis 0`）：**
```
pixels differing by more than 8: 135611 (16.70%)
mean absolute channel delta:   3.386
bounding box of any change:    (0, 0, 1180, 688)
```

**对比上一轮 `stat` 面板的 **0% 像素差**（两张图完全一致）。**

| 调试方式 | 改的是什么 | 能抓吗 |
| --- | --- | --- |
| `stat unit` 面板 | Canvas 覆盖层 | ❌ **0%** |
| **`vis <资源>`** | **场景渲染** | ✅ **16.7%** |

**→ 规则：改**渲染状态**的能截图验证；画**覆盖层**的不能。**
**这条规则直接决定以后怎么验证渲染改动。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-RENDER.md`** | 24 种缓冲 + vis 语法 + A/B 实测 + 可抓性规则 |
| `Tools/practice_render_commands.py` | 跑 `vis help` / `vis pool` / 查 r.* CVar |
| **`Tools/diff_captures.py`** | **像素级 A/B 对比（以后验证渲染改动都用它）** |
| `Tools/vis_on.py` / `vis_off.py` | 开关 vis |

**证据：`Saved/shot_vis.png` vs `Saved/shot_vis_off.png`。**

### 七、新增的通用工具

**`Tools/diff_captures.py` 是本轮最有复用价值的产出：**
```
python Tools/diff_captures.py a.png b.png
→ 差异像素数 / 占比 / 平均通道差 / 变化包围盒 / 判定
```
**以后任何「改了渲染但看不出差别」的问题，都能用它给出**数值**答案，而不是靠眼睛。**

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **蓝图与脚本调试** —— Python 异常栈、蓝图断点、PIE 调试 |
| 2 | 网络调试 |
| 3 | 资产与加载问题 |


## 63. 调试系列第 6 轮：**脚本 — Python 炸不垮编辑器，蓝图会弹框**（2026-11-26 48:00）

### 一、Python 四个日志通道（实测格式）

```
LogPython:          [LingXuJie] PYB: this is unreal.log
LogPython: Warning: [LingXuJie] PYB-WARN: this is unreal.log_warning
LogPython: Error:   [LingXuJie] PYB-ERR: this is unreal.log_error
LogPython: this is bare print - goes through Python stdout redirection
```

**⚠️ `log_error` 是 Error 级别 —— Commandlet 里会导致返回非零。**

### 二、异常栈：带完整路径和行号

**自己捕获后格式化：**
```
Traceback (most recent call last):
  File ".../practice_python_failures.py", line 46, in main
    nested_one()
  File ".../practice_python_failures.py", line 34, in nested_two
  ...
ValueError: deliberate failure inside nested_three
```

**未捕获时插件自己打（源码 `PyUtil.cpp` 1649-1665 用 `traceback.format_exception`）：**
```
LogPython: Error: Traceback (most recent call last):
LogPython: Error:   File ".../test_uncaught.py", line 3, in <module>
LogPython: Error:     raise RuntimeError("...")
LogPython: Error: RuntimeError: truly uncaught, no try block anywhere
```

### 三、🔴 关键结论：Python 异常**打不垮编辑器**

**实测连炸 4 次（ValueError / RuntimeError / 语法错误 / 未捕获），
每次之后 `EditorGuard check` 都是 `CHECK: healthy`。**

**→ 「脚本报错了」和「编辑器崩了」是**两件不同的事**，不要混着排查。**

### 四、语法错误会**报两遍**

```
LogPython: Error:   def broken(:
LogPython: Error:              ^
LogPython: Error: SyntaxError: invalid syntax (..., line 2)
LogPython: Error:   def broken(:          ← 又来一遍
```

**→ 插件一次 + Python stderr 重定向一次。**
**→ 日志里重复的错误块 ≠ 脚本跑了两次。**

### 五、我的 `-WaitPattern` 为什么可靠

| 情况 | `done` 会不会出现 |
| --- | --- |
| 正常结束 | ✅ |
| 异常（被 except 兜住）| ❌ |
| 异常（未捕获）| ❌ |
| 语法错误 | ❌ |
| 卡死在 API | ❌（超时）|

**→ `-WaitPattern` 超时 = 没走到最后一行 = 有失败。**

**标准骨架（建议所有脚本都这样）：**
```python
def main():
    ...
    log("PREFIX: done")

try:
    main()
except Exception as error:
    import traceback
    log("PREFIX: FATAL: %r" % error)
    log(traceback.format_exc())
```
**等 `'PREFIX: done|PREFIX: FATAL'` —— 失败时不用等超时。**

### 六、`sys.exit(0)` 会被吞掉

**源码 `PyUtil.cpp` 1620-1646：**
```cpp
// Trap and discard SystemExit with an exit code of zero
PyErr_Clear();
```
**→ 脚本里 `sys.exit(0)` 什么都不会发生。不要用它做「提前结束」。**

### 七、蓝图侧：九种运行时异常

**源码 `BlueprintExceptionInfo.h` 9-21：**
`Breakpoint / Tracepoint / WireTracepoint / AccessViolation / InfiniteLoop /
NonFatalError / FatalError / AbortExecution / UserRaisedError`

**⚠️ `AccessViolation` 在蓝图里也存在 —— 蓝图也能造成内存违例。**

### 八、🔴🔴 蓝图守卫阈值与**模态框陷阱**

**源码 `ScriptCore.cpp`：**
```cpp
static int32 GScriptRecurseLimit = 120;                 // bp.ScriptRecurseLimit
COREUOBJECT_API int32 GMaximumScriptLoopIterations = 1000000;
```

**触发时的原文：**
```
"Infinite script recursion ({0} calls) detected - see log for stack trace"
"Runaway loop detected (over {0} iterations) - see log for stack trace"
"Computation timed out - see log for stack trace"
```

**🔴 第 1283-1291 行的注释是重点：**
```cpp
// Need to reset Runaway counter BEFORE throwing script exception, because the exception causes
// a modal dialog, and other scripts running will then erroneously think they are also "runaway".
```

**→ `ThrowScriptException` 会**弹模态对话框**。**
**→ 自动化环境里那个框会挡住一切（和 gotcha #61 同类）。**
**→ 如果 PIE 里有蓝图跑出 runaway，自动化会**卡死在一个没人看的对话框上**。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-SCRIPT.md`** | 四通道 + 异常格式 + 蓝图九种异常 + 守卫阈值 + 模态框陷阱 |
| `Tools/practice_python_failures.py` | 故意制造四种失败，对比输出 |

**清理了 4 个临时测试脚本（`test_uncaught.py` / `test_syntax.py` / `vis_on.py` / `vis_off.py`）。**

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **网络调试** —— replication、net.* CVar、lag simulation、`net.PackageMap` |
| 2 | 资产与加载问题 |


## 64. 调试系列第 7 轮：**网络 — 大部分只能读源码，我不假装验证过**（2026-11-26 49:00）

### 一、先说诚实的边界

**灵虚界是单人项目：`.uproject` 里没有网络插件，`Config` 里没有 NetDriver 段。**

**所以本篇大部分结论是**读源码**得出的，**没有运行验证**。**

**文档里每个结论都标了 `✅ 实测` 或 `📖 源码`。这是本系列第一篇大部分未实测的。**
**我不打算把它写成看起来都验证过了的样子。**

### 二、✅ 实测部分：本项目网络是静默的

| 检查 | 结果 |
| --- | --- |
| `net`（无参数）| **无任何输出** |
| `unreal.World` 的 `get_net_mode` / `get_net_driver` | **都不存在** |
| `unreal.World` 上含 `net` 的属性 | **一个都没有** |

**存在的 CVar：**
```
net.AllowPIESeamlessTravel        = "false"
net.UseAdaptiveNetUpdateFrequency = "0"
net.Iris.UseIrisReplication       = "0"
net.DebugDrawCullDistance         = "0"
```

**不存在的（只有 `Cmd:` 没有 `= value`）：**
```
net.PackageMap.LocateNetDriver / net.RepDriver / net.MaxRepArraySize / net.DebugDrawRelevant
```

### 三、🎯 一个新学到的通用判据

> **敲一个 CVar 名字：**
> **有 `= value` → 存在**
> **只有 `Cmd: xxx` → 不存在**
>
> **不用猜，回显自己会说。**

### 四、📖 丢包模拟的完整参数与**互斥关系**

**`FPacketSimulationSettings::ParseSettings` 接受的 token：**
`PktEmulationProfile= / PktLoss= / PktLossMinSize= / PktLossMaxSize= /
PktOrder= / PktLag= / PktDup= / PktLagVariance= / PktLagMin=`

**🔴 互斥关系（源码注释原文）：**

| 约束 | 后果 |
| --- | --- |
| `PktOrder` **优先于** `PktDup` 和 `PktLag` | 设了 PktOrder，另两个**静默失效** |
| `PktDup` **不能**和 `PktOrder`/`PktLag` 同用 | 同上 |
| `PktLagVariance` 只在 `PktLag` 开启时有效 | 单独设没用 |
| `PktLagMin/Max` 在 `PktLag` 设置后**被忽略** | 被覆盖 |
| `PktJitter` **会造成接收端丢包** | 不是单纯加抖动 |

**→ 这是本篇最实用的一条：以为设了两个参数，实际只有一个生效，测出来的数据是假的。**

### 五、📖 模拟设置会**跨 PIE 重启残留**

**源码 `NetEmulationHelper.cpp` 16-47：**
```cpp
/** Global that stores the network emulation values outside the NetDriver lifetime */
static TOptional<FPacketSimulationSettings> PersistentPacketSimulationSettings;
// 应用到该世界里所有活跃的 NetDriver
```

**→ PIE 里设的 `PktLag=100`，PIE 重启后**仍然有效**。**
**→ 排查「为什么 PIE 有延迟」时先检查这个 —— 和无头日志级别残留是同一类问题。**
**→ 要清零得显式 `net PktLag=0`，不要以为重启就清了。**

### 六、📖 三个编译门

| 宏 | 定义 | 影响 |
| --- | --- | --- |
| `DO_ENABLE_NET_TEST` | `!(UE_BUILD_SHIPPING)` | 丢包模拟在 Shipping 里没有 |
| `Exec_Dev` 包在 `!UE_BUILD_SHIPPING` | — | **`net` 子命令在 Shipping 里没有** |
| `DO_BLUEPRINT_GUARD` | 独立宏 | 蓝图循环守卫 |

**→ 「打包后网络问题查不了」是编译期就删掉的，不是错觉。**

### 七、📖 `net` 子命令全表

`SOCKETS / PACKAGEMAP / NETFLOOD / NETDEBUGTEXT / NETDISCONNECT /
DUMPSERVERRPC / DUMPDORMANCY / PKTLOSSBURST= / FLUSHALLNETDORMANCY /
DUMPSUBOBJECTS / DUMPREPLAYOUTFLAGS`

**排查最常用的三个：`net PACKAGEMAP`（对象映射）、`net DUMPSERVERRPC`（RPC 统计）、
`net DUMPDORMANCY`（休眠状态）。**

### 八、解锁点

**一旦 PIE 设成 `Play As Listen Server` + 2 客户端，`net` 就**有接收者**了，
本篇所有「未验证」的内容就能逐条变实测。**

**这一条写进了文档第八节，作为下次起步的第一步。**

### 九、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-NET.md`** | 诚实标注 ✅/📖 的网络调试文档 |
| `Tools/practice_net_commands.py` | 探本项目网络状况 + CVar 存在性 |

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **资产与加载问题**（最后一个域）—— 引用链、Size Map、Cook 错误、加载失败 |
| 2 | 之后：回头做**实战演练**——用前七篇的方法定位项目里的真实问题 |


## 65. 调试系列第 8 轮：**资产 — 八条真实失败，根因是路径猜错**（2026-11-26 50:00）

### 一、真实素材：日志里八条 `LoadAsset failed`

```
LogEditorAssetSubsystem: Error: LoadAsset failed: The AssetData
'/Game/Moxiang/Static/SM_Boss001.SM_Boss001' could not be found in the Asset Registry.
```

### 二、🔴 这句话的真正含义

**关键字不是「文件不存在」，是 **"could not be found in the Asset Registry"**。**
**→ 资产注册表里**没有这个路径**。**

**两种可能：路径不对（常见）／注册表还没扫到（少见）。**

### 三、本项目的根因：**Interchange 自动嵌套**

**`/Game/Moxiang/Static/SM_Boss001` 从来不存在。**

**真路径：**
```
/Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001
```

**多出来的 `boss001_static/StaticMeshes/` 是 Interchange 导入器按**源文件名**自动嵌套的。**

**→ 我的脚本按扁平路径猜，猜错了。**
**→ 和 gotcha #82/#83 同一个根因。**

### 四、正确做法：**按名字搜，不要猜路径**

**`Tools/find_asset.py` 实测：**
```
registry holds 2194 asset(s) under /Game
    /Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001
        class=StaticMesh
found 1 match(es) for 'SM_Boss001'
load .../SM_Boss001.SM_Boss001 -> ok
```

**→ 一次搜索拿到真路径，然后加载成功。**

**规则（以后所有脚本）：**
> **不要手写 `/Game/...` 路径。用 `get_assets_by_path` 搜，或从已有对象 `get_path_name()` 读。**
> **路径是人猜的，注册表是事实。**

**⚠️ 实测坑：`get_asset_by_object_path(SoftObjectPath(...))` 会**
**`TypeError: Failed to convert parameter 'object_path'`** —— 不接受这个类型。**

### 五、本项目资产分布（实测）

```
/Game                        2194 asset(s)
/Game/Moxiang                 370 asset(s)
/Game/Moxiang/Skeletal         59 asset(s)
/Game/Moxiang/Textures          1 asset(s)     ← 但磁盘有 2,407 张 PNG
/Game/Moxiang/Materials         1 asset(s)
/Game/Moxiang/Static            1 asset(s)
```

**🔴 两个陷阱：**
1. **`/Game` 2194，但项目自己的只有 370** —— 另外 1824 个是引擎模板。
   「项目有 2194 个资产」是**错的**。
2. **`Textures` 只有 1 个资产，磁盘却有 2,407 张 PNG** —— 贴图基本没导入。

### 六、预防：资产审计工具（实测）

**`Tools/audit_assets.py`：**
```
known set holds 2194 object path(s)
level has 116 actor(s)
checked 4 skeletal mesh reference(s), 0 not in registry
```

**→ 本项目当前**零缺失引用**。**

**价值：在「加载失败」发生**之前**发现路径不对。**

**⚠️ 只查了 `SkeletalMeshComponent`（4 个），`StaticMeshComponent` 还没加。**

### 七、打包版特有：Cook 找不到资产

**源码错误文本：**
```
"Generated package %ls is missing its generation data and cannot be saved."   CookOnTheFlyServer.cpp:3751
"CookPackageSplitter is missing %ls during PreSaveGeneratorPackage."         同上 :3993
```

**→ 「编辑器里好好的、打包后加载失败」的头号原因是**硬编码路径**：
**Cooker 靠引用图找资产，靠字符串猜的路径它看不见。****

**→ 这也说明本篇那个 `LoadAsset failed` 案例为什么危险：
编辑器里报错还能看见，打包后就**静默失败**。**

### 八、🎯 八个域全部完成

| # | 域 | 文档 | 实测程度 |
| --- | --- | --- | --- |
| 1 | 日志与断言 | `UE5-DEBUG-LOGGING.md` + `ASSERTS.md` | ✅ 全部实测 |
| 2 | 崩溃与调用栈 | `UE5-DEBUG-CRASH.md` | ✅ 用本项目真实崩溃 |
| 3 | 性能剖析 | `UE5-DEBUG-PERF.md` | ✅ 部分（面板抓不到）|
| 4 | 内存与泄漏 | `UE5-DEBUG-MEMORY.md` | ✅ 全部实测 |
| 5 | 渲染调试 | `UE5-DEBUG-RENDER.md` | ✅ 含像素级 A/B |
| 6 | 蓝图与脚本 | `UE5-DEBUG-SCRIPT.md` | ✅ 故意失败实测 |
| 7 | 网络调试 | `UE5-DEBUG-NET.md` | ⚠️ **源码为主，未实测** |
| 8 | 资产与加载 | `UE5-DEBUG-ASSET.md` | ✅ 用本项目真实日志 |

**共 10 篇调试文档（含索引）。**

### 九、下一轮该做什么

**按目标原文「直到能独立定位真实 UE5 故障为止」——现在该**实战**了。**

**不再继续写文档，而是：**
1. 找项目里一个**还没解决的问题**
2. 用这九篇的方法从头定位（不查既有结论）
3. 记录用了哪篇的哪个方法、定位过程、结论

**候选问题（从 `Docs/BATCH-EXPORT-STATUS.md` 的未解决项里挑）：**
- 78 个模型没有 MATERIAL 块
- 101 个贴图名对应文件不存在
- `thunder3` 转换失败
- 动画在编辑器里看不见播放


## 66. 调试系列第 9 轮：**第一个实战 —— Boss 动画不播放，从零定位到根因**（2026-11-26 51:00）

### 一、起点

**既有记录只说了「动画数据验证过，但引擎驱动被阻塞」—— 这是个**没有定位**的问题。**
**我从零开始，不采信那句话。**

### 二、四步定位

| 步 | 脚本 | 结果 |
| --- | --- | --- |
| 1 | `diag_anim_step1.py` | 只观察。**`get_play_rate=0.0` 误导了我** |
| 2 | `diag_anim_step2.py` | **直接 dump 结构体 → 找到根因一** |
| 3 | `diag_anim_step3.py` | 失败两次（API 签名）后成功，**验证根因二** |
| 4 | 恢复原状 | 确认改动可逆 |

### 三、🔴 根因：一个脚本里两处

**`Tools/import_and_place.py`：**
```python
if anim is not None:
    length = anim.get_editor_property("sequence_length")
    log("  animation length %.4f s" % length)     # ← 打了长度，然后把它扔了
    ...
component.set_skeletal_mesh_asset(mesh)          # ← 只设网格
                                                  # ← 从没设 animation_mode
                                                  # ← 从没设 anim_to_play
level.save_current_level()                        # ← 顺便：19:52 崩溃的调用
```

**实测确认的组件状态：**
```
mode = <AnimationMode.ANIMATION_BLUEPRINT: 0>     ← 默认模式，不是 SINGLE_NODE
anim_to_play = None                                ← 没有动画
```

### 四、验证（不改项目，改完恢复）

```
D3: bind pose -> (9350.0, -6200.0, 3740.0)
D3: applied single node mode and an animation
D3:   t=0.00 -> (9428.808, -6355.831, 3717.728)
D3:   t=0.25 -> (9428.805, -6356.584, 3718.637)
D3:   t=0.50 -> (9428.727, -6358.372, 3720.965)
D3:   t=0.75 -> (9428.489, -6360.426, 3724.013)
D3: distinct poses across four times: 4
D3: VERDICT: the animation moves the skeleton once it is assigned
D3: restored: mode=ANIMATION_BLUEPRINT, anim=None
```

**→ 四个时间点四个位姿。动画确实驱动了机型。**
**→ 之后恢复原状，关卡没被改。**

### 五、🔴 这次实战更正了两条既有结论

| 我之前说的 | 实际 | 错在哪 |
| --- | --- | --- |
| **「`set_position` 不触发重新求值」** | **会触发** | 当时没有动画被赋值，所以当然不动 |
| **「`get_bone_pose` 挂死 → 读不到骨骼」** | **`get_bone_transform` 完全能用** | 用错了 API |

**共同点：**把「我用这个方法失败了」当成「这件事做不到」。****

**这已经是本系列第 N 次同类错误。已经写进文档第十节。**

### 六、三个 API 坑

| 坑 | 表现 | 正确用法 |
| --- | --- | --- |
| `get_bone_transform(name, BoneSpaces.X)` | **TypeError** | **只传名字**，默认世界空间 |
| `get_play_rate()` | 无实例时返回 0.0，误导 | 读 `animation_data.saved_play_rate`（实际 1.0）|
| `get_asset_by_object_path(SoftObjectPath)` | **TypeError** | `get_assets_by_path` + 过滤 |

### 七、修复方案（**未应用**）

**在 `import_and_place.py` 的 `set_skeletal_mesh_asset` 之后加：**
```python
if anim is not None:
    component.set_editor_property("animation_mode",
                                  unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    data = component.get_editor_property("animation_data")
    data.set_editor_property("anim_to_play", anim)
    data.set_editor_property("saved_playing", True)
    data.set_editor_property("saved_play_rate", 1.0)
    component.set_editor_property("animation_data", data)
```

**并建议删掉结尾的 `level.save_current_level()`（崩溃触发点，且关卡由 `build_level.py` 重建）。**

**⚠️ 按用户要求「先不要急着开发」，**代码一字未改**。**

### 八、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-ANIM.md`** | 完整定位记录（起点/四步/根因/验证/更正/修复方案）|
| `Tools/diag_anim_step1.py` | 观察：组件状态 + 可用 API |
| `Tools/diag_anim_step2.py` | dump 结构体，找到根因 |
| `Tools/diag_anim_step3.py` | 验证根因并恢复原状 |

### 九、这次实战的意义

**九篇文档里的方法在这一个真实问题上串起来了：**
- 读结构体不读派生 getter（内存篇的教训）
- `-WaitPattern` 当失败检测（脚本篇）
- 按名字搜资产（资产篇）
- 改完恢复原状（项目规则 5）

**→ 这是第一次「不是写文档，而是用文档解决问题」。**

### 十、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 再来一个实战案例（候选：78 个模型无 MATERIAL 块 / `thunder3` 转换失败）|
| 2 | 或者：等用户指示后应用这个修复 |


