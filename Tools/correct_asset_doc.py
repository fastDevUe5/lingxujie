"""Correct the asset breakdown in the pipeline document.

An earlier section called a hundred and seven assets stale because their names did not match the
manifest. Checking the referencers and the class of each one disproved that: they are Texture2D
assets referenced by the material instances, which is exactly what a material instance should
reference. The names differ from the manifest because the manifest names meshes and materials, not
textures.

Being wrong here matters more than usual because the next step would have been deleting them.

    python Tools/correct_asset_doc.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-ASSET-PIPELINE.md"

OLD_START = "### 4.2 发现 107 个历史遗留资产"
OLD_END = "### 4.3 编辑器 API vs 运行时 API"

NEW = """### 4.2 🔴 更正：「107 个遗留资产」是我搞错了

**我先前的判断：不在清单里的 107 个资产是旧构建遗留，可以清理。**

**实测推翻了它：**

```
jp_roof00            -> Texture2D       被 M_LZ_JP_ROOF00 引用
17_101_stonew01      -> Texture2D       被 M_LZ_17_101_STONEW01 引用
54_nanju_04          -> Texture2D       被 M_LZ_54_NANJU_04 引用
101_10_soongsan_door -> Texture2D       被 M_LZ_101_10_SOONGSAN_DOOR 引用
```

**它们是**贴图**，而且正是材质实例所引用的那些贴图。**

**为什么不在清单里：清单只列网格和材质，不列贴图。**

**正确的资产构成：**

| 类别 | 数量 | 说明 |
| --- | --- | --- |
| `SM_LZ_*` | 96 | 网格 |
| `M_LZ_*` | 95 | 材质实例 |
| **`M_Moxiang_*`** | 5 | **母材质**（`Building` / `Building_Masked` / `Ground` / `Stone` / `Lanzhou_Stone`）|
| **其余** | ~102 | **贴图（Texture2D）** |
| **合计** | **298** | |

**⚠️ 如果按我原来的判断去删，会把材质实例的贴图删掉 —— 整个城市的贴图会全部丢失。**

**这条更正比原来的结论重要得多。**

**得到的教训：**
> **「名字对不上清单」不是「没人用」的证据。**
> **必须查两件事：`get_asset_class`（它是什么）和 `get_referencers`（谁引用它）。**
> **两个都查完才知道能不能删。**

"""


def main():
    text = open(PATH, encoding="utf-8").read()
    start = text.find(OLD_START)
    end = text.find(OLD_END)
    if start < 0 or end < 0:
        print("boundaries not found: start=%d end=%d" % (start, end))
        return
    updated = text[:start] + NEW + text[end:]
    open(PATH, "w", encoding="utf-8").write(updated)
    print("corrected section 4.2: %d -> %d bytes" % (len(text), len(updated)))


if __name__ == "__main__":
    main()
