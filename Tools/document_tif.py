"""Record the .tif discovery, which turned a sixteen percent gap into one and a half.

The first full pass said eight hundred forty-one models had no texture. They did: the material blocks
name .tif files and nine hundred twenty-nine of those sit on disk. One missing extension in a regular
expression accounted for the whole apparent gap.

    python Tools/document_tif.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 二十一、🔴 漏了 `.tif` —— 16% 的「无材质」变成 1.5%（第 35 轮）

### 21.1 发现

**抽查「无材质」的 841 个模型，打印它们的 MATERIAL 块文本：**

```
13120.mod        MAT=6   MESH=2  BONE=96   贴图: '13120.tif', '13120.tif', '13120'
104_water00.mod  MAT=1   MESH=1  BONE=0    贴图: 'map101_welltree3.tif'
108_bird.mod     MAT=1   MESH=1  BONE=9    贴图: '108_bird.tif', '107_crow.tga111'
```

**扩展名是 `.tif`，我的正则只匹配 `tga|dds|bmp|png|jpg`。**

**磁盘上确实有 929 个 `.tif`：**
```
图片总数: 6,762
  .dds  5,315
  .tif    929     <- 我完全漏了
  .tga    518
```

### 21.2 修后对比

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 有贴图的模型 | 4,464（**84.1%**）| 5,227（**98.5%**）|
| 无材质的模型 | **841** | **78** |
| 不同贴图名 | 1,905 | **2,533** |
| 转换的 PNG | 1,814 | **2,407** |
| PNG 体积 | 263 MB | **340 MB** |

**600 模型抽样更明显：561 → 596 有贴图，39 → 4 无材质。**

### 21.3 抽样的分类（修前）

```
按网格块名字：
  effect-like（水/火/雾）:  22
  body-like:               184
  neither:                 635

按骨架：
  无骨骼（静态道具）:      374
  有骨骼（角色/附属）:     467
```

**「有骨骼」的 467 个里包括 `13120.mod`（96 骨骼）、`13130`、它们的 LOD0-2 ——
这些明显是**角色**，本来就不该「没有贴图」。**

**这条线索（96 骨骼的角色没有贴图，不合理）直接指向「检测有问题」，
而不是「数据缺失」。**

### 21.4 教训

> **「16% 缺失」这个数字本身应该被怀疑。**
>
> 我没有立刻怀疑它，而是先把它写进文档当结论 —— 直到抽查样本才发现是正则漏了一个扩展名。
>
> **一个「坏消息比例很高」的统计，先怀疑统计方法。**

**这和 gotcha #92（把「没有我要的东西」计入「失败」）是同一类：
统计方式决定了结论，而结论的合理性应该反过来检验统计。**

### 21.5 剩余缺口

| 项 | 数量 | 说明 |
| --- | --- | --- |
| 无材质条目的模型 | **78（1.5%）** | 真的没有 MATERIAL 块 |
| 磁盘上缺失的贴图 | **101（4.0%）** | 名字在但文件不在 |
| 转换失败 | **1** | `thunder3`，Pillow 无法识别 |

**78 和 101 都小到可以留待后续，1 个失败是单点问题。**

### 21.6 新增知识

**墨香贴图有三种格式：**
| 格式 | 数量 | 特点 |
| --- | --- | --- |
| `.dds` | 5,315 | 主体，DXGI 格式（UE 不认，gotcha #100）|
| **`.tif`** | **929** | **大图（500-830 KB），Pillow 能读** |
| `.tga` | 518 | 早期格式 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 二十一、🔴 漏了 `.tif`" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
