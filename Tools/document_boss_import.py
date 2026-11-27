"""Record the two centring/filtering errors that made a two-metre boss fourteen kilometres wide.

The bounds were the symptom and they were loud: fourteen kilometres. Both causes are about scope -
a centre computed per mesh instead of per model, and background geometry kept because it happens to
carry bone weights.

    python Tools/document_boss_import.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十二、真角色进引擎：36/38 骨骼 + 49 通道（第 26 轮）

### 12.1 导出结果

```
mod: 38 bones, 24 meshes
anm: 56 tracks
matched bones: 36 of 38            <- 全身动画
nodes=39 joints=38 animation channels=49
```

**第 23 轮我以为「这个 Boss 只动画尾巴」。**
**`SCALE_KEY=36` 修好后，**36/38 骨骼匹配** —— 全身都在动。**

### 12.2 导入结果

```
BOSS: import produced 4 assets
  Skeleton         SK_BossCowf_Skeleton
  SkeletalMesh     SK_BossCowf
  PhysicsAsset     SK_BossCowf_PhysicsAsset
  AnimSequence     SK_BossCowf_Anim
  animation length 1.7000 s
```

### 12.3 🔴 修掉两个「作用域」错误

**修前包围盒：`(1419593.2, 1323042.6, 1973750.8) cm` = **14 公里**。**
**修后：`(279.8, 161.6, 87.5) cm` = **2.8 米**。**

#### 错误 1：每个网格块独立居中

**24 个网格各自减去自己的重心 → 全部叠到原点，相对位置全毁。**

**修法：整个模型算**一个**重心，所有块共用。**
```python
centre = 所有块所有顶点变换后的平均值
for each in meshes:
    positions = [transform(p) - centre for p in each.positions]
```

#### 错误 2：背景/特效网格也被保留

**24 个块里有 12 个的顶点跨度 **14–22 公里**（背景板、天空面）。**

**它们**也有骨骼权重**（`bone_records` 非空），所以按绑定筛选无效。**

**修法：按尺寸过滤**
```python
if block_extent(each) > 10000.0:   # 100 米
    dropped += 1
    continue
```

**实测：`dropped 12 block(s) larger than 100 m` → 剩 12 块，最大 2.51 米。**

### 12.4 位置与尺寸的对照表

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 包围盒 | **14 公里** | **2.8 米** |
| 网格块 | 24 | **12** |
| 骨骼匹配 | — | **36 / 38** |
| 动画通道 | — | **49** |
| AnimSequence 长度 | — | **1.70 秒** |
| glTF 大小 | 81,812 B | 63,247 B |

### 12.5 两种「作用域」错误的共同点

| 错误 | 作用域错了在哪 |
| --- | --- |
| 每块独立居中 | 居中应该是**整个模型**的操作，不是每块的 |
| 保留背景网格 | 「哪些块属于这个角色」是**模型级**判断，不是**块级** |

> **两次都是把「整体」的运算写在了「局部」上。**
>
> 而症状（14 公里包围盒）指向的是**数据**，不是**代码结构** ——
> 所以一开始会去怀疑顶点坐标、怀疑缩放、怀疑坐标系。

### 12.6 仍待解决

**画面里角色仍不清晰（看到的是它的一块 2.5m 平面）。**

**这属于**摆放与朝向**，不是数据：包围盒已经证明几何是对的（2.8 米、36/38 骨骼、49 通道）。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十二、真角色进引擎" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
