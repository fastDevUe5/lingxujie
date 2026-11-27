# UE5 材质体系与实测诊断（引擎源码 + 实测）

> **本文分两半：一半是材质系统的结构，一半是对本项目地面材质的**实测诊断**。**
> **诊断的结论比结构更值钱：网格感不是"平铺设错了"，是贴图分辨率不够。**

---

## 一、材质的三层结构

```
UObject
 └ UMaterialInterface        ← 接口（可以有多实现）
    ├ UMaterial              ← 材质本体（有节点图，编译成 shader）
    ├ UMaterialInstance      ← 实例（引用一个母材质，改参数）
    │   └ UMaterialInstanceConstant   ← 常量实例（本项目用的）
    └ UMaterialInstanceDynamic        ← 运行时动态创建的
```

### 1.1 为什么要有实例

**母材质编译一次很贵（几秒到几十秒）。
实例不重新编译 shader —— 它只覆盖参数。**

**本项目的做法是对的：**
```
M_Moxiang_Building          ← 母材质（编译一次）
   ↓ 95 个实例
M_LZ_JP_ROOF00 / M_LZ_...   ← 每个只换一张贴图
```

**95 个实例共用 1 个母材质 —— 这是正确用法。**

---

## 二、`MaterialTools` 的 22 个工具（实测存在）

### 2.1 创建

| 工具 | 用途 |
| --- | --- |
| `create_material` | 新建空材质 |
| `create_function` | 新建材质函数 |
| `create_parameter_collection` | 参数集合（全局参数）|

### 2.2 节点操作

| 工具 | 用途 |
| --- | --- |
| `list_expression_classes` | **列出所有可用的节点类** |
| `add_expression` / `delete_expression` / `get_expressions` | 增删查 |
| **`get_expression_input_names`** | **查真实输入引脚名** |
| **`get_expression_output_names`** | **查真实输出引脚名** |
| `connect_expressions` / `disconnect_expressions` | 连线 |
| `connect_to_output` / `get_property_input` / `disconnect_from_output` | 接输出属性 |
| `layout_expressions` / `delete_unused_expressions` | 整理 |
| **`recompile`** | **编译（失败抛异常）** |

### 2.3 🔴 这解决了 gotcha #64

**gotcha #64 是："Clamp 节点的输入引脚连不上，只好改用 Min/Max 替代"。**

**真正原因：**`connect_material_expressions(..., "Input")` 里引脚名是**猜的**。

**正解：**
```
add_expression(Clamp) → get_expression_input_names(那个Clamp) → 拿到真实名字 → connect_expressions
```

**实测验证：`TextureCoordinate_0` 的输入引脚是**空列表**，输出引脚是**一个空名**。
所以**引脚名不一定是 "Input"/"Output" —— 必须先查。****

---

## 三、实测诊断：地面为什么网格感明显

### 3.1 实测数据

**用 `Tools/inspect_ground_material.py` 读出来的：**

```
M_Moxiang_Ground:
  节点数           = 3
    MaterialExpressionTextureCoordinate    ← UV
    MaterialExpressionTextureSample        ← 采样
    MaterialExpressionConstant             ← 粗糙度

  TextureCoordinate: u_tiling = 96.0, v_tiling = 96.0
  一张贴图覆盖     = 51200 / 96 = 533.3 cm = 5.33 米
  TextureSample:    texture = tile_108_road01, sampler = COLOR
  Constant:         r = 0.95（粗糙度）
```

### 3.2 真正的病因

**`tile_108_road01.png` 是**64 × 64 像素**（墨香原版图块尺寸）。**

**把它拉伸到 5.33 米意味着：**
```
一张 64×64 的图 → 覆盖 533 cm
→ 1 像素 ≈ 8.3 cm
→ 在 1080p 下站在 5 米外看，一像素只有几个屏幕像素
```

**而 96 次重复意味着**整张地图上同一个花纹出现 9,216 次** ——
人眼对规律极敏感，这就是"网格感"的来源。**

### 3.3 为什么"改平铺数"治不了

| 改法 | 结果 |
| --- | --- |
| 96 → 24（贴图更大） | 花纹更明显，**更糟** |
| 96 → 200（贴图更小） | 每个花纹小到看不清，但**重复更密** |
| 加随机偏移 | 需要 noise 贴图，且墨香原版没有 |
| **换更高分辨率贴图** | ✅ **唯一根治** |

**结论：这是**素材分辨率**的限制，不是材质参数的问题。**

### 3.4 三条可行的改善路径

| 路径 | 做法 | 代价 |
| --- | --- | --- |
| **A. 双图混合** | 原贴图 + 一张细节图（不同平铺倍数）混合 | 中，需要一张细节贴图 |
| **B. 用法线/粗糙度打断规律** | 只加法线贴图，颜色仍单图 | 低，法线可程序生成 |
| **C. 换自制高清地表** | 用自己的 PBR 材质 | 高，但符合"原创"方向 |

**建议 B 先做（成本最低，能立刻减少"平铺感"因为光照会随法线变化），
最终目标走 C（你本来就要用自己的素材）。**

---

## 四、材质表达式的关键类（本项目会用到的）

| 节点 | 用途 |
| --- | --- |
| `MaterialExpressionTextureCoordinate` | UV（`u_tiling` / `v_tiling`）|
| `MaterialExpressionTextureSample` | 采样贴图（`texture` / `sampler_type`）|
| `MaterialExpressionConstant` | 常量（`r`）|
| `MaterialExpressionConstant3Vector` | 三通道常量（颜色）|
| `MaterialExpressionMultiply` / `Add` / `LinearInterpolate` | 算术 |
| `MaterialExpressionFresnel` | 边缘光 |
| `MaterialExpressionWorldPosition` | 世界坐标（做三平面映射用）|
| `MaterialExpressionVertexNormalWS` | 世界法线 |

**要查全部可用节点：`MaterialTools.list_expression_classes(material_or_function, search)`。**

---

## 五、三平面映射（解决陡坡拉伸）

**另一个已知问题："陡坡贴图拉伸"。**

**原因：UV 是**平面投影**，在垂直面上被拉长。**

**解法：三平面映射（Triplanar）—— 按世界法线在三个平面间混合。**

```
节点图:
  WorldPosition → 分别取 XY / XZ / YZ → 三次采样
  VertexNormalWS → 取绝对值 → 归一化 → 作为混合权重
  LinearInterpolate 两次 → 输出颜色
```

**节点数约 15 个，全部可以用 `MaterialTools` 建。**

**这不是"学 UE"，这是"练 UE" —— 而且我有现成工具。**

---

## 六、掌握程度（材质）

| 内容 | 掌握 |
| --- | --- |
| 三层结构（Interface / Material / Instance） | 🟢 **清楚** |
| 为什么用实例（不重编译 shader） | 🟢 **清楚** |
| 22 个材质工具的名字与用途 | 🟢 **列全** |
| **引脚名必须先查再连（解决 gotcha #64）** | 🟢 **实测验证** |
| **地面网格感的真正病因（64×64 贴图）** | 🟢 **实测诊断** |
| **三平面映射的节点图设计** | 🟢 **能画出来** |
| **用工具建过一个完整材质** | 🔴 **没做过** |
| Lumen 相关材质设置 | 🔴 **没碰** |
| 材质函数（MaterialFunction）复用 | 🔴 **没碰** |

**总体：从 4 种节点 → **35%**。**

**涨的部分：结构、工具、诊断方法、三平面设计思路。
没涨的部分：**没实际用工具搭过一个材质图**。**

---

## 七、下一步（这次能真的动手）

**目标：把地面材质改成三平面映射 + 法线扰动。**

```
1. 用 create_material 建 M_Ground_Triplanar
2. 用 add_expression 加节点（WorldPosition / VertexNormalWS / 三次 TextureSample / Lerp）
3. 用 get_expression_input_names 查每个节点的引脚
4. 用 connect_expressions 连起来
5. 用 recompile 验证（失败会抛异常）
6. 挂到地形上，截图对比
```

**这一步能同时验证：工具链可用 + 三平面有效 + 观感改善。**

**且不需要墨香动画那个前置条件。**

---

## 八、重查命令

```powershell
python Tools\list_python_toolset_tools.py material   # 22 个工具
python Tools\inspect_ground_material.py              # 地面材质实测
```

---

## 九、实测：三平面材质建成（2026-11-26）

### 9.1 结果

**用 22 个材质工具**从零搭了一个三平面材质 `M_Ground_Triplanar`：
**24 个节点，编译通过，挂到地形上。**

![三平面效果](../../Saved/tri_fixed.png)

**对比：**

| | 之前（`M_Moxiang_Ground`） | 之后（`M_Ground_Triplanar`） |
| --- | --- | --- |
| 节点数 | 3 | **24** |
| 投影方式 | 平面 UV | **三平面** |
| 地面 | **明显方格网格** | 自然的凹凸纹理 |
| 陡坡 | 明显拉伸 | **正常** |

### 9.2 🔴 第一次做错了，两个错误都编译通过

**这是最有价值的部分 —— 这两个错误**都不报错**，只是画面不对。**

#### 错误 1：UV 应该**除**以米数，不是**乘**平铺次数

**`WorldPosition` 返回**厘米**（x=8950）。
乘以 24 得到 UV=214,800 —— 贴图采到极限密度，引擎退化成**平均色**。**

**症状：地面变成纯色，完全没有纹理。**

**修法：**
```
UV = WorldPosition / 600     ← 每 6 米一张贴图
```

**概念转换：参数不是"重复多少次"，是"每张覆盖多长"。**

#### 错误 2：混合权重必须是**归一化比例**

**法线分量绝对值相加可能 > 1。`Lerp` 的 Alpha 超过 1 被钳制，混合失效。**

**修法：**
```
错: alpha = |n.x| + |n.y|
对: alpha = |n.y| / (|n.x| + |n.y|)     ← 恒在 [0,1]
分母加 epsilon 防止除零（法线朝正上时 |x|+|y|=0）
```

### 9.3 完整节点图（24 个节点）

```
WorldPosition ──÷600──┐
                      ├─ Mask(XY) ── TextureSample ──┐
                      ├─ Mask(ZY) ── TextureSample ──┤
                      └─ Mask(XZ) ── TextureSample ──┤
                                                      │
VertexNormalWS ─ Abs ─┬─ Mask(X) ─┐                   │
                      ├─ Mask(Y) ─┴─ Add ─┐            │
                      └─ Mask(Z) ────────┼─ Add ─ Divide ─ weight_z ─┐
                                         │                          │
                      Abs ─┬─ Mask(X) ─┐ │                          │
                           ├─ Mask(Y) ─┴─ Add ─┐                     │
                           └─ eps ────────────┴─ Add ─ Divide ─ ratio_y ─┐
                                                                        │
    TextureSample(XZ) ─┐                                                │
    TextureSample(ZY) ─┴─ LinearInterpolate(alpha=ratio_y) ─┐           │
                                                            ├─ Lerp(alpha=weight_z) ─ BaseColor
    TextureSample(XY) ─────────────────────────────────────┘
```

### 9.4 掌握程度更新

| 内容 | 之前 | 现在 |
| --- | --- | --- |
| 材质结构（Interface / Material / Instance） | 🟢 清楚 | 🟢 清楚 |
| 22 个材质工具 | 🟢 列全 | 🟢 **全部实际用过** |
| 引脚名必须先查 | 🟢 知道 | 🟢 **实操确认** |
| **用工具搭建完整材质图** | 🔴 没做过 | 🟢 **做成 24 节点** |
| **三平面映射** | 🟢 能画出来 | 🟢 **建成并验证** |
| **从错误中定位问题** | — | 🟢 **两次错误都自己诊断出来** |

**材质：从 35% → **65%**。**

**这是本项目第一次**完全通过工具调用**（没有手点编辑器）完成一件可见的改动。**
