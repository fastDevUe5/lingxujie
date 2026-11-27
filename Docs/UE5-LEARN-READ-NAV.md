# UE5 学习 · 补读（二十一）：导航 —— 项目选择完全不用它

> **两篇导航文档都是**入门教程**，前提是「关卡里有一个 NavMesh」。
> **实测：项目一个都没有。**源码里怪物用 `AddMovementInput` 直线走。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、navigation-basic.md（6.9 KB）—— 分步教程

```
Overview / Goals / Objectives
1 - Required Setup
2 - Building the Navigation Mesh
3 - Visualizing the Navigation Mesh
4 - Creating your First Agent
```

**两篇的章节结构几乎一样，都是**一步步带你做**，不是参考手册。**

**唯一有名字的实体：**
- **`RecastNavMesh-Default`** —— 构建导航后自动加到关卡的 actor
- **`Draw Tile Bounds`** —— 可视化单个寻路瓦片

## 二、navigation-mesh.md（7.6 KB）

```
Overview / Objectives
1 - Required Setup
2 - Creating Your Test Level
3 - Creating Your Agent
```

**→ 两篇加起来能提取的硬事实很少：**
**导航网格由 Recast 生成；生成后关卡里有 `RecastNavMesh` actor；瓦片边界可以可视化。**

---

## 三、✅ 实测：项目完全没有导航

```
LingXuJie   116 actors   nav actors []   bounds volumes []
L_Scene01    14 actors   nav actors []   bounds volumes []

Config/*.ini → 完全没有 NavigationSystem / RecastNavMesh / RuntimeGeneration 配置
```

**→ 没有 `RecastNavMesh` actor，没有 `NavMeshBoundsVolume`，配置里零条目。**

### 3.1 🔴 源码确认：怪物直线移动

```cpp
// Source/LingXuJie/LXJMonster.cpp:199
AddMovementInput(Direction, 1.f);
```

**全项目搜索：**
```
AI_MoveTo        → 0 处
MoveToLocation   → 0 处
AIController     → 0 处
NavMesh          → 0 处
PathFinding      → 0 处
```

**→ 怪物用 `AddMovementInput(方向)` 直接走，**完全没有寻路。****

**→ 这和 AGENTS.md 记载的「`LXJMonsterBrain` 是**纯函数状态机**」一致：
决策是纯函数，移动是直接输入，中间没有寻路层。**

---

## 四、🎯 这意味着什么

### 4.1 `AddMovementInput` 的行为

**→ 它把方向向量交给 CharacterMovementComponent，后者做**扫掠（sweep）移动**：
碰到墙会沿墙滑动，但**不会主动绕开障碍**。**

**→ 所以会发生：**
- 玩家躲到墙后，怪物会**顶着墙推**
- 有凹形障碍时可能**卡住**
- 但不会穿墙（有碰撞检测）

### 4.2 这个选择的代价与收益

| 代价 | 收益 |
| --- | --- |
| 无法绕障碍 | **零导航构建时间** |
| 凹角可能卡住 | **零 NavMesh 内存** |
| 玩家可以靠走位摆脱 | **决策逻辑简单可测** |
| 不能做「巡逻路线」 | 纯函数状态机**没有隐藏状态** |

**→ 对一个 P0 单机垂直切片，这个选择是**合理的**：
怪物只需要「追玩家 + 攻击」，直线追击已经足够。**

**→ 但这是**明确的能力边界**：一旦要做「绕建筑追人」，
就必须引入 NavMesh 或至少一个简单的物理绕行逻辑。**

---

## 五、这一篇学到什么

**1. 🎯 导航网格由 **Recast** 生成，构建后关卡出现 `RecastNavMesh` actor。**
瓦片边界可用 `Draw Tile Bounds` 可视化。

**2. 🔴 `AddMovementInput` 不等于寻路。**
它只做扫掠移动 —— **会沿墙滑，但不会绕路。**

**3. 🎯 这个项目用「纯函数状态机 + 直接移动输入」，没有寻路层。**
**→ 决策和移动之间没有中间件，所以行为可预测、可测试。**

**4. 🔴 能力边界：**玩家躲到墙后，怪物会顶墙推，不会绕。****

**5. ✅ 两篇导航文档我**没能实操** —— 因为项目没有导航系统，
而「加一个 NavMesh 到练习关卡」属于开发，不在本目标范围内。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「有 AI 怪物就该有导航」 | ❌ **项目零导航，怪物直线走** |
| 「`AddMovementInput` 是简化版的寻路」 | ❌ **它根本不是寻路，没有绕障能力** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **在练习关卡建 NavMesh 实操** | 属于开发，不做 |
| `RecastNavMesh` 的参数（Agent Radius/Height）| 项目没有，查不到活值 |
| 导航的运行时生成（Runtime Generation）| 同上 |
| Navigation Invoker（按需生成）| 同上 |

**→ 这两篇是本系列**第一对「完全没有实操条件」**的文档。
→ 但「项目为什么没有导航」这个结论**本身有价值**。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-NAV.md   1 篇（共 39 篇 learn 文档）
补读进度：22 / 57
主关卡 116 actor / 视口复位
```

---

## 九、下一篇

**继续补读（还剩 35 篇）。下一批优先：**
- `blueprints.md`（21.4 KB）—— 蓝图（虽然项目用 C++，但要懂它）
- `game-mode.md`（12 KB）—— 游戏框架
- `gameplay-framework.md`（9.6 KB 索引）
- `data-tables.md`（8.7 KB）

**→ 选 `game-mode.md` + `gameplay-framework.md`，把游戏框架这条线补上（项目的 `LXJGameMode` 就在这）。**
