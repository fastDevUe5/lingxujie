INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
t = open(INDEX, encoding="utf-8").read()
anchor = None
for line in t.split(chr(10)):
    if "UE5-LEARN-READ-LIGHT" in line:
        anchor = line; break
ROW = "| **补读-8 \u540e\u5904\u7406\u6750\u8d28** | **`Docs/UE5-LEARN-READ-PP.md`** | \u2705 **\u5168 Python \u4ece\u96f6\u5efa\u540e\u5904\u7406\u6750\u8d28**\uff08M_PPDesat\uff09\u5e76\u751f\u6548\uff1a\u9971\u548c\u5ea6 52.68\u21920.05\uff0c97.57%\u50cf\u7d20\u53d8\uff1b`WeightedBlendable.material` \u5b9e\u9645\u53eb **object** |"
if anchor and "UE5-LEARN-READ-PP" not in t:
    t = t.replace(anchor, anchor + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added PP row")
else:
    print("index: anchor=%s already=%s" % (bool(anchor), "UE5-LEARN-READ-PP" in t))
