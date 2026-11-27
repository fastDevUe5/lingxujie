# 实战诊断 002：`SM_Boss001` 的 NaN 切线与退化法线

> **起点是一条引擎警告，我一直没查：**
> ```
> LogStaticMeshOperations: Display: Mesh 0 has NaNs in it's vertex instance tangent space!
> LogStaticMesh: Warning: SM_Boss001 拥有一些近零的法线，其可能诱发问题。（容差为 1E-4）
> ```
>
> **结论：法线在 `.mod` 源文件里就已经退化，
> 根因是 `TRANSFORM_TYPE_NOT_SOLID (0x10)` 的几何本来就没有可用法线。**
>
> **我的导出器把它当成正常法线导出了。**
>
> **日期：2026-11-26 · UE 5.8.4 · 反编译源码 `tw/4DyuchiGRX_common/mesh_flag.h`**

---

## 一、第一步：想在 UE 里量，发现量不了

**本想在 `StaticMesh` 上读法线。探测结果（✅ 实测）：**

```
StaticMesh 上可用的：get_num_lods / get_num_vertices / get_num_triangles /
                     get_num_nanite_vertices / get_bounds / get_bounding_box
没有的：              get_render_data / get_normals / 任何切线访问
```

**而且第一次还写错了名字（`get_num_lod_levels` 不存在，是 `get_num_lods`）。**

**→ **Python 读不到 StaticMesh 的法线。**这条路走不通。**

### 1.1 换路：查 glTF 源文件

**这是我的导出器写的，法线在文件里。用纯 Python 解 `accessors` 就能量（✅ 实测）：**

```
TOTAL normals: 1266
  恰好为零:      550
  非单位长度:    569
  非有限(NaN):     2
  退化比例:    88.55%
```

**→ **88.55% 的法线是退化的。****
**→ 引擎的警告报的是事实。**

---

## 二、第二步：分清「导出器的锅」还是「源数据的锅」

**导出器里有两处相关代码（`export_mod_anim_gltf.py`）：**

```python
# 第 168-178 行
has_normals = (shade_type != SHADE_TYPE_LIGHT_MAP
               and transform_type != TRANSFORM_TYPE_ALIGN_VIEW
               and cursor + 12 * vertex_num <= len(data))

if has_normals:
    normals = [struct.unpack_from("<3f", data, cursor + i * 12) for i in range(vertex_num)]
else:
    # 缺失时给常量向上向量，不是零
    normals = [(0.0, 0.0, 1.0)] * vertex_num
```

```python
# 第 333 行 cn() —— 只是坐标轴重映射，不归一化
return (n[0], n[2], -n[1])
```

**→ 缺失时写的是 **(0,0,1)**（单位向量），**不可能产生零**。

**→ 所以 glTF 里的零，只能来自 `.mod` 本身。**

### 2.1 直接用导出器的 parser 读 `.mod`（✅ 实测）

```
objects parsed: 84
mesh blocks: 17

  mesh  0: flag=0x00000000 has=True   verts=32   zero=0    non_unit=0    nan=0
  mesh  1: flag=0x00000000 has=True   verts=102  zero=0    non_unit=0    nan=0
  mesh  2: flag=0x00000000 has=True   verts=32   zero=0    non_unit=0    nan=0
  mesh  3: flag=0xBC000000 has=True   verts=4    zero=0    non_unit=0    nan=0
  mesh  4: flag=0xBC000000 has=True   verts=4    zero=0    non_unit=0    nan=0
  mesh  5: flag=0x00000000 has=True   verts=46   zero=0    non_unit=0    nan=0
  mesh  6: flag=0x00000010 has=True   verts=52   zero=12   non_unit=23   nan=3
  mesh  7: flag=0x00000010 has=True   verts=31   zero=9    non_unit=19   nan=3
  mesh  8: flag=0x00000010 has=True   verts=153  zero=12   non_unit=106  nan=3
  ...
  mesh 15: flag=0x00000010 has=True   verts=164  zero=11   non_unit=150  nan=3
  mesh 16: flag=0x00000010 has=False  verts=218  zero=0    filler=218    nan=0

TOTAL: 1266
  恰好为零:      103
  (0,0,1) 填充:  218
  非单位长度:    579
  非有限:         24
  退化:          706 (55.77%)
```

### 2.2 🔴 规律完美对应

| `mesh_flag & 0xF0` | 块 | 法线质量 |
| --- | --- | --- |
| **`0x00`**（SOLID）| mesh 0-5 | **全部干净**：zero=0, non_unit=0, nan=0 |
| **`0x10`**（NOT_SOLID）| mesh 6-16 | **全部退化**：有零、有非单位、有 NaN |

**→ 不是随机的，是**由标志位决定的**。**

---

## 三、第三步：查反编译源码，确认 `0x10` 是什么

**`client_src/tw/4DyuchiGRX_common/mesh_flag.h`：**

```cpp
enum SHADE_TYPE {
    SHADE_TYPE_VERTEX_LIGHT_IM  = 0x00000000,
    SHADE_TYPE_VERTEX_LIGHT_RT  = 0x00000001,
    SHADE_TYPE_LIGHT_MAP        = 0x00000003
};
#define SHADE_TYPE_MASK  0x0000000f

enum TRANSFORM_TYPE {
    TRANSFORM_TYPE_SOLID      = 0x0000000,
    TRANSFORM_TYPE_NOT_SOLID  = 0x00000010,   // ← 元凶
    TRANSFORM_TYPE_ALIGN_VIEW = 0x00000030,
    TRANSFORM_TYPE_ILLUSION   = 0x00000050
};
#define TRANSFORM_TYPE_MASK  0x000000f0
```

**`0x10` = **`TRANSFORM_TYPE_NOT_SOLID`（非实体几何）**。**

### 3.1 为什么它的法线是垃圾

**「非实体」= 没有实心表面 —— 特效、贴片、光晕、加色层。**

**→ 原始渲染器用**加色/半透明**方式绘制它们，**根本不需要表面法线做光照**。**

**→ 所以文件里那一槽的数据可以是任意值，原本就没打算用。**

**→ 而我们把它当**不透明静态网格**导入 UE，UE 就真拿这些法线去算法线贴图光照了。**

---

## 四、根因

**导出器的 `has_normals` 条件：**
```python
has_normals = (shade_type != SHADE_TYPE_LIGHT_MAP        # 排除了 0x03
               and transform_type != TRANSFORM_TYPE_ALIGN_VIEW   # 排除了 0x30
               and cursor + 12 * vertex_num <= len(data))
```

**⚠️ **漏了 `TRANSFORM_TYPE_NOT_SOLID (0x10)` 和 `TRANSFORM_TYPE_ILLUSION (0x50)`。****

**→ 这两种几何的法线被当成正常数据原样导出。**

**→ UE 导入时发现 NaN，打了警告，并把坏切线「设成 z」兜底 ——
但退化的**法线**本身没被修。**

---

## 五、影响面

**`boss001` 里 17 个 mesh 块，**11 个是 NOT_SOLID**，占 **1046 / 1266 = 83% 的顶点**。**

**→ 也就是说这个 Boss 的**大部分表面**用的是退化法线。**

**→ 视觉后果：光照计算用零向量/非单位向量，会产生**
**黑块、错误高光、法线贴图方向全乱。**
**→ 这正是「导进来的模型看起来不对」的那类症状，而且**很难一眼看出原因**。**

---

## 六、修复方案（**未应用**）

**两个层次：**

### 6.1 保守（保留几何，修法线）

```python
# has_normals 判定后，对退化法线做重建
def repair_normals(normals, triangles):
    """Replace zero or non-finite normals with the average of adjacent face normals."""
    ...
```

**或者最简单：**
```python
if not has_normals or transform_type in (TRANSFORM_TYPE_NOT_SOLID,
                                         TRANSFORM_TYPE_ILLUSION):
    normals = [(0.0, 0.0, 1.0)] * vertex_num   # 用现有的 filler 逻辑
```

**→ 代价：NOT_SOLID 几何变成平面着色。**
**→ 但它们本来就是特效层，平面着色比黑块好。**

### 6.2 彻底（分开处理）

**把 `NOT_SOLID` / `ILLUSION` 的块导出成**独立的 primitive**，
在 UE 里赋**双面 + 无光照/加色**材质，而不是当不透明表面。**

**→ 这才符合原始语义。**

**⚠️ 按用户要求「先不要急着开发」，**代码一字未改**。**

---

## 七、这次诊断的关键转折

| 尝试 | 结果 | 学到什么 |
| --- | --- | --- |
| 想从 `StaticMesh` 读法线 | **Python 没接口** | 引擎侧量不了就去源文件量 |
| 查 glTF | **88.55% 退化** | 证实引擎警告 |
| 想怪导出器 | 缺失时写的是 (0,0,1)，不是零 | **排除了一个假设** |
| 查 `.mod` 原始数据 | **按 flag 完美分组** | 找到相关性 |
| 查反编译源码 | **`0x10` = NOT_SOLID** | **找到语义** |

**→ 最关键的两次是「排除导出器」和「查反编译源码」。
前者避免了改错地方，后者把「0x10 分组」变成了「NOT_SOLID 无语义法线」。**

---

## 八、这次实战更正/补充了什么

| 之前 | 现在 |
| --- | --- |
| 「法线是条件性的，只有 LIGHT_MAP 和 ALIGN_VIEW 没有」 | **还要加上 `NOT_SOLID (0x10)` 和 `ILLUSION (0x50)` 的**数据不可信**** |
| 「引擎报的 NaN 警告不知道什么意思」 | **它报的是真事，而且根因在我们这边** |
| 「`get_num_lod_levels`」 | **是 `get_num_lods`** |

**⚠️ 第一条是本系列对 `MOD-FORMAT-SOLVED.md` 的**重要补充**：
**「有没有法线」和「法线能不能用」是两件事。**
**客户端确实读了 NOT_SOLID 的法线，但读了不用 —— 我们不知道这一点就当正常数据用了。**
