import re
INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
ANCHOR = "| **📋 阶段总结** | **`Docs/UE5-LEARN-SUMMARY.md`** | 22 篇 / 28 条更正；**目标终点已达成**，但 69 篇只覆盖约 17% |"
ROW = "| **补读-1 Nanite 技术** | **`Docs/UE5-LEARN-READ-NANITE.md`** | ✅ 文档给的 12B/16B 经源码核实；默认 16M/4M = **256 MB**；引擎溢出会自动告警，**本项目从未触发** |"
t = open(INDEX, encoding="utf-8").read()
if "UE5-LEARN-READ-NANITE" not in t and ANCHOR in t:
    t = t.replace(ANCHOR, ANCHOR + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added reading row")
else:
    print("index: nothing to add")
