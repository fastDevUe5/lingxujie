"""Link the second material block and tidy this round's scripts.

    python Tools/link_learn_mat02.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

MAT1_ROW = ("| **材质第一块** | **`Docs/UE5-LEARN-MAT-01.md`** | "
            "✅ **从零建材质并贴到 6 个面，盒子从白变黑（画面证明）**；"
            "顺手修好白盒子问题 |")

MAT2_ROW = ("| **材质第二块** | **`Docs/UE5-LEARN-MAT-02.md`** | "
            "✅ **参数化材质 + 两个实例，一张图看出参数差异**；"
            "🔴 `set_..._scalar_parameter_value` 返回 False 但值生效 |")

SCRATCH = ["Tools/mat_apply_instances.py"]
KEEP = ["Tools/mat_build_tex.py", "Tools/mat_instance.py",
        "Tools/mat_build_dark.py", "Tools/mat_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-MAT-02" not in text and MAT1_ROW in text:
        text = text.replace(MAT1_ROW, MAT1_ROW + "\n" + MAT2_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the second material block")
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
