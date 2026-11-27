# 用 MCP 写 Blueprint 图（引擎 5.8.4｜实测 2026-11-19 ✅）

## 一句话结论

**能。** UE 5.8 官方 MCP 的 `editor_toolset.toolsets.blueprint.BlueprintTools`（51 个工具）可以**在不开编辑器界面的情况下创建 Blueprint、加节点、连线、设默认值、编译**；
Python 做不到这件事（见 `editor-python-boundaries.md`），但 MCP 可以。

## 实测走通的流程

以 `BP_SpinningCube`（父类 `StaticMeshActor`）为例，全部通过 MCP 调用完成：

| 步骤 | 工具 | 参数要点 |
| --- | --- | --- |
| 1. 建 BP | `BlueprintTools.create` | `folder_path="/Game/Blueprints"`, `asset_name`, `asset_type`=父类 Class |
| 2. 加事件 | `create_node` | `graph`=BP 的 `EventGraph`，`type_id="添加事件|事件BeginPlay"`，`pos` |
| 3. 加函数调用 | `create_node` | `type_id="开发|PrintString"` |
| 4. 查 pin | `get_node_type_pins` | 返回 pin 名与 `index_id`（注意：会**真的创建一个临时节点**） |
| 5. 设默认值 | `set_pin_value` | `pin={direction, index_id, node.refPath}`, `value="..."` |
| 6. 连线 | `connect_pins` | `output_pin`（事件的 `then`, index 1）→ `input_pin`（PrintString 的 `execute`, index 0） |
| 7. 编译 | `compile_blueprint` | 返回 `null` 即成功；失败会抛异常 |
| 8. 放进关卡 | `SceneTools.add_to_scene_from_class` | `actor_type` = `.../BP_SpinningCube.BP_SpinningCube_C` |
| 9. 运行验证 | `EditorAppToolset.StartPIE` / `StopPIE` | PIE 里执行到 BeginPlay |

## 运行时证据

```
LogBlueprint: Compiling Blueprint '/Game/Blueprints/BP_SpinningCube.BP_SpinningCube'
LogBlueprintUserMessages: [BP_SpinningCube_C_0] Blueprint BeginPlay fired
```

## 坑（中文编辑器必看）

1. **`type_id` 是本地化的**。这台机器编辑器是中文，节点类型 ID 不是文档里的英文：
   - `添加事件|事件BeginPlay`、`添加事件|事件Tick`
   - `开发|PrintString`
   - `变换|AddActorLocalRotation`
   - `数学|旋转|MakeRotator`
   用 `find_node_types(graph, type_id_filter="BeginPlay", context_pins=[])` 先查真实 ID，别猜。
2. **`write_graph_dsl` 的 `(event ...)` 形式在中文环境解析失败**：
   `AddEvent|EventBeginPlay does not exist`（`ReceiveBeginPlay`、`事件BeginPlay` 同样失败）。
   事件节点请用 `create_node` 建；DSL 目前只适合写**表达式/函数**部分。
3. **`get_node_type_pins` 会创建节点实例**（`K2Node_CallFunction_N`），只查 pin 也会在图里留下节点。拿到 pin 名后要么复用该节点，要么 `delete_node` 清掉。
4. **孤立节点会让编译失败**，而错误列表可能为空（`Compile Errors: []`）。改图前先确认图里只有计划内的节点；`find_nodes(entry_points_only=true)` 能列出所有入口节点。
5. `read_graph_dsl` 对事件图可能返回空字符串（本次实测为空），验证逻辑更可靠的方式是 `get_node_infos` + 编译 + PIE 日志。

## 给 Blueprint 配网格和材质（CDO 上的组件）

BP 的默认值存在 CDO 上，组件是 CDO 的子对象，所以要分两步：

1. `BlueprintTools.get_default_object(blueprint)` → 拿到 CDO（`...Default__BP_X_C`）
2. `ActorTools.get_components(actor=CDO)` → 组件引用（如 `...:StaticMeshComponent0`）
3. `ObjectTools.set_properties(instance=组件, values='{"StaticMesh": "/Engine/BasicShapes/Cube.Cube"}')`
   材质用 `{"OverrideMaterials": ["/Game/Materials/M_Accent.M_Accent"]}`
4. 直接对 BP 资产 `set_properties` 设 `StaticMeshComponent` 会失败（子对象属性必须先拿组件引用）

查 actor 变换用 `ActorTools.get_actor_transform`（`get_transform` 不存在）。

## 运行时验证的局限

立方体绕 Z 轴旋转在**静态截图**里看不出来（90° 对称）。要肉眼验证，把实例缩放改成非对称（如 `1.6 / 0.8 / 1.0`），
或挂一个偏心的小网格；否则请用“图已编译 + `get_node_infos` 确认连线 + PIE 日志”三者一起证明。

## 实战样例二：朝向玩家的炮塔（BP_Turret）

节点链（全部在 EventGraph，Tick 驱动）：

```
添加事件|事件Tick
  → 变换|SetActorRotation (NewRotation)
      ← 数学|旋转|FindLookatRotation (ReturnValue)
          Start  ← 变换|GetActorLocation（self 留空 = 本 Actor）
          Target ← 变换|GetActorLocation（self ← 游戏|GetPlayerPawn.ReturnValue）
```

要点：

- `GetActorLocation` 的 `self` 不连线时默认就是本 Actor；要取别的 Actor 就把引用接到 `self`。
- 朝向节点名是 `FindLookatRotation`（注意小写 `at`，与 C++ 的 `FindLookAtRotation` 不同）。
- 立方体网格要能看出旋转，必须用**非均匀缩放**（本例 `4.0 / 0.5 / 0.5` 做成长条），否则 90° 对称看不出转动。
- 实测：`BP_Turret` 在游戏里长条始终指向玩家，`Saved/Screenshots/BP_Turret_InGame2.png` 可辨。

## 实例级设置：移动性与碰撞（踩过坑）

**StaticMeshActor 蓝图里 Tick 的旋转/位移会被静默忽略**——它的网格组件默认是 `Static` 移动性，
运行时只有一条日志：`Mobility of ... has to be 'Movable' if you'd like to move.`

- 在 CDO 的组件上用 `set_properties({"Mobility": "Movable"})` **改不动**（返回 true 但会被模板覆盖）；
- 可靠做法：在关卡生成器里对**实例组件**设置（`Tools/build_level.py::configure_blueprint_prop`）：

```python
component = actor.get_components_by_class(unreal.StaticMeshComponent)[0]
component.set_mobility(unreal.ComponentMobility.MOVABLE)          # 允许被蓝图移动
component.set_collision_profile_name("OverlapAllDynamic")          # 拾取物：重叠而非阻挡
component.set_editor_property("generate_overlap_events", True)     # 注意：没有 set_generate_overlap_events
```

`set_properties` 改 `BodyInstance.CollisionProfileName` 同样不生效——碰撞必须在实例上用函数调用设置。

## 实例级拾取/惩罚实测（BP_TimeOrb / BP_Hazard）

```
BP_TimeOrb:   事件 ActorBeginOverlap → CoinRush|AddBonusTime (5.0)    → Actor|DestroyActor
BP_Hazard:    事件 ActorBeginOverlap → CoinRush|ApplyTimePenalty (3.0)
```

运行日志：

```
[CoinRush] Bonus time +5.0s (time left 50.0s)
[CoinRush] Time penalty -3.0s (time left 45.0s)
```

倒计时 44→49（加时球消失）、44（踩陷阱扣 3 秒）——蓝图确实参与了玩法。
陷阱不销毁自己，靠 `ActorBeginOverlap` 只在**进入**时触发一次；要持续伤害得改成 Tick 里判距离。

## 什么时候值得用

- 需要**少量**蓝图侧逻辑（关卡里的小机关、美术/音频同学要接的钩子、快速原型验证）。
- 需要**批量**：同一套节点结构复制到 N 个 BP（`duplicate` + `retarget_node_class`）。
- 不适合：大规模 gameplay 逻辑（C++ 可 diff、可测试、可复用；蓝图二进制不可 review）。
