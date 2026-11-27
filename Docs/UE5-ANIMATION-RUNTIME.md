# UE5 动画运行时：播放 / 切换 / 混合 / 通知（引擎源码核实）

> **前一篇讲的是**资产**（数据怎么存、怎么写入）。**
> **这一篇讲**运行时**：动画怎么被播、怎么切换、怎么混合、怎么在特定帧触发事件。**
>
> **这是「能导入」和「能用」的差别。**

---

## 一、五个类的分工（实测规模）

| 类 | 头文件 | 职责 |
| --- | --- | --- |
| **`UAnimInstance`** | **98,676 B** | **动画的运行实例**（每个角色一个）|
| `UAnimMontage` | 39,517 B | **单次播放的动画**（攻击、受击）|
| `UBlendSpace` | 39,704 B | **按参数混合多个动画**（走/跑过渡）|
| `UAnimNotify` | 4,583 B | **在某一帧触发事件** |
| `UAnimNotifyState` | 4,986 B | **在一段帧区间内持续** |
| `UAnimationStateMachineLibrary` | 5,036 B | 状态机的运行时查询/切换 |
| `FAnimNode_StateMachine` | 13,520 B | 状态机节点本体 |

**`UAnimInstance` 的 98,676 字节是这批里最大的 —— 因为它承载全部运行时状态。**

---

## 二、`UAnimInstance` —— 运行实例

### 2.1 它负责什么

**每个有骨骼网格的角色，运行时都有一个 `UAnimInstance`。**

| 它管 | 说明 |
| --- | --- |
| 骨骼变换 | `GetLocalSpaceTransform` / `GetComponentSpaceTransform` |
| 姿态快照 | `AddPoseSnapshot` / `GetPoseSnapshot` |
| 蒙太奇槽位 | `GetSlotMontageGlobalWeight` / `LocalWeight` |
| 同步组 | `GetSyncGroupMapRead` |
| 曲线 | `GetAnimationCurves` |
| 并行求值 | `IsRunningParallelEvaluation` |

**"槽位"（Slot）是一个关键概念：**
> **槽位是默认动画图和蒙太奇之间的**插入点**。**
> **默认图在槽位那里暂停，等蒙太奇播完再接回去。**

**`GetSlotMontageGlobalWeight` = 蒙太奇在某个槽位上占多少权重。**
**这就是"攻击动作盖住走路动作"的机制。**

### 2.2 姿态快照（Pose Snapshot）

```
AddPoseSnapshot / RemovePoseSnapshot / GetPoseSnapshot
```

**用途：** 把某一帧的姿态**冻住**，之后可以从这个姿态继续。
**做"死亡定格"、"击中顿帧"时用。**

---

## 三、`UAnimMontage` —— 单次播放

### 3.1 为什么需要它

| | 普通 `AnimSequence` | `AnimMontage` |
| --- | --- | --- |
| 循环 | 可以 | 通常单次 |
| 分段 | 无 | **有 Section（可跳到某段）** |
| 混合 | 靠状态机 | **自带权重与混合时间** |
| 适用 | 走/跑/待机 | **攻击/受击/技能** |

**本项目需要的正是后者** —— 墨香有大量攻击动作，都是一次性播放。

### 3.2 关键方法

```
GetCurrentSectionIndex            ← 当前在第几段
GetRemainingPlayTimeToSectionEnd  ← 这段还剩多久
GetCurrentSectionEndPosition
GetWeight / GetDesiredWeight / GetBlendTime   ← 混合控制
MontageSync_Follow / StopLeading / StopFollowing  ← 多个角色的攻击同步
```

**`MontageSync_*` 值得注意 —— 它让多个角色**同步播放同一段蒙太奇**。
**墨香是武侠游戏，双人合击/对招可能用到这个。**

---

## 四、`UBlendSpace` —— 按参数混合

### 4.1 它解决什么问题

**走路和跑步不是一个动作，是两个。**
**中间速度怎么办？**

**`UBlendSpace` 就是"按一个参数（比如速度）在两个动作之间插值"。**

| 方法 | 作用 |
| --- | --- |
| `GetRange` | 参数范围（比如速度 0–600）|
| `GetGridSize` | 网格采样数 |
| `GetSamples1D` / `GetSamples2D` | 采样点 |
| `GetBlendParameter` | 混合参数定义 |
| `GetSamplePlayLength` | 每个样本的时长 |
| `GetPerBoneInterpolationData` | **按骨骼差异化插值** |

**`GetPerBoneInterpolationData` 很有意思 —— 可以让**不同骨骼用不同插值**，
比如身体混合快、脚混合慢（防止脚滑）。**

### 4.2 本项目的情况

**墨香 4,056 个动画里，走/跑是分开的文件。**
**要做平滑过渡，`UBlendSpace` 是标准做法。**

---

## 五、`UAnimNotify` 和 `UAnimNotifyState` —— 在特定帧触发

### 5.1 两者区别

| | `UAnimNotify` | `UAnimNotifyState` |
| --- | --- | --- |
| 触发时机 | **某一帧，一次性** | **一段帧区间，开始和结束各一次** |
| 典型用途 | **播放音效、生成投射物** | **无敌帧、持续伤害判定** |
| 头文件 | 4,583 B | 4,986 B |

### 5.2 它们提供什么

```
GetNotifyName                 ← 名称
GetDefaultTriggerWeightThreshold  ← 触发权重阈值
GetEditorColor / GetEditorComment
GetWorld / GetContainingAsset
```

**注意：这两个类**本身很轻**（不到 5 KB）—— 因为它们只是"标记"，
实际行为由子类实现。**

### 5.3 对本项目的意义

**墨香的特效脚本有 3,268 个，每个都是"在动作的某几帧做什么"。**

**UE 的对应机制就是 Notify：**
- "第 15 帧播剑气音效" → `UAnimNotify`
- "第 12–18 帧是伤害窗口" → `UAnimNotifyState`

**所以墨香特效脚本 → UE Notify 是一条自然的映射路径。**

---

## 六、状态机：默认动画图怎么切

### 6.1 `UAnimationStateMachineLibrary`（5,036 B，蓝图可调）

```
SetState / GetState                 ← 切状态 / 查状态
IsStateBlendingIn / IsStateBlendingOut
GetRelevantAnimTimeRemaining
GetRelevantAnimTimeRemainingFraction
```

**这是**蓝图里**调状态机的接口（`SetState` 可以从代码强制切换）。**

### 6.2 `FAnimNode_StateMachine`（13,520 B，C++ 内部）

```
GetCurrentState / GetCurrentStateName / GetCurrentStateElapsedTime
GetStateWeight / GetStateInfo / GetTransitionInfo
IsTransitionActive / SetState / SetStateInternal
UpdateTransitionStates / IsAConduitState
```

**"Conduit State"（导管状态）是一个容易忽略的概念：**
> **导管是一个**不播放动画**的状态，只用来做条件判断。
> **它的作用是让多个转移共享同一套条件。**

**本项目做"攻击→受击→死亡"的切换时会用到。**

### 6.3 状态机从哪来

**`UAnimBlueprintGeneratedClass` 有 `GetBakedStateMachines` ——
状态机是**动画蓝图编译时烘焙**进去的，不是运行时构造的。**

**所以：**
```
UAnimBlueprint（资产，编辑器里编辑）
   ↓ 编译
UAnimBlueprintGeneratedClass（生成的类，含烘焙状态机）
   ↓ 实例化
UAnimInstance（每个角色一个）
```

---

## 七、本项目的动画链路（完整图）

```
墨香 .anm（三条轨道，已解）
   ↓
FBX 或 glTF（转换器，待写）
   ↓
SkeletalMeshTools.import_file(import_animations=True)
   ↓
UAnimSequence + USkeleton（资产，已学怎么存）
   ↓
   ├→ 挂到 UBlendSpace（走/跑混合）
   ├→ 做成 UAnimMontage（攻击/受击）
   └→ 配 UAnimNotify（在特定帧触发特效/音效）
   ↓
UAnimBlueprint（状态机，决定何时播哪个）
   ↓
UAnimInstance（运行时，每个角色一个）
   ↓
角色动起来
```

**每一环现在都有对应的文档或已验证的工具。**

---

## 八、掌握程度（动画运行时）

| 内容 | 掌握 |
| --- | --- |
| `UAnimInstance` 的职责（槽位/快照/同步组） | 🟢 **清楚** |
| **槽位（Slot）机制 —— 蒙太奇如何覆盖默认图** | 🟢 **清楚** |
| `UAnimMontage` 的段与权重 | 🟢 **清楚** |
| `UBlendSpace` 的混合原理 | 🟢 **清楚** |
| **Notify / NotifyState 的区别与用途** | 🟢 **清楚**，且看出它和墨香特效脚本的对应 |
| 状态机的三态（普通/导管/转移） | 🟢 **清楚** |
| 状态机是从蓝图烘焙的 | 🟢 **清楚** |
| **实际创建过一个动画蓝图** | 🔴 **没做过** |
| **实际配过一个 BlendSpace** | 🔴 **没做过** |
| **实际写过 Notify 子类** | 🔴 **没做过** |

**总体：动画运行时从 30% → **50%**。**

**涨的部分：机制层面全清楚了，能说出完整链路。
没涨的部分：**一个都没动手做过**。**

**这和我对编辑器脚本的掌握有本质区别 —— 那边我建过工具、跑通过；
这边只是读懂了。**

---

## 九、下一步（该动手了）

**学到这里，动画的四层（格式 → 资产 → 运行时 → 链路）都懂了，但零实操。**

**最小动手验证（不需要墨香数据，用引擎自带素材）：**

```
1. 用引擎自带的 Mannequin 或随便一个 SkeletalMesh
2. 建一个 AnimBlueprint，加一个简单状态机
3. 建一个 AnimMontage，加一个 Notify
4. 在 PIE 里播一次，截图为证
```

**这一步过了，"动画运行时"才算真会。**

**⚠️ 但这条和本项目的实际需求顺序有冲突：
项目真正卡的是**墨香动画导入**（格式转换），不是动画蓝图。**

**所以两条路并行：**
- **主线：** `.anm → glTF`（解决导入）
- **副线：** 用引擎素材练一次动画蓝图（补上实操）

---

## 十、重查命令

```powershell
python Tools\map_animation_runtime.py
```
