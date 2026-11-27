"""Link the second packaging block and tidy the optimisation scripts.

    python Tools/link_learn_pkg02.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PKG1_ROW = ("| **打包与优化第一块** | **`Docs/UE5-LEARN-PKG-01.md`** | "
            "✅ **帧时间终于量出来**（GameThread 8.863 ms）：发现 `stat dump*` 写日志；"
            "⚠️ 打包需关编辑器（Live Coding 互斥体），未做 |")

PKG2_ROW = ("| **打包与优化第二块** | **`Docs/UE5-LEARN-PKG-02.md`** | "
            "🔴 **失败实验的结论**：编辑器 PIE 帧时间被**睡眠主导**（8.36ms 里 7.94ms 是 Stall），"
            "Lumen 开关差 0.024ms 被淹没；判据是看 Stall 占比 |")

SCRATCH = [
    "Tools/opt2_baseline.py",
    "Tools/opt2_nolumen.py",
    "Tools/opt2_base2.py",
    "Tools/opt2_uncap.py",
    "Tools/opt3_cleanup.py",
]

KEEP = ["Tools/opt2_base2.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-PKG-02" not in text and PKG1_ROW in text:
        text = text.replace(PKG1_ROW, PKG1_ROW + "\n" + PKG2_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the second packaging block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    removed = 0
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            if relative == "Tools/opt2_base2.py":
                continue
            os.remove(path)
            removed += 1
    print("removed %d script(s), kept opt2_base2.py as the reusable measurement" % removed)


if __name__ == "__main__":
    main()
