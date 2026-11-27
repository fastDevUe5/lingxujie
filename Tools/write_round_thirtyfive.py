"""Append the thirty-fifth round.

    python Tools/write_round_thirtyfive.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 52. 第三十五轮：**漏了 `.tif` —— 16% 的「无材质」变成 1.5%**（2026-11-26 36:00）

### 一、发现

**抽查「无材质」的 841 个模型，打印它们的 MATERIAL 块文本：**
```
13120.mod        MAT=6  MESH=2  BONE=96   贴图: '13120.tif'
104_water00.mod  MAT=1  MESH=1  BONE=0    贴图: 'map101_welltree3.tif'
108_bird.mod     MAT=1  MESH=1  BONE=9    贴图: '108_bird.tif'
```

**扩展名是 `.tif` —— 我的正则只匹配 `tga|dds|bmp|png|jpg`。**

**磁盘上确实有 929 个 `.tif`：**
```
图片总数: 6,762
  .dds  5,315
  .tif    929     <- 完全漏了
  .tga    518
```

### 二、修后对比

| 项 | 修前 | 修后 |
| --- | --- | --- |
| 有贴图的模型 | 4,464（**84.1%**）| 5,227（**98.5%**）|
| 无材质的模型 | **841** | **78** |
| 不同贴图名 | 1,905 | **2,533** |
| 转换的 PNG | 1,814 | **2,407** |
| PNG 体积 | 263 MB | **340 MB** |

**600 模型抽样：561 → 596 有贴图，39 → 4 无材质。**

### 三、线索是怎么来的

**`13120.mod` 有 **96 骨骼**却是「无材质」—— 这不合理。**

**这条线索直接指向「检测有问题」，而不是「数据缺失」。**

### 四、教训（gotcha #104）

> **「16% 缺失」这个数字本身应该被怀疑。**
>
> **我没有立刻怀疑它，而是先把它写进文档当结论 —— 直到抽查样本才发现是漏了一个扩展名。**
>
> **一个「坏消息比例很高」的统计，先怀疑统计方法。**

**这和 gotcha #92（把「没有我要的东西」计入「失败」）是同一类：
统计方式决定结论，而结论的合理性应该反过来检验统计。**

### 五、剩余缺口（都很小）

| 项 | 数量 | 说明 |
| --- | --- | --- |
| 无材质条目的模型 | **78（1.5%）** | 真的没有 MATERIAL 块 |
| 磁盘上缺失的贴图 | **101（4.0%）** | 名字在但文件不在 |
| 转换失败 | **1** | `thunder3`，Pillow 无法识别 |

### 六、墨香贴图的三种格式（完整）

| 格式 | 数量 | 特点 |
| --- | --- | --- |
| `.dds` | 5,315 | 主体，DXGI 格式（UE 不认，gotcha #100）|
| **`.tif`** | **929** | **大图（500-830 KB），Pillow 能读** |
| `.tga` | 518 | 早期格式 |

**总计 6,762 张 —— 全库贴图现已转出 2,407 个 PNG（340 MB）。**

### 七、下一轮（剩余 5 轮）

| 顺序 | 任务 |
| --- | --- |
| **1** | **最终汇总文档**（把 35 轮的结论收成一份可查的总览）|
| 2 | 更新 `LEARNING-INDEX.md` 指向所有新文档 |
| 3 | 批量建材质（2,407 PNG → 材质实例）|
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 52." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 52; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
