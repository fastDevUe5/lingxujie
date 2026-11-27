"""Record the deletion-safety gotcha that came out of being wrong about the stale assets.

The correction belongs in the gotcha list because the same mistake would repeat: a naming
convention is not evidence of ownership, and a manifest that lists two categories says nothing
about the third.

    python Tools/add_asset_gotcha.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-Gotchas.md"

ENTRY = """
## 75. 「名字对不上清单」不是「没人用」的证据

- **症状**：`Content/Moxiang` 里 104 个资产不在导入清单里，看着像旧构建遗留，
  我据此写了「107 个遗留资产待清理」
- **实测推翻**：
  ```
  jp_roof00            -> Texture2D   <- 被 M_LZ_JP_ROOF00 引用
  17_101_stonew01      -> Texture2D   <- 被 M_LZ_17_101_STONEW01 引用
  ```
  **它们是**贴图**，正是材质实例所引用的那些贴图。清单只列网格和材质，不列贴图。**
- **后果**：按原判断删掉 = **整座城的贴图全部丢失**
- **正确做法**：删任何资产前查**两件事**
  ```
  AssetTools.get_asset_class(asset)      <- 它是什么
  AssetTools.get_referencers(asset)      <- 谁引用它
  ```
  两个都查完才知道能不能删
- **出处**：2026-11-26，本轮最重要的更正
"""


def main():
    text = open(PATH, encoding="utf-8").read()
    if "## 75." in text:
        print("already present")
        return
    with open(PATH, "a", encoding="utf-8") as handle:
        handle.write(ENTRY)
    import re
    numbers = re.findall(r"^## (\d+)\.", text + ENTRY, re.M)
    print("added gotcha 75; total %d" % len(numbers))


if __name__ == "__main__":
    main()
