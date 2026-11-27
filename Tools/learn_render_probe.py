"""Find out what the editor Python API can actually do about screenshots and console variables.

Two questions decide how the rendering practice is run:
  1. can a script take a picture itself, or must every capture come from an MCP round trip?
  2. does execute_console_command hand back the command's text, so a CVar's value can be read?

Answers are logged, not remembered: the API surface differs between 5.x minors.

    py "Tools/learn_render_probe.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] LEARN: %s" % text)


def names_with(obj, needles):
    found = []
    for name in dir(obj):
        lowered = name.lower()
        if any(needle in lowered for needle in needles):
            found.append(name)
    return sorted(found)


def main():
    for label, obj in (
        ("AutomationLibrary", getattr(unreal, "AutomationLibrary", None)),
        ("SystemLibrary", getattr(unreal, "SystemLibrary", None)),
        ("EditorLevelLibrary", getattr(unreal, "EditorLevelLibrary", None)),
        ("EditorLoadingAndSavingUtils", getattr(unreal, "EditorLoadingAndSavingUtils", None)),
    ):
        if obj is None:
            log("%s: absent" % label)
            continue
        log("%s screenshot-ish: %s" % (label, names_with(obj, ("screen", "shot", "capture"))))

    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    log("UnrealEditorSubsystem screenshot-ish: %s" % names_with(subsystem, ("screen", "shot", "capture", "view")))
    log("LevelEditorSubsystem screenshot-ish: %s" % names_with(level_subsystem, ("screen", "shot", "capture", "view")))

    world = subsystem.get_editor_world()
    for command in (
        "r.Lumen.ScreenProbeGather.DownsampleFactor",
        "r.DynamicGlobalIlluminationMethod",
        "r.ReflectionMethod",
        "stat unit",
    ):
        try:
            returned = unreal.SystemLibrary.execute_console_command(world, command)
            log("command %-46s returned %r" % (command, returned))
        except Exception as error:  # noqa: BLE001
            log("command %-46s error %r" % (command, error))

    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
