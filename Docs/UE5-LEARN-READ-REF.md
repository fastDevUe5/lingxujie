# UE5 学习 · 补读（十）：反射与捕获 —— 开了 Lumen，捕获就是白放的

> **这一篇的结论是「**没问题，但值得记下来**」。**
> **文档说开 Lumen 后反射捕获不起作用；源码枚举证实；项目里确实一个都没放。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档结构（20 KB，17 节）

```
Reflections Captures
Reflection Capture Shapes
  Sphere shape   ← "currently the most useful"
  Box shape      ← "very limited in usefulness... only works for hallways or rectangular rooms"
Reflection Capture Properties
Runtime Capture
Setting Up a Level to use the Reflection Environment
Glossy Indirect Specular
Reflection Capture Lightmap Mixing
Lightmap Mixing and Existing Content
Editing Reflection Probes
Using a Custom HDRI Cubemap in a Reflection Probe
Adjusting Reflection Probe Resolution
Adjusting Skylight Reflection Resolution
Blending Multiple Reflection Probe Data
Visualizing
Performance Considerations
Limitations
```

**文档对两种形状的评价很直接：**
- **球体：「currently the most useful」** —— 永远不匹配几何形状，但到处都能用
- **盒体：「very limited in usefulness」，只适合走廊或矩形房间**

---

## 二、🎯 文档的核心断言

> **「Reflection Captures only contribute when **Lumen isn't providing** your project's indirect lighting.」**
> **「When Lumen Global Illumination is enabled, **which is the default for new projects**,
> Lumen provides all indirect specular lighting」**

**→ 开 Lumen → 反射捕获**不参与**。**

---

## 三、✅ 源码核实：枚举注释说得更明确

**`Engine/Source/Runtime/Engine/Classes/Engine/EngineTypes.h:472`**
```cpp
namespace EReflectionMethod
{
    enum Type : int
    {
        /** No global reflection method will be used.
         *  **Reflections can still come from Reflection Captures, Planar Reflections
         *  or a Skylight placed in the level.** */
        None,

        /** Use Lumen Reflections, which supports Screen / Software / Hardware Ray Tracing
         *  together and integrates with Lumen Global Illumination for rough reflections
         *  and Global Illumination seen in reflections. */
        Lumen,

        /** Standalone Screen Space Reflections. Low cost, but limited by screen space information. */
        ScreenSpace UMETA(DisplayName="Screen Space"),
    };
}
```

**→ **只有 `None` 的注释里提到 Reflection Captures。****
**→ `Lumen` 的注释里完全没有捕获 —— 它自己接管全部反射。**

**同文件 `EDynamicGlobalIlluminationMethod`（452 行）：**
```cpp
None          // 无动态 GI（烘焙光照仍可用）
Lumen         // 全部光源 + 自发光 + SkyLight 遮蔽
ScreenSpace   // DEPRECATED
Plugin
```

---

## 四、✅ 本项目实测

### 4.1 两个关卡都没有反射捕获（✅）

```
LingXuJie   116 actors  {'SkyLight': 1, 'PostProcessVolume': 1}
L_Scene01    14 actors  {'SkyLight': 1, 'PostProcessVolume': 1}
```

**→ **一个 Sphere/Box Reflection Capture 都没有。****
**→ 项目正确地依赖 Lumen，没有放多余的捕获。**

### 4.2 相关 CVar

```
r.DynamicGlobalIlluminationMethod   = 1     ← Lumen
r.ReflectionMethod                  = 1     ← Lumen
r.Lumen.Reflections.Allow           = 1     ← 开
r.SSR.Quality                       = 3     Scalability
r.SkyLight.RealTimeReflectionCapture= 1     Constructor
```

**→ 全部指向 Lumen 反射路径。**

---

## 五、🎯 这一篇的实际价值：一个「不用做」的清单

**因为项目用 Lumen 反射，下面这些**都是白费功夫**：**

| 想做的事 | 用 Lumen 时 |
| --- | --- |
| 放 Sphere Reflection Capture | ❌ **无效** |
| 放 Box Reflection Capture（走廊）| ❌ **无效** |
| 调捕获分辨率 | ❌ **无效** |
| 用自定义 HDRI 立方体贴图做探针 | ❌ **无效** |
| 混合多个探针的立方体贴图 | ❌ **无效** |
| 用 Reflection Override 视图看捕获 | ⚠️ 能看，但看的不是实际生效的 |

**→ **如果哪天要关掉 Lumen 反射**（比如为了性能），
**那时候才需要放探针** —— 这正是文档说的 `EReflectionMethod::None` 的场景。**

---

## 六、这一篇学到什么

**1. 🎯 Lumen 接管**全部**间接镜面反射，反射捕获被旁路。**
**→ 用 Lumen 的项目**不需要放探针**。**

**2. 🔴 源码枚举注释比文档更精确。**
文档说「only contribute when Lumen isn't providing」，
源码直接把「Reflection Captures」写进 `None` 模式的注释里，
**`Lumen` 模式里一个字没提。**

**3. 🎯 两种捕获形状的定位：球体通用，盒体只适合矩形空间。**

**4. ✅ 本项目是干净的** —— 一个探针都没放，没有无效负担。

**5. 「不用做」也是一种知识。**
这一篇没有产出新资产，但它确认了一整类工作**不该做**。

---

## 七、更正

| 之前 | 现在 |
| --- | --- |
| 「反射靠 Reflection Capture」 | ❌ **开 Lumen 时靠 Lumen，捕获无效** |
| 「放着探针不影响」 | ❌ **是纯开销，没收益** |

---

## 八、还没做到

| 项 | 说明 |
| --- | --- |
| 实测「放探针 vs 不放」的画面差异 | 理论上无差异，可以验证但价值低 |
| 关掉 Lumen 反射（`r.ReflectionMethod 0`）后的画面 | 没试 |
| Planar Reflections | 没试 |
| SkyLight 的立方体贴图分辨率 | 没调 |

---

## 九、状态

```
Docs/UE5-LEARN-READ-REF.md   1 篇（共 33 篇 learn 文档）
补读进度：10 / 57
编辑器：主关卡 116 actor（脚本最后停在 L_Scene01，需复位）
```

---

## 十、渲染域小结

**已读：Lumen 6 + Nanite 2 + VSM 1 + 天空大气 2 + 方向光 1 + 后处理材质 1 + TSR 1 + 反射 1 = 15 篇**

**渲染域还剩：**
- `lighting-environment.md`（索引 4.2 KB）
- `light-types.md`（索引 5.5 KB）
- `instanced-materials.md`（索引 9.7 KB）
- `material-editor-guide.md`（7.6 KB）
- `texture-asset-editor.md`（30 KB）

**→ 下一篇 `material-editor-guide.md`（7.6 KB，小但基础）。**
