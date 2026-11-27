# 编辑器 Python 的能力边界（引擎 5.8.4｜核对 2026-11-17｜本工程实测 ✅）

## 一句话结论

编辑器 Python 能**建资产、改属性、摆 Actor、存包**，足够把“关卡和材质”完全脚本化；
但它**不能连线蓝图节点、不能搭 Niagara/Widget 图**。所以本工程的原则是：
**能脚本化的都脚本化（关卡/材质/数据），需要图编辑的都不做（玩法走 C++，UI 走 Canvas）。**

## 能做（本工程实测通过的 API）

| 能力 | API | 我们怎么用 |
| --- | --- | --- |
| 建资产并保存 | `AssetToolsHelpers.get_asset_tools().create_asset(...)` + `EditorAssetLibrary.save_asset` | 5 个材质 |
| 查/删资产 | `EditorAssetLibrary.does_asset_exist` / `delete_asset` | 幂等重建前清理 |
| 材质图 | `MaterialEditingLibrary.create_material_expression` / `connect_material_expressions` / `connect_material_property` / `recompile_material` | 常量色、粗糙度、金属度、Emissive |
| 关卡 | `LevelEditorSubsystem.new_level` / `load_level` / `save_current_level` | 生成 `/Game/Maps/CoinRush` |
| Actor | `EditorActorSubsystem.spawn_actor_from_class` / `destroy_actor` / `get_all_level_actors` | 34 个 actor |
| 属性读写 | `get_editor_property` / `set_editor_property` | 灯光强度、后处理参数 |
| 子系统入口 | `unreal.get_editor_subsystem(unreal.XxxSubsystem)` | 替代已废弃的 `EditorLevelLibrary` |

**属性命名规律**：Python 名 = `UPROPERTY` 名去掉 `b` 前缀并转下划线。例如
`bEnableVolumetricFog` → `enable_volumetric_fog`、`bAtmosphereSunLight` → `atmosphere_sun_light`。
猜错会直接抛 `Failed to find property 'xxx'`，所以用 `safe_set()` 包一层（见 `Tools/build_level.py`）。

**材质表达式输入的坑**：`FExpressionInput` 成员是 protected，`set_editor_property("a", expr)` 会报错，
必须用 `connect_material_expressions(from, "", to, "A")`。常量本身仍可用 `set_editor_property("constant", LinearColor)`。

## 不能做 / 很弱

| 能力 | 现状 | 替代方案 |
| --- | --- | --- |
| 蓝图节点图（加节点、连线） | **Python 无公开 API**；但 **MCP 的 BlueprintTools 可以**（见 [blueprint-authoring-via-mcp.md](blueprint-authoring-via-mcp.md)） | 逻辑写 C++；少量蓝图逻辑走 MCP |
| UMG Widget 层级（拖控件、设锚点） | 只能建 WidgetBlueprint 资产，层级编辑很弱 | 本工程直接用 `AHUD` + Canvas 绘制 |
| Niagara 图、Control Rig、动画状态机 | 基本不可行 | 交给编辑器人工，或用 MCP 的 Niagara toolset 试 |
| Slate 编辑器面板操作 | Python 不可达 | MCP 的 `SlateInspectorToolset` |
| 导入选项的细粒度控制 | `AssetImportTask` 有限支持 | 用 `.ini` 配置导入默认值 + 人工抽检 |

> 以上“不能做”是**公开 API 层面的经验判断**，没有逐项穷举引擎内部接口；真要突破需自写 C++ 编辑器插件。

## 可复制片段

```python
# 容错设置属性（属性名随版本漂移时只警告、不中断生成）
def safe_set(obj, name, value):
    try:
        obj.set_editor_property(name, value)
        return True
    except Exception as exc:
        unreal.log("[CoinRush] skip property %s (%s)" % (name, exc))
        return False

# 幂等重建关卡：已存在就加载+清空，不存在才新建
def ensure_empty_level():
    if EDITOR_ASSETS.does_asset_exist(LEVEL_PATH):
        LEVELS.load_level(LEVEL_PATH)
        for actor in ACTORS.get_all_level_actors():
            ACTORS.destroy_actor(actor)
        return True
    return LEVELS.new_level(LEVEL_PATH)
```

## 工程取舍与理由

- **关卡/材质全部脚本生成**：`Tools/build_level.py` 可重跑，改一个数字就能重建，不用手点编辑器。
- **玩法不写蓝图**：蓝图是二进制资产，agent 改不了、Code Review 看不见、diff 无法读；C++ 全部可审。
- **UI 用 Canvas HUD**：不需要 UMG 资产，也不需要拖控件；代价是布局要手写坐标。

## 待复核（升级 5.9 时）

- [ ] `unreal.get_editor_subsystem` 入口是否仍覆盖 `LevelEditorSubsystem` / `EditorActorSubsystem`
- [ ] `MaterialEditingLibrary.connect_material_expressions` 的参数顺序是否变化
- [ ] 5.9 是否新增蓝图图编辑 API（若有，重新评估“玩法全 C++”的必要性）
