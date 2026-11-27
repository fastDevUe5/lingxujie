"""Point the learning index at the finished local document mirror.

    python Tools/link_local_docs.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/LEARNING-INDEX.md"

PAIRS = [
    ("| **本地有哪些官方文档** | `Docs/LOCAL-UE-DOCS.md` | 镜像范围与更新方法 |",
     "| **🔄 要查官方文档** | **`Docs/LOCAL-UE-DOCS.md`** | **本地已有 52 篇手册 + 190 篇 API，先查这里** |"),
    ("| `LOCAL-UE-DOCS.md` | 本地文档镜像的范围 | 想知道查什么有没有本地版 |",
     "| **`LOCAL-UE-DOCS.md`** | **本地官方文档：52 篇手册 / 730 KB** | **先查这里，别再抓网页** |"),
]


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    for old, new in PAIRS:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1
    if changed:
        open(PATH, "w", encoding="utf-8").write(text)
        print("learning index: %d row(s) updated" % changed)
    else:
        print("nothing changed")

    # Report what the file now says.
    for line in open(PATH, encoding="utf-8").read().split("\n"):
        if "LOCAL-UE-DOCS" in line:
            print("  " + line.strip())


if __name__ == "__main__":
    main()
