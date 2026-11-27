INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
import re
t = open(INDEX, encoding="utf-8").read()
# 找 VSM 那行做锚点
anchor = None
for line in t.split(chr(10)):
    if "UE5-LEARN-READ-VSM" in line:
        anchor = line
        break
ROW = "| **补读-5 天空大气** | **`Docs/UE5-LEARN-READ-SKY.md`** | \u2705 \u56db\u7ec4\u6563\u5c04\u914d\u7f6e\u5b9e\u6d4b\uff1aRayleigh\u00d74.5 \u8ba9\u65e5\u843d\u66f4\u7ea2(194/154/140)\uff1bMie\u00d712.5 \u53d8\u7070(165/152/165)\uff1bMie \u672c\u8eab\u5c31\u662f\u9ad8\u5ea6\u96fe |"
if anchor and "UE5-LEARN-READ-SKY" not in t:
    t = t.replace(anchor, anchor + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added sky row")
else:
    print("index: anchor=%s already=%s" % (bool(anchor), "UE5-LEARN-READ-SKY" in t))
