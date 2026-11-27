"""Link the scene block and tidy this round's scripts.

    python Tools/link_learn_scene01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PKG2_ROW = ("| **打包与优化第二块** | **`Docs/UE5-LEARN-PKG-02.md`** | "
            "🔴 **失败实验的结论**：编辑器 PIE 帧时间被**睡眠主导**（8.36ms 里 7.94ms 是 Stall），"
            "Lumen 开关差 0.024ms 被淹没；判据是看 Stall 占比 |")

SCENE_ROW = ("| **🎯 完整场景第一块** | **`Docs/UE5-LEARN-SCENE-01.md`** | "
             "✅ **用官方素材搭出并调优完整场景**（8 actor：日/天空/天光/云/雾/地面/出生点/后处理）；"
             "🔴 `AEM_MANUAL` 不给值会黑屏（亮度 0.7 → 140.6）|")

SCRATCH = [
    "Tools/scene_inventory.py",
    "Tools/scene_read_template.py",
    "Tools/scene_fix_exposure.py",
]

KEEP = ["Tools/scene_build.py", "Tools/scene_tune.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-SCENE-01" not in text and PKG2_ROW in text:
        text = text.replace(PKG2_ROW, PKG2_ROW + "\n" + SCENE_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the scene block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
    print("kept: %s" % ", ".join(os.path.basename(p) for p in KEEP))


if __name__ == "__main__":
    main()
