# UE5 核心架构（引擎源码核实）

> **本文的目的：把"谁继承谁、谁拥有谁、谁 tick"讲清。
> 90% 的 UE 困惑都来自这张图没在脑子里。**
>
> **所有数字来自 `Tools/map_core_object_model.py` 扫 `Engine/Source` 的结果。**

---

## 一、继承链（实测，非记忆）

```
UObjectBase → UObjectBaseUtility → UObject
                                    │
    ┌───────────────────────────────┼──────────────────────────┐
    │                               │                          │
 AActor                      UActorComponent               UWorld
 (159 UFUNCTION)                    │                    (3 UFUNCTION)
    │                          USceneComponent                 │
    │                         (62 UFUNCTION)              ULevel
    │                               │                    (0 UFUNCTION)
    │                        UPrimitiveComponent
    │                        (165 UFUNCTION)
    │
    ├── APawn ── ACharacter
    │   (34)      (49)
    │
    ├── AHUD  (29)
    │
    ├── AInfo
    │    ├── AGameModeBase (29)
    │    └── AGameStateBase (10)
    │
    └── AController
         └── APlayerController (164)
```

**另两条独立支线：**
```
UObject → UEngine (0 UFUNCTION / 372 UPROPERTY)
UObject → UGameInstance (6 / 6)
```

---

## 二、四个"最容易搞混"的概念

### 2.1 `AActor` vs `UActorComponent`

| | `AActor` | `UActorComponent` |
| --- | --- | --- |
| 能不能放进关卡 | ✅ 能（有 Transform 的那个） | ❌ 不能单独存在 |
| 有自己的位置吗 | ✅ | ❌（`USceneComponent` 才有）|
| 生命周期 | `BeginPlay` / `Tick` / `EndPlay` | `BeginPlay` / `TickComponent` / `EndPlay` |
| 典型用途 | 门、怪、玩家、灯光 | 血量、背包、技能 |

**一句话：Actor 是"场景里的东西"，Component 是"挂在东西上的能力"。**

### 2.2 `USceneComponent` vs `UPrimitiveComponent`

**这是分层，不是并列：**

```
UObject
 └ UActorComponent        ← 有 tick，没有位置
    └ USceneComponent     ← 有位置（Transform），但看不见
       └ UPrimitiveComponent  ← 有形状、材质、碰撞，能看见
```

| 类 | 有位置 | 有形状/材质 | 例子 |
| --- | --- | --- | --- |
| `UActorComponent` | ❌ | ❌ | `ULXJHealthComponent` |
| `USceneComponent` | ✅ | ❌ | `USpringArmComponent` |
| `UPrimitiveComponent` | ✅ | ✅ | `UStaticMeshComponent` |

**实测依据：**
```
UPrimitiveComponent.h  190,729 字节  165 UFUNCTION  127 UPROPERTY
USceneComponent.h       93,497 字节   62 UFUNCTION   32 UPROPERTY
UActorComponent.h       67,671 字节   27 UFUNCTION   21 UPROPERTY
```
**层层递增 —— 每往下一层就多一批能力。**

### 2.3 `UWorld` vs `ULevel`

| | `UWorld` | `ULevel` |
| --- | --- | --- |
| 是 | **世界容器**（管时间、物理、网络、tick） | **一张"地图块"**（存 Actor 列表） |
| 数量 | 一个世界可以有多个 Level | 一个 Level 属于一个 World |
| 典型 | `GetWorld()` 拿到的 | 流送关卡、子关卡 |
| 头文件 | 211,135 字节 | 64,362 字节 |

**本项目的关系：**
```
UWorld（一个游戏世界）
 └ ULevel（/Game/Maps/LingXuJie —— 我们的关卡）
      └ 110 个 Actor
```

### 2.4 `UGameInstance` vs `UEngine` vs `UWorld`

**生命周期长度：**

```
UEngine        ← 整个编辑器/游戏进程，最长
  └ UGameInstance   ← 一次"开始游戏"，跨关卡存活
      └ UWorld      ← 一个世界，切关卡就换
          └ ULevel  ← 一个地图块
```

**实际用途：**

| 想存什么 | 存哪 |
| --- | --- |
| 跨关卡的数据（存档槽、玩家档案） | **`UGameInstance`** |
| 只在当前关卡有效 | `AGameState` 或 Actor |
| 编辑器工具状态 | 编辑器子系统 |

---

## 三、Gameplay 框架：五个类的职责

**实测代码量（UFUNCTION / UPROPERTY）：**

| 类 | UFUNCTION | UPROPERTY | 职责 |
| --- | --- | --- | --- |
| `AGameModeBase` | 29 | 18 | **规则**：用什么 Pawn、怎么开局、怎么重生 |
| `AGameStateBase` | 10 | 8 | **状态**：比分、时间、玩家列表（要复制给客户端的）|
| `APlayerController` | **164** | 64 | **玩家意志**：输入、相机、UI 交互 |
| `APawn` | 34 | 20 | **身体**：能被控制的东西 |
| `ACharacter` | 49 | 66 | **人形身体**：自带移动组件 + 胶囊 |
| `AHUD` | 29 | 16 | **画 2D**（本项目用的是 Canvas HUD）|

**关键区分：**

| 容易混的 | 区别 |
| --- | --- |
| GameMode vs GameState | GameMode **只在服务端存在**；GameState **会复制到客户端** |
| Pawn vs Character | Pawn 是"可被控制的东西"（可以是车、飞船）；Character **是有移动组件的人形 Pawn** |
| PlayerController vs Pawn | Controller 是"意志"，Pawn 是"身体"。**死亡时 Controller 可以换个 Pawn 继续** |

### 3.1 "GameMode 只在服务端"—— 用源码验证过

**不引用传闻，查的是"这个类有没有声明复制属性"：**

| 头文件 | `GetLifetimeReplicatedProps` | 含义 |
| --- | --- | --- |
| **`GameModeBase.h`** | **❌ 没有** | **不复制 → 只在服务端** |
| **`GameStateBase.h`** | **✅ 有** | **复制 → 客户端能看到** |
| `PlayerController.h` | ✅ 有 | 复制 |
| `Pawn.h` | ✅ 有 | 复制 |
| `Character.h` | ✅ 有 | 复制 |
| **`HUD.h`** | **❌ 没有** | **纯客户端渲染，不需要复制** |
| `Info.h` | ❌ 没有 | 只是一个基类 |
| `Actor.h` | ✅ 有 | 所有 Actor 的复制机制都在这里 |

**重查命令：`python Tools\check_replication_flags.py`**

**为什么 `bReplicates` 等在头文件里显示 `-`：** 那些标志是在 `.cpp` 构造函数里赋值的，
头文件里只有声明。**所以判据要用 `GetLifetimeReplicatedProps` —— 它声明在头文件里。**

**`APlayerController` 有 164 个 UFUNCTION —— 是这五个里最多的。
它是"玩家在游戏里的全部接口"，所以名字里带 Controller 不是偶然。**

---

## 四、生命周期顺序（哪个先，哪个后）

```
① 引擎启动
   UEngine::Init

② 开始游戏
   UGameInstance::Init
   ↓
③ 加载关卡
   UWorld::BeginPlay
   ↓
④ 关卡里的 Actor
   对每个 Actor：
     PostInitializeComponents()   ← 组件都建好了
     BeginPlay()                  ← 游戏逻辑从这里开始
   ↓
⑤ 每帧
   Tick(DeltaSeconds)            ← Actor
   TickComponent(DeltaSeconds)   ← 组件
   ↓
⑥ 结束
   EndPlay()
   ↓
⑦ 关关卡
   UWorld 销毁
```

**⚠️ 重要事实：编辑器里打开关卡时，`BeginPlay` **不执行** —— 只有 PIE 或运行时才执行。**
**所以"我在编辑器里看得到但游戏里没有"这类问题，先查它是不是写在 `BeginPlay` 里。**

---

## 五、`UObject` 层的基础能力

**`UObject.h` 81,890 字节，但只有 1 个 UFUNCTION 和 0 个 UPROPERTY —— 这是对的。**

**`UObject` 的价值不在暴露给蓝图，在于它提供：**

| 能力 | 说明 |
| --- | --- |
| **反射** | 运行时能查类型、属性、函数 |
| **序列化** | 自动存读盘 |
| **垃圾回收** | 引用计数 + GC |
| **网络复制** | `UPROPERTY(Replicated)` |
| **编辑器集成** | 属性面板自动生成 |

**这就是为什么"几乎所有东西都继承 UObject" —— 继承一次，五样能力全有。**

---

## 六、本项目的映射

| 引擎类 | 我们的实现 |
| --- | --- |
| `AActor` | `ALXJMonster` / `ALXJPickup` |
| `ACharacter` | `ALXJCharacter` |
| `AHUD` | `ALXJHUD`（Canvas HUD） |
| `UActorComponent` | `ULXJHealthComponent` / `ULXJProgressComponent` / `ULXJInventoryComponent` / `ULXJCombatComponent` |
| `AGameModeBase` | `ALXJGameMode` |
| `USceneComponent` | 角色的 `CameraBoom`（`USpringArmComponent`） |
| `UPrimitiveComponent` | 角色的 `BodyMesh`（`UStaticMeshComponent`） |

**所以 AGENTS.md 里那张"代码地图"其实就是在填上面这张表。**

---

## 七、怎么自己重查

```powershell
python Tools\map_core_object_model.py
```

**脚本读 `Engine/Source` 里的类声明，提取继承列表、统计 UFUNCTION/UPROPERTY 数量。
引擎升级后重跑即可。**

---

## 八、还没深入的（下一块）

| 主题 | 状态 |
| --- | --- |
| 子系统的四层（Engine / Editor / World / GameInstance） | 下一块 |
| 渲染（Nanite / Lumen / 材质图） | 待学 |
| 物理与碰撞 | 待学 |
| 音频 | 待学 |
| UI（UMG / Slate） | 待学 |
| 网络复制 | 待学 |
