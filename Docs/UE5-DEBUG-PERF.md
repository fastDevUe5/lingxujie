# UE5 调试 · 四：性能剖析（stat 与帧预算）

> **本篇全部结论来自本机源码 + 在灵虚界项目上的实测。**
>
> **最有价值的一条：`stat unit` 显示的是**平滑值**，单帧卡顿会被稀释掉 —— 要看卡顿必须用 `stat unitmax`。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、`stat unit` 那几行数字到底是什么

**源码：`Runtime/Engine/Private/UnrealClient.cpp`，`FStatUnitData::DrawStat`**

```cpp
// 第 381-411 行 —— 每个值都是 0.9/0.1 的指数平滑
RawFrameTime      = DiffTime * 1000.0f;
FrameTime         = 0.9 * FrameTime + 0.1 * RawFrameTime;

RawGameThreadTime = FPlatformTime::ToMilliseconds(GGameThreadTime);
GameThreadTime    = 0.9 * GameThreadTime + 0.1 * RawGameThreadTime;

RawRenderThreadTime = FPlatformTime::ToMilliseconds(GRenderThreadTime);
RenderThreadTime    = 0.9 * RenderThreadTime + 0.1 * RawRenderThreadTime;

RawRHITTime = FPlatformTime::ToMilliseconds(GRHIThreadTime);
RHITTime    = 0.9 * RHITTime + 0.1 * RawRHITTime;

RawGPUFrameTime[GPUIndex] = FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles(GPUIndex));
GPUFrameTime[GPUIndex]    = 0.9 * GPUFrameTime[GPUIndex] + 0.1 * RawGPUFrameTime[GPUIndex];

// 第 434-438 行 —— 注册成 stat
SET_FLOAT_STAT(STAT_UnitFrame,  FrameTime);          // 面板上的 "Frame"
SET_FLOAT_STAT(STAT_UnitGame,   GameThreadTime);     // "Game"
SET_FLOAT_STAT(STAT_UnitRender, RenderThreadTime);   // "Draw"
SET_FLOAT_STAT(STAT_UnitGPU,    GPUFrameTime[0]);    // "GPU"
SET_FLOAT_STAT(STAT_UnitRHIT,   RHITTime);           // "RHIT"
```

### 1.1 🔴 最重要的性质：**EMA 平滑**

**`FrameTime = 0.9 × 旧值 + 0.1 × 新值`**

**→ 一帧突然 200 ms，面板上只会上涨 `0.1 × (200 - 正常值)`。
如果正常是 16 ms，这一帧只会让显示值涨到约 34 ms，**下一帧就开始回落**。**

**→ **`stat unit` 天生看不见单帧卡顿。**这是设计如此，不是 bug。**

---

## 二、`stat unit` 家族：各有各的用途

**源码：`UnrealEngine.cpp` 第 19272-19275 行注册的名称**
```cpp
DetailedStats.Add(TEXT("Unit"));
DetailedStats.Add(TEXT("UnitCriticalPath"));
DetailedStats.Add(TEXT("UnitMax"));
DetailedStats.Add(TEXT("UnitGraph"));
```

| 命令 | 显示什么 | 什么时候用 |
| --- | --- | --- |
| `stat unit` | **EMA 平滑**的 Frame/Game/Draw/GPU/RHIT | 看整体趋势、判断谁是瓶颈 |
| **`stat unitmax`** | **环形缓冲里每个通道的最大值** | **🔴 抓卡顿** |
| `stat unitgraph` | 时间曲线（保留 `NumberOfSamples` 帧）| 看波动形态 |
| `stat unitcriticalpath` | 关键路径耗时 | 判断是哪个线程在等 |
| `stat raw` | 切换 graph/unitmax 用**原始值**而非平滑值 | 分析细节 |

**`stat unitmax` 的实现（`UnrealClient.cpp` 第 476-489 行）：**
```cpp
if (bShowUnitMaxTimes) {
    for (int32 MaxIndex = 0; MaxIndex < NumberOfSamples; MaxIndex++) {
        if (Max_RenderThreadTime < RenderThreadTimes[MaxIndex]) Max_RenderThreadTime = RenderThreadTimes[MaxIndex];
        if (Max_GameThreadTime   < GameThreadTimes[MaxIndex])   Max_GameThreadTime   = GameThreadTimes[MaxIndex];
        ...
    }
}
```

**→ 它扫整个环形缓冲取最大值。**卡顿帧不会因为后续帧而消失。**
**→ 判断「有没有卡顿」用 `unitmax`，判断「平均多少」用 `unit`。**

---

## 三、帧预算：引擎怎么定义「好」「差」「卡」

**源码：`Runtime/Engine/Private/Performance/EnginePerformanceTargets.cpp`**

```cpp
t.UnacceptableFrameTimeThreshold  默认 50.0 ms   // 超过 = 红色
t.TargetFrameTimeThreshold        默认 33.9 ms   // 低于 = 绿色，之上 = 黄/红
t.HitchFrameTimeThreshold         默认 60.0 ms   // 卡顿帧的绝对阈值
t.HitchDeadTimeWindow             默认 200.0 ms  // 两次卡顿记录的最小间隔
t.HitchVersusNonHitchRatio        默认 1.5       // 比上一帧慢多少倍算卡顿
```

**本项目实测（控制台 `t.XXX` 回显）：**
```
t.HitchFrameTimeThreshold = "60"      LastSetBy: Constructor
t.HitchDeadTimeWindow     = "200"     LastSetBy: Constructor
t.HitchVersusNonHitchRatio= "1.5"     LastSetBy: Constructor
t.TargetFrameTimeThreshold= "33.9"    LastSetBy: Constructor
```

### 3.1 🔴 发现一个值得注意的不一致

**引擎默认目标帧时间是 **33.9 ms ≈ 30 fps**，不是 16.6 ms。**

**而本项目 `AGENTS.md` 的帧预算目标是 **16.6 ms（60 fps）**。**

**→ 如果不在项目里改 `t.TargetFrameTimeThreshold`，
`stat unit` 会把 30 fps 显示成**绿色**，而项目实际目标是 60 fps。**

**→ 这会导致「看起来是绿的，其实不达标」。**

**改法（待做，本轮未改）：**
```ini
; DefaultEngine.ini
[ConsoleVariables]
t.TargetFrameTimeThreshold=16.6
t.UnacceptableFrameTimeThreshold=33.3
```

### 3.2 卡顿的精确判定

**`GetHitchToNonHitchRatio()`（第 77 行）：**
```cpp
const float MaximumRatio = GetHitchFrameTimeThresholdMS() / GetTargetFrameTimeThresholdMS();
return FMath::Clamp(GHitchVersusNonHitchMinimumRatioCVar.GetValueOnGameThread(), 1.0f, MaximumRatio);
```

**按默认值算：`Clamp(1.5, 1.0, 60/33.9 = 1.77)` = **1.5**。**

**→ 一帧要同时满足「≥ 比上一帧慢 1.5 倍」**且**「≥ 60 ms」才算 hitch。**

---

## 四、🔴 实测：`stat` 面板**抓不到**

**这是本篇最实用的发现。**

**试了两条路，都失败：**

| 尝试 | 结果 |
| --- | --- |
| `CaptureViewport` + `bShowUI: false` | **截图里没有任何 stat 面板** |
| `CaptureViewport` + `bShowUI: true` | **两张图**完全一样**，仍然没有** |

**原因：`stat` 是 `FStatUnitData::DrawStat` 画进 viewport 的 **Canvas 层**，
而 `CaptureViewport` 走的是**场景渲染**路径，不包含 Canvas/HUD 覆盖层。**

### 4.1 Python 也读不到

**探过：**
```
unreal.Engine                     → AttributeError: module 'unreal' has no attribute 'Engine'
unreal.get_console_variable       → False
unreal.ConsoleVariable            → False
SystemLibrary / GameplayStatics   → 只有 get_real_time_seconds / get_accurate_real_time
```

**→ 没有 Python 可见的帧时间读取接口。**

### 4.2 所以在本机怎么读帧时间

| 方法 | 可用性 | 代价 |
| --- | --- | --- |
| `stat unit` 面板 + 人看 | ✅ | 要人盯着 |
| `CaptureViewport` | ❌ 无 Canvas 层 | — |
| Python API | ❌ 无接口 | — |
| **整屏截图（`RunGame.ps1`）** | ✅ 但**会抢焦点 / 关编辑器** | **规则 2 禁止日常用** |
| **`stat startfile` → Insights** | ✅ **唯一可自动化的路径** | 要装/开 Insights（待验证）|

**⚠️ 这条结论很重要：**
> **在本项目的自动化流程里，性能数据只能通过**抓 trace**得到，
> 不能通过截图得到。**
>
> **所以「看 `stat` 面板」这件事本身是**人**的工作，不是我的。**

---

## 五、性能排查清单

### 5.1 「哪一项是瓶颈」

| 现象 | 判断 |
| --- | --- |
| **Game 最高** | 游戏线程：蓝图/脚本/物理/AI/组件 Tick |
| **Draw 最高** | 渲染线程：Draw call 数、材质复杂度、阴影 |
| **GPU 最高** | GPU：过绘制、分辨率、Lumen 质量、后处理 |
| **Frame 远高于三者** | **在等**：VSync、`t.MaxFPS`、GPU 同步 |
| RHIT 明显 | RHI 线程：命令提交瓶颈（少见）|

**判断原则：**
> **Frame 应该 ≈ max(Game, Draw, GPU)。
> 如果 Frame 明显大于这三者，说明不在算，在**等**。**

### 5.2 「有卡顿但平均好看」

**用 `stat unitmax`，不用 `stat unit`。**

**`unit` 是 EMA，卡顿被 0.9 的衰减吃掉。
`unitmax` 扫环形缓冲取最大值，卡顿帧不会消失。**

### 5.3 「改了设置但数字没变」

**检查 `LastSetBy`：**
```
t.TargetFrameTimeThreshold = "33.9"   LastSetBy: Constructor
```
**`LastSetBy` 会告诉你是 Constructor / Scalability / Console / Code / Scalability。**
**如果是 `Constructor`，说明你改的 ini 没生效（被代码默认值覆盖）。**

**这一招和日志那篇的 `log list` 完全同源：
**先看"当前值是什么、谁设的"，再改。**

---

## 六、待做

| 事项 | 为什么 |
| --- | --- |
| 把 `t.TargetFrameTimeThreshold` 改成 16.6 | 项目目标是 60 fps，默认 33.9 会显示成绿 |
| 验证 `stat startfile` → Insights 的自动化路径 | 目前唯一可自动化的性能采集 |
| 量一次本项目在编辑器里的 Frame/Game/Draw/GPU | 还没量过 |

**⚠️ 按用户要求本轮**只读不改**，配置和 C++ 一字未动。**

---

## 七、本篇依据的源码位置

| 事实 | 文件 | 行 |
| --- | --- | --- |
| 五个 unit 数字 + EMA 平滑 | `UnrealClient.cpp` | 381-411 |
| 注册成 STAT_Unit* | 同上 | 434-438 |
| `unitmax` 扫环形缓冲 | 同上 | 476-489 |
| `stat raw` 切换原始值 | 同上 | 455-464 |
| 注册 `Unit/UnitMax/UnitGraph/UnitCriticalPath` | `UnrealEngine.cpp` | 19272-19275 |
| 帧预算三个阈值默认值 | `EnginePerformanceTargets.cpp` | 10-30 |
| `TargetFrameTimeThreshold` 默认 33.9 | 同上 | 21-27 |
| hitch 比值 clamp | 同上 | 77 |
