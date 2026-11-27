"""Record finding the real boss body and the sparse bone index fix.

Two things came out of this round and both were about looking at the right thing. The file named
after the boss contains fire, not a body; and the body that does exist numbers its bones in a way
that broke the joint attribute.

    python Tools/document_boss001.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十三、找到真正的 Boss 本体 + 稀疏骨骼索引 bug（第 27 轮）

### 13.1 🔴 `boss_cowf_01.mod` 不是 Boss，是它的**火焰特效**

**逐块打印名字：**
```
fire_U_b_08, fire_U_b_09, fire03, fire04, fire05, fire, fire02, fire01,
BU_fire_boom_01..04, fire_U_b_07, fire_U_b_06, fire09, fire11, fire10,
fire06, fire08, fire07, fire_U_b_01, fire_U_b_10, BU_fire_boom_02, _03
```

**24 个块**全是火焰面片**。**

**那 12 个「14–22 公里」的块，`raw extent = 431,602,078` —— 顶点是**垃圾数据**，
`mat4` 缩放 `(0.00, 0.00, 0.01)` 退化的。**

### 13.2 教训：**文件名告诉你它属于谁，不告诉你它是什么**

**`boss_cowf_01.mod` 属于 Boss cowf，但内容是它的火。**
**`boss_cowf_02..06` 同样是火/烟/雾的不同部分。**

**判断方法：看**网格块的名字**。**
- 含 `fire`/`eff`/`smoke`/`boom` → 特效
- 含 `head`/`arm`/`shoulder`/`eye` → 身体

### 13.3 `boss001.mod` 才是本体

```
boss01_shoulderR, boss_biseok, boss01_shoulderL, boss01_eyeR, boss01_eyeL,
boss01_teok, boss01_hand, boss01_armL, boss01_chain, boss01_armR, boss01_head
```

**17 个身体部件，0 个特效块。**

**导出后的 17 个 primitive 尺寸（米）：**
```
0  (0.23, 0.21, 0.21)   眼
1  (0.80, 1.02, 0.65)   躯干
8  (0.26, 0.43, 1.11)   手臂/腿
15 (0.32, 0.43, 0.67)
```

**全部 0.05–1.11 米 —— 真人形尺度。**

### 13.4 🔴 稀疏骨骼索引 bug（gotcha #94）

**第一次导出 `boss001` 报：**
```
struct.error: 'H' format requires 0 <= number <= 65535
```

**原因：`boss001` 有 **67 根骨骼，但索引是 11..83**（稀疏的）。**

**我把**骨骼索引**直接当成**关节索引**写进 `JOINTS_0`，
于是出现 83 这种超过骨骼数（67）的值。**

**在 `bird`（0..8）和 `bobu`（0..30）上碰巧正确，因为它们的索引正好连续。**

**修法：**
```python
ordered_bones = sorted(bones, key=lambda b: b["index"])
joint_of_bone = {b["index"]: i for i, b in enumerate(ordered_bones)}
...
mapped = joint_of.get(bone_index)
if mapped is not None:
    js.append(mapped)
```

**这是第 N 次「在小样本上碰巧正确」。**
**`bird` 9 骨骼、`bobu` 31 骨骼连续，`boss001` 67 骨骼稀疏 —— 第三个样本才暴露。**

### 13.5 现在的画面

**Boss 本体在关卡里可见：**
- 圆形身体/头部
- 向上伸的手臂
- 右侧链条状结构

**包围盒 `(96.2, 217.1, 76.1) cm` —— 双足人物。**

**但部件是**散开**的 —— 因为**逆绑定矩阵仍是单位矩阵**，
蒙皮没有把顶点绑定到骨骼的绑定姿态上。**

### 13.6 下一步：算真正的逆绑定矩阵

**现在：**
```python
identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
for i in range(len(joint_nodes)):
    binary[start:start+64] = struct.pack("<16f", *identity)
```

**应该是：**
```
IBM[bone] = inverse(bind_pose_world[bone])
```
**而 `bind_pose_world` 从骨骼的 NODE_TM 层级累乘得到。**

**这是让姿态正确、部件不散的关键。**

### 13.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/find_real_body.py`** | **按网格名打分找出有身体的模型** |
| `Tools/check_dropped_blocks.py` | 查被丢弃的块是否被变换放大 |
| `Tools/switch_to_boss001.py` | 切换导入目标 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十三、找到真正的 Boss 本体" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
