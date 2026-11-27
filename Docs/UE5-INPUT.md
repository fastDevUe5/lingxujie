# UE5 输入系统：三代方案与我们的选择（源码 + 工程实测）

> **这一篇有个少见的性质：它同时讲引擎的输入架构**和**我们发现的本项目实现矛盾。
>
> **结论先行：本项目用的是**轮询**（最原始的一代），
> 而工程配置里默认的是 Enhanced Input（第三代）。两者完全没打通。**

---

## 一、UE5 的三代输入方案

| 代 | 方案 | 怎么用 | 状态 |
| --- | --- | --- | --- |
| **1** | **直接轮询** | `PC->IsInputKeyDown(EKeys::W)` | 能跑，最原始 |
| **2** | **输入组件（Action/Axis Mapping）** | `BindAction("Jump", ...)` + ini 映射 | 仍支持 |
| **3** | **Enhanced Input** | `InputAction` + `InputMappingContext` 资产 | **UE5 默认** |

### 1.1 三者的本质区别

| | 轮询 | Action Mapping | Enhanced Input |
| --- | --- | --- | --- |
| 键位可重映射 | ❌ **要改代码** | ✅ ini | ✅ 资产 |
| 手柄支持 | ❌ 要自己加判断 | ⚠️ 要配 | ✅ 内置 |
| 组合键/长按/双击 | ❌ 手写 | ❌ 不支持 | ✅ **内置** |
| 上下文切换 | ❌ | ❌ | ✅ **MappingContext 可叠加** |
| 代码量 | 少 | 中 | 中（但可配） |

---

## 二、🔴 本项目的实际情况（实测）

### 2.1 角色根本没有输入绑定

**`LXJCharacter.cpp` 里：**
```
SetupPlayerInputComponent    0 处
BindAction                   0 处
BindAxis                     0 处
InputComponent               0 处
```

**取而代之：**
```
IsInputKeyDown              18 处
EKeys::                     20 处
```

**实际代码：**
```cpp
const float ForwardAxis =
    (PC->IsInputKeyDown(EKeys::W) || PC->IsInputKeyDown(EKeys::Up) ? 1.f : 0.f)
  - (PC->IsInputKeyDown(EKeys::S) || PC->IsInputKeyDown(EKeys::Down) ? 1.f : 0.f);
```

**在 `Tick` 里每帧调用 `UpdateMove` / `UpdateLook` / `UpdateJumpAndGlide` / `UpdateDash`。**

### 2.2 但工程配置默认是 Enhanced Input

**`Config/DefaultInput.ini` 第 86-87 行：**
```ini
DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput
DefaultInputComponentClass=/Script/EnhancedInput.EnhancedInputComponent
```

**所以：**
- 引擎给我们装的是 Enhanced Input 的输入组件
- **但我们从来没调用它** —— 它是空转的

### 2.3 没有任何 Action/Axis 映射

**`DefaultInput.ini` 里 `ActionMapping` / `AxisMapping` 一条都没有。**

**这印证了：我们从设计上就没打算用映射系统。**

---

## 三、这个选择的代价与合理性

### 3.1 代价（诚实列表）

| 代价 | 影响 |
| --- | --- |
| **键位写死在 C++ 里** | 玩家改键 = 改代码重编译 |
| **不能做手柄支持** | 要加 `EKeys::Gamepad_*` 的判断 |
| **没有组合键/长按** | 都要手写计时 |
| **输入和 Tick 耦合** | 无法独立测试输入逻辑 |
| **绕过 Enhanced Input 资产** | 引擎给的能力一点没用 |

### 3.2 但当时的选择也有道理

| 理由 | 说明 |
| --- | --- |
| **单机 + 键盘** | P0 只需要 W/A/S/D + 鼠标 |
| **零配置** | 不用建 InputAction 资产，不用配 MappingContext |
| **好调试** | `IsInputKeyDown` 一眼看懂 |
| **不需要改资产** | 全在 C++ 里，Python 不用管 |

**对 P0 垂直切片来说，这是**合理的最小实现**。**

### 3.3 什么时候必须换

| 触发条件 | 必须换成 |
| --- | --- |
| 玩家要改键 | Enhanced Input |
| 要支持手柄 | Enhanced Input |
| 要做"按下右键进入瞄准模式" | Enhanced Input（有上下文切换）|
| 要做连招/长按蓄力 | Enhanced Input（有 Combo 和 Hold）|

**按 P0 范围，这些都不急。但**做 UI 设置面板时一定要先换** ——
否则"改键"这个设置项做不出来。**

---

## 四、Enhanced Input 的核心概念（源码核实）

**关键类（在 `Engine/Plugins/EnhancedInput/Source/EnhancedInput/Public/`）：**

| 类 | 作用 |
| --- | --- |
| `UInputAction` | **一个动作**（跳跃、攻击）|
| `UInputMappingContext` | **一套键位**（可以有多套，切换）|
| `UEnhancedInputComponent` | 绑定用 |
| `UEnhancedInputLocalPlayerSubsystem` | 管理上下文叠加 |

### 4.1 三者的关系

```
UInputAction "IA_Jump"
     ↑ 被映射
UInputMappingContext "IMC_Gameplay"
     ├ Space → IA_Jump
     ├ W → IA_Move (Axis2D)
     └ Mouse → IA_Look (Axis2D)
     ↓ 叠加到玩家
UEnhancedInputLocalPlayerSubsystem
```

**"上下文可叠加"是 Enhanced Input 最强的地方：**
- 游戏时叠 `IMC_Gameplay`
- 打开菜单时叠 `IMC_Menu`（屏蔽移动，只响应 Esc）
- 两者可以并存，优先级决定谁生效

**这个用轮询做不到 —— 必须自己维护状态机。**

---

## 五、掌握程度（输入）

| 内容 | 掌握 |
| --- | --- |
| 三代方案的区别 | 🟢 **清楚** |
| **本项目用哪代、为什么** | 🟢 **实测确认** |
| **工程配置默认是 Enhanced Input** | 🟢 **实测确认并指出矛盾** |
| Enhanced Input 的三个核心类 | 🟢 **清楚** |
| 上下文叠加的价值 | 🟢 **清楚** |
| **实际写过 Enhanced Input** | 🔴 **没写过** |
| **配过 InputMappingContext** | 🔴 **没配过** |
| 手柄 / 组合键 / 长按 | 🔴 **没碰** |

**输入系统：**从零 → 45%。**

**涨的是"架构和我们的选择都清楚了"，没涨的是"没写过 Enhanced Input"。**

---

## 六、该不该现在改（判断）

**不该。理由：**

1. **P0 只需要键鼠** —— 轮询够用
2. **改输入 = 改 C++ = 要编译 = 要关编辑器** —— 成本不小
3. **现在改成 Enhanced Input 不会让游戏变好** —— 只是更"标准"

**该改的时机：做设置面板（改键）之前。**

**在那之前，这条记录的价值是：**
> **知道我们在用第一代方案，知道第三代长什么样，知道换的成本在哪。**

---

## 七、重查命令

```powershell
# 看我们用了多少轮询
Select-String -Path Source\LingXuJie\LXJCharacter.cpp -Pattern 'IsInputKeyDown'

# 看工程默认输入类
Select-String -Path Config\DefaultInput.ini -Pattern 'EnhancedInput'
```
