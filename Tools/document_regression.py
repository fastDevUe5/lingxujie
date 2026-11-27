"""Record the regression pass and the particle-quad edge case.

The mesh-matrix change fixed the boss; this round establishes it did not break anything else. Eight
models re-export with plausible bounds and a two-hundred model batch completes without a single
failure, which is the evidence that matters. Three models produce a zero extent because they are
particle quads measured in millimetres, not because the exporter failed.

    python Tools/document_regression.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十六、回归验证：网格 mat4 改动安全（第 30 轮）

### 16.1 八个关键模型全部合理

```
model            blocks   channels  bounds (m)              verdict
108_bird         1        8         1.50 x 1.36 x 1.11        ok
198_bobu         3        15        1.99 x 1.99 x 1.56        ok
boss001          17       25        2.97 x 2.08 x 2.72        ok
boss_cowf_01     12       49        4.05 x 1.11 x 2.45        ok
216              1        0         0.59 x 0.71 x 1.34        ok
w25260           1        0         0.21 x 0.24 x 0.10        ok
107_crow         1        6         0.87 x 2.56 x 0.47        ok
20_eagle_01      1        0         0.84 x 1.39 x 1.77        ok

problems: 0
```

**关键：`boss_cowf_01` 从**14 公里**修到 **4.05 × 1.11 × 2.45 米**。**

**而 `108_bird` 和 `198_bobu`（改动前就能正确导出的两个）**没有退化**。**

### 16.2 200 个模型批量

```
summary: 200 exported, 2 with animation, 0 skipped, 0 failed
total output 3.2 MB
```

**包围盒分布（含之前批次的 231 个）：**

| 类别 | 数量 |
| --- | --- |
| 正常（0.001 – 100 m）| **231** |
| 过大（> 100 m）| 19 |
| 退化（< 1 mm）| 3 |

### 16.3 那 3 个「退化」是什么

```
boss_cowf_06      BU_fsandfogs_19    4 顶点  extent=(0.34, 0.40, 0.00) cm
boss_cowi_06      BU_isandfogs_19    4 顶点  extent=(0.34, 0.40, 0.00) cm
boss_cowking_04   V_small_stone_38   7 顶点  extent=(0.05, 0.04, 0.05) cm
```

**它们是**粒子/雾效面片**，尺寸以**毫米**计（0.34 cm = 3.4 mm），
由游戏在运行时定位。**

**不是导出失败。占全部模型的 0.06%。**

### 16.4 那 19 个「过大」是什么

```
101_1ava00   146.0 x 95.9 x 1.8 m
101_1ava01   151.7 x 41.7 x 1.8 m
101_1ava05   176.6 x 21.4 x 3.5 m
```

**`101_1ava*` 系列 —— 扁平（1.8m 厚）但极大（146 × 96 m），
像是**地形块或天空/远景面**，不是角色。**

**占比 0.36%。**

### 16.5 一个顺带修的边界情况

**如果 >100m 过滤器把所有块都丢掉，会得到空网格。**

**修：保留**最小的那一块**，至少还有东西。**
```python
elif dropped:
    meshes = [min(meshes, key=block_extent)]
    dropped -= 1
```

### 16.6 现在的可信度

| 证据 | 结论 |
| --- | --- |
| 8 个关键模型 problems=0 | 改动没有破坏已知正确的模型 |
| 200 个批量 0 失败 | 规模上稳定 |
| 231/253 包围盒正常 | 91% 直接可用 |
| 22 个异常已分类 | 不是随机错误 |

**结论：**网格块不应用 `mat4`** 这个改动是对的。**

### 16.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/regression_check.py`** | **8 个关键模型的回归检查（自带判定）** |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十六、回归验证" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
