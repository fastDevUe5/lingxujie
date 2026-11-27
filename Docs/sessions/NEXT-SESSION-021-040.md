# NEXT-SESSION 归档 · 第 21–40 节

> 从 `Docs/NEXT-SESSION.md` 分出来的历史（2026-11-27）。**当前状态看主文件。**

## 21. UE5 第四轮：网格合并实测 + 找 API 的正确方法（2026-11-26 19:30）

### 一、网格合并：学会了，然后决定不用

**实测结果：**
```
MERGE: found 96 building actors
MERGE: merged mesh SM_SM_Lanzhou_City, material slots 96
合并后：64,740 三角形 / 85,522 顶点 / 96 个材质槽
```

**🔴 最重要的认知：合并**减 actor，不减 draw call**。**

> **96 actor + 96 材质 = 96 次 draw call**
> **1 actor + 96 材质 = 仍然 96 次 draw call**

**所以合并的真实收益只有两个：大纲整洁、整座城能一起移动。**

**决定：不采用。** 理由：
1. 对 draw call 无帮助
2. 96 个 actor 便于单独调整
3. 96 不算多

**合并产生的 asset 留在磁盘（`SM_SM_Lanzhou_City`），actor 已删除，关卡恢复原状。**

### 二、🔴 本轮最大的方法收获：找 API 读引擎工具的实现

**踩了三个坑才找对合并 API：**
```
1. EditorLevelLibrary.merge_actors        -> 不存在
2. MeshMergingSettings.generate_lightmap_uv -> 属性不存在
3. 正确答案：StaticMeshEditorSubsystem.merge_static_mesh_actors(actors, options)
```

**怎么找到的：读引擎自带 `SceneTools.merge_actors` 的实现 —— 它内部就这么调。**

> **引擎自己的 217 个工具是**最好的 API 示例**，
> 因为它们只能调用真实存在的方法。**

**这条已写进 `Docs/UE5-MESH-MERGE.md` 第六节，应该进开工流程。**
**已加入 `AGENTS.md` 规则 0 的查询顺序（见下）。**

### 三、新增文档

| 文档 | 大小 |
| --- | --- |
| **`UE5-MESH-MERGE.md`** | 4.9 KB |

### 四、掌握度更新

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **网格合并** | 0 | **70%**（跑通 + 有判断）|

### 五、下一步（转向实操）

| 顺位 | 任务 | 说明 |
| --- | --- | --- |
| 1 | 清理 107 个遗留资产 | 先查 referencers |
| 2 | 音频接入关卡（背景音 + 环境音）| 有 SoundClass 了 |
| 3 | 动画实操 | 等 .mod 蒙皮 |


## 22. UE5 第五轮：Gameplay 流程 + 输入系统 + 一个重要更正（2026-11-26 19:45）

### 一、新增两篇

| 文档 | 内容 |
| --- | --- |
| **`UE5-GAMEPLAY-FLOW.md`** | **从关卡加载到玩家能操作的 14 步**（全部源码逐一确认）|
| **`UE5-INPUT.md`** | 输入的三代方案 + **本项目用第一代** |

### 二、Gameplay 流程（14 步，源码确认）

```
GameInstance::Init → World::BeginPlay → SpawnActor → GameMode::InitGame
→ PostLogin → HandleStartingNewPlayer → RestartPlayer
→ [ChoosePlayerStart + SpawnDefaultPawnFor] → RestartPlayerAtPlayerStart
→ PlayerController::SetPawn → Pawn::PossessedBy → AcknowledgePossession
→ Actor::BeginPlay → 每帧 PlayerTick / Tick
```

**关键：`BeginPlay` 在**所有生成和占有之后**才跑，所以里面能拿到 Controller 和 Pawn。**

**我们的日志 `Player ready at V(...)` 就是 `BeginPlay` 打的 ——
它出现就说明 ①到⑫ 全走完了。**

### 三、🔴 发现本项目的输入矛盾

```
LXJCharacter.cpp:
  SetupPlayerInputComponent  0 处
  BindAction                 0 处
  IsInputKeyDown            18 处
  EKeys::                   20 处
```

**角色在 `Tick` 里轮询 `PC->IsInputKeyDown(EKeys::W)`，完全绕过输入系统。**

**但 `Config/DefaultInput.ini` 第 86-87 行写着：**
```ini
DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput
DefaultInputComponentClass=/Script/EnhancedInput.EnhancedInputComponent
```

**引擎装的是第三代 Enhanced Input，我们在用第一代轮询。**

**判断：P0 不改。** 理由：键鼠够用、改要编译、现在改不会让游戏变好。
**该改的时机：做设置面板（改键）之前 —— 那时轮询做不出来。**

### 四、🔴 一个必须记下的更正

**我先前写「107 个遗留资产待清理」—— **这是错的**。**

**实测：**
```
jp_roof00            -> Texture2D   被 M_LZ_JP_ROOF00 引用
17_101_stonew01      -> Texture2D   被 M_LZ_17_101_STONEW01 引用
```

**它们是被材质实例引用的**贴图**，不是遗留资产。
按我的判断去删，**整座城的贴图会全部丢失。**（gotcha #75）**

**正确构成（实测）：**
| 类别 | 数量 |
| --- | --- |
| `SM_LZ_*` 网格 | 96 |
| `M_LZ_*` 材质实例 | 95 |
| `M_Moxiang_*` 母材质 | 4 |
| 贴图 | 104 |
| **合计** | **299** |

**教训：删之前必须查 `get_asset_class` + `get_referencers`，两个都查完才知道能不能删。**

### 五、掌握度更新

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **Gameplay 流程** | 60% | **65%**（14 步 + 钩子全清）|
| **输入系统** | 0 | **45%**（三代方案 + 本项目的选择）|

### 六、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频接入关卡 | 有 SoundClass 体系了 |
| 2 | Lumen | 渲染 35% 里最大空白 |
| 3 | 动画实操 | 等 .mod 蒙皮 |


## 23. UE5 第六轮：物理仿真（2026-11-26 20:00）

### 一、新增文档

| 文档 | 大小 | 内容 |
| --- | --- | --- |
| **`UE5-PHYSICS.md`** | ~9 KB | 查询 vs 仿真两半分 + 13 个开关 + 物理材质 + 约束 + 布娃娃 |

### 二、🔴 核心认知：物理是两个独立的半边

| | 查询 | 仿真 |
| --- | --- | --- |
| 回答 | 能不能打中 | 会不会掉 |
| 机制 | 通道 + 响应 + 形状 | **刚体求解器（Chaos）** |
| 本项目 | **全开**（地形 CTF）| **全关** |

**两个独立：物体可以"能被射线打中但不掉"，也可以"掉但不参与查询"。**

### 三、实测：本项目零物理仿真

```
PHYS: actors 110
PHYS: primitive components: 26 MOVABLE + 98 STATIC = 124
PHYS: simulating physics:              0
PHYS: gravity enabled:                 0
PHYS: physical material override:      0
PHYS: physics constraints:             0
PHYS: skeletal meshes with physics asset: 0
```

**这是**对的**，不是缺陷。理由：**

**① 城市是静态几何**
**② 玩家用 `CharacterMovementComponent` —— 它是**运动学**的**

**关键认知：**
> **角色的移动不是"物理引擎推它"，而是"用碰撞查询扫掠着移动"。**
> **所以碰撞全开 + 仿真全关，玩家照样能站在地上走路。**

### 四、物理材质的两组容易忽略的参数

| 参数 | 意义 |
| --- | --- |
| `StaticFriction` vs `Friction` | **静摩擦**（推不推得动）vs **滑动摩擦** |
| `FrictionCombineMode` | **两个物体接触时摩擦怎么合**（平均/取大/取小/相乘）|

**所以"冰面 + 石头"的摩擦不是简单相加 —— 由 CombineMode 决定。**

### 五、踩到的坑

| # | 坑 |
| --- | --- |
| **76** | 遍历 `PrimitiveComponent` 时不能假设都有仿真属性（`ArrowComponent` 没有）|

### 六、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **物理（碰撞部分）** | 70% | 70% |
| **物理（仿真部分）** | 0 | **50%** |
| **物理合计** | — | **60%** |

### 七、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | **Lumen** | 渲染 35% 里最大的空白 |
| 2 | 音频接入关卡 | 有 SoundClass 体系 |
| 3 | 动画实操 | 等 .mod 蒙皮 |


## 24. UE5 第七轮：Lumen —— 一个被我自己搞错的「零」（2026-11-26 20:15）

### 一、更正：Lumen 从第一天就在跑

**我之前说「Lumen 是零」。错的。**

**`Config/DefaultEngine.ini` 实测：**
```ini
r.DynamicGlobalIlluminationMethod=1     ; = Lumen GI
r.ReflectionMethod=1                    ; = Lumen 反射
r.Shadow.Virtual.Enable=1               ; 虚拟阴影贴图
r.GenerateMeshDistanceFields=True       ; Lumen 软件光追的前提
r.AllowStaticLighting=False             ; 全动态光照
r.AntiAliasingMethod=4                  ; = TSR
r.DefaultFeature.AutoExposure=False     ; 固定曝光（截图可复现）
```

**枚举（`EngineTypes.h` 源码核实）：**
```
EDynamicGlobalIlluminationMethod:  0=None  1=Lumen  2=ScreenSpace(废弃)  3=Plugin
EReflectionMethod:                 0=None  1=Lumen
```

**所以场景光照好看不是「默认天光凑合」，是 Lumen 在算间接光。**

### 二、Lumen 的硬前提（源码注释原文）

> *Requires 'Generate Mesh Distance Fields' enabled for Software Ray Tracing
> and 'Support Hardware Ray Tracing' enabled for Hardware Ray Tracing.*

**两条路：**
| 路径 | 前提 | 本项目 |
| --- | --- | --- |
| 软件光追（SDF） | `r.GenerateMeshDistanceFields=True` | ✅ 已开 |
| 硬件光追 | `r.Lumen.HardwareRayTracing=True` + 显卡支持 | ❌ 关着 |

**「网格距离场」= 把每个网格预处理成体素化的「离表面多远」，
光线在场里走比在三角形里走快几个数量级 —— 这是软件光追能实时的原因。**

**代价：勾了距离场的网格构建变慢、内存占用上升（地形 524,288 面尤其明显）。**

### 三、配置文件里还有一条重要注释

```ini
; Revisit for the MMO scale test (P0.5) - Lumen is expensive with many players on screen.
```

**这说明配置时就意识到了 MMO 规模问题。不是忘了，是**知道并推迟决定**。**

### 四、待办：Lumen 的 MMO 规模问题

| 方案 | 做法 |
| --- | --- |
| A. 只用 Lumen 做主角附近 | 远处切烘焙 |
| B. 全烘焙 + 少量动态 | 关 Lumen |
| C. 混合 | 室内 Lumen、室外烘焙 |

**P0.5 测试时必须重新决定。现在不做。**

### 五、踩到的坑

| # | 坑 |
| --- | --- |
| **77** | Lumen 软件光追依赖「生成网格距离场」，两者必须同时开 |

### 六、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **渲染（含 Lumen）** | 35% | **55%** |

**涨的：Lumen 原理、两个独立开关、距离场前提、本项目配置、MMO 代价。
没涨的：没实际调过任何 Lumen 参数。**

### 七、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频接入关卡（背景音 + 环境音）| 有 SoundClass 体系 |
| 2 | 动画实操 | 等 .mod 蒙皮 |
| 3 | 关闭 Lumen 做一次对比截图 | **需重启编辑器，要先问人** |

## 25. UE5 第八轮：配置审计工具 + 防再犯（2026-11-26 20:30）

### 一、新增工具与文档

| 产出 | 说明 |
| --- | --- |
| **\Tools/audit_project_config.py\** | **输出 92 个配置键 + 来源文件 + 枚举解读** |
| **\Docs/UE5-PROJECT-CONFIG.md\** | 全项目配置一张表 |

### 二、为什么做这个

**我前两轮判断错了两次，原因完全一样：凭印象不读文件。**

| 轮次 | 我说 | 实际 |
| --- | --- | --- |
| 第 5 轮 | 「107 个遗留资产」 | 是被材质实例引用的**贴图** |
| 第 7 轮 | 「Lumen 是零」 | .DynamicGlobalIlluminationMethod=1\，一直在跑 |

**两次都只用读 14 KB 的 ini 就能定论。**

### 三、工具输出（实测）

\92 个配置键，全部带来源文件
渲染 - 全局光照   r.DynamicGlobalIlluminationMethod  1 (Lumen)
渲染 - 反射       r.ReflectionMethod                 1 (Lumen)
渲染 - 抗锯齿     r.AntiAliasingMethod               4 (TSR)
渲染 - 网格距离场 r.GenerateMeshDistanceFields       True
输入 - 输入组件类 DefaultInputComponentClass        EnhancedInput
\
### 四、顺带发现的一个不一致

\RayTracingMode = Full              <- 引擎级光追打开
r.Lumen.HardwareRayTracing = False  <- 但 Lumen 不用硬件光追
\
**两者不矛盾（RayTracingMode 管非 Lumen 的 RT 特性），但容易误解。
实际状态：Lumen 全软件光追。**

### 五、已写进 AGENTS.md 开工流程第 0 步

> **判断「某个功能有没有开」之前，先跑 \python Tools\\audit_project_config.py\。**

**gotcha #78 记录了完整教训和四步查证顺序：**
\1. Config/*.ini              <- 有没有开
2. get_asset_class           <- 这是什么
3. get_referencers           <- 谁在用
4. Saved/Logs/*.log          <- 运行时报了什么
\
### 六、掌握度

**本轮不是学新知识，是**堵住一个反复犯的错误**。
配置审计这一层现在有了工具和文档，不需要再靠记忆。**

## 26. UE5 第九轮：兰州城有了背景音乐（2026-11-26 20:45）

### 一、实测结果

`
MUSIC: imported bg_field.mp3 as SoundWave (95.2 s)
MUSIC: sound class set to SC_Music
MUSIC: ambient actor placed with S_bg_field
MUSIC: level saved
MUSIC: verify: sound=S_bg_field auto_activate=True volume=0.60
`

**关卡验证：**
`
MX_AMBIENT_MUSIC (AmbientSound)     <- 新加的
MX_CHARACTER (LXJCharacter)
MX_TERRAIN (StaticMeshActor)
`

### 二、为什么用 AmbientSound 而不是一次性播放

| 需求 | 一次性 | **AudioComponent** |
| --- | --- | --- |
| 循环 | 否 | **是** |
| 能停止 | 否 | **是** |
| 能调音量 | 否 | **是** |
| 跟随玩家 | 否 | **是** |

**背景音乐四条都要，所以必须用组件。**

### 三、⚠️ 发现体积问题（gotcha #79）

`
bg_field.mp3        1,488 KB   (源)
S_bg_field.uasset  11,410 KB   (导入后)
`

**涨了 7.7 倍。UE 默认不对 MP3 转成的 SoundWave 做有损压缩。**

**12 首 BGM 会到 132 MB。打包前必须处理**（三条缓解措施已记入 gotcha）。

### 四、可用的 12 首 BGM

| 文件 | 用途 |
| --- | --- |
| g_field.mp3 | **野外（已用）** |
| BG_Town1/2/3.mp3 | 城镇 |
| BG_Battle.mp3 | 战斗 |
| g_login.mp3 | 登录 |
| jangan.mp3 | **长安**（地图 12）|
| BG_Dungeon1.mp3 | 地牢 |
| BG_Titan01/Intro.mp3 | BOSS |

### 五、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **音频** | 50% | **60%** |

**涨的：mp3 导入、关卡有音乐、发现体积问题。
没涨的：压缩质量、3D 衰减、MetaSounds。**

### 六、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 音频压缩质量配置 | 打包前必做 |
| 2 | 动画实操 | 等 .mod 蒙皮 |
| 3 | Lumen 参数对比 | 需重启编辑器，先问人 |

## 27. UE5 第十轮：音频压缩实测 + 第三次自我更正（2026-11-26 21:00）

### 一、真实数据（日志的压缩行才是运行时大小）

`
质量 80: S_bg_field 压缩为 17.39%（从 17,851KB 到 3,103KB）
质量 40: S_bg_field 压缩为 12.59%（从 17,851KB 到 2,247KB）
`

| 项 | 值 |
| --- | --- |
| 源波形（PCM） | 17,851 KB |
| **质量 80 运行时** | **3,103 KB** |
| **质量 40 运行时** | **2,247 KB**（小 28%）|
| uasset 磁盘 | 11,140 KB ← **编辑器侧源波形** |

### 二、修正了两个错误

| 错误 | 更正 |
| --- | --- |
| 「mp3 导入涨 7 倍」 | **uasset 存编辑器源波形，不是运行时数据** |
| 「压缩设置无效」 | **确实有效：质量 80→40，运行时 3,103→2,247 KB（-28%）** |

**12 首 BGM 按质量 40 算约 **27 MB 运行时**，不是 132 MB。**

### 三、元教训：**这是我第三次同类错误**

| 轮次 | 错误 | 共同点 |
| --- | --- | --- |
| 5 | 「107 个遗留资产」 | **数字是真的，但被当成了别的东西** |
| 7 | 「Lumen 是零」 | 同上 |
| 10 | 「音频涨 7 倍」 | 同上 |

**gotcha #80 记录了报数字前必须问的三个问题：**
`
1. 这个数字是谁的？（文件？内存？运行时？打包后？）
2. 它随时间/设置变化吗？
3. 有没有第二个来源能对上？
`

### 四、已完成的修复

- compression_quality 从 80 改为 **40**（已保存）
- loading_behavior 设为 RETAIN_ON_LOAD
- gotcha #79 已替换为实测版本
- UE5-AUDIO.md 第 10.4 节已更正

### 五、掌握度

| 域 | 上一轮 | 本轮 |
| --- | --- | --- |
| **音频** | 60% | **65%**（含压缩实测）|
| **工程素养（报数字的严谨性）** | — | **本轮重点** |

### 六、下一步

| 顺位 | 任务 | 备注 |
| --- | --- | --- |
| 1 | 把其余 11 首 BGM 都设成质量 40 | 可批量做 |
| 2 | 动画实操 | 等 .mod 蒙皮 |
| 3 | 打包一次看真实 pak 大小 | 需关编辑器，先问人 |

## 28. UE5 第十一轮：API 体量实测 —— 目标分母被修正（2026-11-26 21:15）

### 一、实测推翻了引用了很多轮的数字

`
module attributes:       11,509
classes:                 11,459      <- 实测
callables (not class):       49
total callable members: 330,365      <- 真正的 API 面
`

**文档记的是 11,675，差 216（1.8%）。方向对，但不精确 —— 已更正。**
**（这是第四次引用未验证的数字，见 gotcha #80。）**

### 二、三个影响判断的发现

**① 类数严重高估知识量**

| 类 | 方法数 |
| --- | --- |
| MathLibrary | **728** |
| SkeletalMeshComponent 及 7 个派生类 | **各 471**（继承重复）|

**同一批方法在多个类里重复出现。**

**② 本项目真正相关的只有 ~870 个类**

按实际工作推导（Actor ~200、资产 ~100、材质 ~120、音频 ~60、
物理 ~50、输入 ~40、动画 ~80、UI ~60、渲染 ~80、数学 ~80）。

**870 / 11,459 = 7.6%。这才是真实分母。**

**③ 但按使用频次加权，覆盖已经很高**

**本项目最常用的 20 个类，全部实际用过并验证过，
覆盖编辑期 80%+ 的操作。**

### 三、诚实的掌握度表述

| 说法 | 准不准 |
| --- | --- |
| 「精通 11,459 个类」 | **不可能，也不是目标** |
| 「本项目相关 ~870 个类，掌握约 17%」 | **有依据** |
| 「按频次加权覆盖编辑期 80%+」 | **有依据** |
| 「系统性读过十个领域源码」 | **21 篇文档为证** |

### 四、目标从不可测变成可测

| 之前 | 现在 |
| --- | --- |
| 「对标 11,675 个类」（模糊） | **「对标本项目 ~870 个类」（可完成）** |

### 五、下一步该学什么（结论变了）

**不是学「更多类」，是学「本项目没碰过的领域里最高频的类」：**

| 顺位 | 领域 | 理由 |
| --- | --- | --- |
| **1** | **动画（471 方法的大类）** | **且 .mod 转换是硬阻塞** |
| 2 | UMG（56 个 Widget 类） | 古风 UI 做不出来 |
| 3 | 后处理（350 字段已读未调） | 观感 |
| 4 | 网络 | P0 不需要 |

### 六、新增文档

| 文档 | 内容 |
| --- | --- |
| **UE5-API-INVENTORY.md** | 实测体量 + 分布 + 掌握路径 + 诚实的百分比 |
| Tools/inventory_python_api.py | 可重跑的盘点工具 |


## 29. 第十二轮：`.mod` 容器格式确证（2026-11-26 21:30）

### 一、之前三种块头长度全错

试过 28 / 30 / 12 字节 —— **全错。正确的块头是 8 字节。**

```
+0  u32  block_type    (标记符)
+4  u32  block_size    (载荷字节数，不含这 8 字节)
+8  载荷开始
```

### 二、标记不是常量 —— 这是走不通的真正原因

| 标记 | 类型 |
| --- | --- |
| **0x00F00000** | **MATERIAL** |
| **0xF5000000** | **BONE** |
| **0xF4000000** | **MESH** |

**按标记分类后，块数与文件头声明精确匹配：**

```
jp03_dht00: 声明 4 骨骼 -> 走到 4 个 BONE 块   OK
w25260:     声明 38 骨骼 -> 走到 38 个 BONE 块 OK
```

### 三、两个新规则（两个文件都成立）

**① 对象数 = 材质数 + 骨骼数（不含网格）**

```
jp03:  1 + 4  = 5   OK
w25260: 1 + 38 = 39 OK
```

**② 骨骼块倒序存储，载荷第一个 int 是骨骼编号**

```
jp03: [1] word0=4, [2] word0=3, [3] word0=2, [4] word0=1
```

**倒序意味着网格里的骨骼索引可能也从后往前算 —— 这解释了以前对不上父骨骼。**

### 四、推翻了旧文档两条结论

| 旧说法 | 实际 |
| --- | --- |
| 「+36 开始是法线」 | **法线在载荷靠后位置，且有多组单位向量** |
| 「头后面 20 个零 + 名字」 | **名字在载荷里，不在头里** |

### 五、蒙皮权重仍未解 —— 但卡点变精确了

**三种扫描（u8 和=255 / u16 和=65535 / f32 和=1.0）都没匹配。**

**可能原因：**
1. 每顶点影响数不是 4
2. 权重不归一化（原引擎存原始值）
3. 索引与权重交错存

**下一步（明确，不是「继续试」）：**

```
1. 提取所有 .mod 的 MESH 载荷
2. 统计每组单位向量数组的长度
3. 找长度 == 顶点数 x 影响数 的那个数组
4. 用值域/单调性区分骨骼索引 vs 权重
```

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/parse_mod.py` | 走完全部块（8 字节头）|
| `Tools/classify_mod_blocks.py` | 按标记分类 + 载荷首几字 |
| `Tools/find_unit_normals.py` | 单位向量数组定位 |
| `Tools/brute_mod_layout.py` | 暴力验证走法 |

### 七、掌握度

| 项 | 上一轮 | 本轮 |
| --- | --- | --- |
| **`.mod` 容器格式** | 走不通 | **确证** |
| **块类型标记** | 未知 | **三种已分类** |
| **网格载荷结构** | 错（旧结论） | **未知，但知道法线在后面** |
| **蒙皮权重** | 未解 | **未解（卡点更精确）** |

## 30. 第十三轮：批量扫描排除两种浮点布局（2026-11-26 22:00)

### 一、先按骨骼数过滤（之前漏了）

| 类别 | 数量 |
| --- | --- |
| bones = 0（道具/特效）| 3,412 |
| **bones > 0（有骨架）** | **1,893** |
| bones > 60（角色体型）| 1,385 |

**第一批扫的是字母序前 40 个，几乎全是 bones=0 —— 那是布景的结构，不是角色的。**

### 二、两个否定结论

| 假设 | 结果 |
| --- | --- |
| 法线是 f32 单位向量 | **多数角色找不到** |
| 法线是 f16 半精度 | **全部找不到（0 个）** |

**少数模型确实有 f32 法线（19240.mod 有 348 个），所以格式支持，但多数不用。**

### 三、新假设：法线字节量化

> 每个法线 3 个 u8，[-1,1] 映射到 [0,255]，加载时归一化。

**依据：2000 年代引擎标准做法；f32/f16 都扫不到；载荷大小比例吻合。**

### 四、下一轮的第一件事（具体测试，不是方向）

`
对每个角色载荷，假设:
  位置 = f32 x 3 x vertexcount
  法线 = u8  x 3 x vertexcount
遍历 vertexcount，检查法线段每个三元组归一化后长度是否约为 1.0
`

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| Tools/batch_mod_meshes.py | 批量提取载荷 + 单位向量数组列表 |
| Tools/compare_mesh_layouts.py | 按骨骼数分组对比 |



## 31. 第十四轮：`.mod` 网格与蒙皮格式**完全解开**（2026-11-26 22:30）

### 一、结果：四文件逐字节验证通过

| 文件 | 顶点 | 面组 | 骨骼记录 | 影响数 | 法线 | tail |
| --- | --- | --- | --- | --- | --- | --- |
| `216.mod` | 517 | 2 | 669 | {1:180, 2:229, 3:108} | **517/517** | **0** |
| `19240.mod` | 348 | 1 | 0 | — | **348/348** | **0** |
| `choco.mod` | 190 | 6 | 174 | {1:118, 2:72} | **190/190** | **0** |
| `108_bird.mod` | 146 | 2 | 134 | {1:132, 2:14} | **146/146** | **0** |

**四条验证标准全过：法线 100% 单位长度、权重 0..1、骨骼索引在范围、字节精确消耗完。**

### 二、完整读取顺序（源码 + 实测）

```
FILE_BASE_OBJECT_HEADER   324 字节  (dwIndex 4 + NODE_TM 184 + children 4 + parent 4 + name 128)
FILE_MESH_HEADER           48 字节
positions                  12 x V
uvs                         8 x T
extIndices                  4 x E
faceGroups                 每組 28 字节头 + 2*faces*3 + 8*lightUV1 + 8*lightUV2
FILE_PHYSIQUE_HEADER       12 字节
PHYSIQUE_VERTEX x n         5 字节each  (bBonesNum u8 + 起始索引 u32)
BONE x boneNum             44 字节each (索引 u32 + 权重 f32 + 3xVECTOR3)
normals                    12 x V     <- 在最后
```

### 三、🔴 为什么之前四轮全错

**三个错误叠在一起：**

| 错误 | 实际 |
| --- | --- |
| 网格头是 36 字节 | **48 字节** |
| 载荷直接从网格头开始 | **前面有 324 字节基类头** |
| 面组是 `[count][indices]` | **28 字节 7 字段头** |

**而蒙皮扫不到的根本原因：**
> **`PHYSIQUE_VERTEX.bBonesNum` 每顶点**可变**（1~3）。
> `108_bird.mod` 有 132 个顶点只受 1 个骨骼影响 —— 刚性绑定是常态。**

**我一直假设「固定 4 个影响、权重之和 = 255/1.0」，所以永远扫不到。**

### 四、🔴 更重要的教训：答案在源码里

**研究区 `client_src\tw\4DyuchiGXGeometry\` 有**完整客户端 C++ 源码**：**
```
geom_obj.cpp     -- CMeshObject::ReadFile
object.cpp       -- CBaseObject::ReadFile
face_group.cpp   -- CFaceGroup::ReadFile
Physique.cpp     -- CPhysique::ReadFile   <- 蒙皮，15 行
typedef.h        -- BONE / PHYSIQUE_VERTEX / NODE_TM
```

**`FORMAT-REFERENCE.md` 里甚至摘录了这些源码。**

**我把「研究区是数据仓库」当成「研究区只有数据」。实际它有一手源码。**

**→ gotcha #81：逆向任何格式前，先查研究区有没有读取代码。**

### 五、动画路径现在通了

**之前阻塞的三个未知：**

| 未知 | 状态 |
| --- | --- |
| 蒙皮权重格式 | ✅ **解开** |
| 骨骼层级来源 | ✅ **`dwParentObjectIndex` 在基类头 +192** |
| `.anm` 帧率 | 🟡 仍未知，但不阻塞 |

**剩下的是纯工程：写 glTF 导出器。**
**每顶点 `bBonesNum` 个影响要**补齐到 4** 才能写 glTF 的 `JOINTS_0`/`WEIGHTS_0`。**

### 六、新增文档与工具

| 产出 | 说明 |
| --- | --- |
| **`Docs/MOD-FORMAT-SOLVED.md`** | 完整格式参考（含源码出处）|
| `Tools/verify_mod_layout.py` | 逐字节验证（四样本，tail=0）|
| `Docs/MOD-SKIN-STATUS.md` | 保留为历史（含四轮失败的记录）|

## 32. 第十五轮：.mod → UE 骨骼网格全链路跑通（2026-11-26 23:00)

### 一、结果：鸟在兰州城里

`
导出: 108_bird.mod (9 bones, 146 verts, 190 tris) -> bird.gltf + bird.bin
导入: Interchange import completed
生成: SK_Bird (SkeletalMesh) + SK_Bird_Skeleton (9 bones) + SK_Bird_PhysicsAsset
验证: bone count=9 / bounds (75.1, 55.5, 68.1)
`

**截图 Saved/bird_front.png：画面上方可见。**

### 二、两个导入坑

| # | 坑 |
| --- | --- |
| **82** | SkeletalMeshTools.import_file 钉死 FBX 工厂，不认 glTF |
| — | 	ask.imported_object_paths 是字符串不是对象 |

**正解：AssetImportTask 不给 factory -> Interchange。**

### 三、导出器做了什么

| 转换 | 规则 |
| --- | --- |
| 位置 | (x, z, -y) x 0.01（Z朝上厘米 -> Y朝上米）|
| 法线 | (x, z, -y) |
| UV | (u, 1-v)（glTF 原点在左上）|
| 权重 | BonesNum(1~3) 补齐到 4，归一化 |
| 层级 | dwParentObjectIndex，0xFFFFFFFF = 根 |

**逆绑定矩阵当前写的是单位矩阵** —— 静态展示够用，做动画时要算真的。

### 四、下一批

| 任务 | 说明 |
| --- | --- |
| **批量导出** | 现在一次一个，5,305 个要脚本化 |
| 材质 | 导入警告「未指定材质的图元」|
| 动画 | .anm -> glTF animation |
| 逆绑定矩阵 | 动画姿态不对时再算 |

### 五、新增文档

| 文档 | 内容 |
| --- | --- |
| **MOD-TO-UE-PIPELINE.md** | 全链路参考（导出/导入/验证三段）|


## 33. 第十六轮：`.anm` 动画格式解开 + 帧率 = 30 fps（2026-11-26 23:30）

### 一、两个结论

**① `.anm` 容器结构与 `.mod` 同构**

```
[文件头（长度不固定！）]
[0xF000 块 × N]        每块 = 8 字节头（marker 0xF000 + size）+ 152 字节 FILE_MOTION_OBJECT_HEADER + 关键帧
[尾部资源引用]
```

**⚠️ 头长度**不固定**：`108_birda.anm` 里第一个块在 **206**，不是研究区文档说的 160。
160..206 之间是堆地址 —— 写入时把运行时指针也 dump 了。
**所以必须扫描 `00 F0 00 00` 找块，不要假设偏移。**

**② 帧率 = 30 fps（推导）**

```
Bone07 位移:  ticks=160/480/800  frame=0/2/4  → 160 ticks/帧
跨 60 个文件统计:  distinct ticks-per-frame = [1.0, 160.0]  ← 几乎全是 160
4800 ticks/秒 ÷ 160 = 30.0 fps   ← 唯一干净整数
```

**4800 是 3ds Max 的 `TICKS_PER_SECOND`，而墨香骨架是标准 Biped（`Bip01 R Finger` 出现 16,052 次）。**

**→ 时间换算：`time_seconds = ticks / 4800.0`**

### 二、字节数学精确验证

**`108_birda.anm` 全部 11 块，每块 `expected == size`：**

```
152 + 136×24            = 3416  ✓  （纯旋转轨）
152 + 136×24 + 135×20   = 6116  ✓  （旋转 + 位移轨）
```

**11 块无一块不吻合。**

### 三、关键帧结构（源码 `CMotionObject::ReadFile`）

```c
struct FILE_MOTION_OBJECT_HEADER {   // 152 字节
    DWORD dwIndex, dwRotKeyNum, dwPosKeyNum, dwScaleKeyNum, dwAnimatedMeshKeyNum;
    char  szObjectName[128];         // +20
    CMotionFlag motionFlag;          // +148
};

struct POS_KEY   { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Pos; };   // 20
struct ROT_KEY   { DWORD dwTicks; DWORD dwFrame; QUARTERNION Q; };   // 24
struct SCALE_KEY { DWORD dwTicks; DWORD dwFrame; VECTOR3 v3Scale;
                   VECTOR3 v3ScaleAxis; float fScaleAxisAng; };     // 40
```

**顺序：POS → ROT → SCALE（不是 ROT 先）。**

### 四、动画链路现在完整

| 环节 | 状态 |
| --- | --- |
| `.mod` 网格 + 蒙皮 | ✅ 解开（第 14 轮）|
| 导出 glTF | ✅ 验证（第 15 轮）|
| SkeletalMesh in UE | ✅ 鸟已可见（第 15 轮）|
| **`.anm` 动画 + 30fps** | ✅ **本轮解开** |
| 导出动画 glTF | 待做（纯工程）|

### 五、新增文档与工具

| 产出 | 说明 |
| --- | --- |
| **`Docs/ANM-FORMAT-SOLVED.md`** | 完整格式 + 帧率推导 + 伪代码 |
| `Tools/inspect_anm.py` | dump 头部 + 首块 |
| `Tools/scan_anm_blocks.py` | 扫描所有块（不假设头长度）|
| `Tools/parse_anm_motion.py` | 按客户端结构解析 + 逐块验算 |
| `Tools/verify_anm_tickrate.py` | 跨 60 文件统计 → 帧率 |

### 六、下一轮

**写 `.anm` → glTF animation 导出器（纯工程）：**

```
1. 解析 .anm（工具已有）
2. 每个骨骼的 rot/pos/scale 关键帧 → glTF animation channel
3. time = ticks / 4800.0
4. 和网格一起导入（AssetImportTask 不钉 factory）
5. 验证：动画能否播
```


## 34. 第十七轮：**完整管道打通 —— 动画进引擎了**（2026-11-26 24:00）

### 一、结果：一次导入产生四个资产

```
ANIM: import produced 4 assets
  Skeleton        SK_BirdAnim_Skeleton
  SkeletalMesh    SK_BirdAnim
  PhysicsAsset    SK_BirdAnim_PhysicsAsset
  AnimSequence    SK_BirdAnim_Anim        <- 动画序列
```

**日志原文：**
```
LogInterchangeEngine: Display: Interchange import completed
```

**动画长度 `sequence_length = 9.0` 秒 —— 与源文件一致（见第三节）。**

### 二、整个管道

```
mod/108_bird.mod    +   anm/108_birda.anm
       ↓ Tools/export_mod_anim_gltf.py
bird_anim.gltf + bird_anim.bin      （网格 + 动画在一个文件）
       ↓ AssetImportTask（不给 factory → Interchange）
SkeletalMesh + Skeleton + PhysicsAsset + AnimSequence
```

### 三、我算错了一个数字，导出是对的

**导入后长度 9.0 秒，我一开始以为应该是 4.5 秒。**

**实际：**
```
136 个关键帧，间隔 320 ticks
160 ticks/帧  →  每关键帧间隔 2 帧
→ 跨度 = 135 × 2 = 270 帧
→ 270 / 30 = 9.0 秒  ✓
```

**关键帧数 ≠ 帧数。** 又是「数字是真的，但被当成了别的东西」——
和第 5/7/10 轮同一类错误（gotcha #80 的三问法）。

### 四、踩到的坑（gotcha #83）

**glTF 的 `byteLength` 必须在**所有 accessor 写完之后**才算：**

```python
gltf = { ..., "buffers": [{"byteLength": len(binary)}] }   # 算早了
# 之后 add_view() 往 binary 追加动画数据
# → 声明值比实际小 → 导入器报「缓冲文件大小不匹配」
```

**症状像文件损坏，实际是顺序问题。**

### 五、只有 6/9 骨骼有动画轨

```
matched bones: 6 of 9 -> Bone02, Bone01, Bone05, Bone04, Bone07, Bone09
```

**其余 3 根（`Bone03`/`Bone06`/`Bone08`）在 `.anm` 里 `rot=0 pos=0 scale=0` ——
这个动作里它们不动，**不是丢失**。**

### 六、七轮的弧线

| 轮次 | 成果 | 方法 |
| --- | --- | --- |
| 11 | API 体量 11,459 类 | 实测代替引用 |
| 12 | `.mod` 容器 | 暴力搜索 |
| 13 | 排除 f32/f16 法线 | 否定实验 |
| **14** | **`.mod` 完全解开** | **读客户端源码** ← 转折 |
| 15 | 导出 → 骨骼网格可见 | 工程 |
| **16** | **`.anm` + 帧率 30fps** | **先读源码**（#81 生效）|
| **17** | **AnimSequence 进引擎** | 工程 |

### 七、下一批

| 任务 | 说明 |
| --- | --- |
| **批量导出** | 5,305 模型 + 4,014 动画要脚本化 |
| **材质** | 导入警告「未指定材质的图元」|
| **角色模型** | 现在只验证了鸟（9 骨骼）；要试 96 骨骼人形 |
| **逆绑定矩阵** | 当前单位矩阵；姿态不对时再算 |
| **动画蓝图** | 有 AnimSequence 了，可以建状态机 |

### 八、新增文档

| 文档 | 内容 |
| --- | --- |
| **`Docs/MOXIANG-TO-UE-PIPELINE.md`** | 完整管道 + 两格式对照表 + 四个实现细节 |


## 35. 第十八轮：人形角色 — 两个只有复杂模型才暴露的 bug（2026-11-26 24:30）

### 一、结果

**角色**渲染出来了**，但还趴着。两个真 bug 已修。**

### 二、bug 1：只导出第一个网格块

**`198_bobu.mod` 有 **3 个 MESH 块**：**

| 块 | 名字 | 顶点 |
| --- | --- | --- |
| `[2]` | `N012-1` | 164 |
| `[3]` | **`N012`** | **632** ← 主体 |
| `[4]` | `N012-2` | 37 |

**我的导出器取 `meshes[0]` —— 导的是 164 顶点的小零件。**

**症状：包围盒 34.3 × 44.0 × 39.5 cm。**

**修法：每个网格块生成一个 glTF primitive，共用同一个 skin。**

**修后：包围盒 99.6 × 77.8 × 99.4 cm。**

### 三、🔴 bug 2：顶点坐标是世界位置，不是局部坐标

**修完多网格后，角色**完全不渲染** —— actor 位置对、`visible=True`、有材质、骨骼正常。**

**查 glTF 的 `POSITION` min/max：**
```
primitive 0: min=[22.44, 23.98, -0.89]  max=[23.12, 24.77, -0.01]
primitive 1: min=[23.17, 24.58, -1.55]  max=[24.43, 25.67, 0.00]
```

**所有顶点都在 **(23, 25, -1) 米** —— 即 (2300, 2500, -100) 厘米。**

**也就是说 `.mod` 的顶点是**模型在原地图里的世界位置**。
actor 放到 (9100, -6200)，几何实际在 (11400, -3700) —— 画面外。**

**修法：导出时减去顶点中心。**
```python
centre = [sum(p[i] for p in positions) / len(positions) for i in range(3)]
positions = [(p[0]-centre[0], p[1]-centre[1], p[2]-centre[2]) for p in positions]
```

**修后 min/max 全部居中，角色立刻渲染。**

### 四、为什么鸟没暴露这两个 bug

| bug | 鸟为什么没事 |
| --- | --- |
| 只导第一个网格 | 鸟只有 1 个网格块 |
| 顶点不在原点 | 鸟的顶点恰好接近原点 |

> **单一小样本通过，不代表管道正确。**

**这和前面几輪的错误同类：拿一个样本证明规则。**

### 五、还没解决的：朝向（趴着）

**包围盒 99.4 × 77.8 × **54.8** —— Z（高度）最小，人形应该 Z 最大。**

**最可能的原因：**
> **对象的 `NODE_TM` 变换（`fRotAng` / `fRotAxis` / `fPos` / `fScale`）
> 我只写进了节点，没有应用到顶点上。**
> **如果原模型靠对象旋转来"立起来"，顶点本身就是躺着的。**

**下一步：把 NODE_TM 构造成矩阵，乘到顶点上。**

### 六、动画长度核对

```
SK_Bobu_Anim: sequence_length = 10.666666984558105 秒
```

**320 键 × 每帧 1 键 = 320 帧 ÷ 30 fps = **10.67 秒** ✓**

**（鸟是每 2 帧 1 键，136 键 = 270 帧 = 9 秒。两个文件关键帧密度不同。）**

### 七、新增文档与坑

| 产出 | 说明 |
| --- | --- |
| **`Docs/CHARACTER-IMPORT-STATUS.md`** | 两个 bug + 未解决项 + 下一步 |
| **gotcha #84** | 一个模型可能有多个网格块 |
| **gotcha #85** | `.mod` 顶点是世界位置不是局部坐标 |


## 36. 第十九轮：对象变换应用到顶点（2026-11-26 25:00）

### 一、修掉第三个 bug：`NODE_TM` 的 mat4 没作用到顶点

**每个对象的基类头里有 `NODE_TM`（184 字节），含位置 / 旋转轴角 / 缩放 /
**两个准备好的矩阵**（`mat4` 和 `mat4Inverse`）。**

**实测 `198_bobu.mod` 的三个网格：**

| 网格 | fRotAng | fPos | fScale |
| --- | --- | --- | --- |
| `N012-1` | **2.0071 弧度（115°）** | (2278.8, -8.3, 2438.3) | **0.7314** |
| `N012` | 0 | (0, **112.7**, 20.5) | 1.0 |
| `N012-2` | 3.1661 弧度 | (23.7, 0.1, 9.3) | 1.0 |

**各部件靠这个变换摆到位置 —— 有旋转 115° 的，有抬高 112.7cm 的。
不应用它，部件散落、模型趴着。**

**mat4 是**行向量**约定，平移在最后一行：**
```
[-0.3091  0.0000  -0.6629  0.0000]
[ 0.0000  0.7314   0.0000  0.0000]
[ 0.6629 -0.0000  -0.3091  0.0000]
[2278.78  -8.35  2438.33  1.0000]
```

**变换公式：**
```python
x' = x*m[0] + y*m[4] + z*m[8]  + m[12]
y' = x*m[1] + y*m[5] + z*m[9]  + m[13]
z' = x*m[2] + y*m[6] + z*m[10] + m[14]
```

**⚠️ 顺序：先乘 mat4，**再**减顶点中心。**

### 二、修后数据

```
primitive 0: extent=(0.56, 0.58, 0.64) m
primitive 1: extent=(1.26, 1.10, 1.56) m     <- 主体
primitive 2: extent=(1.16, 1.36, 0.43) m
```

**各部分对齐、尺寸合理（1–1.5m）。角色渲染出来了。**

### 三、仍未解决的：外观（不再纠结这一个模型）

**包围盒 79.4 × 77.8 × 76.5 cm —— 近立方体。
直立人形应该 Z 明显大于 X/Y。**

**三种可能：**
1. **`198_bobu` 本来就是小型生物**（31 骨骼 + `Bip01` 命名，可能是宠物/小怪）
2. **坐标轴映射还需调整**（当前 `(x, z, -y)`）
3. 非均匀缩放处理

**决定：不再在这一个模型的外观上花时间。管道已验证（鸟完全正确）。
换一个比例明确的模型再校准朝向。**

### 四、三个 bug 的共通点

| bug | 鸟为什么没暴露 |
| --- | --- |
| 只导第一个网格 | 鸟只有 1 个网格块 |
| 顶点不在原点 | 鸟的顶点恰好接近原点 |
| NODE_TM 没应用 | 鸟的 mat4 恰好是单位矩阵 |

> **单一小样本通过，不代表管道正确。**
> **三个 bug 全是「鸟恰好不需要这个逻辑」造成的。**

### 五、诚实的进度表

| 项 | 鸟 | 人形角色 |
| --- | --- | --- |
| 网格导入 | ✅ | ✅ |
| 骨骼数量正确 | ✅ 9 | ✅ 31 |
| AnimSequence | ✅ | ✅ 10.67s |
| 渲染可见 | ✅ | ✅ |
| **外观正确** | ✅ | ❌ **待校准** |
| 多网格 | 不适用 | ✅ 已修 |
| 对象变换 | 恰好单位矩阵 | ✅ 已修 |

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **换 `w25260.mod`（38 骨骼，真 Biped 名字）验证朝向** |
| 2 | 坐标轴候选对比：`(x,y,z)` / `(x,z,-y)` / `(x,-z,y)` |
| 3 | 逆绑定矩阵（当前单位矩阵）|
| 4 | 批量导出 |

### 七、新增工具与坑

| 产出 | 说明 |
| --- | --- |
| `Tools/inspect_node_tm.py` | dump NODE_TM 与两个矩阵 |
| **gotcha #86** | 对象的 NODE_TM 矩阵必须应用到顶点上 |
| `Docs/CHARACTER-IMPORT-STATUS.md` | 已重写为完整进展记录 |


## 37. 第二十轮：朝向问题关闭 + 40 轮中点盘点（2026-11-26 25:30）

### 一、朝向问题关闭

**原计划：用两种映射各导一次，保留让 Z 最高的那个。**

**实测七个模型（同一套映射）：**

| 文件 | X / Y / Z (cm) | 最高轴 |
| --- | --- | --- |
| `198_bobu` | 126 / 156 / 110 | Y |
| `w25260` | 10 / 20 / 23 | Z |
| `216` | 59 / 134 / 71 | Y |
| `20_eagle_01` | 84 / 177 / 139 | Y |
| `108_bird` | 143 / 111 / 144 | Z |
| `19240` | 174 / 98 / 133 | X |
| `choco` | 186 / 149 / 40 | X |

**分布 `{Y:3, Z:2, X:2}` —— 没有主导轴，**判据本身无效**。**

**真正的原因：**
> **「最高」只对直立人形等于「高度」。
> 鸟的 Y 是**翼展**，四足兽的 Y 是**体长**，扁平道具的 X 是**宽度**。**

**正确判据是源格式的约定：**
- `.hfl` 高度场把高程存为 **Z**
- `.map` 摆放 `(x y z)`，**z 是高程**
- → 源是 **Z-up**，映射 `(x, z, -y)` 让 glTF Y = 源 Z，**正确**

**`198_bobu` 的 126 × 156 × 110 就是**一只体长大于身高的矮胖生物**，不是 bug。**

**→ gotcha #87：选判据前先验证判据本身。**

### 二、40 轮中点：目标进度盘点

**已完成（20/40 轮）：**

| 领域 | 文档 | 状态 |
| --- | --- | --- |
| 核心架构 | `UE5-CORE-ARCHITECTURE.md` | ✅ |
| 子系统四层 | `UE5-SUBSYSTEMS.md` | ✅ |
| 碰撞 | `UE5-COLLISION.md` | ✅ |
| 物理仿真 | `UE5-PHYSICS.md` | ✅ |
| 渲染 | `UE5-RENDERING.md` | ✅ |
| Lumen | `UE5-LUMEN.md` | ✅ |
| 材质 | `UE5-MATERIALS.md` | ✅ 含实操 |
| 动画（引擎）| `UE5-ANIMATION-ENGINE.md` | ✅ |
| 动画（运行时）| `UE5-ANIMATION-RUNTIME.md` | ✅ |
| 音频 | `UE5-AUDIO.md` | ✅ 含实装 |
| UI | `UE5-UI.md` | ✅ 边界实测 |
| 网络 | `UE5-NETWORKING.md` | ✅ |
| 输入 | `UE5-INPUT.md` | ✅ |
| 资产管线 | `UE5-ASSET-PIPELINE.md` | ✅ |
| API 体量 | `UE5-API-INVENTORY.md` | ✅ 实测 |
| 项目配置 | `UE5-PROJECT-CONFIG.md` | ✅ |
| 网格合并 | `UE5-MESH-MERGE.md` | ✅ |
| Gameplay 流程 | `UE5-GAMEPLAY-FLOW.md` | ✅ |
| **墨香格式** | `MOD-FORMAT-SOLVED` / `ANM-FORMAT-SOLVED` / `MOXIANG-TO-UE-PIPELINE` | ✅ |
| 角色导入 | `CHARACTER-IMPORT-STATUS.md` | ✅ 管道通 |

**共 30+ 篇文档、87 条坑、102 次提交。**

### 三、诚实的掌握度（中点评估）

| 域 | 掌握 | 依据 |
| --- | --- | --- |
| 编辑器脚本 / MCP | **90%** | 自建工具集 + 200+ 工具用过 |
| 核心架构 | **80%** | 继承链 + 生命周期 + 复制标志 |
| 子系统 | **75%** | 四层 + 取用 |
| 碰撞 | **70%** | 三组正交 + CTF |
| 物理仿真 | **50%** | 开关 + 材质 + 约束（零实操）|
| 材质 | **65%** | 三平面实操 |
| 渲染 / Lumen | **55%** | 配置 + 原理（没调过参数）|
| 动画（引擎+运行时）| **55%** | 数据结构 + 状态机（实操靠自建管道）|
| 音频 | **65%** | 实装背景音乐 + 压缩实测 |
| UI | **30%** | 边界实测（做不了）|
| 网络 | **25%** | 机制清楚（零需求）|
| 输入 | **45%** | 三代方案 + 本项目选择 |
| 资产管线 | **45%** | 引用链实测 |
| **墨香格式逆向** | **90%** | 两格式全解 + 端到端验证 |

**`★` 附注：动画和墨香格式这两块已经**超出"学习"进入"工程"** —— 自建了可用管道。**

### 四、剩下的 20 轮

| 优先级 | 任务 | 为什么 |
| --- | --- | --- |
| **1** | **批量导出** | 5,305 模型 + 4,014 动画，现在一次一个 |
| **2** | **材质接入** | 导入警告「未指定材质的图元」|
| 3 | 逆绑定矩阵 | 动画姿态对不上时 |
| 4 | Lumen 参数实操 | 需重启编辑器，先问人 |
| 5 | 后处理实操 | 350 字段已读未调 |

**目标**仍然未完成**，但**主要知识骨架已建立**。**


## 38. 第二十一轮：批量导出跑通（2026-11-26 26:00）

### 一、结果

| 批次 | 导出 | 带动画 | 失败 |
| --- | --- | --- | --- |
| 前 25（初版）| 25 | 1 | **10** |
| 前 30（修后）| 30 | 1 | **0** |
| **前 100** | **100** | **2** | **0** |

**失败 10 → 0，靠两个解析修复。**

### 二、两个解析 bug

**① `.mod` 的法线是条件性的（gotcha #88）**

```c
if (shadeType == SHADE_TYPE_LIGHT_MAP)         ReadLightTexture();
else if (transformType != TRANSFORM_TYPE_ALIGN_VIEW)  FSRead(normals, 12*V);
```

**`mesh_flag` 位域：`0x0F`=SHADE_TYPE（3=LIGHT_MAP）、`0xF0`=TRANSFORM_TYPE（0x30=ALIGN_VIEW）。**

**我无条件读法线 → ALIGN_VIEW 和 LIGHT_MAP 的网格全部越界。**

**② `.anm` 走块撞进尾部资源引用（gotcha #89）**

**修法：块大小自校验**
```python
expected = 152 + pos_n*20 + rot_n*24 + scale_n*40
if expected != size: break
```

**同一个手法在 `.mod` 上已经用过：让数据自己证明自己。**

### 三、为什么 100 个里只有 2 个带动画

**全库统计：**

| 类别 | 数量 | 占比 |
| --- | --- | --- |
| `.mod` 总 | 5,305 | 100% |
| **`bones = 0`（道具/特效）** | **3,412** | **64%** |
| `bones > 0`（有骨架）| 1,893 | 36% |
| 其中 `bones > 60` | 1,385 | 26% |

**字母序前 100 个是 `101_*` … `108_*`，绝大多数是场景道具。
道具的动画走**顶点/UV 轨**（`dwAnimatedMeshKeyNum` 和 UV 矩形），不是骨骼 —— 这部分还没接。**

### 四、配对规则是错的（下一步）

**`70003cn02_*` 有 **68 骨骼**但没配上动画 —— 文件名和 `.anm` 完全对不上。**

**真正的映射在 `.chx` 容器（纯文本）：**
```
*MOD_FILE_NUM   1
*MOD_FILE_NAME  L001.MOD
*MOTION_NUM     12
    L001_01.anm
    L001_02.anm
```

**→ 下一轮：读 `.chx` 做正确配对，不猜文件名。**

### 五、新增工具与文档

| 产出 | 说明 |
| --- | --- |
| **`Tools/batch_export.py`** | **批量导出（`--limit` / `--pattern`）** |
| `Tools/find_shade_flag.py` | 查 mesh_flag 位域 |
| **`Docs/BATCH-EXPORT-STATUS.md`** | 完整统计 + 两个 bug + 下一步 |
| **gotcha #88/#89** | 法线条件性 / anm 自校验 |

### 六、用法

```powershell
python Tools\batch_export.py --limit 100
python Tools\batch_export.py --limit 30 --pattern "n0"
```

**输出：`Assets/Moxiang/ue_import/batch/`**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **读 `.chx` 做正确配对** |
| 2 | 道具顶点/UV 动画 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |


## 39. 第二十二轮：`.chx` 配对接入（2026-11-26 26:30）

### 一、`.chx` 解析结果

```
chx files parsed: 1081 models, 12 without a parse
animation references: 21919 across 1081 models
models with at least one animation: 926
animation references resolved: 21878, missing: 41     <- 99.8%
```

**12 个解析失败是 `m_do+N.chx` / `m_gum+N.chx`（武器强化文件，结构不同）。**

### 二、格式与两个坑（gotcha #90）

**文本格式：**
```
*MOD_FILE_NUM	1

*MOD_FILE_NAME	P005_A.MOD
*MOTION_NUM		10
	P005_A_01.ANM
	...
```

**坑 1**：部分 `.chx` 前面有**二进制头**（`}   Q     øê`）→ 从 `*MOD_FILE_NUM` 定位
**坑 2**：名字大小写和磁盘不一致（`boss_cowi_01` → `Boss_cowI_01.anm`）→ 不区分大小写 + 目录扫描兜底

### 三、真角色导出来了

**`--pattern boss` 实测：**

| 模型 | 骨骼 | 网格 | 通道 | glTF |
| --- | --- | --- | --- | --- |
| `boss_cowf_01` | 38 | 24 | **8** | 56 KB |
| `boss_cowi_01` | 38 | 35 | **8** | 73 KB |
| `boss_cowking_01` | 38 | 10 | **8** | 35 KB |
| `boss_cowking_05` | **86** | 67 | 0 | 134 KB |

**目前 150 个 gltf 落盘，其中 5 个带动画。**

### 四、两个已记录但未解决的缺口

**① 每个模型只导第一个动画**

**`.chx` 里每个模型列**几十个**动画：**
```
boss_01 -> boss01_stand, boss01_move, boss01_attack01, boss01_attack02
```
**当前只取 `listed[0]`。**

**② 38 骨骼只出 8 通道**

**两个可能：**
- 这个 `.anm` 只驱动 8 根骨骼（其余不动）
- 骨骼名不匹配

**判断方法：比对 `.anm` 骨骼名与 `.mod` 骨骼名的交集大小。**

### 五、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/parse_chx.py`** | **解析所有 `.chx`，建映射（1,081 模型）** |
| `Tools/wire_chx.py` | 接入批量导出 |
| `Tools/batch_export.py` | 已用 `.chx` 优先、文件名兜底 |

### 六、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **一个模型导出多个动画**（`listed` 全部） |
| 2 | **比对骨骼名交集**，查明为何 38 骨骼只有 8 通道 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |


## 40. 第二十三轮：8 通道之谜解开 + 又一个解析 bug（2026-11-26 27:00）

### 一、修了解析 bug：自校验条件写错了

**`Boss_cowf_01.anm` 有 **70 处** `0xF000`，解析器只找到 **5 个块**。**

**根因：我把自校验写成「必须完全相等」，但源码里还有一段可变长度数据：**
```c
if (dwAnimatedMeshKeyNum)
    for (j...) {
        FSRead(&ANIMATED_MESH_KEY, sizeof);
        if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);      // 可变
        if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);     // 可变
    }
```

**正确条件不是相等，是「装得下」：**
```python
required = 152 + pos*20 + rot*24 + scale*40
if required > size: break
```

**放宽后六个文件全部能解析。**

### 二、放宽后看到真相

| 文件 | 轨道 | 轨道名 | 类别 |
| --- | --- | --- | --- |
| `Boss_cowf_01.anm` | **6** | `Bip01 Tail*` | **骨骼动画（只有尾巴）** |
| `Boss_cowf_02.anm` | 5 | `BU_fireball_*` | **特效网格**（只缩放）|
| `Boss_cowf_03.anm` | 15 | `BU_green_fire_*` | 特效 |
| `Boss_cowf_04.anm` | 16 | `BU_black_smoke_*` | 特效 |
| `Boss_cowf_05.anm` | 11 | `BU_fireball_*` | 特效 |
| `Boss_cowf_06.anm` | 12 | `BU_fsandfogs_*` | 特效 |

### 三、🔴 8 通道是**正确**的

**`Boss_cowf_01.mod` 有 38 骨骼，但 `Boss_cowf_01.anm` **只动画 6 根尾巴骨**。**

**6 轨 × (rot+pos) ≈ 8 通道 —— 就是对的。**

**其余 32 根骨骼在这个动作里**不动**。不是管道 bug。**

### 四、`.chx` 混了两类动画

| 类别 | 特征 |
| --- | --- |
| **骨骼动画** | 有 rot 键（四元数），名字是 `Bip01 …` |
| **特效动画** | **只有 scale 键**，名字是 `BU_fireball_*` / `U_Cylinder*` |

**所以配对要**按骨骼名重合度打分**，不能取第一个：**
```python
score = sum(1 for name in tracks if name.lower() in model_bone_names)
best = max(candidates, key=score)
```

**实测：Tail 文件得 4–6 分，特效文件得 0 分。**

### 五、一个更大的发现

**`Boss_cowf_01.mod` … `_06.mod` 是**六个不同模型**（骨骼 38/38/0/38/0/0，
网格 24/52/43/75/56/13）—— 可能是不同 LOD 或不同部位。**

**而 `.chx` 是按**模型组**列出全部动画的。**

**→ 正确的配对粒度是「模型组 ↔ 动画列表」，不是一个模型对一个动画。**
**→ 下一步：按组配对，组内所有动画都导出。**

### 六、修正后的理解

| 之前以为 | 实际 |
| --- | --- |
| 38 骨骼该出几十通道 | **源动画只动 6 根** |
| 一个模型对一个动画 | **一个模型组对一组动画** |
| `.chx` 全是骨骼动画 | **混了特效动画，要打分筛选** |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **按模型组配对，导出组内所有动画** |
| 2 | 特效动画（只有 scale 的）单独处理 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |


