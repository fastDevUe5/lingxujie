"""Practise the stat commands against the live editor.

stat draws to the viewport, not to the log, so the evidence is a screenshot taken after enabling the
panels. This enables the ones worth knowing and leaves them on so the capture shows real numbers from
this project.

    py "Tools/practice_stat_commands.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] STAT: %s" % text)


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def run(command):
    unreal.SystemLibrary.execute_console_command(world(), command)


def main():
    # Frame-level panels. unit is the smoothed one; unitmax keeps the worst sample in its window,
    # which is what actually shows a hitch.
    for command in ("stat unit", "stat unitmax", "stat unitgraph", "stat fps"):
        run(command)
        log("enabled: %s" % command)

    # Thread and render detail.
    for command in ("stat game", "stat render", "stat rhi", "stat scenerendering"):
        run(command)
        log("enabled: %s" % command)

    # The hitch detection knobs, printed so their current values are on record.
    for cvar in ("t.HitchFrameTimeThreshold", "t.HitchDeadTimeWindow",
                 "t.HitchVersusNonHitchRatio", "t.TargetFrameTimeThreshold"):
        run(cvar)
        log("queried: %s" % cvar)

    log("done - panels enabled; the numbers come from the viewport capture")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
