"""Correct the two counts the summary had drifted from.

The summary was written when there were a hundred four gotchas and it claimed thirty-two topic
documents when the filesystem holds thirty-one. Both are small, and both are exactly the kind of drift
that makes a reference document untrustworthy - a reader cannot tell which numbers to believe if any
of them are stale.

    python Tools/fix_summary_counts.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Docs/UE5-KNOWLEDGE-SUMMARY.md"

PAIRS = [
    ("104 条坑", "106 条坑"),
    ("31 篇专题文档", "31 篇专题文档"),
    ("（104 条）", "（106 条）"),
    ("104 条坑分类", "106 条坑分类"),
    ("31 篇文档地图", "31 篇文档地图"),
    ("32 篇文档地图", "31 篇文档地图"),
    ("共 34 篇文档", "共 31 篇专题文档"),
]


def main():
    text = open(PATH, encoding="utf-8").read()
    before = text
    changed = 0
    # Replace only the specific stale figures.
    for old, new in (("104 条", "106 条"),
                     ("104 条坑", "106 条坑")):
        if old in text and old != new:
            text = text.replace(old, new)
            changed += 1

    # The header line carries both figures.
    text = text.replace("104 条坑", "106 条坑")
    text = text.replace("32 篇文档地图", "31 篇文档地图")
    text = text.replace("31 篇专题文档", "31 篇专题文档")

    if text == before:
        print("no change needed")
    else:
        open(PATH, "w", encoding="utf-8").write(text)
        print("summary corrected")

    # Report what the file now says, so the result is visible rather than assumed.
    import re
    updated = open(PATH, encoding="utf-8").read()
    gotcha_mentions = sorted(set(re.findall(r"(\d+)\s*条坑", updated)))
    doc_mentions = sorted(set(re.findall(r"(\d+)\s*篇(?:专题)?文档", updated)))
    print("gotcha figures mentioned: %s" % gotcha_mentions)
    print("document figures mentioned: %s" % doc_mentions)


if __name__ == "__main__":
    main()
