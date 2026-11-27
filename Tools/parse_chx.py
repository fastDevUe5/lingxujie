"""Pair models with their animations by reading the .chx container instead of guessing names.

A .chx is a text listing:

    *MOD_FILE_NUM    1
    *MOD_FILE_NAME   P005_A.MOD
    *MOTION_NUM      10
        P005_A_01.ANM
        P005_A_02.ANM
        ...

but some files carry a binary prefix before that text, so the parse starts at the first occurrence
of the marker rather than at byte zero. A trailing binary tail follows the list for the same reason.

This matters because name matching is not a rule. A sixty-eight bone monster whose animation is
named nothing like it still has a .chx that names both.

    python Tools/parse_chx.py [--limit N]
"""

import os

CHX_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/chx"
MOD_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/mod"
ANM_FOLDER = "C:/Users/tk/Desktop/moxiang-study/resources/anm"


def read_text(path):
    raw = open(path, "rb").read()
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def parse_chx(path):
    """Return (model name, [animation names]) or None."""
    text = read_text(path)
    start = text.find("*MOD_FILE_NUM")
    if start < 0:
        return None
    body = text[start:]

    model_name = None
    animations = []

    lines = body.split("\n")
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("*MOD_FILE_NAME"):
            parts = stripped.split("\t")
            if len(parts) < 2:
                parts = stripped.split(None, 1)
            if len(parts) >= 2:
                model_name = parts[-1].strip()
        elif stripped.startswith("*MOTION_NUM"):
            # The animation names follow on their own lines.
            for following in lines[index + 1:]:
                candidate = following.strip()
                if not candidate:
                    continue
                if candidate.startswith("*"):
                    break
                if candidate.upper().endswith(".ANM"):
                    animations.append(candidate)
                else:
                    break

    if model_name is None:
        return None
    return model_name, animations


def build_map():
    """Map lower-case model stem to the list of animation stems named by its .chx."""
    mapping = {}
    unparsed = []
    names = sorted(n for n in os.listdir(CHX_FOLDER) if n.lower().endswith(".chx"))
    for name in names:
        path = os.path.join(CHX_FOLDER, name)
        try:
            parsed = parse_chx(path)
        except OSError:
            unparsed.append(name)
            continue
        if parsed is None:
            unparsed.append(name)
            continue
        model_name, animations = parsed
        stem = os.path.splitext(model_name)[0].lower()
        mapping.setdefault(stem, []).extend(
            os.path.splitext(animation)[0] for animation in animations)
    return mapping, unparsed


def main():
    import sys

    limit = 20
    args = sys.argv[1:]
    if "--limit" in args:
        index = args.index("--limit")
        if index + 1 < len(args):
            limit = int(args[index + 1])

    mapping, unparsed = build_map()
    print("chx files parsed: %d models, %d without a parse" % (len(mapping), len(unparsed)))
    if unparsed:
        print("  examples of unparsed: %s" % unparsed[:5])
    print("")

    total_animations = sum(len(v) for v in mapping.values())
    print("animation references: %d across %d models" % (total_animations, len(mapping)))
    models_with = sum(1 for v in mapping.values() if v)
    print("models with at least one animation: %d" % models_with)
    print("")

    # How many of these actually resolve to files on disk?
    resolved = 0
    missing = 0
    for stem, animations in mapping.items():
        for animation in animations:
            path = os.path.join(ANM_FOLDER, animation + ".anm")
            if os.path.exists(path):
                resolved += 1
            else:
                # Case matters on some filesystems; try a directory listing.
                found = any(f.lower() == (animation + ".anm").lower()
                            for f in os.listdir(ANM_FOLDER))
                if found:
                    resolved += 1
                else:
                    missing += 1
    print("animation references resolved: %d, missing: %d" % (resolved, missing))
    print("")

    print("sample pairings:")
    shown = 0
    for stem, animations in sorted(mapping.items()):
        if not animations:
            continue
        print("  %-24s -> %s" % (stem, ", ".join(animations[:4])))
        shown += 1
        if shown >= limit:
            break


if __name__ == "__main__":
    main()
