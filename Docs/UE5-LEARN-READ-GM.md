# UE5 学习 · 补读（二十三）：游戏框架 —— 项目选对了基类

> **文档说单机该用 `AGameModeBase`（简单高效），多人才用 `AGameMode`（带 match state）。**
> **源码核实：`ALXJGameMode : public AGameModeBase` —— 选对了。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、game-mode.md（12 KB，7 节）

```
Game Mode and Game State Overview
Game Modes
AGameModeBase
AGameMode
Game Mode Blueprints
Setting the Game Mode
Game State
```

### 1.1 🎯 核心区分（文档原文）

> **「Engine version 4.14 introduces **AGameModeBase**, which is the base class for all Game Modes
> and is a simplified and streamlined version of the classic AGameMode.
>
> AGameMode ... still exists and functions as it did before, but is **now a child of AGameModeBase**.
> **AGameMode is more suited to standard game types like multiplayer shooters
> due to its implementation of the concept of match state.**
>
> **AGameModeBase is the new default game mode** included in new code projects
> due to its **simplicity and efficiency**.」**

**→ 一句话：**
- **`AGameModeBase`** = 单机 / 简单 / 默认
- **`AGameMode`** = 多人 / 带 **match state**（比赛阶段机）

### 1.2 `AGameModeBase` 的关键函数

| 函数 | 什么时候调用 |
| --- | --- |
| **`InitGame`** | **在任何其它脚本之前**，包括 `PreInitializeComponents` |
| `PreLogin` | 玩家尝试加入时；设 `ErrorMessage` 可拒绝 |
| **`PostLogin`** | 登录成功后；**第一个能安全调用复制函数的地方** |
| `HandleStartingNewPlayer` | `PostLogin` 或无缝旅行后；**默认会创建 pawn** |
| `RestartPlayer` | 开始生成玩家 pawn |
| `SpawnDefaultPawnAtTransform` | **真正生成 pawn 的地方** |

**→ 这几个函数连起来就是「玩家进来的完整链路」：**
```
InitGame → PreLogin → PostLogin → HandleStartingNewPlayer
  → RestartPlayer → SpawnDefaultPawnAtTransform
```

---

## 二、gameplay-framework.md（9.6 KB，4 节）

```
Overview（类关系可视化）
Gameplay Framework Classes（重要类的总览表）
Directory
```

**→ 这是一篇**导航页**（把框架类列出来，各自链到自己的页面）。
→ 核心价值：**一张类关系图 + 一张职责表**。

---

## 三、✅ 源码核实：项目选对了基类

```
LXJGameMode.h:15   class LINGXUJIE_API ALXJGameMode : public AGameModeBase    ✅
```

**→ 用的是**简化版**，没有 match state 那套多人机制。**

### 3.1 配置链（✅ 三处核实）

```
DefaultEngine.ini:4    GlobalDefaultGameMode=/Script/LingXuJie.LXJGameMode
LXJGameMode.cpp:9      DefaultPawnClass = ALXJCharacter::StaticClass();
LXJGameMode.cpp:10     HUDClass        = ALXJHUD::StaticClass();
```

**→ 全局默认 GameMode 指向项目的 `LXJGameMode`。
→ 该 GameMode 指定了 `LXJCharacter` 作为 pawn、`LXJHUD` 作为 HUD。**

**→ 这解释了补读里 begin_play 为什么能自动生成 `LXJCharacter_0` / `LXJHUD_0` / `LXJGameMode_0`。**

### 3.2 世界设置没有覆盖

**→ `WorldSettings` 里没有关卡级的 GameMode 覆盖，
所以用的是 `GlobalDefaultGameMode`。**

**→ 这也意味着：**练习关卡 `L_Scene01` 也会跑项目的 GameMode**（之前 begin_play 时证实了）。**

---

## 四、🎯 这个选择的正确性

| 项目情况 | 需要什么 | `AGameModeBase` 提供了吗 |
| --- | --- | --- |
| **单机** | 无 match state | ✅ 正好不提供 |
| 需要自定义 pawn | `DefaultPawnClass` | ✅ |
| 需要自定义 HUD | `HUDClass` | ✅ |
| 需要出生点逻辑 | `RestartPlayer` | ✅ |
| **不需要**多阶段比赛流程 | — | ✅ 没有多余负担 |

**→ 完全匹配。如果选了 `AGameMode`，会白白背上 match state 的状态机。**

---

## 五、这一篇学到什么

**1. 🎯 `AGameModeBase` vs `AGameMode` 的分界线是 **match state**。**
单机用 `Base`，多人用 `AGameMode`。**选错的代价是多余的状态机。**

**2. 🎯 玩家进入的完整链路：**
`InitGame → PreLogin → PostLogin → HandleStartingNewPlayer → RestartPlayer → SpawnDefaultPawnAtTransform`

**3. 🔴 `InitGame` 在**任何**其它脚本之前调用** —— 包括它自己的 `PreInitializeComponents`。
→ 这是**唯一**能做「比一切更早」的初始化的地方。

**4. 🎯 `PostLogin` 是第一个能安全调用复制函数的地方。**
→ 网络相关逻辑的起点。

**5. ✅ 本项目选对了 `AGameModeBase`，配置链完整（ini → GameMode → pawn/HUD）。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「GameMode 就是一个大基类」 | ❌ **是两个：`Base`（单机）vs `AGameMode`（多人 match state）** |
| 「关卡可以自己指定 GameMode」 | ✅ **可以，但本项目用全局默认（WorldSettings 无覆盖）** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| `PreLogin` / `PostLogin` 的实测 | **单机不触发网络登录流程** |
| Match state 的行为 | 项目没用 `AGameMode`，**无实测条件** |
| `HandleStartingNewPlayer` 的覆写 | 项目没覆写 |
| GameState 的用途 | 文档有，项目没自定义 GameState |

---

## 八、状态

```
Docs/UE5-LEARN-READ-GM.md   1 篇（共 40 篇 learn 文档）
补读进度：24 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 33 篇）。下一批：**
- `blueprints.md`（21.4 KB）—— 蓝图（项目用 C++，但要懂）
- `data-tables.md`（8.7 KB）
- `savegame.md`（12.2 KB）
- `enhanced-input.md`（24.7 KB）—— 输入（项目弱项）
- `python-scripting.md`（32.6 KB）—— 我天天在用
- `unreal-mcp.md`（31.4 KB）

**→ 选 `enhanced-input.md`（24.7 KB）—— 输入是能力盘点里 45% 的弱项。**
