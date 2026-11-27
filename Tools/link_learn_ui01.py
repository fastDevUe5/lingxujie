"""Link the UI block and tidy this round's probe scripts.

    python Tools/link_learn_ui01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

MAT3_ROW = ("| **材质第三块** | **`Docs/UE5-LEARN-MAT-03.md`** | "
            "✅ **Nanite override 源码→实测→画面全链条**；"
            "搞清材质解析三层优先级；项目 0/60 材质用了 override |")

UI_ROW = ("| **UI/UMG 第一块** | **`Docs/UE5-LEARN-UI-01.md`** | "
          "🔴 **负面结论**：只通第 1 环（建资产）；树不可访问、面板无构造方法、"
          "`construct` 后仍 0×0、`add_to_viewport` 无效（PIE 亦同）|")

SCRATCH = [
    "Tools/ui_probe.py",
    "Tools/ui_probe_tree.py",
    "Tools/ui_runtime.py",
    "Tools/ui_existing.py",
    "Tools/ui_construct.py",
    "Tools/ui_a_pie.py",
    "Tools/ui_b_widget.py",
]

KEEP = ["Tools/ui_build_widget.py", "Tools/ui_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-UI-01" not in text and MAT3_ROW in text:
        text = text.replace(MAT3_ROW, MAT3_ROW + "\n" + UI_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the UI block")
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
