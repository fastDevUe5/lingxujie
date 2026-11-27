"""Link the third packaging block and tidy this round's scripts.

    python Tools/link_learn_pkg03.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

SCENE4_ROW = ("| **🎯 完整场景第四块** | **`Docs/UE5-LEARN-SCENE-04.md`** | "
              "✅ **begin_play 游戏态验证**（PlayerController/Pawn/HUD/GameMode 全在）；"
              "量出 14 actor 场景：FrameTime 10.73ms / 工作 0.469ms |")

PKG3_ROW = ("| **打包与优化第三块** | **`Docs/UE5-LEARN-PKG-03.md`** | "
            "🔴 **GPU 耗时读不到**：`stat gpu` 不写日志，`r.GPUStats.Enabled`/`r.GPUCapture` 都不存在；"
            "CPU 和 GPU 走两套统计系统 |")

SCRATCH = ["Tools/gpu_probe.py", "Tools/gpu_end.py", "Tools/gpu_back.py"]
KEEP = []


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-PKG-03" not in text and SCENE4_ROW in text:
        text = text.replace(SCENE4_ROW, SCENE4_ROW + "\n" + PKG3_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the third packaging block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
    print("cleaned up probe scripts")


if __name__ == "__main__":
    main()
