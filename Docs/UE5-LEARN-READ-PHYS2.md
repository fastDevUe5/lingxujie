# UE5 学习 · 补读（十九）：碰撞与物理 —— 材质属性拿到了，弹跳实验失败了

> **这一篇是**半成功**：物理材质的真实默认值全部拿到，
> 但**弹跳实验因为一个属性名失败**，球没落下来。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、collision.md（7.1 KB，7 节）

```
Collision Overview
Interactions
Common Collision Interaction Examples
Collision
**Collision and Simulation Generates Hit Events**
**Overlap and Ignore**
**Overlap and Generate Overlap Events**
```

**→ 这是一篇**概念**文档（碰撞响应怎么工作），没有硬数字。
→ 但它的章节名点出了两个**常见坑**：
1. **模拟要产生 Hit 事件，得单独勾选**（`Simulation Generates Hit Events`）
2. **Overlap 要产生事件，也得单独勾选**（`Generate Overlap Events`）

**→ 这两条是 UE 里最经典的「为什么我的事件不触发」的答案。**

---

## 二、physics.md（15.9 KB，16 节）—— 这是**功能地图**

| 章节 | 子系统 |
| --- | --- |
| Chaos Physics | 总述 |
| **Rigid Body Dynamics** | 刚体 |
| Rigid Body Animation Nodes / Physical Animation | 物理动画 |
| **Destruction** | Chaos 破坏 |
| **Physics Fields** | 力场（直接作用于 Chaos 模拟）|
| **Cloth Physics / Machine Learning Cloth** | 布料 |
| **Ragdoll** | 布娃娃 |
| **Chaos Vehicles** | 载具 |
| **Fluid Simulation** | 2D/3D 流体 |
| **Hair Physics** | 头发（strand-based）|
| **Chaos Flesh** | 可形变体 |
| **Dataflow Graph** | 节点式程序化资产生成 |
| Networked Physics | 网络物理 |
| **Chaos Visual Debugger (CVD)** | 可视化调试器 |

**→ 这一篇的价值是**清单**：知道 Chaos 有哪些子系统，以及每个都有独立文档。
→ **本项目一个都没用**（它是 RPG 动作，只需要刚体 + 碰撞）。**

---

## 三、✅ 实测：物理材质的真实默认值

**`unreal.PhysicalMaterial()` 的 18 个可读属性（✅ 全部枚举）：**

```
density                            1.0
friction                           0.7
static_friction                    0.0        ← 注意
friction_combine_mode              AVERAGE
override_friction_combine_mode     False
restitution                        0.3        ← 弹性
restitution_combine_mode           AVERAGE
override_restitution_combine_mode  False
raise_mass_to_power                0.75
sleep_angular_velocity_threshold   0.05
sleep_linear_velocity_threshold    1.0
sleep_counter_threshold            4
surface_type                       SURFACE_TYPE_DEFAULT
damage_modifier                    <struct>
strength                           <struct>
debug_color                        <struct LinearColor>
```

### 3.1 🔴 一个值得注意的不对称

```
friction         = 0.7    （动摩擦）
static_friction  = 0.0    （静摩擦）
```

**→ **静摩擦是 0，动摩擦是 0.7。**
→ 意思：物体**不会抵抗开始滑动**，但一旦滑起来就有 0.7 的阻力。
→ 这和现实直觉相反（通常静摩擦 ≥ 动摩擦）。

**→ 这可能就是引擎默认值，也可能需要项目自己设。**
**→ 我**没有**核实这是不是 Chaos 的刻意设计 —— 只记录了读到的事实。**

### 3.2 `restitution` 默认 0.3

**→ 非 0，意味着**默认材质是有弹性的**。
→ 如果想让物体落地就停，需要显式设 `restitution = 0`。**

### 3.3 `PhysicalMaterialFactory` **不存在**

```
unreal.PhysicalMaterialFactory  →  False
```

**→ 不能像 Material/WidgetBlueprint 那样用工厂建资产。**
**→ 但 `unreal.PhysicalMaterial()` 可以直接构造对象（上面就是这么拿到默认值的）。**

---

## 四、🔴 弹跳实验失败

### 4.1 我的设计

```
1. 建 PhysicalMaterial，设 restitution
2. 在 z=1200 放一个球
3. 设 phys_material_override = 该材质
4. set_simulate_physics(True)
5. 分次运行读最终高度
```

### 4.2 失败点

```
BOUNCE: physical material restitution 0.00     ✅
BOUNCE: FATAL: Exception("StaticMeshComponent: Failed to find property '...'")
```

**→ **`phys_material_override` 不是可写的 Python 属性名。****
**→ 脚本在第 3 步就崩了，后面的 simulate_physics 没执行。**
**→ 所以球一直在 z=1200 没动（读回来就是 1200，velocity 也读不到）。**

### 4.3 这个失败暴露的问题

**→ 我**又一次**在第 1 步就用了猜的属性名**（本系列第 8 次）。**
**→ 正确做法应该是先 `dir()` 枚举 StaticMeshComponent 的属性，再写脚本。**

---

## 五、这一篇学到什么

**1. 🎯 `restitution` 默认 **0.3**，不是 0。**
**→ 想让物体落地即停，必须显式设 0。**

**2. 🔴 `static_friction = 0.0` 而 `friction = 0.7`。**
**→ 静摩擦为 0 意味着物体不会抵抗初始滑动 —— 这和现实直觉相反。
→ 我只记录事实，没核实这是不是刻意设计。**

**3. 🎯 `PhysicalMaterialFactory` 不存在，但 `unreal.PhysicalMaterial()` 可以直接构造。**

**4. 🔴 又一次在写脚本前没枚举属性名（第 8 次）。**
**→ 正确顺序：先 `dir()` 看有什么，再写代码。**

**5. 🎯 collision.md 的两条「为什么事件不触发」：**
**`Simulation Generates Hit Events` 和 `Generate Overlap Events` 都要单独勾。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「物理材质默认无弹性」 | ❌ **restitution 默认 0.3** |
| 「`static_friction` 应该 ≥ `friction`」 | ⚠️ **引擎默认是 0.0 vs 0.7，反直觉** |
| 「`phys_material_override` 能直接设」 | ❌ **不存在的属性名** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **弹跳实验** | **失败，需要先枚举正确属性名** |
| `Simulation Generates Hit Events` 的实测 | 需要绑事件，Python 里可能做不到 |
| Overlap 事件 | 同上 |
| Chaos 的其它子系统（破坏/布料/流体）| 项目没用，也没资产 |

---

## 八、状态

```
Docs/UE5-LEARN-READ-PHYS.md   1 篇（共 38 篇 learn 文档）
补读进度：20 / 57
主关卡 116 actor / 视口复位（PHYS 球已清）
```

---

## 九、下一篇

**继续补读（还剩 37 篇）。下一批：**
- `navigation-basic.md`（6.9 KB）+ `navigation-mesh.md`（7.6 KB）—— AI 寻路
- `game-mode.md`（12 KB）—— 游戏框架
- `blueprints.md`（21.4 KB）

**→ 选 `navigation-mesh.md` + `navigation-basic.md`，把 AI 域补上。**
