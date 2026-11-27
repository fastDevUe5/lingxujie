"""Count what the Python API actually exposes, and compare it with the figure on record.

The documentation says eleven thousand six hundred and seventy-five classes. That number has been
carried for many sessions without being checked, which is the same mistake as the other recent
ones: a figure repeated rather than verified. The reflected module is the authority, so this counts
it directly and buckets the result.

    py "Tools/inventory_python_api.py"
"""

import collections

import unreal


def log(text):
    unreal.log("[LingXuJie] API: %s" % text)


def main():
    # Everything the module exposes that is not a private or dunder name.
    names = [name for name in dir(unreal) if not name.startswith("_")]
    log("module attributes: %d" % len(names))

    classes = []
    enums = []
    functions = []
    other = []
    for name in names:
        try:
            value = getattr(unreal, name)
        except Exception:  # noqa: BLE001
            other.append(name)
            continue
        if isinstance(value, type):
            classes.append(name)
        elif callable(value):
            functions.append(name)
        else:
            other.append(name)

    log("classes: %d" % len(classes))
    log("callables (not classes): %d" % len(functions))
    log("other values: %d" % len(other))

    # How many classes actually look like reflected object types by prefix.
    prefixes = collections.Counter()
    for name in classes:
        for prefix in ("Actor", "Animation", "Asset", "Audio", "Blueprint", "Component",
                       "Data", "Editor", "Engine", "Game", "Input", "Material",
                       "Mesh", "Particle", "Physics", "Render", "Scene", "Skeletal",
                       "Slate", "Sound", "Static", "Texture", "Widget", "World"):
            if name.startswith(prefix):
                prefixes[prefix] += 1
                break
        else:
            prefixes["other"] += 1

    log("classes by leading word:")
    for word, count in prefixes.most_common(14):
        log("    %-16s %d" % (word, count))

    # Methods across all classes, which is the surface an agent actually uses.
    method_total = 0
    biggest = []
    for name in classes:
        value = getattr(unreal, name, None)
        if value is None:
            continue
        try:
            members = [member for member in dir(value)
                       if not member.startswith("_") and callable(getattr(value, member, None))]
        except Exception:  # noqa: BLE001
            continue
        method_total += len(members)
        biggest.append((len(members), name))

    biggest.sort(reverse=True)
    log("total callable members across classes: %d" % method_total)
    log("largest classes:")
    for count, name in biggest[:8]:
        log("    %-40s %d" % (name, count))

    log("note: the documented figure was 11,675. measured classes: %d" % len(classes))


main()
