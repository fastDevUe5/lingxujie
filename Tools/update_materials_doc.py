"""Append the triplanar result to the materials document.

    python Tools/update_materials_doc.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-MATERIALS.md"

SECTION = """
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
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 九、实测：三平面材质建成" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
