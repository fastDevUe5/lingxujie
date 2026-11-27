"""Optimisation round 2, baseline for real: the same 120-frame average with Lumen GI on.

The earlier baseline attempt only started the play session, so it measured nothing. The variant was
measured at a hundred twenty frames, so this does the same count with Lumen at its default enabled state.
Comparing a single frame against an average would not be a comparison.

    py "Tools/opt2_base2.py"
"""

import unreal

FRAMES = 120


def log(text):
    unreal.log("[LingXuJie] BASE2: %s" % text)


def main():
    subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = subsystem.get_game_world()
    if world is None:
        log("no game world; start simulate first")
        return

    unreal.SystemLibrary.execute_console_command(world, "r.Lumen.DiffuseIndirect.Allow 1")
    unreal.SystemLibrary.execute_console_command(world, "r.Lumen.DiffuseIndirect.Allow")

    log("dumping %d frames with Lumen GI on" % FRAMES)
    unreal.SystemLibrary.execute_console_command(
        world, "stat dumpave -start -ms=0 -num=%d" % FRAMES)
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
