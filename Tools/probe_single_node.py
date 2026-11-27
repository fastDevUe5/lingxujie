"""List what AnimSingleNodeInstance actually exposes.

set_animation does not exist, and guessing a second name would waste another round. The reflected
member list says what can be called.

    py "Tools/probe_single_node.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] SN: %s" % text)


try:
    cls = unreal.AnimSingleNodeInstance
    names = [n for n in dir(cls) if not n.startswith("_")]
    log("AnimSingleNodeInstance has %d members" % len(names))
    interesting = [n for n in names
                   if any(word in n.lower()
                          for word in ("anim", "play", "position", "current", "set", "asset"))]
    for name in sorted(interesting):
        log("    %s" % name)

    log("")
    log("all set_* members:")
    for name in sorted(n for n in names if n.startswith("set_")):
        log("    %s" % name)
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())

log("done")
