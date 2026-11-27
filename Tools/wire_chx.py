"""Wire the chx map into the batch exporter's export path.

The map is built and the helpers exist, but export_one still calls the name-guessing finder. This
switches it to resolve_animation, which consults the container first and only falls back to names
when there is no entry.

    python Tools/wire_chx.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/batch_export.py"

REPLACEMENTS = [
    (
        '    animation = find_animation(stem)\n    tracks = exporter.parse_anm(animation) if animation else {}',
        '    animation, listed = resolve_animation(stem)\n'
        '    tracks = exporter.parse_anm(animation) if animation else {}',
    ),
    (
        '        "animation": os.path.basename(animation) if animation else None,',
        '        "animation": os.path.basename(animation) if animation else None,\n'
        '        "available": len(listed),',
    ),
    (
        '    names = sorted(n for n in os.listdir(MOD_FOLDER) if n.endswith(".mod"))',
        '    build_chx_map()\n\n'
        '    names = sorted(n for n in os.listdir(MOD_FOLDER) if n.endswith(".mod"))',
    ),
]


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    if changed == 0:
        print("nothing to change; already wired")
        return
    open(PATH, "w", encoding="utf-8").write(text)
    print("applied %d of %d replacements" % (changed, len(REPLACEMENTS)))


if __name__ == "__main__":
    main()
