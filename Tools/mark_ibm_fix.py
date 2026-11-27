"""Add the two-part IBM fix to the learning index.

    python Tools/mark_ibm_fix.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = "- **验证必须用独立读取者**"

LINE = (
    "- **IBM 要修两处**：槽位顺序（3/7/11 → 12/13/14）**加**平移乘 0.01（厘米转米）"
    " —— 只修第一处会得到放大 100 倍的模型\n"
)


def main():
    text = open(PATH, encoding="utf-8").read()
    if "IBM 要修两处" in text:
        print("already present")
        return
    if ANCHOR not in text:
        print("anchor not found")
        return
    text = text.replace(ANCHOR, LINE + ANCHOR, 1)
    open(PATH, "w", encoding="utf-8").write(text)
    print("added the two-part IBM fix note")


if __name__ == "__main__":
    main()
