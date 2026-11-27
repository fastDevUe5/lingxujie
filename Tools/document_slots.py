"""Record the multi-slot fix: one primitive per face group, forty slots where there was one.

The mesh always had forty materials in its source file and was importing with a single slot, so every
part of the boss shared one surface. The face groups each name a material and the exporter was
flattening them, which is why the slot count never matched the source.

    python Tools/document_slots.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 二十二、材质槽：1 → 40（第 37 轮）

### 22.1 面组里本来就有材质索引

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

**每个面组有 `g_mtl`（材质块索引）和 `g_index`（槽索引）。**

**各区件的材质：**
```
boss01_shoulderR  1 面组  材质 [40]
boss_biseok       6 面组  材质 [39, 38, 37, 36, 35, 34]
boss01_shoulderL  1 面组  材质 [33]
boss01_eyeR       1 面组  材质 [32]
boss01_eyeL       1 面组  材质 [31]
```

**所以 `boss001` 用了 **31–40+ 号材质，10 多个不同材质**。**

### 22.2 🔴 问题：导出时把面组合并了

**原来 `read_mod_mesh` 把 6 个面组的所有三角面塞进一个 `triangles` 列表，
导出一个 primitive → UE 只给 **1 个槽**。**

**`boss001` 有 **40 个 MATERIAL 块**，却只用了 1 个槽 —— 全身一个surface。**

### 22.3 修法：每个面组一个 primitive

**① `read_mod_mesh` 保留分组**
```python
groups.append({"material": g_mtl, "slot": g_index, "triangles": group_triangles})
```

**② 每个面组生成独立索引缓冲**
```python
for group in each.get("groups") or []:
    group_flat = [i for tri in group["triangles"] for i in tri]
    accessor = add_accessor(add_view(...), 5123, len(group_flat), "SCALAR")
    group_indices.append((group.get("material", 0), accessor))
```

**③ glTF 允许多个 primitive **共享顶点属性**、只换索引缓冲 —— 所以这很便宜。**

**④ 写 `materials` 数组（占位灰材质），primitive 用 `"material": index` 引用**

### 22.4 结果

```
primitives: 40      <- 原 17
materials: 40       <- 原 0
引用到的材质索引: [0..39]   <- 全部 40 个都用到了

SLOTS: mesh material slots: 40
SLOTS:   slot 0: moxiang_material_0
SLOTS:   slot 1: moxiang_material_1
```

**材质量从 1 变 **40**，与 `.mod` 里的 40 个 MATERIAL 块**精确对应**。**

### 22.5 为什么值得做

**单槽的后果是：Boss 全身一个材质 —— 眼睛、盔甲、链条、头发只能用同一张贴图。**

**现在每个部件有独立槽，可以分别挂对应的贴图。**

**下一步：把 40 个槽映射到 `.mod` 里的 40 个 MATERIAL 块，
再按块里的贴图名分别挂 2,407 个 PNG 中的对应文件。**

### 22.6 结构上的意义

> **这一轮修的是**数据结构的表达能力**，不是渲染效果。**
>
> **之前管道能导出几何，但**丢掉了「哪些面用哪个材质」这个信息**。
> 视觉效果是次要的；**信息丢失**才是问题。**

### 22.7 新增工具

| 工具 | 作用 |
| --- | --- |
| `Tools/add_group_materials.py` | 记录面组的材质索引 |
| `Tools/finish_groups.py` | 按组生成 primitive |
| `Tools/add_materials_array.py` | 写 glTF materials 数组 |
| `Tools/check_slots.py` | 查 UE 里的槽数 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 二十二、材质槽：1 → 40" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
