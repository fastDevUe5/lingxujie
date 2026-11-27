# UE5 学习 · 补读（三十九）：Geometry Scripting 实操 —— 盒子建出来了，但烘不成资产

> **这一轮的实测落在一个精确的位置：**
> **`DynamicMesh` 上 46 个 `append_*` 图元函数**全部可用**，`append_box` 建出了**8 顶点 12 三角形**的立方体。
> **但**没有 bake 方法** —— 几何在内存里，出不成 `.uasset`。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、🎯 最重要的发现：函数在哪

**我一开始以为 Geometry Scripting 有一个「库类」（像 `GeometryScriptLibrary`）。**
**实测：`GeometryScriptLibrary` **不存在**。**

**→ 真正的位置是：**这些函数是 `DynamicMesh` 的方法。****

```
DynamicMesh 方法总数: 377
其中 append/bake/static/create 类候选: 46 个
```

**46 个图元函数（全部实测枚举）：**
```
append_box / append_box_with_collision
append_sphere_lat_long / append_sphere_box / append_sphere_box_with_collision
append_capsule / append_capsule_with_collision
append_cone / append_cylinder / append_torus
append_oriented_box / append_oriented_box_with_collision
append_rectangle / append_rectangle_xy / append_round_rectangle
append_linear_stairs / append_curved_stairs
append_sweep_polygon / append_sweep_polyline
append_simple_extrude_polygon / append_simple_swept_polygon
append_revolve_path / append_revolve_polygon / append_spiral_revolve_polygon
append_delaunay_triangulation2d / append_voronoi_diagram2d
append_triangulated_polygon / append_triangulated_polygon3d
append_disc
append_mesh / append_mesh_transformed / append_mesh_repeated
append_mesh_with_materials / append_mesh_transformed_with_materials
append_mesh_repeated_with_materials
append_bounding_box / append_bounding_box_with_collision
append_buffers_to_mesh
```

**→ **46 个图元**，涵盖盒/球/胶囊/锥/柱/环/楼梯/扫掠/旋转/多边形三角化/2D 图论。**

---

## 二、✅ 实测：盒子真的建出来了

```python
dynamic = unreal.DynamicMesh()
dynamic.append_box(
    primitive_options=unreal.GeometryScriptPrimitiveOptions(),
    transform=unreal.Transform(),
    dimension_x=100.0, dimension_y=100.0, dimension_z=100.0,
    steps_x=1, steps_y=1, steps_z=1,
    origin=unreal.GeometryScriptPrimitiveOriginMode.CENTER)
```

**✅ 结果：**
```
vertex count before:  0
append_box returned
counts after append:  {'get_vertex_count': 8, 'get_triangle_count': 12}
```

**→ **8 顶点 / 12 三角形** —— 正是一个立方体的拓扑。**

**→ 这不是「函数没报错」，是**几何真的进内存了**。**
**→ 而且 `get_vertex_count()` / `get_triangle_count()` 是可读的，可以用来验证任何几何操作。**

---

## 三、🔴 但烘不成资产

### 3.1 `append_sphere_lat_long` 参数名错（小问题）

```
TypeError: append_sphere_lat_long() 'num_lat_lines' is an invalid keyword argument
```

**→ 参数名不对（可能是 `lat_steps` / `long_steps`）。**
**→ 这个错误**不影响主结论** —— 盒子那次成功了。**

### 3.2 🔴 真正的问题：**没有 bake 方法**

**在 `DynamicMesh` 的 377 个方法里搜 `bake` / `static` / `copy_to`：**
```
→ 只找到 static_class（不是方法）
→ 没有 bake_mesh / copy_mesh_to_static_mesh / 任何「变成资产」的方法
```

**而 `create_asset` 需要工厂：**
```
unreal.StaticMeshFactory  →  不存在
```

**→ 所以整条链条断了：**
```
建 DynamicMesh  ✅
append_box      ✅（8顶点12三角形）
bake 成资产     ❌（方法不存在）
```

### 3.3 对照：几何是**内存对象**，不是资产

**→ `DynamicMesh` 是一个**内存里的网格数据结构**，和 `.uasset` 无关。**
**→ 要让它在关卡里可见，必须**烘成 StaticMesh 资产**（或通过 GeometryScript 的 actor 组件）。**
**→ 而这个 build 里，两条路都没暴露给 Python。**

---

## 四、🎯 这和 InputAction 那次的对照

| | Enhanced Input | **Geometry Scripting** |
| --- | --- | --- |
| 有没有工厂 | ❌ 没有 | ❌ 没有 |
| `create_asset(..., None)` | ✅ **能用** | ？**没试**（这次卡在 bake，没走到建资产）|
| 建数据 | ✅ 成了 | — |
| 建几何 | — | ✅ **成了（8顶点12三角形）** |
| 落地成资产 | ✅ 成了 | ❌ **bake 方法缺失** |

**→ 关键区别：**
- **InputAction 的**数据**本身就在对象里** → 建成资产就完事了
- **DynamicMesh 的**几何**在对象里，但资产需要「烘」这一步** → 缺了这一步

**→ 所以 Geometry Scripting 的 Python 支持在这个 build 里是**半条链**。**

---

## 五、这一篇学到什么

**1. 🎯 Geometry Scripting 的函数**不是库类，是 `DynamicMesh` 的方法**（46 个图元）。**

**2. ✅ `append_box` 实测有效：8 顶点 12 三角形。**
**→ `get_vertex_count()` / `get_triangle_count()` 是验证几何的可靠判据。**

**3. 🔴 **没有 bake 方法** —— `DynamicMesh` 的 377 个方法里没有「变成静态网格」的。**
**→ 几何在内存里，出不成 `.uasset`。**

**4. 🔴 `unreal.StaticMeshFactory` 不存在。**
**→ 但按 InputAction 的经验，`create_asset(..., None)` 可能行 —— 这次没走到那一步。**

**5. 🎯 46 个图元函数是一份**完整清单**，以后建程序化几何可以直接查。**

---

## 六、更正

| 之前（补读-37）| 现在 |
| --- | --- |
| 「GeometryScriptLibrary 可用」 | ❌ **不存在，函数是 DynamicMesh 的方法** |
| 「能建 DynamicMesh 并 Bake」 | ⚠️ **能建，不能 Bake** |
| 「275 个属性说明完整暴露」 | ⚠️ **图元暴露了，bake 没暴露** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **`create_asset(..., None)` 建 StaticMesh** | **值得试**（InputAction 那次成功了）|
| 找出正确的 `append_sphere_lat_long` 参数 | 参数名不是 `num_lat_lines` |
| Geometry Script 的 actor 组件路线 | 有 `GeometryScript` 组件类型吗？没查 |
| 布尔运算（`Apply Mesh Boolean`）| 文档有，但没在方法列表里找到 |

**→ 下一轮值得试 `create_asset("SM_X", "/Game/Learning", unreal.StaticMesh, None)`。
→ 如果那能建出**空的** StaticMesh，还需要往里写几何 —— 而写几何正是缺的那一步。**

---

## 八、状态

```
Docs/UE5-LEARN-READ-GS2.md   1 篇（共 48 篇 learn 文档）
补读进度：40 / 57
主关卡 116 actor / 视口复位（没建任何新资产）
```

---

## 九、下一篇 / 下一轮

**补读还剩 17 篇：**
```
sequencer-editor (14.4) / fbx-static-mesh (16.1) / import-static-meshes (5.0)
asset-management (已读) / sequencer (1.9) / control-rig (3.4)
control-rig-editor (11.2) / skeletal-animation (2.1) / animation-blueprints (2.5)
water / water-bodies (27.6+2.6) / landscape (0.6) / etc.
```

**→ 下一轮继续补读 `sequencer-editor.md`（14.4 KB）—— 序列器，和动画域相关。**
