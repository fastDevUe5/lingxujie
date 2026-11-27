# UE5 学习 · 补读（九）：TSR —— 25% 分辨率的重建质量，以及一个测不出来的代价

> **85 KB、37 节，是本系列读过的最大一篇。**
> **实测部分：25% 屏幕百分比下，TSR 重建的画面和原生相差不大。**
> **但那个最重要的代价（后处理在显示分辨率上跑）**量不到**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档结构（37 节，85.2 KB）

**前半是使用与调试：**
```
Supported Platforms / TSR Scalability
Understanding the Caveats of Temporal Accumulation of Details
Upscaling GPU Cost / Anti-Aliasing Scalability Group
**Hidden GPU Costs of Temporal Upscaling**     ← 最重要
Optimizing Motion Blur with TSR
Tools for Debugging TSR
  Visualize Temporal Upscaler Inputs and Outputs
  Visualize TSR / DumpGPU Viewer
Console Variables
```

**后半是原理：**
```
The Components of TSR
TSR History / TSR Nyquist-Shannon History
Parallax Disocclusion
Animation World Position Offset
Shading Rejection
TSR and Translucency / Translucency Pass / Outputting Translucency Velocities
TSR with Post Process Materials
Spatial Anti-Aliaser
TSR Flickering Temporal Analysis / Moire Patterns
Temporal History's Causality Dilemma
Flickering Luminance Measurement
Effects of Frame Rate
Anti-Aliasing with Movement and Changing Resolution
Materials with Pixel Animation
History Resurrection / Reprojection Field
Troubleshooting Ghosting Issues
FAQ
```

---

## 二、🎯 文档最重要的论断：**隐藏的 GPU 代价**

**原文：**
> **「TSR, along with any other temporal upscaler, happens **in the middle of the
> post processing render chain**.
> This means that passes, such as **motion blur and tonemapper**,
> run **after TSR is no longer scaling with the primary screen percentage**.
>
> In the absence of a secondary screen percentage with a spatial upscaler
> (`r.SecondaryScreenPercentage.GameViewport`),
> the output resolution of TSR runs at the **display resolution** rather than the
> **rendering resolution** set by screen percentage.
>
> Because of this and TSR being enabled by default,
> there is a lot of effort focused on reducing the hidden temporal upscaling costs
> of passes that happen after TSR.」**

**→ 意思很清楚：**
1. **TSR 在**后处理链的中间**工作**
2. **它之后的 pass（运动模糊、色调映射）跑在**显示分辨率**上，不是渲染分辨率**
3. **所以「屏幕百分比 25%，后处理也只算 25%」是**错的****
4. **`r.SecondaryScreenPercentage.GameViewport` 是对策**

**→ 这是一个**反直觉的性能陷阱**：降低屏幕百分比不会线性地省掉所有 pass 的代价。**

---

## 三、✅ 本项目的活值

```
r.AntiAliasingMethod                    = 4        ← TSR
r.ScreenPercentage                      = 0        ← 自动（100%）
r.TSR.History.ScreenPercentage          = 200      Scalability
r.SecondaryScreenPercentage.GameViewport= 0        Constructor
r.TemporalAA.Upsampling                 = 1        Constructor
r.TSR.ShadingRejection.Flickering       = 1        Scalability
r.TSR.AsyncCompute                      = 2        Constructor
r.MotionBlurQuality                     = 4        Scalability
```

**→ 项目用的是 **TSR**（方法 4），屏幕百分比自动。**

**源码核实（`RendererSettings.h:195-199`）枚举：**
```
FXAA = AAM_FXAA
MSAA = AAM_MSAA
TSR  = AAM_TSR
```

---

## 四、🎯 实测：25% 屏幕百分比的重建质量

### 4.1 测量方法的失败

**先试了「平均梯度」作为锐度指标：**
```
屏幕百分比 100  平均梯度 1.793
屏幕百分比 50   平均梯度 2.077   ← 反而更高
屏幕百分比 25   平均梯度 1.705   ← 更低
```

**→ **50% 比 100% 更锐**？不合理。**

**→ 结论：梯度指标在 TSR 的**时域累积 + 自适应锐化**下不可靠。
→ **这条路放弃，改用看图。**

### 4.2 看图（✅ 有效）

![屏幕百分比 100%（原生）](</C:\Users\tk\Desktop\lingxujie\Saved\shot_sp_100.png>)

![屏幕百分比 25%（1/16 像素）](</C:\Users\tk\Desktop\lingxujie\Saved\shot_sp_25.png>)

**对比观察：**

| | 100% | 25% |
| --- | --- | --- |
| 物体边缘 | **锐利** | 略柔，但**无锯齿** |
| 天空渐变 | 平滑 | 平滑（几乎一样） |
| 圆柱分色边界 | 清晰 | 略软 |
| 锥体边缘 | 锐 | 略柔，无台阶 |
| 整体可用性 | — | **完全可用** |

**→ 1/16 的像素量，重建出的画面**和原生相差不大**。
→ 这就是 TSR 的全部意义：**用四分之一的渲染分辨率拿到接近原生的画质。**

---

## 五、🔴 那个「隐藏代价」量不到

**按文档，25% 屏幕百分比下：**
- 几何/材质 pass 在 25% 分辨率跑 ✅ 省了
- **运动模糊、色调映射在**100% 显示分辨率**跑** ❌ 没省

**→ 要验证这一点，需要**分别测量这些 pass 的 GPU 时间**。
→ **而 GPU 时间在本环境里读不到**（见 PKG-03：`stat gpu` 不写日志、`r.GPUStats.Enabled` 不存在）。**

**→ 所以这一条只能**记录为「文档说的、我验证不了」**，不能写成「实测」。**

**⚠️ 这是本系列反复出现的边界：读到的结论 ≠ 验证过的结论。**

---

## 六、这一篇学到什么

**1. 🎯 TSR 的核心价值：25% 分辨率 → 1/16 像素 → 画面几乎不变。**
（看图判断，因为梯度指标失效了）

**2. 🔴 最重要的性能陷阱：**TSR 之后的 pass 跑在显示分辨率上。**
**→ 「降低屏幕百分比省一切」是错的。**

**3. 🔴 「平均梯度」不能衡量 TSR 的锐度。**
时域累积 + 自适应锐化会让梯度指标失效。
**→ 有些量就是**没有便宜的代理指标**，必须看图或上工具。**

**4. 🔴 有些结论只能读到，验证不了。**
「隐藏 GPU 代价」需要 Insights/RenderDoc —— 本环境没有。
**→ 记录时要分清「文档说」和「我量到」。**

**5. 项目用 TSR（方法 4），参数全默认。**

---

## 七、更正

| 之前 | 现在 |
| --- | --- |
| 「屏幕百分比降低 → 整体线性省性能」 | ❌ **TSR 之后的 pass 仍跑显示分辨率** |
| 「边缘梯度能衡量锐度」 | ❌ **对 TSR 无效，实测 50% 比 100% 还高** |

---

## 八、还没做到

| 项 | 说明 |
| --- | --- |
| **验证「隐藏 GPU 代价」** | **需 Insights/RenderDoc，本环境做不到** |
| TSR vs TAA vs FXAA 的画面对比 | 只测了屏幕百分比，没切方法 |
| Ghosting / 闪烁的调试工具 | `Visualize TSR` 是屏幕可视化，读不到日志 |
| `r.TSR.AsyncCompute` 的 0/1/2/3 对比 | 没试 |
| 动态分辨率（`r.TSR.DynamicRes`） | 没试 |

---

## 九、状态

```
Docs/UE5-LEARN-READ-TSR.md   1 篇（共 32 篇 learn 文档）
补读进度：9 / 57
编辑器已还原：屏幕百分比 0（自动）/ VolumetricCloud 1 / 主关卡 116 actor / 视口复位
```

---

## 十、渲染域小结

**Lumen 系列 6 篇 + Nanite 2 篇 + VSM 1 篇 + 天空大气 2 篇 + 方向光 1 篇 + 后处理材质 1 篇 + TSR 1 篇 = 14 篇**

**渲染域剩下的高价值文档：**
- `reflections-captures.md`（20 KB）
- `lighting-environment.md`（索引 4.2 KB）
- `texture-asset-editor.md`（30 KB）
- `material-editor-guide.md`（7.6 KB）

**→ 下一篇选 `reflections-captures.md`（反射与捕获），把渲染的闭环补完。**
