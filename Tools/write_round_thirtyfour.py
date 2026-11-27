"""Append the thirty-fourth round.

    python Tools/write_round_thirtyfour.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/NEXT-SESSION.md"

SECTION = """

## 51. 第三十四轮：**全库材质批量转换 —— 1,814 个 PNG**（2026-11-26 35:00）

### 一、结果

```
scanning 5305 models for material textures

models with a named texture:     4464      (84%)
models with no material entry:   841
distinct texture names:          1905

textures found on disk:  1823
textures missing:        82
converted this run:      1719
already converted:        104
conversion failures:         0

PNG folder now holds 1814 files, 263.1 MB
```

### 二、最常被引用的贴图（共享图集）

| 贴图 | 使用模型数 |
| --- | --- |
| **`amgi`** | **256** |
| `chang` | 132 |
| `gum` | 130 |
| `do` | 128 |
| `gung` | 128 |
| `combo1` | 107 |

**`amgi` 被 256 个模型共用 —— 原游戏大量使用**共享图集**。
这解释了为什么 5,305 个模型只有 1,905 个不同贴图名（约 1:2.8）。**

### 三、关键比例

| 项 | 数量 | 占比 |
| --- | --- | --- |
| 有贴图引用的模型 | 4,464 | **84.1%** |
| 无材质条目的模型 | 841 | 15.9% |
| 贴图名解析到文件 | 1,823 / 1,905 | **95.7%** |
| 转换成功 | 1,823 | **100%** |
| 磁盘上缺失 | 82 | 4.3% |

### 四、两个已量化的缺口

**① 841 个模型没有 MATERIAL 块（16%）**
可能是纯几何道具、特效面片、骨骼附属件。**值得抽查。**

**② 82 个贴图名在磁盘上找不到（4.3%）**
可能是改名了、在别的资源包里、或扩展名不是 dds/tga。

### 五、技术要点

**用 Pillow 读 DDS 写 PNG，绕开 UE 的 DDS 读取器（它拒绝 DXGI 格式）：**
```python
image = Image.open(source)
image.load()
image.save(target, "PNG")
```

**1,719 个转换，0 失败，263 MB。**

### 六、新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/batch_materials.py`** | **扫全库材质引用 + 只转被引用的贴图** |

**用法：**
```powershell
python Tools\\batch_materials.py --limit 6000
```

### 七、这一轮的意义

> **这是第一个覆盖**全库**而不是抽样的批量产出。**
>
> **它给出了剩余工作的边界：**
> - 84% 的模型有贴图可挂
> - 16% 没有（要么不需要，要么要另外处理）
> - 贴图资源 96% 完整

### 八、下一轮

| 顺序 | 任务 |
| --- | --- |
| **1** | **抽查 841 个「无材质」模型**，确认它们是哪类 |
| 2 | 批量建材质（1,814 个 PNG → 材质实例）|
| 3 | 批量导入 UE（253 个 gltf + 材质）|
| 4 | 最终汇总文档 |
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 51." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended section 51; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
