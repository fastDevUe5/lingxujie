INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
ANCHOR = "| **补读-3 A/B 标准流程** | **`Docs/UE5-LEARN-READ-AB.md`** | \u2705 \u5173\u4e91\u540e\u5e95\u566a **0.62%**\uff0cNanite \u5f00\u5173\u5dee\u5f02 **46.37%**\uff0875\u00d7\u5e95\u566a\uff09\uff1b\u5f15\u64ce\u62a5 **VSM \u975eNanite\u961f\u5217\u6ea2\u51fa** |"
ANCHOR = ANCHOR.encode().decode('unicode_escape') if '\\u' in ANCHOR else ANCHOR
ROW = "| **补读-4 虚拟阴影贴图** | **`Docs/UE5-LEARN-READ-VSM.md`** | ✅ VSM 有**五种**溢出（源码核实）；只有 MARKING_JOB_QUEUE 只影响性能；「尽量让几何是 Nanite」；页池 4096 页 |"
t = open(INDEX, encoding="utf-8").read()
if "UE5-LEARN-READ-VSM" not in t and ANCHOR in t:
    t = t.replace(ANCHOR, ANCHOR + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added VSM row")
else:
    print("index: anchor found=%s, already=%s" % (ANCHOR in t, "UE5-LEARN-READ-VSM" in t))
