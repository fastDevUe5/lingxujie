"""Record that the 284 "failures" were mostly correct behaviour under a misleading label.

A file that animates mesh vertices has no bone tracks, and reporting none for it is right. Counting
those as failures overstated how much was broken by a factor of the whole category.

    python Tools/document_vertex_anims.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 十一、284 个「失败」的真相：153 个是**正确行为**（第 25 轮）

### 11.1 分类结果

```
files with no bone tracks: 284

  顶点动画（无骨骼键，有 mesh 键）:  153    <- 正确行为
    这些文件共 66,068 个 mesh 键
  块起点定位不到:                   105    <- 待查
  其他形态:                          26
```

### 11.2 153 个顶点动画文件

**它们的块头特征是 `rot=0 pos=0 scale=0` 但 `mesh>0`：**

```
102_flame.anm      1 块,   15 mesh 键   Plane02
102_light.anm      4 块,  202 mesh 键
105_staywater.anm  2 块,   31 mesh 键   102_LAKE_0811
108_sea00.anm      1 块,  400 mesh 键
108_waterfall.anm 69 块, 3780 mesh 键
110_magma_01.anm  26 块, 2600 mesh 键
```

**也就是说：动画数据全在 `dwAnimatedMeshKeyNum` 的顶点键里，没有骨骼轨道。**

**`parse_anm` 对它们返回 `{}` 是**正确的** —— 它们不是角色，是水、火、瀑布、岩浆。**

### 11.3 关键教训

> **「失败」这个词用错了。**
>
> **一个文件没有骨骼轨道，可能因为它**本来就没有骨骼轨道**。
> 把「没有我要的东西」和「解析失败了」混成一个数字，
> 就会得出「7% 解析失败」这种不准确的结论。**

**正确的说法：**
- **3,772 个文件有骨骼动画（93%）**
- **153 个文件只有顶点动画（3.8%）—— 预期行为**
- **105 个文件块起点定位不到（2.6%）—— 真正的待查项**
- **26 个文件形态未知（0.6%）**

### 11.4 `.anm` 的三种动画载体

| 载体 | 字段 | 用途 | 状态 |
| --- | --- | --- | --- |
| **骨骼** | `dwRotKeyNum` / `dwPosKeyNum` / `dwScaleKeyNum` | 角色 | ✅ 已实现 |
| **顶点** | `dwAnimatedMeshKeyNum` | 水/火/瀑布/旗帜 | ❌ 未实现 |
| **UV** | （在顶点键内部）| 贴图滚动 | ❌ 未实现 |

**顶点动画的每条键后面跟可变长度的顶点数组：**
```c
FSRead(&ANIMATED_MESH_KEY, sizeof);
if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);
if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);
```

**所以块大小会大于「头 + 骨骼键」需要的量 —— 这正是我第 23 轮把自校验从
「必须相等」放宽为「装得下」的原因。**

### 11.5 105 个定位不到块起点的

**例如 `102_lake.anm`（40,160 字节）：**
```
marker @205  size=39992
205 + 8 + 39992 = 40205 > 40160    <- 超出 45 字节
```

**只有一个 marker，且它声明的 size 比实际剩余多 45 字节。**

**可能是**文件本身被截断**，或**尾部在 size 之内**。**

**这 105 个（2.6%）暂不处理 —— 影响有限，且需要更多样本才能判明。**
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 十一、284 个「失败」的真相" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
