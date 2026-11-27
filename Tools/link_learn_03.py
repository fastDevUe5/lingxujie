"""Append the third Lumen block, and remove the workshop's temporary scripts.

    python Tools/link_learn_03.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

SECOND_ROW = ("| **Lumen 第二块** | **`Docs/UE5-LEARN-LUMEN-02.md`** | "
              "✅ 源码判定骨骼网格有 Card；发现官方文档限制清单不完整 |")

THIRD_ROW = ("| **Lumen 第三块** | **`Docs/UE5-LEARN-LUMEN-03.md`** | "
             "✅ 量出 4 个网格薄于 10 cm（1 个 0.0）；漏光实验**失败**并写明原因 |")

# One-off probes used only to face the wall; the reusable ones stay.
SCRATCH = [
    "Tools/lumen_face_wall.py",
    "Tools/lumen_face_wall2.py",
    "Tools/lumen_skeletal_check.py",
]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-LUMEN-03" not in text and SECOND_ROW in text:
        text = text.replace(SECOND_ROW, SECOND_ROW + "\n" + THIRD_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the third block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
            print("removed %s" % os.path.basename(path))


if __name__ == "__main__":
    main()
