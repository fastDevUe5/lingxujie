"""Add the summary pointer to the debug index header.

    python Tools/link_summary_in_debug_index.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-DEBUG-INDEX.md"

ANCHOR = "> **🔴 出问题时先看 `UE5-DEBUG-PLAYBOOK.md` —— 症状 → 该查什么。**"
NEW = ("> **🔴 出问题时先看 `UE5-DEBUG-PLAYBOOK.md` —— 症状 → 该查什么。**\n"
       ">\n"
       "> **📋 要看整段学下来做到了什么、还差什么：`UE5-DEBUG-SUMMARY.md`。**")


def main():
    text = open(PATH, encoding="utf-8").read()
    if "UE5-DEBUG-SUMMARY" in text:
        print("already present")
        return
    if ANCHOR not in text:
        print("anchor not found")
        return
    text = text.replace(ANCHOR, NEW, 1)
    open(PATH, "w", encoding="utf-8").write(text)
    print("debug index: added the summary pointer")


if __name__ == "__main__":
    main()
