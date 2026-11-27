"""Link the physics block and tidy the one-off scripts from this round.

    python Tools/link_learn_phys01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANIM_ROW = ("| **动画第一块** | **`Docs/UE5-LEARN-ANIM-01.md`** | "
            "✅ 单节点 API 全摸清；🔴 编辑器里姿态刷不动（需 tick，属性不可改）；"
            "**发现 API 镜像 190 篇只有 110 可用** |")

PHYS_ROW = ("| **物理第一块** | **`Docs/UE5-LEARN-PHYS-01.md`** | "
            "✅ **实测球落下 275 cm 并静止**；🔴 发现 `time.sleep()` 会冻住世界，"
            "这是之前所有失败的根因 |")

SCRATCH = [
    "Tools/phys_setup_drop.py",
    "Tools/phys_read_drop.py",
    "Tools/phys_read_game.py",
    "Tools/phys_reset.py",
    "Tools/phys_sample_fall.py",
    "Tools/phys_drop_saved.py",
]

KEEP = ["Tools/phys_a_prepare.py", "Tools/phys_b_read.py", "Tools/phys_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-PHYS-01" not in text and ANIM_ROW in text:
        text = text.replace(ANIM_ROW, ANIM_ROW + "\n" + PHYS_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the physics block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    removed = 0
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
            removed += 1
    print("removed %d scratch script(s)" % removed)
    print("kept the three-step sequence: %s" % ", ".join(os.path.basename(p) for p in KEEP))


if __name__ == "__main__":
    main()
