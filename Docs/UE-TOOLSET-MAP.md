# UE 5.8.4 现成工具能力地图（2026-11-26 实测）

> **核心发现：这个引擎版本自带 217 个 MCP 工具，覆盖了本项目大部分要手写的东西。**
> **先查这张图，再决定要不要写代码。**

---

## 一、总量

| 类别 | 数量 |
| --- | --- |
| C++ 内置工具集 | 5 个 |
| **Python 工具集** | **16 个** |
| 我们自建 | 1 个（`LingXuJieTools`） |
| **Python 工具集里的工具总数** | **217 个** |

**源码位置（可随时重查）：**
```
Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python\editor_toolset\toolsets\
```

**列举脚本：`python Tools/list_python_toolset_tools.py [工具集名...]`**

---

## 二、🔴 三个改变方案的发现

### 2.1 `SkeletalMeshTools.import_file` —— **动画导入现成就有**

```python
import_file(folder_path, asset_name, source_file,
            skeleton=None,
            import_materials=False,
            import_textures=False,
            import_animations=False,     # ← 这里
            create_physics_asset=False) -> list[unreal.Object]
```

**官方 docstring 原文：**
> `import_animations`: When True, create AnimSequence assets for any animations contained in the file.

**所以 `.anm` 的完整路径是：**

```
墨香 .anm
   ↓ 转成 FBX（带骨架 + 动画轨道）
   ↓ 一次工具调用：
SkeletalMeshTools.import_file(
    folder_path="/Game/Moxiang/Anim",
    asset_name="bobu",
    source_file="...bobu.fbx",
    import_animations=True)
   ↓
SkeletalMesh + Skeleton + AnimSequence 全出来
```

**不需要写自定义导入器，不需要 C++。**

**这比之前设想的"写 FBX 序列化 + 自定义导入"省掉了整个导入环节。**

### 2.2 `SceneTools.merge_actors` —— **解决 96 个 actor 的问题**

```python
merge_actors(actors: list[unreal.StaticMeshActor],
             output_path: str, name: str = '') -> unreal.StaticMeshActor
```

**"Merges multiple StaticMesh actors into a single mesh asset and actor."**

**兰州城现在是 96 个材质组 = 96 个 actor。合并后可以变成一个（或按语义合并成几个），
既能提高视口性能，也便于管理。**

### 2.3 `MaterialTools` 的引脚查询 —— **解决 gotcha #64**

```python
get_expression_input_names(expression) -> list[str]
get_expression_output_names(expression) -> list[str]
```

**gotcha #64 是"Clamp 节点的输入引脚连不上，只能改用 Min/Max 替代"。**
**根因是**猜引脚名**。有了这两个工具，可以**先查真实引脚名再连**，不用猜。**

**以后建材质应该：**
```
add_expression → get_expression_input_names → connect_expressions(用查到的名字)
```

---

## 三、各工具集速查（只列本项目会用到的）

### 3.1 场景 —— `SceneTools`（19 个）

| 工具 | 用途 |
| --- | --- |
| `load_level` / `get_current_level` | 关卡切换 |
| `find_actors` | 按条件搜 actor |
| **`add_to_scene_from_class`** | 按类生成 actor |
| **`add_to_scene_from_asset`** | 按资产路径生成 actor |
| `remove_from_scene` | 删除 actor |
| **`merge_actors`** | **合并多个 StaticMeshActor** |
| `create_level_instance` / `edit_level_instance` / `commit_level_instance` | 关卡实例（分区加载）|
| `get_folders` / `set_actor_folder` / `rename_folder` / `delete_folder` | 大纲分组 |
| `save_actor` | 保存单个 actor |

**→ 关卡搭建流程可以全部走工具，不用碰 Python 脚本。**

### 3.2 骨骼网格 —— `SkeletalMeshTools`（22 个）

| 工具 | 用途 |
| --- | --- |
| **`import_file`** | **导入骨骼网格 + 可选动画/材质/贴图/物理资产** |
| `get_bone_names` / `get_bone_parent` / `get_bone_children` | **骨骼层级查询** |
| `get_skeleton` | 取骨架资产 |
| `get_material_slots` / `get_material` / `set_material` | 材质槽 |
| `get_morph_target_names` | 变形目标 |
| `add_socket` / `get_socket_names` / `set_socket_transform` / `remove_socket` / `rename_socket` | 挂点 |
| `get_physics_asset` / `assign_physics_asset` | 物理资产 |
| `get_lod_count` / `get_vertex_count` / `get_section_count` / `get_bounds` | 查询 |

**→ 骨骼验证（骨骼名是否与 `.mod` 一致）直接用 `get_bone_names` 查，不用写脚本。**

### 3.3 材质 —— `MaterialTools`（22 个）

| 工具 | 用途 |
| --- | --- |
| `create_material` / `create_function` / `create_parameter_collection` | 新建 |
| `list_expression_classes` | **列出可用的材质节点类** |
| `add_expression` / `delete_expression` / `get_expressions` | 增删查节点 |
| **`get_expression_input_names` / `get_expression_output_names`** | **查真实引脚名** |
| `connect_expressions` / `disconnect_expressions` | 连线 |
| `connect_to_output` / `get_property_input` / `disconnect_from_output` | 接输出属性 |
| `recompile` | **编译（失败会抛异常）** |
| `layout_expressions` / `delete_unused_expressions` | 整理 |
| `get_referencing_materials` | 谁引用了这个材质函数 |

**→ 地面材质、建筑材质都可以用这个建，且能查引脚、能重编译验证。**

### 3.4 静态网格 —— `StaticMeshTools`（15 个）

**导入、LOD、碰撞、Nanite 设置等。**（`import_file` 也在，OBJ 导入可以走它）

### 3.5 其他

| 工具集 | 数量 | 用途 |
| --- | --- | --- |
| `ActorTools` | — | actor 查看与修改 |
| `AssetTools` | — | 资产与磁盘文件 |
| `TextureTools` | — | 贴图（`get_size` 等）|
| `ObjectTools` | — | 任意对象属性读写 |
| `BlueprintTools` / `blueprint_dsl` | — | 蓝图（本项目不用）|
| `DataTableTools` / `DataAssetTools` / `CurveTableTools` / `StringTableTools` | — | 数据资产 |
| `PrimitiveTools` | — | 加基础几何 |
| `ProgrammaticToolset` | — | **编排其他工具**（非通用 Python）|

---

## 四、对本项目的直接影响

| 原来打算写的 | 现在不用写 |
| --- | --- |
| 自定义 OBJ 导入器 | `StaticMeshTools.import_file` |
| 自定义骨骼网格导入 | `SkeletalMeshTools.import_file` |
| **自定义动画导入器** | **`import_file(import_animations=True)`** |
| 自定义材质构建 | `MaterialTools` 全套 |
| 手动摆 actor 的 Python 脚本 | `SceneTools.add_to_scene_from_*` |
| 查引脚名试错 | `get_expression_input_names` |
| 96 个 actor 的管理 | `merge_actors` |

**唯一必须自己写的，只剩**格式转换**：**
```
.anm → FBX        ← 这个没有现成工具
.mod → OBJ/FBX    ← 已有 build_map_obj.py
```

---

## 五、怎么查某个工具的具体签名

```powershell
# 全部工具（217 个）
python Tools\list_python_toolset_tools.py

# 只看某几个工具集
python Tools\list_python_toolset_tools.py skeletal_mesh material scene
```

**或者查 `Docs/PythonAPI/` 里对应类的官方签名。**

---

## 六、教训

**我在这个项目上花了大量时间手写工具，而引擎里已经有 217 个。**

**以后接手任何 UE 工作的第一步应该是：**
```
1. list_toolsets          ← 看有哪些工具集
2. 读对应工具集的 .py 源  ← 看每个工具的确切签名和 docstring
3. 再决定要不要自己写
```

**这比"先写一个再说"省太多了。**
