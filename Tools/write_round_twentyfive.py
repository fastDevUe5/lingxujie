"""Append the twenty-fifth round.

    python Tools/write_round_twentyfive.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 42. 第二十五轮：「284 个失败」里 153 个是**正确行为**（2026-11-26 28:00）

### 一、分类结果

```
files with no bone tracks: 284

  顶点动画（无骨骼键，有 mesh 键）:  153    <- 正确行为
    这些文件共 66,068 个 mesh 键
  块起点定位不到:                   105    <- 待查
  其他形态:                          26
```

### 二、153 个顶点动画文件

**块头特征：`rot=0 pos=0 scale=0` 但 `mesh>0`。**

```
102_flame.anm      1 块,   15 mesh 键   Plane02
102_light.anm      4 块,  202 mesh 键
105_staywater.anm  2 块,   31 mesh 键
108_sea00.anm      1 块,  400 mesh 键
108_waterfall.anm 69 块, 3780 mesh 键
110_magma_01.anm  26 块, 2600 mesh 键
```

**动画数据全在 `dwAnimatedMeshKeyNum` 的顶点键里，没有骨骼轨道。
`parse_anm` 返回空是**正确的** —— 它们是水、火、瀑布、岩浆。**

### 三、修正后的真实分布

| 类别 | 数量 | 性质 |
| --- | --- | --- |
| 有骨骼动画 | **3,772（93%）** | 正常 |
| 只有顶点动画 | **153（3.8%）** | **预期行为** |
| 块起点定位不到 | **105（2.6%）** | 真正的待查项 |
| 形态未知 | **26（0.6%）** | ? |

### 四、`parse_anm` 现在更严格了

**新增 `anm_first_block()`：**
- 验证块名是**可打印字符串**（排除头部里巧合出现的 `00 F0 00 00`）
- 选**能走出最多块**的那个候选起点

**修前 95 个「first block implausible」+ 11 个「counts overflow」都是定位到了假 marker。**

### 五、`.anm` 的三种动画载体

| 载体 | 字段 | 用途 | 状态 |
| --- | --- | --- | --- |
| **骨骼** | `dwRotKeyNum` / `dwPosKeyNum` / `dwScaleKeyNum` | 角色 | ✅ 已实现 |
| **顶点** | `dwAnimatedMeshKeyNum` | 水/火/瀑布/旗帜 | ❌ 未实现 |
| **UV** | 顶点键内部 | 贴图滚动 | ❌ 未实现 |

**顶点动画每条键后跟可变长度数组：**
```c
FSRead(&ANIMATED_MESH_KEY, sizeof);
if (dwVertexNum)    FSRead(pv3Pos, 12*vertexNum);
if (dwTexVertexNum) FSRead(ptUV,  8*texVertexNum);
```

**这正是第 23 轮把自校验从「必须相等」放宽为「装得下」的原因。**

### 六、教训（gotcha #92）

> **「失败」这个词用错了。**
>
> **一个文件没有骨骼轨道，可能因为它**本来就没有骨骼轨道**。
> 把「没有我要的东西」和「解析失败了」混成一个数字，
> 就会得出「7% 解析失败」这种不准确的结论。**

### 七、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **顶点动画实现**（水/火/瀑布）—— 需要引擎端 morph target 或 WPO |
| 2 | 查 105 个定位不到块起点的 |
| 3 | 批量重导（步长修了，旧输出要重生成）|
| 4 | 批量导入 UE |
| 5 | 材质接入 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 42." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 42; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
