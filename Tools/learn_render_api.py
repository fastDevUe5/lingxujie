"""Print the exact signatures of the automation screenshot helpers.

The signature decides whether a script can frame its own shots (camera transform per shot) or is stuck
with whatever the viewport happens to show. Docstrings are the only reliable source here, because the
generated Python binding does not expose typed defaults.

    py "Tools/learn_render_api.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] LEARN: %s" % text)


def main():
    automation = unreal.AutomationLibrary
    for name in ("take_automation_screenshot", "take_automation_screenshot_at_camera",
                 "take_automation_screenshot_of_ui", "take_high_res_screenshot",
                 "get_default_screenshot_options_for_rendering"):
        func = getattr(automation, name, None)
        if func is None:
            log("%s: absent" % name)
            continue
        doc = (func.__doc__ or "").strip().replace("\n", " | ")
        log("%s: %s" % (name, doc[:400]))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
