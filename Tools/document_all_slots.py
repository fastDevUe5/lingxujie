"""Record that all forty slots are assigned, and why the picture did not change.

Assigning the same material to forty slots produces the same image as one slot. Saying that plainly
matters, because the round's value is structural - the slots exist and can differ - not visual.

    python Tools/document_all_slots.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 二十三、40 个槽全部赋材质 —— 但画面不变（第 38 轮）

### 23.1 关键事实：40 个材质用**同一张贴图**

**逐块打印 `boss001.mod` 的 40 个 MATERIAL 块：**
```
MAT @28     dwIndex=0  size=1444  图: ['boss_mob01.tga']
MAT @1480   dwIndex=0  size=1444  图: ['boss_mob01.tga']
...
MAT @56656  dwIndex=0  size=1444  图: ['boss_mob01.tga']
```

**40 个块**全部**引用 `boss_mob01.tga`，`dwIndex` 全是 0。**

**所以它们不是「每个部件一张贴图」，而是**同一张图集的不同 UV 区域**。**

### 23.2 赋值结果

```
ALLSLOT: mesh has 40 slot(s)
ALLSLOT: assigned to 40 of 40 slots (0 failed)
```

**40 个槽全部挂上 `M_Boss_Mob01`，0 失败。**

### 23.3 🔴 画面**没有变化**

**截图与「只有 1 个槽」时**完全相同**。**

**原因很直接：40 个槽用同一张图、同一套 UV，渲染结果必然一样。**

> **这一轮的产出是**结构**，不是外观。**
> **槽存在且可以不同 —— 这是后续按部件贴不同图的前提。
> 现在还不能不同，因为源数据就不需要不同。**

### 23.4 那这一轮有什么意义

| 之前 | 现在 |
| --- | --- |
| 40 个材质信息**丢失**，引擎里 1 个槽 | 40 个槽**存在**，每个可独立赋材质 |
| 想给眼睛单独挂贴图 —— **做不到** | 可以做到（槽 32/31 是眼睛）|
| UV 区域混在一个 primitive 里 | 每个面组独立 primitive，UV 各自完整 |

**即使当前源数据不需要多贴图，**信息保真**本身是管道正确的标志。**

### 23.5 如果将来要按部件贴图，需要什么

**`.mod` 里 40 个材质块只给了 1 个贴图名。**但它们可能还有别的字段**（颜色、透明度、混合模式）没被利用。**

**下一步若要真正的「一个部件一个外观」，需要：**
1. 解析材质块里的**颜色 / 透明度**字段（不只是贴图名）
2. 或从贴图集里按 UV 区域**裁出子图**
3. 或直接接受「一张图集 + 完整 UV」—— 这本来就是原游戏的做法

**第三种是最可能的：原游戏就是一个 Boss 一张图集。**

### 23.6 结论

**材质管线现在**完整**：**
```
.mod 材质块 → 贴图名 → .tif/.dds/.tga → PNG → UE Texture2D → Material → 组件槽（按面组）
```

**「所有槽同一材质」是**源数据的真实情况**，不是管道的简化。**

### 23.7 新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/assign_all_slots.py` | 给所有槽赋同一材质 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 二十三、40 个槽全部赋材质" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
