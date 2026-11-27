# UE5 调试 · 五：内存与泄漏（memreport / obj cycles）

> **本篇全部结论来自本机源码 + 在灵虚界项目上的实测。**
>
> **最重要的两条：**
> **1. `memreport` 是**延迟到帧末**执行的，因为要先强制 GC 才能报出真实占用。**
> **2. `obj cycles` 报出 29 个环内对象 —— 但**一个都不是项目对象**。环数不等于泄漏。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、`memreport` 的机制：先 GC，再报告

**源码：`UnrealEngine.cpp` 第 8120-8126 行**
```cpp
bool UEngine::HandleMemReportCommand(const TCHAR* Cmd, FOutputDevice& Ar, UWorld* InWorld) {
    // This will defer the report to the end of the frame so we can force a GC and get a real report
    // with no gcable objects
    GEngine->DeferredCommands.Add(FString::Printf(TEXT("MemReportDeferred %s"), Cmd));
    return true;
}
```

**→ 命令只是把 `MemReportDeferred` 塞进延迟队列。**
**→ 帧末真正执行时**先跑一次 GC**，所以报告里没有待回收对象。**

**⚠️ 这解释了一个常见困惑：**
> **你在控制台敲 `memreport`，看不到立刻输出 —— 因为它在帧末才跑。
> 报告写进文件，不是写进控制台。**

### 1.1 报告落在哪

**实测路径：**
```
Saved/Profiling/MemReports/<项目名>-<平台>-<日期>/
    Pid<PID>_<项目名>-<平台>-<日期>.memreport
```

**本次：`Pid4544_LingXuJie-WindowsEditor-26-20.54.27.memreport`，**468.5 KB**。**

### 1.2 选项（源码 `HandleMemReportDeferredCommand`，第 8169-8191 行）

| 参数 | 作用 |
| --- | --- |
| `-LOG` | 输出到引擎日志，而不是文件 |
| `-CSV` | CSV 格式 |
| `-FULL` | 用 `[MemReportFullCommands]` 段 |
| `TYPE=<Profile>` | 用自定义段 `[MemReport<Profile>Commands]` |
| `NAME=<文件名>` | 指定文件名 |

### 1.3 🔴 报告内容是可配置的

**默认 `[MemReportCommands]` 有 **34 条命令**（`BaseEngine.ini` 第 2371 行起）：**
```ini
+Cmd="Mem FromReport"
+Cmd="LogCountedInstances"
+Cmd="obj list -resourcesizesort"
+Cmd="rhi.DumpMemory"
+Cmd="rhi.DumpResourceMemory"
+Cmd="rhi.dumpresourcememory summary name=Lumen"
+Cmd="rhi.dumpresourcememory summary name=Nanite"
+Cmd="rhi.dumpresourcememory summary name=Shadow"
+Cmd="rhi.dumpresourcememory summary name=DistanceFields"
+Cmd="rhi.dumpresourcememory summary name=GPUScene"
+Cmd="rhi.dumpresourcememory summary name=SkinCache"
+Cmd="rhi.dumpresourcememory summary name=VertexBuffer"
+Cmd="obj list class=SkeletalMesh -resourcesizesort"
+Cmd="obj list class=StaticMesh -resourcesizesort"
+Cmd="listtextures nonvt"
+Cmd="listtextures uncompressed"
+Cmd="LogOutStatLevels"
+Cmd="ListSpawnedActors"
+Cmd="wp.DumpDataLayers"
+Cmd="wp.DumpStreamingSources"
+Cmd="r.DumpRenderTargetPoolMemory"
```

**`[MemReportFullCommands]` 有 **43 条**。**

**→ 可以自己加段：**
```ini
; DefaultEngine.ini
[MemReportLingXuJieCommands]
+Cmd="Mem FromReport"
+Cmd="obj list class=SkeletalMesh -resourcesizesort"
+Cmd="obj list -resourcesizesort"
```
**然后 `memreport -type=LingXuJie`。**

---

## 二、`obj cycles`：找引用环

**源码：`Runtime/CoreUObject/Private/UObject/Obj.cpp` 第 5161-5208 行**
```cpp
if (FParse::Command(&Str, TEXT("CYCLES"))) {
    // find all cycles in the reference graph
    FFindStronglyConnected IndexSet;
    IndexSet.FindAllCycles();
    ...
    Ar.Logf(TEXT("%d total objects, %d total edges."), ...);
    Ar.Logf(TEXT("Non-permanent: %d objects, %d edges, %d strongly connected components, "
                 "%d objects are included in cycles."), ...);
}
```

**用的算法是**强连通分量（Strongly Connected Components）** —— 这正是找引用环的正确算法。**

### 2.1 本项目实测（真实输出）

```
66998 total objects, 126353 total edges.
Non-permanent: 12333 objects, 8616 edges, 14 strongly connected components,
               29 objects are included in cycles.
```

**6.7 万个 UObject，12.6 万条引用边，**29 个对象卡在 14 个环里**。**

### 2.2 🔴 但这 29 个**一个都不是项目对象**

**逐个看过环的成员，只有 4 种类型：**
```
Level / ParticleEventManager / World / WorldSettings
```
**全是 `/Engine/Transient.World_N` 下的引擎对象，`/Game/` 出现 **0 次**。**

**环的结构（每种在 `World_N` 上重复）：**
```
ParticleEventManager → WorldSettings      [Actor:Owner]
WorldSettings → ParticleEventManager      [Actor:Children]

Level → World                             [Level:OwningWorld]
World → Level                             [World:PersistentLevel / LevelCollection:*]
```

**→ 这是引擎**设计如此**的持有关系。
**World 不是靠 GC 回收的，是靠 `UWorld::Destroy()` 显式销毁。**

### 2.3 🔴 最重要的教训

> **`obj cycles` 报「29 个对象在环里」不等于「有 29 个泄漏」。**
>
> **必须看**环里是谁**。**
> **引擎固有的环（World↔Level、WorldSettings↔ParticleEventManager）永远存在，
> 且永远不会被回收 —— 因为它们不该被回收。**

**判断方法：**
```powershell
# 在日志里搜 obj cycles 的输出，看有没有 /Game/
$lines | Where-Object { $_ -match '^\[.*\](/Game/|/Engine/Transient)' }
```

**如果只有 `/Engine/`，说明项目自己零泄漏。**

**这和本系列反复出现的「数字是真的但量错了东西」是同一类：
**「环的数量」不是「泄漏的数量」，必须看内容。**

---

## 三、本项目实测内存数据

**`memreport -full` 报告开头：**
```
Time Since Boot: 3733.60 Seconds          （62 分钟）
Process Physical Memory: 4554.05 MB used, 4648.82 MB peak
Process Virtual Memory:  8406.94 MB used, 9719.43 MB peak
Physical Memory: 18471.45 MB used, 30466.34 MB free, 48937.79 MB total
FPageAllocator (all threads) = [14.81 / 0.00] MB
Nametable memory usage = 17.76 MB
AssetRegistry memory usage = 140.97 MB
```

### 3.1 按类的资源占用（`obj list -resourcesizesort`）

| 类 | 数量 | 对象内存 | **资源内存** |
| --- | --- | --- | --- |
| **Texture2D** | **251** | 339 KB | **43.1 MB** |
| **TextureCube** | **3** | 3.9 KB | **16.5 MB** |
| Material | 152 | 524 KB | 15.0 MB |
| StaticMesh | 136 | 682 KB | 10.6 MB |
| **VolumeTexture** | **7** | 9.5 KB | **10.5 MB** |
| BodySetup | 138 | 318 KB | 7.4 MB |
| MaterialInstanceConstant | 186 | 404 KB | 7.3 MB |
| **FontFace** | **7** | **4.8 MB** | 4.8 MB |
| NavCollision | 134 | 41 KB | 181 KB |

### 3.2 🔴 反直觉的发现：10 张贴图占了 63%

**3 张 cubemap = 16.5 MB，
7 张 volume texture = 10.5 MB，
合计 27 MB。而 251 张 Texture2D 是 43 MB。**

**→ 10 个资产的资源占用，是 251 个的 63%。**

### 3.3 但这 10 个**全是引擎的**

**逐个列过（`TextureCube` 加载了 3 个，资产库里 18 个）：**
```
/Engine/EditorMaterials/AssetViewer/EpicQuadPanorama_CC+EV1
/Engine/EngineMaterials/DefaultCubemap
/Engine/EngineResources/DefaultTextureCube
/Engine/MapTemplates/Sky/DaylightAmbientCubemap
...
```
```
/Engine/EngineMaterials/Hair/Hair_DualScattering
/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128   ← 体积云
/Engine/EngineSky/VolumetricClouds/VT_PerlinWorley_Balanced
...
```

**→ **没有一张是 `/Game/`。****

**→ 结论：本项目的内存大头是**引擎编辑器本身的开销**，不是项目内容。**
**→ 这对编辑器会话是正常的。要评估项目真实占用，必须在**打包版**里量。**

---

## 四、内存排查清单

### 4.1 「内存一直在涨」

| 步 | 命令 | 看什么 |
| --- | --- | --- |
| 1 | `memreport -full` | 记录基线 |
| 2 | 做可疑操作 N 次 | — |
| 3 | `memreport -full` 再来一次 | **对比两份报告** |
| 4 | 看 `obj list -resourcesizesort` 哪一类的 Count 涨了 | **数量涨 = 对象在泄漏** |
| 5 | 看 NumKB 涨而 Count 不涨 | **单个对象在变大（缓存没释放）** |
| 6 | `obj cycles` | 引用环 |

**⚠️ 第 4 和第 5 要分开看：**
- **Count 涨** → 对象没被回收 → 引用环或强引用没断
- **Count 不变、NumKB 涨** → 同一个对象在累积数据 → 数组/缓存没清

### 4.2 「怀疑某个对象泄漏了」

```
obj refs name=<对象完整路径>
```

**源码 `Obj.cpp` 第 5375 行起支持这些修饰词：**

| 修饰词 | 作用 |
| --- | --- |
| `shortest` | 只显示最短引用链 |
| `longest` | 只显示最长引用链 |
| `all` | 显示全部结果 |
| `direct` | 只显示直接引用者 |
| `external` | 只显示包外引用 |
| `full` | 完整链 |
| `minimal` | 最小输出 |

**用法：**
```
obj refs name=/Game/Moxiang/Skeletal/Boss001/.../SK_Boss001.SK_Boss001 shortest
```

**→ 会打印出「谁持有它」，一路指到根（通常是 GameInstance / World / 静态变量）。**

**这就是回答「这个对象为什么还没被销毁」的唯一可靠办法。**

### 4.3 「`memreport` 没反应」

**它是延迟执行的（本篇第一节）。**
**→ 看 `Saved/Profiling/MemReports/` 目录，不要看控制台。**
**→ 如果目录里没有，检查 `ALLOW_DEBUG_FILES`（`HandleMemReportDeferredCommand` 整个包在 `#if ALLOW_DEBUG_FILES` 里，第 8171 行）。**

---

## 五、待做

| 事项 | 为什么 |
| --- | --- |
| 在**打包版**量一次内存 | 编辑器数据被引擎开销污染，不能代表运行时 |
| 给项目加 `[MemReportLingXuJieCommands]` | 现在跑的是引擎默认 34 条，很多与项目无关 |
| 量一次 `AssetRegistry` 140 MB 的构成 | 项目只有 370 个 UE 资产，140 MB 偏高 |

**⚠️ 按用户要求本轮**只读不改**。**

---

## 六、本篇依据的源码位置

| 事实 | 文件 | 行 |
| --- | --- | --- |
| `memreport` 延迟到帧末（先 GC）| `UnrealEngine.cpp` | 8120-8126 |
| 选项 `-LOG`/`-CSV`/`-FULL`/`TYPE`/`NAME` | 同上 | 8176-8191 |
| 整个报告包在 `#if ALLOW_DEBUG_FILES` | 同上 | 8171 |
| `obj cycles` 用强连通分量 | `Obj.cpp` | 5161-5208 |
| `obj refs` 的修饰词 | 同上 | 5375-5419 |
| 默认 34 条 memreport 命令 | `Config/BaseEngine.ini` | 2371 起 |
| Full 段 43 条命令 | 同上 | 2408 起 |
