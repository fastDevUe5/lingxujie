"""Check that the numbers the documents claim match what is on disk.

A knowledge base whose stated counts drift from reality is worse than one with no counts, because the
drift is invisible. This compares the figures the summary asserts against filesystem facts and lists
any mismatch.

    python Tools/verify_doc_numbers.py
"""

import glob
import os
import re

DOCS = "C:/Users/tk/Desktop/lingxujie/Docs"
ROOT = "C:/Users/tk/Desktop/lingxujie"


def fact(label, value):
    return (label, value)


def main():
    print("=== measured ===")
    gltf = len(glob.glob(os.path.join(ROOT, "Assets/Moxiang/ue_import/batch/*.gltf")))
    png = len(glob.glob(os.path.join(ROOT, "Assets/Moxiang/textures_png/*.png")))
    png_bytes = sum(os.path.getsize(p) for p in
                    glob.glob(os.path.join(ROOT, "Assets/Moxiang/textures_png/*.png")))
    gotchas = len(re.findall(r"^## \d+\.", open(os.path.join(DOCS, "UE5-Gotchas.md"),
                                               encoding="utf-8").read(), re.M))
    special = [f for f in os.listdir(DOCS) if f.endswith(".md")
               and f.startswith(("UE5-", "MOD-", "ANM-", "MOXIANG-", "CHARACTER-", "BATCH-"))]

    facts = {
        "batch gltf": gltf,
        "png files": png,
        "png MB": round(png_bytes / (1024.0 * 1024.0), 1),
        "gotchas": gotchas,
        "topic documents": len(special),
    }
    for label, value in facts.items():
        print("  %-18s %s" % (label, value))

    print("")
    print("=== what the summary claims ===")
    summary_path = os.path.join(DOCS, "UE5-KNOWLEDGE-SUMMARY.md")
    summary = open(summary_path, encoding="utf-8").read()

    patterns = {
        "batch gltf": r"(\d[\d,]*)\s*\|\s*—",
        "png files": r"\*\*(\d[\d,]*)\*\*\s*\|\s*\*\*(\d+)\s*MB\*\*",
        "gotchas": r"（(\d+)\s*条）",
    }
    claims = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, summary)
        if match:
            claims[key] = match.group(0)
            print("  %-18s %s" % (key, match.group(0)[:60]))
        else:
            print("  %-18s (no pattern match)" % key)

    print("")
    print("=== documents that mention counts ===")
    for name in ("UE5-KNOWLEDGE-SUMMARY.md", "BATCH-EXPORT-STATUS.md"):
        path = os.path.join(DOCS, name)
        text = open(path, encoding="utf-8").read()
        numbers = sorted(set(re.findall(r"\b(\d{3,5})\b", text)))
        interesting = [n for n in numbers
                       if n in {str(gltf), str(png), str(gotchas)}]
        print("  %-32s mentions %s" % (name, interesting if interesting else "none of note"))

    print("")
    print("manual check list:")
    print("  - summary says %d batch glTF, disk has %d" % (253, gltf))
    print("  - summary says %d PNG, disk has %d" % (2407, png))
    print("  - summary says %d gotchas, file has %d" % (106, gotchas))
    print("  - summary says %d topic documents, disk has %d" % (31, len(special)))
    matches = (gltf == 253 and png == 2407 and gotchas == 106 and len(special) == 31)
    print("")
    print("VERDICT: %s" % ("all stated counts match" if matches else "counts differ; update them"))


if __name__ == "__main__":
    main()

