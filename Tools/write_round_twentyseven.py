"""Append the twenty-seventh round.

    python Tools/write_round_twentyseven.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 44. 第二十七轮：**找到真身 —— `boss001` 里有 17 个身体部件**（2026-11-26 29:30）

### 一、🔴 `boss_cowf_01.mod` 是 Boss 的**火焰特效**

**逐块打印名字：**
```
fire_U_b_08, fire03, fire04, fire05, BU_fire_boom_01..04,
fire09, fire11, fire10, fire06, fire08, fire07, fire_U_b_01...
```

**24 个块**全是火焰面片**。那 12 个「14 公里」的块 `raw extent = 431,602,078` —— 顶点是垃圾，
`mat4` 缩放 `(0.00, 0.00, 0.01)` 退化的。**

### 二、教训（gotcha #95）：**文件名告诉你它属于谁，不告诉你它是什么**

**判断方法：看网格块的名字**
- 含 `fire`/`eff`/`smoke`/`boom`/`fog` → **特效**
- 含 `head`/`arm`/`shoulder`/`eye` → **身体**

### 三、`boss001.mod` 才是本体

```
boss01_shoulderR, boss_biseok, boss01_shoulderL, boss01_eyeR, boss01_eyeL,
boss01_teok, boss01_hand, boss01_armL, boss01_chain, boss01_armR, boss01_head
```

**17 个身体部件，0 个特效块。**

**17 个 primitive 的尺寸（米）：**
```
0  (0.23, 0.21, 0.21)   眼
1  (0.80, 1.02, 0.65)   躯干
8  (0.26, 0.43, 1.11)   手臂/腿
```

**全部 0.05–1.11 米 —— 真人形尺度。**

### 四、🔴 稀疏骨骼索引 bug（gotcha #94）

**第一次导出报 `struct.error: 'H' format requires 0 <= number <= 65535`。**

**`boss001` 有 **67 骨骼，索引是 11..83**（稀疏）。
我把**骨骼索引**直接当**关节索引**写进 `JOINTS_0` → 出现 83 > 67。**

**为什么之前没暴露：**
- `108_bird` 9 骨骼，索引 0..8 连续
- `198_bobu` 31 骨骼，0..30 连续
- **`boss001` 67 骨骼稀疏 —— 第三个样本才暴露**

**修法：**
```python
ordered = sorted(bones, key=lambda b: b["index"])
joint_of = {b["index"]: i for i, b in enumerate(ordered)}
mapped = joint_of.get(bone_index)
```

### 五、Boss 本体现在可见

**画面里能看到：圆形身体/头部、向上伸的手臂、右侧链条状结构。**
**包围盒 `(96.2, 217.1, 76.1) cm` —— 双足人物。**

**但部件是**散开**的 —— 因为**逆绑定矩阵仍是单位矩阵**。**

### 六、下一步：算真正的逆绑定矩阵

**现在：**
```python
identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
```

**应该是：**
```
IBM[bone] = inverse(bind_pose_world[bone])
```
**`bind_pose_world` 从骨骼的 NODE_TM 层级累乘得到。**

**这是让姿态正确、部件不散的关键。**

### 七、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/find_real_body.py`** | **按网格名打分找出有身体的模型** |
| `Tools/check_dropped_blocks.py` | 查被丢弃的块是否被变换放大 |
| `Tools/switch_to_boss001.py` | 切换导入目标 |

### 八、这一轮最大的收获

> **「有骨骼 + 有动画」不等于「是角色」。**
> **`boss_cowf_01` 有 38 骨骼、36/38 匹配、49 通道 —— 一切都是对的，但它是火。**
>
> **判断一个文件是什么，只能看**它里面有什么几何**，不能看名字、不能看骨骼数。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 44." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 44; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
