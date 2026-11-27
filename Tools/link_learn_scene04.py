"""Link the fourth scene block and tidy this round's scripts.

    python Tools/link_learn_scene04.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

SCENE3_ROW = ("| **🎯 完整场景第三块** | **`Docs/UE5-LEARN-SCENE-03.md`** | "
              "✅ **从 PlayerStart 验证构图，三次迭代才成**；"
              "🔴 相机 yaw0 朝 +X 时画面**宽沿 Y 轴**（我搞错两次）|")

SCENE4_ROW = ("| **🎯 完整场景第四块** | **`Docs/UE5-LEARN-SCENE-04.md`** | "
              "✅ **begin_play 游戏态验证**（PlayerController/Pawn/HUD/GameMode 全在）；"
              "量出 14 actor 场景：FrameTime 10.73ms / 工作 0.469ms |")

SCRATCH = [
    "Tools/scene_a_beginplay.py",
    "Tools/scene_b_ingame.py",
    "Tools/scene_end.py",
    "Tools/scene_back.py",
]

KEEP = ["Tools/scene_build.py", "Tools/scene_tune.py",
        "Tools/scene_compose.py", "Tools/scene_relayout2.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-SCENE-04" not in text and SCENE3_ROW in text:
        text = text.replace(SCENE3_ROW, SCENE3_ROW + "\n" + SCENE4_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the fourth scene block")
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
