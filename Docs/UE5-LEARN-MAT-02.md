# UE5 学习 · 材质（第二块）：参数化材质 + 实例，画面证明了参数生效

> **上一块建的是常量材质（不能做实例）。这一块改成**参数**，然后建两个实例、贴不同的面，
> **一张截图里同时看到两种参数值**。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、为什么常量材质不能做实例

**上一块的 `M_LabDark` 用的是 `MaterialExpressionConstant3Vector`（常量）：
**常量是烘进图里的，实例改不了。****

**要做实例，节点必须是**参数**：**
```
MaterialExpressionTextureSampleParameter2D   → 贴图参数
MaterialExpressionScalarParameter            → 标量参数
MaterialExpressionVectorParameter            → 向量参数
```

---

## 二、🎯 建参数化材质 `M_LabTex`

**图结构（4 个表达式）：**

```
  [TextureSampleParameter2D]     [ScalarParameter]
   参数名 BaseTexture              参数名 Brightness
   贴图 T_Default_Material_Grid_M   默认值 0.08
            │  RGB                     │
            └────────►[Multiply]◄──────┘
                          │
                          ▼
                    MP_BASE_COLOR

  [Constant 0.7] ──► MP_ROUGHNESS
```

**实测输出（✅）：**
```
created /Game/Learning/M_LabTex
texture loaded: True ('T_Default_Material_Grid_M')
scalar parameter 'Brightness' default 0.08
texture parameter 'BaseTexture' set to T_Default_Material_Grid_M
texture and brightness combined through a multiply
base colour connected: True
roughness connected: True
expressions: 4
saved: True
```

**关键 API：**
```python
sample = library.create_material_expression(
    m, unreal.MaterialExpressionTextureSampleParameter2D, -700, 0)
sample.set_editor_property("parameter_name", "BaseTexture")
sample.set_editor_property("texture", texture)

scalar = library.create_material_expression(
    m, unreal.MaterialExpressionScalarParameter, -700, 300)
scalar.set_editor_property("parameter_name", "Brightness")
scalar.set_editor_property("default_value", 0.08)

library.connect_material_expressions(sample, "RGB", multiply, "A")
library.connect_material_expressions(scalar, "", multiply, "B")
library.connect_material_property(multiply, "", unreal.MaterialProperty.MP_BASE_COLOR)
```

**⚠️ 贴图出口名字是 `"RGB"`，标量出口是 `""`（空字符串）—— 不同节点的出口名不一样。**

---

## 三、🎯 建两个实例，参数不同

```python
instance = asset_tools.create_asset(name, "/Game/Learning",
             unreal.MaterialInstanceConstant,
             unreal.MaterialInstanceConstantFactoryNew())
library.set_material_instance_parent(instance, base)
library.set_material_instance_scalar_parameter_value(instance, "Brightness", value)
library.update_material_instance(instance)
```

**实测结果（✅）：**
```
MI_LabDim:     set=False  reads back=0.020  parent='M_LabTex'
MI_LabBright:  set=False  reads back=0.900  parent='M_LabTex'
```

**🔴 重大注意：`set_material_instance_scalar_parameter_value` 返回 `False`，
但**值其实设上了**（读回 0.020 / 0.900 都对）。**

**→ 这个方法的返回值**不可信**，必须用 `get_..._value` 读回验证。**

---

## 四、🎯 贴到不同的面，一张图证明

**分配：**
```
LXJ_LAB_Ceiling  -> MI_LabBright  (0.9)
LXJ_LAB_Floor    -> MI_LabDim     (0.02)
LXJ_LAB_Wall_E/W/S/N -> MI_LabDim (0.02)
```

**画面：**

![实例效果](</C:\Users\tk\Desktop\lingxujie\Saved\shot_instances.png>)

**读法：**

| 观察 | 说明 |
| --- | --- |
| 盒子整体**黑** | 暗参数 0.02 生效了（墙、地板）|
| 顶面出现**红/青色网格图案** | **亮参数 0.9** 生效 + **贴图**生效（`T_Default_Material_Grid_M` 本身就是彩色网格）|
| 图案集中在顶面中央 | 那是**10 cm 天花板漏进来的光**照在贴图上的结果 |

**→ **同一张图里同时看到两个参数值的效果** —— 比拍两张图更有说服力。**

**→ 而且它顺带把上一块的漏光问题**变成了可见的彩色图案**。**

---

## 五、这一块学到什么

**1. 常量节点不能做实例，必须用参数节点。**
`Constant3Vector` → `ScalarParameter` / `VectorParameter` / `TextureSampleParameter2D`。

**2. 🔴 `set_material_instance_scalar_parameter_value` 返回 False 但值是设上的。**
**必须读回验证，不能信返回值。**

**3. 不同节点的出口名不同。**
贴图参数 → `"RGB"`；标量参数 → `""`（空）。

**4. `set_material_instance_parent` 必须在设参数**之前**调，否则找不到参数。**

**5. 一张图证明两件事：**
把两个实例贴到不同的面，一次截图就能看出参数差异。

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「材质可用 Python 完整控制」 | ✅ 对，但**返回值不可信** —— 要读回 |
| 「一次只能验证一个变化」 | ❌ **可以在一张图里同时验证两个**（不同面不同实例）|

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| **`get_nanite_override_material`** | **和项目那个「Nanite 网格缺材质」直接相关**，还没试 |
| 向量参数 | 只用了标量 |
| 混合模式 / 双层 / 遮罩 | 只用了不透明单层 |
| 材质函数（Material Function）| 没做 |
| 该方法的官方签名与返回值含义 | **只有实测，没读源码解释为什么返回 False** |

---

## 八、下一块

**三个选择：**
- **A. `get_nanite_override_material`** —— 直指项目的真实问题（101 个 Nanite 网格材质）
- **B. 读源码搞清 `set_material_instance_scalar_parameter_value` 为什么返回 False**
- **C. 转 UI/UMG**（目标里的下一项）

**→ 我倾向 A** —— 它直接连到项目的实际缺陷，而且材质这块已有扎实基础。

**⚠️ 练习关卡现在是：天花板 MI_LabBright、其余 MI_LabDim、灯 1200、10 actor。**
