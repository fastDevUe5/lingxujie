# UE5 子系统：代码放哪（引擎源码核实）

> **子系统回答的是「这段代码属于谁的寿命」这个问题。**
> **放错层的症状往往看起来无关：状态莫名重置、编辑器里留了旧数据、工具只能用一次。**
>
> **数据来自 `Tools/map_subsystems.py`。**

---

## 一、四层（实测继承与钩子）

| 类 | 继承 | 头文件 | 生命周期钩子 |
| --- | --- | --- | --- |
| `UEngineSubsystem` | `UDynamicSubsystem` | 765 B | 少（继承来的） |
| `UEditorSubsystem` | `UDynamicSubsystem` | 777 B | 少（继承来的） |
| **`UWorldSubsystem`** | `USubsystem` | **4,216 B** | **6 个** |
| `UTickableWorldSubsystem` | `UWorldSubsystem` | 同上 | 6 + Tick |
| `UGameInstanceSubsystem` | `USubsystem` | 632 B | 少 |
| `ULocalPlayerSubsystem` | `USubsystem` | 936 B | 少 |

**`UWorldSubsystem` 的头文件有 4,216 字节，是其余几个的 5 倍 —— 因为它钩子最多：**

```
Initialize
Deinitialize
OnWorldBeginPlay
ShouldCreateSubsystem
DoesSupportWorldType
Tick
```

**钩子多说明它的生命周期最复杂 —— 也说明它是最常用的那一层。**

---

## 二、四层的寿命对比

```
UEngineSubsystem        ← 整个进程（编辑器开着就在）
   ↓
UEditorSubsystem        ← 编辑器会话（只存在于编辑器）
   ↓
UGameInstanceSubsystem  ← 一次"开始游戏"，跨关卡存活
   ↓
UWorldSubsystem         ← 一个世界，切关卡就销毁
   ↓
ULocalPlayerSubsystem   ← 一个本地玩家（分屏时一人一个）
```

**横向对比：**

| 想存多久 | 用哪层 | 典型用途 |
| --- | --- | --- |
| 整个编辑器进程 | `UEngineSubsystem` | 全局缓存、后台服务 |
| 编辑器会话 | `UEditorSubsystem` | **工具窗口、资产校验器** |
| 一次游戏（跨关卡） | `UGameInstanceSubsystem` | **存档、玩家档案、设置** |
| 一个关卡 | `UWorldSubsystem` | 关卡逻辑、刷怪管理 |
| 一个本地玩家 | `ULocalPlayerSubsystem` | 分屏玩家的输入/UI |

---

## 三、怎么判断该用哪层（三个问题）

**按顺序问：**

```
① 这东西需要 Tick 吗？
   ├─ 需要 → 用 `UTickableWorldSubsystem`（它专门给 Tick 支持）
   └─ 不需要 → 继续问

② 换关卡时该保留吗？
   ├─ 该保留 → `UGameInstanceSubsystem`
   └─ 该销毁 → `UWorldSubsystem`

③ 只在编辑器里用吗？
   ├─ 是 → `UEditorSubsystem`
   └─ 不是 → `UEngineSubsystem`（很少用）
```

**本项目对照：**

| 我们的组件 | 为什么是组件不是子系统 |
| --- | --- |
| `ULXJHealthComponent` | 它属于**一个 Actor** —— 血量是每只怪各自的 |
| `ULXJProgressComponent` | 同理，经验属于角色 |
| `ULXJInventoryComponent` | 同理，背包属于角色 |

**组件 vs 子系统的判据：**

| | 组件 | 子系统 |
| --- | --- | --- |
| 归属 | **一个 Actor** | 整个引擎/编辑器/世界 |
| 数量 | 每个 Actor 一份 | **自动单例** |
| 获取 | `Actor->FindComponentByClass()` | `GetSubsystem<T>()` |
| 需要挂载 | ✅ 挂在 Actor 上 | ❌ 自动创建 |

**一句话：**
> **"这只怪的血量" → 组件**
> **"所有怪的血量怎么计算" → 子系统**

---

## 四、取用方式

```python
# Python
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)   # 编辑器
engine = unreal.get_engine_subsystem(unreal.SomeEngineSubsystem)     # 引擎
```

```cpp
// C++
UMyWorldSubsystem* Sub = GetWorld()->GetSubsystem<UMyWorldSubsystem>();
UMyGameInstanceSubsystem* GI = GetGameInstance()->GetSubsystem<UMyGameInstanceSubsystem>();
```

**⚠️ 编辑器子系统和运行子系统的取法**不同**：**
- 编辑器（`UEditorSubsystem`）→ `unreal.get_editor_subsystem()`
- 引擎（`UEngineSubsystem`）→ `unreal.get_engine_subsystem()`
- 世界/GameInstance → 从 `World` / `GameInstance` 上取

**这也解释了为什么 `unreal.UnrealEditorSubsystem` 只能 `get_editor_subsystem` 拿到。**

---

## 五、`ShouldCreateSubsystem` 和 `DoesSupportWorldType`

**`UWorldSubsystem` 独有这两个钩子 —— 它们决定"这个子系统在这个世界里要不要创建"。**

| 钩子 | 用途 |
| --- | --- |
| `ShouldCreateSubsystem` | 返回 `false` 就不创建（可用于按配置关闭）|
| `DoesSupportWorldType` | 按世界类型过滤（游戏世界 / 编辑器世界 / PIE / 预览）|

**`DoesSupportWorldType` 很关键：默认情况下，编辑器里编辑关卡时和 PIE 运行时**世界类型不同**。
写"只在游戏里生效"的逻辑，可以在这里排除编辑器世界。**

**这条能避免一类常见 bug：编辑器里好好的，一进游戏就重复执行。**

---

## 六、本项目的实际使用

| 子系统 | 我们怎么用 |
| --- | --- |
| **`unreal.UnrealEditorSubsystem`** | 视口相机（`set_level_viewport_camera_info`） |
| **`unreal.LevelEditorSubsystem`** | PIE 控制（`editor_request_end_play`）、存盘 |
| **`unreal.EditorActorSubsystem`** | Actor 增删查 |
| **`unreal.StaticMeshEditorSubsystem`** | Nanite、碰撞设置 |
| **`unreal.EditorAssetSubsystem`** | 资产加载/删除 |

**注意：这些全是**编辑器**子系统 —— 因为我们的脚本都跑在编辑器里。
运行时逻辑（组件、GameMode）是另一套。**

---

## 七、基类关系（已核实）

**`Subsystem.h`（2,903 字节）里只有三个类，但它们是整个体系的地基：**

```
UObject
 └ USubsystem                      ← 有 Initialize / Deinitialize
    ├ UDynamicSubsystem            ← 多一个 ShouldCreateSubsystem
    │   ├ UEngineSubsystem
    │   └ UEditorSubsystem
    └ UWorldSubsystem              ← 钩子最多（6 个）
       ├ UTickableWorldSubsystem
       ├ UGameInstanceSubsystem
       └ ULocalPlayerSubsystem
```

**⚠️ 注意：`UGameInstanceSubsystem` 直接继承 `USubsystem`，不是 `UWorldSubsystem`。**
**所以它**不随关卡销毁** —— 这正是"跨关卡数据放 GameInstance"的机制来源。**

**`UDynamicSubsystem` 只比 `USubsystem` 多一个 `ShouldCreateSubsystem`：**
**返回 `false` 就可以让整个子系统不创建（按配置开关功能时用）。**

### 已确认的钩子归属

| 钩子 | 在哪个基类 |
| --- | --- |
| `Initialize` / `Deinitialize` | `USubsystem`（**所有子系统都有**）|
| `ShouldCreateSubsystem` | `UDynamicSubsystem` + `UWorldSubsystem` |
| `OnWorldBeginPlay` / `DoesSupportWorldType` / `Tick` | **`UWorldSubsystem` 独有** |

---

## 八、还没验证的

| 问题 | 状态 |
| --- | --- |
| 引擎源码里直接继承各子系统的类有多少 | 脚本扫出来是 0 —— 说明**游戏代码不写在引擎源码里**，这个统计口径不对 |
| `FSubsystemCollection` 的初始化顺序 | 未读（头文件 11,158 字节） |

**第二条值得看一眼 —— 子系统之间的初始化顺序会影响"谁能引用谁"。**

---

## 九、重查命令

```powershell
python Tools\map_subsystems.py
```
