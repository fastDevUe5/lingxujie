"""Link the sixth Lumen block and tidy the one-off scripts.

    python Tools/link_learn_06.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

FIFTH_ROW = ("| **Lumen 第五块** | **`Docs/UE5-LEARN-LUMEN-05.md`** | "
             "🔴 **更正**：练习关卡零距离场，测的是阴影穿透不是 GI 漏光 |")

SIXTH_ROW = ("| **Lumen 第六块** | **`Docs/UE5-LEARN-LUMEN-06.md`** | "
             "✅ 发现距离场是**流式**的；用有 DF 的 7.6 cm 网格证明薄面漏光（78.49% 像素变化）|")

# These were diagnostics with no reuse value.
SCRATCH = [
    "Tools/learn_df_probe.py",
    "Tools/learn_df_by_atlas.py",
    "Tools/learn_df_probe_place.py",
    "Tools/learn_df_read.py",
    "Tools/learn_df_control_off.py",
    "Tools/learn_df_ceiling_build.py",
    "Tools/learn_df_restore_all.py",
]

KEEP = ["Tools/learn_wall_thickness.py", "Tools/learn_build_lightlab.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-LUMEN-06" not in text and FIFTH_ROW in text:
        text = text.replace(FIFTH_ROW, FIFTH_ROW + "\n" + SIXTH_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the sixth block")
    else:
        print("learning index: nothing to add")

    root = "C:/Users/tk/Desktop/lingxujie/"
    for relative in SCRATCH:
        path = root + relative
        if os.path.exists(path):
            os.remove(path)
            print("removed %s" % os.path.basename(path))

    print("kept: %s" % ", ".join(os.path.basename(p) for p in KEEP))


if __name__ == "__main__":
    main()
