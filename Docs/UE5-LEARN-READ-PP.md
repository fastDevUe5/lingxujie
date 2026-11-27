# UE5 学习 · 补读（八）：后处理材质 —— 全 Python 从零建一个，实测变成灰度

> **这是本系列**第一次完全用 Python 从零建出一个**后处理材质**并证明它生效**。**
> **饱和度从 52.68 降到 0.05 —— 整幅画面变灰度。**
>
> **日期：2026-11-27 · UE 5.8.4**

---

## 一、文档给了三条硬要求

> **「A post processing material needs to specify the material domain **post process**:
> The material should only use **Emissive Color** to output the new color.」**

### 1.1 Blendable Location 三选一

| 位置 | 特点 |
| --- | --- |
| **Before Tonemapping** | **HDR**，用 `Post Process Input 0`；**修 TAA 和 GBuffer 查询的问题** |
| **After Tonemapping** | **LDR**，**性能首选**（精度和带宽需求低）；Input 2（tonemap 前）/ 3（后）|
| **Before Translucency** | 比 Before Tonemapping 更早 |

**→ 文档明确：`After Tonemapping` 是**性能首选**，因为 LDR 更省带宽。**

### 1.2 其它章节

```
Post Processing Graph
Using a Post Process Material
Blending Between Different Material Instances
The Material Expression "SceneTexture"
Using GBuffer Properties
CustomDepth / CustomDepth Stencil
Temporal Anti-Aliasing or Why the GBuffer Jitters
UV and ScreenPosition / Filtered texture lookups
Replacing the Tonemapper
Known Issues / FAQ
```

---

## 二、🎯 从零建材质（✅ 全部成功）

```
created /Game/Learning/M_PPDesat
domain: <MaterialDomain.MD_POST_PROCESS: 4>                       ✅
scene texture: PPI_POST_PROCESS_INPUT0                            ✅
scene -> desaturation                                             ✅
scalar parameter Desaturation = 1.0                               ✅
lerp: A = scene colour, B = desaturated, alpha = Desaturation     ✅
lerp -> Emissive Color                                            ✅
blendable_location <BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING: 0>   ✅
blendable_priority 0
```

**节点图：**
```
SceneTexture(PPI_POST_PROCESS_INPUT0)
        │
        ├──────────────► Lerp.A（原色）
        │
        └──► Desaturation ──► Lerp.B（去饱和）
                                │
        ScalarParameter ───────► Lerp.Alpha（Desaturation）
                                │
                                └──► Emissive Color
```

**→ 默认 `blendable_location` 就是 `AFTER_TONEMAPPING` —— 正好是文档说的性能首选，不用改。**

---

## 三、🔴 应用环节踩了两个字段名（又是猜名字）

**第一次尝试：**
```
'WeightedBlendables' object is not iterable
Failed to find property 'material'
```

**→ 两个字段名都猜错了。**

**✅ 用内省（`dir()`）+ 逐个试 `get_editor_property` 找到真名：**

| 我以为 | **真名** |
| --- | --- |
| `weighted_blendables` 可直接迭代 | **`.get_editor_property("array")`** |
| `WeightedBlendable.material` | **`WeightedBlendable.object`** |

**→ 正确写法：**
```python
container = settings.get_editor_property("weighted_blendables")
entries = container.get_editor_property("array")

entry = unreal.WeightedBlendable()
entry.set_editor_property("weight", 1.0)
entry.set_editor_property("object", material)     # ← object，不是 material
entries.append(entry)

container.set_editor_property("array", entries)
settings.set_editor_property("weighted_blendables", container)
```

---

## 四、🎯 实测结果

### 4.1 权重 0（= 关闭）vs 权重 1（= 全开）

```
weight 0 : 平均饱和度 52.68       ← 正常彩色
weight 1 : 平均饱和度  0.05       ← 几乎完全灰度
```

**像素差异：**
```
pixels differing by more than 8: 792,091 (97.57%)
mean absolute channel delta: 19.198
VERDICT: the two captures differ over most of the frame
```

**→ **97.57% 的像素变了，饱和度归零。****
**→ 后处理材质**完全按设计生效**。**

### 4.2 画面

![后处理灰度](</C:\Users\tk\Desktop\lingxujie\Saved\shot_pp2_1.png>)

**天空、云、地面、六个形体 —— **全部变成单色**。**

---

## 五、这一篇学到什么

**1. 🎯 后处理材质的三条要求：Domain = Post Process、只用 Emissive Color、Blendable Location 决定 HDR/LDR。**

**2. 🔴 `After Tonemapping` 是**性能首选**（LDR，带宽小），且它是**默认值**。**
→ 想省性能，不要选 `Before Tonemapping`。

**3. 🔴 又踩了「猜字段名」（本系列第 7 次）。**
- `WeightedBlendables` → 必须走 `.array`
- `WeightedBlendable.material` → 实际叫 **`.object`**

**→ 正确做法：先 `dir()` 内省，再试 `get_editor_property`，不要猜。**

**4. 🎯 「饱和度」是一个好判据。**
用它验证「去饱和材质」比看平均亮度直接得多 —— 52.68 → 0.05 是**语义对应**的数字。

**5. 整个后处理材质**从零到生效**全在 Python 里完成，没有手点编辑器。**

---

## 六、更正

| 之前 | 现在 |
| --- | --- |
| 「后处理材质必须手工建」 | ✅ **可以全 Python 建，已验证** |
| 「`WeightedBlendable` 有 `material` 字段」 | ❌ **叫 `object`** |

---

## 七、还没做到

| 项 | 说明 |
| --- | --- |
| `Before Tonemapping` 的对比 | 只用了默认的 After |
| GBuffer 查询（法线/深度）| 只用了 Scene Color |
| `CustomDepth` / `Stencil` | 没试 |
| 替换 Tonemapper | 没试 |
| 多个 blendable 的优先级顺序 | 只放了一个 |

---

## 八、状态

```
Docs/UE5-LEARN-READ-PP.md   1 篇（共 31 篇 learn 文档）
补读进度：8 / 57
资产：/Game/Learning/M_PPDesat（保留，作为「后处理材质可全 Python 建」的证据）
场景已还原：blendable 已移除（0 个）、主关卡 116 actor、视口复位
```

---

## 九、下一篇

**继续补读。`temporal-super-resolution.md`（85 KB，最大的文档）** ——
渲染域最后一块大骨头。
