"""Record the full-library texture conversion.

This is the first batch result that covers everything rather than a sample, and the numbers are
worth writing down exactly because they bound the remaining work: how many models name a texture, how
many distinct textures exist, how many were found and converted, and how many are missing.

    python Tools/document_texture_batch.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/BATCH-EXPORT-STATUS.md"

SECTION = """
---

## 二十、全库材质批量转换：1,814 个 PNG（第 34 轮）

### 20.1 结果

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

### 20.2 最常被引用的贴图（共享图集）

| 贴图 | 使用模型数 |
| --- | --- |
| `amgi` | **256** |
| `chang` | 132 |
| `gum` | 130 |
| `do` | 128 |
| `gung` | 128 |
| `combo1` | 107 |
| `eff_09` | 99 |
| `amgi2` | 65 |
| `do2` | 64 |
| `EFF_01` | 49 |

**`amgi` 被 256 个模型共用 —— 说明原游戏大量使用**共享图集**，
不是每个模型一套贴图。**

**这解释了为什么 5,305 个模型只有 1,905 个不同贴图名（约 1:2.8）。**

### 20.3 关键比例

| 项 | 数量 | 占比 |
| --- | --- | --- |
| 有贴图引用的模型 | 4,464 | **84.1%** |
| 无材质条目的模型 | 841 | 15.9% |
| 贴图名解析到文件 | 1,823 / 1,905 | **95.7%** |
| 转换成功 | 1,823 | **100%** |
| 磁盘上缺失 | 82 | 4.3% |

### 20.4 「无材质条目」的 841 个是什么

**没有 MATERIAL 块的模型 —— 可能是：**
- 纯几何道具（用顶点色）
- 特效面片（用程序化材质）
- 骨骼网格的附属件

**因为数量占 16%，值得下一轮抽查几个确认。**

### 20.5 82 个缺失的贴图

**`.mod` 里写了名字，但 `dds/` 和 `tga/` 里都没有。**

**可能原因：**
- 名字在 `.mod` 里存的是旧名（改名了）
- 贴图在别的 `.chx` 或资源包里
- 扩展名不是我试的两种

**占 4.3%，暂不处理。**

### 20.6 转换技术

**用 Pillow 读 DDS 写 PNG：**
```python
image = Image.open(source)      # Pillow 能读 DXGI 格式的 DDS
image.load()
if image.mode not in ("RGB", "RGBA"):
    image = image.convert("RGBA" if "A" in image.mode else "RGB")
image.save(target, "PNG")
```

**⚠️ 这一步绕开了 UE 的 DDS 读取器（它拒绝 DXGI 格式，gotcha #100）。**

**1,719 个转换，0 失败，263 MB。**

### 20.7 新增工具

| 工具 | 作用 |
| --- | --- |
| **`Tools/batch_materials.py`** | **扫全库材质引用 + 只转被引用的贴图（`--limit N`）** |

**用法：**
```powershell
python Tools\\batch_materials.py --limit 6000
```
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 二十、全库材质批量转换" in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(SECTION)
    print("appended; file now %d bytes" % (len(text) + len(SECTION)))


if __name__ == "__main__":
    main()
