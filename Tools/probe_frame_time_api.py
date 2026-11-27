"""Look for a programmatic way to read frame times, since stat panels are not capturable.

The capture path renders the scene without canvas overlays, so stat unit cannot be photographed
through MCP. That makes a programmatic reader the only option that works while the person uses the
machine, so this lists every Python-visible method that might expose frame timing.

    py "Tools/probe_frame_time_api.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] FT: %s" % text)


def names_with(owner, needles):
    found = []
    for name in dir(owner):
        lowered = name.lower()
        if any(needle in lowered for needle in needles):
            found.append(name)
    return sorted(found)


def main():
    log("--- methods on the Engine class that mention unit/game/render/gpu/frame ---")
    try:
        engine_class = getattr(unreal, "Engine")
        log("Engine: %s" % names_with(engine_class, ("unit", "frame", "gpu", "render", "game")))
    except Exception as error:  # noqa: BLE001
        log("no unreal.Engine: %r" % error)

    log("--- SystemLibrary ---")
    try:
        log("SystemLibrary: %s" % names_with(unreal.SystemLibrary, ("frame", "time", "fps", "stat")))
    except Exception as error:  # noqa: BLE001
        log("no SystemLibrary: %r" % error)

    log("--- GameplayStatics ---")
    try:
        log("GameplayStatics: %s" % names_with(unreal.GameplayStatics, ("time", "frame", "fps")))
    except Exception as error:  # noqa: BLE001
        log("no GameplayStatics: %r" % error)

    log("--- anything named like a performance helper ---")
    candidates = [n for n in dir(unreal)
                  if any(k in n.lower() for k in ("perform", "stat", "profiler", "insight"))]
    log("top level: %s" % sorted(candidates)[:40])

    log("--- is there a console variable reader? ---")
    for name in ("get_console_variable", "ConsoleVariable", "get_default_object"):
        log("%s present: %s" % (name, hasattr(unreal, name)))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
