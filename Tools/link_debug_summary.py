"""Link the summary from the learning index.

    python Tools/link_debug_summary.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

ANCHOR = "| **🩺 症状手册** | **`Docs/UE5-DEBUG-PLAYBOOK.md`** | ✅ **出问题先看这份** |"
NEW = "| **📋 调试总结** | **`Docs/UE5-DEBUG-SUMMARY.md`** | ✅ 17 轮到什么程度、还差什么 |"


def main():
    text = open(PATH, encoding="utf-8").read()
    if "UE5-DEBUG-SUMMARY" in text:
        print("already present")
        return
    if ANCHOR not in text:
        print("anchor not found; current rows around the playbook:")
        for line in text.split("\n"):
            if "PLAYBOOK" in line:
                print("  " + line)
        return
    text = text.replace(ANCHOR, ANCHOR + "\n" + NEW, 1)
    open(PATH, "w", encoding="utf-8").write(text)
    print("learning index: linked the summary")


if __name__ == "__main__":
    main()
