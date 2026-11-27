"""Append the thirtieth round.

    python Tools/write_round_thirty.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 47. 第三十轮：**回归验证通过 —— 网格 mat4 改动是安全的**（2026-11-26 31:00）

### 一、八个关键模型全部合理

```
108_bird         1 块   8 通道  1.50 x 1.36 x 1.11 m
198_bobu         3 块  15 通道  1.99 x 1.99 x 1.56 m
boss001         17 块  25 通道  2.97 x 2.08 x 2.72 m
boss_cowf_01    12 块  49 通道  4.05 x 1.11 x 2.45 m
216              1 块   0 通道  0.59 x 0.71 x 1.34 m
w25260           1 块   0 通道  0.21 x 0.24 x 0.10 m
107_crow         1 块   6 通道  0.87 x 2.56 x 0.47 m
20_eagle_01      1 块   0 通道  0.84 x 1.39 x 1.77 m

problems: 0
```

**关键：`boss_cowf_01` 从**14 公里** → **4.05 × 1.11 × 2.45 米**。
而 `108_bird` / `198_bobu`（改动前就能正确导出的两个）**没有退化**。**

### 二、200 个模型批量

```
summary: 200 exported, 2 with animation, 0 skipped, 0 failed
total output 3.2 MB
```

**包围盒分布：**

| 类别 | 数量 | 占比 |
| --- | --- | --- |
| 正常（0.001–100 m）| **231** | 91% |
| 过大（>100 m）| 19 | 7.5% |
| 退化（<1 mm）| 3 | 1.2% |

### 三、22 个异常已分类（不是随机错误）

**3 个「退化」= 粒子/雾效面片（毫米级）：**
```
boss_cowf_06      BU_fsandfogs_19    4 顶点  0.34 cm
boss_cowking_04   V_small_stone_38   7 顶点  0.05 cm
```

**19 个「过大」= 扁平大面（地形/远景）：**
```
101_1ava00   146.0 x 95.9 x 1.8 m     ← 1.8m 厚，146×96m 宽
```

### 四、顺带修的边界情况

**如果 >100m 过滤器丢掉所有块，会得到空网格。
修：保留最小的那一块。**

```python
elif dropped:
    meshes = [min(meshes, key=block_extent)]
    dropped -= 1
```

### 五、可信度评估

| 证据 | 结论 |
| --- | --- |
| 8 个关键模型 problems=0 | 没破坏已知正确的模型 |
| 200 个批量 0 失败 | 规模上稳定 |
| 91% 包围盒正常 | 大部分直接可用 |
| 22 个异常已分类 | 不是随机错误 |

**结论：网格块不应用 `mat4` 这个改动是对的。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/regression_check.py`** | 8 个关键模型的回归检查（自带判定规则）|

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **材质接入** —— 导入警告「未指定材质的图元」，所有角色都是灰的 |
| 2 | 动画播放验证（把 AnimSequence 挂到组件上）|
| 3 | 批量导入 UE（导出只是第一步）|
| 4 | 骨骼名不匹配的 46 根（boss001 21/67）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 47." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 47; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
