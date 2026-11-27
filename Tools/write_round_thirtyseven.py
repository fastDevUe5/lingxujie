"""Append the thirty-seventh round.

    python Tools/write_round_thirtyseven.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 54. 第三十七轮：**材质槽 1 → 40**（2026-11-26 38:00）

### 一、面组里本来就有材质索引

**逐面组打印 `boss001` 的一个网格块：**
```
MESH @83800: verts=102 faceGroups=6
   group 0: mtl=39  index=5  faces=7
   group 1: mtl=38  index=4  faces=7
   group 2: mtl=37  index=3  faces=6
   group 3: mtl=36  index=2  faces=6
   group 4: mtl=35  index=1  faces=44
   group 5: mtl=34  index=0  faces=26
```

**各区件的材质：**
```
boss01_shoulderR  材质 [40]
boss_biseok       材质 [39, 38, 37, 36, 35, 34]
boss01_shoulderL  材质 [33]
boss01_eyeR       材质 [32]
boss01_eyeL       材质 [31]
```

### 二、🔴 问题：导出时把面组合并了

**`read_mod_mesh` 把面组的所有三角面塞进一个列表 → 一个 primitive → UE 给 **1 个槽**。**

**`boss001` 有 **40 个 MATERIAL 块**，却只用 1 个槽 —— 全身一个表面。**

### 三、修法

**① 保留分组：**
```python
groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})
```

**② 每个面组生成独立索引缓冲（共享顶点属性）：**
```python
for group in each.get("groups") or []:
    accessor = add_accessor(add_view(...), 5123, len(group_flat), "SCALAR")
    group_indices.append((group.get("material", 0), accessor))
```

**③ glTF 允许多 primitive 共享顶点属性、只换索引缓冲 —— 成本几乎为零。**

**④ 写 `materials` 数组（占位灰材质）+ `"material": index` 引用**

### 四、结果

```
primitives: 40      <- 原 17
materials: 40       <- 原 0
引用到的材质索引: [0..39]   <- 全部 40 个用到

SLOTS: mesh material slots: 40
SLOTS:   slot 0: moxiang_material_0
SLOTS:   slot 1: moxiang_material_1
```

**槽数从 1 变 **40**，与 `.mod` 的 40 个 MATERIAL 块**精确对应**。**

### 五、回归检查（改动影响所有模型）

```
108_bird       1 → 2 块    包围盒不变   ok
198_bobu       3 → 8 块    包围盒不变   ok
boss001       17 → 40 块   包围盒不变   ok
216            1 → 2 块    包围盒不变   ok
20_eagle_01    1 → 5 块    包围盒不变   ok

problems: 0
```

**所有模型 primitive 数增加，包围盒完全不变。**

### 六、为什么值得做（gotcha #105）

**单槽的后果：Boss 的**眼睛、盔甲、链条、头发**只能用同一张贴图。**

**现在每个部件独立槽，可以分别挂对应贴图。**

> **这一轮修的是**数据结构的表达能力**，不是渲染效果。**
>
> **之前管道能导出几何，但**丢掉了「哪些面用哪个材质」这个信息**。
> 视觉效果是次要的，**信息丢失**才是问题 ——
> 它不会报错，只会让所有东西变一个颜色。**

### 七、下一轮（剩 3 轮）

| 轮 | 任务 |
| --- | --- |
| 38 | **40 个槽映射到 40 个 MATERIAL 块的贴图**（按块里的贴图名挂 PNG）|
| 39 | 收口：更新总览 + 交叉引用一致性 |
| 40 | 最终验收：回归 + 报告 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 54." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 54; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
