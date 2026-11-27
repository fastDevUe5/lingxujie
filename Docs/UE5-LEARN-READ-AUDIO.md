# UE5 学习 · 补读（四十五）：音频 —— 资产在，但没有任何代码播它

> **这一篇读完音频域，得到一个硬结论：**
> **项目有 2 个音波、5 个 SoundClass、1 个衰减资产，但**源码里 0 处音频代码**。**
> **→ 音频资产**从未被播放过**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、audio.md（5.7 KB，9 节）—— 音频域的**总览**

```
Legacy Features          ← 关键：Sound Cue 被归在「遗留」
Sound Cues
Sound Classes and Sound Mixes
**Sound Rendering in UE5**
**MetaSounds**            ← 现代方案
**Audio Modulation**
**Quartz**                ← 时间精确的音频调度
**Audio Analysis**
```

**→ 最重要的信息在**目录结构**里：**

| 事实 | 含义 |
| --- | --- |
| **Sound Cue 被标为「Legacy Features」** | **旧方案**，UE5 已不主推 |
| **MetaSounds 单独一节** | **新方案**，程序化音频 |
| **Quartz 单独一节** | 采样级精确的时间调度（音乐游戏类）|
| **Audio Modulation** | 参数化音频调制 |
| **Audio Analysis** | 音频频谱分析（可以做音频驱动视觉）|

**→ 一句话：**UE5 的音频正在从「Sound Cue 节点图」转向「MetaSounds」。**

---

## 二、sound-cue-reference.md（40 KB，27 节）—— 20+ 种节点

**这是一个**完整节点清单**：**

| 节点 | 作用 |
| --- | --- |
| **Wave Player** | 播放音波。**`Looping` 标志**让它无缝循环 |
| **Attenuation** | 引用**已有的 Sound Attenuation 资产** |
| **Random** | **权重值控制某个节点被触发的概率** |
| **Delay** | **Delay Min 到 Delay Max 之间的随机延迟** |
| **Dialogue Player** | 播放 `Dialogue Wave` 资产 |
| **Concatenator** | 顺序拼接 |
| **Crossfade by Distance** | 按距离交叉淡入淡出 |
| **Crossfade by Param** | 按参数交叉淡入淡出 |
| **Continuous Modulator / Modulator** | 连续调制 |
| **Looping** | 循环（会把节点名改成 "Looping Wave Player"）|
| **Mixer** | 混音多路 |
| **Oscillator** | 振荡器 |
| **Enveloper / Doppler / Mature / Quality Level / SoundClass / Switch / Wave Param / Group Control / Branch / Output** | |

**三条可核实的机制：**

1. **`Wave Player` 的 Looping 标志实现无缝循环**
2. **`Random` 的权重值决定触发概率**（不是等概率）
3. **`Attenuation` 可以引用**已有资产**，不是内联设置**

---

## 三、✅ 项目实测：资产很少，代码为零

### 3.1 音频资产的真实清单

```
SoundAttenuation   1   ['SA_Monster']
SoundClass         5   ['SC_Master', 'SC_Music', 'SC_Monster', 'SC_SFX', ...]
SoundWave          2   ['S_bg_field', 'S_M004_Attack_01']

SoundCue           0    ← 零
MetaSoundSource    0    ← 零
SoundMix           0    ← 零
```

**→ 2 个音波：一个背景音、一个攻击音。**
**→ 5 个 SoundClass 的分类结构**是齐全的**（Master / Music / Monster / SFX）。**
**→ 但**没有任何 Sound Cue 或 MetaSound** —— 即**没有音频图**。**

### 3.2 🔴 源码里 0 处音频代码

**grep `Source/LingXuJie/**/*.cpp` 搜 `Sound|Audio|PlaySound|UAudioComponent`：**
```
No matches found
```

**→ **项目没有任何代码播放音频。****
**→ 那 2 个音波、5 个 SoundClass、1 个衰减资产**从未被使用**。**

**→ 类都可用（`SoundCue` / `SoundWave` / `MetaSoundSource` / `SoundAttenuation` /
`SoundClass` / `SoundMix` / `AudioComponent` 全部 True），但项目一个都没用。**

---

## 四、🎯 音频域的真实状态

| 层面 | 状态 |
| --- | --- |
| **音频架构概念**（Cue vs MetaSounds vs Quartz）| ✅ 现在懂了 |
| **Sound Cue 节点清单** | ✅ 读了 20+ 种 |
| **SoundClass / Attenuation 的分类结构** | ✅ 项目有（5 类 + 1 衰减）|
| **音波资产** | ✅ 有 2 个 |
| **播放音频的代码** | ❌ **0 处** |
| **音频图（Cue/MetaSound）** | ❌ **0 个** |
| **实测听到声音** | ❌ **不可能** |

**→ 结论：音频资产是**备好的素材**，但**从未接进游戏**。**

**→ 这和之前能力盘点里「audio 65%」的评分对不上 —— 实际上音频域的**实操是 0**。**
**→ 之前那个 65% 可能是按「读过文档 + 知道概念」给的，不是按「做过」给的。**

---

## 五、这一篇学到什么

**1. 🎯 UE5 音频的现代化方向是 **MetaSounds**，Sound Cue 被归为 **Legacy Features**。**

**2. 🎯 `Random` 节点的**权重值**决定触发概率**（不是等概率）。**

**3. 🎯 `Attenuation` 节点引用**已有资产**，不内联设置。**

**4. 🔴 项目有音频**资产**（2 音波 + 5 类 + 1 衰减），但**源码 0 处播放代码**。**

**5. 🔴 「读过文档」≠「做过」。**
音频域的证据是：资产存在但从未被使用。

---

## 六、更正

| 之前（能力盘点）| 现在 |
| --- | --- |
| 「audio 65%」 | ❌ **实际实操 0：无播放代码、无音频图** |
| 「有 SoundClass 就算配好了」 | ❌ **分类结构齐全 ≠ 有声音** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **建一个 Sound Cue 并播放** | **可以做**（`SoundCue` 类可用 + 有 2 个音波）|
| **建 MetaSound** | 类可用，但 MetaSound 图编辑需要专门接口 |
| Quartz 时间调度实测 | 没试 |
| Audio Analysis（频谱驱动视觉）| 没试 |

**→ 下一轮值得做：**用 2 个已有音波建一个 Sound Cue，然后验证能播。
→ 那是「让已有资产真的发出声音」的一步。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-AUDIO.md   1 篇（共 51 篇 learn 文档）
补读进度：46 / 57
主关卡 116 actor / 视口复位
```

---

## 九、补读还剩 11 篇

```
water (2.6) / water-bodies (27.6)
light-types (5.5) / lighting-environment (4.2) / instanced-materials (9.7)
niagara (3.2) / niagara-modules (2.5)
fbx-static-mesh (16.1) / import-static-meshes (5.0)
sound-cue-editor (3.7)
python-with-ai-agents (8.0) / chaos-destruction (0.6)
```

**→ 下一轮：`water-bodies.md`（27.6 KB）—— 水体域最大一篇。**
