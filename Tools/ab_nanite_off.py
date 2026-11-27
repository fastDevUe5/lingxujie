"""Reading round: the second half of the Nanite A/B, with the camera held still.

Same level, same frozen clouds, only r.Nanite changes from one to zero. Two captures taken before the
toggle give the noise floor for this camera so the difference can be judged rather than guessed at.

    py "Tools/ab_nanite_off.py"
"""

import unreal


def log(text):
    unreal.log("[LingXuJie] AB2: %s" % text)


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None:
        log("no editor world")
        return

    unreal.SystemLibrary.execute_console_command(world, "r.VolumetricCloud 0")
    unreal.SystemLibrary.execute_console_command(world, "r.Nanite 0")
    unreal.SystemLibrary.execute_console_command(world, "r.Nanite")
    log("nanite off, clouds still off -- capture B now")
    log("done")


try:
    main()
except Exception as error:  # noqa: BLE001
    import traceback
    log("FATAL: %r" % error)
    log(traceback.format_exc())
