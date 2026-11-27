# UE5 学习 · 打包与优化（第一块）：帧时间终于量出来了

> **之前能力盘点里有一条：「性能域**只有机制，没有数字**」。
> **这一块把它补上了 —— 而且发现了一个**不需要看面板**的办法。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、官方文档说了什么

### 1.1 `performance.md`（16.3 KB，22 节）

| 章节 | 要点 |
| --- | --- |
| **Understanding Performance** | 性能依赖两件事（原文没展开，但后面分了）|
| **Measuring FPS and Frame Time** | 怎么量 |
| **Hardware Limitations and Framerate Drops** | 硬件限制 |
| **CPU-Bound vs. GPU-Bound** | **判断瓶颈在哪一侧 —— 优化的第一步** |
| **Processing Spikes** | 突发的短时峰值 |
| **Expensive vs. Inexpensive Operations** | 昂贵 vs 廉价操作 |
| **Memory in Realtime Applications** | 内存 |
| **Performance and Power Usage** | 功耗 |
| **Profiling Tools** | **Unreal Insights** / **Stat Commands** / **RenderDoc** |
| **Performance Configuration Tools** | 配置手段 |
| **Console Commands and Variables** | CVar / 输出日志 / 配置文件 / 设备配置 |
| **Tips: Test Early and Test Often** | 早测常测 |

### 1.2 `command-line-arguments.md`（14.2 KB，29 节）

**覆盖：从命令行/编辑器传参、Game/Server 参数、自己建参数（Flags / Key-Value）、
**用命令行改引擎配置**、**用命令行执行控制台命令**、URL 参数、**从文件读取参数**、参数全表。**

---

## 二、🔴 打包确实需要关编辑器 —— 项目脚本自己写明了

**`Tools/Package.ps1` 的注释：**
```
The editor's Live Coding holds a mutex on UnrealEditor.exe, so UBT refuses to build
("Unable to build while Live Coding is active"). BuildCookRun does not accept
-NoHotReloadFromIDE, so we build both targets ourselves first and let
BuildCookRun -skipbuild only cook/stage/pak/archive.
```

**→ **Live Coding 持有互斥体，UBT 拒绝构建。** 这是硬约束。**

**打包相关配置（✅ 实测）：**
```
DefaultEngine.ini:2   GameDefaultMap=/Game/Maps/LingXuJie.LingXuJie
DefaultGame.ini:3     ProjectName=LingXuJie
DefaultGame.ini:12    +DirectoriesToAlwaysCook=(Path="/Game/Materials")
```

---

## 三、🎯🎯 这一块最重要的发现：`stat dump*` 会**写进日志**

**问题：`stat unit` 面板是 canvas 覆盖层，视口截图抓不到；Python 也没有读帧时间的 API。**

**实测过的 API（✅）：**
```
get_time_seconds        → 15.43   ✅
get_real_time_seconds   → 15.43   ✅
get_frame_count         → 不存在
get_delta_seconds       → 不存在
get_smooth_frame_rate   → 不存在
```

**→ 读不到 `stat unit` 的分解。**

### 出路：统计系统有**dump 到日志**的命令

**`Engine/Source/Runtime/Core/Private/Stats/StatsCommand.cpp:1874-1882`：**
```cpp
Ar.Log( TEXT("stat dumpframe [-ms=5.0] [-root=empty] [-depth=maxint] - dumps a frame of stats"));
Ar.Log( TEXT("stat dumpave|dumpmax|dumpsum [-start|-stop] [-num=30] [-ms=5.0] [-depth=maxint]"));
Ar.Log( TEXT("stat dumphitches - toggles dumping hitches"));
Ar.Log( TEXT("stat dumpevents [-ms=0.2] [-all]"));
Ar.Log( TEXT("stat dumpnonframe"));
Ar.Log( TEXT("stat dumpcpu - dumps cpu stats"));
```

**→ `Ar.Log()` = **写进输出日志** = **Python 能读**。**

---

## 四、🎯 实测：真实帧时间

### 4.1 第一次尝试被裁剪

```
stat dumpave -start -ms=250 -num=240
→ LogStats:  334.551ms (1273)  -  OtherChildren     ← 只有 2 行
```

**→ `-ms=250` 把树砍到只剩一个聚合项。**

### 4.2 加 `-ms=0 -depth=maxint` 拿到全树（✅）

```
stat dumpframe -ms=0 -depth=maxint

LogStats: Single Frame 2016854 ---------------------------------
LogStats:   8.865ms (   4)  -  Thread_4728_0 - GameThread - STATGROUP_Threads
LogStats:     8.863ms (   2)  -  FrameTime - STAT_FrameTime - STATGROUP_Engine
```

**→ **GameThread FrameTime = 8.863 ms** ≈ **113 FPS**（CPU 游戏线程）**

### 4.3 各线程耗时（✅ 实测）

```
14.319ms  Background Worker #4
12.005ms  Background Worker #13
10.483ms  FUdpMessageProcessor        ← UDP 消息处理器
 9.479ms  ShaderCompilingThread       ← 着色器还在编译
 9.216ms  Foreground Worker (Standby #0)
 8.970ms  Background Worker #8
 8.950ms  Background Worker #11
 8.865ms  GameThread                  ← 帧时间
```

**→ **游戏线程 8.865 ms**，但好几个后台线程比它更慢。**

**→ 那些后台线程是**编辑器的**（DDC 维护、着色器编译），**不是游戏的** —— 日志里同时看到
`LogDerivedDataCache: Maintenance finished in +00:00:58`。**

### 4.4 RHI 单项

```
0.043ms / 0.039ms / 0.025ms  FRDGPass Execute
```

**→ 这些是**单个 RDG pass** 的耗时，不能相加成 GPU 总时间。**

---

## 五、⚠️ 这个数字的适用边界

| 事实 | 说明 |
| --- | --- |
| 8.865 ms 是**编辑器 PIE** 里的游戏线程 | **不是打包后的数字** |
| 编辑器有 DDC/着色器编译等后台负载 | 会拉高整体，但不直接占游戏线程 |
| GPU 总时间**没量到** | 只有单项 RDG pass |

**→ 项目目标 1080p/60（16.6 ms）。**8.865 ms 看起来有余量，但这是在编辑器里，
且场景是空的黑盒子（10 个 actor），不是兰州街景（116 个 actor）。**

**→ **这个数字不能当作「项目性能达标」的证据。****

---

## 六、这一块学到什么

**1. 🎯 `stat dump*` 命令写日志，是拿统计数据的**唯一 Python 可用路径**。**
比截图可靠，也比 Insights 轻。

**2. `-ms` 会裁剪输出。** 不加 `-ms=0` 只能看到一两个聚合项。

**3. `-depth=maxint` 才能看到完整调用树**（FrameTime 在第 2 层）。

**4. 后台线程比游戏线程慢是**编辑器的正常现象**，不能拿它判断游戏性能。**

**5. 在编辑器里量性能 ≠ 打包后量性能。**
文档（`performance.md`）也说要先分清 CPU/GPU 瓶颈再优化 —— 但**环境必须是目标环境**。

---

## 七、打包这一半：为什么没做

**`Package.ps1` 明确写着 Live Coding 持有互斥体，UBT 会拒绝构建。
→ **必须关闭编辑器才能打包。****

**按 AGENTS.md 规则 1（关掉前必须问一句），我**没有**关编辑器。**

**→ 打包实操需要你点头。下面是需要的信息：**

| 项 | 值 |
| --- | --- |
| 脚本 | `Tools\Package.ps1 -Config Development`（默认 Development）|
| 产物目录 | `Saved\Package\<Config>` |
| 需要 | **关闭编辑器**（Live Coding 互斥体）|
| 预计耗时 | 未测（首次 cook 可能十几分钟到半小时）|

---

## 八、下一块

**如果你同意关编辑器，下一块就跑一次 Development 打包，验证：
① 构建成功 ② cook 包含 `/Game/Maps/LingXuJie` ③ stage/pak 产物存在 ④ 能启动。**

**如果不想关，就继续做**不需要打包的优化实验**（比如在练习关卡里
用 `stat dumpave` 对比不同设置的帧时间）。**

**⚠️ 编辑器状态：主关卡 116 actor、视口复位、练习关卡 10 actor。**
