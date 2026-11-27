# UE5 物理仿真：碰撞之外的那一半（源码 + 实测）

> **`UE5-COLLISION.md` 讲的是**查询**：「能不能打中」。**
> **这篇讲**仿真**：「会不会掉」。**
>
> **实测结论：本项目当前**零物理仿真** —— 全关。这是合理的，不是缺陷。**

---

## 一、物理的两个半边（必须分清）

| | 查询（Query） | 仿真（Simulation） |
| --- | --- | --- |
| 回答 | **能不能打中 / 会不会穿过** | **会不会掉 / 会不会滚** |
| 机制 | 碰撞通道 + 响应 + 形状 | **刚体求解器（Chaos）** |
| 每帧成本 | 一次检测 | **持续积分** |
| 关闭方式 | `SetCollisionEnabled(NoCollision)` | `SetSimulatePhysics(false)` |
| 本项目 | ✅ **有**（地形 CTF） | ❌ **全关** |

**两个是**独立的**：物体可以"能被射线打中但不掉"，也可以"掉但不参与查询"。**

---

## 二、仿真的开关（13 个，源码确认全部存在）

**都在 `UPrimitiveComponent` 上（190,729 字节 —— 最大的一个类，因为它同时承载查询和仿真）：**

| 开关 | 作用 |
| --- | --- |
| **`SetSimulatePhysics`** | **总开关** |
| **`SetEnableGravity`** | 受不受重力 |
| `SetMassOverrideInKg` | 质量（否则按密度算） |
| `SetPhysicsLinearVelocity` | 线速度 |
| `SetPhysicsAngularVelocityInDegrees` | 角速度 |
| `AddForce` | 持续的力 |
| `AddImpulse` | **瞬间冲量**（打击感用它） |
| `AddTorqueInDegrees` | 扭矩 |
| `SetLinearDamping` | 线阻尼 |
| `SetAngularDamping` | 角阻尼 |
| `SetCollisionEnabled` | 碰撞开关（仿真也要碰撞才不会穿地） |
| `SetNotifyRigidBodyCollision` | **碰撞时发事件**（做打击音效/特效） |
| `SetConstraintMode` | 约束模式 |

**关键：`SetSimulatePhysics(true)` 只是打开仿真，**还必须 `SetCollisionEnabled` 为 QueryAndPhysics 或 PhysicsOnly**，
否则物体会穿过地面掉下去。**

---

## 三、`UPhysicalMaterial`：手感从哪来

**10,000 字节，字段不多但都是"落地感觉"：**

| 字段 | 作用 |
| --- | --- |
| **`Friction`** | 滑动摩擦（滚动/滑动）|
| **`StaticFriction`** | **静摩擦**（推不推得动）|
| **`Restitution`** | **弹性**（0 = 不弹，1 = 完美弹）|
| `Density` | 密度（换算质量）|
| `RaiseMassToPower` | 密度到质量的指数 |
| `FrictionCombineMode` | **两个物体摩擦怎么合**（取大/取小/相乘）|
| `RestitutionCombineMode` | **两个物体弹性怎么合** |

**`FrictionCombineMode` 是个容易忽略的点：**
> **A 的摩擦是 0.5，B 的摩擦是 0.1，接触时用哪个？**
> **`Average`（默认）/ `Min` / `Max` / `Multiply`。**

**这解释了"为什么冰面和石头的摩擦力不是简单相加"。**

---

## 四、`FBodyInstance`：真正的求解器绑定

**79,950 字节 —— 这是 UE 的物理体和 Chaos 之间的桥。**

**关键成员（源码确认）：**
```
bSimulatePhysics          ← 对应上面的总开关
MassInKgOverride          ← 质量覆盖
LinearDamping / AngularDamping
PhysMaterialOverride      ← 物理材质
SleepFamily               ← 睡眠分组（决定多快"睡着"）
```

**`SleepFamily` 值得注意：**
> **物体会"睡着"（停止计算）省性能。
> `SleepFamily` 决定它多快睡、多容易被吵醒。
> **默认族不适合所有东西 —— 一片树叶和一个铁球不该用同一个睡眠参数。**

---

## 五、三个资产类型（物理专用）

| 资产 | 类 | 用途 |
| --- | --- | --- |
| **物理材质** | `UPhysicalMaterial` | 手感参数 |
| **物理约束** | `UPhysicsConstraintComponent`（23,844 B）| **关节**（门轴、绳索、链条）|
| **物理资产** | `UPhysicsAsset`（18,671 B）| **布娃娃**（骨骼怎么和刚体对应）|

### 5.1 物理约束的六种

**`UPhysicsConstraintComponent` 支持的约束（源码里是线性/角度限制的组合）：**

| 类型 | 自由什么 |
| --- | --- |
| 球窝（Ball-Socket） | 任意方向转 |
| 铰链（Hinge） | 单轴转（门）|
| 棱柱（Prismatic） | 单轴滑（抽屉）|
| 固定（Fixed） | 全锁 |
| 距离（Distance） | 保持距离（绳）|
| 6DOF | 六自由度分别设 |

### 5.2 布娃娃（PhysicsAsset）

**这是"角色死后摊软"的机制。**

**它做的是：把每根骨骼对应一个胶囊/盒子刚体，再用约束连起来。**

**所以：**
```
SkeletalMesh + PhysicsAsset → 可布娃娃
SkeletalMesh 没有 PhysicsAsset → 死了就是站着（或播个死亡动画）
```

---

## 六、🔴 本项目实测：零物理仿真

**跑 `Tools/audit_level_physics.py` 的结果：**

```
PHYS: actors 110
PHYS: primitive components by mobility: MOVABLE 26, STATIC 98
PHYS: simulating physics: 0
PHYS: gravity enabled: 0
PHYS: with a physical material override: 0
PHYS: physics constraints: 0
PHYS: skeletal meshes with a physics asset: 0
```

### 6.1 怎么解读

| 数字 | 含义 |
| --- | --- |
| 124 个图元组件 | 26 可移动 + 98 静态 |
| **仿真 0 个** | **没有任何东西会掉** |
| 重力 0 个 | 同上（`enable_gravity` 只在仿真时才有意义）|
| 物理材质 0 个 | 没有摩擦/弹性的差异化 |
| 约束 0 个 | 没有门轴、绳索 |
| 布娃娃 0 个 | 没有骨骼网格（还没导入）|

### 6.2 这是**对**的，不是缺陷

**理由：**

| 项 | 为什么不需要 |
| --- | --- |
| 建筑 / 地形 | **静态几何，不该动** |
| 玩家 | **用 `CharacterMovementComponent`，它是运动学的**，不是刚体 |
| 怪物 | 同上（还没做） |
| 掉落物 | 目前没有物理化的拾取物 |

**`CharacterMovementComponent` 是一个关键点：**
> **角色的移动是**运动学**的 —— 它用碰撞查询（扫掠）来移动，不是让物理引擎推它。
> **所以"角色能站在地上"和"仿真开关"无关** —— 那是碰撞查询在工作。**
>
> **这也解释了为什么本项目碰撞全开、仿真全关，但玩家能正常走路。**

---

## 七、什么时候需要打开仿真

| 场景 | 需要什么 |
| --- | --- |
| **掉落物要滚动/堆积** | `SetSimulatePhysics` + 物理材质 |
| **可破坏物碎块飞散** | 同上 + `AddImpulse` |
| **怪物死后布娃娃** | `UPhysicsAsset` + 布娃娃 |
| **门要能推开** | `UPhysicsConstraintComponent`（铰链）|
| **绳索/锁链** | 距离约束 |
| **打击感（顿帧/击退）** | `AddImpulse`（不需要全开仿真）|

**按 P0 范围，只有"掉落物"和"打击感"可能需要。
两者都不急。**

---

## 八、掌握程度（物理）

| 内容 | 掌握 |
| --- | --- |
| 查询 vs 仿真的区别 | 🟢 **清楚** |
| 13 个仿真开关 | 🟢 **列全（源码确认）** |
| `UPhysicalMaterial` 的 7 个关键字段 | 🟢 **清楚** |
| **两个 CombineMode 的意义** | 🟢 **清楚** |
| `FBodyInstance` 的职责 | 🟢 **清楚** |
| `SleepFamily` 的意义 | 🟢 **清楚** |
| 三种物理资产 | 🟢 **清楚** |
| **六种约束** | 🟢 **清楚** |
| **本项目的物理状态** | 🟢 **实测（零仿真）** |
| **`CharacterMovementComponent` 是运动学的** | 🟢 **关键认知** |
| **实际做过一个刚体** | 🔴 **没做过** |
| **做过布娃娃** | 🔴 **没做过** |

**物理：从"只懂碰撞"到 **60%**（碰撞 70% + 仿真 50%）。**

---

## 九、下一步（如果要动手）

**最小验证：在广场上放一块会掉的箱子。**

```
1. 在离地 3 米处 spawn 一个 Cube
2. SetSimulatePhysics(true) + SetCollisionEnabled(QueryAndPhysics)
3. 给一个 UPhysicalMaterial（摩擦 0.6）
4. 进 PIE，看它掉下来并停住
5. 加 AddImpulse 推一下，看它滚
```

**⚠️ 需要 PIE 才能看到（编辑器里物理不 tick）。**

**这一步能验证：仿真开关 + 物理材质 + 碰撞三者协同。**

---

## 十、重查命令

```powershell
python Tools\map_physics.py              # 物理类与开关
py "Tools/audit_level_physics.py"        # 本项目的物理状态
```
