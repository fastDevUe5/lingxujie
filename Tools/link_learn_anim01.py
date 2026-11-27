"""Link the first animation block and tidy this round's one-off scripts.

    python Tools/link_learn_anim01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

SIXTH_ROW = ("| **Lumen 第六块** | **`Docs/UE5-LEARN-LUMEN-06.md`** | "
             "✅ 发现距离场是**流式**的；用有 DF 的 7.6 cm 网格证明薄面漏光（78.49% 像素变化）|")

ANIM_ROW = ("| **动画第一块** | **`Docs/UE5-LEARN-ANIM-01.md`** | "
            "✅ 单节点 API 全摸清；🔴 编辑器里姿态刷不动（需 tick，属性不可改）；"
            "**发现 API 镜像 190 篇只有 110 可用** |")

SCRATCH = [
    "Tools/anim_single_node_test.py",
    "Tools/anim_find_assets.py",
    "Tools/anim_pair_assets.py",
    "Tools/anim_drive_test.py",
    "Tools/anim_bone_test.py",
    "Tools/anim_probe_bones.py",
    "Tools/anim_bone_test2.py",
    "Tools/anim_diagnose.py",
    "Tools/anim_tick_test.py",
]

KEEP = ["Tools/audit_api_mirror.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-ANIM-01" not in text and SIXTH_ROW in text:
        text = text.replace(SIXTH_ROW, SIXTH_ROW + "\n" + ANIM_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the animation block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
    print("removed %d scratch script(s)" % len(SCRATCH))
    print("kept: %s" % ", ".join(os.path.basename(p) for p in KEEP))


if __name__ == "__main__":
    main()
