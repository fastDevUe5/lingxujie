# UE5 学习 · 补读（二十五）：增强输入 —— 项目用的是最原始的方式

> **文档讲的是 Enhanced Input 的四大概念。**
> **实测：项目**一个 Input 资产都没有**，源码用 `PC->IsInputKeyDown(EKeys::W)` **逐帧硬轮询**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、enhanced-input.md（24.7 KB，15 节）

```
Dynamic and Contextual input mappings
Creating Enhanced Input Assets
**Core Concepts**
Input Actions
Trigger States
Adding Input Listeners
Input Mapping Contexts
Input Modifiers
Directional Input
Input Triggers
Player Mappable Input Config (PMI)
Debug Commands
Injecting Input
Platform Settings
```

### 1.1 🎯 四个核心概念（文档原文）

> **「The Enhanced Input system has four main concepts,
> **Input Actions**, **Input Mapping Contexts**, **Input Modifiers**, and **Input Triggers**.」**

| 概念 | 作用 |
| --- | --- |
| **Input Action** | 一个抽象动作（比如「跳跃」），**不带任何按键** |
| **Input Mapping Context** | 一张「动作 ← 按键」的映射表，**可动态增删** |
| **Input Modifier** | 修改输入值（取反、缩放、死区、轴交换）|
| **Input Trigger** | 决定**何时**触发（按下、长按、连击、脉冲）|

**→ 核心设计思想：**动作和按键**解耦**。
→ 同一个 Input Action 可以被多个 Context 映射到不同按键 → **这就是可重绑定的基础。**

### 1.2 其它值得注意的

| 章节 | 价值 |
| --- | --- |
| **Player Mappable Input Config (PMI)** | **把按键配置做成资产**，支持玩家自定义 |
| **Debug Commands** | 运行时看输入状态 |
| **Injecting Input** | **代码里模拟输入**（测试用）|
| **Trigger States** | 触发器内部状态，调试用 |

---

## 二、🔴 实测：项目完全没用 Enhanced Input

### 2.1 零资产

```
/Game 下所有 "Input" 类别资产：0 个
```

**→ 没有 Input Action、没有 Input Mapping Context、没有 PMI 配置。**

### 2.2 源码用的是**逐帧硬轮询**

```cpp
// LXJCharacter.cpp
const bool bLookLeft  = PC->IsInputKeyDown(EKeys::Q);
const bool bLookRight = PC->IsInputKeyDown(EKeys::E);

const float ForwardAxis = (PC->IsInputKeyDown(EKeys::W) || PC->IsInputKeyDown(EKeys::Up) ? 1.f : 0.f)
                        - (PC->IsInputKeyDown(EKeys::S) || PC->IsInputKeyDown(EKeys::Down) ? 1.f : 0.f);
const float RightAxis   = (PC->IsInputKeyDown(EKeys::D) || PC->IsInputKeyDown(EKeys::Right) ? 1.f : 0.f)
                        - (PC->IsInputKeyDown(EKeys::A) || PC->IsInputKeyDown(EKeys::Left) ? 1.f : 0.f);

bSprinting  = (PC->IsInputKeyDown(EKeys::LeftShift) || PC->IsInputKeyDown(EKeys::RightShift)) && ...;
bJumpDown   = PC->IsInputKeyDown(EKeys::SpaceBar);
bDashDown   = PC->IsInputKeyDown(EKeys::LeftControl) || PC->IsInputKeyDown(EKeys::C);
PC->GetInputMouseDelta(MouseDX, MouseDY);

// 技能
const FKey Slots[3] = { EKeys::LeftMouseButton, EKeys::One, EKeys::Two };
const bool bDown = PC->IsInputKeyDown(Slots[Index]) || (Index == 0 && PC->IsInputKeyDown(EKeys::J));
```

**→ 这是**最原始**的方式：**
- ❌ 不是 Enhanced Input
- ❌ **也不是**老的 `BindAxis` / `BindAction`
- ✅ 是 **`PC->IsInputKeyDown(FKey)` 每帧自己查**

### 2.3 全部硬编码的按键

| 动作 | 按键 |
| --- | --- |
| 前后 | **W / S**（或 Up / Down）|
| 左右 | **A / D**（或 Left / Right）|
| 视角 | **Q / E** + 鼠标 |
| 跳跃 | **Space** |
| 冲刺 | **LeftShift / RightShift** |
| 闪避 | **LeftCtrl / C** |
| 技能 1/2/3 | **LMB(或 J) / 1 / 2** |
| 菜单 | **Esc** |

**→ 全部写死在 C++ 里。**

---

## 三、🎯 这个选择的代价

| 拿不到的 | 原因 |
| --- | --- |
| **按键重绑定** | 键写死在代码，没有映射表可换 |
| **PMI 玩家配置** | 没有 Input Action 资产 |
| **手柄支持** | 只查了键盘键和鼠标，没查手柄轴 |
| **输入触发器**（长按/连击/双击）| 只能自己用 `bXxxKeyHeld` 手写边沿检测 |
| **动态上下文切换** | 没有 Context 概念（比如「按 Esc 打开菜单时禁用移动」）|
| **死区/缩放/轴交换** | 没有 Modifier |
| **输入注入测试** | 没有 Input Action 可注入 |

**→ 代码里确实手写了边沿检测**（`bJumpKeyHeld`、`bDashKeyHeld`、`bSkillKeysHeld[3]`）
**→ 那正是 Input Trigger 该做的事，这里手写了一遍。**

### 3.1 收益

| 得到的 | 说明 |
| --- | --- |
| **零资产依赖** | 不用建 Input Action / Context 资产 |
| **立即可用** | 不需要在 BeginPlay 里 AddMappingContext |
| **逻辑集中** | 所有输入在一个函数里，好读 |
| **无 Input 组件开销** | 不走 EnhancedInputComponent 的委托分发 |

---

## 四、🎯 这是输入域的核心事实

**之前能力盘点把「输入」评为 45%（弱项）。
现在有了具体解释：**

| 层面 | 掌握情况 |
| --- | --- |
| **Enhanced Input 的概念** | ✅ 现在读懂了（四概念 + PMI + 触发器）|
| **Enhanced Input 的实操** | ❌ **项目根本没用，我没写过一行** |
| **项目实际用的输入方式** | ✅ **读懂了（逐帧硬轮询 + 手写边沿检测）** |

**→ 诚实结论：**
**我懂「Enhanced Input 是什么」，但**没有在项目里用过**，也没有在练习关卡里建过 Input Action。**
**→ 这个域的实操部分仍然是空的。**

---

## 五、这一篇学到什么

**1. 🎯 Enhanced Input 的核心是**动作与按键解耦**。**
Input Action 是抽象动作，Mapping Context 是「动作←按键」的表。

**2. 🎯 四个概念各解决一个问题：**
Action（抽象）/ Context（映射）/ Modifier（改值）/ Trigger（定时）。

**3. 🔴 项目用 `PC->IsInputKeyDown(EKeys::W)` **逐帧轮询**。**
**→ 比老式 `BindAxis` 还原始 —— 连绑定都不走，直接查键状态。**

**4. 🔴 代价是**所有按键硬编码**，无法重绑定、无手柄、无触发器。**

**5. 🎯 手写的 `bXxxKeyHeld` 三处边沿检测，正是 Input Trigger 的本职工作。**
**→ 重造了一个已经有的轮子。**

**6. ✅ 诚实：Enhanced Input 我只读懂了概念，**一次都没实操过**。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「项目用 Enhanced Input」 | ❌ **一个 Input 资产都没有** |
| 「输入弱项是因为不懂概念」 | ⚠️ **概念懂了，但**项目里没有可实操的对象**** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **在练习关卡建 Input Action + Context** | **可以做**（`InputAction` 类可用），值得下一轮做 |
| `InputMappingContext` 的 Python 可写性 | 没试 |
| `Injecting Input` 的实测 | 没试 |
| 手柄输入 | 项目不支持，没测 |

**→ 下一轮值得做：**在 `L_Scene01` 里建一对 Input Action + Context，即使是空跑，
也算「摸过 Enhanced Input 的资产结构」—— 那会比只读文档强。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-INPUT.md   1 篇（共 41 篇 learn 文档）
补读进度：26 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**两个方向：**
- **继续补读**（还剩 31 篇）：`blueprints.md` / `data-tables.md` / `savegame.md` / `python-scripting.md`
- **或先做 Enhanced Input 的实操**：建 Input Action + Context 资产，验证 Python 能不能建

**→ 我倾向先做实操** —— 这一篇的结论是「只懂概念没实操」，
**那正好可以用下一轮把这个洞补上，而不是再读一篇只懂概念的文档。**
