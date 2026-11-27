# UE5 学习 · 材质（第三块）：Nanite override 材质，源码到画面的完整链条

> **这一块把「Nanite 专用材质覆盖」从源码语义一直验到画面。**
> **而且它直接连到项目的一个真实缺陷。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、源码：材质解析的完整优先级

**`Runtime/Engine/Public/StaticMeshComponentHelper.h:133-164`：**

```cpp
UMaterialInterface* FStaticMeshComponentHelper::GetMaterial(
    const T& Component, int32 MaterialIndex,
    bool bDoingNaniteMaterialAudit, bool bIgnoreNaniteOverrideMaterials)
{
    // ① 组件 override 材质优先
    if (OverrideMaterials.IsValidIndex(MaterialIndex) && OverrideMaterials[MaterialIndex])
        OutMaterial = OverrideMaterials[MaterialIndex];
    // ② 否则用网格自己的槽材质
    else if (Component.GetStaticMesh())
        OutMaterial = Component.GetStaticMesh()->GetMaterial(MaterialIndex);

    // ③ 如果材质有 Nanite override 且组件启用，它再覆盖一层
    if (OutMaterial)
    {
        if (!bIgnoreNaniteOverrideMaterials
            && Component.UseNaniteOverrideMaterials(bDoingNaniteMaterialAudit))
        {
            UMaterialInterface* NaniteOverride = OutMaterial->GetNaniteOverride();
            OutMaterial = NaniteOverride != nullptr ? NaniteOverride : OutMaterial;
        }
    }
    return OutMaterial;
}
```

**→ **优先级：组件 override > 网格槽 > 再被 Nanite override 替换。****

---

## 二、源码：什么时候用 Nanite override

**`Runtime/Engine/Public/Rendering/NaniteResourcesHelper.h:204-208`：**

```cpp
bool FNaniteResourcesHelper::UseNaniteOverrideMaterials(
    const T& Component, bool bDoingMaterialAudit)
{
    return (bDoingMaterialAudit || ShouldCreateNaniteProxy(Component, nullptr))
        && Nanite::GEnableNaniteMaterialOverrides != 0;
}
```

**🔴 关键：`bDoingMaterialAudit` 为 true 时**短路** —— 不管组件是不是 Nanite 都返回 true。**
**→ 这就是 MapCheck 审计能看到 override 的原因。**

**全局开关（`StaticMeshSceneProxy.cpp:123-133`）：**
```cpp
int32 GEnableNaniteMaterialOverrides = 1;
TEXT("r.Nanite.MaterialOverrides"),
  "Enable support for Nanite specific material overrides."
```

---

## 三、源码：结构体字段名

**`Runtime/Engine/Public/Materials/MaterialOverrideNanite.h:19-78`：**

```cpp
struct FMaterialOverrideNanite
{
    UPROPERTY() bool bEnableOverride = true;
#if WITH_EDITORONLY_DATA
    UPROPERTY(EditAnywhere, meta=(DisplayName="Nanite Override Material"))
    TObjectPtr<UMaterialInterface> OverrideMaterialEditor;   // ← 编辑器里能设的
#endif
protected:
    UPROPERTY(SkipSerialization)
    TObjectPtr<UMaterialInterface> OverrideMaterial;         // ← 仅 cooked 包里有
};
```

**→ Python 侧只有 **`override_material_editor`** 能设。
`b_enable_override` 和 `override_material` 都**读不到也设不了**（不是反射可见）。**

---

## 四、实测：项目现状

**✅ 实测（扫 `/Game` 的 546 个材质，抽查前 60 个）：**

```
r.Nanite.MaterialOverrides = "1"      LastSetBy: Constructor   → 全局启用
r.Nanite                   = "1"      Constructor
materials found: 546
checked 60, with a nanite override: 0        ← 一个都没设

M_LabTex:
  nanite_override_material  <Struct 'MaterialOverrideNanite'>   ← 是结构体
  used_with_nanite          False
```

**→ 项目里**没有任何材质**用了 Nanite override。**

---

## 五、🎯 实测：设一个 override

**代码（`Tools/mat_nanite_set2.py`）：**
```python
structure = base.get_editor_property("nanite_override_material")
structure.set_editor_property("override_material_editor", red)
base.set_editor_property("nanite_override_material", structure)
```

**✅ 实测输出：**
```
set override_material_editor   ok
struct written back
override_material_editor   'M_LabRedOverride'
library says: 'M_LabRedOverride'          ← 两条读回路径一致
used_with_nanite: False -> True
saved: True
```

**→ 设上了，而且**两种读法结果一致**（直接读属性 / `get_nanite_override_material`）。**

**⚠️ 第一次我猜的字段名 `b_override_material` 和 `nanite_override_material` 都**不存在** ——
**必须读源码拿真实字段名**，这是本系列第 5 次因为猜名字失败。**

---

## 六、🎯 画面证明：Nanite 立方体渲染成红色

**步骤：**
```
1. 给 /Engine/BasicShapes/Cube 开 Nanite（默认关 → 开）
2. 放一个 120 cm 立方体，材质用 M_LabTex（网格纹理）
3. M_LabTex 的 Nanite override = M_LabRedOverride（纯红）
```

**结果：**

![Nanite 覆盖](</C:\Users\tk\Desktop\lingxujie\Saved\shot_nanite.png>)

**左上角那块是**红色**的 —— 而它用的材质是 `M_LabTex`（网格纹理）。**

**→ 那红色就是 `M_LabRedOverride` —— **Nanite override 生效了**。**

---

## 七、🎯 这对项目的意义

**项目之前的诊断结论：**
> 101 个 Nanite 网格，槽材质全是 `WorldGridMaterial`，
> 98 个靠**组件 override** 拿到真材质，1 个（`MX_BOSS001_STATIC`）没有。

**现在可以解释清楚了：**

| 机制 | 位置 | 优先级 |
| --- | --- | --- |
| **组件 override** | `OverrideMaterials[index]` | **最高** |
| 网格槽材质 | `GetStaticMesh()->GetMaterial(index)` | 中 |
| **Nanite override** | 材质的 `FMaterialOverrideNanite` | **最后替换一层** |

**→ 项目那 98 个网格是走**第 1 层**（组件 override）解决的。
→ 项目**没用过第 3 层**（0 / 60 材质有 override）。
→ **`MX_BOSS001_STATIC` 缺材质，有两条路可修：**
  - **给它组件 override 一个材质**（简单）
  - 或者给 `WorldGridMaterial` 加 Nanite override（**不推荐**，那是引擎资产）

**→ 现在明确了：这是同一个问题的两条不同解法，不是两个问题。**

---

## 八、这一块学到什么

**1. 🎯 材质解析有**三层优先级**，Nanite override 是最后一层替换。**

**2. 🔴 审计标志会短路 `UseNaniteOverrideMaterials` —— 审计时不管组件是不是 Nanite 都看 override。**

**3. 🔴 结构体字段名必须读源码。**
`OverrideMaterialEditor`（编辑器）vs `OverrideMaterial`（cooked）。
**Python 只能设前者。**

**4. 项目 0/60 材质用了 Nanite override** —— 所以那 98 个靠的是组件 override。**

**5. 猜测字段名的代价：这一块猜了两次才查源码。**

---

## 九、更正

| 之前 | 现在 |
| --- | --- |
| 「Nanite 网格缺材质是**一个问题**」 | ✅ **是三层解析机制里的**两个不同修法**** |
| 「`used_with_nanite` 和 override 是一回事」 | ❌ **两个独立的东西**：usage 标志 vs 覆盖材质 |

---

## 十、下一块

**转 UI/UMG**（目标里的下一项）。

**材质这块三轮已经很扎实：**
- 常量材质（M01）
- 参数化 + 实例（M02）
- Nanite override 完整链条（M03）

**⚠️ 练习关卡 10 actor（已清理测试立方体），引擎 Cube 的 Nanite 已改回 False，主关卡 116 actor。**
**M_LabTex 保留了 Nanite override 和 usage 标志（这是成果，不删）。**
