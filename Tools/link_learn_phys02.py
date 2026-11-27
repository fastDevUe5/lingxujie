"""Link the second physics block and tidy this round's one-off scripts.

    python Tools/link_learn_phys02.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PHYS1_ROW = ("| **物理第一块** | **`Docs/UE5-LEARN-PHYS-01.md`** | "
             "✅ **实测球落下 275 cm 并静止**；🔴 发现 `time.sleep()` 会冻住世界，"
             "这是之前所有失败的根因 |")

PHYS2_ROW = ("| **物理第二块** | **`Docs/UE5-LEARN-PHYS-02.md`** | "
             "🔴 **推翻**「球会滚」：立方体比球漂得远（83 vs 20 cm）；"
             "✅ **阻尼把漂移降到 0** |")

SCRATCH = [
    "Tools/phys2_a_prepare.py",
    "Tools/phys2_b_read.py",
    "Tools/phys2_c_damping.py",
    "Tools/phys2_d_cleanup.py",
    "Tools/phys_reset_state.py",
]

KEEP = [
    "Tools/phys2_final_cleanup.py",
    "Tools/phys_a_prepare.py",
    "Tools/phys_b_read.py",
    "Tools/phys_cleanup.py",
]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-PHYS-02" not in text and PHYS1_ROW in text:
        text = text.replace(PHYS1_ROW, PHYS1_ROW + "\n" + PHYS2_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the second physics block")
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
    print("kept: %s" % ", ".join(os.path.basename(p) for p in KEEP))


if __name__ == "__main__":
    main()
