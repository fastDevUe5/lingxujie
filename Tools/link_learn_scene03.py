"""Link the third scene block and tidy this round's scripts.

    python Tools/link_learn_scene03.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

SCENE2_ROW = ("| **🎯 完整场景第二块** | **`Docs/UE5-LEARN-SCENE-02.md`** | "
              "✅ 加 6 个形体构图；**户外关掉 Lumen 有 20.45% 像素变化** —— "
              "和第 19 轮室内「测不出来」形成对照 |")

SCENE3_ROW = ("| **🎯 完整场景第三块** | **`Docs/UE5-LEARN-SCENE-03.md`** | "
              "✅ **从 PlayerStart 验证构图，三次迭代才成**；"
              "🔴 相机 yaw0 朝 +X 时画面**宽沿 Y 轴**（我搞错两次）|")

SCRATCH = [
    "Tools/scene_a_pie.py",
    "Tools/scene_measure.py",
    "Tools/scene_relayout.py",
]

KEEP = ["Tools/scene_build.py", "Tools/scene_tune.py",
        "Tools/scene_compose.py", "Tools/scene_relayout2.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-SCENE-03" not in text and SCENE2_ROW in text:
        text = text.replace(SCENE2_ROW, SCENE2_ROW + "\n" + SCENE3_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the third scene block")
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
