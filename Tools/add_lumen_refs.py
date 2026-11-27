"""Correct the rendering document and point the index at Lumen.

The rendering document said Lumen had not been studied, and an earlier summary said the project had
none. The configuration shows both GI and reflections were set to Lumen from the start, and the
requirement they depend on - mesh distance fields - was enabled alongside them.

    python Tools/add_lumen_refs.py
"""

RENDERING = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-RENDERING.md"
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
GOTCHAS = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

RENDERING_NOTE = """
---

## 十、更正：Lumen 一直在运行（2026-11-26）

**本文原先写「Lumen 零」。这是错的。**

**`Config/DefaultEngine.ini` 实测：**
```ini
r.DynamicGlobalIlluminationMethod=1     ; = Lumen GI
r.ReflectionMethod=1                    ; = Lumen 反射
r.Shadow.Virtual.Enable=1               ; 虚拟阴影贴图
r.GenerateMeshDistanceFields=True       ; Lumen 软件光追的前提
r.AllowStaticLighting=False             ; 全动态光照
r.AntiAliasingMethod=4                  ; = TSR
```

**`EDynamicGlobalIlluminationMethod` 的枚举（`EngineTypes.h` 源码）：**
```
0 = None
1 = Lumen        <- 本项目
2 = ScreenSpace（已废弃）
3 = Plugin
```

**所以场景光照看起来不错，不是"默认天光凑合"，而是 Lumen 在算间接光。**

**详细原理见 `Docs/UE5-LUMEN.md`。**
"""

INDEX_OLD = "| **Nanite、后处理、材质设置** | **`Docs/UE5-RENDERING.md`** | 两套 Nanite 结构 + 351 个后处理字段 |"
INDEX_NEW = (
    "| **Nanite、后处理、材质设置** | **`Docs/UE5-RENDERING.md`** | 两套 Nanite 结构 + 351 个后处理字段 |\n"
    "| **Lumen 全局光照 / 为什么光照好看** | **`Docs/UE5-LUMEN.md`** | **本项目已开 Lumen**；前提是距离场 |"
)

GOTCHA = """
## 77. Lumen 的软件光追依赖「生成网格距离场」，两者必须同时开

- **症状**：开了 `r.DynamicGlobalIlluminationMethod=1`（Lumen），但间接光看起来不对或很弱
- **根因**：源码注释写明 Lumen 的前提：
  > *Requires 'Generate Mesh Distance Fields' enabled for Software Ray Tracing
  > and 'Support Hardware Ray Tracing' enabled for Hardware Ray Tracing.*
- **修法**：软件光追路径必须同时有 `r.GenerateMeshDistanceFields=True`；
  硬件光追路径还需要 `r.Lumen.HardwareRayTracing=True` 且显卡支持
- **代价**：开了距离场，网格构建时间变长、内存占用上升（大网格尤其明显）
- **出处**：2026-11-26，读 Lumen 枚举注释
"""


def main():
    text = open(RENDERING, encoding="utf-8").read()
    if "## 十、更正：Lumen 一直在运行" in text:
        print("rendering note already present")
    else:
        with open(RENDERING, "a", encoding="utf-8") as handle:
            handle.write(RENDERING_NOTE)
        print("appended the Lumen correction to the rendering document")

    index = open(INDEX, encoding="utf-8").read()
    if INDEX_OLD in index and "UE5-LUMEN" not in index:
        index = index.replace(INDEX_OLD, INDEX_NEW)
        open(INDEX, "w", encoding="utf-8").write(index)
        print("index updated")
    else:
        print("index row already split or not found")

    gotchas = open(GOTCHAS, encoding="utf-8").read()
    if "## 77." in gotchas:
        print("gotcha already present")
    else:
        with open(GOTCHAS, "a", encoding="utf-8") as handle:
            handle.write(GOTCHA)
        print("added gotcha 77")


if __name__ == "__main__":
    main()
