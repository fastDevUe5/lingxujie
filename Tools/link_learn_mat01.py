"""Link the material block and tidy this round's scripts.

    python Tools/link_learn_mat01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

NIA_ROW = ("| **Niagara 第一块** | **`Docs/UE5-LEARN-NIAGARA-01.md`** | "
           "🔴 项目**零** Niagara 资产、Python**无**系统工厂；"
           "✅ 遗留 Cascade 粒子实测 40→39 存活；截图失败（白盒子）|")

MAT_ROW = ("| **材质第一块** | **`Docs/UE5-LEARN-MAT-01.md`** | "
           "✅ **从零建材质并贴到 6 个面，盒子从白变黑（画面证明）**；"
           "顺手修好白盒子问题 |")

SCRATCH = ["Tools/mat_check.py", "Tools/mat_a_apply.py"]

KEEP = ["Tools/mat_build_dark.py", "Tools/mat_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-MAT-01" not in text and NIA_ROW in text:
        text = text.replace(NIA_ROW, NIA_ROW + "\n" + MAT_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the material block")
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
