"""Append the twenty-third round.

    python Tools/write_round_twentythree.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 40. 第二十三轮：8 通道之谜解开 + 又一个解析 bug（2026-11-26 27:00）

### 一、修了解析 bug：自校验条件写错了

**`Boss_cowf_01.anm` 有 **70 处** `0xF000`，解析器只找到 **5 个块**。**

**根因：我把自校验写成「必须完全相等」，但源码里还有一段可变长度数据：**
```c
if (dwAnimatedMeshKeyNum)
    for (j...) {
        FSRead(&ANIMATED_MESH_KEY, sizeof);
        if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);      // 可变
        if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);     // 可变
    }
```

**正确条件不是相等，是「装得下」：**
```python
required = 152 + pos*20 + rot*24 + scale*40
if required > size: break
```

**放宽后六个文件全部能解析。**

### 二、放宽后看到真相

| 文件 | 轨道 | 轨道名 | 类别 |
| --- | --- | --- | --- |
| `Boss_cowf_01.anm` | **6** | `Bip01 Tail*` | **骨骼动画（只有尾巴）** |
| `Boss_cowf_02.anm` | 5 | `BU_fireball_*` | **特效网格**（只缩放）|
| `Boss_cowf_03.anm` | 15 | `BU_green_fire_*` | 特效 |
| `Boss_cowf_04.anm` | 16 | `BU_black_smoke_*` | 特效 |
| `Boss_cowf_05.anm` | 11 | `BU_fireball_*` | 特效 |
| `Boss_cowf_06.anm` | 12 | `BU_fsandfogs_*` | 特效 |

### 三、🔴 8 通道是**正确**的

**`Boss_cowf_01.mod` 有 38 骨骼，但 `Boss_cowf_01.anm` **只动画 6 根尾巴骨**。**

**6 轨 × (rot+pos) ≈ 8 通道 —— 就是对的。**

**其余 32 根骨骼在这个动作里**不动**。不是管道 bug。**

### 四、`.chx` 混了两类动画

| 类别 | 特征 |
| --- | --- |
| **骨骼动画** | 有 rot 键（四元数），名字是 `Bip01 …` |
| **特效动画** | **只有 scale 键**，名字是 `BU_fireball_*` / `U_Cylinder*` |

**所以配对要**按骨骼名重合度打分**，不能取第一个：**
```python
score = sum(1 for name in tracks if name.lower() in model_bone_names)
best = max(candidates, key=score)
```

**实测：Tail 文件得 4–6 分，特效文件得 0 分。**

### 五、一个更大的发现

**`Boss_cowf_01.mod` … `_06.mod` 是**六个不同模型**（骨骼 38/38/0/38/0/0，
网格 24/52/43/75/56/13）—— 可能是不同 LOD 或不同部位。**

**而 `.chx` 是按**模型组**列出全部动画的。**

**→ 正确的配对粒度是「模型组 ↔ 动画列表」，不是一个模型对一个动画。**
**→ 下一步：按组配对，组内所有动画都导出。**

### 六、修正后的理解

| 之前以为 | 实际 |
| --- | --- |
| 38 骨骼该出几十通道 | **源动画只动 6 根** |
| 一个模型对一个动画 | **一个模型组对一组动画** |
| `.chx` 全是骨骼动画 | **混了特效动画，要打分筛选** |

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **按模型组配对，导出组内所有动画** |
| 2 | 特效动画（只有 scale 的）单独处理 |
| 3 | 批量导入 UE |
| 4 | 材质接入 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 40." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 40; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
