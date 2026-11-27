INDEX = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"
t = open(INDEX, encoding="utf-8").read()
anchor = None
for line in t.split(chr(10)):
    if "UE5-LEARN-READ-PP" in line:
        anchor = line; break
ROW = "| **\u8865\u8bfb-9 TSR** | **`Docs/UE5-LEARN-READ-TSR.md`** | \u2705 25%\u5c4f\u5e55\u767e\u5206\u6bd4\uff081/16\u50cf\u7d20\uff09\u91cd\u5efa\u753b\u9762\u63a5\u8fd1\u539f\u751f\uff1b\u{1F534} TSR \u4e4b\u540e\u7684 pass \u8dd1\u663e\u793a\u5206\u8fa8\u7387\uff08\u9690\u85cf\u4ee3\u4ef7\uff09\uff1b\u68af\u5ea6\u6307\u6807\u5bf9 TSR \u65e0\u6548 |"
if anchor and "UE5-LEARN-READ-TSR" not in t:
    t = t.replace(anchor, anchor + "\n" + ROW, 1)
    open(INDEX, "w", encoding="utf-8").write(t)
    print("index: added TSR row")
else:
    print("index: anchor=%s already=%s" % (bool(anchor), "UE5-LEARN-READ-TSR" in t))
