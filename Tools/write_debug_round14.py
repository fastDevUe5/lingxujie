"""Append the fourteenth debugging round.

    python Tools/write_debug_round14.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 71. 调试系列第 14 轮：**一百个「缺材质」的误报，和一个真的**（2026-11-26 56:00）

### 一、换个方向：先扫日志，再决定查什么

**前三轮都是我怀疑某处、再去查。这轮反过来：按类别统计日志里全部 74 条 Warning/Error。**

```
LogAutomationTest        Error    13   Condition failed
LogInterchangeEngine     Error     8   发现无效网格体数据（NAN）   ← 案例 002
LogEditorAssetSubsystem  Error     7   LoadAsset failed            ← 另一个案例
LogInterchangeImport     Warning   3   网格体拥有未指定材质的图元
MapCheck                 Warning   2   M_Ground_Triplanar 缺失 Nanite 标记
LogTexture               Warning   1   Texture2D contains no miplevels!
LogAnimation             Warning   1   Invalid animation skeleton
```

### 二、🔴 看起来像 101 个缺陷

**扫所有 Nanite 网格的材质槽（✅ 实测）：**
```
nanite-enabled static meshes: 101
WorldGridMaterial occurrences: 101
唯一材质: WorldGridMaterial
```

**`WorldGridMaterial` 是「未赋材质」的默认灰格材质。**
**→ 很容易写成「101 个建筑全都没材质」。**

### 三、🎯 拦住它的一句反问

**「截图上建筑明明有贴图，那材质从哪来的？」**

**→ 检查组件 override（✅ 实测）：**
```
static mesh components showing a real material: 98
static mesh components still on WorldGridMaterial: 1
    grid on MX_BOSS001_STATIC  (WorldGridMaterial)
```

**→ **98 个靠 `override_materials` 正常显示。资产级槽为空是**正常工作流**。**
**→ 只有 **1 个**真的没材质。**

### 四、那个真的

```
MX_BOSS001_STATIC:
  mesh slot 0        = WorldGridMaterial
  component override = 无（有效材质也是 WorldGridMaterial）
  项目里存在 M_Boss_Mob01（就是给它做的）
  nanite enabled = True
```

**→ 用默认灰格渲染，就是截图 `shot_scatter2.png` 里那个**灰白大块**。**
**→ 为什么漏了：`MX_BOSS001`（骨骼版）做过材质处理，`MX_BOSS001_STATIC` 是另一个 actor，**没跟上**。**

### 五、🔴 这是第四次同型错误被**提前**拦住

| 轮 | 我说 | 实际 | 同型 |
| --- | --- | --- | --- |
| 5 | 107 个遗留资产 | 是被引用的贴图 | 数字真、含义错 |
| 7 | Lumen 是零 | 一直在跑 | 同上 |
| 资产篇 | Textures 只有 1 个 | 实际 99 个 | **分母错** |
| **本轮** | **101 个缺材质** | **98 个有 override** | **数字真、含义错** |

**⚠️ 拦住它的不是工具，是一句**直觉反问**。**
**→ 结论与观察矛盾时，先信观察。**

**正确表述：**
> **「101 个网格的**资产级**材质槽是默认材质，但 98 个靠组件 override 正常显示。
> 只有 1 个既无资产材质也无 override。」**

### 六、MapCheck 那条警告怎么理解

**`used_with_nanite` 实测：**
```
M_Lanzhou_Stone        True
M_Ground_Triplanar     True     ← 内存里已经是 True
M_Boss_Mob01           False    ← 这个也是 False
M_Moxiang_Stone        False
```

**→ 警告说的是「**如果材质资产未重新保存**」——
内存 True、磁盘可能还是 False，MapCheck 在比较两者。**
**→ 修法：重新保存材质。**
**→ 而 `M_Boss_Mob01` 也是 False，所以就算赋给 `MX_BOSS001_STATIC`，
它也不是 Nanite-ready 材质，两件事要一起处理。**

### 七、新增

| 产出 | 内容 |
| --- | --- |
| **`Docs/UE5-DEBUG-CASE-MATERIAL.md`** | 误报 + 真缺陷 + 方法论 |
| `Tools/diag_warn_step1/2/3/4.py` | 四步：扫网格 → 查 override → 聚焦 → 确认 |

### 八、待修清单（**未应用**）

| # | 事项 |
| --- | --- |
| 1 | 给 `MX_BOSS001_STATIC` 赋 `M_Boss_Mob01` |
| 2 | 把 `M_Boss_Mob01` 的 `used_with_nanite` 设为 True 并保存 |
| 3 | 重新保存 `M_Ground_Triplanar` |
| 4 | 查 `T_Boss_Mob01` 的 mip 设置 |
| 5 | 查 `LogAnimation: Invalid animation skeleton`（**可能补充案例 001**）|

### 九、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | 查 `Invalid animation skeleton` —— 它可能推翻案例 001 的一部分 |
| 2 | 查 13 条 `LogAutomationTest: Condition failed` |
| 3 | 查贴图 mip |

**⚠️ 代码仍未改。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 71." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 71; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
