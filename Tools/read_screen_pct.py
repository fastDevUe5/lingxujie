"""Reading round, practice: what screen percentage does to a TSR frame.

The page's most concrete claim about cost is that a temporal upscaler outputs at display resolution, so the
passes after it - motion blur and the tonemapper - run at full display resolution rather than at the render
resolution the screen percentage sets. Testing that properly needs GPU timings this environment cannot
read. What can be seen is the other side of the trade: lowering screen percentage makes TSR upscale from
fewer pixels, and the resulting softness is measurable.

    percentage comes from Saved/screen_pct.txt
"""

import unreal

SCENE = "/Game/Learning/L_Scene01"
MARKER = "C:/Users/tk/Desktop/lingxujie/Saved/screen_pct.txt"


def log(text):
    unreal.log("[LingXuJie] SP: %s" % text)


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    if level_subsystem.is_in_play_in_editor():
        level_subsystem.editor_request_end_play()
        log("end play requested -- rerun after it ends")
        return

    current = level_subsystem.get_current_level()
    if (current.get_name() if current else "") != "L_Scene01":
        if not level_subsystem.load_level(SCENE):
            log("could not load the scene")
            return
        log("loaded L_Scene01")

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:
        log("no editor world")
        return

    percentage = 100
    try:
        percentage = int(open(MARKER, encoding="utf-8").read().strip())
    except (OSError, ValueError):
        pass

    unreal.SystemLibrary.execute_console_command(world, "r.ScreenPercentage %d" % percentage)
    unreal.SystemLibrary.execute_console_command(world, "r.AntiAliasingMethod 4")
    unreal.SystemLibrary.execute_console_command(world, "r.ScreenPercentage")
    unreal.SystemLibrary.execute_console_command(world, "r.AntiAliasingMethod")
    log("screen percentage %d, TSR" % percentage)
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
