INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
ANCHOR = "| **补读-2 Nanite 概述 + 噪声排查** | **`Docs/UE5-LEARN-READ-NANITE2.md`** | 🔴 **推翻 SCENE-02**：噪声底 5.4-7.7%(云在动)；藏云后 **Lumen 实际只差 0.18%**，20.45% 是云 |"
ROW = "| **补读-3 A/B 标准流程** | **`Docs/UE5-LEARN-READ-AB.md`** | ✅ 关云后底噪 **0.62%**，Nanite 开关差异 **46.37%**（75×底噪）；引擎报 **VSM 非Nanite队列溢出** |"
t = open(INDEX, encoding="utf-8").read()
if "UE5-LEARN-READ-AB" not in t and ANCHOR in t:
    t = t.replace(ANCHOR, ANCHOR + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added reading row 3")
else:
    print("index: nothing to add")
