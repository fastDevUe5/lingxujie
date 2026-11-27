"""Move the focus rule to the end and number it 12.

It landed before rule 11, which reads as an out-of-order list. The content is right; only its place
and number were wrong.

    python Tools/fix_rule_order.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/AGENTS.md"

START = "11b. **自动化绝不能抢焦点"
END = "11. **人手动创建的文件，一律不许动"


def main():
    text = open(PATH, encoding="utf-8").read()
    if "11b." not in text:
        print("rule 11b not found; nothing to move")
        return

    start = text.find(START)
    end = text.find(END, start)
    if start < 0 or end < 0:
        print("could not find both boundaries")
        return

    block = text[start:end]
    text = text[:start] + text[end:]

    block = block.replace("11b. **自动化绝不能抢焦点", "12. **自动化绝不能抢焦点", 1)

    # Append after the whole rule-11 block, which ends at the next top-level heading.
    anchor = "\n## 开工流程"
    position = text.find(anchor)
    if position < 0:
        print("could not find where rule 11 ends")
        return
    text = text[:position] + "\n" + block.rstrip() + "\n" + text[position:]

    open(PATH, "w", encoding="utf-8").write(text)
    print("rule moved to the end and numbered 12")

    # Report the order so the result is visible.
    import re
    for match in re.finditer(r"^(\d+[a-z]?)\. \*\*(.{0,24})", open(PATH, encoding="utf-8").read(), re.M):
        print("  %-5s %s" % (match.group(1), match.group(2)))


if __name__ == "__main__":
    main()
