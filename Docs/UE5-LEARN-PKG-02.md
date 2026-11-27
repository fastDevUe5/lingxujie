# UE5 学习 · 打包与优化（第二块）：编辑器里量性能，量到的是睡眠

> **这一块是一次**失败实验**，但失败本身给出了一个关键方法论结论：**
> **编辑器 PIE 里的帧时间被「睡眠」主导，用它做优化对比是**无效的**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、实验设计

**目标：量出 Lumen GI 在同一场景里的性能代价。**

**方法：同一场景、同一相机、同一帧数（120 帧），只改 `r.Lumen.DiffuseIndirect.Allow`。**

```
stat dumpave -start -ms=0 -num=120
```

---

## 二、🎯 结果：两组数字几乎一样

| 设置 | GameThread | FrameTime | FrameTime 子项（实际工作）|
| --- | --- | --- | --- |
| **Lumen 关** | 8.468 ms | 8.464 ms | **0.404 ms** |
| **Lumen 开** | 8.360 ms | 8.357 ms | **0.428 ms** |

**→ 帧时间：Lumen **开**反而快 0.1 ms —— 在噪声里。
→ 实际 CPU 工作：Lumen 开多 **0.024 ms**（0.428 − 0.404）。

**→ 一个只值 0.024 ms 的差异，配在 8.4 ms 的帧时间里，被完全淹没了。**

---

## 三、🔴 为什么 —— 8.4 ms 里只有 0.4 ms 是工作

**同一份 dump 里，`CPU Stall` 占了绝大部分：**

```
LogStats:  8.571ms  -  CPU Stall - Wait For Event - STAT_EventWait
LogStats:  8.375ms  -  CPU Stall - Sleep - STAT_Sleep
LogStats:  8.356ms  -  CPU Stall - Sleep - STAT_Sleep
LogStats:  8.339ms  -  CPU Stall - Wait For Event - STAT_EventWait
...
LogStats:  8.360ms  -  Thread_4728_0 - GameThread
LogStats:    8.357ms -  FrameTime - STAT_FrameTime
LogStats:      0.428ms -  FrameTime - STAT_FrameTime     ← 真正的帧工作
```

**→ 游戏线程 8.36 ms 里，**8.36 − 0.428 ≈ 7.94 ms 是 Stall（睡眠/等待）**。**

**→ 帧率约 **119.6 FPS** —— 看上去像被钳制在 120。**

---

## 四、🔴 但**不是**帧率钳制

**我查了钳制相关的 CVar（✅ 实测）：**

```
t.MaxFPS              = "0"    LastSetBy: Scalability   ← 已经是 0，不钳制
r.VSync               = "0"    LastSetBy: SystemSettingsIni  ← 已经关
t.IdleWhenNotForeground = "0"  LastSetBy: Constructor
r.OneFrameThreadLag   （未报错）
```

**显式再设一遍 `t.MaxFPS 0` / `r.VSync 0` 后重测 —— **还是 8.3–8.5 ms，Stall 还是 8.3 ms。****

**→ 不是钳制。是**编辑器在主动休眠**，避免空转烧 CPU。**

**→ 这是编辑器 PIE 的固有行为，不是场景的性能。**

---

## 五、🎯 方法论结论

**在编辑器 PIE 里做优化对比时：**

| 做法 | 有效性 |
| --- | --- |
| 比较**帧时间**（FrameTime）| ❌ **无效** —— 被睡眠主导 |
| 比较 **FrameTime 的子项**（实际工作）| ✅ **有效** —— 这一项会随负载变 |
| 比较 `stat unit` 的 GPU 项 | 需另找读取途径（本次没拿到 GPU 总时间）|

**→ 正确做法：**
1. **先确认这一帧是「工作主导」还是「睡眠主导」**
   —— 看 `CPU Stall` 占了 FrameTime 的多大比例
2. **睡眠主导时，量工作子项，不要量帧时间**
3. **要量真实帧时间，必须跳出编辑器**（打包版 / `-game` 独立运行）

---

## 六、这次实验的**唯一有效数字**

**FrameTime 子项：0.404 ms（关）vs 0.428 ms（开）**

**→ Lumen GI 在这个场景里的 CPU 侧代价约 **0.024 ms**。**

**⚠️ 这个数字的边界：**
- 场景是 10 个 actor 的黑盒子，不是 116 个 actor 的兰州街景
- 只反映 **CPU 侧**，不含 GPU
- Lumen 的主要代价在 GPU，而 GPU 总时间**本次没量到**

**→ 所以不能据此说「Lumen 很便宜」。只能说「在这个 CPU 场景里代价很小」。**

---

## 七、这一块学到什么

**1. 🔴 编辑器 PIE 的帧时间是**睡眠主导**的，不能用来做优化对比。**
8.36 ms 里 7.94 ms 是 Stall。

**2. 🔴 「帧率刚好是 120」不等于「被钳制」—— 查了 `t.MaxFPS` 和 `r.VSync` 都是关的。**

**3. 🎯 判据：看 `CPU Stall` 占 FrameTime 的比例。**
比例高 → 睡眠主导 → 量工作子项。

**4. 优化的第一步不是改参数，是确认**当前帧是工作主导还是等待主导**。**
文档说要先分清 CPU/GPU 瓶颈 —— **这一步还得加一条：先分清工作还是等待。**

**5. 一个只值 0.024 ms 的差异，在 8.4 ms 的噪声里是测不出来的。**
**要么放大差异，要么换测量口径。**

---

## 八、更正

| 之前 | 现在 |
| --- | --- |
| 「`stat dump*` 能拿到帧时间，可以做优化对比」 | ⚠️ **能拿到，但编辑器里拿到的是睡眠时间** |
| 「帧率 119.6 可能是被钳制」 | ❌ **不是，`t.MaxFPS=0` / `r.VSync=0` 都关着** |

---

## 九、下一块的两个方向

**A. 换测量口径** —— 量 FrameTime 的**工作子项**（已知有效），
在练习关卡里对比不同设置（阴影质量、VSM、TSR 等）。

**B. 跳出编辑器** —— 跑打包版或 `-game` 独立运行才能量到真实帧时间。
**但这需要关编辑器（`Package.ps1` 明写 Live Coding 互斥体），上一轮已问过，未获答复。**

**→ 我倾向 A** —— 不需要关编辑器，而且刚刚证明了工作子项是有效的。

---

## 十、状态

**⚠️ 编辑器已恢复：主关卡 116 actor、视口复位、退出 PIE。**
