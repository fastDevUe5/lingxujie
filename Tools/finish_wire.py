"""Finish wiring the scoring: pass the model's bone names and report the match count.

The unpack failure is from resolve_animation now returning three values while export_one still
expects two.

    python Tools/finish_wire.py
"""

PATH = "C:/Users/tk/Desktop/lingxujie/Tools/batch_export.py"

OLD = "    animation, listed = resolve_animation(stem)"
NEW = ('    animation, listed, matched = resolve_animation(\n'
       '        stem, [bone["name"] for bone in bones])')

OLD2 = '        "available": len(listed),'
NEW2 = '        "available": len(listed),\n        "matched": matched,'


def main():
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    if OLD in text:
        text = text.replace(OLD, NEW)
        changed += 1
    if OLD2 in text and '"matched": matched' not in text:
        text = text.replace(OLD2, NEW2)
        changed += 1
    if changed == 0:
        print("nothing to change")
        return
    open(PATH, "w", encoding="utf-8").write(text)
    print("applied %d change(s)" % changed)


if __name__ == "__main__":
    main()
