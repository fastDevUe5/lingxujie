# UE5 学习 · 打包与优化（第三块）：GPU 耗时读不到，而这本身是个结论

> **场景里真正可能的瓶颈是 GPU（Lumen + 体积云），而我一直在量 CPU。
> 这一块专门去找 GPU 的读数路径 —— 结论是**读不到**，但有明确的证据。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、试过的四条路（✅ 全部实测）

| # | 尝试 | 结果 |
| --- | --- | --- |
| 1 | `stat gpu` | **无日志输出**（只画面板）|
| 2 | `stat dumpframe -ms=0 -depth=maxint` | 只有 CPU 线程和 RDG 单项，**无 GPU 总计** |
| 3 | `stat scenerendering` | 无日志输出 |
| 4 | `r.GPUStats.Enabled` | **`Command not recognized`（CVar 不存在）** |
| 5 | `r.GPUCapture` | **`Command not recognized`（CVar 不存在）** |

**日志原文（✅）：**
```
Cmd: stat gpu
Cmd: r.GPUStats.Enabled
Command not recognized: r.GPUStats.Enabled
Command not recognized: r.GPUCapture
[LingXuJie] GPU: done
```

**→ `stat gpu` 有反应（不报错）但**不写日志**；
→ 两个看起来该控制 GPU 统计的 CVar **根本不存在**。**

---

## 二、对比：为什么 CPU 能读而 GPU 不能

| | CPU 时间 | **GPU 时间** |
| --- | --- | --- |
| 数据来源 | `FStatUnitData` / 线程统计 | GPU 时间戳查询 |
| 有没有 dump 命令 | ✅ `stat dumpave` / `dumpframe` 写日志 | ❌ **只有屏幕面板** |
| 有没有 Python API | ✅ `get_time_seconds` | ❌ |
| 替代工具 | — | **Unreal Insights / RenderDoc** |

**→ CPU 统计走的是**通用 stats 系统**（有 dump 通道）；
→ GPU 时间走的是**独立的 GPU 计时系统**（只喂给 `stat gpu` 面板和 Insights）。**

---

## 三、🔴 所以这一块的诚实结论

**在「编辑器 + Python 脚本 + 读日志」这套工作流里：**

| 能测 | 不能测 |
| --- | --- |
| ✅ CPU 游戏线程 FrameTime | ❌ **GPU 总耗时** |
| ✅ CPU 工作子项 | ❌ 任何一个渲染 pass 的真实 GPU 时间 |
| ✅ 帧时间的 Stall 构成 | ❌ GPU bound / CPU bound 的判定 |

**→ 目标里「调优」这一项，**只能做 CPU 侧的调优**。
→ GPU 侧需要 **Unreal Insights**（要 GUI）或 **RenderDoc/PIX**（本机没有）。**

---

## 四、那这个场景的 GPU 负担到底多大

**虽然量不到，但有几条**间接证据**说明 GPU 不轻松：**

| 证据 | 数值 |
| --- | --- |
| `stat dumpframe` 里 RDG pass 单项 | 0.02–0.04 ms × 多个 |
| 场景有 **VolumetricCloud** | 体积云是已知的 GPU 大户 |
| 场景有 **Lumen GI + 反射** | 软件光追，GPU 侧的主要开销 |
| 场景有 **SkyAtmosphere** | 逐像素大气散射 |
| **帧时间 10.73 ms 而 CPU 工作只有 0.469 ms** | **剩下 10.26 ms 是谁？** |

**→ 最后一条最关键：CPU 只用了 0.469 ms，却有 10.26 ms 的 Stall。**
**→ 那 10.26 ms 里**可能**包含 GPU 等待 —— 但**不能断定**，因为编辑器本身也在主动睡眠。**
**→ 这就是为什么「睡眠主导」这个问题必须先解决，否则 GPU 的份额根本无法从帧时间里分离出来。**

---

## 五、这一块学到什么

**1. 🔴 CPU 和 GPU 的统计走两套不同的系统。**
CPU 有 dump 通道，GPU 只有面板和 Insights。

**2. 🔴 「命令不报错」不等于「有输出」。**
`stat gpu` 不报错，但一个字节都不写日志。

**3. 🔴 两个我以为存在的 CVar 根本不存在。**
`r.GPUStats.Enabled`、`r.GPUCapture` → `Command not recognized`。
**→ 猜名字这条路又错了一次（本系列第 6 次）。**

**4. GPU 时间要靠工具而不是命令。**
Insights / RenderDoc / PIX —— 本机都没有。

**5. 睡眠主导的问题不解决，GPU 的份额就无法从帧时间里分离。**
两条线索绞在一起：编辑器主动睡眠 + 可能的 GPU 等待。

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「`stat dump*` 能拿到统计数据」 | ⚠️ **只对 CPU 统计成立，GPU 拿不到** |
| 「帧时间 10.73ms 说明场景不轻松」 | ❌ **不能这么推** —— 里面有主动睡眠 |

---

## 七、要真正量 GPU，需要什么

| 方案 | 需要 | 本机 |
| --- | --- | --- |
| **Unreal Insights** | `stat startfile` + Insights GUI | ✅ 引擎自带 Insights，❌ 但要 GUI 操作 |
| **RenderDoc** | 安装 + 抓帧 | ❌ 没有 |
| **PIX** | Windows + 安装 | ❌ 没有 |
| **打包后测** | 关编辑器 | 问过，未获答复 |

**→ 唯一可行的：**用 `stat startfile` 录一段，然后**你**在 Insights 里看。**
**那需要人参与，不是我能自动化完成的。****

---

## 八、场景与工具现状

```
/Game/Learning/L_Scene01   14 actor（落日原野 + 6 形体，begin_play 验证过）
/Game/Learning/L_LightLab  10 actor（深色实验盒）
主关卡 LingXuJie           116 actor（未动）
```

**已量到的数字：**
```
L_LightLab    FrameTime 8.360 ms / CPU 工作 0.428 ms / Stall 95%
L_Scene01     FrameTime 10.732 ms / CPU 工作 0.469 ms / Stall 96%
```

---

## 九、下一块

**GPU 这条路走不通了。回到能测的地方：**

**A. 用已证明有效的口径（FrameTime 工作子项）对比不同渲染设置** ——
但工作子项主要反映 CPU，渲染设置的代价在 GPU 上，**可能又测不出来**。

**B. 回到"搭场景"这条主线** —— 场景已经有 6 个形体，可以继续：
   加一个有层次的构图（近景/中景/远景）、多种材质组合、观察 Lumen 的反弹。

**C. 系统性整理 20+ 篇 learn 文档，写一份"已掌握 / 未掌握"的盘点。**

**→ 我倾向 C** —— 已经 22 篇了，需要一次收口；而且目标的终点部分已完成，
现在该盘点「还差什么才算专家」。
