"""Record the finding that mesh matrices must not be applied, with the measurements.

This is the change that made the boss into a body rather than a scatter of pieces, and it was found
by comparing two readings of the same vertices rather than by reasoning about what the matrix means.

    python Tools/document_mesh_matrix.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十五、🔴 网格块的 `mat4` 不该应用（第 29 轮）—— Boss 终于有实体

### 15.1 决定性对比

**同一批顶点，两种读法：**

| 读法 | 总包围盒 | 块中心散布 |
| --- | --- | --- |
| **应用每块 `mat4`** | 192.4 × **434.2** × 152.2 cm | 158.8 × **383.0** × 75.2 |
| **不应用 `mat4`** | 296.9 × 272.2 × 207.7 cm | 181.0 × 191.2 × 104.5 |

**应用 mat4 把模型沿 Y 拉了**两倍**。**

### 15.2 为什么之前一直以为该应用

**`NODE_TM` 的 `mat4` 确实「看起来像」摆放矩阵 —— 它有平移、有旋转、有缩放，
而且应用后各部件确实会移动。**

**但它移动的方向是**拉开**，不是**归位**。**

### 15.3 关键的不对称

| 对象 | `mat4` 该用吗 | 证据 |
| --- | --- | --- |
| **骨骼** | **该用** | 连续脊柱骨骼 Y = 94→112→127→144 递增，是真世界坐标 |
| **网格** | **不该用** | 应用后包围盒 Y 从 272 拉到 434 |

**所以同一个结构体字段，在两类对象上语义不同。**

### 15.4 修后结果

```
总包围盒: 2.97 x 2.08 x 2.72 m
```

**2.97 × 2.08 × 2.72 米 —— 一个大型 Boss 的合理体型。**

**画面里能看到实体躯干/护甲板，占屏幕三分之一。**

### 15.5 怎么找到的（方法）

**不是靠推理，是靠**同一个数据的两种读法**对比：**

1. 先做了「无蒙皮静态网格」版本，发现包围盒和骨骼版**一模一样**
   → 证明散开不是蒙皮造成的，是顶点数据本身
2. 然后才去对比「应用/不应用 mesh mat4」两种读法
   → 数据直接指向答案

**上一轮的错误是：先改三处（IBM、节点变换、累乘方式）再猜。
这一轮是先测量，再改一处。**

### 15.6 连带修的一处

**共享中心必须用**同一批顶点**算 —— 因为 emit 路径不再应用 mat4，
中心若还用应用后的点，就会错位。**

```python
all_points = []
for each in meshes:
    all_points.extend(each["positions"])   # 原始顶点
```

### 15.7 现在的状态

| 项 | 值 |
| --- | --- |
| 包围盒 | **2.97 × 2.08 × 2.72 m** |
| 网格块 | 17 |
| 骨骼 | 67（21 个有动画轨）|
| 动画通道 | 25 |
| 可见性 | **有实体，占屏幕三分之一** |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十五、🔴 网格块的 `mat4` 不该应用" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
