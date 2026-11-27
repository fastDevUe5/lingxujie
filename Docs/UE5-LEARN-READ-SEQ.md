# UE5 学习 · 补读（四十一）：Sequencer 与 Control Rig —— 界面导览，项目两条都没用

> **两篇都是**「这个窗口里有什么」**的界面说明，没有硬数字。**
> **实测发现一个更有价值的事实：项目 50 个骨骼，只有 7 个动画序列。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、sequencer-editor.md（14.4 KB，18 节）

**纯界面导览：**
```
Toolbar / Outliner / Timeline
Navigation（Panning / Zooming）
Playhead / Scrubbing
  **Scrubbing Responsiveness**
  Media Player Info
  **Synchronous Scrubbing** ← 「perfect frame alignment while scrubbing」
Selection Ranges / Custom Frame Marks
Playback Controls
**Playback and Looping**
  Baseline Looping
  Internal Clipped Looping
```

**→ 能提取的硬事实很少。有价值的几条：**

| 事实 | 说明 |
| --- | --- |
| **Synchronous Scrubbing** | 拖动时间轴时能保证**逐帧精确对齐**（默认是「responsive」模式，可能跳帧） |
| **Selection Ranges** | 可以在序列里标自定义区间 |
| **Custom Frame Marks** | 可以标注时间点 |
| **两种循环方式** | **Baseline Looping**（基准循环）vs **Internal Clipped Looping**（内部裁剪循环）|

**→ 这四条是**工作流**知识，不是机制知识。**

---

## 二、control-rig-editor.md（11.2 KB，10 节）

**也是界面导览：**
```
Toolbar / Viewport
**Rig Hierarchy**
My Blueprint
**Execution Stack**
**Curve Container**
**Rig Graph**
Details / Preview Scene Settings
```

**六个窗格各自的作用：**

| 窗格 | 作用 |
| --- | --- |
| **Rig Hierarchy** | 骨骼控制层级 |
| **My Blueprint** | 变量与函数 |
| **Execution Stack** | 求解顺序（前向/后向/自定义）|
| **Curve Container** | 曲线容器 |
| **Rig Graph** | 节点图 |

**🎯 一条可核实的：**
> **「You can also access Control Rig **Python commands** such as Python Context and Copy Python Script.」**

**→ Control Rig 有 Python 支持。**
**→ 但项目**没有任何 Control Rig 资产**，所以这条用不上。**

---

## 三、✅ 项目实测：动画内容的真实状况

### 3.1 有 50 个骨骼，但只有 7 个动画

```
Skeleton       50   ['SK_Bird_Skeleton', 'SK_Boss001_Skeleton', 'SK_BossCowf_Sk...']
AnimSequence    7   ['SK_Boss001_Anim', 'jujube-tree-0e69dd_Anim', 'stone-guardi...']
```

**→ **50 : 7** —— 绝大多数骨骼网格**没有动画序列**。**
**→ 这些是导入的墨香/Megascans 素材，带动画的只有少数几个。**

### 3.2 零 Sequencer / ControlRig / AnimMontage

```
LevelSequence 资产:      0
ControlRig 资产:         0
AnimMontage 资产:        0
BlendSpace 资产:         0
```

**→ 类都可用（`LevelSequence` / `ControlRig` / `ControlRigBlueprint` / `AnimSequence` / `AnimMontage`），
但项目一个都没建。**

### 3.3 🎯 这解释了动画域一直是弱项

**回顾补读-ANIM-01 的结论：**
> **「编辑器里刷不动动画（组件不 tick），`bUpdateAnimationInEditor` Python 改不了」**

**→ 加上这一轮的事实：**
**→ 不只是「刷不动」，而是**没有足够的动画资产可研究**。**
**→ 50 个骨骼里 43 个**根本没有动画序列**。**
**→ 剩下的 7 个是导入素材自带的。**

**→ 所以动画域的真实状态是：**
| 层面 | 状态 |
| --- | --- |
| **动画原理（状态机/混合）** | ✅ 读过（ANIM-01） |
| **动画资产（Sequence/Montage/BlendSpace）** | ❌ **项目零个自建** |
| **Sequencer（过场动画）** | ❌ **零资产** |
| **Control Rig（程序化动画）** | ❌ **零资产，虽然类可用** |
| **骨骼动画的实际播放** | ⚠️ **编辑器刷不动，PIE 里能播但没法观察中间态** |

---

## 四、这一篇学到什么

**1. 🎯 两篇都是**界面导览**，不是机制说明。**
**→ 它们教「按钮在哪」，不教「为什么这样设计」。**
**→ 这类文档的价值在于「知道有这个功能」，不在于「理解它」。**

**2. 🎯 Sequencer 的 `Synchronous Scrubbing` 保证逐帧精确对齐**（默认模式可能跳帧）。

**3. 🎯 Control Rig 有 **Python 支持**（Python Context / Copy Python Script）。**
**→ 意味着程序化动画有可能从 Python 驱动 —— 但项目没有 Control Rig 资产。**

**4. 🔴 项目 **50 骨骼 : 7 动画** —— 绝大多数骨骼没有动画。**

**5. 🔴 零 Sequencer / 零 ControlRig / 零 AnimMontage / 零 BlendSpace。**
**→ 动画域「弱」的根因不是我不会，是**项目里几乎没有可研究的内容**。**

---

## 五、更正

| 之前 | 现在 |
| --- | --- |
| 「动画域弱是因为编辑器刷不动」 | ⚠️ **更根本的原因：50 骨骼只有 7 动画，且零自建动画资产** |
| 「Sequencer/ControlRig 应该是基本功」 | ❌ **项目完全没用到，没有实操对象** |

---

## 六、还没做到

| 项 | 说明 |
| --- | --- |
| **建一个 LevelSequence 实操** | **可以做**（类可用），但没有可绑定的相机/actor 逻辑 |
| **建一个 ControlRig** | 类可用，但需要骨骼网格 |
| AnimMontage / BlendSpace | 项目没有 |
| 用 Python 驱动 Control Rig | 文档说有 Python Context，没试 |

**→ 下一轮值得做：建一个**空的 LevelSequence 资产**并往里加一条相机轨道。
→ 那是「摸过 Sequencer 的资产结构」，和 Enhanced Input 那次同一种做法。**

---

## 七、状态

```
Docs/UE5-LEARN-READ-SEQ.md   1 篇（共 49 篇 learn 文档）
补读进度：42 / 57
主关卡 116 actor / 视口复位
```

---

## 八、补读进度盘点（还剩 15 篇）

**已读 42 篇（含索引页）。剩下的大多是：**
```
water (2.6) / water-bodies (27.6)       ← 水体
landscape (0.6 索引)                      ← 已读 technical
light-types (5.5 索引) / lighting-environment (4.2 索引)
instanced-materials (9.7 索引)
niagara (3.2) / niagara-modules (2.5)    ← 索引页
fbx-static-mesh (16.1) / import-static-meshes (5.0)
geometries / chaos-fracture (19.3) / chaos-destruction (0.6)
attenuation (0.6) / audio (5.7) / sound-cue-editor (3.7) / sound-cue-reference (40.0)
foliage 已读 / navigation 已读
python-with-ai-agents (8.0)
```

**→ 下一轮：`chaos-fracture.md`（19.3 KB）—— 破坏系统，物理域的实质内容。
或 `sound-cue-reference.md`（40 KB）—— 音频域最大一篇。**
