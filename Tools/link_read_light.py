INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
t = open(INDEX, encoding="utf-8").read()
anchor = None
for line in t.split(chr(10)):
    if "UE5-LEARN-READ-SUN" in line:
        anchor = line; break
ROW = "| **补读-7 \u65b9\u5411\u5149** | **`Docs/UE5-LEARN-READ-LIGHT.md`** | \u2705 \u5f3a\u5ea6\u5355\u4f4d\u662f **lux**\uff0c\u6211\u8bbe\u7684 8 lux \u6bd4\u5ba4\u5185\u8fd8\u6697\uff1b\u66dd\u5149\u9002\u5e94\u53ea\u6709 **8.06 \u6863(267\u500d)**\uff0c8\u2192100000 \u662f 13.61 \u6863 \u2192 \u8fc7\u66dd |"
if anchor and "UE5-LEARN-READ-LIGHT" not in t:
    t = t.replace(anchor, anchor + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added light row")
else:
    print("index: anchor=%s already=%s" % (bool(anchor), "UE5-LEARN-READ-LIGHT" in t))
