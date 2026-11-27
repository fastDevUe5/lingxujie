# UE5 Gameplay 框架：从关卡加载到玩家能操作（引擎源码核实）

> **前一篇文章讲"这五个类各是什么"。这篇讲"它们的调用顺序"。**
> **顺序搞错是"玩家出生点不对""输入没反应"这类问题的根源 —— 而且都不报错。**
>
> **14 个步骤全部在头文件里逐一确认过。**

---

## 一、完整流程（14 步，源码确认）

```
① UGameInstance::Init                    ← 一次游戏会话开始
      ↓
② UWorld::BeginPlay                      ← 世界开始运行
      ↓
③ UWorld::SpawnActor                     ← 生成 Actor（GameMode 就在这里被生成）
      ↓
④ AGameModeBase::InitGame                ← GameMode 初始化（读配置、建规则）
      ↓
⑤ AGameModeBase::PostLogin               ← 玩家登录（这时才有 PlayerController）
      ↓
⑥ AGameModeBase::HandleStartingNewPlayer ← 决定怎么"开始"这个玩家
      ↓
⑦ AGameModeBase::RestartPlayer           ← 让玩家重生（核心步骤）
      ↓
   ┌── ⑦a ChoosePlayerStart               ← 选出生点
   └── ⑦b SpawnDefaultPawnFor             ← 生成 Pawn
      ↓
⑧ AGameModeBase::RestartPlayerAtPlayerStart  ← 在出生点放 Pawn
      ↓
⑨ APlayerController::SetPawn              ← Controller 拿到身体
      ↓
⑩ APawn::PossessedBy                      ← Pawn 知道自己被控制了
      ↓
⑪ APlayerController::AcknowledgePossession ← 客户端确认（联机时才有意义）
      ↓
⑫ AActor::BeginPlay（各 Actor）           ← 游戏逻辑从这里开始
      ↓
⑬ 每帧：APlayerController::PlayerTick → AActor::Tick
```

**⚠️ 注意 ⑫：`BeginPlay` 在**所有生成和占有之后**才跑。
所以 `BeginPlay` 里能拿到 Controller 和 Pawn。**

---

## 二、对本项目的直接对应

**我们的实现：**

| 引擎步骤 | 我们的代码 |
| --- | --- |
| ③ 生成 GameMode | `ALXJGameMode`（`LXJGameMode.h`） |
| ⑦ 重生玩家 | 引擎默认流程（没重写） |
| ⑦a 选出生点 | **`MX_PLAYERSTART`**（我们在 `build_moxiang_map.py` 里放的） |
| ⑨ SetPawn | 引擎默认 |
| ⑫ BeginPlay | `ALXJCharacter` 里的初始化 |

**日志验证过：**
```
[LingXuJie] Player ready at V(X=4000.00, Y=-8830.49, Z=3684.00) (level 1)
```

**这行日志是在哪里打的？在 `ALXJCharacter` 的 `BeginPlay` 里 ——
所以它出现就说明**①到⑫全走完了**。**

---

## 三、可重写的钩子（按类分，源码确认）

**这是"改游戏逻辑该写在哪"的清单：**

### 3.1 `AActor`

```
BeginPlay                    ← 游戏开始
EndPlay                      ← 结束
Tick                         ← 每帧
PostInitializeComponents     ← 组件都建好后
OnConstruction               ← 编辑器里拖动时也跑
```

**⚠️ `OnConstruction` 在**编辑器里**也会跑，所以不要在里面写"游戏开始才该做"的事。
这是新手常见错误。**

### 3.2 `APawn`

```
PossessedBy                  ← 被控制时
UnPossessed                  ← 被放开时
Restart                      ← 重生
SetupPlayerInputComponent    ← 绑定输入（关键）
```

**`SetupPlayerInputComponent` 是输入绑定唯一正确的地方。**
**写在 `BeginPlay` 里也能跑，但会被重置。**

### 3.3 `APlayerController`

```
BeginPlay
SetupInputComponent          ← 绑定输入的另一半
OnPossess / OnUnPossess      ← 占有/释放 Pawn
AcknowledgePossession        ← 联机专用
PlayerTick                   ← 每帧（早于 Actor Tick）
```

### 3.4 `AGameModeBase`

```
InitGame                                  ← 初始化规则
PostLogin                                 ← 玩家登录
HandleStartingNewPlayer                   ← 怎么开始玩家
RestartPlayer                             ← 重生
ChoosePlayerStart                         ← 选出生点（重写它就能改出生逻辑）
SpawnDefaultPawnFor                       ← 决定生成什么 Pawn
```

**🔴 `ChoosePlayerStart` 和 `SpawnDefaultPawnFor` 是最常重写的两个：**

| 想做什么 | 重写哪个 |
| --- | --- |
| 按条件选不同出生点 | `ChoosePlayerStart` |
| 玩家生成时就带某个配件 | `SpawnDefaultPawnFor` |
| 禁止某些情况重生 | `RestartPlayer` |

### 3.5 `AGameStateBase`

```
HandleBeginPlay          ← 只有一个（状态复制用）
```

**GameState 的钩子很少 —— 因为它只负责"广播状态"，不负责逻辑。**

---

## 四、三个容易搞错的点（都有实测依据）

### 4.1 `BeginPlay` 在编辑器里**不执行**

**这条之前已写进 `UE5-CORE-ARCHITECTURE.md`，这里重申：**
**编辑器打开关卡时 `BeginPlay` 不跑，只有 PIE 或运行时跑。**

**所以"编辑器里看不到效果"不等于"代码错了"。**

### 4.2 输入绑定必须在 `SetupPlayerInputComponent`

**写在 `BeginPlay` 里：
- 单机可能能跑
- 但 Pawn 被重新 Possess 后会失效

**正确位置是 `SetupPlayerInputComponent`（`APawn`）或 `SetupInputComponent`（`PlayerController`）。**

### 4.3 `OnConstruction` 编辑器也会跑

**它用于"在编辑器里摆的时候就要看效果"的东西（比如程序化生成的几何）。
不要在里面改游戏状态。**

---

## 五、本项目的 Gameplay 现状

| 项 | 状态 |
| --- | --- |
| `ALXJGameMode` | ✅ 有（设置默认 Pawn 和 HUD） |
| `ALXJCharacter` | ✅ 有（越肩相机、技能输入、冲刺/闪避/滑翔） |
| `ALXJHUD` | ✅ 有（Canvas HUD） |
| `ALXJGameState` | ❌ **没有**（单机不需要复制状态） |
| 出生点 | ✅ `MX_PLAYERSTART` |
| 重生逻辑 | ⚠️ 引擎默认（没自定义） |

**所以流程是"引擎默认跑通，我们没有重写任何一步"。**

**这解释了为什么 `Player ready at ...` 能打出来 —— 走的是标准路径。**

---

## 六、掌握程度（Gameplay 框架）

| 内容 | 之前 | 现在 |
| --- | --- | --- |
| 五个类的职责 | 🟢 清楚 | 🟢 清楚 |
| **14 步调用顺序** | 🔴 不知道 | 🟢 **逐一源码确认** |
| **每类可重写的钩子** | 🟡 部分 | 🟢 **列全** |
| **`BeginPlay` 在编辑器不跑** | 🟢 知道 | 🟢 重申 |
| **输入绑定该写哪** | 🔴 不知道 | 🟢 **清楚** |
| **`OnConstruction` 编辑器也跑** | 🔴 不知道 | 🟢 **清楚** |
| **重写过 `ChoosePlayerStart`** | 🔴 | 🔴 **没重写过** |
| 自定义重生逻辑 | 🔴 | 🔴 **没做过** |

**Gameplay 框架：从"知道五个类"到 **65%**。**

**涨的是"顺序和钩子清楚"，没涨的是"没重写过任何一个"。**

---

## 七、下一步（如果要动手）

**最小验证：重写 `ChoosePlayerStart` 让玩家随机出生。**

```
1. 在 LXJGameMode 里重写 ChoosePlayerStart
2. 返回关卡里随机一个 PlayerStart
3. 放三个 PlayerStart 在城里不同位置
4. PIE 跑三次，看每次出生点不同
```

**这一步能验证：重写钩子生效 + 流程理解正确。**

**⚠️ 但这会改 C++，要编译。改之前要问人。**

---

## 八、重查命令

```powershell
python Tools\map_gameplay_flow.py
```
