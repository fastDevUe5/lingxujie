# UE5 学习 · 材质（第一块）：从零建一个材质，并且它真的生效了

> **这一块是**成功**的：材质从零建起来，贴到 6 个面上，并且**用画面证明了它生效**。**
> **而且顺手修好了上一块卡住的「白盒子」问题。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、官方文档说了什么

**`material-editor-guide.md`（7.5 KB）讲的是编辑器 UI 操作：
新建材质 → 打开编辑器 → 放表达式和函数 → 连到主材质节点 → 预览和应用 → 整理图表。**

**`material-expressions.md`（7.4 KB）是**表达式参考索引**（按 Color / Coordinates / Depth /
Font / Vector / Material Parameter / Utility 分类）。**

**⚠️ 两篇都以**编辑器 UI**为主。但 Python 侧实际能力比文档暗示的强得多。**

---

## 二、🎯 Python 侧的材质 API 有 **77 个方法**

**`MaterialEditingLibrary`（从本地镜像核实）：**

| 类别 | 方法 |
| --- | --- |
| **建表达式** | `create_material_expression` / `create_material_expression_in_function` |
| **连线** | `connect_material_expressions` / `connect_material_property` / `disconnect_*` |
| **查询** | `get_num_material_expressions` / `get_material_expressions` / `get_material_property_input_node` |
| **编译** | `recompile_material` / `layout_material_expressions` |
| **实例** | `set_material_instance_parent` / `set_material_instance_scalar_parameter_value` / `*_vector_*` / `*_texture_*` |
| **参数默认值** | `get_material_default_scalar_parameter_value` / `*_vector_*` / `*_texture_*` |
| **其他** | `delete_unused_expressions` / `get_material_used_textures` / **`get_nanite_override_material`** |

**建资产用 `AssetTools.create_asset(name, path, Material, MaterialFactoryNew())`。**

**→ 材质的完整工作流（建资产 → 加节点 → 连线 → 编译 → 保存 → 赋给组件）**全部能用 Python 做**。**

---

## 三、🎯 实操：从零建 M_LabDark

**代码（`Tools/mat_build_dark.py`）核心四步：**

```python
factory = unreal.MaterialFactoryNew()
material = asset_tools.create_asset("M_LabDark", "/Game/Learning",
                                    unreal.Material, factory)

colour = library.create_material_expression(
    material, unreal.MaterialExpressionConstant3Vector, -400, 0)
colour.set_editor_property("constant", unreal.LinearColor(0.04, 0.04, 0.04, 1.0))
library.connect_material_property(colour, "", unreal.MaterialProperty.MP_BASE_COLOR)

roughness = library.create_material_expression(
    material, unreal.MaterialExpressionConstant, -400, 200)
roughness.set_editor_property("r", 0.6)
library.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)

library.recompile_material(material)
unreal.EditorAssetLibrary.save_asset("/Game/Learning/M_LabDark")
```

**实测输出（✅）：**
```
created /Game/Learning/M_LabDark
expressions before: 0
added a constant vector at 0.04
added a roughness constant at 0.6
base colour connected: True
roughness connected: True
expressions now: 2
saved: True

blend_mode      BLEND_OPAQUE
shading_model   MSM_DEFAULT_LIT
two_sided       False
```

**→ **2 个表达式、两条连线都返回 True、编译、保存成功。****

---

## 四、🎯 赋给 6 个面（✅ 逐个核实）

```
LXJ_LAB_Floor      'BasicShapeMaterial' -> 'M_LabDark'
LXJ_LAB_Ceiling    'BasicShapeMaterial' -> 'M_LabDark'
LXJ_LAB_Wall_E     'BasicShapeMaterial' -> 'M_LabDark'
LXJ_LAB_Wall_W     'BasicShapeMaterial' -> 'M_LabDark'
LXJ_LAB_Wall_S     'BasicShapeMaterial' -> 'M_LabDark'
LXJ_LAB_Wall_N     'BasicShapeMaterial' -> 'M_LabDark'
surfaces changed: 6
```

**复查确认（从编辑器重新读取）：6 个面全部是 `M_LabDark`。**

---

## 五、🎯 画面证明：盒子从白变黑

| | 截图 |
| --- | --- |
| **改之前**（白 BasicShapeMaterial）| 整个盒子**雪白**，任何东西都被淹没 |
| **改之后**（M_LabDark 0.04）| 盒子**近乎全黑** |

![深色盒子](</C:\Users\tk\Desktop\lingxujie\Saved\shot_mat_outside.png>)

**→ 而且**在黑盒子上一眼就能看到那团柔和的白斑** —— 那是 10 cm 天花板漏出来的光。
上一块（白盒子）里完全看不出来。**

**→ 材质生效 + 上一块的漏光问题**现在可视化了**，一个动作解决两个问题。**

---

## 六、🔴 但内部截图还是白的 —— 原因是灯

**相机在房间内 (-420, 0, 200)，灯在 (0, 0, 240)，**距离只有 4.2 米，强度 5000**。**

**→ 那不是材质失败，是**真的过曝**。**

**→ 已把灯降到 **1200**。**

**判据教训：**
> **外部黑、内部白 → 说明材质生效了，问题在**照明强度**，不在材质。**

---

## 七、这一块学到什么

**1. 🎯 材质的完整工作流 Python 全能做到。**
建资产 → 加表达式 → 连线 → 编译 → 保存 → 赋给组件。

**2. `connect_material_property` 返回 True 就是连上了。**
可以立即验证，不用猜。

**3. `recompile_material` 之后要**等 shader 编译**。**
日志里 `LogShaderCompilers` 说明它在后台跑。

**4. 🔴 判据要选对。**
内部白的时候我怀疑材质；**从外面看**才发现材质早生效了 —— 是灯太亮。
**同一件事，换个观察角度结论就对了。**

**5. 一个动作解决两个问题。**
深色材质既练了材质，又修好了上一块的白盒子。

---

## 八、更正

| 之前 | 现在 |
| --- | --- |
| 「练习关卡够用了」 | ❌ **白盒子不行** —— 现已换成 M_LabDark（0.04）|
| 「Niagara 截不到画面是粒子的原因」 | ❌ **是环境原因**：白底没对比度。现在深色底，漏光都看得见了 |

---

## 九、还没做到

| 项 | 说明 |
| --- | --- |
| 材质实例（Material Instance） | API 有，没建过 |
| 贴图参数 | `set_material_instance_texture_parameter_value` 没试 |
| 混合模式 / 双层 | 只用了默认不透明单层 |
| **`get_nanite_override_material`** | **和项目那个 Nanite 材质问题直接相关**，没试 |

---

## 十、下一块

**继续材质，做三件事：**
1. **建一个 Material Instance** 并改参数（比直接改材质更符合项目做法）
2. **接一张贴图**（`/Engine/EngineMaterials` 有现成贴图）
3. **试 `get_nanite_override_material`** —— 项目那个「Nanite 网格缺材质」的问题可能靠它解决

**⚠️ 练习关卡现在是深色的（M_LabDark），灯 1200，10 个 actor。主关卡 116 actor 已重开。**
