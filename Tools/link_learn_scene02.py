"""Link the second scene block and tidy this round's scripts.

    python Tools/link_learn_scene02.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

SCENE1_ROW = ("| **🎯 完整场景第一块** | **`Docs/UE5-LEARN-SCENE-01.md`** | "
              "✅ **用官方素材搭出并调优完整场景**（8 actor：日/天空/天光/云/雾/地面/出生点/后处理）；"
              "🔴 `AEM_MANUAL` 不给值会黑屏（亮度 0.7 → 140.6）|")

SCENE2_ROW = ("| **🎯 完整场景第二块** | **`Docs/UE5-LEARN-SCENE-02.md`** | "
              "✅ 加 6 个形体构图；**户外关掉 Lumen 有 20.45% 像素变化** —— "
              "和第 19 轮室内「测不出来」形成对照 |")

SCRATCH = [
    "Tools/scene_lumen_off.py",
    "Tools/scene_restore.py",
]

KEEP = ["Tools/scene_build.py", "Tools/scene_tune.py", "Tools/scene_compose.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-SCENE-02" not in text and SCENE1_ROW in text:
        text = text.replace(SCENE1_ROW, SCENE1_ROW + "\n" + SCENE2_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the second scene block")
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
