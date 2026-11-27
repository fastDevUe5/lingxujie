INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
t = open(INDEX, encoding="utf-8").read()
anchor = None
for line in t.split(chr(10)):
    if "UE5-LEARN-READ-SKY" in line:
        anchor = line; break
ROW = "| **补读-6 \u592a\u9633\u9ad8\u5ea6\u626b\u63cf** | **`Docs/UE5-LEARN-READ-SUN.md`** | \u2705 \u4e94\u4e2a\u70b9\u5355\u8c03\uff1aR\u2212B \u4ece \u221218.4(-5\u00b0) \u5230 \u221274.4(-60\u00b0)\uff1b\u771f\u6b63\u81ea\u53d8\u91cf\u662f\u592a\u9633\u9ad8\u5ea6\uff0cRayleigh \u53ea\u662f\u653e\u5927\u5668 |"
if anchor and "UE5-LEARN-READ-SUN" not in t:
    t = t.replace(anchor, anchor + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added sun row")
else:
    print("index: anchor=%s already=%s" % (bool(anchor), "UE5-LEARN-READ-SUN" in t))
