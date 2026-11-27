# UE5 网格合并（Merge Actors）：实测与边界

> **本篇是"学一个真实能力"的记录：96 个建筑 actor 合成一个，
> 过程踩了三个坑，最后量化了收益与代价。**

---

## 一、它解决什么问题

**兰州城现在是 **96 个材质组 = 96 个独立 actor**。**

| 后果 | 说明 |
| --- | --- |
| 96 次 draw call | 每个 actor 一次 |
| 大纲里 96 项 | 移动整座城要选 96 个 |
| 96 个资产引用 | 打包时全部加载 |

**引擎有合并操作专门解决这个。**

---

## 二、正确的 API（踩了三个坑才找到）

### 2.1 不在 `EditorLevelLibrary` 上

```
merge failed: type object 'EditorLevelLibrary' has no attribute 'merge_actors'
```

### 2.2 在 `StaticMeshEditorSubsystem` 上

```python
subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
merged = subsystem.merge_static_mesh_actors(actors, options)
```

**怎么找到的：读引擎自带 `SceneTools.merge_actors` 的实现 ——
它内部就是这么调的。**（这比翻文档快，见第六节）

### 2.3 选项对象

```python
options = unreal.MergeStaticMeshActorsOptions()
options.base_package_name = "/Game/Moxiang/Merged/SM_Lanzhou_City"
options.new_actor_label = "MX_LANZHOU_MERGED"
options.destroy_source_actors = False
options.spawn_merged_actor = True
```

**⚠️ `MeshMergingSettings` 里没有 `generate_lightmap_uv` / `use_vertex_colors` 这两个属性** ——
名字猜错了会抛 `Failed to find property`。**不设它们，用默认值即可。**

---

## 三、实测结果

```
MERGE: found 96 building actors
MERGE: distinct meshes 96, material slots assigned 96
MERGE: merging in /Game/Maps/LingXuJie.LingXuJie:PersistentLevel
MERGE: merge returned StaticMeshActor_97
MERGE: merged mesh SM_SM_Lanzhou_City, material slots 96
MERGE: after merge: 96 MX_LZ_ actors remain (originals kept), +1 merged
```

| 项 | 值 |
| --- | --- |
| **合并后 mesh** | `SM_SM_Lanzhou_City` |
| **材质槽** | **96** |
| **三角形** | **64,740** |
| **顶点** | **85,522** |
| **actor 数** | 96 → 96 + 1（`destroy_source_actors=False`）|

### 3.1 两个关键事实

**① 材质槽保留了 96 个 —— 每个材质组的贴图仍然独立。**

**这是最重要的：合并**不会**把 96 种材质压成一种。**
**所以合并后观感和合并前一样。**

**② 64,740 三角形是整座兰州城的几何总量。**

**对比地形 524,288 —— 地形是建筑的 8 倍。**

---

## 四、代价与边界（诚实）

### 4.1 合并的代价

| 代价 | 说明 |
| --- | --- |
| **不能再单独移动一栋房子** | 合并后是一个整体 |
| **不能再单独换一个组的材质** | 槽位固定了 |
| **96 个材质槽仍然存在** | 所以 draw call 不是"1 次"，是"按材质分 96 次" |
| **合并后的资产更大** | 一份独立的几何拷贝 |

**关键认知：合并**减少的是 actor 数量，不是 draw call 数量**。**

> **96 个 actor + 96 个材质 = 96 次 draw call**
> **1 个 actor + 96 个材质 = **仍然 96 次 draw call**
>
> **合并对 draw call 没有帮助 —— 它帮的是大纲整洁和移动方便。**

**这条是本次实测最有价值的认知。**

### 4.2 什么情况下合并真的有用

| 场景 | 有用吗 |
| --- | --- |
| 减少 draw call | ❌ **没用**（材质数没变）|
| 大纲整洁 | ✅ 有用 |
| 移动整座城 | ✅ 有用 |
| 减少资产引用 | ⚠️ 合并后是 1 个引用指向 1 个大资产 |
| 减少流送开销 | ⚠️ 需要配合关卡流送 |

### 4.3 本项目的实际决定

**测完之后**没有采用合并**。理由：**

1. **对 draw call 无帮助**（材质槽数不变）
2. **原 96 个 actor 便于按组件调（比如单独挪一栋房子）**
3. **96 个 actor 在编辑器里不算多**

**所以这条能力"学会了但不用" —— 这也是一种正确判断。**

---

## 五、掌握程度（网格合并）

| 内容 | 掌握 |
| --- | --- |
| 合并的正确 API 在哪 | 🟢 **清楚**（`StaticMeshEditorSubsystem`）|
| 选项对象与字段 | 🟢 **清楚**（哪些有、哪些没有）|
| **实测跑通** | 🟢 **96 actor → 1，96 槽，64,740 面** |
| **合并对 draw call 无帮助** | 🟢 **实测认知** |
| 何时该用 / 不该用 | 🟢 **清楚** |

**这一块从 0 → **70%**，因为**跑通了并且有判断**。**

---

## 六、找 API 的更快办法（本轮最大收获）

**踩了三次坑才找对 API。更快的办法是：**

> **读引擎自带工具的实现，看它内部调什么。**
>
> ```python
> # SceneTools.merge_actors 的实现里直接写着：
> merged = smes.merge_static_mesh_actors(actors, options)
> ```
>
> **引擎自己的 217 个工具就是最好的 API 示例 —— 它们必须调用可用的方法。**

**这条应该写进明天的开工流程：找 API 时，先看引擎工具的实现。**

---

## 七、重查命令

```powershell
py "Tools/merge_buildings.py"        # 执行合并
py "Tools/remove_merged_actor.py"    # 清理合并结果
```
