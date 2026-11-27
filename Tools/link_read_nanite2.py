INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
ANCHOR = "| **补读-1 Nanite 技术** | **`Docs/UE5-LEARN-READ-NANITE.md`** | ✅ 文档给的 12B/16B 经源码核实；默认 16M/4M = **256 MB**；引擎溢出会自动告警，**本项目从未触发** |"
ROW = "| **补读-2 Nanite 概述 + 噪声排查** | **`Docs/UE5-LEARN-READ-NANITE2.md`** | 🔴 **推翻 SCENE-02**：噪声底 5.4-7.7%(云在动)；藏云后 **Lumen 实际只差 0.18%**，20.45% 是云 |"
t = open(INDEX, encoding="utf-8").read()
if "UE5-LEARN-READ-NANITE2" not in t and ANCHOR in t:
    t = t.replace(ANCHOR, ANCHOR + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added reading row 2")
else:
    print("index: nothing to add")
