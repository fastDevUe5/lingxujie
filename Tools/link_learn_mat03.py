"""Link the third material block and tidy this round's scripts.

    python Tools/link_learn_mat03.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

MAT2_ROW = ("| **材质第二块** | **`Docs/UE5-LEARN-MAT-02.md`** | "
            "✅ **参数化材质 + 两个实例，一张图看出参数差异**；"
            "🔴 `set_..._scalar_parameter_value` 返回 False 但值生效 |")

MAT3_ROW = ("| **材质第三块** | **`Docs/UE5-LEARN-MAT-03.md`** | "
            "✅ **Nanite override 源码→实测→画面全链条**；"
            "搞清材质解析三层优先级；项目 0/60 材质用了 override |")

SCRATCH = [
    "Tools/mat_nanite_probe.py",
    "Tools/mat_nanite_set.py",
    "Tools/mat_nanite_visual.py",
]

KEEP = ["Tools/mat_nanite_set2.py", "Tools/mat_nanite_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-MAT-03" not in text and MAT2_ROW in text:
        text = text.replace(MAT2_ROW, MAT2_ROW + "\n" + MAT3_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the third material block")
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
