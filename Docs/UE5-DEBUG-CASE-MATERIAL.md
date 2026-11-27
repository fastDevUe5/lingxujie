# 实战诊断 004：一百个「缺材质」的误报，和一个真的

> **起点：日志里 `MapCheck` 的一条警告，以及我在体检时注意到的 101 个 Nanite 网格。**
>
> **结论分两半：**
> **① 「101 个 Nanite 网格都用默认材质」是**误报** —— 98 个靠组件 override 正常显示。**
> **② 但查出一个**真的**：`MX_BOSS001_STATIC` 既没素材质也没 override，而 `M_Boss_Mob01` 就在项目里。**
>
> **⚠️ 这一篇的重点不是那个真缺陷，是**我怎么差点报错一个假缺陷**。**
>
> **日期：2026-11-26 · UE 5.8.4**

---

## 一、起点：日志里的 74 条告警

**用「先扫再查」的方式，把日志里所有 Warning/Error 按类别统计（✅ 实测）：**
```
total warning/error lines: 74

  LogPython                Warning  16    （我自己测试脚本打的）
  LogPython                Error    15    （同上）
  LogAutomationTest        Error    13    Condition failed
  LogInterchangeEngine     Error     8    发现无效网格体数据（NAN）    ← 案例 002
  LogEditorAssetSubsystem  Error     7    LoadAsset failed             ← 另一个案例
  LogInterchangeImport     Warning   3    网格体拥有未指定材质的图元
  MapCheck                 Warning   2    M_Ground_Triplanar 材质缺失使用标记Nanite
  LogStaticMesh            Warning   2    近零法线                    ← 案例 002
  LogTexture               Warning   1    Texture2D contains no miplevels!
  LogAnimation             Warning   1    Invalid animation skeleton
  ...
```

**本篇查的是**材质**那一条。**

---

## 二、第一个发现：看起来像 101 个缺陷

**扫所有 Nanite 网格的材质槽（✅ 实测）：**
```
nanite-enabled static meshes: 101
WorldGridMaterial occurrences: 101
唯一材质: WorldGridMaterial
```

**`WorldGridMaterial` 是引擎的**「未赋材质」默认灰格材质**。**

**→ 如果直接下结论：「101 个 Lanzhou 建筑全都没材质」。**

**⚠️ **这是个假结论。**而它看起来非常像真的 —— 数字一致、重复 101 次。**

---

## 三、🔴 关键的一步：先验证再说

**我没有写那份报告，而是先问了一句：
**「截图上建筑明明有贴图，那材质是从哪来的？」**

**→ 检查组件级 override（✅ 实测）：**
```
static mesh components showing a real material: 98
static mesh components still on WorldGridMaterial: 1
    grid on MX_BOSS001_STATIC  (WorldGridMaterial)

样本：
  MX_TERRAIN                 -> M_Ground_Triplanar
  MX_LZ_101_10_SOONGSAN_DOOR -> M_LZ_101_10_SOONGSAN_DOOR
  MX_LZ_10_SOONGSAN_BRICK    -> M_LZ_10_SOONGSAN_BRICK
  MX_LZ_17_101_STONEW01      -> M_LZ_17_101_STONEW01
```

**→ 98 个组件通过 `override_materials` 拿到了正确材质。
→ **资产级材质槽为空是这个项目的**正常工作流**，不是缺陷。**

**→ 只有 **1 个** 真的没有材质。**

---

## 四、那个真的缺陷

**`MX_BOSS001_STATIC`（✅ 实测）：**
```
mesh: /Game/Moxiang/Static/boss001_static/StaticMeshes/SM_Boss001.SM_Boss001
mesh slot count: 1
  slot 0: 'WorldGridMaterial'        ← 资产上没赋
component material count: 1
  effective 0: 'WorldGridMaterial'   ← 组件也没 override

项目里存在的候选材质：
  M_Boss_Mob01  (Material)           ← 就是给这个模型做的

nanite enabled on this mesh: True
```

**→ 这个 actor 用默认灰格渲染。**
**→ 截图 `Saved/shot_scatter2.png` 里那个**灰白大块**就是它。**
**→ 而 `M_Boss_Mob01` **已经在项目里**，只是从没赋给这个 actor。**

### 4.1 为什么它被漏掉了

**`MX_BOSS001`（骨骼版）在更早的轮次里做了材质处理（`apply_boss_material.py` 等）。
但 `MX_BOSS001_STATIC`（静态网格版）是另一个 actor，**没有跟上**。**

**→ 这是「修了一个，忘了另一个」的典型。**

---

## 五、🔴 方法论：这次差点犯的错

**「101 个 Nanite 网格都用 WorldGridMaterial」这句话：**

| 成分 | 真假 |
| --- | --- |
| 101 个 Nanite 网格 | **真** |
| 都用 WorldGridMaterial | **真**（资产槽）|
| 「所以都缺材质」 | **假**（组件 override 补上了）|

**→ **三个陈述里两个是真的，只有推论是假的。**这是最容易骗过自己的形态。**

**和本系列之前的错误对照：**

| 轮 | 我说 | 实际 | 同型 |
| --- | --- | --- | --- |
| 5 | 107 个遗留资产 | 是被引用的贴图 | 数字真、含义错 |
| 7 | Lumen 是零 | 一直在跑 | 数字真、含义错 |
| 资产篇 | Textures 只有 1 个 | 实际 99 个 | **分母错** |
| **本轮** | **101 个缺材质** | **98 个有 override** | **数字真、含义错** |

**→ 这是第四次同型错误被**提前拦住**。**

**⚠️ 拦住它的不是一个方法，是一句**直觉反问**：
**「画面上明明有贴图，那材质从哪来的？」**

**→ 结论与观察矛盾时，先信观察。**

---

## 六、正确的表述方式

**❌ 错误写法：**
> 「101 个 Nanite 网格缺材质」

**✅ 正确写法：**
> 「101 个 Nanite 网格的**资产级**材质槽是 `WorldGridMaterial`，
> 但其中 **98 个**通过组件 override 正确显示。
> **只有 1 个（`MX_BOSS001_STATIC`）既无资产材质也无 override。**」

**→ 差别在于：前者说「101 个问题」，后者说「1 个问题」，而后者才是真的。**

---

## 七、这条警告本身怎么理解

**日志原文：**
```
MapCheck: Warning: M_Ground_Triplanar 材质 ... 缺失使用标记Nanite。
如果材质资产未重新保存，那么其在编辑器外运行时可能...
```

**实测 `used_with_nanite`：**
```
M_Lanzhou_Stone              True
M_Ground_Triplanar           True    ← 内存里已经是 True
M_Moxiang_Building           False
M_Boss_Mob01                 False
M_Moxiang_Stone              False
```

**→ 警告说的是「**如果材质资产未重新保存**」——
**内存里是 True，但**磁盘上存的可能还是 False**。**

**→ 这是 MapCheck 在比较「运行时状态」和「已保存状态」。**
**→ 修法：重新保存那个材质。**（待做，需授权）

**⚠️ 注意 `M_Boss_Mob01` 也是 `False` —— 所以就算赋给 `MX_BOSS001_STATIC`，
它也不是 Nanite-ready 的材质。两件事要一起处理。**

---

## 八、待修（**未应用**）

| # | 事项 | 依据 |
| --- | --- | --- |
| 1 | 给 `MX_BOSS001_STATIC` 赋 `M_Boss_Mob01` | 实测唯一无材质组件 |
| 2 | 把 `M_Boss_Mob01` 的 `used_with_nanite` 设为 True 并保存 | 它挂的网格是 Nanite |
| 3 | 重新保存 `M_Ground_Triplanar` | 消除 MapCheck 警告 |
| 4 | 查 `T_Boss_Mob01` 的 mip 设置 | 日志报「contains no miplevels」|
| 5 | 查 `LogAnimation: Invalid animation skeleton` | **可能补充案例 001** |

**⚠️ 按用户要求「先不要急着开发」，一条都没改。**

---

## 九、这次的方法清单

| 步 | 做什么 | 得到什么 |
| --- | --- | --- |
| 1 | **按类别统计日志告警** | 74 条里的 11 类 |
| 2 | 挑可疑的查 | 材质相关 |
| 3 | 扫全部 Nanite 网格的材质 | 101 个 WorldGrid（看起来是缺陷）|
| 4 | **检查组件 override** | **98 个其实正常** |
| 5 | 聚焦剩下的 1 个 | 真缺陷 |
| 6 | 查项目里有没有对应材质 | `M_Boss_Mob01` 存在 |

**→ 第 4 步是唯一拦住误报的一步。**
**→ 它来自一句反问，不是来自任何工具。**

---

## 十、更正（2026-11-27，已实测）

**第八节那条「组件也没 override」的措辞不准确。**

**实测：`MX_BOSS001_STATIC` 的组件 `overrideMaterials` 里有一条**显式** `WorldGridMaterial`，
不是空数组。**结论不变**（这个 actor 真的没有材质），但**修法完全不同**：

```
StaticMeshTools.set_material(资产, 槽, M_Boss_Mob01)   ← 返回 true、回读也对，但画面不变
ObjectTools.set_properties(组件, {"overrideMaterials": [M_Boss_Mob01]})  ← 这个才生效
```

**→ 原因是组件 override 优先于资产槽。详见 gotcha #116。**

**已应用**：`MX_BOSS001_STATIC` → `M_Boss_Mob01`（组件 override），关卡已保存；
`Tools/place_static_boss.py` 也补了逐槽赋材质，重建 actor 时不会再丢。
