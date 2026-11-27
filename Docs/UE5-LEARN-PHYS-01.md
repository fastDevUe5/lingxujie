# UE5 学习 · 物理（第一块）：终于让东西真的动了

> **这一块最重要的不是物理知识，是发现了**为什么之前所有的「让东西动起来」都失败**。
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、官方文档：`physics.md` 是索引页

**15.7 KB，16 个小节，但每节只有一两句概述 ——「Chaos」出现 46 次，**实质内容几乎为零**。**

```
Destruction / Networked Physics / Chaos Visual Debugger
Rigid Body Dynamics / Rigid Body Animation Nodes
Cloth Physics / Ragdoll / Chaos Vehicles / Physics Fields
Fluid Simulation / Hair Physics / Chaos Flesh / Dataflow Graph
```

**→ 这是 22 个索引页之一。真正有实质的是 `collision.md`（7 KB，7 节）：
Collision / Collision Responses / Overlap / Ignore / Generate Hit Events。**

---

## 二、🔴🔴 本块最大的发现：`time.sleep()` 会冻住世界

**之前所有的失败，根因是同一个：**

```python
# 错误做法
level_subsystem.editor_play_simulate()
time.sleep(1.5)              # ← 这一行阻塞了游戏线程
position = read_position()   # ← 世界根本没推进
```

**`time.sleep()` 在控制台命令里执行时**阻塞游戏线程**，PIE **无法 tick**。**

**→ 那段时间世界是冻住的。读到的位置永远是开始的位置。**

**这也解释了动画那一块：`set_position` 写进去的值没有被求值 —— 因为没有 tick。**

### 正确做法：拆成两次独立运行

```
运行 A：放置 + 存盘 + 启动 simulate + 立即退出
   ↓（工具调用之间有真实时间，编辑器自由 tick）
运行 B：读位置 + 结束 simulate
```

**✅ 实测成功。**

---

## 三、🔴 另外三个坑

### 3.1 `set_simulate_physics` 是**方法**不是属性

```
❌ component.get_editor_property("simulate_physics")
✅ component.set_simulate_physics(True)
✅ component.set_enable_gravity(True)
```

**`PrimitiveComponent` 上的完整物理接口：**
```
set_simulate_physics(simulate)
set_enable_gravity(gravity_enabled)
set_mass_override_in_kg(bone_name, mass_in_kg, override_mass)
set_mass_scale(bone_name, mass_scale)
get_mass() → float
add_impulse / add_impulse_at_location / add_impulse_at_position
```

### 3.2 结束 PIE 会**从磁盘重载关卡**

**第一次测完，球不见了 —— 因为我 spawn 的 actor **没存盘**，end play 一重载就没了。**

**→ 要让 PIE 里有东西，必须先 `save_current_level()`。**

### 3.3 `get_all_level_actors()` 拿不到 PIE 世界的 actor

**PIE 在**独立的 World 对象**里跑：**

```
❌ unreal.EditorLevelLibrary.get_all_level_actors()   ← 编辑器世界，PIE 期间是空的
✅ unreal.UnrealEditorSubsystem.get_game_world()      ← PIE 世界
✅ unreal.GameplayStatics.get_all_actors_of_class(game_world, ...)
```

---

## 四、🎯 实测结果

**用官方素材 `/Engine/BasicShapes/Sphere`（100 cm 球，缩放 0.4 → 40 cm），
放在练习关卡地板（z=0）上方 z=300。**

### 4.1 台阶式排查

| 尝试 | 结果 | 原因 |
| --- | --- | --- |
| 1 | `FATAL: Failed to find property 'simulate_physics'` | 是方法不是属性 |
| 2 | 同上（我的日志行还在读属性） | 自己写错 |
| 3 | `is_in_play=False` | 启动是延迟的 |
| 4 | `first read: None` | 读的是编辑器世界 |
| 5 | `fell 0.00 cm`，但速度有值 | 已经落完了 |
| 6 | `no game world` | 0.4 秒 + sleep 冻住了 |
| 7 | **`fell 275.0 cm`** | **拆成两次运行** ✅ |

### 4.2 最终数据（✅ 实测）

```
in play: True
game world: 'L_LightLab'
sphere now at (-320.0, 469.5, 25.0)
fell 275.0 cm from the start height
velocity (0.0, 0.0, 0.0)        ← 已静止
mass 13.93 kg
```

**读法：**

| 项 | 值 | 含义 |
| --- | --- | --- |
| 起点 z | 300 | 放置高度 |
| 终点 z | **25** | **地面 + 球半径 20** |
| 下落 | **275 cm** | 300 − 25 |
| 速度 | **(0, 0, 0)** | **已静止**（不是还在飞）|
| 质量 | **13.93 kg** | 碰撞体很轻 |

**→ 重力、碰撞、静止全部正常工作。**

### 4.3 一个意外：球滚了 5 米

**x/y 从 (0, 0) 漂到 (-320, 469.5) —— 水平移动了约 **570 cm**。**

**→ 球落地后**滚动**了。可能原因：**
- 地面不绝对水平
- 落地有弹性（restitution）
- 初始有微小水平速度

**→ 这条值得单独查，本轮没做。**

---

## 五、官方文档里对得上的部分

**`collision.md` 讲的 Collision / Collision Responses / Overlap / Ignore，
实际用到的就是「球 vs 地板」这一组碰撞响应 —— 两者都默认 Block，所以球停在地面上。**

**`physics.md` 提到的 Chaos 刚体动力学，本轮实测的就是最基础的一环：
刚体 + 重力 + 碰撞 + 静止。**

---

## 六、这一块学到什么

**1. 🔴 `time.sleep()` 在编辑器脚本里 = 冻住整个世界。**
这解释了之前**所有**「让东西动起来却不动」的失败。

**2. 要观察模拟，必须拆成多次独立运行，中间留真实时间。**

**3. PIE 有独立的 World。** 读 PIE 的东西用 `get_game_world()`。

**4. 结束 PIE 会从磁盘重载关卡。** 没存盘的 actor 会消失。

**5. 物理 API 是方法不是属性** —— 第 4 次因为猜 API 名失败。

**6. 一条可以推广的经验：**
> **编辑器脚本里不要 `sleep`，要「分次运行」。**

---

## 七、还没做到

| 项 | 为什么 |
| --- | --- |
| 为什么滚了 5 米 | 需要查物理材质、弹性、地面平整度 |
| 约束（Constraint） | 没测 |
| 冲量 / 力 | API 有了，没测 |
| 物理子步 | 没测 |
| 帧时间 | 还是没量 |

---

## 八、下一块

**两个选择：**
- **A. 继续物理**：查为什么滚 5 米（物理材质 / 弹性 / 摩擦）
- **B. 转 Niagara**（目标里的下一项）

**→ A 更连贯，而且「球滚太远」是真实项目会遇到的问题（掉落物会滚出拾取范围）。
但先把这一块的「分次运行」方法写进工具，别让下一块重新踩。**
