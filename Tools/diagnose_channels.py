"""Record what the channel-count investigation actually found.

The question was why a thirty-eight bone character yielded eight animation channels. The answer is
in the data: the character's own animation file moves only the tail, and the other files in its chx
listing are effect animations for fireballs and smoke whose track names are not bone names at all.

    python Tools/diagnose_channels.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 九、「38 骨骼只出 8 通道」已查明（第 23 轮）

### 9.1 先修了一个解析 bug

**`Boss_cowf_01.anm` 有 **70 处** `0xF000`，我的解析器只找到 **5 个块**。**

**根因：块大小自校验条件写成了「必须完全相等」，但源码里还有一段可变长度数据：**

```c
if (dwAnimatedMeshKeyNum) {
    for (j...) {
        FSRead(&ANIMATED_MESH_KEY, sizeof);
        if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);      // 可变！
        if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);     // 可变！
    }
}
```

**所以正确条件不是相等，而是「声明的关键帧必须**装得下**」：**
```python
required = 152 + pos*20 + rot*24 + scale*40
if required > size:
    break        # 真正的越界才停
```

**放宽后六个文件全部能解析。**

### 9.2 放宽后看到的内容

| 文件 | 轨道数 | 轨道名 | 语义 |
| --- | --- | --- | --- |
| `Boss_cowf_01.anm` | **6** | `Bip01 TailNub/Tail3/Tail2/Tail1/Tail` | **骨骼动画（只有尾巴）** |
| `Boss_cowf_02.anm` | 5 | `BU_fireball_03/02/01`, `U_Cylinder06` | **特效网格**（只缩放）|
| `Boss_cowf_03.anm` | 15 | `BU_green_fire_*` | 特效 |
| `Boss_cowf_04.anm` | 16 | `BU_black_smoke_*` | 特效 |
| `Boss_cowf_05.anm` | 11 | `BU_fireball_*` | 特效 |
| `Boss_cowf_06.anm` | 12 | `BU_fsandfogs_*` | 特效 |

### 9.3 结论：8 通道是**正确**的

**`Boss_cowf_01.mod` 有 38 骨骼，但它的动画文件 `Boss_cowf_01.anm` **只动画 6 根尾巴骨**。**

**6 条轨道 × (旋转 + 位移) ≈ 8–12 条 glTF 通道 —— 8 就是对的。**

**其余 32 根骨骼在这个动作里**不动**。**

**这不是管道 bug，是源数据就是这样。**

### 9.4 `.chx` 里混了两类动画

**一个 `.chx` 列出的动画包含两类：**

| 类别 | 特征 | 轨道名 |
| --- | --- | --- |
| **骨骼动画** | 有 rot 键（四元数）| `Bip01 …` |
| **特效动画** | **只有 scale 键** | `BU_fireball_*` / `U_Cylinder*` |

**特效动画的"骨骼"其实是**网格对象名**，动画内容是缩放（火焰变大变小）。**

**所以配对不能取第一个，要**按骨骼名重合度打分**：**

```python
score = sum(1 for name in tracks if name.lower() in model_bone_names)
best = max(candidates, key=score)
```

**实测：`Boss_cowf_01.anm` 得 4–6 分，其余得 0 分 —— 打分正确选出了骨骼动画。**

### 9.5 一个更大的发现：`_01`…`_06` 是不同模型

**`Boss_cowf_01.mod` … `Boss_cowf_06.mod` 是**六个不同的模型文件**（骨骼数 38/38/0/38/0/0，
网格数 24/52/43/75/56/13）—— 可能是不同 LOD 或不同部位。**

**而 `.chx` 是按**模型组**（`boss_cowf`）列出全部动画的。**

**所以正确的配对粒度是「模型组 ↔ 动画列表」，不是一个模型对一个动画。**

**→ 下一步：按组配对，把组内**所有**动画都导出为该组模型的 AnimSequence。**

### 9.6 修正后的理解

| 之前以为 | 实际 |
| --- | --- |
| 38 骨骼应该出几十通道 | **源动画只动 6 根，8 通道正确** |
| 一个模型对一个动画 | **一个模型组对一组动画** |
| `.chx` 列表都是骨骼动画 | **混了特效动画，要按骨骼名打分** |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 九、「38 骨骼只出 8 通道」已查明" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
