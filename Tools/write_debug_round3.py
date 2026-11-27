"""Append the third debugging round.

    python Tools/write_debug_round3.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 60. 调试系列第 3 轮：**性能剖析 — stat 是平滑值，而且抓不到**（2026-11-26 45:00）

### 一、`stat unit` 那几行数字的真身

**源码 `UnrealClient.cpp` 381-411：**
```cpp
FrameTime      = 0.9 * FrameTime      + 0.1 * RawFrameTime;
GameThreadTime = 0.9 * GameThreadTime + 0.1 * RawGameThreadTime;
RenderThreadTime = 0.9 * RenderThreadTime + 0.1 * RawRenderThreadTime;
RHITTime       = 0.9 * RHITTime       + 0.1 * RawRHITTime;
GPUFrameTime[i]= 0.9 * GPUFrameTime[i]+ 0.1 * RawGPUFrameTime[i];
```

**🔴 五个数字全是 **EMA 平滑**。**

**→ 一帧突然 200ms，如果正常值 16ms，面板只涨到约 34ms，下一帧就开始回。**

**→ **`stat unit` 天生看不见单帧卡顿。**这是设计，不是 bug。**

### 二、要看卡顿必须用 `stat unitmax`

| 命令 | 内容 |
| --- | --- |
| `stat unit` | EMA 平滑值 |
| **`stat unitmax`** | **环形缓冲里的最大值** ← 卡顿不会消失 |
| `stat unitgraph` | 时间曲线 |
| `stat unitcriticalpath` | 关键路径 |
| `stat raw` | 原始未平滑值 |

**`unitmax` 实现（`UnrealClient.cpp` 476-489）：扫 `NumberOfSamples` 帧取每通道最大值。**

### 三、帧预算默认值 —— 有个不一致

**实测控制台回显：**
```
t.HitchFrameTimeThreshold  = "60"      LastSetBy: Constructor
t.HitchDeadTimeWindow      = "200"     LastSetBy: Constructor
t.HitchVersusNonHitchRatio = "1.5"     LastSetBy: Constructor
t.TargetFrameTimeThreshold = "33.9"    LastSetBy: Constructor
```

**🔴 `t.TargetFrameTimeThreshold` 默认 **33.9 ms ≈ 30 fps**，不是 60 fps。**

**而本项目 `AGENTS.md` 目标是 **16.6 ms（60 fps）**。**

**→ **不在项目里改这个值，`stat unit` 会把 30 fps 显示成绿色。**
**→ 「看起来是绿的，其实不达标」。**

**待做（未改）：**
```ini
[ConsoleVariables]
t.TargetFrameTimeThreshold=16.6
t.UnacceptableFrameTimeThreshold=33.3
```

### 四、🔴 实测：`stat` 面板**抓不到**

| 尝试 | 结果 |
| --- | --- |
| `CaptureViewport` + `bShowUI:false` | 截图中**无 stat 面板** |
| `CaptureViewport` + `bShowUI:true` | **两张图一模一样**，仍无 |

**原因：`stat` 画在 viewport 的 **Canvas 层**，
`CaptureViewport` 走**场景渲染**路径，不含 Canvas/HUD。**

**Python 也读不到（探过）：**
```
unreal.Engine                → AttributeError
unreal.get_console_variable  → False
SystemLibrary/GameplayStatics → 只有 get_real_time_seconds
```

**→ 本机读帧时间的唯一自动化路径是 `stat startfile` → Insights（待验证）。**

**→ **「看 stat 面板」是**人**的工作，不是我的。** 这条要记住。

### 五、`LastSetBy` 是个好用的排查线索

```
t.TargetFrameTimeThreshold = "33.9"   LastSetBy: Constructor
```

**`LastSetBy` 会告诉你是 Constructor / Scalability / Console / Code。
如果是 Constructor，说明 ini 里的设置没生效（被代码默认值覆盖）。**

**这和日志那篇的 `log list` 同源：**先看「当前值是什么、谁设的」，再改。**

### 六、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-PERF.md`** | stat 家族 + 帧预算 + 抓不到的实测 |
| `Tools/practice_stat_commands.py` | 开各 stat 面板 + 查询 CVar |
| `Tools/probe_frame_time_api.py` | 探 Python 有没有帧时间接口 |

**截图证据：`Saved/shot_stat_unit.png` / `Saved/shot_stat_ui.png`（都是无 stat 面板的）**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **内存与泄漏** —— `memreport`、`obj list`、引用链、GC |
| 2 | 渲染调试 —— CVar、VisualizeBuffer、GPU 抓帧 |
| 3 | 蓝图与脚本调试 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 60." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 60; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
