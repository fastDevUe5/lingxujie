"""Link the Niagara block and tidy this round's one-off scripts.

    python Tools/link_learn_nia01.py
"""

import os

INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PHYS2_ROW = ("| **物理第二块** | **`Docs/UE5-LEARN-PHYS-02.md`** | "
             "🔴 **推翻**「球会滚」：立方体比球漂得远（83 vs 20 cm）；"
             "✅ **阻尼把漂移降到 0** |")

NIA_ROW = ("| **Niagara 第一块** | **`Docs/UE5-LEARN-NIAGARA-01.md`** | "
           "🔴 项目**零** Niagara 资产、Python**无**系统工厂；"
           "✅ 遗留 Cascade 粒子实测 40→39 存活；截图失败（白盒子）|")

SCRATCH = [
    "Tools/nia_probe.py",
    "Tools/nia_can_create.py",
    "Tools/nia_find_legacy.py",
    "Tools/nia_a_place.py",
    "Tools/nia_b_dim.py",
    "Tools/nia_c_activate.py",
    "Tools/nia_d_light_back.py",
    "Tools/nia_e_exposure.py",
    "Tools/nia_end.py",
    "Tools/nia_dim2.py",
    "Tools/nia_lightoff.py",
]

KEEP = ["Tools/nia_cleanup.py"]


def main():
    text = open(INDEX, encoding="utf-8").read()
    if "UE5-LEARN-NIAGARA-01" not in text and PHYS2_ROW in text:
        text = text.replace(PHYS2_ROW, PHYS2_ROW + "\n" + NIA_ROW, 1)
        open(INDEX, "w", encoding="utf-8").write(text)
        print("learning index: added the Niagara block")
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
