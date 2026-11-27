# 渲染实操一：Lumen 参数、官方素材、以及"没有变化"的三种含义

> **这一篇是渲染域从"读配置"走向"动手"的第一块。全部数字来自本机 5.8.4 实测，图片在
> `Saved/learn_ab*`。**
>
> **最重要的一条：`r.LumenScene.Visualize` 和 `r.LumenScene.Radiosity.Enable` 这两个名字根本
> 不存在 —— 我把"命令不存在"当成了"没有视觉效果"，差点写进结论。**
>
> **日期：2026-11-26 · 练习场地：Fab 免费包 KHS 建春门自带 Demo 关卡**

---

## 一、为什么换场地

**墨香是 2003 年的客户端，贴图 64×64、模型面数低、光照烘焙在资源里。
在它上面调 Lumen，调出来的"好看"不代表渲染器对了。**

**所以本轮起，渲染/材质/性能的实操全部挪到官方免费素材上：**

| 项 | 值 |
| --- | --- |
| 场地 | `/Game/GeonchunmunComplex/Maps/Demo_GeonchunmunComplex` |
| 来源 | Fab 免费包 KHS Geonchunmun Complex（Korea Heritage Service，CC-BY） |
| 规模 | **1159 个 actor**：1131 StaticMesh / 19 Decal / 4 其它 |
| 灯光 | DirectionalLight + SkyLight + SkyAtmosphere + **VolumetricCloud** + ExponentialHeightFog |
| 观察位 | `5830, -1382, 570` yaw `169.5` pitch `4.4`（正对城门） |

**这个关卡的价值是：光照、材质、贴图都是包作者按 PBR 流程做的，改渲染参数能看到该看到的变化。**

---

## 二、测量管道（可复用）

```
Tools/learn_practice.py     打开官方 Demo 关卡 / 恢复工程关卡 + 默认视角
Tools/learn_render_one.py   读 Saved/learn_one.json，执行复位 + 变体 CVar 命令
Tools/learn_ab_run3.ps1     逐个变体：跑脚本 → 回读 CVar → MCP 抓图 → 存 PNG
Tools/learn_diff_all.py     逐张和基线比，控制组当噪音地板
Tools/learn_diff_regions.py 3×3 分块，定位差异在画面哪一块
Tools/learn_cvar_read.py    把回读 JSON 压成"变体 → 旋钮 → 当时的值"
```

**关键设计：每一轮都拍一张"控制组"（设置完全不变），它的差异就是噪音地板。
低于地板的变化，正确结论是"这个阈值下测不到"，不是"效果很小"。**

---

## 三、三个坑，每一个都改变了结论

### 3.1 `time.sleep` 会卡住游戏线程 —— 循环里只拍得到最后一张

**第一版脚本在一个 python 循环里请求 9 张高分辨率截图，结果磁盘上只有 1 个文件（最后那张）。**

**原因：编辑器里的 Python 跑在游戏线程上，`time.sleep` 睡的就是要出图的那条线程；
每请求一张都取消上一张，脚本返回后只有最后一张能渲染。**

**改法：一个变体一次运行，抓图放到脚本返回之后（由 MCP 从外部抓）。**

### 3.2 动态天空让"整帧像素差"失去分辨力

**第一轮（云开着）控制组 vs 基线：23.48% 像素不同。**
**分块一看就清楚了：**

| 区域 | 变化 |
| --- | --- |
| 天空带（上 1/3） | **56.0%** |
| 下方带（城楼+地面） | 7.2% |
| 最下排三块 | **0.0–0.0%** |

**体积云在飘，天空整片在动；城楼和地面是稳的。**
**→ 冻结 `r.VolumetricCloud 0` 后，控制组降到 **0.03%**。**

**结论：场景里有任何逐帧动画（云、粒子、草木风摆、时序抖动）时，整帧像素差必须先冻结它们，
否则测到的是动画，不是参数。**

### 3.3 复位清单漏项 —— 三张图完全相同，我差点判成"引擎单向"

**第二轮里 `ab_diffuse_off` / `ab_reflections_off` / `ab_spg_ds4` 三张和基线的差异都是
**17.56%、误差 12 像素**。两两比对**完全相同（0.00–0.03%）**。**

**我第一反应是"Lumen GI 关掉后引擎不会恢复"。**
**实际原因是我的复位清单没写 `r.Lumen.DiffuseIndirect.Allow`：GI 被第一个变体关掉后，
后面每个变体的"复位"都没把它打开，于是三张图都是"GI 关着"的样子。
连重载关卡都没用 —— CVar 是全局的，重载世界不会重置它。**

**→ 复位清单必须写全每个变体碰过的旋钮（两个方向都写），并且最后用一张"复位后截图"
证明复位真的发生了。现在这张自检图是 `ab_after_restore.png`：0.02%，等于基线。**

**教训和调试系列里那几次是同型：**把"我的工具/我的流程给出的结果"当成了"引擎的行为"。****

---

## 四、最终数据（云冻结，噪音地板 0.03%）

**基线：`Saved/learn_ab4/ab_base.png`；1180×688；阈值 8/255。**

| 变体 | 命令 | 变化像素 | 平均通道差 | 结论 |
| --- | --- | --- | --- | --- |
| 控制组 | 无 | **0.03%** | 0.347 | 噪音地板 |
| 复位自检 | 无（复位后） | **0.02%** | 0.240 | 复位可信 |
| **GI 关** | `r.Lumen.DiffuseIndirect.Allow 0` | **17.55%** | **4.018** | 本场景最大视觉贡献者 |
| VSM 关 | `r.Shadow.Virtual.Enable 0` | **1.17%** | 0.604 | 真实可见，主要在地面阴影 |
| AA 关 | `r.AntiAliasingMethod 0` | **0.99%** | 0.735 | 真实可见，边缘锯齿 |
| Radiosity 关 | `r.LumenScene.Radiosity 0` | **0.04%** | 0.598 | 此机位测不到 |
| 反射关 | `r.Lumen.Reflections.Allow 0` | **0.02%** | 0.367 | 此机位测不到 |
| 探针降采样 ×4 | `r.Lumen.ScreenProbeGather.DownsampleFactor 4` | **0.02%** | 0.347 | 此机位测不到 |

**每个变体在拍摄那一刻的 CVar 值都回读记录在
`Saved/learn_ab4/cvar_readback.txt`，所以"设置没生效"和"生效了但看不出来"是分开的：**

```
ab_gi_off          r.Lumen.DiffuseIndirect.Allow   value=0
ab_reflections_off r.Lumen.Reflections.Allow       value=0
ab_spg_ds4         r.Lumen.ScreenProbeGather.DownsampleFactor value=4
ab_vsm_off         r.Shadow.Virtual.Enable         value=0
ab_aa_none         r.AntiAliasingMethod            value=0
ab_radiosity_off   r.LumenScene.Radiosity          value=0
```

### 4.1 三个"测不到"不是三个"没效果"

| 变体 | 为什么测不到 | 下一步怎么证 |
| --- | --- | --- |
| 反射关 | 这个场景表面是粗石头/土，粗糙度超出可追踪范围，屏幕空间反射贡献接近 0 | 放一个金属球再看；或 `r.Lumen.Reflections.MaxRoughnessToTrace 1` |
| Radiosity 关 | 天空光直射主导，表面缓存之间的二次弹射在这个机位占比极小 | 换近景/降低天光，或看 `r.LumenScene.Radiosity.VisualizeProbes 1` |
| 探针降采样 ×4 | 间接光梯度在整帧里太缓，降采样看不出来 | 贴近墙面拍局部；或 ×8 再测 |

**这三条的共同点：**"没测到"只说明**这个机位、这个阈值**下没有变化，
不说明机制不存在。**这是"数字真、含义错"的又一例。**

---

## 五、Lumen 自己的诊断视图（本轮最有用的发现）

**`r.Lumen.Visualize 1` 会把视口切成三块诊断视图：**

| 子视图 | 看什么 |
| --- | --- |
| Geometry Normals | 法线是否正常（紫蓝渐变 = 平顺；花斑 = 法线坏） |
| Reflection View (SWRT) | 软件光追看到的反射源 |
| **Lumen Scene** | **Pink = 该处缺失 Surface Cache 覆盖；Yellow = 其它告警** |

**实测图：`Saved/learn_ab3/ab_lumen_visualize.png`**

**这张图上城楼与地面出现大片 Pink —— 说明这个免费包的部分网格没有被 Lumen 的
Surface Cache 覆盖（卡片生成失败或半径不足）。这不是配置错，是资源层面的问题，
正是"先看渲染器怎么理解场景，再谈调参"的那一步。**

**用法：性能或观感异常时，先开这个视图确认"Lumen 眼里有没有这个物体"，
再去调质量档 —— 否则会把"资源没进场景"当成"参数调不对"。**

**注意：这个视图会改变视口状态，把 `r.Lumen.Visualize` 设回 0 后视口不一定立刻复原；
它必须放在一组 A/B 的最后一个，或者拍完重开视口。这是本轮第二次踩 "开关改了视图模式"，
和 gotcha #65（CaptureViewport 不改视口）属于同一类问题。**

---

## 六、更正清单（本轮自己错了三次）

| # | 当时的结论 | 实际 | 类型 |
| --- | --- | --- | --- |
| 1 | "三个旋钮没有视觉效果" | 其中两个名字根本不存在（`r.LumenScene.Visualize`、`r.LumenScene.Radiosity.Enable`） | **把命令不存在当成没效果** |
| 2 | "Lumen GI 关掉后引擎不恢复" | 我的复位清单漏了 `r.Lumen.DiffuseIndirect.Allow` | **把自己的流程缺陷当成引擎行为** |
| 3 | "整帧像素差可以判断渲染改动" | 云没冻结时噪音 23%，远大于真实改动 | **验证方法本身没有分辨力** |

**三条都能用同一句话防：**先找一个能推翻当前解释的独立观察。
本轮的第 3 条就是"3×3 分块"和"两两比对"推翻的。**

---

## 七、新增可复用工具

| 工具 | 作用 |
| --- | --- |
| `Tools/learn_practice.py` | 切到官方 Demo 场地 / 切回工程关卡并复位视角 |
| `Tools/learn_render_one.py` | 应用一组 CVar（复位 + 变体），供外部驱动 |
| `Tools/learn_ab_run3.ps1` | **完整 A/B 驱动：复位 → 变体 → 回读 → 抓图 → 复位自检** |
| `Tools/learn_diff_all.py` | 逐张对基线 + 控制组当噪音地板 + 结论措辞 |
| `Tools/learn_diff_regions.py` | 3×3 分块定位差异区域 |
| `Tools/learn_cvar_read.py` | 回读 JSON → 变体/旋钮/值 一行一条 |
| `Tools/learn_dirty.py` | 切关卡前报告脏包（避免丢未保存的东西） |

---

## 八、下一轮（渲染域还没做完的）

| 优先级 | 实验 | 为什么 |
| --- | --- | --- |
| 1 | **给三个"测不到"各补一个决定性实验**（金属球/近景/×8） | 把"此机位测不到"变成"机制确认" |
| 2 | **这些开关的帧时间代价** | 目前只有像素差，没有毫秒数 |
| 3 | Lumen 质量档（`r.Lumen.ScreenProbeGather.RadianceCache` 等）在**性能**上的台阶 | 学会按预算调，而不是按好看调 |
| 4 | 后处理（曝光/ Bloom / AO）同法实测 | 渲染域的后半 |

**⚠️ 性能数字需要 trace 或 stat 面板读数。`stat` 面板抓不到的问题本轮没碰，
下一轮用"整窗截图"或 trace 解决。**
